import re

def extract_names(lines):
    buyer, supplier = "Not Found", "Not Found"
    
    # 1. Supplier: पहली 5 लाइन में सबसे बड़ा और बोल्ड टेक्स्ट (इग्नोर 'Invoice')
    for i, item in enumerate(lines[:5]):
        text = item.get("text", "").strip()
        if len(text) > 5 and not re.search(r"(?i)invoice|tax|bill|cash", text):
            supplier = text
            break

    # 2. Buyer: 'Bill To' के नीचे की सटीक लाइन
    for i, item in enumerate(lines):
        text = item.get("text", "").lower()
        if any(k in text for k in ["bill to", "buyer", "consignee"]):
            # कीवर्ड के बाद वाली 3 लाइनों में ढूंढें
            for offset in range(1, 4):
                if i + offset < len(lines):
                    name_candidate = lines[i+offset].get("text", "").strip()
                    # नाम में GSTIN या Date नहीं होनी चाहिए
                    if len(name_candidate) > 3 and not re.search(r"\d{2}[A-Z]{5}|\d{2}[/-]\d{2}", name_candidate):
                        buyer = name_candidate
                        break
            if buyer != "Not Found": break
            
    return buyer, supplier
