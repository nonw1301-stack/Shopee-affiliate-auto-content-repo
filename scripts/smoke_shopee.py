"""Shopee smoke-run helper.

Usage:
  - Dry-run (no real network unless env endpoints set):
      python scripts/smoke_shopee.py --dry-run
  - Real run (requires SHOPEE_PARTNER_ID and SHOPEE_PARTNER_KEY and API base):
      python scripts/smoke_shopee.py --run-real --query "phone case"

The script will:
  - instantiate `ShopeeClient` from env or args
  - perform a search (or popular items), then attempt to generate an affiliate link for the first item
  - print results

Note: Do NOT paste your real partner key into public chat. Run this locally.
"""
import argparse
import os
import json
from src.shopee_client import ShopeeClient


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default)")
    p.add_argument("--run-real", action="store_true", help="Run real API calls if env configured")
    p.add_argument("--query", type=str, help="Search query (optional)")
    p.add_argument("--limit", type=int, default=5)
    args = p.parse_args()

    partner_id = os.getenv("SHOPEE_PARTNER_ID")
    partner_key = os.getenv("SHOPEE_PARTNER_KEY")
    base = os.getenv("SHOPEE_API_BASE")

    client = ShopeeClient(partner_id=partner_id, partner_key=partner_key, base=base)

    try:
        if args.query:
            print(f"Searching for '{args.query}' (limit={args.limit})")
            res = client.search_items(query=args.query, limit=args.limit)
        else:
            print(f"Fetching popular items (limit={args.limit})")
            res = client.search_popular_items(limit=args.limit)
        print(json.dumps(res, indent=2, ensure_ascii=False))

        # pick first item if available
        items = res.get('items') if isinstance(res, dict) else None
        if items:
            first = items[0]
            # Support different shapes: {'item_id': .., 'shopid': ..} or simple tuples
            if isinstance(first, dict):
                item_id = first.get('item_id') or first.get('itemid') or first.get('id')
                shopid = first.get('shopid') or first.get('shop_id') or first.get('shopid')
            elif isinstance(first, (list, tuple)) and len(first) >= 2:
                item_id, shopid = first[0], first[1]
            else:
                item_id, shopid = None, None

            if item_id and shopid:
                print(f"Attempting to generate affiliate link for item={item_id}, shop={shopid}")
                link = client.generate_affiliate_link(item_id, shopid)
                print(json.dumps(link, indent=2, ensure_ascii=False))
            else:
                print("No usable item_id/shopid found in results to generate affiliate link.")
        else:
            print("No items returned from search/popular endpoint.")

    except Exception as e:
        print("Smoke run error:", e)


if __name__ == '__main__':
    main()
