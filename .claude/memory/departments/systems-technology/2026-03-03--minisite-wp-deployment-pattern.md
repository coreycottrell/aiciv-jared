# Minisite WordPress Deployment Pattern
**Date**: 2026-03-03
**Type**: pattern
**Topic**: Deploying self-contained HTML minisites to purebrain.ai WordPress

## What Was Done
Deployed Mark Christie minisite (`exports/mark-christie-minisite.html`) to purebrain.ai as WordPress page.

## Result
- Live URL: https://purebrain.ai/mark-christie/
- Page ID: 1225
- HTTP 200 confirmed, content verified

## Key Pattern: Self-Contained HTML Minisite Deployment

### Template Rule
- Self-contained HTML pages → `elementor_canvas` template
- Blog posts → default template (empty string "")
- elementor_canvas strips ALL WordPress theme chrome (correct for standalone minisites)

### wp:html Wrap (MANDATORY)
Always wrap full HTML in:
```
<!-- wp:html -->
[full HTML here]
<!-- /wp:html -->
```
Without this, WordPress wpautop filter injects `<p>` tags into `<style>` blocks, destroying CSS.

### urllib + User-Agent (MANDATORY)
Must include User-Agent header or Cloudflare returns 403:
```python
headers = {
    "Authorization": "Basic " + base64.b64encode(b"Aether:APP_PASSWORD").decode(),
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ..."
}
```
Use urllib (NOT requests library) — same User-Agent requirement.

### WordPress Credentials
- Username: Aether (NOT purebrainai)
- App Password: from .env or task instructions
- Endpoint: /wp-json/wp/v2/pages

### noindex for Private Pages
Set via Yoast meta in the page payload:
```python
"meta": {
    "_yoast_wpseo_meta-robots-noindex": "1",
    "_yoast_wpseo_meta-robots-nofollow": "1"
}
```
Note: HTML files already containing `<meta name="robots" content="noindex, nofollow">` are still indexed by WP unless Yoast meta is also set.

### Verification Steps
1. Check HTTP status == 200 on live URL
2. Check for brand/name strings in response body
3. Confirm page_status == "publish" in API response

## Deployment Script
Reference: `/home/jared/projects/AI-CIV/aether/tools/deploy_mark_christie.py`
Reusable pattern for future minisite deployments.

## Gotchas
- Always check for existing page by slug first to avoid duplicates
- elementor_canvas pages return full rendered HTML (~150KB) not just the raw content
- Cloudflare may cache the page — allow a few seconds after deploy before verifying
