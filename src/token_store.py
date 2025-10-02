"""Encrypted token store using Fernet symmetric encryption.

This small utility uses a FERNET_KEY env var (URL-safe base64) to encrypt and
decrypt a JSON blob stored on disk. It's minimal and suitable for local use.
"""
import os
import json
from typing import Optional

try:
    from cryptography.fernet import Fernet
except Exception:
    Fernet = None

try:
    import keyring
except Exception:
    keyring = None


STORE_PATH = os.getenv("TOKEN_STORE_PATH", ".tokens.enc")
KEYRING_SERVICE = os.getenv("TOKEN_KEYRING_SERVICE", "shopee_affiliate_auto_content")


def _get_fernet():
    key = os.getenv("FERNET_KEY")
    if not key:
        raise RuntimeError("FERNET_KEY not set in env. Set it to use encrypted token store.")
    if Fernet is None:
        raise RuntimeError("cryptography package not available. Install cryptography to use token encryption.")
    return Fernet(key.encode())


def _use_keyring() -> bool:
    return os.getenv("USE_OS_KEYRING", "false").lower() in ("1", "true", "yes") and keyring is not None


def save_tokens(data: dict, path: Optional[str] = None):
    if _use_keyring():
        # store JSON blob in OS keyring (string)
        raw = json.dumps(data)
        keyring.set_password(KEYRING_SERVICE, "tokens", raw)
        return

    path = path or STORE_PATH
    f = _get_fernet()
    payload = json.dumps(data).encode("utf-8")
    token = f.encrypt(payload)
    with open(path, "wb") as fh:
        fh.write(token)


def load_tokens(path: Optional[str] = None) -> dict:
    if _use_keyring():
        if keyring is None:
            return {}
        raw = keyring.get_password(KEYRING_SERVICE, "tokens")
        if not raw:
            return {}
        return json.loads(raw)

    path = path or STORE_PATH
    if not os.path.exists(path):
        return {}
    f = _get_fernet()
    with open(path, "rb") as fh:
        blob = fh.read()
    data = f.decrypt(blob)
    return json.loads(data.decode("utf-8"))
