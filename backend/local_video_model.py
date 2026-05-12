import os
from functools import lru_cache

import cv2
import numpy as np

try:
    import joblib
except ImportError:
    joblib = None


LOCAL_VIDEO_MODEL_PATH = os.getenv(
    "LOCAL_VIDEO_MODEL_PATH",
    os.path.join("models", "video_ai_detector.joblib"),
)
FEATURE_VERSION = "video_features_v1"


def _sample_frame_indexes(total_frames, max_frames):
    if total_frames <= 0:
        return []

    if max_frames <= 1:
        return [max(1, total_frames // 2)]

    start = max(1, total_frames // 20)
    end = max(start + 1, total_frames - 2)
    step = max(1, (end - start) // (max_frames - 1))
    return sorted({min(end, start + (i * step)) for i in range(max_frames)})


def _frame_features(frame):
    small = cv2.resize(frame, (160, 160), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)

    hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 6, 6], [0, 180, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()

    edges = cv2.Canny(gray, 80, 160)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    fft = np.fft.fftshift(np.fft.fft2(gray))
    magnitude = np.log(np.abs(fft) + 1)
    center = magnitude.shape[0] // 2
    low_band = magnitude[center - 12:center + 12, center - 12:center + 12].mean()
    high_band = magnitude.mean()
    frequency_ratio = high_band / (low_band + 1e-6)

    ok, encoded = cv2.imencode(".jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 70])
    if ok:
        decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        compression_error = np.abs(small.astype(np.float32) - decoded.astype(np.float32))
        compression_mean = compression_error.mean()
        compression_std = compression_error.std()
    else:
        compression_mean = 0.0
        compression_std = 0.0

    scalar_features = np.array(
        [
            gray.mean(),
            gray.std(),
            hsv[:, :, 1].mean(),
            hsv[:, :, 1].std(),
            laplacian_var,
            edges.mean() / 255,
            frequency_ratio,
            compression_mean,
            compression_std,
        ],
        dtype=np.float32,
    )

    return np.concatenate([hist.astype(np.float32), scalar_features])


def extract_video_features(path, max_frames=12):
    cap = cv2.VideoCapture(path)

    try:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        frame_indexes = _sample_frame_indexes(total_frames, max_frames)
        frame_features = []

        for frame_index in frame_indexes:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = cap.read()

            if ret:
                frame_features.append(_frame_features(frame))

        if not frame_features:
            raise ValueError("No readable frames found")

        matrix = np.vstack(frame_features)
        return np.concatenate(
            [
                matrix.mean(axis=0),
                matrix.std(axis=0),
                matrix.min(axis=0),
                matrix.max(axis=0),
            ]
        ).astype(np.float32)
    finally:
        cap.release()


@lru_cache(maxsize=1)
def _load_local_model():
    if joblib is None:
        return None

    if not os.path.exists(LOCAL_VIDEO_MODEL_PATH):
        return None

    bundle = joblib.load(LOCAL_VIDEO_MODEL_PATH)

    if bundle.get("feature_version") != FEATURE_VERSION:
        return None

    return bundle


def predict_with_local_model(path):
    bundle = _load_local_model()

    if not bundle:
        dependency_note = " Install scikit-learn/joblib and train the model." if joblib is None else ""
        return {
            "status": "unavailable",
            "labels": [f"Local trained video model not found.{dependency_note} Train it with train_video_model.py."],
        }

    try:
        features = extract_video_features(path, max_frames=bundle.get("max_frames", 12)).reshape(1, -1)
        model = bundle["model"]
        classes = list(model.classes_)

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(features)[0]
            score_by_class = dict(zip(classes, probabilities))
            fake_probability = float(score_by_class.get(1, 0))
        else:
            fake_probability = float(model.predict(features)[0] == 1)

        fake_score = int(round(fake_probability * 100))

        return {
            "status": "ok",
            "fake_score": fake_score,
            "real_score": 100 - fake_score,
            "labels": [
                f"local trained model fake: {fake_score}%",
                f"local trained model real: {100 - fake_score}%",
            ],
        }
    except Exception as exc:
        return {
            "status": "error",
            "labels": [f"Local trained video model error: {exc}"],
        }
