import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(
    token=HF_TOKEN
)

def check_frame_with_ai(image_path):
    try:
        if not HF_TOKEN:
            return 0, ["HF_TOKEN missing. Add it in backend/.env and restart backend."]

        result = client.image_classification(
            image_path,
            model="dima806/deepfake_vs_real_image_detection"
        )

        fake_score = 0
        labels = []

        for item in result:
            label = item["label"].lower()
            confidence = float(item["score"])

            labels.append(f"{item['label']}: {round(confidence * 100, 2)}%")

            if "fake" in label or "ai" in label or "deepfake" in label:
                fake_score = max(fake_score, int(confidence * 100))

        return fake_score, labels

    except Exception as e:
        return 0, [f"AI model error: {str(e)}"]