import psycopg2
import csv

conn = psycopg2.connect(
    dbname="sql_automation",
    user="u0_a509",
    host="127.0.0.1"
)

cur = conn.cursor()

cur.execute("""
SELECT 
    c.customer_name,
    COUNT(o.order_id) AS order_count
FROM customers c
LEFT JOIN orders o
ON c.customer_id = o.customer_id
GROUP BY c.customer_name
ORDER BY order_count DESC;
""")

rows = cur.fetchall()

with open("reports/customer_order_summary.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["customer_name", "total_orders"])
    writer.writerows(rows)

print("✅ CSV report generated: reports/customer_order_summary.csv")

cur.close()
conn.close()
