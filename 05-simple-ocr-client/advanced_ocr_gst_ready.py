"""
Advanced GST-Ready OCR Engine (Production Grade)
Author: Jitendra
"""

import pytesseract
from PIL import Image
import pandas as pd
import os
import re
import cv2
from datetime import datetime

# =========================
# CONFIG
# =========================
IMAGES_DIR = "images"
OUTPUT_FILE = "output/invoices_gst_ready.xlsx"
DEBUG_DIR = "debug"
HSN_RATE_FILE = "hsn_gst_rates.csv"

os.makedirs(DEBUG_DIR, exist_ok=True)
os.makedirs("output", exist_ok=True)

# =========================
# LOAD HSN → GST RATE MAP
# =========================
hsn_df = pd.read_csv(HSN_RATE_FILE)
HSN_RATE_MAP = dict(zip(hsn_df["HSN"].astype(str), hsn_df["GST_RATE"]))

# =========================
# IMAGE PREPROCESSING
# =========================
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.fastNlMeansDenoising(gray)

# =========================
# OCR CLEANUP
# =========================
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    return text

# =========================
# SAVE RAW OCR
# =========================
def save_raw_ocr(filename, text):
    path = os.path.join(DEBUG_DIR, f"ocr_raw_{filename}.txt")
    with open(path, "w") as f:
        f.write(text)

# =========================
# SAFE REGEX HELPERS
# =========================
def safe_search(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else "NOT FOUND"

def safe_amount(label, text):
    m = re.search(rf'{label}[\s@:%]*([\d,]+\.?\d*)', text, re.IGNORECASE)
    return float(m.group(1).replace(",", "")) if m else 0.0

# =========================
# MAIN EXTRACTION
# =========================
def extract_invoice(image_path):
    img = preprocess_image(image_path)
    pil_img = Image.fromarray(img)

    text = pytesseract.image_to_string(
        pil_img,
        config="--oem 3 --psm 4"
    )

    save_raw_ocr(os.path.basename(image_path), text)
    text = clean_text(text)

    # -------- BASIC FIELDS --------
    invoice_no = safe_search(r'(INV[\W_]*\d+)', text)
    invoice_date = safe_search(r'(\d{2}[-/]\d{2}[-/]\d{4})', text)

    supplier_gstin = safe_search(r'GSTIN[:\s]*([A-Z0-9]{15})', text)
    buyer_gstin = safe_search(r'Bill To.*?GSTIN[:\s]*([A-Z0-9]{15})', text)

    pos = safe_search(r'Place\s+of\s+Supp\w+[:\s]*([A-Za-z]+)', text)

    total_value = safe_amount("Total Invoice Value", text)
    cgst = safe_amount("CGST", text)
    sgst = safe_amount("SGST", text)
    igst = safe_amount("IGST", text)

    taxable = total_value - (cgst + sgst + igst)

    # -------- ITEM EXTRACTION --------
    items = []
    item_pattern = r'HSN[:\s]*(\d{4}).*?Qty[:\s]*(\d+).*?Rate[:\s]*(\d+).*?Taxable Value[:\s]*(\d+)'
    matches = re.findall(item_pattern, text, re.DOTALL)

    for hsn, qty, rate, val in matches:
        gst_rate = HSN_RATE_MAP.get(hsn, "")
        items.append({
            "Invoice Number": invoice_no,
            "HSN": hsn,
            "Quantity": int(qty),
            "Rate": int(rate),
            "Taxable Value": int(val),
            "GST Rate (%)": gst_rate
        })

    # -------- CONFIDENCE SCORE --------
    score = 0
    score += 25 if invoice_no != "NOT FOUND" else 0
    score += 25 if supplier_gstin != "NOT FOUND" else 0
    score += 25 if total_value > 0 else 0
    score += 25 if (cgst + sgst + igst) > 0 else 0

    return {
        "Invoice Number": invoice_no,
        "Invoice Date": invoice_date,
        "Supplier GSTIN": supplier_gstin,
        "Buyer GSTIN": buyer_gstin,
        "Place of Supply": pos,
        "Taxable Value": taxable,
        "CGST Amount": cgst,
        "SGST Amount": sgst,
        "IGST Amount": igst,
        "Total Invoice Value": total_value,
        "Confidence Score": score,
        "Review Status": "AUTO OK" if score >= 75 else "NEEDS REVIEW",
        "Items": items
    }

# =========================
# RUN PIPELINE
# =========================
summaries = []
line_items = []

print("🚀 GST OCR PIPELINE STARTED")

for img in os.listdir(IMAGES_DIR):
    if img.lower().endswith((".png", ".jpg", ".jpeg")):
        print("Processing:", img)
        data = extract_invoice(os.path.join(IMAGES_DIR, img))
        summaries.append({k: v for k, v in data.items() if k != "Items"})
        line_items.extend(data["Items"])

# =========================
# EXPORT EXCEL
# =========================
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as w:
    pd.DataFrame(summaries).to_excel(w, "Invoices_Summary", index=False)
    pd.DataFrame(line_items).to_excel(w, "Invoice_Line_Items", index=False)

print("✅ GST READY EXCEL GENERATED:", OUTPUT_FILE)
