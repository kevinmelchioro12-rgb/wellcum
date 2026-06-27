# Sicurezza

VelociTAI tratta **prove a valenza legale** e **dati personali** (targhe,
intestatari, codici fiscali, PEC). La sicurezza è quindi un requisito, non un
optional. Questo documento descrive il modello di minaccia e i controlli
implementati. Il modulo di riferimento è
[`velocitai/security.py`](../velocitai/security.py).

## Modello di minaccia (STRIDE sintetico)

| Minaccia | Esempio | Controllo |
|---|---|---|
| **Spoofing / accesso non autorizzato** | accesso alla console con PII | token bearer su dashboard + restrizione localhost; confronto a tempo costante |
| **Tampering della prova** | un insider altera la clip/manifest dopo l'accertamento | catena di custodia **HMAC-SHA256** (non falsificabile senza chiave) + scritture atomiche |
| **Tampering del registro** | cancellazione/modifica di voci d'audit | **audit-log a catena di hash** (HMAC), tamper-evident |
| **Repudiation** | "non ho emesso io quel verbale" | audit-log firmato con `violation_issued` per ogni atto |
| **Information disclosure (GDPR)** | PII nei log o file leggibili da tutti | redazione PII nei log + permessi `0600/0700` su prove e verbali |
| **Denial of Service** | input gigante / YAML annidato / flood HTTP | limiti su frame/veicoli/tracce, limite di profondità config, rate-limiter, cap dimensione richiesta |
| **Elevation / injection** | path traversal via `violation_id`/protocollo, XSS in dashboard | sanitizzazione dei componenti di path + `secure_join`; escaping HTML + CSP |

## Controlli implementati

### 1. Input non fidato → filesystem
- `safe_path_component()` consente solo `[A-Za-z0-9._-]`, rifiuta `..`, path
  assoluti, null-byte; `secure_join()` verifica con `realpath` di restare dentro
  la radice. Applicati a `violation_id` (recorder) e `protocol_number` (notifier).
- Deserializzazione: **solo `yaml.safe_load`** e `json` (nessun `pickle`, `eval`,
  `exec`, né `yaml.load` non sicuro).

### 2. Catena di custodia (integrità + non-ripudio)
- `keyed_digest_of_files()`: con chiave segreta usa **HMAC-SHA256**, altrimenti
  SHA-256. Il digest lega il *basename* + contenuto (verifica indipendente dalla
  posizione su disco). `verify_evidence()` confronta a tempo costante e fallisce
  in sicurezza se manca la chiave per una prova HMAC.
- La chiave proviene da `VELOCITAI_EVIDENCE_KEY` (mai hardcoded).

### 3. Audit-log tamper-evident
- `AuditLog`: JSONL append-only; ogni voce incatena l'hash della precedente.
  Modificare/rimuovere una riga rompe la catena (`verify()` lo rileva).
  Opzionale HMAC con `VELOCITAI_AUDIT_KEY`. La PII è redatta prima della scrittura.
- `velocitai doctor` verifica config, integrità prove **e** catena d'audit.

### 4. Protezione PII (GDPR)
- `PIIRedactingFilter` redige targhe (`AB***CD`), codici fiscali ed email da
  **tutti** i log. Applicato centralmente in `get_logger`.
- `set_secure_permissions()` impone `0600` (file) / `0700` (dir) su prove e
  verbali.

### 5. Dashboard web blindata
- **Header**: `Content-Security-Policy` (default-src 'none', niente script),
  `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: no-referrer`, `Cache-Control: no-store`, `Permissions-Policy`.
- **Auth**: token bearer (`VELOCITAI_DASHBOARD_TOKEN`); in sua assenza l'accesso
  è ristretto a localhost.
- **DoS**: rate-limiter token-bucket per IP, limite lunghezza URI, **solo `GET`**
  (ogni altro metodo → `405`).
- **XSS**: ogni valore dinamico è `html.escape`-ato; l'API è JSON con `nosniff`.

### 6. Resilienza a DoS / esaurimento risorse
- Limiti configurabili: `max_frames`, `max_vehicles_per_frame`, `max_tracks`
  (`SecurityConfig`); profondità massima del merge di configurazione.
- Coda dead-letter e ledger durabili con potatura (`doctor --prune-ledger-days`).

## Gestione dei segreti

I segreti **non sono mai** nel codice o nella config: si indicano i **nomi**
delle variabili d'ambiente in `SecurityConfig`.

| Variabile | Scopo |
|---|---|
| `VELOCITAI_EVIDENCE_KEY` | chiave HMAC catena di custodia |
| `VELOCITAI_AUDIT_KEY` | chiave HMAC audit-log |
| `VELOCITAI_DASHBOARD_TOKEN` | token bearer console operatore |

Esempio:

```bash
export VELOCITAI_EVIDENCE_KEY="$(openssl rand -hex 32)"
export VELOCITAI_AUDIT_KEY="$(openssl rand -hex 32)"
export VELOCITAI_DASHBOARD_TOKEN="$(openssl rand -hex 24)"
```

## Checklist di hardening per la messa in esercizio

- [ ] Chiavi `EVIDENCE`/`AUDIT` generate (32+ byte) e custodite in un secret store.
- [ ] Token dashboard impostato; console dietro TLS/reverse-proxy autenticato.
- [ ] Permessi del filesystem verificati (`doctor`), backup cifrato delle prove.
- [ ] `last_calibration_date`/`homologation_number` reali (vedi LEGAL_COMPLIANCE).
- [ ] DPIA/GDPR completata; retention e potatura del ledger configurate.
- [ ] Aggiornamenti di sicurezza delle dipendenze di produzione monitorati.

## Superficie d'attacco minima

Il **core gira in sola libreria standard**: nessuna dipendenza di terze parti
nel percorso critico (parsing, sanzioni, prova, verbale), quindi nessun rischio
supply-chain sul nucleo. Le dipendenze ML/PEC sono confinate ai backend di
produzione, opzionali e isolati dietro interfacce.

## Segnalazione vulnerabilità

Per una divulgazione responsabile contattare il responsabile sicurezza del
fornitore (canale da definire in fase contrattuale).
