# Memory: Page 860 White Page - Root Cause and Fix

**Date**: 2026-02-24
**Type**: teaching
**Agent**: full-stack-developer
**Topic**: Why page 860 was white despite having correct dark theme CSS

---

## The Problem

`/ai-website-execution/` (page 860) showed 100% white in incognito despite:
- Correct `elementor_canvas` template
- `<!-- wp:html -->` block wrapping
- Dark background CSS (`background: #080a12 !important`) in page content
- All content rendering correctly (158KB HTML, "You Saw the Gaps" text present)

## Root Cause: Missing page-id-860 in Plugin Footer Fix

**Primary cause**: The plugin's `pb-magic-cursor-body-override` style block (injected via `wp_footer` at priority 99) had explicit overrides for pages 816, 825, 826, 859 - but **NOT page 860**.

The footer fix is authoritative because it:
1. Loads LAST (wp_footer priority 99)
2. Uses maximum specificity: `body.page-id-860.tt-magic-cursor` = (0,2,1)
3. Has `!important`

**Secondary cause**: Bootstrap v5.3.2 CSS (loaded by Artistics theme) sets:
- `:root { --bs-body-bg: #fff; }`
- `body { background-color: var(--bs-body-bg) }` (no !important)

**Tertiary cause**: Additional CSS (wp-custom-css) had:
- `[class*="magic"] { background-color: #f1420b !important }` = specificity (0,1,0)
- This matches `body.tt-magic-cursor` (class attribute contains "magic")
- Makes body orange with !important

**Why the content CSS wasn't enough**:
- Content CSS (`body.page-id-860 { background: #080a12 !important }`) DOES load in the body
- But with same specificity (0,1,1) and same !important, the LATER rule wins
- The Additional CSS (head) loads before our content CSS (body)
- Our content CSS should win... but Cloudflare CDN was caching an old version

## Fix Applied

### 1. Plugin v5.0.0 - Added page-id-860 to footer override

In `/tools/security/purebrain-security/purebrain-security-plugin.php`:

```css
/* Page-860 specific maximum-specificity override for /ai-website-execution/ */
body.page-id-860.tt-magic-cursor {
    color: #e8edf5 !important;
    background-color: #080a12 !important;
    background: #080a12 !important;
    border-color: inherit !important;
}
```

Added after page-id-859 block in `pb-magic-cursor-body-override` style.

### 2. Nuclear CSS in page content

Added a comprehensive multi-level override at the top of the page CSS:
- Level 1: `html body` (all variants including page-id-860)
- Level 2: `body.tt-magic-cursor` (specificity 0,1,1)
- Level 3: `body.page-id-860.tt-magic-cursor` (specificity 0,2,1)
- Level 4: `:root { --bs-body-bg: #080a12 }` (overrides Bootstrap variable)
- Level 5: `body[class]` (attribute+class, specificity 0,1,1)

## Plugin Deployment Process

The WordPress REST API `PUT /plugins/{plugin}` does NOT update PHP code.
To update plugin code:

```python
# 1. Delete plugin via REST
requests.delete('https://purebrain.ai/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin', auth=auth)

# 2. Login via wp-login.php to get session cookies
session.post('https://purebrain.ai/wp-login.php', data={...})

# 3. Get nonce from plugin-install.php
install_r = session.get('https://purebrain.ai/wp-admin/plugin-install.php?tab=upload')
nonce = re.search(r'name="_wpnonce"\s+value="([^"]+)"', install_r.text).group(1)

# 4. Upload zip via update.php
session.post('https://purebrain.ai/wp-admin/update.php?action=upload-plugin',
    data={'_wpnonce': nonce, 'action': 'upload-plugin'},
    files={'pluginzip': ('name.zip', zip_bytes, 'application/zip')})

# 5. Activate via REST API
requests.put('.../plugins/purebrain-security/purebrain-security-plugin', auth=auth, json={'status': 'active'})
```

**Note**: wp-login.php returns 429 if called too frequently. Use app password for REST API.

## CSS Specificity Reference for This Site

| Rule | Specificity | Source |
|------|-------------|--------|
| `[class*="magic"]` | (0,1,0) | Additional CSS (head) |
| `body.tt-magic-cursor` | (0,1,1) | Plugin footer fix |
| `body.page-id-860.tt-magic-cursor` | (0,2,1) | Plugin footer fix (authoritative) |

## Future Prevention

When creating new self-contained HTML pages on purebrain.ai:
1. Note the new page ID
2. Add `body.page-id-{NEW_ID}.tt-magic-cursor` to the plugin footer fix
3. Deploy plugin update BEFORE or ALONGSIDE the page content
4. The page content CSS alone is NOT sufficient because CF caching and load order

## Files Changed

- `/tools/security/purebrain-security/purebrain-security-plugin.php` - v5.0.0
- `/exports/ai-website-execution.html` - Nuclear CSS added to source
- WordPress page 860 - Updated content via REST API
