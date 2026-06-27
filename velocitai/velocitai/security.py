"""Strati di sicurezza trasversali del sistema di accertamento.

Modello di minaccia (sintesi; dettaglio in ``docs/SECURITY.md``):

* **Input non fidato** -> path traversal, injection, XSS: ogni dato esterno
  (targa, id violazione, protocollo, nomi file) viene sanitizzato prima di
  toccare il filesystem o l'HTML.
* **Manomissione della prova** (anche da insider) -> la catena di custodia usa
  un **HMAC con chiave segreta** (non un semplice SHA-256 falsificabile da chi
  sa scrivere i file): senza la chiave non si puo' forgiare un digest valido.
* **Esfiltrazione di PII** (GDPR) -> redazione di targa/codice fiscale nei log e
  **permessi restrittivi** (0600/0700) su prove e verbali.
* **Ripudio / alterazione del registro** -> **audit-log a catena di hash**
  (append-only, tamper-evident): cancellare o modificare una riga rompe la
  catena.
* **DoS** -> il rate-limiter e i limiti di risorsa (altrove) contengono gli abusi.

Tutto in sola libreria standard. Le chiavi/segreti provengono dall'ambiente,
non sono mai hardcoded ne' scritti nei log.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import re
import threading
import time
from typing import Any, Dict, Iterable, List, Optional


class SecurityError(ValueError):
    """Violazione di un controllo di sicurezza (input ostile, path illecito)."""


# ---------------------------------------------------------------------------
# Sanitizzazione di input usati come path / nomi file
# ---------------------------------------------------------------------------

_SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9._-]+$")
_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def safe_path_component(name: str, *, max_len: int = 128,
                        field: str = "valore") -> str:
    """Rende ``name`` sicuro come SINGOLO componente di path.

    Difende da path traversal (``../``), path assoluti, null-byte e separatori:
    consente solo ``[A-Za-z0-9._-]``. Rifiuta ``.``/``..`` e i nomi vuoti.
    Solleva :class:`SecurityError` se l'input e' palesemente ostile, altrimenti
    normalizza i caratteri non ammessi a ``_`` (robustezza > rigidita').
    """
    if name is None:
        raise SecurityError(f"{field}: nome di path nullo")
    raw = str(name)
    if "\x00" in raw:
        raise SecurityError(f"{field}: null-byte nel nome di path")
    # rimuove eventuali componenti di directory e normalizza
    base = raw.replace("\\", "/").split("/")[-1].strip()
    cleaned = _UNSAFE_CHARS.sub("_", base)[:max_len]
    if cleaned in ("", ".", "..") or set(cleaned) <= {".", "_"}:
        raise SecurityError(f"{field}: nome di path non valido dopo sanitizzazione: {raw!r}")
    return cleaned


def secure_join(base_dir: str, *components: str) -> str:
    """Unisce i componenti a ``base_dir`` garantendo di restare DENTRO base_dir.

    Difesa in profondita' contro il path traversal: dopo il join si verifica con
    ``realpath`` che il risultato non esca dalla radice consentita.
    """
    safe = [safe_path_component(c, field="componente") for c in components]
    base_abs = os.path.realpath(base_dir)
    full = os.path.realpath(os.path.join(base_abs, *safe))
    if full != base_abs and not full.startswith(base_abs + os.sep):
        raise SecurityError(f"path fuori dalla radice consentita: {full}")
    return full


# ---------------------------------------------------------------------------
# Segreti (mai hardcoded ne' loggati)
# ---------------------------------------------------------------------------

def load_secret(env_var: str, *, required: bool = False) -> Optional[bytes]:
    """Carica un segreto dall'ambiente. Non viene mai scritto nei log."""
    val = os.environ.get(env_var)
    if not val:
        if required:
            raise SecurityError(f"Segreto obbligatorio assente: variabile {env_var}")
        return None
    return val.encode("utf-8")


def constant_time_equals(a: str, b: str) -> bool:
    """Confronto a tempo costante (anti timing-attack su token/hash)."""
    return hmac.compare_digest(str(a), str(b))


# ---------------------------------------------------------------------------
# Catena di custodia con HMAC (anti-falsificazione)
# ---------------------------------------------------------------------------

def keyed_digest_of_files(paths: Iterable[str], key: Optional[bytes]) -> str:
    """Digest di integrita' dei file della prova.

    Con ``key`` presente usa **HMAC-SHA256** (non falsificabile senza la chiave,
    quindi resistente alla manomissione da parte di chi ha accesso in scrittura
    al disco). Senza chiave ricade su SHA-256 semplice (sviluppo/demo). Lega il
    *basename* (non il path assoluto): l'integrita' dipende dal contenuto, non
    dalla posizione su disco.
    """
    h = hmac.new(key, digestmod=hashlib.sha256) if key else hashlib.sha256()
    for path in sorted(paths):
        h.update(os.path.basename(path).encode("utf-8"))
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
        except OSError:
            h.update(b"<missing>")
    return h.hexdigest()


def digest_algo(key: Optional[bytes]) -> str:
    return "hmac-sha256" if key else "sha256"


# ---------------------------------------------------------------------------
# Permessi restrittivi su artefatti con PII
# ---------------------------------------------------------------------------

def set_secure_permissions(path: str) -> None:
    """Imposta permessi restrittivi (file 0600, dir 0700) sugli artefatti con PII.

    Best-effort: su filesystem che non supportano i permessi POSIX (es. Windows)
    l'operazione e' silenziosamente ignorata.
    """
    try:
        mode = 0o700 if os.path.isdir(path) else 0o600
        os.chmod(path, mode)
    except (OSError, NotImplementedError):
        pass


# ---------------------------------------------------------------------------
# Redazione PII nei log (GDPR)
# ---------------------------------------------------------------------------

_PLATE_RE = re.compile(r"\b([A-Z]{2})\d{3}([A-Z]{2})\b")
_FISCAL_RE = re.compile(r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")


def redact_plate(plate: str) -> str:
    """``AB123CD`` -> ``AB***CD`` (mantiene utilita' diagnostica senza esporre)."""
    if not plate:
        return plate
    return _PLATE_RE.sub(r"\1***\2", str(plate))


def redact_pii(text: str) -> str:
    """Maschera targhe, codici fiscali ed email in una stringa di log."""
    s = _PLATE_RE.sub(r"\1***\2", str(text))
    s = _FISCAL_RE.sub("CF-REDACTED", s)
    s = _EMAIL_RE.sub("EMAIL-REDACTED", s)
    return s


class PIIRedactingFilter(logging.Filter):
    """Filtro di logging che redige la PII dal messaggio gia' formattato."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        try:
            msg = record.getMessage()
        except Exception:  # pragma: no cover - messaggi malformati
            return True
        redacted = redact_pii(msg)
        if redacted != msg:
            record.msg = redacted
            record.args = ()
        return True


# ---------------------------------------------------------------------------
# Audit-log a catena di hash (append-only, tamper-evident)
# ---------------------------------------------------------------------------

class AuditLog:
    """Registro di audit a prova di manomissione (catena di hash su file JSONL).

    Ogni voce include l'hash della precedente: alterare o rimuovere una riga
    rompe la catena e viene rilevato da :meth:`verify`. Per il non-ripudio si
    puo' fornire una ``key`` (HMAC) cosi' che la catena non sia ricostruibile da
    chi non possiede il segreto.
    """

    GENESIS = "0" * 64

    def __init__(self, path: str, key: Optional[bytes] = None) -> None:
        self.path = path
        self.key = key
        self._lock = threading.Lock()

    def _mac(self, data: str) -> str:
        if self.key:
            return hmac.new(self.key, data.encode("utf-8"), hashlib.sha256).hexdigest()
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def _last_hash(self) -> str:
        if not os.path.exists(self.path):
            return self.GENESIS
        last = self.GENESIS
        try:
            with open(self.path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    import json
                    try:
                        last = json.loads(line).get("hash", last)
                    except ValueError:
                        continue
        except OSError:
            return self.GENESIS
        return last

    def record(self, event: str, **fields: Any) -> str:
        """Appende un evento di sicurezza alla catena. Ritorna l'hash della voce.

        La PII negli ``fields`` viene redatta prima della scrittura.
        """
        import json
        safe_fields = {k: redact_pii(str(v)) for k, v in fields.items()}
        with self._lock:
            prev = self._last_hash()
            entry = {
                "ts": round(time.time(), 3),
                "event": str(event),
                "fields": safe_fields,
                "prev": prev,
            }
            payload = json.dumps(entry, sort_keys=True, ensure_ascii=False)
            entry["hash"] = self._mac(prev + payload)
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            set_secure_permissions(self.path)
            return entry["hash"]

    def verify(self) -> bool:
        """Verifica l'integrita' dell'intera catena (True = intatta)."""
        import json
        if not os.path.exists(self.path):
            return True
        prev = self.GENESIS
        try:
            with open(self.path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    stored = entry.get("hash")
                    base = {k: entry[k] for k in ("ts", "event", "fields", "prev")}
                    payload = json.dumps(base, sort_keys=True, ensure_ascii=False)
                    if entry.get("prev") != prev or self._mac(prev + payload) != stored:
                        return False
                    prev = stored
        except (OSError, ValueError, KeyError):
            return False
        return True


# ---------------------------------------------------------------------------
# Rate limiter (token bucket) per il server web
# ---------------------------------------------------------------------------

class RateLimiter:
    """Token bucket per-client: limita le richieste e contiene i DoS leggeri."""

    def __init__(self, rate_per_s: float = 20.0, burst: int = 40,
                 clock=time.monotonic) -> None:
        self.rate = rate_per_s
        self.burst = burst
        self._clock = clock
        self._buckets: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def allow(self, client: str) -> bool:
        now = self._clock()
        with self._lock:
            tokens, last = self._buckets.get(client, (float(self.burst), now))
            tokens = min(self.burst, tokens + (now - last) * self.rate)
            if tokens < 1.0:
                self._buckets[client] = (tokens, now)
                return False
            self._buckets[client] = (tokens - 1.0, now)
            return True
