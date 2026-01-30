import os
import pandas as pd
from datetime import datetime
from core_agent_ready import process_invoice
from pathlib import Path
import xml.etree.ElementTree as ET

INPUT_DIR = "input"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_tally_xml(sales_rows, filename):
    root = ET.Element("ENVELOPE")
    body = ET.SubElement(root, "BODY")
    data = ET.SubElement(ET.SubElement(body, "IMPORTDATA"), "REQUESTDATA")

    for s in sales_rows:
        msg = ET.SubElement(data, "TALLYMESSAGE")
        v = ET.SubElement(msg, "VOUCHER", {"VCHTYPE": "Sales", "ACTION": "Create"})
        ET.SubElement(v, "DATE").text = s["InvoiceDate"].replace("-", "")
        ET.SubElement(v, "VOUCHERTYPENAME").text = "Sales"
        ET.SubElement(v, "REFERENCE").text = s["Invoice No"]
        ET.SubElement(v, "PARTYLEDGERNAME").text = s["Buyer Name"] or "UNKNOWN"
        ET.SubElement(v, "PERSISTEDVIEW").text = "Accounting Voucher View"

        l = ET.SubElement(v, "ALLLEDGERENTRIES.LIST")
        ET.SubElement(l, "LEDGERNAME").text = s["Buyer Name"] or "UNKNOWN"
        ET.SubElement(l, "ISDEEMEDPOSITIVE").text = "YES"
        ET.SubElement(l, "AMOUNT").text = f"-{s['Total']}"

    path = os.path.join(OUTPUT_DIR, filename)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path


def main():
    invoices, sales, inventory, missing = [], [], [], []

    for pdf in Path(INPUT_DIR).glob("*.pdf"):
        print(f"📄 Processing: {pdf.name}")
        inv_rows = process_invoice(str(pdf))

        for r in inv_rows:
            invoices.append(r)

            sales.append({
                "Invoice No": r["Invoice No"],
                "InvoiceDate": r["InvoiceDate"],
                "Buyer Name": r["Buyer Name"],
                "Buyer GSTIN": r["Buyer GSTIN"],
                "Total": r["Total"]
            })

    xlsx = os.path.join(
        OUTPUT_DIR,
        f"GST_REPORT_{datetime.now().strftime('%H%M%S')}.xlsx"
    )

    with pd.ExcelWriter(xlsx, engine="xlsxwriter") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(sales).to_excel(w, "Tally_Sales", index=False)
        pd.DataFrame(inventory).to_excel(w, "Tally_Inventory", index=False)
        pd.DataFrame(missing).to_excel(w, "Missing_Fields", index=False)

    xml = generate_tally_xml(sales, "TALLY_IMPORT.xml")

    print("✅ Excel:", xlsx)
    print("✅ XML:", xml)

if __name__ == "__main__":
    main()
