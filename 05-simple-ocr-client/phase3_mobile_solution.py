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

GSTIN_REGEX = r"[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][A-Z0-9]Z[A-Z0-9]"

# ================= TEXTRACT =================

def analyze_document_bytes(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    res = textract.analyze_document(
        Document={"Bytes": data},
        FeatureTypes=["TABLES", "FORMS"]
    )
    return res["Blocks"]

# ================= LINE GROUPING =================

def group_lines(blocks, y_tol=0.01):
    words = [b for b in blocks if b["BlockType"] == "WORD"]
    lines = []

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

# ================= STRICT EXTRACTION RULES =================
def extract_invoice_no(lines):
    BLOCK = ["ROAD", "NAGAR", "AMBIKAPUR", "CG", "MOBILE"]
    for ln in lines[:15]:
        t = ln["text"].strip()
        if any(x in t.upper() for x in ["INVOICE", "SALES"]):
            if any(ch.isdigit() for ch in t):
                if not any(b in t.upper() for b in BLOCK):
                    return t.replace("Invoice", "").replace("No", "").strip()
    return "NOT FOUND"

def extract_invoice_date(lines, invoice_no):
    for i, ln in enumerate(lines):
        if invoice_no in ln["text"]:
            for j in range(1, 3):
                if i + j < len(lines):
                    m = re.search(r"\d{2}-\d{2}-\d{4}", lines[i+j]["text"])
                    if m:
                        return m.group()
    return "NOT FOUND"

def extract_gstins(lines):
    found = []
    for ln in lines:
        m = re.search(GSTIN_REGEX, ln["text"])
        if m:
            found.append(m.group())
    supplier = found[0] if len(found) >= 1 else "NOT FOUND"
    buyer = found[1] if len(found) >= 2 else "NOT FOUND"
    return supplier, buyer

def extract_grand_total(lines, table_end_y):
    candidates = []
    for ln in lines:
        if ln["y"] > table_end_y:
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
            for rel in b.get("Relationships", []):
                if rel["Type"] == "CHILD":
                    for cid in rel["Ids"]:
                        cell = block_map[cid]
                        if cell["BlockType"] == "CELL":
                            r = cell["RowIndex"]
                            c = cell["ColumnIndex"]
                            txt = ""
                            for cr in cell.get("Relationships", []):
                                if cr["Type"] == "CHILD":
                                    for wid in cr["Ids"]:
                                        if block_map[wid]["BlockType"] == "WORD":
                                            txt += block_map[wid]["Text"] + " "
                            rows.setdefault(r, {})[c] = txt.strip()
            tables.append(rows)
    return tables

# ================= MAIN =================

def main():
    invoices, missing, sales, inventory = [], [], [], []

    files = list(Path(INPUT_DIR).glob("*.pdf"))
    if not files:
        print("❌ No PDF files found")
        return

    for f in files:
        print("Processing:", f.name)

        blocks = analyze_document_bytes(f)
        lines = group_lines(blocks)
        tables = extract_tables(blocks)

        # table position
        table_ys = [ln["y"] for ln in lines if "Description" in ln["text"]]
        table_start_y = min(table_ys) if table_ys else 0.4
        table_end_y = max( ln["y"] for ln in lines
    if "TOTAL" in ln["text"].upper() or "TAXABLE" in ln["text"].upper()
)
        invoice_no = extract_invoice_no(lines)
        invoice_date = extract_invoice_date(lines, invoice_no)
        supplier_gstin, buyer_gstin = extract_gstins(lines)
        total_amount = extract_grand_total(lines, table_end_y)

        invoices.append({
            "invoice_no": invoice_no,
            "invoice_date": invoice_date,
            "supplier_name": "NEW ANURAG MOBILE",
            "supplier_gstin": supplier_gstin,
            "buyer_name": "MOBILE SOLUTION",
            "buyer_gstin": buyer_gstin,
            "total_amount": total_amount,
            "file": f.name
        })

        for fld, val in {
            "invoice_no": invoice_no,
            "invoice_date": invoice_date,
            "buyer_gstin": buyer_gstin,
            "total_amount": total_amount
        }.items():
            if val in ["NOT FOUND", 0, 0.0]:
                missing.append({
                    "file": f.name,
                    "field_name": fld,
                    "current_value": val,
                    "correct_value": "",
                    "source_link": f.name
                })

        sales.append({
            "VoucherType": "Sales",
            "Date": invoice_date,
            "PartyName": "MOBILE SOLUTION",
            "PartyGSTIN": buyer_gstin,
            "RefNo": invoice_no,
            "Amount": total_amount,
            "Narration": f"AUTO OCR | {f.name}"
        })

        for table in tables:
            for r, cols in table.items():
                item = cols.get(2, "")
                if not item or "total" in item.lower():
                    continue

                sgst_rate = cols.get(8, "")
                sgst_amt = cols.get(9, "")
                sgst_rate, sgst_amt = sgst_amt, sgst_rate  # swap fix

                inventory.append({
                    "InvoiceNo": invoice_no,
                    "PartyName": "MOBILE SOLUTION",
                    "ItemName": item,
                    "HSN": cols.get(3, ""),
                    "Qty": cols.get(5, ""),
                    "Rate": cols.get(6, ""),
                    "CGST_Rate": cols.get(7, ""),
                    "SGST_Rate": sgst_rate,
                    "SGST_Amt": sgst_amt,
                    "Amount": cols.get(10, "")
                })

    out = os.path.join(
        OUTPUT_DIR,
        f"PHASE3_VENDOR_LOCK_WOW_{datetime.now().strftime('%H%M')}.xlsx"
    )

    with pd.ExcelWriter(out, engine="xlsxwriter") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(missing).to_excel(w, "Missing_Corrections", index=False)
        pd.DataFrame(sales).to_excel(w, "Tally_Sales", index=False)
        pd.DataFrame(inventory).to_excel(w, "Tally_Inventory", index=False)

    print("✅ PRODUCTION READY:", out)

if __name__ == "__main__":
    main()
