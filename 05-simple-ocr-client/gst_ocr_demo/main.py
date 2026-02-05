import os
import json

from pipeline.invoice_number_extractor import extract_invoice_number
from pipeline.invoice_date_extractor import extract_invoice_date
from pipeline.gstin_extractor import extract_gstins
from pipeline.total_amount_extractor import extract_total_amount
from pipeline.excel_writer import write_excel

# ---------------- CONFIG ----------------
TEXTRACT_DIR = "textract_json"
MODE = "PROD"   # PROD | DEMO
# ----------------------------------------

def load_lines_from_textract(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = []
    for block in data.get("Blocks", []):
        if block.get("BlockType") == "LINE":
            lines.append({
                "text": block.get("Text", ""),
                "confidence": block.get("Confidence", 0),
                "source": "line"
            })
    return lines


def process_single_invoice(json_path):
    file_name = os.path.basename(json_path)
    lines = load_lines_from_textract(json_path)

    inv_no = extract_invoice_number(lines)
    inv_date = extract_invoice_date(lines)
    gst = extract_gstins(lines)
    total = extract_total_amount(lines)

    debug_rows = []
    for section in [inv_no, total]:
        for d in section.get("debug", []):
            d["file"] = file_name
            debug_rows.append(d)

    return {
        "file": file_name,
        "invoice_no": inv_no.get("invoice_no"),
        "invoice_date": inv_date.get("invoice_date"),
        "supplier_gstin": gst.get("supplier_gstin"),
        "buyer_gstin": gst.get("buyer_gstin"),
        "total_amount": total.get("total_amount"),
        "status": final_status(inv_no, inv_date, gst, total),
        "score": max(
            inv_no.get("score", 0),
            total.get("score", 0)
        ),
        "debug": debug_rows
    }


def final_status(*sections):
    if any(s.get("status") == "EXCEPT" for s in sections):
        return "EXCEPT"
    if any(s.get("status") == "REVIEW" for s in sections):
        return "REVIEW"
    return "AUTO"


def run_all_invoices():
    results = []
    debug_all = []

    for f in os.listdir(TEXTRACT_DIR):
        if not f.endswith(".json"):
            continue

        print("Processing:", f)
        out = process_single_invoice(os.path.join(TEXTRACT_DIR, f))

        results.append(out)
        debug_all.extend(out.get("debug", []))

    return results, debug_all


if __name__ == "__main__":
    results, debug_rows = run_all_invoices()
    output_file = write_excel(results, debug_rows)
    print("✅ FINAL Excel generated:", output_file)
