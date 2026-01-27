import os
import re
import boto3
import pandas as pd
from pathlib import Path
from datetime import datetime

# ================= CONFIG =================
INPUT_DIR = "input"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# AWS credentials ENV se aayenge
textract = boto3.client("textract")

# ================= TEXTRACT HELPERS =================

def analyze_document_bytes(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()

    response = textract.analyze_document(
        Document={"Bytes": bytes_data},
        FeatureTypes=["TABLES", "FORMS"]
    )
    return response["Blocks"]


def build_block_maps(blocks):
    block_map = {}
    for b in blocks:
        block_map[b["Id"]] = b
    return block_map


# --------- KEY VALUE EXTRACTION ----------
def extract_kv(blocks):
    keys = {}
    values = {}
    kvs = {}

    for block in blocks:
        if block["BlockType"] == "KEY_VALUE_SET":
            if "KEY" in block.get("EntityTypes", []):
                keys[block["Id"]] = block
            else:
                values[block["Id"]] = block

    for k_id, k_block in keys.items():
        key_text = ""
        val_text = ""

        for rel in k_block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for cid in rel["Ids"]:
                    key_text += block_text(blocks, cid)

            if rel["Type"] == "VALUE":
                for vid in rel["Ids"]:
                    v_block = values.get(vid)
                    if not v_block:
                        continue
                    for vrel in v_block.get("Relationships", []):
                        if vrel["Type"] == "CHILD":
                            for vcid in vrel["Ids"]:
                                val_text += block_text(blocks, vcid)

        if key_text:
            kvs[key_text.strip()] = val_text.strip()

    return kvs


def block_text(blocks, block_id):
    for b in blocks:
        if b["Id"] == block_id and b["BlockType"] == "WORD":
            return b["Text"] + " "
    return ""


# --------- TABLE EXTRACTION ----------
def extract_tables(blocks):
    block_map = build_block_maps(blocks)
    tables = []

    for block in blocks:
        if block["BlockType"] == "TABLE":
            table = {}

            for rel in block.get("Relationships", []):
                if rel["Type"] == "CHILD":
                    for cid in rel["Ids"]:
                        cell = block_map[cid]
                        if cell["BlockType"] == "CELL":
                            row = cell["RowIndex"]
                            col = cell["ColumnIndex"]

                            text = ""
                            for crel in cell.get("Relationships", []):
                                if crel["Type"] == "CHILD":
                                    for wid in crel["Ids"]:
                                        text += block_text(blocks, wid)

                            table.setdefault(row, {})[col] = text.strip()

            tables.append(table)

    return tables


# ================= MAIN =================
def main():
    invoices = []
    missing = []
    sales = []
    inventory = []

    files = list(Path(INPUT_DIR).glob("*.pdf"))
    if not files:
        print("❌ No PDF files found in input folder")
        return

    for f in files:
        print(f"Processing: {f.name}")

    for f in files:
        invoices.append(data)

    return invoices


    for f in Path(INPUT_DIR).glob("*.*"):
        if f.suffix.lower() not in [".pdf", ".jpg", ".jpeg", ".png"]:
            continue

        print(f"Processing: {f.name}")
        blocks = analyze_document_bytes(f)

        kv = extract_kv(blocks)
        tables = extract_tables(blocks)

        # -------- BASIC FIELDS --------
        invoice_no = kv.get("Invoice No", kv.get("Invoice Number", "NOT FOUND"))
        invoice_date = kv.get("Date", "NOT FOUND")
        buyer_name = kv.get("Billed to", "MOBILE SOLUTION")
        buyer_gstin = kv.get("GSTIN/UIN", "NOT FOUND")
        supplier_name = "NEW ANURAG MOBILE"

        total_amount = 0.0
        for k, v in kv.items():
            if "Total" in k:
                v = re.sub(r"[^\d.]", "", v)
                if v:
                    clean_v = re.sub(r"[^0-9.]", "", v)
                    total_amount = float(clean_v) if clean_v else 0.0

invoices.append({
            "invoice_no": invoice_no,
            "invoice_date": invoice_date,
            "supplier_name": supplier_name,
            "buyer_name": buyer_name,
            "buyer_gstin": buyer_gstin,
            "total_amount": total_amount,
            "file": f.name
        })

        # -------- MISSING --------
miss = []
for k in ["invoice_no", "invoice_date", "buyer_gstin", "total_amount"]:
    if locals().get(k) in ["NOT FOUND", 0, 0.0]:
        miss.append(k)

        missing.append({
            "file": f.name,
            "missing_fields": ", ".join(miss)
        })

        # -------- TALLY SALES --------
        sales.append({
            "VoucherType": "Sales",
            "Date": invoice_date,
            "PartyName": buyer_name,
            "PartyGSTIN": buyer_gstin,
            "RefNo": invoice_no,
            "Amount": total_amount,
            "Narration": f"AUTO OCR | {f.name}"
        })

        # -------- INVENTORY (TABLES) --------
        for table in tables:
            for row_idx, cols in table.items():
                if row_idx == 1:
                    continue  # header skip

                inventory.append({
                    "PartyName": buyer_name,
                    "InvoiceNo": invoice_no,
                    "StockItem": cols.get(2, ""),
                    "HSN": cols.get(3, ""),
                    "Qty": cols.get(5, ""),
                    "Rate": cols.get(6, ""),
                    "Amount": cols.get(10, "")
                })

    # ================= SAVE EXCEL =================
    out_file = os.path.join(
        OUTPUT_DIR,
        f"PHASE3_MOBILE_WOW_{datetime.now().strftime('%H%M')}.xlsx"
    )

    with pd.ExcelWriter(out_file, engine="xlsxwriter") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(missing).to_excel(w, "Missing_Fields", index=False)
        pd.DataFrame(sales).to_excel(w, "Tally_Sales", index=False)
        pd.DataFrame(inventory).to_excel(w, "Tally_Inventory", index=False)

    print("✅ WOW DONE:", out_file)


if __name__ == "__main__":
    main()
