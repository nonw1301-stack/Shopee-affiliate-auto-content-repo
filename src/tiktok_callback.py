"""FastAPI example for handling TikTok OAuth callback.

Usage: set TIKTOK_CLIENT_ID, TIKTOK_CLIENT_SECRET, and TIKTOK_TOKEN_URL in env,
then run: uvicorn src.tiktok_callback:app --reload
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import os
from .poster_tiktok_api import exchange_code_for_token

app = FastAPI()


@app.get("/tiktok/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    client_id = os.getenv("TIKTOK_CLIENT_ID")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
    redirect_uri = os.getenv("TIKTOK_REDIRECT_URI")

    token = exchange_code_for_token(client_id, client_secret, code, redirect_uri)
    return HTMLResponse(f"<pre>{token}</pre>")
