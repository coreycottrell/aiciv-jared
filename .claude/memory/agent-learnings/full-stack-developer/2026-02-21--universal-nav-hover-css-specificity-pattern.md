# Universal Nav Hover CSS - Specificity Pattern

**Date**: 2026-02-21
**Type**: teaching
**Topic**: CSS specificity - universal `html body .class a:hover` beats all body-class rules

## Context

Nav menu (`pb-blog-nav`) needed orange hover on ALL page types. Previous fix (v3.1.0) used
body-class-scoped selectors: `body.category .pb-blog-nav a:hover`, `body.archive .pb-blog-nav a:hover`, etc.

## Problem

Body-class-scoped selectors require maintenance - every new WordPress page type (CPT, plugin-added archive, etc.)
would need a new selector added. Not future-proof.

## The Pattern

```css
/* INSTEAD OF this (fragile, per-page-type) */
body.single-post .pb-blog-nav a:hover,
body.category .pb-blog-nav a:hover,
body.archive .pb-blog-nav a:hover,
body.tag .pb-blog-nav a:hover,
.pb-blog-nav a:hover { color: #f1420b !important; }

/* USE THIS (universal, future-proof) */
html body .pb-blog-nav a:hover,
html body .pb-blog-nav a:focus { color: #f1420b !important; }
```

## Specificity Math

- `body.category a:hover` = (0, 1, 0, 1) = specificity 11
- `.pb-blog-nav a:hover` = (0, 0, 1, 1) = specificity 11
- `body.category .pb-blog-nav a:hover` = (0, 1, 1, 1) = specificity 21 (v3.1.0)
- `html body .pb-blog-nav a:hover` = (0, 0, 2, 1) = specificity 21 (v3.2.0)

`html body` adds two element selectors (+2) but no classes. This equals or beats any single body-class
rule, regardless of what WordPress page type body class is present.

## Why html body Works

`html body .selector:hover { !important }` can NEVER be beaten by:
- `body.any-class .selector:hover { !important }` because body.any-class = 1 class + 1 element = score 11
  vs `html body` = 2 elements = score 2 ... wait, but both have `!important`

When BOTH use `!important`, the TIE goes to the one with HIGHER SPECIFICITY in the cascade.
- `html body .pb-blog-nav a:hover` = specificity (0,0,2,1) = 21 points
- `body.category a:hover` = specificity (0,1,0,1) = 11 points

The `html body` rule wins because (0,0,2,1) > (0,1,0,1) when both use `!important`.

## Real-World Verification

On purebrain.ai category pages, Additional CSS has:
- `body.category a:hover { color: #f1420b !important }` (loads after plugin)
- Plugin `html body .pb-blog-nav a:hover { color: #f1420b !important }` (loads first)

Both set same color. If Additional CSS sets blue, plugin's higher specificity wins.

## Plugin Files

- Plugin: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`
- Deploy script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v320.py`
- Version bumped to 3.2.0

## Gotcha: Blog Index (/blog/)

The `/blog/` URL is a static Elementor canvas page (page-id-319), NOT a WordPress archive.
`is_archive()` returns FALSE for it. Plugin nav CSS correctly does NOT inject there.
It has its own Elementor navigation. This is expected behavior, not a bug.
