# Pricing Audit: $79 Tier Removal from Non-Protected Pages

**Date**: 2026-03-02
**Type**: audit + fix
**Tags**: pricing, $79, Awakened, WordPress, Elementor, audit

---

## Rule Established

**$79 (Awakened tier) should ONLY appear on:**
- Main page (ID=11, slug: pure-brain-agentic-ai-partner)
- Test/sandbox pages (IDs: 383, 338, 174, 439, 468, 688, 689)

**All other pages must NOT show $79 as PureBrain pricing.**

---

## Audit Results (78 total items: 62 pages + 16 posts)

### Issues Found and Fixed

| Page ID | Slug | Issue | Fix Applied |
|---------|------|-------|-------------|
| 987 | invitation | Awakened $79/mo pricing card | Removed entire Awakened pricing card |
| 923 | partners | $79 in commission calculator + FAQ | Removed $79 option from selector, updated FAQ example to $149 |
| 777 | ai-tool-stack-calculator | $79 in OG meta, TIERS array, mobile display | Updated to $149 across all 3 locations |
| 541 | terms-of-service | $79/month in billing table | Updated Awakened row to "See purebrain.ai for current pricing" |
| 403 | ai-readiness-assessment | $79 in tier display + JS result desc | Required TWO separate fixes (post_content + _elementor_data) |

### Pages Confirmed OK (No Change Needed)

| Page ID | Slug | Reason |
|---------|------|--------|
| 1044 | purebrain-vs-sitegpt | $79 = SiteGPT Growth plan price (competitor), PureBrain shown at $179 |

### Protected Pages (Allowed to Keep $79)

| Page ID | Slug |
|---------|------|
| 11 | pure-brain-agentic-ai-partner (main homepage) |
| 439, 468, 688, 689 | pay-test, pay-test-sandbox, pay-test-2, pay-test-sandbox-2 |

---

## Critical Technical Gotcha: Elementor vs post_content

**Page 403 required two separate updates:**

1. First fix: Updated `post_content` (via `content` field in REST API) -- this worked but Elementor IGNORED it
2. Elementor serves from `_elementor_data` meta field, NOT from `post_content`
3. Required fetching `_elementor_data` via `context=edit`, doing string replacement, and POSTing back via `meta._elementor_data`

**Pattern for Elementor pages:**
```python
# Get
r = requests.get('https://purebrain.ai/wp-json/wp/v2/pages/{id}?context=edit', auth=auth)
elementor_data = r.json()['meta']['_elementor_data']

# Fix
elementor_data = elementor_data.replace(old_text, new_text)

# Update
requests.post(url, auth=auth, json={'meta': {'_elementor_data': elementor_data}})

# MUST clear Elementor cache after:
requests.delete('https://purebrain.ai/wp-json/elementor/v1/cache', auth=auth)
```

**How to identify Elementor pages:**
- `template: 'elementor_canvas'` in REST API response
- `meta._elementor_edit_mode: 'builder'`
- `meta._elementor_data` present and non-empty

**How to identify post_content pages (wp:html blocks):**
- `template: ''` or standard template
- `content.raw` has the actual HTML content
- Updates via `content` field in REST API

---

## WP Caching Notes

- After updating `_elementor_data`, must clear Elementor cache: `DELETE /wp-json/elementor/v1/cache`
- Cloudflare may also cache pages - verification should fetch with `Cache-Control: no-cache` header
- REST API `rendered` content reflects WP's server-side render, which uses Elementor data

---

## Verification Method

Final verification scan: 78 items, fetched rendered content, searched for $79.

Results:
- 76 clean (no $79 at all)
- 1 protected (main page, $79 allowed)
- 1 competitor pricing (1044, $79 = SiteGPT)
- 0 issues

---

## What Each Non-$79 Change Did

- **Invitation page**: Removed Awakened pricing card entirely (pricing section still shows Bonded, Partnered, Unified)
- **Partners page**: Calculator starts at $149 (Bonded) as lowest tier; FAQ example updated
- **Calculator**: Awakened tier price changed to 149 in TIERS array - affects all calculator recommendations
- **Terms of Service**: Legal reference to Awakened price now says "See purebrain.ai for current pricing"
- **Readiness Assessment**: Tier display shows "See pricing", result desc no longer cites specific price
