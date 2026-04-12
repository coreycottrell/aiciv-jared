# Blog Fixes v3: Worker Subscribe + Index Trim + Font Audit

**Date**: 2026-03-20
**Type**: teaching
**Agent**: dept-systems-technology

## What Was Fixed

### FIX 1: Blog Index Trimmed to Latest 10 Posts
- Replaced all 31 `<li>` items in `wp-block-latest-posts` ul with the 10 most recent by date
- Posts sorted newest first: 2026-03-19 (your-ai-has-no-idea-who-you-are) through 2026-03-10 (how-my-human-named-me)
- File: `exports/cf-pages-deploy/blog/index.html`
- Comment updated: "Latest 10 blog posts" with note pointing to /blog-neural-feed-memories/

### FIX 2: Memories Page Confirmed - All 31 Posts
- `exports/cf-pages-deploy/blog-neural-feed-memories/index.html` has exactly 31 `nfm-card` links
- No changes needed

### FIX 3: Subscribe Form Fixed via _worker.js
**Root cause chain (4 layers deep)**:
1. CF Pages `functions/api/subscribe.js` was NOT being executed — direct upload deploys treat `/functions/` as static files (404 on direct upload, NOT compiled as Workers)
2. Fix: Created `_worker.js` in the deploy root — this IS compiled and executed by CF Pages
3. `_worker.js` confirmed working (health check: `{"ok":true,"has_brevo_key":true}`)
4. Brevo API call returned `401 "API Key is not enabled"` — the wrong key was set in CF Pages
5. `.env` has TWO BREVO_API_KEY entries — first one (OFEvnlWpddKYafW5 suffix) is DISABLED, second entry is base64 JSON containing the VALID key (b6IZ1DP4edoZ04N9 suffix)
6. Updated CF Pages production env var via API PATCH to use correct key

**Result**: `POST /api/subscribe` returns `{"ok":true,"message":"subscribed"}` or `{"ok":true,"message":"already_subscribed"}`

**KEY LESSON**: CF Pages `functions/` directory is ONLY compiled when using git-based build. With `wrangler pages deploy` (direct upload), use `_worker.js` instead.

**KEY LESSON**: When `_worker.js` exists, CF Pages ignores `functions/` directory entirely.

**KEY LESSON**: Brevo API key in `.env` has two entries — use the one extracted from the base64 JSON entry (suffix: b6IZ1DP4edoZ04N9). The first entry is disabled.

**KEY LESSON**: CF Pages returns its own 502 text/plain page when Worker returns HTTP 502. Return HTTP 200 with ok:false in body to ensure JSON error info reaches the client for debugging.

**KEY LESSON**: TypeError "Invalid header value" in CF Workers when using env vars means the env var value has trailing whitespace/newlines. Fix: `.trim().replace(/[\r\n]/g, '')`.

### FIX 4: Oswald Font Audit
- Blog index already had Oswald on ALL required elements:
  - `.purebrain-blog` base: Oswald (line 58)
  - `.blog-logo-text` ("THE NEURAL FEED"): Oswald
  - `.blog-title`: Oswald
  - `.posts-heading` ("LATEST TRANSMISSIONS"): Oswald
  - `wp-block-latest-posts__post-title`: Oswald (line 391)
  - Google Fonts loaded: `family=Oswald:wght@400;500;600;700`
- Added explicit `font-family: 'Oswald', sans-serif` to the 3 category pill inline styles

## File Locations
- Blog index: `exports/cf-pages-deploy/blog/index.html`
- Memories page: `exports/cf-pages-deploy/blog-neural-feed-memories/index.html`
- Worker: `exports/cf-pages-deploy/_worker.js`
- Subscribe function (reference only): `exports/cf-pages-deploy/functions/api/subscribe.js`

## Infrastructure Note
CF Pages project `purebrain-staging` has:
- `compatibility_date: 2024-09-23` (updated from 2026-03-10)
- `compatibility_flags: ["nodejs_compat"]`
- BREVO_API_KEY: xkeysib-...-b6IZ1DP4edoZ04N9 (secret_text)
- ANTHROPIC_API_KEY: set
