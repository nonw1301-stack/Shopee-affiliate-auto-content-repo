import pytest
from unittest.mock import patch, MagicMock
import requests

from src.shopee_client import ShopeeClient


def test_search_popular_items_success(monkeypatch):
    client = ShopeeClient(partner_id='p', partner_key='k', base='https://example.com')

    # patch requests.get to return a fake response
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"items": [1, 2, 3]}
    mock_resp.raise_for_status.return_value = None

    monkeypatch.setattr('src.shopee_client.requests.get', lambda url, params, headers, timeout: mock_resp)

    res = client.search_popular_items(limit=2)
    assert res.get('items') == [1, 2, 3]


def test_search_popular_items_rate_limit_retry(monkeypatch):
    client = ShopeeClient(partner_id='p', partner_key='k', base='https://example.com')

    call_count = {'n': 0}

    class FakeResp:
        def __init__(self, status_code, json_data=None):
            self.status_code = status_code
            self._json = json_data or {"items": [1]}

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(response=self)

        def json(self):
            return self._json

    def fake_get(url, params=None, headers=None, timeout=None):
        import pytest
        from unittest.mock import MagicMock
        import requests

        from src.shopee_client import ShopeeClient


        def test_search_popular_items_success(monkeypatch):
            client = ShopeeClient(partner_id='p', partner_key='k', base='https://example.com')

            # patch requests.get to return a fake response
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"items": [1, 2, 3]}
            mock_resp.raise_for_status.return_value = None

            monkeypatch.setattr('src.shopee_client.requests.get', lambda url, params, headers, timeout: mock_resp)

            res = client.search_popular_items(limit=2)
            assert res.get('items') == [1, 2, 3]


        def test_search_popular_items_rate_limit_retry(monkeypatch):
            client = ShopeeClient(partner_id='p', partner_key='k', base='https://example.com')

            call_count = {'n': 0}

            class FakeResp:
                def __init__(self, status_code, json_data=None):
                    self.status_code = status_code
                    self._json = json_data or {"items": [1]}

                def raise_for_status(self):
                    if self.status_code >= 400:
                        raise requests.HTTPError(response=self)

                def json(self):
                    return self._json

            def fake_get(url, params=None, headers=None, timeout=None):
                call_count['n'] += 1
                # first two calls simulate 429, then success
                if call_count['n'] < 3:
                    resp = FakeResp(429)
                    # Simulate requests.get raising HTTPError on rate-limit
                    raise requests.HTTPError(response=resp)
                return FakeResp(200, {"items": [1]})

            monkeypatch.setattr('src.shopee_client.requests.get', fake_get)

            res = client.search_popular_items(limit=1)
            assert res.get('items') == [1]