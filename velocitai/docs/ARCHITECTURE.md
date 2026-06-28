# Architettura

## Principio guida
Il **core** dipende solo dalla libreria standard di Python: l'intera logica di
dominio (tracking, geometria, velocità, ANPR, sanzioni, verbale) è eseguibile e
testabile senza GPU, OpenCV o modelli ML. I componenti che richiedono visione
artificiale sono **backend intercambiabili** dietro interfacce minime.

## Flusso dati

```
FrameSource ─▶ Detector ─▶ Tracker ─▶ SpeedEstimator ─┐
 (scenario/video)  │           │            │          │
                   ▼           ▼            ▼          ▼
              Detection     Track    SpeedMeasurement  │
                                                       │ apply_tolerance()
                                                       ▼
                                            contested > limit ?
                                                       │ sì
                          ┌────────────────────────────┼───────────────┐
                          ▼                             ▼               ▼
                       ANPR.read              Recorder.record   SanctionCalculator
                          │                          │                 │
                          ▼                          ▼                 ▼
                    PlateReading             EvidencePackage        Sanction
                          │                          │                 │
                          └──────────────┬───────────┴────────┬────────┘
                                         ▼                    ▼
                                  OwnerRegistry         build_verbale()
                                         │                    │
                                         └─────────┬──────────┘
                                                   ▼
                                              Notifier.notify ─▶ PEC/file
```

## Moduli e responsabilità

| Modulo | Responsabilità | Interfaccia chiave |
|---|---|---|
| `models.py` | dataclass del dominio | `Detection, Track, Violation, Verbale` |
| `geometry.py` | calibrazione immagine→mondo | `Homography.project`, `Calibration` |
| `detection.py` | rilevamento veicoli | `Detector.detect(frame) -> [Detection]` |
| `tracking.py` | identità tra fotogrammi | `IoUTracker.update / finalize` |
| `speed.py` | stima velocità | `*.estimate(track) -> SpeedMeasurement` |
| `anpr.py` | targa: lettura/validazione | `ANPRBackend.read(track, frames)` |
| `recorder.py` | prova + custodia | `*.record(...) -> EvidencePackage` |
| `registry.py` | visura intestatario | `OwnerRegistry.lookup(plate)` |
| `fines.py` | sanzione art.142/202 | `SanctionCalculator`, `build_verbale` |
| `notifier.py` | verbale + notifica | `Notifier.notify(verbale)` |
| `pipeline.py` | orchestrazione | `EnforcementPipeline.process_frames` |

Tutti i backend (`Detector`, `ANPRBackend`, recorder) sono **Protocol**: esiste
una coppia *simulato/produzione* (`SimulatedDetector`/`YOLODetector`,
`SimulatedANPR`/`EasyOCRANPR`, `SimulatedRecorder`/`CV2Recorder`).

## Modalità di stima velocità

- **`world_regression`**: regressione lineare ai minimi quadrati delle posizioni
  mondo `(t, x)` e `(t, y)`; il modulo del vettore pendenza è la velocità.
  Robusto al rumore per-fotogramma; confidenza = R² dell'asse dominante.
- **`line_pair`**: tempo di attraversamento tra due linee a distanza nota (come
  autovelox a doppia spira / tutor). Confidenza = densità dei campioni tra i gate.

## Elaborazione: per-clip vs streaming

Il prototipo elabora **per-clip** (off-line): accumula i fotogrammi, costruisce le
tracce, poi stima/valuta. È deterministico e ideale per demo e collaudo.

In **produzione streaming** la stessa logica gira a finestra mobile:
1. buffer circolare degli ultimi *N* fotogrammi (pre-evento);
2. tracker aggiornato in tempo reale;
3. quando una traccia attraversa il secondo gate, si chiude la misura;
4. se supera il limite (post-tolleranza) si congelano i fotogrammi pre/post e si
   avvia ANPR + registrazione + verbale in modo asincrono.

L'orchestratore è già strutturato per questa evoluzione (la stima è isolata in
`SpeedEstimator`, la finestra-prova in `_clip_for_track`).

## Determinismo e test
La simulazione usa PRNG deterministici (xorshift/LCG) e timestamp fissi: i 34
test ricostruiscono il ground-truth con accuratezza esatta, così le regressioni
sono individuabili immediatamente.
