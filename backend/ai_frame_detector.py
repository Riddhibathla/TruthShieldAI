import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
AI_MODEL_TIMEOUT_SECONDS = os.getenv("AI_MODEL_TIMEOUT_SECONDS")
AI_VIDEO_FRAME_MODEL = os.getenv(
    "AI_VIDEO_FRAME_MODEL",
    "dima806/deepfake_vs_real_image_detection",
)

client_timeout = float(AI_MODEL_TIMEOUT_SECONDS) if AI_MODEL_TIMEOUT_SECONDS else None
client = InferenceClient(token=HF_TOKEN, timeout=client_timeout) if HF_TOKEN else None

FAKE_LABELS = ("fake", "deepfake", "ai", "synthetic", "generated", "artificial")
REAL_LABELS = ("real", "genuine", "authentic", "natural", "human")
MODEL_LABEL_MAP = {
    "label_0": "real",
    "label_1": "fake",
    "0": "real",
    "1": "fake",
}


def _read_item(item):
    if isinstance(item, dict):
        label = str(item.get("label", "")).lower()
        confidence = float(item.get("score", 0))
        return MODEL_LABEL_MAP.get(label, label), confidence

    label = str(getattr(item, "label", "")).lower()
    confidence = float(getattr(item, "score", 0))
    return MODEL_LABEL_MAP.get(label, label), confidence


def check_frame_with_ai(image_path):
    if not client:
        return {
            "fake_score": 0,
            "real_score": 0,
            "status": "unavailable",
            "labels": ["HF_TOKEN missing. Add it in backend/.env or deployment variables."],
        }

    try:
        result = client.image_classification(
            image_path,
            model=AI_VIDEO_FRAME_MODEL,
        )

        fake_score = 0
        real_score = 0
        top_label = ""
        top_score = 0
        labels = []

        for item in result:
            label, confidence = _read_item(item)
            percent = int(round(confidence * 100))
            labels.append(f"{label or 'unknown'}: {percent}%")

            if percent > top_score:
                top_label = label
                top_score = percent

            if any(term in label for term in FAKE_LABELS):
                fake_score = max(fake_score, percent)

            if any(term in label for term in REAL_LABELS):
                real_score = max(real_score, percent)

        if fake_score == 0 and real_score == 0 and labels:
            fake_score = top_score if top_label != "real" else 0
            real_score = top_score if top_label == "real" else 0

        if not labels:
            return {
                "fake_score": 0,
                "real_score": 0,
                "status": "error",
                "labels": ["AI model returned no labels"],
            }

        return {
            "fake_score": fake_score,
            "real_score": real_score,
            "top_label": top_label,
            "top_score": top_score,
            "status": "ok",
            "labels": labels,
        }

    except Exception as exc:
        return {
            "fake_score": 0,
            "real_score": 0,
            "status": "error",
            "labels": [f"AI model error: {exc}"],
        }
