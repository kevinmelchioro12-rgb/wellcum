"""Il tracker mantiene identita' stabili e archivia le tracce concluse."""

import unittest

from velocitai.geometry import Calibration
from velocitai.detection import SimulatedDetector
from velocitai.tracking import IoUTracker
from velocitai.scenario import Scenario, SimVehicle


class TestTracking(unittest.TestCase):
    def test_distinct_lanes_distinct_tracks(self):
        sc = Scenario(
            vehicles=[
                SimVehicle(1, "AB123CD", 60.0, lane_x=10.0, entry_time=0.0),
                SimVehicle(2, "EF456GH", 80.0, lane_x=25.0, entry_time=0.0),
            ],
            fps=25.0, duration_s=4.0, segment_length_m=40.0,
        )
        det = SimulatedDetector(Calibration())
        tr = IoUTracker(min_hits=3)
        for fr in sc.frames():
            tr.update(det.detect(fr))
        tracks = tr.finalize()
        self.assertEqual(len(tracks), 2)

    def test_single_vehicle_one_track_many_points(self):
        sc = Scenario(vehicles=[SimVehicle(1, "AB123CD", 50.0, 10.0, 0.0)],
                      fps=25.0, duration_s=4.0)
        det = SimulatedDetector(Calibration())
        tr = IoUTracker(min_hits=3)
        for fr in sc.frames():
            tr.update(det.detect(fr))
        tracks = tr.finalize()
        self.assertEqual(len(tracks), 1)
        self.assertGreaterEqual(len(tracks[0].points), 10)

    def test_archived_after_leaving_scene(self):
        # veicolo veloce: esce di scena ben prima della fine clip
        sc = Scenario(vehicles=[SimVehicle(1, "AB123CD", 200.0, 10.0, 0.0)],
                      fps=25.0, duration_s=4.0, segment_length_m=40.0)
        det = SimulatedDetector(Calibration())
        tr = IoUTracker(min_hits=3, max_misses=5)
        for fr in sc.frames():
            tr.update(det.detect(fr))
        # la traccia non e' piu' "viva" ma deve comparire in finalize (archiviata)
        self.assertEqual(len(tr.finalize()), 1)


if __name__ == "__main__":
    unittest.main()
