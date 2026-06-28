# Changelog — VelociTAI

Tutte le modifiche rilevanti a questo progetto. Versionamento [SemVer](https://semver.org/lang/it/).

## [1.0.0] — 2026-06-28
Prima release commerciale del **software** (la piena operatività per emettere
sanzioni richiede comunque omologazione MIT, taratura e DPIA — vedi
`docs/LEGAL_COMPLIANCE.md` e `docs/SALES_READINESS.md`).

### Aggiunto
- **Pipeline di accertamento** completa Art. 142 CdS: rilevamento → tracking →
  stima velocità (regressione/line-pair) → ANPR → prova → sanzione → verbale →
  notifica. Core a sola libreria standard.
- **Resilienza & auto-riparazione** (`resilience.py`): isolamento guasti, retry,
  circuit breaker, dead-letter persistente, ledger idempotente, monitor salute,
  comando `doctor`.
- **Sicurezza by-design** (`security.py`): catena di custodia **HMAC**, audit-log
  a catena di hash, anti path-traversal, redazione PII, permessi 0600/0700,
  rate-limit e header di sicurezza sulla dashboard, limiti anti-DoS.
- **Backend di produzione** (scaffolding): YOLO, EasyOCR, OpenCV (`CV2Recorder`),
  PEC (SMTP-SSL), sorgente video; rilevatore classico `MotionDetector`.
- **Demo VIDEO reale** (`examples/video_demo.py`): rileva l'infrazione dai pixel.
- **Commerciale**: modello di prezzo (`pricing.py` + comando `quote`), listino,
  dossier di vendita, capitolato, kit go-to-market (`docs/sales/`), licenza.
- **Qualità**: 105 test automatici; fuzzing di robustezza e di sicurezza.

### Note
- Importi edittali e riferimenti normativi sono configurabili (aggiornamento
  biennale ISTAT, art. 195 CdS).
