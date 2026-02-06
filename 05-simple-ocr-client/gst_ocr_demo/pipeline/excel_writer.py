import os
from openpyxl import Workbook
from datetime import datetime

# ================= PATH =================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # gst_ocr_demo/
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================= MAIN =================
def write_excel(results, debug_rows):
    wb = Workbook()

    # ==================================================
    # INVOICES MAIN
    # ==================================================
    ws = wb.active
    ws.title = "INVOICES_MAIN"

    ws.append([
        "file",
        "invoice_no",
        "invoice_date",
        "supplier_gstin",
        "buyer_gstin",
        "supplier_name",
        "buyer_name",
        "total_amount",
        "status",
        "score"
    ])

    for r in results:
        ws.append([
            r.get("file"),
            r.get("invoice_no"),
            r.get("invoice_date"),
            r.get("supplier_gstin"),
            r.get("buyer_gstin"),
            r.get("supplier_name"),
            r.get("buyer_name"),
            r.get("total_amount"),
            r.get("status"),
            r.get("score"),
        ])

    # ==================================================
    # DEBUG RAW
    # ==================================================
    dbg = wb.create_sheet("DEBUG_RAW")
    dbg.append([
        "file",
        "raw_text",
        "extracted",
        "score",
        "confidence",
        "rejected"
    ])

    for d in debug_rows:
        dbg.append([
            d.get("file"),
            d.get("raw_text"),
            d.get("extracted_amount") or d.get("extracted") or d.get("extracted_value"),
            d.get("score"),
            d.get("confidence"),
            d.get("rejected"),
        ])

    # ==================================================
    # INVENTORIES
    # ==================================================
    inv = wb.create_sheet("INVENTORIES")
    inv.append([
        "file",
        "item",
        "qty",
        "rate",
        "amount"
    ])

    for r in results:
        for it in r.get("inventories", []):
            inv.append([
                r.get("file"),
                it.get("item"),
                it.get("qty"),
                it.get("rate"),
                it.get("amount"),
            ])

    # ==================================================
    # MISSING / CORRECTION
    # ==================================================
    miss = wb.create_sheet("MISSING_CORRECTION")
    miss.append([
        "file",
        "invoice_no_fix",
        "invoice_date_fix",
        "supplier_gstin_fix",
        "buyer_gstin_fix",
        "supplier_name_fix",
        "buyer_name_fix",
        "total_amount_fix",
        "remarks"
    ])

    for r in results:
        if r.get("status") != "AUTO":
            miss.append([r.get("file")] + [""] * 8)

    # ==================================================
    # DASHBOARD
    # ==================================================
    dash = wb.create_sheet("DASHBOARD")

    total = len(results)
    auto = sum(1 for r in results if r.get("status") == "AUTO")
    review = sum(1 for r in results if r.get("status") == "REVIEW")
    excepts = sum(1 for r in results if r.get("status") == "EXCEPT")

    dash.append(["Metric", "Value"])
    dash.append(["Total Invoices", total])
    dash.append(["AUTO", auto])
    dash.append(["REVIEW", review])
    dash.append(["EXCEPT", excepts])
    dash.append(["AUTO %", round((auto / total) * 100, 2) if total else 0])

    # ==================================================
    # SAVE
    # ==================================================
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = os.path.join(
        OUTPUT_DIR,
        f"GST_Output_FINAL_{timestamp}.xlsx"
    )

    wb.save(output_file)
    return output_file
