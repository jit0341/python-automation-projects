import psycopg2

conn = psycopg2.connect(
    dbname="sql_automation",
    user="u0_a509"
)

cur = conn.cursor()

cte_query = """
WITH order_summary AS (
    SELECT 
        customer_id,
        COUNT(*) AS total_orders
    FROM orders
    GROUP BY customer_id
)
SELECT 
    c.customer_name,
    COALESCE(os.total_orders, 0) AS total_orders
FROM customers c
LEFT JOIN order_summary os
ON c.customer_id = os.customer_id
ORDER BY total_orders DESC;
"""

cur.execute(cte_query)

rows = cur.fetchall()

print("Customer Order Summary:")
print("-----------------------")
for row in rows:
    print(row)

cur.close()
conn.close()
