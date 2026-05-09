def detect_url_scam(url):
    suspicious_words = ["free", "claim", "bonus", "wallet", "airdrop", "login"]

    score = 0
    reasons = []

    url = url.lower()

    for word in suspicious_words:
        if word in url:
            score += 15
            reasons.append(f"Suspicious word found: {word}")

    if "http" not in url:
        score += 10
        reasons.append("Invalid or missing protocol")

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
        "advice": "Avoid opening unknown links."
    }