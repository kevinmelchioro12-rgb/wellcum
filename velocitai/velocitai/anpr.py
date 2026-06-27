"""ANPR / riconoscimento targa: normalizzazione, validazione formato italiano,
correzione errori OCR posizionale e backend di lettura.

Formato targa italiana (dal 1994): ``LL NNN LL`` — due lettere, tre cifre, due
lettere. Le lettere ``I O Q U`` non sono usate perche' confondibili con cifre/
altre lettere. Sono quindi ammesse 22 lettere.
"""

from __future__ import annotations

import re
import zlib
from typing import Dict, List, Optional, Protocol

from .models import PlateReading, Track, BBox

# Lettere ammesse: A-H, J-N, P, R-T, V-Z  (escludono I, O, Q, U)
_LETTER = "[A-HJ-NPR-TV-Z]"
ITALIAN_PLATE_RE = re.compile(rf"^{_LETTER}{{2}}[0-9]{{3}}{_LETTER}{{2}}$")
ALLOWED_LETTERS = set("ABCDEFGHJKLMNPRSTVWXYZ")

# Confusioni OCR comuni. Per gli slot-lettera convertiamo cifre -> lettere
# ammesse; per gli slot-cifra convertiamo lettere -> cifre.
_DIGIT_TO_LETTER: Dict[str, str] = {
    "2": "Z", "5": "S", "8": "B", "6": "G", "4": "A", "7": "T",
}
_LETTER_TO_DIGIT: Dict[str, str] = {
    "O": "0", "I": "1", "Z": "2", "S": "5", "B": "8", "G": "6",
    "D": "0", "Q": "0", "T": "7", "A": "4",
}


def normalize_plate(raw: str) -> str:
    """Maiuscolo, rimozione di spazi/trattini/simboli."""
    return re.sub(r"[^A-Z0-9]", "", (raw or "").upper())


def is_valid_italian_plate(text: str) -> bool:
    return bool(ITALIAN_PLATE_RE.match(text or ""))


def correct_plate(text: str) -> str:
    """Correzione posizionale degli errori OCR per targhe a 7 caratteri.

    Applica la mappa di confusione SOLO se la lunghezza e' 7, sfruttando le
    posizioni note (lettere agli indici 0,1,5,6; cifre agli indici 2,3,4).
    Se il testo non ha lunghezza 7, viene restituito invariato.
    """
    if len(text) != 7:
        return text
    out: List[str] = []
    for i, ch in enumerate(text):
        if i in (0, 1, 5, 6):           # slot lettera
            if ch.isdigit():
                out.append(_DIGIT_TO_LETTER.get(ch, ch))
            else:
                out.append(ch)
        else:                            # slot cifra (2,3,4)
            if ch.isalpha():
                out.append(_LETTER_TO_DIGIT.get(ch, ch))
            else:
                out.append(ch)
    return "".join(out)


class PlateValidator:
    """Normalizza + (opzionale) corregge + valida una lettura grezza."""

    def __init__(self, country: str = "IT", autocorrect: bool = True) -> None:
        self.country = country
        self.autocorrect = autocorrect

    def validate(self, raw_text: str, confidence: float,
                 bbox: Optional[BBox] = None) -> PlateReading:
        norm = normalize_plate(raw_text)
        text = norm
        corrected = False
        if self.country == "IT" and not is_valid_italian_plate(norm) and self.autocorrect:
            cand = correct_plate(norm)
            if is_valid_italian_plate(cand):
                text = cand
                corrected = True
        valid = is_valid_italian_plate(text) if self.country == "IT" else len(text) >= 4
        # una correzione abbassa lievemente la confidenza dichiarata
        conf = confidence * (0.92 if corrected else 1.0)
        return PlateReading(
            text=text,
            confidence=round(conf, 4),
            raw_text=raw_text,
            valid_format=valid,
            bbox=bbox,
            country=self.country,
        )


# ---------------------------------------------------------------------------
# Backend di lettura
# ---------------------------------------------------------------------------

class ANPRBackend(Protocol):
    def read(self, track: Track, frames: list) -> Optional[PlateReading]: ...


class SimulatedANPR:
    """Backend ANPR per la modalita' scenario.

    Legge la targa "ground-truth" dal ``SimFrame`` associando la traccia al
    veicolo simulato piu' vicino, e applica un tasso d'errore OCR deterministico
    (seed derivato dalla targa) per simulare letture imperfette.
    """

    def __init__(self, validator: PlateValidator,
                 char_error_rate: float = 0.0,
                 base_confidence: float = 0.97) -> None:
        self.validator = validator
        self.char_error_rate = char_error_rate
        self.base_confidence = base_confidence

    def _match_vehicle(self, track: Track, frames: list):
        """Trova lo stato veicolo simulato piu' vicino all'ultima bbox del track."""
        if not track.points:
            return None
        target = track.last.bbox.center
        best = None
        best_d = float("inf")
        for fr in frames:
            for vs in getattr(fr, "vehicles", []):
                c = vs.bbox.center
                d = c.distance_to(target)
                if d < best_d:
                    best_d = d
                    best = vs
        return best

    def _inject_noise(self, plate: str) -> str:
        if self.char_error_rate <= 0:
            return plate
        # PRNG deterministico (LCG) seminato dalla targa. NB: si usa crc32 e non
        # hash() builtin, che per le stringhe e' randomizzato per-processo
        # (PYTHONHASHSEED) e renderebbe il rumore NON riproducibile.
        seed = zlib.crc32(plate.encode("utf-8")) % (2**31)
        chars = list(plate)
        confus = {"0": "O", "O": "0", "8": "B", "B": "8", "5": "S", "S": "5"}
        for i in range(len(chars)):
            seed = (1103515245 * seed + 12345) % (2**31)
            if (seed / (2**31)) < self.char_error_rate:
                chars[i] = confus.get(chars[i], chars[i])
        return "".join(chars)

    def read(self, track: Track, frames: list) -> Optional[PlateReading]:
        veh = self._match_vehicle(track, frames)
        if veh is None:
            return None
        raw = self._inject_noise(veh.plate)
        return self.validator.validate(raw, confidence=self.base_confidence,
                                       bbox=track.last.bbox)


class EasyOCRANPR:  # pragma: no cover - richiede dipendenze pesanti
    """Backend di produzione: rilevamento targa + EasyOCR sui pixel reali.

    Attivato solo se ``easyocr``/``opencv`` sono installati. La firma e'
    identica a :class:`SimulatedANPR` per intercambiabilita'.
    """

    def __init__(self, validator: PlateValidator, gpu: bool = False) -> None:
        import easyocr  # noqa: F401  (errore esplicito se mancante)
        self.validator = validator
        # 'it' non e' un modello dedicato: si usa la lista latina + 'en'
        self._reader = easyocr.Reader(["en"], gpu=gpu)

    def read(self, track: Track, frames: list) -> Optional[PlateReading]:
        # Si sceglie il fotogramma in cui la bbox del veicolo e' piu' grande
        # (targa piu' leggibile), si ritaglia la ROI e si esegue OCR.
        if not track.points:
            return None
        best = max(track.points, key=lambda p: p.bbox.area)
        frame = next((f for f in frames
                      if getattr(f, "frame_index", None) == best.frame_index), None)
        if frame is None or getattr(frame, "image", None) is None:
            return None
        img = frame.image
        h, w = img.shape[:2]
        x1 = max(0, int(best.bbox.x1)); y1 = max(0, int(best.bbox.y1))
        x2 = min(w, int(best.bbox.x2)); y2 = min(h, int(best.bbox.y2))
        if x2 <= x1 or y2 <= y1:
            return None
        roi = img[y1:y2, x1:x2]
        # candidati OCR: testo + confidenza; si normalizza e si sceglie il
        # migliore che superi la validazione di formato.
        best_reading: Optional[PlateReading] = None
        for item in self._reader.readtext(roi):
            text, conf = item[1], float(item[2])
            reading = self.validator.validate(text, confidence=conf,
                                              bbox=best.bbox)
            if reading.valid_format and (best_reading is None
                                         or reading.confidence > best_reading.confidence):
                best_reading = reading
            elif best_reading is None:
                best_reading = reading       # fallback: miglior tentativo grezzo
        return best_reading
