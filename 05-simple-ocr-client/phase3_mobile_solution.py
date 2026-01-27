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

textract = boto3.client("textract")

# ================= HELPERS =================

def normalize_number(val):
    if not val:
        return 0.0
    val = re.sub(r"[^\d.]", "", str(val))
    try:
        return float(val)
    except:
        return 0.0


def block_text(blocks, block_id):
    for b in blocks:
        if b["Id"] == block_id and b["BlockType"] == "WORD":
            return b["Text"] + " "
    return ""


def analyze_document_bytes(file_path):
    with open(file_path, "rb") as f:
        data = f.read()

    res = textract.analyze_document(
        Document={"Bytes": data},
        FeatureTypes=["TABLES", "FORMS"]
    )
    return res["Blocks"]


# ================= KV EXTRACTION =================

def extract_kv(blocks):
    keys, values, kvs = {}, {}, {}

    for b in blocks:
        if b["BlockType"] == "KEY_VALUE_SET":
            if "KEY" in b.get("EntityTypes", []):
                keys[b["Id"]] = b
            else:
                values[b["Id"]] = b

    for k_id, k_block in keys.items():
        key_text, val_text = "", ""

        for rel in k_block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for cid in rel["Ids"]:
                    key_text += block_text(blocks, cid)

            if rel["Type"] == "VALUE":
                for vid in rel["Ids"]:
                    v_block = values.get(vid)
                    if not v_block:
                        continue
                    for vr in v_block.get("Relationships", []):
                        if vr["Type"] == "CHILD":
                            for vc in vr["Ids"]:
                                val_text += block_text(blocks, vc)

        if key_text:
            kvs[key_text.strip()] = val_text.strip()

    return kvs


# ================= TABLE EXTRACTION =================

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
                            row, col = cell["RowIndex"], cell["ColumnIndex"]
                            text = ""
                            for cr in cell.get("Relationships", []):
                                if cr["Type"] == "CHILD":
                                    for wid in cr["Ids"]:
                                        text += block_text(blocks, wid)
                            table.setdefault(row, {})[col] = text.strip()
            tables.append(table)

    return tables


# ================= INVENTORY RULE (VENDOR LOCK) =================

def is_inventory_row(cols):
    hsn = cols.get(2, "")
    qty = cols.get(4, "")
    unit = cols.get(5, "").lower()

    return (
        hsn.isdigit()
        and len(hsn) >= 6
        and qty.replace(".", "").isdigit()
        and ("pcs" in unit or "nos" in unit)
    )


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

        # -------- BASIC --------
        invoice_no = kv.get("Invoice No", "NOT FOUND")
        invoice_date = kv.get("Dated", "NOT FOUND")
        buyer_name = kv.get("Billed to", "MOBILE SOLUTION")
        buyer_gstin = kv.get("GSTIN / UIN", "NOT FOUND")
        supplier_name = "NEW ANURAG MOBILE"

        # -------- TAX --------
        taxable, cgst, sgst, grand_total = 0, 0, 0, 0
        gst_rate = 0

        for k, v in kv.items():
            kl = k.lower()
            if "taxable" in kl:
                taxable = normalize_number(v)
            elif "cgst amount" in kl:
                cgst = normalize_number(v)
            elif "sgst amount" in kl:
                sgst = normalize_number(v)
            elif "grand total" in kl:
                grand_total = normalize_number(v)
            elif "cgst rate" in kl:
                gst_rate = int(normalize_number(v) * 2)

        total_amount = grand_total

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
        for fld, val in {
            "invoice_no": invoice_no,
            "invoice_date": invoice_date,
            "buyer_gstin": buyer_gstin,
            "total_amount": total_amount
        }.items():
            if val in ["NOT FOUND", 0, 0.0]:
                miss.append(fld)

        if miss:
            missing.append({
                "file": f.name,
                "missing_fields": ", ".join(miss),
                "invoice_link": f.name
            })

        # -------- SALES --------
        sales.append({
            "VoucherType": "Sales",
            "Date": invoice_date,
            "PartyName": buyer_name,
            "PartyGSTIN": buyer_gstin,
            "RefNo": invoice_no,
            "Amount": total_amount,
            "GST_Rate": gst_rate,
            "Taxable": taxable,
            "CGST": cgst,
            "SGST": sgst,
            "Narration": f"AUTO OCR | {f.name}"
        })

        # -------- INVENTORY --------
        for table in tables:
            for row, cols in table.items():
                if row == 1:
                    continue
                if not is_inventory_row(cols):
                    continue

                qty = normalize_number(cols.get(4, "1"))
                amt = normalize_number(cols.get(10, ""))
                rate = round(amt / qty, 2) if qty else 0

                inventory.append({
                    "PartyName": buyer_name,
                    "InvoiceNo": invoice_no,
                    "StockItem": cols.get(1, ""),
                    "HSN": cols.get(2, ""),
                    "Qty": qty,
                    "UOM": "Pcs",
                    "Rate": rate,
                    "Amount": amt
                })

    # ================= SAVE =================
    out_file = os.path.join(
        OUTPUT_DIR,
        f"PHASE3_VENDOR_LOCKED_{datetime.now().strftime('%H%M')}.xlsx"
    )

    with pd.ExcelWriter(out_file, engine="xlsxwriter") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(missing).to_excel(w, "Missing_Fields", index=False)
        pd.DataFrame(sales).to_excel(w, "Tally_Sales", index=False)
        pd.DataFrame(inventory).to_excel(w, "Tally_Inventory", index=False)

    print("✅ WOW DONE:", out_file)


if __name__ == "__main__":
    main()
