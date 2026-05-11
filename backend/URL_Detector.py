from urllib.parse import urlparse
import re


SUSPICIOUS_WORDS = [
    "free",
    "claim",
    "bonus",
    "wallet",
    "airdrop",
    "login",
    "verify",
    "bank",
    "crypto",
    "win",
    "urgent",
    "password",
    "security",
    "support",
    "update",
]

TRUSTED_BRANDS = [
    "microsoft",
    "google",
    "amazon",
    "paypal",
    "facebook",
    "apple",
    "instagram",
    "netflix",
]

KNOWN_SPOOFS = {
    "microsoft": ["rnicrosoft", "micr0soft", "microsooft", "micros0ft"],
    "google": ["g00gle", "goog1e", "gooogle"],
    "amazon": ["amaz0n", "arnazon"],
    "paypal": ["paypa1", "paypai"],
    "apple": ["app1e", "applle"],
}

LOOKALIKE_TRANSLATION = str.maketrans({
    "0": "o",
    "1": "l",
    "3": "e",
    "5": "s",
    "7": "t",
    "@": "a",
    "$": "s",
})


def _levenshtein(left, right):
    if left == right:
        return 0

    if len(left) < len(right):
        left, right = right, left

    previous = list(range(len(right) + 1))

    for i, left_char in enumerate(left, start=1):
        current = [i]
        for j, right_char in enumerate(right, start=1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (left_char != right_char)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current

    return previous[-1]


def _registrable_name(domain):
    domain = domain.lower().strip(".")

    if domain.startswith("www."):
        domain = domain[4:]

    parts = [part for part in domain.split(".") if part]

    if not parts:
        return ""

    if len(parts) >= 3 and parts[-2] in {"co", "com", "net", "org"}:
        return parts[-3]

    return parts[-2] if len(parts) >= 2 else parts[0]


def _looks_like_brand(domain_name, brand):
    compact = re.sub(r"[^a-z0-9@$-]", "", domain_name)
    normalized = compact.translate(LOOKALIKE_TRANSLATION).replace("rn", "m")
    normalized = normalized.replace("-", "")

    if compact == brand:
        return False

    if normalized == brand:
        return True

    if brand in compact or brand in normalized:
        return True

    if compact in KNOWN_SPOOFS.get(brand, []) or normalized in KNOWN_SPOOFS.get(brand, []):
        return True

    return _levenshtein(normalized, brand) <= 2


def detect_url_scam(url):
    original_url = url or ""
    normalized_url = original_url.lower().strip()

    score = 0
    reasons = []

    if not normalized_url:
        return {
            "url": original_url,
            "risk_score": 0,
            "risk_level": "No Input",
            "reasons": ["Enter a URL to analyze"],
            "advice": "Paste a suspicious link or domain before scanning.",
        }

    if not normalized_url.startswith(("http://", "https://")):
        normalized_url = "http://" + normalized_url
        score += 10
        reasons.append("Missing protocol")

    parsed = urlparse(normalized_url)
    domain = parsed.netloc.split("@")[-1].split(":")[0]
    domain_name = _registrable_name(domain)

    for word in SUSPICIOUS_WORDS:
        if word in normalized_url:
            score += 12
            reasons.append(f"Suspicious keyword detected: '{word}'")

    if domain.count(".") > 3:
        score += 15
        reasons.append("Too many subdomains")

    if re.match(r"^\d+\.\d+\.\d+\.\d+$", domain):
        score += 30
        reasons.append("IP address used instead of a domain")

    if "@" in normalized_url:
        score += 25
        reasons.append("@ symbol can hide the real destination")

    if "-" in domain_name:
        score += 10
        reasons.append("Hyphenated domain name")

    if len(normalized_url) > 100:
        score += 15
        reasons.append("URL is unusually long")

    if not normalized_url.startswith("https://"):
        score += 20
        reasons.append("Website is not using HTTPS")

    for brand in TRUSTED_BRANDS:
        if _looks_like_brand(domain_name, brand):
            score += 60
            reasons.append(f"Possible spoofing of '{brand}'")
            break

    if re.search(r"[%$^*(){}|<>]", normalized_url):
        score += 15
        reasons.append("Strange or suspicious characters detected")

    score = min(score, 100)

    if score >= 70:
        level = "High Risk"
    elif score >= 35:
        level = "Suspicious"
    else:
        level = "Likely Genuine"
        reasons = reasons or ["No strong phishing indicators detected"]

    return {
        "url": original_url,
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons,
        "advice": "Avoid clicking suspicious or unknown links. Open trusted sites by typing the address yourself.",
    }
