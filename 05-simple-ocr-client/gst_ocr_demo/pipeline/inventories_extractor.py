import re

def extract_inventories_advanced(blocks):
    inventory_rows = []
    lines = [b for b in blocks if b['BlockType'] == 'LINE']
    if not lines: return []

    rows = {}
    for b in lines:
        t = b['Geometry']['BoundingBox']['Top']
        found = False
        for k in rows.keys():
            if abs(k - t) < 0.012: # थोड़ी टॉलरेंस बढ़ाई गई है
                rows[k].append(b)
                found = True
                break
        if not found: rows[t] = [b]

    table_started = False
    for t in sorted(rows.keys()):
        parts = sorted(rows[t], key=lambda x: x['Geometry']['BoundingBox']['Left'])
        row_text = " ".join([p['Text'] for p in parts])
        low = row_text.lower()

        # हेडर पहचानना
        if any(k in low for k in ["description", "qty", "rate", "amount"]):
            table_started = True
            continue
        
        if table_started:
            if any(k in low for k in ["total", "amount in words", "bank"]): break
            
            # कॉलम आधारित एक्सट्रैक्शन
            item_desc = " ".join([p['Text'] for p in parts if p['Geometry']['BoundingBox']['Left'] < 0.45])
            # नंबर्स को ढूंढें और क्लीन करें (करेंसी सिंबल हटाएं)
            nums = re.findall(r"(\d+(?:,\d{3})*(?:\.\d{2,3})?)", row_text.replace('₹', '').replace('Rs', ''))
            
            if len(item_desc) > 2 and len(nums) >= 1:
                inventory_rows.append({
                    "item": item_desc.strip(),
                    # अगर 3 नंबर हैं तो (Qty, Rate, Amount), 2 हैं तो (Rate, Amount), 1 है तो सिर्फ Amount
                    "qty": nums[0] if len(nums) >= 3 else "1",
                    "rate": nums[-2] if len(nums) >= 2 else nums[-1],
                    "tax_rate": "GST",
                    "tax_amount": "0.00", # इसे आप GST कैलकुलेशन से भर सकते हैं
                    "amount": nums[-1]
                })
    return inventory_rows
