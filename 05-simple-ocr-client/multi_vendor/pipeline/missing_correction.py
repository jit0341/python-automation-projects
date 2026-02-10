#missing_correction.py
def build_missing_corrections(results):
    rows = []

    for r in results:
        if not r.get("invoice_no"):
            rows.append({
                "file": r["file"],
                "field": "invoice_no",
                "suggested": "CHECK MANUALLY"
            })

        if not r.get("invoice_date"):
            rows.append({
                "file": r["file"],
                "field": "invoice_date",
                "suggested": "FROM PDF HEADER"
            })

        if not r.get("total_amount"):
            rows.append({
                "file": r["file"],
                "field": "total_amount",
                "suggested": sum(i.get("amount", 0) for i in r["inventories"])
            })

    return rows
