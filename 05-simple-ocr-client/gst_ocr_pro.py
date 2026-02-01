# ================= GST OCR PRO v2 =================
# Stable | Tables-based Inventory | Invoice-level GST split
# Author: Jitendra Bharti (PRO)

import os, re, sys, socket
import boto3
import pandas as pd
from pathlib import Path
from datetime import datetime

# ================= CONFIG =================
PRODUCT_MODE = "PRO"
INPUT_DIR = "input"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GSTIN_REGEX = r"\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]"

# ================= LICENSE =================
LICENSE_FILE = "license_start.txt"
LOCK_DAYS = 30
RENEW_UPI = "8871097310-2@ybl"
RENEW_MOBILE = "8871097310"

def license_check():
    today = datetime.now().date()
    if not os.path.exists(LICENSE_FILE):
        open(LICENSE_FILE, "w").write(today.strftime("%Y-%m-%d"))
        return
    start = datetime.strptime(open(LICENSE_FILE).read().strip(), "%Y-%m-%d").date()
    if (today - start).days >= LOCK_DAYS:
        print("🔒 PRO PLAN EXPIRED")
        print(f"UPI: {RENEW_UPI}")
        print(f"Mobile: {RENEW_MOBILE}")
        sys.exit()

# ================= INTERNET =================
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except:
        return False

# ================= AWS =================
def get_textract_client():
    return boto3.client("textract", region_name="ap-south-1")

textract = get_textract_client()

# ================= OCR =================
def analyze_document_bytes(file_path):
    return textract.analyze_document(
        Document={"Bytes": open(file_path, "rb").read()},
        FeatureTypes=["TABLES"]
    )["Blocks"]

# ================= LINE GROUP =================
def line_groups(blocks):
    words = [b for b in blocks if b["BlockType"] == "WORD"]
    lines = []

    for w in words:
        y = round(w["Geometry"]["BoundingBox"]["Top"], 3)
        for ln in lines:
            if abs(ln["y"] - y) <= 0.01:
                ln["words"].append(w)
                break
        else:
            lines.append({"y": y, "words": [w]})

    for ln in lines:
        ln["words"].sort(key=lambda x: x["Geometry"]["BoundingBox"]["Left"])
        ln["text"] = " ".join(w["Text"] for w in ln["words"])

    return sorted(lines, key=lambda x: x["y"])

# ================= HEADER =================
def extract_supplier(lines):
    for ln in lines[:10]:
        if re.search(GSTIN_REGEX, ln["text"]):
            return ln["text"].replace(re.search(GSTIN_REGEX, ln["text"]).group(), "").strip()
    for ln in lines[:5]:
        if ln["text"].isupper() and len(ln["text"]) > 6:
            return ln["text"]
    return "UNKNOWN"

def extract_gstins(lines):
    gstins = re.findall(GSTIN_REGEX, " ".join(l["text"] for l in lines))
    supplier = gstins[0] if len(gstins) > 0 else ""
    buyer = gstins[1] if len(gstins) > 1 else ""
    return supplier, buyer

def extract_invoice_date(lines):
    for ln in lines:
        m = re.search(r"\d{2}-\d{2}-\d{4}", ln["text"])
        if m:
            return m.group()
    return ""

def extract_total(lines):
    nums = []
    for ln in lines:
        for n in re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d{2})", ln["text"]):
            v = float(n.replace(",", ""))
            if v > 1000:
                nums.append(v)
    return max(nums) if nums else 0.0

# ================= GST RATE (INVOICE LEVEL) =================
def extract_invoice_gst_rate(lines):
    text = " ".join(l["text"] for l in lines).upper()
    if "18%" in text:
        return 9.0, 9.0
    if "12%" in text:
        return 6.0, 6.0
    if "5%" in text:
        return 2.5, 2.5
    return 9.0, 9.0   # SAFE DEFAULT (MOBILE)

# ================= TABLE EXTRACTION =================
def extract_tables(blocks):
    block_map = {b["Id"]: b for b in blocks}
    tables = []

    for b in blocks:
        if b["BlockType"] == "TABLE":
            rows = {}
            for rel in b.get("Relationships", []):
                for cid in rel.get("Ids", []):
                    cell = block_map[cid]
                    if cell["BlockType"] == "CELL":
                        text = ""
                        for r in cell.get("Relationships", []):
                            for wid in r.get("Ids", []):
                                if block_map[wid]["BlockType"] == "WORD":
                                    text += block_map[wid]["Text"] + " "
                        rows.setdefault(cell["RowIndex"], {})[cell["ColumnIndex"]] = text.strip()
            tables.append(rows)
    return tables

# ================= MAIN =================
def main():
    license_check()
    if not check_internet():
        print("❌ Internet required")
        return

    invoices, inventory, sales, missing = [], [], [], []

    for pdf in Path(INPUT_DIR).glob("*.pdf"):
        blocks = analyze_document_bytes(pdf)
        lines = line_groups(blocks)
        tables = extract_tables(blocks)

        supplier_name = extract_supplier(lines)
        supplier_gstin, buyer_gstin = extract_gstins(lines)
        buyer_name = "MOBILE" if buyer_gstin else "UNKNOWN"
        inv_date = extract_invoice_date(lines)
        total = extract_total(lines)
        inv_no = pdf.stem

        cgst_rate, sgst_rate = extract_invoice_gst_rate(lines)

        invoices.append({
            "Invoice No": inv_no,
            "Invoice Date": inv_date,
            "Supplier Name": supplier_name,
            "Supplier GSTIN": supplier_gstin,
            "Buyer Name": buyer_name,
            "Buyer GSTIN": buyer_gstin,
            "Total Amount": total,
            "File": pdf.name
        })

        sales.append({
            "VoucherType": "Sales",
            "Date": inv_date,
            "PartyName": buyer_name,
            "Reference": inv_no,
            "Amount": total,
            "Narration": f"AUTO OCR | {pdf.name}"
        })

        # ========= INVENTORY (TABLES ONLY) =========
        for table in tables:
            for r, row in table.items():
                cells = list(row.values())
                line = " ".join(cells).upper()

                if any(x in line for x in ["TOTAL", "CGST", "SGST", "IGST", "TAX", "RATE"]):
                    continue

                if not re.search(r"[A-Z]{2,}", line):
                    continue

                nums = re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?", line)
                if not nums:
                    continue

                taxable = float(nums[-1].replace(",", ""))

                qty = 1.0
                for n in nums[:-1]:
                    try:
                        q = float(n.replace(",", ""))
                        if q <= 100:
                            qty = q
                            break
                    except:
                        pass

                name = re.sub(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?", "", line)
                name = re.sub(GSTIN_REGEX, "", name)
                name = re.sub(r"\bPCS?|NOS?|QTY\b", "", name)
                name = name.strip()

                if len(name) < 4:
                    continue

                cgst_amt = round(taxable * cgst_rate / 100, 2)
                sgst_amt = round(taxable * sgst_rate / 100, 2)

                inventory.append({
                    "Invoice No": inv_no,
                    "Item Name": name,
                    "Qty": qty,
                    "UOM": "Pcs.",
                    "Taxable Value": taxable,
                    "CGST Rate": cgst_rate,
                    "CGST Amount": cgst_amt,
                    "SGST Rate": sgst_rate,
                    "SGST Amount": sgst_amt,
                    "Line Total": round(taxable + cgst_amt + sgst_amt, 2)
                })

    dashboard = [{
        "Total Invoices": len(invoices),
        "Total Inventory Rows": len(inventory),
        "Missing Fields Count": len(missing),
        "Generated On": datetime.now().strftime("%d-%m-%Y %H:%M")
    }]

    out = os.path.join(OUTPUT_DIR, f"GST_PRO_{datetime.now().strftime('%H%M')}.xlsx")
    with pd.ExcelWriter(out, engine="xlsxwriter") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(sales).to_excel(w, "Tally_Sales", index=False)
        pd.DataFrame(inventory).to_excel(w, "Tally_Inventory", index=False)
        pd.DataFrame(missing).to_excel(w, "Missing_Fields", index=False)
        pd.DataFrame(dashboard).to_excel(w, "Dashboard", index=False)

    print("✅ PRO DONE:", out)

if __name__ == "__main__":
    main()
