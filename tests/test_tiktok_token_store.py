import os
import json
import tempfile
from unittest.mock import patch, MagicMock

import src.token_store as ts


def test_token_store_save_load(monkeypatch, tmp_path):
    # create a fake Fernet implementation if cryptography not available
    class FakeFernet:
        def __init__(self, key):
            pass

        def encrypt(self, payload):
            return payload[::-1]

        def decrypt(self, blob):
            return blob[::-1]

    monkeypatch.setenv('FERNET_KEY', 'testkey')
    monkeypatch.setattr(ts, 'Fernet', FakeFernet)

    path = tmp_path / 'tokens.enc'
    data = {'access_token': 'abc'}
    ts.save_tokens(data, path=str(path))
    loaded = ts.load_tokens(path=str(path))
    assert loaded == data


def test_refresh_flow(monkeypatch):
    from src.poster_tiktok_api import refresh_access_token
    monkeypatch.setenv('TIKTOK_REFRESH_URL', 'https://api.example.com/refresh')

    fake_resp = MagicMock()
    fake_resp.json.return_value = {'access_token': 'new', 'refresh_token': 'r2'}
    fake_resp.raise_for_status.return_value = None

    def fake_post(url, data=None, timeout=None):
        assert url == 'https://api.example.com/refresh'
        assert data.get('refresh_token') == 'oldrefresh'
        return fake_resp

    monkeypatch.setattr('src.poster_tiktok_api.requests.post', fake_post)
    res = refresh_access_token('cid', 'csecret', 'oldrefresh')
    assert res.get('access_token') == 'new'
