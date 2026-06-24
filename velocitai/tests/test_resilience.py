"""Test dei primitivi di resilienza e auto-riparazione."""

import os
import tempfile
import shutil
import unittest

from velocitai.resilience import (
    retry, CircuitBreaker, CircuitBreakerOpen, guard,
    HealthMonitor, DeadLetterQueue, IssuedLedger,
)
from velocitai.utils import atomic_write_text, is_finite_number, safe_float


class TestRetry(unittest.TestCase):
    def test_succeeds_after_transient_failures(self):
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise ValueError("transient")
            return "ok"

        out = retry(flaky, attempts=5, base_delay=0.0)
        self.assertEqual(out, "ok")
        self.assertEqual(calls["n"], 3)

    def test_raises_after_exhausting_attempts(self):
        calls = {"n": 0}

        def always():
            calls["n"] += 1
            raise RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            retry(always, attempts=3, base_delay=0.0)
        self.assertEqual(calls["n"], 3)   # esattamente attempts tentativi


class TestCircuitBreaker(unittest.TestCase):
    def _cb(self):
        self.t = [0.0]
        return CircuitBreaker(fail_max=2, reset_after=10.0,
                              clock=lambda: self.t[0])

    def test_opens_and_rejects(self):
        cb = self._cb()
        for _ in range(2):
            with self.assertRaises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("x")))
        self.assertEqual(cb.state, "open")
        # con circuito aperto le chiamate sono respinte subito
        with self.assertRaises(CircuitBreakerOpen):
            cb.call(lambda: "mai eseguita")

    def test_half_open_then_close_on_success(self):
        cb = self._cb()
        for _ in range(2):
            with self.assertRaises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("x")))
        self.t[0] = 11.0                         # superato reset_after
        self.assertEqual(cb.call(lambda: "ok"), "ok")
        self.assertEqual(cb.state, "closed")


class TestGuardAndHealth(unittest.TestCase):
    def test_guard_isolates_and_records(self):
        mon = HealthMonitor()
        ok = guard(lambda: 42, component="c", monitor=mon)
        self.assertTrue(ok.ok)
        self.assertEqual(ok.value, 42)
        bad = guard(lambda: 1 / 0, component="c", monitor=mon, default="x")
        self.assertFalse(bad.ok)
        self.assertEqual(bad.value, "x")
        self.assertIsNotNone(bad.error)
        h = mon.get("c")
        self.assertEqual(h.successes, 1)
        self.assertEqual(h.failures, 1)

    def test_health_unhealthy_after_consecutive_failures(self):
        mon = HealthMonitor()
        for _ in range(3):
            mon.record("x", ok=False, error="e")
        self.assertFalse(mon.is_healthy())
        mon.record("x", ok=True)
        self.assertTrue(mon.is_healthy())   # un successo azzera i consecutivi


class TestDeadLetterQueue(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="dlq-")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_add_list_and_retry(self):
        dlq = DeadLetterQueue(self.dir)
        dlq.add("notification", "PL-1", {"x": 1}, error="pec down")
        self.assertEqual(len(dlq.pending()), 1)

        # handler che fallisce -> elemento resta in coda
        res = dlq.retry_pending(lambda rec: (_ for _ in ()).throw(RuntimeError("no")))
        self.assertEqual(res, {"resolved": 0, "failed": 1})
        self.assertEqual(len(dlq.pending()), 1)

        # handler che riesce -> elemento risolto e rimosso
        res = dlq.retry_pending(lambda rec: None)
        self.assertEqual(res, {"resolved": 1, "failed": 0})
        self.assertEqual(len(dlq.pending()), 0)

    def test_attempts_increment_on_readd(self):
        dlq = DeadLetterQueue(self.dir)
        dlq.add("track", "7", {"a": 1})
        dlq.add("track", "7", {"a": 1})
        rec = dlq.pending()[0]
        self.assertEqual(rec["attempts"], 2)


class TestIssuedLedger(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ledger-")
        self.path = os.path.join(self.dir, "led.json")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_idempotent_and_durable(self):
        led = IssuedLedger(self.path, window_s=2.0)
        k = led.key_for("DEV1", "AB123CD", 100.0)
        self.assertFalse(led.seen(k))
        led.add(k)
        self.assertTrue(led.seen(k))
        # ricaricato da disco: lo stato persiste (durabilita')
        led2 = IssuedLedger(self.path, window_s=2.0)
        self.assertTrue(led2.seen(k))

    def test_time_window_bucketing(self):
        led = IssuedLedger(self.path, window_s=2.0)
        k1 = led.key_for("D", "AB123CD", 100.0)
        k2 = led.key_for("D", "AB123CD", 101.0)   # stessa finestra di 2s
        k3 = led.key_for("D", "AB123CD", 103.0)   # finestra successiva
        self.assertEqual(k1, k2)
        self.assertNotEqual(k1, k3)

    def test_prune_bounds_growth(self):
        led = IssuedLedger(self.path, window_s=2.0)
        led.add(led.key_for("D", "AB123CD", 100.0))    # vecchia
        led.add(led.key_for("D", "EF456GH", 10_000.0))  # recente
        removed = led.prune(older_than_ts=5_000.0)
        self.assertEqual(removed, 1)
        self.assertFalse(led.seen(led.key_for("D", "AB123CD", 100.0)))
        self.assertTrue(led.seen(led.key_for("D", "EF456GH", 10_000.0)))
        # persistito: ricaricando, la chiave potata resta assente
        led2 = IssuedLedger(self.path, window_s=2.0)
        self.assertFalse(led2.seen(led.key_for("D", "AB123CD", 100.0)))


class TestAtomicWriteAndFloats(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="atomic-")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_atomic_write_no_temp_leftover(self):
        path = os.path.join(self.dir, "sub", "f.txt")
        atomic_write_text(path, "contenuto")
        with open(path, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "contenuto")
        atomic_write_text(path, "nuovo")          # sovrascrittura atomica
        with open(path, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "nuovo")
        leftovers = [n for n in os.listdir(os.path.dirname(path))
                     if n.startswith(".tmp-")]
        self.assertEqual(leftovers, [])

    def test_finite_checks(self):
        self.assertTrue(is_finite_number(1.5))
        self.assertFalse(is_finite_number(float("nan")))
        self.assertFalse(is_finite_number(float("inf")))
        self.assertFalse(is_finite_number(True))   # bool non e' un numero fisico
        self.assertFalse(is_finite_number(None))
        self.assertEqual(safe_float("3.2"), 3.2)
        self.assertEqual(safe_float("x", 9.0), 9.0)
        self.assertEqual(safe_float(float("inf"), 9.0), 9.0)


if __name__ == "__main__":
    unittest.main()
