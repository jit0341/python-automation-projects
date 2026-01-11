import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os
from tabulate import tabulate
from datetime import datetime

# =====================================================
# 1. PATH SETUP (Portable & Safe)
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "..", "data", "customers.db")
CSV_PATH = os.path.join(BASE_DIR, "..", "reports", "country_customer_report.csv")
IMG_PATH = os.path.join(BASE_DIR, "..", "reports", "customer_charts.png")

# =====================================================
# 2. TIMESTAMP
# =====================================================

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =====================================================
# 3. DATABASE CONNECTION & QUERY
# =====================================================

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    Country AS Country,
    COUNT(*) AS Total_Customers
FROM Customers
GROUP BY Country
ORDER BY Total_Customers DESC;
"""

df = pd.read_sql_query(query, conn)

# =====================================================
# 4. DATA VALIDATION & TERMINAL OUTPUT
# =====================================================

if df.empty:
    print("⚠️ No data found.")
    conn.close()
    exit()

print(f"\n📊 CUSTOMER REPORT SUMMARY ({now})")
print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))

# Save CSV
df.to_csv(CSV_PATH, index=False)

# =====================================================
# 5. DATA VISUALIZATION
# =====================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

# --- Bar Chart ---
bars = ax1.bar(df["Country"], df["Total_Customers"], color="skyblue")
ax1.set_title(f"Customer Count\nGenerated: {now}", fontsize=12)
ax1.set_xlabel("Country")
ax1.set_ylabel("Total Customers")
ax1.bar_label(bars, padding=3)

# --- Pie Chart ---
ax2.pie(
    df["Total_Customers"],
    labels=df["Country"],
    autopct="%1.1f%%",
    startangle=140
)
ax2.set_title("Market Share %", fontsize=12)

plt.tight_layout()
plt.savefig(IMG_PATH)
plt.close()

conn.close()

print("\n" + "=" * 55)
print(f"✅ Report Date: {now}")
print("✅ CSV & Charts saved in 'reports/' folder")
print("=" * 55 + "\n")
