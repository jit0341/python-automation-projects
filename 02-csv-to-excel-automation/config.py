# ================= CLIENT CONFIG =================

CLIENT_NAME = "ABC Traders"

INPUT_FILE = "data/sales_data.csv"
OUTPUT_FILE = "clean_sales_report.xlsx"

# ================= COLUMN RULES =================

REQUIRED_COLUMNS = ["Name", "Product", "Amount", "City"]

COLUMN_ALIASES = {
    "Name": ["CustomerName", "Customer Name", "customer_name", "NAME", "name"],
    "Product": ["product", "Item", "item_name"],
    "Amount": ["amount", "Price", "Total", "total_amount"],
    "City": ["city", "Location", "location"]
}

# Drop columns after cleaning
DROP_COLUMNS = ["City"]

# Final rename before export
FINAL_COLUMN_RENAME = {
    "Name": "CustomerName"
}
