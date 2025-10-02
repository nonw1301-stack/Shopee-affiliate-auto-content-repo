"""Smoke test: run the orchestration runner in --run (uses dev token) and assert outputs.

This script is intended to be run locally by a developer. It sets minimal env vars
to use the dev token path and runs the runner, then checks OUTPUT_DIR for created artifacts.
"""
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("TIKTOK_CLIENT_KEY", "dev-key")
os.environ.setdefault("TIKTOK_CLIENT_SECRET", "dev-secret")

print("Running runner in --run (dev token)...")
proc = subprocess.run(["python", "-m", "src.runner", "--run"], cwd=str(ROOT))
if proc.returncode != 0:
    print("Runner exited with non-zero status", proc.returncode)
    raise SystemExit(proc.returncode)

out = Path(os.environ.get("OUTPUT_DIR", ROOT / "output"))
print("Checking output dir:", out)
exists = any(out.rglob("*.png")) or any(out.rglob("*.mp4")) or any(out.rglob("dry_runs/tiktok_api/*.json"))
if not exists:
    print("Smoke test failed: no output artifacts found in OUTPUT_DIR")
    raise SystemExit(2)

print("Smoke test passed — artifacts found in OUTPUT_DIR")
