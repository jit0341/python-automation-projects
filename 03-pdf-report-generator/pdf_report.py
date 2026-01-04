"""
====================================================
PDF SALES REPORT GENERATOR
Author  : Jitendra Bharti
Purpose : Convert CSV sales data into a professional
          PDF summary report with totals.
====================================================
"""

# ==================================================
# STEP 0: IMPORT REQUIRED LIBRARIES
# ==================================================

# PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# CSV reading
import csv

# File & directory handling
import os

# Command-line arguments (client-ready feature)
import argparse

# Logging for audit & debugging
import logging


# ==================================================
# STEP 1: LOGGING CONFIGURATION
# ==================================================

logging.basicConfig(
    filename="report.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ==================================================
# STEP 2: COMMAND-LINE ARGUMENT PARSER
# ==================================================

def parse_arguments():
    """
    Allows client or user to customize:
    - Input CSV file
    - Output PDF path
    - Report title
    """
    parser = argparse.ArgumentParser(
        description="Generate PDF sales report from CSV file"
    )

    parser.add_argument(
        "--input",
        default="data/sales_summary.csv",
        help="Path to input CSV file"
    )

    parser.add_argument(
        "--output",
        default="output/sales_report.pdf",
        help="Path to output PDF file"
    )

    parser.add_argument(
        "--title",
        default="Sales Summary Report",
        help="PDF report title"
    )

    return parser.parse_args()


# ==================================================
# STEP 3: HELPER FUNCTIONS
# ==================================================

def format_currency(amount):
    """
    Convert numeric value into Indian currency format.
    Example: 250000 -> ₹250,000
    """
    return f"₹{amount:,.0f}"


def draw_table_header(pdf, y_position):
    """
    Draw table column headers on PDF.
    Reused on every new page.
    """
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y_position, "Product")
    pdf.drawString(220, y_position, "Quantity")
    pdf.drawString(330, y_position, "Revenue")


# ==================================================
# STEP 4: MAIN PDF GENERATION FUNCTION
# ==================================================

def generate_pdf_report():
    """
    Core automation logic:
    1. Validate input
    2. Create PDF
    3. Read CSV
    4. Write rows
    5. Apply business logic
    6. Save final PDF
    """

    # -------------------------------
    # STEP 4.1: READ ARGUMENTS
    # -------------------------------
    args = parse_arguments()
    input_file = args.input
    output_file = args.output
    report_title = args.title

    logging.info("PDF automation started")

    # -------------------------------
    # STEP 4.2: INPUT VALIDATION
    # -------------------------------
    if not os.path.exists(input_file):
        logging.error("Input CSV file not found")
        print("❌ CSV file not found")
        return

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # -------------------------------
    # STEP 4.3: CREATE PDF CANVAS
    # -------------------------------
    pdf = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4

    # -------------------------------
    # STEP 4.4: DRAW REPORT TITLE
    # -------------------------------
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, height - 50, report_title)

    # -------------------------------
    # STEP 4.5: DRAW TABLE HEADER
    # -------------------------------
    y = height - 100
    draw_table_header(pdf, y)
    y -= 25

    pdf.setFont("Helvetica", 10)

    # -------------------------------
    # STEP 4.6: PROCESS CSV DATA
    # -------------------------------
    total_revenue = 0

    with open(input_file, newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            try:
                product = row["Product"]
                quantity = row["Quantity"]
                revenue = int(float(row["Revenue"]))

                # Write row to PDF
                pdf.drawString(50, y, product)
                pdf.drawString(220, y, str(quantity))
                pdf.drawString(330, y, format_currency(revenue))

                total_revenue += revenue
                y -= 20

                # -------------------------------
                # STEP 4.7: HANDLE PAGE OVERFLOW
                # -------------------------------
                if y < 60:
                    pdf.showPage()
                    pdf.setFont("Helvetica-Bold", 18)
                    pdf.drawString(50, height - 50, report_title)

                    y = height - 100
                    draw_table_header(pdf, y)
                    y -= 25
                    pdf.setFont("Helvetica", 10)

            except Exception as e:
                logging.warning(f"Skipped invalid row: {row} | {e}")

    # -------------------------------
    # STEP 4.8: SUMMARY SECTION
    # -------------------------------
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(
        50,
        y - 20,
        f"Total Revenue: {format_currency(total_revenue)}"
    )

    # -------------------------------
    # STEP 4.9: SAVE PDF
    # -------------------------------
    pdf.save()

    logging.info(f"PDF generated successfully: {output_file}")
    print(f"✅ PDF generated successfully: {output_file}")


# ==================================================
# STEP 5: PROGRAM ENTRY POINT
# ==================================================

if __name__ == "__main__":
    print("---- Generating PDF Sales Report ----")
    generate_pdf_report()
