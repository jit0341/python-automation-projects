# File: automation_utils.py
# Your Personal Automation Library
# Reusable across ALL projects!

import pandas as pd
import os
import logging
from datetime import datetime
import json

# ============================================
# STEP 1: INPUT FUNCTIONS
# ============================================

def load_csv(path, encoding='utf-8'):
    """
    Universal CSV loader with error handling
    """
    if not os.path.exists(path):
        logging.error(f"File not found: {path}")
        print(f"❌ File not found: {path}")
        return None
    
    try:
        df = pd.read_csv(path, encoding=encoding)
        
        if df.empty:
            logging.error("CSV file is empty")
            print("❌ CSV file is empty")
            return None
        
        logging.info(f"Loaded {len(df)} rows from {path}")
        print(f"✅ Loaded {len(df)} rows successfully")
        return df
    
    except Exception as e:
        logging.error(f"Error reading CSV: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return None

def load_excel(path, sheet_name=0):
    """
    Universal Excel loader
    """
    if not os.path.exists(path):
        logging.error(f"File not found: {path}")
        return None
    
    try:
        df = pd.read_excel(path, sheet_name=sheet_name)
        logging.info(f"Loaded {len(df)} rows from Excel")
        return df
    except Exception as e:
        logging.error(f"Error reading Excel: {str(e)}")
        return None

def load_json(path):
    """
    Universal JSON loader
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info(f"Loaded JSON from {path}")
        return data
    except Exception as e:
        logging.error(f"Error reading JSON: {str(e)}")
        return None

# ============================================
# STEP 2: VALIDATION FUNCTIONS
# ============================================

def validate_columns(df, required_columns):
    """
    Universal column validator
    """
    missing = [c for c in required_columns if c not in df.columns]
    
    if missing:
        logging.error(f"Missing columns: {missing}")
        print(f"❌ Missing columns: {missing}")
        print(f"📋 Available: {list(df.columns)}")
        return False
    logging.info("All required columns present")
    return True

def validate_data_types(df, type_map):
    """
    Validate column data types
    type_map = {'Amount': 'numeric', 'Date': 'datetime'}
    """
    errors = []
    
    for col, expected_type in type_map.items():
        if col not in df.columns:
            continue
        
        if expected_type == 'numeric':
            if not pd.api.types.is_numeric_dtype(df[col]):
                errors.append(f"{col} should be numeric")
        
        elif expected_type == 'datetime':
            try:
                pd.to_datetime(df[col])
            except:
                errors.append(f"{col} should be datetime")
    
    if errors:
        logging.error(f"Type validation errors: {errors}")
        print(f"❌ Type errors: {errors}")
        return False
    return True

def validate_not_null(df, columns):
    """
    Check if specified columns have null values
    """
    null_counts = df[columns].isnull().sum()
    has_nulls = null_counts[null_counts > 0]
    
    if not has_nulls.empty:
        logging.warning(f"Null values found: {has_nulls.to_dict()}")
        print(f"⚠️ Null values: {has_nulls.to_dict()}")
        return False
    
    return True

# ============================================
# STEP 3: CLEANING FUNCTIONS
# ============================================

def remove_duplicates(df, subset=None):
    """
    Universal duplicate remover
    """
    initial = len(df)
    df = df.drop_duplicates(subset=subset)
    removed = initial - len(df)
    
    logging.info(f"Duplicates removed: {removed}")
    print(f"🧹 Duplicates removed: {removed}")
    return df, removed

def handle_missing_data(df, strategy='drop', fill_value=None):
    """
    Universal missing data handler
    strategy: 'drop', 'fill', 'forward', 'backward'
    """
    initial = len(df)
    
    if strategy == 'drop':
        df = df.dropna()
    elif strategy == 'fill':
        df = df.fillna(fill_value)
    elif strategy == 'forward':
        df = df.ffill()
    elif strategy == 'backward':
        df = df.bfill()
    
    removed = initial - len(df)
    logging.info(f"Missing data handled ({strategy}): {removed} rows affected")
    
    return df, removed

def normalize_columns(df, column_aliases):
    """
    Universal column normalizer
    """
    renamed = {}
    for standard_col, aliases in column_aliases.items():
        for col in df.columns:
            if col in aliases:
                renamed[col] = standard_col
                break
    
    df = df.rename(columns=renamed)
    logging.info(f"Columns normalized: {renamed}")
    
    return df

def clean_text_columns(df, columns):
    """
    Strip whitespace, convert to title case
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    
    return df

# ============================================
# STEP 4: BUSINESS RULES (CUSTOM PER PROJECT)
# ============================================

def apply_business_rules(df, rules_function):
    """
    Apply custom business logic
    rules_function: User-defined function
    """
    try:
        df = rules_function(df)
        logging.info("Business rules applied successfully")
        return df
    except Exception as e:
        logging.error(f"Error applying rules: {str(e)}")
        return df

# ============================================
# STEP 5: OUTPUT FUNCTIONS
# ============================================

def save_to_excel(df, path, sheet_name='Sheet1'):
    """
    Universal Excel saver
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_excel(path, sheet_name=sheet_name, index=False)
        logging.info(f"Excel saved: {path}")
        print(f"✅ Excel saved: {path}")
        return True
    except Exception as e:
        logging.error(f"Error saving Excel: {str(e)}")
        return False

def save_to_csv(df, path):
    """
    Universal CSV saver
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        logging.info(f"CSV saved: {path}")
        print(f"✅ CSV saved: {path}")
        return True
    except Exception as e:
        logging.error(f"Error saving CSV: {str(e)}")
        return False

def create_output_directory(client_name, base_dir='output'):
    """
    Create client-wise, date-wise output structure
    """
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(base_dir, client_name.replace(" ", "_"), today)
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir

# ============================================
# STEP 6: REPORTING & LOGGING
# ============================================

def setup_logging(log_file='logs/automation.log'):
    """
    Universal logging setup
    """
    if os.path.dirname(log_file):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Reset logging handlers to avoid duplicates
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    
    print(f"📝 Logging to: {log_file}")

def generate_summary_report(
    client_name,
    input_file,
    initial_rows,
    final_rows,
    operations,
    output_dir
):
    """
    Universal quality report generator
    """
    success_rate = (final_rows / initial_rows * 100) if initial_rows > 0 else 0
    
    report = f"""
╔══════════════════════════════════════════════════╗
║          AUTOMATION SUMMARY REPORT               ║
╚══════════════════════════════════════════════════╝

Client: {client_name}
Input File: {input_file}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DATA METRICS:
├─ Initial Rows: {initial_rows}
├─ Final Rows: {final_rows}
├─ Rows Removed: {initial_rows - final_rows}
└─ Success Rate: {success_rate:.1f}%

OPERATIONS PERFORMED:
"""
    
    for operation, count in operations.items():
        report += f"├─ {operation.title()}: {count}\n"
    
    report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: ✅ COMPLETED SUCCESSFULLY
"""
    
    report_path = os.path.join(output_dir, "automation_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    logging.info("Summary report generated")
    
    return report_path

# ============================================
# HELPER UTILITIES
# ============================================

def print_dataframe_info(df, title="DataFrame Info"):
    """
    Pretty print dataframe information
    """
    print(f"\n{'='*50}")
    print(f"📊 {title}")
    print(f"{'='*50}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Column Names: {list(df.columns)}")
    print(f"{'='*50}\n")

def timer_decorator(func):
    """
    Measure execution time
    """
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"⏱️ {func.__name__} took {end-start:.2f}s")
        return result
    return wrapper

# Database connection (future)
def connect_to_db(config):
    pass

# Email sending (future)
def send_email_report(to, subject, body, attachment):
    pass

# Web scraping base (for Project 4)
def fetch_webpage(url):
    pass

def parse_html(html):
    pass

# API calling (future)
def call_api(url, method, data):
    pass
