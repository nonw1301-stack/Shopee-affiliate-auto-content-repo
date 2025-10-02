import os
from unittest.mock import MagicMock
import tempfile

from src.poster_tiktok_api import upload_video_chunked, Config


def test_upload_video_chunked(monkeypatch, tmp_path):
    # create a small fake video file
    f = tmp_path / "video.bin"
    data = b"0123456789" * 1024  # ~10KB
    f.write_bytes(data)

    # mock initiate_upload_session to return small part_size and template
    def fake_initiate(access_token, file_size):
        return {"upload_id": "u1", "part_size": 4096, "upload_url_template": "https://example.com/upload/{upload_id}/{part_number}"}

    # mock upload_chunk to assert calls
    calls = []

    def fake_upload_chunk(upload_url, chunk_data, part_number, headers=None):
        calls.append((upload_url, len(chunk_data), part_number, headers.get('X-Chunk-MD5') if headers else None))
        # return server ack with md5 to validate
        return {"status": "ok", "part": part_number, "md5": headers.get('X-Chunk-MD5') if headers else None}

    def fake_commit(access_token, upload_id):
        return {"status": "committed", "upload_id": upload_id}

    monkeypatch.setattr('src.poster_tiktok_api.initiate_upload_session', fake_initiate)
    monkeypatch.setattr('src.poster_tiktok_api.upload_chunk', fake_upload_chunk)
    monkeypatch.setattr('src.poster_tiktok_api.commit_upload', fake_commit)

    # ensure uploader uses temporary output dir (avoid stale state files)
    monkeypatch.setattr(Config, 'OUTPUT_DIR', str(tmp_path))

    res = upload_video_chunked('T', str(f), 'token', dry_run=False)
    assert res.get('status') == 'committed'
    # ensure at least 1 chunk uploaded
    assert len(calls) >= 1
