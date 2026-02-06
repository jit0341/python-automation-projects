BUYER_KEYS = ["bill to", "billed to", "buyer", "ship to"]
SUPPLIER_KEYS = ["sold by", "supplier", "from"]

def extract_names(lines):
    buyer = None
    supplier = None

    for i, item in enumerate(lines):
        text = (item.get("text") or "").strip()
        low = text.lower()

        if any(k in low for k in BUYER_KEYS) and i+1 < len(lines):
            buyer = lines[i+1].get("text")

        if any(k in low for k in SUPPLIER_KEYS) and i+1 < len(lines):
            supplier = lines[i+1].get("text")

    return buyer, supplier
