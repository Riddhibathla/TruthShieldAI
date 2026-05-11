from urllib.parse import urlparse
from Levenshtein import distance
import re


def detect_url_scam(url):

    suspicious_words = [
        "free", "claim", "bonus", "wallet",
        "airdrop", "login", "verify", "bank",
        "crypto", "win", "urgent", "password"
    ]

    trusted_brands = [
        "microsoft",
        "google",
        "amazon",
        "paypal",
        "facebook",
        "apple"
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

    # Remove www
    domain = domain.replace("www.", "")

    # Main domain name only
    domain_name = domain.split(".")[0]

    # 1. Suspicious keywords
    for word in suspicious_words:
        if word in url:
            score += 12
            reasons.append(f"Suspicious keyword detected: '{word}'")

    # 2. Too many subdomains
    if domain.count(".") > 3:
        score += 15
        reasons.append("Too many subdomains")

    # 3. IP address instead of domain
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", domain):
        score += 30
        reasons.append("IP address used instead of domain")

    # 4. @ symbol trick
    if "@" in url:
        score += 25
        reasons.append("@ symbol detected in URL")

    # 5. Hyphenated domains
    if "-" in domain:
        score += 10
        reasons.append("Hyphenated domain detected")

    # 6. Long URL
    if len(url) > 100:
        score += 15
        reasons.append("URL is unusually long")

    # 7. HTTP instead of HTTPS
    if not url.startswith("https://"):
        score += 20
        reasons.append("Website is not using HTTPS")

    # 8. Brand spoof detection using similarity
    for trusted in trusted_brands:

        dist = distance(domain_name, trusted)

        # Small spelling difference = suspicious
        if dist <= 2 and domain_name != trusted:
            score += 60
            reasons.append(f"Possible spoofing of '{trusted}'")

    # 9. Strange characters
    if re.search(r"[%$^*(){}|<>]", url):
        score += 15
        reasons.append("Strange/suspicious characters detected")

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
    "rnicrosoft.com",
    "micr0soft-login.net",
    "g00gle-security.com",
    "paypa1verify.org",
    "https://google.com",
    "http://192.168.1.1/login",
    "free-airdrop-bonus.net",
    "https://amazon.com"
]

for url in test_urls:
    result = detect_url_scam(url)

    print("\nURL:", result["url"])
    print("Risk Score:", result["risk_score"])
    print("Risk Level:", result["risk_level"])

    print("Reasons:")
    for reason in result["reasons"]:
        print("-", reason)

    print("Advice:", result["advice"])
    print("-" * 60)