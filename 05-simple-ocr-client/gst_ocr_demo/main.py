import os
import json
import sys

from pipeline.invoice_number_extractor import extract_invoice_number
from pipeline.invoice_date_extractor import extract_invoice_date
from pipeline.gstin_extractor import extract_gstins
from pipeline.total_amount_extractor import extract_total_amount
from pipeline.excel_writer import write_excel
from pipeline.inventories_extractor import extract_inventories
from pipeline.name_extractor import extract_names

#-----------AWS Credentials------------
def setup_aws_credentials():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    aws_dir = os.path.join(base_dir, "aws")

    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = os.path.join(aws_dir, "credentials")
    os.environ["AWS_CONFIG_FILE"] = os.path.join(aws_dir, "config")

setup_aws_credentials()

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
    buyer_name, supplier_name = extract_names(lines)
    inventories = extract_inventories(lines)

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
        "supplier_name": supplier_name,
        "buyer_name": buyer_name,
        "total_amount": total.get("total_amount"),
        "inventories": inventories,
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
