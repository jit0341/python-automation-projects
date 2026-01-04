# ==========================================================
# CLIENT SALES PDF REPORT GENERATOR
# ==========================================================
# Author   : Jitendra Bharti
# Purpose  : Convert CSV sales data into a professional,
#            client-ready branded PDF summary report.
# ==========================================================


# ==========================================================
# STEP 0: IMPORT REQUIRED LIBRARIES
# ==========================================================

# PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# CSV reading
import csv

# File & directory handling
import os

# Command-line arguments
import argparse

# Logging for audit & debugging
import logging


# ==========================================================
# STEP 1: LOGGING CONFIGURATION
# ==========================================================
logging.basicConfig(
    filename="report.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ==========================================================
# STEP 2: ARGUMENT PARSER (CLIENT-READY)
# ==========================================================
def parse_arguments():
    parser = argparse.ArgumentParser(description="Client Sales PDF Report Generator")
    parser.add_argument("--client", default="ABC Traders", help="Client name")
    parser.add_argument("--input", default="data/sales_summary.csv", help="Input CSV file")
    parser.add_argument("--output", default="output/sales_report.pdf", help="Output PDF file")
    parser.add_argument("--logo", default=None, help="Optional company logo path")
    return parser.parse_args()


# ==========================================================
# STEP 3: PDF REPORT GENERATION
# ==========================================================
def generate_pdf_report(client, input_file, output_file, logo_path=None):

    logging.info(f"Report generation started for client: {client}")

    # -------------------------------
    # INPUT VALIDATION
    # -------------------------------
    if not os.path.exists(input_file):
        logging.error("CSV input file not found")
        print("❌ CSV input file not found")
        return

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # -------------------------------
    # PDF SETUP
    # -------------------------------
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4

    # -------------------------------
    # HEADER SECTION (BRANDING)
    # -------------------------------
    if logo_path and os.path.exists(logo_path):
        c.drawImage(logo_path, 40, height - 100, width=80, height=50)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(140, height - 50, f"{client} – Sales Summary Report")

    c.setFont("Helvetica", 10)
    c.drawString(140, height - 70, "Automatically generated PDF report")

    # -------------------------------
    # TABLE HEADER
    # -------------------------------
    y = height - 120
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Product")
    c.drawString(220, y, "Quantity")
    c.drawString(320, y, "Revenue (INR)")

    y -= 20
    c.setFont("Helvetica", 10)

    total_revenue = 0

    # -------------------------------
    # READ CSV & WRITE DATA
    # -------------------------------
    with open(input_file, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            c.drawString(50, y, row.get("Product", ""))
            c.drawString(220, y, row.get("Quantity", ""))
            c.drawString(320, y, row.get("Revenue", ""))

            revenue = row.get("Revenue", "0")
            if revenue.isdigit():
                total_revenue += int(revenue)

            y -= 18

            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50

    # -------------------------------
    # SUMMARY SECTION
    # -------------------------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 20, f"Total Revenue: INR {total_revenue}")

    # -------------------------------
    # FOOTER
    # -------------------------------
    c.setFont("Helvetica", 8)
    c.drawString(
        50,
        30,
        "Generated using Python Automation | Author: Jitendra Bharti"
    )

    c.save()
    logging.info("PDF report generated successfully")
    print(f"✅ PDF generated successfully: {output_file}")


# ==========================================================
# PROGRAM ENTRY POINT
# ==========================================================
if __name__ == "__main__":
    args = parse_arguments()
    generate_pdf_report(
        client=args.client,
        input_file=args.input,
        output_file=args.output,
        logo_path=args.logo
    )
