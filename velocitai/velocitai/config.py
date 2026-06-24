"""Configurazione di sistema (postazione, soglie, importi sanzionatori).

Gli importi e i parametri legali sono **interamente configurabili** perche':
- gli importi edittali dell'Art. 142 CdS sono aggiornati ogni 2 anni (Art. 195
  CdS, aggiornamento ISTAT) con decreto ministeriale;
- la tolleranza strumentale e i limiti dipendono dall'omologazione dello strumento.

I valori di default riflettono l'aggiornamento biennale 2024-2025 e vanno
verificati/aggiornati con l'ufficio legale prima della messa in esercizio.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, fields as dc_fields
from typing import Dict, List, Optional, Tuple, Any

try:
    import yaml  # PyYAML
    _HAS_YAML = True
except Exception:  # pragma: no cover
    _HAS_YAML = False


class ConfigError(ValueError):
    """Configurazione non valida: blocca l'avvio prima di emettere atti errati."""


@dataclass
class SpeedBracket:
    """Fascia sanzionatoria dell'Art. 142 CdS."""
    name: str                 # es. "comma 8"
    articolo: str             # es. "Art. 142 comma 8 CdS"
    over_min_kmh: float       # superamento > di questo
    over_max_kmh: Optional[float]  # ... e <= di questo (None = nessun limite sup.)
    amount_min_eur: float
    amount_max_eur: float
    points_deducted: int
    suspension_months: Tuple[int, int] = (0, 0)
    # La maggiorazione notturna +1/3 (Art. 142 c. 8-bis) si applica SOLO alle
    # violazioni dei commi 9 e 9-bis commesse tra le 22:00 e le 07:00.
    night_eligible: bool = False


@dataclass
class SanctionConfig:
    """Parametri sanzionatori Art. 142 / 202 / 203 CdS."""
    # Abbattimento per tolleranza strumentale: si sottrae alla velocita' misurata
    # il massimo tra (percentuale * misura) e il minimo assoluto.
    # Regola consolidata: 5% con minimo 5 km/h (a favore del trasgressore).
    tolerance_percent: float = 5.0
    tolerance_min_kmh: float = 5.0

    # Maggiorazione notturna (dalle 22:00 alle 07:00): +1/3 dell'importo (Art.142 c.)
    night_surcharge_factor: float = 1.0 / 3.0
    night_start_hour: int = 22
    night_end_hour: int = 7

    # Pagamento in misura ridotta (Art. 202 CdS): importo minimo edittale.
    # Sconto del 30% se pagato entro 5 giorni (Art. 202 c.1).
    early_payment_discount: float = 0.30
    early_payment_days: int = 5

    # Termini perentori
    notification_deadline_days: int = 90   # Art. 201 CdS (notifica)
    payment_deadline_days: int = 60        # Art. 202 CdS (pagamento misura ridotta)

    # Spese di accertamento e notificazione (a carico del trasgressore)
    notification_costs_eur: float = 16.50

    brackets: List[SpeedBracket] = field(default_factory=lambda: [
        SpeedBracket("comma 7", "Art. 142 comma 7 CdS", 0.0, 10.0,
                     42.0, 173.0, 0, (0, 0), night_eligible=False),
        SpeedBracket("comma 8", "Art. 142 comma 8 CdS", 10.0, 40.0,
                     173.0, 695.0, 3, (0, 0), night_eligible=False),
        SpeedBracket("comma 9", "Art. 142 comma 9 CdS", 40.0, 60.0,
                     543.0, 2170.0, 6, (1, 3), night_eligible=True),
        SpeedBracket("comma 9-bis", "Art. 142 comma 9-bis CdS", 60.0, None,
                     845.0, 3382.0, 10, (6, 12), night_eligible=True),
    ])


@dataclass
class CalibrationConfig:
    """Punti di calibrazione e geometria della postazione."""
    # corrispondenze pixel <-> metri sul piano stradale (>=4)
    image_points: List[Tuple[float, float]] = field(default_factory=list)
    world_points: List[Tuple[float, float]] = field(default_factory=list)
    # in alternativa, gate a due linee
    line_gate_entry_y: Optional[float] = None
    line_gate_exit_y: Optional[float] = None
    line_gate_distance_m: Optional[float] = None
    meters_per_pixel: Optional[float] = None


@dataclass
class ANPRConfig:
    min_confidence: float = 0.55     # sotto soglia: revisione manuale
    require_valid_format: bool = True
    country: str = "IT"


@dataclass
class RecorderConfig:
    output_dir: str = "data/evidence"
    pre_event_frames: int = 30        # frame prima dell'evento da conservare
    post_event_frames: int = 30
    fps: float = 25.0
    save_plate_crop: bool = True


@dataclass
class NotifierConfig:
    mode: str = "simulated"           # simulated | pec | email | file
    sender: str = "comando.pl@comune.example.it"
    pec_endpoint: str = ""
    output_dir: str = "data/verbali"


@dataclass
class SpeedConfig:
    method: str = "line_pair"         # line_pair | world_regression
    min_track_points: int = 4
    min_duration_s: float = 0.15
    # scarto misure con confidenza inferiore
    min_confidence: float = 0.6


@dataclass
class DeviceConfig:
    """Identita' e omologazione della postazione (campi obbligatori nel verbale)."""
    device_id: str = "VELOCITAI-0001"
    homologation_number: str = "OMOL-DA-DEFINIRE"   # numero decreto di approvazione MIT
    last_calibration_date: str = "2026-01-01"       # taratura periodica (obbligatoria)
    operator_authority: str = "Comando Polizia Locale - Comune di Esempio"
    operator_fiscal_code: str = "00000000000"


@dataclass
class LocationConfig:
    road_name: str = "SS1 Via Aurelia km 12+300"
    municipality: str = "Comune di Esempio"
    province: str = "MI"
    latitude: float = 45.4642
    longitude: float = 9.1900
    direction: str = "carreggiata Nord"
    speed_limit_kmh: float = 50.0
    urban_area: bool = True


@dataclass
class Config:
    device: DeviceConfig = field(default_factory=DeviceConfig)
    location: LocationConfig = field(default_factory=LocationConfig)
    calibration: CalibrationConfig = field(default_factory=CalibrationConfig)
    speed: SpeedConfig = field(default_factory=SpeedConfig)
    anpr: ANPRConfig = field(default_factory=ANPRConfig)
    recorder: RecorderConfig = field(default_factory=RecorderConfig)
    notifier: NotifierConfig = field(default_factory=NotifierConfig)
    sanction: SanctionConfig = field(default_factory=SanctionConfig)
    registry_path: str = "data/registry/owners.json"
    # Offset orario fisso (CET=+1, CEST=+2). Semplificazione: la versione di
    # produzione usa zoneinfo "Europe/Rome" per gestire l'ora legale.
    tz_offset_hours: float = 2.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Caricamento da YAML con merge ricorsivo sui default
# ---------------------------------------------------------------------------

def _merge(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        out = dict(base)
        for k, v in override.items():
            out[k] = _merge(base.get(k), v) if k in base else v
        return out
    return override if override is not None else base


def _build_brackets(raw: List[Dict[str, Any]]) -> List[SpeedBracket]:
    out = []
    for i, b in enumerate(raw):
        if not isinstance(b, dict):
            raise ConfigError(f"sanction.brackets[{i}] deve essere una mappa, non {type(b).__name__}")
        for req in ("name", "articolo", "over_min_kmh", "amount_min_eur", "amount_max_eur"):
            if req not in b:
                raise ConfigError(f"sanction.brackets[{i}] manca il campo obbligatorio '{req}'")
        susp = b.get("suspension_months", [0, 0]) or [0, 0]
        out.append(SpeedBracket(
            name=b["name"], articolo=b["articolo"],
            over_min_kmh=b["over_min_kmh"], over_max_kmh=b.get("over_max_kmh"),
            amount_min_eur=b["amount_min_eur"], amount_max_eur=b["amount_max_eur"],
            points_deducted=b.get("points_deducted", 0),
            suspension_months=tuple(susp),
            night_eligible=b.get("night_eligible", False),
        ))
    return out


def _known(cls, d: Dict[str, Any]) -> Dict[str, Any]:
    """Filtra le chiavi non riconosciute da un dataclass.

    Un refuso nello YAML (es. ``speed_limit`` invece di ``speed_limit_kmh``) non
    deve far crashare il caricamento con un ``TypeError`` criptico: la chiave
    ignota viene scartata e segnalata, e il resto della config viene applicato.
    """
    if not isinstance(d, dict):
        return {}
    allowed = {f.name for f in dc_fields(cls)}
    out: Dict[str, Any] = {}
    unknown: List[str] = []
    for k, v in d.items():
        if k in allowed:
            out[k] = v
        else:
            unknown.append(k)
    if unknown:
        from .utils import get_logger
        get_logger(__name__).warning("Config: chiavi ignote in %s ignorate: %s",
                                     cls.__name__, ", ".join(unknown))
    return out


def validate_config(cfg: Config) -> List[str]:
    """Verifica la coerenza dei parametri; ritorna l'elenco degli errori critici.

    Un elenco vuoto significa configurazione valida. Copre i casi che renderebbero
    invalido un verbale: importi/soglie negative, fasce incoerenti o sovrapposte,
    ore della finestra notturna fuori range, limite o tolleranza assurdi.
    """
    e: List[str] = []
    s = cfg.sanction
    if not (0 <= s.tolerance_percent <= 100):
        e.append(f"sanction.tolerance_percent fuori range [0,100]: {s.tolerance_percent}")
    if s.tolerance_min_kmh < 0:
        e.append(f"sanction.tolerance_min_kmh negativo: {s.tolerance_min_kmh}")
    if not (0.0 <= s.early_payment_discount < 1.0):
        e.append(f"sanction.early_payment_discount fuori range [0,1): {s.early_payment_discount}")
    if not (0 <= s.night_start_hour <= 23) or not (0 <= s.night_end_hour <= 23):
        e.append("sanction.night_start_hour/night_end_hour devono essere in [0,23]")
    for d in ("notification_deadline_days", "payment_deadline_days", "early_payment_days"):
        if getattr(s, d) <= 0:
            e.append(f"sanction.{d} deve essere positivo")
    if s.notification_costs_eur < 0:
        e.append("sanction.notification_costs_eur negativo")
    if not s.brackets:
        e.append("sanction.brackets vuoto: impossibile classificare le violazioni")
    prev_max = 0.0
    for b in s.brackets:
        if b.amount_min_eur < 0 or b.amount_max_eur < 0:
            e.append(f"fascia '{b.name}': importi negativi")
        if b.amount_min_eur > b.amount_max_eur:
            e.append(f"fascia '{b.name}': minimo ({b.amount_min_eur}) > massimo ({b.amount_max_eur})")
        if b.over_max_kmh is not None and b.over_min_kmh >= b.over_max_kmh:
            e.append(f"fascia '{b.name}': over_min >= over_max")
        if b.points_deducted < 0:
            e.append(f"fascia '{b.name}': punti negativi")
        if b.suspension_months[0] > b.suspension_months[1]:
            e.append(f"fascia '{b.name}': sospensione min > max")
        if b.over_min_kmh < prev_max:
            e.append(f"fascia '{b.name}': sovrapposta alla precedente (over_min < {prev_max})")
        prev_max = b.over_max_kmh if b.over_max_kmh is not None else b.over_min_kmh
    if cfg.location.speed_limit_kmh <= 0:
        e.append(f"location.speed_limit_kmh deve essere positivo: {cfg.location.speed_limit_kmh}")
    if cfg.speed.method not in ("line_pair", "world_regression"):
        e.append(f"speed.method sconosciuto: {cfg.speed.method}")
    if cfg.speed.min_track_points < 2:
        e.append("speed.min_track_points deve essere >= 2")
    return e


def load_config(path: Optional[str] = None, strict: bool = True) -> Config:
    """Carica la configurazione da YAML (se fornito) sovrascrivendo i default.

    Con ``strict=True`` (default) una configurazione incoerente solleva
    :class:`ConfigError` PRIMA di poter emettere un verbale invalido.
    """
    cfg = Config()
    if path:
        if not _HAS_YAML:  # pragma: no cover
            raise RuntimeError("PyYAML non disponibile: impossibile leggere %s" % path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
        except FileNotFoundError as exc:
            raise ConfigError(f"File di configurazione non trovato: {path}") from exc
        except yaml.YAMLError as exc:  # pragma: no cover - dipende da PyYAML
            raise ConfigError(f"YAML non valido in {path}: {exc}") from exc
        if not isinstance(raw, dict):
            raise ConfigError(f"La radice di {path} deve essere una mappa YAML")

        base = cfg.to_dict()
        merged = _merge(base, raw)

        sanction_raw = merged.get("sanction", {}) or {}
        brackets_raw = sanction_raw.get("brackets")
        sanction = SanctionConfig(**_known(
            SanctionConfig, {k: v for k, v in sanction_raw.items() if k != "brackets"}))
        if brackets_raw:
            sanction.brackets = _build_brackets(brackets_raw)

        cfg = Config(
            device=DeviceConfig(**_known(DeviceConfig, merged.get("device", {}))),
            location=LocationConfig(**_known(LocationConfig, merged.get("location", {}))),
            calibration=CalibrationConfig(**_known(CalibrationConfig, merged.get("calibration", {}))),
            speed=SpeedConfig(**_known(SpeedConfig, merged.get("speed", {}))),
            anpr=ANPRConfig(**_known(ANPRConfig, merged.get("anpr", {}))),
            recorder=RecorderConfig(**_known(RecorderConfig, merged.get("recorder", {}))),
            notifier=NotifierConfig(**_known(NotifierConfig, merged.get("notifier", {}))),
            sanction=sanction,
            registry_path=merged.get("registry_path", cfg.registry_path),
            tz_offset_hours=merged.get("tz_offset_hours", cfg.tz_offset_hours),
        )

    errors = validate_config(cfg)
    if errors and strict:
        raise ConfigError("Configurazione non valida:\n  - " + "\n  - ".join(errors))
    return cfg
