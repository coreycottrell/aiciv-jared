# Awakened Page Creation + Levels Link Injection v1.1

**Date**: 2026-03-05
**Type**: operational
**Topic**: PureBrain Awakened tier page + injection script update for proCta/Awakened button

---

## What Was Done

### Task 1: Created `/awakened-how-this-levels-you-up/` page
- **WordPress page ID**: 1315
- **URL**: https://purebrain.ai/awakened-how-this-levels-you-up/
- **Template**: elementor_canvas
- **Source file**: `/home/jared/projects/AI-CIV/aether/exports/awakened-how-this-levels-you-up.html`
- Adapted from `/home/jared/projects/AI-CIV/aether/exports/partnered-how-this-levels-you-up.html`

Key adaptations from Partnered → Awakened:
- All "Partnered" → "Awakened"
- Price: $499/mo → $999/mo
- Feature list replaced with Awakened tier features (unlimited agents, 50+, permanent home, wisdom inheritance, comms hub, managed maintenance, proactive health checks, priority skills sync, 24h support, Telegram+Bluesky setup, community support, basic docs)
- **NO PAYMENT TODAY** callout (waitlist, not direct purchase)
- CTA button links to `https://purebrain.ai/#pricing` (back to main pricing, not a payment form)
- Primary accent color: orange (`--orange: #f1420b`) — Awakened uses orange highlight vs Partnered's blue
- Card icons use `--orange-dim` background + orange border
- Feature dots use `--orange` color
- Section labels in orange
- Value table highlights in orange-dim

### Tasks 2 & 3: Updated Link Injection Script v1.0 → v1.1

**Pages updated**:
- Page 689 (pay-test-2): https://purebrain.ai/pay-test-2/
- Page 1232 (pay-test-sandbox-3): https://purebrain.ai/pay-test-sandbox-3/

**The injection script lives in `_elementor_data` meta** — inside the main HTML widget as a `<script>` block appended AFTER `</html>`. It is NOT in `post_content` (which is empty on Elementor canvas pages).

**How the update worked**:
1. Fetch `_elementor_data` via `GET /wp-json/wp/v2/pages/{id}?context=edit`
2. The field value is a **string containing JSON** (double-encoded)
3. `json.loads(ed_str)` → list of Elementor elements
4. Walk elements to find `elType=widget, widgetType=html` containing the target script
5. Replace OLD script with NEW script in the `settings.html` field
6. `json.dumps(ed_data)` → back to string
7. POST to `wp-json/wp/v2/pages/{id}` with `{"meta": {"_elementor_data": new_str}}`

**New v1.1 entry added**:
```js
{id:"proCta",onclick:"openWaitlistModal('Awakened')",href:"/awakened-how-this-levels-you-up/"},
```
This goes FIRST in the links array (before partnerCta and unifiedCta).

**Verification pattern**:
Live page HTML doesn't show the injection script contents — Elementor renders the HTML widget content dynamically. The verification must be done via the WP API (`?context=edit`) to read the stored Elementor data and confirm the script is there.

---

## Key Technical Patterns

### Elementor Data Double-Encoding
`_elementor_data` is stored as a JSON string. To modify it:
1. `json.loads(page_meta['_elementor_data'])` → Python list
2. Modify the Python structure
3. `json.dumps(modified_data)` → back to string
4. POST `{"meta": {"_elementor_data": string_value}}`

### Elementor Cache Must Be Cleared After Meta Update
```bash
curl -X DELETE "https://purebrain.ai/wp-json/elementor/v1/cache" -u "$USER:$PASS"
```

### Script Injection Pattern for Elementor Canvas Pages
Scripts appended after `</html>` in HTML widgets still execute in browsers. This is where the levels link injection lives on pay-test-2 and pay-test-sandbox-3.

### Awakened vs Partnered Design Tokens
- Partnered: card icons/dots/tags use `--blue` accent
- Awakened: card icons/dots/tags use `--orange` accent
- Both use same dark background `--bg: #080a12`

---

## Files
- HTML source: `/home/jared/projects/AI-CIV/aether/exports/awakened-how-this-levels-you-up.html`
- WP Page ID: 1315
- Updated pages: 689 (pay-test-2), 1232 (pay-test-sandbox-3)
