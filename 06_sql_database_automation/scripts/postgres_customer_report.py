import os
import smtplib
import psycopg2
import pandas as pd
from tabulate import tabulate
from email.message import EmailMessage

# ================== STEP 1: POSTGRESQL DB ==================

conn = psycopg2.connect(
    host="localhost",
    database="customer_reports",
    user="u0_a509",
    password=os.getenv("PG_PASSWORD"),
    port=5432
)

cursor = conn.cursor()

query = """
SELECT
    country,
    COUNT(*) AS total_customers
FROM customers
GROUP BY country
ORDER BY total_customers DESC;
"""

cursor.execute(query)
rows = cursor.fetchall()
conn.close()

print("PostgreSQL query executed")

# ================== STEP 2: TERMINAL OUTPUT ==================

def green(text):
    return f"\033[92m{text}\033[0m"

display_rows = [[c, green(t)] for c, t in rows]

print(
    tabulate(
        display_rows,
        headers=["Country", "Total_Customers"],
        tablefmt="grid",
        colalign=("center", "center")
    )
)

# ================== STEP 3: CSV ==================

os.makedirs("reports", exist_ok=True)
csv_path = "reports/country_customer_report_pg.csv"

df = pd.DataFrame(rows, columns=["Country", "Total_Customers"])
df.to_csv(csv_path, index=False)

print(f"CSV exported successfully → {csv_path}")

# ================== STEP 4: EMAIL (UNCHANGED) ==================

def send_email(csv_file):
    smtp_key = os.getenv("BREVO_SMTP_KEY")
    msg = EmailMessage()
    msg["Subject"] = "📊 PostgreSQL Customer Report"
    msg["From"] = "jitendrablog6@gmail.com"
    msg["To"] = "jitendrablog7@gmail.com"
    msg.set_content("PostgreSQL automated report attached.")

    with open(csv_file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename="country_customer_report_pg.csv"
        )

    with smtplib.SMTP("smtp-relay.brevo.com", 587) as server:
        server.starttls()
        server.login("9f859b001@smtp-brevo.com", smtp_key)
        server.send_message(msg)

    print("✓email sent successfully via BREVO SMPT")

send_email(csv_path)
