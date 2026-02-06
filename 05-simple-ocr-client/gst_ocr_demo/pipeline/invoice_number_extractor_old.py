import re

# ============================================================
# 🔒 KEYWORD CANON (FROZEN)
# ============================================================

INVOICE_KEYS = [
    "invoice no", "invoice number", "inv no", "inv. no",
    "inv#", "invoice#", "tax invoice no",
    "bill no", "bill number", "bill#",
    "document no", "doc no", "invoice ref", "ref no"
]

# ============================================================
# 🔒 REGEX CANON (ORDERED)
# ============================================================

REGEX_PATTERNS = [
    # Explicit invoice label
    r"(?i)invoice(?:\s*number|\s*no|\.?\s*no)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9\/\-\#]{1,80})",

    # INV prefix variants
    r"(?i)\bINV(?:OICE)?[^A-Z0-9]{0,3}([A-Z0-9][A-Z0-9\/\-\#]{1,80})\b",

    # Bill No variants
    r"(?i)bill(?:\s*no|\.?\s*no|number|\#)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9\/\-\#]{1,80})",

    # Tax invoice explicit
    r"(?i)tax\s+invoice\s*(?:no|number|\#)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9\/\-\#]{1,80})",

    # Pattern-only fallback (recall booster)
    r"\b([A-Z]{1,5}[\-\/]?\d{2,6}[\-\/]?\d{0,6}[A-Z0-9\-\/]{0,6})\b"
]

# ============================================================
# ❌ HARD REJECT REGEX
# ============================================================

DATE_RE = r"\b(\d{2}[\/\-]\d{2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{2}[\/\-]\d{2})\b"

GSTIN_RE = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]\b"

VEHICLE_RE = r"^[A-Z]{2}\d{2}[A-Z]{1,2}\d{3,4}$"

AMOUNT_RE = r"[₹\u20B9]\s*\d+(\.\d{2})?"

BAD_TOKENS = {
    "invoice", "tax invoice", "signature", "authorised",
    "authorized", "gst invoice", "bill"
}

# ============================================================
# ✅ TOKEN VALIDATOR
# ============================================================

def is_valid_invoice_number(token: str) -> bool:
    t = token.lower().strip()

    if t in BAD_TOKENS:
        return False

    if re.fullmatch(GSTIN_RE, token):
        return False

    if not any(ch.isdigit() for ch in t):
        return False

    if len(t) < 4 or len(t) > 40:
        return False

    if t.endswith((".jpg", ".png", ".pdf")):
        return False

    return True

# ============================================================
# 🧠 CORE EXTRACTOR
# ============================================================

def extract_invoice_number(textract_lines):
    candidates = []
    debug_rows = []

    for idx, item in enumerate(textract_lines):
        text = (item.get("text") or "").strip()
        confidence = item.get("confidence", 0)
        source = item.get("source", "line")

        if not text or len(text) < 4:
            continue

        for pattern in REGEX_PATTERNS:
            match = re.search(pattern, text)
            if not match:
                continue

            value = match.group(1).strip()

            debug = {
                "raw_text": text,
                "extracted_value": value,
                "source": source,
                "confidence": confidence,
                "score": None,
                "rejected": None
            }

            # ❌ HARD REJECTS (LOGGED)
            if re.search(DATE_RE, value):
                debug["rejected"] = "date_pattern"
                debug_rows.append(debug)
                continue

            if re.search(GSTIN_RE, value):
                debug["rejected"] = "gstin_pattern"
                debug_rows.append(debug)
                continue

            if re.fullmatch(VEHICLE_RE, value):
                debug["rejected"] = "vehicle_number"
                debug_rows.append(debug)
                continue

            if re.search(AMOUNT_RE, value):
                debug["rejected"] = "amount_pattern"
                debug_rows.append(debug)
                continue

            if not is_valid_invoice_number(value):
                debug["rejected"] = "invalid_token"
                debug_rows.append(debug)
                continue

            # ✅ SCORING
            score = 0

            if source == "kv":
                score += 40
            elif source == "table":
                score += 30
            else:
                score += 25

            if confidence:
                score += min(confidence / 3, 30)

            # 🔑 Keyword proximity (+/- 1 line)
            context_texts = []
            for j in (idx - 1, idx, idx + 1):
                if 0 <= j < len(textract_lines):
                    context_texts.append(textract_lines[j].get("text", "").lower())

            if any(k in ctx for ctx in context_texts for k in INVOICE_KEYS):
                score += 20

            score = round(score, 1)

            debug["score"] = score
            debug["rejected"] = "accepted"
            debug_rows.append(debug)

            candidates.append({
                "invoice_no": value,
                "score": score,
                "raw_text": text
            })

    # ========================================================
    # 🧯 FINAL SAFETY NET
    # ========================================================

    if not candidates:
        return {
            "invoice_no": None,
            "status": "EXCEPT",
            "score": 0,
            "debug": debug_rows
        }

    best = max(candidates, key=lambda x: x["score"])

    AUTO_THRESHOLD = 70  # demo polish
    REVIEW_THRESHOLD = 50

    if best["score"] >= AUTO_THRESHOLD:
        return {
            "invoice_no": best["invoice_no"],
            "status": "AUTO",
            "score": best["score"],
            "debug": debug_rows
        }

    return {
        "invoice_no": best["invoice_no"],
        "status": "REVIEW",
        "score": best["score"],
        "debug": debug_rows
    }
