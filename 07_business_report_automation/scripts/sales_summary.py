import pandas as pd

df = pd.read_csv("reports/clean_sales_data.csv")

total_sales = df["amount"].sum()
orders_count = len(df)
country_summary = df.groupby("country")["amount"].sum().sort_values(ascending=False)

print("📊 SALES SUMMARY")
print("----------------")
print("Total Orders:", orders_count)
print("Total Sales:", total_sales)
print("\nSales by Country:")
print(country_summary)

# Save summary
country_summary.reset_index().to_csv(
    "reports/country_sales_summary.csv", index=False
)

print("\n✅ Country-wise summary saved to reports/country_sales_summary.csv")
