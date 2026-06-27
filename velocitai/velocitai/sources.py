"""Sorgenti di fotogrammi per l'ESERCIZIO (file video / RTSP).

In modalita' scenario i fotogrammi provengono da :mod:`velocitai.scenario`
(``SimFrame`` con ground-truth). In produzione provengono da una telecamera o
da un file video, come :class:`VideoFrame` (immagine BGR + indice + timestamp).

Questo modulo richiede OpenCV ed e' quindi **opzionale**: l'import e' interno ai
metodi, cosi' il core resta a sola libreria standard.

NB: codice di produzione fornito come scaffolding; va collaudato con hardware/
video reali prima della messa in esercizio (vedi docs/PRODUCTION_BACKENDS.md).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Optional


@dataclass
class VideoFrame:
    """Fotogramma reale: immagine BGR (ndarray) + indice + timestamp UNIX."""
    frame_index: int
    timestamp: float
    image: Any                 # numpy.ndarray BGR (H, W, 3)
    width: int = 0
    height: int = 0


class VideoFrameSource:  # pragma: no cover - richiede OpenCV + sorgente reale
    """Genera :class:`VideoFrame` da un file video o stream RTSP via OpenCV.

    Il timestamp di ciascun fotogramma e' ``start_epoch + pos_ms/1000``: in
    esercizio ``start_epoch`` deve essere l'istante reale di acquisizione del
    primo fotogramma (da metadati telecamera/NTP), perche' i tempi entrano nel
    calcolo della velocita' e nel verbale.
    """

    def __init__(self, uri: str, start_epoch: float,
                 max_frames: Optional[int] = None) -> None:
        import cv2  # errore esplicito se OpenCV non e' installato
        self._cv2 = cv2
        self.uri = uri
        self.start_epoch = start_epoch
        self.max_frames = max_frames
        self._cap = cv2.VideoCapture(uri)
        if not self._cap.isOpened():
            raise OSError(f"Impossibile aprire la sorgente video: {uri}")
        self.fps = self._cap.get(cv2.CAP_PROP_FPS) or 25.0

    def frames(self) -> Iterator[VideoFrame]:
        cv2 = self._cv2
        idx = 0
        try:
            while True:
                if self.max_frames is not None and idx >= self.max_frames:
                    break
                ok, image = self._cap.read()
                if not ok:
                    break
                pos_ms = self._cap.get(cv2.CAP_PROP_POS_MSEC)
                ts = self.start_epoch + (pos_ms / 1000.0 if pos_ms else idx / self.fps)
                h, w = image.shape[:2]
                yield VideoFrame(frame_index=idx, timestamp=ts, image=image,
                                 width=w, height=h)
                idx += 1
        finally:
            self.release()

    def release(self) -> None:
        try:
            self._cap.release()
        except Exception:
            pass
