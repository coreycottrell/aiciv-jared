# Brevo Template Icon + Branding Fix

**Date**: 2026-02-21
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Added PureBrain hexagon icon to all 7 Neural Feed Brevo email templates

---

## What Was Done

Added the PureBrain hexagon icon and fixed brand colors across all 7 Neural Feed welcome
sequence templates (Template IDs 1-7).

---

## Changes Per Template

1. Added PureBrain hexagon icon (52x52px) above the PUREBRAIN.ai text in header
2. Added `.header-ai-suffix { color: #ffffff; }` CSS for white ".ai" on dark bg
3. Wrapped ".ai" in `<span class="header-ai-suffix">` so it renders white
4. PUREBR + N remain #2a93c1 (blue), AI remains #f1420b (orange)

---

## Files

- **Update script**: `/home/jared/projects/AI-CIV/aether/tools/update_brevo_templates_icon.py`
- **Icon source**: `/home/jared/projects/AI-CIV/aether/docs/assets/logos/purebrain-icon.png` (2100x2100 RGBA)
- **Icon public URL**: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon-email.png` (WP media ID 607)

---

## New Header HTML Structure

```html
<div class="header">
  <a href="https://purebrain.ai" style="text-decoration: none;">
    <!-- Icon -->
    <div style="margin-bottom: 10px;">
      <img src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon-email.png"
           alt="PureBrain" width="52" height="52"
           style="width: 52px; height: 52px; display: block; margin: 0 auto;" />
    </div>
    <!-- Logo text -->
    <div class="header-logo">PUREBR<span class="ai">AI</span>N<span class="header-ai-suffix">.ai</span></div>
  </a>
  <div class="header-sub">The Neural Feed</div>
</div>
```

---

## Icon Upload to WordPress

Used WordPress REST API to upload PNG to media library:
- Endpoint: `POST https://purebrain.ai/wp-json/wp/v2/media`
- Auth: Aether user + PUREBRAIN_WP_APP_PASSWORD
- Headers: `Content-Disposition: attachment; filename="purebrain-icon-email.png"` + `Content-Type: image/png`
- Result: 201 Created, media ID 607

---

## Brand Color Reference

| Element | Color |
|---------|-------|
| PUREBR | #2a93c1 (blue) via `.pure`, `.br` CSS classes |
| AI | #f1420b (orange) via `.ai` CSS class |
| N | #2a93c1 (blue) - bare text in `.header-logo` |
| .ai suffix | #ffffff (white) via `.header-ai-suffix` CSS class |
| Background | #0d1117 (dark) |

---

## Test Verification

After updating all 7 templates, sent test email of Template 1 to jaredsanborn@yahoo.com.
Message ID: `<202602211503.73498715556@smtp-relay.mailin.fr>`

---

## Brevo API Pattern for Template Updates

```python
# PUT to update template HTML
resp = requests.put(
    f'https://api.brevo.com/v3/smtp/templates/{template_id}',
    headers={'api-key': BREVO_API_KEY, 'Content-Type': 'application/json'},
    json={'htmlContent': new_html, 'subject': existing_subject},
    timeout=15,
)
# 204 = success (no body returned)
```

Note: Must preserve the `subject` field when updating - passing empty string would blank it.
