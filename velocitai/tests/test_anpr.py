"""Validazione formato targa italiana, correzione OCR e backend simulato."""

import unittest

from velocitai.anpr import (
    normalize_plate, is_valid_italian_plate, correct_plate, PlateValidator,
    SimulatedANPR,
)
from velocitai.scenario import Scenario, SimVehicle
from velocitai.geometry import Calibration
from velocitai.detection import SimulatedDetector
from velocitai.tracking import IoUTracker


class TestPlateFormat(unittest.TestCase):
    def test_valid_plates(self):
        for p in ("EB512FG", "FH983KL", "GA419LM", "DZ704XP", "AA000BB"):
            self.assertTrue(is_valid_italian_plate(p), p)

    def test_invalid_letters_excluded(self):
        # I, O, Q, U non sono ammesse nelle posizioni-lettera
        for p in ("IB512FG", "OB512FG", "QB512FG", "UB512FG", "EB512FI"):
            self.assertFalse(is_valid_italian_plate(p), p)

    def test_wrong_structure(self):
        for p in ("ABC123D", "1B512FG", "EB5123F", "EB12FGH", ""):
            self.assertFalse(is_valid_italian_plate(p), p)

    def test_normalize(self):
        self.assertEqual(normalize_plate(" eb 512-fg "), "EB512FG")


class TestCorrection(unittest.TestCase):
    def test_digit_in_letter_slot(self):
        # 5 nello slot-lettera -> S ; targa ricostruita valida
        self.assertEqual(correct_plate("EB512F5"), "EB512FS")

    def test_letter_in_digit_slot(self):
        # O nello slot-cifra -> 0
        self.assertEqual(correct_plate("EBO12FG"), "EB012FG")

    def test_validator_autocorrects(self):
        v = PlateValidator(country="IT", autocorrect=True)
        r = v.validate("EBO12FG", confidence=0.9)
        self.assertEqual(r.text, "EB012FG")
        self.assertTrue(r.valid_format)
        self.assertLess(r.confidence, 0.9)   # penalita' per correzione


class TestSimulatedANPR(unittest.TestCase):
    def _track(self, plate):
        sc = Scenario(vehicles=[SimVehicle(1, plate, 70.0, 10.0, 0.0)],
                      fps=25.0, duration_s=3.0)
        frames = list(sc.frames())
        det = SimulatedDetector(Calibration())
        tr = IoUTracker(min_hits=3)
        for fr in frames:
            tr.update(det.detect(fr))
        return tr.finalize()[0], frames

    def test_reads_exact_plate(self):
        track, frames = self._track("GA419LM")
        anpr = SimulatedANPR(PlateValidator(), char_error_rate=0.0)
        r = anpr.read(track, frames)
        self.assertEqual(r.text, "GA419LM")
        self.assertTrue(r.valid_format)


if __name__ == "__main__":
    unittest.main()
