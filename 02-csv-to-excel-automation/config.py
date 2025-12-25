# Client Configuration

CLIENT_NAME = "ABC Traders"
REPORT_TITLE = "Monthly Sales Report"

INPUT_FILE = "data/sales_data.csv"
OUTPUT_FILE = "clean_sales_report.xlsx"

REQUIRED_COLUMNS = ["Name", "Product", "Amount", "City"]

# Acceptable alternate column name

COLUMN_ALIASES = {
    "Name": ["CustomerName", "Customer Name", "customer_name", "NAME", "name"],
    "Product": ["product", "Item", "item_name"],
    "Amount": ["amount", "Price", "Total", "total_amount"],
    "City": ["city", "Location", "location"]
}



# ---------------- COLUMN TRANSFORM RULES ----------------

# Rename columns AFTER normalization
COLUMN_RENAME_RULES = {
    "Name": "CustomerName"
}

# Columns to drop
COLUMNS_TO_DROP = ["City"]

# Extra columns to add (column_name: default_value)
EXTRA_COLUMNS = {
    "ProcessedDate": "AUTO"
}

# Columns to drop (client specific)
DROP_COLUMNS = ["City"]

# Final column rename before export
FINAL_COLUMN_RENAME = {
    "Name": "CustomerName"
}
