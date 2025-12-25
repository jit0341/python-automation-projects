## Project: Folder file organiser

### Step 1- INPUTS
1. Source Folder Path
2. File type ~Destination Mapping
3. Move or copy mode (Future)

### Step 2- Validation
1. check source folder exists
2. check it is a directory
3. check folder is not empty
4. validate extension ~folder mappins
5. Prevent duplicate extentions

### Step 3- Scanning/Preparation
1. list all items inside source folder
2. Seperate files from folder
3. ignore hidden files.
4. Extract file extension
5. Mark unknown extemsions as 'Others'
"""File scan inside folder, ignore Hidden files,Identify extensions of each files.
"""
### Step 4- Business Rules
1. Map file extension to destination folder
2. Create destination folder if missing
3. Move file to destination folder
4. Skip file if same name exists
5. Handle errors gracefully (log and continue)
""" “File का extension देखूँगा,
destination decide करूँगा,
folder न हो तो बनाऊँगा,
file move करूँगा,
error आए तो skip करूँगा।”"""

### STEP 5 – Output

1. Create destination folders
2. Move files to respective folders
3. Skip files that cannot be moved
""" “Destination folders बनेंगे
और files अपने-अपने folder में move होंगी।”
"""
### STEP 6 – Report & Logging

1. Print summary in terminal
2. Log actions and errors
3. Handle errors without stopping program
4. Future: Dry-run / preview mode
""" “Program बताएगा क्या हुआ, log बनाएगा,
और error होने पर भी चलता रहेगा।” """

🧩 Final Design Notes (Complete Flow)
Copy code

STEP 1 – Inputs
STEP 2 – Validation
STEP 3 – Scan files
STEP 4 – Business rules
STEP 5 – Output (move files)
STEP 6 – Report & logging

👉 यही template
CSV → Excel
PDF Generator
Web Scraper
Email Automation
सब जगह चलेगा।
