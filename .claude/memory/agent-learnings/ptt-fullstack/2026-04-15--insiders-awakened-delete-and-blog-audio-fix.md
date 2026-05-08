# /insiders/awakened/ deletion + Apr 14 blog audio player fix

**Date**: 2026-04-15
**Type**: operational
**Agent**: ptt-fullstack

## What was done

### FIX 1: Deleted /insiders/awakened/
- File: `exports/cf-pages-deploy/insiders/awakened/index.html` (475 lines, ZERO PayPal SDK)
- Backup: `exports/cf-pages-deploy/_archived/insiders-awakened-2026-04-15/index.html`
- Deployment ID (delete): `ce1d39c5-220b-4cf9-875e-71e4d4ed9465`
- Redirect rule added to `_redirects` (lines 5-7):
  ```
  /insiders/awakened/* /insiders/ 301
  /insiders/awakened /insiders/ 301
  ```

### FIX 2: Audio players added to 2 Apr 14 blog posts
- Files:
  - `exports/cf-pages-deploy/blog/why-your-ai-investment-isnt-paying-off/index.html`
  - `exports/cf-pages-deploy/blog/your-next-direct-report-wont-be-human/index.html`
- Backups: `.bak-2026-04-15-audio-fix` suffix each
- Deployment ID: `dcddb419-fceb-432d-8554-ea8558dae693`
- Inserted standard `pb-audio-player` div with `<source src="audio.mp3">`

## Standard audio player markup (from when-ai-starts-writing-prescriptions)

```html
<!-- Blog Audio Player -->
<div class="pb-audio-player" style="margin: 24px auto 32px; max-width: 720px; padding: 16px 20px; background: rgba(42,147,193,0.08); border: 1px solid rgba(42,147,193,0.2); border-radius: 12px; display: flex; align-items: center; gap: 12px;">
    <span style="font-size: 0.9rem; color: rgba(255,255,255,0.7); white-space: nowrap;">&#127911; Listen to this post</span>
    <audio controls preload="none" style="flex: 1; height: 36px; filter: invert(1) hue-rotate(180deg) brightness(0.8);">
        <source src="audio.mp3" type="audio/mpeg">
    </audio>
</div>
```

## Gotcha / Blocker

- **NO mp3 files exist** for the 2 Apr 14 posts — Jared's claim that mp3s exist was inaccurate. HTML players will 404 until audio.mp3 is generated (via voice.purebrain.ai or Chatterbox GPU at 37.27.237.109:8950) and uploaded to each post directory.
- **CF `_redirects` 301 not firing** for `/insiders/awakened/` — CF Pages is instead serving `/insiders/index.html` as fallback (returns 200 with the valid payment page). Functionally correct (user lands on working payment page with PayPal SDK) but not a clean 301. Worth investigating: may need rule placement change or CF Pages SPA-fallback config.

## Verification

- Staging URL (post 1): `grep -c "pb-audio-player"` = 1 ✓
- Staging URL (post 2): `grep -c "pb-audio-player"` = 1 ✓
- `/insiders/awakened/` now serves `/insiders/` payment page content (PayPal SDK present) ✓
- CF Pages deployment manifest confirms awakened/index.html deleted ✓

## Commands that worked

- Pre-deploy: `bash tools/pre-deploy-sync.sh`
- Delete: `python3 tools/cf-deploy.py --delete insiders/awakened/index.html -m "..."`
- Multi-file deploy: `python3 tools/cf-deploy.py _redirects blog/.../index.html blog/.../index.html -m "..."`
- CF cache purge via API: `curl -X POST "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/purge_cache" -H "Authorization: Bearer ${CF_API_TOKEN}"`
