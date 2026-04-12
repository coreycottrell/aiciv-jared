# Hunden Partners Password-Protected Page Deployment

**Date**: 2026-03-02
**Type**: operational
**Topic**: Deploying a large self-contained HTML file as a password-protected WordPress page

## What Was Done

Deployed `/home/jared/projects/AI-CIV/aether/exports/hunden-partners-purebrain.html` (73KB) to purebrain.ai as a password-protected page.

## Result

- Page ID: 1206
- URL: https://purebrain.ai/hunden-partners/
- Password: hunden2026
- Password protection confirmed live

## Key Patterns

### Python requests (not curl) for large HTML

curl struggles with large files and special characters. Use Python requests with `json=data` parameter so the payload is properly serialized:

```python
import requests
r = requests.post(url, json=data, auth=('Aether', wp_pass), timeout=60)
```

### Password protection via REST API

Include `"password": "hunden2026"` in the JSON body. WordPress sets the page to password-protected automatically.

### elementor_canvas template

For self-contained sales pages that should not show any WordPress theme chrome (no header, no footer, no sidebar), use `"template": "elementor_canvas"`.

### wp:html wrapper

Always wrap raw HTML in `<!-- wp:html -->...\n<!-- /wp:html -->` to prevent wpautop from injecting `<p>` tags into `<style>` blocks.

### Verification pattern

After deployment, GET the page URL without credentials. WordPress returns the `post-password-form` element when password protection is active.

```python
r = requests.get('https://purebrain.ai/hunden-partners/', allow_redirects=True)
assert 'post-password-form' in r.text or 'Protected' in r.text
```

## Credentials Location

- PUREBRAIN_WP_APP_PASSWORD in `/home/jared/projects/AI-CIV/aether/.env`
- WordPress user: `Aether`
- API endpoint: `https://purebrain.ai/wp-json/wp/v2/pages`
