
import pandas as pd
import os
import logging
import argparse
from datetime import datetime

from config import CLIENT_NAME, INPUT_FILE, OUTPUT_FILE, REQUIRED_COLUMNS
from config import COLUMN_ALIASES


# ---------------- LOGGING ----------------
logging.basicConfig(
    filename="logs/automation.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ---------------- ARGUMENT PARSER ----------------
def parse_arguments():
    parser = argparse.ArgumentParser(description="CSV to Excel Automation")
    parser.add_argument("--client", default=CLIENT_NAME)
    parser.add_argument("--input", default=INPUT_FILE)
    parser.add_argument("--output", default=OUTPUT_FILE)
    return parser.parse_args()

# ---------------- LOAD CSV ----------------
def load_csv(path):
    if not os.path.exists(path):
        logging.error(f"Input file not found: {path}")
        print(f"❌ File not found: {path}")
        return None

    try:
        df = pd.read_csv(path)
        
        if df.empty:
            logging.error("CSV file is empty")
            print("❌ CSV file is empty")
            return None
        
        return df
    except Exception as e:
        logging.error(f"Error reading CSV: {str(e)}")
        print(f"❌ Error reading CSV: {str(e)}")
        return None

# ---------------- COLUMN NORMALISE ----------------
def normalize_columns(df, column_aliases):
    """
    Rename columns to standard names using aliases
    """
    renamed = {}

    for standard_col, aliases in column_aliases.items():
        for col in df.columns:
            if col in aliases:
                renamed[col] = standard_col
                break  # Stop after first match

    df = df.rename(columns=renamed)
    return df

# ---------------- COLUMN VALIDATION ----------------
def validate_columns(df, required_columns):
    missing = [c for c in required_columns if c not in df.columns]

    if missing:
        logging.error(f"Missing required columns: {missing}")
        print(f"❌ Missing required columns: {missing}")
        print(f"📋 Available columns: {list(df.columns)}")
        print("💡 Please fix the CSV and try again.")
        return False

    logging.info("All required columns present")
    return True
# -------------Column Rules apply ------------------------------
def apply_column_rules(df, drop_columns, rename_map):
    """
    Apply client specific column rules
    """
    # Drop unwanted columns
    df = df.drop(columns=[c for c in drop_columns if c in df.columns])

    # Rename final columns
    df = df.rename(columns=rename_map)

    return df

# ---------------- CLEAN DATA ----------------
def clean_data(df):
    initial_rows = len(df)

    # Remove duplicates
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)

    # Remove rows with missing names
    df = df.dropna(subset=["Name"])
    missing_names_removed = initial_rows - duplicates_removed - len(df)

    return df, duplicates_removed, missing_names_removed, initial_rows

# -------Helper Function ------------------------------------

def create_output_path(client):
    today = datetime.now().strftime("%Y-%m-%d")
    base_dir = os.path.join("output", client.replace(" ", "_"), today)
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

# ---------Generate Quality Report --------------------------

def generate_quality_report(
    client,
    input_file,
    initial_rows,
    duplicates_removed,
    missing_removed,
    final_rows,
    output_dir
):
    success_rate = (final_rows / initial_rows) * 100

    report = f"""
Client: {client}
Input File: {input_file}

Initial Rows: {initial_rows}
Duplicates Removed: {duplicates_removed}
Missing Names Removed: {missing_removed}
Final Rows: {final_rows}
Success Rate: {success_rate:.1f}%
"""

    report_path = os.path.join(output_dir, "data_quality_report.txt")
    with open(report_path, "w") as f:
        f.write(report)

        logging.info("Data quality report generated")

# ---------------- MAIN AUTOMATION ----------------
def csv_to_excel_automation():
    args = parse_arguments()
    client = args.client
    input_file = args.input
    output_file = args.output
    output_dir = create_output_path(client)
    output_file = os.path.join(output_dir, OUTPUT_FILE)

    logging.info(f"Automation started for client: {client}")
    print(f"🚀 Processing started for client: {client}")

    # Load CSV
    df = load_csv(input_file)
    if df is None:
        return

    # Normalize column names
    df = normalize_columns(df, COLUMN_ALIASES)
    print("\n🧪 Columns after normalization:")
    print(df.columns.tolist())
    logging.info(f"Columns after normalization: {df.columns.tolist()}")

    # Validate required c
    if not validate_columns(df, REQUIRED_COLUMNS):
        return

    print("\n📊 Raw Data:")
    print(df.head())

    # Clean data
    df, dup_removed, missing_removed, initial_rows = clean_data(df)

    from config import DROP_COLUMNS, FINAL_COLUMN_RENAME

    df = apply_column_rules(df, DROP_COLUMNS, FINAL_COLUMN_RENAME)

    logging.info(f"Duplicates removed: {dup_removed}")
    logging.info(f"Missing names removed: {missing_removed}")
    logging.info(f"Final rows: {len(df)}")

    print("\n🧹 Cleaning Summary")
    print(f"Initial rows: {initial_rows}")
    print(f"Duplicates removed: {dup_removed}")
    print(f"Missing names removed: {missing_removed}")
    print(f"Final rows: {len(df)}")

    # Export to Excel
    df.to_excel(output_file, index=False, engine="openpyxl")
    generate_quality_report(
    client,
    input_file,
    initial_rows,
    dup_removed,
    missing_removed,
    len(df),
    output_dir
)
    logging.info(f"Excel exported: {output_file}")

    print(f"\n✅ Excel file created: {output_file}")
    print("\n🏁 Automation finished successfully")

# ---------------- RUN ----------------
if __name__ == "__main__":
    csv_to_excel_automation()

