"""Test degli strati di sicurezza: input/path, crypto/integrita', PII, DoS, web."""

import os
import tempfile
import shutil
import threading
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer

from velocitai.security import (
    safe_path_component, secure_join, SecurityError,
    keyed_digest_of_files, digest_algo, constant_time_equals,
    redact_plate, redact_pii, PIIRedactingFilter, AuditLog, RateLimiter,
    set_secure_permissions, load_secret,
)


class TestPathSafety(unittest.TestCase):
    def test_blocks_traversal_and_nullbyte(self):
        self.assertEqual(safe_path_component("../../etc/passwd"), "passwd")  # basename
        self.assertEqual(safe_path_component("foo/bar"), "bar")
        for bad in ("..", ".", "", "....//", "/", "\x00"):
            with self.assertRaises(SecurityError):
                safe_path_component(bad)

    def test_secure_join_confines_to_base(self):
        base = tempfile.mkdtemp(prefix="sj-")
        try:
            p = secure_join(base, "violazione-0001")
            self.assertTrue(p.startswith(os.path.realpath(base) + os.sep))
            # un tentativo di evasione viene sanitizzato a basename, mai fuori base
            p2 = secure_join(base, "../../etc/passwd")
            self.assertTrue(p2.startswith(os.path.realpath(base) + os.sep))
        finally:
            shutil.rmtree(base, ignore_errors=True)


class TestKeyedDigest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="dig-")
        self.f = os.path.join(self.d, "a.txt")
        with open(self.f, "w") as fh:
            fh.write("contenuto-prova")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_hmac_vs_plain_and_key_sensitivity(self):
        plain = keyed_digest_of_files([self.f], None)
        h1 = keyed_digest_of_files([self.f], b"k1")
        h2 = keyed_digest_of_files([self.f], b"k2")
        self.assertNotEqual(plain, h1)        # keyed != non-keyed
        self.assertNotEqual(h1, h2)           # chiavi diverse -> digest diversi
        self.assertEqual(digest_algo(None), "sha256")
        self.assertEqual(digest_algo(b"k"), "hmac-sha256")

    def test_tampering_changes_digest(self):
        before = keyed_digest_of_files([self.f], b"k")
        with open(self.f, "a") as fh:
            fh.write("X")
        self.assertNotEqual(before, keyed_digest_of_files([self.f], b"k"))

    def test_constant_time_equals(self):
        self.assertTrue(constant_time_equals("abc", "abc"))
        self.assertFalse(constant_time_equals("abc", "abd"))


class TestPIIRedaction(unittest.TestCase):
    def test_plate_and_fields(self):
        self.assertEqual(redact_plate("AB123CD"), "AB***CD")
        red = redact_pii("targa AB123CD CF RSSMRA85T10A562S mail a@b.it")
        self.assertIn("AB***CD", red)
        self.assertNotIn("AB123CD", red)
        self.assertIn("CF-REDACTED", red)
        self.assertIn("EMAIL-REDACTED", red)

    def test_logging_filter_redacts(self):
        import logging
        rec = logging.LogRecord("x", logging.INFO, __file__, 1,
                                "violazione targa %s", ("AB123CD",), None)
        PIIRedactingFilter().filter(rec)
        self.assertNotIn("AB123CD", rec.getMessage())
        self.assertIn("AB***CD", rec.getMessage())


class TestAuditLog(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="audit-")
        self.p = os.path.join(self.d, "audit.log")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_chain_integrity_and_tamper_detection(self):
        a = AuditLog(self.p, key=b"secret")
        a.record("violation_issued", violation_id="V1", plate="AB123CD")
        a.record("violation_issued", violation_id="V2", plate="FH983KL")
        self.assertTrue(a.verify())
        # la PII e' redatta nel file
        content = open(self.p, encoding="utf-8").read()
        self.assertNotIn("AB123CD", content)
        self.assertIn("AB***CD", content)
        # manomissione di una riga -> catena rotta
        lines = content.splitlines()
        lines[0] = lines[0].replace("V1", "V9")
        with open(self.p, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        self.assertFalse(a.verify())

    def test_hmac_key_prevents_forgery(self):
        # senza la chiave giusta la catena non e' ricostruibile/verificabile
        a = AuditLog(self.p, key=b"right")
        a.record("e", x="1")
        self.assertFalse(AuditLog(self.p, key=b"wrong").verify())


class TestRateLimiter(unittest.TestCase):
    def test_burst_then_block(self):
        rl = RateLimiter(rate_per_s=0.0, burst=3, clock=lambda: 0.0)
        self.assertTrue(all(rl.allow("1.2.3.4") for _ in range(3)))
        self.assertFalse(rl.allow("1.2.3.4"))      # esaurito il burst
        self.assertTrue(rl.allow("9.9.9.9"))        # altro client indipendente


class TestSecurePermissions(unittest.TestCase):
    def test_file_perms_restricted(self):
        d = tempfile.mkdtemp(prefix="perm-")
        try:
            f = os.path.join(d, "x")
            with open(f, "w") as fh:
                fh.write("pii")
            set_secure_permissions(f)
            mode = os.stat(f).st_mode & 0o777
            self.assertEqual(mode, 0o600)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestConfigDoS(unittest.TestCase):
    def test_merge_depth_limit(self):
        from velocitai.config import _merge, ConfigError
        d = {"x": 1}
        for _ in range(60):
            d = {"a": d}
        with self.assertRaises(ConfigError):
            _merge(d, d)


class TestPipelineResourceLimits(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="reslim-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _pipe(self, **sec):
        from velocitai.config import Config
        from velocitai.pipeline import build_simulated_pipeline
        cfg = Config()
        cfg.recorder.output_dir = os.path.join(self.tmp, "ev")
        cfg.notifier.output_dir = os.path.join(self.tmp, "vb")
        cfg.registry_path = os.path.join(self.tmp, "none.json")
        for k, v in sec.items():
            setattr(cfg.security, k, v)
        return build_simulated_pipeline(cfg), cfg

    def test_max_vehicles_per_frame_skips_frames(self):
        from velocitai.scenario import default_scenario
        pipe, _ = self._pipe(max_vehicles_per_frame=1)
        result = pipe.process_frames(default_scenario().frames())
        # i fotogrammi con piu' di 1 veicolo vengono scartati: nessun crash
        self.assertEqual(result.stats["violations"], 0)

    def test_max_frames_truncates(self):
        from velocitai.scenario import default_scenario
        pipe, _ = self._pipe(max_frames=10)
        result = pipe.process_frames(default_scenario().frames())
        self.assertEqual(result.stats["frames"], 10)


class TestDashboardSecurity(unittest.TestCase):
    """Test d'integrazione HTTP del server blindato (token, header, metodi)."""

    def setUp(self):
        import velocitai.dashboard as dash
        from velocitai.config import Config
        from velocitai.pipeline import build_simulated_pipeline
        from velocitai.scenario import default_scenario
        self.dash = dash
        self.tmp = tempfile.mkdtemp(prefix="web-")
        cfg = Config()
        cfg.recorder.output_dir = os.path.join(self.tmp, "ev")
        cfg.notifier.output_dir = os.path.join(self.tmp, "vb")
        cfg.registry_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "registry", "owners.json")
        result = build_simulated_pipeline(cfg).process_frames(default_scenario().frames())
        state = dash._State()
        state.config = cfg
        state.result = result
        dash._Handler.state = state
        dash._Handler.token = b"segreto-token"
        dash._Handler.rate_limiter = dash.RateLimiter(rate_per_s=1000, burst=1000)
        dash._Handler.require_localhost = True
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), dash._Handler)
        self.port = self.httpd.server_address[1]
        self.t = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.t.start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _get(self, path, headers=None, method="GET"):
        url = f"http://127.0.0.1:{self.port}{path}"
        req = urllib.request.Request(url, headers=headers or {}, method=method)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, dict(resp.headers), resp.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read()

    def test_requires_token(self):
        code, _, _ = self._get("/")
        self.assertEqual(code, 401)

    def test_wrong_token_rejected(self):
        code, _, _ = self._get("/", {"Authorization": "Bearer sbagliato"})
        self.assertEqual(code, 401)

    def test_authorized_with_security_headers(self):
        code, headers, _ = self._get("/", {"Authorization": "Bearer segreto-token"})
        self.assertEqual(code, 200)
        self.assertEqual(headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
        self.assertIn("Content-Security-Policy", headers)
        self.assertIn("no-store", headers.get("Cache-Control", ""))

    def test_non_get_method_rejected(self):
        code, _, _ = self._get("/", {"Authorization": "Bearer segreto-token"},
                               method="POST")
        self.assertEqual(code, 405)


if __name__ == "__main__":
    unittest.main()
