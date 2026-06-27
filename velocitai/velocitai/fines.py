"""Calcolo sanzionatorio a norma del Codice della Strada (Art. 142 / 202 / 201).

Passi (nell'ordine giuridicamente corretto):

1. **Abbattimento per tolleranza strumentale** sulla velocita' misurata:
   si sottrae il massimo tra il 5% e 5 km/h (regola a favore del trasgressore,
   coerente con la giurisprudenza e i decreti di omologazione).
2. **Determinazione della fascia** (Art. 142 commi 7/8/9/9-bis) in base al
   superamento del limite calcolato sulla velocita' contestabile.
3. **Maggiorazione notturna** (+1/3) se la violazione e' tra le 22:00 e le 07:00.
4. **Spese di accertamento e notificazione**.
5. **Pagamento in misura ridotta** (Art. 202): importo minimo edittale; con
   ulteriore **riduzione del 30%** se pagato entro 5 giorni.
6. **Termini perentori**: notifica entro 90 gg (Art. 201), pagamento entro 60 gg.

Gli importi edittali sono configurabili (aggiornamento biennale ISTAT, Art. 195).
"""

from __future__ import annotations

import re
from typing import Optional

from .config import SanctionConfig, SpeedBracket
from .models import Violation, OwnerRecord, Sanction, Verbale
from .utils import hour_of_day, is_finite_number

SECONDS_PER_DAY = 86400.0


def apply_tolerance(measured_kmh: float, cfg: SanctionConfig) -> float:
    """Velocita' contestabile = misurata - max(percentuale, minimo assoluto)."""
    if not is_finite_number(measured_kmh) or measured_kmh <= 0:
        return 0.0
    abatement = max(measured_kmh * cfg.tolerance_percent / 100.0,
                    cfg.tolerance_min_kmh)
    return max(0.0, measured_kmh - abatement)


def classify(overspeed_kmh: float, cfg: SanctionConfig) -> Optional[SpeedBracket]:
    """Restituisce la fascia applicabile, o ``None`` se non c'e' superamento.

    Un valore non finito (NaN/inf) NON viene mai classificato: restituisce
    ``None`` per non emettere mai una sanzione su un dato corrotto.
    """
    if not is_finite_number(overspeed_kmh) or overspeed_kmh <= 0:
        return None
    for b in cfg.brackets:
        within_upper = b.over_max_kmh is None or overspeed_kmh <= b.over_max_kmh
        if overspeed_kmh > b.over_min_kmh and within_upper:
            return b
    return cfg.brackets[-1] if cfg.brackets else None


def _is_night(ts: float, cfg: SanctionConfig, tz_offset_hours: float) -> bool:
    h = hour_of_day(ts, tz_offset_hours)
    # notte: dalle night_start (22) alle night_end (7), a cavallo della mezzanotte
    if cfg.night_start_hour <= cfg.night_end_hour:
        return cfg.night_start_hour <= h < cfg.night_end_hour
    return h >= cfg.night_start_hour or h < cfg.night_end_hour


class SanctionCalculator:
    def __init__(self, cfg: SanctionConfig, tz_offset_hours: float = 1.0) -> None:
        self.cfg = cfg
        self.tz = tz_offset_hours

    def compute_sanction(self, violation: Violation) -> Optional[Sanction]:
        bracket = classify(violation.overspeed_kmh, self.cfg)
        if bracket is None:
            return None

        amin, amax = bracket.amount_min_eur, bracket.amount_max_eur
        # Maggiorazione notturna +1/3 SOLO per le fasce eleggibili (commi 9 e
        # 9-bis, Art. 142 c. 8-bis) e solo tra le 22:00 e le 07:00.
        night = (bracket.night_eligible
                 and _is_night(violation.timestamp, self.cfg, self.tz))
        if night:
            f = 1.0 + self.cfg.night_surcharge_factor
            amin, amax = amin * f, amax * f

        costs = self.cfg.notification_costs_eur
        # Pagamento in misura ridotta (Art. 202 c.1): la somma e' pari al minimo
        # edittale, o a 1/3 del massimo se piu' favorevole (il minore dei due).
        reduced_base = min(amin, amax / 3.0)
        due = round(reduced_base + costs, 2)
        early = round(reduced_base * (1.0 - self.cfg.early_payment_discount) + costs, 2)

        notes = []
        if night:
            notes.append(f"Maggiorazione notturna +1/3 (Art. 142 c. 8-bis CdS): "
                         f"violazione tra le {self.cfg.night_start_hour}:00 e le "
                         f"{self.cfg.night_end_hour}:00.")
        notes.append(f"Importi comprensivi di spese di accertamento/notifica "
                     f"(EUR {costs:.2f}).")
        notes.append(f"Riduzione del {int(self.cfg.early_payment_discount*100)}% se "
                     f"pagato entro {self.cfg.early_payment_days} giorni (Art. 202 CdS).")

        return Sanction(
            articolo=bracket.articolo,
            comma=bracket.name,
            amount_min_eur=round(amin, 2),
            amount_max_eur=round(amax, 2),
            amount_due_eur=due,
            reduced_amount_eur=early,
            points_deducted=bracket.points_deducted,
            suspension_months=bracket.suspension_months,
            night_surcharge_applied=night,
            notes=" ".join(notes),
        )


def _protocol_number(violation: Violation, issued_at: float, tz: float) -> str:
    # violation_id contiene gia' la data (GGMMAAAA-NNNN); evitiamo ridondanze.
    # SICUREZZA (difesa in profondita'): device_id e violation_id confluiscono in
    # nomi file -> si ammettono solo caratteri sicuri, cosi' il protocollo non
    # puo' veicolare un path traversal anche se la sanitizzazione a valle mancasse.
    dev = re.sub(r"[^A-Za-z0-9_-]", "", (violation.device_id or "")) or "VELOCITAI"
    vid = re.sub(r"[^A-Za-z0-9_-]", "", (violation.violation_id or "")) or "0000"
    return f"PL-{dev[:32]}-{vid[:48]}"


def build_verbale(violation: Violation, owner: Optional[OwnerRecord],
                  sanction: Sanction, issued_at: float,
                  cfg: SanctionConfig, tz_offset_hours: float = 1.0) -> Verbale:
    """Assembla il verbale completo con numero di protocollo e termini di legge."""
    notification_deadline = violation.timestamp + cfg.notification_deadline_days * SECONDS_PER_DAY
    payment_deadline = issued_at + cfg.payment_deadline_days * SECONDS_PER_DAY
    return Verbale(
        protocol_number=_protocol_number(violation, issued_at, tz_offset_hours),
        violation=violation,
        owner=owner,
        sanction=sanction,
        issued_at=issued_at,
        notification_deadline=notification_deadline,
        payment_deadline=payment_deadline,
        status="ISSUED",
    )
