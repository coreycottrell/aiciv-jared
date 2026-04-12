---
type: technique
topic: PureBrain CSS Scoping Fix - Homepage vs Blog isolation
date: 2026-02-18
agent: browser-vision-tester
tags: [css, purebrain, scoping, homepage, blog, social-sharing, captcha]
confidence: high
---

# PureBrain CSS Scoping Fix - Three Critical Issues

## Context

Three CSS issues on purebrain.ai caused by unscoped blog CSS bleeding into homepage:
1. Social sharing icons hidden by aggressive `display: none !important` rules
2. Homepage CTA arrow not orange (was white from previous fix)
3. Orange square artifact in top-left corner from body background

## Root Causes

### Issue 1: Social Sharing Hidden
Lines 39-72 of the CSS had `display: none !important` on ALL social sharing selectors globally.
The social styling block at lines 1451-1547 tried to re-show them but couldn't override the earlier block.
**Fix**: Remove the entire `display: none` block and replace with `body.single-post` scoped BLUE styling.

### Issue 2: Body Background Orange
The `body` element on the homepage has `background-color: rgb(241, 66, 11)` (orange).
This is the Artistics theme default. Previous CSS had `[class*="magic"]` with `background-color: #f1420b !important` which is unscoped and can affect any element with "magic" in its class name.
**Fix**: Scope ALL `[class*="magic"]` and `[class*="floating"]` rules to `body.single-post` and `body.blog`.

### Issue 3: CTA Arrow
Previous fix set arrow to white (stroke: #ffffff). Jared wants it orange.
Arrow SVG uses `stroke="currentColor"` and needs both `stroke` and `color` overrides.
**Fix**: `.btn__icon--arrow` with `stroke: #f1420b !important`.

## Key CSS Scoping Rules

ALL blog-specific CSS must use one of these prefixes:
- `body.single-post` - individual blog post pages
- `body.blog` - blog listing page
- `body.page-id-95` - specific blog page by ID

NEVER use unscoped selectors like:
- `[class*="magic"]` - matches homepage elements
- `.elementor-section::before` - global override
- `html, body { overflow-x: hidden }` - affects all pages
- `[class*="subscribe"]` - matches homepage elements
- `[class*="menu"]` - hides homepage navigation!

## WordPress Login CAPTCHA Challenge

The purebrain.ai WordPress login has a `wpsec_captcha` text CAPTCHA with heavily distorted characters.
Multiple failed attempts trigger GoDaddy's reCAPTCHA "I'm not a robot" block.

**What works**: REST API with Application Password (for posts, media, settings)
**What doesn't work**: REST API for Custom CSS (endpoint not exposed)
**What's blocked**: Playwright login (CAPTCHA + rate limiting)

**Recommendation**: Disable or whitelist the CAPTCHA for the Aether user, or expose Custom CSS via REST API.

## Files

- Fixed CSS: `/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css`
- Deployment scripts: `tools/deploy_css_single_session.py`, `tools/deploy_css_fix_v2.py`
- Screenshots: `/tmp/purebrain-css-fix-2026-02-18/`

## Manual Deployment Steps

1. Login to purebrain.ai/wp-admin (solve CAPTCHA manually)
2. Go to Appearance > Customize > Additional CSS
3. Select ALL existing CSS (Ctrl+A)
4. Delete it
5. Paste contents of `exports/purebrain-complete-styling.css`
6. Click Publish

## When to Apply

- Any time blog CSS is modified, ensure it's scoped to `body.blog` or `body.single-post`
- Never use `[class*="keyword"]` selectors without body-class scoping
- Test homepage AFTER deploying blog CSS changes

---

**Tags**: css, wordpress, purebrain, scoping, social-sharing, captcha, homepage
