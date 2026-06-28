"""Multi-object tracker basato su IoU + nearest-centroid.

Mantiene identita' stabili tra fotogrammi gestendo brevi occlusioni (``max_misses``).
E' l'equivalente leggero e deterministico di SORT/ByteTrack; il backend di
produzione puo' sostituirlo con ByteTrack mantenendo la stessa interfaccia
(``update`` riceve ``Detection`` e restituisce i ``Track`` attivi).
"""

from __future__ import annotations

from typing import Dict, List

from .models import Detection, Track, TrackPoint, BBox


class IoUTracker:
    def __init__(
        self,
        iou_threshold: float = 0.2,
        max_misses: int = 8,
        min_hits: int = 3,
    ) -> None:
        self.iou_threshold = iou_threshold
        self.max_misses = max_misses
        self.min_hits = min_hits
        self._tracks: Dict[int, Track] = {}
        # tracce confermate gia' uscite di scena: conservate per la stima
        # off-line della velocita' a fine clip.
        self._archived: List[Track] = []
        self._next_id = 1

    @property
    def tracks(self) -> List[Track]:
        return list(self._tracks.values())

    def reset(self) -> None:
        """Azzera lo stato interno: rielaborare una clip deve ripartire pulito.

        Senza reset, chiamate successive accumulerebbero tracce di clip diverse,
        falsando conteggi e (in combinazione col ledger) l'idempotenza.
        """
        self._tracks.clear()
        self._archived.clear()
        self._next_id = 1

    def _match(self, det: Detection, used: set) -> int:
        """Trova il miglior track per una detection (IoU max sopra soglia)."""
        best_id = -1
        best_iou = self.iou_threshold
        for tid, track in self._tracks.items():
            if tid in used:
                continue
            iou = track.last.bbox.iou(det.bbox)
            if iou >= best_iou:
                best_iou = iou
                best_id = tid
        return best_id

    def update(self, detections: List[Detection]) -> List[Track]:
        """Aggiorna i track con le detection del fotogramma corrente.

        Restituisce i track confermati (>= ``min_hits`` osservazioni).
        """
        used: set = set()
        for det in detections:
            tid = self._match(det, used)
            if tid == -1:
                # nuova traccia
                tid = self._next_id
                self._next_id += 1
                self._tracks[tid] = Track(track_id=tid, vehicle_class=det.vehicle_class)
            used.add(tid)
            self._tracks[tid].add(TrackPoint(
                frame_index=det.frame_index,
                timestamp=det.timestamp,
                bbox=det.bbox,
                world_point=det.world_point,
            ))
            if len(self._tracks[tid].points) >= self.min_hits:
                self._tracks[tid].confirmed = True

        # incrementa i miss dei track non aggiornati ed elimina i persi
        for tid in list(self._tracks):
            if tid not in used:
                self._tracks[tid].misses += 1
                if self._tracks[tid].misses > self.max_misses:
                    lost = self._tracks.pop(tid)
                    if lost.confirmed:
                        self._archived.append(lost)

        return [t for t in self._tracks.values() if t.confirmed]

    def finalize(self) -> List[Track]:
        """Tutti i track confermati a fine sequenza (vivi + archiviati).

        Per l'elaborazione per-clip serve includere anche le tracce gia' uscite
        di scena, altrimenti la stima velocita' off-line le perderebbe.
        """
        alive = [t for t in self._tracks.values() if t.confirmed]
        return self._archived + alive
