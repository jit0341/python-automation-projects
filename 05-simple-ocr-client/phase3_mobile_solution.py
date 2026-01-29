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

GSTIN_REGEX = r"\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]"

# ================= TEXTRACT HELPERS =================

def analyze_document_bytes(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    res = textract.analyze_document(
        Document={"Bytes": data},
        FeatureTypes=["TABLES"]
    )
    return res["Blocks"]

def get_words(blocks):
    return [b for b in blocks if b["BlockType"] == "WORD"]

def line_groups(blocks, y_tol=0.01):
    lines = []
    words = get_words(blocks)

    for w in words:
        y = round(w["Geometry"]["BoundingBox"]["Top"], 3)
        placed = False
        for ln in lines:
            if abs(ln["y"] - y) <= y_tol:
                ln["words"].append(w)
                placed = True
                break
        if not placed:
            lines.append({"y": y, "words": [w]})

    for ln in lines:
        ln["words"].sort(key=lambda x: x["Geometry"]["BoundingBox"]["Left"])
        ln["text"] = " ".join(w["Text"] for w in ln["words"])

    return sorted(lines, key=lambda x: x["y"])

# ================= HEADER EXTRACTION =================

def extract_invoice_no(lines):
    BLOCK = ["ROAD", "NAGAR", "AMBIKAPUR", "CG", "GSTIN"]
    for ln in lines[:20]:
        t = ln["text"].strip()
        if any(x in t.upper() for x in ["INVOICE", "SALES"]):
            if any(ch.isdigit() for ch in t):
                if not any(b in t.upper() for b in BLOCK):
                    return t
    return "NOT FOUND"

def extract_invoice_date(lines):
    for ln in lines[:25]:
        m = re.search(r"\d{2}-\d{2}-\d{4}", ln["text"])
        if m:
            return m.group()
    return "NOT FOUND"

def extract_supplier_gstin(lines):
    for ln in lines:
        m = re.search(GSTIN_REGEX, ln["text"])
        if m:
            return m.group()
    return "NOT FOUND"
def extract_buyer_gstin(lines):
    for ln in lines:
        txt = ln["text"].upper()
        if any(k in txt for k in ["BUYER", "BILL TO", "SHIP TO"]):
            m = re.search(GSTIN_REGEX, txt)
            if m:
                return m.group()
    return ""

def extract_grand_total(lines):
    candidates = []
    for ln in lines:
        nums = re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d{2})", ln["text"])
        for n in nums:
            val = float(n.replace(",", ""))
            if val > 1000:
                candidates.append(val)
    return max(candidates) if candidates else 0.0

# ================= TABLE EXTRACTION =================

def extract_tables(blocks):
    block_map = {b["Id"]: b for b in blocks}
    tables = []

    for b in blocks:
        if b["BlockType"] == "TABLE":
            rows = {}
            for r in b.get("Relationships", []):
                if r["Type"] == "CHILD":
                    for cid in r["Ids"]:
                        cell = block_map[cid]
                        if cell["BlockType"] == "CELL":
                            row = cell["RowIndex"]
                            col = cell["ColumnIndex"]
                            txt = ""
                            for cr in cell.get("Relationships", []):
                                if cr["Type"] == "CHILD":
                                    for wid in cr["Ids"]:
                                        if block_map[wid]["BlockType"] == "WORD":
                                            txt += block_map[wid]["Text"] + " "
                            rows.setdefault(row, {})[col] = txt.strip()
            tables.append(rows)
    return tables

def is_summary_row(text):
    BAD = ["TOTAL", "TAXABLE", "CGST", "SGST", "AMOUNT"]
    return any(b in text.upper() for b in BAD)

# ================= MAIN =================

def main():
    invoices = []
    missing = []
    sales = []
    inventory = []

    files = list(Path(INPUT_DIR).glob("*.pdf"))
    if not files:
        print("No PDFs found")
        return

    for f in files:
        print("Processing:", f.name)

        blocks = analyze_document_bytes(f)
        lines = line_groups(blocks)
        tables = extract_tables(blocks)

        invoice_no = extract_invoice_no(lines)
        invoice_date = extract_invoice_date(lines)
        supplier_gstin = extract_supplier_gstin(lines)
        buyer_gstin = extract_buyer_gstin(lines)       
        total_amount = extract_grand_total(lines)

        invoices.append({
            "invoice_no": invoice_no,
            "invoice_date": invoice_date,
            "supplier_name": "NEW ANURAG MOBILE",
            "supplier_gstin": supplier_gstin,
            "buyer_name": "MOBILE",
            "buyer_gstin": buyer_gstin,       
            "buyer_gstin": "",
            "total_amount": total_amount,
            "file": f.name
        })

        for fld, val in {
            "invoice_no": invoice_no,
            "invoice_date": invoice_date,
            "total_amount": total_amount
        }.items():
            if val in ["NOT FOUND", 0, 0.0]:
                missing.append({
                    "file": f.name,
                    "missing_field": fld,
                    "invoice_link": f.name
                })

        sales.append({
            "VoucherType": "Sales",
            "Date": invoice_date,
            "PartyName": "MOBILE",
            "PartyGSTIN": "",
            "RefNo": invoice_no,
            "Amount": total_amount,
            "Narration": f"AUTO OCR | {f.name}"
        })

        for table in tables:
            for r, cols in table.items():
                text = " ".join(cols.values())
                if is_summary_row(text):
                    continue

                item = cols.get(2, "")
                if not item:
                    continue

                inventory.append({
                    "InvoiceNo": invoice_no,
                    "PartyName": "MOBILE",
                    "ItemName": item,
                    "HSN": cols.get(3, ""),
                    "Qty": cols.get(5, ""),
                    "UOM": cols.get(6, ""),
                    "CGST_Rate": cols.get(7, ""),
                    "SGST_Rate": cols.get(8, ""),
                    "SGST_Amt": cols.get(9, ""),
                    "Amount": ""   # intentionally blank (safe)
                })

    out = os.path.join(
        OUTPUT_DIR,
        f"GST_OCR_VENDOR_LOCK_{datetime.now().strftime('%H%M')}.xlsx"
    )

    with pd.ExcelWriter(out, engine="xlsxwriter") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(missing).to_excel(w, "Missing_Fields", index=False)
        pd.DataFrame(sales).to_excel(w, "Tally_Sales", index=False)
        pd.DataFrame(inventory).to_excel(w, "Tally_Inventory", index=False)

    print("✅ DONE:", out)

if __name__ == "__main__":
    main()
