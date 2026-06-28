# Innesto dei backend di produzione

Il core resta invariato: si sostituiscono i backend *simulati* con quelli reali,
che rispettano le stesse interfacce. Installazione:

```bash
pip install -r requirements-prod.txt
```

## 1. Rilevamento veicoli — YOLOv8 (`detection.YOLODetector`)

```python
from ultralytics import YOLO
from velocitai.models import Detection, BBox

class YOLODetector:
    def detect(self, frame):           # frame: ndarray BGR (OpenCV)
        res = self.model.predict(frame, conf=self.conf, verbose=False)[0]
        dets = []
        for b in res.boxes:
            cls = int(b.cls)
            if cls not in self.VEHICLE_CLASSES:
                continue
            x1, y1, x2, y2 = map(float, b.xyxy[0])
            bbox = BBox(x1, y1, x2, y2)
            # punto di contatto al suolo = centro base bbox, proiettato nel piano
            ground = Point((x1 + x2) / 2, y2)
            world = self.calibration.image_to_world(ground)
            dets.append(Detection(frame_index, timestamp, bbox,
                                  self.VEHICLE_CLASSES[cls], float(b.conf), world))
        return dets
```

Tracker consigliato in produzione: **ByteTrack** (Ultralytics lo integra) al
posto di `IoUTracker`, mantenendo `update(detections) -> [Track]`.

## 2. ANPR — EasyOCR (`anpr.EasyOCRANPR`)

```python
def read(self, track, frames):
    frame, bbox = pick_best_frame(track, frames)     # bbox più grande = targa leggibile
    roi = crop_plate_region(frame, bbox)             # rilevatore targa o ritaglio inferiore
    results = self._reader.readtext(roi)
    raw, conf = best_text(results)
    return self.validator.validate(raw, conf, bbox)  # normalizza+corregge+valida
```

`PlateValidator` (già pronto) applica normalizzazione, correzione posizionale
degli errori OCR e validazione del formato italiano.

## 3. Registrazione prova — OpenCV (`recorder.CV2Recorder`)

```python
import cv2
def record(self, violation_id, frames, track, plate):
    path = f"{self.output_dir}/{violation_id}/clip.mp4"
    h, w = frames[0].shape[:2]
    vw = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), self.fps, (w, h))
    for f in frames: vw.write(f)
    vw.release()
    crop_path = save_plate_crop(frames, track, plate)
    # catena di custodia HMAC (chiave da VELOCITAI_EVIDENCE_KEY) - non falsificabile
    digest = keyed_digest_of_files([path, crop_path, manifest], self.signing_key)
    return EvidencePackage(path, [], crop_path, digest, len(frames), digest_algo(...))
```

`CV2Recorder` (implementato) riusa `keyed_digest_of_files`, `secure_join` e i
permessi `0600/0700`. In esercizio aggiungere anche **marca temporale** qualificata.

## 4. Notifica — PEC (`notifier.Notifier._send_pec`, implementato)

Invio via **SMTP over SSL** verso il gestore PEC; credenziali SOLO da ambiente
(`VELOCITAI_PEC_USER`/`VELOCITAI_PEC_PASSWORD`), endpoint da
`notifier.pec_endpoint`. Il testo del verbale è il corpo, con allegato JSON.
Gli errori transitori sono ritentati e, se persistono, finiscono in dead-letter
(`doctor --repair`). In esercizio aggiungere il verbale **PDF** (reportlab) e la
registrazione delle **ricevute** di accettazione/consegna come prova di notifica.

## 5. Visura intestatario — ANV/PRA-ACI (`registry.OwnerRegistry`)

Sostituire il registro JSON con un client verso l'**Archivio Nazionale Veicoli**
(Motorizzazione) o **PRA-ACI**, previa convenzione. Mantenere la firma
`lookup(plate) -> OwnerRecord | None`.

## 6. API di servizio — FastAPI (opzionale)

La dashboard stdlib è sufficiente per la demo. Per l'integrazione di sistema si
può esporre una API FastAPI (`/violations`, `/verbali/{id}`, webhook di stato),
riusando `EnforcementPipeline` come servizio.

## 7. Sorgente video di produzione (`sources.VideoFrameSource`)

In esercizio i fotogrammi provengono da file o stream RTSP via OpenCV:

```python
from velocitai.sources import VideoFrameSource
src = VideoFrameSource("rtsp://camera/stream", start_epoch=acquisizione_ntp)
result = pipeline.process_frames(src.frames())   # VideoFrame: image BGR + ts
```

Il `start_epoch` deve essere l'istante reale (NTP/metadati telecamera) del primo
fotogramma: i tempi entrano nel calcolo della velocità e nel verbale.

## 8. Sicurezza in produzione (segreti via ambiente)

I backend reali riusano gli stessi controlli di sicurezza del core
(vedi [`SECURITY.md`](SECURITY.md)). I segreti si impostano via ambiente:

```bash
export VELOCITAI_EVIDENCE_KEY="$(openssl rand -hex 32)"   # firma HMAC prova
export VELOCITAI_AUDIT_KEY="$(openssl rand -hex 32)"      # firma audit-log
export VELOCITAI_DASHBOARD_TOKEN="$(openssl rand -hex 24)" # token console
export VELOCITAI_PEC_USER="postazione@pec.comune.it"      # credenziali PEC
export VELOCITAI_PEC_PASSWORD="..."
```

`CV2Recorder` e `SimulatedRecorder` accettano `signing_key` e producono la stessa
catena di custodia HMAC; `EasyOCRANPR`/`YOLODetector` non toccano il filesystem.

---

**Stato**: i backend di produzione (sezioni 1–4, 7) sono implementati come
**scaffolding funzionale** ma **non collaudato in questo ambiente** (richiede
GPU/OpenCV/telecamere). Vanno validati con hardware e video reali prima della
messa in esercizio. La modalità simulata resta il riferimento testato (95 test).
