#!/usr/bin/env python3
# ==================================================
# GST OCR – Demo v1.2
# Q1 Implemented: Reconciliation + GSTIN Risk + Tax Boundary
# ==================================================

import os, re, sys
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

RECON_TOLERANCE = 2.0  # ₹ rounding tolerance

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
                return lines[i + 1][:30]
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

def gstin_risk_flag(sup, sup_conf, buy, buy_conf):
    if sup == "NA" and buy == "NA":
        return "NO_GSTIN"
    if buy == "NA":
        return "SINGLE_GSTIN_ONLY"
    if sup == buy:
        return "POSSIBLE_SWAP"
    if sup_conf != "HIGH" or buy_conf != "HIGH":
        return "LOW_CONFIDENCE"
    return "OK"

# ================= INVENTORY =================
def inventory_score(line):
    score = 0
    low = line.lower()
    if any(k in low for k in IGNORE_KEYWORDS):
        score -= 5
    if re.search(r"\d+\s*x\s*\d+", low):
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
            "Invoice No": invoice_no,
            "Item Text": l[:80],
            "Amount": amt,
            "Score": score
        }

        if score >= 2 and amt not in seen_amounts:
            clean.append(row)
            seen_amounts.add(amt)
        else:
            row["Reject Reason"] = "Low score / duplicate"
            rejected.append(row)

    return clean, rejected

# ================= RECONCILIATION =================
def reconciliation_status(invoice_total, inventory_rows):
    if invoice_total <= 0 or not inventory_rows:
        return "UNKNOWN"

    item_sum = sum(r["Amount"] for r in inventory_rows)

    if abs(invoice_total - item_sum) <= RECON_TOLERANCE:
        return "OK"
    return "MISMATCH"

# ================= MAIN =================
def main(folder):
    invoices = []
    inventory_ok, inventory_bad = [], []
    sales = []
    gstin_rows = []
    exceptions = []

    for f in os.listdir(folder):
        if not f.lower().endswith((".pdf", ".jpg", ".png", ".jpeg")):
            continue

        path = os.path.join(folder, f)
        lines = textract_text(path)

        invoice_no = find_invoice_no(lines)
        invoice_date = find_invoice_date(lines)

        sup_gstin, sup_conf, buy_gstin, buy_conf = extract_gstins(lines)
        gst_risk = gstin_risk_flag(sup_gstin, sup_conf, buy_gstin, buy_conf)

        amounts = [normalize_amount(l) for l in lines if normalize_amount(l)]
        invoice_total = max(amounts) if amounts else 0

        inv_ok, inv_bad = extract_inventory(lines, invoice_no)
        inventory_ok += inv_ok
        inventory_bad += inv_bad

        recon = reconciliation_status(invoice_total, inv_ok)

        invoice_row = {
            "Invoice No": invoice_no,
            "Invoice Date": invoice_date,
            "Supplier GSTIN": sup_gstin,
            "Supplier Conf": sup_conf,
            "Buyer GSTIN": buy_gstin,
            "Buyer Conf": buy_conf,
            "GSTIN_RISK_FLAG": gst_risk,
            "Invoice Amount": invoice_total,
            "Invoice_Reconciliation_Status": recon,
            "Tax_Parse_Status": "NOT_ATTEMPTED",
            "File": f
        }
        invoices.append(invoice_row)

        gstin_rows.append({
            "Invoice No": invoice_no,
            "Supplier GSTIN": sup_gstin,
            "Supplier Conf": sup_conf,
            "Buyer GSTIN": buy_gstin,
            "Buyer Conf": buy_conf,
            "GSTIN_RISK_FLAG": gst_risk
        })

        # Sales only if SAFE
        if recon == "OK" and gst_risk == "OK":
            sales.append({
                "Voucher Type": "Sales",
                "Date": invoice_date,
                "Reference": invoice_no,
                "Amount": invoice_total,
                "Narration": "OCR ASSIST – VERIFIED STRUCTURE"
            })
        else:
            exceptions.append({
                "Invoice No": invoice_no,
                "Reason": f"Recon={recon}, GSTIN={gst_risk}",
                "File": f
            })

    os.makedirs("output", exist_ok=True)
    out = f"output/GST_OUTPUT_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

    with pd.ExcelWriter(out, engine="openpyxl") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(inventory_ok).to_excel(w, "Inventory_Clean", index=False)
        pd.DataFrame(inventory_bad).to_excel(w, "Inventory_Rejected", index=False)
        pd.DataFrame(sales).to_excel(w, "Sales", index=False)
        pd.DataFrame(gstin_rows).to_excel(w, "GSTIN_Found", index=False)
        pd.DataFrame(exceptions).to_excel(w, "Exceptions", index=False)
        pd.DataFrame([{
            "Invoices": len(invoices),
            "Sales Posted": len(sales),
            "Exceptions": len(exceptions),
            "Generated On": datetime.now().strftime("%d-%m-%Y %H:%M")
        }]).to_excel(w, "Dashboard", index=False)

    print(f"✅ DONE v1.2: {out}")

# ================= RUN =================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gst_ocr_demo_v12.py <folder>")
        sys.exit(1)
    main(sys.argv[1])
