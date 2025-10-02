import os
import shutil
from src.poster_tiktok import upload as tiktok_upload
from src.poster_instagram import upload as insta_upload
from src.config import Config


def test_tiktok_dry_run(tmp_path, monkeypatch):
    # set a temporary output dir
    Config.OUTPUT_DIR = str(tmp_path)
    res = tiktok_upload("caption text", "/path/to/media.mp4", dry_run=True)
    assert res["status"] == "dry_run"
    assert "preview_path" in res
    assert os.path.exists(res["preview_path"]) is True


def test_instagram_dry_run(tmp_path):
    Config.OUTPUT_DIR = str(tmp_path)
    res = insta_upload("/path/to/image.jpg", "Nice caption", dry_run=True)
    assert res["status"] == "dry_run"
    assert os.path.exists(res["preview_path"]) is True
