import openai
from .config import Config

openai.api_key = Config.OPENAI_API_KEY

class OpenAIClient:
    def __init__(self, model=None):
        self.model = model or Config.OPENAI_MODEL

    def generate_caption(self, product_name, price, affiliate_link):
        prompt = (
            f"เขียนโพสต์ขายของสั้น ๆ ดึงดูด ใช้ Emoji และ Hashtag สำหรับสินค้าต่อไปนี้:\n"
            f"- ชื่อ: {product_name}\n- ราคา: {price} บาท\n- ลิงก์: {affiliate_link}\n"
            "เขียน 1 ย่อหน้า + 3 hashtag ที่เกี่ยวข้อง"
        )

        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.8,
        )
        return resp.choices[0].message["content"].strip()
