"""Dry-run TikTok poster interface.

Provides a simple upload(text, media_path, dry_run=True) function that writes a
preview JSON file to `Config.OUTPUT_DIR/dry_runs/tiktok` when dry_run is True.
Real upload is intentionally not implemented in this scaffold.
"""
from .config import Config
import os
import json
import time
import uuid
import logging

logger = logging.getLogger(__name__)


def upload(text: str, media_path: str, dry_run: bool = True) -> dict:
    """Upload a TikTok post. In dry_run mode, write a preview JSON and return metadata.

    Returns a dict with keys: status, preview_path, id, timestamp
    """
    ts = int(time.time())
    post_id = str(uuid.uuid4())

    if dry_run:
        out_dir = os.path.join(Config.OUTPUT_DIR, "dry_runs", "tiktok")
        os.makedirs(out_dir, exist_ok=True)
        preview_path = os.path.join(out_dir, f"{post_id}.json")
        payload = {
            "id": post_id,
            "timestamp": ts,
            "text": text,
            "media_path": media_path,
            "status": "dry_run",
        }
        with open(preview_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        logger.info("TikTok dry-run created: %s", preview_path)
        return {"status": "dry_run", "preview_path": preview_path, "id": post_id, "timestamp": ts}

    # Placeholder for real implementation
    raise NotImplementedError("Real TikTok upload not implemented. Use dry_run=True for previews.")
