
"""
Advanced OCR for Delivery Notes with PO Matching
Author: Jitendra
Version: FINAL (Client Ready)
"""

import pytesseract
from PIL import Image
import pandas as pd
import os
import re
import cv2

# =========================
# CONFIG
# =========================
IMAGES_DIR = "images"
OUTPUT_FILE = "output/delivery_notes_final.xlsx"
PO_FILE = "po_data.csv"      # optional
ENABLE_PO_MATCHING = True   # turn ON/OFF

# =========================
# IMAGE PREPROCESSING
# =========================
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced = cv2.equalizeHist(gray)
    denoised = cv2.fastNlMeansDenoising(enhanced)
    return denoised

# =========================
# OCR TEXT CLEANUP
# =========================
def clean_ocr_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'([a-zA-Z])\n([a-zA-Z])', r'\1 \2', text)
    return text

# =========================
# LINE ITEM EXTRACTION
# =========================
def extract_items(text):
    items = []

    pattern = r'([A-Z]{2,6}\d{2,4})\s+([A-Za-z\s]+)\s+(\d+)\s+(\d+\.?\d*)'
    matches = re.findall(pattern, text)

    for m in matches:
        items.append({
            "Code": m[0],
            "Description": m[1].strip(),
            "Quantity": int(m[2]),
            "Amount": float(m[3])
        })

    return items

# =========================
# PO DATA
# =========================
def load_po_data(po_file):
    if not os.path.exists(po_file):
        return None

    if po_file.endswith(".csv"):
        return pd.read_csv(po_file)
    else:
        return pd.read_excel(po_file)

def match_items_with_po(items, po_df):
    matched = []

    for item in items:
        row = po_df[po_df["Product Code"] == item["Code"]]

        if row.empty:
            status = "NO PO MATCH"
            po_qty = None
        else:
            po_qty = int(row.iloc[0]["Ordered Qty"])
            status = "MATCH" if item["Quantity"] == po_qty else "QTY MISMATCH"

        matched.append({
            **item,
            "PO Qty": po_qty,
            "PO Match Status": status
        })

    return matched

# =========================
# MAIN EXTRACTION
# =========================
def extract_from_image(image_path, po_df=None):
    pre = preprocess_image(image_path)
    pil_img = Image.fromarray(pre)

    text = pytesseract.image_to_string(pil_img, config="--psm 6")
    print("------ RAW OCR TEXT ------")
    print(text)
    print("--------------------------")
    text = clean_ocr_text(text)

    # --- DN ---
    
    dn_match = re.search(
    r'(D[-\s]?\d{4}[-\s]?\d{3})',
    text,
    re.IGNORECASE
)
    dn_number = dn_match.group(1) if dn_match else "NOT FOUND"

    # --- DATE ---
    date_match = re.search(r'\d{2}[-/]\d{2}[-/]\d{4}', text)
    date = date_match.group() if date_match else "NOT FOUND"

    # --- SUPPLIER ---
    supplier_match = re.search(
        r'(Supplier|From)[:\s]+([A-Za-z\s]+)',
        text,
        re.IGNORECASE
    )
    supplier = supplier_match.group(2).strip() if supplier_match else "NOT FOUND"

    # --- TOTAL ---
    total_match = re.search(
    r'Total[:\s]*\$?\s*([\d,]+\.?\d*)',
    text,
    re.IGNORECASE
)
    total = total_match.group(1).replace(',', '') if total_match else "0"

    # --- ITEMS ---
    items = extract_items(text)

    if ENABLE_PO_MATCHING and po_df is not None:
        items = match_items_with_po(items, po_df)
        po_status = "PO CHECKED"
    else:
        po_status = "PO NOT USED"

    return {
        "File": os.path.basename(image_path),
        "DN Number": dn_number,
        "Date": date,
        "Supplier": supplier,
        "Total Amount": total,
        "Items Count": len(items),
        "PO Status": po_status,
        "Items": items
    }

# =========================
# EXPORT
# =========================
def export_to_excel(results, output_file):
    main_rows = []
    item_rows = []

    for r in results:
        main_rows.append({
            "File": r["File"],
            "DN Number": r["DN Number"],
            "Date": r["Date"],
            "Supplier": r["Supplier"],
            "Total Amount": r["Total Amount"],
            "Items Count": r["Items Count"],
            "PO Status": r["PO Status"]
        })

        for it in r["Items"]:
            item_rows.append({
                "DN Number": r["DN Number"],
                "Item Code": it["Code"],
                "Description": it["Description"],
                "Quantity": it["Quantity"],
                "Amount": it["Amount"],
                "PO Qty": it.get("PO Qty"),
                "PO Match Status": it.get("PO Match Status")
            })

    df_main = pd.DataFrame(main_rows)
    df_items = pd.DataFrame(item_rows)

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_main.to_excel(writer, sheet_name="Delivery Notes", index=False)
        if not df_items.empty:
            df_items.to_excel(writer, sheet_name="Line Items", index=False)

# =========================
# RUN
# =========================
print("🚀 Starting ADVANCED OCR Processing")

po_df = load_po_data(PO_FILE) if ENABLE_PO_MATCHING else None

results = []

for f in os.listdir(IMAGES_DIR):
    if f.lower().endswith((".png", ".jpg", ".jpeg")):
        print(f"📄 Processing: {f}")
        data = extract_from_image(os.path.join(IMAGES_DIR, f), po_df)
        results.append(data)

if results:
    export_to_excel(results, OUTPUT_FILE)
    print(f"✅ DONE! Excel created: {OUTPUT_FILE}")
else:
    print("❌ No images found")
