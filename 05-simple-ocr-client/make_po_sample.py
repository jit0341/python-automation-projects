import pandas as pd

po_data = [
    {"Product Code": "ITEM001", "Product Name": "Widget A", "Ordered Qty": 50},
    {"Product Code": "ITEM002", "Product Name": "Widget B", "Ordered Qty": 30},
    {"Product Code": "PROD101", "Product Name": "Component X", "Ordered Qty": 100},
]

df = pd.DataFrame(po_data)
df.to_csv("po_data.csv", index=False)
print("✅ Sample PO data created: po_data.csv")
