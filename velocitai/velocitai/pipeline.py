"""Orchestratore della pipeline di accertamento.

Flusso (elaborazione per-clip, off-line e deterministica):

    frame  ->  rilevamento  ->  tracciamento  ->  stima velocita'
           ->  (se supero limite dopo tolleranza)  ->  ANPR
           ->  registrazione prova  ->  visura intestatario
           ->  calcolo sanzione  ->  verbale  ->  notifica

La variante streaming (finestra mobile) e' descritta in docs/ARCHITECTURE.md;
qui si elabora l'intera clip per semplicita' e riproducibilita'.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from .config import Config
from .geometry import Calibration, LineGate
from .detection import SimulatedDetector
from .tracking import IoUTracker
from .speed import build_estimator
from .anpr import SimulatedANPR, PlateValidator
from .recorder import SimulatedRecorder
from .registry import OwnerRegistry
from .fines import SanctionCalculator, apply_tolerance, build_verbale
from .notifier import Notifier
from .models import (
    Violation, PlateReading, GeoLocation, Verbale, Track,
)
from .scenario import SimFrame
from .utils import get_logger, format_timestamp

log = get_logger(__name__)


@dataclass
class TrackOutcome:
    track_id: int
    plate: Optional[str]
    measured_kmh: float
    contested_kmh: float
    limit_kmh: float
    is_violation: bool
    needs_review: bool = False


@dataclass
class PipelineResult:
    violations: List[Violation] = field(default_factory=list)
    verbali: List[Verbale] = field(default_factory=list)
    dispatches: List[dict] = field(default_factory=list)
    outcomes: List[TrackOutcome] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


class EnforcementPipeline:
    def __init__(self, config: Config, detector, tracker: IoUTracker,
                 estimator, anpr, recorder, registry: Optional[OwnerRegistry],
                 calculator: SanctionCalculator, notifier: Notifier) -> None:
        self.config = config
        self.detector = detector
        self.tracker = tracker
        self.estimator = estimator
        self.anpr = anpr
        self.recorder = recorder
        self.registry = registry
        self.calculator = calculator
        self.notifier = notifier

    # -- helper ------------------------------------------------------------
    def _location(self) -> GeoLocation:
        loc = self.config.location
        return GeoLocation(
            road_name=loc.road_name, municipality=loc.municipality,
            province=loc.province, latitude=loc.latitude,
            longitude=loc.longitude, direction=loc.direction,
        )

    def _clip_for_track(self, frames: List[SimFrame], track: Track) -> List[SimFrame]:
        first = track.first.frame_index
        last = track.last.frame_index
        pre = self.config.recorder.pre_event_frames
        post = self.config.recorder.post_event_frames
        lo = max(0, first - pre)
        hi = min(len(frames) - 1, last + post)
        return frames[lo:hi + 1]

    # -- main --------------------------------------------------------------
    def process_frames(self, frames: Iterable[SimFrame]) -> PipelineResult:
        frame_list = list(frames)
        for fr in frame_list:
            dets = self.detector.detect(fr)
            self.tracker.update(dets)

        tracks = self.tracker.finalize()
        result = PipelineResult()
        limit = self.config.location.speed_limit_kmh
        issued_at = frame_list[-1].timestamp if frame_list else 0.0
        seq = 0

        for track in sorted(tracks, key=lambda t: t.track_id):
            measurement = self.estimator.estimate(track)
            if measurement is None or measurement.confidence < self.config.speed.min_confidence:
                continue
            measured = measurement.measured_speed_kmh
            contested = apply_tolerance(measured, self.config.sanction)

            if contested <= limit:
                result.outcomes.append(TrackOutcome(
                    track.track_id, None, measured, contested, limit, False))
                continue

            # --- ANPR ---
            plate = self.anpr.read(track, frame_list)
            if plate is None:
                plate = PlateReading(text="ILLEGGIBILE", confidence=0.0,
                                     valid_format=False)
            needs_review = (plate.confidence < self.config.anpr.min_confidence
                            or (self.config.anpr.require_valid_format
                                and not plate.valid_format))

            seq += 1
            vid = self._violation_id(issued_at, seq)

            violation = Violation(
                violation_id=vid,
                timestamp=measurement.t_start,
                location=self._location(),
                track_id=track.track_id,
                measured_speed_kmh=round(measured, 1),
                speed_limit_kmh=limit,
                plate=plate,
                measurement=measurement,
                device_id=self.config.device.device_id,
                contested_speed_kmh=round(contested, 1),
            )

            # --- prova ---
            clip = self._clip_for_track(frame_list, track)
            violation.evidence = self.recorder.record(vid, clip, track, plate)

            # --- intestatario ---
            owner = self.registry.lookup(plate.text) if (self.registry and plate.valid_format) else None

            # --- sanzione + verbale ---
            sanction = self.calculator.compute_sanction(violation)
            if sanction is None:
                continue
            verbale = build_verbale(violation, owner, sanction, issued_at,
                                    self.config.sanction, self.config.tz_offset_hours)
            if needs_review:
                verbale.status = "DA_VERIFICARE"
            dispatch = self.notifier.notify(verbale)

            result.violations.append(violation)
            result.verbali.append(verbale)
            result.dispatches.append(dispatch)
            result.outcomes.append(TrackOutcome(
                track.track_id, plate.text, measured, contested, limit, True, needs_review))

        result.stats = {
            "frames": len(frame_list),
            "tracks": len(tracks),
            "violations": len(result.violations),
            "compliant": sum(1 for o in result.outcomes if not o.is_violation),
            "needs_review": sum(1 for o in result.outcomes if o.needs_review),
        }
        log.info("Elaborazione completata: %s", result.stats)
        return result

    def _violation_id(self, issued_at: float, seq: int) -> str:
        day = format_timestamp(issued_at, self.config.tz_offset_hours).split(" ")[0]
        day = day.replace("/", "")
        return f"{day}-{seq:04d}"


# ---------------------------------------------------------------------------
# Factory: costruisce una pipeline in modalita' scenario (backend simulati)
# ---------------------------------------------------------------------------

def build_simulated_pipeline(config: Config,
                             anpr_error_rate: float = 0.0,
                             detection_prob: float = 1.0,
                             bbox_jitter: float = 0.0) -> EnforcementPipeline:
    calibration = Calibration()  # modalita' scenario: immagine == mondo (metri)

    gate = None
    if config.speed.method == "line_pair":
        # gate di default a meta' del tratto osservato, distanza 20 m
        gate = LineGate(entry_y=10.0, exit_y=30.0, distance_m=20.0)

    detector = SimulatedDetector(calibration, detection_prob=detection_prob,
                                 bbox_jitter=bbox_jitter)
    tracker = IoUTracker(iou_threshold=0.2, max_misses=8, min_hits=3)
    estimator = build_estimator(config.speed.method, gate,
                                config.speed.min_track_points,
                                config.speed.min_duration_s)
    validator = PlateValidator(country=config.anpr.country, autocorrect=True)
    anpr = SimulatedANPR(validator, char_error_rate=anpr_error_rate)
    recorder = SimulatedRecorder(config.recorder.output_dir, fps=config.recorder.fps,
                                 pre_frames=config.recorder.pre_event_frames,
                                 post_frames=config.recorder.post_event_frames)
    registry = None
    try:
        registry = OwnerRegistry.from_json(config.registry_path)
    except (OSError, ValueError):
        log.warning("Registro intestatari non trovato: %s", config.registry_path)
    calculator = SanctionCalculator(config.sanction, config.tz_offset_hours)
    notifier = Notifier(config)

    return EnforcementPipeline(config, detector, tracker, estimator, anpr,
                               recorder, registry, calculator, notifier)
