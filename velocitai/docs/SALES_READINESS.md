# VelociTAI — Prontezza alla vendita alla PA italiana

Questo documento è la **checklist operativa** per portare VelociTAI dalla
condizione attuale (prodotto software maturo e collaudato) alla vendita e
all'esercizio presso Enti pubblici italiani. È volutamente **onesto** su ciò che
è pronto e su ciò che richiede passaggi esterni.

## 1. Sintesi: a che punto siamo

| Dimensione | Stato | Note |
|---|---|---|
| **Prodotto software** | ✅ Pronto | core stdlib, 98 test, resilienza, sicurezza by-design |
| **Sicurezza/GDPR (tecnica)** | ✅ Pronto | HMAC, audit-log, redazione PII, permessi, anti-DoS (`SECURITY.md`) |
| **Backend di produzione** | 🟡 Scaffolding | YOLO/EasyOCR/OpenCV/PEC da collaudare su hardware reale |
| **Omologazione MIT** | ⛔ Da avviare | requisito di legge per multe valide — iter ministeriale |
| **Taratura periodica** | ⛔ Da impostare | laboratorio accreditato (Corte Cost. 113/2015) |
| **DPIA / GDPR (formale)** | 🟡 Da redigere | impianto tecnico pronto; serve il documento e la nomina |
| **Qualificazione ACN (SaaS)** | 🟡 Da ottenere | necessaria per il cloud venduto alla PA |
| **Convenzione PRA/ANV** | ⛔ Da stipulare | per le visure intestatario |
| **Iscrizione MEPA / partner gara** | ⛔ Da fare | canale di acquisto della PA |

Legenda: ✅ pronto · 🟡 in carico a noi, fattibile in settimane · ⛔ dipende da terzi/iter.

## 2. Percorso di conformità (perché non si vende "domani")

Una multa è **annullabile** se lo strumento non è omologato e tarato
(giurisprudenza consolidata; Cassazione 2024 ha ribadito la distinzione tra
*approvazione* e *omologazione*). Quindi l'ordine corretto è:

1. **Pilota tecnico** (4–8 settimane): backend ML su strada reale, calibrazione e
   raccolta dati di una postazione campione, confronto con strumento di
   riferimento.
2. **Metrologia legale**: domanda di **omologazione al MIT** della catena di
   misura (hardware + VelociTAI) + piano di **taratura periodica**. È il collo di
   bottiglia (mesi); va avviato per primo, in parallelo al resto.
3. **Compliance dati**: **DPIA**, registro dei trattamenti, nomina responsabili,
   **convenzione PRA/ANV** per le visure, qualificazione **ACN** del SaaS.
4. **Procurement**: iscrizione **MEPA/CONSIP** o partnership con un fornitore già
   accreditato; predisposizione del **capitolato** (vedi `CAPITOLATO_TECNICO.md`).

## 3. Cosa possiamo vendere *subito* (senza omologazione)

- **Licenza del back-office e dell'API** per la gestione/notifica dei verbali a
  partire da accertamenti di strumenti **già omologati** di terzi (VelociTAI come
  motore di calcolo sanzione + catena di custodia + gestionale).
- **Progetti pilota** e **proof-of-value** retribuiti.
- **Servizi**: integrazione, DPIA, formazione, assistenza all'omologazione.

Questo permette **ricavi e referenze** mentre l'omologazione del modulo di misura
procede in parallelo.

## 4. Modello di partnership (consigliato)

VelociTAI **non produce hardware**. Strategia: accordo con **1–2 produttori di
postazioni/telecamere omologate** (o laboratori metrologici) per:
- includere VelociTAI come modulo di accertamento/AI nelle loro forniture;
- condividere il costo/tempo dell'omologazione della catena di misura;
- accedere ai loro canali di gara già attivi.

In alternativa/aggiunta: integrazione **OEM** nei gestionali esistenti
(PMWEB/Concilia/Cityware) come motore di calcolo e prova.

## 5. Differenziatori da vendere (value proposition)

1. **Difendibilità del verbale** → meno annullamenti in autotutela e meno ricorsi
   accolti (tolleranza di legge, riferimenti normativi puntuali, termini, catena
   di custodia **HMAC** verificabile, audit-log tamper-evident).
2. **Sicurezza e GDPR by-design** → riduce il rischio sanzioni Garante e data
   breach (redazione PII, cifratura/permessi, accessi controllati).
3. **Affidabilità operativa** → isolamento guasti, auto-riparazione, idempotenza
   anti doppia-multa: meno fermi e meno errori contestabili.
4. **Aggiornamento normativo come servizio** → importi ISTAT/CdS sempre allineati.
5. **Nessun lock-in** → backend e gestionali intercambiabili; API aperte.

## 6. Prossimi passi concreti (90 giorni)

- **Settimana 1–2**: individuare 1 Comando di Polizia Locale pilota e 1 partner
  hardware; preparare demo (incl. `examples/video_demo.py`) e offerta.
- **Settimana 2–6**: pilota tecnico su una postazione; avvio domanda omologazione
  (con partner) e bozza DPIA.
- **Settimana 6–12**: iscrizione MEPA/accordo OEM; prima offerta formale
  (modello SaaS o pay-per-verbale); piano di qualificazione ACN.

## 7. Riferimenti
- `LEGAL_COMPLIANCE.md` — dettaglio normativo e metrologico.
- `PRICING.md` — listino e modelli di prezzo.
- `CAPITOLATO_TECNICO.md` — specifica tecnica per gare.
- `SECURITY.md` — controlli di sicurezza e checklist di hardening.
