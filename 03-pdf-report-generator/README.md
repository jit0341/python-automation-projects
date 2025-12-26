# PDF Sales Report Generator (Python Automation)

This project demonstrates real-world PDF report generation using Python.  
It reads sales data from a CSV file and automatically generates a professional PDF summary report with totals.

---

## 🚀 Features

- Reads structured data from CSV  
- Generates clean, formatted PDF report  
- Calculates total revenue automatically  
- Safe to run multiple times (no “generate once” issue)  
- Well-commented code for learning & maintenance  

---

## 🛡️ Error Handling & Safety

- Verifies input CSV file existence before processing  
- Prevents PDF corruption by saving the canvas only once  
- Safe to re-run multiple times (existing PDF is overwritten)  
- Ensures numeric validation for revenue calculation  
- Gracefully exits if input data is missing or invalid  

---

## 📄 Example Output (PDF Content)

Sales Summary Report

Product     Quantity     Revenue

Laptop      5            250000 Mobile      10           200000 Tablet      3            45000


---

Total Revenue: INR 495000

*(Actual output is generated as a formatted PDF)*

---

## 🧩 Automation Design Pattern (6 Steps)

1. **Input Configuration**  
   - Define CSV input path and PDF output path  

2. **Input Validation**  
   - Check if CSV file exists before processing  

3. **Output Setup**  
   - Initialize PDF canvas with A4 layout  

4. **Core Processing**  
   - Read CSV row-by-row and write data into PDF  

5. **Business Logic**  
   - Calculate total revenue during iteration  

6. **Finalization**  
   - Write summary section and save the PDF safely  

---

## 📁 Project Structure

03-pdf-report-generator/ │ ├── data/ │   └── sales_summary.csv      # Input CSV data │ ├── output/ │   └── sales_report.pdf       # Generated PDF report │ ├── screenshots/ │   └── before_data.jpg        # CSV preview (optional) │ ├── pdf_report.py             # Main automation script └── README.md

---

## 🧾 Input CSV Format

The CSV file must contain the following headers:

Product,Quantity,Revenue Laptop,5,250000 Mobile,10,200000 Tablet,3,45000

---

## ▶️ How to Run

```bash
python pdf_report.py

Output:

---- Generating PDF report ----
✅ PDF generated successfully: output/sales_report.pdf


---

📌 Key Learning Points

PDF canvas must be saved only once

Variables inside functions are local (scope matters)

Layout positioning is critical in report generation

Automation scripts should be repeatable & safe



---

🧠 Real-World Use Cases

Sales summary reports

Invoice generation

Business analytics exports

Client deliverables automation



---

💼 Freelance & Real-World Use

This automation script can be customized for:

Sales & revenue summary reports

Invoice & billing PDF generation

Daily / monthly business reports

Client-branded PDF deliverables


Typical customization pricing:

Basic customization: ₹1000–1500

Advanced formatting & branding: ₹2000–3000



---

🧰 Technologies Used

Python

ReportLab

CSV module

File system handling



---

👨‍💻 Author

Jitendra Bharti
Python Automation Developer (PAD)
Focused on real-world automation & freelancing-ready projects.

-
