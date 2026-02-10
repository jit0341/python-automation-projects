def extract_names(lines):
    buyer, supplier = "Not Found", "Not Found"
    noise = ["invoice", "tax", "gst", "date", "original", "bill to", "buyer", "consignee", "ship to"]

    # Supplier: टॉप 7 लाइनों में पहला गैर-नॉइज़ टेक्स्ट
    for l in lines[:7]:
        t = l.get('text', "").strip()
        if len(t) > 3 and not any(n in t.lower() for n in noise):
            supplier = t
            break

    # Buyer: "Bill To" या "Consignee" कीवर्ड मिलने के बाद वाली लाइन
    for i, l in enumerate(lines):
        t_low = l.get('text', "").lower()
        if any(k in t_low for k in ["bill to", "buyer", "consignee", "party"]):
            for next_l in lines[i+1 : i+5]: # अगली 5 लाइनों तक चेक करें
                txt = next_l.get('text', "").strip()
                if len(txt) > 3 and not any(n in txt.lower() for n in noise):
                    buyer = txt
                    break
            if buyer != "Not Found": break
    return buyer, supplier
