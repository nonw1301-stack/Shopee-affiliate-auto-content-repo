import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch

# Ensure test imports the project
from src import generator


@patch("src.generator.ShopeeClient")
@patch("src.generator.OpenAIClient")
def test_run_once_creates_output(mock_openai_cls, mock_shopee_cls, tmp_path):
    # Setup mocks
    shopee = mock_shopee_cls.return_value
    openai_client = mock_openai_cls.return_value

    # Mock items response
    shopee.search_popular_items.return_value = {
        "items": [
            {"itemid": "1001", "shopid": "2001", "name": "Test Item", "price": 150000}
        ]
    }
    shopee.generate_affiliate_link.return_value = {"affiliate_link": "https://aff.link/1001"}
    openai_client.generate_caption.return_value = "Caption for Test Item\n#tag1 #tag2 #tag3"

    # Use a temp output dir and DB
    temp_out = tmp_path / "out"
    temp_out.mkdir()
    generator.Config.OUTPUT_DIR = str(temp_out)
    # Use an in-memory DB by patching DB path
    with patch("src.generator.DB") as MockDB:
        db_inst = MockDB.return_value
        db_inst.is_posted.return_value = False
        db_inst.mark_posted.return_value = True

        res = generator.run_once()

    # Assert output file created
    files = list(temp_out.iterdir())
    assert any(f.suffix == ".txt" for f in files)
    assert len(res) == 1
