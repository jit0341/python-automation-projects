
# 📊 SQL Database Automation – Customer & Orders Reporting

## 🔍 Project Overview

This project demonstrates **production-style SQL database automation** using Python.

It simulates a real-world business scenario where **customer and order data** must be queried, analyzed, and converted into **client-ready reports** — without manual SQL work.

The project is intentionally designed to be:
- Freelancing-ready
- Client-verifiable
- Business-focused (not just SQL syntax)

---

## 🧠 Business Problem Simulated

A business wants to:

- Track customers and their orders
- Identify customers without orders
- Analyze order status (delivered vs pending)
- Generate country-wise order insights
- Automate reports using Python instead of manual queries

---

## 🗄️ Database Design

### Tables Used

**customers**
- customer_id (PK)
- customer_name
- country

**orders**
- order_id (PK)
- customer_id (FK)
- status
- order_date

🔗 Relationship:

customers.customer_id → orders.customer_id

---

## 🔗 SQL Concepts Demonstrated

- INNER JOIN
- LEFT JOIN
- RIGHT JOIN (simulated)
- FULL OUTER JOIN
- GROUP BY + COUNT
- HAVING clause
- Business-oriented reporting queries

📌 All JOIN outputs are captured as screenshots for proof.

---

## ⚙️ Automation with Python

Python scripts automate:

- PostgreSQL / SQLite database connections
- SQL execution via psycopg2
- Terminal-based reports
- CSV report generation (client-ready)

---

## 📁 Project Structure

06_sql_database_automation/ ├── README.md ├── data/ │   └── customers.db ├── scripts/ │   ├── terminal_customer_order_report.py │   ├── customer_order_report_csv.py │   ├── cte_customer_order_summary.py │   ├── postgres_customer_report.py │   └── test_pg_connection.py ├── reports/ │   └── customer_order_summary.csv ├── screenshots/ │   ├── terminal_customer_order_report.png │   ├── csv_report_preview.png │   └── join_results_proofs.png └── screenshots.md

---

## 🖼️ Screenshots & Proof

All SQL results and automation outputs are documented visually.

See full index here 👉 **[screenshots.md](screenshots.md)**

Examples:
- Terminal execution proof
- CSV report preview
- JOIN results
- Customers without orders
- Order status analysis

---

## 🚀 How to Run

1. Clone the repository
2. Navigate to the project folder
3. Ensure Python & PostgreSQL are installed
4. Run scripts:

```bash
python scripts/terminal_customer_order_report.py
python scripts/customer_order_report_csv.py


---

🛠️ Tech Stack

Python 3

PostgreSQL

SQLite

SQL

psycopg2

CSV reporting



---

🎯 What This Project Proves

Strong understanding of relational databases

Practical JOIN usage (business-driven)

PostgreSQL production usage

Python-based SQL automation

Freelancing & client-report mindset



---

👤 Author

Jitendra Bharti
Python | SQL | Automation
Focused on practical, freelance-ready solutions.

---
