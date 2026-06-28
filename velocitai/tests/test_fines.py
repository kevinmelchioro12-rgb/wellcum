"""Calcolo sanzionatorio Art. 142/202 CdS: tolleranza, fasce, notturno, termini."""

import unittest
from datetime import datetime, timezone, timedelta

from velocitai.config import SanctionConfig
from velocitai.fines import (
    apply_tolerance, classify, SanctionCalculator, build_verbale, SECONDS_PER_DAY,
)
from velocitai.models import (
    Violation, GeoLocation, PlateReading, SpeedMeasurement, SpeedMethod,
)


def _epoch(y, m, d, hh, mm=0, tz=2):
    return datetime(y, m, d, hh, mm, tzinfo=timezone(timedelta(hours=tz))).timestamp()


def _violation(contested, limit=50.0, ts=None, measured=None):
    ts = ts if ts is not None else _epoch(2026, 6, 24, 14, 30)
    measured = measured if measured is not None else contested
    return Violation(
        violation_id="20260624-0001",
        timestamp=ts,
        location=GeoLocation("via X", "Milano", "MI", 45.0, 9.0),
        track_id=1,
        measured_speed_kmh=measured,
        speed_limit_kmh=limit,
        plate=PlateReading("AB123CD", 0.95, valid_format=True),
        measurement=SpeedMeasurement(1, measured, SpeedMethod.LINE_PAIR,
                                     0.0, 1.0, 20.0, 1.0),
        contested_speed_kmh=contested,
    )


class TestTolerance(unittest.TestCase):
    def test_min_5kmh(self):
        cfg = SanctionConfig()
        self.assertAlmostEqual(apply_tolerance(67.0, cfg), 62.0)   # 5% = 3.35 < 5
        self.assertAlmostEqual(apply_tolerance(121.0, cfg), 114.95)  # 5% = 6.05 > 5

    def test_borderline_saved_by_tolerance(self):
        cfg = SanctionConfig()
        # 52 km/h con limite 50: dopo tolleranza 47 -> nessuna violazione
        self.assertAlmostEqual(apply_tolerance(52.0, cfg), 47.0)


class TestClassification(unittest.TestCase):
    def test_brackets(self):
        cfg = SanctionConfig()
        self.assertIsNone(classify(0.0, cfg))
        self.assertEqual(classify(8.0, cfg).name, "comma 7")
        self.assertEqual(classify(12.0, cfg).name, "comma 8")
        self.assertEqual(classify(44.0, cfg).name, "comma 9")
        self.assertEqual(classify(65.0, cfg).name, "comma 9-bis")

    def test_boundary_inclusive_upper(self):
        cfg = SanctionConfig()
        # esattamente 10 -> ancora comma 7 ; appena oltre -> comma 8
        self.assertEqual(classify(10.0, cfg).name, "comma 7")
        self.assertEqual(classify(10.0001, cfg).name, "comma 8")
        self.assertEqual(classify(40.0, cfg).name, "comma 8")
        self.assertEqual(classify(60.0, cfg).name, "comma 9")


class TestSanction(unittest.TestCase):
    def setUp(self):
        self.cfg = SanctionConfig()
        self.calc = SanctionCalculator(self.cfg, tz_offset_hours=2.0)

    def test_no_violation(self):
        self.assertIsNone(self.calc.compute_sanction(_violation(48.0)))

    def test_comma8_amounts(self):
        s = self.calc.compute_sanction(_violation(62.0))
        self.assertEqual(s.comma, "comma 8")
        self.assertEqual(s.points_deducted, 3)
        self.assertAlmostEqual(s.amount_due_eur, 173.0 + 16.5)
        self.assertAlmostEqual(s.reduced_amount_eur, 173.0 * 0.7 + 16.5)
        self.assertFalse(s.night_surcharge_applied)

    def test_comma9_suspension(self):
        s = self.calc.compute_sanction(_violation(94.0))
        self.assertEqual(s.comma, "comma 9")
        self.assertEqual(s.points_deducted, 6)
        self.assertEqual(s.suspension_months, (1, 3))

    def test_comma9bis(self):
        s = self.calc.compute_sanction(_violation(115.0))
        self.assertEqual(s.comma, "comma 9-bis")
        self.assertEqual(s.points_deducted, 10)
        self.assertEqual(s.suspension_months, (6, 12))

    def test_night_surcharge_only_for_commi_9_and_9bis(self):
        night_ts = _epoch(2026, 6, 24, 23, 30)
        # comma 8 (over +12) NON e' soggetto a maggiorazione notturna (Art.142 c.8-bis)
        c8_night = self.calc.compute_sanction(_violation(62.0, ts=night_ts))
        self.assertFalse(c8_night.night_surcharge_applied)
        self.assertAlmostEqual(c8_night.amount_min_eur, 173.0, places=2)

        # comma 9 (over +44) SI: +1/3 sul minimo edittale
        c9_day = self.calc.compute_sanction(_violation(94.0))
        c9_night = self.calc.compute_sanction(_violation(94.0, ts=night_ts))
        self.assertFalse(c9_day.night_surcharge_applied)
        self.assertTrue(c9_night.night_surcharge_applied)
        self.assertAlmostEqual(c9_night.amount_min_eur, 543.0 * (4.0 / 3.0), places=2)
        self.assertGreater(c9_night.amount_due_eur, c9_day.amount_due_eur)


class TestReducedPayment(unittest.TestCase):
    def test_one_third_of_max_when_lower_than_minimum(self):
        # fascia in cui il minimo (300) > 1/3 del massimo (600/3=200):
        # la misura ridotta deve usare 200, non 300 (Art. 202 c.1)
        from velocitai.config import SpeedBracket
        cfg = SanctionConfig()
        cfg.brackets = [SpeedBracket("test", "Art. X", 0.0, None,
                                     300.0, 600.0, 0, (0, 0))]
        calc = SanctionCalculator(cfg, 2.0)
        s = calc.compute_sanction(_violation(60.0))   # +10 sul limite 50
        self.assertAlmostEqual(s.amount_due_eur, 200.0 + cfg.notification_costs_eur)


class TestVerbale(unittest.TestCase):
    def test_deadlines(self):
        cfg = SanctionConfig()
        calc = SanctionCalculator(cfg, 2.0)
        v = _violation(62.0)
        s = calc.compute_sanction(v)
        issued = v.timestamp + 10
        verbale = build_verbale(v, None, s, issued, cfg, 2.0)
        self.assertAlmostEqual(verbale.notification_deadline,
                               v.timestamp + 90 * SECONDS_PER_DAY)
        self.assertAlmostEqual(verbale.payment_deadline,
                               issued + 60 * SECONDS_PER_DAY)
        self.assertIn("PL-", verbale.protocol_number)


if __name__ == "__main__":
    unittest.main()
