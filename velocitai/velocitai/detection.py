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


class MotionDetector:  # pragma: no cover - richiede opencv
    """Rilevatore CLASSICO (senza ML/GPU) basato su sottrazione di sfondo MOG2.

    Adatto a postazioni fisse a basso costo o a demo: il veicolo in movimento e'
    foreground sullo sfondo statico della strada. Stessa interfaccia di
    :class:`YOLODetector` / :class:`SimulatedDetector`.
    """

    def __init__(self, calibration: Calibration, min_area: int = 1200,
                 history: int = 120, var_threshold: float = 40.0) -> None:
        import cv2
        import numpy as np
        self._cv2 = cv2
        self._np = np
        self.calibration = calibration
        self.min_area = min_area
        self._bg = cv2.createBackgroundSubtractorMOG2(
            history=history, varThreshold=var_threshold, detectShadows=False)

    def detect(self, frame) -> List[Detection]:
        cv2, np = self._cv2, self._np
        fg = self._bg.apply(frame.image)
        _, th = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
        th = cv2.morphologyEx(th, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        # CLOSE con kernel ampio: unisce le parti di uno stesso veicolo (carrozzeria,
        # parabrezza, targa) in un unico blob evitando tracce duplicate.
        th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
        th = cv2.dilate(th, np.ones((5, 5), np.uint8), iterations=2)
        contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dets: List[Detection] = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w * h < self.min_area:
                continue
            bbox = BBox(float(x), float(y), float(x + w), float(y + h))
            ground = Point(x + w / 2.0, float(y + h))   # contatto al suolo
            dets.append(Detection(
                frame_index=frame.frame_index,
                timestamp=frame.timestamp,
                bbox=bbox,
                vehicle_class=VehicleClass.CAR,
                confidence=0.9,
                world_point=self.calibration.image_to_world(ground),
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

    def detect(self, frame) -> List[Detection]:
        """Rileva i veicoli in un :class:`~velocitai.sources.VideoFrame`.

        Il punto-mondo e' il **contatto al suolo** del veicolo (centro del lato
        inferiore della bbox) proiettato dalla calibrazione: e' il punto corretto
        per misurare la posizione sul piano stradale.
        """
        results = self.model.predict(frame.image, conf=self.conf, verbose=False)
        dets: List[Detection] = []
        for res in results:
            boxes = getattr(res, "boxes", None)
            if boxes is None:
                continue
            for b in boxes:
                cls_id = int(b.cls[0])
                vclass = self.VEHICLE_CLASSES.get(cls_id)
                if vclass is None:           # non e' un veicolo
                    continue
                x1, y1, x2, y2 = (float(v) for v in b.xyxy[0])
                bbox = BBox(x1, y1, x2, y2)
                ground = Point((x1 + x2) / 2.0, y2)   # centro-base = contatto suolo
                dets.append(Detection(
                    frame_index=frame.frame_index,
                    timestamp=frame.timestamp,
                    bbox=bbox,
                    vehicle_class=vclass,
                    confidence=float(b.conf[0]),
                    world_point=self.calibration.image_to_world(ground),
                ))
        return dets
