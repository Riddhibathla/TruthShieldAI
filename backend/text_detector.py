def detect_text_scam(text):
    keywords = ["urgent", "winner", "click now", "free", "limited offer"]

    score = 0
    reasons = []

    text = text.lower()

    for word in keywords:
        if word in text:
            score += 15
            reasons.append(f"Detected: {word}")

    if score >= 70:
        level = "High Risk"
    elif score >= 35:
        level = "Suspicious"
    else:
        level = "Low Risk"

    return {
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons,
        "advice": "Do not trust unknown messages."
    }