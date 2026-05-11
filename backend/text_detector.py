import re


def detect_text_scam(text):
    original_text = text or ""
    normalized = original_text.lower().strip()

    scam_patterns = {
        "Urgency or pressure language": [
            "urgent",
            "immediately",
            "act now",
            "limited time",
            "final warning",
            "account suspended",
            "will be blocked",
            "expires today",
        ],
        "Credential or identity request": [
            "password",
            "otp",
            "one time password",
            "pin",
            "verify your account",
            "confirm your identity",
            "login",
            "sign in",
            "kyc",
        ],
        "Financial or payment request": [
            "bank",
            "upi",
            "paypal",
            "wallet",
            "crypto",
            "bitcoin",
            "gift card",
            "transfer",
            "refund",
            "fee",
        ],
        "Reward or prize bait": [
            "won",
            "winner",
            "prize",
            "reward",
            "bonus",
            "cashback",
            "free",
            "claim",
            "selected",
            "congratulations",
        ],
    }

    score = 0
    reasons = []

    for category, terms in scam_patterns.items():
        matched_terms = [term for term in terms if term in normalized]
        if matched_terms:
            score += min(35, 15 * len(matched_terms))
            reasons.append(f"{category}: {', '.join(matched_terms[:4])}")

    if re.search(r"https?://|www\.|[a-z0-9-]+\.(com|net|org|in|co|io|info|xyz)\b", normalized):
        score += 25
        reasons.append("Contains a link or domain")

    if re.search(r"\b\d{4,}\b", normalized) and any(term in normalized for term in ["otp", "code", "pin", "password"]):
        score += 20
        reasons.append("Requests or includes a sensitive numeric code")

    if len(normalized) > 250 and any(term in normalized for term in ["click", "verify", "claim", "login"]):
        score += 10
        reasons.append("Long persuasive message with action request")

    score = min(score, 100)

    if not normalized:
        level = "No Input"
        reasons = ["Enter text to analyze"]
        advice = "Paste a suspicious message before scanning."
    elif score >= 70:
        level = "High Risk"
        advice = "Do not click links, share codes, or send money. Verify through the official app or website."
    elif score >= 35:
        level = "Suspicious"
        advice = "Treat this message carefully and verify it through an official channel."
    else:
        level = "Likely Genuine"
        reasons = reasons or ["No strong scam indicators detected"]
        advice = "No major red flags were found, but stay cautious with unexpected requests."

    return {
        "text": original_text,
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons,
        "advice": advice,
    }
