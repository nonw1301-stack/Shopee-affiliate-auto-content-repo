"""Utilities for PKCE (code_verifier / code_challenge)"""
import os
import hashlib
import secrets


def generate_code_verifier(length: int = 64) -> str:
    # allowed chars: ALPHA / DIGIT / '-' / '.' / '_' / '~'
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~'
    return ''.join(secrets.choice(alphabet) for _ in range(max(43, min(128, length))))


def code_challenge_from_verifier(verifier: str) -> str:
    # hex-encoded SHA256
    h = hashlib.sha256(verifier.encode('utf-8')).hexdigest()
    return h
