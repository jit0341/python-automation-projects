"""
GST OCR – PDF + Image Support (FINAL CLEAN VERSION)
Author: Jitendra Bharti
Purpose: CA / GST Consultants (Offline EXE)
"""

import os
import re
import json
import pytesseract
import pandas as pd
from PIL import Image
from datetime import datetime

# ------------------ PATH SETUP ------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGES_DIR = os.path.join(BASE_DIR, "images")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR   = os.path.join(BASE_DIR, "temp_pdf")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Tesseract
TESS_PATH = os.path.join(BASE_DIR, "tesseract-portable", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESS_PATH

# PDF support
try:
    from pdf2image import convert_from_path
    POPPLER_PATH = os.path.join(BASE_DIR, "poppler-portable", "bin")
    PDF_OK = True
except:
    PDF_OK = False

FAILED = []

# ------------------ HELPERS ------------------

def find(pattern, text):
    m = re.search(pattern, text, re.I)
    return m.group(1).strip() if m else "NOT FOUND"

def money(val):
    try:
        return float(val.replace(",", "").replace("₹", "").strip())
    except:
        return 0.0

# ------------------ OCR CORE ------------------

def extract_invoice(img_path):
    try:
        text = pytesseract.image_to_string(Image.open(img_path))

        return {
            "File": os.path.basename(img_path),
            "Invoice No": find(r"(Invoice|Inv|Bill)\s*(No|#)?[:\- ]*([A-Z0-9\-\/]+)", text),
            "Invoice Date": find(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text),
            "Supplier GSTIN": find(r"GSTIN[:\- ]*([0-9A-Z]{15})", text),
            "Total Value": money(find(r"(Total|Grand Total|Amount)[:₹ ]*([\d,]+)", text)),
        }

    except Exception as e:
        FAILED.append({"File": os.path.basename(img_path), "Error": str(e)})
        return None

# ------------------ PDF HANDLER ------------------

def process_pdf(pdf_path):
    results = []
    pages = convert_from_path(
        pdf_path,
        dpi=300,
        poppler_path=POPPLER_PATH
    )

    for i, page in enumerate(pages, 1):
        img_file = os.path.join(TEMP_DIR, f"page_{i}.jpg")
        page.save(img_file, "JPEG")

        data = extract_invoice(img_file)
        if data:
            data["Source PDF"] = os.path.basename(pdf_path)
            data["Page"] = i
            results.append(data)

        os.remove(img_file)

    return results

# ------------------ MAIN ------------------

def main():
    print("GST OCR – PDF + IMAGE (OFFLINE)")
    print("=" * 40)

    files = os.listdir(IMAGES_DIR)
    results = []

    for f in files:
        path = os.path.join(IMAGES_DIR, f)

        if f.lower().endswith((".jpg", ".png", ".jpeg")):
            data = extract_invoice(path)
            if data:
                results.append(data)

        elif f.lower().endswith(".pdf") and PDF_OK:
            results.extend(process_pdf(path))

    if not results:
        print("No invoices processed.")
        input("Press Enter...")
        return

    df = pd.DataFrame(results)

    out_xlsx = os.path.join(
        OUTPUT_DIR,
        f"gst_invoices_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    )

    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Invoices")
        if FAILED:
            pd.DataFrame(FAILED).to_excel(w, sheet_name="Failed", index=False)

    with open(out_xlsx.replace(".xlsx", ".json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"✔ Processed: {len(results)} invoices")
    print(f"✔ Excel: {out_xlsx}")
    print("✔ JSON created")
    input("Press Enter to exit...")

# ------------------

if __name__ == "__main__":
    main()
