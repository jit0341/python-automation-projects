import os
import re
import boto3
import pandas as pd
from pathlib import Path
from datetime import datetime

# ===== ADD THIS FUNCTION HERE =====
def safe_float(value):
    if not value:
        return 0.0

    clean = re.sub(r"[^0-9.]", "", value)

    # अगर multiple dots हैं (OCR issue)
    if clean.count(".") > 1:
        parts = clean.split(".")
        clean = "".join(parts[:-1]) + "." + parts[-1]

    try:
        return float(clean)
    except:
        return 0.0
# ================= CONFIG =================
INPUT_DIR = "input"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

textract = boto3.client("textract")

# ================= TEXTRACT =================

def analyze_document_bytes(file_path):
    with open(file_path, "rb") as f:
        data = f.read()

    response = textract.analyze_document(
        Document={"Bytes": data},
        FeatureTypes=["FORMS", "TABLES"]
    )
    return response["Blocks"]


def block_text(blocks, block_id):
    for b in blocks:
        if b["Id"] == block_id and b["BlockType"] == "WORD":
            return b["Text"] + " "
    return ""


# ================= KEY VALUE =================

def extract_kv(blocks):
    keys, values, kvs = {}, {}, {}

    for b in blocks:
        if b["BlockType"] == "KEY_VALUE_SET":
            if "KEY" in b.get("EntityTypes", []):
                keys[b["Id"]] = b
            else:
                values[b["Id"]] = b

    for k_id, k_block in keys.items():
        key, val = "", ""

        for rel in k_block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for cid in rel["Ids"]:
                    key += block_text(blocks, cid)

            if rel["Type"] == "VALUE":
                for vid in rel["Ids"]:
                    v_block = values.get(vid)
                    if not v_block:
                        continue
                    for vrel in v_block.get("Relationships", []):
                        if vrel["Type"] == "CHILD":
                            for vcid in vrel["Ids"]:
                                val += block_text(blocks, vcid)

        if key.strip():
            kvs[key.strip()] = val.strip()

    return kvs


# ================= TABLES =================

def extract_tables(blocks):
    block_map = {b["Id"]: b for b in blocks}
    tables = []

    for b in blocks:
        if b["BlockType"] == "TABLE":
            table = {}

            for rel in b.get("Relationships", []):
                if rel["Type"] == "CHILD":
                    for cid in rel["Ids"]:
                        cell = block_map[cid]
                        if cell["BlockType"] == "CELL":
                            r, c = cell["RowIndex"], cell["ColumnIndex"]
                            text = ""
                            for crel in cell.get("Relationships", []):
                                if crel["Type"] == "CHILD":
                                    for wid in crel["Ids"]:
                                        text += block_text(blocks, wid)
                            table.setdefault(r, {})[c] = text.strip()

            tables.append(table)

    return tables


# ================= MAIN =================

def main():
    invoices, missing, sales, inventory = [], [], [], []

    files = list(Path(INPUT_DIR).glob("*.pdf"))
    if not files:
        print("❌ No PDF files found")
        return

    for f in files:
        print(f"Processing: {f.name}")
        blocks = analyze_document_bytes(f)

        kv = extract_kv(blocks)
        tables = extract_tables(blocks)

        invoice_no = kv.get("Invoice No", kv.get("Invoice Number", "NOT FOUND"))
        invoice_date = kv.get("Date", "NOT FOUND")
        buyer_name = kv.get("Billed to", "MOBILE SOLUTION")
        buyer_gstin = kv.get("GSTIN/UIN", "NOT FOUND")
        supplier_name = "NEW ANURAG MOBILE"

        total_amount = 0.0
        for k, v in kv.items():
            if "Total" in k:
                total_amount = safe_float(v)
        invoices.append({
            "invoice_no": invoice_no,
            "invoice_date": invoice_date,
            "supplier_name": supplier_name,
            "buyer_name": buyer_name,
            "buyer_gstin": buyer_gstin,
            "total_amount": total_amount,
            "file": f.name
        })

        miss = []
        for fld, val in {
            "invoice_no": invoice_no,
            "invoice_date": invoice_date,
            "buyer_gstin": buyer_gstin,
            "total_amount": total_amount
        }.items():
            if val in ["NOT FOUND", 0, 0.0]:
                miss.append(fld)

        if miss:
            missing.append({"file": f.name, "missing_fields": ", ".join(miss)})

        sales.append({
            "VoucherType": "Sales",
            "Date": invoice_date,
            "PartyName": buyer_name,
            "PartyGSTIN": buyer_gstin,
            "RefNo": invoice_no,
            "Amount": total_amount,
            "Narration": f"AUTO OCR | {f.name}"
        })

        for table in tables:
            for r, cols in table.items():
                if r == 1:
                    continue
                inventory.append({
                    "PartyName": buyer_name,
                    "InvoiceNo": invoice_no,
                    "StockItem": cols.get(2, ""),
                    "HSN": cols.get(3, ""),
                    "Qty": cols.get(5, ""),
                    "Rate": cols.get(6, ""),
                    "Amount": cols.get(10, "")
                })

    out = os.path.join(
        OUTPUT_DIR,
        f"PHASE3_MOBILE_WOW_{datetime.now().strftime('%H%M')}.xlsx"
    )

    with pd.ExcelWriter(out, engine="xlsxwriter") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(missing).to_excel(w, "Missing_Fields", index=False)
        pd.DataFrame(sales).to_excel(w, "Tally_Sales", index=False)
        pd.DataFrame(inventory).to_excel(w, "Tally_Inventory", index=False)

    print("✅ WOW DONE:", out)


if __name__ == "__main__":
    main()
