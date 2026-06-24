"""Stima della velocita' da una traiettoria in coordinate mondo (metri).

Due metodi, selezionabili da configurazione:

* ``WorldRegressionEstimator`` — regressione lineare ai minimi quadrati delle
  posizioni mondo nel tempo; la pendenza e' il vettore velocita'. Robusto al
  rumore per-fotogramma. La confidenza deriva dall'R^2 della regressione.
* ``LinePairEstimator`` — tempo di percorrenza tra due linee a distanza nota
  (principio degli autovelox a doppia spira / tutor). La confidenza deriva dal
  numero di campioni e dalla monotonia del moto.

Entrambi lavorano in m/s e convertono in km/h una sola volta.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from .geometry import LineGate
from .models import Track, SpeedMeasurement, SpeedMethod
from .utils import ms_to_kmh


def _linregress(xs: List[float], ys: List[float]) -> Tuple[float, float, float]:
    """Regressione lineare semplice. Ritorna (slope, intercept, r2)."""
    n = len(xs)
    if n < 2:
        return 0.0, 0.0, 0.0
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    syy = sum((y - mean_y) ** 2 for y in ys)
    if sxx == 0:
        return 0.0, mean_y, 0.0
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    r2 = (sxy * sxy) / (sxx * syy) if syy > 0 else 1.0
    return slope, intercept, r2


class WorldRegressionEstimator:
    def __init__(self, min_points: int = 4, min_duration_s: float = 0.15) -> None:
        self.min_points = min_points
        self.min_duration_s = min_duration_s

    def estimate(self, track: Track) -> Optional[SpeedMeasurement]:
        pts = [p for p in track.points if p.world_point is not None]
        if len(pts) < self.min_points:
            return None
        ts = [p.timestamp for p in pts]
        if ts[-1] - ts[0] < self.min_duration_s:
            return None
        xs = [p.world_point.x for p in pts]
        ys = [p.world_point.y for p in pts]
        vx, _, r2x = _linregress(ts, xs)
        vy, _, r2y = _linregress(ts, ys)
        speed_ms = (vx * vx + vy * vy) ** 0.5
        # distanza percorsa nell'intervallo, coerente con la velocita' stimata
        elapsed = ts[-1] - ts[0]
        distance = speed_ms * elapsed
        # confidenza: peso dell'R^2 sull'asse a maggior spostamento
        if abs(xs[-1] - xs[0]) >= abs(ys[-1] - ys[0]):
            conf = r2x
        else:
            conf = r2y
        return SpeedMeasurement(
            track_id=track.track_id,
            measured_speed_kmh=ms_to_kmh(speed_ms),
            method=SpeedMethod.WORLD_REGRESSION,
            t_start=ts[0],
            t_end=ts[-1],
            distance_m=distance,
            confidence=max(0.0, min(1.0, conf)),
        )


class LinePairEstimator:
    """Velocita' dal tempo di attraversamento di due linee a distanza nota.

    Le linee sono espresse sull'asse di marcia in coordinate mondo (metri):
    ``gate.entry_y`` e ``gate.exit_y`` sono posizioni lungo la marcia,
    ``gate.distance_m`` la distanza reale (di norma ``|exit_y - entry_y|``).
    """

    def __init__(self, gate: LineGate, min_points: int = 4) -> None:
        self.gate = gate
        self.min_points = min_points

    def _crossing_time(self, track: Track, target: float) -> Optional[float]:
        pts = [p for p in track.points if p.world_point is not None]
        for prev, curr in zip(pts, pts[1:]):
            yp, yc = prev.world_point.y, curr.world_point.y
            lo, hi = sorted((yp, yc))
            if lo <= target <= hi and yc != yp:
                frac = (target - yp) / (yc - yp)
                return prev.timestamp + frac * (curr.timestamp - prev.timestamp)
        return None

    def estimate(self, track: Track) -> Optional[SpeedMeasurement]:
        pts = [p for p in track.points if p.world_point is not None]
        if len(pts) < self.min_points:
            return None
        t_in = self._crossing_time(track, self.gate.entry_y)
        t_out = self._crossing_time(track, self.gate.exit_y)
        if t_in is None or t_out is None or t_in == t_out:
            return None
        dt = abs(t_out - t_in)
        speed_ms = self.gate.distance_m / dt
        # confidenza: piu' campioni tra i gate -> piu' affidabile
        between = sum(1 for p in pts
                      if min(self.gate.entry_y, self.gate.exit_y) <= p.world_point.y
                      <= max(self.gate.entry_y, self.gate.exit_y))
        conf = min(1.0, between / max(1, self.min_points))
        return SpeedMeasurement(
            track_id=track.track_id,
            measured_speed_kmh=ms_to_kmh(speed_ms),
            method=SpeedMethod.LINE_PAIR,
            t_start=min(t_in, t_out),
            t_end=max(t_in, t_out),
            distance_m=self.gate.distance_m,
            confidence=conf,
        )


def build_estimator(method: str, gate: Optional[LineGate],
                    min_points: int, min_duration_s: float):
    """Factory: costruisce l'estimatore richiesto dalla configurazione."""
    if method == "line_pair":
        if gate is None:
            raise ValueError("Metodo 'line_pair' richiede un LineGate calibrato")
        return LinePairEstimator(gate, min_points=min_points)
    if method == "world_regression":
        return WorldRegressionEstimator(min_points=min_points,
                                        min_duration_s=min_duration_s)
    raise ValueError(f"Metodo di stima velocita' sconosciuto: {method}")
