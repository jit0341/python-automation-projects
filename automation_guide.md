# 🚀 Automation Utils: Developer Guide
**Internal documentation for using the Automation Library.**

This file explains the workflow of `automation_utils.py` so you can quickly implement it in any new project.

---

## 🛠 Project Structure
To keep your work professional, follow this folder structure:

/Project_Root
│
├── automation_utils.py    <-- The Library
├── main.py                <-- Your Logic
├── AUTOMATION_GUIDE.md    <-- This Guide
├── logs/                  <-- Auto-generated
└── output/                <-- Results (Client > Date > Files)

---

## 🔄 The 5-Step Workflow (Kaam Karne Ka Sahi Tareeka)



### Step 1: Initialization
Start by setting up logs and loading your data.
- `setup_logging()`: Track errors and progress.
- `load_csv()` / `load_excel()`: Universal loaders with error handling.

### Step 2: Data Validation
Make sure the input file is correct before processing.
- `validate_columns()`: Check if required columns exist.
- `validate_data_types()`: Check if Numbers are Numbers and Dates are Dates.

### Step 3: Cleaning & Normalization
- `remove_duplicates()`: Auto-clean repetitive rows.
- `handle_missing_data()`: Choose 'drop' or 'fill' strategy.
- `clean_text_columns()`: Strip spaces and fix Title Case.

### Step 4: Business Rules (The Brain)
Create a function for the client's specific logic and pass it to:
- `apply_business_rules(df, your_logic_function)`

### Step 5: Professional Output
- `create_output_directory()`: Organizes files by Client Name and Date.
- `save_to_excel()`: Exports the clean data.
- `generate_summary_report()`: Generates a high-quality audit report for the client.

---

## 💡 Quick Tips for Neovim Users
- This file uses **English & Hinglish** to ensure perfect rendering in terminal editors.
- All code examples are compatible with standard Python environments.
- Use `timer_decorator` on your functions to see how fast your automation is running.

---

## 📝 Automation Summary Preview
Every time you run the script, it generates a report like this:
- Initial Rows: 1000
- Final Rows: 950
- Efficiency: 95.0%
- Status: COMPLETED SUCCESSFULLY

