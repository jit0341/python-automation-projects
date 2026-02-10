import re

def extract_inventories_advanced(blocks):
    inventory_rows = []
    lines = [b for b in blocks if b.get("BlockType") == "LINE"]
    
    rows = {}
    for b in lines:
        t = b['Geometry']['BoundingBox']['Top']
        found = False
        for k in rows.keys():
            if abs(k - t) < 0.012:
                rows[k].append(b)
                found = True
                break
        if not found: rows[t] = [b]

    table_started = False
    for t in sorted(rows.keys()):
        parts = sorted(rows[t], key=lambda x: x['Geometry']['BoundingBox']['Left'])
        row_text = " ".join([p.get('Text', '') for p in parts])
        low = row_text.lower()

        if any(k in low for k in ["description", "qty", "rate", "amount"]):
            table_started = True
            continue
        
        if table_started:
            if any(k in low for k in ["total", "bank", "gst", "amount in words"]): break
            
            # Description: बायीं तरफ का टेक्स्ट
            item_desc = " ".join([p['Text'] for p in parts if p['Geometry']['BoundingBox']['Left'] < 0.40])
            
            # Numbers: केवल 1-4 डिजिट के नंबर Qty हो सकते हैं (लंबी ID को छोड़ देगा)
            all_nums = re.findall(r"(\d+(?:,\d{3})*(?:\.\d{1,3})?)", row_text.replace('₹',''))
            
            if len(item_desc) > 3 and all_nums:
                # Qty: आमतौर पर पहला या दूसरा छोटा नंबर
                qty_val = "1"
                for n in all_nums:
                    if len(n.split('.')[0]) <= 4: # 4 डिजिट से छोटा नंबर ही Qty होगा
                        qty_val = n
                        break
                
                inventory_rows.append({
                    "item": item_desc.strip(),
                    "qty": qty_val,
                    "rate": all_nums[-2] if len(all_nums) >= 2 else "0.00",
                    "amount": all_nums[-1]
                })
    return inventory_rows
