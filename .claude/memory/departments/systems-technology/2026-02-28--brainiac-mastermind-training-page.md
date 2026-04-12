# Brainiac Mastermind Training Page — Build Record
**Date**: 2026-02-28
**Page ID**: 1115
**URL**: https://purebrain.ai/training/
**Template**: elementor_canvas
**File**: /home/jared/projects/AI-CIV/aether/exports/brainiac-mastermind-training.html

## What Was Built
Password-gated video training library for PureBrain paying clients.

## Architecture
- Single self-contained HTML file — all CSS + JS inline
- Password gate: sessionStorage-based, hardcoded MVP password "brainiac2026"
- VIDEO_LIBRARY JS array at top of file — add new videos by adding entries there
- HLS adaptive bitrate streaming via hls.js@1.5.7 (CDN pinned version)
- Modal player pattern — cards open full video modal, close returns to grid
- `elementor_canvas` template (full-page, no WP theme chrome)
- `<!-- wp:html -->` wrapper — required to prevent wpautop from breaking CSS/JS

## Video Entry Schema
```js
{
  id: "unique-string",
  title: "Display Title",
  description: "Shown on card and in modal",
  duration: "MM:SS or null",
  posterUrl: "https://...poster.jpg or null",
  hlsUrl: "https://...master.m3u8 or null for coming_soon",
  status: "live" | "coming_soon",
  badge: "new" | null
}
```

## R2 CDN Base
`https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/`

## Current Videos
1. Portal Demo — LIVE — `eaf39ae1_Portal_demo/master.m3u8`
2. PureBrain Complete Demo — COMING SOON (placeholder)

## Security Notes
- Password is client-side (by design for MVP). OAuth/payment gate swap: replace `handleGateSubmit()` logic
- All user-facing data goes through `escHtml()` — 5-character XSS coverage confirmed
- No eval(), no document.write, no localStorage, no non-HTTPS R2 URLs
- hls.js pinned to specific version (not @latest) — supply chain risk minimized

## Deployment Pattern
```bash
# To update the page content:
curl -s -X POST "https://purebrain.ai/wp-json/wp/v2/pages/1115" \
  -u "Aether:${PUREBRAIN_WP_APP_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d '{"content":"<!-- wp:html -->NEW_HTML<!-- /wp:html -->"}'
```

## QA Results
- HTTP 200 confirmed
- 15/15 content markers verified on live page

## Next Steps (Future)
- Tie to payment gateway (swap `handleGateSubmit` for API call)
- Move to app.purebrain.ai as dedicated section
- Add more videos as they are transcoded on R2
- Consider adding category/tag filtering when library grows beyond 6+ videos
