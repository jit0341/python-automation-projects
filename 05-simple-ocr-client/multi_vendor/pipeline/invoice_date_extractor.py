#invoice_date_extractor.py
import re

DATE_RE = r"\b(\d{1,2}[\/\-\.][A-Za-z]{3}[\/\-\.]\d{2,4}|\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\b"

def extract_invoice_date(lines):
    for i, l in enumerate(lines[:20]):
        if any(k in l.get("text", "").lower() for k in ["date", "dated"]):
            m = re.search(DATE_RE, l.get("text", ""))
            if m:
                return {"invoice_date": m.group(1)}

    for l in lines:
        m = re.search(DATE_RE, l.get("text", ""))
        if m:
            return {"invoice_date": m.group(1)}

    return {"invoice_date": None}

