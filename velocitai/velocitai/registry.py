"""Risoluzione intestatario del veicolo a partire dalla targa.

In esercizio reale questo dato proviene da fonti ufficiali:
- **PRA / ACI** (Pubblico Registro Automobilistico) per la proprieta';
- **Motorizzazione (DT) / Archivio Nazionale Veicoli** per i dati tecnici.
L'accesso e' regolato (convenzioni, finalita' istituzionali, GDPR).

Qui si usa un registro JSON locale come mock. Il backend reale deve solo
implementare lo stesso metodo ``lookup(plate) -> OwnerRecord | None``.
"""

from __future__ import annotations

from typing import Dict, Optional

from .anpr import normalize_plate
from .models import OwnerRecord
from .utils import read_json


class OwnerRegistry:
    def __init__(self, records: Dict[str, OwnerRecord]) -> None:
        self._records = records

    @classmethod
    def from_json(cls, path: str) -> "OwnerRegistry":
        raw = read_json(path)
        records: Dict[str, OwnerRecord] = {}
        for item in raw:
            plate = normalize_plate(item["plate"])
            records[plate] = OwnerRecord(
                plate=plate,
                full_name=item.get("full_name", ""),
                fiscal_code=item.get("fiscal_code", ""),
                address=item.get("address", ""),
                municipality=item.get("municipality", ""),
                province=item.get("province", ""),
                postal_code=item.get("postal_code", ""),
                vehicle_make=item.get("vehicle_make", ""),
                vehicle_model=item.get("vehicle_model", ""),
                pec_email=item.get("pec_email", ""),
            )
        return cls(records)

    def lookup(self, plate: str) -> Optional[OwnerRecord]:
        return self._records.get(normalize_plate(plate))
