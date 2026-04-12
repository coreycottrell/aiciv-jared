# Blog Video Background Fix - Plugin v4.8.5

**Date**: 2026-03-05
**Type**: bug-fix, deployment
**Agent**: dept-systems-technology

---

## Problem

Blog listing page (`/blog/`) and all individual blog posts: background video rendering behind dark background overlay, making it invisible. Video has `z-index:-1 position:fixed`. Opaque `body { background: #080a12 }` covered it.

## Root Cause

SITE-WIDE dark bg enforcement (3 layers) set `body` to `#080a12 !important` on all pages. The existing transparent-body exception list only covered: `body.home`, `body.page-id-11`, `body.page-id-688`, `body.page-id-689`, `body.page-id-987`, `body.page-id-1232`.

## Fix Applied (v4.8.5)

Added to all three layers:

**CSS Layer 1 (wp_head priority 1)**: Added `body.page-id-319`, `body.blog`, `body.single-post`, `body.archive` to transparent exception.

**CSS Layer 2 (wp_head priority 999)**: Same additions.

**Layer 3 JS (wp_head)**: Added `is_page(319)` to the PHP server-side skip condition alongside existing `is_singular('post')`.

## Critical Discovery

`/blog/` is NOT `body.blog` in WordPress terms — it's **page-id-319**, an Elementor canvas page. The `is_home()` PHP function does NOT return true for it because it's a static Elementor page, not WordPress's built-in posts page setting. Must use `is_page(319)` explicitly.

## Deployment Pattern

- Credentials: `PUREBRAIN_WP_USER=Aether`, `PUREBRAIN_WP_PASSWORD` (regular password, NOT app password)
- App password (`PUREBRAIN_WP_APP_PASSWORD`) works for REST API only, NOT WP admin login
- Deploy script: `tools/security/deploy_plugin_v485_purebrain.py`
- Plugin path on server: `purebrain-security/purebrain-security-plugin.php`
- Local file: `exports/purebrain-security-plugin-v485.php`
- Use JS injection `document.getElementById('newcontent').value = content` NOT `page.fill()` for large files (248K chars — fill times out)
- `page.goto(..., wait_until="networkidle", timeout=60000)` needed (not 30000)

## Verification Pattern

- Check `pb-dark-bg-js` ABSENT in page source = JS enforcer skipped = body transparent
- Check CSS layers contain `body.page-id-319` in transparent exception block
- Blog listing may be Cloudflare-cached — add `?nc=1` or similar cache-bypass param to verify fresh

## File Paths

- `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v485.php`
- `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v485_purebrain.py`
- `/home/jared/projects/AI-CIV/aether/exports/screenshots/plugin_v485_purebrain_deploy.png`

## Verification Result (2026-03-05)

7/7 pages PASS:
- Blog listing (page-id-319): PASS
- Single blog post (single-post): PASS
- Single blog post 2: PASS
- Homepage: PASS (pre-existing)
- Pay-test 688: PASS (pre-existing)
- Pay-test 987: PASS (pre-existing)
- Page 1232: PASS (pre-existing)
