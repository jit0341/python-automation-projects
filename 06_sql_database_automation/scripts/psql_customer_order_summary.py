import psycopg2

conn = psycopg2.connect(
    dbname="sql_automation",
    user="u0_a509",
    host="127.0.0.1",
    port="5432"
)

cur = conn.cursor()

query = """
SELECT c.customer_name, COUNT(o.order_id) AS order_count
FROM customers c
LEFT JOIN orders o
ON c.customer_id = o.customer_id
GROUP BY c.customer_name;
"""

cur.execute(query)

rows = cur.fetchall()
for row in rows:
    print(row)

cur.close()
conn.close()
