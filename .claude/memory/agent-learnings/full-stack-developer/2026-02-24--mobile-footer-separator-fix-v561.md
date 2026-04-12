# Mobile Footer Separator Fix - Plugin v5.6.1

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: gotcha + operational
**Plugin Version**: 5.6.1

---

## Bug Fixed

### Bug 1: Orphan separator pipe on mobile

**Problem**: When "Why Choose PureBrain?" and "Migrate" pills were hidden on mobile (<600px),
the `|` separator BETWEEN Why and Mission had no named CSS class. So it appeared as a dangling
pipe before "Mission & Values" on mobile: `| Mission & Values`.

**Root cause**: 3 separators in footer HTML — only 2 had named classes:
- `pb-footer-sep-why` (before Why) — had class, was hidden ✓
- `pb-footer-sep` (between Why and Mission) — NO specific class, NOT hidden ✗
- `pb-footer-sep-migrate` (before Migrate) — had class, was hidden ✓

**Fix**: Added `pb-footer-sep-before-mission` class to the middle separator.
Added it to the mobile CSS `display: none !important` block.

### Bug 2: Footer overlap with Privacy/Terms bar

**Fix**: `body { padding-bottom: 80px !important; }` in `@media (max-width: 600px)` block.
Prevents fixed Aether footer from overlapping the legal footer bar.

---

## Key Pattern: Always Name ALL Separators

When you have `A | B | C` with conditional hide/show, EVERY `|` separator needs a named class:
- `sep-before-A` (or `sep-after-A`) — depends on what's being hidden
- Never leave a plain `pb-footer-sep` in between hideable elements
- Mobile CSS must list ALL separator classes in the hide block

---

## Files Changed

- Plugin: `tools/security/purebrain-security/purebrain-security-plugin.php` (v5.5.0 → v5.6.1)
  - Note: v5.6.0 was local-only with incomplete fix; v5.6.1 is the deployed version
- Deploy script: `tools/security/deploy_plugin_v561_purebrain.py`

---

## Deployment

- Deployed via Playwright (CodeMirror editor)
- All 16 validation checks: OK
- Live verification (with cache-bust query string): ALL 5 PAGES PASS
  - homepage, pay-test, pay-test-2, pay-test-sandbox, pay-test-sandbox-2
- Note: CDN cache serves stale HTML on first request without `?cb=timestamp`. Cache-bust
  or wait for CDN TTL to expire for immediate confirmation.

---

## Gotcha: CDN Cache on Homepage

The homepage (purebrain.ai) has aggressive CDN caching. After plugin deploy:
- First fetch without cache-bust: shows old CSS (no `pb-footer-sep-before-mission`)
- Fetch with `?cb=timestamp` query param: shows new CSS immediately
- CDN will propagate on its own within minutes

Pay-test pages don't have the same aggressive caching — they showed new content immediately.
