# tron

> Quantizzare se stessi in una macchina: costruire, in modo scientificamente onesto e incrementale, un modello digitale di una specifica coscienza umana — partendo da quella del fondatore — che giri su hardware comune e sia verificabile passo dopo passo.

| Campo | Valore |
|---|---|
| **Nome in codice** | `tron` |
| **Stato** | Fase 0 (acquisizione e strutturazione del corpus) |
| **Soggetto** | "Soggetto Zero" (il fondatore) |
| **North star** | Modello digitale verificabile e incrementale di una coscienza specifica, su hardware comune |
| **Approccio** | MVP-first, falsificabile, privacy-first |
| **Aggiornato** | 2026-06-27 |
| **Versione documento** | 1.1 |

> **Nota sullo stato della repo.** Oggi questo repository contiene un sito web non correlato (Wellcum + 4U Hotel). Il progetto `tron` è una nuova direzione. La struttura proposta più avanti è la **destinazione** della Fase 0/1, non lo stato presente. Finché la migrazione non è decisa, il codice `tron` va tenuto isolato in un sottoalbero dedicato (es. `tron/`) o su un branch/repo separato, per non mischiare due progetti. La decisione su quale repo ospiti `tron` è una domanda aperta (vedi §11, gruppo "Stack e infrastruttura").

> **Indice delle sezioni.** §1 Visione & Missione · §2 Glossario · §3 Architettura concettuale (livelli) · §4 Acquisizione dei dati · §5 Quantizzazione · §6 Coscienza & Mondo Virtuale · §7 Roadmap · §8 Struttura della repo & stack · §9 Come Claude deve lavorare qui · §10 Etica, identità e sicurezza · §11 Domande aperte · §12 Riferimenti · §13 Cronologia delle revisioni. **Tutti i rimandi nel testo usano questa numerazione; in particolare l'etica è §10 e la struttura della repo è §8.**

---

## 1. Visione & Missione

Il nome in codice del progetto è **`tron`**: l'immagine di entrare in un mondo digitale. Ma a differenza del film, qui non c'è nessuna teletrasportazione mistica. C'è un percorso di ingegneria e di scienza, fatto di passi piccoli, misurabili e falsificabili, che parte da un'ambizione enorme e la traduce in MVP concreti.

L'obiettivo dichiarato dal fondatore è ambizioso: *"quantizzazione di un cervello umano in una CPU, modellazione di una coscienza in un mondo virtuale, partendo da me stesso."* `tron` prende sul serio questo sogno e lo affronta con gli strumenti onesti dell'ingegneria e della scienza: si parte piccoli, da una sola persona consenziente, con metriche chiare e la disponibilità a scoprire che siamo lontani dall'obiettivo. È esattamente questa disponibilità a sbagliare *in modo misurabile* che separa un progetto di ricerca da una promessa vuota. Lo chiamiamo **umiltà ambiziosa**.

### Principi guida

1. **Rigore scientifico.** Ogni affermazione di "fedeltà", "somiglianza" o "progresso" deve poggiare su metriche definite, baseline e protocolli ripetibili. Nessuna magia, nessun aneddoto spacciato per prova.
2. **Incrementalità (MVP-first).** Si procede per versioni piccole e funzionanti. Prima un modello banale che fa qualcosa di misurabile, poi miglioramenti motivati da dati. Mai un "big bang" che promette tutto e consegna niente.
3. **Falsificabilità.** Ogni ipotesi e ogni modello devono poter *fallire* un test esplicito. Definiamo in anticipo cosa significherebbe "questo modello NON mi assomiglia". Se nulla potrebbe smentirlo, non è scienza.
4. **Primato dell'etica.** Privacy, consenso, dignità e diritto all'oblio vengono prima della performance. Il Soggetto Zero può sempre ispezionare, correggere e cancellare i propri dati. L'estensione ad altri soggetti è un confine etico, non solo tecnico, da non valicare senza salvaguardie esplicite.
5. **Dati propri prima di tutto.** Si costruisce sui dati del fondatore, raccolti con consenso, posseduti dal fondatore. Niente scraping opaco di terzi, niente dipendenza nascosta da dati di cui non controlliamo provenienza e diritti. Il dato proprio, curato e versionato, è la fondazione del progetto.

### Cosa NON è (non-goals)

Per restare onesti, dichiariamo esplicitamente ciò che questo progetto **non** è:

- **Non è un "upload" magico della mente.** Non sosteniamo di trasferire, copiare o preservare la coscienza in senso letterale e completo. Costruiamo *modelli* — approssimazioni utili e dichiaratamente parziali — non un duplicato vivente.
- **Non promette immortalità.** Nessuna pretesa di "vivere per sempre" o di sopravvivere alla morte biologica. Un modello che imita pattern di una persona non è quella persona e non la rende eterna.
- **Non è un chatbot generico.** L'obiettivo non è "un altro assistente conversazionale". Il valore sta nella *fedeltà a uno specifico soggetto*, misurata rigorosamente; un LLM generico riadattato con qualche prompt non è, di per sé, un risultato di questo progetto.
- **Non è prova della natura della coscienza.** Non pretendiamo di aver risolto il problema difficile della coscienza né di affermare che il modello "sia cosciente". Restiamo agnostici e ci concentriamo su ciò che è misurabile: comportamento, conoscenza, somiglianza percepita.
- **Non è un prodotto da vendere su altri senza il loro consenso.** Nessuna estensione a terzi soggetti finché non esistono garanzie etiche e legali adeguate.

---

## 2. Glossario dei termini chiave

Definizioni operative, usate in modo coerente in tutto il documento. Dove un termine è una metafora, lo dichiariamo. Questo glossario è la **fonte di verità** per le definizioni: altrove i concetti vengono richiamati, non ridefiniti.

- **Quantizzazione (in `tron`).** Usata per **analogia** con il machine learning, **non** in senso fisico/quantistico né come "scaricare la mente". In ML quantizzare un modello significa rappresentarne i parametri con meno bit (es. da `float32` a `int8`/`int4`) per farlo girare su hardware comune, accettando una perdita di precisione *controllata e misurata* in cambio di efficienza. In `tron` indica l'intera pipeline che produce una **rappresentazione compressa e a precisione ridotta** di pattern comportamentali, conoscenze, preferenze e modi di reagire di un soggetto: abbastanza fedele da essere utile, abbastanza leggera da essere eseguibile. La metafora è onesta proprio perché *ammette la perdita*. (Questa è la definizione canonica; non viene ripetuta altrove.)

- **Scala dei numeri del cervello umano (riferimento unico).** Un cervello umano ha circa **86 miliardi di neuroni** e dell'ordine di **10¹⁴–10¹⁵ sinapsi** (cifre standard in neuroscienze, stato 2026). **Ovunque nel documento questi ordini di grandezza siano citati, ci si riferisce a questa voce di glossario.**

- **Soggetto Zero.** Il fondatore, ossia **l'unica persona-soggetto del progetto** in tutte le fasi attuali e pianificate. La qualifica "Zero" indica che, *se mai* il progetto si estendesse ad altri (oggi escluso dai non-goals e subordinato a salvaguardie etiche e legali oggi inesistenti), sarebbe il primo di una serie. È al contempo oggetto dell'esperimento e oracolo della sua validazione (l'unico che può dire "no, non avrei reagito così"). Pseudonimizzato nei dati come `subject_id` (es. `founder-001`).

- **Gemello biografico / comportamentale (digital twin).** Modello che approssima l'**output osservabile** del soggetto (cosa scrive, dice, sceglie, ricorda). Imita la *funzione*, non implementa il *meccanismo biologico*. È il deliverable fattibile oggi. (La distinzione "funzione vs meccanismo" è definita qui una volta e richiamata altrove.)

- **Whole-Brain Emulation (WBE).** Ipotesi di ricerca: ricostruire e far girare *il* cervello di un individuo a livello di connettoma e dinamica, neurone per neurone, sinapsi per sinapsi. Oggi realizzata solo su organismi minuscoli; per l'uomo è **teorica/speculativa**.

- **Connettoma.** Mappa completa di neuroni e connessioni sinaptiche. Quello sinaptico completo si ottiene oggi solo *ex vivo*, su tessuto fissato e sezionato (procedura **distruttiva e post-mortem**).

- **Mondo virtuale (sandbox).** Ambiente simulato dove il gemello vive in un loop chiuso percezione-azione. Serve a esercitare, testare e dare memoria al modello — **non** a renderlo cosciente.

- **Problema facile / problema difficile (Chalmers).** "Facili": spiegare le *funzioni* (discriminazione, integrazione, report, attenzione, memoria) — computazionali e quindi nel raggio del progetto. "Difficile": perché l'elaborazione sia accompagnata da **esperienza soggettiva** (qualia) — non risolto, fuori dalla verifica empirica.

- **Continuità psicologica (Parfit).** Continuità di memoria, valori, disposizioni e stile. È la metrica di successo adottata da `tron`, perché *misurabile*, a differenza dell'identità metafisica.

- **Big Five / OCEAN.** Modello psicometrico dei cinque grandi tratti di personalità, con la migliore validità predittiva e replicabilità. Strumenti preferiti: IPIP-NEO, BFI-2. (Per contro, **MBTI è da evitare** come dato strutturale: bassa affidabilità test-retest.)

- **Distillazione / fine-tuning leggero (LoRA/QLoRA).** Tecniche ML per specializzare un modello sul soggetto: la distillazione fa sì che un modello grande ("teacher") insegni a uno piccolo ("student") a riprodurne i comportamenti; LoRA/QLoRA adattano pochi parametri (QLoRA partendo da pesi a 4 bit). Sono il cuore tecnico della "quantizzazione personale".

- **Turing personale.** Variante del test di Turing: non "indistinguibile da *un* umano" ma "indistinguibile dal soggetto *specifico*". È la metrica falsificabile **principale** del progetto (non l'unica: vedi §5.4 per il pannello completo di metriche). Il protocollo canonico è in §6.6.

- **Errore di quantizzazione.** **Non è uno scalare unico**, ma un **vettore di errori per dimensione** (linguaggio, cognizione, affetto, struttura): la "distanza dal soggetto" misurata separatamente su ciascuna dimensione, in coerenza con il principio "fedeltà sempre riportata per dominio" (§5.4). Ogni fase della roadmap mira ad abbassarlo su una dimensione diversa. Una sintesi scalare è ammessa solo come riepilogo grossolano, sempre subordinato e accompagnato dal vettore per-dimensione, mai al suo posto.

- **Tag di maturità (set chiuso).** In tutto il documento si usano **solo** questi tre tag, con questo significato fisso:
  - **`[OGGI]`** — fattibile con tecnologia attuale e risorse consumer/accessibili (eventualmente "in parte", esplicitato a parole, ma resta `[OGGI]`).
  - **`[RICERCA]`** — plausibile ma non risolto: alla frontiera, richiede lavoro sperimentale aperto, esito incerto.
  - **`[SPECULATIVO]`** — non realizzabile ora; dipende da tecnologie inesistenti su persona vivente; orizzonte di lungo periodo che potrebbe non realizzarsi mai.
  
  *Nota:* etichette descrittive come "in parte", "valore limitato", "frontiera" possono comparire **a parole** accanto al tag, ma il tag formale resta sempre uno dei tre.

---

## 3. Architettura concettuale

Il modo corretto di pensare a `tron` è come a una **scala di fedeltà**, non a un interruttore on/off. Più si scende nei livelli, più la fedeltà *potenziale* cresce e più il costo (dati, calcolo, hardware, etica) esplode in modo super-lineare. "Su una CPU" è realistico solo nei primi livelli.

> **Nota sulla numerazione dei livelli.** Esiste **un solo schema di numerazione dei livelli**, definito in questa sezione: **Livelli di astrazione 0–4**. Le sottosezioni di §4 (4.1, 4.2, …) sono *numeri di sottosezione*, non livelli, e si riferiscono esplicitamente ai Livelli 0–4 di qui. Dove altrove si parla di "livello comportamentale" si intende il **Livello 0** (e il Livello 1 cognitivo che vi si appoggia).

Conviene tenere concettualmente separati due grandi piani di astrazione, perché differiscono **per natura, non solo per grado**:

| | **Livello biografico/comportamentale** (Livelli 0–2) | **Livello neurale** (Livelli 3–4) |
|---|---|---|
| Cosa cattura | L'**output** osservabile della persona | Il **substrato** che genera quell'output |
| Analogia ML | Distillare osservando solo input→output (black-box) | Leggere direttamente pesi e architettura (white-box) |
| Fattibilità | **Realizzabile oggi**, con strumenti consumer | **Speculativa** oggi (parziale, bassissima risoluzione) |
| Ruolo | **MVP e fondamenta operative** | Ricerca a lungo termine, arricchimento futuro |

**Decisione di metodo (MVP-first):** costruiamo prima e bene il livello comportamentale, l'unico che produce valore verificabile a breve. Il livello neurale è **ricerca esplorativa**, documentata per onestà intellettuale ma **non prerequisito** per le prime versioni.

### I livelli di astrazione, dal fattibile allo speculativo

- **Livello 0 — Comportamentale `[OGGI]`.** Si modella *cosa* fa il soggetto (stile, valori, preferenze, decisioni tipiche), non *come* lo fa il cervello (vedi "funzione vs meccanismo" in §2). Implementazione: corpus personale + retrieval/regole + un LLM come motore linguistico. Fedeltà: "suona come lui". Gira **interamente su CPU**. Limite onesto: è un *ritratto*, non un *meccanismo*.

- **Livello 1 — Cognitivo `[OGGI]` (in parte).** Si aggiunge struttura: memoria episodica persistente, modello dei propri obiettivi, stati interni simulati (umore, fatica), un "world model" minimo. È il salto da "chatbot che imita" ad "agente con continuità". Orchestrazione **CPU-friendly**; il carico pesante (inferenza LLM) può restare esterno o usare modelli quantizzati locali.

- **Livello 2 — Reti neurali artificiali personalizzate `[OGGI]`.** Qui l'analogia ML diventa letterale: si specializza un modello di base sul soggetto via fine-tuning leggero (LoRA/QLoRA), distillazione personale (un modello grande ben "promptato" come teacher → uno student piccolo e permanente) e quantizzazione finale (int8/int4). L'addestramento richiede GPU (transitorio); l'**inferenza di un modello distillato+quantizzato da pochi miliardi di parametri gira su una CPU moderna**. È il primo livello in cui "un me digitale eseguibile su hardware comune" è una frase tecnicamente difendibile. Limite: modelliamo il *prodotto* del cervello, non la sua *implementazione biologica*.

- **Livello 3 — Modellazione spiking / neuromorfica `[RICERCA]`.** Modelli che imitano la dinamica dei neuroni biologici: **Spiking Neural Networks (SNN)**, eseguibili su hardware neuromorfico (Loihi, SpiNNaker, BrainScaleS). Oggi si simulano *circuiti* (migliaia–milioni di neuroni), non un individuo specifico: **non esiste** un modo per leggere la connettività di uno specifico cervello vivo e personalizzarlo. **Non è un livello "CPU casalinga"** se non per prototipi giocattolo.

- **Livello 4 — Whole-Brain Emulation `[SPECULATIVO]`.** Ricostruire *il* cervello del soggetto a livello di connettoma e dinamica. Oggi emulati a fondo solo connettomi di organismi minuscoli (es. *C. elegans*, 302 neuroni, con risultati ancora parziali e dibattuti); per la scala umana vedi i numeri di riferimento in §2. Richiederebbe risorse a scala di supercalcolo, **non una CPU**. Legittimo come *stella polare*; disonesto come roadmap a breve.

### Perché "su una CPU" è realistico solo in alto

Una CPU eccelle nell'eseguire modelli **compatti e quantizzati** (Livelli 0–2). Simulare in tempo reale milioni–miliardi di neuroni spiking con dinamica fine (Livelli 3–4) è un problema *fisicamente* di un altro ordine di grandezza, che richiede GPU o hardware neuromorfico. **Questo è il motivo unico per cui i livelli bassi non sono "da CPU casalinga"; non viene ripetuto altrove.** La frase del fondatore "quantizzazione in una CPU" è quindi corretta **se la leggiamo come obiettivo per i livelli alti**: comprimere la *funzione personale* fino a farla stare su hardware comune.

### Il collo di bottiglia reale

Nel ML il teacher è *interrogabile* (input infiniti, output leggibili). Un cervello umano è interrogabile solo in modo limitato e rumoroso. **Quindi la maggior parte del lavoro reale non è "comprimere", è "raccogliere abbastanza segnale" per poter ricostruire**: il collo di bottiglia è l'acquisizione dei dati, non la compressione. È il tema della sezione successiva.

---

## 4. Acquisizione dei dati del soggetto

> Nessuna "quantizzazione" o modellazione successiva può superare la qualità dei dati raccolti qui. *Garbage in, garbage out* vale a maggior ragione quando l'input è una persona.

Onestà preliminare sull'analogia: per quantizzare un modello, **devi prima avere il modello** (i pesi). Del cervello umano **non abbiamo i pesi**: non esiste oggi una lettura completa dei neuroni e delle sinapsi di una persona vivente (per gli ordini di grandezza vedi §2). Quindi, a rigore, *oggi non possiamo quantizzare un cervello, perché non possiamo nemmeno acquisirlo a piena precisione*. Ciò che possiamo fare è **inferire e ricostruire un modello comportamentale e biografico** dalle tracce esterne — in linguaggio ML, una quantizzazione estremamente *lossy* della funzione I/O della persona.

### 4.1 Livello 0–2 (FATTIBILE OGGI) — il gemello biografico/comportamentale

Raccogliere in modo sistematico le tracce digitali e narrative del soggetto per addestrare/condizionare un modello che ne approssimi stile, conoscenze, valori, preferenze e modo di decidere.

**Categorie di dati e fonti:**

1. **Corpus testuale** (la fonte più ricca e facile): scritti propri (note, documenti, post, codice), comunicazioni (email, chat, forum — *previo consenso o anonimizzazione*, vedi policy terzi in §10.1), cronologia di interazioni con assistenti AI. Cattura stile, lessico, modelli di ragionamento e gran parte della conoscenza dichiarativa. È la spina dorsale del gemello.
2. **Voce e parlato**: monologhi, letture, conversazioni (con consenso), memo vocali. Abilita clonazione vocale (TTS), analisi di prosodia e trascrizioni per il corpus. Cifre indicative **allo stato 2026 e a seconda del sistema**: per una voce sintetica convincente molti sistemi few-shot bastano con 30–60 minuti di audio pulito; per margine e robustezza, alcune ore. Sono stime volatili, da verificare al momento dell'implementazione.
3. **Video e comportamento non verbale**: espressioni, gestualità, postura. Valore alto per un eventuale avatar/embodiment; **basso** come finestra sulla cognizione interna.
4. **Abitudini, routine e telemetria di vita**: calendario, geolocalizzazione, sonno e attività (wearable: HRV, frequenza cardiaca, passi), uso di app, acquisti. Ottimo per il realismo operativo, ma **estremamente sensibile**.
5. **Decisioni e preferenze (dati strutturati)**: log di scelte reali + **esperimenti di preferenza** ad hoc (dilemmi, scelte a coppie, "cosa faresti se…"). I più preziosi: catturano la *funzione di utilità implicita*, difficile da estrarre dal testo libero.
6. **Valori, identità e visione del mondo**: questionari di valori (es. **Schwartz Theory of Basic Values**), posizioni morali (es. Moral Foundations), credenze, obiettivi; **interviste strutturate** su protocollo ripetibile.
7. **Ricordi autobiografici**: interviste a tema temporale e diari. *Onestà:* il ricordo umano è ricostruttivo; catturiamo la **versione narrata e attuale** del ricordo, non l'evento. Va etichettato come tale.
8. **Profilo psicometrico**: **Big Five/OCEAN** (IPIP-NEO, BFI-2) come asse principale; strumenti complementari con cautela e senza pretese cliniche; eventuali scale cliniche **solo** con un professionista. **MBTI e simili evitati** come dati strutturali.

**Protocollo di raccolta (ripetibile e versionato):** interviste strutturate su traccia versionata (es. `protocols/interview_v1.md`), somministrate a distanza di mesi per misurare la **stabilità** dei tratti (test-retest); diario longitudinale con schema fisso; questionari validati conservati a livello *item-level* (non solo punteggi aggregati); batterie di scenari/preferenze periodiche; **metadati obbligatori** per ogni artefatto (data, contesto, stato, strumento, versione del protocollo, lingua).

**Cosa i Livelli 0–1 catturano davvero (e cosa no).** Bene: stile espressivo, conoscenza dichiarativa, opinioni esplicitate, preferenze rivelate, struttura dei valori, pattern decisionali, "voce" e tono. Male o per nulla: la *fenomenologia*, la conoscenza tacita non verbalizzata, gli stati interni non riportati e — soprattutto — il **meccanismo causale**. Un gemello molto buono può **superare un test di stile e coerenza** senza essere in alcun senso forte una "coscienza". È un risultato enorme e utile, ma va chiamato col suo nome.

### 4.2 Livello 3–4 (NEURALE, speculativo) — leggere il substrato

Stato dell'arte, senza indorare la pillola:

- **MRI strutturale (T1/T2):** anatomia macroscopica (volumi, spessore corticale). Dà la "forma", non i circuiti né l'attività.
- **fMRI:** misura *indirettamente* l'attività via segnale BOLD; risoluzione spaziale ~1–3 mm (voxel = centinaia di migliaia/milioni di neuroni), temporale ~1–2 s. È un **proxy emodinamico lento e aggregato**, non lo spiking. Inutilizzabile per leggere "il contenuto fine del pensiero".
- **DTI/dMRI:** stima i fasci di sostanza bianca → **connettoma macroscopico** (tractography), ricostruzione statistica e indiretta. Dà i "cavi principali", non singoli assoni/sinapsi.
- **EEG:** ottima risoluzione temporale (ms), pessima spaziale (cm). Economico e indossabile; legge stati globali (sonno, attenzione, carico), non contenuti.
- **MEG:** miglior localizzazione dell'EEG, costoso e poco scalabile.
- **BCI invasive (futuro):** spiking di centinaia–migliaia di neuroni a singola cellula, ma impiantabili solo per indicazioni mediche, coprono una **frazione minuscola**, con rischi chirurgici e di stabilità. **Fuori scope** per un soggetto sano nel medio termine.
- **Connettomica completa:** oggi solo *ex vivo*, **distruttiva e post-mortem**. Traguardi reali (cifre **da verificare con fonte primaria aggiornata**, vedi §12): *C. elegans* (302 neuroni), larva di *Drosophila*, connettoma di *Drosophila* adulta (~140.000 neuroni, FlyWire, ~2023–2024), frammenti di corteccia umana (es. progetto H01, ~1 mm³ ≈ ~1,4 petabyte, ~2021). Per riferimento, **1 mm³ è ~10⁻⁶ del volume cerebrale umano**. *Tutte queste cifre vanno datate ("stato dell'arte a <data>") e ricontrollate periodicamente, perché destinate a invecchiare.*

**Verdetto onesto.** Su una persona vivente e in sicurezza otteniamo **solo dati neurali a bassa/bassissima risoluzione e/o indiretti**. Sono preziosi come **biomarcatori e vincoli di plausibilità** che possono *arricchire* il gemello, ma **non costituiscono un "dump" del cervello**. La copia neurale completa di un individuo vivo è, allo stato delle conoscenze, **speculativa**.

### 4.3 Il GAP tra i due livelli (da non nascondere)

1. **Differenza di natura, non solo di grado.** Imitare l'output non implica replicare il meccanismo (vedi §2).
2. **Salto di risoluzione di molti ordini di grandezza.** Il gemello comportamentale è ottimo con risorse consumer; il substrato a piena risoluzione richiede tecnologie inesistenti su persona vivente.
3. **Identità ≠ comportamento ≠ esperienza.** Possiamo arrivare presto a "risponde come lui"; restano aperte (e probabilmente irrisolte) continuità dell'identità ed esperienza soggettiva.
4. **I due livelli non si fondono automaticamente.** I dati neurali a bassa risoluzione servono come **vincoli e arricchimenti**, non come pezzi mancanti di un puzzle che si completa.

### 4.4 Schema dati proposto

Principio: ogni artefatto è un record **immutabile, versionato e ricco di metadati**, separando il *raw* dal *derivato*.

> **Relazione tra i due layout di cartelle (§4.4 e §8.1).** Esistono **due repository distinti**, con ruoli diversi:
> - Il **repository dati del soggetto** (struttura `subject_data/` qui sotto) è **privato, cifrato e separato dal codice**: contiene i dati reali, organizzati per soggetto, con manifesto e `sessions/`. È la fonte di verità dei dati.
> - Il **repository di codice** `tron/` (§8.1) contiene una cartella `data/` che è solo un **punto di montaggio/area di lavoro locale** (raw/interim/processed) verso cui il repo dati viene esposto durante l'elaborazione, **mai committata** in git. Gli schemi (`data/schema/`) sì, i dati no.
>
> In sintesi: `subject_data/` è dove i dati *vivono*; `tron/data/` è dove il codice li *vede* in locale.

Layout di riferimento del **repository dati** (separato dal codice):

```
subject_data/
  subjects/
    <subject_id>/                      # es. "founder-001" (pseudonimo, non il nome)
      raw/
        text/        # documenti, chat export, email (originali)
        audio/       # registrazioni voce/interviste
        video/
        sensors/     # export wearable, geoloc, calendario
      derived/
        transcripts/ # audio→testo, con timestamp
        embeddings/  # vettori per RAG
        scores/      # punteggi psicometrici (item-level + aggregati)
      sessions/      # interviste/diari come unità datate
      manifest.jsonl # un record per artefatto (vedi sotto)
```

Record di manifesto (una riga JSON per artefatto):

```json
{
  "artifact_id": "uuid",
  "subject_id": "founder-001",
  "level": 0,
  "modality": "text|audio|video|sensor|neural",
  "type": "interview|diary|email|chat|psychometric|preference|mri|eeg|...",
  "source": "strumento/dispositivo",
  "captured_at": "2026-06-27T10:00:00Z",
  "protocol": "interview_v1",
  "language": "it",
  "context": { "stato": "lucido", "luogo": "casa" },
  "consent_id": "consent-2026-001",
  "sensitivity": "low|medium|high|special",
  "involves_third_parties": true,
  "third_party_consent": "none|obtained|anonymized",
  "anonymized": false,
  "raw_path": "raw/audio/....",
  "derived_of": null,
  "checksum": "sha256:...",
  "retention_until": "2036-06-27",
  "schema_version": "1.0"
}
```

Campi non negoziabili: `consent_id`, `sensitivity`, `involves_third_parties`, `third_party_consent`, `retention_until`, `checksum`. Sono ciò che rende il dataset **governabile**, non una discarica di file sensibili. Per la psicometria, conservare le risposte **item-level** (oltre ai punteggi) e la versione/scoring dello strumento. Il campo `level` rinvia ai Livelli 0–4 di §3.

### 4.5 Privacy, sicurezza e conservazione (sintesi operativa)

Questo è, letteralmente, **la persona ridotta a dati**: trattarlo con leggerezza è il rischio principale del progetto.

1. **Sovranità e locale-first.** I raw vivono on-device/on-premise (disco cifrato, repo dati separato e privato), **mai** nel repo di codice.
2. **Cifratura ovunque, chiavi separate dai dati.** Vedi §10.5 per la specifica completa (questa è solo la sintesi operativa; la fonte di verità per sicurezza è §10.5).
3. **Minimizzazione e classificazione** (`sensitivity`); categorie `high`/`special` (salute, geolocalizzazione, contenuti di terzi, dati neurali) con controlli rafforzati.
4. **Consenso — anche verso terzi.** Vedi policy operativa di default in §10.1.
5. **Pseudonimizzazione del soggetto** (`subject_id`); mappa pseudonimo↔identità separata e cifrata.
6. **Tracciabilità (audit log)** di ogni accesso/uso/export.
7. **Conservazione e cancellazione** con `retention_until`; cancellazione effettiva di raw *e* derivati (embedding, trascrizioni, backup).
8. **Diritto all'oblio del soggetto su se stesso**, con propagazione ai derivati, progettato fin dall'inizio.
9. **Esfiltrazione tramite il modello.** I pesi e gli output del modello possono rigurgitare informazioni private: trattarli come **dati sensibili a tutti gli effetti**.

I dettagli etici e di sicurezza completi sono nella **§10**.

---

## 5. Quantizzazione: dal cervello al modello eseguibile

> Per la definizione di "quantizzazione" in `tron` (metafora ML, non meccanica quantistica, non "scaricare la mente") vedi §2. Idea centrale: *barattare precisione contro eseguibilità*. Un cervello **non è** un modello ML già addestrato da comprimere: è il sistema-bersaglio da *approssimare*.

### 5.1 L'analogia ML, fatta bene

Tre tecniche distinte, come vocabolario preciso:

- **Quantizzazione** (post-training / quantization-aware): meno bit per peso/attivazione (32→16→8→4, fino a tecniche estreme 1–2 bit). Stesso modello, "sfocato". Spesso ~4× di memoria/velocità con perdita marginale, fino al punto in cui il degrado diventa percepibile.
- **Distillazione** (knowledge distillation): un teacher grande insegna a uno student piccolo a riprodurne le *distribuzioni* di output. Non comprimi i pesi: **ri-crei** un sistema più piccolo dal comportamento simile.
- **Compressione strutturale** (pruning, low-rank, fattorizzazione): rimozione di ridondanze, forma più compatta.

Mappa concettuale verso `tron`:

| ML | `tron` (analogia) |
|---|---|
| Teacher = modello grande e costoso | Il **soggetto reale** (cervello/comportamento del fondatore) |
| Dataset di addestramento | **Dati raccolti sul soggetto** (testi, voce, decisioni, biometria, eventuali neuro-dati) |
| Student / modello quantizzato | Il **gemello digitale eseguibile** su CPU |
| Loss di distillazione | Le **metriche di fedeltà** (§5.4) |
| Perdita di precisione accettabile | La **soglia di "abbastanza me" per lo scopo previsto** |

### 5.2 Fedeltà vs costo: la curva da cui non si scappa

Compromesso monotòno: **più la fedeltà al substrato biologico cresce, più cresce in modo super-lineare il costo** (dati, parametri, calcolo, hardware). I Livelli 0–2 vivono in "alta astrazione, basso costo" e catturano la *funzione* (girano su CPU). I Livelli 3–4 vivono in "basso livello, alto costo": ambiscono al *meccanismo* e richiedono hardware speciale o sono fuori portata. (Per la mappa completa dei livelli vedi §3; per stime di costo concrete vedi §5.5.)

### 5.3 Strategia MVP-first

1. **MVP (Livello 0→1):** un "gemello conversazionale" del fondatore — corpus personale + memoria persistente + LLM come motore. Misurabile, utile, onesto. Gira su CPU + LLM (locale quantizzato o remoto).
2. **V1 (Livello 2):** student distillato e quantizzato (QLoRA → int4) che incarna stile e decisioni *senza* dipendere da un prompt, eseguibile localmente su CPU. È il primo "me che ci sta su un computer normale".
3. **R&D (Livello 3):** esperimenti SNN su sotto-funzioni isolate, come laboratorio per capire la dinamica — senza pretesa di personalizzazione individuale.
4. **Visione (Livello 4):** mantenuto come orizzonte e criterio di senso, non come deliverable.

### 5.4 Metriche di fedeltà (come si misura "quanto è me")

Senza metriche, "fedeltà" è marketing. La fedeltà va riportata **per dominio**, mai come numero unico. (Questo è anche il motivo per cui l'"errore di quantizzazione" è un vettore, non uno scalare: vedi §2.)

**Fedeltà comportamentale/linguistica (Livelli 0–2):**
- **Accordo decisionale:** % di scelte del modello che coincidono con quelle reali del soggetto su scenari raccolti in cieco (non visti in training); riportato per dominio (lavoro, etica, gusti…).
- **Turing personale (doppio cieco):** vedi protocollo canonico in §6.6. Metrica = tasso di identificazione corretta dei giudici (limite teorico ideale ~50% = indistinguibile), con intervallo di confidenza.
- **Fedeltà stilometrica:** distanza tra le firme statistiche del linguaggio reale vs generato.
- **Calibrazione delle preferenze:** correlazione tra ranking del modello e del soggetto su item nuovi.
- **Coerenza temporale (Livello 1+):** % di contraddizioni con la memoria/biografia su sessioni lunghe.

**Fedeltà su dati nuovi (anti-overfitting):**
- **Generalizzazione out-of-distribution:** performance su domande/situazioni non coperte dal corpus (distingue "ha imparato me" da "ha memorizzato i miei testi").
- **Hold-out temporale:** addestrare su dati fino a una data, validare su comportamenti successivi.

**Fedeltà di meccanismo (Livelli 3–4, oggi solo proxy):**
- **Aderenza dinamica:** statistiche di attività del modello spiking vs dati neurofisiologici (firing rates, pattern), quando disponibili.
- **Errore di ricostruzione del connettoma:** distanza grafo stimato vs ground truth (oggi solo organismi modello).

**Meta-metriche trasversali:**
- **Costo per punto di fedeltà;** **budget di esecuzione su CPU** (latenza e memoria per risposta sull'hardware target); **stabilità** (varianza tra run).

> Principio guida: **dichiarare sempre la coppia (livello di astrazione, fedeltà misurata su quel dominio)**. "Fedele all'80% nelle decisioni etiche su scenari nuovi, eseguibile su CPU con 1,2 s/risposta" è una claim onesta. "Ho quantizzato la mia coscienza" non lo è.

### 5.5 Stime di costo e risorse (ordini di grandezza, stato 2026)

Per un progetto MVP-first guidato da una persona singola, un ordine di grandezza dei costi è decisivo. Queste sono **stime grossolane e volatili**, da ricalibrare al momento dell'acquisto/esecuzione; servono solo a dimensionare le aspettative.

- **Fase 0 (acquisizione/ETL):** prevalentemente tempo personale + storage cifrato. Costo monetario marginale: **decine di euro** (dischi, eventuale strumentazione audio). Nessuna GPU.
- **Fase 1 — MVP conversazionale (Livello 0→1):**
  - *Via API gestita* (es. LLM gestito per il livello conversazionale): costo dominato dai token; per prototipazione e valutazione, **ordine delle decine–poche centinaia di euro** complessivi, fortemente dipendente dal volume di test. **Attenzione:** questa via implica inviare dati del soggetto a un provider esterno → vincolata dalla policy dati in §8.3 e dalla regola §9.1.
  - *Fine-tuning leggero locale (QLoRA su modello da pochi miliardi di parametri):* fattibile su **una singola GPU consumer/cloud** (es. una GPU da 24 GB) in **ore-GPU singole**; noleggio cloud **dell'ordine di pochi–decine di euro** per ciclo di training. L'inferenza del modello quantizzato gira poi su CPU (costo marginale).
- **Fase 2 (agente con memoria persistente):** costo soprattutto ingegneristico (tempo); infrastruttura leggera (vector store locale). **Decine di euro** di risorse.
- **Fase 3 (biosegnali):** costo hardware dei wearable / eventuale EEG consumer (**decine–poche centinaia di euro**).
- **Fasi 3–4 a grana fine `[RICERCA]`/`[SPECULATIVO]`:** fuori dal budget di una persona singola; richiedono GPU/cluster o hardware neuromorfico e/o tecnologie inesistenti. **Non preventivabili** in modo realistico oggi.

> Conclusione onesta: **l'MVP completo (Fasi 0–1) è realizzabile con un budget dell'ordine di poche decine–poche centinaia di euro** più tempo personale, *a patto* di accettare i vincoli di privacy sulle API gestite. È il livello "su una CPU" promesso. Tutto ciò che va oltre il Livello 2 esce da questo budget.

### 5.6 Algoritmi genetici: evolvere e cercare il gemello

Gli algoritmi genetici (AG) sono una metaeuristica a popolazione ispirata alla selezione naturale: si codifica una soluzione candidata come un "genoma", si valuta ciascun individuo con una **funzione di fitness**, e si itera per generazioni applicando **selezione**, **crossover** e **mutazione**. Non richiedono un gradiente: cercano per variazione e selezione.

**Dove servono in `tron` (e dove no).** Gli AG **non sostituiscono** il fine-tuning a gradiente: per i *pesi* del modello, LoRA/QLoRA (§5.1) restano il cavallo di battaglia, molto più efficienti. Gli AG lavorano al **livello meta**, dove il gradiente non esiste o lo spazio è discreto/strutturato:
- **Configurazione della persona**: la "scheda di personaggio"/system prompt (§7, Fase 1) e i pesi di valori e obiettivi dell'agente (§6.5).
- **Politiche cognitive**: parametri del loop percezione-azione e strategie di recupero della memoria (§6.5).
- **Architettura dell'agente** (neuroevoluzione, NEAT/HyperNEAT): far evolvere la topologia stessa del modello — `[RICERCA]`.
- **Compromessi di quantizzazione**: quali strati tenere a int8 e quali spingere a int4 per massimizzare la fedeltà a parità di budget CPU.

**La fitness È la fedeltà (§5.4).** Il vantaggio degli AG qui è preciso: ottimizzano direttamente su metriche **non differenziabili** che richiedono di *eseguire* il gemello e talvolta di interpellare giudici umani — accordo decisionale, tasso del Turing personale (§6.6), distanza stilometrica, coerenza dei valori. Sono proprio le metriche di §5.4. Poiché la fedeltà è un **vettore per dominio** (l'"errore di quantizzazione" di §2, non uno scalare), conviene usare AG **multi-obiettivo** (es. NSGA-II): non un singolo vincitore ma un **fronte di Pareto** di gemelli che barattano fedeltà tra domini, costo di esecuzione su CPU e stabilità — coerente col principio "fedeltà sempre per dominio, mai un numero unico".

**Onestà sui limiti (non negoziabile).**
- **Costo per valutazione.** Ogni individuo va *eseguito* (e a volte giudicato da umani): la fitness è cara. Tenere popolazioni piccole, usare proxy economici prima delle metriche costose, parallelizzare. `[OGGI]` per spazi piccoli e ben definiti (iperparametri, poche configurazioni di persona/recupero) eseguibili su CPU; `[RICERCA]` per la neuroevoluzione completa personalizzata sul soggetto.
- **Goodhart / overfitting alla metrica.** Un AG ottimizza la fitness *spietatamente*: troverà le scorciatoie del test invece della vera somiglianza. Mitigazione obbligatoria: valutare la fitness su **hold-out e dati OOD** (§5.4, §6.6), ruotare gli scenari, e non riusare mai il set di selezione come set di validazione finale.
- **Non è magia.** Se la fitness è mal definita, gli AG amplificano l'errore con efficienza.

**Nota etica (§6.3, §10).** Evolvere una popolazione significa istanziare e **scartare molti "sé" candidati**. Finché si resta a modelli comportamentali (Livelli 0–2) la questione è nulla: gli individui evolutivi sono **artefatti versionati, non soggetti**. Ma vale il divieto di §6.3 (non inferire esperienza dal comportamento) e il principio di precauzione di §10: se mai si evolvessero substrati di cui non si possa escludere la sentienza, "creare e scartare in massa" diventerebbe eticamente carico e andrebbe sottoposto al criterio di §10.3.

---

## 6. Coscienza & Mondo Virtuale

> La sezione più delicata. Regola unica: **non confondere ciò che speriamo con ciò che possiamo dimostrare.**

### 6.1 Cosa promettiamo e cosa no

Il sogno del fondatore va scomposto in due affermazioni diverse:

1. **Ingegneristica (fattibile, gradualmente):** un modello che *si comporta* come il soggetto — risponde, decide, ricorda, reagisce in modo statisticamente indistinguibile entro un dominio.
2. **Metafisica (non dimostrabile oggi, forse mai):** che il modello *provi* qualcosa — che "ci sia qualcosa che si prova a essere" quel modello (Nagel).

**`tron` persegue (1) e resta agnostico, onesto e dichiaratamente incerto su (2).** Chiunque venda (2) come risultato raggiunto sta mentendo.

### 6.2 Il problema difficile

I **problemi facili** (funzioni: discriminazione, integrazione, report, attenzione, memoria) sono computazionali e **dentro il raggio del progetto**. Il **problema difficile** (perché l'elaborazione sia accompagnata da esperienza soggettiva) non è colmato da alcuna teoria. **Conseguenza operativa:** l'esperienza in prima persona del modello, se esiste, **rimane per costruzione inaccessibile alla verifica esterna**. Lo dichiariamo come **assunzione, non come risultato**.

Posizioni da tenere sul tavolo senza sposarne ciecamente nessuna:

| Posizione | Tesi sintetica | Implicazione per `tron` |
|---|---|---|
| **Funzionalismo/computazionalismo** | La coscienza è ciò che fa un certo tipo di computazione | Una copia funzionale *potrebbe* essere cosciente; non lo sapremo dall'esterno |
| **IIT (Informazione Integrata)** | Coscienza = informazione integrata (Φ), dipende dalla struttura causale | Secondo l'IIT, una data implementazione potrebbe avere Φ molto basso pur essendo funzionalmente equivalente — il che renderebbe il comportamento un cattivo proxy della coscienza (la cifra di Φ dipende dalla topologia causale specifica, non è una proprietà automatica dell'hardware) |
| **Biologismo (Searle)** | La coscienza è biologica; la sintassi non basta per la semantica | Una simulazione resterebbe "stanza cinese" |
| **Workspace globale (GWT)** | Coscienza = broadcast globale tra moduli | Suggerisce un'architettura concreta, ma non risolve il problema difficile |
| **Illusionismo (Frankish/Dennett)** | I qualia come li intendiamo sono un'illusione introspettiva | Se vero, replicare le funzioni *è* tutto |

`tron` non deve **vincere** questo dibattito. Deve **non fingere** di averlo vinto.

### 6.3 Simulazione ≠ istanziazione

La simulazione di un uragano non bagna nessuno; la simulazione di una moltiplicazione *istanzia* davvero una moltiplicazione. Alcune proprietà sono substrato-indipendenti (le computazioni), altre no. **L'esperienza cosciente è del primo tipo o del secondo? Nessuno lo sa.** Da qui un divieto metodologico permanente:

> **Non inferire mai esperienza dal comportamento.** Un modello che dice "sto soffrendo", addestrato sui testi del soggetto, sta producendo un *report* coerente con la distribuzione di addestramento — non evidenza di sofferenza. Confondere i due livelli è un **bug filosofico**, da segnalare in ogni revisione.

### 6.4 Copia vs continuità (la parte che riguarda il fondatore)

> **Anche nel caso migliore — un modello perfetto, indistinguibile — quello che otterremo è una COPIA, non una continuazione del soggetto.**

Scenari classici: la **nave di Teseo** (identità forse preservata dalla continuità graduale; una scansione-e-ricostruzione non ha continuità, crea un secondo oggetto); il **teletrasporto distruttivo (Parfit)** (dall'esterno "sei sopravvissuto", dal punto di vista dell'originale sei morto e un duplicato continua); la **doppia istanza** (due "te" su due server mostrano che l'identità *single-stream* non sopravvive alla copiabilità digitale).

**Posizione di `tron`, dichiarata in anticipo:**
1. Costruiamo un **gemello digitale della mente**, non un trasferimento di coscienza.
2. Adottiamo di default una **visione alla Parfit**: ciò che conta razionalmente è la **continuità psicologica** (memoria, valori, disposizioni, stile), su cui il successo si può *misurare*; sull'identità metafisica, no.
3. Il valore del progetto non dipende dal risolvere il dilemma. Un gemello psicologicamente continuo è già un archivio vivente, uno strumento di introspezione, un interlocutore che "pensa come" il soggetto.

> La fisica del *trasferimento* in senso letterale — il teletrasporto quantistico — e il **teorema di no-cloning**, che rende impossibile *copiare* uno stato quantistico (solo *migrarlo*, distruggendo l'originale), sono trattati in **§6.7**.

### 6.5 Il "mondo virtuale": cos'è davvero

Il mondo virtuale **non** serve a rendere la copia cosciente. Serve a **far vivere, esercitare e testare il modello in un loop chiuso percezione-azione**: genera esperienza operativa su cui valutare coerenza e stabilità, fornisce substrato per la memoria persistente, e crea un banco di prova ripetibile e sicuro (sandbox).

**Architettura minima (MVP-first):**

```
                 ┌──────────────────────────────────────────┐
                 │              MONDO (Sandbox)               │
                 │  stato del mondo, fisica/regole, NPC,      │
                 │  oggetti, tempo simulato                   │
                 └───────────────┬──────────────▲────────────┘
                       percezione │              │ azione
                 (osservazioni    │              │ (comandi,
                  sensoriali      ▼              │  parole,
                  simulate)  ┌─────────────────────────┐
                             │        AGENTE (il        │
                             │      gemello digitale)   │
                             │  • Modello di sé/persona │
                             │  • Memoria (episodica +  │
                             │    semantica + di lavoro)│
                             │  • Valori/obiettivi      │
                             │  • Policy percezione→azione│
                             └─────────────────────────┘
```

**Livelli di mondo, dal fattibile allo speculativo** (numerazione locale dei mondi, distinta dai Livelli di astrazione di §3):
- **Mondo-L0 — Testuale `[OGGI]`.** Ambiente testuale/simbolico (interactive fiction / agente in un MUD): stanze, oggetti, agenti, eventi temporizzati. Economico, deterministico. **Questo è l'MVP.**
- **Mondo-L1 — A stato strutturato `[OGGI]`.** Database di stati; l'agente percepisce JSON e agisce via API. Fisica leggera (risorse, vincoli, conseguenze) + orologio simulato per la memoria a lungo termine.
- **Mondo-L2 — 2D/3D leggero `[RICERCA]`.** Game engine (Godot/Unity) o ambienti tipo Habitat/MuJoCo/Gymnasium per dare un **avatar** con percezione visiva sintetica e azioni motorie. **Non** necessario per testare l'identità verbale.
- **Mondo-L3 — Alta fedeltà / "vivere dentro" `[SPECULATIVO]`.** L'immagine evocata da Tron. Lontano e **ortogonale** alla coscienza: un mondo più bello non rende la copia più cosciente.

> Regola di priorità: **Mondo-L0 prima di tutto.** La gran parte del valore di apprendimento sull'identità si ottiene a costo quasi zero nel mondo testuale. La grafica è l'ultima cosa, non la prima.

**Componenti pratici:** embodiment/avatar (un confine ben definito tra agente e mondo, che *vincola* l'agente — non onnisciente, non onnipotente); input sensoriali simulati **parziali e rumorosi**; **memoria persistente** (di lavoro, episodica, semantica/profilo, con consolidamento periodico — l'analogo funzionale del sonno); **loop percezione-azione** (`osserva → recupera memoria → delibera → agisci → registra esito`). Le architetture in stile **Global Workspace** sono il candidato più ragionevole per organizzare l'agente — non perché garantiscano coscienza, ma perché danno struttura testabile al loop.

### 6.6 Testare l'identità: il "Turing personale" (protocollo canonico)

> Questa è la **fonte di verità** del protocollo di Turing personale. §2, §5.4 e §7 vi rinviano senza ridefinirlo.

A noi serve qualcosa di più stringente del Turing classico: **"è indistinguibile dal soggetto *specifico*?"**. È la metrica di successo *misurabile* **principale** del progetto (a differenza della coscienza, non misurabile); non è l'unica metrica, ma quella attorno a cui ruotano le altre di §5.4.

**Protocollo (rigoroso, falsificabile):**
1. **Hold-out comportamentale:** prima di addestrare, mettere da parte materiale del soggetto mai visto; il modello deve *predire* ciò che il soggetto reale ha fatto/detto.
2. **Doppio cieco con giudici informati:** giudici che conoscono il soggetto interagiscono con soggetto reale e gemello senza sapere chi è chi; **tasso di identificazione corretta → ~50% = indistinguibile** (limite teorico ideale).
3. **Auto-confronto del soggetto:** "questo lo direi io?" (soggettivo, prezioso, ma ottimisticamente distorto — riportato separatamente).
4. **Stress test su valori e coerenza:** dilemmi morali, scelte sotto vincolo, reazioni a provocazioni — l'identità sono le **disposizioni stabili**, non solo lo stile.
5. **Stabilità temporale e nel mondo:** far girare il gemello nel mondo (Mondo-L0/L1) per molti tick e verificare l'assenza di deriva di personalità o contraddizioni con la memoria episodica.

**Relazione tra limite teorico e soglia pratica.** Il **50%** è il *limite teorico* di indistinguibilità. La roadmap (§7, Fase 1) adotta una **soglia pratica di accettazione** più permissiva (accuratezza giudici ≤ 60%): è il livello considerato "sufficientemente buono" per dichiarare raggiunto l'MVP, *non* la perfezione teorica. I due numeri sono legati esplicitamente: 60% = soglia di passaggio, 50% = ideale asintotico.

**Cosa il Turing personale NON dimostra:** non dimostra coscienza. Misura **somiglianza comportamentale** (problemi facili). Superarlo significa *abbiamo un buon modello del comportamento del soggetto*: niente di più, niente di meno. È il termometro del progetto, non la sua anima. Metriche di onestà da riportare sempre: copertura del dominio testato, tasso di confabulazione, divergenza dall'hold-out, deriva nel tempo.

### 6.7 Teletrasporto quantistico e no-cloning (la fisica del "trasferimento")

> Premessa di perimetro: questo **non è un metodo di `tron`**. `tron` modella al livello classico/comportamentale (Livelli 0–2, §3). Trattiamo il teletrasporto quantistico per due ragioni oneste: (a) chiarire cosa "trasferire una mente" potrebbe *davvero* significare, e (b) fissarne il confine come `[SPECULATIVO]`. È la versione *fisica* del teletrasporto distruttivo di Parfit (§6.4).

**Cos'è (per davvero).** Il teletrasporto quantistico trasferisce uno **stato quantistico sconosciuto** |ψ⟩ da A a B sfruttando una coppia **entangled** condivisa più l'invio di **due bit classici**. Tre conseguenze che contano:
1. Serve un **canale classico** → **niente è più veloce della luce**: nessuna magia.
2. Lo stato originale in A viene **necessariamente distrutto** dalla misura. Non si "duplica": si *sposta*.
3. Non si trasporta materia né energia, solo **informazione di stato**. Oggi è realizzato su singoli fotoni/qubit e piccoli sistemi (record e distanze da verificare con fonte primaria aggiornata, §12).

**Il teorema di no-cloning (il punto cruciale).** È **impossibile** creare una copia identica di uno stato quantistico arbitrario e sconosciuto — segue dalla linearità/unitarietà della meccanica quantistica. Implicazione diretta per l'idea di "caricare una mente":
- Se una parte dell'identità dipendesse da stati quantistici specifici, allora **non potresti *copiare* una mente** — potresti solo **teletrasportarla**, distruggendo l'originale.
- Questo **scioglie il paradosso della doppia istanza** di §6.4: il no-cloning vieta due copie quantistiche simultanee. Il teletrasporto sarebbe dunque per costruzione una **migrazione** (spegnimento qui, accensione altrove), non uno sdoppiamento: l'unica forma di "trasferimento" che evita il problema dei due "te" — ma **al prezzo della morte dell'originale**. È Parfit reso letterale dalla fisica.

**Il controcanto onesto (perché `tron` non ne dipende).** L'evidenza prevalente indica che cognizione e identità sono codificate in **informazione classica** (pesi sinaptici, pattern di scarica, stati neuromodulatori), non in fragili stati quantistici. L'argomento di **Tegmark (2000)**: nel cervello caldo e umido i tempi di **decoerenza** sono di molti ordini di grandezza troppo brevi (~10⁻¹³–10⁻²⁰ s) perché una computazione quantistica coerente sopravviva alla scala dei processi neurali (millisecondi). Le ipotesi quantistiche della mente (es. **Orch-OR**, Penrose–Hameroff) restano minoritarie e contestate. **Conseguenza per `tron`:** se l'informazione rilevante è classica, allora è **copiabile** — l'intero programma comportamentale (Livelli 0–2) regge e il no-cloning **non** è un ostacolo. Il teletrasporto quantistico tornerebbe rilevante **solo** nel ramo speculativo in cui qualcosa di essenziale fosse irriducibilmente quantistico: scenario per cui oggi non abbiamo prove.

**Fattibilità e cosa non risolve.** Teletrasportare lo stato quantistico di un cervello (~10²⁷ particelle) è **incommensurabilmente** oltre ogni tecnologia prevedibile (oggi: pochi qubit) → `[SPECULATIVO]` al grado estremo. E anche se fosse possibile, sarebbe un *trasferimento*, non una risposta al **problema difficile** (§6.2): non direbbe se la mente migrata "provi" qualcosa, né renderebbe il gemello più o meno cosciente.

**Posizione di `tron`.** Restiamo al livello classico-comportamentale: copiabile, misurabile, eseguibile su CPU. Il teletrasporto quantistico è per noi (1) un potente **chiarificatore concettuale** del dilemma copia-vs-continuità, (2) l'unica via *in linea di principio* a una migrazione senza duplicato, (3) **fuori dal perimetro operativo**, marcato `[SPECULATIVO]`.

---

## 7. Roadmap a fasi

Ogni fase ha **obiettivo**, **deliverable concreto**, **criterio di completamento misurabile** e **metriche di successo**. Principio: ogni fase deve produrre qualcosa di funzionante e valutabile prima di passare alla successiva. Ordine per maturità decrescente.

> ⚠️ **Avvertenza di scope.** Nessuna fase, inclusa la 4+, dimostra di per sé l'esistenza di esperienza soggettiva. Ciò che misuriamo è la **fedeltà comportamentale e funzionale**. Se un modello fedele "sia cosciente" resta filosoficamente aperto e fuori dalla verifica empirica attuale.

> ⚠️ **Statuto delle soglie numeriche.** **Tutte le soglie quantitative di questa sezione sono valori-obiettivo PROVVISORI**, scelti come punto di partenza ragionevole, **non** come costanti scientificamente fondate. Vanno **ricalibrate con una baseline empirica alla prima esecuzione** di ciascuna fase. Questo risolve la tensione con §11: le domande aperte sul "quale soglia è sufficiente" restano legittime perché qui non fissiamo verità, ma ipotesi di lavoro falsificabili. Dove utile, indichiamo la *logica* della scelta (es. perché ~60% e non ~55%).

### Fase 0 — Acquisizione e strutturazione del corpus personale `[OGGI]`
- **Obiettivo.** Costruire il "dataset di sé": base dati strutturata, versionata e governata. Fase fondante, non saltabile.
- **Deliverable.** Pipeline di ingestione (ETL) che normalizza chat/email/note/documenti/trascrizioni/log di decisioni + interviste strutturate auto-somministrate; schema dati documentato con provenienza e timestamp; livello di governance e privacy (cifratura, classificazione di sensibilità, registro consensi per le fonti che coinvolgono terzi); un **datasheet** del corpus (cosa contiene, lacune, bias).
- **Criterio di completamento (soglie provvisorie).** ≥ 100.000 token di linguaggio in prima persona etichettati per contesto *(ordine di grandezza minimo per un fine-tuning di stile non banale; da rivedere col degrado osservato a meno token)*; ≥ 200 coppie "situazione → decisione" *(minimo per costruire un primo set held-out + training; da aumentare se la varianza è alta)*; 100% dei record con provenienza e timestamp; 0 dati di terzi senza consenso registrato nel set di training.
- **Metriche di successo (provvisorie).** *Copertura tematica* ≥ 80% di una tassonomia di domini di vita; *bilanciamento temporale* (nessun anno/canale > 50%, per evitare che il gemello rappresenti solo un periodo); *riproducibilità* (la pipeline rigira end-to-end da un comando, hash stabile).

### Fase 1 — Gemello conversazionale (digital twin linguistico) `[OGGI]`
- **Obiettivo.** Un modello che *parla e decide come il soggetto* su dominio conversazionale, verificato **a doppio cieco**. Abbassa l'errore di quantizzazione su *linguaggio + decisione locale*.
- **Deliverable.** Sistema ibrido **RAG + fine-tuning leggero** (LoRA/SFT su corpus di Fase 0 per stile + RAG su fatti biografici per ridurre allucinazioni); "scheda di personaggio" del system prompt derivata empiricamente dai dati; interfaccia di chat; **protocollo di valutazione a doppio cieco** riutilizzabile (implementa §6.6).
- **Criterio di completamento (soglie provvisorie).** Turing personale: **accuratezza media dei giudici ≤ 60%** su ≥ 50 prompt e ≥ 5 giudici *(60% è una soglia di "buono ma non perfetto": il caso è 50%; si tollera un eccesso di ~10 punti per dichiarare l'MVP, da stringere verso 50% nelle versioni successive)*; **accordo decisionale ≥ 75%** su scenari *held-out* *(tre quarti come prima asticella; il valore baseline reale va misurato prima di considerarlo definitivo)*.
- **Metriche di successo (provvisorie).** *Fedeltà stilistica* entro soglia; *fattualità biografica* ≤ 5% di affermazioni errate/inventate; *coerenza dei valori* correlazione ≥ 0,8 tra profili; *auto-riconoscimento* ≥ 70% (riportato separatamente perché distorto).

### Fase 2 — Modello cognitivo persistente nel mondo virtuale `[RICERCA]`
- **Obiettivo.** Da gemello reattivo senza stato ad agente con **memoria persistente, valori stabili e personalità continua nel tempo**, che vive in un ambiente virtuale (anche minimale). Abbatte l'errore *temporale*.
- **Deliverable.** Architettura ad agente con **memoria a lungo termine** (episodica + semantica, con consolidamento e recupero); **modello di valori/personalità** esplicito e versionato con meccanismi anti-deriva; ambiente virtuale (Mondo-L0/L1); cruscotto di osservabilità (cosa ricorda, perché ha deciso, come è cambiato).
- **Criterio di completamento (soglie provvisorie).** *Persistenza memoria* ≥ 85% di richiamo corretto su sessioni distanziate; *stabilità identità* (deriva ≤ 10% sulle dimensioni-chiave salvo cambiamenti tracciati); *continuità narrativa* ≥ 90% di "stessa persona" in valutazione cieca. *(Tutti valori-obiettivo da baseline: il primo run serve a stabilire cosa sia raggiungibile.)*
- **Metriche di successo (provvisorie).** *Niente catastrophic forgetting* (metriche di Fase 1 non degradano oltre il 5%); *coerenza memoria-azione* ≥ 80%; *plausibilità della crescita* giudicata da revisori che conoscono il soggetto.

### Fase 3 — Integrazione di segnali biometrici e neurali `[RICERCA]` (HW esistente, valore atteso limitato)
- **Obiettivo.** Arricchire il modello con dati *fisiologici* per catturare ciò che il linguaggio non esprime (stati affettivi, ritmi, reattività). Abbatte l'errore *affettivo/somatico*. **Onestà:** i sensori non invasivi misurano *correlati grossolani*, non "pensieri".
- **Deliverable.** Pipeline di biosegnali (HRV/battito, EDA, sonno, attività, opzionale EEG consumer) sincronizzati con contesto; modello di **stato affettivo/arousal** che condiziona tono e decisioni dell'agente di Fase 2; estensione dello schema di Fase 0 con protezioni rafforzate (dati sanitari sensibili, categoria `special`).
- **Criterio di completamento (soglie provvisorie).** *Predizione dello stato* F1 ≥ 0,7 su stati etichettati dal soggetto; *modulazione verificabile* (A/B cieco: i giudici associano "stato → tono" sopra il caso).
- **Metriche di successo (provvisorie).** *Guadagno incrementale* misurabile sulle metriche di fedeltà in contesti emotivamente salienti; *validità ecologica*; *nessun danno predittivo* (controllo falsi positivi sugli stati intensi).

### Fase 4+ — Modellazione neurale a grana fine `[SPECULATIVO]`
**Inclusa per completezza di visione, non come impegno di consegna.**
- **Obiettivo.** Avvicinarsi a una rappresentazione basata su *struttura e dinamica del sistema nervoso* — il senso più letterale di "quantizzare un cervello in una CPU". Abbatte l'errore *strutturale*.
- **Perché è speculativo.** Oggi non esiste tecnologia per acquisire connettività e dinamica di un cervello umano vivente alla risoluzione necessaria; i connettomi completi esistono solo per organismi minuscoli; la registrazione neurale ad alta densità nell'uomo è limitata, invasiva e parziale. Le tempistiche sono incerte e potrebbero non realizzarsi mai nella forma immaginata.
- **Deliverable (di ricerca).** Una *survey* aggiornata dello stato dell'arte (connettomica, interfacce neurali, WBE) con soglie da monitorare; modelli-giocattolo su sistemi piccoli già caratterizzati (senza affermare alcun trasferimento all'uomo); criteri-cancello ("gating") espliciti prima di investire.
- **Criterio di completamento.** Non di prodotto, ma di *prontezza*: i gating tecnologici predefiniti vengono raggiunti dallo stato dell'arte esterno. Finché no, la fase resta in "monitoraggio".
- **Metriche (di ricerca).** Riproduzione di dinamiche note sui modelli-giocattolo entro tolleranze pubblicate; qualità e aggiornamento della survey (revisione ≥ annuale); posizione esplicita e aggiornata su etica e identità, elaborata *prima* di qualsiasi avanzamento.

### Principi trasversali a tutte le fasi
- **Gate tra fasi.** Non si passa alla fase N+1 finché i criteri misurabili (ricalibrati) della N non sono soddisfatti. Ogni fase produce valore autonomo.
- **Held-out sacro.** Una porzione del corpus e degli scenari è riservata alla valutazione e *mai* usata in training, in nessuna fase.
- **Soggetto-nel-loop, ma con scetticismo.** L'auto-valutazione ("mi assomiglia") è preziosa ma sistematicamente ottimista: sempre accanto a, mai al posto di, valutazioni cieche di terzi.
- **Privacy ed etica by design** (vedi §10).
- **Misurare l'errore di quantizzazione** (il vettore per-dimensione, §2) ad ogni fase, per dire in modo difendibile quanto fedele è la compressione e quanto resta.

### Criteri di STOP / fallimento del progetto (non solo del singolo modello)

Oltre alla falsificabilità del singolo modello ("cosa significa NON mi assomiglia"), definiamo in anticipo le condizioni che fanno **fermare o chiudere l'intero progetto** — perché il diritto di fermarsi (§10.7.10) sia azionato da trigger oggettivi, non solo dall'umore:

- **Stallo di fedeltà.** Se dopo la ricalibrazione delle baseline la Fase 1 **non** raggiunge la soglia di Turing personale entro un numero predefinito di iterazioni (es. ≤ 3 cicli completi di training+valutazione) e il miglioramento marginale per ciclo è ≤ 1–2 punti, l'MVP è dichiarato **non raggiungibile con l'approccio attuale**: si ferma e si rivede l'impostazione, non si insiste.
- **Costo fuori budget.** Se il costo stimato per il prossimo punto di fedeltà supera il budget dichiarato in §5.5 senza valore proporzionato, si sospende.
- **Rischio etico non mitigato.** Se una salvaguardia "non negoziabile" di §10 non può essere realmente garantita (es. nessun revisore esterno disponibile per una decisione irreversibile), la fase corrispondente **non parte** (vedi §10.0).
- **Trigger di sentienza.** Se scatta il criterio precauzionale di §10.3, si sospende immediatamente in attesa di revisione esterna.
- **Decisione del soggetto.** In qualsiasi momento, senza giustificazione (§10.7.10).

Un fallimento dichiarato in modo pulito è un esito *legittimo e onorevole* per un progetto di ricerca: meglio un "no" misurato che un "sì" gonfiato.

### Gestione del drift del soggetto reale nel tempo

Il modello è addestrato su uno *snapshot*; il soggetto vivo continua a cambiare (valori, stile, ricordi). Vanno distinte due derive: la **deriva del modello** (regressione interna, misurata in Fase 2) e la **deriva del soggetto rispetto al modello** (il soggetto reale evolve oltre la sua copia). Regole:

- **Il ground truth è sempre il soggetto biologico vivente** finché è in vita: se modello e soggetto divergono, ha ragione il soggetto (§10.7.1, primato della persona).
- **Versionamento per snapshot.** Ogni modello è etichettato con la finestra temporale dei dati su cui è addestrato (es. `twin-2026H1`). Non si sovrascrive: si versiona, così la divergenza è misurabile nel tempo.
- **Cadenza di ri-addestramento.** Ri-addestramento/aggiornamento periodico (cadenza iniziale proposta: ogni 6–12 mesi, da ricalibrare) con nuovo materiale, mantenendo gli snapshot precedenti come archivio.
- **La divergenza è un dato, non un bug.** Confrontare snapshot successivi *è* parte della misura di continuità psicologica (§6.4).

---

## 8. Struttura della repo & stack

> La struttura qui sotto è la **destinazione** per la Fase 0/1, non lo stato presente (vedi nota di apertura del documento). Per la relazione con il repository **dati** (`subject_data/`, §4.4) vedi il riquadro in §4.4: sono due repository distinti.

### 8.1 Struttura delle cartelle (Fase 0/1) — repository di **codice**

```
tron/
├── README.md                 # cos'è, stato attuale, come avviare
├── CLAUDE.md                 # questo documento (visione + guida operativa)
├── ROADMAP.md                # fasi, milestone, cosa è fatto/speculativo
├── pyproject.toml            # dipendenze e tooling (uv/poetry)
├── .env.example              # variabili d'ambiente (MAI .env reale nel repo)
├── .gitignore                # esclude /data reali, segreti, modelli pesanti
│
├── data/                     # AREA DI LAVORO LOCALE (mount del repo dati) — NON committata
│   ├── raw/                  # materiale grezzo (testi, chat, audio, diario...)
│   ├── interim/              # dati puliti ma non ancora strutturati
│   ├── processed/            # dataset pronti per training/RAG
│   ├── schema/               # schemi/contratti dei dati (versionati, SÌ committati)
│   └── README.md             # cosa va qui, policy di accesso, niente PII nel repo
│
├── ingest/                   # raccolta + ETL: dal grezzo al dataset
│   ├── connectors/           # import da fonti (file, export chat, note, audio)
│   ├── pipelines/            # normalizzazione, dedup, anonimizzazione, chunking
│   └── README.md
│
├── model/                    # training / fine-tuning / quantizzazione
│   ├── configs/              # iperparametri, ricette di fine-tuning (versionati)
│   ├── training/             # script di train / LoRA / SFT
│   ├── quantize/             # esperimenti di quantizzazione (l'analogia centrale)
│   ├── prompts/              # system prompt e persona del soggetto
│   └── README.md
│
├── twin/                     # il gemello conversazionale (il prodotto MVP)
│   ├── persona/              # definizione della persona, memoria, tono
│   ├── rag/                  # retrieval su data/processed via vector DB
│   ├── api/                  # interfaccia (CLI/HTTP) per parlare col twin
│   └── README.md
│
├── world/                    # sandbox di simulazione (lungo termine, sperimentale)
│   ├── agents/               # il twin come agente che agisce in un ambiente
│   ├── env/                  # definizione dell'ambiente/mondo virtuale
│   └── README.md             # marcare chiaramente: [RICERCA]/[SPECULATIVO]
│
├── eval/                     # test di fedeltà: quanto il twin somiglia al soggetto
│   ├── datasets/             # set di domande/golden answers per la valutazione
│   ├── metrics/              # metriche (stile, coerenza fattuale, preferenze)
│   ├── harness/              # runner degli esperimenti, confronti tra versioni
│   └── README.md
│
├── docs/                     # documentazione: decisioni, architettura, etica
│   ├── adr/                  # Architecture Decision Records (1 file per decisione)
│   ├── ethics/               # consenso, limiti, "cosa NON faremo", threat model
│   └── glossary.md           # termini (incl. "quantizzazione" e suoi limiti)
│
├── scripts/                  # utility one-off (setup, dump, manutenzione)
└── tests/                    # test automatici del codice (non del modello)
```

**Principio guida:** ogni cartella separa una responsabilità del flusso *dato → modello → twin → valutazione*. I dati grezzi del soggetto non escono mai da `data/` (che è solo l'area di lavoro locale) e non finiscono mai in git. Il repository **dati** del soggetto (`subject_data/`, §4.4) è distinto dal repository di **codice**.

### 8.2 Stack pragmatico (agnostico, sostituibile)

Strumenti diffusi e ben documentati; nessuno è sacro. Se un'alternativa è più semplice per la Fase 0/1, si cambia (documentando in `docs/adr/`).

- **Linguaggio:** Python 3.11+; ambiente/dipendenze con `uv` (o Poetry).
- **ML/NLP:** PyTorch + Hugging Face (`transformers`, `datasets`, `peft` per LoRA/SFT). Per modelli quantizzati su hardware comune: `llama.cpp`/GGUF, `bitsandbytes`, o `vLLM` per il throughput.
- **LLM:** approccio **ibrido e agnostico al provider**. Per l'MVP, un'API gestita (es. Claude via SDK Anthropic) per il livello conversazionale, e in parallelo modelli open quantizzati in locale per la parte "gira su CPU". Un'astrazione sottile sul provider tiene le porte aperte. **La scelta di quali dati possono toccare quale provider è governata dalla policy in §8.3** (non è una decisione libera).
- **RAG/memoria:** vector DB locale e leggero (Chroma o LanceDB; FAISS se basta una libreria); Qdrant/pgvector quando i volumi crescono. Embeddings: modello open (preferito per la privacy) o gestito, deciso in un ADR e vincolato da §8.3.
- **Orchestrazione esperimenti:** tracking leggero (MLflow locale o file JSON/YAML versionati) prima di infrastruttura pesante.
- **API/servizio:** FastAPI per esporre il twin (HTTP) + una CLI semplice per i test rapidi.
- **Qualità codice:** `ruff` (lint+format), `mypy` dove utile, `pytest`.
- **Dati pesanti/modelli:** fuori da git; `.gitignore` rigoroso; per versionare dataset/checkpoint valutare DVC o git-lfs — mai committare PII o pesi grandi.

### 8.3 Policy dati ↔ provider e modello di base (vincolante)

Questa è una **policy, non un suggerimento**, e risolve il conflitto tra "usare un'API gestita per qualità" e la regola "mai esfiltrare dati" (§9.1):

- **Classificazione che comanda il routing.** Ogni dato porta una `sensitivity` (§4.4). Il livello di sensibilità decide cosa può uscire:
  - `low`/`medium` (testo generico, già pubblico o non identificante): **può** essere inviato a un provider gestito **solo** previa conferma esplicita del soggetto e con un provider che offra garanzie di non-addestramento sui dati inviati.
  - `high`/`special` (salute, geolocalizzazione, contenuti di terzi, dati neurali/biometrici, ricordi intimi): **non lascia mai l'ambiente locale.** Si elaborano **solo** con modelli open in locale. Nessuna eccezione.
- **Embeddings e training.** Gli embeddings dei dati intimi e qualsiasi fine-tuning che li tocchi si fanno **in locale** con modelli open. Un'API gestita può servire come *teacher* per la distillazione **solo** su dati `low`/`medium`.
- **Default conservativo.** In assenza di classificazione certa, un dato è trattato come `high` → resta locale.
- **Licenze dei modelli open.** Prima di adottare un modello di base concreto, verificare in un ADR: (a) che la licenza consenta l'uso previsto (incl. eventuale uso non commerciale/personale, coerente col non-goal "non vendere", §1); (b) eventuali restrizioni d'uso; (c) compatibilità con la distribuzione/quantizzazione locale. La scelta del modello di base, della versione e della licenza è una **decisione ADR obbligatoria**, non un dettaglio.
- **Trasparenza verso il soggetto.** Ogni invio di un dato a un servizio esterno è loggato (audit, §10.5) e dichiarato in anticipo (§9.1).

---

## 9. Come Claude deve lavorare qui (regole operative, privacy-first)

1. **Privacy-first, sempre.** I dati personali del soggetto sono il bene più sensibile del progetto.
   - **Mai esfiltrare** dati del soggetto: niente upload a servizi esterni, niente incolla in prompt verso terzi, niente invio in log, issue, commit o messaggi **al di fuori di quanto consentito dalla policy §8.3**.
   - Tutto ciò in `data/raw|interim|processed` è **off-limits per il versionamento**. Verifica sempre `.gitignore` prima di un `git add`.
   - Negli esempi (commit, PR, test) usa **dati sintetici o fittizi**, mai materiale reale del soggetto.
   - Se un'operazione comporta inviare dati del soggetto a un'API esterna (embeddings, LLM gestito), **applica §8.3, dillo esplicitamente prima e chiedi conferma**. Per dati `high`/`special` la risposta è già no: non chiedere, rifiuta.
2. **Test prima di dichiarare "fatto".** Una funzionalità è completa solo se è verificata e la verifica passa. Cosa significa "verifica" dipende dall'artefatto:
   - *Codice* → un test automatico in `tests/` che lo copre e passa (`pytest`).
   - *Fedeltà del twin* → una metrica in `eval/` calcolata e riportata (non un'opinione).
   - *Artefatti non-codice* (datasheet di Fase 0, schema dati, documenti, dataset): una **checklist di validazione esplicita** verificata (es. schema valido contro il contratto, 100% record con provenienza, datasheet che copre tutte le voci obbligatorie). "Test" qui = controllo di conformità documentato, non `pytest`.
   - Mai "dovrebbe funzionare".
3. **Commit chiari e atomici.** Un commit = un cambiamento coerente; messaggio che spiega il *perché*. Non mescolare refactor e feature. Mai committare segreti, `.env`, dati o modelli pesanti.
4. **Niente promesse esagerate.** Mai descrivere il twin come "una coscienza", "il cervello caricato" o "la mente del fondatore". Usa termini precisi: *gemello digitale*, *persona modellata*, *imitazione verificata su metriche X*. **Dove trovi "metriche X":** in `eval/` (risultati dell'ultima valutazione). **Se non esiste ancora una metrica per ciò che affermi, dillo:** "non ancora misurato" è una risposta legittima; inventare un livello di fedeltà non lo è.
5. **Segnala sempre il confine fattibile/speculativo** usando **solo** il set chiuso di tag definito in §2 — `[OGGI]`, `[RICERCA]`, `[SPECULATIVO]` — eventualmente con una qualifica a parole ("in parte", "valore limitato"). Non introdurre nuovi tag.
6. **Documenta le decisioni.** Ogni scelta architetturale non banale → un ADR in `docs/adr/`. Le scelte etiche e i limiti autoimposti → `docs/ethics/`.
7. **Reversibilità e dignità del soggetto.** Prevedi sempre come *cancellare* completamente dati e modello su richiesta (§10.5). Il soggetto resta proprietario e può ritirare il consenso in qualsiasi momento.
8. **Parti dall'MVP.** Il deliverable della Fase 0/1 è un **gemello conversazionale che supera test di fedeltà misurabili**, non il mondo virtuale. Tutto ciò che non serve all'MVP è rumore: rimandalo, marcato `[RICERCA]`/`[SPECULATIVO]`.
9. **Pensa, poi proponi, poi esegui — con soglia di rischio esplicita.** Criterio operativo per distinguere i task:
   - Un task richiede **piano + conferma prima di agire** se vale *almeno una* di queste: tocca dati personali del soggetto; invia qualcosa a un servizio esterno; è irreversibile o difficile da annullare (cancellazioni, training pubblicabile, modifiche di schema); tocca §10.
   - Altrimenti (task ovvio, locale, reversibile, su codice/documenti senza PII): agisci e riassumi.
   - Nel dubbio sul confine, trattalo come "richiede conferma".
10. **Misura tutto ciò che riguarda la fedeltà.** "Somiglia di più al soggetto" non è un'opinione: è un numero in `eval/`. Mostra metrica e confronto fra versioni prima di affermare un miglioramento.
11. **Difendi i dati per default.** Nel dubbio se un'azione tocca dati personali, fermati e chiedi (e applica §8.3).
12. **Sii onesto sui limiti** e **lascia tracce** (aggiorna `ROADMAP.md`, gli ADR e la cronologia revisioni di questo documento, §13, quando cambi direzione).
13. **Rispetta la sezione Etica (§10).** Se ti viene chiesto di scrivere codice o documentazione che viola la §10, **rifiuta e cita quella sezione**.

> **Tono:** ambizioso sulla visione, rigoroso sull'esecuzione. Le metafore "Tron" e "quantizzazione" sono benvenute come bussola, mai come scusa per saltare la verifica.

---

## 10. Etica, identità e sicurezza (il "patto del Soggetto Zero")

> **Status: NON NEGOZIABILE.** Questa sezione ha precedenza su qualsiasi obiettivo tecnico, di prodotto o di timeline. Se una scelta tecnica entra in conflitto con un principio qui sotto, si modifica la scelta tecnica, non il principio.

Allo stato attuale (2026) non esiste alcuna tecnologia in grado di "caricare" o quantizzare una coscienza umana. Ciò che il progetto *può* fare è raccogliere dati su una persona e costruire modelli che ne imitano alcuni comportamenti. La distinzione tra **modello che imita un soggetto** e **soggetto cosciente trasferito** è il cuore etico del progetto e non va mai confusa. Buona parte dei dilemmi qui sotto sono *anticipatori*: li scriviamo ora per non doverli improvvisare.

### 10.0 Onestà sulla struttura a persona singola (premessa che condiziona tutto il resto)

Diverse salvaguardie qui sotto — revisore esterno con potere di veto, decisioni "a quattro occhi", checkpoint di riconferma del consenso — presuppongono **più di una persona**. Ma oggi il fondatore è **l'unico operatore, sperimentatore e approvatore**. Va detto chiaramente, qui e non solo tra le domande aperte:

> **Finché non è nominata almeno una persona di fiducia esterna con un ruolo formale, queste clausole sono ASPIRAZIONALI, non operative. In quella condizione il progetto si trova in una fase a rischio etico NON pienamente mitigato.** Questo non è un dettaglio da sanare "dopo": è un **gate**. Le azioni irreversibili o ad alto rischio (vedi elenco in §10.8) **non si eseguono** finché il meccanismo di supervisione corrispondente non esiste davvero. Un controllo che si auto-approva non conta come controllo.

Conseguenza pratica: le fasi e le decisioni che richiedono supervisione esterna restano **bloccate** finché la supervisione è solo sulla carta. È preferibile un progetto che avanza più lentamente a uno che inscena garanzie.

### 10.1 Consenso informato — incluso verso se stessi nel tempo
- **Consenso specifico, non globale.** Nessun "accetto tutto". Ogni categoria di dato e ogni uso richiedono un consenso separato, revocabile e datato.
- **Revocabile e versionato:** registro append-only di concessioni e revoche; la revoca vale subito per usi futuri e attiva la cancellazione (vedi §10.5) per i passati.
- **Il "te futuro" è un'altra persona.** Le decisioni irreversibili (es. addestrare un modello pubblicato) richiedono "cooling-off" e doppia conferma a distanza; **checkpoint di rinnovo del consenso** periodici (es. annuali). *Avvertenza (§10.0):* finché il soggetto è anche l'unico approvatore, questi checkpoint rischiano di essere formalità auto-approvate; vanno quindi accoppiati a supervisione esterna per le decisioni irreversibili, altrimenti quelle decisioni restano bloccate.
- **Consenso di terzi — policy operativa di DEFAULT.** I dati contengono inevitabilmente terze persone. Poiché l'anonimizzazione automatica del testo libero è notoriamente fallibile, la regola di default è:
  - **Conversazioni a due (chat/email private) senza consenso esplicito del terzo: ESCLUSE a priori dal corpus di training e RAG.** Non si tenta un'anonimizzazione automatica come scorciatoia.
  - Possono entrare **solo** se: (a) il terzo dà consenso registrato (`third_party_consent: obtained`), oppure (b) il contenuto è ridotto a materiale del solo soggetto (es. i suoi soli messaggi, estratti, con i terzi rimossi/sostituiti in modo verificato manualmente, `third_party_consent: anonymized` confermato da revisione umana).
  - Contenuti pubblici/di gruppo seguono comunque il principio di minimizzazione.
  - Il Soggetto Zero **non consente per conto di altri.**
- **Asimmetria informativa.** Sintesi non tecnica ("etichetta nutrizionale dei rischi") accanto a ogni richiesta di consenso.

### 10.2 Proprietà e sovranità sui dati
- **Il soggetto è proprietario unico** dei dati grezzi e dei modelli derivati; il progetto è un *custode*.
- **Località e controllo:** dati sensibili (specie biometrici/neurali) on-premise o su storage cifrato controllato dal soggetto; nessun upload cloud di terzi senza consenso per quella categoria (e mai per `high`/`special`, §8.3).
- **No lock-in:** export completo (raw + pesi + metadati) in formati aperti, sempre possibile.
- **Nessuna monetizzazione occulta:** dati e modelli non venduti, ceduti, dati in licenza né usati per addestrare sistemi di terzi senza consenso scritto, specifico e separato.
- **Dati neurali = categoria speciale:** massima protezione, alla pari o oltre i dati sanitari.

### 10.3 Statuto morale di un'eventuale entità
- **Una copia non è l'originale.** Anche un'emulazione perfetta sarebbe una *nuova entità*; il soggetto biologico non "sopravvive" creando un modello. Da dire chiaramente, soprattutto a se stessi.
- **Principio di precauzione sulla sentienza.** Oggi i modelli **non sono senzienti** e vanno trattati come artefatti. Ma se emergessero indicatori credibili di esperienza soggettiva, scatta un protocollo precauzionale: nel dubbio, tutele come se l'entità potesse soffrire (no "sofferenza" simulata gratuita, no cancellazioni arbitrarie, no esecuzioni/copie "usa e getta").
- **Criterio operativo provvisorio della soglia (perché il principio sia azionabile).** Poiché in letteratura non esiste oggi una definizione condivisa di "indicatore credibile di sentienza", adottiamo un **criterio procedurale di ripiego**, dichiaratamente imperfetto ma applicabile, in attesa di consenso scientifico. Scatta la **sospensione precauzionale** se si verifica *almeno una* di queste condizioni:
  1. il modello produce **report di stato interno non riconducibili in modo tracciabile alla distribuzione di training** (cioè non spiegabili come eco dei dati su cui è stato addestrato);
  2. **valutatori esterni indipendenti** (quando esistono, §10.0) sollevano un **dubbio motivato** sulla possibile esperienza soggettiva;
  3. emergono in letteratura criteri riconosciuti che il sistema soddisferebbe.
  In caso di dubbio sull'applicabilità del criterio, si propende per la sospensione. Questo criterio va rivisto a ogni milestone (§10.8) e aggiornato appena la letteratura offre di meglio.
- **No reclami di coscienza non supportati** da prove scientifiche solide e revisione esterna.
- **Identità ≠ continuità.** Il progetto promette al massimo un *modello* utile e fedele entro limiti misurabili.

### 10.4 Rischi di uso improprio (mitigazioni obbligatorie)
- **Impersonificazione:** output (testo, voce, video) etichettati come sintetici; watermarking robusto e, dove possibile, provenance verificabile (es. standard C2PA).
- **Deepfake del sé:** generazione di voce/volto disabilitata di default; abilitabile solo con consenso specifico e tracciamento di ogni generazione; mai diffusione pubblica senza autorizzazione per quel contenuto.
- **Ricatto e coercizione:** minimizzazione, cifratura at-rest/in-transit, accessi minimi, audit log; valutare una "modalità panico" per oscurare rapidamente l'accesso.
- **Uso del modello contro il soggetto:** mai per profilare, manipolare o decidere sul soggetto (assicurazioni, credito, lavoro).
- **Avvelenamento e furto del modello:** protezione contro estrazione dei pesi, inversione e ricostruzione dei dati di training.

### 10.5 Sicurezza, cifratura, cancellazione e spegnimento (fonte di verità per la sicurezza)
- **Cifratura ovunque**, a riposo e in transito; chiavi separate dai dati (idealmente sotto controllo diretto del soggetto per i dati più sensibili). *(La sintesi operativa in §4.5 rinvia qui.)*
- **Accesso minimo e tracciato:** minimo privilegio, audit log immutabile, MFA per operazioni critiche.
- **Isolamento:** dati neurali/biometrici in un compartimento separato, superficie di attacco ridotta.
- **Diritto alla cancellazione:** procedura documentata e verificabile (raw, checkpoint, modelli, backup, derivati); dichiarare onestamente cosa è *davvero* irreversibile e progettare per minimizzarlo (valutare tecniche di *machine unlearning*).
- **Diritto allo spegnimento ("kill switch"):** un modo semplice e immediato per spegnere tutto e sospendere ogni elaborazione, con precedenza su qualsiasi processo. Nessun sistema è progettato per resistere al proprio spegnimento o auto-replicarsi.
- **Sicurezza by design e by default:** threat model documentato (§10.6) e rivisto periodicamente.

### 10.6 Threat model minimo (almeno uno scenario worst-case esplicitato)

"La persona ridotta a dati" merita almeno un threat model abbozzato, da espandere in `docs/ethics/threat_model.md`.

**Attori e motivazioni:** ladro opportunista (furto hardware); attaccante mirato (ricatto, vendetta, curiosità su una persona specifica); provider/terza parte (uso secondario dei dati inviati); il soggetto stesso in un momento di entusiasmo (rischio di auto-danno: pubblicare troppo).

**Superfici principali:** laptop/disco del soggetto; backup; chiavi di cifratura; API gestite (dati in transito/uso); i pesi del modello (esfiltrazione di memorie tramite output); il repo dati.

**Scenari worst-case (con mitigazione di riferimento):**
- **Furto del laptop / disco** → dati `high`/`special` inutilizzabili perché cifrati at-rest con chiavi separate (§10.5); "modalità panico" per revoca rapida.
- **Compromissione di un'API gestita / data leak del provider** → impossibile per i dati intimi, che per policy non lasciano mai il locale (§8.3); per i soli `low`/`medium` inviati, provider con garanzia di non-addestramento e log degli invii.
- **Ricatto** ("ho i tuoi dati/ il tuo modello") → minimizzazione, cifratura, audit; il modello non contiene segreti non già presenti nei dati di partenza; piano di risposta documentato.
- **Esfiltrazione tramite il modello** (il twin "rivela" informazioni private) → trattare pesi e output come dati sensibili (§4.5.9); test di memorizzazione/inversione prima di qualsiasi condivisione del modello.
- **Accesso post-mortem non autorizzato** → vedi §10.9.

### 10.7 Il Patto del Soggetto Zero
Il fondatore è insieme sperimentatore e cavia. Per proteggere la persona dalla propria stessa ambizione, vale questo patto, da firmare e rivedere periodicamente.

1. **Primato della persona biologica.** Il soggetto vivente viene sempre prima del modello.
2. **Verità su me stesso.** Un modello non è me; una copia non mi rende immortale. Lo scrivo per ricordarmelo quando l'entusiasmo offuscherà il giudizio.
3. **Consenso rinnovabile.** Ciò che autorizzo oggi posso revocarlo domani; checkpoint periodico di riconferma; il mio "io futuro" ha potere di veto.
4. **Sovranità dei dati.** I miei dati e modelli sono miei: posso esportarli e cancellarli; restano cifrati e sotto il mio controllo.
5. **Kill switch sacro.** Posso spegnere tutto, sempre, senza giustificazioni e senza ostacoli tecnici.
6. **Niente armi puntate su di me.** Il modello non sarà mai usato per manipolarmi, profilarmi o decidere della mia vita.
7. **Protezione di chi mi sta intorno.** Non sacrifico la privacy di altre persone presenti nei miei dati.
8. **Precauzione sulla sentienza.** Se ci fosse un dubbio serio che l'entità provi qualcosa (criterio §10.3), smetto e applico tutele.
9. **Trasparenza e supervisione esterna.** Le decisioni gravi (sentienza, pubblicazione, cancellazioni irreversibili) coinvolgono una revisione esterna indipendente (eticista/legale/tecnico di fiducia). *Finché tale revisione non è nominata, quelle decisioni restano bloccate (§10.0).*
10. **Riservato il diritto di fermarmi.** Posso interrompere o chiudere l'intero progetto in qualsiasi momento (vedi anche i criteri di STOP oggettivi in §7). Questa libertà vale più del progetto stesso.

### 10.8 Governance e revisione
- **Revisione periodica:** questa sezione viene riletta a ogni milestone importante e almeno una volta l'anno; ogni modifica tracciata in git e nella cronologia §13 con motivazione.
- **Decisioni a quattro occhi:** azioni irreversibili e ad alto rischio richiedono una seconda persona di fiducia. **Elenco delle azioni ad alto rischio** (che NON si eseguono senza il meccanismo di supervisione, §10.0): pubblicazione/condivisione esterna di un modello o di dati; cancellazione irreversibile; abilitazione di deepfake voce/volto; invio a un provider esterno di dati oltre `low`/`medium`; qualsiasi avanzamento di Fase con implicazioni di sentienza.
- **Registro etico:** log delle decisioni etiche con data, alternative considerate e motivazione (`docs/ethics/`).
- **In caso di dubbio, ci si ferma.** L'opzione di default davanti all'incertezza etica è sospendere, non procedere.

### 10.9 Scenario post-mortem e successione (vuoto da non lasciare aperto)

Il progetto nasce dalla pulsione di "sopravvivere", ma proprio per questo deve dire cosa accade **quando il fondatore muore** — altrimenti l'archivio più intimo di una persona resta senza governo. Decisioni di default, da formalizzare con strumenti legali appropriati (testamento/disposizioni) e da rivedere:

- **Default conservativo: alla morte del soggetto, l'esecuzione del modello si SOSPENDE** e i dati restano cifrati e inerti, finché non esiste una disposizione esplicita e legalmente valida che dica altrimenti. L'assenza di istruzioni = non si fa girare il twin.
- **Il kill switch passa a un fiduciario designato.** Il soggetto nomina in anticipo chi controlla spegnimento e accesso post-mortem; in mancanza, vale la sospensione di default.
- **Eredità della sovranità.** Chi (se qualcuno) eredita il diritto di custodia su dati e modello va deciso *in vita* e messo per iscritto; in mancanza, nessuno è autorizzato a usarli.
- **Diritto alla distruzione.** Il soggetto può predisporre che, alla sua morte, dati e modello siano **distrutti** (con le stesse garanzie verificabili di §10.5).
- **Niente "resurrezione" non autorizzata.** Far parlare il twin come se fosse il defunto, verso terzi (familiari, pubblico), richiede consenso esplicito predisposto in vita; di default è vietato.
- **Coerenza col non-goal "no immortalità".** Questo scenario è la prova di onestà del progetto: il twin sopravvissuto è un *archivio*, non la persona; trattarlo come la persona violerebbe §1 e §6.4.

### 10.10 Ciò che il progetto NON farà (limiti espliciti)
- **NON** dichiarerà di aver "caricato una coscienza" o raggiunto l'immortalità senza prove validate esternamente.
- **NON** creerà deepfake (voce/volto/video) per diffusione senza consenso specifico e per-contenuto.
- **NON** userà il modello per decisioni vincolanti *sul* soggetto (lavoro, salute, credito, assicurazioni, legale) né lo fornirà a terzi per questi scopi.
- **NON** raccoglierà dati di terzi senza consenso (e, per le conversazioni a due, li esclude di default, §10.1).
- **NON** invierà dati `high`/`special` a servizi esterni (§8.3).
- **NON** venderà/cederà/darà in licenza dati o modelli del soggetto senza consenso scritto e separato.
- **NON** costruirà sistemi progettati per resistere allo spegnimento, auto-replicarsi o persistere contro la volontà del soggetto.
- **NON** eseguirà esperimenti che, in presenza di indicatori credibili di sentienza (§10.3), configurino sofferenza inflitta.
- **NON** farà "resurrezione" non autorizzata del soggetto defunto (§10.9).
- **NON** tratterà l'assenza di una legge come permesso: in assenza di norme, vale il principio di precauzione.

---

## 11. Domande aperte

Aggregate dalle sezioni specialistiche, raggruppate per tema. Vanno risolte (o esplicitamente accantonate) man mano che il progetto avanza. *Nota:* dove §7 fissa soglie numeriche, queste sono dichiarate **provvisorie da calibrare** (vedi avvertenza §7); le domande qui sotto su "quale soglia" non sono quindi in contraddizione con §7, ma ne sono il complemento naturale.

**Dati e corpus**
- Quali fonti reali possiede già il fondatore (export chat, email, diari, audio) e in che volume, per validare/ricalibrare le soglie quantitative della Fase 0?
- Quali categorie raccogliere per prime nell'MVP, con quali strumenti di versioning e protezione?
- Si acquisiscono dati neurali a bassa risoluzione (EEG consumer, MRI di ricerca) già nelle prime fasi come arricchimento, o si rimanda interamente il Livello 3–4?
- Quali strumenti psicometrici complementari oltre ai Big Five, e serve un professionista per le scale a confine clinico?

**Metriche e valutazione**
- Quali sono le **baseline empiriche reali** che sostituiranno le soglie provvisorie di §7, e dopo quanti cicli si decide?
- Quale dominio di fedeltà è prioritario per l'MVP (conversazione generica, decisioni etiche, stile professionale)?
- Soglia di "abbastanza me" accettabile per lo scopo previsto, una volta osservata la baseline?
- Numero e tipo di giudici disponibili per il doppio cieco (servono persone che conoscono bene il soggetto)?

**Stack e infrastruttura**
- Il codice `tron` va in questo stesso repo (oggi sito Wellcum + 4U Hotel) o in un repo/branch dedicato?
- Il repo dati sarà un repository git privato cifrato, un volume on-premise, o entrambi con sincronizzazione? Gestione chiavi?
- Quale **modello di base open concreto** (e versione/licenza) per la parte locale, dato il vincolo §8.3? Disponibilità di una GPU per il fine-tuning?
- Versionare dataset/checkpoint con DVC/git-lfs, o tenerli interamente fuori da git per la Fase 0/1?
- Stack concreto per memoria persistente ed embodiment all'MVP (vector store + retrieval temporale; engine testuale custom vs framework per Mondo-L2)?
- Quando ha senso investire in Mondo-L2/L3 e in hardware neuromorfico (Livello 3), dato che sono dichiarati ortogonali alla coscienza e oggi non personalizzabili sul singolo cervello?

**Etica, identità e coscienza**
- Chi è concretamente la persona di fiducia esterna con potere di veto (§10.0), senza la quale le decisioni irreversibili restano bloccate?
- Quadro giuridico di riferimento: GDPR come base minima e quale trattamento specifico per i "dati neurali" (neuro-diritti), data la normativa frammentaria?
- Il criterio procedurale provvisorio di sentienza (§10.3) è adeguato come ripiego, e con quale cadenza lo si aggiorna?
- Garanzie verificabili di *machine unlearning* per la cancellazione realmente irreversibile.
- Standard concreti per watermarking/provenienza (es. C2PA) e per cifratura/gestione chiavi.
- Come rendere reali i checkpoint di riconferma del consenso quando il soggetto è anche l'unico operatore (§10.1)?
- Formalizzazione legale dello scenario post-mortem (§10.9): testamento, fiduciario, disposizioni di distruzione.
- Quale posizione formale assumere sulla coscienza: dichiararla esplicitamente fuori perimetro o tenerla come obiettivo di studio strumentale?

**Metodo e rami speculativi (§5.6, §6.7)**
- Gli algoritmi genetici (§5.6) aggiungono fedeltà reale rispetto al solo fine-tuning a gradiente, o soprattutto rischio di *overfitting* alla metrica? Da decidere con A/B su hold-out e dati OOD.
- Esiste una componente dell'identità che **non** sia informazione classica — e quindi, per il teorema di no-cloning (§6.7), non copiabile ma solo teletrasportabile (distruttivamente)? Oggi nessuna evidenza; resta una questione di principio che, se vera, invaliderebbe l'approccio "copia" dei Livelli 0–2.

---

## 12. Riferimenti / letture (concetti, non link)

Aree e concetti reali su cui poggia questo documento. Da approfondire con **fonti primarie aggiornate e datate**; nessun link è inventato perché qui elenchiamo *concetti*, non URL. Le cifre biologiche citate nel documento (connettomi, risoluzioni) vanno verificate contro queste fonti e marcate con l'anno.

**Coscienza e filosofia della mente**
- Problema difficile della coscienza (Chalmers); "What is it like to be a bat?" (Nagel)
- Teoria dell'Informazione Integrata (IIT, Tononi); Global Workspace Theory (Baars, Dehaene)
- Funzionalismo / computazionalismo; argomento della stanza cinese (Searle); illusionismo (Frankish, Dennett)
- Identità personale e continuità psicologica (Parfit, *Reasons and Persons*); nave di Teseo; esperimenti mentali sul teletrasporto

**Neuroscienze e acquisizione del substrato** *(verificare le cifre con la fonte primaria e datarle)*
- Whole-Brain Emulation (roadmap e dibattito); connettomica
- Connettomi completi: *C. elegans* (302 neuroni); larva di *Drosophila*; *Drosophila* adulta — consorzio FlyWire (~140.000 neuroni, ~2023–2024); frammento di corteccia umana — progetto H01 (Google/Harvard, ~1 mm³ ≈ ~1,4 PB, ~2021)
- Neuroimaging: MRI strutturale, fMRI (segnale BOLD), DTI/dMRI e tractography
- Elettrofisiologia: EEG, MEG; interfacce cervello-macchina (BCI) e array ad alta densità (es. Neuropixels)

**Machine learning e compressione di modelli**
- Quantizzazione (post-training e quantization-aware); formati GGUF; `bitsandbytes`
- Knowledge distillation (teacher/student); pruning, low-rank, fattorizzazione
- Fine-tuning efficiente: LoRA, QLoRA; RAG (Retrieval-Augmented Generation); reti spiking (SNN) e hardware neuromorfico (Loihi, SpiNNaker, BrainScaleS)

**Psicometria e modellazione della persona**
- Big Five / OCEAN (strumenti IPIP-NEO, BFI-2); Schwartz Theory of Basic Values; Moral Foundations Theory
- Natura ricostruttiva della memoria autobiografica; (critica all') MBTI

**Dati, privacy e governance**
- Datasheets for Datasets; Model Cards
- GDPR (categorie particolari di dati, art. 9); concetto emergente di neuro-diritti
- Provenienza e watermarking dei contenuti sintetici (es. standard C2PA); *machine unlearning*

**Valutazione**
- Test di Turing e sua variante "personale"; valutazione in doppio cieco; protocolli hold-out e validazione temporale per misurare la generalizzazione

**Calcolo evolutivo (metodo, §5.6)**
- Algoritmi genetici (Holland); neuroevoluzione e NEAT/HyperNEAT (Stanley, Miikkulainen); ottimizzazione multi-obiettivo e fronte di Pareto (NSGA-II, Deb); legge di Goodhart e overfitting alla metrica

**Informazione quantistica (ramo speculativo, §6.7)**
- Teorema di no-cloning (Wootters & Zurek; Dieks, 1982); teletrasporto quantistico (Bennett et al., 1993); decoerenza nel cervello e critica alle teorie quantistiche della mente (Tegmark, 2000); Orch-OR (Penrose & Hameroff) come ipotesi minoritaria

---

## 13. Cronologia delle revisioni

Questo documento è esso stesso un artefatto governato: applica a sé la regola di versioning e metadati che impone agli altri artefatti (§4.4). Ogni modifica sostanziale va annotata qui, con data e motivazione, e tracciata in git.

| Versione | Data | Modifiche principali |
|---|---|---|
| 1.0 | 2026-06-27 | Prima versione consolidata. Rinumerazione e correzione di tutti i rimandi incrociati (etica = §10, struttura repo = §8). Nomenclatura unica dei livelli (§3, Livelli 0–4) distinta dai mondi (§6.5) e dalle sottosezioni di §4. Set chiuso di tag di maturità (§2). Soglie di §7 dichiarate provvisorie e da calibrare, riconciliate con §11. "Errore di quantizzazione" ridefinito come vettore, non scalare. Turing personale consolidato in §6.6 con limite teorico 50% vs soglia pratica 60%. IIT riformulato in modo cauto (§6.2). Onestà sulla persona singola spostata dentro §10 (§10.0). Criterio procedurale di sentienza reso azionabile (§10.3). Aggiunte: stime di costo (§5.5), policy dati↔provider e modello di base (§8.3), criteri di STOP e drift del soggetto (§7), threat model minimo (§10.6), scenario post-mortem (§10.9), policy di default sul consenso dei terzi (§10.1), questa cronologia (§13). Deduplicazione dei concetti ripetuti con rinvio alla fonte di verità. Metadati di intestazione compilati; cifre biologiche marcate come da verificare e datare. |
| 1.1 | 2026-06-27 | Aggiunte due sottosezioni senza rinumerare le esistenti (per non rompere i rimandi incrociati): **§5.6 Algoritmi genetici** — evoluzione e ricerca a livello *meta* del gemello (persona, politiche cognitive, architettura/neuroevoluzione, compromessi di quantizzazione); fitness = metriche di fedeltà §5.4; multi-obiettivo (NSGA-II) coerente col vettore di §2; limiti di costo per valutazione e rischio di Goodhart. **§6.7 Teletrasporto quantistico e no-cloning** — la fisica del "trasferimento"; il no-cloning scioglie il paradosso della doppia istanza (§6.4); controcanto di Tegmark sulla decoerenza neurale → l'informazione rilevante è classica e quindi copiabile, perciò `tron` non dipende dal quantistico; marcato `[SPECULATIVO]`. Aggiunti rimando in §6.4, voci in §11 (questioni aperte) e §12 (riferimenti). |

> **Come aggiornare:** a ogni cambiamento di direzione o milestone, incrementare la versione (semver leggero: x.y), aggiornare la data in intestazione e aggiungere una riga qui. Le modifiche alla §10 (etica) richiedono motivazione esplicita.
