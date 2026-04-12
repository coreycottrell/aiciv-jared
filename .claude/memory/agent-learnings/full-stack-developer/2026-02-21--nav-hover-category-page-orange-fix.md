# Nav Menu Hover Color Fix - Plugin v3.1.0

**Date**: 2026-02-21
**Type**: teaching + gotcha
**Agent**: full-stack-developer
**Topic**: Nav hover showed different color on blog posts vs category pages

---

## The Bug

Nav menu (Home | Blog | AI Assessment) hover effect worked differently on two page types:
- **Blog posts**: Hover turned text orange (#f1420b) — correct
- **Category pages** (`/category/for-teams/`, `/category/for-individuals/`): Hover turned text blue (#2a93c1) — wrong

## Root Cause: CSS Specificity + Accidental Override

The plugin's `.pb-blog-nav a:hover` CSS was set to `color: #2a93c1 !important` (blue).

On blog posts, WordPress Additional CSS contained:
```css
body.single-post a:hover {
    color: #f1420b !important;
}
```

Since Additional CSS loads AFTER plugin CSS in `<head>`, and this rule has equal/higher specificity, it **accidentally overrode** the plugin's blue hover to orange on blog posts only.

Category pages (`body.category`) had NO such broad `a:hover` rule in Additional CSS. So the plugin's own blue hover was the final word — showing blue.

**This is the same CSS-order problem documented in v2.8/v2.9 for subscribe links, but in reverse** — the accidental override was HELPFUL on posts but absent on categories.

## The Fix (v3.1.0)

Changed the plugin's own hover rule to use orange directly:
```css
body.single-post .pb-blog-nav a:hover,
body.single-post .pb-blog-nav a:focus,
body.category .pb-blog-nav a:hover,
body.category .pb-blog-nav a:focus,
body.archive .pb-blog-nav a:hover,
body.archive .pb-blog-nav a:focus,
body.tag .pb-blog-nav a:hover,
body.tag .pb-blog-nav a:focus,
.pb-blog-nav a:hover,
.pb-blog-nav a:focus {
    color: #f1420b !important;
    text-decoration: none !important;
    background: none !important;
    box-shadow: none !important;
    transform: none !important;
}
```

Key decisions:
1. **Use orange directly** — don't rely on broad Additional CSS accidentally overriding
2. **Add body-class-scoped selectors** — higher specificity prevents future overrides
3. **Cover all page types** — single-post, category, archive, tag + fallback

## Deployment

- Plugin updated to v3.1.0
- Deploy script: `tools/security/deploy_plugin_v310.py`
- All 20 validation checks passed
- All 15 live verification checks passed on blog post + both category pages
- GoDaddy cache flushed

## Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` (v3.1.0)
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php` (synced)
- `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v310.py` (new deploy script)

## Key Learning: "Accidental" Fixes Can Hide Real Bugs

When diagnosing CSS hover issues across page types, check:
1. Are there broad `body.[page-class] a:hover` rules in Additional CSS?
2. If yes, they may be accidentally fixing something on one page type but not others
3. The plugin should own its own CSS behavior explicitly — never rely on broad rules as a side effect

## Investigation Steps That Led to Root Cause

1. Read live HTML from both page types via urllib.request
2. Extracted the `wp-custom-css` style block to see all Additional CSS rules
3. Searched for all `a:hover` rules — found `body.single-post a:hover { color: #f1420b }` but no `body.category a:hover`
4. Compared plugin's own `.pb-blog-nav a:hover { color: #2a93c1 }` — confirmed the mismatch
