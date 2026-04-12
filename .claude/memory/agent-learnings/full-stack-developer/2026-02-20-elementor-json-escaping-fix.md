# Learning: Elementor _elementor_data JSON Escaping - innerHTML vs DOM API

**Date**: 2026-02-20
**Agent**: full-stack-developer
**Context**: pay-test-sandbox page (WP page 468) fix

## The Bug

When injecting JavaScript into Elementor `_elementor_data` that contains HTML strings with double-quoted attributes, the JSON becomes invalid.

Example of what BREAKS:
```javascript
// In JS code being injected into _elementor_data:
el.innerHTML = '<hr style="border:none;" />';  // BREAKS JSON
```

The `"` in `style="..."` terminates the surrounding JSON string prematurely.

## The Fix

Use DOM API instead of innerHTML when building HTML elements in injected JS:

```javascript
// SAFE - no double quotes in strings:
var hr = document.createElement('hr');
hr.style.border = 'none';
hr.style.borderTop = '1px solid rgba(255,255,255,0.1)';
parent.appendChild(hr);
```

## JSON Escaping Rules for _elementor_data

The raw `_elementor_data` file is a JSON array string. When editing it in Python:

| What you want in file | In Python string |
|----------------------|-----------------|
| newline in JS (`\n`) | `\\n` |
| single quote `'` | `'` (no escaping needed in JSON) |
| double quote `"` | `\"` (must escape) |

**NEVER use `\'` in Python replacement strings** - this produces invalid JSON escape `\'`.

## Validation Step (MANDATORY)

Always validate before deploying:
```python
import json
json.loads(modified_elementor_data)  # Must not raise JSONDecodeError
```

## Diagnosis Pattern

If page shows orange color or `Unexpected token '<'` JS errors:
1. Check `_elementor_data` JSON validity: `json.loads(elem_data)`
2. Elementor error → falls back to `content.raw`
3. `content.raw` + `wpautop` → `<p>` tags injected into `<script>` blocks
4. JS parse errors cascade from `<p>` tags

## Files Involved
- `/tmp/sandbox_elem_data.json` - original valid backup
- `/tmp/fix_sandbox_v3.py` - working fix script (DOM API approach)
- `/tmp/sandbox_elem_data_fixed_v3.json` - deployed version
- WordPress page 468 (`pay-test-sandbox`) - fixed
