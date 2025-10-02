# ตัวอย่างง่าย ๆ: สร้างรูป Banner ด้วย Pillow
from PIL import Image, ImageDraw, ImageFont
from .config import Config


def make_banner(title, price, output_path):
    img = Image.new("RGB", (720, 1280), color=(255,255,255))
    d = ImageDraw.Draw(img)
    # ใส่ text (ปรับ font path ตามระบบ)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    d.text((30, 50), title, font=font, fill=(0,0,0))
    d.text((30, 120), f"ราคา {price} บาท", font=font, fill=(255,0,0))
    img.save(output_path)
    return output_path
