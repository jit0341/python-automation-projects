import re

GSTIN_RE = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]\b"

BUYER_KEYS = ["bill to", "buyer", "ship to", "recipient"]
SUPPLIER_KEYS = ["supplier", "from", "seller"]

def extract_gstins(textract_lines):
    buyer_gstin = None
    supplier_gstin = None

    for idx, item in enumerate(textract_lines):
        text = (item.get("text") or "")
        up = text.upper()

        m = re.search(GSTIN_RE, up)
        if not m:
            continue

        gstin = m.group(0)

        # context window ±1 line
        context = ""
        for j in (idx-1, idx, idx+1):
            if 0 <= j < len(textract_lines):
                context += " " + (textract_lines[j].get("text") or "").lower()

        if any(k in context for k in BUYER_KEYS) and not buyer_gstin:
            buyer_gstin = gstin
            continue

        if any(k in context for k in SUPPLIER_KEYS) and not supplier_gstin:
            supplier_gstin = gstin
            continue

        # fallback
        if not supplier_gstin:
            supplier_gstin = gstin
        elif not buyer_gstin:
            buyer_gstin = gstin

    return {
        "buyer_gstin": buyer_gstin,
        "supplier_gstin": supplier_gstin
    }
