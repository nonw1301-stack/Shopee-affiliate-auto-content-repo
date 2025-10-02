
# How to host Terms & Privacy pages on GitHub Pages

1. Create a branch (optional) and commit the `docs/` folder (already included in repo). The `docs/` folder will be served by GitHub Pages if enabled for this repo.

2. Push to GitHub:

   git add docs/; git commit -m "Add minimal Terms/Privacy for TikTok verification"; git push origin main

3. Enable GitHub Pages:

   - Go to the repository on GitHub → Settings → Pages
   - Under 'Source' choose the `main` branch and `/docs` folder
   - Save. GitHub will publish the pages at the GitHub Pages URL for your repo.

4. Example URLs once published (replace with your repo owner/name):

   - Terms: `https://<owner>.github.io/<repo>/terms.html`
   - Privacy: `https://<owner>.github.io/<repo>/privacy.html`

5. After publishing, in the TikTok Developer Console add those URLs for Terms and Privacy and press "Verify" (or follow the verification instruction they show).

Notes:

- Replace the placeholder text with your real legal text before going public.
- If TikTok requires a specific verification token or meta tag, they will show that during verification; place the token in `docs/tiktok_verification.txt` or add a meta tag into `docs/terms.html` as instructed.
