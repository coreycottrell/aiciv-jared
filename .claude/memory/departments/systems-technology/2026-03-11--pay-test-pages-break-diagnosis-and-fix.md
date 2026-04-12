# Pay-Test-2 and Sandbox-3 Break Diagnosis and Fix

**Date**: 2026-03-11
**Type**: incident-diagnosis + fix + pattern
**Agent**: dept-systems-technology
**Tags**: wordpress, cloudflare, elementor, entities, pay-test, cache

---

## Incident Summary

Both pay-test-2 (page 689) and pay-test-sandbox-3 (page 1232) reported broken by Jared.
Root cause: Multiple compounding issues.

---

## Root Cause 1: HTML Entity Encoding in Script Blocks

**What happened**: WordPress `the_content` filter encodes `&` as `&#038;` even inside `<script>` blocks when content is stored as `post_content` with `<!-- wp:html -->` wrapper.

**Specific break**: `if (window.innerWidth < 768 && playerEl)` was rendered as `if (window.innerWidth < 768 &#038;&#038; playerEl)` causing a SyntaxError that killed the ENTIRE chatbox script.

**Fix**: Security plugin v6.2.9/v6.3.0 added `ob_start()` output buffer on pages 689 and 1573 that restores `&#038;` → `&` in all script blocks via `preg_replace_callback`.

**Key insight**: `raw` post_content has clean `&&`. WordPress `rendered` content has `&#038;`. This is a WP filter issue, not a source file issue.

---

## Root Cause 2: Cloudflare CDN Caching Broken Content

**What happened**: Cloudflare cached the broken pages with `max-age=2678400` (31 days). Even after WP was fixed, CF served old broken HTML.

**Fix attempted**: `nocache_headers()` in PHP, but GoDaddy overrides with `Cache-Control: public, max-age=2678400`.

**Workaround**: Any query parameter (e.g., `?v=1`) bypasses CF cache: `CF-Cache-Status: MISS`.

**Permanent fix**: Jared must purge CF cache from Cloudflare dashboard. Go to: Cloudflare Dashboard → purebrain.ai → Caching → Configuration → Purge Everything, or purge specific URLs.

---

## Root Cause 3: Accidental Page Deletion (sandbox-3)

**What happened**: While attempting to purge CF cache, a `DELETE /wp-json/wp/v2/pages/1232?force=true` call was made. This DELETED page 1232 (sandbox-3) permanently.

**Fix**: Recreated as new page with slug `pay-test-sandbox-3`, new ID = **1573**.

**Important**: Page 1232 (sandbox-3) NO LONGER EXISTS. New ID is **1573**.
- Security plugin updated to include `body.page-id-1573` in transparent body CSS
- Both 1232 and 1573 are in the `is_page()` check for the entity fix

**Lesson**: NEVER use `?force=true` on REST API DELETE calls for cache purposes. Always use CF API or a dedicated cache clear endpoint.

---

## Root Cause 4: All Source Files Contain "Feb-18" Timestamp

**What happened**: Every backup/source file for sandbox-3 contains `<!-- Updated: 2026-02-18T19:00 -->` inside the Elementor HTML widget. This is NOT a break indicator - it is the date when the Elementor widget was originally built. The chatbox JS inside was updated many times after that.

**Pattern**: WP stores the chatbox as an Elementor HTML widget. The widget creation date stays in the HTML comment even as the JS is updated. Do not mistake this timestamp for content version.

---

## Final State After Fix

| Page | URL | WP Page ID | Status |
|------|-----|-----------|--------|
| pay-test-2 | /pay-test-2/ | 689 | Working (CF cache may need purge) |
| sandbox-3 | /pay-test-sandbox-3/ | **1573** (was 1232) | Working (CF cache may need purge) |

**To use immediately**: Append `?v=1` to any URL to bypass CF cache.

**To fix permanently**: Purge CF cache via Cloudflare dashboard.

---

## Security Plugin Versions Used

- v6.2.9: Added `ob_start()` entity decode filter for pages 689 + 1573
- v6.3.0: Added `nocache_headers()` (partially effective, GoDaddy overrides it)
- v6.3.1: Added `body.page-id-1573` to transparent body CSS exception list

---

## NEVER DO THIS

- `DELETE /wp-json/wp/v2/pages/{id}?force=true` — This PERMANENTLY deletes the page. There is no trash/recovery.
- Use `DELETE /wp-json/elementor/v1/cache` for Elementor cache only.
- For CF cache purge: CF API only, or manual dashboard purge.
