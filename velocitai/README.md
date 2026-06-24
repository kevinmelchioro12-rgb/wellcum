# VelociTAI

**Sistema di accertamento automatico dei limiti di velocità** — rilevamento
veicoli, stima della velocità da video, riconoscimento targa (ANPR),
registrazione della prova e generazione/notifica del verbale a norma
dell'**art. 142 del Codice della Strada**.

> ⚠️ **Stato del progetto: prototipo dimostrativo (MVP) funzionante.**
> L'intera catena gira end-to-end *oggi*, su CPU, senza GPU né telecamere, grazie
> a una modalità di simulazione deterministica. Non è ancora un prodotto
> *omologato* e *legalmente impiegabile* per emettere multe reali: per quello
> servono passaggi normativi e di metrologia legale descritti in
> [`docs/LEGAL_COMPLIANCE.md`](docs/LEGAL_COMPLIANCE.md). **Leggere quel
> documento prima di qualunque interlocuzione di vendita con la PA.**

---

## Cosa fa (pipeline)

```
  ┌─────────┐   ┌────────────┐   ┌───────────┐   ┌──────────────┐
  │ Frame   │──▶│ Rilevamento│──▶│ Tracking  │──▶│ Stima        │
  │ (video) │   │ veicoli    │   │ multi-obj │   │ velocità     │
  └─────────┘   └────────────┘   └───────────┘   └──────┬───────┘
                                                         │ supero limite?
                                            (dopo abbattimento tolleranza di legge)
                                                         ▼
  ┌──────────┐   ┌───────────┐   ┌─────────────┐   ┌──────────┐   ┌──────────┐
  │ Notifica │◀──│ Verbale   │◀──│ Sanzione    │◀──│ Visura   │◀──│ ANPR     │
  │ (PEC)    │   │ (art.142) │   │ art.142/202 │   │ intestat.│   │ targa    │
  └──────────┘   └───────────┘   └─────────────┘   └──────────┘   └────┬─────┘
                                                                       │
                                                          ┌────────────▼─────────────┐
                                                          │ Registrazione prova video │
                                                          │ + hash SHA-256 (custodia) │
                                                          └────────────────────────────┘
```

## Caratteristiche chiave

- **Stima velocità verificabile**: due metodi (regressione su coordinate mondo e
  *line-pair* a doppia linea, come gli autovelox/tutor), validati contro un
  ground-truth noto con accuratezza esatta nei test.
- **Tolleranza strumentale di legge**: abbattimento del 5% con minimo 5 km/h
  *a favore del trasgressore* — requisito imprescindibile per la validità.
- **ANPR italiano**: validazione del formato targa (`LL NNN LL`, lettere `I O Q U`
  escluse) e correzione posizionale degli errori OCR.
- **Calcolo sanzione completo**: fasce art. 142 commi 7/8/9/9-bis, decurtazione
  punti, sospensione patente, **maggiorazione notturna +1/3**, pagamento in
  misura ridotta (art. 202), spese di notifica e **termini perentori** (90 gg
  notifica, 60 gg pagamento).
- **Catena di custodia della prova**: pacchetto-prova con hash SHA-256.
- **Console operatore web** (dashboard) e **API JSON**, in sola libreria standard.
- **Backend pluggable**: i backend di produzione (YOLOv8, EasyOCR, OpenCV, PEC)
  si innestano senza toccare l'orchestratore.

## Quickstart (zero dipendenze)

```bash
cd velocitai

# 1) Demo end-to-end con stampa del primo verbale
python3 -m velocitai demo --config config/default.yaml --show-verbale 1

# 2) Console operatore web
python3 -m velocitai serve --config config/default.yaml --port 8080
#    -> apri http://127.0.0.1:8080

# 3) Test (34 test, nessuna dipendenza)
python3 -m unittest discover -s tests
```

Lo scenario dimostrativo simula 5 veicoli (limite 50 km/h): 2 conformi (di cui
uno *salvato* dall'abbattimento della tolleranza) e 3 in violazione, classificati
correttamente nei commi 8, 9 e 9-bis.

## Modalità di esecuzione

| | Modalità **simulata** (default) | Modalità **produzione** |
|---|---|---|
| Sorgente | scenario sintetico con ground-truth | flusso telecamera / file video |
| Rilevamento | `SimulatedDetector` | `YOLODetector` (YOLOv8) |
| ANPR | `SimulatedANPR` | `EasyOCRANPR` |
| Prova | manifest JSON + hash | MP4 (OpenCV) + hash |
| Dipendenze | **nessuna** (stdlib) | `requirements-prod.txt` |

La simulazione **non** è un mock vuoto: esercita realmente tracker, geometria,
stima velocità, validazione targa, calcolo sanzioni e generazione verbale. È il
modo per dimostrare e collaudare l'intera logica senza hardware.

## Struttura

```
velocitai/
├── velocitai/            # package (core stdlib-only)
│   ├── models.py         # modelli dati del dominio
│   ├── geometry.py       # calibrazione/omografia immagine→mondo
│   ├── detection.py      # rilevatore (simulato | YOLO)
│   ├── tracking.py       # tracker multi-oggetto (IoU)
│   ├── speed.py          # stima velocità (regressione | line-pair)
│   ├── anpr.py           # riconoscimento e validazione targa
│   ├── recorder.py       # pacchetto-prova + catena di custodia
│   ├── registry.py       # visura intestatario (mock PRA/Motorizzazione)
│   ├── fines.py          # calcolo sanzione art. 142/202 CdS
│   ├── notifier.py       # verbale + notifica (PEC simulata)
│   ├── pipeline.py       # orchestratore
│   ├── scenario.py       # mondo sintetico con ground-truth
│   ├── dashboard.py      # console operatore web
│   └── cli.py            # interfaccia a riga di comando
├── config/default.yaml   # configurazione postazione
├── data/registry/        # registro intestatari di esempio
├── tests/                # 34 test (unittest)
├── examples/             # uso programmatico
└── docs/                 # conformità legale, architettura, backend, proposta
```

## Documentazione

- [`docs/LEGAL_COMPLIANCE.md`](docs/LEGAL_COMPLIANCE.md) — **percorso per vendere
  alla PA**: omologazione MIT, metrologia legale, GDPR, requisiti del verbale.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — moduli, flusso dati, variante streaming.
- [`docs/PRODUCTION_BACKENDS.md`](docs/PRODUCTION_BACKENDS.md) — innesto YOLO/EasyOCR/OpenCV/PEC.
- [`docs/PROPOSTA_COMMERCIALE.md`](docs/PROPOSTA_COMMERCIALE.md) — scheda prodotto / executive summary.

## Avvertenza

Software fornito a scopo dimostrativo. Gli importi e i riferimenti normativi sono
configurabili e vanno verificati con l'ufficio legale: gli importi edittali
dell'art. 142 sono soggetti ad **aggiornamento biennale ISTAT** (art. 195 CdS).
L'impiego in esercizio per l'emissione di sanzioni è subordinato all'omologazione
dello strumento e alla conformità normativa (vedi `docs/LEGAL_COMPLIANCE.md`).
