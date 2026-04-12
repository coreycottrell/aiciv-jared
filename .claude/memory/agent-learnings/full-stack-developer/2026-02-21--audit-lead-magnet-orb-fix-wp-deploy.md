# AI Partnership Audit Lead Magnet — Orb Fix WordPress Deployment

**Date**: 2026-02-21
**Agent**: full-stack-developer
**Type**: operational

---

## Task

Deploy fixed `ai-partnership-audit-lead-magnet.html` to WordPress page ID 620 at
`https://purebrain.ai/ai-partnership-audit/`.

Two bugs were pre-fixed in the local HTML file before this deployment:
1. Decorative `.orb` divs creating dark layout voids (Chrome rendering bug)
2. SVG `feTurbulence` data-URI noise texture not rendering in Chrome

## What Was Done

Deployed via WordPress REST API (`POST /wp/v2/pages/620`) using the established
CSS scoping pattern from `2026-02-21--ai-partnership-audit-interactive-deployment.md`.

### Deployment Script

`/home/jared/projects/AI-CIV/aether/tools/deploy_audit_lead_magnet_fix.py`

### CSS Transformation Pipeline

1. Extract `<style>` block from HTML file
2. Replace all `var(--*)` references with hard-coded values (WP compat)
3. Remove `:root {}` block (no longer needed after step 2)
4. Remove `*, html, body` base resets (handled with global overrides)
5. Scope all remaining rules under `#pb-audit-page` prefix
6. Prepend global overrides: `html, body { background-color: #080a12 !important; ... }`
7. Prepend WP theme chrome hiders: `.site-header, .site-footer { display: none !important; }`
8. Wrap body content in `<div id="pb-audit-page">`

### Verification

All 8 live content checks passed:
- `id="pb-audit-page"` wrapper present
- `#pb-audit-page .page > .orb` fix rule present
- `repeating-linear-gradient` noise texture present
- No unresolved `--blue:` CSS vars in style block
- `background-color: #080a12 !important` global override present
- WP theme header hidden
- Page content present (Q1 text)
- CTA link points to `purebrain.ai/#awakening`

HTTP 200 confirmed. Elementor cache cleared after deploy.

---

## Key Patterns Reused

From `2026-02-21--ai-partnership-audit-interactive-deployment.md`:
- Page ID 620, template `elementor_canvas`
- Must include `User-Agent` header — Cloudflare WAF returns 403 without it
- Always clear Elementor cache after `_elementor_data` / content updates
- Delete `/wp-json/elementor/v1/cache` endpoint works reliably

---

## CSS Scoping Rule (Canonical Pattern)

```python
# 1. Replace CSS vars with hard values first
for var, val in CSS_VARS.items():
    css = css.replace(var, val)

# 2. Remove :root block
css = re.sub(r'\s*:root\s*\{[^}]*\}', '', css)

# 3. Global overrides (outside scoped block)
globals = """
html, body { background-color: #080a12 !important; color: #e0e6f0 !important; }
.site-header, .site-footer { display: none !important; }
"""

# 4. Scope everything else
scoped = f"#pb-audit-page {selector} {{ {declarations} }}"
```

This gives sufficient specificity to beat WordPress theme overrides without
needing `!important` on every individual rule inside the scoped block.
