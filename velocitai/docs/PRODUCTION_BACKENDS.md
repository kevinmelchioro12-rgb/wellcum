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
    digest = sha256_of_files([path, crop_path])      # catena di custodia
    return EvidencePackage(path, [], crop_path, digest, len(frames))
```

In esercizio aggiungere **firma digitale** e **marca temporale** del pacchetto.

## 4. Notifica — PEC (`notifier.Notifier._send_pec`)

Integrazione con gestore PEC accreditato (es. via SMTP/PEC o API del provider):
- generare il verbale in **PDF** (reportlab) oltre al testo;
- inviare la **notificazione** entro 90 gg all'indirizzo PEC dell'intestatario o
  tramite il canale di notifica previsto;
- registrare ricevuta di accettazione/consegna come prova della notifica.

## 5. Visura intestatario — ANV/PRA-ACI (`registry.OwnerRegistry`)

Sostituire il registro JSON con un client verso l'**Archivio Nazionale Veicoli**
(Motorizzazione) o **PRA-ACI**, previa convenzione. Mantenere la firma
`lookup(plate) -> OwnerRecord | None`.

## 6. API di servizio — FastAPI (opzionale)

La dashboard stdlib è sufficiente per la demo. Per l'integrazione di sistema si
può esporre una API FastAPI (`/violations`, `/verbali/{id}`, webhook di stato),
riusando `EnforcementPipeline` come servizio.

---

**Nota**: i metodi di produzione sono presenti come stub che sollevano
`NotImplementedError` con il riferimento a questa guida, così l'integrazione è
guidata e non altera il comportamento della modalità simulata.
