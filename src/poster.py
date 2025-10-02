# ตอนนี้จะเก็บไฟล์ text + banner ลงโฟลเดอร์ output
import os
from .config import Config


def prepare_post(item):
    # item: dict จาก generator.run_once
    slug = item["name"].replace(" ", "_")[:40]
    text_file = os.path.join(Config.OUTPUT_DIR, f"{slug}.txt")
    banner_file = os.path.join(Config.OUTPUT_DIR, f"{slug}.png")

    # (สมมติ) media_creator.make_banner
    try:
        from .media_creator import make_banner
        make_banner(item["name"], item["price"], banner_file)
    except Exception as e:
        banner_file = None

    return {"text": text_file, "banner": banner_file}
