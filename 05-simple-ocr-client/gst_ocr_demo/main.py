import os
import json
from datetime import datetime

# --- Pipeline folder से सही Imports ---
from pipeline.invoice_number_extractor import extract_invoice_number
from pipeline.total_amount_extractor import extract_total_amount
from pipeline.invoice_date_extractor import extract_invoice_date
from pipeline.gstin_extractor import extract_gstins
from pipeline.name_extractor import extract_names
from pipeline.inventories_extractor import extract_inventories_advanced
from pipeline.excel_writer import write_to_excel

# --- CONFIG (As per your directory structure) ---
TEXTRACT_DIR = "textract_json" 
OUTPUT_DIR = "outputs"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def extract_kv_pairs(blocks):
    """AWS Textract के ब्लॉक्स से Key-Value जोड़े (Forms) निकालना"""
    kvs = {}
    key_map = {}
    value_map = {}
    block_map = {b['Id']: b for b in blocks}

    # पहले Keys और Values को मैप करें
    for block in blocks:
        if block['BlockType'] == "KEY_VALUE_SET":
            if 'Relationships' in block:
                if 'KEY' in block['EntityTypes']:
                    key_id = [r['Ids'] for r in block['Relationships'] if r['Type'] == 'CHILD'][0]
                    key_text = " ".join([block_map[i]['Text'] for i in key_id if i in block_map]).lower()
                    
                    # Value ID ढूँढें
                    val_ids = [r['Ids'] for r in block['Relationships'] if r['Type'] == 'VALUE']
                    if val_ids:
                        kvs[key_text] = val_ids[0]
    
    # Value IDs को टेक्स्ट में बदलें
    final_kvs = {}
    for k, v_ids in kvs.items():
        v_text = ""
        for v_id in v_ids:
            if v_id in block_map and 'Relationships' in block_map[v_id]:
                child_ids = [r['Ids'] for r in block_map[v_id]['Relationships'] if r['Type'] == 'CHILD'][0]
                v_text += " ".join([block_map[i]['Text'] for i in child_ids if i in block_map]) + " "
        final_kvs[k.strip(": ")] = v_text.strip()
    return final_kvs

def process_invoice(json_path):
    """एक सिंगल इनवॉइस को प्रोसेस करना"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    blocks = data.get("Blocks", [])
    file_name = os.path.basename(json_path)
    
    # 1. Key-Value pairs निकालें (Forms extraction)
    kv_data = extract_kv_pairs(blocks)
    
    # 2. LINE ब्लॉक्स निकालें (Regex extractors के लिए)
    lines = [{"text": b.get("Text", ""), "confidence": b.get("Confidence", 0)} 
             for b in blocks if b.get("BlockType") == "LINE"]
    
    # --- DATA EXTRACTION LOGIC ---
    
    # Invoice Number (पहले KV, फिर Regex)
    inv_no = kv_data.get("invoice no", kv_data.get("inv no", kv_data.get("invoice number", "Not Found")))
    if inv_no == "Not Found" or len(inv_no) < 3:
        inv_no = extract_invoice_number(lines).get("invoice_no")
        
    # Invoice Date
    inv_date = kv_data.get("date", kv_data.get("invoice date", kv_data.get("dated", "Not Found")))
    if inv_date == "Not Found":
        inv_date = extract_invoice_date(lines).get("invoice_date")
        
    # GSTINs (Supplier and Buyer)
    gst = extract_gstins(lines)
    
    # Buyer Name (पहले 'Bill To' KV से, फिर Name Extractor से)
    buyer_name = kv_data.get("bill to", kv_data.get("buyer name", kv_data.get("consignee", "Not Found")))
    names = extract_names(lines)
    if buyer_name == "Not Found":
        buyer_name = names[0] # Extractor से Buyer Name
    
    supplier_name = names[1] # Extractor से Supplier Name
    
    # Total Amount
    total_res = extract_total_amount(lines)
    total_amt = total_res.get("total_amount")
    
    # Inventories (Advanced table logic)
    items = extract_inventories_advanced(blocks)

    return {
        "file": file_name,
        "invoice_no": inv_no,
        "invoice_date": inv_date,
        "supplier_name": supplier_name,
        "supplier_gstin": gst.get("supplier_gstin"),
        "buyer_name": buyer_name,
        "buyer_gstin": gst.get("buyer_gstin"),
        "total_amount": total_amt,
        "inventories": items
    }

if __name__ == "__main__":
    if os.path.exists(TEXTRACT_DIR):
        files = [f for f in os.listdir(TEXTRACT_DIR) if f.endswith(".json")]
        if not files:
            print(f"⚠️ No JSON files found in '{TEXTRACT_DIR}'")
        else:
            all_results = []
            for f in files:
                print(f"🔍 Processing: {f}")
                try:
                    res = process_invoice(os.path.join(TEXTRACT_DIR, f))
                    all_results.append(res)
                except Exception as e:
                    print(f"❌ Error processing {f}: {e}")
            
            if all_results:
                timestamp = datetime.now().strftime('%d%m%Y_%H%M')
                output_path = os.path.join(OUTPUT_DIR, f"Final_Professional_Report_{timestamp}.xlsx")
                write_to_excel(all_results, output_path)
                print(f"\n✅ Success! Professional Excel created: {output_path}")
    else:
        print(f"❌ Error: Folder '{TEXTRACT_DIR}' not found.")
