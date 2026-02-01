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

# ================= OCR CORE =================
def analyze_document_bytes(file_path):
    return textract.analyze_document(
        Document={"Bytes": open(file_path, "rb").read()},
        FeatureTypes=["TABLES"]
    )["Blocks"]

def get_words(blocks):
    return [b for b in blocks if b["BlockType"] == "WORD"]

def line_groups(blocks):
    lines = []
    for w in get_words(blocks):
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

# ================= HEADER EXTRACTION =================
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

# ================= INVENTORY RULES =================
def is_valid_item(name, qty):
    bad = ["CGST", "SGST", "IGST", "TAX", "TOTAL"]
    if any(b in name.upper() for b in bad):
        return False
    if not re.match(r"\d+(\.\d+)?", str(qty)):
        return False
    return True

# ================= MAIN =================
def main():
    license_check()

    if not check_internet():
        print("Internet required")
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

# ================= PRO INVENTORY (TAX-AWARE) =================

       for ln in lines:
           txt = ln["text"]

    # Skip headers / totals
           if any(x in txt.upper() for x in [
        "CGST", "SGST", "IGST", "TOTAL", "TAX",
        "RATE", "GST", "HSN", "AMOUNT"
    ]):
        continue

    # Must look like a product line
    if not re.search(r"[A-Z]{2,}", txt):
        continue

    nums = re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?", txt)
    if not nums:
        continue

    taxable = float(nums[-1].replace(",", ""))

    qty_match = re.search(r"\b\d+(\.\d+)?\b", txt)
    qty = float(qty_match.group()) if qty_match else 1.0

    name = txt
    name = re.sub(GSTIN_REGEX, "", name)
    name = re.sub(r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?", "", name)
    name = re.sub(r"\bPCS?|NOS?|QTY\b", "", name, flags=re.I)
    name = name.strip()

    if len(name) < 4:
        continue

    # ---- TAX CALCULATION ----
    cgst_rate = invoice_cgst_rate
    sgst_rate = invoice_sgst_rate

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
