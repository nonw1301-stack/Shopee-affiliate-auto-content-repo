import openai
from dotenv import load_dotenv
import os

# โหลดค่า API Key จากไฟล์ .env (ถ้ามี)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("กรุณาตั้งค่า OPENAI_API_KEY ในไฟล์ .env หรือ environment variable ก่อนใช้งาน!")

client = openai.OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, OpenAI!"}]
)
print(response.choices[0].message.content)
