import re

def extract_gstins(lines):
    gst_re = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]\b"
    gsteins_found = []

    for i, item in enumerate(lines):
        text = item.get("text", "").upper()
        match = re.search(gst_re, text)
        if match:
            gsteins_found.append({"gst": match.group(0), "index": i})

    res = {"supplier_gstin": "Not Found", "buyer_gstin": "Not Found"}

    if len(gsteins_found) >= 1:
        # जो सबसे पहले मिला वो Supplier
        res["supplier_gstin"] = gsteins_found[0]["gst"]
    
    if len(gsteins_found) >= 2:
        # जो बाद में मिला वो Buyer
        res["buyer_gstin"] = gsteins_found[1]["gst"]
    elif len(gsteins_found) == 1:
        # अगर सिर्फ एक ही मिला, तो चेक करें कि कहीं वो 'Bill To' के नीचे तो नहीं?
        idx = gsteins_found[0]["index"]
        context = " ".join([l.get("text", "").lower() for l in lines[max(0, idx-5):idx]])
        if any(k in context for k in ["bill to", "buyer", "consignee"]):
            res["buyer_gstin"] = gsteins_found[0]["gst"]
            res["supplier_gstin"] = "Not Found"

    return res
