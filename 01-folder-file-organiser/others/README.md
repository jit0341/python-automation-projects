

📁 Folder File Organizer (Python Automation)

A professional Python automation script that organizes files into folders based on file type.
Designed for real-world use, learning clarity, and freelancing delivery.


---

🔍 Problem

Many users keep all files in a single folder (Downloads / Desktop).
Over time this leads to:

Difficulty finding files

Wasted time

Poor file hygiene


Manual organization is repetitive and error-prone.


---

💡 Solution

This script automatically:

Scans a target folder

Identifies file types using extensions

Creates folders if needed

Moves files to the correct location

Displays a clear summary report


Result: Clean, structured folders in seconds.


---

🧠 How the Script Works (6-Step Logic)

This project follows a clear 6-step automation framework
(the same framework used in all professional automation projects).

Step 1 — Inputs & Setup

Define source folder

Define file type → folder mapping

Initialize counters (total, moved, skipped)


Step 2 — Validation

Process only files (skip folders)

Skip the script file itself


Step 3 — Scan Files

Loop through all items in the source directory

Identify valid files


Step 4 — Business Rules

Extract file extension

Match extension against predefined rules

Decide destination folder

Default to Others if no match


Step 5 — Action

Create destination folders if missing

Move files to appropriate folders

Update counters


Step 6 — Report

Print a summary:

Total files found

Files moved

Files skipped

Final status



> Core Pattern:
Input → Validate → Scan → Decide → Act → Report




---

▶️ How to Run

1. Place organizer.py inside the folder you want to organize


2. Open terminal in that folder


3. Run:



python organizer.py


---

📊 Example Output

📊 Folder Organizer Summary
---------------------------
Total files found : 12
Files moved       : 9
Files skipped     : 3
Status            : Completed


---

🗂 Supported File Types

Category	Extensions

Images	.jpg, .png, .jpeg
Documents	.pdf, .docx, .txt
Videos	.mp4, .mkv
Others	All unmatched types


> File mappings can be customized easily.




---

🛠 Tools Used

Python 3

os module

shutil module


No external libraries required.


---

🎯 Use Cases

Downloads folder cleanup

Office file organization

Student project folders

Freelancers managing client assets

Small business document hygiene



---

🔮 Future Enhancements

Logging to file

Dry-run mode (preview without moving files)

CLI arguments (custom paths)

GUI version



---

💰 Freelancing Use

This script can be customized for clients:

Custom folder rules

Scheduled automation

Enterprise folder structures


> Ready for delivery as a standalone automation script.




---

👨‍💻 Author

Jitendra Bharti
Python Automation Developer (PAD)

Focused on:

Real-world automation

Process clarity

Freelancing-ready Python projects


📧 Email: jitendrablog6@gmail.com


---

📜 License

MIT License
Free to use, modify, and distribute with attribution.


---
