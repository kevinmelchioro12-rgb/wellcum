"""Utility trasversali: logging, hashing di integrita', conversioni, tempo."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Iterable

MS_PER_S = 1000.0
KMH_PER_MS = 3.6  # 1 m/s = 3.6 km/h


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
    """Timestamp UNIX -> stringa leggibile in ora locale italiana (CET, default).

    Per un sistema legale conviene un fuso esplicito; qui CET/CEST e' approssimato
    con un offset fisso configurabile (la versione di produzione usa zoneinfo).
    """
    tz = timezone(timedelta(hours=tz_offset_hours))
    return datetime.fromtimestamp(ts, tz).strftime("%d/%m/%Y %H:%M:%S")


def hour_of_day(ts: float, tz_offset_hours: float = 1.0) -> int:
    tz = timezone(timedelta(hours=tz_offset_hours))
    return datetime.fromtimestamp(ts, tz).hour


def write_json(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
