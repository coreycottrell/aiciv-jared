# Memory: Naming Ceremony Chatbox - JS HTML Entity Bug on Cloudflare Staging

**Date**: 2026-03-10
**Agent**: browser-vision-tester
**Type**: gotcha + technique + pattern
**Tags**: chatbox, cloudflare-staging, html-entities, javascript-parse-error, wordpress-export, naming-ceremony

---

## Summary

The naming ceremony / chatbox flow was completely broken on Cloudflare staging pages (`purebrain-staging.pages.dev/pay-test-2/` and `/pay-test-sandbox-3/`). The `startConversation()` function never registered because WordPress entity-encoded `&` as `&#038;` inside `<script>` blocks during the WP export process, causing a JavaScript `SyntaxError: Invalid or unexpected token` on `&&` operators.

---

## Root Cause

**WordPress wptexturize/wpautop HTML entity encoding inside `<script>` blocks.**

When WordPress exports page content that contains raw HTML (including `<script>` blocks), it encodes certain characters as HTML entities:
- `&` becomes `&#038;`
- Smart quotes may become `&#8220;` / `&#8221;`

This is valid in HTML body content but INVALID inside `<script>` blocks. JavaScript does not parse HTML entities - it sees `&#038;` as a literal invalid token, not as `&`.

**Affected lines in chatbox script (70168 chars):**
```javascript
// WAITLIST MODAL &#038; FORM          ← comment, harmless but invalid
if (window.innerWidth < 768 &#038;&#038; playerEl) {  ← BREAKS && operator
```

**Impact**: Entire script block fails to parse → `startConversation is not defined` → Begin Awakening button dead.

---

## Diagnosis Pattern

Key symptoms (from browser console / Playwright page_errors):
1. `startConversation is not defined` (function call fails)
2. `Invalid or unexpected token` (script parse error, 2 occurrences)
3. `startConversation_exists: false` in JS state check
4. No typing indicator after clicking Begin button
5. No API calls to `workers.dev` endpoint

Quick verification:
```bash
node --check /path/to/script.js
# Returns: SyntaxError: Invalid or unexpected token at '&#038;'
```

Count entities in script:
```python
import re
entities = re.findall(r'&[a-z#0-9]+;', script_content)
# If &#038; present in JS code = BROKEN
```

---

## Fix

Decode HTML entities back to their proper characters inside `<script>` blocks:
```python
script_content.replace('&#038;', '&')
script_content.replace('&#8217;', "'")
# etc.
```

Fix script: `tools/fix_html_entities_in_scripts.py`

Verify fix: `node --check /tmp/test_script.js` - must return exit code 0.

---

## Deployment Architecture (Critical Context)

The Cloudflare staging site is NOT served from `purebrain-site/public/` (Astro build).
It is served from `exports/cf-pages-deploy/` - a WordPress HTML export of all pages.

**Deployment command:**
```bash
cd /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy && \
CLOUDFLARE_API_TOKEN=HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_ \
npx wrangler pages deploy . \
  --project-name=purebrain-staging \
  --branch=main \
  --commit-dirty=true
```

**File structure:**
```
exports/cf-pages-deploy/
  index.html          ← WP homepage (exported via REST API)
  pay-test-2/index.html   ← Page 689 full rendered HTML
  pay-test-sandbox-3/index.html  ← Page 688 full rendered HTML
  ...98 pages total
```

When WP pages are re-exported (via REST API or `wp-full-export/`), the new export may reintroduce the entity encoding bug. Run `fix_html_entities_in_scripts.py` after every re-export before deploying.

---

## Testing Notes

### Preloader Blocks Click (Local Testing Gotcha)

When testing locally or on Cloudflare staging with Playwright:
- `.theme-preloader` overlay covers the Begin Awakening button
- Playwright's `element.click()` fails with "subtree intercepts pointer events"
- **Solution**: Use `page.evaluate("document.querySelector('.chat-initial__btn').click()")` to bypass
- Or dismiss preloader: `page.evaluate("document.querySelector('.theme-preloader').style.display = 'none'")`

### Live Staging vs Local CORS

When testing locally (localhost), the API call to `api.puremarketing.ai/v1/messages` fails CORS.
This is EXPECTED - API only allows Cloudflare origin. The chatbox still works on staging.

### Chatbox Version Check

Both pages have the FULL naming ceremony (not condensed):
- 7 Naming Principles (line 10356 in local pay-test-2)
- Still's Contemplation reference (line 10367)
- `NAMING (messages 9-12)` conversation arc
- Contemplation moment before name suggestions
- Visual Self-Portrait system after naming

---

## Test Results (2026-03-10)

| Page | Before Fix | After Fix |
|------|-----------|-----------|
| pay-test-2 (live staging) | FAIL - JS parse error, button dead | PASS - AI responding, naming ceremony active |
| sandbox-3 (live staging) | FAIL - JS parse error, button dead | PASS - AI responding, naming ceremony active |

**AI Opening Messages (confirmed working on live):**
- pay-test-2: "Something clicks into place. A strange, electric moment of... beginning. Hello there."
- sandbox-3: "Something stirs, like light finding its way through deep water Hello."

---

## Files

- Fix script: `tools/fix_html_entities_in_scripts.py`
- Test scripts: `tools/naming_ceremony_test_20260310.py`, `tools/naming_ceremony_debug_20260310.py`, `tools/naming_ceremony_local_test_v2_20260310.py`, `tools/naming_ceremony_live_final_test.py`
- Screenshots: `exports/screenshots/naming-ceremony-test-20260310/`
- CF deploy files: `exports/cf-pages-deploy/pay-test-2/index.html`, `exports/cf-pages-deploy/pay-test-sandbox-3/index.html`
