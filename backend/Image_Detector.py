import pytesseract
import cv2
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def analyze_image(path):
    image = cv2.imread(path)

    if image is None:
        return {
            "risk_score": 0,
            "risk_level": "Error",
            "reasons": ["Unable to read image"],
            "advice": "Upload a valid image file."
        }

    extracted_text = pytesseract.image_to_string(image).lower()

    scam_keywords = [
        "urgent", "won", "prize", "gift card", "claim",
        "reward", "malicious", "phishing", "verify",
        "bank account", "compromised", "paypal",
        "suspended", "confirm your identity",
        "work-from-home", "earn", "click the link",
        "selected", "receive", "link", "account"
    ]

    score = 0
    reasons = []

    for word in scam_keywords:
        if word in extracted_text:
            score += 15
            reasons.append(f"Suspicious text found: {word}")

    if ".com" in extracted_text or "http" in extracted_text:
        score += 25
        reasons.append("Suspicious link/domain detected in screenshot")

    score = min(score, 100)

    if score >= 70:
        level = "High Risk"
    elif score >= 35:
        level = "Suspicious"
    else:
        level = "Likely Genuine"

    if os.path.exists(path):
        os.remove(path)

    return {
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons if reasons else ["No scam text detected"],
        "advice": "Do not click links or share personal, bank, PayPal, or wallet details.",
        "extracted_text": extracted_text[:500]
    }