#!/usr/bin/env python3
# =========================
# GST OCR – Demo v1.1
# Header + Inventory Focused Rewrite
# =========================

import os, re, sys, hashlib
from datetime import datetime
import pandas as pd
import boto3

# ================= CONFIG =================
GSTIN_REGEX = r"\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b"

IGNORE_KEYWORDS = [
    "gstin", "cgst", "sgst", "igst", "total", "round off",
    "grand total", "bank", "ifsc", "account", "address",
    "terms", "conditions", "authorized", "signature",
    "eway", "transport"
]

INVOICE_NO_KEYS = ["invoice", "inv no", "bill no", "tax invoice"]
DATE_REGEXES = [
    r"\b\d{2}[-/]\d{2}[-/]\d{4}\b",
    r"\b\d{4}[-/]\d{2}[-/]\d{2}\b"
]

# ================= TEXTRACT =================
def get_textract():
    return boto3.client("textract", region_name="ap-south-1")

def textract_text(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    client = get_textract()
    res = client.detect_document_text(Document={"Bytes": data})
    return [b["Text"] for b in res["Blocks"] if b["BlockType"] == "LINE"]

# ================= HELPERS =================
def normalize_amount(txt):
    txt = txt.replace(",", "").replace("₹", "")
    try:
        return float(re.findall(r"\d+\.\d+|\d+", txt)[0])
    except:
        return None

def find_invoice_no(lines):
    for i, l in enumerate(lines):
        low = l.lower()
        if any(k in low for k in INVOICE_NO_KEYS):
            if i + 1 < len(lines):
                return lines[i+1][:30]
            return l[-30:]
    return "NA"

def find_invoice_date(lines):
    for l in lines:
        for r in DATE_REGEXES:
            m = re.search(r, l)
            if m:
                return m.group()
    return "NA"

def extract_gstins(lines):
    found = re.findall(GSTIN_REGEX, " ".join(lines))
    unique = list(dict.fromkeys(found))
    if len(unique) >= 2:
        return unique[0], "HIGH", unique[1], "HIGH"
    if len(unique) == 1:
        return unique[0], "HIGH", "NA", "LOW"
    return "NA", "LOW", "NA", "LOW"

# ================= INVENTORY LOGIC =================
def inventory_score(line):
    score = 0
    if any(k in line.lower() for k in IGNORE_KEYWORDS):
        score -= 5
    if re.search(r"\d+\s*x\s*\d+", line.lower()):
        score += 5
    if re.search(r"\d+\.\d+", line):
        score += 2
    return score

def extract_inventory(lines, invoice_no):
    clean, rejected = [], []
    seen_amounts = set()

    for l in lines:
        amt = normalize_amount(l)
        if not amt:
            continue

        score = inventory_score(l)

        row = {
            "Invoice": invoice_no,
            "Item Text": l[:80],
            "Amount": amt,
            "Score": score
        }

        if score >= 2 and amt not in seen_amounts:
            clean.append(row)
            seen_amounts.add(amt)
        else:
            row["Reason"] = "Low score / duplicate"
            rejected.append(row)

    return clean, rejected

# ================= MAIN =================
def main(folder):
    textract = get_textract()
    invoices = []
    inventory_ok, inventory_bad = [], []
    sales = []
    gstin_rows = []
    amount_debug = []

    for f in os.listdir(folder):
        if not f.lower().endswith((".pdf", ".jpg", ".png", ".jpeg")):
            continue

        path = os.path.join(folder, f)
        lines = textract_text(path)

        invoice_no = find_invoice_no(lines)
        invoice_date = find_invoice_date(lines)
        sup_gstin, sup_conf, buy_gstin, buy_conf = extract_gstins(lines)

        amounts = [normalize_amount(l) for l in lines if normalize_amount(l)]
        invoice_total = max(amounts) if amounts else 0

        invoices.append({
            "Invoice No": invoice_no,
            "Invoice Date": invoice_date,
            "Supplier GSTIN": sup_gstin,
            "Supplier Conf": sup_conf,
            "Buyer GSTIN": buy_gstin,
            "Buyer Conf": buy_conf,
            "Invoice Amount": invoice_total,
            "File": f
        })

        gstin_rows.append({
            "Invoice": invoice_no,
            "Supplier GSTIN": sup_gstin,
            "Supplier Conf": sup_conf,
            "Buyer GSTIN": buy_gstin,
            "Buyer Conf": buy_conf
        })

        amount_debug += [{"Invoice": invoice_no, "Raw Amount": a} for a in amounts]

        inv_ok, inv_bad = extract_inventory(lines, invoice_no)
        inventory_ok += inv_ok
        inventory_bad += inv_bad

        sales.append({
            "Voucher Type": "Sales",
            "Date": invoice_date,
            "Reference": invoice_no,
            "Amount": invoice_total,
            "Narration": "OCR AUTO – VERIFY"
        })

    os.makedirs("output", exist_ok=True)
    out = f"output/GST_OUTPUT_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

    with pd.ExcelWriter(out, engine="openpyxl") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(inventory_ok).to_excel(w, "Inventory_Clean", index=False)
        pd.DataFrame(inventory_bad).to_excel(w, "Inventory_Rejected", index=False)
        pd.DataFrame(sales).to_excel(w, "Sales", index=False)
        pd.DataFrame(gstin_rows).to_excel(w, "GSTIN_Found", index=False)
        pd.DataFrame(amount_debug).to_excel(w, "Amounts_Debug", index=False)
        pd.DataFrame([{
            "Invoices": len(invoices),
            "Inventory OK": len(inventory_ok),
            "Inventory Rejected": len(inventory_bad),
            "Generated On": datetime.now().strftime("%d-%m-%Y")
        }]).to_excel(w, "Dashboard", index=False)

    print(f"✅ DONE: {out}")

# ================= RUN =================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gst_ocr_demo_v11.py <folder>")
        sys.exit(1)
    main(sys.argv[1])
