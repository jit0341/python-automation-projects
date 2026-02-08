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

# CONFIG
TEXTRACT_DIR = "textract_json" 
OUTPUT_DIR = "outputs"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def process_invoice(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    blocks = data.get("Blocks", [])
    lines = [{"text": b.get("Text", ""), "confidence": b.get("Confidence", 0)} 
             for b in blocks if b.get("BlockType") == "LINE"]
    
    file_name = os.path.basename(json_path)
    
    # एक्सट्रैक्शन लॉजिक
    inv_no = extract_invoice_number(lines)
    inv_date = extract_invoice_date(lines)
    gst = extract_gstins(lines)
    total = extract_total_amount(lines)
    buyer, supplier = extract_names(lines)
    items = extract_inventories_advanced(blocks)

    return {
        "file": file_name,
        "invoice_no": inv_no.get("invoice_no"),
        "invoice_date": inv_date.get("invoice_date"),
        "supplier_name": supplier,
        "buyer_name": buyer,
        "supplier_gstin": gst.get("supplier_gstin"),
        "buyer_gstin": gst.get("buyer_gstin"),
        "total_amount": total.get("total_amount"),
        "inventories": items
    }

if __name__ == "__main__":
    if os.path.exists(TEXTRACT_DIR):
        files = [f for f in os.listdir(TEXTRACT_DIR) if f.endswith(".json")]
        if not files:
            print(f"⚠️ No JSON files found in {TEXTRACT_DIR}")
        else:
            results = []
            for f in files:
                print(f"🔍 Processing: {f}")
                results.append(process_invoice(os.path.join(TEXTRACT_DIR, f)))
            
            output_path = os.path.join(OUTPUT_DIR, f"Final_GST_Report_{datetime.now().strftime('%d%m%Y_%H%M')}.xlsx")
            write_to_excel(results, output_path)
            print(f"\n✅ Success! Professional Excel created at: {output_path}")
    else:
        print(f"❌ Error: Folder '{TEXTRACT_DIR}' missing.")
