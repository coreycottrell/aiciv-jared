# Plugin v5.7.0 - Homepage Banner Removal

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: operational
**Plugin Version**: v5.6.1 → v5.7.0

---

## Change Made

Removed the "See Why PureBrain Is Different" homepage banner from the purebrain-security plugin.

**What was removed**: A fixed-position bar injected via `wp_footer` at priority 99, only on the homepage. It had the CSS class `pb-why-purebrain-bar`.

**Why removed**: Was causing mobile overlap with the Aether footer credit bar. The Mission section now serves the same purpose, making the banner redundant.

**Also removed**: The duplicate `body { padding-bottom: 76px }` that conflicted with the footer bar's own 64px/80px(mobile) padding rules.

---

## Validation Checks (14/14 OK)

Key checks:
- `pb-why-purebrain-bar` ABSENT from plugin PHP ✓
- `pb-aether-footer` still present ✓
- All other features intact (FAQ, transparency, IndexNow, footer pills, etc.) ✓

---

## Deployment

- Method: Playwright via WP Plugin Editor (CodeMirror)
- Login: GoDaddy SSO overlay handled
- Save result: "File edited successfully"
- Elementor cache clear: HTTP 403 (known - permissions limited, non-blocking)

---

## Live Verification

- Fetched `https://purebrain.ai/?cb={timestamp}` (cache-busted)
- `pb-why-purebrain-bar` NOT in homepage HTML ✓
- `pb-aether-footer` still present ✓
- `pb-footer-mission` still present ✓

---

## Files

- Plugin: `tools/security/purebrain-security/purebrain-security-plugin.php` (v5.6.1 → v5.7.0)
- Deploy script: `tools/security/deploy_plugin_v570_purebrain.py`

---

## Pattern Notes

- Elementor cache clear returning 403 is normal/non-blocking on purebrain.ai
- CDN cache-bust with `?cb=timestamp` query param confirms new plugin instantly
- Homepage HTML does not embed version number — verify by checking for/against specific CSS class names
