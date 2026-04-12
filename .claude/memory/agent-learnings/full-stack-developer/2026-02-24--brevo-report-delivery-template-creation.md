# Brevo Transactional Template Creation via API — Website Analysis Delivery

**Date**: 2026-02-24
**Type**: teaching + operational
**Agent**: full-stack-developer

---

## What Was Done

Created Brevo transactional email template programmatically via API for the website analysis report delivery flow.

- **Template ID**: 22
- **Template Name**: "PureBrain - Website Analysis Report Delivery"
- **Subject**: "Your Website Analysis Report is Ready"
- **Sender**: PureBrain <purebrain@puremarketing.ai>
- **Reply-To**: jared@puretechnology.nyc
- **isActive**: True
- **HTML Source**: `exports/email-templates/website-analysis-delivery.html` (23,927 chars)
- **Stored in .env as**: `BREVO_REPORT_DELIVERY_TEMPLATE_ID=22`

---

## Key Pattern: Brevo Template Creation API

**Endpoint**: `POST https://api.brevo.com/v3/smtp/templates`

**Critical gotcha**: The field for template name is `templateName`, NOT `name`.
Using `name` returns `{"code":"missing_parameter","message":"Template name is missing"}`.

```python
payload = {
    "templateName": "Your Template Name Here",   # NOT "name"
    "subject": "Your Subject",
    "sender": {
        "name": "Sender Display Name",
        "email": "sender@domain.com"
    },
    "replyTo": "replyto@domain.com",
    "isActive": True,
    "htmlContent": "<html>...</html>"  # Full HTML string
}

# Headers
headers = {
    'api-key': BREVO_API_KEY,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
```

**Response**: `{"id": 22}` — just the template ID on success.

**Verify created template**:
```
GET https://api.brevo.com/v3/smtp/templates/{templateId}
```

---

## Template Variable Tokens

The HTML uses Brevo-compatible `{{VARIABLE}}` syntax:
- `{{FIRST_NAME}}` — recipient's first name
- `{{COMPANY_NAME}}` — client's company name
- `{{REPORT_URL}}` — URL to the password-protected report page
- `{{REPORT_PASSWORD}}` — the page password
- `{{UNSUBSCRIBE_URL}}` — Brevo auto-populates this

When sending via API (`POST /v3/smtp/email`), pass these as `params` object:
```json
{
  "templateId": 22,
  "to": [{"email": "client@example.com", "name": "Client Name"}],
  "params": {
    "FIRST_NAME": "Corey",
    "COMPANY_NAME": "DuckDive",
    "REPORT_URL": "https://purebrain.ai/client-report-duckdive/",
    "REPORT_PASSWORD": "duckdive2024"
  }
}
```

---

## File References

- HTML template: `exports/email-templates/website-analysis-delivery.html`
- .env key: `BREVO_REPORT_DELIVERY_TEMPLATE_ID=22`
- Template verified live in Brevo dashboard at ID 22

---

## Gotchas

1. **`name` vs `templateName`**: Brevo's API uses `templateName` for the create endpoint — NOT `name`. This is different from many other APIs.
2. **HTML length**: 23,927 chars uploaded cleanly with no truncation.
3. **replyTo**: Accepts a plain email string (not an object), unlike `sender` which requires `{name, email}`.
