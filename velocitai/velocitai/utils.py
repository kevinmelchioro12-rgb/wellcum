"""Utility trasversali: logging, hashing di integrita', conversioni, tempo."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Iterable

try:
    from zoneinfo import ZoneInfo
    _ROME = ZoneInfo("Europe/Rome")
except Exception:  # pragma: no cover - zoneinfo/tzdata assente
    _ROME = None

MS_PER_S = 1000.0
KMH_PER_MS = 3.6  # 1 m/s = 3.6 km/h


def _tz(tz_offset_hours: float):
    """Fuso orario italiano DST-aware (Europe/Rome) con fallback a offset fisso.

    Usare il fuso reale e' importante: la maggiorazione notturna (Art. 142
    c. 8-bis) dipende dall'ora locale e l'Italia osserva l'ora legale.
    """
    if _ROME is not None:
        return _ROME
    return timezone(timedelta(hours=tz_offset_hours))


def ms_to_kmh(speed_ms: float) -> float:
    return speed_ms * KMH_PER_MS


def kmh_to_ms(speed_kmh: float) -> float:
    return speed_kmh / KMH_PER_MS


def get_logger(name: str = "velocitai") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(os.environ.get("VELOCITAI_LOGLEVEL", "INFO").upper())
    return logger


def sha256_of_files(paths: Iterable[str]) -> str:
    """Hash di integrita' di un insieme di file (catena di custodia della prova).

    L'ordine dei file e' normalizzato per determinismo.
    """
    h = hashlib.sha256()
    for path in sorted(paths):
        h.update(path.encode("utf-8"))
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
        except OSError:
            # file mancante: si include comunque il nome per non falsare la catena
            h.update(b"<missing>")
    return h.hexdigest()


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def format_timestamp(ts: float, tz_offset_hours: float = 1.0) -> str:
    """Timestamp UNIX -> stringa leggibile in ora locale italiana (DST-aware).

    Usa Europe/Rome quando disponibile; ``tz_offset_hours`` e' solo fallback.
    """
    return datetime.fromtimestamp(ts, _tz(tz_offset_hours)).strftime("%d/%m/%Y %H:%M:%S")


def hour_of_day(ts: float, tz_offset_hours: float = 1.0) -> int:
    return datetime.fromtimestamp(ts, _tz(tz_offset_hours)).hour


def write_json(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
