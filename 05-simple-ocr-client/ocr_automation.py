"""
ADVANCED GST OCR – BUSINESS CONTROLLED VERSION (STANDALONE EXE READY)
Author: Jitendra Bharti
Purpose: CA / GST Consultants - One-click Laptop EXE
"""

import os
import re
import json
import sys
import pytesseract
import pandas as pd
from PIL import Image
from datetime import datetime

# =========================
# TESSERACT PATH SETUP (PORTABLE)
# =========================
def setup_tesseract():
    # Try relative portable path first
    tess_paths = [
        r'.\tesseract-portable\tesseract.exe',
        r'.\tesseract.exe',
        r'../tesseract-portable\tesseract.exe'
    ]
    
    for path in tess_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"✅ Tesseract found: {path}")
            return True
    
    print("❌ Tesseract not found! Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    input("Press Enter to exit...")
    sys.exit(1)

# =========================
# CONFIG (EXE FRIENDLY)
# =========================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, "images")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
HSN_GST_FILE = os.path.join(SCRIPT_DIR, "hsn_gst_rates.csv")

OUTPUT_EXCEL = os.path.join(OUTPUT_DIR, "invoices_gst_ready.xlsx")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "gstr1_output.json")
COUNTER_FILE = os.path.join(SCRIPT_DIR, "invoice_counter.json")

# ---- BUSINESS CONTROLS ----
ALLOWED_GSTINS = {
    "22AAAAA0000A1Z5",   # CLIENT GSTIN - EDIT AS NEEDED
}

MAX_INVOICES_PER_MONTH = 1000

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
FAILED_INVOICES = []

# =========================
# UTILS
# =========================
def extract(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m and m.groups() else "NOT FOUND"

def safe_int(val, default=0):
    try:
        return int(str(val).strip().replace(',', ''))
    except:
        return default

def safe_float(val, default=0.0):
    try:
        return float(str(val).strip().replace(',', ''))
    except:
        return default

# =========================
# COUNTER UTILS
# =========================
def load_counter():
    if not os.path.exists(COUNTER_FILE):
        return {}
    try:
        with open(COUNTER_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_counter(counter):
    try:
        with open(COUNTER_FILE, "w", encoding='utf-8') as f:
            json.dump(counter, f, indent=2)
    except Exception as e:
        print(f"Counter save error: {e}")

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
    if not gstin or gstin == "NOT FOUND":
        return True  # Skip validation if not found
    gstin = gstin.strip().upper()
    return gstin in ALLOWED_GSTINS

# =========================
# LOAD HSN → GST MAP
# =========================
def load_hsn_map():
    if not os.path.exists(HSN_GST_FILE):
        print("⚠️ HSN file not found, using default rates")
        return {}
    
    try:
        df = pd.read_csv(HSN_GST_FILE)
        df.columns = df.columns.str.strip().str.upper()
        if "HSN" in df.columns and "GST_RATE" in df.columns:
            return dict(zip(df["HSN"].astype(str), df["GST_RATE"]))
    except Exception as e:
        print(f"⚠️ HSN load error: {e}")
    
    return {}

HSN_GST_MAP = load_hsn_map()

# =========================
# OCR PER INVOICE (IMPROVED PATTERNS)
# =========================
def extract_invoice(image_path):
    try:
        print(f"📄 Processing: {os.path.basename(image_path)}")
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, config='--psm 6')  # Table mode

        # Improved patterns for Indian invoices
        invoice_no = extract(r"(?i)(?:invoice|inv|bill)s*(?:no|#|num|number)?[:-.s]*s*([A-Z0-9/\\-]+)", text)
        invoice_date = extract(r"(d{1,2}[/-]d{1,2}[/-]d{2,4})", text)
        
        supplier = extract(r"(?i)(?:supplier|from|seller)[:s]*([A-Za-zs&.,]+?)(?=
|$)", text)
        supplier_gstin = extract(r"(?i)(?:gstin|gsts*no|pan)[:s]*([0-9A-Z]{15})", text)
        
        buyer = extract(r"(?i)(?:buyer|bills*to|to|customer)[:s]*([A-Za-zs&.,]+?)(?=
|$)", text)
        buyer_gstin = extract(r"(?i)(?:gstin|gsts*no|pan).*?([0-9A-Z]{15})", text)
        
        place = extract(r"(?i)(?:places*ofs*supply|supply|state)[:s]*([A-Za-zs]+)", text)

        # GSTIN validation (non-blocking for EXE)
        if supplier_gstin != "NOT FOUND" and not is_allowed_gstin(supplier_gstin):
            print(f"⚠️ Supplier GSTIN restricted: {supplier_gstin}")

        # Items extraction
        hsn = extract(r"(?i)hsn[:s]*(d{4})", text)
        qty = safe_int(extract(r"(?i)qty[:s]*(d+)", text), 1)
        rate = safe_float(extract(r"(?i)(?:rate|price|₹?)[:s]*([0-9,]+.?d*)", text), 0)
        
        taxable = safe_float(extract(r"(?i)(?:taxable|value|amt|amount)[:s]*([0-9,]+.?d*)", text), rate * qty)
        
        cgst = safe_float(extract(r"(?i)cgst[:s@%]*([0-9,]+.?d*)", text))
        sgst = safe_float(extract(r"(?i)sgst[:s@%]*([0-9,]+.?d*)", text))
        igst = safe_float(extract(r"(?i)igst[:s@%]*([0-9,]+.?d*)", text))
        
        total = safe_float(extract(r"(?i)(?:total|grands*total|amount)[:s]*([0-9,]+.?d*)", text))

        gst_rate = HSN_GST_MAP.get(hsn, safe_int(extract(r"(d+)[/%]", text), 18))

        # Confidence score
        confidence = 100
        for field in [invoice_no, supplier, hsn, invoice_date]:
            if field == "NOT FOUND":
                confidence -= 20
        
        current_count = increment_invoice_count()
        if current_count > MAX_INVOICES_PER_MONTH:
            confidence -= 15
            print("⚠️ Monthly limit approaching")

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
            "HSN Code": hsn,
            "GST Rate": gst_rate,
            "File Name": os.path.basename(image_path),
            "Items": [{
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
        print(f"❌ Failed: {os.path.basename(image_path)} - {e}")
        return None

# =========================
# MAIN EXECUTION
# =========================
def main():
    print("🚀 ADVANCED GST OCR - BUSINESS VERSION")
    print("=" * 50)
    
    # Setup Tesseract
    setup_tesseract()
    
    # Scan images
    image_extensions = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp')
    results = []
    
    print(f"🔍 Scanning {IMAGES_DIR}...")
    if not os.listdir(IMAGES_DIR):
        print("❌ No images found in 'images' folder!")
        print("📁 Put invoice JPG/PNG files in 'images' folder")
        input("Press Enter to exit...")
        return
    
    for filename in os.listdir(IMAGES_DIR):
        if filename.lower().endswith(image_extensions):
            image_path = os.path.join(IMAGES_DIR, filename)
            data = extract_invoice(image_path)
            if data:
                results.append(data)
    
    if not results:
        print("❌ No valid invoices processed!")
        if FAILED_INVOICES:
            print("📋 Check Failed_Invoices sheet for details")
        input("Press Enter to exit...")
        return
    
    print(f"✅ Processed {len(results)} invoices successfully!")
    
    # =========================
    # EXPORT RESULTS
    # =========================
    df_summary = pd.DataFrame(results)
    
    with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Invoices_Summary", index=False)
        
        if FAILED_INVOICES:
            pd.DataFrame(FAILED_INVOICES).to_excel(
                writer, sheet_name="Failed_Invoices", index=False
            )
    
    # JSON backup
    with open(OUTPUT_JSON, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Excel saved: {OUTPUT_EXCEL}")
    print("🎉 GST OCR COMPLETED SUCCESSFULLY!")
    print("
📈 SUMMARY:")
    print(f"• Total Invoices: {len(results)}")
    print(f"• Avg Confidence: {df_summary['Confidence Score'].mean():.1f}%")
    print(f"• Total Value: ₹{df_summary['Invoice Value'].sum():,.0f}")
    
    input("
Press Enter to exit...")

if __name__ == "__main__":
    main()
