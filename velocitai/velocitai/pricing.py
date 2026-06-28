"""Modello di prezzo e generatore di preventivo/TCO (vedi docs/PRICING.md).

Strumento commerciale: dato il numero di postazioni, il modello e la durata,
calcola un'offerta indicativa e il TCO. I valori riflettono il listino in
``docs/PRICING.md`` e sono **indicativi** (IVA esclusa), da personalizzare in
sede di offerta. Nessuna dipendenza esterna.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# --- Listino (IVA esclusa) — allineato a docs/PRICING.md ---------------------
SAAS_PER_POSTAZIONE_ANNO = 6000.0
SAAS_CENTRALE_ANNO = 7200.0
SAAS_SETUP_POSTAZIONE = 3500.0

ONPREM_EDGE = 9500.0
ONPREM_CENTRALE = 19000.0
ONPREM_CANONE_PCT = 0.20
ONPREM_SETUP_POSTAZIONE = 4500.0

PPV_PER_VERBALE = 1.20
PPV_MINIMO_MESE_POSTAZIONE = 350.0

TURNKEY_MESE_POSTAZIONE = 2650.0   # media €2.400–2.900 (hardware incluso)

MODELS = ("saas", "onprem", "ppv", "turnkey")


def _volume_discount(n: int) -> float:
    """Sconto volume per postazioni (SaaS/on-prem): 5+ 10%, 10+ 18%."""
    if n >= 10:
        return 0.18
    if n >= 5:
        return 0.10
    return 0.0


@dataclass
class Offer:
    model: str
    postazioni: int
    anni: int
    one_time: float = 0.0
    recurring_year: float = 0.0
    discount_pct: float = 0.0
    tco: float = 0.0
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return {
            "modello": self.model,
            "postazioni": self.postazioni,
            "anni": self.anni,
            "una_tantum_eur": round(self.one_time, 2),
            "canone_annuo_eur": round(self.recurring_year, 2),
            "sconto_volume_pct": round(self.discount_pct * 100, 1),
            "tco_eur": round(self.tco, 2),
            "note": self.notes,
        }


def compute_offer(postazioni: int, model: str = "saas", anni: int = 3,
                  con_centrale: bool = True, verbali_anno_postazione: int = 3750
                  ) -> Offer:
    """Calcola un'offerta indicativa e il TCO sull'orizzonte ``anni``.

    ``verbali_anno_postazione`` serve solo al modello ``ppv``.
    """
    if postazioni < 1:
        raise ValueError("postazioni deve essere >= 1")
    if anni < 1:
        raise ValueError("anni deve essere >= 1")
    if model not in MODELS:
        raise ValueError(f"modello sconosciuto: {model} (usa {MODELS})")

    o = Offer(model=model, postazioni=postazioni, anni=anni)

    if model == "saas":
        disc = _volume_discount(postazioni)
        o.discount_pct = disc
        per_post = SAAS_PER_POSTAZIONE_ANNO * (1 - disc)
        o.recurring_year = per_post * postazioni + (SAAS_CENTRALE_ANNO if con_centrale else 0.0)
        o.one_time = SAAS_SETUP_POSTAZIONE * postazioni
        o.notes.append("Canone tutto incluso (Edge + cloud back-office + SLA + aggiornamenti).")
    elif model == "onprem":
        disc = _volume_discount(postazioni)
        o.discount_pct = disc
        lic = ONPREM_EDGE * postazioni * (1 - disc) + (ONPREM_CENTRALE if con_centrale else 0.0)
        o.one_time = lic + ONPREM_SETUP_POSTAZIONE * postazioni
        o.recurring_year = lic * ONPREM_CANONE_PCT
        o.notes.append(f"Canone annuo = {int(ONPREM_CANONE_PCT*100)}% delle licenze (manutenzione+aggiornamenti+SLA).")
    elif model == "ppv":
        per_post_year = max(
            PPV_PER_VERBALE * verbali_anno_postazione,
            PPV_MINIMO_MESE_POSTAZIONE * 12.0)
        o.recurring_year = per_post_year * postazioni
        o.notes.append(f"€{PPV_PER_VERBALE:.2f}/verbale, minimo €{PPV_MINIMO_MESE_POSTAZIONE:.0f}/mese/postazione.")
        o.notes.append("Nessun investimento iniziale; rischio condiviso.")
    elif model == "turnkey":
        o.recurring_year = TURNKEY_MESE_POSTAZIONE * 12.0 * postazioni
        o.notes.append("Noleggio full-service: hardware omologato + software + manutenzione + SLA.")

    o.tco = o.one_time + o.recurring_year * anni
    return o
