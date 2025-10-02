"""Instagram API poster skeleton.

Provides a small helper for obtaining an access token (stub) and a `post_image`
function that supports dry-run preview files.
"""
from .config import Config
import os
import json
import time
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)


_TOKEN_STORE = {}


def obtain_access_token(client_id: str, client_secret: str) -> Optional[str]:
    if not client_id or not client_secret:
        return None
    token = f"fake-instagram-token-{uuid.uuid4()}"
    _TOKEN_STORE['access_token'] = token
    _TOKEN_STORE['expires_at'] = int(time.time()) + 3600
    return token


def post_image(image_path: str, caption: str, access_token: Optional[str] = None, dry_run: bool = True) -> dict:
    ts = int(time.time())
    post_id = str(uuid.uuid4())

    if dry_run:
        out_dir = os.path.join(Config.OUTPUT_DIR, "dry_runs", "instagram_api")
        os.makedirs(out_dir, exist_ok=True)
        preview_path = os.path.join(out_dir, f"{post_id}.json")
        payload = {"id": post_id, "timestamp": ts, "caption": caption, "image_path": image_path, "status": "dry_run"}
        with open(preview_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return {"status": "dry_run", "preview_path": preview_path, "id": post_id}

    raise NotImplementedError("Real Instagram API posting is not implemented in this scaffold.")
