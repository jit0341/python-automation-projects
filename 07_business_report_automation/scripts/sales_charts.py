import pandas as pd
import matplotlib.pyplot as plt

# Load summary data
df = pd.read_csv("reports/country_sales_summary.csv")

# -------- Bar Chart --------
plt.figure()
plt.bar(df["country"], df["amount"])
plt.title("Sales by Country")
plt.xlabel("Country")
plt.ylabel("Total Sales")
plt.tight_layout()
plt.savefig("reports/sales_by_country_bar.png")
plt.close()

# -------- Pie Chart --------
plt.figure()
plt.pie(
    df["amount"],
    labels=df["country"],
    autopct="%1.1f%%",
    startangle=140
)
plt.title("Sales Share by Country")
plt.tight_layout()
plt.savefig("reports/sales_share_pie.png")
plt.close()

print("✅ Charts generated:")
print(" - reports/sales_by_country_bar.png")
print(" - reports/sales_share_pie.png")
