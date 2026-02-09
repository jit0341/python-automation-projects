import re

def extract_gstins(lines_with_geo):
    gst_re = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]\b"
    all_found = []
    for i, line in enumerate(lines_with_geo):
        m = re.search(gst_re, line['text'].upper())
        if m:
            all_found.append({"gst": m.group(0), "top": line['geometry']['BoundingBox']['Top'], "text": line['text']})

    res = {"supplier_gstin": "Not Found", "buyer_gstin": "Not Found"}
    if all_found:
        # टॉप वाली सप्लायर, बॉटम वाली बायर
        sorted_gst = sorted(all_found, key=lambda x: x['top'])
        res["supplier_gstin"] = sorted_gst[0]["gst"]
        if len(sorted_gst) > 1:
            res["buyer_gstin"] = sorted_gst[-1]["gst"]
            
    return res
