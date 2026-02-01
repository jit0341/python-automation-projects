# ================= GST OCR – BASIC (FIXED) =================
import os, re, sys, socket, boto3
import pandas as pd
from pathlib import Path
from datetime import datetime

INPUT_DIR = "input"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GSTIN_REGEX = r"\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]"

textract = boto3.client("textract", region_name="ap-south-1")

def analyze(file):
    return textract.analyze_document(
        Document={"Bytes": open(file, "rb").read()},
        FeatureTypes=["TABLES"]
    )["Blocks"]

def get_lines(blocks):
    words = [b for b in blocks if b["BlockType"] == "WORD"]
    lines = {}
    for w in words:
        y = round(w["Geometry"]["BoundingBox"]["Top"], 3)
        lines.setdefault(y, []).append(w)

    out = []
    for y in sorted(lines):
        row = sorted(lines[y], key=lambda x: x["Geometry"]["BoundingBox"]["Left"])
        out.append(" ".join(w["Text"] for w in row))
    return out

def extract_header(lines):
    inv_no = inv_date = supplier = buyer = ""
    gstins = []

    for l in lines:
        if "INVOICE" in l.upper() and not inv_no:
            inv_no = l.strip()
        if re.search(r"\d{2}-\d{2}-\d{4}", l):
            inv_date = re.search(r"\d{2}-\d{2}-\d{4}", l).group()
        if "NEW ANURAG MOBILE" in l.upper():
            supplier = "NEW ANURAG MOBILE"
        if "MOBILE SOLUTION" in l.upper():
            buyer = "MOBILE"
        gstins += re.findall(GSTIN_REGEX, l)

    supplier_gstin = gstins[0] if len(gstins) > 0 else ""
    buyer_gstin = gstins[1] if len(gstins) > 1 else ""

    total = max(
        [float(x.replace(",", "")) for l in lines
         for x in re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d{2})", l)]
        or [0]
    )

    return inv_no, inv_date, supplier, supplier_gstin, buyer, buyer_gstin, total

def main():
    invoices, sales = [], []

    for pdf in Path(INPUT_DIR).glob("*.pdf"):
        blocks = analyze(pdf)
        lines = get_lines(blocks)

        inv_no, inv_date, sname, sgst, bname, bgst, total = extract_header(lines)

        invoices.append({
            "Invoice No": inv_no,
            "Invoice Date": inv_date,
            "Supplier Name": sname,
            "Supplier GSTIN": sgst,
            "Buyer Name": bname,
            "Buyer GSTIN": bgst,
            "Total Amount": total,
            "File": pdf.name
        })

        sales.append({
            "VoucherType": "Sales",
            "Date": inv_date,
            "PartyName": bname,
            "Reference": inv_no,
            "Amount": total,
            "Narration": f"AUTO OCR | {pdf.name}",
            "File": pdf.name
        })

    dashboard = [{
        "Total Invoices": len(invoices),
        "Generated On": datetime.now().strftime("%d-%m-%Y %H:%M")
    }]

    out = f"{OUTPUT_DIR}/GST_BASIC_FIXED.xlsx"
    with pd.ExcelWriter(out, engine="xlsxwriter") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(sales).to_excel(w, "Tally_Sales", index=False)
        pd.DataFrame(dashboard).to_excel(w, "Dashboard", index=False)

    print("✅ BASIC FIXED:", out)

if __name__ == "__main__":
    main()
