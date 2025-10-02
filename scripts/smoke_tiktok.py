"""Smoke test runner for TikTok integration.

This script will run a dry-run by default. To run real integration, set the
required env vars and run with --run-real. Use with caution (will attempt to
upload using the configured endpoints).

Do NOT place credentials in source or chat. Provide them in your local .env or
CI secrets.
"""
import argparse
import os
from src.poster_tiktok_api import post_video, obtain_access_token


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--title", default="Smoke test")
    p.add_argument("--run-real", action="store_true")
    args = p.parse_args()

    dry_run = not args.run_real

    token = None
    if os.getenv("TIKTOK_CLIENT_ID") and os.getenv("TIKTOK_CLIENT_SECRET"):
        token = obtain_access_token(os.getenv("TIKTOK_CLIENT_ID"), os.getenv("TIKTOK_CLIENT_SECRET"))

    res = post_video(args.title, args.video, access_token=token, dry_run=dry_run)
    print(res)


if __name__ == "__main__":
    main()
