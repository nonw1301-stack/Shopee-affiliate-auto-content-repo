# ตัวอย่างง่าย ๆ: สร้างรูป Banner ด้วย Pillow
from PIL import Image, ImageDraw, ImageFont
from .config import Config
import os
from pathlib import Path
try:
    from moviepy.editor import ImageClip, concatenate_videoclips
    MOVIEPY_AVAILABLE = True
except Exception:
    MOVIEPY_AVAILABLE = False


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


def make_video_from_images(image_paths, output_path, duration_per_image=2):
    """Create a short MP4 from one or more images using moviepy.

    If moviepy isn't installed, falls back to returning the first image path.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    if not MOVIEPY_AVAILABLE:
        # fallback: return first image as a 'video' placeholder (poster will handle dry-run)
        return image_paths[0]

    clips = []
    for img in image_paths:
        clip = ImageClip(img).set_duration(duration_per_image)
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(output_path, fps=24, codec="libx264", audio=False, verbose=False, logger=None)
    return output_path
