#!/usr/bin/env python3
# =====================================================
# GST OCR – Demo v1.3
# Assist-Only + Auto-Post Gate (CA-Safe)
# =====================================================

import os, re, sys
from datetime import datetime
import pandas as pd
import boto3

# ================= CONFIG =================

REGION = "ap-south-1"

GSTIN_REGEX = r"\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b"

ASSIST_ONLY_FIELDS = {
    "supplier_gstin",
    "buyer_gstin",
    "invoice_no",
    "invoice_date",
    "invoice_total",
    "tax_breakup",
    "line_items"
}

CONFIDENCE_THRESHOLDS = {
    "gstin": 0.90,
    "amount": 0.85,
    "date": 0.85
}

RECON_TOLERANCE = 2.0  # ₹2 rounding tolerance

IGNORE_KEYWORDS = [
    "gst", "cgst", "sgst", "igst", "total", "round",
    "bank", "ifsc", "account", "authorized",
    "signature", "eway", "transport"
]

INVOICE_KEYS = ["invoice", "tax invoice", "bill no", "inv no"]
DATE_REGEXES = [
    r"\b\d{2}[-/]\d{2}[-/]\d{4}\b",
    r"\b\d{4}[-/]\d{2}[-/]\d{2}\b"
]

# ================= TEXTRACT =================

def get_textract():
    return boto3.client("textract", region_name=REGION)

def textract_lines(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    res = get_textract().detect_document_text(
        Document={"Bytes": data}
    )
    return [
        (b["Text"], b.get("Confidence", 0) / 100)
        for b in res["Blocks"]
        if b["BlockType"] == "LINE"
    ]

# ================= HELPERS =================

def normalize_amount(txt):
    txt = txt.replace(",", "").replace("₹", "")
    m = re.findall(r"\d+\.\d+|\d+", txt)
    return float(m[0]) if m else None

def find_invoice_no(lines):
    for i, (l, _) in enumerate(lines):
        if any(k in l.lower() for k in INVOICE_KEYS):
            return l[:40]
    return "NA"

def find_invoice_date(lines):
    for l, _ in lines:
        for r in DATE_REGEXES:
            m = re.search(r, l)
            if m:
                return m.group()
    return "NA"

def extract_gstins(lines):
    text = " ".join([l for l, _ in lines])
    found = re.findall(GSTIN_REGEX, text)
    unique = list(dict.fromkeys(found))
    if len(unique) >= 2:
        return unique[0], "HIGH", unique[1], "HIGH"
    if len(unique) == 1:
        return unique[0], "HIGH", "NA", "LOW"
    return "NA", "LOW", "NA", "LOW"

# ================= INVENTORY =================

def inventory_score(line):
    score = 0
    low = line.lower()
    if any(k in low for k in IGNORE_KEYWORDS):
        score -= 5
    if re.search(r"\d+\.\d+", line):
        score += 2
    if re.search(r"\d+\s*x\s*\d+", low):
        score += 3
    return score

def extract_inventory(lines, invoice_no):
    clean, rejected = [], []
    for l, _ in lines:
        amt = normalize_amount(l)
        if amt is None:
            continue
        score = inventory_score(l)
        row = {
            "Invoice": invoice_no,
            "Item Text": l[:80],
            "Amount": amt,
            "Score": score
        }
        if score >= 2:
            clean.append(row)
        else:
            row["Reject Reason"] = "Low score"
            rejected.append(row)
    return clean, rejected

# ================= RECON + GATE =================

def reconciliation_check(invoice_total, items):
    item_sum = sum(i["Amount"] for i in items)
    diff = abs(invoice_total - item_sum)
    return diff <= RECON_TOLERANCE, item_sum, diff

def auto_post_decision(flags):
    return "AUTO_POSTABLE" if not flags else "REVIEW_REQUIRED"

# ================= MAIN =================

def main(folder):
    invoices = []
    inventory_ok, inventory_bad = [], []
    exceptions = []

    for f in os.listdir(folder):
        if not f.lower().endswith((".pdf", ".jpg", ".png", ".jpeg")):
            continue

        path = os.path.join(folder, f)
        lines = textract_lines(path)

        invoice_no = find_invoice_no(lines)
        invoice_date = find_invoice_date(lines)
        sup_gstin, sup_conf, buy_gstin, buy_conf = extract_gstins(lines)

        amounts = [normalize_amount(l) for l, _ in lines if normalize_amount(l)]
        invoice_total = max(amounts) if amounts else 0

        inv_ok, inv_bad = extract_inventory(lines, invoice_no)

        recon_ok, item_sum, diff = reconciliation_check(invoice_total, inv_ok)

        flags = []
        if sup_conf == "LOW" or buy_conf == "LOW":
            flags.append("GSTIN_VERIFY")
        if not recon_ok:
            flags.append("RECON_MISMATCH")
        if invoice_no == "NA":
            flags.append("INVOICE_NO_MISSING")
        if invoice_date == "NA":
            flags.append("DATE_MISSING")

        post_status = auto_post_decision(flags)

        invoices.append({
            "Invoice No": invoice_no,
            "Invoice Date": invoice_date,
            "Supplier GSTIN": sup_gstin,
            "Supplier Conf": sup_conf,
            "Buyer GSTIN": buy_gstin,
            "Buyer Conf": buy_conf,
            "Invoice Total": invoice_total,
            "Item Sum": item_sum,
            "Recon Diff": diff,
            "Post Status": post_status,
            "Risk Flags": ",".join(flags) if flags else "OK",
            "File": f
        })

        inventory_ok += inv_ok
        inventory_bad += inv_bad

        if post_status != "AUTO_POSTABLE":
            exceptions.append({
                "Invoice": invoice_no,
                "Reason": ",".join(flags),
                "File": f
            })

    os.makedirs("output", exist_ok=True)
    out = f"output/GST_OUTPUT_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

    with pd.ExcelWriter(out, engine="openpyxl") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(inventory_ok).to_excel(w, "Inventory_Clean", index=False)
        pd.DataFrame(inventory_bad).to_excel(w, "Inventory_Rejected", index=False)
        pd.DataFrame(exceptions).to_excel(w, "Exceptions", index=False)
        pd.DataFrame([{
            "Invoices": len(invoices),
            "Auto-Postable": sum(i["Post Status"] == "AUTO_POSTABLE" for i in invoices),
            "Exceptions": len(exceptions),
            "Generated On": datetime.now().strftime("%d-%m-%Y %H:%M")
        }]).to_excel(w, "Dashboard", index=False)

    print(f"✅ DONE: {out}")

# ================= RUN =================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gst_ocr_demo_v13.py <folder>")
        sys.exit(1)
    main(sys.argv[1])
