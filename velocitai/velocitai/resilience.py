"""Resilienza operativa e auto-riparazione del sistema di accertamento.

Principio guida: **nessun singolo errore deve fermare l'accertamento o produrre
un atto invalido.** Un fotogramma corrotto, un disco pieno, il backend ANPR in
crash, la PEC irraggiungibile o un dato numerico NaN sono *attesi* in esercizio
e vengono gestiti, non subiti:

* :func:`retry` — ritentativi con backoff esponenziale per guasti transitori.
* :class:`CircuitBreaker` — isola un backend che continua a fallire ed evita di
  martellarlo, consentendo la *degradazione controllata* (es. salto ANPR ->
  verbale "DA_VERIFICARE" invece di crash).
* :class:`DeadLetterQueue` — persiste gli elementi non elaborati (violazioni,
  notifiche) per la **ripresa automatica** in un momento successivo.
* :class:`HealthMonitor` — traccia successi/fallimenti per componente, espone lo
  stato di salute e abilita il self-check operativo.
* :class:`IssuedLedger` — registro idempotente anti **doppia sanzione**.
* :func:`guard` — esegue una funzione isolando qualunque eccezione.

Tutto in sola libreria standard, scritture atomiche e durabili.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from .utils import atomic_write_text, get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Retry con backoff esponenziale
# ---------------------------------------------------------------------------

def retry(
    fn: Callable[[], Any],
    *,
    attempts: int = 3,
    base_delay: float = 0.0,
    max_delay: float = 30.0,
    exceptions: Tuple[type, ...] = (Exception,),
    sleep: Callable[[float], None] = time.sleep,
    on_retry: Optional[Callable[[int, BaseException], None]] = None,
    label: str = "operazione",
) -> Any:
    """Esegue ``fn`` ritentando fino a ``attempts`` volte sui guasti transitori.

    Il ritardo cresce esponenzialmente (``base_delay * 2**i``) fino a
    ``max_delay``. ``base_delay=0`` rende il retry istantaneo (utile nei test).
    Rilancia l'ultima eccezione se tutti i tentativi falliscono.
    """
    if attempts < 1:
        raise ValueError("attempts deve essere >= 1")
    last: Optional[BaseException] = None
    for i in range(attempts):
        try:
            return fn()
        except exceptions as exc:  # noqa: BLE001 - retry deliberato
            last = exc
            if i + 1 >= attempts:
                break
            if on_retry is not None:
                on_retry(i + 1, exc)
            delay = min(max_delay, base_delay * (2 ** i)) if base_delay > 0 else 0.0
            log.warning("Retry %s (%d/%d) dopo errore: %s",
                        label, i + 1, attempts, exc)
            if delay > 0:
                sleep(delay)
    assert last is not None
    raise last


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------

class CircuitBreakerOpen(RuntimeError):
    """Sollevata quando il circuito e' aperto (backend isolato)."""


class CircuitBreaker:
    """Interruttore a tre stati: ``closed`` -> ``open`` -> ``half_open``.

    Dopo ``fail_max`` fallimenti consecutivi il circuito si **apre** e le
    chiamate vengono rifiutate subito (``CircuitBreakerOpen``) per ``reset_after``
    secondi, evitando di martellare un backend guasto. Trascorso il timeout passa
    a ``half_open`` e lascia passare una chiamata di prova: se va a buon fine si
    richiude, altrimenti si riapre.
    """

    def __init__(self, fail_max: int = 5, reset_after: float = 30.0,
                 name: str = "backend",
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.fail_max = fail_max
        self.reset_after = reset_after
        self.name = name
        self._clock = clock
        self._failures = 0
        self._opened_at: Optional[float] = None
        self.state = "closed"

    def _allow(self) -> bool:
        if self.state == "open":
            assert self._opened_at is not None
            if self._clock() - self._opened_at >= self.reset_after:
                self.state = "half_open"
                log.info("Circuit '%s' -> half_open (prova di ripristino)", self.name)
                return True
            return False
        return True

    def record_success(self) -> None:
        if self.state != "closed":
            log.info("Circuit '%s' -> closed (backend ripristinato)", self.name)
        self._failures = 0
        self._opened_at = None
        self.state = "closed"

    def record_failure(self) -> None:
        self._failures += 1
        if self.state == "half_open" or self._failures >= self.fail_max:
            self.state = "open"
            self._opened_at = self._clock()
            log.warning("Circuit '%s' APERTO dopo %d fallimenti", self.name,
                        self._failures)

    def call(self, fn: Callable[[], Any]) -> Any:
        if not self._allow():
            raise CircuitBreakerOpen(f"circuito '{self.name}' aperto")
        try:
            result = fn()
        except Exception:
            self.record_failure()
            raise
        self.record_success()
        return result


# ---------------------------------------------------------------------------
# Esecuzione isolata
# ---------------------------------------------------------------------------

@dataclass
class GuardResult:
    ok: bool
    value: Any = None
    error: Optional[str] = None


def guard(fn: Callable[[], Any], *, component: str = "",
          monitor: Optional["HealthMonitor"] = None,
          default: Any = None) -> GuardResult:
    """Esegue ``fn`` catturando QUALUNQUE eccezione (eccetto interruzioni).

    Aggiorna il monitor di salute (se fornito) e ritorna un :class:`GuardResult`
    invece di propagare il guasto: il chiamante decide come degradare.
    """
    try:
        value = fn()
        if monitor is not None and component:
            monitor.record(component, ok=True)
        return GuardResult(ok=True, value=value)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as exc:  # noqa: BLE001 - isolamento deliberato
        log.error("Componente '%s' fallito: %s", component or "?", exc)
        if monitor is not None and component:
            monitor.record(component, ok=False, error=str(exc))
        return GuardResult(ok=False, value=default, error=str(exc))


# ---------------------------------------------------------------------------
# Monitor di salute
# ---------------------------------------------------------------------------

@dataclass
class ComponentHealth:
    name: str
    successes: int = 0
    failures: int = 0
    consecutive_failures: int = 0
    last_error: Optional[str] = None

    @property
    def total(self) -> int:
        return self.successes + self.failures

    @property
    def healthy(self) -> bool:
        # sano se non ha una raffica di fallimenti consecutivi
        return self.consecutive_failures < 3

    @property
    def success_rate(self) -> float:
        return self.successes / self.total if self.total else 1.0


class HealthMonitor:
    """Aggrega lo stato di salute dei componenti della pipeline."""

    def __init__(self) -> None:
        self._components: Dict[str, ComponentHealth] = {}

    def record(self, component: str, ok: bool, error: Optional[str] = None) -> None:
        h = self._components.setdefault(component, ComponentHealth(component))
        if ok:
            h.successes += 1
            h.consecutive_failures = 0
        else:
            h.failures += 1
            h.consecutive_failures += 1
            h.last_error = error

    def get(self, component: str) -> ComponentHealth:
        return self._components.setdefault(component, ComponentHealth(component))

    def is_healthy(self) -> bool:
        return all(h.healthy for h in self._components.values())

    def report(self) -> Dict[str, Any]:
        return {
            "healthy": self.is_healthy(),
            "components": {
                name: {
                    "successes": h.successes,
                    "failures": h.failures,
                    "consecutive_failures": h.consecutive_failures,
                    "success_rate": round(h.success_rate, 4),
                    "healthy": h.healthy,
                    "last_error": h.last_error,
                }
                for name, h in sorted(self._components.items())
            },
        }


# ---------------------------------------------------------------------------
# Coda dead-letter persistente (ripresa automatica)
# ---------------------------------------------------------------------------

class DeadLetterQueue:
    """Persiste su disco gli elementi non elaborati per la ripresa successiva.

    Ogni elemento e' un file JSON in ``directory``; questo rende la coda durabile
    a un riavvio del processo. ``retry_pending`` ritenta gli elementi con un
    handler e rimuove quelli elaborati con successo (auto-riparazione).
    """

    def __init__(self, directory: str) -> None:
        self.directory = directory

    def _ensure(self) -> None:
        os.makedirs(self.directory, exist_ok=True)

    def add(self, kind: str, key: str, payload: Dict[str, Any],
            error: str = "") -> str:
        self._ensure()
        safe_key = "".join(c if c.isalnum() or c in "-_." else "_" for c in key)
        path = os.path.join(self.directory, f"{kind}__{safe_key}.json")
        record = {"kind": kind, "key": key, "error": error,
                  "attempts": 1, "payload": payload}
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    record["attempts"] = json.load(fh).get("attempts", 1) + 1
            except (OSError, ValueError):
                pass
        atomic_write_text(path, json.dumps(record, ensure_ascii=False, indent=2,
                                           default=str))
        log.warning("Dead-letter aggiunto: %s/%s (tentativi=%d)", kind, key,
                    record["attempts"])
        return path

    def pending(self) -> List[Dict[str, Any]]:
        if not os.path.isdir(self.directory):
            return []
        out: List[Dict[str, Any]] = []
        for name in sorted(os.listdir(self.directory)):
            if not name.endswith(".json"):
                continue
            full = os.path.join(self.directory, name)
            try:
                with open(full, encoding="utf-8") as fh:
                    rec = json.load(fh)
                rec["_path"] = full
                out.append(rec)
            except (OSError, ValueError) as exc:
                log.error("Voce dead-letter illeggibile %s: %s", name, exc)
        return out

    def resolve(self, path: str) -> None:
        try:
            os.unlink(path)
        except OSError:
            pass

    def retry_pending(self, handler: Callable[[Dict[str, Any]], None],
                      kinds: Optional[Tuple[str, ...]] = None) -> Dict[str, int]:
        """Ritenta gli elementi in coda. Ritorna {'resolved', 'failed'}."""
        resolved = failed = 0
        for rec in self.pending():
            if kinds and rec.get("kind") not in kinds:
                continue
            res = guard(lambda: handler(rec), component="dead_letter_retry")
            if res.ok:
                self.resolve(rec["_path"])
                resolved += 1
            else:
                failed += 1
        if resolved or failed:
            log.info("Ripresa dead-letter: %d risolti, %d ancora in errore",
                     resolved, failed)
        return {"resolved": resolved, "failed": failed}


# ---------------------------------------------------------------------------
# Ledger idempotente anti doppia-sanzione
# ---------------------------------------------------------------------------

class IssuedLedger:
    """Registro persistente delle violazioni gia' verbalizzate.

    Evita la **doppia sanzione** se la stessa clip viene rielaborata: la chiave
    e' deterministica su (dispositivo, targa, finestra temporale). Idempotente e
    durabile (un file JSON append-only riscritto in modo atomico).
    """

    def __init__(self, path: str, window_s: float = 2.0) -> None:
        self.path = path
        self.window_s = max(0.0, window_s)
        self._keys: set = set()
        self._load()

    def _load(self) -> None:
        # Formato append-only: una chiave per riga. Caricamento tollerante (una
        # riga corrotta da un crash a meta' scrittura viene semplicemente saltata,
        # e l'idempotenza tollera comunque una chiave mancante o doppia).
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, encoding="utf-8") as fh:
                for line in fh:
                    k = line.strip()
                    if k:
                        self._keys.add(k)
        except OSError as exc:
            log.error("Ledger illeggibile %s: %s (riparto vuoto)", self.path, exc)
            self._keys = set()

    def key_for(self, device_id: str, plate: str, ts: float,
                extra: str = "") -> str:
        bucket = int(ts // self.window_s) if self.window_s > 0 else int(ts)
        key = f"{device_id}|{plate}|{bucket}|{extra}"
        return key.replace("\n", " ").replace("\r", " ")

    def seen(self, key: str) -> bool:
        return key in self._keys

    def add(self, key: str) -> None:
        # Append O(1) e durabile: niente riscrittura dell'intero file ad ogni
        # violazione (evita un costo O(n^2) ai volumi di esercizio).
        if key in self._keys:
            return
        self._keys.add(key)
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        line = key.replace("\n", " ").replace("\r", " ")
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def prune(self, older_than_ts: float) -> int:
        """Rimuove le chiavi piu' vecchie di ``older_than_ts`` (manutenzione).

        Limita la crescita illimitata del ledger: una violazione oltre i termini
        perentori (notifica/pagamento) non puo' piu' essere riemessa, quindi la
        sua chiave non serve. Il bucket temporale e' gia' nella chiave, percio'
        non serve storage aggiuntivo. Le chiavi non interpretabili sono conservate
        (fail-safe: meglio non sanzionare due volte che potare per errore).
        """
        if self.window_s <= 0:
            return 0
        cutoff = older_than_ts / self.window_s
        keep = set()
        for k in self._keys:
            parts = k.split("|")
            try:
                bucket = int(parts[2])
            except (IndexError, ValueError):
                keep.add(k)
                continue
            if bucket >= cutoff:
                keep.add(k)
        removed = len(self._keys) - len(keep)
        if removed:
            self._keys = keep
            atomic_write_text(self.path,
                              "".join(k + "\n" for k in sorted(self._keys)))
            log.info("Ledger: potate %d chiavi anteriori a %s", removed, older_than_ts)
        return removed
