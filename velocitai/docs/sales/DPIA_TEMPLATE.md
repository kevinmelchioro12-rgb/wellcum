# DPIA — Bozza/scheletro (Valutazione d'Impatto sulla Protezione dei Dati)

> Bozza di lavoro ai sensi dell'**art. 35 GDPR**. NON è una DPIA approvata: va
> completata e validata dal **DPO/RPD** dell'Ente (titolare del trattamento) e,
> se necessario, sottoposta a consultazione preventiva del Garante. Serve a
> velocizzare la pratica, non a sostituirla.

## 1. Titolarità e ruoli
- **Titolare del trattamento**: [Ente / Comune] (l'autorità che accerta).
- **Responsabile del trattamento (art. 28)**: VelociTAI / fornitore del servizio.
- **DPO/RPD**: [nominativo e contatti].

## 2. Descrizione del trattamento
- **Finalità**: accertamento delle violazioni dei limiti di velocità (Art. 142
  CdS) e gestione del procedimento sanzionatorio. Base giuridica: **obbligo
  legale / interesse pubblico** (art. 6(1)(c)(e) GDPR; CdS).
- **Dati trattati**: targa, immagini/video del veicolo al momento della
  violazione, velocità, luogo/ora; per i soli trasgressori: dati dell'intestatario
  da PRA/ANV (nome, indirizzo, codice fiscale, PEC).
- **Categorie di interessati**: conducenti/intestatari dei veicoli in violazione.
- **Conservazione**: per il tempo necessario al procedimento e ai termini di
  legge/contenzioso; **i veicoli conformi non generano dati personali conservati**.

## 3. Necessità e proporzionalità
- Trattamento limitato ai veicoli in **violazione** (minimizzazione).
- Postazione giustificata da **esigenze di sicurezza** (decreto autovelox 2025).
- Nessun uso secondario; niente profilazione.

## 4. Rischi e misure (mappa sui controlli VelociTAI)
| Rischio | Misura |
|---|---|
| Accesso non autorizzato ai dati | controllo accessi (token), TLS, permessi 0600/0700 |
| Esfiltrazione di PII (log) | **redazione PII** automatica nei log |
| Alterazione/manomissione della prova | catena di custodia **HMAC** + audit-log a catena di hash |
| Doppio trattamento/errore | **idempotenza** (no doppie multe), validazioni |
| Indisponibilità del servizio | resilienza, dead-letter, auto-riparazione |
| Conservazione eccessiva | retention configurata + potatura (`doctor --prune-ledger-days`) |
| Trasferimento dati extra-UE | hosting **UE**; nessun trasferimento non necessario |

## 5. Diritti degli interessati
Informativa sul verbale; esercizio dei diritti (accesso, rettifica) presso il
Titolare; modalità di ricorso (Prefetto/Giudice di Pace) indicate nell'atto.

## 6. Misure organizzative
Nomina responsabili e autorizzati, formazione operatori, registro dei trattamenti,
contratto art. 28 con il fornitore, piano di **data breach**.

## 7. Esito (a cura del DPO)
- [ ] Rischi residui accettabili → trattamento ammesso.
- [ ] Necessaria consultazione preventiva del Garante (art. 36).

_Redatto da: [.....] · Validato dal DPO: [.....] · Data: [.....]_
