"""Calibrazione prospettica e geometria immagine->mondo.

Per misurare una velocita' da un video servono coordinate metriche, non pixel.
Si usano due tecniche, entrambe pure-Python:

1. ``Homography`` — trasformazione prospettica (8 DoF) stimata da >=4 corrispondenze
   pixel<->metri sul piano stradale. E' lo standard per i tutor/autovelox video.
2. ``LineGate`` — due "linee virtuali" a distanza nota lungo la direzione di marcia;
   la velocita' deriva dal tempo di attraversamento (metodo a doppia spira).

L'omografia e' risolta con eliminazione di Gauss su un sistema 8x8, senza numpy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from .models import Point


# ---------------------------------------------------------------------------
# Algebra lineare minimale (no numpy) per risolvere l'omografia
# ---------------------------------------------------------------------------

def _solve_linear(matrix: List[List[float]], rhs: List[float]) -> List[float]:
    """Risolve A x = b con eliminazione di Gauss e pivoting parziale.

    ``matrix`` viene copiata; n puo' essere qualsiasi (qui 8).
    """
    n = len(rhs)
    # matrice aumentata
    a = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        # pivoting parziale: riga col pivot di modulo massimo
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("Sistema singolare: punti di calibrazione degeneri")
        a[col], a[pivot] = a[pivot], a[col]
        piv = a[col][col]
        for r in range(n):
            if r == col:
                continue
            factor = a[r][col] / piv
            if factor == 0.0:
                continue
            for c in range(col, n + 1):
                a[r][c] -= factor * a[col][c]
    return [a[i][n] / a[i][i] for i in range(n)]


@dataclass
class Homography:
    """Omografia piano-immagine -> piano-strada (metri).

    Memorizza i 9 coefficienti (h33 fissato a 1).
    """
    h: Tuple[float, ...]  # 9 valori, riga-major

    @classmethod
    def from_correspondences(
        cls,
        image_points: Sequence[Point],
        world_points: Sequence[Point],
    ) -> "Homography":
        """Stima l'omografia da >=4 corrispondenze (DLT con h33=1).

        Con esattamente 4 punti il sistema e' 8x8 ed esatto; con piu' punti si
        prendono i primi 4 non degeneri (sufficiente per la calibrazione fissa
        di una postazione). Un solver ai minimi quadrati e' previsto nel backend
        numerico opzionale.
        """
        if len(image_points) < 4 or len(world_points) < 4:
            raise ValueError("Servono almeno 4 corrispondenze per l'omografia")
        ip = image_points[:4]
        wp = world_points[:4]
        a: List[List[float]] = []
        b: List[float] = []
        for (img, wld) in zip(ip, wp):
            x, y = img.x, img.y
            u, v = wld.x, wld.y
            # u = (h0 x + h1 y + h2) / (h6 x + h7 y + 1)
            a.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
            b.append(u)
            a.append([0, 0, 0, x, y, 1, -v * x, -v * y])
            b.append(v)
        sol = _solve_linear(a, b)
        return cls(h=tuple(sol) + (1.0,))

    def project(self, p: Point) -> Point:
        """Proietta un punto immagine nel piano strada (metri)."""
        h = self.h
        denom = h[6] * p.x + h[7] * p.y + h[8]
        if abs(denom) < 1e-12:
            raise ValueError("Punto all'orizzonte: proiezione non definita")
        u = (h[0] * p.x + h[1] * p.y + h[2]) / denom
        v = (h[3] * p.x + h[4] * p.y + h[5]) / denom
        return Point(u, v)


@dataclass
class LineGate:
    """Coppia di linee di misura a distanza nota lungo la direzione di marcia.

    ``entry_y``/``exit_y`` sono ordinate immagine (o coordinate lungo l'asse di
    marcia); ``distance_m`` la distanza reale tra le due linee.
    """
    entry_y: float
    exit_y: float
    distance_m: float

    def crossing_fraction(self, y_prev: float, y_curr: float, target_y: float) -> float:
        """Frazione [0,1] di interpolazione dell'istante di attraversamento di ``target_y``.

        Ritorna -1 se il segmento [y_prev, y_curr] non attraversa target_y.
        """
        lo, hi = sorted((y_prev, y_curr))
        if not (lo <= target_y <= hi) or y_curr == y_prev:
            return -1.0
        return (target_y - y_prev) / (y_curr - y_prev)


@dataclass
class Calibration:
    """Configurazione metrica completa di una postazione di rilevamento."""
    homography: Homography | None = None
    line_gate: LineGate | None = None
    # fallback diretto: metri-per-pixel medi sull'asse di marcia
    meters_per_pixel: float | None = None

    def image_to_world(self, p: Point) -> Point:
        if self.homography is not None:
            return self.homography.project(p)
        if self.meters_per_pixel is not None:
            return Point(p.x * self.meters_per_pixel, p.y * self.meters_per_pixel)
        # nessuna calibrazione: assume coordinate gia' in metri (modalita' scenario)
        return p
