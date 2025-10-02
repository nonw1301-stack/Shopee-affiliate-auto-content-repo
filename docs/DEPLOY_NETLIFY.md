Deploying `docs/` to Netlify (quick) — fixes trailing-slash verification issues

Why: Netlify supports simple `_redirects` rules which let you map requests like `/file.txt/` to `/file.txt` or to a folder. This ensures TikTok's verification requests succeed even if they append a trailing slash.

Quick steps:
1. Create a free Netlify account and log in.
2. From the Netlify dashboard, choose "New site from Git" and connect your GitHub account.
3. Select the `nonw1301-stack/Shopee-affiliate-auto-content-repo` repository.
4. For build settings, choose "Deploy from branch": `main`. Set the publish directory to `docs`.
5. Deploy the site. After deploy you'll get a `https://<your-name>.netlify.app` domain.
6. Use the Netlify URL for verification in TikTok Console. Example:
   `https://<your-name>.netlify.app/tiktok6BhCfHOzgJpfpHRdyUu0KRLFBWqYHWzh.txt`

I added a `_redirects` file under `docs/` to map `.html/` and `.txt/` trailing-slash variants to the expected file/folder. Once Netlify is deployed, TikTok's trailing-slash requests will be handled.
