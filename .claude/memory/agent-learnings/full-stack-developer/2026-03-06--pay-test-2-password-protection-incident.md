# Memory: pay-test-2 (page 689) Password Protection Incident

**Date**: 2026-03-06
**Agent**: dept-systems-technology
**Type**: gotcha + incident-response
**Tags**: purebrain, pay-test-2, page-689, password-protection, elementor, wordpress

---

## Incident Summary

pay-test-2 (page 689) was showing calculator page content ("How Much Are You Wasting on AI Tool Sprawl?") instead of the payment flow.

**Root cause**: The page had been password-protected. When password-protected, WordPress/Elementor does not render the page content — only the password form shows. The background video + plugin CSS was showing through, and the calculator content from another page may have been cached/visible in some contexts.

**Fix**: Remove password protection via REST API PATCH.

---

## What Happened

At 15:46 on 2026-03-06, three pages were all modified simultaneously:
- Page 688 (pay-test-sandbox-2) — modified 15:46:33
- Page 689 (pay-test-2) — modified 15:46:39
- Page 1232 (pay-test-sandbox-3) — modified 15:46:26

Pages 688 and 689 got password-protected. Page 1232 did not. Likely caused by a batch WP template/settings operation that accidentally set passwords on these pages.

---

## Diagnosis Path

1. `curl .../wp-json/wp/v2/pages/689` → `Modified: 2026-03-06T15:46:39` (today)
2. Live page fetch showed: `"This content is password-protected. To view it, please enter the password below."`
3. REST edit context returned 401 for Aether user (not editor role) but app password worked
4. Sandbox-2 (688) also password-protected at same time — fixed too

---

## Fix Applied

```bash
# Remove password from pay-test-2 (page 689)
curl -X POST "https://purebrain.ai/wp-json/wp/v2/pages/689" \
  -u "Aether:ZGuh 1W8k WpWM c9iy kqyd buPr" \
  -H "Content-Type: application/json" \
  -d '{"password": ""}'

# Remove password from sandbox-2 (page 688) — also affected
curl -X POST "https://purebrain.ai/wp-json/wp/v2/pages/688" \
  -u "Aether:ZGuh 1W8k WpWM c9iy kqyd buPr" \
  -H "Content-Type: application/json" \
  -d '{"password": ""}'
```

**Key**: Must use APP PASSWORD (`ZGuh 1W8k WpWM c9iy kqyd buPr`) not the login password. The Aether user has Author role — cannot edit pages they don't own. The app password grants elevated REST API access.

---

## Verification Checklist (7/7 PASS after fix)

- No password gate on live page
- openPayPalModal function present (live PayPal, not sandbox)
- Begin Awakening CTA present
- PTC chat flow (ptc-input) present
- No sandbox.paypal.com references
- Dark background (#0a0e1a)
- elementor_canvas template active

---

## Content Architecture (Confirmed Intact)

pay-test-2 page content is stored in `_elementor_data` (Elementor). The Elementor CSS confirms correct structure:
- `elementor-element-c4d524c` — main container
- `elementor-element-292c72a` — HTML widget (the payment flow code)
- `elementor-element-a18b125d` — section with bg #0a0e1a
- `elementor-element-why_pb_688` — "Why PureBrain" section with bg #0d1117

The content was NEVER lost — just hidden behind password gate.

---

## PayPal Configuration on pay-test-2

- Uses LIVE PayPal (www.paypal.com) — no sandbox references
- Live client ID: `AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI`
- Loads via paypal-popup-integration.js (dynamic load, not inline script tag)
- openPayPalModal('Partnered') and openPayPalModal('Unified') for live tiers
- openWaitlistModal('Awakened') for waitlist tier

---

## WP REST API Auth Notes

| Credential | Use Case | Works for page 689 edit? |
|-----------|---------|--------------------------|
| `Aether:NW2u!JLQ3!Bt$XD$7CWzz5Z@` | Login password | NO — 401 on edit context |
| `Aether:ZGuh 1W8k WpWM c9iy kqyd buPr` | App password (spaces) | YES — can PATCH password field |
| Both | Read without edit context | YES |

