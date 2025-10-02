import os
from src.predictor import score_variant
from PIL import Image


def test_score_variant_basic(tmp_path):
    img = tmp_path / "thumb.png"
    # create a simple image
    im = Image.new("RGB", (320, 480), color=(255, 255, 255))
    im.save(img)
    caption = "ลดราคาพิเศษ! สั่งเลย #ดีล #ลดราคา"
    score, details = score_variant(caption, str(img))
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
    assert 'len_score' in details