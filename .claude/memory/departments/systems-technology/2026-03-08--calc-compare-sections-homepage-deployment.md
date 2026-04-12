# Deployment: Calculator CTA + Compare Sections Across Pages

**Date**: 2026-03-08
**Type**: deployment, gotcha, pattern
**Outcome**: SUCCESS

---

## Task

Add FREE TOOL calculator section and COMPARE PUREBRAIN section to:
- Homepage (page 11)
- pay-test-2 (page 689)
- pay-test-sandbox-3 (page 1232)

Note: Task description said sandbox-3 = page 688, but actual page IDs:
- 688 = pay-test-sandbox-2 (different page)
- 1232 = pay-test-sandbox-3 (the correct one)

---

## What We Found (Pre-Deployment State)

- **Homepage (11)**: Had COMPARE PUREBRAIN section in Elementor HTML widget. MISSING calc section.
- **pay-test-2 (689)**: Had BOTH sections. Already working.
- **sandbox-3 (1232)**: Had BOTH sections. Already working.

Only action needed: Add calculator CTA section to Homepage.

---

## How Sections Are Deployed

- **COMPARE PUREBRAIN**: Embedded directly in Elementor HTML widget on each page's `_elementor_data`
- **FREE TOOL / Calculator CTA**: Via `purebrain-calculator-cta` plugin (active, targets pages 689 and 1232 in v1.0.0)
- **Both sections injected via JS DOM manipulation** (inject() function pattern)
- **Button hover CSS**: `purebrain-button-styling` plugin (all pages)

---

## Solution

Updated `pb-calculator-cta` plugin from v1.0.0 to v2.0.0:
- Added `is_front_page() || is_home()` check to also fire on homepage
- Added page 11 to `PB_CALC_CTA_PAGES` array
- Added `id="pb-calc-cta-injector"` to script tag (makes deployment verifiable)
- Improved injection strategy: searches all element types for "Compare PureBrain" text

Local file: `/home/jared/projects/AI-CIV/aether/tools/security/pb-calculator-cta/pb-calculator-cta.php`
Deploy script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_pb_calculator_cta_v200.py`

---

## Critical Gotchas

### 1. WP Plugin Slug vs Directory Name vs Deploy URL

The server plugin slug (`purebrain-calculator-cta`) does NOT always match the local directory name (`pb-calculator-cta`).
However, the WP plugin editor URL used `?file=pb-calculator-cta/pb-calculator-cta.php` and still saved successfully.
This worked because WP has its own internal mapping. Do not assume slug = directory name.

### 2. Cloudflare/CDN Caching

After plugin deploy, live page verification FAILED with standard requests.
The deployment WAS live, but Cloudflare was serving cached responses.
Cache-busted requests (`?nocache=TIMESTAMP`) bypassed CDN and confirmed success.
Always use cache-busted URLs for post-deploy verification.

### 3. CAPTCHA Rate-Limiting

After the deploy script logged in via Playwright, subsequent Playwright login attempts
were blocked with "Please verify you are human." from the security plugin.
This is rate-limiting after rapid login attempts.
Solution: Use different user agents, wait between attempts, or use WP App Password API.

### 4. Page ID Accuracy

Always verify page IDs via REST API before assuming they are correct:
```python
resp = requests.get('https://purebrain.ai/wp-json/wp/v2/pages/688', headers=auth)
data = resp.json()
print(data['slug'], data['link'])
```
In this case: 688 = pay-test-sandbox-2 (NOT sandbox-3). Sandbox-3 = 1232.

---

## Verification Method

After deploy, always cache-bust:
```python
req = urllib.request.Request(
    f'https://purebrain.ai/?nocache={int(time.time())}',
    headers={'Cache-Control': 'no-cache, no-store', 'Pragma': 'no-cache'}
)
```

Check for `pb-calc-cta-injector` (v2.0.0 script ID marker) to confirm new code is live.
Check for `Tool Sprawl` text to confirm calc section content is rendering.
Check for `Compare PureBrain` or `purebrain-vs-chatgpt` for compare section.
