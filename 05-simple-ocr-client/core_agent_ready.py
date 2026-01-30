# ============================================================
# CORE GST ENGINE – AGENT READY (WITH ROLE ACCURACY + CACHE)
# ============================================================

import os, re, json, boto3
import pandas as pd
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

# ================= CONFIG =================

OUTPUT_DIR = "output"
CACHE_FILE = "vendor_profile_cache.json"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GSTIN_REGEX = r"\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]"
DATE_PATTERNS = [r"\d{2}-\d{2}-\d{4}", r"\d{2}/\d{2}/\d{4}"]

textract = boto3.client("textract")

# ================= CACHE =================

def load_vendor_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_vendor_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

# ================= VALIDATION =================

def validate_gstin(g):
    if not g:
        return "Missing"
    return "Valid" if re.fullmatch(GSTIN_REGEX, g) else "Invalid"

# ================= OCR =================

def run_ocr(file_path):
    with open(file_path, "rb") as f:
        data = f.read()

    blocks = textract.analyze_document(
        Document={"Bytes": data},
        FeatureTypes=["TABLES"]
    )["Blocks"]

    return {"blocks": blocks, "confidence": 0.9}

# ================= OCR HELPERS =================

def group_lines(blocks):
    lines, words = [], [b for b in blocks if b["BlockType"] == "WORD"]
    for w in words:
        y = round(w["Geometry"]["BoundingBox"]["Top"], 3)
        for ln in lines:
            if abs(ln["y"] - y) <= 0.01:
                ln["words"].append(w)
                break
        else:
            lines.append({"y": y, "words": [w]})

    for ln in lines:
        ln["words"].sort(key=lambda x: x["Geometry"]["BoundingBox"]["Left"])
        ln["text"] = " ".join(w["Text"] for w in ln["words"])

    return sorted(lines, key=lambda x: x["y"])

# ================= HEADER EXTRACTION (ADVANCED) =================

def extract_header_structured(lines, vendor_cache):
    header = {
        "InvoiceNo": "NOT FOUND",
        "InvoiceDate": None,
        "SupplierName": None,
        "SupplierGSTIN": None,
        "BuyerName": None,
        "BuyerGSTIN": None
    }

    gstin_hits = []

    for idx, l in enumerate(lines[:50]):
        txt = l["text"]
        up = txt.upper()

        # Invoice No
        if header["InvoiceNo"] == "NOT FOUND" and any(k in up for k in ["INVOICE", "BILL"]):
            header["InvoiceNo"] = txt

        # Date
        for p in DATE_PATTERNS:
            m = re.search(p, txt)
            if m:
                header["InvoiceDate"] = m.group()

        # GSTINs with context
        for g in re.findall(GSTIN_REGEX, txt):
            gstin_hits.append({
                "gstin": g,
                "line": up,
                "idx": idx
            })

    # ---------- ROLE DECISION ----------
    for hit in gstin_hits:
        g = hit["gstin"]
        ctx = hit["line"]

        # 1. Cache wins
        if g in vendor_cache:
            role = vendor_cache[g]["role"]
            if role == "SUPPLIER":
                header["SupplierGSTIN"] = g
                header["SupplierName"] = vendor_cache[g]["name"]
            else:
                header["BuyerGSTIN"] = g
                header["BuyerName"] = vendor_cache[g]["name"]
            continue

        # 2. Keyword context
        if any(k in ctx for k in ["SUPPLIER", "SELLER", "FROM"]):
            header["SupplierGSTIN"] = g
        elif any(k in ctx for k in ["BUYER", "BILL TO", "SHIP TO", "TO"]):
            header["BuyerGSTIN"] = g
        else:
            # 3. Positional fallback
            if hit["idx"] < len(lines) * 0.4 and not header["SupplierGSTIN"]:
                header["SupplierGSTIN"] = g
            elif not header["BuyerGSTIN"]:
                header["BuyerGSTIN"] = g

    header["InvoiceDate"] = header["InvoiceDate"] or "01-01-2026"
    return header

# ================= MAIN CORE =================

def process_invoice(file_path):
    vendor_cache = load_vendor_cache()

    file = os.path.basename(file_path)
    ocr = run_ocr(file_path)

    lines = group_lines(ocr["blocks"])
    header = extract_header_structured(lines, vendor_cache)

    # Learn vendor profiles (auto-memory)
    if header["SupplierGSTIN"]:
        vendor_cache.setdefault(header["SupplierGSTIN"], {
            "name": header["SupplierName"] or "UNKNOWN SUPPLIER",
            "role": "SUPPLIER"
        })

    if header["BuyerGSTIN"]:
        vendor_cache.setdefault(header["BuyerGSTIN"], {
            "name": header["BuyerName"] or "UNKNOWN BUYER",
            "role": "BUYER"
        })

    save_vendor_cache(vendor_cache)

    total = max(
        [float(n.replace(",", "")) for l in lines
         for n in re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d{2})", l["text"])
         if float(n.replace(",", "")) > 1000] or [0.0]
    )

    df = pd.DataFrame([{
        "Invoice No": header["InvoiceNo"],
        "InvoiceDate": header["InvoiceDate"],

        "Supplier GSTIN": header["SupplierGSTIN"],
        "Supplier GST Status": validate_gstin(header["SupplierGSTIN"]),

        "Buyer GSTIN": header["BuyerGSTIN"],
        "Buyer GST Status": validate_gstin(header["BuyerGSTIN"]),

        "Total": total,
        "File": file
    }])

    out = os.path.join(
        OUTPUT_DIR,
        f"AGENT_OUTPUT_{datetime.now().strftime('%H%M%S')}.xlsx"
    )
    df.to_excel(out, index=False)
    print(f"📦 Output generated → {out}")

# ================= TEST RUN =================

if __name__ == "__main__":
    INPUT_DIR = "input"

    pdfs = list(Path(INPUT_DIR).glob("*.pdf"))
    if not pdfs:
        print("❌ No PDF files found in input/")
    else:
        for pdf in pdfs:
            print(f"▶ Processing: {pdf.name}")
            process_invoice(str(pdf))    
