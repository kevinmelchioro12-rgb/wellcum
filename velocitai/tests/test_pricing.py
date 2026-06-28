"""Test del modello di prezzo / preventivo (docs/PRICING.md)."""

import argparse
import unittest

from velocitai.pricing import (
    compute_offer, SAAS_PER_POSTAZIONE_ANNO, SAAS_CENTRALE_ANNO,
    SAAS_SETUP_POSTAZIONE, ONPREM_EDGE, ONPREM_CENTRALE, ONPREM_CANONE_PCT,
)


class TestPricing(unittest.TestCase):
    def test_saas_single(self):
        o = compute_offer(1, "saas", anni=3)
        self.assertEqual(o.discount_pct, 0.0)
        self.assertAlmostEqual(o.recurring_year,
                               SAAS_PER_POSTAZIONE_ANNO + SAAS_CENTRALE_ANNO)
        self.assertAlmostEqual(o.one_time, SAAS_SETUP_POSTAZIONE)
        self.assertAlmostEqual(o.tco, o.one_time + o.recurring_year * 3)

    def test_saas_volume_discounts(self):
        self.assertEqual(compute_offer(4, "saas").discount_pct, 0.0)
        self.assertEqual(compute_offer(5, "saas").discount_pct, 0.10)
        self.assertEqual(compute_offer(12, "saas").discount_pct, 0.18)
        # piu' postazioni con sconto -> canone per-postazione minore
        per1 = compute_offer(1, "saas", con_centrale=False).recurring_year / 1
        per10 = compute_offer(10, "saas", con_centrale=False).recurring_year / 10
        self.assertLess(per10, per1)

    def test_onprem(self):
        o = compute_offer(1, "onprem", anni=5)
        lic = ONPREM_EDGE + ONPREM_CENTRALE
        self.assertAlmostEqual(o.recurring_year, lic * ONPREM_CANONE_PCT)
        self.assertGreater(o.one_time, lic)        # licenze + setup

    def test_ppv_minimum_applies(self):
        # pochi verbali -> scatta il minimo garantito (350*12=4200 > 1.20*1000)
        o = compute_offer(1, "ppv", verbali_anno_postazione=1000)
        self.assertAlmostEqual(o.recurring_year, 350.0 * 12)
        self.assertEqual(o.one_time, 0.0)

    def test_turnkey_recurring_positive(self):
        o = compute_offer(2, "turnkey", anni=3)
        self.assertGreater(o.recurring_year, 0)
        self.assertAlmostEqual(o.tco, o.recurring_year * 3)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            compute_offer(0, "saas")
        with self.assertRaises(ValueError):
            compute_offer(1, "inesistente")
        with self.assertRaises(ValueError):
            compute_offer(1, "saas", anni=0)


class TestQuoteCLI(unittest.TestCase):
    def test_cmd_quote_runs(self):
        from velocitai import cli
        ns = argparse.Namespace(postazioni=6, modello="saas", anni=3,
                                no_centrale=False, verbali_anno=3750)
        self.assertEqual(cli.cmd_quote(ns), 0)


if __name__ == "__main__":
    unittest.main()
