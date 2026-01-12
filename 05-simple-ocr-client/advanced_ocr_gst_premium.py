"""
GST PREMIUM OCR AUTOMATION
Author: Jitendra
Client Ready – CA / GST Firm Edition
"""

import pytesseract
import cv2
import re
import os
import json
import pandas as pd
from PIL import Image
from datetime import datetime

# ==============================
# CONFIG
# ==============================

IMAGES_DIR = "images"
OUTPUT_EXCEL = "output/invoices_gst_ready.xlsx"
OUTPUT_JSON = "output/gstr1_output.json"
DEBUG_DIR = "debug"
HSN_GST_MAP = "config/hsn_gst_mapping.csv"

os.makedirs("output", exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)

# ==============================
# LOAD HSN → GST RATE
# ==============================

hsn_df = pd.read_csv(HSN_GST_MAP)
HSN_RATE = dict(zip(hsn_df["HSN"], hsn_df["GST_RATE"]))

# ==============================
# OCR ENGINE (MULTI PASS)
# ==============================

def ocr_multi_pass(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    text_psm6 = pytesseract.image_to_string(gray, config="--psm 6")
    text_psm4 = pytesseract.image_to_string(gray, config="--psm 4")

    return text_psm6 + "\n" + text_psm4

# ==============================
# REGEX EXTRACTORS
# ==============================

def extract(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(0).strip() if m else "NOT FOUND"

# ==============================
# CONFIDENCE ENGINE
# ==============================

def confidence_score(data):
    score = 0
    weights = {
        "Invoice Number": 15,
        "Invoice Date": 10,
        "Supplier GSTIN": 20,
        "Buyer GSTIN": 20,
        "Taxable Value": 20,
        "Total Invoice Value": 15
    }
    for k, w in weights.items():
        if data.get(k) not in ["", "NOT FOUND", 0]:
            score += w
    return score

# ==============================
# MAIN EXTRACTION
# ==============================

summary_rows = []
line_rows = []
gstr1 = {"b2b": [], "b2c": []}

for file in os.listdir(IMAGES_DIR):
    if not file.lower().endswith((".png", ".jpg", ".jpeg")):
        continue

    path = os.path.join(IMAGES_DIR, file)
    raw_text = ocr_multi_pass(path)

    with open(f"{DEBUG_DIR}/{file}_raw.txt", "w") as f:
        f.write(raw_text)

    invoice_no = extract(r'INV[-\s]?\d+', raw_text)
    invoice_date = extract(r'\d{2}[-/]\d{2}[-/]\d{4}', raw_text)

    supplier_gstin = extract(r'GSTIN[:\s]*([0-9A-Z]{15})', raw_text)
    buyer_gstin = extract(r'Bill To.*?GSTIN[:\s]*([0-9A-Z]{15})', raw_text)

    place = extract(r'Place of Supply[:\s]*([A-Za-z]+)', raw_text)
    hsn = extract(r'HSN[:\s]*(\d{4})', raw_text)

    qty = extract(r'Qty[:\s]*(\d+)', raw_text)
    rate = extract(r'Rate[:\s]*(\d+)', raw_text)
    taxable = extract(r'Taxable Value[:\s]*(\d+)', raw_text)

    cgst = extract(r'CGST.*?(\d+)', raw_text)
    sgst = extract(r'SGST.*?(\d+)', raw_text)
    igst = extract(r'IGST.*?(\d+)', raw_text)

    total = extract(r'Total Invoice Value[:\s]*(\d+)', raw_text)

    gst_rate = HSN_RATE.get(hsn, "")

    invoice_type = "B2B" if buyer_gstin != "NOT FOUND" else "B2C"

    summary = {
        "Invoice Number": invoice_no,
        "Invoice Date": invoice_date,
        "Supplier GSTIN": supplier_gstin,
        "Buyer GSTIN": buyer_gstin,
        "Place of Supply": place,
        "Invoice Type": invoice_type,
        "Taxable Value": int(taxable) if taxable.isdigit() else 0,
        "CGST Amount": int(cgst) if cgst.isdigit() else 0,
        "SGST Amount": int(sgst) if sgst.isdigit() else 0,
        "IGST Amount": int(igst) if igst.isdigit() else 0,
        "Total Invoice Value": int(total) if total.isdigit() else 0
    }

    score = confidence_score(summary)
    summary["Confidence Score"] = score
    summary["Review Status"] = "AUTO OK" if score >= 90 else "NEEDS REVIEW"

    summary_rows.append(summary)

    line_rows.append({
        "Invoice Number": invoice_no,
        "HSN": hsn,
        "Quantity": qty,
        "Rate": rate,
        "Taxable Value": taxable,
        "GST Rate %": gst_rate
    })

    # GSTR-1 JSON
    if invoice_type == "B2B":
        gstr1["b2b"].append(summary)
    else:
        gstr1["b2c"].append(summary)

# ==============================
# EXPORT
# ==============================

with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as w:
    pd.DataFrame(summary_rows).to_excel(w, sheet_name="Invoices_Summary", index=False)
    pd.DataFrame(line_rows).to_excel(w, sheet_name="Invoice_Line_Items", index=False)

with open(OUTPUT_JSON, "w") as f:
    json.dump(gstr1, f, indent=2)

print("✅ PREMIUM GST OCR COMPLETED")
print("📊 Excel:", OUTPUT_EXCEL)
print("🧾 GSTR-1 JSON:", OUTPUT_JSON)
