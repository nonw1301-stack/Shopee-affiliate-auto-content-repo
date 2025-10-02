"""TikTok API poster skeleton.

This module provides a minimal OAuth token helper and a `post_video` function
that currently supports dry-run mode (writes preview JSON). The real HTTP
integration is left as a TODO since it requires app credentials and platform
agreement.
"""
from .config import Config
import os
import json
import time
import uuid
import logging
from typing import Optional
import requests
from . import token_store
import hashlib
import concurrent.futures
import math
from pathlib import Path

logger = logging.getLogger(__name__)


# In-memory token store for this scaffold. Replace with persistent storage if needed.
_TOKEN_STORE = {}


def get_authorize_url(client_key: str, redirect_uri: str, scope: str = "user.info.basic,video.upload", state: Optional[str] = None) -> str:
    """Return the TikTok authorization URL for redirecting users.

    Uses `TIKTOK_AUTH_URL` from env if present, otherwise defaults to TikTok's
    documented authorization endpoint.
    """
    base = os.getenv("TIKTOK_AUTH_URL", "https://www.tiktok.com/v2/auth/authorize/")
    params = {
        "client_key": client_key,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": redirect_uri,
    }
    if state:
        params["state"] = state
    qs = requests.utils.requote_uri("?" + "&".join(f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()))
    return base + qs


def exchange_code_for_token(client_key: str, client_secret: str, code: str, redirect_uri: str) -> dict:
    """Exchange an authorization code for an access token.

    The token endpoint URL is taken from env var `TIKTOK_TOKEN_URL` or the
    caller must set it in Config/TIKTOK settings. This function returns the
    parsed JSON response from the token endpoint.
    """
    token_url = os.getenv("TIKTOK_TOKEN_URL")
    if not token_url:
        raise RuntimeError("TIKTOK_TOKEN_URL not configured in env. Set the token endpoint before calling exchange_code_for_token.")

    data = {
        "client_key": client_key,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }

    resp = requests.post(token_url, data=data, timeout=15)
    resp.raise_for_status()
    j = resp.json()
    # persist tokens securely (if token_store available)
    try:
        token_store.save_tokens(j)
    except Exception:
        _TOKEN_STORE.update(j)
    return j


def obtain_access_token(client_key: str, client_secret: str) -> Optional[str]:
    """Obtain an access token for development/testing.

    If a real token endpoint is configured, callers should perform the full
    OAuth flow (redirect user -> exchange code). This helper returns a fake
    token for local/dev use and persists it via token_store when possible.
    """
    if not client_key or not client_secret:
        return None

    # If we already have saved tokens, return the access_token
    try:
        saved = token_store.load_tokens()
        if saved.get('access_token'):
            return saved['access_token']
    except Exception:
        pass

    # generate a fake token for local testing
    token = f"dev-token-{uuid.uuid4()}"
    payload = {'access_token': token, 'expires_in': 3600}
    try:
        token_store.save_tokens(payload)
    except Exception:
        _TOKEN_STORE.update(payload)
    return token


def post_video(title: str, video_path: str, access_token: Optional[str] = None, dry_run: bool = True) -> dict:
    """Upload a video using TikTok Content Posting API.

    If `dry_run` is True, a preview JSON is written and returned. For a real
    upload, the environment must set `TIKTOK_UPLOAD_URL` to the correct
    endpoint and `access_token` must be a valid OAuth token.
    """
    ts = int(time.time())
    post_id = str(uuid.uuid4())

    if dry_run:
        out_dir = os.path.join(Config.OUTPUT_DIR, "dry_runs", "tiktok_api")
        os.makedirs(out_dir, exist_ok=True)
        preview_path = os.path.join(out_dir, f"{post_id}.json")
        payload = {"id": post_id, "timestamp": ts, "title": title, "video_path": video_path, "status": "dry_run"}
        with open(preview_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return {"status": "dry_run", "preview_path": preview_path, "id": post_id}

    upload_url = os.getenv("TIKTOK_UPLOAD_URL")
    if not upload_url:
        raise RuntimeError("TIKTOK_UPLOAD_URL not configured. Set the upload endpoint to enable real uploads.")

    headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

    # The real TikTok API may require multipart/form-data upload and additional
    # parameters; here we attempt a minimal implementation that callers can
    # adapt based on the API response.
    with open(video_path, "rb") as fh:
        files = {"video": fh}
        resp = requests.post(upload_url, headers=headers, files=files, timeout=60)
    resp.raise_for_status()
    return resp.json()


def initiate_upload_session(access_token: str, file_size: int) -> dict:
    """Initiate an upload session. Endpoint taken from env `TIKTOK_INIT_UPLOAD_URL`.

    Returns session metadata (upload_id, part_size, upload_url_template)
    """
    url = os.getenv("TIKTOK_INIT_UPLOAD_URL")
    if not url:
        raise RuntimeError("TIKTOK_INIT_UPLOAD_URL not configured")

    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.post(url, json={"file_size": file_size}, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def upload_chunk(upload_url: str, chunk_data: bytes, part_number: int, headers: dict = None) -> dict:
    """Upload a single chunk to the given URL. Returns server response JSON."""
    headers = headers or {}
    files = {"file": (f"part-{part_number}", chunk_data)}
    resp = requests.post(upload_url, files=files, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()


def commit_upload(access_token: str, upload_id: str) -> dict:
    """Commit the multipart upload session. Endpoint from `TIKTOK_COMMIT_UPLOAD_URL`."""
    url = os.getenv("TIKTOK_COMMIT_UPLOAD_URL")
    if not url:
        raise RuntimeError("TIKTOK_COMMIT_UPLOAD_URL not configured")
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.post(url, json={"upload_id": upload_id}, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def upload_video_chunked(title: str, video_path: str, access_token: str, dry_run: bool = True) -> dict:
    """High-level orchestrator to upload a video using chunked upload.

    Steps:
      1. initiate_upload_session(file_size)
      2. split file into parts (session.part_size)
      3. upload_chunk for each part
      4. commit_upload(upload_id)

    This implementation is resilient and uses simple retries for each chunk.
    """
    if dry_run:
        return post_video(title, video_path, access_token=access_token, dry_run=True)

    # 1. Initiate
    file_size = os.path.getsize(video_path)
    session = initiate_upload_session(access_token, file_size)
    upload_id = session.get("upload_id")
    part_size = int(session.get("part_size", 5 * 1024 * 1024))
    upload_url_template = session.get("upload_url_template")

    # 2-3. Upload parts with MD5 checksums, resume support, server validation and parallel uploads
    state_path = Path(Config.OUTPUT_DIR) / f"upload_state_{upload_id}.json"
    state = {"uploaded_parts": {}}
    if state_path.exists():
        try:
            with open(state_path, "r", encoding="utf-8") as sf:
                state = json.load(sf)
        except Exception:
            state = {"uploaded_parts": {}}

    def md5_hex(b: bytes) -> str:
        m = hashlib.md5()
        m.update(b)
        return m.hexdigest()

    # read and split file into parts first so we can upload in parallel
    file_size = os.path.getsize(video_path)
    total_parts = math.ceil(file_size / part_size) if part_size > 0 else 1

    parts = []  # list of (part_number, offset, length)
    for part_number in range(1, total_parts + 1):
        offset = (part_number - 1) * part_size
        length = min(part_size, file_size - offset)
        parts.append((part_number, offset, length))

    max_workers = int(os.getenv("TIKTOK_UPLOAD_WORKERS", "4"))

    def upload_part(part_info):
        part_number, offset, length = part_info
        # skip if already uploaded
        if str(part_number) in state.get("uploaded_parts", {}):
            return {"status": "skipped", "part": part_number}

        # derive upload URL per-part if template provided
        if upload_url_template:
            upload_url = upload_url_template.replace("{part_number}", str(part_number)).replace("{upload_id}", upload_id)
        else:
            upload_url = os.getenv("TIKTOK_PART_UPLOAD_URL")

        # read chunk
        with open(video_path, "rb") as fh:
            fh.seek(offset)
            chunk = fh.read(length)

        checksum = md5_hex(chunk)
        headers = {"Authorization": f"Bearer {access_token}", "X-Chunk-MD5": checksum}

        # retry per-part
        tries = 3
        last_exc = None
        while tries:
            try:
                resp = upload_chunk(upload_url, chunk, part_number, headers=headers)
                # validation: check server ack md5 matches local checksum
                server_md5 = None
                if isinstance(resp, dict):
                    server_md5 = resp.get("md5") or resp.get("server_md5") or resp.get("checksum")
                if server_md5 and server_md5 != checksum:
                    raise RuntimeError(f"MD5 mismatch for part {part_number}: server={server_md5} local={checksum}")

                # mark uploaded with server response and checksum
                state.setdefault("uploaded_parts", {})[str(part_number)] = {"md5": checksum, "resp": resp}
                # persist state
                state_path.parent.mkdir(parents=True, exist_ok=True)
                with open(state_path, "w", encoding="utf-8") as sf:
                    json.dump(state, sf)
                return {"status": "ok", "part": part_number}
            except Exception as e:
                last_exc = e
                tries -= 1
        raise last_exc

    # run uploads in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as exe:
        futures = {exe.submit(upload_part, p): p[0] for p in parts}
        for fut in concurrent.futures.as_completed(futures):
            part_no = futures[fut]
            try:
                r = fut.result()
                results.append(r)
            except Exception as e:
                logger.exception("Failed to upload part %s", part_no)
                raise
    # 4. Commit
    result = commit_upload(access_token, upload_id)
    return result


def refresh_access_token(client_key: str, client_secret: str, refresh_token: str) -> dict:
    """Refresh access token using a refresh token. Endpoint taken from env `TIKTOK_REFRESH_URL`.

    Stores new tokens via token_store when available.
    """
    refresh_url = os.getenv("TIKTOK_REFRESH_URL")
    if not refresh_url:
        raise RuntimeError("TIKTOK_REFRESH_URL not configured in env.")

    data = {"client_key": client_key, "client_secret": client_secret, "grant_type": "refresh_token", "refresh_token": refresh_token}
    resp = requests.post(refresh_url, data=data, timeout=15)
    resp.raise_for_status()
    j = resp.json()
    try:
        token_store.save_tokens(j)
    except Exception:
        _TOKEN_STORE.update(j)
    return j

