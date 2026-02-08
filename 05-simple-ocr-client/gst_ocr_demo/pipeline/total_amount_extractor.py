import re

def extract_total_amount(lines):
    amt_re = r"(\d{1,3}(?:,\d{3})*(?:\.\d{2}))"
    candidates = []
    
    for item in lines:
        text = item.get("text", "").lower()
        match = re.search(amt_re, text)
        if match:
            clean_amt = float(match.group(1).replace(",", ""))
            score = 0
            if any(k in text for k in ["grand total", "total amount", "payable"]): score += 100
            elif "total" in text: score += 50
            
            candidates.append({"amt": match.group(1), "val": clean_amt, "score": score})
    
    if not candidates: return {"total_amount": "0.00"}
    
    # स्कोर और अमाउंट की वैल्यू दोनों के आधार पर सबसे बेस्ट चुनें
    best = max(candidates, key=lambda x: (x['score'], x['val']))
    return {"total_amount": best['amt']}
