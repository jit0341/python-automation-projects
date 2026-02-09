import re

def extract_names(lines_with_geo):
    buyer, supplier = "Not Found", "Not Found"
    # सख्त फिल्टर लिस्ट
    noise_keywords = ["invoice", "tax", "original", "copy", "date", "dated", "no:", "num", "gstin"]

    # Supplier: टॉप 10% एरिया में
    for line in lines_with_geo[:7]:
        t = line['text'].strip()
        if len(t) > 3 and not any(k in t.lower() for k in noise_keywords) and not re.search(r"\d{2}[A-Z]{5}", t.upper()):
            supplier = t
            break

    # Buyer: "Bill to" के नीचे 1-3 लाइन के भीतर
    for i, line in enumerate(lines_with_geo):
        if "bill to" in line['text'].lower() or "buyer" in line['text'].lower():
            l_box = line['geometry']['BoundingBox']
            for next_line in lines_with_geo[i+1:i+5]:
                n_box = next_line['geometry']['BoundingBox']
                # एलाइनमेंट चेक (Left margin < 5% का अंतर)
                if abs(n_box['Left'] - l_box['Left']) < 0.05:
                    candidate = next_line['text'].strip()
                    if len(candidate) > 2 and not any(k in candidate.lower() for k in noise_keywords):
                        buyer = candidate
                        break
            if buyer != "Not Found": break
            
    return buyer, supplier
