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
from .utils import write_json, atomic_write_text, get_logger
from .security import (
    safe_path_component, secure_join, keyed_digest_of_files, digest_algo,
    set_secure_permissions, constant_time_equals,
)

log = get_logger(__name__)


def verify_evidence(evidence: EvidencePackage, key: Optional[bytes] = None) -> bool:
    """Verifica la catena di custodia: ricalcola il digest e lo confronta.

    Ritorna ``True`` se la prova e' integra. Per le prove firmate con HMAC
    (``digest_algo == 'hmac-sha256'``) e' necessaria la stessa ``key`` usata in
    registrazione: senza la chiave la verifica fallisce in modo sicuro (una prova
    manomessa non puo' superare il controllo, ne' essere forgiata da chi non ha
    il segreto). Il confronto e' a tempo costante.
    """
    if not evidence or not evidence.clip_path or not evidence.sha256:
        return False
    files = [evidence.clip_path]
    if evidence.plate_crop_path:
        files.append(evidence.plate_crop_path)
    if not all(os.path.exists(p) for p in files):
        return False
    # se la prova e' firmata HMAC ma non abbiamo la chiave, fallisce in sicurezza
    if (evidence.digest_algo or "sha256") == "hmac-sha256" and key is None:
        return False
    use_key = key if (evidence.digest_algo or "sha256") == "hmac-sha256" else None
    return constant_time_equals(keyed_digest_of_files(files, use_key), evidence.sha256)


class SimulatedRecorder:
    """Scrive il pacchetto-prova come manifest JSON (modalita' scenario)."""

    def __init__(self, output_dir: str, fps: float = 25.0,
                 pre_frames: int = 30, post_frames: int = 30,
                 signing_key: Optional[bytes] = None) -> None:
        self.output_dir = output_dir
        self.fps = fps
        self.pre_frames = pre_frames
        self.post_frames = post_frames
        # chiave per la firma HMAC della catena di custodia (None = SHA-256)
        self.signing_key = signing_key

    def record(self, violation_id: str, frames: List[SimFrame],
               track: Track, plate: Optional[PlateReading]) -> EvidencePackage:
        # SICUREZZA: il violation_id finisce in un path -> sanitizzato contro
        # path traversal e il join e' confinato dentro output_dir.
        out = secure_join(self.output_dir, safe_path_component(
            violation_id, field="violation_id"))
        os.makedirs(out, exist_ok=True)
        set_secure_permissions(out)

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
        set_secure_permissions(clip_path)

        plate_crop_path = None
        if plate is not None:
            plate_crop_path = os.path.join(out, "plate.txt")
            atomic_write_text(plate_crop_path, plate.text + "\n")
            set_secure_permissions(plate_crop_path)

        # Catena di custodia: digest dei file della prova, salvato in un file
        # SEPARATO (incorporarlo nel manifest lo renderebbe non verificabile).
        # Con una chiave segreta si usa HMAC -> non falsificabile da chi puo'
        # scrivere i file ma non possiede la chiave.
        files = [clip_path] + ([plate_crop_path] if plate_crop_path else [])
        digest = keyed_digest_of_files(files, self.signing_key)
        algo = digest_algo(self.signing_key)
        sha_path = os.path.join(out, "evidence.sha256")
        atomic_write_text(
            sha_path,
            f"# algo={algo}\n" +
            "".join(f"{digest}  {os.path.basename(p)}\n" for p in sorted(files)))
        set_secure_permissions(sha_path)

        return EvidencePackage(
            clip_path=clip_path,
            frame_paths=[],
            plate_crop_path=plate_crop_path,
            sha256=digest,
            frame_count=len(frames),
            digest_algo=algo,
        )


class CV2Recorder:  # pragma: no cover - richiede opencv
    """Backend di produzione: scrive un MP4 con i fotogrammi reali (ndarray BGR).

    Mantiene la STESSA catena di custodia del backend simulato (digest HMAC se la
    chiave e' presente, scritture e permessi sicuri).
    """

    def __init__(self, output_dir: str, fps: float = 25.0,
                 signing_key: Optional[bytes] = None) -> None:
        import cv2  # noqa: F401  (errore esplicito se OpenCV manca)
        self._cv2 = cv2
        self.output_dir = output_dir
        self.fps = fps
        self.signing_key = signing_key

    def record(self, violation_id: str, frames: list, track: Track,
               plate: Optional[PlateReading]) -> EvidencePackage:
        cv2 = self._cv2
        out = secure_join(self.output_dir, safe_path_component(
            violation_id, field="violation_id"))
        os.makedirs(out, exist_ok=True)
        set_secure_permissions(out)

        if not frames:
            raise ValueError("Nessun fotogramma da registrare")
        h, w = frames[0].image.shape[:2]
        clip_path = os.path.join(out, "clip.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(clip_path, fourcc, self.fps, (w, h))
        try:
            for fr in frames:
                writer.write(fr.image)
        finally:
            writer.release()
        set_secure_permissions(clip_path)

        # ritaglio targa dal fotogramma con bbox piu' grande
        plate_crop_path = None
        if track.points:
            best = max(track.points, key=lambda p: p.bbox.area)
            frame = next((f for f in frames
                          if getattr(f, "frame_index", None) == best.frame_index), None)
            if frame is not None:
                x1 = max(0, int(best.bbox.x1)); y1 = max(0, int(best.bbox.y1))
                x2 = min(w, int(best.bbox.x2)); y2 = min(h, int(best.bbox.y2))
                if x2 > x1 and y2 > y1:
                    plate_crop_path = os.path.join(out, "plate.png")
                    cv2.imwrite(plate_crop_path, frame.image[y1:y2, x1:x2])
                    set_secure_permissions(plate_crop_path)

        manifest = {
            "violation_id": violation_id,
            "track_id": track.track_id,
            "plate": plate.text if plate else None,
            "fps": self.fps,
            "frame_count": len(frames),
            "first_ts": frames[0].timestamp,
            "last_ts": frames[-1].timestamp,
        }
        manifest_path = os.path.join(out, "manifest.json")
        write_json(manifest_path, manifest)
        set_secure_permissions(manifest_path)

        files = [clip_path, manifest_path] + ([plate_crop_path] if plate_crop_path else [])
        digest = keyed_digest_of_files(files, self.signing_key)
        algo = digest_algo(self.signing_key)
        sha_path = os.path.join(out, "evidence.sha256")
        atomic_write_text(
            sha_path,
            f"# algo={algo}\n" +
            "".join(f"{digest}  {os.path.basename(p)}\n" for p in sorted(files)))
        set_secure_permissions(sha_path)

        return EvidencePackage(
            clip_path=clip_path,
            frame_paths=[],
            plate_crop_path=plate_crop_path,
            sha256=digest,
            frame_count=len(frames),
            digest_algo=algo,
        )
