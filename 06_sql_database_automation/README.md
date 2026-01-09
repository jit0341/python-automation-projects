
---

📊 SQL Database Automation – Customer & Orders Reporting

🔍 Project Overview

This project demonstrates end-to-end SQL database handling and reporting automation using Python.

The focus is on:

Designing and querying relational databases

Performing SQL JOIN operations for business insights

Automating data extraction, analysis, and report generation

Working with both SQLite and PostgreSQL


This project simulates a real-world client scenario where customer and order data must be analyzed and converted into meaningful reports.


---

🧠 Business Problem Simulated

A business wants to:

Track customers and their orders

Identify customers without orders

Analyze order status (delivered vs pending)

Generate country-wise customer reports

Automate reports using Python instead of manual SQL work



---

🗄️ Database Structure

Tables Used

customers

customer_id

customer_name

country


orders

order_id

customer_id

status


Relational link:

customers.customer_id → orders.customer_id


---

🔗 SQL Concepts Demonstrated

INNER JOIN

LEFT JOIN

RIGHT JOIN (simulated)

FULL OUTER JOIN (using UNION)

Filtering with WHERE

Aggregation with COUNT

Business-focused queries (not just syntax)


All JOIN outputs are captured as screenshots for proof.


---

⚙️ Automation with Python

Python scripts automate:

Connecting to SQLite / PostgreSQL databases

Running SQL queries

Generating CSV reports

Preparing data for visualization or email delivery



---

📁 Project Structure

06_sql_database_automation/
├── README.md
├── data/
│   └── customers.db
├── scripts/
│   ├── customer_report_automation.py
│   ├── generate_country_report.py
│   ├── generate_country_report_pg.py
│   └── postgres_customer_report.py
├── reports/
├── screenshots/
│   ├── join proofs
│   ├── customers without orders
│   ├── order status analysis
│   └── terminal output
└── screenshots.md


---

🖼️ Screenshots & Proof

The screenshots/ folder contains:

SQL JOIN results

Business queries output

Terminal execution proof


This ensures transparent verification of results, useful for clients and reviewers.


---

🛠️ Tech Stack

Python 3

SQLite

PostgreSQL

SQL

CSV Reporting



---

🚀 How to Run

1. Clone the repository


2. Navigate to the project folder


3. Ensure Python is installed


4. Run any script from scripts/:

python generate_country_report.py




---

🎯 What This Project Proves

Strong understanding of relational databases

Ability to write business-oriented SQL queries

Practical experience with JOINs

Skill in Python-based database automation

Client-ready reporting mindset



---

👤 Author

Jitendra Bharti
Python | SQL | Automation
Focused on practical, freelance-ready solutions.


---

