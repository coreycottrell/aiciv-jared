# Memory: Migration Portal V2 WordPress Deployment

**Date**: 2026-02-24
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Deploy migration-portal-v2-updated.html to purebrain.ai/migrate/ (page ID 800)

---

## What Was Done

Deployed `/home/jared/projects/AI-CIV/aether/exports/migration-portal-v2-updated.html` to:
- **URL**: https://purebrain.ai/migrate/
- **WordPress page ID**: 800
- **Slug**: migrate
- **Template**: elementor_canvas
- **Status**: publish

## Anti-Orange Override Added Before Deploy

Injected `body.tt-magic-cursor` override directly into the HTML file (line 26, after `body.page` rule):
```css
body.tt-magic-cursor { background: #080a12 !important; color: #e0e6f0 !important; border-color: transparent !important; }
```
This is required for all purebrain.ai pages using the tt-magic-cursor theme to prevent orange bleed.

## Deploy Method

Used Python `requests` library (not curl) to POST JSON payload to WP REST API:
```
POST https://purebrain.ai/wp-json/wp/v2/pages/800
Auth: Basic (Aether / PUREBRAIN_WP_APP_PASSWORD)
Payload: { content, status: "publish", template: "elementor_canvas" }
```

Using Python requests avoids `!important` corruption that curl --data-urlencode can cause with complex HTML content at this scale (97,230 chars).

## Finding Existing Page

Search by exact slug:
```
GET /wp-json/wp/v2/pages?slug=migrate
```
Returned page ID 800 on first try. The `?search=migrate` query did NOT return it - always use `?slug=` for exact matches.

## Verification

- HTTP 200 on deploy
- `curl https://purebrain.ai/migrate/` returns 200
- "Migration Portal" and "Bring Your AI History" in live HTML
- `tt-magic-cursor` override present 23 times in live page (theme applies it to multiple selectors)

## File State

Post-deploy file: `/home/jared/projects/AI-CIV/aether/exports/migration-portal-v2-updated.html`
- 2027 lines, 97,230 chars
- Properly wrapped in `<!-- wp:html -->` ... `<!-- /wp:html -->`
- Contains tt-magic-cursor override at line 26
