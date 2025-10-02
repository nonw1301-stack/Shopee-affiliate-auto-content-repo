from .shopee_client import ShopeeClient
from .openai_client import OpenAIClient
from .config import Config
from .db import DB
import os
import logging

logger = logging.getLogger(__name__)

shopee = None
openai_client = None
# instantiate DB lazily so tests can patch Config.OUTPUT_DIR / DB easily
db = None



def run_once():
    # ensure output dir exists (Config may be updated by tests before calling)
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

    global db, shopee, openai_client
    if db is None:
        db = DB()

    # lazy init clients so tests that patch the client classes work
    if shopee is None:
        shopee = ShopeeClient()
    if openai_client is None:
        openai_client = OpenAIClient()

    items = shopee.search_popular_items(limit=Config.MAX_PRODUCTS)
    # Developer/testing: force a sample item when Shopee returns empty and env flag is set
    if (not items or not items.get("items")) and os.getenv("DEV_FORCE_ITEMS"):
        items = {"items": [{"itemid": "dev-1", "shopid": "dev-shop", "name": "ตัวอย่างสินค้า", "price": 19900000}]}
    # สมมติ response มี items list
    results = []
    for it in items.get("items", [])[: Config.MAX_PRODUCTS]:
        itemid = it.get("itemid") or it.get("item_id")
        shopid = it.get("shopid") or it.get("shop_id")
        # Skip if already posted
        if db.is_posted(str(itemid)):
            continue
        name = it.get("name")
        price = (it.get("price") or 0) / 100000

        try:
            aff = shopee.generate_affiliate_link(itemid, shopid)
            aff_link = aff.get("affiliate_link") or aff.get("url")

            caption = openai_client.generate_caption(name, price, aff_link)
        except Exception as e:
            logger.exception("Failed to process item %s: %s", itemid, e)
            continue

        out = {
            "name": name,
            "price": price,
            "affiliate_link": aff_link,
            "caption": caption,
        }
        results.append(out)

        # บันทึกออกไฟล์ (json/text)
        slug = name.replace(" ", "_")[:40]
        with open(os.path.join(Config.OUTPUT_DIR, f"{slug}.txt"), "w", encoding="utf-8") as f:
            f.write(caption + "\n\n" + aff_link)
        # Mark as posted in DB
        db.mark_posted(str(itemid), str(shopid))

    return results

if __name__ == "__main__":
    r = run_once()
    print("Generated", len(r), "items")
