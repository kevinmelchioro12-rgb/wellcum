# Affidabilità e auto-riparazione

Un sistema che emette atti amministrativi non può fermarsi al primo imprevisto né
produrre un verbale su un dato corrotto. VelociTAI tratta i guasti come eventi
**attesi** e li gestisce in modo che:

1. nessun singolo errore interrompa l'accertamento dell'intera clip;
2. nessun dato non valido (NaN/inf, prova mancante) finisca in un verbale;
3. ciò che non si può completare subito venga **conservato e ripreso**;
4. lo stato di salute sia sempre ispezionabile e riparabile (`velocitai doctor`).

Il modulo di riferimento è [`velocitai/resilience.py`](../velocitai/resilience.py).

## Scenari di errore gestiti

| Scenario | Dove | Comportamento |
|---|---|---|
| Fotogramma corrotto / detector in errore | `pipeline.process_frames` | il frame è isolato e saltato (`guard`), l'accertamento prosegue |
| Coordinate mondo NaN/inf | `speed._finite_world_points` | i campioni non finiti sono scartati; se restano troppo pochi, nessuna misura |
| Velocità implausibile (dt≈0) | `speed` (cap `max_speed_kmh`) | misura scartata, nessuna contestazione assurda |
| `overspeed` NaN/inf | `fines.classify` | ritorna `None`: **mai** una sanzione su dato corrotto |
| Backend ANPR in crash | `pipeline._process_track` | degradazione controllata: targa `ILLEGGIBILE` + stato `DA_VERIFICARE` |
| Registrazione prova fallita (disco pieno) | isolamento per-traccia | la violazione va in **dead-letter**; gli altri verbali sono comunque emessi |
| Notifica PEC irraggiungibile | `notifier.notify` | retry con backoff → dead-letter; il verbale resta scritto su disco |
| Visura intestatario fallita | `pipeline._process_track` | `owner = None` → verbale "intestatario NON DISPONIBILE" |
| Config incoerente | `config.validate_config` | `ConfigError` all'avvio, **prima** di emettere atti |
| Chiave YAML errata (refuso) | `config._known` | chiave ignota scartata e segnalata, il resto applicato |
| Registro intestatari malformato | `registry.from_json` | i record non validi sono saltati, gli altri restano usabili |
| Rielaborazione della stessa clip | `IssuedLedger` | **idempotenza**: nessuna doppia sanzione |
| Crash a metà scrittura | `utils.atomic_write_text` | scrittura atomica: file o vecchio (intatto) o nuovo (completo) |
| Prova alterata/corrotta | `recorder.verify_evidence` | rilevata dal confronto dell'hash (`doctor`) |

## Primitivi

- **`retry(fn, attempts, base_delay, …)`** — ritentativi con backoff esponenziale
  per guasti transitori.
- **`CircuitBreaker`** — `closed → open → half_open`; isola un backend che continua
  a fallire ed evita di martellarlo, abilitando la degradazione controllata.
- **`guard(fn, component, monitor)`** — esegue una funzione isolando qualunque
  eccezione e aggiornando il monitor di salute.
- **`HealthMonitor`** — successi/fallimenti per componente, raffiche consecutive,
  report aggregato (mostrato anche a fine `demo`).
- **`DeadLetterQueue`** — coda **persistente** (un file JSON per elemento, durabile
  a un riavvio) con `retry_pending(handler)` per la ripresa automatica.
- **`IssuedLedger`** — registro idempotente; la chiave è
  `dispositivo | targa | finestra-temporale | velocità`, robusta anche con targhe
  illeggibili (veicoli distinti non collidono).

## Auto-diagnosi operativa

```bash
# Verifica config, integrità di tutte le prove, stato della coda dead-letter
python3 -m velocitai doctor --config config/default.yaml

# Come sopra + ripresa automatica degli elementi in coda
python3 -m velocitai doctor --repair

# Manutenzione: pota dal ledger idempotente le chiavi oltre N giorni
python3 -m velocitai doctor --prune-ledger-days 120
```

`doctor` ritorna codice 0 se tutto è in salute, ≠0 se trova problemi (config non
valida, prova manomessa, elementi non ripristinabili) — adatto a un health-check
in cron o in un orchestratore.

## Garanzie sulle scritture

Tutti gli atti (verbali `.txt`/`.json`, manifest-prova, file hash, ledger,
dead-letter) usano `atomic_write_text` (scrittura su file temporaneo + `os.replace`
+ `fsync`). Una caduta di corrente o un kill del processo non possono lasciare un
atto legale troncato.

## Copertura di test

Gli scenari sopra sono verificati da
[`tests/test_resilience.py`](../tests/test_resilience.py) (primitivi) e
[`tests/test_robustness.py`](../tests/test_robustness.py) (end-to-end:
NaN, guasto backend isolato, degradazione ANPR, idempotenza, config invalida,
registro malformato, manomissione prove).
