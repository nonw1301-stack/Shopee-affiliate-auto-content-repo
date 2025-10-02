import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from .config import Config
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def retry(exceptions, tries=3, delay=1, backoff=2):
    def deco(func):
        @wraps(func)
        def f(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning("%s failed with %s, retrying in %s seconds...", func.__name__, e, mdelay)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return func(*args, **kwargs)

        return f

    return deco

# NOTE: Shopee Affiliate API มักใช้การเซ็น request/ใช้ partner_id/partner_key.
# ตัวอย่างนี้เป็นโครงร่าง: ให้แทนที่ด้วยเอกสาร Shopee Partner API ของคุณ

class ShopeeClient:
    def __init__(self, partner_id=None, partner_key=None, base=None):
        self.partner_id = partner_id or Config.SHOPEE_PARTNER_ID
        self.partner_key = partner_key or Config.SHOPEE_PARTNER_KEY
        self.base = base or Config.SHOPEE_API_BASE

    def _sign(self, path, payload):
        # Default signing: HMAC-SHA256 over (path + sorted_payload + timestamp)
        # Many Shopee Partner APIs require a timestamp and HMAC using partner_key.
        # This implementation is a reasonable starting point but MUST be adjusted
        # to match Shopee's official spec for your region.
        ts = str(int(time.time()))
        # Prepare payload string deterministically
        if isinstance(payload, dict):
            # sort keys to ensure consistent signing
            try:
                items = sorted(payload.items())
                payload_str = urlencode(items)
            except Exception:
                payload_str = str(payload)
        else:
            payload_str = str(payload)

        message = path + payload_str + ts
        if not self.partner_key:
            return ""
        sig = hmac.new(self.partner_key.encode(), message.encode(), hashlib.sha256).hexdigest()
        # return signature and timestamp so callers can set headers
        return sig, ts

    @retry((requests.RequestException, ), tries=3, delay=1, backoff=2)
    def search_popular_items(self, limit=10):
        # ตัวอย่าง endpoint สมมติ: /items/popular
        path = "/items/popular"
        url = f"{self.base}{path}"
        params = {"partner_id": self.partner_id, "limit": limit}
        sig = self._sign(path, params)
        if isinstance(sig, tuple):
            signature, ts = sig
            headers = {"Content-Type": "application/json", "X-Signature": signature, "X-Timestamp": ts}
        else:
            headers = {"Content-Type": "application/json", "X-Signature": sig}
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        logger.info("Fetched popular items, count=%s", len(resp.json().get('items', [])))
        return resp.json()

    @retry((requests.RequestException, ), tries=3, delay=1, backoff=2)
    def generate_affiliate_link(self, item_id, shop_id):
        # สมมติ endpoint: /items/generate_affiliate
        path = "/items/generate_affiliate"
        url = f"{self.base}{path}"
        payload = {"partner_id": self.partner_id, "item_id": item_id, "shopid": shop_id}
        sig = self._sign(path, payload)
        if isinstance(sig, tuple):
            signature, ts = sig
            headers = {"Content-Type": "application/json", "X-Signature": signature, "X-Timestamp": ts}
        else:
            headers = {"Content-Type": "application/json", "X-Signature": sig}
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        logger.info("Generated affiliate link for item=%s", item_id)
        return resp.json()
