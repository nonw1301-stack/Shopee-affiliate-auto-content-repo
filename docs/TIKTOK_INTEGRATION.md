TikTok Content Posting - Integration & Smoke Test Guide

This guide explains how to configure and run a local smoke-test for the TikTok
chunked uploader implemented in `src/poster_tiktok_api.py`.

Prerequisites
- Python 3.11+ environment
- `pip install -r requirements.txt` (includes `requests`, `cryptography`, etc.)
- A registered TikTok developer app with Content Posting access (client_key, client_secret)
- A `FERNET_KEY` for encrypting tokens when using the token store

Environment variables
Set these in your environment or in a local `.env` file (see `.env.example`):

- TIKTOK_AUTH_URL (optional)
- TIKTOK_TOKEN_URL
- TIKTOK_INIT_UPLOAD_URL
- TIKTOK_PART_UPLOAD_URL (optional if init returns per-part URLs)
- TIKTOK_COMMIT_UPLOAD_URL
- TIKTOK_REFRESH_URL
- TIKTOK_UPLOAD_URL (simple single-step upload, optional)
- FERNET_KEY (generate using the command below)
- TOKEN_STORE_PATH (optional path for encrypted token file)
- TIKTOK_UPLOAD_WORKERS (optional, defaults to 4)

Generating a FERNET_KEY (PowerShell)

Run in PowerShell:

```powershell
python - <<'PY'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
PY
```

Copy the output and set `FERNET_KEY` to that value.

Quick smoke-test (dry-run)

This project includes a guarded smoke-run script `scripts/smoke_tiktok.py` that
by default runs in dry-run mode and will not call live endpoints. To perform a
real upload you must set the required TikTok endpoints and supply valid
credentials.

PowerShell smoke-run commands (example)

```powershell
# Activate your venv and install deps
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Set env vars (example). Replace placeholders with real values.
$env:FERNET_KEY = "<your-fernet-key>"
$env:TIKTOK_INIT_UPLOAD_URL = "https://api.tiktok.com/video/upload/init"
$env:TIKTOK_COMMIT_UPLOAD_URL = "https://api.tiktok.com/video/upload/commit"
$env:TIKTOK_PART_UPLOAD_URL = "https://api.tiktok.com/video/upload/part"
$env:TIKTOK_TOKEN_URL = "https://api.tiktok.com/oauth/token"

# Run the smoke-runner in dry-run mode (safe)
python .\scripts\smoke_tiktok.py --dry-run

# To run a real upload (only if you configured endpoints and have credentials):
python .\scripts\smoke_tiktok.py --run-real --video sample.mp4 --title "Test Upload"
```

Checklist before running real upload
- [ ] You have a valid developer app and access to Content Posting API
- [ ] All TIKTOK_* endpoint env vars are set correctly
- [ ] `FERNET_KEY` is set and secure
- [ ] You have a test video file (under 200MB recommended for smoke-test)
- [ ] Review `scripts/smoke_tiktok.py` to confirm behavior

Notes
- This implementation uses per-chunk MD5 headers (`X-Chunk-MD5`) and will
  validate the server's ack md5 (response field `md5` / `server_md5` / `checksum`) if
  present. If your provider uses a different header or field name, update
  `src/poster_tiktok_api.py` accordingly.

- If TikTok's official doc specifies different field names, provide the link
  and we will adapt the uploader to match exactly.
