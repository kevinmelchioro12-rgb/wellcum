# VelociTAI — Scheda prodotto / Executive summary

## Il problema
L'eccesso di velocità è tra le prime cause di incidentalità grave. Gli Enti
locali necessitano di sistemi di accertamento **automatici, affidabili e
giuridicamente solidi**, che riducano il contenzioso e i costi di gestione del
procedimento sanzionatorio.

## La soluzione
VelociTAI è una piattaforma software di accertamento automatico dei limiti di
velocità che copre l'intero ciclo: **rilevamento veicolo → misura velocità →
riconoscimento targa → prova video → calcolo sanzione → verbale → notifica PEC**.

### Differenziatori
- **Difendibilità del verbale**: tolleranza di legge (5% / min 5 km/h),
  riferimenti normativi puntuali, termini perentori, **catena di custodia HMAC**
  (prova non falsificabile) e **audit-log a prova di manomissione** → meno
  annullamenti e ricorsi accolti.
- **Sicurezza e GDPR by-design**: redazione PII, permessi restrittivi, controllo
  accessi, anti-DoS/injection (vedi [`SECURITY.md`](SECURITY.md)).
- **Affidabilità operativa**: isolamento guasti, auto-riparazione, idempotenza
  anti doppia-multa (vedi [`RESILIENCE.md`](RESILIENCE.md)).
- **Architettura aperta**: backend ML/gestionali intercambiabili, nessun lock-in.
- **Time-to-demo immediato**: end-to-end su laptop, senza GPU — inclusa una
  **demo VIDEO reale** (`examples/video_demo.py`).

## Cosa è pronto oggi
- Pipeline completa e testata: **98 test automatici**, fuzzing di robustezza e di
  sicurezza.
- Stima velocità (regressione / line-pair) validata su ground-truth; demo che
  rileva l'infrazione **dai pixel di un video** e produce la sanzione.
- ANPR italiano con validazione formato e correzione OCR.
- Calcolo sanzione art. 142 (commi 7/8/9/9-bis), punti, sospensione, maggiorazione
  notturna (commi 9/9-bis), misura ridotta (art. 202), spese e termini.
- Resilienza/auto-riparazione, sicurezza by-design, console web + API JSON,
  comando di auto-diagnosi `doctor`.

## Cosa serve per l'esercizio (roadmap)
Dettaglio in [`LEGAL_COMPLIANCE.md`](LEGAL_COMPLIANCE.md). Sintesi:

| Fase | Attività | Tempo indicativo |
|---|---|---|
| 1. Pilota tecnico | backend ML su strada, calibrazione postazione | 4–8 settimane |
| 2. Metrologia legale | omologazione MIT + taratura | dipende da iter ministeriale |
| 3. Compliance | DPIA, GDPR, convenzione ANV/PRA | 4–6 settimane |
| 4. Procurement | iscrizione MEPA / gara | settimane–mesi |

## Modello di vendita e prezzo
Tre modelli a scelta dell'Ente (listino completo in [`PRICING.md`](PRICING.md)):

| Modello | Prezzo di riferimento | Per chi |
|---|---|---|
| **SaaS tutto incluso** (consigliato) | **€6.000 / postazione / anno** (+ setup) | Enti che preferiscono OPEX |
| **Licenza on-premise** | **€9.500** Edge + **€19.000** Centrale + 20%/anno | Enti con infrastruttura propria |
| **Pay-per-verbale** (a risultato) | **€1,20 / verbale** notificato | piccoli Comuni / avvio a basso rischio |
| **Chiavi in mano** (con partner HW) | **€2.400–2.900 / mese / postazione** | fornitura gestita unica |

Acquisto via **MEPA/CONSIP** (sotto soglia) o **gara** (D.Lgs 36/2023); sconti
volume e accordi quadro multi-Ente. Capitolato pronto in
[`CAPITOLATO_TECNICO.md`](CAPITOLATO_TECNICO.md).

## Realismo sui tempi
> Un sistema che emette multe valide **non** è vendibile/operativo «entro domani»:
> dipende da omologazione e gara pubblica. Ciò che è disponibile da subito è
> questo **MVP dimostrabile** e una **roadmap credibile** — il modo concreto per
> aprire le interlocuzioni con Comandi di Polizia Locale ed Enti.

## Prossimo passo consigliato
1. Demo live a una Polizia Locale interessata (`python3 -m velocitai serve`) e
   demo VIDEO (`python3 examples/video_demo.py`).
2. Definizione di un **pilota** su una postazione reale e di un **partner
   hardware** per l'omologazione della catena di misura.
3. Avvio parallelo dell'iter di **omologazione** e dell'iscrizione **MEPA**.

Piano operativo a 90 giorni e checklist di prontezza completa in
[`SALES_READINESS.md`](SALES_READINESS.md).
