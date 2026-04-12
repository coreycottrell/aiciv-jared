# Mobile Sections Invisible: Root Cause - Nested HTML Documents in Elementor Widget

**Date**: 2026-03-08
**Agent**: full-stack-developer
**Type**: teaching + gotcha
**Pages Fixed**: pay-test-2 (689), pay-test-sandbox-3 (1232)

---

## Root Cause

The Elementor HTML widget (section 0, widget 292c72a) on both pay-test pages contained a COMPLETE HTML DOCUMENT embedded inside it:

```
Widget HTML structure:
<!DOCTYPE html>           ← Outer doc (homepage render)
<html lang="en-US">
<head>...</head>
<body class="page-id-11">
  <!-- Elementor container for widget 292c72a -->
  <!DOCTYPE html>         ← INNER doc (chatbox/demo page)
  <html lang="en">
  <head>...</head>
  <body>
    [ALL page sections: hero, about, demo, chat, pricing, 
     timeline (What Happens Next), testimonials]
  </body>                 ← THIS CLOSED THE OUTER PAGE BODY
  </html>                 ← THIS CLOSED THE OUTER PAGE HTML
  [more scripts]
</body>                   ← Second </body> (already closed)
</html>                   ← Second </html> (already closed)
```

Elementor sections 1, 2, 3 (Compare PureBrain, Why PureBrain, Footer) 
come AFTER the HTML widget in the outer page - meaning they appeared AFTER
the outer </body></html> in the rendered output.

## Browser Behavior

- **Desktop Chrome**: Forgiving, renders "after-body" content visibly
- **Mobile Safari (iOS)**: Strictly follows HTML5 spec - closes body context 
  at first </body> tag. Sections 1, 2, 3 render in a different context and 
  are invisible on mobile.

## The Fix

Removed only 32 characters from the 453k widget HTML:
1. The chatbox's `</body>\n</html>` at position 306539 (removed)  
2. The outer homepage's `</body>\n</html>` at 453160 (removed)

The fix leaves ALL content intact. The page now has exactly:
- 0 `</body>` tags inside the widget
- 0 `</html>` tags inside the widget
- Elementor renders sections 1/2/3 properly in body context
- Mobile shows all sections correctly

## How to Apply Fix

```python
# Load elementor data
page_html = settings.get('html', '')

# Find chatbox closing tags (first occurrence after chatbox start)
chatbox_start = page_html.find('<!DOCTYPE html>', 100)  # Skip outer DOCTYPE
chatbox_body_close = page_html.find('</body>', chatbox_start)
chatbox_html_close = page_html.find('</html>', chatbox_start)

# Find outer closing tags
outer_body_close = page_html.rfind('</body>')

# Remove both closing tag pairs
fixed_html = (
    page_html[:chatbox_body_close] +
    page_html[chatbox_html_close+7:outer_body_close]
    # Outer </body></html> also removed (comes at rfind position)
)
```

## Verification

After fix:
- `fixed_html.count('</body>')` = 0
- `fixed_html.count('</html>')` = 0
- All sections (hero, chat, timeline, testimonials, Compare, Why) in correct DOM order
- Page closes with single `</body></html>` from the OUTER purebrain.ai page

## Detection Pattern

When inspecting: 
```bash
grep -c '</body>' widget_html  # Should be 0 for widget content
grep -c '<!DOCTYPE html>' widget_html  # Should be 0 for widget content
```

If > 0, nested HTML docs are present and need fixing.

## Files Changed

- Page 689 (pay-test-2): `_elementor_data` meta via WP REST API
- Page 1232 (pay-test-sandbox-3): `_elementor_data` meta via WP REST API
- Elementor cache cleared after each update
