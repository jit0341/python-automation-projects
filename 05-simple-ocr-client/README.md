

---

📄 Simple Delivery Note OCR — One-Click Automation

Photo / Image → Excel (Admin-Ready, Local & Offline)


---

🎯 Overview

A client-ready, one-click OCR automation system that converts delivery note images into clean, structured Excel reports — ready for admin review and upload into existing systems.

This tool is designed for real office workflows, not demos.

> ✔ Runs locally on the client’s computer
✔ No cloud uploads
✔ No ERP lock-in
✔ No automation theatre



The system prioritizes accuracy, transparency, and control, making it suitable for accounting teams, warehouses, and small businesses.


---

✅ What This Tool Does

📥 Input

Delivery note images (PNG / JPG / JPEG)

Optional PO reference file (po_data.csv)


📤 Output

Clean Excel file (.xlsx)

Structured, admin-friendly format

Ready for review and system upload


🔄 One-Click Workflow

1. Place images in the images/ folder


2. Run the script


3. Excel report is generated automatically


4. Admin reviews and uploads



> No manual copy-paste.
No repetitive data entry.




---

✨ Key Features

🔹 Core Capabilities

OCR using Tesseract

Batch image processing

Regex-based field extraction

Excel export (.xlsx)

Designed for reliability, not complexity


🔹 Extracted Fields

Delivery Note Number

Date

Supplier Name

Total Amount

Line Items (Advanced mode)

PO Quantity Match Status (optional)


🔹 Reliability-First Design

Image preprocessing (Advanced mode)

Review flags for mismatches

Raw OCR text visibility (debug option)

Clear, admin-friendly Excel output



---

🧩 Processing Modes

1️⃣ Basic OCR (Fast)

File: ocr_simple.py

What it does

Extracts key header fields only

Single Excel sheet

Fast and lightweight


Best for

Simple delivery notes

Low-volume work

Quick admin data entry


Run

python ocr_simple.py

Output

output/delivery_notes_basic.xlsx


---

2️⃣ Advanced OCR (Recommended)

File: ocr_advanced.py

What it does

Image preprocessing (OpenCV)

Line-item extraction

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

The screenshots in this repository demonstrate:

A typical delivery note image captured from a mobile device

OCR processing feedback in the terminal

Final Excel output with:

Summary sheet

Line-item & PO matching sheet



These examples show how unstructured images are converted into structured, review-ready Excel data suitable for real admin workflows.


---

⚡ Quick Demo (60 Seconds)

1️⃣ Install dependencies

pip install -r requirements.txt

2️⃣ Add delivery note images

cp your_image.png images/

3️⃣ Run Advanced OCR

python ocr_advanced.py

✔ Excel file generated in output/
✔ Ready for admin review & upload


---

📊 Excel Output Structure

Sheet 1 – Delivery Notes

| File | DN Number | Date | Supplier | Total | Items Count | Status |

Sheet 2 – Line Items

| DN Number | Item Code | Description | Quantity | Amount | PO Qty | Match Status |


---

📦 Requirements

🔹 System Dependency

Install Tesseract OCR

Linux / Termux

sudo apt install tesseract-ocr -y

Windows

Install Tesseract OCR

Ensure tesseract.exe is added to PATH


Verify installation:

tesseract --version

🔹 Python Packages

pip install -r requirements.txt

requirements.txt

pytesseract
Pillow
pandas
openpyxl
opencv-python
numpy


---

⚠️ Important Notes

This is a semi-automated system by design

Admin review is expected before upload

Handwritten or very low-quality images may need correction

Regex patterns can be adjusted per client document format



---

🧪 Accuracy Expectations

Clean images: 90–95%

Blurry / handwritten: manual review required

Accuracy improves with consistent document formats


> This balance between automation and review is intentional and practical.




---

🧠 Designed For

Accounting & admin teams

Warehouses & logistics

Small businesses

Freelancers handling document processing

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

🚀 Optional Next Improvements

PDF input support

Web upload interface

API integration

Multi-language OCR

Batch scheduler



---




