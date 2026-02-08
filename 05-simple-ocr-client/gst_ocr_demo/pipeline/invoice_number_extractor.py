import re

def extract_invoice_number(lines):
    # पुराने और नए पैटर्न्स का मिश्रण
    patterns = [
        r"(?i)(?:invoice|inv|bill)\s*(?:no|number|#)?[:\-\s]*([A-Z0-9\/\-]+)",
        r"\b([A-Z]{2,}\d{4,})\b", # Pattern like ABC/2024/001
        r"\b(\d{3,8})\b"          # Pure numeric invoice no (3-8 digits)
    ]
    
    for idx, item in enumerate(lines[:15]): # शुरुआत की 15 लाइनें
        text = item.get("text", "").strip()
        for p in patterns:
            match = re.search(p, text)
            if match:
                val = match.group(1) if len(match.groups()) > 0 else match.group(0)
                # सफाई: अगर अंत में स्लैश या डैश है तो हटा दें
                val = val.strip("/- ")
                # तारीख या साल (जैसे 2024-25) को इनवॉइस नंबर न समझें
                if len(val) >= 3 and not re.search(r"^\d{2,4}[-/]\d{2}$", val):
                    return {"invoice_no": val}
                    
    return {"invoice_no": "Not Found"}
