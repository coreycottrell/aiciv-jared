# Memory: White Page Fix - Rebuilt Pages 825/826 as New Pages 859/860

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer
**Topic**: When pages are persistently white/broken, rebuild on brand-new pages

---

## Problem

Pages 825 (`/client-report-duckdive/`) and 826 (`/ai-website-execution/`) were showing 100% white in incognito + hard refresh after multiple fix attempts.

Root causes:
1. Page 825: Zero raw content - content was never stored in block editor (RAW LEN: 0)
2. Page 826: Had rendered content (42KB) but CSS selectors were failing due to elementor_canvas rendering issues
3. Multiple previous fix attempts did not resolve the blank rendering

## Solution: Rebuild on New Pages

When pages are persistently broken after multiple fix attempts, the correct approach is to create brand new pages:

1. Read source HTML from exports/ directory or API rendered content
2. Extract style + body content components
3. Apply MANDATORY anti-orange CSS overrides (see below)
4. Wrap in `<!-- wp:html -->` block
5. POST to create new page (not PUT to update old broken page)
6. Verify via API (context=edit) and live HTTP check
7. Trash old pages
8. Update new page slugs to canonical URLs

## New Page IDs

- Old page 825 → New page 859 (`/client-report-duckdive/`, password: duckdive2024)
- Old page 826 → New page 860 (`/ai-website-execution/`, no password)

## HTML Content Sources

- Page 825 (DuckDive report): `/home/jared/projects/AI-CIV/aether/exports/website-analysis-report-duckdive.html`
- Page 826 (Execution service): Reconstructed from page 826 rendered API output (strip prepended magic-cursor-fix style)

## Mandatory CSS Pattern for elementor_canvas Pages

Every self-contained HTML page deployed to purebrain.ai MUST include:

```css
/* Override WordPress [class*="magic"] orange poison */
html body {
  background: #0a0e1a !important;
  background-color: #0a0e1a !important;
  color: #e8edf5 !important;
  border-color: transparent !important;
}
body.tt-magic-cursor,
body.page {
  background: #0a0e1a !important;
  background-color: #0a0e1a !important;
  color: #e8edf5 !important;
  border-color: transparent !important;
  fill: currentColor !important;
}
[class*="magic"] {
  color: inherit !important;
  background-color: inherit !important;
  border-color: inherit !important;
  fill: inherit !important;
}
```

Inject this at the TOP of the `<style>` block before deployment.

## Deployment Pattern

```python
# 1. Read source HTML
with open('exports/my-page.html', 'r') as f:
    raw_html = f.read()

# 2. Extract components
import re
font_links = '\n'.join(re.findall(r'<link[^>]+googleapis\.com[^>]+>', raw_html))
paypal = (re.search(r'<script[^>]+paypal\.com/sdk[^>]*></script>', raw_html) or type('', (), {'group': lambda s, n: ''})()).group(0)
style_content = re.search(r'<style>(.*?)</style>', raw_html, re.DOTALL).group(1)
body_content = re.search(r'<body[^>]*>(.*?)</body>', raw_html, re.DOTALL).group(1)

# 3. Inject anti-orange CSS
combined_style = f'<style>{ANTI_ORANGE_CSS}{style_content}</style>'

# 4. Wrap in wp:html
content = f'<!-- wp:html -->\n{font_links}\n{paypal}\n{combined_style}\n{body_content}\n<!-- /wp:html -->'

# 5. POST to create NEW page (don't update old broken one)
r = requests.post(
    'https://purebrain.ai/wp-json/wp/v2/pages',
    auth=AUTH,
    json={
        'title': 'Page Title',
        'content': content,
        'status': 'publish',
        'slug': 'page-slug-v2',  # Temp slug, update after verification
        'template': 'elementor_canvas'
    }
)
new_id = r.json()['id']

# 6. Verify
api_check = requests.get(f'https://purebrain.ai/wp-json/wp/v2/pages/{new_id}?context=edit', auth=AUTH).json()
assert '<!-- wp:html -->' in api_check['content']['raw']
assert 'html body' in api_check['content']['raw']

# 7. Trash old page
requests.delete(f'https://purebrain.ai/wp-json/wp/v2/pages/OLD_ID', auth=AUTH)

# 8. Update slug to canonical
requests.post(f'https://purebrain.ai/wp-json/wp/v2/pages/{new_id}', auth=AUTH,
              json={'slug': 'canonical-slug'})
```

## Verification Checklist

- Page status: 200 (or 401 for password-protected - correct)
- Content length: >50KB (if <10KB, something went wrong)
- `#0a0e1a` present in live HTML (dark background applied)
- `html body {` present in live HTML (anti-orange CSS in place)
- `<!-- wp:html -->` in raw API content
- Old -v2 slugs return 404 after cleanup
