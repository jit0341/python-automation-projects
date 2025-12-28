# make_samples.py - Simple sample maker
from PIL import Image, ImageDraw, ImageFont

def make_sample(filename, dn, date, supplier, total):
    img = Image.new('RGB', (600, 400), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/system/fonts/DroidSans.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((50, 50), "DELIVERY NOTE", fill='black', font=font)
    draw.text((50, 100), f"DN No: {dn}", fill='black', font=font)
    draw.text((50, 140), f"Date: {date}", fill='black', font=font)
    draw.text((50, 180), f"Supplier: {supplier}", fill='black', font=font)
    draw.text((50, 300), f"Total: ${total}", fill='black', font=font)
    
    img.save(filename)
    print(f"✓ Created: {filename}")

# Create 3 samples
import os
os.makedirs('images', exist_ok=True)

make_sample('images/dn_001.png', 'DN-2024-001', '28-12-2024', 'ABC Suppliers Ltd', '1250.00')
make_sample('images/dn_002.png', 'DN-2024-002', '27-12-2024', 'XYZ Industries', '3500.00')
make_sample('images/dn_003.png', 'DN-2024-003', '26-12-2024', 'Global Parts Co', '7750.00')

print("\n✅ Sample images ready in 'images' folder!")

