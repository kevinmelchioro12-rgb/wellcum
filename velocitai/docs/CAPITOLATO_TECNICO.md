# VelociTAI — Capitolato tecnico (schema per gare/MEPA)

Schema di **specifica tecnica** riutilizzabile in capitolati di gara o RdO MEPA.
Le voci sono mappate sulle capacità **reali e collaudate** del prodotto; le voci
soggette a omologazione/hardware sono marcate.

## 1. Oggetto
Fornitura di un sistema software di **accertamento automatico delle violazioni
dei limiti di velocità** (art. 142 CdS) con gestione del procedimento
sanzionatorio: rilevamento, misura, riconoscimento targa, prova, calcolo
sanzione, verbale e notifica.

## 2. Requisiti funzionali
| # | Requisito | Stato |
|---|---|---|
| F1 | Rilevamento e tracciamento veicoli da flusso video | ✅ (sim. + backend YOLO/MOG2) |
| F2 | Misura della velocità con metodo verificabile (≥1) | ✅ regressione mondo e line-pair |
| F3 | Applicazione **tolleranza di legge** (5% / min 5 km/h) | ✅ |
| F4 | Riconoscimento targa (ANPR) formato italiano + correzione OCR | ✅ |
| F5 | Calcolo sanzione art. 142 commi 7/8/9/9-bis, punti, sospensione | ✅ |
| F6 | Maggiorazione notturna (solo commi 9/9-bis), misura ridotta (art. 202) | ✅ |
| F7 | Generazione **verbale** completo e **notifica** (PEC) | ✅ (PEC: backend prod.) |
| F8 | **Catena di custodia** della prova con integrità verificabile | ✅ HMAC-SHA256 |
| F9 | Visura intestatario (PRA/ANV) | 🟡 interfaccia pronta, convenzione esterna |
| F10 | Console operatore + API di integrazione | ✅ dashboard web + API JSON |
| F11 | Gestione stati verbale (emesso/notificato/pagato/contestato) | ✅ |

## 3. Requisiti prestazionali e di affidabilità
| # | Requisito | Copertura VelociTAI |
|---|---|---|
| P1 | Continuità di servizio: un errore non blocca l'accertamento | ✅ isolamento guasti per-veicolo |
| P2 | Ripresa automatica da guasti transitori | ✅ retry, circuit breaker, **dead-letter** |
| P3 | Nessuna **doppia sanzione** sullo stesso evento | ✅ ledger idempotente |
| P4 | Integrità degli atti a fronte di crash | ✅ scritture atomiche |
| P5 | Auto-diagnosi e verifica integrità prove | ✅ comando `doctor` |
| P6 | Robustezza a dati corrotti (NaN/inf) e input ostili | ✅ sanitizzazione + fuzzing |

## 4. Requisiti di sicurezza (rif. `SECURITY.md`)
| # | Requisito | Copertura |
|---|---|---|
| S1 | Integrità/non-ripudio della prova | ✅ HMAC (chiave segreta), predisposto a firma qualificata |
| S2 | Registro di audit a prova di manomissione | ✅ audit-log a catena di hash |
| S3 | Protezione dati personali (GDPR) | ✅ redazione PII nei log, permessi 0600/0700, segreti da env |
| S4 | Controllo accessi e trasporto | ✅ token + header di sicurezza; TLS via reverse-proxy |
| S5 | Resistenza ad abusi (DoS, injection, path traversal, XSS) | ✅ limiti, sanitizzazione, CSP, rate-limit |
| S6 | Cifratura at-rest, firma asimmetrica, marca temporale RFC3161 | 🟡 in checklist di produzione |

## 5. Conformità normativa
| # | Requisito | Stato |
|---|---|---|
| N1 | Strumento **omologato MIT** | ⛔ da ottenere (catena di misura) |
| N2 | **Taratura periodica** documentata | ⛔ laboratorio accreditato |
| N3 | Aggiornamento importi edittali (ISTAT/CdS, art. 195) | ✅ configurabile, incluso nel canone |
| N4 | Termini perentori (notifica 90 gg, pagamento 60 gg) | ✅ gestiti |
| N5 | **DPIA** e registro trattamenti | 🟡 da redigere |
| N6 | Qualificazione **ACN** del SaaS | 🟡 da ottenere |

## 6. Livelli di servizio (SLA proposti)
| Livello | Disponibilità | Presa in carico guasto bloccante | Aggiornamenti normativi |
|---|---|---|---|
| Standard | 99,0% | entro 8 ore lavorative | entro 30 gg dall'entrata in vigore |
| Premium | 99,5% | entro 4 ore (H24 opz.) | entro 10 gg |

## 7. Documentazione fornita
Manuale operatore, manuale di installazione/calibrazione, documentazione API,
`SECURITY.md`, `LEGAL_COMPLIANCE.md`, evidenze dei test (98 test automatici) e
report di collaudo del pilota.

## 8. Reversibilità e anti lock-in
Formati aperti (JSON), API documentate, backend ML/gestionali intercambiabili,
export integrale dei dati e delle prove a fine contratto.

---
*Le voci ⛔/🟡 fanno parte del percorso descritto in `SALES_READINESS.md`; le ✅
sono dimostrabili oggi con la suite di test e la demo (`examples/video_demo.py`).*
