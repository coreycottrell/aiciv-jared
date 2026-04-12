# Bash wp:html Backslash Escape Bug

**Date**: 2026-03-01
**Severity**: CRITICAL — breaks page rendering
**Type**: deployment gotcha

## Problem

When deploying HTML to WordPress via bash + curl, the `<!-- wp:html -->` block marker gets mangled to `<\!-- wp:html -->` because bash interprets `!` as history expansion and escapes it with a backslash.

WordPress then renders `<\!-- wp:html -->` as **visible text** on the page instead of treating it as an HTML comment.

## Root Cause

Bash history expansion (`!` character) inside double-quoted strings. Even with `set +H`, some shell environments still escape `!` in heredocs and variable expansions.

## Solution

**ALWAYS deploy WordPress content via Python**, not bash + curl:

```python
import json, requests
content = '<!-- wp:html -->' + html + '<!-- /wp:html -->'
payload = json.dumps({"content": {"raw": content}})
r = requests.post(f'{base}/{page_id}', auth=auth,
    headers={'Content-Type': 'application/json'}, data=payload)
```

Python's string handling doesn't have history expansion, so `!` passes through cleanly.

## Rule

**NEVER use bash/curl for deploying wp:html-wrapped content to WordPress. Use Python requests.**
