📂 Folder File Organizer – Python Automation

A lightweight Python automation tool that instantly organizes messy folders
(Downloads / Desktop / Client files) into clean, categorized directories.

Built for real-world use and freelancing delivery.

---

## 🚩 Problem

Unorganized folders waste time and reduce productivity.

Common issues:
- Mixed documents, images, videos in one place
- Manual sorting is slow and error-prone
- Repeated cleanup required

---

## ✅ Solution

This script automatically:
- Scans a target folder
- Detects file types by extension
- Creates category folders if missing
- Moves files safely
- Prints a clear summary report

Result: **Clean folders in seconds.**

---

## 🧠 How It Works (Professional Automation Pattern)

**Input → Validate → Scan → Decide → Act → Report**

1. Read folder contents  
2. Validate files (skip folders & script itself)  
3. Apply business rules (extension → folder)  
4. Create folders if needed  
5. Move files  
6. Display summary  

This pattern is reusable across automation projects.

---

## ▶️ How to Run

1. Place `organizer.py` inside the folder you want to organize  
2. Open terminal in that folder  
3. Run:

```bash
python organizer.py

📊 Example Output
Copy code

Folder Organizer Summary
------------------------
Total files found : 12
Files moved       : 9
Files skipped     : 3
Status            : Completed
🗂 Supported File Types
Category
Extensions
Images
.jpg, .png, .jpeg
Documents
.pdf, .docx, .txt
Videos
.mp4, .mkv
Others
All unmatched files
(Easily customizable)

🎯 Use Cases
Downloads folder cleanup
Office document organization
Client asset management
Automation demo for freelancing
🔮 Possible Enhancements
Dry-run mode (preview without moving)
Logging to file
CLI arguments (custom path)
Scheduled execution
👨‍💻 Author
Jitendra Bharti
Python Automation Developer
GitHub: https://github.com/jit0341
