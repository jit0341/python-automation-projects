# ============================
# STEP 0: IMPORTS
# ============================
# ReportLab for PDF creation
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# CSV reading
import csv

# File & directory handling
import os


# ============================
# STEP 1: INPUT & CONFIGURATION
# ============================
# Input CSV file (data source)
input_file = "data/sales_summary.csv"

# Output PDF file (final report)
output_file = "output/sales_report.pdf"


# ============================
# STEP 2: MAIN FUNCTION
# ============================
def generate_pdf_report():
    """
    Generates a PDF sales report from CSV data.
    Steps:
    - Validate input file
    - Create PDF canvas
    - Read CSV data
    - Write data to PDF
    - Generate summary
    - Save PDF
    """

    # ----------------------------
    # STEP 2.1: INPUT VALIDATION
    # ----------------------------
    # Check if CSV file exists
    if not os.path.exists(input_file):
        print("❌ CSV file not found.")
        return

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # If PDF already exists, delete it (safe re-run)
    if os.path.exists(output_file):
        os.remove(output_file)


    # ----------------------------
    # STEP 3: PDF SETUP
    # ----------------------------
    # Create PDF canvas
    c = canvas.Canvas(output_file, pagesize=A4)

    # Page width and height
    width, height = A4


    # ----------------------------
    # STEP 4: REPORT HEADER
    # ----------------------------
    # Set font for title
    c.setFont("Helvetica-Bold", 18)

    # Draw report title
    c.drawString(50, height - 50, "Sales Summary Report")

    # Table header font
    c.setFont("Helvetica-Bold", 12)

    # Y-position for table header
    y = height - 100

    # Column headers
    c.drawString(50, y, "Product")
    c.drawString(200, y, "Quantity")
    c.drawString(300, y, "Revenue")


    # ----------------------------
    # STEP 5: DATA PROCESSING
    # ----------------------------
    # Initialize total revenue
    total_revenue = 0

    # Start data rows below header
    y = height - 120

    # Set normal font for rows
    c.setFont("Helvetica", 10)

    # Open CSV file
    with open(input_file, newline="") as file:
        reader = csv.DictReader(file)

        # Loop through each CSV row
        for row in reader:
            # Write row data to PDF
            c.drawString(50, y, row["Product"])
            c.drawString(200, y, row["Quantity"])
            c.drawString(300, y, row["Revenue"])

            # Business logic: calculate total revenue
            revenue = row.get("Revenue", "0")
            if revenue.isdigit():
                total_revenue += int(revenue)

            # Move to next line
            y -= 20

            # Handle page overflow
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50


    # ----------------------------
    # STEP 6: SUMMARY & FINAL SAVE
    # ----------------------------
    # Summary section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 20, f"Total Revenue: INR {total_revenue}")

    # Save the PDF (MOST IMPORTANT STEP)
    c.save()

    # Success message
    print(f"✅ PDF generated successfully: {output_file}")


# ============================
# PROGRAM ENTRY POINT
# ============================
if __name__ == "__main__":
    print("---- Generating PDF report ----")
    generate_pdf_report()
