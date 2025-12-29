"""
Searchable PDF Generator using OCR
Converts scanned images into searchable PDF files

Author: Python Automation Projects
"""

import os
from PIL import Image
import pytesseract
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

IMAGES_FOLDER = "images"
OUTPUT_PDF = "output/searchable_delivery_notes.pdf"

def create_searchable_pdf(images_folder, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=A4)
    page_width, page_height = A4

    for filename in os.listdir(images_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(images_folder, filename)
            print(f"📄 Processing: {filename}")

            # Load image
            img = Image.open(image_path)

            # OCR text
            text = pytesseract.image_to_string(img, config="--psm 6")

            # Resize image to fit page
            img_width, img_height = img.size
            scale = min(page_width / img_width, page_height / img_height)

            new_width = img_width * scale
            new_height = img_height * scale

            x_offset = (page_width - new_width) / 2
            y_offset = (page_height - new_height) / 2

            # Draw image (visible)
            c.drawImage(image_path, x_offset, y_offset, new_width, new_height)

            # Draw invisible OCR text
            c.setFillColorRGB(0, 0, 0, alpha=0)
            c.setFont("Helvetica", 8)

            y_text = page_height - 40
            for line in text.split("\n"):
                c.drawString(40, y_text, line)
                y_text -= 10
                if y_text < 40:
                    break

            c.showPage()

    c.save()
    print("✅ Searchable PDF created:", output_pdf)


if __name__ == "__main__":
    print("🚀 Starting Searchable PDF Generation...")
    create_searchable_pdf(IMAGES_FOLDER, OUTPUT_PDF)
