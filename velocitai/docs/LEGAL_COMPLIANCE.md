# Conformità legale e percorso verso l'impiego in esercizio

> Questo documento è la parte **più importante** del progetto per chiunque
> intenda proporre il sistema a una Pubblica Amministrazione. Il software è un
> prototipo funzionante; trasformarlo in uno strumento che emette sanzioni
> *valide e non impugnabili* richiede passaggi normativi, metrologici e
> procedurali che **non dipendono dal codice** e **non si esauriscono in un
> giorno**. Qui sono elencati con onestà.

## 1. Sintesi onesta

| Aspetto | Stato nel prototipo | Necessario per l'esercizio |
|---|---|---|
| Pipeline tecnica (rilevamento→verbale) | ✅ funzionante end-to-end | Backend ML reali collaudati sul campo |
| Stima velocità | ✅ accurata in simulazione | Validazione metrologica su strumento fisico |
| Calcolo sanzione art. 142 | ✅ implementato e testato | Verifica importi vigenti con ufficio legale |
| Omologazione strumento | ❌ assente | **Decreto di omologazione MIT** |
| Taratura periodica | ❌ N/A (no hardware) | Certificato di taratura annuale |
| Conformità GDPR | ⚠️ predisposta (hash, minimizzazione) | **DPIA** + misure + parere/registro |
| Accesso dati intestatari | ⚠️ mock locale | Convenzione ANV/PRA-ACI |
| Acquisto da parte della PA | ❌ | **Gara d'appalto** (D.Lgs 36/2023) |

**Conclusione**: «vendere allo Stato entro domani» non è realistico per un sistema
che emette multe reali. È invece realistico, da subito, **presentare un MVP
dimostrabile** e una **roadmap di omologazione e gara**. Questo repository serve
esattamente a questo.

## 2. Requisiti normativi per l'accertamento automatico

### 2.1 Omologazione / approvazione dello strumento (art. 142 c.6 CdS)
Le risultanze sono prova solo se ottenute da apparecchiature **«debitamente
omologate»**. La giurisprudenza recente della Corte di Cassazione (2024) ha
distinto nettamente **omologazione** da semplice **approvazione**, annullando
sanzioni basate su dispositivi solo *approvati*. È in corso a livello ministeriale
la definizione della procedura di omologazione (decreto attuativo dell'art. 142
c.6). **Azione**: avviare l'iter di omologazione presso il MIT; senza decreto di
omologazione i verbali sono impugnabili con elevata probabilità di annullamento.

### 2.2 Taratura periodica (Corte Cost. 113/2015)
Ogni dispositivo di misura della velocità deve essere sottoposto a **verifiche
periodiche di funzionalità e taratura** (almeno annuali) presso laboratorio
accreditato. Il numero del certificato e la data vanno riportati nel verbale
(campo già previsto: `device.last_calibration_date`).

### 2.3 Segnaletica e presegnalazione (art. 142 c.6-bis; direttive ministeriali)
La postazione deve essere **preceduta da segnaletica** di preavviso a distanza
adeguata e ben visibile. La mancata o irregolare segnalazione è motivo di
annullamento.

### 2.4 Autorizzazione delle postazioni (art. 4 DL 121/2002)
Sulle strade dove non è possibile la **contestazione immediata**, le postazioni
di rilevamento automatico devono essere individuate con **decreto del Prefetto**.
Il sistema supporta il funzionamento «documentale» (verbale notificato), che è
ammesso **solo** sulle strade autorizzate.

### 2.5 Contenuto e notifica del verbale (artt. 200–201, 383 Reg. CdS)
- Notifica all'obbligato entro **90 giorni** dall'accertamento (gestita: campo
  `notification_deadline`).
- Pagamento in misura ridotta entro **60 giorni**; ricorso al Prefetto entro 60
  gg o al Giudice di Pace entro 30 gg (riportati nel verbale).
- Dati obbligatori: autorità, estremi strumento e omologazione, luogo/data,
  veicolo, intestatario, velocità rilevata, norma violata, sanzione e termini —
  **tutti già presenti** nel verbale generato.

## 3. Protezione dei dati personali (GDPR / Codice Privacy)

L'accoppiata **video + ANPR** tratta dati personali (targa = dato personale; il
contesto può rivelare spostamenti). Requisiti minimi:

- **DPIA** (valutazione d'impatto, art. 35 GDPR) prima dell'attivazione.
- **Minimizzazione**: i veicoli **conformi non devono essere conservati**. Il
  prototipo non genera né archivia verbali per i conformi; in produzione la clip
  dei conformi va scartata immediatamente.
- **Limitazione della conservazione**: retention della prova limitata al tempo
  necessario al procedimento sanzionatorio e all'eventuale contenzioso.
- **Integrità e catena di custodia**: già previsto l'hash SHA-256 del
  pacchetto-prova; in produzione aggiungere firma digitale/marca temporale.
- **Titolarità e ruoli**: il Comune/Ente è titolare; il fornitore è responsabile
  del trattamento (nomina ex art. 28 GDPR).
- **Accesso ai dati intestatario**: tramite **Archivio Nazionale Veicoli / PRA-ACI**
  con apposita convenzione; non è consentito l'uso di banche dati non ufficiali.

## 4. Acquisto da parte della Pubblica Amministrazione

La PA non «compra» liberamente: acquisisce tramite **procedure di evidenza
pubblica** (D.Lgs 36/2023 — Codice dei contratti pubblici). Canali tipici:

- **MEPA / Consip** (mercato elettronico) per importi sotto soglia;
- **gara d'appalto** (procedura aperta/negoziata) per forniture/servizi rilevanti;
- **accordi quadro** o convenzioni.

Tempi realistici: settimane/mesi. Quello che si può fare *subito*: iscrizione al
MEPA, predisposizione della **scheda tecnica di prodotto** (vedi
[`PROPOSTA_COMMERCIALE.md`](PROPOSTA_COMMERCIALE.md)) e **demo** alle Polizie
Locali interessate.

## 5. Checklist operativa (dalla demo all'esercizio)

- [ ] Strumento hardware (telecamera + ottica + illuminatore IR) selezionato
- [ ] Backend ML collaudati su strada (YOLOv8 + EasyOCR) — vedi `PRODUCTION_BACKENDS.md`
- [ ] Calibrazione prospettica della postazione (≥4 punti rilevati a terra)
- [ ] **Omologazione MIT** dello strumento di misura
- [ ] **Taratura** annuale presso laboratorio accreditato
- [ ] Decreto prefettizio di autorizzazione delle postazioni
- [ ] Segnaletica di preavviso installata e verificata
- [ ] **DPIA** e misure GDPR; nomina a responsabile del trattamento
- [ ] Convenzione ANV/PRA-ACI per la visura intestatari
- [ ] Verifica importi edittali vigenti (aggiornamento biennale, art. 195 CdS)
- [ ] Integrazione con il gestionale verbali del Comando e con la PEC
- [ ] Iscrizione MEPA / partecipazione a gara

> **Disclaimer**: questo documento è una sintesi tecnica a uso interno e **non
> costituisce parere legale**. Ogni passaggio va validato con l'ufficio legale
> dell'Ente e con un consulente in materia di Codice della Strada e privacy.
