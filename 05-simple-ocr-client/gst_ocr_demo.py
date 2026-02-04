#!/usr/bin/env python3
"""
GST OCR DEMO v0.9
Rule-driven, demo-grade, Termux compatible
"""

import re
import os
import sys
import hashlib
from datetime import datetime
from pathlib import Path

import boto3
import pandas as pd

# ========================= CONFIG =========================

GSTIN_REGEX = r"\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]"
DATE_REGEX = r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b"

MIN_VALID_AMOUNT = 100.0

BAD_INVOICE_WORDS = {
    "eway", "e-way", "sign", "signature", "auth",
    "transport", "gst", "cgst", "sgst", "total"
}

# ========================= TEXTRACT =========================

def textract_lines(file_path):
    client = boto3.client("textract", region_name="ap-south-1")

    with open(file_path, "rb") as f:
        bytes_data = f.read()

    resp = client.detect_document_text(Document={"Bytes": bytes_data})

    lines = []
    for b in resp.get("Blocks", []):
        if b["BlockType"] == "LINE":
            lines.append(b["Text"].strip())

    return lines

# ========================= HELPERS =========================

def normalize_amount(val):
    try:
        return float(re.sub(r"[^\d.]", "", val))
    except:
        return None

def valid_invoice_candidate(txt):
    t = txt.lower()
    if len(txt) < 4:
        return False
    if any(w in t for w in BAD_INVOICE_WORDS):
        return False
    if not re.search(r"\d", txt):
        return False
    return True

def parse_date(d):
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y"):
        try:
            return datetime.strptime(d, fmt).date()
        except:
            pass
    return None

# ========================= EXTRACTION =========================

def extract_invoice_no(lines, filename):
    candidates = []

    for l in lines:
        if "invoice" in l.lower():
            parts = re.split(r"[:\s]", l)
            for p in parts:
                if valid_invoice_candidate(p):
                    candidates.append(p)

    if candidates:
        return candidates[0]

    # fallback: filename
    base = Path(filename).stem
    return base[:20]

def extract_invoice_date(lines):
    for l in lines:
        if "date" in l.lower() and not any(x in l.lower() for x in ["eway", "delivery"]):
            m = re.search(DATE_REGEX, l)
            if m:
                d = parse_date(m.group(1))
                if d and abs((datetime.now().date() - d).days) < 400:
                    return d.isoformat()

    # fallback global scan
    for l in lines:
        m = re.search(DATE_REGEX, l)
        if m:
            d = parse_date(m.group(1))
            if d:
                return d.isoformat()

    return "NA"

def extract_gstin(lines):
    found = []
    for l in lines:
        m = re.search(GSTIN_REGEX, l)
        if m:
            found.append(m.group())

    if len(found) >= 2:
        return found[0], found[1]
    if len(found) == 1:
        return found[0], "NA"
    return "NA", "NA"

# ========================= INVENTORY =========================

def extract_inventory(lines, invoice_total):
    rows = []

    for l in lines:
        if any(x in l.lower() for x in ["gst", "cgst", "sgst", "total", "%"]):
            continue

        nums = re.findall(r"\d+\.\d{1,2}", l)
        if not nums:
            continue

        amt = normalize_amount(nums[-1])
        if not amt:
            continue

        if amt < MIN_VALID_AMOUNT:
            continue
        if invoice_total and amt > invoice_total:
            continue

        rows.append({
            "Item Text": l[:80],
            "Amount": amt,
            "Ignored": "NO"
        })

    return rows

# ========================= MAIN =========================

def process_file(file_path):
    lines = textract_lines(file_path)

    invoice_no = extract_invoice_no(lines, file_path)
    invoice_date = extract_invoice_date(lines)
    sup_gst, buy_gst = extract_gstin(lines)

    amounts = []
    for l in lines:
        for n in re.findall(r"\d+\.\d{1,2}", l):
            v = normalize_amount(n)
            if v:
                amounts.append(v)

    invoice_total = max(amounts) if amounts else None

    inventory = extract_inventory(lines, invoice_total)

    return {
        "invoice": {
            "Invoice No": invoice_no,
            "Invoice Date": invoice_date,
            "Supplier GSTIN": sup_gst,
            "Buyer GSTIN": buy_gst,
            "Amount": invoice_total
        },
        "inventory": inventory
    }

# ========================= ENTRY =========================

def main():
    if len(sys.argv) < 2:
        print("Usage: python gst_ocr_demo_v09.py <folder>")
        sys.exit(1)

    folder = sys.argv[1]
    invoices = []
    inventory_all = []
    sales = []

    for f in os.listdir(folder):
        if not f.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        res = process_file(os.path.join(folder, f))
        inv = res["invoice"]

        invoices.append(inv)

        for r in res["inventory"]:
            r["Invoice"] = inv["Invoice No"]
            inventory_all.append(r)

        if inv["Invoice No"] != "NA" and inv["Amount"]:
            sales.append({
                "Voucher Type": "Sales",
                "Date": inv["Invoice Date"],
                "Reference": inv["Invoice No"],
                "Amount": inv["Amount"],
                "Narration": "OCR ASSISTED"
            })

    out = f"GST_OUTPUT_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        pd.DataFrame(invoices).to_excel(w, "Invoices", index=False)
        pd.DataFrame(inventory_all).to_excel(w, "Inventory", index=False)
        pd.DataFrame(sales).to_excel(w, "Sales_Possible", index=False)

    print("✅ DONE:", out)

if __name__ == "__main__":
    main()
