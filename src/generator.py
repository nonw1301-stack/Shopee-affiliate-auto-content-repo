from .shopee_client import ShopeeClient
from .openai_client import OpenAIClient
from .config import Config
import os

shopee = ShopeeClient()
openai_client = OpenAIClient()

os.makedirs(Config.OUTPUT_DIR, exist_ok=True)


def run_once():
    items = shopee.search_popular_items(limit=Config.MAX_PRODUCTS)
    # สมมติ response มี items list
    results = []
    for it in items.get("items", [])[: Config.MAX_PRODUCTS]:
        itemid = it.get("itemid") or it.get("item_id")
        shopid = it.get("shopid") or it.get("shop_id")
        name = it.get("name")
        price = (it.get("price") or 0) / 100000

        aff = shopee.generate_affiliate_link(itemid, shopid)
        aff_link = aff.get("affiliate_link") or aff.get("url")

        caption = openai_client.generate_caption(name, price, aff_link)

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

    return results

if __name__ == "__main__":
    r = run_once()
    print("Generated", len(r), "items")
