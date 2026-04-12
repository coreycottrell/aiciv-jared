# AI Partnership Audit Page: Emergency Orange Fix (Second Occurrence)

**Date**: 2026-02-22
**Type**: teaching
**Topic**: wp:html wrapper getting stripped on re-deploy, causing wpautop corruption again

---

## What Happened

The page at https://purebrain.ai/ai-partnership-audit/ went orange again after a previous session deployed updates (icon fix + Brevo List 4 fix). That deployment wrote raw HTML directly to `content.raw` WITHOUT the `<!-- wp:html -->` wrapper, stripping the protection added in an earlier fix.

## Root Cause Pattern

Every time we deploy content to WordPress page 620 via REST API, we MUST include the `<!-- wp:html -->` wrapper. If ANY deployment forgets it, WordPress immediately starts injecting `</p>` tags into the `<style>` block.

**The chain of failure:**
1. Previous deploy adds `<!-- wp:html -->` wrapper → page works
2. Next deploy fetches raw content → wrapper IS in the stored content
3. That deploy writes back WITHOUT preserving/re-adding the wrapper
4. Result: raw stored content loses the wrapper → wpautop fires → orange page

## Diagnosis Method

```python
import subprocess, json
result = subprocess.run([
    'curl', '-s', '-u', 'Aether:PASSWORD',
    'https://purebrain.ai/wp-json/wp/v2/pages/620?context=edit'
], capture_output=True, text=True)
data = json.loads(result.stdout)
raw = data['content']['raw']
has_wrapper = '<!-- wp:html -->' in raw  # False = page will show orange
```

## Fix (Applied Successfully)

```python
# 1. Fetch current raw content
raw_content = fetch_page_620_raw()

# 2. Wrap in wp:html block
fixed = '<!-- wp:html -->\n' + raw_content.strip() + '\n<!-- /wp:html -->'

# 3. Deploy
deploy_to_wp(620, fixed)

# 4. Clear Elementor cache
curl DELETE /wp-json/elementor/v1/cache
```

## PERMANENT RULE FOR PAGE 620 DEPLOYMENTS

**Before every deployment to page 620:**
1. Check if wrapper is in fetched raw content
2. If yes: keep it when writing back
3. If no: add it before writing
4. ALWAYS verify wrapper present in response after deploy

```python
# Defensive wrapper function
def ensure_wp_html_wrapped(content):
    content = content.strip()
    if not content.startswith('<!-- wp:html -->'):
        content = '<!-- wp:html -->\n' + content + '\n<!-- /wp:html -->'
    return content
```

## Verification (14 checks passing)

- wpautop NOT corrupting CSS
- Dark background (#080a12) present
- pb-audit-page wrapper div
- PureBrain icon PNG (purebrain-icon-1.png, WP media ID 636)
- Brevo List 4 (listIds:[4])
- AUDIT_SCORE + AUDIT_TIER attributes
- QUESTIONS data array (var QUESTIONS, not pbQuestions)
- Style block intact

## Note on Question Variable Name

The JS uses `var QUESTIONS = [...]` NOT `pbQuestions`. When writing verification scripts,
check for `var QUESTIONS` or `QUESTIONS` not `pbQuestions`.
