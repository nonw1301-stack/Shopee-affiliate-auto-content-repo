import openai
from .config import Config
import logging

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, model=None, api_key=None):
        self.model = model or Config.OPENAI_MODEL
        self.api_key = api_key or Config.OPENAI_API_KEY
        # Allow instantiation without API key to support tests/import-time.
        # If no API key provided, self.client will be None and generate_caption
        # will raise when actually called.
        if self.api_key:
            # Use the v1 client surface
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def generate_caption(self, product_name, price, affiliate_link):
        prompt = (
            f"เขียนโพสต์ขายของสั้น ๆ ดึงดูด ใช้ Emoji และ Hashtag สำหรับสินค้าต่อไปนี้:\n"
            f"- ชื่อ: {product_name}\n- ราคา: {price} บาท\n- ลิงก์: {affiliate_link}\n"
            "เขียน 1 ย่อหน้า + 3 hashtag ที่เกี่ยวข้อง"
        )
        if not self.client:
            raise ValueError("OpenAI client is not configured (missing API key)")

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.8,
            )
            # Safety: navigate response structure
            if resp and resp.choices:
                # Depending on SDK, message content may be nested
                msg = resp.choices[0].message
                return getattr(msg, "content", None) or msg.get("content")
            return None
        except Exception as e:
            logger.exception("OpenAI caption generation failed: %s", e)
            raise
