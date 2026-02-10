import re

INVOICE_REGEX = re.compile(
    r'\b([A-Z]{1,5}[-/ ]?\d{1,6}[-/ ]?\d{0,4}|\d{3,10})\b'
)

INVALID_WORDS = ["GSTIN", "STATE", "DATE", "TOTAL", "AMOUNT"]

LABELS = [
    "invoice no", "inv no", "invoice number",
    "invoice#", "inv#", "bill no", "bill#", "tax invoice"
]


def clean_value(val: str) -> str:
    val = val.strip().replace(":", "").replace("#", "")
    val = re.sub(r'[^A-Za-z0-9/-]', '', val)
    return val


def is_valid_invoice(val: str) -> bool:
    if not val or len(val) < 3:
        return False

    val_up = val.upper()

    # must contain at least one digit
    if not any(c.isdigit() for c in val):
        return False

    # common junk words
    JUNK = [
        "ORIGINAL", "DUPLICATE", "REF", "REFERENCE",
        "INTERNAL", "COPY", "TAX", "GST", "STATE",
        "PLACE", "NAME"
    ]
    if any(j in val_up for j in JUNK):
        return False

    if val in ["N/A", "NA", "0", "-", ":"]:
        return False

    return True

def extract_invoice_number(lines):
    """
    Strong invoice number extractor
    Returns: {"invoice_no": value or "N/A"}
    """

    # ---- PASS 1: Label based search ----
    for i, l in enumerate(lines[:25]):
        text = l.get("text", "").strip()
        low = text.lower()

        for lb in LABELS:
            if lb in low:
                # Same line extraction
                after = re.sub(r'(?i).*' + re.escape(lb), '', text)
                after = clean_value(after)

                if is_valid_invoice(after):
                    return {"invoice_no": after}

                # Next line fallback
                if i + 1 < len(lines):
                    nxt = clean_value(lines[i + 1].get("text", ""))
                    if is_valid_invoice(nxt):
                        return {"invoice_no": nxt}

    # ---- PASS 2: Regex based fallback ----
    for l in lines[:30]:
        text = l.get("text", "").strip()
        for match in INVOICE_REGEX.findall(text):
            candidate = clean_value(match)
            if is_valid_invoice(candidate):
                return {"invoice_no": candidate}

    return {"invoice_no": "N/A"}
