"""Registrazione del pacchetto-prova della violazione.

Per ogni violazione si conserva:
- una clip dei fotogrammi attorno all'evento (pre/post event),
- un ritaglio della targa,
- un manifest con metadati e un hash SHA-256 per la **catena di custodia**.

Il backend simulato (default) scrive un manifest JSON deterministico, cosi' che
l'intera pipeline sia eseguibile senza codec/telecamere. Il backend di
produzione (:class:`CV2Recorder`) scrive un MP4 con OpenCV.
"""

from __future__ import annotations

import os
from typing import List, Optional

from .models import EvidencePackage, Track, PlateReading
from .scenario import SimFrame
from .utils import write_json, sha256_of_files, atomic_write_text, get_logger

log = get_logger(__name__)


def verify_evidence(evidence: EvidencePackage) -> bool:
    """Verifica la catena di custodia: ricalcola l'hash dei file e lo confronta.

    Ritorna ``True`` se la prova e' integra. Usata dal self-check operativo per
    individuare prove mancanti, troncate o manomesse prima di portarle in
    giudizio.
    """
    if not evidence or not evidence.clip_path or not evidence.sha256:
        return False
    files = [evidence.clip_path]
    if evidence.plate_crop_path:
        files.append(evidence.plate_crop_path)
    if not all(os.path.exists(p) for p in files):
        return False
    return sha256_of_files(files) == evidence.sha256


class SimulatedRecorder:
    """Scrive il pacchetto-prova come manifest JSON (modalita' scenario)."""

    def __init__(self, output_dir: str, fps: float = 25.0,
                 pre_frames: int = 30, post_frames: int = 30) -> None:
        self.output_dir = output_dir
        self.fps = fps
        self.pre_frames = pre_frames
        self.post_frames = post_frames

    def record(self, violation_id: str, frames: List[SimFrame],
               track: Track, plate: Optional[PlateReading]) -> EvidencePackage:
        out = os.path.join(self.output_dir, violation_id)
        os.makedirs(out, exist_ok=True)

        manifest = {
            "violation_id": violation_id,
            "track_id": track.track_id,
            "plate": plate.text if plate else None,
            "fps": self.fps,
            "frame_count": len(frames),
            "frames": [
                {
                    "frame_index": f.frame_index,
                    "timestamp": f.timestamp,
                    "vehicles": [
                        {
                            "bbox": [round(v.bbox.x1, 3), round(v.bbox.y1, 3),
                                     round(v.bbox.x2, 3), round(v.bbox.y2, 3)],
                            "plate": v.plate,
                        }
                        for v in f.vehicles
                    ],
                }
                for f in frames
            ],
        }
        clip_path = os.path.join(out, "clip_manifest.json")
        write_json(clip_path, manifest)

        plate_crop_path = None
        if plate is not None:
            plate_crop_path = os.path.join(out, "plate.txt")
            atomic_write_text(plate_crop_path, plate.text + "\n")

        # L'hash di integrita' e' calcolato sui file della prova e salvato in un
        # file SEPARATO: incorporarlo nel manifest lo renderebbe non verificabile
        # (l'hash cambierebbe il contenuto che esso stesso certifica).
        files = [clip_path] + ([plate_crop_path] if plate_crop_path else [])
        digest = sha256_of_files(files)
        atomic_write_text(
            os.path.join(out, "evidence.sha256"),
            "".join(f"{digest}  {os.path.basename(p)}\n" for p in sorted(files)))

        return EvidencePackage(
            clip_path=clip_path,
            frame_paths=[],
            plate_crop_path=plate_crop_path,
            sha256=digest,
            frame_count=len(frames),
        )


class CV2Recorder:  # pragma: no cover - richiede opencv
    """Backend di produzione: scrive un MP4 con i fotogrammi reali (ndarray BGR)."""

    def __init__(self, output_dir: str, fps: float = 25.0) -> None:
        import cv2  # noqa: F401
        self.output_dir = output_dir
        self.fps = fps

    def record(self, violation_id: str, frames: list, track: Track,
               plate: Optional[PlateReading]) -> EvidencePackage:
        raise NotImplementedError(
            "Scrittura MP4 con cv2.VideoWriter + ritaglio targa. "
            "Vedi docs/PRODUCTION_BACKENDS.md."
        )
