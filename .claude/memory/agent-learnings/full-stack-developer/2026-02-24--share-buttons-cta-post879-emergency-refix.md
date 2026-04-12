# Memory: Post 879 Emergency Re-Fix — Backslash !important + Share Pills Root Cause

**Date**: 2026-02-24
**Type**: teaching
**Topic**: Why post 879 STILL wasn't fixed after previous attempts — root cause was Python JSON serialization escaping `!important` as `\!important` in CSS

---

## What Jared Reported

Post at purebrain.ai/your-next-direct-report-wont-be-human/ still broken after previous fix:
1. Share buttons still not correct
2. Orange CTA button text still not visible

---

## Root Cause (The REAL One)

### Problem 1: Backslash-escaped !important in CSS

Previous fix deployed CSS via Python `json.dumps()` or similar. Python escaped `!important` inside the JSON payload to `\!important` — stored in WordPress as literal backslash+exclamation in the CSS.

**What was in the post CSS (invalid):**
```css
#pb-agent-manager-post .pb-inline-cta a {
  color: #ffffff \!important;    /* INVALID - not recognized as !important */
  -webkit-text-fill-color: #ffffff \!important;   /* INVALID */
}
```

**Why this happens:**
When you construct a JSON payload in Python with `!important` inside a string, and the serializer is doing something weird (or the content went through an extra JSON encode/decode cycle), `!` can get backslash-escaped. The CSS stored in WP then renders as `\!important` in the browser — which browsers silently ignore, meaning those CSS rules do NOTHING.

**Fix:** Replace all `\!important` with `!important` in the content before deploying.

### Problem 2: Diagnostic Difficulty

The backslash only shows up in the RAW content (via `context=edit` API). In normal rendered HTML, the `<style>` block gets HTML-entity-encoded in some places but still shows `\!important` literally. Easy to miss unless you explicitly grep for it.

---

## Fixes Applied

### Fix 1: Remove all backslash-escaped !important
```python
# Pattern to find
'\\!important'   # literal backslash + !important

# Replace with
'!important'
```

### Fix 2: Add html body high-specificity override for share buttons

The plugin CSS (`body.single-post .pt-social-share a:hover { background: #ffffff; color: #2a93c1 }`) could compete with post CSS. Added double-layer override:

```css
/* Original (ID specificity = 1,1,1) */
#pb-agent-manager-post .pt-social-share a { ... }

/* Added (html+body+ID = 1,1,3 — wins over plugin's 0,2,1) */
html body #pb-agent-manager-post .pt-social-share a {
  background: rgba(255,255,255,0.06) !important;
  color: rgba(255,255,255,0.85) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 6px !important;
  width: auto !important;
  height: auto !important;
  padding: 8px 14px !important;
}
```

### Fix 3: Added inline style to the footer share div itself
```html
<div class="pt-social-share" style="display:flex;align-items:center;gap:10px;padding:20px 0;margin:20px 0;border-top:2px solid rgba(42,147,193,0.3);flex-wrap:wrap;">
```

---

## Deployment Method That WORKS

Use `--data @file.json` with curl to avoid shell escaping issues:

```bash
# Step 1: Write payload to file (Python)
payload = json.dumps({"content": content})
with open('/tmp/payload.json', 'w') as f:
    f.write(payload)

# Step 2: Deploy with curl from file
curl -s -X POST \
  -u "Aether:APP_PASSWORD" \
  -H "Content-Type: application/json" \
  --data @/tmp/payload.json \
  "https://purebrain.ai/wp-json/wp/v2/posts/879"
```

**NEVER use heredoc with `<< 'PAYLOAD'`** for HTML content — it works for simple strings but can cause issues with complex HTML content.

---

## Verification After Fix

8/8 checks passed on live page:
1. No backslash !important in CSS: PASS
2. html body high-specificity share override: PASS
3. Pill background rgba(255,255,255,0.06): PASS
4. Share hover orange #f1420b: PASS
5. CTA button inline white text: PASS
6. Inline CTA white text present: PASS
7. Footer share div inline style: PASS
8. pb-inline-cta CSS correct: PASS

Cache headers showed `cf-cache-status: MISS` — live content, no cache issue.

---

## Key Pattern: Always Grep for Backslash in CSS After Deploy

After every REST API post deploy, run this check:
```bash
# In the raw API response
curl ... "?context=edit" | python3 -c "
import json, sys
raw = json.load(sys.stdin)['content']['raw']
backslash_count = raw.count(chr(92) + '!important')
print('Backslash !important count:', backslash_count, '(should be 0)')
"
```

---

## Affected Post

| Site | Post ID | Slug |
|------|---------|------|
| purebrain.ai | 879 | your-next-direct-report-wont-be-human |
