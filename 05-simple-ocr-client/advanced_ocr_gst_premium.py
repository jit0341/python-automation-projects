"""
ADVANCED GST OCR – PREMIUM VERSION (STABLE)
Author: Jitendra
Purpose: CA / GST Consultants
"""

import os
import re
import json
import pytesseract
import pandas as pd
from PIL import Image
from datetime import datetime

# =========================
# CONFIG
# =========================
IMAGES_DIR = "images"
OUTPUT_DIR = "output"
OUTPUT_EXCEL = os.path.join(OUTPUT_DIR, "invoices_gst_ready.xlsx")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "gstr1_output.json")
HSN_GST_FILE = "hsn_gst_rates.csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)

FAILED_INVOICES = []

# =========================
# UTILS
# =========================
def extract(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m and m.groups() else "NOT FOUND"

def safe_int(val, default=0):
    try:
        return int(str(val).strip())
    except:
        return default

def safe_float(val, default=0.0):
    try:
        return float(str(val).strip())
    except:
        return default

# =========================
# LOAD HSN → GST MAP (SAFE)
# =========================
def load_hsn_map():
    if not os.path.exists(HSN_GST_FILE):
        print("⚠️ hsn_gst_rates.csv not found")
        return {}

    df = pd.read_csv(HSN_GST_FILE)
    df.columns = df.columns.str.strip().str.upper()

    if "HSN" not in df.columns or "GST_RATE" not in df.columns:
        print("⚠️ Invalid HSN GST CSV format")
        return {}

    return dict(zip(df["HSN"].astype(str), df["GST_RATE"]))

HSN_GST_MAP = load_hsn_map()

# =========================
# OCR EXTRACTION (PER INVOICE SAFE)
# =========================
def extract_invoice(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)

        invoice_no = extract(r"Invoice\s*No[:\-]?\s*([A-Z0-9\-]+)", text)
        invoice_date = extract(r"(\d{2}[-/]\d{2}[-/]\d{4})", text)

        supplier = extract(r"Supplier[:\s]*([A-Za-z\s]+)", text)
        supplier_gstin = extract(r"GSTIN[:\s]*([0-9A-Z]{15})", text)

        buyer = extract(r"Bill\s*To[:\s]*([A-Za-z\s]+)", text)
        buyer_gstin = extract(r"GSTIN[:\s]*([0-9A-Z]{15})", text)

        place = extract(r"Place\s*of\s*Supply[:\s]*([A-Za-z\s]+)", text)

        hsn = extract(r"HSN[:\s]*(\d{4})", text)
        qty = safe_int(extract(r"Qty[:\s]*(\d+)", text), 1)
        rate = safe_float(extract(r"Rate[:\s]*(\d+)", text), 0)

        taxable = safe_float(
            extract(r"Taxable\s*Value[:\s]*(\d+)", text),
            rate * qty
        )

        cgst = safe_float(extract(r"CGST.*?(\d+)", text))
        sgst = safe_float(extract(r"SGST.*?(\d+)", text))
        igst = safe_float(extract(r"IGST.*?(\d+)", text))

        total = safe_float(extract(r"Total\s*Invoice\s*Value[:\s]*(\d+)", text))

        gst_rate = HSN_GST_MAP.get(hsn, extract(r"(\d+)%", text))
        gst_rate = safe_int(gst_rate)

        confidence = 100
        for v in [invoice_no, supplier, hsn]:
            if v == "NOT FOUND":
                confidence -= 25

        return {
            "Invoice Number": invoice_no,
            "Invoice Date": invoice_date,
            "Supplier Name": supplier,
            "Supplier GSTIN": supplier_gstin,
            "Buyer Name": buyer,
            "Buyer GSTIN": buyer_gstin,
            "Place of Supply": place,
            "Invoice Type": "B2B" if buyer_gstin != "NOT FOUND" else "B2C",
            "Taxable Value": taxable,
            "CGST": cgst,
            "SGST": sgst,
            "IGST": igst,
            "Invoice Value": total,
            "Confidence Score": confidence,
            "Items": [{
                "Description": "Item",
                "HSN": hsn,
                "Quantity": qty,
                "Unit Price": rate,
                "Taxable Value": taxable,
                "GST Rate": gst_rate
            }]
        }

    except Exception as e:
        FAILED_INVOICES.append({
            "File Name": os.path.basename(image_path),
            "Error Reason": str(e),
            "Error Stage": "Image Load / OCR",
            "Suggested Action": "Re-scan or replace invoice",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"❌ Invoice failed: {os.path.basename(image_path)} → {e}")
        return None

# =========================
# BUILD TALLY LINE ITEMS
# =========================
def build_tally_line_items(results):
    rows = []
    for r in results:
        for it in r["Items"]:
            rows.append({
                "Invoice Number": r["Invoice Number"],
                "Party Name": r["Buyer Name"] if r["Buyer Name"] != "NOT FOUND" else r["Supplier Name"],
                "Stock Item": it["Description"],
                "HSN Code": it["HSN"],
                "Rate": it["Unit Price"],
                "Qty": it["Quantity"],
                "UOM": "Nos",
                "GST Rate": it["GST Rate"],
                "Cess": 0,
                "Taxable Value": it["Taxable Value"]
            })
    return pd.DataFrame(rows)

# =========================
# MAIN RUN
# =========================
results = []

for f in os.listdir(IMAGES_DIR):
    if f.lower().endswith((".png", ".jpg", ".jpeg")):
        print(f"📄 Processing: {f}")
        data = extract_invoice(os.path.join(IMAGES_DIR, f))
        if data:
            results.append(data)

if not results:
    print("❌ No valid invoices processed")

# =========================
# EXPORT
# =========================
summary_rows = []
line_rows = []

for r in results:
    summary_rows.append({
        "Invoice Number": r["Invoice Number"],
        "Invoice Date": r["Invoice Date"],
        "Supplier GSTIN": r["Supplier GSTIN"],
        "Buyer GSTIN": r["Buyer GSTIN"],
        "Place of Supply": r["Place of Supply"],
        "Invoice Type": r["Invoice Type"],
        "Taxable Value": r["Taxable Value"],
        "CGST": r["CGST"],
        "SGST": r["SGST"],
        "IGST": r["IGST"],
        "Invoice Value": r["Invoice Value"],
        "Confidence Score": r["Confidence Score"]
    })

    for it in r["Items"]:
        line_rows.append({
            "Invoice Number": r["Invoice Number"],
            "Description": it["Description"],
            "HSN": it["HSN"],
            "Qty": it["Quantity"],
            "Rate": it["Unit Price"],
            "GST Rate": it["GST Rate"],
            "Taxable Value": it["Taxable Value"]
        })

df_summary = pd.DataFrame(summary_rows)
df_lines = pd.DataFrame(line_rows)
df_tally = build_tally_line_items(results)

with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:
    df_summary.to_excel(writer, sheet_name="Invoices_Summary", index=False)
    df_lines.to_excel(writer, sheet_name="Invoice_Line_Items", index=False)
    df_tally.to_excel(writer, sheet_name="Tally_Line_Items", index=False)

    if FAILED_INVOICES:
        pd.DataFrame(FAILED_INVOICES).to_excel(
            writer,
            sheet_name="Failed_Invoices",
            index=False
        )

# =========================
# GSTR-1 JSON
# =========================
with open(OUTPUT_JSON, "w") as f:
    json.dump(results, f, indent=2)

print("\n✅ PREMIUM GST OCR COMPLETED")
print(f"📊 Excel: {OUTPUT_EXCEL}")
print(f"📄 GSTR-1 JSON: {OUTPUT_JSON}")

if FAILED_INVOICES:
    print(f"⚠️ Failed invoices: {len(FAILED_INVOICES)} (see Failed_Invoices sheet)")
else:
    print("✅ No failed invoices")
