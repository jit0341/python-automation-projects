import sqlite3
import os
import smtplib
from email.message import EmailMessage
from tabulate import tabulate
import pandas as pd

# ================== STEP 1: DATABASE + QUERY ==================

conn = sqlite3.connect("data/customers.db")
cursor = conn.cursor()

query = """
SELECT
    Country,
    COUNT(*) AS Total_Customers
FROM Customers
GROUP BY Country
ORDER BY Total_Customers DESC;
"""

cursor.execute(query)
rows = cursor.fetchall()
conn.close()

# ================== STEP 2: TERMINAL DISPLAY ==================

def green(text):
    return f"\033[92m{text}\033[0m"

display_rows = [[c, green(t)] for c, t in rows]

print("\n📊 Generated Report:\n")
print(
    tabulate(
        display_rows,
        headers=["Country", "Total_Customers"],
        tablefmt="grid",
        colalign=("center", "center")
    )
)

# ================== STEP 3: CSV EXPORT ==================

os.makedirs("reports", exist_ok=True)

csv_path = "reports/country_customer_report.csv"
df = pd.DataFrame(rows, columns=["Country", "Total_Customers"])
df.to_csv(csv_path, index=False)

# ================== STEP 4: EMAIL VIA BREVO SMTP ==================

def send_email(csv_file):
    smtp_key = os.getenv("BREVO_SMTP_KEY")

    if not smtp_key:
        raise ValueError("BREVO_SMTP_KEY not set")

    msg = EmailMessage()
    msg["Subject"] = "📊 Automated Customer Report (SQL + Python)"
    msg["From"] = "jitendrablog6@gmail.com"
    msg["To"] = "jitendrablog7@gmail.com"
    msg.set_content("Please find the attached customer distribution report.")

    with open(csv_file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename="country_customer_report.csv"
        )

    with smtplib.SMTP("smtp-relay.brevo.com", 587) as server:
        server.starttls()
        server.login("9f859b001@smtp-brevo.com", smtp_key)   # 👈 VERY IMPORTANT
        server.send_message(msg)

    print("\n✅ Email sent successfully via Brevo SMTP")

# ================== STEP 5: CALL EMAIL ==================

send_email(csv_path)
