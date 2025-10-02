from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SHOPEE_PARTNER_ID = os.getenv("SHOPEE_PARTNER_ID")
    SHOPEE_PARTNER_KEY = os.getenv("SHOPEE_PARTNER_KEY")
    SHOPEE_API_BASE = os.getenv("SHOPEE_API_BASE", "https://partner.shopeemobile.com/api/v1")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
    MAX_PRODUCTS = int(os.getenv("MAX_PRODUCTS", 5))
