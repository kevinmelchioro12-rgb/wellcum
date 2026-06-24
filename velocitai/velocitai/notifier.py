"""Generazione e notifica del verbale.

``render_verbale_text`` produce il testo del verbale con tutti i campi richiesti
(autorita', strumento e omologazione, luogo/data, veicolo e intestatario,
velocita' misurata e contestabile, sanzione, termini, hash della prova,
modalita' di pagamento e ricorso).

Il :class:`Notifier` lo scrive su file e ne simula la notifica. In esercizio il
backend ``pec`` invia la notificazione via PEC entro 90 giorni (Art. 201 CdS).
"""

from __future__ import annotations

import os
from typing import Optional

from .config import Config
from .models import Verbale
from .utils import format_timestamp, write_json, get_logger

log = get_logger(__name__)


def render_verbale_text(verbale: Verbale, config: Config) -> str:
    v = verbale.violation
    s = verbale.sanction
    o = verbale.owner
    tz = config.tz_offset_hours
    loc = v.location

    susp = ""
    if s.suspension_months != (0, 0):
        susp = (f"  - Sospensione patente: da {s.suspension_months[0]} a "
                f"{s.suspension_months[1]} mesi\n")

    owner_block = (
        f"  Intestatario : {o.full_name}\n"
        f"  Codice fisc. : {o.fiscal_code}\n"
        f"  Residenza    : {o.address}, {o.postal_code} {o.municipality} ({o.province})\n"
        f"  Veicolo      : {o.vehicle_make} {o.vehicle_model}\n"
        if o else
        "  Intestatario : NON DISPONIBILE (richiesta visura PRA/Motorizzazione in corso)\n"
    )

    return f"""\
================================================================================
                      VERBALE DI CONTESTAZIONE / NOTIFICAZIONE
                  Violazione dei limiti di velocita' - Art. 142 CdS
================================================================================
Autorita' accertatrice : {config.device.operator_authority}
Numero verbale         : {verbale.protocol_number}
Emesso il              : {format_timestamp(verbale.issued_at, tz)}

STRUMENTO DI MISURA
  Dispositivo          : {v.device_id}
  Decreto omologazione : {config.device.homologation_number}
  Ultima taratura      : {config.device.last_calibration_date}

LUOGO E DATA DELLA VIOLAZIONE
  Strada               : {loc.road_name}
  Comune               : {loc.municipality} ({loc.province})
  Direzione            : {loc.direction}
  Coordinate           : {loc.latitude:.5f}, {loc.longitude:.5f}
  Data e ora           : {format_timestamp(v.timestamp, tz)}

VEICOLO
  Targa rilevata       : {v.plate.text}  (confidenza ANPR {v.plate.confidence:.2f})
{owner_block}\
RILEVAZIONE DELLA VELOCITA'
  Limite vigente       : {v.speed_limit_kmh:.0f} km/h
  Velocita' misurata   : {v.measured_speed_kmh:.1f} km/h
  Tolleranza applicata : -{v.measured_speed_kmh - v.contested_speed_kmh:.1f} km/h (a favore)
  Velocita' contestata : {v.contested_speed_kmh:.1f} km/h
  Superamento          : +{v.overspeed_kmh:.1f} km/h
  Metodo               : {v.measurement.method.value} (confidenza {v.measurement.confidence:.2f})

SANZIONE - {s.articolo}
  Sanzione amministrativa pecuniaria: da EUR {s.amount_min_eur:.2f} a EUR {s.amount_max_eur:.2f}
  Pagamento in misura ridotta (entro {config.sanction.payment_deadline_days} gg): EUR {s.amount_due_eur:.2f}
  Importo ridotto (entro {config.sanction.early_payment_days} gg): EUR {s.reduced_amount_eur:.2f}
  Decurtazione punti   : {s.points_deducted}
{susp}\
  Note                 : {s.notes}

TERMINI
  Notifica entro       : {format_timestamp(verbale.notification_deadline, tz)} (Art. 201 CdS)
  Pagamento entro      : {format_timestamp(verbale.payment_deadline, tz)} (Art. 203 CdS)

PROVA (catena di custodia)
  Pacchetto prova      : {v.evidence.clip_path}
  Hash SHA-256         : {v.evidence.sha256}
  Fotogrammi           : {v.evidence.frame_count}

RICORSI
  - Ricorso al Prefetto entro 60 giorni (Art. 203 CdS), oppure
  - Ricorso al Giudice di Pace entro 30 giorni (Art. 204-bis CdS).
================================================================================
"""


class Notifier:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.output_dir = config.notifier.output_dir

    def notify(self, verbale: Verbale) -> dict:
        os.makedirs(self.output_dir, exist_ok=True)
        text = render_verbale_text(verbale, self.config)
        base = os.path.join(self.output_dir, verbale.protocol_number)
        txt_path = base + ".txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        json_path = base + ".json"
        write_json(json_path, verbale.to_dict())

        mode = self.config.notifier.mode
        recipient = verbale.owner.pec_email if (verbale.owner and verbale.owner.pec_email) else None
        status = "WRITTEN"
        if mode == "simulated":
            status = "SIMULATED_DISPATCH"
            log.info("Verbale %s -> notifica simulata a %s",
                     verbale.protocol_number, recipient or "intestatario sconosciuto")
        elif mode == "pec":  # pragma: no cover
            status = self._send_pec(verbale, text, recipient)

        verbale.status = "NOTIFIED" if status.endswith("DISPATCH") else verbale.status
        return {
            "protocol_number": verbale.protocol_number,
            "txt_path": txt_path,
            "json_path": json_path,
            "recipient": recipient,
            "status": status,
        }

    def _send_pec(self, verbale: Verbale, text: str, recipient: Optional[str]) -> str:  # pragma: no cover
        raise NotImplementedError(
            "Integrazione PEC: invio notificazione tramite gestore PEC accreditato. "
            "Vedi docs/PRODUCTION_BACKENDS.md."
        )
