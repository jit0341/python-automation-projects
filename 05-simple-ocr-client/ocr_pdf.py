from PIL import Image
import pytesseract
from reportlab.pdfgen import canvas

image_path = "images/dn_001.png"
pdf_path = "output/searchable.pdf"

# OCR
img = Image.open(image_path)
text = pytesseract.image_to_string(img)

# PDF
c = canvas.Canvas(pdf_path)
c.drawImage(image_path, 0, 0, width=600, height=800)

# Invisible text
c.setFillColorRGB(0, 0, 0, alpha=0)
c.setFont("Helvetica", 8)

y = 780
for line in text.split("\n"):
    c.drawString(10, y, line)
    y -= 10

c.save()
