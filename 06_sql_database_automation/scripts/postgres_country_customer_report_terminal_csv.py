import psycopg2
import pandas as pd
from tabulate import tabulate

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="customer_reports",
    user="u0_a509",
    password="",
    host="localhost"
)

print("✅ Connected to PostgreSQL")

# SQL query
query = """
SELECT
    Country,
    COUNT(*) AS Total_Customers
FROM customers
GROUP BY Country
ORDER BY Total_Customers DESC;
"""

# Load into DataFrame
df = pd.read_sql(query, conn)

# Terminal output
print("\n📊 CUSTOMER REPORT (PostgreSQL)\n")
print(tabulate(df, headers="keys", tablefmt="psql"))

# CSV export
df.to_csv("../reports/country_customer_report_pg.csv", index=False)
print("\n✅ CSV saved in reports/ folder")

conn.close()
print("🔒 Connection closed")
