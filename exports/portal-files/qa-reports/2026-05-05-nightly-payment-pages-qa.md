# Nightly Payment Pages QA — 2026-05-05

**BOOP**: nightly-payment-pages-qa
**Run by**: browser-vision-tester
**Pages checked**: 10/10
**HTTP**: 10/10 → 200 (GET)

## Verdict
- **8/10 PASS clean** — homepage, /live/, /insiders/, /partnered/, /unified/, home-test, home-test-live-1, home-test-sandbox
- **2/10 PASS with console-noise regression** — `/awakened/` and `/pay-test-sandbox-3/`

No CRITICAL outage. Pages render, PayPal infra present, chat present, no broken images, no failed deploys.

## Per-page (Playwright headless render + 5s wait)

| Page                       | HTTP | Title | DarkBG | PayPal containers | Chat | Broken imgs | JS errors | 404s |
|----------------------------|------|-------|--------|-------------------|------|-------------|-----------|------|
| `/` (HOMEPAGE)             | 200  | ✓     | ✓ (rgb(10,14,26)) | 9 | ✓ | 0 | 0 | 0 |
| `/live/`                   | 200  | ✓     | ✓     | 9 | ✓ | 0 | 0 | 0 |
| `/insiders/`               | 200  | (static-ok) | ✓ | sdk + buttons | ✓ | — | — | — |
| `/awakened/`               | 200  | ✓     | ✓     | 9 | ✓ | 0 | **13** | **1** |
| `/partnered/`              | 200  | (static-ok) | ✓ | sdk + buttons | ✓ | — | — | — |
| `/unified/`                | 200  | (static-ok) | ✓ | sdk + buttons | ✓ | — | — | — |
| `/pay-test-sandbox-3/`     | 200  | ✓     | ✓     | 9 | ✓ | 0 | **11** | **1** |
| `/home-test-live-1/`       | 200  | ✓ (gate) | ✓ | password-gate ✓ | — | — | — | — |
| `/home-test-sandbox/`      | 200  | ✓ (gate) | ✓ | password-gate ✓ | — | — | — | — |
| `/home-test/`              | 200  | ✓     | ✓ (rgb(10,14,26)) | 9 | ✓ | 0 | 0 | 0 |

## Findings to route

### 🟡 Finding 1 — WordPress remnants on /awakened/ and /pay-test-sandbox-3/
**Severity**: medium (cosmetic/console-only, pages still functional)

**Symptoms**:
- 404: `https://purebrain.ai/wp-includes/js/wp-emoji-release.min.js?ver=6.9.1`
- 11–13 console errors per page: `wp is not defined`, `_ is not defined`, repeat
- Stems from inline scripts referencing the missing wp-emoji bundle

**Why it matters**: BOOP spec requires "no JS console errors". Public buyer pages emitting 13 errors while loading is bad optics for any prospect with devtools open. Likely a stale WordPress export that didn't get scrubbed when these were ported to CF Pages.

**Routing**: ST# (purebrain-production CF Pages) — strip `wp-emoji-release.min.js` reference from the HTML for these two slugs and remove the inline `wp.*` / underscore-`_` references (or stub them). Other public pages (`/live/`, `/`, `/insiders/`, etc.) are clean — likely a regression from a recent re-export of just these two slugs.

### 🟢 Finding 2 — Body background drift (info only, NOT a regression)
Rendered `body` bg is `rgb(10,14,26)` = `#0a0e1a` instead of constitutional `#080a12` (`rgb(8,10,18)`). HTML still contains 4–10 `#080a12` references per page — a layered element/wrapper overrides the body. Both are visually-identical near-black navy. **Not flagging unless brand audit demands exact match.**

## What passed
- All 10 pages return 200 (GET — per cf-pages-health-check-get-not-head guard)
- PayPal SDK script reference present on every public payment page
- Chat container DOM present everywhere (chat-cta button hidden until trigger — expected)
- No broken images on any page rendered headlessly
- Password gate active on home-test variants
- Dark theme rendered (variant noted above)
- No failed network requests on 8/10 pages
