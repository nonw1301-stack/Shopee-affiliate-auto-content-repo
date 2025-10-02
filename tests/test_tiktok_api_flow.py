import os
import json
import tempfile
from unittest.mock import patch, MagicMock

from src.poster_tiktok_api import exchange_code_for_token, post_video


def test_exchange_code_for_token(monkeypatch, tmp_path):
    os.environ['TIKTOK_TOKEN_URL'] = 'https://api.example.com/token'

    fake_resp = MagicMock()
    fake_resp.json.return_value = {"access_token": "abc", "expires_in": 3600}
    fake_resp.raise_for_status.return_value = None

    def fake_post(url, data=None, timeout=None):
        assert url == os.environ['TIKTOK_TOKEN_URL']
        # assert required fields exist
        assert 'client_key' in data and 'code' in data
        return fake_resp

    monkeypatch.setattr('src.poster_tiktok_api.requests.post', fake_post)

    res = exchange_code_for_token('cid', 'csecret', 'code123', 'https://app/callback')
    assert res.get('access_token') == 'abc'


def test_post_video_upload_invokes_requests(monkeypatch, tmp_path):
    # setup a temp file to represent video
    vid = tmp_path / "video.mp4"
    vid.write_bytes(b"fakevideo")

    os.environ['TIKTOK_UPLOAD_URL'] = 'https://api.example.com/upload'

    fake_resp = MagicMock()
    fake_resp.json.return_value = {"id": "123"}
    fake_resp.raise_for_status.return_value = None

    def fake_post(url, headers=None, files=None, timeout=None):
        assert url == os.environ['TIKTOK_UPLOAD_URL']
        # ensure file key present
        assert 'video' in files
        return fake_resp

    monkeypatch.setattr('src.poster_tiktok_api.requests.post', fake_post)

    res = post_video('My Title', str(vid), access_token='token', dry_run=False)
    assert res.get('id') == '123'
