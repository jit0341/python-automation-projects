import re

QTY_RE = re.compile(r"\b\d+(\.\d+)?\b")
AMT_RE = re.compile(r"\b\d+(?:,\d{3})*(?:\.\d{2})?\b")

def extract_inventories(textract_lines):
    inventories = []

    for item in textract_lines:
        text = (item.get("text") or "").strip()
        low = text.lower()

        # very simple heuristic (demo-safe)
        if any(k in low for k in ["qty", "quantity", "rate", "amount"]):
            continue

        nums = AMT_RE.findall(text)
        if len(nums) >= 2:
            inventories.append({
                "item": text[:60],
                "qty": None,
                "rate": None,
                "amount": None
            })

    return inventories
