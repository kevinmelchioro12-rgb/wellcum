"""Demo VIDEO end-to-end (pixel reali, senza ML pesante).

Genera un breve video sintetico di una strada con un veicolo che supera il
limite, poi lo elabora con la pipeline VelociTAI usando un rilevatore CLASSICO
OpenCV (sottrazione di sfondo MOG2 — niente YOLO/torch) e una lettura targa per
template-matching. Output: infrazione rilevata + sanzione (verbale).

    pip install opencv-python-headless numpy
    python3 examples/video_demo.py

NB: il video e la lettura sono REALI (pixel), non ground-truth: la velocita' e'
misurata dal movimento osservato e la targa e' letta dall'immagine.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np

from velocitai.config import Config
from velocitai.geometry import Calibration
from velocitai.detection import MotionDetector
from velocitai.tracking import IoUTracker
from velocitai.speed import WorldRegressionEstimator
from velocitai.anpr import PlateValidator, ALLOWED_LETTERS
from velocitai.recorder import CV2Recorder
from velocitai.fines import SanctionCalculator
from velocitai.notifier import Notifier, render_verbale_text
from velocitai.pipeline import EnforcementPipeline
from velocitai.sources import VideoFrameSource
from velocitai.models import PlateReading

# --- parametri scena ---------------------------------------------------------
W, H, FPS = 640, 760, 30
MPP = 0.08                      # metri per pixel (H = 60.8 m)
PLATE = "FH983KL"
SPEED_PX_PER_FRAME = 12.5       # -> 12.5*30*0.08 = 30 m/s = 108 km/h
FONT = cv2.FONT_HERSHEY_SIMPLEX
PLATE_SCALE, PLATE_TH = 0.95, 2
START_TS = 1782304200.0
# targa grande e leggibile -> dimensione auto derivata dalla targa
(_TW, _TH), _ = cv2.getTextSize(PLATE, FONT, PLATE_SCALE, PLATE_TH)
PLATE_PAD = 12
PLATE_W, PLATE_H = _TW + 2 * PLATE_PAD, _TH + 2 * PLATE_PAD
CAR_W, CAR_H = PLATE_W + 70, 300


def _draw_road(img):
    img[:] = (95, 95, 95)
    cv2.rectangle(img, (78, 0), (82, H), (235, 235, 235), -1)         # bordo sx
    cv2.rectangle(img, (W - 82, 0), (W - 78, H), (235, 235, 235), -1)  # bordo dx
    for y in range(0, H, 70):                                          # tratteggio
        cv2.rectangle(img, (W // 2 - 3, y), (W // 2 + 3, y + 38), (220, 220, 220), -1)


def _build_car_sprite():
    """Sprite del veicolo CON TEXTURE: un'auto a tinta unita avrebbe l'interno
    uniforme e la sottrazione di sfondo ne rileverebbe solo i bordi (due blob).
    Con texture e dettagli, traslando, ogni pixel interno cambia -> un solo blob."""
    rng = np.random.default_rng(3)
    s = np.full((CAR_H, CAR_W, 3), (40, 40, 180), np.uint8)
    s = (s.astype(np.int16) + rng.integers(-22, 22, (CAR_H, CAR_W, 1))).clip(0, 255).astype(np.uint8)
    cv2.rectangle(s, (18, 24), (CAR_W - 18, 72), (120, 90, 60), -1)       # parabrezza
    for yy in (90, 150, 210):                                            # linee carrozzeria
        cv2.line(s, (8, yy), (CAR_W - 8, yy), (25, 25, 110), 2)
    cv2.rectangle(s, (0, 60), (12, 150), (20, 20, 20), -1)               # ruota sx
    cv2.rectangle(s, (CAR_W - 12, 60), (CAR_W, 150), (20, 20, 20), -1)   # ruota dx
    cv2.rectangle(s, (12, CAR_H - 26), (46, CAR_H - 8), (170, 220, 245), -1)        # fari
    cv2.rectangle(s, (CAR_W - 46, CAR_H - 26), (CAR_W - 12, CAR_H - 8), (170, 220, 245), -1)
    px, py = (CAR_W - PLATE_W) // 2, int(CAR_H * 0.60)                   # targa
    cv2.rectangle(s, (px, py), (px + PLATE_W, py + PLATE_H), (245, 245, 245), -1)
    cv2.rectangle(s, (px, py), (px + PLATE_W, py + PLATE_H), (20, 20, 20), 1)
    cv2.putText(s, PLATE, (px + PLATE_PAD, py + PLATE_PAD + _TH), FONT,
                PLATE_SCALE, (15, 15, 15), PLATE_TH, cv2.LINE_AA)
    return s


_CAR_SPRITE = _build_car_sprite()


def _paste(img, sprite, x, y):
    h_, w_ = img.shape[:2]
    sh, sw = sprite.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(w_, x + sw), min(h_, y + sh)
    if x1 <= x0 or y1 <= y0:
        return
    img[y0:y1, x0:x1] = sprite[y0 - y:y1 - y, x0 - x:x1 - x]


def generate_video(path):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(path, fourcc, FPS, (W, H))
    rng = np.random.default_rng(7)
    n_frames = 80
    car_x = W // 2 - CAR_W // 2
    for i in range(n_frames):
        img = np.zeros((H, W, 3), np.uint8)
        _draw_road(img)
        img = (img.astype(np.int16) + rng.normal(0, 3, img.shape)).clip(0, 255).astype(np.uint8)
        if i >= 12:                                   # 12 frame di warmup (solo strada)
            top = -CAR_H + int((i - 12) * SPEED_PX_PER_FRAME)
            _paste(img, _CAR_SPRITE, car_x, top)
        vw.write(img)
    vw.release()
    return n_frames


# --- ANPR per template-matching (lettura REALE dei pixel della targa) --------
class TemplateANPR:
    def __init__(self, validator, size=(28, 18)):
        self.validator = validator
        self.size = size
        self._tpl = self._build_templates()

    def _render_glyph(self, ch):
        (tw, th), _ = cv2.getTextSize(ch, FONT, PLATE_SCALE, PLATE_TH)
        canvas = np.full((th + 8, tw + 8), 255, np.uint8)
        cv2.putText(canvas, ch, (4, th + 4), FONT, PLATE_SCALE, 0, PLATE_TH, cv2.LINE_AA)
        return self._norm(canvas)

    def _norm(self, glyph_gray):
        _, b = cv2.threshold(glyph_gray, 128, 255, cv2.THRESH_BINARY_INV)
        ys, xs = np.where(b > 0)
        if len(xs) == 0:
            return np.zeros(self.size, np.float32)
        b = b[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        return cv2.resize(b, (self.size[1], self.size[0])).astype(np.float32) / 255.0

    def _build_templates(self):
        chars = sorted(ALLOWED_LETTERS) + [str(d) for d in range(10)]
        return {c: self._render_glyph(c) for c in chars}

    def _match(self, glyph, candidates):
        g = self._norm(glyph)
        best, best_score = "?", -1.0
        for c in candidates:
            t = self._tpl[c]
            score = 1.0 - np.abs(g - t).mean()          # similarita' [0,1]
            if score > best_score:
                best_score, best = score, c
        return best, best_score

    def read(self, track, frames):
        if not track.points:
            return None
        best = max(track.points, key=lambda p: p.bbox.area)
        frame = next((f for f in frames if f.frame_index == best.frame_index), None)
        if frame is None:
            return None
        x1, y1 = max(0, int(best.bbox.x1)), max(0, int(best.bbox.y1))
        x2, y2 = min(W, int(best.bbox.x2)), min(H, int(best.bbox.y2))
        roi = frame.image[y1:y2, x1:x2]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # localizza la targa: regione chiara con aspetto ~3:1
        _, bright = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        cnts, _ = cv2.findContours(bright, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        plate_box = None
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if w > 40 and h > 10 and 1.8 < w / h < 6.0:
                if plate_box is None or w * h > plate_box[2] * plate_box[3]:
                    plate_box = (x, y, w, h)
        if plate_box is None:
            return PlateReading(text="ILLEGGIBILE", confidence=0.0, valid_format=False)
        x, y, w, h = plate_box
        plate = gray[y:y + h, x:x + w]
        # segmenta i caratteri (testo scuro su sfondo chiaro)
        _, chars_bin = cv2.threshold(plate, 110, 255, cv2.THRESH_BINARY_INV)
        ccnts, _ = cv2.findContours(chars_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for c in ccnts:
            cx, cy, cw, ch = cv2.boundingRect(c)
            if ch > 0.45 * h and cw > 2:
                boxes.append((cx, cy, cw, ch))
        boxes.sort(key=lambda b: b[0])
        letters_slots = {0, 1, 5, 6}
        text, scores = [], []
        for idx, (cx, cy, cw, ch) in enumerate(boxes[:7]):
            glyph = plate[cy:cy + ch, cx:cx + cw]
            if 0 <= idx < 7 and idx in letters_slots:
                cand = sorted(ALLOWED_LETTERS)
            elif idx < 7:
                cand = [str(d) for d in range(10)]
            else:
                cand = sorted(ALLOWED_LETTERS) + [str(d) for d in range(10)]
            ch_pred, sc = self._match(glyph, cand)
            text.append(ch_pred)
            scores.append(sc)
        raw = "".join(text)
        conf = float(np.mean(scores)) if scores else 0.0
        return self.validator.validate(raw, confidence=conf, bbox=best.bbox)


def build_pipeline(cfg):
    calib = Calibration(meters_per_pixel=MPP)
    return EnforcementPipeline(
        cfg,
        detector=MotionDetector(calib, min_area=12000),
        tracker=IoUTracker(iou_threshold=0.15, max_misses=20, min_hits=6),
        estimator=WorldRegressionEstimator(min_points=6, min_duration_s=0.2),
        anpr=TemplateANPR(PlateValidator(country="IT", autocorrect=True)),
        recorder=CV2Recorder(cfg.recorder.output_dir, fps=FPS),
        registry=None,
        calculator=SanctionCalculator(cfg.sanction, cfg.tz_offset_hours),
        notifier=Notifier(cfg),
    )


def _demo_config(out):
    cfg = Config()
    cfg.location.speed_limit_kmh = 50.0
    cfg.location.road_name = "Via Demo Video km 1+000"
    cfg.speed.method = "world_regression"
    cfg.speed.min_track_points = 6
    cfg.speed.min_duration_s = 0.2
    cfg.speed.min_confidence = 0.5
    cfg.recorder.output_dir = os.path.join(out, "evidence")
    cfg.notifier.output_dir = os.path.join(out, "verbali")
    cfg.registry_path = os.path.join(out, "none.json")
    return cfg


def run(out):
    """Genera il video, lo elabora e ritorna (result, cfg). Riusabile dai test."""
    os.makedirs(out, exist_ok=True)
    video_path = os.path.join(out, "strada.mp4")
    generate_video(video_path)
    cfg = _demo_config(out)
    pipeline = build_pipeline(cfg)
    result = pipeline.process_frames(VideoFrameSource(video_path, start_epoch=START_TS).frames())
    return result, cfg


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_video_demo")
    print("1) Genero il video sintetico della strada...")
    print("2) Elaboro il VIDEO (rilevamento MOG2 + tracking + velocita' + ANPR)...")
    result, cfg = run(out)
    print(f"   video: {os.path.join(out, 'strada.mp4')}  ({W}x{H} @ {FPS}fps)")

    print("\n3) ESITO ACCERTAMENTO")
    print(f"   Fotogrammi: {result.stats['frames']}  veicoli: {result.stats['tracks']}  "
          f"violazioni: {result.stats['violations']}")
    for o in result.outcomes:
        esito = "VIOLAZIONE" if o.is_violation else "conforme"
        print(f"   - track {o.track_id}: targa {o.plate or '-'}  "
              f"misurata {o.measured_kmh:.1f} km/h  contestata {o.contested_kmh:.1f} km/h  -> {esito}")

    if result.verbali:
        print("\n4) SANZIONE\n")
        print(render_verbale_text(result.verbali[0], cfg))
    else:
        print("\n[!] Nessuna violazione rilevata dal video.")
    return 0 if result.verbali else 1


if __name__ == "__main__":
    raise SystemExit(main())
