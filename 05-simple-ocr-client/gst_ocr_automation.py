"""
ADVANCED GST OCR – BUSINESS CONTROLLED VERSION
Author: Jitendra Bharti
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

# ---- BUSINESS CONTROLS (SILENT) ----
ALLOWED_GSTINS = {
    "22AAAAA0000A1Z5",   # CLIENT GSTIN
}

MAX_INVOICES_PER_MONTH = 1000
COUNTER_FILE = "invoice_counter.json"

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
# COUNTER UTILS
# =========================

def load_counter():
    if not os.path.exists(COUNTER_FILE):
        return {}
    with open(COUNTER_FILE, "r") as f:
        return json.load(f)

def save_counter(counter):
    with open(COUNTER_FILE, "w") as f:
        json.dump(counter, f, indent=2)

def increment_invoice_count():
    counter = load_counter()
    month_key = datetime.now().strftime("%Y-%m")

    counter.setdefault(month_key, 0)
    counter[month_key] += 1

    save_counter(counter)
    return counter[month_key]

# =========================
# GSTIN VALIDATION
# =========================

def is_allowed_gstin(gstin):
    gstin = gstin.strip().upper()
    return gstin in ALLOWED_GSTINS

# =========================
# LOAD HSN → GST MAP
# =========================

def load_hsn_map():
    if not os.path.exists(HSN_GST_FILE):
        return {}

    df = pd.read_csv(HSN_GST_FILE)
    df.columns = df.columns.str.strip().str.upper()

    if "HSN" not in df.columns or "GST_RATE" not in df.columns:
        return {}

    return dict(zip(df["HSN"].astype(str), df["GST_RATE"]))

HSN_GST_MAP = load_hsn_map()

# =========================
# OCR PER INVOICE
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

        # ---- HARD GSTIN LOCK ----
        if supplier_gstin != "NOT FOUND" and not is_allowed_gstin(supplier_gstin):
            raise ValueError("Invalid invoice format detected.")

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

        # ---- CONFIDENCE + SOFT LIMIT ----
        confidence = 100
        for v in [invoice_no, supplier, hsn]:
            if v == "NOT FOUND":
                confidence -= 25

        current_count = increment_invoice_count()
        if current_count > MAX_INVOICES_PER_MONTH:
            confidence -= 20

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
            "Error": str(e),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return None

# =========================
# MAIN RUN
# =========================

results = []

for f in os.listdir(IMAGES_DIR):
    if f.lower().endswith((".png", ".jpg", ".jpeg")):
        data = extract_invoice(os.path.join(IMAGES_DIR, f))
        if data:
            results.append(data)

if not results:
    print("❌ No valid invoices processed")

# =========================
# EXPORT
# =========================

df_summary = pd.DataFrame(results)

with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:
    df_summary.to_excel(writer, sheet_name="Invoices_Summary", index=False)

    if FAILED_INVOICES:
        pd.DataFrame(FAILED_INVOICES).to_excel(
            writer,
            sheet_name="Failed_Invoices",
            index=False
        )

with open(OUTPUT_JSON, "w") as f:
    json.dump(results, f, indent=2)

print("✅ GST OCR AUTOMATION COMPLETED")
