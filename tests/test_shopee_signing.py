import os
import hmac
import hashlib
from src.shopee_client import ShopeeClient


def deterministic_sig(message: str, key: str) -> str:
    return hmac.new(key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()


def test_sign_mode_a():
    os.environ['SHOPEE_SIGN_MODE'] = 'A'
    client = ShopeeClient(partner_id='pid', partner_key='pkey', base='https://example.com')
    # path + canonical(query) + ts
    path = '/items/popular'
    params = {'limit': 2, 'partner_id': 'pid'}
    sig, ts = client._sign(path, params, method='GET')
    # recompute expected
    canonical = 'limit=2&partner_id=pid'
    expected = deterministic_sig(path + canonical + ts, 'pkey')
    assert sig == expected


def test_sign_mode_b():
    os.environ['SHOPEE_SIGN_MODE'] = 'B'
    client = ShopeeClient(partner_id='pid', partner_key='pkey', base='https://example.com')
    path = '/items/popular'
    sig, ts = client._sign(path, None, method='GET')
    expected = deterministic_sig('pid' + path + ts, 'pkey')
    assert sig == expected


def test_sign_mode_c():
    os.environ['SHOPEE_SIGN_MODE'] = 'C'
    client = ShopeeClient(partner_id='pid', partner_key='pkey', base='https://example.com')
    path = '/items/generate_affiliate'
    payload = {'partner_id': 'pid', 'item_id': '1001'}
    sig, ts = client._sign(path, payload, method='POST')
    # canonical json (no spaces, sorted keys)
    canonical = '{"item_id":"1001","partner_id":"pid"}'
    message = 'POST' + path + ts + canonical
    expected = deterministic_sig(message, 'pkey')
    assert sig == expected