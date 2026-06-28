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
- **Difendibilità del verbale**: applicazione corretta della **tolleranza di
  legge** (5% / min 5 km/h), riferimenti normativi puntuali, **termini perentori**
  gestiti, **catena di custodia** della prova con hash.
- **Architettura aperta**: backend ML intercambiabili (YOLOv8/EasyOCR), nessun
  lock-in hardware; integrabile con il gestionale del Comando.
- **Time-to-demo immediato**: dimostrazione end-to-end su laptop, senza GPU.
- **Privacy by design**: i veicoli conformi non vengono conservati; predisposto
  per DPIA e conformità GDPR.

## Cosa è pronto oggi (MVP)
- Pipeline completa e testata (34 test automatici).
- Stima velocità con due metodi (regressione / line-pair) validati su ground-truth.
- ANPR italiano con validazione formato e correzione OCR.
- Calcolo sanzione art. 142 (commi 7/8/9/9-bis), punti, sospensione, maggiorazione
  notturna, misura ridotta, spese e termini.
- Console operatore web + API JSON.

## Cosa serve per l'esercizio (roadmap)
Dettaglio in [`LEGAL_COMPLIANCE.md`](LEGAL_COMPLIANCE.md). Sintesi:

| Fase | Attività | Tempo indicativo |
|---|---|---|
| 1. Pilota tecnico | backend ML su strada, calibrazione postazione | 4–8 settimane |
| 2. Metrologia legale | omologazione MIT + taratura | dipende da iter ministeriale |
| 3. Compliance | DPIA, GDPR, convenzione ANV/PRA | 4–6 settimane |
| 4. Procurement | iscrizione MEPA / gara | settimane–mesi |

## Modello di vendita alla PA
- **MEPA/Consip** per forniture sotto soglia; **gara d'appalto** per progetti
  rilevanti; possibili **accordi quadro** con più Enti.
- Licenza software + canone di manutenzione/aggiornamenti normativi (gli importi
  edittali cambiano ogni 2 anni: l'aggiornamento è parte del servizio).
- Opzione **as-a-service** (postazione gestita) o **on-premise**.

## Realismo sui tempi
> Un sistema che emette multe valide **non** è vendibile/operativo «entro domani»:
> dipende da omologazione e gara pubblica. Ciò che è disponibile da subito è
> questo **MVP dimostrabile** e una **roadmap credibile** — il modo concreto per
> aprire le interlocuzioni con Comandi di Polizia Locale ed Enti.

## Prossimo passo consigliato
1. Demo live a una Polizia Locale interessata (`make serve`).
2. Definizione di un **pilota** su una postazione reale.
3. Avvio parallelo dell'iter di **omologazione** e dell'iscrizione **MEPA**.
