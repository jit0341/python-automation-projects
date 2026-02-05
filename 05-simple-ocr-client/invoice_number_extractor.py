# ===========================
# v1.4 – Invoice Number Extractor (GST OCR)
# STATUS: FROZEN LOGIC
# ===========================

import re

# -------------------------------------------------
# 🔒 KEYWORD CANON (FROZEN – DO NOT CHANGE)
# -------------------------------------------------
INVOICE_KEYS = [
    "invoice no", "invoice number", "inv no", "inv. no", "inv#", "invoice#",
    "tax invoice no", "bill no", "bill number", "bill#",
    "document no", "doc no", "invoice ref", "ref no"
]

# -------------------------------------------------
# 🔒 REGEX CANON (ORDERED, FROZEN)
# -------------------------------------------------
REGEX_PATTERNS = [
    # 1️⃣ Explicit invoice label
    r"(?i)invoice(?:\s*number|\s*no|\.?\s*no|#)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9\/\-\.\#_]{1,80})",

    # 2️⃣ INV prefix variants
    r"(?i)\bINV(?:OICE)?[^\w]{0,3}([A-Z0-9][A-Z0-9\/\-\.\#_]{1,80})\b",

    # 3️⃣ Bill No variants
    r"(?i)bill(?:\s*no|\.?\s*no|number|#)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9\/\-\.\#_]{1,80})",

    # 4️⃣ Tax invoice explicit
    r"(?i)tax\s+invoice\s*(?:no|number|#)?\s*[:\-]?\s*([A-Z0-9\/\-\.\#_]{1,80})",

    # 5️⃣ Pattern-only fallback (lowest priority)
    r"\b([A-Z]{1,6}\/\d{1,6}\/\d{2,4}|[A-Z0-9]{2,8}-\d{1,7}|[A-Z0-9]{4,40}\/[A-Z0-9\-\/]{1,40})\b"
]

# -------------------------------------------------
# ❌ HARD REJECT FILTERS (NON-NEGOTIABLE)
# -------------------------------------------------
DATE_RE   = r"\b(\d{2}[\/\-]\d{2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{2}[\/\-]\d{2})\b"
GSTIN_RE  = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]\b"
AMOUNT_RE = r"[₹\u20B9]|\d+\.\d{2}"

# -------------------------------------------------
# 🧠 CORE EXTRACTOR
# -------------------------------------------------
def extract_invoice_number(textract_lines):
    """
    textract_lines: list of dicts (OLD Textract JSON compatible)
    [
        {
            "text": "Invoice No: INV/2024/00123",
            "confidence": 92,          # optional
            "source": "kv|line|table"  # optional
        }
    ]
    """

    candidates = []

    for item in textract_lines:
        text = item.get("text", "")
        confidence = item.get("confidence", 0)
        source = item.get("source", "line")

        if not text or len(text) < 4:
            continue

        for pattern in REGEX_PATTERNS:
            match = re.search(pattern, text)
            if not match:
                continue

            value = match.group(1).strip()

            # ---------------------------
            # ❌ HARD REJECTS
            # ---------------------------
            if re.search(DATE_RE, value):
                continue
            if re.search(GSTIN_RE, value):
                continue
            if re.search(AMOUNT_RE, value):
                continue
            if len(value) < 4 or len(value) > 40:
                continue

            # ---------------------------
            # ✅ SCORING
            # ---------------------------
            score = 0

            # Source weight
            if source == "kv":
                score += 40
            elif source == "table":
                score += 30
            else:
                score += 25

            # OCR confidence bonus (max 30)
            if confidence:
                score += min(confidence / 3, 30)

            candidates.append({
                "invoice_no": value,
                "score": round(score, 1),
                "source": source,
                "ocr_confidence": confidence,
                "raw_text": text
            })

    # ---------------------------
    # FINAL DECISION
    # ---------------------------
    if not candidates:
        return {
            "invoice_no": None,
            "status": "EXCEPTION",
            "score": 0,
            "reason": "Invoice number not found"
        }

    best = max(candidates, key=lambda x: x["score"])

    if best["score"] >= 70:
        return {
            "invoice_no": best["invoice_no"],
            "status": "AUTO",
            "score": best["score"]
        }

    return {
        "invoice_no": best["invoice_no"],
        "status": "REVIEW",
        "score": best["score"]
    }

# -------------------------------------------------
# 🧪 LOCAL TEST (OPTIONAL)
# -------------------------------------------------
if __name__ == "__main__":
    sample = [
        {"text": "Invoice No: INV/2024/00123", "confidence": 94, "source": "kv"},
        {"text": "Invoice Date: 31/03/2024", "confidence": 90},
        {"text": "GSTIN: 27AAPFU0939F1ZV", "confidence": 96},
        {"text": "Total Amount ₹12,345.00", "confidence": 95}
    ]

    result = extract_invoice_number(sample)
    print(result)
