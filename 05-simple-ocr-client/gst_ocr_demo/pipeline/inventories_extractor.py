import re

def extract_inventories_advanced(blocks):
    inventory_rows = []
    lines = [b for b in blocks if b['BlockType'] == 'LINE']
    
    for line in lines:
        text = line.get("Text", "").strip()
        # अमाउंट ढूंढें
        nums = re.findall(r"\d+(?:,\d{3})*(?:\.\d{2})", text)
        
        if len(nums) >= 1:
            amount = nums[-1]
            # डिस्क्रिप्शन: लाइन की शुरुआत से लेकर पहले नंबर के पहले तक
            # उदाहरण: "Amul Milk 500ml 2 30.00 60.00" -> "Amul Milk 500ml"
            description = re.split(r'\d', text, 1)[0].strip()
            
            if len(description) < 2: 
                continue # फालतू लाइनों को छोड़ दें

            inventory_rows.append({
                "item": description,
                "qty": nums[-3] if len(nums) >= 3 else "1",
                "rate": nums[-2] if len(nums) >= 2 else amount,
                "tax_rate": "18%",
                "tax_amount": "{:.2f}".format(float(amount.replace(",","")) * 0.18),
                "amount": amount
            })
    return inventory_rows

