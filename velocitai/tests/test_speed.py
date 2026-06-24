"""La stima di velocita' deve ricostruire esattamente il ground-truth."""

import unittest

from velocitai.geometry import Calibration, LineGate
from velocitai.detection import SimulatedDetector
from velocitai.tracking import IoUTracker
from velocitai.speed import (
    WorldRegressionEstimator, LinePairEstimator, _linregress,
)
from velocitai.scenario import Scenario, SimVehicle
from velocitai.models import VehicleClass


def _track_for(vehicle: SimVehicle):
    sc = Scenario(vehicles=[vehicle], fps=25.0, duration_s=4.0, segment_length_m=40.0)
    det = SimulatedDetector(Calibration())
    tr = IoUTracker(min_hits=3)
    for fr in sc.frames():
        tr.update(det.detect(fr))
    tracks = tr.finalize()
    assert len(tracks) == 1, f"attesa 1 traccia, trovate {len(tracks)}"
    return tracks[0]


class TestLinearRegression(unittest.TestCase):
    def test_perfect_line(self):
        xs = [0, 1, 2, 3, 4]
        ys = [1, 3, 5, 7, 9]            # y = 2x + 1
        slope, intercept, r2 = _linregress(xs, ys)
        self.assertAlmostEqual(slope, 2.0, places=9)
        self.assertAlmostEqual(intercept, 1.0, places=9)
        self.assertAlmostEqual(r2, 1.0, places=9)


class TestWorldRegression(unittest.TestCase):
    def test_recovers_true_speed(self):
        for true_kmh in (30.0, 50.0, 67.0, 99.0, 121.0):
            veh = SimVehicle(1, "AB123CD", true_kmh, lane_x=10.0, entry_time=0.0)
            track = _track_for(veh)
            est = WorldRegressionEstimator(min_points=4)
            m = est.estimate(track)
            self.assertIsNotNone(m)
            self.assertAlmostEqual(m.measured_speed_kmh, true_kmh, places=4)
            self.assertGreater(m.confidence, 0.999)


class TestLinePair(unittest.TestCase):
    def test_recovers_true_speed(self):
        gate = LineGate(entry_y=10.0, exit_y=30.0, distance_m=20.0)
        for true_kmh in (40.0, 80.0, 130.0):
            veh = SimVehicle(1, "AB123CD", true_kmh, lane_x=10.0, entry_time=0.0)
            track = _track_for(veh)
            est = LinePairEstimator(gate, min_points=4)
            m = est.estimate(track)
            self.assertIsNotNone(m)
            # interpolazione lineare: ricostruzione quasi esatta
            self.assertAlmostEqual(m.measured_speed_kmh, true_kmh, delta=0.5)
            self.assertEqual(m.distance_m, 20.0)

    def test_gate_crossing_fraction(self):
        gate = LineGate(0.0, 10.0, 10.0)
        self.assertAlmostEqual(gate.crossing_fraction(8.0, 12.0, 10.0), 0.5)
        self.assertEqual(gate.crossing_fraction(0.0, 5.0, 8.0), -1.0)


if __name__ == "__main__":
    unittest.main()
