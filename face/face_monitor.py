import os
import sys
import time
import urllib.request
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

MODEL_DIR = os.path.join(os.path.expanduser("~"), ".antidistract", "models")
PROTOTXT_PATH = os.path.join(MODEL_DIR, "deploy.prototxt")
CAFFEMODEL_PATH = os.path.join(MODEL_DIR, "res10_300x300_ssd_iter_140000.caffemodel")
LANDMARKS_PATH = os.path.join(MODEL_DIR, "shape_predictor_68_face_landmarks.dat")

PROTOTXT_URL = (
    "https://raw.githubusercontent.com/opencv/opencv/master/"
    "samples/dnn/face_detector/deploy.prototxt"
)
CAFFEMODEL_URL = (
    "https://github.com/opencv/opencv_3rdparty/raw/"
    "dnn_samples_face_detector_20170830/"
    "res10_300x300_ssd_iter_140000.caffemodel"
)
LANDMARKS_URL = (
    "https://github.com/italojs/facial-landmarks-recognition/raw/master/"
    "shape_predictor_68_face_landmarks.dat"
)

# Optional dlib import for sleep detection
try:
    import dlib
    HAS_DLIB = True
except ImportError:
    HAS_DLIB = False
    dlib = None


# ── EAR constants ─────────────────────────────────────────────

LEFT_EYE_IDXS = list(range(36, 42))
RIGHT_EYE_IDXS = list(range(42, 48))
EAR_THRESHOLD = 0.2
DEFAULT_SLEEP_THRESHOLD_S = 10


def _download_with_progress(url, path, label):
    print(f"[FaceMonitor] Mengunduh {label}...")

    last_pct = [-1]

    def _progress(count, block_size, total_size):
        if total_size > 0:
            pct = min(int(count * block_size * 100 / total_size), 100)
            if pct >= last_pct[0] + 20:
                last_pct[0] = pct
                print(f"[FaceMonitor]   {label}: {pct}%")

    try:
        urllib.request.urlretrieve(url, path, _progress)
        print(f"[FaceMonitor] {label} selesai.")
    except Exception as e:
        raise RuntimeError(f"Gagal mengunduh {label}: {e}")


def _ensure_models():
    os.makedirs(MODEL_DIR, exist_ok=True)

    # PyInstaller bundled model path
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
        for fname in ["deploy.prototxt", "res10_300x300_ssd_iter_140000.caffemodel"]:
            src = os.path.join(bundle_dir, "models", fname)
            dst = os.path.join(MODEL_DIR, fname)
            if os.path.exists(src) and not os.path.exists(dst):
                import shutil
                shutil.copy2(src, dst)

    if not os.path.exists(PROTOTXT_PATH):
        _download_with_progress(PROTOTXT_URL, PROTOTXT_PATH, "deploy.prototxt")
    if not os.path.exists(CAFFEMODEL_PATH):
        _download_with_progress(CAFFEMODEL_URL, CAFFEMODEL_PATH, "caffemodel")


def _ensure_landmarks_model():
    """Download dlib shape predictor if dlib is available."""
    if not HAS_DLIB:
        print("[FaceMonitor] dlib tidak terinstall — sleep detection dinonaktifkan.")
        return False
    if not os.path.exists(LANDMARKS_PATH):
        print("[FaceMonitor] Mengunduh shape_predictor_68_face_landmarks.dat (~100MB)...")
        try:
            _download_with_progress(LANDMARKS_URL, LANDMARKS_PATH, "shape predictor")
        except Exception as e:
            print(f"[FaceMonitor] Gagal mengunduh shape predictor: {e}")
            print("[FaceMonitor] Sleep detection dinonaktifkan.")
            return False
    return True


def _ear(landmarks: np.ndarray, eye_idxs: list) -> float:
    """Eye Aspect Ratio — low value = eyes closed."""
    pts = landmarks[eye_idxs]
    # Vertical distances
    a = np.linalg.norm(pts[1] - pts[5])
    b = np.linalg.norm(pts[2] - pts[4])
    # Horizontal distance
    c = np.linalg.norm(pts[0] - pts[3])
    if c < 1e-6:
        return 1.0
    return (a + b) / (2.0 * c)


class FaceMonitor(QThread):
    status_changed = pyqtSignal(bool, float, float)
    away_alert = pyqtSignal(float)
    face_returned = pyqtSignal()
    multi_face_detected = pyqtSignal(int)
    sleep_detected = pyqtSignal(float)    # away_seconds
    sleep_ended = pyqtSignal()

    def __init__(self, away_threshold: int = 30, sleep_threshold: int = DEFAULT_SLEEP_THRESHOLD_S, parent=None):
        super().__init__(parent)
        self.away_threshold = away_threshold
        self.sleep_threshold = sleep_threshold
        self._running = False
        self._face_time = time.time()
        self._alerted = False
        self._sleep_alerted = False
        self._eyes_closed_since: float | None = None
        self._sleep_detection_enabled = True
        self.enabled = True
        self._net = None
        self._predictor = None

    def run(self):
        self._running = True

        try:
            _ensure_models()
            self._net = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, CAFFEMODEL_PATH)
            self._net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
            self._net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        except Exception as e:
            print(f"[FaceMonitor] Gagal init detektor: {e}")
            self._running = False
            return

        # Init sleep detection
        sleep_enabled = _ensure_landmarks_model()
        if sleep_enabled:
            try:
                self._predictor = dlib.shape_predictor(LANDMARKS_PATH)
                print("[FaceMonitor] Sleep detection siap.")
            except Exception as e:
                print(f"[FaceMonitor] Gagal load shape predictor: {e}")
                sleep_enabled = False

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[FaceMonitor] Kamera tidak ditemukan.")
            self._running = False
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        cap.set(cv2.CAP_PROP_FPS, 10)

        while self._running:
            if not self.enabled:
                time.sleep(0.3)
                continue

            ret, frame = cap.read()
            if not ret:
                time.sleep(0.2)
                continue

            h, w = frame.shape[:2]

            blob = cv2.dnn.blobFromImage(
                frame, 1.0, (300, 300), [104, 117, 123],
                swapRB=False, crop=False,
            )
            self._net.setInput(blob)
            detections = self._net.forward()

            face_found = False
            confidence = 0.0
            face_count = 0
            face_box = None

            candidates = []
            best_conf = 0.0
            best_box = None
            for i in range(detections.shape[2]):
                conf = float(detections[0, 0, i, 2])
                if conf >= 0.5:
                    candidates.append(conf)
                    if conf > best_conf:
                        best_conf = conf
                        x1 = int(detections[0, 0, i, 3] * w)
                        y1 = int(detections[0, 0, i, 4] * h)
                        x2 = int(detections[0, 0, i, 5] * w)
                        y2 = int(detections[0, 0, i, 6] * h)
                        best_box = (x1, y1, x2, y2)

            if candidates:
                face_count = len(candidates)
                confidence = max(candidates)
                face_found = True
                face_box = best_box

                if face_count > 1:
                    self.multi_face_detected.emit(face_count)

            now = time.time()

            # ── Face presence tracking ──
            if face_found:
                away_sec = 0.0
                if self._alerted:
                    self._alerted = False
                    self.face_returned.emit()
                self._face_time = now
            else:
                away_sec = now - self._face_time
                if away_sec >= self.away_threshold and not self._alerted:
                    self._alerted = True
                    self.away_alert.emit(away_sec)

            # ── Sleep detection ──
            if sleep_enabled and self._sleep_detection_enabled and face_found and face_box is not None:
                x1, y1, x2, y2 = face_box
                # Expand box slightly for landmarks
                fx1 = max(0, x1)
                fy1 = max(0, y1)
                fx2 = min(w, x2)
                fy2 = min(h, y2)

                gray = cv2.cvtColor(frame[fy1:fy2, fx1:fx2], cv2.COLOR_BGR2GRAY)
                try:
                    rect = dlib.rectangle(0, 0, fx2 - fx1, fy2 - fy1)
                    shape = self._predictor(gray, rect)
                    landmarks = np.array([[p.x, p.y] for p in shape.parts()])

                    left_ear = _ear(landmarks, LEFT_EYE_IDXS)
                    right_ear = _ear(landmarks, RIGHT_EYE_IDXS)
                    avg_ear = (left_ear + right_ear) / 2.0

                    if avg_ear < EAR_THRESHOLD:
                        if self._eyes_closed_since is None:
                            self._eyes_closed_since = now
                        closed_duration = now - self._eyes_closed_since
                        if closed_duration >= self.sleep_threshold and not self._sleep_alerted:
                            self._sleep_alerted = True
                            self.sleep_detected.emit(closed_duration)
                    else:
                        if self._sleep_alerted:
                            self._sleep_alerted = False
                            self.sleep_ended.emit()
                        self._eyes_closed_since = None
                except Exception:
                    pass  # Landmark detection failed, skip frame
            elif not face_found:
                self._eyes_closed_since = None

            self.status_changed.emit(face_found, away_sec, confidence)
            time.sleep(0.3)

        cap.release()

    def stop(self):
        self._running = False
        self.wait(3000)

    def set_threshold(self, seconds: int):
        self.away_threshold = seconds
        self._face_time = time.time()
        self._alerted = False

    def set_sleep_threshold(self, seconds: int):
        self.sleep_threshold = seconds
        self._sleep_alerted = False
        self._eyes_closed_since = None

    def set_sleep_detection_enabled(self, enabled: bool):
        self._sleep_detection_enabled = enabled
        if not enabled:
            self._sleep_alerted = False
            self._eyes_closed_since = None
