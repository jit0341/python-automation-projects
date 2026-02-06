import os
import json
import sys
from datetime import datetime

# Import enhanced extractors
sys.path.insert(0, '/home/claude')
from invoice_number_extractor_v2 import extract_invoice_number
from total_amount_extractor_v2 import extract_total_amount

# Import original extractors for comparison
sys.path.insert(0, '/home/claude')

# Simple implementations for other fields (using your original logic)
import re

def extract_invoice_date(lines):
    """Simple date extractor"""
    DATE_PATTERNS = [
        r"\b(\d{2}[\/\-]\d{2}[\/\-]\d{4})\b",
        r"\b(\d{2}[\/\-]\d{2}[\/\-]\d{2})\b",
        r"\b(\d{4}[\/\-]\d{2}[\/\-]\d{2})\b",
    ]
    
    for item in lines:
        text = item.get("text", "")
        for pat in DATE_PATTERNS:
            m = re.search(pat, text)
            if m:
                return {
                    "invoice_date": m.group(1),
                    "status": "AUTO",
                    "score": 70
                }
    
    return {"invoice_date": None, "status": "EXCEPT", "score": 0}

def extract_gstins(lines):
    """Simple GSTIN extractor"""
    GSTIN_RE = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]\b"
    
    supplier_gstin = None
    buyer_gstin = None
    
    for item in lines:
        text = item.get("text", "")
        m = re.search(GSTIN_RE, text.upper())
        if m:
            gstin = m.group(0)
            if not supplier_gstin:
                supplier_gstin = gstin
            elif not buyer_gstin:
                buyer_gstin = gstin
    
    return {
        "supplier_gstin": supplier_gstin,
        "buyer_gstin": buyer_gstin
    }

def extract_names(lines):
    """Simple name extractor"""
    return None, None

# ---------------- CONFIG ----------------
TEXTRACT_DIR = "test_textract_json"
# ----------------------------------------

def load_lines_from_textract(json_path):
    """Load LINE blocks from Textract JSON"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = []
    for block in data.get("Blocks", []):
        if block.get("BlockType") == "LINE":
            lines.append({
                "text": block.get("Text", ""),
                "confidence": block.get("Confidence", 0),
                "source": "line"
            })
    return lines


def process_single_invoice(json_path):
    """Process a single invoice"""
    file_name = os.path.basename(json_path)
    print(f"\n{'='*60}")
    print(f"Processing: {file_name}")
    print(f"{'='*60}")
    
    lines = load_lines_from_textract(json_path)
    print(f"Total lines extracted: {len(lines)}")
    
    # Sample first few lines
    print("\nSample text:")
    for i, line in enumerate(lines[:5]):
        print(f"  {i+1}. {line['text'][:60]}...")
    
    # Extract fields using ENHANCED extractors
    print("\n🔍 Extracting invoice number...")
    inv_no = extract_invoice_number(lines)
    print(f"   Result: {inv_no.get('invoice_no')} (Score: {inv_no.get('score')}, Status: {inv_no.get('status')})")
    
    print("\n🔍 Extracting invoice date...")
    inv_date = extract_invoice_date(lines)
    print(f"   Result: {inv_date.get('invoice_date')} (Status: {inv_date.get('status')})")
    
    print("\n🔍 Extracting GSTINs...")
    gst = extract_gstins(lines)
    print(f"   Supplier: {gst.get('supplier_gstin')}")
    print(f"   Buyer: {gst.get('buyer_gstin')}")
    
    print("\n🔍 Extracting total amount...")
    total = extract_total_amount(lines)
    print(f"   Result: ₹{total.get('total_amount')} (Score: {total.get('score')}, Status: {total.get('status')})")
    
    buyer_name, supplier_name = extract_names(lines)
    
    debug_rows = []
    for section in [inv_no, total]:
        for d in section.get("debug", []):
            d["file"] = file_name
            debug_rows.append(d)
    
    return {
        "file": file_name,
        "invoice_no": inv_no.get("invoice_no"),
        "invoice_date": inv_date.get("invoice_date"),
        "supplier_gstin": gst.get("supplier_gstin"),
        "buyer_gstin": gst.get("buyer_gstin"),
        "supplier_name": supplier_name,
        "buyer_name": buyer_name,
        "total_amount": total.get("total_amount"),
        "status": final_status(inv_no, inv_date, gst, total),
        "score": max(
            inv_no.get("score", 0),
            total.get("score", 0)
        ),
        "debug": debug_rows
    }


def final_status(*sections):
    """Determine final status"""
    if any(s.get("status") == "EXCEPT" for s in sections):
        return "EXCEPT"
    if any(s.get("status") == "REVIEW" for s in sections):
        return "REVIEW"
    return "AUTO"


def run_all_invoices():
    """Process all invoices"""
    results = []
    debug_all = []
    
    if not os.path.exists(TEXTRACT_DIR):
        print(f"❌ Directory not found: {TEXTRACT_DIR}")
        return results, debug_all
    
    files = [f for f in os.listdir(TEXTRACT_DIR) if f.endswith(".json")]
    print(f"\n🎯 Found {len(files)} invoice files to process\n")
    
    for f in files:
        try:
            out = process_single_invoice(os.path.join(TEXTRACT_DIR, f))
            results.append(out)
            debug_all.extend(out.get("debug", []))
        except Exception as e:
            print(f"❌ Error processing {f}: {e}")
    
    return results, debug_all


def write_simple_excel(results, debug_rows):
    """Write results to Excel"""
    try:
        from openpyxl import Workbook
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Results"
        
        # Headers
        ws.append([
            "File", "Invoice No", "Date", "Supplier GSTIN", 
            "Buyer GSTIN", "Amount", "Status", "Score"
        ])
        
        # Data
        for r in results:
            ws.append([
                r.get("file"),
                r.get("invoice_no"),
                r.get("invoice_date"),
                r.get("supplier_gstin"),
                r.get("buyer_gstin"),
                r.get("total_amount"),
                r.get("status"),
                r.get("score")
            ])
        
        output_file = f"/mnt/user-data/outputs/GST_Improved_Results.xlsx"
        wb.save(output_file)
        return output_file
    except Exception as e:
        print(f"⚠️ Excel creation failed: {e}")
        return None


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 GST OCR IMPROVED SYSTEM - DEMO")
    print("="*70)
    
    results, debug_rows = run_all_invoices()
    
    if results:
        print("\n" + "="*70)
        print("📊 SUMMARY STATISTICS")
        print("="*70)
        
        total = len(results)
        auto = sum(1 for r in results if r["status"] == "AUTO")
        review = sum(1 for r in results if r["status"] == "REVIEW")
        excepts = sum(1 for r in results if r["status"] == "EXCEPT")
        
        print(f"\nTotal Invoices Processed: {total}")
        print(f"✅ AUTO (High Confidence): {auto} ({auto/total*100:.1f}%)")
        print(f"⚠️  REVIEW (Needs Check): {review} ({review/total*100:.1f}%)")
        print(f"❌ EXCEPT (Failed): {excepts} ({excepts/total*100:.1f}%)")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 70)
        for r in results:
            status_icon = "✅" if r["status"] == "AUTO" else "⚠️" if r["status"] == "REVIEW" else "❌"
            print(f"{status_icon} {r['file'][:30]:30s} | Invoice: {str(r['invoice_no'])[:15]:15s} | Amount: ₹{r['total_amount'] or 'N/A'}")
        
        # Write Excel
        output_file = write_simple_excel(results, debug_rows)
        if output_file:
            print(f"\n✅ Excel file created: {output_file}")
    else:
        print("\n❌ No results to display")
    
    print("\n" + "="*70)
    print("✨ Processing Complete!")
    print("="*70 + "\n")
