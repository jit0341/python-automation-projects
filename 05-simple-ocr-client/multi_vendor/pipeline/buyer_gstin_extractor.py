import re

# Strong GSTIN regex (India)
GSTIN_REGEX = re.compile(
    r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b"
)

def extract_buyer_gstin(lines, supplier_gstin=None):
    """
    Returns:
        {
            "buyer_gstin": "27ABCDE1234F1Z5" or "Not Found",
            "confidence": 0.0 - 1.0
        }
    """

    found = []

    for line in lines:
        text = line.get("text", "").upper()

        matches = GSTIN_REGEX.findall(text)
        for gst in matches:
            if supplier_gstin and gst == supplier_gstin:
                continue  # skip supplier GSTIN

            found.append(gst)

    # --- LOCK LOGIC ---
    if found:
        # first valid GSTIN = buyer GSTIN
        return {
            "buyer_gstin": found[0],
            "confidence": 0.95
        }

    return {
        "buyer_gstin": "Not Found",
        "confidence": 0.0
    }
