"""Rilevamento veicoli: interfaccia comune e backend (simulato / YOLO).

Il rilevatore trasforma un fotogramma in una lista di :class:`Detection`,
proiettando ogni veicolo in coordinate mondo tramite la calibrazione della
postazione (necessaria per stimare la velocita').
"""

from __future__ import annotations

from typing import List, Optional, Protocol

from .geometry import Calibration
from .models import Detection, BBox, Point, VehicleClass
from .scenario import SimFrame


class Detector(Protocol):
    def detect(self, frame) -> List[Detection]: ...


class SimulatedDetector:
    """Rilevatore per la modalita' scenario: legge i veicoli da un ``SimFrame``.

    Puo' simulare imperfezioni del rilevatore reale:
    - ``detection_prob`` < 1.0 -> fotogrammi in cui il veicolo non e' rilevato;
    - ``bbox_jitter`` -> rumore additivo sulla bounding box (metri/pixel).

    Con i default (prob=1, jitter=0) il comportamento e' deterministico ed esatto,
    utile per la validazione contro il ground-truth.
    """

    def __init__(self, calibration: Optional[Calibration] = None,
                 detection_prob: float = 1.0, bbox_jitter: float = 0.0) -> None:
        self.calibration = calibration or Calibration()
        self.detection_prob = detection_prob
        self.bbox_jitter = bbox_jitter
        self._seed = 2463534242

    def _rand(self) -> float:
        # xorshift32 deterministico (evita dipendenza dallo stato globale random)
        x = self._seed
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17)
        x ^= (x << 5) & 0xFFFFFFFF
        self._seed = x & 0xFFFFFFFF
        return self._seed / 0xFFFFFFFF

    def detect(self, frame: SimFrame) -> List[Detection]:
        dets: List[Detection] = []
        for vs in frame.vehicles:
            if self.detection_prob < 1.0 and self._rand() > self.detection_prob:
                continue
            bbox = vs.bbox
            if self.bbox_jitter > 0:
                j = self.bbox_jitter
                bbox = BBox(
                    bbox.x1 + (self._rand() - 0.5) * 2 * j,
                    bbox.y1 + (self._rand() - 0.5) * 2 * j,
                    bbox.x2 + (self._rand() - 0.5) * 2 * j,
                    bbox.y2 + (self._rand() - 0.5) * 2 * j,
                )
            world = self.calibration.image_to_world(bbox.center)
            dets.append(Detection(
                frame_index=frame.frame_index,
                timestamp=frame.timestamp,
                bbox=bbox,
                vehicle_class=vs.vehicle_class,
                confidence=0.99,
                world_point=world,
            ))
        return dets


class YOLODetector:  # pragma: no cover - richiede ultralytics/torch
    """Backend di produzione: Ultralytics YOLOv8 su fotogrammi reali (BGR ndarray).

    Stessa interfaccia di :class:`SimulatedDetector`. La calibrazione proietta il
    punto di contatto al suolo (centro-base bbox) nel piano strada.
    """

    VEHICLE_CLASSES = {
        2: VehicleClass.CAR, 3: VehicleClass.MOTORCYCLE,
        5: VehicleClass.BUS, 7: VehicleClass.TRUCK,
    }

    def __init__(self, calibration: Calibration, weights: str = "yolov8n.pt",
                 conf: float = 0.35) -> None:
        from ultralytics import YOLO  # errore esplicito se mancante
        self.calibration = calibration
        self.model = YOLO(weights)
        self.conf = conf

    def detect(self, frame) -> List[Detection]:  # frame: np.ndarray BGR
        raise NotImplementedError(
            "Integrazione YOLOv8: model.predict(frame) -> mappare box+classe in "
            "Detection. Vedi docs/PRODUCTION_BACKENDS.md."
        )
