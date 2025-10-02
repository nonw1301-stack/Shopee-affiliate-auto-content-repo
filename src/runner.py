"""Orchestration runner: generator -> media_creator -> poster (dry-run or real)

Usage:
  python -m src.runner --dry-run
  python -m src.runner --run
"""
import argparse
import logging
import os
from .generator import run_once
from . import media_creator
from . import poster_tiktok_api
from .config import Config
from . import predictor
import time

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", default=False)
    p.add_argument("--run", action="store_true", default=False)
    args = p.parse_args()
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

    logger.info("Starting runner. dry_run=%s", args.dry_run)
    results = run_once()
    logger.info("Generator produced %s items", len(results))

    # For each generated item, produce media and post (dry-run by default)
    for idx, item in enumerate(results):
        title = item.get("title") or item.get("name") or f"item-{idx}"
        price = item.get("price") or item.get("price_min") or ""

        # create an output path per item
        safe_name = title.replace(" ", "_").replace("/", "_")[:50]
        img_out = os.path.join(Config.OUTPUT_DIR, f"banner_{safe_name}_{int(time.time())}.png")

        try:
            logger.info("Creating media for item %s -> %s", title, img_out)
            media_creator.make_banner(title, price, img_out)
        except Exception:
            logger.exception("Failed to create media for %s", title)
            continue

        # Generate caption variants (predictor will use OpenAI if available)
        caption_variants = predictor.generate_caption_variants(title, price, item.get("affiliate_link", ""), n=3)

        # Create thumbnail variants (original + adjusted)
        thumb_variants = [img_out]
        try:
            # brightness/contrast variant
            alt = os.path.join(Config.OUTPUT_DIR, f"banner_{safe_name}_alt_{int(time.time())}.png")
            media_creator.make_banner(title, price, alt)
            thumb_variants.append(alt)
        except Exception:
            logger.exception("Failed to create thumbnail variant for %s", title)

        # Score variants and pick top
        best = None
        best_score = -1.0
        best_details = None
        for cap in caption_variants:
            for thumb in thumb_variants:
                try:
                    sc, details = predictor.score_variant(cap, thumb)
                except Exception:
                    sc, details = 0.0, {}
                if sc > best_score:
                    best_score = sc
                    best = (cap, thumb)
                    best_details = details

        if best is None:
            logger.warning("No viable variant for %s, skipping", title)
            continue

        chosen_caption, chosen_thumb = best
        logger.info("Chosen variant for %s: score=%.3f details=%s", title, best_score, best_details)

        # call poster: if run flag present, try to create a short video and upload via chunked API
        try:
            if args.run:
                # obtain access token (uses token_store if configured, or dev token)
                access_token = poster_tiktok_api.obtain_access_token(os.getenv("TIKTOK_CLIENT_KEY"), os.getenv("TIKTOK_CLIENT_SECRET"))
                # create a short video from the banner as a single-frame video
                video_out = os.path.join(Config.OUTPUT_DIR, f"video_{safe_name}_{int(time.time())}.mp4")
                media_path = media_creator.make_video_from_images([chosen_thumb], video_out)
                logger.info("Uploading video %s with token present=%s", media_path, bool(access_token))
                upload_res = poster_tiktok_api.upload_video_chunked(chosen_caption, media_path, access_token or "", dry_run=False)
                logger.info("Upload result: %s", upload_res)
            else:
                logger.info("Posting to TikTok (dry_run=%s) for %s", True, title)
                post_res = poster_tiktok_api.post_video(chosen_caption, chosen_thumb, access_token=None, dry_run=True)
                logger.info("Post result: %s", post_res)
        except Exception:
            logger.exception("Failed to post item %s", title)

    logger.info("Runner finished")


if __name__ == '__main__':
    main()
