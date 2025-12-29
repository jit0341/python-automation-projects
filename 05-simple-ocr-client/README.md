📄 Simple Delivery Note OCR (Photo/PDF → Excel)

🎯 Overview

A lightweight, reliable OCR tool to extract structured data from delivery note images and export it into clean Excel sheets for admin review and upload into existing systems.

Designed for simplicity, accuracy, and human verification — not over-automation.


---

✅ What This Tool Does

Input

Delivery note images (PNG / JPG / JPEG)


Output

Structured Excel file with:

Delivery note summary

Optional line items

Review-friendly format



Workflow

1. Image → OCR


2. Key fields extracted


3. Optional PO matching


4. Excel export


5. Admin review & upload




---

✨ Key Features

Core Features

OCR using Tesseract

Batch processing of images

Regex-based field extraction

Excel export (.xlsx)


Extracted Fields

Delivery Note Number

Date

Supplier

Total Amount

Line Items (Advanced mode)


Reliability

Preprocessing for better OCR accuracy

Review flags for mismatches

Designed for human verification



---

🧩 Two Processing Modes

1️⃣ Basic OCR (Fast)

File: ocr_simple.py

Extracts main fields only

Single Excel sheet

Fast processing


Best for

Simple delivery notes

Low-volume work

Quick data entry


Run:

python ocr_simple.py

Output:

output/delivery_notes_basic.xlsx


---

2️⃣ Advanced OCR (Recommended)

File: ocr_advanced.py

Image preprocessing (OpenCV)

Line item extraction

PO quantity matching (optional)

Multi-sheet Excel output


Best for

Inventory workflows

Admin review

Client delivery


Run:

python ocr_advanced.py

Output:

output/delivery_notes_final.xlsx


---

📊 Excel Output Structure

Sheet 1: Delivery Notes

File	DN Number	Date	Supplier	Total	Items Count	Status



Sheet 2: Line Items

| DN Number | Item Code | Description | Quantity | Amount | PO Qty | Match Status |


---

📦 Requirements

System Dependency

Install Tesseract OCR:

pkg install tesseract
# or
sudo apt install tesseract-ocr -y

Verify:

tesseract --version

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

🚀 Quick Start

# Go to project
cd 05-simple-ocr-client

# Install dependencies
pip install -r requirements.txt

# (Optional) Generate sample images
python make_samples.py

# Add your images
cp your_image.png images/

# Run Advanced OCR
python ocr_advanced.py


---

📁 Project Structure

05-simple-ocr-client/
│
├── ocr_simple.py
├── ocr_advanced.py
├── make_samples.py
├── po_data.csv            # Optional
│
├── images/                # Input images
├── output/                # Excel output
└── README.md


---

⚠️ Important Notes

This tool is semi-automated by design

Admin review is expected

Handwritten text may require correction

Regex patterns can be customized per client format



---

🧪 Accuracy Expectations

Clean images: 90–95%

Blurry / handwritten: manual review needed

Accuracy improves with consistent document formats



---

🧠 Designed For

Accounting & Admin teams

Warehouses & logistics

Small businesses

Freelance document processing work

OCR-based automation projects



---

🛠 Customization Examples

Add PO Number:

po_match = re.search(r'PO[:\s]+([A-Z0-9-]+)', text)

Change date format:

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

