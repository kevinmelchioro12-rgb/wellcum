"""Omografia: ricostruzione e proiezione immagine->mondo."""

import unittest

from velocitai.geometry import Homography, _solve_linear
from velocitai.models import Point


class TestSolver(unittest.TestCase):
    def test_solve_linear(self):
        # 2x + y = 5 ; x - y = -1  -> x=4/3? verifichiamo numericamente
        sol = _solve_linear([[2.0, 1.0], [1.0, -1.0]], [5.0, -1.0])
        x, y = sol
        self.assertAlmostEqual(2 * x + y, 5.0, places=9)
        self.assertAlmostEqual(x - y, -1.0, places=9)


class TestHomography(unittest.TestCase):
    def test_affine_recovery(self):
        # mappa affine nota: x_w = 2*x , y_w = 3*y
        img = [Point(0, 0), Point(10, 0), Point(0, 10), Point(10, 10)]
        wld = [Point(0, 0), Point(20, 0), Point(0, 30), Point(20, 30)]
        H = Homography.from_correspondences(img, wld)
        p = H.project(Point(5, 5))
        self.assertAlmostEqual(p.x, 10.0, places=6)
        self.assertAlmostEqual(p.y, 15.0, places=6)

    def test_overdetermined_least_squares(self):
        # 6 corrispondenze (sovradeterminato) coerenti con x_w=2x, y_w=3y:
        # i minimi quadrati devono comunque ricostruire la mappa esatta
        img = [Point(0, 0), Point(10, 0), Point(0, 10), Point(10, 10),
               Point(5, 0), Point(0, 5)]
        wld = [Point(0, 0), Point(20, 0), Point(0, 30), Point(20, 30),
               Point(10, 0), Point(0, 15)]
        H = Homography.from_correspondences(img, wld)
        p = H.project(Point(7, 4))
        self.assertAlmostEqual(p.x, 14.0, places=5)
        self.assertAlmostEqual(p.y, 12.0, places=5)

    def test_perspective_recovery(self):
        # corrispondenze prospettiche generiche: i 4 punti devono mappare esatto
        img = [Point(100, 200), Point(540, 210), Point(120, 460), Point(520, 470)]
        wld = [Point(0, 0), Point(3.5, 0), Point(0, 20), Point(3.5, 20)]
        H = Homography.from_correspondences(img, wld)
        for ip, wp in zip(img, wld):
            p = H.project(ip)
            self.assertAlmostEqual(p.x, wp.x, places=4)
            self.assertAlmostEqual(p.y, wp.y, places=4)


if __name__ == "__main__":
    unittest.main()
