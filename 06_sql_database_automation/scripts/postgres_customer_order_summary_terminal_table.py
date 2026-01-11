import psycopg2
from tabulate import tabulate

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

headers = ["Customer Name", "Total Orders"]
print(tabulate(rows, headers=headers, tablefmt="grid"))

cur.close()
conn.close()
