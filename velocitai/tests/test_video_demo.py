"""Test della demo VIDEO end-to-end (rilevamento classico OpenCV su pixel reali).

Saltato automaticamente dove OpenCV non e' installato (es. la CI a sola libreria
standard): in locale, con ``pip install opencv-python-headless numpy``, verifica
che dal video sintetico si rilevi UNA infrazione, si legga la targa dai pixel e
si produca la sanzione corretta (Art. 142 comma 9)."""

import os
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import cv2  # noqa: F401
    import numpy  # noqa: F401
    _HAS_CV = True
except Exception:
    _HAS_CV = False


@unittest.skipUnless(_HAS_CV, "OpenCV/numpy non installati (richiede requirements-prod)")
class TestVideoDemo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="vdemo-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_detects_single_infraction_from_video(self):
        from examples import video_demo as vd
        result, cfg = vd.run(self.tmp)

        # esattamente UNA violazione (un veicolo, niente doppioni)
        self.assertEqual(result.stats["violations"], 1)
        v = result.violations[0]
        # targa letta dai PIXEL del video
        self.assertEqual(v.plate.text, "FH983KL")
        self.assertTrue(v.plate.valid_format)
        # velocita' misurata coerente col moto sintetico (~104 km/h, limite 50)
        self.assertGreater(v.measured_speed_kmh, 95.0)
        self.assertLess(v.measured_speed_kmh, 120.0)
        # sanzione corretta per il superamento
        self.assertEqual(result.verbali[0].sanction.comma, "comma 9")
        self.assertEqual(result.verbali[0].sanction.points_deducted, 6)
        # pacchetto-prova MP4 scritto e verificabile
        self.assertTrue(os.path.exists(v.evidence.clip_path))
        from velocitai.recorder import verify_evidence
        self.assertTrue(verify_evidence(v.evidence))


if __name__ == "__main__":
    unittest.main()
