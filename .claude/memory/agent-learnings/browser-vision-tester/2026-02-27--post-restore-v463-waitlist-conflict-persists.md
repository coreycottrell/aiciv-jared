# Memory: Post-GoDaddy Restore Audit — v4.6.3 Waitlist Conflict Still Present

**Date**: 2026-02-27
**Type**: teaching + operational
**Topic**: GoDaddy restore to Feb 26 10pm EST — same openWaitlistModal JS collision bug persists in page HTML

---

## Finding

After GoDaddy restore to v4.6.3 (Feb 26 10pm EST state), both pay-test-2 (689) and pay-test-sandbox-2 (688) still have the JS function collision bug. The restore did NOT fix it because the bug was in the WordPress PAGE CONTENT (not the plugin), and the restore returned the pages to the same broken state.

---

## Bug Structure (v4.6.3 restored state)

Page 689 has 26 inline scripts, including 4 `openWaitlistModal` definitions:

1. PayPal Integration Script (30,448 chars) — defines `openWaitlistModal` as PayPal checkout
2. Integration Glue Script (3,876 chars) — wires PayPal to chatbox
3. PayPal Alias Fix Script (809 chars) — sets `openPayPalModal = openWaitlistModal`
4. OLD Waitlist Modal (at char 277,349) — redefines `openWaitlistModal` as waitlist form

**Last JS definition wins → definition #4 (waitlist form) overrides definition #1 (PayPal)**

---

## Pricing Button State

Most tier buttons call `openWaitlistModal(tier)` — gets the waitlist form. Only Unified tier uses `openPayPalModal(tier)` which might work via alias (if alias fired before overwrite).

---

## What's Correct

- Production PayPal client ID: `AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI`
- Sandbox banner present on page 688 only (correct separation)
- Chatbox elements all present in content (chatMessages, userInput, awakening section, birth call)
- PayPal SDK dynamically injected via `document.createElement('script')` — no static script tag
- Both pages: last modified Feb 26 16:31-32 UTC (10pm EST ≈ Feb 26 22:00 EST → 03:00 UTC Feb 27)

Wait — these timestamps (16:31-32 UTC = 11:31am EST, not 10pm EST). The restore point was "10pm EST" but the page content modification timestamp suggests these pages were last touched at 11:31am EST Feb 26. The plugin version may differ from what's in page content.

---

## Browser Access Issue

Our server IP (89.167.19.20) hit GoDaddy WAF rate limit again. Multiple postpass form submissions from automated testing triggered reCAPTCHA CAPTCHA challenge. Headless browser got CAPTCHA page, not actual page content. Used WP REST API as fallback.

**WAF recovery time**: 15-20 min minimum.

---

## Fix Required

Remove `#waitlistModal` div and the old `openWaitlistModal` function from the WordPress page HTML (both pages 689 and 688). The PayPal integration script will then be the sole definition and will win.

---

## Tags

pay-test-2, pay-test-sandbox-2, page-689, page-688, waitlist-conflict, openWaitlistModal, paypal, restore, v4.6.3, godaddy, waf, wp-rest-api
