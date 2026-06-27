"""Test dei comandi CLI che hanno logica propria (doctor / manutenzione)."""

import argparse
import os
import tempfile
import shutil
import time
import unittest

import velocitai.cli as cli
from velocitai.config import Config
from velocitai.resilience import IssuedLedger


class TestDoctorPrune(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cli-")
        self._orig_config = cli.Config

        def _patched():
            c = Config()
            c.recorder.output_dir = os.path.join(self.tmp, "evidence")
            c.notifier.output_dir = os.path.join(self.tmp, "verbali")
            return c

        cli.Config = _patched

    def tearDown(self):
        cli.Config = self._orig_config
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_prune_ledger_via_doctor(self):
        led = IssuedLedger(os.path.join(self.tmp, "issued_ledger.json"), window_s=2.0)
        now = time.time()
        old_k = led.key_for("DEV", "AB123CD", now - 200 * 86400)
        new_k = led.key_for("DEV", "EF456GH", now)
        led.add(old_k)
        led.add(new_k)

        ns = argparse.Namespace(config=None, repair=False, prune_ledger_days=90.0)
        rc = cli.cmd_doctor(ns)
        self.assertEqual(rc, 0)

        reloaded = IssuedLedger(os.path.join(self.tmp, "issued_ledger.json"), window_s=2.0)
        self.assertFalse(reloaded.seen(old_k))   # potata
        self.assertTrue(reloaded.seen(new_k))     # conservata

    def test_doctor_clean_returns_zero(self):
        ns = argparse.Namespace(config=None, repair=False, prune_ledger_days=None)
        self.assertEqual(cli.cmd_doctor(ns), 0)


if __name__ == "__main__":
    unittest.main()
