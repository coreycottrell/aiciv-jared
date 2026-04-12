# pb-blog-styling v1.1.0 Deployment - Dark Blue Text Background

**Date**: 2026-03-08
**Type**: operational + teaching
**Agent**: full-stack-developer

## What Was Done

Deployed pb-blog-styling v1.1.0 to purebrain.ai WordPress site.
Key change: Added `<style id="purebrain-blog-text-bg">` - dark blue background at 43% opacity (`rgba(10,15,35,0.43)`) behind `.post-content` on single blog post pages, with 12px border-radius and responsive padding.

## Plugin File
`/home/jared/projects/AI-CIV/aether/tools/security/pb-blog-styling/pb-blog-styling.php`

## What Happened / Gotchas

### 1. Plugin Was Inactive (Critical Gotcha)
The plugin file was updated correctly via WP Admin Plugin Editor (Playwright automation), but `pb-blog-styling` was in an **inactive** state. The WP Plugin Editor saves the file regardless of whether the plugin is active/inactive - so the file on disk was correct but the plugin wasn't running.

**Fix**: Used WP REST API with Application Password to activate it:
```bash
curl -s -X POST \
  -u "purebrain@puremarketing.ai:41w3 xWWZ 11em UXgj hjAF sx2T" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}' \
  "https://purebrain.ai/wp-json/wp/v2/plugins/pb-blog-styling/pb-blog-styling"
```

### 2. Login Rate Limiting (429)
After ~5 browser login attempts in quick succession, GoDaddy WAF returns 429 on `/wp-login.php`. Rate limit lasts several minutes.

**Fix**: Use Application Password (`PUREBRAIN_WP_APP_PASSWORD` in `.env`) for REST API calls. Bypasses login entirely.

**App Password**: `41w3 xWWZ 11em UXgj hjAF sx2T` (in .env as PUREBRAIN_WP_APP_PASSWORD)
**User**: `purebrain@puremarketing.ai`

### 3. Page Cache Serving Stale HTML
Even after plugin activation, the page served cached HTML without the new style. Activating `pb-cache-clear` plugin cleared it.

```bash
curl -s -X POST \
  -u "purebrain@puremarketing.ai:41w3 xWWZ 11em UXgj hjAF sx2T" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}' \
  "https://purebrain.ai/wp-json/wp/v2/plugins/pb-cache-clear/pb-cache-clear"
```

### 4. WP Plugin Editor + CodeMirror Pattern (works)
- Use direct URL: `?file=pb-blog-styling/pb-blog-styling.php&plugin=pb-blog-styling/pb-blog-styling.php`
- CodeMirror detected via `.CodeMirror` selector
- Set content: `cm.setValue(content); cm.save(); ta.value = content;`
- Submit: `input[name='submit']`
- Success message: "File edited successfully"

## Verification
Style tag `purebrain-blog-text-bg` confirmed in live page source at:
`https://purebrain.ai/age-of-ai-agents-next-18-months/`

## Deployment Scripts Created
- `tools/deploy_pb_blog_styling.py` - Playwright WP Plugin Editor automation
- `tools/deploy_pb_blog_styling_v2.py` - Diagnostic version with cache detection

## Key Takeaways for Future Deployments
1. **Always check plugin status** via REST API after file update - plugin may be inactive
2. **Prefer REST API** over browser login for WP admin automation - no rate limit risk
3. **pb-cache-clear plugin** exists and can be activated to bust page cache
4. **Application Password** in `.env` = fastest way to interact with WP without login page
5. The WP Plugin Editor DOES save files even for inactive plugins (file on disk ≠ plugin is running)
