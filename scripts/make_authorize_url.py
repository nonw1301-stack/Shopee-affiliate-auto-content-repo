"""CLI helper to print the TikTok authorize URL using env vars or arguments.

Usage:
    python scripts/make_authorize_url.py
    TIKTOK_CLIENT_KEY and TIKTOK_REDIRECT_URI can be supplied via env or args.
"""
import os
import argparse
from src.poster_tiktok_api import get_authorize_url
from src.pkce import generate_code_verifier, code_challenge_from_verifier
import json
import uuid

p = argparse.ArgumentParser()
p.add_argument("--client-key", help="TikTok client key")
p.add_argument("--redirect-uri", help="Redirect URI")
args = p.parse_args()

client_key = args.client_key or os.getenv("TIKTOK_CLIENT_KEY")
redirect = args.redirect_uri or os.getenv("TIKTOK_REDIRECT_URI")
if not client_key or not redirect:
    print("Provide --client-key and --redirect-uri or set TIKTOK_CLIENT_KEY / TIKTOK_REDIRECT_URI in env")
    raise SystemExit(2)

# PKCE: generate code_verifier and code_challenge, persist code_verifier by state
state = str(uuid.uuid4())
code_verifier = generate_code_verifier(64)
code_challenge = code_challenge_from_verifier(code_verifier)

# persist mapping to OUTPUT_DIR so callback can find code_verifier
outdir = os.getenv("OUTPUT_DIR") or os.path.join(os.getcwd(), "output")
os.makedirs(outdir, exist_ok=True)
path = os.path.join(outdir, f"pkce_state_{state}.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump({"state": state, "code_verifier": code_verifier}, fh)

url = get_authorize_url(client_key, redirect, state=state) + f"&code_challenge={code_challenge}&code_challenge_method=S256"
print(url)
print("Saved PKCE verifier to", path)
