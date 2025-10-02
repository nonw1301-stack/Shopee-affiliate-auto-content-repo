# How to rotate TikTok client secret locally and re-authorize

1. In TikTok Developer Console: Reset (rotate) the client secret for your app and copy the new value.

2. Run the PowerShell helper (from repo root):

   .\scripts\rotate_tiktok_secret.ps1 -ClientKey AWD551S8FF0G2R8N -NewSecret '<NEW_SECRET>'

   This updates `.env` in the repo root and removes the local encrypted token store (`.tokens.enc`).

3. Re-run the connect flow to re-authorize and persist tokens:

   .\scripts\connect_tiktok.ps1

4. Verify tokens:

   python -m scripts.check_tokens
