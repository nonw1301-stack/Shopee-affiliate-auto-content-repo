import openai
from .config import Config
import logging

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, model=None, api_key=None):
        self.model = model or Config.OPENAI_MODEL
        self.api_key = api_key or Config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")
        # Use the v1 client surface
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_caption(self, product_name, price, affiliate_link):
        prompt = (
            f"เขียนโพสต์ขายของสั้น ๆ ดึงดูด ใช้ Emoji และ Hashtag สำหรับสินค้าต่อไปนี้:\n"
            f"- ชื่อ: {product_name}\n- ราคา: {price} บาท\n- ลิงก์: {affiliate_link}\n"
            "เขียน 1 ย่อหน้า + 3 hashtag ที่เกี่ยวข้อง"
        )
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
