
---

📊 Customer Order Analytics & Automated Reporting System

(PostgreSQL + Python)

🔍 Project Overview

This project demonstrates production-grade SQL database automation using PostgreSQL and Python.

It simulates a real-world business reporting system where customer and order data is queried, analyzed, and automatically converted into client-ready reports — eliminating the need for manual SQL execution.

The project is intentionally designed to be:

✅ Freelancing-ready

✅ Client-verifiable (with screenshots & outputs)

✅ Business-focused (not just SQL syntax practice)



---

🧠 Business Problem Simulated

A business wants to:

Track customers and their orders

Identify customers who have never placed orders

Analyze order status (Delivered vs Pending)

Generate country-wise customer insights

Automate recurring SQL reports using Python instead of manual queries


This project solves all of the above using PostgreSQL-driven SQL logic and Python automation.


---

🗄️ Database Design

Tables Used

customers

customer_id (Primary Key)

customer_name

country


orders

order_id (Primary Key)

customer_id (Foreign Key)

status

order_date


Relationship

customers.customer_id → orders.customer_id


---

🔗 SQL Concepts Demonstrated

This project showcases business-oriented SQL usage, including:

INNER JOIN

LEFT JOIN

RIGHT JOIN (simulated logic)

FULL OUTER JOIN

GROUP BY with COUNT & SUM

HAVING clause

CTE-based summary queries


📌 All JOIN results and outputs are captured as screenshots for verification.


---

⚙️ Automation with Python

Python scripts are used to automate:

PostgreSQL & SQLite database connections

SQL execution using psycopg2

Terminal-based analytical reports

CSV report generation (client-deliverable format)


This mirrors real freelance and production workflows, where SQL runs are automated rather than manual.


---

📁 Project Structure

06_sql_database_automation/
├── README.md
├── data/
│   └── customers.db
├── scripts/
│   ├── terminal_customer_order_report.py
│   ├── customer_order_report_csv.py
│   ├── cte_customer_order_summary.py
│   ├── postgres_customer_report.py
│   └── test_pg_connection.py
├── reports/
│   └── customer_order_summary.csv
├── screenshots/
│   ├── terminal_customer_order_report.png
│   ├── csv_report_preview.png
│   └── join_results_proofs.png
└── screenshots.md


---

🖼️ Screenshots & Proof

All SQL queries and automation outputs are documented visually for transparency and client verification.

📌 Full screenshot index available here → screenshots.md

Included proofs:

Terminal execution output

CSV report preview

JOIN results

Customers without orders

Order status analysis



---

🚀 How to Run

1. Clone the repository


2. Navigate to the project directory


3. Ensure Python and PostgreSQL are installed


4. Run automation scripts:



python scripts/terminal_customer_order_report.py
python scripts/customer_order_report_csv.py


---

🛠️ Tech Stack

Python 3

PostgreSQL

SQLite

SQL

psycopg2

CSV Reporting



---

🎯 What This Project Demonstrates

Strong understanding of relational database design

Practical, business-driven SQL JOIN usage

PostgreSQL usage in production-style scenarios

Python-based SQL automation

Freelancing-ready reporting mindset



---

👤 Author

Jitendra Bharti
Python | SQL | Automation
Focused on building practical, client-ready data solutions
