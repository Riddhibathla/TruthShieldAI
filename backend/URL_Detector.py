from urllib.parse import urlparse
import re

def detect_url_scam(url):
    suspicious_words = [
        "free", "claim", "bonus", "wallet",
        "airdrop", "login", "verify", "bank",
        "crypto", "win", "urgent", "password"
    ]

    trusted_domains = [
        "google.com",
        "microsoft.com",
        "amazon.com",
        "paypal.com",
        "apple.com"
    ]

    score = 0
    reasons = []

    original_url = url
    url = url.lower().strip()

    # Add protocol if missing
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
        score += 10
        reasons.append("Missing HTTPS/HTTP protocol")

    parsed = urlparse(url)
    domain = parsed.netloc

    # 1. Suspicious keywords
    for word in suspicious_words:
        if word in url:
            score += 12
            reasons.append(f"Suspicious keyword detected: '{word}'")

    # 2. Too many dots/subdomains
    if domain.count(".") > 3:
        score += 15
        reasons.append("Too many subdomains")

    # 3. IP address instead of domain
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", domain):
        score += 30
        reasons.append("IP address used instead of domain")

    # 4. Detect @ symbol trick
    if "@" in url:
        score += 25
        reasons.append("@ symbol detected in URL")

    # 5. Hyphen abuse
    if "-" in domain:
        score += 10
        reasons.append("Hyphenated domain detected")

    # 6. Fake/spoofed trusted brands
    spoof_patterns = {
        "microsoft": ["rnicrosoft", "micr0soft"],
        "google": ["g00gle", "goog1e"],
        "amazon": ["amaz0n"],
        "paypal": ["paypa1"],
    }

    for brand, fakes in spoof_patterns.items():
        for fake in fakes:
            if fake in domain:
                score += 50
                reasons.append(f"Possible spoofing of {brand}")

    # 7. Very long URL
    if len(url) > 100:
        score += 15
        reasons.append("URL is unusually long")

    # 8. Non-HTTPS
    if not url.startswith("https://"):
        score += 20
        reasons.append("URL is not secure (HTTPS missing)")

    # Final risk level
    if score >= 70:
        level = "High Risk"
    elif score >= 35:
        level = "Suspicious"
    else:
        level = "Low Risk"

    return {
        "url": original_url,
        "risk_score": min(score, 100),
        "risk_level": level,
        "reasons": reasons,
        "advice": "Avoid clicking suspicious or unknown links."
    }


# TESTING
test_urls = [
    "rnicrosoft-login.com",
    "http://shop.coolapp.org/home",
    "https://google.com",
    "http://192.168.1.1/login",
    "free-airdrop-bonus.net"
]

for url in test_urls:
    print(detect_url_scam(url))
    print("-" * 50)