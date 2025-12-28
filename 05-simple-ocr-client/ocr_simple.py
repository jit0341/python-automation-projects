# ocr_simple.py
"""
Simple OCR for Delivery Notes
For: XYZ Client
Date: 28-Dec-2024
"""

import pytesseract
from PIL import Image
import pandas as pd
import os
import re

def extract_from_image(image_path):
    """Extract text and find required fields"""
    
    # Simple OCR - no preprocessing needed
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    
    # Find DN Number (format: DN-2024-001)
    dn_match = re.search(r'DN[-\s]?\d{4}[-\s]?\d{3}', text)
    dn_number = dn_match.group() if dn_match else "NOT FOUND"
    
    # Find Date (format: DD-MM-YYYY or DD/MM/YYYY)
    date_match = re.search(r'\d{2}[-/]\d{2}[-/]\d{4}', text)
    date = date_match.group() if date_match else "NOT FOUND"
    
    # Find Supplier (line after "Supplier:")
    supplier_match = re.search(r'Supplier[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
    supplier = supplier_match.group(1).strip() if supplier_match else "NOT FOUND"
    
    # Find Total (last number with $ or after "Total")
    total_match = re.search(r'Total[:\s]*\$?[\s]*(\d+\.?\d*)', text, re.IGNORECASE)
    total = total_match.group(1) if total_match else "0"
    
    return {
        'File': os.path.basename(image_path),
        'DN Number': dn_number,
        'Date': date,
        'Supplier': supplier,
        'Total Amount': total,
        'Review Status': 'NEEDS REVIEW'
    }

# Main
print("🚀 Starting OCR Processing...")
print()

results = []

# Process all images
for filename in os.listdir('images'):
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        print(f"Processing: {filename}")
        
        image_path = os.path.join('images', filename)
        data = extract_from_image(image_path)
        results.append(data)
        # Show what was found
        print(f"  ✓ DN: {data['DN Number']}")
        print(f"  ✓ Date: {data['Date']}")
        print(f"  ✓ Supplier: {data['Supplier']}")
        print(f"  ✓ Total: ${data['Total Amount']}")
        print()

# Export to Excel
if results:
    df = pd.DataFrame(results)
    output_file = 'output/delivery_notes.xlsx'
    df.to_excel(output_file, index=False)
    
    print("=" * 50)
    print(f"✅ DONE! Processed {len(results)} images")
    print(f"📊 Excel file: {output_file}")
    print("=" * 50)
else:
    print("❌ No images found in 'images' folder!")
