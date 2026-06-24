"""Test end-to-end della pipeline sullo scenario dimostrativo."""

import os
import json
import tempfile
import unittest

from velocitai.config import Config
from velocitai.pipeline import build_simulated_pipeline
from velocitai.scenario import default_scenario

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _config(tmp):
    cfg = Config()
    cfg.recorder.output_dir = os.path.join(tmp, "evidence")
    cfg.notifier.output_dir = os.path.join(tmp, "verbali")
    cfg.registry_path = os.path.join(PROJECT_ROOT, "data", "registry", "owners.json")
    return cfg


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="velocitai-test-")
        self.cfg = _config(self.tmp)
        self.pipeline = build_simulated_pipeline(self.cfg)
        self.result = self.pipeline.process_frames(default_scenario().frames())

    def test_counts(self):
        s = self.result.stats
        self.assertEqual(s["tracks"], 5)
        self.assertEqual(s["violations"], 3)
        self.assertEqual(s["compliant"], 2)
        self.assertEqual(s["needs_review"], 0)

    def test_violation_brackets(self):
        by_plate = {v.plate.text: v for v in self.result.violations}
        self.assertIn("FH983KL", by_plate)
        self.assertIn("GA419LM", by_plate)
        self.assertIn("DZ704XP", by_plate)
        self.assertNotIn("EB512FG", by_plate)   # conforme
        self.assertNotIn("JB256RT", by_plate)   # conforme dopo tolleranza

        articoli = {}
        for verbale in self.result.verbali:
            articoli[verbale.violation.plate.text] = verbale.sanction.comma
        self.assertEqual(articoli["FH983KL"], "comma 8")
        self.assertEqual(articoli["GA419LM"], "comma 9")
        self.assertEqual(articoli["DZ704XP"], "comma 9-bis")

    def test_speed_accuracy(self):
        by_plate = {v.plate.text: v for v in self.result.violations}
        self.assertAlmostEqual(by_plate["FH983KL"].measured_speed_kmh, 67.0, delta=0.5)
        self.assertAlmostEqual(by_plate["DZ704XP"].measured_speed_kmh, 121.0, delta=0.5)

    def test_evidence_and_chain_of_custody(self):
        from velocitai.utils import sha256_of_files
        for v in self.result.violations:
            self.assertTrue(v.evidence.clip_path)
            self.assertTrue(os.path.exists(v.evidence.clip_path))
            self.assertEqual(len(v.evidence.sha256), 64)   # SHA-256 hex
            # la prova e' verificabile: ricalcolando l'hash sui file si ottiene
            # esattamente il digest registrato (catena di custodia)
            files = [v.evidence.clip_path]
            if v.evidence.plate_crop_path:
                files.append(v.evidence.plate_crop_path)
            self.assertEqual(sha256_of_files(files), v.evidence.sha256)

    def test_verbali_written(self):
        for d in self.result.dispatches:
            self.assertTrue(os.path.exists(d["txt_path"]))
            self.assertTrue(os.path.exists(d["json_path"]))
            self.assertEqual(d["status"], "SIMULATED_DISPATCH")

    def test_owner_resolved(self):
        by_plate = {verb.violation.plate.text: verb for verb in self.result.verbali}
        self.assertEqual(by_plate["FH983KL"].owner.full_name, "Giulia Bianchi")


if __name__ == "__main__":
    unittest.main()
