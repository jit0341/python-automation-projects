import re

def extract_total_amount(lines):
    amount_re = r"(\d{1,3}(?:,\d{3})*(?:\.\d{2}))"
    candidates = []
    for l in lines:
        t = l.get("text", "").lower()
        if any(k in t for k in ["total", "payable", "grand", "net amount"]):
            m = re.search(amount_re, t)
            if m:
                val = float(m.group(1).replace(",", ""))
                candidates.append(val)
    
    if candidates:
        return {"total_amount": max(candidates)}
    return {"total_amount": 0.0}
