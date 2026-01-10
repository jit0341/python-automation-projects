import pandas as pd

# Load data
df = pd.read_csv("data/sales_data.csv")

# Basic cleaning
df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Remove invalid rows (amount <= 0)
clean_df = df[df["amount"] > 0].copy()

print("Raw rows:", len(df))
print("Clean rows:", len(clean_df))
print("\nPreview:")
print(clean_df.head())

# Save cleaned data
clean_df.to_csv("reports/clean_sales_data.csv", index=False)
print("\n✅ Cleaned data saved to reports/clean_sales_data.csv")
