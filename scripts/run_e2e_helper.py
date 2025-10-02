"""Helper to guide an end-to-end run.

This script prints the required env vars and can run the runner in dry-run or run mode.
It will NOT send secrets anywhere; you must supply them via env or .env.
"""
import os
import subprocess
import argparse

REQ = [
    "TIKTOK_CLIENT_KEY",
    "TIKTOK_CLIENT_SECRET",
    # optionally set real endpoints
    # "TIKTOK_INIT_UPLOAD_URL",
    # "TIKTOK_PART_UPLOAD_URL",
    # "TIKTOK_COMMIT_UPLOAD_URL",
]

p = argparse.ArgumentParser()
p.add_argument("--run", action="store_true", help="Run in production mode (will attempt uploads)")
p.add_argument("--etl", action="store_true", help="Run metrics ETL after the run to aggregate metrics into CSV")
args = p.parse_args()

print("Required env vars (missing will be printed):")
for r in REQ:
    print(r, "=", bool(os.getenv(r)))

if not args.run:
    print("Running dry-run: python -m src.runner --dry-run")
    subprocess.run(["python", "-m", "src.runner", "--dry-run"], check=False)
else:
    print("Running real-run (ensure endpoints and secrets are set): python -m src.runner --run")
    subprocess.run(["python", "-m", "src.runner", "--run"], check=False)

if args.etl:
    print("Running metrics ETL...")
    subprocess.run(["python", "-m", "tools.metrics_etl", "--output-dir", os.getenv("OUTPUT_DIR", "./output")], check=False)
