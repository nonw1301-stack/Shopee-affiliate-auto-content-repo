"""Generate a placeholder 1024x1024 PNG icon and a sample description file.

Requires Pillow. Usage:
  python .\scripts\generate_app_assets.py
This writes to scripts/output_icon.png and scripts/app_description.txt
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT_ICON = os.path.join(os.path.dirname(__file__), 'output_icon.png')
OUT_DESC = os.path.join(os.path.dirname(__file__), 'app_description.txt')

def make_icon(path):
    size = (1024, 1024)
    bg = (30, 144, 255)
    im = Image.new('RGB', size, bg)
    draw = ImageDraw.Draw(im)
    # Draw a simple logo: white rounded rectangle + letter
    rect = [160, 160, 864, 864]
    draw.rounded_rectangle(rect, radius=120, fill=(255,255,255))
    # Draw letter N in center
    try:
        fnt = ImageFont.truetype('arial.ttf', 420)
    except Exception:
        fnt = ImageFont.load_default()
    w,h = draw.textsize('N', font=fnt)
    draw.text(((size[0]-w)/2, (size[1]-h)/2-30), 'N', font=fnt, fill=bg)
    im.save(path)

def write_description(path):
    desc = 'สร้างคอนเทนต์วิดีโอสั้นโดยอัตโนมัติสำหรับสินค้าบน Shopee และโพสต์ไปยัง TikTok เพื่อช่วยการตลาดแบบ Affiliate.'
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(desc)

if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT_ICON), exist_ok=True)
    make_icon(OUT_ICON)
    write_description(OUT_DESC)
    print('Wrote', OUT_ICON)
    print('Wrote', OUT_DESC)
