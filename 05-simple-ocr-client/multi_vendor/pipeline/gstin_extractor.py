import re

def extract_gstins(lines):
    gst_re = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]\b"
    found = []
    for l in lines:
        m = re.search(gst_re, l.get('text', "").upper())
        if m:
            found.append({
                "gst": m.group(0),
                "top": l.get('geometry', {}).get('BoundingBox', {}).get('Top', 0)
            })

    res = {"supplier_gstin": "Not Found", "buyer_gstin": "Not Found"}
    if found:
        # ऊपर वाला GST सप्लायर का, नीचे वाला बायर का
        found = sorted(found, key=lambda x: x['top'])
        res["supplier_gstin"] = found[0]["gst"]
        if len(found) > 1:
            res["buyer_gstin"] = found[-1]["gst"]
    return res
