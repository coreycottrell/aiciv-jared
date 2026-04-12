# Page 11 Pricing Button Text Changes
**Date**: 2026-03-01
**Agent**: dept-systems-technology
**Type**: technique + gotcha

## Task
Changed pricing button text on purebrain.ai homepage (page 11):
- Awakened, Bonded, Partnered: "Reserve Your Spot" -> "Reserve Your AI Now" (static HTML)
- Bonded JS (showPricing fn): "Activate ${aiName} Now" -> "Reserve ${aiName} Now"
- Bonded JS fallback: "Activate Now" -> "Reserve Now"
- Unified and Enterprise "Reserve Your Spot" intentionally left unchanged

## Key Technical Findings

### "Activate Keen Now" is JS-injected, not static HTML
- The Bonded button's static HTML says "Reserve Your Spot"
- The `showPricing()` JavaScript function replaces it via `document.getElementById('proCta').textContent`
- "Keen" is the AI name generated during the chatbox naming session — not a hardcoded tier name
- Jared saw "Activate Keen Now" because he had gone through the chatbox before viewing pricing

### Awakened and Partnered have NO hardcoded AI names
- They use `ai-name-dynamic` CSS class placeholders populated by `updateAllDynamicNames()`
- The `showPricing()` function only updates `proCta` (Bonded), not the other tier buttons
- Changed their static text to "Reserve Your AI Now" as the most accurate interpretation

### purebrain/v1/update-post-meta does NOT allow _elementor_data
- The custom REST endpoint has an allowlist that excludes _elementor_data
- Must use the standard WP REST API: `POST /wp/v2/pages/11` with `{"meta": {"_elementor_data": "..."}}`
- This works fine with Aether's app password

### Pushing large elementor data (352KB)
- Cannot pass via curl command line argument (argument list too long)
- Must use Python urllib.request to POST the payload

## Deployment Steps Used
1. Fetch raw elementor data via `GET /wp/v2/pages/11?context=edit&_fields=meta`
2. Save RAW backup to /tmp/page11_elementor_RAW_BACKUP.json
3. Apply changes with Python string replacement (by section, not global replace)
4. Push via `POST /wp/v2/pages/11` with meta._elementor_data
5. Clear Elementor cache via `DELETE /elementor/v1/cache`
6. Verify live page with curl + string count checks

## Verification Results (PASS)
- "Reserve Your AI Now" on live page: 3 occurrences (Awakened, Bonded, Partnered) ✓
- "Reserve Your Spot" remaining: 2 (Unified + Enterprise) ✓
- "Activate ${aiName} Now" in JS: 0 ✓
- "Reserve ${aiName} Now" in JS: 1 ✓
- File size delta: +4 chars (3 static buttons +2 each, 2 JS changes net -2) ✓

## Files
- Backup: /tmp/page11_elementor_RAW_BACKUP.json (352,973 chars)
- Modified: /tmp/page11_elementor_MODIFIED.json (352,977 chars)
- Push script: /tmp/push_elementor_v2.py
