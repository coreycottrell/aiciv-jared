# WP Deploy: Password-Protected Page with elementor_canvas Template

**Date**: 2026-02-26
**Type**: operational
**Topic**: Deploy self-contained HTML to WP as password-protected page with elementor_canvas

## What Was Done

Deployed `/docs/from-telegram/No BS Landing Page.html` to purebrain.ai as a new page:
- URL: https://purebrain.ai/demo-no-bs/
- WP Page ID: 963
- Template: elementor_canvas
- Password: purebrain2026
- Status: publish + password protected

## Key Patterns

### wp:html Wrap (CRITICAL)
Always wrap self-contained HTML in `<!-- wp:html -->` block before sending to WP REST API.
WordPress wpautop filter destroys CSS/JS by injecting `<p>` tags into `<style>` blocks.

```
<!-- wp:html -->
[full HTML here]
<!-- /wp:html -->
```

### REST API Payload for Password-Protected Page

```python
payload = {
    "title": "Page Title",
    "slug": "page-slug",
    "content": wrapped_html_content,
    "status": "publish",
    "template": "elementor_canvas",   # clean canvas, no theme header/footer
    "password": "your-password-here"  # WP native password protection
}
```

### Verification Checks
1. POST returns 201 with correct `slug`, `link`, `template`
2. GET /pages/{id} shows `content.protected: true` — confirms password gate active
3. Public curl to URL returns `pwbox` / `post-password` in HTML — confirms WP gate visible

### Notes
- `password` field is write-only in REST API — reading back won't show it, but `content.protected: true` confirms it
- elementor_canvas template confirmed working for standalone HTML pages on purebrain.ai
- Auth: Basic base64(user:app_password), WP user = Aether, cred key = PUREBRAIN_WP_APP_PASSWORD
