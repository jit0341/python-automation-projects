import os, re, sys, socket
import boto3
import pandas as pd
from pathlib import Path
from datetime import datetime, date

# ================== MODE ==================
PRODUCT_MODE = "DEMO"

# ================== PATHS =================
INPUT_DIR = "input"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================== DEMO CONFIG ==================
DEMO_DAYS = 10
DEMO_FILE = "demo_start.txt"

UPGRADE_UPI = "8871097310-2@ybl"
UPGRADE_MOBILE = "8871097310"

GSTIN_REGEX = r"\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]"

# ================== DEMO LOCK ==================
def demo_check():
    today = date.today()

    if not os.path.exists(DEMO_FILE):
        open(DEMO_FILE, "w").write(today.strftime("%Y-%m-%d"))
        return False  # not expired

    start = datetime.strptime(open(DEMO_FILE).read().strip(), "%Y-%m-%d").date()
    days_used = (today - start).days

    return days_used >= DEMO_DAYS

# ================== INTERNET ==================
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=4)
        return True
    except:
        return False

# ================== AWS ==================
def get_textract():
    return boto3.client("textract", region_name="ap-south-1")

textract = get_textract()

# ================== OCR CORE ==================
def analyze_pdf(path):
    return textract.analyze_document(
        Document={"Bytes": open(path, "rb").read()},
        FeatureTypes=["TABLES"]
    )["Blocks"]

def group_lines(blocks):
    words = [b for b in blocks if b["BlockType"] == "WORD"]
    lines = []
    for w in words:
        y = round(w["Geometry"]["BoundingBox"]["Top"], 3)
        for ln in lines:
            if abs(ln["y"] - y) < 0.01:
                ln["w"].append(w)
                break
        else:
            lines.append({"y": y, "w": [w]})

    for ln in lines:
        ln["w"].sort(key=lambda x: x["Geometry"]["BoundingBox"]["Left"])
        ln["text"] = " ".join(x["Text"] for x in ln["w"])

    return sorted(lines, key=lambda x: x["y"])

# ================== HEADER ==================
def extract_gstins(lines):
    gstins = re.findall(GSTIN_REGEX, " ".join(l["text"] for l in lines))
    return gstins[0] if len(gstins) > 0 else "", gstins[1] if len(gstins) > 1 else ""

def extract_date(lines):
    for l in lines:
        m = re.search(r"\d{2}-\d{2}-\d{4}", l["text"])
        if m:
            return m.group()
    return ""

def extract_total(lines):
    vals = []
    for l in lines:
        for n in re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?", l["text"]):
            try:
                v = float(n.replace(",", ""))
                if v > 500:
                    vals.append(v)
            except:
                pass
    return max(vals) if vals else 0.0

# ================== INVENTORY ==================
def extract_inventory(lines, inv_no):
    rows = []
    for l in lines:
        t = l["text"]

        if any(x in t.upper() for x in ["CGST", "SGST", "TOTAL", "TAX", "RATE"]):
            continue

        nums = re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?", t)
        if len(nums) < 2:
            continue

        taxable = float(nums[-1].replace(",", ""))
        qty = float(nums[0])

        name = re.sub(GSTIN_REGEX, "", t)
        name = re.sub(r"\d+(\.\d+)?", "", name)
        name = re.sub(r"[/%]", "", name)
        name = name.strip()

        if len(name) < 3:
            continue

        cgst_rate = sgst_rate = 9
        cgst_amt = round(taxable * cgst_rate / 100, 2)
        sgst_amt = round(taxable * sgst_rate / 100, 2)

        rows.append({
            "Invoice No": inv_no,
            "Item Name": name,
            "Qty": qty,
            "UOM": "Pcs.",
            "Taxable Value": taxable,
            "CGST Rate": cgst_rate,
            "CGST Amount": cgst_amt,
            "SGST Rate": sgst_rate,
            "SGST Amount": sgst_amt,
            "Line Total": round(taxable + cgst_amt + sgst_amt, 2),
            "⚠ DEMO": "UPGRADE REQUIRED"
        })

    return rows

# ================== MAIN ==================
def main():
    if not check_internet():
        print("❌ Internet required")
        return

    expired = demo_check()

    invoices, inventory, sales = [], [], []

    for pdf in Path(INPUT_DIR).glob("*.pdf"):
        blocks = analyze_pdf(pdf)
        lines = group_lines(blocks)

        sup_gst, buy_gst = extract_gstins(lines)
        inv_date = extract_date(lines)
        total = extract_total(lines)

        inv_no = pdf.stem

        invoices.append({
            "Invoice No": inv_no,
            "Invoice Date": inv_date,
            "Supplier Name": "AUTO OCR (95%)",
            "Supplier GSTIN": sup_gst,
            "Buyer Name": "MOBILE",
            "Buyer GSTIN": buy_gst,
            "Total Amount": total,
            "⚠ DEMO": "UPGRADE TO PRO",
            "File": pdf.name
        })

        inventory.extend(extract_inventory(lines, inv_no))

        sales.append({
            "VoucherType": "Sales",
            "Date": inv_date,
            "PartyName": "MOBILE",
            "Reference": inv_no,
            "Amount": total,
            "Narration": "DEMO VERSION"
        })

    dashboard = [{
        "Mode": "DEMO",
        "Status": "EXPIRED" if expired else "ACTIVE",
        "Invoices Found": len(invoices),
        "Inventory Rows": len(inventory),
        "Demo Days Limit": DEMO_DAYS,
        "Contact": UPGRADE_MOBILE,
        "UPI": UPGRADE_UPI,
        "Generated On": datetime.now().strftime("%d-%m-%Y %H:%M")
    }]

    out = os.path.join(OUTPUT_DIR, f"GST_DEMO_{datetime.now().strftime('%H%M')}.xlsx")

    with pd.ExcelWriter(out, engine="xlsxwriter") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(sales).to_excel(w, "Tally_Sales", index=False)
        pd.DataFrame(inventory).to_excel(w, "Tally_Inventory", index=False)
        pd.DataFrame(dashboard).to_excel(w, "Dashboard", index=False)

    if expired:
        print("🔒 DEMO EXPIRED — CONTACT FOR PRO")
    else:
        print("✅ DEMO ACTIVE")

    print("📂 Output:", out)

if __name__ == "__main__":
    main()
