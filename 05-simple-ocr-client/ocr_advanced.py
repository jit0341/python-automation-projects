"""
Simple OCR for Delivery Notes - ADVANCED VERSION
For: XYZ Client
Date: 29-Dec-2024
Version: 2.0 (with preprocessing + item extraction)
"""

import pytesseract
from PIL import Image
import pandas as pd
import os
import re
import cv2
import numpy as np

def preprocess_image(image_path):
    """Enhance image quality for better OCR"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image could not be read: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced = cv2.equalizeHist(gray)
    denoised = cv2.fastNlMeansDenoising(enhanced)
    return denoised

def extract_items(text):
    """Extract line items from delivery note"""
    items = []
    pattern = r'([A-Z]{3,6}\d{3})\s+([A-Za-z\s]+)\s+(\d+)\s+\$?(\d+\.?\d*)'
    matches = re.findall(pattern, text)
    
    for match in matches:
        items.append({
            'Code': match[0],
            'Description': match[1].strip(),
            'Quantity': int(match[2]),
            'Amount': float(match[3])
        })
    return items

def extract_from_image(image_path):
    """Extract text and find required fields - ENHANCED"""
    
    print(f"  → Preprocessing image...")
    preprocessed = preprocess_image(image_path)
    pil_image = Image.fromarray(preprocessed)
    
    print(f"  → Extracting text with OCR...")
    text = pytesseract.image_to_string(
    pil_image,
    config='--psm 6'
)
    
    dn_match = re.search(r'DN[-\s]?\d{4}[-\s]?\d{3}', text)
    dn_number = dn_match.group() if dn_match else "NOT FOUND"
    
    date_match = re.search(r'\d{2}[-/]\d{2}[-/]\d{4}', text)
    date = date_match.group() if date_match else "NOT FOUND"
    supplier_match = re.search(r'Supplier[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
    supplier = supplier_match.group(1).strip() if supplier_match else "NOT FOUND"
    
    total_match = re.search(r'Total[:\s]*\$?[\s]*(\d+\.?\d*)', text, re.IGNORECASE)
    total = total_match.group(1) if total_match else "0"
    
    print(f"  → Extracting line items...")
    items = extract_items(text)
    # Amount consistency check
    try:
        total_amount = float(total)
    except:
        total_amount = 0.0


    if items and abs(sum(i['Amount'] for i in items) - total_amount) > 1:

        review_status = 'CHECK TOTAL MISMATCH'
    else:
        review_status = 'OK'
    
    return {
        'File': os.path.basename(image_path),
        'DN Number': dn_number,
        'Date': date,
        'Supplier': supplier,
        'Total Amount': total,
        'Items Count': len(items),
        'Items': items,
        'Review Status': review_status
    }

def export_to_excel(results, output_file='output/delivery_notes1.xlsx'):
    """Export results with items to Excel"""
    
    main_rows = []
    items_rows = []
    
    for result in results:
        main_rows.append({
            'File': result['File'],
            'DN Number': result['DN Number'],'Date': result['Date'],
            'Supplier': result['Supplier'],
            'Total Amount': result['Total Amount'],
            'Items Count': result['Items Count'],
            'Review Status': result['Review Status']
        })
        
        for item in result['Items']:
            items_rows.append({
                'DN Number': result['DN Number'],
                'Item Code': item['Code'],
                'Description': item['Description'],
                'Quantity': item['Quantity'],
                'Amount': item['Amount']
            })
    
    df_main = pd.DataFrame(main_rows)
    df_items = pd.DataFrame(items_rows)
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_main.to_excel(writer, sheet_name='Delivery Notes', index=False)
        if not df_items.empty:
            df_items.to_excel(writer, sheet_name='Line Items', index=False)
    
    return len(main_rows), len(items_rows)

# Main execution
print("🚀 Starting ADVANCEDOCR Processing...")
print("   ✓ Image preprocessing enabled")
print("   ✓ Line item extraction enabled")
print()

results = []

for filename in os.listdir('images'):
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        print(f"📄 Processing: {filename}")
        print("-" * 50)
        
        image_path = os.path.join('images', filename)
        data = extract_from_image(image_path)
        results.append(data)
        
        print(f"  ✓ DN: {data['DN Number']}")
        print(f"  ✓ Date: {data['Date']}")
        print(f"  ✓ Supplier: {data['Supplier']}")
        print(f"  ✓ Total: ${data['Total Amount']}")
        print(f"  ✓ Items Found: {data['Items Count']}")
        if data['Items']:
            print(f"  ✓ Line Items:")
            for item in data['Items']:
                print(f"     - {item['Code']}: {item['Description']} (Qty: {item['Quantity']}, ${item['Amount']})")
        print()

if results:
    output_file = 'output/delivery_notes1.xlsx'
    main_count, items_count = export_to_excel(results, output_file)
    
    print("=" * 60)
    print(f"✅ DONE! Processed {len(results)} images")
    print(f"📊 Excel file: {output_file}")
    print(f"   → Sheet 1 'Delivery Notes': {main_count} records")
    print(f"   → Sheet 2 'Line Items': {items_count} items")
    print("=" * 60)
else:
    print("❌ No images found in 'images' folder!")
