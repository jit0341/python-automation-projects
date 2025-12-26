 📊 CSV to Excel Automation (Python)
Designed to save hours of manual data cleaning for businesses and freelancers.
Client-ready automation system that cleans, validates, and converts raw CSV files into structured Excel reports.

Designed for **freelancers, small businesses, and data teams** who receive inconsistent CSV data from multiple clients.

---

## 🔹 Problem
Client CSV files often contain:
- Inconsistent column names (Name, customer_name, NAME)
- Duplicate records
- Missing critical values
- No standard reporting format

Manual cleaning is slow, error-prone, and not scalable.

---

## 🔹 Solution
This Python automation:
- Normalizes column names using aliases
- Validates required fields
- Removes duplicates and invalid rows
- Generates clean Excel reports
- Organizes outputs client-wise and date-wise
- Maintains detailed execution logs

The **same script works for multiple clients** by updating only the config file.

---

## ⚙️ Key Features
✔ Column normalization  
✔ Required column validation  
✔ Duplicate removal  
✔ Missing data handling  
✔ Client-wise output folders  
✔ Date-wise report organization  
✔ Detailed logging  
✔ Fully reusable automation  

---

## 🧰 Tech Stack
- Python
- pandas
- openpyxl

---

## 📁 Project Structure

02-csv-excel-automation/ │ ├── csv_to_excel_automation.py ├── config.py ├── data/ │   └── sales_data.csv ├── output/ │   └── ABC_Traders/2025-12-20/clean_sales_report.xlsx ├── logs/ │   └── automation.log └── README.md

---

## ⚙️ Configuration (config.py)
Client-specific settings are defined here:

```python
CLIENT_NAME = "ABC Traders"
INPUT_FILE = "data/sales_data.csv"
OUTPUT_FILE = "clean_sales_report.xlsx"

REQUIRED_COLUMNS = ["Name", "Product", "Amount", "City"]

COLUMN_ALIASES = {
    "Name": ["CustomerName", "customer_name", "NAME"],
    "Product": ["product", "Item"],
    "Amount": ["amount", "Total"],
    "City": ["city", "Location"]
}

👉 New client onboarding = update config only.


---

▶️ How to Run

pip install pandas openpyxl
python csv_to_excel_automation.py


---

📊 Output

Clean Excel report generated at:

output/<Client_Name>/<Date>/clean_sales_report.xlsx


---

📝 Logging

Execution logs stored in:

logs/automation.log

Includes validation results, cleaning stats, and timestamps.


---

🎯 Use Cases

Sales & GST reports

Business CSV cleanup

Client data standardization

Freelance automation tasks



---

👤 Author

Jitendra Bharti
Python Automation Developer
Freelance-ready, client-focused automation projects
🔗 This project is part of my Python Automation Portfolio and is actively used in freelance proposals.
