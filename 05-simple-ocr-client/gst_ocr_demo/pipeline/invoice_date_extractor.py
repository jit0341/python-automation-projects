import re
from datetime import datetime

# ---------------------------------------
# DATE REGEX CANON (FROZEN)
# ---------------------------------------
DATE_PATTERNS = [
    r"\b(\d{2}[\/\-]\d{2}[\/\-]\d{4})\b",   # 12/08/2024
    r"\b(\d{2}[\/\-]\d{2}[\/\-]\d{2})\b",   # 12/08/24
    r"\b(\d{4}[\/\-]\d{2}[\/\-]\d{2})\b",   # 2024-08-12
]

DATE_KEYS = [
    "invoice date",
    "inv date",
    "date of invoice",
    "dated",
]

AUTO_THRESHOLD = 65   # demo friendly

# ---------------------------------------
# CORE EXTRACTOR
# ---------------------------------------
def extract_invoice_date(textract_lines):
    candidates = []
    debug = []

    for idx, item in enumerate(textract_lines):
        text = (item.get("text") or "").strip()
        if not text:
            continue

        confidence = item.get("confidence", 0)
        low = text.lower()

        for pat in DATE_PATTERNS:
            m = re.search(pat, text)
            if not m:
                continue

            raw_date = m.group(1)
            score = 30

            # confidence boost
            if confidence:
                score += min(confidence / 3, 30)

            # keyword proximity (±1 line)
            ctx = []
            for j in (idx - 1, idx, idx + 1):
                if 0 <= j < len(textract_lines):
                    ctx.append(
                        (textract_lines[j].get("text") or "").lower()
                    )

            if any(k in c for c in ctx for k in DATE_KEYS):
                score += 20

            score = round(score, 1)

            # normalize date (best effort)
            normalized = raw_date
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(raw_date, fmt)
                    normalized = dt.strftime("%Y-%m-%d")
                    break
                except:
                    pass

            debug.append({
                "raw_text": text,
                "extracted_date": raw_date,
                "normalized_date": normalized,
                "score": score
            })

            candidates.append((normalized, score))

    # ---------------------------------------
    # FINAL DECISION
    # ---------------------------------------
    if not candidates:
        return {
            "invoice_date": None,
            "status": "EXCEPT",
            "score": 0,
            "debug": debug
        }

    best = max(candidates, key=lambda x: x[1])

    return {
        "invoice_date": best[0],
        "status": "AUTO" if best[1] >= AUTO_THRESHOLD else "REVIEW",
        "score": best[1],
        "debug": debug
    }
