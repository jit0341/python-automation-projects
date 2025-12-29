📄 Simple Delivery Note OCR

Photo / Image → Excel (Admin-Ready)


---

🎯 Overview

A lightweight and reliable OCR tool to extract structured data from delivery note images and export it into clean Excel sheets for admin review and upload into existing systems.

This tool is intentionally simple — focused on accuracy, transparency, and human verification.
No ERP integrations. No automation theatre.


---

✅ What This Tool Does

Input

Delivery note images (PNG / JPG / JPEG)

Optional PO reference file (po_data.csv)


Output

Clean Excel file (.xlsx)

Ready for admin review and upload


Workflow

1. Image → OCR


2. Key fields extracted


3. Optional PO quantity matching


4. Excel export


5. Human review & upload




---

✨ Key Features

Core Capabilities

OCR using Tesseract

Batch image processing

Regex-based field extraction

Excel export (.xlsx)

Designed for reliability, not complexity


Extracted Fields

Delivery Note Number

Date

Supplier Name

Total Amount

Line Items (Advanced mode)

PO Quantity Match Status (optional)


Reliability First

Image preprocessing (Advanced mode)

Review flags for mismatches

Clear visibility of raw OCR text (debug option)

Admin-friendly output



---

🧩 Processing Modes

1️⃣ Basic OCR (Fast)

File: ocr_simple.py

What it does

Extracts main fields only

Single Excel sheet

Fast processing


Best for

Simple delivery notes

Low-volume work

Quick data entry


Run

python ocr_simple.py

Output

output/delivery_notes_basic.xlsx


---

2️⃣ Advanced OCR (Recommended)

File: ocr_advanced.py

What it does

Image preprocessing (OpenCV)

Line item extraction

Optional PO quantity matching

Multi-sheet Excel output


Best for

Inventory workflows

Admin verification

Client delivery & freelancing projects


Run

python ocr_advanced.py

Output

output/delivery_notes_final.xlsx


---

📸 Visual Examples

Sample Input – Delivery Note Image

This is a typical delivery note photo captured from a mobile device.
![Sample Delivery Note Input](screenshots/input_delivery_note.png)


---

OCR Processing – Terminal Output
![OCR Terminal Output](screenshots/terminal_output.png)



---

Excel Output Preview

Sheet 1 – Delivery Notes Summary 

Sheet 2 – Line Items & PO Matching 
![Excel Output](screenshots/excel_output.png)
> The output demonstrates how unstructured delivery note images
> are converted into clean, review-ready Excel data suitable for
> admin workflows and system uploads.
---

⚡ Quick Demo (60 Seconds)

# 1. Install dependencies
pip install -r requirements.txt

# 2. Add delivery note images
cp your_image.png images/

# 3. Run Advanced OCR
python ocr_advanced.py

Result

Excel file generated in output/

Ready for admin review & upload



---

📊 Excel Output Structure

Sheet 1 – Delivery Notes

| File | DN Number | Date | Supplier | Total | Items Count | Status |

Sheet 2 – Line Items

| DN Number | Item Code | Description | Quantity | Amount | PO Qty | Match Status |


---

📦 Requirements

System Dependency

Install Tesseract OCR

pkg install tesseract
# or
sudo apt install tesseract-ocr -y

Verify:

tesseract --version


---

Python Packages

pip install -r requirements.txt

requirements.txt

pytesseract
Pillow
pandas
openpyxl
opencv-python
numpy


---

📁 Project Structure

05-simple-ocr-client/
├── ocr_simple.py
├── ocr_advanced.py
├── make_samples.py
├── po_data.csv          # Optional (PO matching)
│
├── images/              # Input images
├── output/              # Excel output
├── screenshots/         # README visuals
└── README.md


---

⚠️ Important Notes

This is a semi-automated tool by design

Admin review is expected

Handwritten text may need correction

Regex patterns can be adjusted per client format



---

🧪 Accuracy Expectations

Clean images: 90–95%

Blurry / handwritten: manual review required

Accuracy improves with consistent document formats



---

🧠 Designed For

Accounting & admin teams

Warehouses & logistics

Small businesses

Freelancers doing document processing

OCR-based automation projects



---

🛠 Customization Examples

Add PO Number Extraction

po_match = re.search(r'PO[:\s]+([A-Z0-9-]+)', text)
po_number = po_match.group(1) if po_match else "NOT FOUND"

Change Date Format

re.search(r'\d{4}-\d{2}-\d{2}', text)


---

📜 License

Free to use for:

Personal projects

Client delivery

Commercial automation work



---

👤 Author

Python Automation Projects
Created & maintained by: jit0341


---

🚀 Next Improvements (Optional)

PDF input support

Web upload interface

API integration

Multi-language OCR

Batch scheduler



---

Built for real-world admin workflows — simple, reliable, and transparent.


---
