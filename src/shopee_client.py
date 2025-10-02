import time
import hmac
import hashlib
import requests
import json
from urllib.parse import urlencode
from .config import Config
import logging
from functools import wraps
import os

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
                    # Special handling for HTTP 429 (rate limit) when available
                    status = None
                    if hasattr(e, 'response') and getattr(e.response, 'status_code', None):
                        status = e.response.status_code
                    if status == 429:
                        # exponential backoff + extra multiplier for rate limits
                        wait = mdelay * 5
                        logger.warning("%s rate-limited (429). waiting %s seconds before retry...", func.__name__, wait)
                        time.sleep(wait)
                        mtries -= 1
                        mdelay *= backoff
                        continue

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
        # signing mode can be overridden via env var SHOPEE_SIGN_MODE
        # supported modes:
        #  - A: HMAC over (path + sorted_query_or_body + timestamp)  (default)
        #  - B: HMAC over (partner_id + path + timestamp)
        #  - C: HMAC over (method + path + timestamp + body)
        self.sign_mode = os.getenv("SHOPEE_SIGN_MODE", "A").upper()

    def _sign(self, path, payload=None, method: str = "GET"):
        """Create HMAC-SHA256 signature for a request.

        Canonicalization rules used here (adjust if Shopee spec differs):
          - GET: canonicalize query params as sorted urlencode
          - POST/others: canonicalize JSON with sorted keys and no extra whitespace

        Returns (signature_or_None, timestamp).
        If partner_key is missing, returns (None, timestamp) and logs a warning to
        allow local testing without secrets.
        """
        ts = str(int(time.time()))

        canonical = ""
        try:
            if payload is None:
                canonical = ""
            elif isinstance(payload, dict):
                if method.upper() == "GET":
                    canonical = urlencode(sorted(payload.items()))
                else:
                    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
            else:
                canonical = str(payload)
        except Exception:
            canonical = str(payload)

        # Build message according to configured signing mode
        if self.sign_mode == "A":
            message = (path or "") + canonical + ts
        elif self.sign_mode == "B":
            message = (self.partner_id or "") + (path or "") + ts
        elif self.sign_mode == "C":
            message = method.upper() + (path or "") + ts + canonical
        else:
            # fallback to mode A
            message = (path or "") + canonical + ts

        if not self.partner_key:
            logger.warning("Shopee partner key not configured; signature disabled. Set SHOPEE_PARTNER_KEY for production use.")
            return None, ts

        sig = hmac.new(self.partner_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()
        return sig, ts

    def search_items(self, query: str = None, limit: int = 20):
        """Search items. If query is None, fall back to a popular items endpoint."""
        if query:
            path = "/items/search"
            url = f"{self.base}{path}"
            params = {"partner_id": self.partner_id, "q": query, "limit": limit}
            signature, ts = self._sign(path, params, method="GET")
            headers = {"Content-Type": "application/json"}
            if signature:
                headers.update({"X-Signature": signature, "X-Timestamp": ts})
            else:
                headers.update({"X-Timestamp": ts})

            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.json()
        else:
            return self.search_popular_items(limit=limit)

    def build_affiliate_link(self, item_id: int, shop_id: int) -> str:
        """Fallback affiliate link builder when the partner API does not return a direct link.

        You can override this by setting env `SHOPEE_AFFILIATE_URL_TEMPLATE`, where
        placeholders {item_id}, {shop_id}, and {partner_id} are supported.
        """
        tpl = os.getenv("SHOPEE_AFFILIATE_URL_TEMPLATE")
        if tpl:
            return tpl.replace("{item_id}", str(item_id)).replace("{shop_id}", str(shop_id)).replace("{partner_id}", str(self.partner_id or ""))
        # default fallback (not guaranteed to be valid for all Shopee locales)
        return f"https://shopee.com/product/{shop_id}/{item_id}?af={self.partner_id or ''}"

    @retry((requests.RequestException, ), tries=3, delay=1, backoff=2)
    def search_popular_items(self, limit=10):
        # ตัวอย่าง endpoint สมมติ: /items/popular
        path = "/items/popular"
        url = f"{self.base}{path}"
        params = {"partner_id": self.partner_id, "limit": limit}
        signature, ts = self._sign(path, params, method="GET")
        headers = {"Content-Type": "application/json"}
        if signature:
            headers.update({"X-Signature": signature, "X-Timestamp": ts})
        else:
            headers.update({"X-Timestamp": ts})

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
        signature, ts = self._sign(path, payload, method="POST")
        headers = {"Content-Type": "application/json"}
        if signature:
            headers.update({"X-Signature": signature, "X-Timestamp": ts})
        else:
            headers.update({"X-Timestamp": ts})

        # If partner_key is not set, return a locally-built affiliate link for dry-run/dev
        if not self.partner_key:
            logger.info("Partner key missing: returning fallback affiliate link for item=%s", item_id)
            return {"affiliate_link": self.build_affiliate_link(item_id, shop_id)}

        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        j = resp.json()
        # try a few common keys to locate affiliate URL in provider response
        for k in ("affiliate_link", "affiliate_url", "link", "url"):
            if isinstance(j, dict) and j.get(k):
                return {"affiliate_link": j.get(k), "raw": j}

        # fallback: attempt to build one
        return {"affiliate_link": self.build_affiliate_link(item_id, shop_id), "raw": j}


if __name__ == "__main__":
    # Small smoke-run to verify signing logic locally. Not a replacement for unit tests.
    import os
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    client = ShopeeClient(partner_id="testpid", partner_key=os.getenv("SHOPEE_PARTNER_KEY"))
    sig, ts = client._sign("/items/popular", {"limit": 2, "partner_id": "testpid"}, method="GET")
    print("signature:", sig)
    print("timestamp:", ts)
