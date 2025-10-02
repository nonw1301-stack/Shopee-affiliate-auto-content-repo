"""Dry-run Instagram poster interface.

Provides a simple upload(image_path, caption, dry_run=True) that writes a preview
JSON file to `Config.OUTPUT_DIR/dry_runs/instagram` when dry_run is True.
"""
from .config import Config
import os
import json
import time
import uuid
import logging

logger = logging.getLogger(__name__)


def upload(image_path: str, caption: str, dry_run: bool = True) -> dict:
    ts = int(time.time())
    post_id = str(uuid.uuid4())

    if dry_run:
        out_dir = os.path.join(Config.OUTPUT_DIR, "dry_runs", "instagram")
        os.makedirs(out_dir, exist_ok=True)
        preview_path = os.path.join(out_dir, f"{post_id}.json")
        payload = {
            "id": post_id,
            "timestamp": ts,
            "caption": caption,
            "image_path": image_path,
            "status": "dry_run",
        }
        with open(preview_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        logger.info("Instagram dry-run created: %s", preview_path)
        return {"status": "dry_run", "preview_path": preview_path, "id": post_id, "timestamp": ts}

    raise NotImplementedError("Real Instagram upload not implemented. Use dry_run=True for previews.")
