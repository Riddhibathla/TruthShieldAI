import re

def detect_text_scam(text):
    keywords = [
        "urgent", "winner", "click now", "free", "limited offer",
        "claim", "reward", "prize", "congratulations", "verify",
        "password", "otp", "account blocked", "bank account",
        "lottery", "gift card", "airdrop", "wallet", "login"
    ]

    urgency_words = [
        "immediately", "today only", "last chance",
        "act now", "within 24 hours", "expire", "expires"
    ]

    score = 0
    reasons = []

    original_text = text
    text = text.lower().strip()

    # 1. Keyword detection
    for word in keywords:
        if word in text:
            score += 12
            reasons.append(f"Suspicious keyword detected: '{word}'")

    # 2. Urgency detection
    for word in urgency_words:
        if word in text:
            score += 15
            reasons.append(f"Urgency/FOMO phrase detected: '{word}'")

    # 3. Link detection
    if re.search(r"http[s]?://|www\.", text):
        score += 20
        reasons.append("Message contains a link")

    # 4. Phone number detection
    if re.search(r"\b\d{10}\b", text):
        score += 10
        reasons.append("Phone number detected")

    # 5. OTP or PIN request
    if re.search(r"\b(otp|pin|cvv|password)\b", text):
        score += 25
        reasons.append("Sensitive information request detected")

    # 6. Money/prize amount
    if re.search(r"(₹|rs\.?|inr|\$)\s?\d+", text):
        score += 15
        reasons.append("Money amount detected")

    # 7. Excessive punctuation
    if text.count("!") >= 3:
        score += 10
        reasons.append("Excessive exclamation marks detected")

    # 8. All caps detection
    words = original_text.split()
    caps_words = [w for w in words if w.isupper() and len(w) > 3]

    if len(caps_words) >= 2:
        score += 10
        reasons.append("Too many capitalized words detected")

    # Final risk level
    if score >= 70:
        level = "High Risk"
    elif score >= 35:
        level = "Suspicious"
    else:
        level = "Low Risk"

    return {
        "risk_score": min(score, 100),
        "risk_level": level,
        "reasons": reasons,
        "advice": "Do not trust unknown messages asking for money, OTP, password, or urgent action."
    }