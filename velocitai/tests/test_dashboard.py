"""Test di rendering della console operatore (nessun server avviato)."""

import os
import tempfile
import shutil
import unittest

from velocitai.config import Config
from velocitai.pipeline import build_simulated_pipeline
from velocitai.scenario import default_scenario
from velocitai.dashboard import _render_dashboard, _render_verbale_page, _State

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDashboardRendering(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="dash-")
        cfg = Config()
        cfg.recorder.output_dir = os.path.join(self.tmp, "ev")
        cfg.notifier.output_dir = os.path.join(self.tmp, "vb")
        cfg.registry_path = os.path.join(PROJECT_ROOT, "data", "registry", "owners.json")
        self.cfg = cfg
        result = build_simulated_pipeline(cfg).process_frames(default_scenario().frames())
        self.state = _State()
        self.state.config = cfg
        self.state.result = result

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_dashboard_html(self):
        html = _render_dashboard(self.state)
        self.assertIn("VelociTAI", html)
        self.assertIn("Stato sistema", html)          # sezione resilienza
        self.assertIn("OPERATIVO", html)              # salute OK nello scenario
        # i protocolli dei verbali compaiono nella tabella
        for v in self.state.result.verbali:
            self.assertIn(v.protocol_number, html)

    def test_verbale_page_found_and_missing(self):
        proto = self.state.result.verbali[0].protocol_number
        page = _render_verbale_page(self.state, proto)
        self.assertIsNotNone(page)
        self.assertIn(proto, page)
        self.assertIsNone(_render_verbale_page(self.state, "INESISTENTE"))


if __name__ == "__main__":
    unittest.main()
