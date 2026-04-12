# Memory: Pages 825/826 White Page Fix - html body CSS Selector

**Date**: 2026-02-23
**Type**: teaching
**Agent**: full-stack-developer

## Problem

Pages 825 and 826 on purebrain.ai rendered as ALL WHITE / invisible content. The page content existed (69KB and 42KB respectively) but the dark theme CSS was not applying.

## Root Cause

The `<style id="magic-cursor-fix">` block used selectors requiring body classes that don't exist on `elementor_canvas` template pages:

```css
/* BROKEN - requires tt-magic-cursor class on body */
body.page-id-826.tt-magic-cursor {
  background-color: #0a0e1a !important;
}
```

The `elementor_canvas` template renders a bare `<body>` tag with no CSS classes in some rendering contexts (particularly during preview/testing). The selectors never matched, so no dark theme was applied - leaving dark-colored text on white browser default background.

## Fix Applied

Replace class-dependent selectors with universal `html body` selectors:

```css
/* CORRECT - works with bare body tag, no class requirements */
html body {
  background-color: #0a0e1a !important;
  color: #e8edf5 !important;
}
html body h1, html body h2, html body h3, html body h4 {
  color: #ffffff !important;
}
html body a { color: #2a93c1 !important; }
html body a:hover { color: #f1420b !important; }
html body button, html body .cta-btn, html body [class*="btn"]:not(.tag-pill):not(.blog-tag) {
  background-color: #f1420b !important;
  color: #ffffff !important;
}
html body input, html body textarea {
  background-color: #0d1117 !important;
  color: #e8edf5 !important;
  border-color: #1a2332 !important;
}
/* Override Additional CSS poison */
[class*="magic"] {
  color: inherit !important;
  background-color: inherit !important;
}
```

## Important Nuance

The `tt-magic-cursor` class IS actually present on the live body tag when viewed through WordPress frontend (confirmed in live HTML). The issue was during Elementor preview/canvas rendering contexts where the class gets stripped. Using `html body` ensures the dark theme ALWAYS applies regardless of body class state.

## Deployment Steps

```python
import requests, re, os
from dotenv import load_dotenv
load_dotenv('.env')

AUTH = ('Aether', os.environ.get('PUREBRAIN_WP_APP_PASSWORD'))
base = 'https://purebrain.ai/wp-json/wp/v2'

r = requests.get(f'{base}/pages/826?context=edit', auth=AUTH).json()
content = r['content']['raw']

OLD_PATTERN = r'<style id="magic-cursor-fix">.*?</style>'
new_content = re.sub(OLD_PATTERN, NEW_CSS, content, flags=re.DOTALL)

# Deploy
requests.put(f'{base}/pages/826', auth=AUTH, json={'content': new_content})
# For password-protected page 825:
requests.put(f'{base}/pages/825', auth=AUTH, json={'content': new_content825, 'password': 'duckdive2024'})
# Clear cache
requests.delete(f'https://purebrain.ai/wp-json/elementor/v1/cache', auth=AUTH)
```

## Verification Results

- Page 826 live: Status 200, 147KB, dark background `#0a0e1a` present, `html body {` selector confirmed
- Page 825: Password-protected (CSS inside content, not served to unauthenticated visitors - expected)
- Both pages verified via REST API (`context=edit`) showing correct style blocks

## Rule for Future

**When deploying CSS for elementor_canvas pages**: Always use `html body` selector, never `body.CLASSNAME`. The canvas template can strip body classes in unpredictable ways. Universal selectors are the only reliable approach.

## Pages Modified

- Page 825: `/client-report-duckdive/` (password: duckdive2024, draft)
- Page 826: `/ai-website-execution/` (published)
