import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from .config import Config

# NOTE: Shopee Affiliate API มักใช้การเซ็น request/ใช้ partner_id/partner_key.
# ตัวอย่างนี้เป็นโครงร่าง: ให้แทนที่ด้วยเอกสาร Shopee Partner API ของคุณ

class ShopeeClient:
    def __init__(self, partner_id=None, partner_key=None, base=None):
        self.partner_id = partner_id or Config.SHOPEE_PARTNER_ID
        self.partner_key = partner_key or Config.SHOPEE_PARTNER_KEY
        self.base = base or Config.SHOPEE_API_BASE

    def _sign(self, path, payload):
        # placeholder: implement Shopee signing ifจำเป็น
        message = path + str(int(time.time()))
        return hmac.new(self.partner_key.encode(), message.encode(), hashlib.sha256).hexdigest()

    def search_popular_items(self, limit=10):
        # ตัวอย่าง endpoint สมมติ: /items/popular
        path = "/items/popular"
        url = f"{self.base}{path}"
        params = {"partner_id": self.partner_id, "limit": limit}
        headers = {"Content-Type": "application/json", "X-Signature": self._sign(path, params)}
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def generate_affiliate_link(self, item_id, shop_id):
        # สมมติ endpoint: /items/generate_affiliate
        path = "/items/generate_affiliate"
        url = f"{self.base}{path}"
        payload = {"partner_id": self.partner_id, "item_id": item_id, "shopid": shop_id}
        headers = {"Content-Type": "application/json", "X-Signature": self._sign(path, payload)}
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
