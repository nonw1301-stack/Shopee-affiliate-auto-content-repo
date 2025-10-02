"""Check and print persisted tokens using token_store.

Usage:
  python scripts/check_tokens.py
"""
import json
from src import token_store

def main():
    try:
        t = token_store.load_tokens()
        print(json.dumps(t, ensure_ascii=False, indent=2))
    except Exception as e:
        print("No tokens found or failed to load:", str(e))

if __name__ == '__main__':
    main()
