# Memory: Blog Post Missing Header/Nav — elementor_canvas Template Bug (Post 879)

**Date**: 2026-02-24
**Type**: teaching
**Agent**: full-stack-developer

## Problem

Post 879 (`/your-next-direct-report-wont-be-human/`) was missing:
- Site header / nav menu
- Blog banner
- Everything above the post content

Jared reported: "no menu, banner and everything above the actual words are not there."

## Root Cause

The post had `template: "elementor_canvas"` set via WordPress REST API. This caused WordPress to use the Elementor Canvas layout, which strips ALL standard theme wrappers including the header, footer, and nav menu.

**Diagnosis check output:**
- `"template": "elementor_canvas"` returned by REST API GET
- Body class contained `post-template-elementor_canvas` and `elementor-template-canvas`
- `post-template-default` was absent

## Fix (1-line REST API call)

```bash
curl -s -X POST \
  -u "Aether:APP_PASSWORD" \
  -H "Content-Type: application/json" \
  "https://purebrain.ai/wp-json/wp/v2/posts/879" \
  -d '{"template": ""}'
```

Then clear Elementor cache:
```bash
curl -s -X DELETE \
  -u "Aether:APP_PASSWORD" \
  "https://purebrain.ai/wp-json/elementor/v1/cache"
```

## Verification Pattern

After fix, verify these body classes:
- `post-template-default` → SHOULD be present (correct)
- `elementor-template-canvas` → SHOULD NOT be present (bad)
- `post-template-elementor_canvas` → SHOULD NOT be present (bad)

Also confirm:
- `<header` tag present
- `nav-menu` class present
- `post-entry` class present

## Site Comparison

| Site | Post ID | Template Before Fix | Template After Fix | Needed Fix? |
|------|---------|--------------------|--------------------|-------------|
| purebrain.ai | 879 | `elementor_canvas` | `""` | YES |
| jareddsanborn.com | 1195 | `""` | `""` | NO (already correct) |

## Pattern: This Is Recurring

This is the SAME bug as Post 696 (2026-02-23). Both posts were set to `elementor_canvas` template likely during a bulk REST API update that accidentally included `template` in the payload.

## Prevention Rule (PERMANENT — Reinforced)

**NEVER include `template` or `page_template` in bulk REST API updates to blog posts.**

Only `elementor_canvas` template is legitimate for standalone landing pages, NOT blog posts.

When any blog post has broken layout (missing header, nav, banner), check template field FIRST:
```bash
curl -s -u "Aether:APP_PASSWORD" \
  "https://purebrain.ai/wp-json/wp/v2/posts/POST_ID?_fields=id,title,template"
```

If `"template": "elementor_canvas"` → fix with `{"template": ""}`.

## Time to Fix

Diagnosis: < 1 minute (memory from Post 696 incident)
Fix execution: < 1 minute
Total: ~2 minutes
