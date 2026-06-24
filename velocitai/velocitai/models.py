"""Core data models for the VelociTAI traffic-enforcement pipeline.

Tutti i modelli del dominio sono ``dataclass`` di sola libreria standard, in modo
che l'intero sistema giri end-to-end senza dipendenze pesanti (numpy/OpenCV/torch).
I backend di produzione (YOLO, EasyOCR, ...) popolano questi stessi oggetti.

Le grandezze sono in unita' SI dove non diversamente indicato:
- distanze in metri (``_m``)
- velocita' in km/h (``_kmh``) per i campi esposti all'operatore/verbale,
  internamente la stima lavora in m/s e converte una sola volta.
- tempi come timestamp UNIX in secondi (float).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any


# ---------------------------------------------------------------------------
# Geometria di base
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Point:
    """Punto 2D. In coordinate immagine (pixel) o mondo (metri) a seconda dell'uso."""
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def as_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass(frozen=True)
class BBox:
    """Bounding box assi-allineato in coordinate immagine (pixel)."""
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        return max(0.0, self.width) * max(0.0, self.height)

    @property
    def center(self) -> Point:
        return Point((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)

    def iou(self, other: "BBox") -> float:
        """Intersection-over-Union, usata dal tracker per l'associazione."""
        ix1 = max(self.x1, other.x1)
        iy1 = max(self.y1, other.y1)
        ix2 = min(self.x2, other.x2)
        iy2 = min(self.y2, other.y2)
        iw = max(0.0, ix2 - ix1)
        ih = max(0.0, iy2 - iy1)
        inter = iw * ih
        union = self.area + other.area - inter
        return inter / union if union > 0 else 0.0


# ---------------------------------------------------------------------------
# Rilevamento e tracciamento
# ---------------------------------------------------------------------------

class VehicleClass(str, Enum):
    CAR = "car"
    TRUCK = "truck"
    BUS = "bus"
    MOTORCYCLE = "motorcycle"
    VAN = "van"
    UNKNOWN = "unknown"


@dataclass
class Detection:
    """Un veicolo rilevato in un singolo fotogramma."""
    frame_index: int
    timestamp: float
    bbox: BBox
    vehicle_class: VehicleClass = VehicleClass.CAR
    confidence: float = 1.0
    # Coordinate mondo (metri) del punto di contatto al suolo, se calibrate.
    world_point: Optional[Point] = None


@dataclass
class TrackPoint:
    """Osservazione di un track in un istante."""
    frame_index: int
    timestamp: float
    bbox: BBox
    world_point: Optional[Point] = None


@dataclass
class Track:
    """Traiettoria di un singolo veicolo nel tempo (id stabile tra i fotogrammi)."""
    track_id: int
    vehicle_class: VehicleClass = VehicleClass.CAR
    points: List[TrackPoint] = field(default_factory=list)
    # numero di fotogrammi consecutivi senza match (gestione occlusioni)
    misses: int = 0
    confirmed: bool = False

    @property
    def last(self) -> TrackPoint:
        return self.points[-1]

    @property
    def first(self) -> TrackPoint:
        return self.points[0]

    @property
    def duration(self) -> float:
        if len(self.points) < 2:
            return 0.0
        return self.points[-1].timestamp - self.points[0].timestamp

    def add(self, p: TrackPoint) -> None:
        self.points.append(p)
        self.misses = 0


# ---------------------------------------------------------------------------
# Stima velocita'
# ---------------------------------------------------------------------------

class SpeedMethod(str, Enum):
    # Tempo di percorrenza tra due linee virtuali a distanza nota (analogo
    # al funzionamento degli autovelox a doppia spira / "tutor").
    LINE_PAIR = "line_pair"
    # Regressione sullo spostamento in coordinate mondo (omografia).
    WORLD_REGRESSION = "world_regression"


@dataclass
class SpeedMeasurement:
    """Misura di velocita' associata a un track."""
    track_id: int
    measured_speed_kmh: float
    method: SpeedMethod
    t_start: float
    t_end: float
    distance_m: float
    confidence: float = 1.0

    @property
    def elapsed_s(self) -> float:
        return self.t_end - self.t_start


# ---------------------------------------------------------------------------
# ANPR (riconoscimento targa)
# ---------------------------------------------------------------------------

@dataclass
class PlateReading:
    """Lettura di una targa. ``text`` e' normalizzato (maiuscolo, senza spazi)."""
    text: str
    confidence: float
    raw_text: str = ""
    valid_format: bool = False
    bbox: Optional[BBox] = None
    country: str = "IT"


# ---------------------------------------------------------------------------
# Violazione + prova
# ---------------------------------------------------------------------------

@dataclass
class GeoLocation:
    road_name: str
    municipality: str
    province: str          # sigla, es. "MI"
    latitude: float
    longitude: float
    direction: str = ""    # es. "Nord", "carreggiata A->B"


@dataclass
class EvidencePackage:
    """Pacchetto-prova immutabile a corredo della violazione."""
    clip_path: Optional[str] = None          # video/manifest della clip
    frame_paths: List[str] = field(default_factory=list)
    plate_crop_path: Optional[str] = None
    sha256: Optional[str] = None             # hash di integrita' del pacchetto
    frame_count: int = 0


@dataclass
class Violation:
    """Una violazione di velocita' accertata."""
    violation_id: str
    timestamp: float                # istante dell'accertamento
    location: GeoLocation
    track_id: int
    measured_speed_kmh: float
    speed_limit_kmh: float
    plate: PlateReading
    measurement: SpeedMeasurement
    evidence: EvidencePackage = field(default_factory=EvidencePackage)
    device_id: str = ""
    # velocita' contestabile dopo abbattimento tolleranza di legge (km/h)
    contested_speed_kmh: float = 0.0

    @property
    def overspeed_kmh(self) -> float:
        return max(0.0, self.contested_speed_kmh - self.speed_limit_kmh)


# ---------------------------------------------------------------------------
# Intestatario veicolo
# ---------------------------------------------------------------------------

@dataclass
class OwnerRecord:
    """Intestatario del veicolo (dato che in produzione arriva da PRA/Motorizzazione)."""
    plate: str
    full_name: str
    fiscal_code: str
    address: str
    municipality: str
    province: str
    postal_code: str
    vehicle_make: str = ""
    vehicle_model: str = ""
    pec_email: str = ""


# ---------------------------------------------------------------------------
# Verbale (sanzione)
# ---------------------------------------------------------------------------

@dataclass
class Sanction:
    """Esito sanzionatorio calcolato a norma di legge (Art. 142 CdS)."""
    articolo: str                 # es. "Art. 142 comma 8 CdS"
    comma: str
    amount_min_eur: float
    amount_max_eur: float
    amount_due_eur: float         # importo edittale applicato
    reduced_amount_eur: float     # pagamento in misura ridotta (Art. 202 CdS)
    points_deducted: int          # decurtazione punti patente
    suspension_months: Tuple[int, int] = (0, 0)   # (min, max) sospensione patente
    night_surcharge_applied: bool = False
    notes: str = ""


@dataclass
class Verbale:
    """Verbale di contestazione/notificazione completo, pronto per la notifica."""
    protocol_number: str
    violation: Violation
    owner: Optional[OwnerRecord]
    sanction: Sanction
    issued_at: float
    notification_deadline: float  # termine di 90 gg per la notifica (Art. 201 CdS)
    payment_deadline: float       # termine di 60 gg per il pagamento (Art. 203 CdS)
    status: str = "DRAFT"         # DRAFT -> ISSUED -> NOTIFIED -> PAID/CONTESTED

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
