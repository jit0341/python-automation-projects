import re

def extract_inventories_advanced(blocks):
    inventory_rows = []
    # सिर्फ उन ब्लॉक्स को लें जिनमें टेक्स्ट है
    lines = [b for b in blocks if b['BlockType'] == 'LINE']
    
    # 1. टेबल का एरिया पहचानें (Description से Total के बीच)
    table_started = False
    for i, line in enumerate(lines):
        text = line.get("Text", "").lower()
        
        # अगर अमाउंट और रेट वाले कीवर्ड्स दिखें तो टेबल शुरू
        if any(k in text for k in ["qty", "rate", "amount", "description"]):
            table_started = True
            continue
            
        if table_started:
            # अगर 'Total' या 'GST' आ जाए तो टेबल खत्म
            if any(k in text for k in ["total", "subtotal", "gst payable"]):
                break
                
            # Regex: अमाउंट या संख्या ढूंढें
            nums = re.findall(r"\d+(?:,\d{3})*(?:\.\d{2})?", text)
            
            if len(nums) >= 1:
                # डिस्क्रिप्शन: लाइन का शुरुआती हिस्सा
                desc = re.split(r'\d', line.get("Text", ""), 1)[0].strip()
                
                # अगर डिस्क्रिप्शन बहुत छोटा है, तो शायद यह टेबल की हेडर लाइन है
                if len(desc) < 2: continue 

                inventory_rows.append({
                    "item": desc,
                    "qty": nums[-3] if len(nums) >= 3 else "1",
                    "rate": nums[-2] if len(nums) >= 2 else nums[-1],
                    "tax_rate": "18%",
                    "tax_amount": "{:.2f}".format(float(nums[-1].replace(",","")) * 0.18) if nums else "0.00",
                    "amount": nums[-1]
                })

    return inventory_rows
