
# 05-simple-ocr-client

## 🎯 Project Overview

Simple OCR (Optical Character Recognition) system to extract structured data from delivery note images and export to Excel.

**Use Case:** Automate manual data entry from delivery notes/invoices into Excel spreadsheets.

---

## ✨ Features

- Extract text from images (PNG, JPG, JPEG)
- Automatically identify key fields:
  - DN Number
  - Date
  - Supplier Name
  - Total Amount
- Export results to Excel (.xlsx)
- Batch process multiple images at once

---

## 📋 Requirements

### System Dependencies
```bash
# Install Tesseract OCR
sudo apt update
sudo apt install tesseract-ocr -y
```

### Python Packages
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
pytesseract==0.3.13
Pillow==11.0.0
pandas==2.2.0
openpyxl==3.1.5
```

---

## 🚀 Quick Start

### Step 1: Setup
```bash
# Clone or navigate to project
cd 05-simple-ocr-client

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Add Images
```bash
# Put your delivery note images in images/ folder
cp your_delivery_note.png images/
```

### Step 3: Run OCR
```bash
python ocr_simple.py
```

### Step 4: Get Results
```bash
# Excel output will be in output/ folder
# Open: output/delivery_notes.xlsx
```

---

## 📁 Project Structure

```
05-simple-ocr-client/
│
├── README.md              # This file
├── requirements.txt       # Python dependencies
│
├── ocr_simple.py         # Main OCR script
├── make_samples.py       # Create sample images for testing
│
├── images/               # Input folder (put images here)
│   ├── dn_001.png
│   ├── dn_002.png
│   └── dn_003.png
│
└── output/               # Output folder (Excel files)
    └── delivery_notes.xlsx
```

---

## 💻 Usage

### Basic Usage
```bash
# Process all images in images/ folder
python ocr_simple.py
```

### Create Sample Images (for testing)
```bash
# Generate 3 sample delivery notes
python make_samples.py
```

### Expected Output
```
🚀 Starting OCR Processing...

Processing: dn_001.png
  ✓ DN: DN-2024-001
  ✓ Date: 28-12-2024
  ✓ Supplier: ABC Suppliers Ltd
  ✓ Total: $1250.00

Processing: dn_002.png
  ✓ DN: DN-2024-002
  ✓ Date: 27-12-2024
  ✓ Supplier: XYZ Industries
  ✓ Total: $3500.00

==================================================
✅ DONE! Processed 2 images
📊 Excel file: output/delivery_notes.xlsx
==================================================
```

---

## 📊 Excel Output Format

| File | DN Number | Date | Supplier | Total Amount | Review Status|
|------|-----------|------|----------|--------------|----------|
| dn_001.png | DN-2024-001 | 28-12-2024 | ABC Suppliers Ltd | 1250.00 |NEEDS REVIEW|
| dn_002.png | DN-2024-002 | 27-12-2024 | XYZ Industries | 3500.00 | NEEDS REVIEW|

---

## 🔧 Customization

### Extract Additional Fields

Edit `ocr_simple.py` and add new regex patterns:

```python
# Example: Extract PO Number
po_match = re.search(r'PO[:\s]+([A-Z0-9-]+)', text)
po_number = po_match.group(1) if po_match else "NOT FOUND"
```

### Change Date Format

Modify the date regex pattern:

```python
# For DD/MM/YYYY format
date_match = re.search(r'\d{2}/\d{2}/\d{4}', text)

# For YYYY-MM-DD format
date_match = re.search(r'\d{4}-\d{2}-\d{2}', text)
```

---

## 🐛 Troubleshooting

### "Tesseract not found" Error
```bash
# Install Tesseract OCR
sudo apt install tesseract-ocr

# Verify installation
tesseract --version
```

### "No images found" Error
```bash
# Check images folder exists
ls images/

# Add some sample images
python make_samples.py
```

### Poor OCR Accuracy
- Ensure images are clear and high resolution
- Images should be well-lit
- Text should be horizontal (not rotated)
- Minimum recommended resolution: 300 DPI

---

## 📈 Improvements (Future)

- [ ] Add image preprocessing (contrast, brightness)
- [ ] Handle rotated/skewed images
- [ ] Support PDF input files
- [ ] Extract line items/table data
- [ ] Add GUI interface
- [ ] Email results automatically
- [ ] Support multiple languages

---

## 🤝 Use Cases

1. **Accounting Firms:** Digitize paper invoices
2. **Warehouses:** Process delivery notes
3. **Retail Stores:** Extract receipt data
4. **Import/Export:** Convert shipping documents
5. **Healthcare:** Digitize patient forms

---

## 💰 Commercial Use

This tool can be offered as a service:

**Pricing Ideas:**
- ₹5-10 per document processed
- ₹3,000-5,000 for custom implementation
- Monthly subscription for bulk processing

---

## 📝 Notes

- Supported formats: PNG, JPG, JPEG
- Max recommended image size: 5MB
- Processing time: ~2-3 seconds per image
- Accuracy: 85-95% (depends on image quality)

---

## 🔗 Related Projects

- **01-folder-file-organiser** - Organize extracted files
- **02-csv-to-excel-automation** - Further Excel processing
- **03-pdf-report-generator** - Generate reports from OCR data

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review sample images format
3. Verify Tesseract installation

---

## 📜 License

Free to use for personal and commercial projects.

---

## ✅ Success Checklist

- [x] Tesseract OCR installed
- [x] Python packages installed
- [x] Sample images created
- [x] First successful run
- [ ] Processed real documents
- [ ] Delivered to first client

---

**Created:** December 28, 2024  
**Version:** 1.0  
**Author:** Python Automation Projects Series

---

## 🎯 Quick Commands Reference

```bash
# Setup
pip install -r requirements.txt

# Test with samples
python make_samples.py
python ocr_simple.py

# Process your images
# 1. Copy images to images/ folder
# 2. Run: python ocr_simple.py
# 3. Check: output/delivery_notes.xlsx

# Done! 🎉
