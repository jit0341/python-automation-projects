import os, json, sys
from config import MODE, get_mode_config
CFG = get_mode_config()
from pipeline.invoice_number_extractor import extract_invoice_number
from pipeline.invoice_date_extractor import extract_invoice_date
from pipeline.gstin_extractor import extract_gstins
from pipeline.name_extractor import extract_names
from pipeline.total_amount_extractor import extract_total_amount
from pipeline.inventories_extractor import extract_inventories_advanced
from pipeline.excel_writer import write_excel
from pipeline.buyer_gstin_extractor import extract_buyer_gstin

def process_invoice(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        blocks = json.load(f).get("Blocks", [])
    
    file_name = os.path.basename(json_file)
    
    # यहाँ वेरिएबल का नाम 'lines' रखें ताकि extract_names(lines) काम करे
    lines = [{"text": b.get("Text", ""), "geometry": b.get("Geometry", {})} 
             for b in blocks if b.get("BlockType") == "LINE"]

    # Extraction Calls
    inv_no = extract_invoice_number(lines).get("invoice_no", "N/A")
    inv_date = extract_invoice_date(lines).get("invoice_date", "N/A")
    gst_info = extract_gstins(lines)
    supplier_gstin = gst_info.get("supplier_gstin")

    buyer_gstin_info = extract_buyer_gstin(
    lines,
    supplier_gstin=supplier_gstin
)

    buyer_gstin = buyer_gstin_info["buyer_gstin"]
    buyer_gstin_conf = buyer_gstin_info["confidence"]
    
    # Error Fix: अब 'lines' यहाँ परिभाषित है
    buyer_name, supplier_name = extract_names(lines)
    
    total_val = extract_total_amount(lines).get("total_amount", 0)
    items = extract_inventories_advanced(blocks)
    #Fallback Logic: यदि सीधा टोटल नहीं मिला, तो आइटम अमाउंट्स को जोड़ें
    total_extracted = extract_total_amount(lines).get("total_amount", 0)
    calculated_total = sum(float(str(i.get("amount", 0)).replace(',', '')) for i in items)
    final_total = total_extracted if total_extracted > 0 else calculated_total

    result = {
        "file": file_name,
        "invoice_no": inv_no,
        "invoice_date": inv_date,      
        "supplier_name": supplier_name,
        "buyer_name": buyer_name,
        "supplier_gstin": gst_info.get("supplier_gstin", "N/A"),
        "buyer_gstin": buyer_gstin,
        "buyer_gstin_conf": buyer_gstin_conf,
        "total_amount": final_total,
        "inventories": items
    }
    
    dbg = []
    if inv_no == "N/A":
        dbg.append({"file": file_name, "field": "Invoice No", "value": "Missing"})
    
    return result, dbg



def run_elite_run():
    print(f"🚀 Started ELITE Run...")
    results, all_debug = [], []
    input_dir = "textract_json"
    
    if not os.path.exists(input_dir):
        print(f"❌ Error: {input_dir} folder not found")
        return

    files = [f for f in os.listdir(input_dir)     if f.endswith(".json")]
    limit = CFG.get("limit")
    if limit:
        files = files[:limit]
        
    for f in files:
        print(f"⚙️ Processing: {f}", end="\r")
        try:
            res, dbg = process_invoice(os.path.join(input_dir, f))
            results.append(res)
            all_debug.extend(dbg)
        except Exception as e:
            print(f"\n❌ Error in {f}: {e}")

    output = write_excel(results, all_debug,MODE, CFG)
    print(f"\n🎊 Project Complete! Final Report: {output}")
    

if __name__ == "__main__":
    if MODE == "ELITE":
        run_elite_run()
    else:
        print(f"⚠ MODE {MODE} selected, but elite runner active.")
        run_elite_run()
