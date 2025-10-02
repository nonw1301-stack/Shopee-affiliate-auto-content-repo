import os
from src.poster_tiktok_api import obtain_access_token as tiktok_token, post_video
from src.poster_instagram_api import obtain_access_token as insta_token, post_image
from src.config import Config


def test_tiktok_api_dry_run(tmp_path):
    Config.OUTPUT_DIR = str(tmp_path)
    token = tiktok_token('cid', 'csecret')
    assert token is not None
    res = post_video('Title', '/path/video.mp4', access_token=token, dry_run=True)
    assert res['status'] == 'dry_run'
    assert os.path.exists(res['preview_path'])


def test_instagram_api_dry_run(tmp_path):
    Config.OUTPUT_DIR = str(tmp_path)
    token = insta_token('cid', 'csecret')
    assert token is not None
    res = post_image('/path/img.jpg', 'caption', access_token=token, dry_run=True)
    assert res['status'] == 'dry_run'
    assert os.path.exists(res['preview_path'])
