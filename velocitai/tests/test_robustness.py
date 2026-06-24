"""Test di robustezza: ogni scenario di errore previsto deve essere gestito
senza fermare l'accertamento ne' produrre atti invalidi."""

import os
import json
import tempfile
import shutil
import unittest

from velocitai.config import Config, load_config, validate_config, ConfigError
from velocitai.pipeline import build_simulated_pipeline
from velocitai.scenario import default_scenario
from velocitai.recorder import verify_evidence
from velocitai.registry import OwnerRegistry
from velocitai.speed import WorldRegressionEstimator, LinePairEstimator
from velocitai.geometry import LineGate
from velocitai.fines import classify, apply_tolerance
from velocitai.config import SanctionConfig
from velocitai.models import Track, TrackPoint, BBox, Point

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAN = float("nan")
INF = float("inf")


def _bbox(y):
    return BBox(0.0, y, 2.0, y + 1.0)


def _track_with_world(ys, ts=None):
    ts = ts or [i * 0.1 for i in range(len(ys))]
    pts = [TrackPoint(i, ts[i], _bbox(ys[i]), Point(10.0, ys[i]))
           for i in range(len(ys))]
    return Track(track_id=1, points=pts, confirmed=True)


def _pipeline(tmp, **kw):
    cfg = Config()
    cfg.recorder.output_dir = os.path.join(tmp, "evidence")
    cfg.notifier.output_dir = os.path.join(tmp, "verbali")
    cfg.registry_path = os.path.join(PROJECT_ROOT, "data", "registry", "owners.json")
    return build_simulated_pipeline(cfg, **kw), cfg


# ---------------------------------------------------------------------------
# Dati numerici corrotti (NaN / inf)
# ---------------------------------------------------------------------------

class TestCorruptNumerics(unittest.TestCase):
    def test_world_regression_ignores_nan_points(self):
        # un campione NaN non deve produrre una misura: i punti finiti sono < min
        est = WorldRegressionEstimator(min_points=4)
        track = _track_with_world([0.0, NAN, 20.0, INF])
        self.assertIsNone(est.estimate(track))

    def test_world_regression_clean_after_filtering_is_finite(self):
        est = WorldRegressionEstimator(min_points=3)
        track = _track_with_world([0.0, 10.0, 20.0, 30.0])
        m = est.estimate(track)
        self.assertIsNotNone(m)
        import math
        self.assertTrue(math.isfinite(m.measured_speed_kmh))

    def test_linepair_guard_on_bad_gate(self):
        est = LinePairEstimator(LineGate(10.0, 30.0, NAN), min_points=4)
        track = _track_with_world([0.0, 12.0, 24.0, 36.0])
        self.assertIsNone(est.estimate(track))

    def test_classify_rejects_non_finite(self):
        cfg = SanctionConfig()
        self.assertIsNone(classify(NAN, cfg))
        self.assertIsNone(classify(INF, cfg))

    def test_apply_tolerance_on_nan(self):
        self.assertEqual(apply_tolerance(NAN, SanctionConfig()), 0.0)


# ---------------------------------------------------------------------------
# Isolamento dei guasti per-traccia (self-healing)
# ---------------------------------------------------------------------------

class _FailOnceRecorder:
    """Decoratore che fa fallire la registrazione della PRIMA violazione."""
    def __init__(self, inner):
        self.inner = inner
        self.calls = 0

    def record(self, *a, **k):
        self.calls += 1
        if self.calls == 1:
            raise OSError("disco pieno (simulato)")
        return self.inner.record(*a, **k)


class TestPerTrackIsolation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="robust-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_one_failing_track_does_not_lose_others(self):
        pipe, cfg = _pipeline(self.tmp)
        pipe.recorder = _FailOnceRecorder(pipe.recorder)
        result = pipe.process_frames(default_scenario().frames())
        # 3 violazioni nello scenario: 1 fallisce, 2 emesse comunque
        self.assertEqual(len(result.violations), 2)
        self.assertEqual(result.stats["errors"], 1)
        # il guasto e' finito nella coda dead-letter durabile
        dlq_dir = os.path.join(self.tmp, "deadletter")
        self.assertTrue(os.path.isdir(dlq_dir))
        self.assertTrue(any(n.startswith("track__") for n in os.listdir(dlq_dir)))
        # la salute segnala il componente degradato
        self.assertIn("pipeline_track", result.health["components"])


class _AlwaysFailRecorder:
    def __init__(self):
        self.calls = 0

    def record(self, *a, **k):
        self.calls += 1
        raise OSError("storage non disponibile")


class TestCircuitBreakerIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="robust-cb-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_recorder_breaker_stops_hammering(self):
        from velocitai.resilience import CircuitBreaker
        pipe, cfg = _pipeline(self.tmp)
        rec = _AlwaysFailRecorder()
        pipe.recorder = rec
        # soglia bassa: dopo 2 fallimenti il circuito si apre per il resto del run
        pipe._cb_recorder = CircuitBreaker(fail_max=2, reset_after=1e6, name="recorder")
        result = pipe.process_frames(default_scenario().frames())
        # 3 violazioni: le prime 2 invocano il recorder, la 3a e' fast-failed
        self.assertEqual(len(result.violations), 0)
        self.assertEqual(result.stats["errors"], 3)
        self.assertEqual(rec.calls, 2)
        self.assertEqual(pipe._cb_recorder.state, "open")


class TestNotifierDegradation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="robust-pec-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_pec_failure_goes_to_dead_letter_keeping_verbale(self):
        cfg = Config()
        cfg.recorder.output_dir = os.path.join(self.tmp, "ev")
        cfg.notifier.output_dir = os.path.join(self.tmp, "vb")
        cfg.notifier.mode = "pec"      # _send_pec non implementato -> fallisce
        cfg.registry_path = os.path.join(PROJECT_ROOT, "data", "registry", "owners.json")
        pipe = build_simulated_pipeline(cfg)
        result = pipe.process_frames(default_scenario().frames())
        # le violazioni si accertano comunque e il verbale resta scritto su disco
        self.assertEqual(len(result.violations), 3)
        for d in result.dispatches:
            self.assertEqual(d["status"], "DEAD_LETTER")
            self.assertTrue(os.path.exists(d["txt_path"]))
            self.assertTrue(os.path.exists(d["json_path"]))
        # le notifiche fallite sono in coda per la ripresa automatica
        dlq = os.path.join(self.tmp, "deadletter")
        self.assertTrue(any(n.startswith("notification__")
                            for n in os.listdir(dlq)))


class _RaisingANPR:
    def read(self, track, frames):
        raise RuntimeError("backend OCR in crash")


class TestDegradedAnpr(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="robust-anpr-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_anpr_crash_degrades_to_review(self):
        pipe, cfg = _pipeline(self.tmp)
        pipe.anpr = _RaisingANPR()
        result = pipe.process_frames(default_scenario().frames())
        # le violazioni si emettono comunque, ma marcate DA_VERIFICARE
        self.assertEqual(len(result.violations), 3)
        self.assertEqual(result.stats["needs_review"], 3)
        for v in result.violations:
            self.assertEqual(v.plate.text, "ILLEGGIBILE")


# ---------------------------------------------------------------------------
# Idempotenza anti doppia-sanzione
# ---------------------------------------------------------------------------

class TestIdempotency(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="robust-idem-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_reprocessing_does_not_double_fine(self):
        pipe, cfg = _pipeline(self.tmp)
        frames = default_scenario().frames()
        first = pipe.process_frames(frames)
        self.assertEqual(len(first.violations), 3)
        # stessa clip rielaborata: nessuna nuova sanzione
        second = pipe.process_frames(default_scenario().frames())
        self.assertEqual(len(second.violations), 0)
        self.assertEqual(second.stats["skipped_duplicate"], 3)


# ---------------------------------------------------------------------------
# Configurazione invalida / robusta
# ---------------------------------------------------------------------------

class TestConfigValidation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="robust-cfg-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, text):
        p = os.path.join(self.tmp, "c.yaml")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    def test_default_config_is_valid(self):
        self.assertEqual(validate_config(Config()), [])

    def test_negative_tolerance_detected(self):
        cfg = Config()
        cfg.sanction.tolerance_percent = -1.0
        self.assertTrue(validate_config(cfg))

    def test_overlapping_brackets_detected(self):
        cfg = Config()
        cfg.sanction.brackets[1].over_min_kmh = 0.0   # si sovrappone a comma 7
        self.assertTrue(any("sovrapp" in e for e in validate_config(cfg)))

    def test_missing_file_raises_configerror(self):
        with self.assertRaises(ConfigError):
            load_config(os.path.join(self.tmp, "non-esiste.yaml"))

    def test_unknown_keys_are_ignored(self):
        try:
            import yaml  # noqa: F401
        except Exception:
            self.skipTest("PyYAML non disponibile")
        p = self._write("location:\n  speed_limit_kmh: 30\n  refuso_inesistente: 1\n")
        cfg = load_config(p)
        self.assertEqual(cfg.location.speed_limit_kmh, 30)

    def test_strict_rejects_invalid_yaml_values(self):
        try:
            import yaml  # noqa: F401
        except Exception:
            self.skipTest("PyYAML non disponibile")
        p = self._write("location:\n  speed_limit_kmh: -5\n")
        with self.assertRaises(ConfigError):
            load_config(p, strict=True)


# ---------------------------------------------------------------------------
# Registro intestatari malformato
# ---------------------------------------------------------------------------

class TestRegistryRobustness(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="robust-reg-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_malformed_records_skipped(self):
        p = os.path.join(self.tmp, "owners.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump([
                {"plate": "AB123CD", "full_name": "Valido"},
                {"no_plate": "x"},          # malformato -> saltato
                {"plate": "", "full_name": "Vuoto"},  # targa vuota -> saltato
            ], fh)
        reg = OwnerRegistry.from_json(p)
        self.assertIsNotNone(reg.lookup("AB123CD"))
        self.assertIsNone(reg.lookup("XX000XX"))

    def test_non_list_root_raises(self):
        p = os.path.join(self.tmp, "bad.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"plate": "AB123CD"}, fh)
        with self.assertRaises(ValueError):
            OwnerRegistry.from_json(p)


# ---------------------------------------------------------------------------
# Integrita' della prova (rilevamento manomissione)
# ---------------------------------------------------------------------------

class TestEvidenceIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="robust-ev-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_tampering_is_detected(self):
        pipe, cfg = _pipeline(self.tmp)
        result = pipe.process_frames(default_scenario().frames())
        ev = result.violations[0].evidence
        self.assertTrue(verify_evidence(ev))      # integra appena scritta
        # manomissione del file-prova: la verifica deve fallire
        with open(ev.clip_path, "a", encoding="utf-8") as fh:
            fh.write("X")
        self.assertFalse(verify_evidence(ev))

    def test_missing_evidence_file_fails_verification(self):
        pipe, cfg = _pipeline(self.tmp)
        result = pipe.process_frames(default_scenario().frames())
        ev = result.violations[0].evidence
        os.remove(ev.clip_path)
        self.assertFalse(verify_evidence(ev))

    def test_verification_survives_relocation(self):
        # l'integrita' deve dipendere dal contenuto, non dalla posizione su disco:
        # spostare il pacchetto-prova non deve invalidarne la verifica
        import dataclasses
        pipe, cfg = _pipeline(self.tmp)
        result = pipe.process_frames(default_scenario().frames())
        ev = result.violations[0].evidence
        old = os.path.dirname(ev.clip_path)
        new = old + "-archiviato"
        shutil.move(old, new)
        moved = dataclasses.replace(
            ev,
            clip_path=os.path.join(new, os.path.basename(ev.clip_path)),
            plate_crop_path=(os.path.join(new, os.path.basename(ev.plate_crop_path))
                             if ev.plate_crop_path else None))
        self.assertTrue(verify_evidence(moved))


class TestDeterministicAnpr(unittest.TestCase):
    def test_ocr_noise_is_reproducible_across_instances(self):
        # il rumore OCR simulato deve essere identico per la stessa targa anche
        # in processi/istanze diverse (no hash() builtin randomizzato)
        from velocitai.anpr import SimulatedANPR, PlateValidator
        a = SimulatedANPR(PlateValidator(), char_error_rate=0.6)
        b = SimulatedANPR(PlateValidator(), char_error_rate=0.6)
        for plate in ("AB123CD", "FH983KL", "ZZ999ZZ"):
            self.assertEqual(a._inject_noise(plate), b._inject_noise(plate))


if __name__ == "__main__":
    unittest.main()
