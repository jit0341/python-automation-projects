from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def write_to_excel(results, output_path):
    wb = Workbook()
    
    # Styles
    header_font = Font(bold=True, color="FFFFFF")
    summary_fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    item_fill = PatternFill(start_color="375623", end_color="375623", fill_type="solid")
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Sheet 1: Summary (Updated with GSTIN)
    ws1 = wb.active
    ws1.title = "Invoice Summary"
    # GSTIN कॉलम्स यहाँ जोड़े गए हैं
    headers1 = ["File Name", "Invoice No", "Date", "Supplier Name", "Supplier GSTIN", "Buyer Name", "Buyer GSTIN", "Total Amount"]
    ws1.append(headers1)
    
    for cell in ws1[1]:
        cell.font = header_font
        cell.fill = summary_fill
        cell.alignment = center

    for res in results:
        ws1.append([
            res.get('file'), res.get('invoice_no'), res.get('invoice_date'),
            res.get('supplier_name'), res.get('supplier_gstin'), # New
            res.get('buyer_name'), res.get('buyer_gstin'),       # New
            res.get('total_amount')
        ])

    # Sheet 2: Item Details (Improved Layout)
    ws2 = wb.create_sheet("Item Details")
    headers2 = ["File Ref", "Item Description", "Qty", "Unit Rate", "GST %", "Tax Amount", "Net Total"]
    ws2.append(headers2)
    
    for cell in ws2[1]:
        cell.font = header_font
        cell.fill = item_fill
        cell.alignment = center

    for res in results:
        for item in res.get('inventories', []):
            ws2.append([
                res.get('file'), item.get('item'), item.get('qty'),
                item.get('rate'), item.get('tax_rate'), item.get('tax_amount'), item.get('amount')
            ])

    # Column Widths
    ws1.column_dimensions['D'].width = 30
    ws1.column_dimensions['E'].width = 20
    ws1.column_dimensions['F'].width = 30
    ws1.column_dimensions['G'].width = 20
    ws2.column_dimensions['B'].width = 50

    wb.save(output_path)
