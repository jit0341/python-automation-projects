import re

def extract_invoice_number(lines_with_geo):
    labels = ["invoice no", "inv no", "bill no", "invoice number", "inv #"]
    for i, line in enumerate(lines_with_geo[:20]):
        text = line['text']
        low_text = text.lower()
        for label in labels:
            if label in low_text:
                # लेबल हटाकर केवल अल्फा-न्यूमेरिक वैल्यू निकालें
                val = re.sub(r'(?i)' + label, '', text).strip(": -#")
                # अगर वैल्यू उसी लाइन में है
                if len(val) >= 3 and not re.search(r"\d{2}[/-]\d{2}", val):
                    return {"invoice_no": val.split()[0]} # सिर्फ पहला शब्द लें
                
                # अगर वैल्यू नीचे वाली लाइन में है
                if i+1 < len(lines_with_geo):
                    next_val = lines_with_geo[i+1]['text'].strip()
                    if len(next_val) >= 3 and not re.search(r"\d{2}[/-]\d{2}", next_val):
                        return {"invoice_no": next_val.split()[0]}
    return {"invoice_no": "Not Found"}
