"""Utility trasversali: logging, hashing di integrita', conversioni, tempo."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import tempfile
from datetime import datetime, timezone, timedelta
from typing import Any, Iterable, Optional

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
        # SICUREZZA/GDPR: redige targhe, codici fiscali ed email dai log.
        try:
            from .security import PIIRedactingFilter
            handler.addFilter(PIIRedactingFilter())
        except Exception:  # pragma: no cover - non blocca il logging
            pass
        logger.addHandler(handler)
        logger.setLevel(os.environ.get("VELOCITAI_LOGLEVEL", "INFO").upper())
    return logger


def sha256_of_files(paths: Iterable[str]) -> str:
    """Hash di integrita' di un insieme di file (catena di custodia della prova).

    L'ordine dei file e' normalizzato per determinismo. Si lega al digest il
    *basename* (non il path assoluto): l'integrita' deve dipendere dal contenuto
    e dal nome del file, NON dalla sua posizione su disco, cosi' la verifica
    resta valida anche se il pacchetto-prova viene archiviato o spostato.
    """
    h = hashlib.sha256()
    for path in sorted(paths):
        h.update(os.path.basename(path).encode("utf-8"))
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


def is_finite_number(x: Any) -> bool:
    """True solo per int/float reali e finiti (no NaN, no +/-inf, no bool/None).

    Le grandezze fisiche (velocita', tempi, coordinate) non possono essere NaN
    o infinite: un dato simile indica corruzione e non deve mai arrivare al
    verbale. Questo predicato e' la guardia usata in tutto il sistema.
    """
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def safe_float(x: Any, default: float = 0.0) -> float:
    """Converte in float finito; ritorna ``default`` se NaN/inf/non numerico."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return v if math.isfinite(v) else default


def atomic_write_text(path: str, text: str, encoding: str = "utf-8") -> None:
    """Scrittura atomica: scrive su file temporaneo + ``os.replace``.

    Garantisce che un crash a meta' scrittura non lasci mai un file-prova o un
    verbale troncato/corrotto: il file di destinazione o e' quello vecchio
    (intatto) o quello nuovo (completo), mai uno stato intermedio.
    """
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-", suffix=".part")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)               # rinomina atomica sullo stesso fs
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_json(path: str, obj: Any) -> None:
    """Serializza ``obj`` in JSON con scrittura atomica (vedi atomic_write_text)."""
    text = json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    atomic_write_text(path, text)


def read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
