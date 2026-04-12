# Fix Patterns: wp:html Literal Text + Plugin Gate Conflict

**Date**: 2026-03-11
**Agent**: dept-systems-technology
**Pages Fixed**: 689 (pay-test-2), 405 (ai-partnership-guide)

---

## Fix 1: wp:html Appearing as Literal Text

**Symptom**: Page renders `<!-- wp:html -->` as visible text at the top.

**Root Cause**: Page content was stored in WP without proper block parsing. WordPress's `wpautop` filter processed the `<!-- wp:html -->` marker as regular text instead of a block boundary.

**Fix**: Re-deploy the content via WP REST API. WordPress block parser correctly handles `<!-- wp:html -->...\n<!-- /wp:html -->` when POSTed as raw `content`.

**Auth Pattern** (use this, not `Basic SmFyZWQ6...`):
```python
user = "purebrain@puremarketing.ai"
password = "41w3 xWWZ 11em UXgj hjAF sx2T"  # from .env PUREBRAIN_WP_APP_PASSWORD
auth = (user, password)
```

**Deploy command**:
```python
with open("exports/cf-pages-deploy/pay-test-2/index.html") as f:
    content = f.read()
requests.post("https://purebrain.ai/wp-json/wp/v2/pages/689", auth=auth, json={"content": content, "status": "publish"})
```

**Verification**: `curl -sL https://purebrain.ai/pay-test-2/ | grep "wp:html" | wc -l` should return 0.

---

## Fix 2: Duplicate Plugin Gate Conflicting with Inline Gate

**Symptom**: Email gate on ai-partnership-guide is unclickable (pointer-events: none applied to content).

**Root Cause**: Two competing gate systems:
1. **Inline gate** in Elementor HTML widget: `div#guide-email-gate` with `onsubmit="handleGuideUnlock(event)"`
2. **Plugin gate** injected by `purebrain-security` plugin via `wp_head`/`wp_footer` hooks: injects `<style id="pb-guide-gate-css">` (blurs content, sets pointer-events:none) and `<script id="pb-guide-gate-js">` (dynamically wraps DOM in `div#pb-guide-gated-content`)

The plugin gate runs `buildGate()` on DOMContentLoaded, which:
- Finds h2 headings in the page
- Wraps all content after the 4th h2 in `div#pb-guide-gated-content` (pointer-events: none, blurred)
- This wraps the inline gate div, making it unclickable

**Attempted**: Deactivating `pb-content-gate` plugin via API — works but the `purebrain-security` plugin ALSO injects the gate CSS/JS (it also hosts the `/wp-json/purebrain/v1/guide-unlock` endpoint).

**Fix**: Deployed cleanup script v2 inside the page's Elementor HTML widget:
- Runs 50ms after DOMContentLoaded (after plugin's `buildGate()` executes)
- Removes `<style id="pb-guide-gate-css">` from DOM
- Removes `<script id="pb-guide-gate-js">` from DOM
- Unwraps `div#pb-guide-gated-content` (moves children back to parent)
- Removes `div#pb-guide-gate-area` and `div#pb-guide-gate-form-wrapper`
- Restores inline gate: `pointer-events: auto, opacity: 1, filter: none`

**Key finding**: `/wp-json/purebrain/v1/guide-unlock` endpoint is in `purebrain-security` plugin. Do NOT deactivate security plugin to fix this.

**Update Elementor data pattern**:
```python
requests.post(
    "https://purebrain.ai/wp-json/wp/v2/pages/405",
    auth=auth,
    json={"meta": {"_elementor_data": json.dumps(ed)}}
)
requests.delete("https://purebrain.ai/wp-json/elementor/v1/cache", auth=auth)
```

---

## General WP Auth Notes

- **Correct auth**: `("purebrain@puremarketing.ai", "41w3 xWWZ 11em UXgj hjAF sx2T")`
- `context=edit` requires author/admin role — works with the above credentials
- Elementor cache clear after meta updates: `DELETE /wp-json/elementor/v1/cache`
- `pb-content-gate` plugin (now inactive) was originally the gate source but security plugin also injects it
