import re

def extract_invoice_date(lines):
    # भारतीय और ग्लोबल डेट फॉर्मेट्स
    date_patterns = [
        r"\b(\d{1,2}[\/\-\.][A-Za-z]{3}[\/\-\.]\d{2,4})\b", # 08-Feb-2026
        r"\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\b",     # 08-02-2026
        r"\b(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})\b"      # 2026-02-08
    ]
    
    keywords = ["date", "dated", "inv date", "dt:"]

    for i, item in enumerate(lines[:20]):
        text = item.get("text", "").strip()
        low = text.lower()
        
        # अगर कीवर्ड मिला है
        if any(k in low for k in keywords):
            for p in date_patterns:
                m = re.search(p, text)
                if m: return {"invoice_date": m.group(1)}
            
            # अगर उसी लाइन में नहीं, तो अगली लाइन देखें
            if i + 1 < len(lines):
                next_t = lines[i+1].get("text", "").strip()
                for p in date_patterns:
                    m = re.search(p, next_t)
                    if m: return {"invoice_date": m.group(1)}

    # बैकअप सर्च (बिना कीवर्ड के)
    for item in lines[:25]:
        for p in date_patterns:
            m = re.search(p, item.get("text", ""))
            if m: return {"invoice_date": m.group(1)}

    return {"invoice_date": "Not Found"}
