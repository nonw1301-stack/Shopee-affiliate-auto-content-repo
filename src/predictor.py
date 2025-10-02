"""Simple heuristic predictor to score (caption, thumbnail) pairs for TikTok FYP likelihood.

This is a lightweight rule-based scorer intended as a starting point. It returns
score in range 0..1 and a short reason breakdown.
"""
from typing import Tuple, List
import re
from PIL import Image, ImageStat
import os
import time
from .openai_client import OpenAIClient
import logging

logger = logging.getLogger(__name__)


# default CTA words and templates (can be overridden via env)
CTA_WORDS = [w.strip() for w in os.getenv("PREDICTOR_CTA_WORDS", "ดูเลย,รีบซื้อ,กดสั่ง,สั่งเลย,อย่าพลาด,ดูตอนนี้,คลิก").split(",") if w.strip()]
CTA_TEMPLATES = [t.strip() for t in os.getenv("PREDICTOR_CTA_TEMPLATES", "อย่าพลาด! {},รีบเลย - {},กดสั่งตอนนี้: {}").split(",") if t.strip()]


def load_trending_hashtags() -> List[str]:
    """Load trending hashtags from env: either a comma-separated list or a path to a file."""
    raw = os.getenv("TRENDING_HASHTAGS")
    if not raw:
        return []
    if os.path.exists(raw):
        try:
            with open(raw, "r", encoding="utf-8") as f:
                tags = [ln.strip() for ln in f if ln.strip()]
                return tags
        except Exception:
            logger.exception("Failed to load trending hashtags from file %s", raw)
            return []
    return [t.strip() for t in raw.split(",") if t.strip()]


def _contrast_score(image_path: str) -> float:
    try:
        im = Image.open(image_path).convert("L")
        stat = ImageStat.Stat(im)
        std = stat.stddev[0]
        return min(1.0, max(0.0, std / 64.0))
    except Exception:
        return 0.5


def _has_price(text: str) -> bool:
    return bool(re.search(r"\d{2,}", str(text)))


def score_variant(caption: str, thumbnail_path: str) -> Tuple[float, dict]:
    """Return (score, details) for a caption+thumbnail pair.

    Scoring weights are conservative; keep values between 0..1.
    """
    details = {}

    # caption length
    ln = len(caption or "")
    if ln < 20:
        len_score = 0.2
    elif ln < 50:
        len_score = 0.7
    elif ln < 150:
        len_score = 1.0
    else:
        len_score = 0.6
    details['len_score'] = len_score

    # CTA presence
    cta = any(w in caption for w in CTA_WORDS)
    details['cta'] = cta
    cta_score = 0.25 if cta else 0.0

    # hashtags count (prefer 1-4)
    hashtags = re.findall(r"#\w+", caption or "")
    hcnt = len(hashtags)
    if hcnt == 0:
        hscore = 0.6
    elif hcnt <= 4:
        hscore = 1.0
    else:
        hscore = 0.5
    details['hashtags'] = hcnt
    details['hscore'] = hscore

    # price mention bonus
    price_bonus = 0.1 if _has_price(caption) else 0.0
    details['price_bonus'] = price_bonus

    # thumbnail contrast
    contrast = _contrast_score(thumbnail_path)
    details['contrast'] = contrast

    # combine heuristics
    score = (0.35 * len_score) + (0.2 * hscore) + (0.2 * contrast) + cta_score + price_bonus
    score = max(0.0, min(1.0, score))

    return score, details


def generate_caption_variants(name: str, price, affiliate_link: str = "", n: int = 3):
    """Generate caption variants using OpenAI if available; fallback to heuristics.

    Uses prompt-engineering that asks for short, catchy Thai captions, includes 1-3 hashtags and a CTA.
    """
    variants = []
    client = None
    try:
        client = OpenAIClient()
    except Exception:
        client = None

    trending = load_trending_hashtags()

    if client:
        prompt = (
            "Create a short, catchy Thai TikTok caption for the product below. "
            "Include 1-3 relevant hashtags (prefix with #) and a clear CTA. Keep it under 120 chars.\n\n"
            f"Product: {name}\nPrice: {price}\nAffiliate link: {affiliate_link}\n"
        )
        for i in range(n):
            try:
                # use a small retry loop for transient OpenAI errors
                attempt = 0
                while attempt < 2:
                    attempt += 1
                    try:
                        c = client.generate_caption_with_prompt(prompt)
                        if not c:
                            raise RuntimeError("Empty caption from OpenAI")
                        # inject trending tag occasionally
                        if trending and (i % 2 == 0):
                            tag = trending[i % len(trending)]
                            if tag not in c:
                                c = c + " " + tag
                        variants.append(c.strip())
                        break
                    except Exception as e:
                        logger.warning("OpenAI caption attempt %s failed: %s", attempt, str(e))
                        time.sleep(0.3)
            except Exception:
                continue

    # fallback heuristic variants
    if not variants:
        base = f"{name} ราคาพิเศษ {price} บาท"
        for i in range(n):
            tag = (trending[i % len(trending)] if trending else "#โปร")
            cta = CTA_TEMPLATES[i % len(CTA_TEMPLATES)].format(base)
            # ensure at least one hashtag and one CTA
            variants.append(f"{cta} {tag}")

    # deduplicate and trim
    seen = set()
    out = []
    for v in variants:
        tv = v.strip()
        if tv and tv not in seen:
            seen.add(tv)
            out.append(tv)
    return out[:n]


def pick_best_variant(name: str, price, affiliate_link: str, thumbnail_paths: list, n_captions: int = 4):
    """Generate caption variants and score combinations with thumbnails; return best caption, thumbnail, and score/details."""
    captions = generate_caption_variants(name, price, affiliate_link, n=n_captions)
    best = None
    best_score = -1
    best_details = None
    best_thumb = None
    for cap in captions:
        for thumb in thumbnail_paths:
            sc, details = score_variant(cap, thumb)
            if sc > best_score:
                best_score = sc
                best = cap
                best_details = details
                best_thumb = thumb
    return {"caption": best, "thumbnail": best_thumb, "score": best_score, "details": best_details}
