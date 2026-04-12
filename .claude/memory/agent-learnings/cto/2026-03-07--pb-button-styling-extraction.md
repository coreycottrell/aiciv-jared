# Extraction #4: pb-button-styling

**Date**: 2026-03-07
**Type**: operational
**Topic**: Security plugin extraction — button hover CSS (task 4 of 14)

## What Was Extracted

Button hover CSS block (v6.2.2) from `purebrain-security-plugin.php`.

- Calculator button (`a[href*="ai-tool-stack-calculator"]`) → blue hover (#2a93c1)
- Comparisons button (`a[href="/compare/"]`) → orange hover (#f1420b)
- Hook: `wp_head` (no priority specified = default 10)
- Style tag ID: `pb-button-hover-v622`

## Source Location in Security Plugin

- Lines: **6072–6097**
- Section header comment: `// BUTTON HOVER CSS (v6.2.2 — merged from v4.8.4)`
- First line of block: `// =============================================================================`
- Last line of block: `} );`

## Standalone Plugin Created

Path: `tools/security/pb-button-styling/pb-button-styling.php`

## Removal Instructions for Security Plugin

Remove lines 6072–6097 (inclusive) and replace with:

```php
// BUTTON HOVER CSS — extracted to pb-button-styling plugin (2026-03-07)
```

## Pattern Notes

- Smallest extraction so far: 26 lines of functional code inside the block (excluding the section delimiters)
- Pure CSS injection via wp_head — no PHP logic, no conditionals, no page-ID checks
- Zero risk to other functionality when removed from security plugin
