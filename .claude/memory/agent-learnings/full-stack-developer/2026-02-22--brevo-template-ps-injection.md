# Brevo Template P.S. Injection - 2026-02-22

**Type**: operational
**Topic**: Injecting P.S. reply-invitation sections into Brevo email templates via API

## Task
Injected P.S. HTML sections into Neural Feed welcome sequence templates 2, 4, and 5.

## Templates Updated

| Template ID | Name | P.S. Topic |
|-------------|------|-----------|
| 2 | Neural Feed - Email 2 - Jared's Story | When you stopped using AI as a tool |
| 4 | Neural Feed - Email 4 - Partnership in Practice | What topics are useful in The Neural Feed |
| 5 | Neural Feed - Email 5 - The Context Tax | Setup work vs actual thinking ratio |

## API Pattern That Works

```python
# GET template
GET https://api.brevo.com/v3/smtp/templates/{id}
# Returns: htmlContent, name, subject, etc.

# PUT updated template (204 = success, no body)
PUT https://api.brevo.com/v3/smtp/templates/{id}
Body: {"htmlContent": "updated HTML"}
```

## Insertion Point
All Neural Feed templates share this footer structure:
```html
    </div>
    <div class="footer">
      <p>PureBrain.ai — AI partnership...</p>
      <p><a href="{{ unsubscribe }}">Unsubscribe</a>...</p>
    </div>
  </div>
</div>
</body>
</html>
```

**Insert P.S. BEFORE `<div class="footer">`** - this places it after the signature, before unsubscribe.

## P.S. HTML Structure
Wrapped in `<table role="presentation">` for email client compatibility:
```html
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
<tr>
  <td style="padding: 40px 0 0 0; text-align: center; font-family: 'Segoe UI', ...">
    <p style="margin: 0 0 12px 0; font-style: italic; color: #a0adc0;">P.S.</p>
    <p style="margin: 0; color: #b8c5d6;">[Reply invitation text]</p>
  </td>
</tr>
</table>
```

## Verification Method
After PUT, do GET and check:
1. `'P.S.' in html` - P.S. label present
2. Expected unique text snippet is in HTML
3. HTML length increased by ~550-580 chars (expected)

## Result
- Template 2: PASS (7226 chars, +549)
- Template 4: PASS (7010 chars, +566)
- Template 5: PASS (7018 chars, +578)

## Key Lessons
- Brevo PUT template returns 204 (no content) on success - don't expect a body
- Use `str.replace(target, replacement, 1)` with count=1 to avoid double-replacing
- The `{{ unsubscribe }}` Brevo tag is in the footer - preserve it untouched
- Always GET after PUT to verify the change actually persisted
