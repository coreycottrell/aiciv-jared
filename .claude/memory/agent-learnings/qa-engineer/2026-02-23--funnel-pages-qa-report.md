# QA Memory: Funnel Pages Verification — 2026-02-23

**Date**: 2026-02-23
**Type**: operational
**Topic**: QA of 4 PureBrain funnel pages (777, 816, 825, 826)

---

## Pages Verified

| Page | URL | Status |
|------|-----|--------|
| 777 | /ai-tool-stack-calculator/ | PASS |
| 816 | /ai-website-analysis/ | PASS |
| 825 | /?page_id=825 (Corey Draft) | FAIL - EMPTY |
| 826 | /ai-website-execution/ | PARTIAL |

## Critical Finding

**Page 825 is completely empty.** Rendered content = 0 chars, raw content = 0 chars.
Page exists as a draft titled "Website Analysis Report — DuckDive | PureBrain.ai" but has no body content.
This breaks the entire funnel: 816 → 825 → 826.

## Verification Method

- `curl -sL "https://purebrain.ai/{slug}/"` for public pages
- WP REST API `GET /wp-json/wp/v2/pages/825` with Aether creds for draft
- Python regex analysis of full HTML responses

## Notes for Future QA

1. **Hero H1 with `<br>` tags** — Exact string match fails for headlines with line breaks.
   Use partial string match or strip tags before comparing. "Let Our AI Team Fix Your Website"
   appears as `Let Our AI Team Fix<br>Your Website` in raw HTML.

2. **Input fields without `<form>` tag** — Page 816 has 3 form inputs (name/email/website)
   with no wrapping `<form>` tag. This is intentional — JS handles submission directly.
   Don't flag as missing form.

3. **PayPal "Loading" placeholder is normal** — Both paypal containers on page 826 show
   "Loading secure checkout..." text. JS renders actual buttons after SDK loads.
   Cannot verify button render without real browser (Playwright needed).

4. **Category cards on page 777 are JS-generated** — Template literals in script.
   They show as `${isRec}` patterns in HTML analysis. This is correct — not broken templating.

5. **Page 825 WP API pattern** — Authenticated fetch:
   `curl -s "https://purebrain.ai/wp-json/wp/v2/pages/825" -u "Aether:{APP_PASS}"`
   Returns `content.rendered` and `content.raw` — both empty for this page.
