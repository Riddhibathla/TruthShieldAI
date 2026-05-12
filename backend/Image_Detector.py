import os
import re
from functools import lru_cache

import cv2

try:
    import easyocr
except ImportError:
    easyocr = None


EASYOCR_LANGUAGES = os.getenv("EASYOCR_LANGUAGES", "en").split(",")
EASYOCR_GPU = os.getenv("EASYOCR_GPU", "false").lower() == "true"


def _cleanup(path):
    if path and os.path.exists(path):
        os.remove(path)


def _resize_for_ocr(image):
    height, width = image.shape[:2]

    if width > 1600:
        scale = 1600 / width
        return cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    if width < 900:
        return cv2.resize(image, None, fx=1.25, fy=1.25, interpolation=cv2.INTER_CUBIC)

    return image


@lru_cache(maxsize=1)
def _get_reader():
    if easyocr is None:
        return None

    return easyocr.Reader(EASYOCR_LANGUAGES, gpu=EASYOCR_GPU, verbose=False)


def _extract_text(image):
    reader = _get_reader()

    if reader is None:
        raise RuntimeError("EasyOCR is not installed")

    prepared = _resize_for_ocr(image)
    results = reader.readtext(prepared, detail=0, paragraph=True)
    return "\n".join(str(item) for item in results if str(item).strip())


def get_ocr_status():
    if easyocr is None:
        return {
            "ocr_available": False,
            "engine": "EasyOCR",
            "languages": EASYOCR_LANGUAGES,
            "gpu": EASYOCR_GPU,
            "error": "easyocr package is not installed",
            "advice": "Install EasyOCR with: pip install easyocr",
        }

    try:
        _get_reader()
    except Exception as exc:
        return {
            "ocr_available": False,
            "engine": "EasyOCR",
            "languages": EASYOCR_LANGUAGES,
            "gpu": EASYOCR_GPU,
            "error": str(exc),
            "advice": "EasyOCR is installed but could not initialize. Check model download/network access.",
        }

    return {
        "ocr_available": True,
        "engine": "EasyOCR",
        "languages": EASYOCR_LANGUAGES,
        "gpu": EASYOCR_GPU,
        "advice": "OCR is ready.",
    }


def analyze_image(path):
    try:
        image = cv2.imread(path)

        if image is None:
            return {
                "risk_score": 0,
                "risk_level": "Error",
                "reasons": ["Unable to read image"],
                "advice": "Upload a valid image file.",
            }

        try:
            extracted_text = _extract_text(image)
        except Exception as exc:
            return {
                "risk_score": 0,
                "risk_level": "OCR Error",
                "reasons": [f"EasyOCR could not process this image: {exc}"],
                "advice": "Install EasyOCR, then upload a clearer screenshot with readable text.",
                "extracted_text": "",
            }

        normalized_text = extracted_text.lower()

        scam_keywords = [
            "urgent",
            "won",
            "winner",
            "prize",
            "gift card",
            "claim",
            "reward",
            "malicious",
            "phishing",
            "verify",
            "bank account",
            "compromised",
            "paypal",
            "suspended",
            "confirm your identity",
            "work-from-home",
            "earn",
            "click the link",
            "selected",
            "receive",
            "link",
            "account",
            "otp",
            "one time password",
            "one-time password",
        ]

        score = 0
        reasons = []

        for word in scam_keywords:
            if word in normalized_text:
                score += 15
                reasons.append(f"Suspicious text found: {word}")

        if re.search(r"\b\d{4,8}\b", normalized_text) and any(
            term in normalized_text
            for term in ["otp", "one time password", "one-time password", "code", "pin"]
        ):
            score += 25
            reasons.append("Sensitive OTP or verification code pattern detected")

        if re.search(r"https?://|www\.|[a-z0-9-]+\.(com|net|org|in|co|io|info|xyz)\b", normalized_text):
            score += 25
            reasons.append("Suspicious link/domain detected in screenshot")

        if len(normalized_text.strip()) < 4:
            reasons.append("OCR found little or no readable text")

        score = min(score, 100)

        if score >= 70:
            level = "High Risk"
        elif score >= 35:
            level = "Suspicious"
        else:
            level = "Likely Genuine"

        return {
            "risk_score": score,
            "risk_level": level,
            "reasons": reasons if reasons else ["No scam text detected"],
            "advice": "Do not click links or share OTP, password, bank, PayPal, or wallet details.",
            "extracted_text": extracted_text.strip()[:700],
        }
    finally:
        _cleanup(path)
