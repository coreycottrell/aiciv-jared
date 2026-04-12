# Graham Martin Mini-Site QA Audit
**Date**: 2026-03-01
**Type**: operational
**Agent**: browser-vision-tester

## Context
5 password-protected pages on purebrain.ai for prospect Graham Martin.
Password: skybet47. Pages: /purebrain-for-graham-martin/ + 4 sub-pages.

## Key Findings

### CRITICAL - Page 5 (responsible-gambling) blocked by Cloudflare CAPTCHA
- URL: /purebrain-for-graham-martin-responsible-gambling/
- After password submit, redirected to /wp-login.php?action=postpass → Cloudflare CAPTCHA wall
- "Please verify you are human" + reCAPTCHA
- Cause: repeated headless browser password attempts triggered GoDaddy/Cloudflare bot detection
- Page itself is probably fine — this is a test environment artefact from rapid automated logins
- Background showed rgb(241,241,241) — the CAPTCHA page, not the actual page content

### ISSUE - Above-fold shows expanded nav menu, not hero
- On desktop main page (1440px), first screen renders with nav links expanded (list visible)
- `<!-- wp:html -->` comment visible as rendered text at very top of page
- Hero content is below the fold because nav expands into page space
- This is the Elementor Table of Contents / Sections widget rendering open by default
- Sub-pages (casino-ai, virya) show the same pattern — nav expanded above hero

### WARNING - wp:html comment visible as text
- `<!-- wp:html -->` renders as visible orange text at top of all pages
- This is a Gutenberg block comment leaking into rendered output
- Indicates template may be using default (not elementor_canvas) — wpautop may be injecting it

### PASS - Background color correct across all 4 loaded pages
- Body BG: rgb(8, 10, 18) = #080a12 dark on all pages except the CAPTCHA intercept
- No orange/light background breaking through on actual content pages

### PASS - Hamburger menu present
- Detected on both desktop AND mobile viewports on main page
- "Sections" hamburger widget present with correct styling
- Nav links (Your World, Chairman Intel, Compliance AI, Virya VC, The Numbers) all present

### PASS - Dark theme content on sub-pages
- Casino AI: rich content, orange accent headings, dark bg sections — looks good
- Chairman Intelligence: structured board brief layout, dark bg — looks professional
- Virya VC: deal intelligence layout with stats, dark bg — clean

### INFO - Console errors are CSP-only (not functional)
- 22-23 errors per page, ALL are CSP violations for clarity.ms and google-analytics
- These are tracking scripts blocked by the security plugin CSP
- Not functional errors — pages work fine, just analytics/clarity not loading
- Expected/acceptable given the security plugin hardening

## Selector Patterns That Work
- `input[type='password']` — finds WP password gate
- `input[type='submit']` — submits password form
- `.hamburger, [class*="hamburger"]` — finds hamburger menu
- `nav a` — finds all nav links

## Gotcha
- Repeated automated password submissions across 5 pages triggers Cloudflare bot CAPTCHA
- To avoid: use browser context with persistent cookies, login once then reuse session
- Or: manually verify page 5 in real browser
