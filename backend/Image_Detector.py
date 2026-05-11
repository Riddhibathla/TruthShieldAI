import os
import re
import shutil

import cv2
import pytesseract


TESSERACT_CMD = os.getenv("TESSERACT_CMD") or shutil.which("tesseract")

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def _cleanup(path):
    if path and os.path.exists(path):
        os.remove(path)


def _preprocess_for_ocr(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=1.6, fy=1.6, interpolation=cv2.INTER_CUBIC)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def _extract_text(image):
    processed = _preprocess_for_ocr(image)
    config = "--oem 3 --psm 6"
    return pytesseract.image_to_string(processed, config=config)


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
        except pytesseract.TesseractNotFoundError:
            return {
                "risk_score": 0,
                "risk_level": "OCR Unavailable",
                "reasons": ["Tesseract OCR is not installed or TESSERACT_CMD is not configured"],
                "advice": "Install Tesseract on the backend server and set TESSERACT_CMD if needed.",
                "extracted_text": "",
            }
        except Exception as exc:
            return {
                "risk_score": 0,
                "risk_level": "OCR Error",
                "reasons": [f"OCR could not process this image: {exc}"],
                "advice": "Upload a clearer screenshot with readable text.",
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
            term in normalized_text for term in ["otp", "one time password", "one-time password", "code", "pin"]
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
