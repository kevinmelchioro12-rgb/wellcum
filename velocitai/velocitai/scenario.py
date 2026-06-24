"""Scenario sintetico con verita' di riferimento (ground-truth).

Permette di eseguire e validare l'INTERA pipeline senza telecamere reali ne'
modelli ML: si definiscono veicoli con velocita' e targa note, lo scenario
genera i fotogrammi (``SimFrame``) e i backend "simulati" leggono da questi.

Convenzioni geometriche (modalita' scenario, senza calibrazione prospettica):
- l'asse Y mondo coincide con la direzione di marcia, in METRI;
- coordinate immagine == coordinate mondo (1 px = 1 m), cosi' la stima di
  velocita' e' verificabile esattamente contro il ground-truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, List

from .models import Point, BBox, VehicleClass
from .utils import kmh_to_ms

# Istante di partenza di default: 24/06/2026 14:30:00 ora legale (CEST, UTC+2).
DEFAULT_START_TS = 1782304200.0


@dataclass
class SimVehicleState:
    """Stato istantaneo di un veicolo simulato in un fotogramma."""
    vehicle_id: int
    plate: str
    world_point: Point
    bbox: BBox
    vehicle_class: VehicleClass
    speed_kmh: float


@dataclass
class SimFrame:
    frame_index: int
    timestamp: float
    vehicles: List[SimVehicleState]
    width: float = 60.0
    height: float = 50.0


@dataclass
class SimVehicle:
    """Veicolo simulato a moto uniforme lungo la corsia ``lane_x``."""
    vehicle_id: int
    plate: str
    speed_kmh: float
    lane_x: float              # posizione laterale (metri)
    entry_time: float          # istante (s, relativo allo start) di ingresso a y=0
    vehicle_class: VehicleClass = VehicleClass.CAR
    length_m: float = 4.5
    width_m: float = 2.0

    def position_y(self, t_rel: float) -> float:
        return kmh_to_ms(self.speed_kmh) * (t_rel - self.entry_time)

    def state_at(self, t_rel: float) -> SimVehicleState:
        y = self.position_y(t_rel)
        cx, cy = self.lane_x, y
        bbox = BBox(cx - self.width_m / 2, cy - self.length_m / 2,
                    cx + self.width_m / 2, cy + self.length_m / 2)
        return SimVehicleState(
            vehicle_id=self.vehicle_id,
            plate=self.plate,
            world_point=Point(cx, cy),
            bbox=bbox,
            vehicle_class=self.vehicle_class,
            speed_kmh=self.speed_kmh,
        )


@dataclass
class Scenario:
    """Generatore di fotogrammi a partire da un insieme di veicoli."""
    vehicles: List[SimVehicle]
    fps: float = 25.0
    duration_s: float = 6.0
    segment_length_m: float = 40.0          # tratto osservato lungo Y
    start_timestamp: float = DEFAULT_START_TS

    def frames(self) -> Iterator[SimFrame]:
        n = int(round(self.fps * self.duration_s))
        for i in range(n):
            t_rel = i / self.fps
            ts = self.start_timestamp + t_rel
            states: List[SimVehicleState] = []
            for v in self.vehicles:
                y = v.position_y(t_rel)
                if 0.0 <= y <= self.segment_length_m:
                    states.append(v.state_at(t_rel))
            yield SimFrame(frame_index=i, timestamp=ts, vehicles=states)

    def ground_truth(self) -> dict:
        """Mappa targa -> velocita' reale (km/h), per validazione nei test."""
        return {v.plate: v.speed_kmh for v in self.vehicles}


def default_scenario() -> Scenario:
    """Scenario dimostrativo: limite 50 km/h, mix di conformi e in violazione.

    - EB512FG   48 km/h -> conforme (sotto limite)
    - FH983KL   67 km/h -> +12 dopo tolleranza  -> Art. 142 comma 8
    - GA419LM   99 km/h -> +44 dopo tolleranza  -> Art. 142 comma 9
    - DZ704XP  121 km/h -> +65 dopo tolleranza  -> Art. 142 comma 9-bis
    - JB256RT   52 km/h -> conforme dopo abbattimento tolleranza (47 km/h)
    """
    vehicles = [
        SimVehicle(1, "EB512FG", 48.0, lane_x=10.0, entry_time=0.2),    # conforme
        SimVehicle(2, "FH983KL", 67.0, lane_x=20.0, entry_time=0.0),    # +17 -> comma 8
        SimVehicle(3, "GA419LM", 99.0, lane_x=30.0, entry_time=0.4,
                   vehicle_class=VehicleClass.CAR),                       # +49 -> comma 9
        SimVehicle(4, "DZ704XP", 121.0, lane_x=40.0, entry_time=0.1),    # +71 -> comma 9-bis
        SimVehicle(5, "JB256RT", 52.0, lane_x=50.0, entry_time=0.3),     # conforme dopo tolleranza
    ]
    return Scenario(vehicles=vehicles, fps=25.0, duration_s=8.0,
                    segment_length_m=40.0)
