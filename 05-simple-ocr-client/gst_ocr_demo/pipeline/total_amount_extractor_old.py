import re

AMOUNT_KEYS = [
    "grand total",
    "net payable",
    "amount payable",
    "total amount",
    "invoice total",
    "total payable",
    "balance due",
    "total",
    "amount"
]

CURRENCY_RE = re.compile(
    r"(₹|rs\.?)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)",
    re.IGNORECASE
)

def normalize_amount(val):
    try:
        return round(float(val.replace(",", "")), 2)
    except:
        return None

def extract_total_amount(lines):
    candidates = []
    debug = []

    total_lines = len(lines)

    for idx, item in enumerate(lines):
        text = (item.get("text") or "").strip()
        low = text.lower()
        conf = item.get("confidence", 0)

        for m in CURRENCY_RE.finditer(text):
            amt = normalize_amount(m.group(2))
            if not amt or amt < 10:
                continue

            score = 40
            score += min(conf / 2, 25)

            # keyword boost
            if any(k in low for k in AMOUNT_KEYS):
                score += 20

            # bottom of invoice boost
            if idx > total_lines * 0.65:
                score += 15

            score = round(score, 1)

            candidates.append((amt, score))
            debug.append({
                "raw_text": text,
                "extracted_amount": amt,
                "score": score,
                "confidence": conf,
                "rejected": "accepted"
            })

    if not candidates:
        return {
            "total_amount": None,
            "status": "EXCEPT",
            "score": 0,
            "debug": debug
        }

    best = max(candidates, key=lambda x: x[1])

    return {
        "total_amount": best[0],
        "status": "AUTO" if best[1] >= 65 else "REVIEW",
        "score": best[1],
        "debug": debug
    }
