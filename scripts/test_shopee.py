"""Simple script to validate Shopee partner credentials and fetch popular items.

Usage (PowerShell):
  $env:SHOPEE_PARTNER_ID = '...'; $env:SHOPEE_PARTNER_KEY = '...'; python .\scripts\test_shopee.py

The script will print a short sample of items and an affiliate link per item.
"""
import os
import json
import logging
from src.shopee_client import ShopeeClient

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))

def main():
    partner_id = os.getenv('SHOPEE_PARTNER_ID')
    partner_key = os.getenv('SHOPEE_PARTNER_KEY')
    api_base = os.getenv('SHOPEE_API_BASE')

    if not partner_id:
        print('Set SHOPEE_PARTNER_ID in environment and rerun')
        return

    client = ShopeeClient(partner_id=partner_id, partner_key=partner_key, base=api_base)

    print('Using ShopeeClient with partner_id=', partner_id, 'base=', client.base)
    try:
        data = client.search_popular_items(limit=5)
    except Exception as e:
        print('Error fetching popular items:', e)
        return

    items = data.get('items') if isinstance(data, dict) else None
    if not items:
        print('No items returned. Raw response:')
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print(f'Got {len(items)} items. Showing up to 5:')
    for it in items[:5]:
        # normalize common fields
        item_id = it.get('item_id') or it.get('id') or it.get('itemid')
        shop_id = it.get('shop_id') or it.get('shopid') or it.get('shop')
        title = it.get('title') or it.get('name') or it.get('item_name')
        print('-' * 40)
        print('title:', title)
        print('item_id:', item_id, 'shop_id:', shop_id)
        try:
            link_res = client.generate_affiliate_link(item_id, shop_id)
            print('affiliate_link:', link_res.get('affiliate_link') if isinstance(link_res, dict) else link_res)
        except Exception as e:
            print('Failed to generate affiliate link for item:', e)

if __name__ == '__main__':
    main()
