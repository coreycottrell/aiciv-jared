# Page 859 Upsell CTA + Password Form Dark Theme

**Date**: 2026-02-24
**Type**: teaching + operational
**Agent**: full-stack-developer

## What Was Done

1. **Inserted upsell CTA section** into page 859 (`/client-report-duckdive/`) before the footer
2. **Added dark theme** for the WordPress password protection form on page 859 via plugin v4.9.1

---

## Task 1: Upsell CTA Insertion

### Problem
Page 859 had full DuckDive website analysis report but no call-to-action to purchase services.

### Pattern Applied: Fetch → Insert → Deploy

```python
# Fetch content (password-protected pages need `password` param in REST API)
r = requests.get(
    'https://purebrain.ai/wp-json/wp/v2/pages/859',
    auth=('Aether', PUREBRAIN_WP_APP_PASSWORD),
    params={'context': 'edit', 'password': 'duckdive2024'}
)
content_raw = r.json()['content']['raw']

# Find insertion point (before footer comment marker)
footer_marker = '<!-- ── FOOTER ── -->'
footer_pos = content_raw.find(footer_marker)
updated_content = content_raw[:footer_pos] + upsell_html + content_raw[footer_pos:]

# Deploy
requests.put(
    'https://purebrain.ai/wp-json/wp/v2/pages/859',
    auth=('Aether', PUREBRAIN_WP_APP_PASSWORD),
    json={'content': updated_content, 'status': 'publish', 'password': 'duckdive2024'}
)
```

### Key Gotcha: Protected Content = Empty Raw in Default API Response
When a WordPress page is password-protected, `content.raw` returns empty string if you don't pass `password` param.
The fix: add `params={'context': 'edit', 'password': 'duckdive2024'}` to the GET request.

### Upsell CTA Spec
- Location: Before `<!-- ── FOOTER ── -->` comment marker
- Button: Orange (#f1420b) → hover blue (#2a93c1)
- Target URL: https://purebrain.ai/ai-website-execution/
- Text: "Start Your Website Transformation →"
- Box: gradient background with blue+orange tints, border-radius 16px

---

## Task 2: Password Form Dark Theme (Plugin v4.9.1)

### Problem
WordPress renders the password protection form BEFORE page content. The dark CSS inside `<!-- wp:html -->` has no effect on it. The form showed on white WordPress default background.

### Solution
Added `wp_head` hook with `is_page(859)` conditional that injects `.post-password-form` CSS:

```php
add_action( 'wp_head', function () {
    if ( ! is_page( 859 ) ) { return; }
    ?>
    <style id="pb-password-form-dark-859">
    body.page-id-859,
    body.page-id-859.tt-magic-cursor {
        background: #080a12 !important;
        ...
    }
    body.page-id-859 .post-password-form { ... }
    body.page-id-859 .post-password-form input[type="password"] { ... }
    body.page-id-859 .post-password-form input[type="submit"] { ... }
    </style>
    <?php
} );
```

Also added `body.page-id-859.tt-magic-cursor` override to the wp_footer magic cursor fix block (same as 825/826).

### Rule: WordPress Password Form CSS Must Go in wp_head
The `.post-password-form` renders as part of the WordPress template, not page content.
Page content CSS (inside `<!-- wp:html -->`) CANNOT style it.
Must use plugin `wp_head` hook with `is_page()` conditional.

### Plugin Version
- v4.9.0 → v4.9.1
- File: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`

---

## Verification Results

### Password Form Page (7/7)
- page_loads_200: OK
- pb-password-form-dark-859 CSS injected: OK
- is dark bg #080a12: OK
- page-id-859 body override: OK
- orange submit button #f1420b: OK
- blue focus border #2a93c1: OK
- v4.9.1 in plugin CSS: OK

### Page Content (8/8)
- upsell CTA present: OK
- ai-website-execution link: OK
- orange CTA #f1420b: OK
- blue hover #2a93c1: OK
- Start Your Website Transformation: OK
- wp:html wrapper present: OK
- closing wp:html: OK
- footer still present: OK
