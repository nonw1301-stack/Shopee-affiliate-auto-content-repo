from fastapi import FastAPI, Request, HTTPException
import os
import logging
from . import poster_tiktok_api
from . import token_store
from .config import Config
import threading
import time
import json

app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/tiktok/callback")
async def tiktok_callback(request: Request):
    params = dict(request.query_params)
    code = params.get("code")
    state = params.get("state")
    if not code:
        raise HTTPException(status_code=400, detail="missing code")

    if not state:
        raise HTTPException(status_code=400, detail="missing state")

    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
    redirect_uri = os.getenv("TIKTOK_REDIRECT_URI")
    if not client_key or not client_secret or not redirect_uri:
        raise HTTPException(status_code=500, detail="TIKTOK client config not set")

    try:
        token_resp = poster_tiktok_api.exchange_code_for_token(client_key, client_secret, code, redirect_uri, state=state)
        # token_resp should be saved by exchange_code_for_token via token_store
        return {"status": "ok", "token": token_resp}
    except Exception as e:
        logger.exception("Failed to exchange code: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tiktok/webhook")
async def tiktok_webhook(request: Request):
    # Accept publish status callbacks from TikTok (provider may send JSON)
    payload = await request.json()
    ts = int(time.time())
    outdir = os.path.join(Config.OUTPUT_DIR, "webhooks")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"publish_{ts}.json")
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("Failed to write webhook payload")
        raise HTTPException(status_code=500, detail="failed to persist webhook")
    return {"status": "ok", "saved": path}


@app.get("/health")
async def health():
    return {"status": "ok"}


def _refresh_loop():
    """Background thread: refresh access token periodically if refresh_token exists."""
    interval = int(os.getenv("TIKTOK_REFRESH_INTERVAL", "3600"))
    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
    while True:
        try:
            tokens = token_store.load_tokens()
            refresh_token = tokens.get("refresh_token")
            if refresh_token and client_key and client_secret:
                try:
                    logger.info("Refreshing TikTok access token using refresh_token")
                    new = poster_tiktok_api.refresh_access_token(client_key, client_secret, refresh_token)
                    # persist new tokens
                    try:
                        token_store.save_tokens(new)
                    except Exception:
                        logger.exception("Failed to persist refreshed tokens")
                except Exception:
                    logger.exception("Failed to refresh token")
        except Exception:
            logger.exception("Token refresh loop error")
        time.sleep(interval)


@app.on_event("startup")
def start_background_tasks():
    # start token refresh thread
    t = threading.Thread(target=_refresh_loop, daemon=True)
    t.start()
