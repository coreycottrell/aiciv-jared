# Blog Subscribe Button Hover Fix - Plugin v2.9.0

**Prepared by**: full-stack-developer agent
**Date**: 2026-02-21
**Status**: Code ready - awaiting security review + QA before deployment
**File**: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php`

---

## Problem

Blog post subscribe links (links containing "subscribe", "newsletter", "neural-feed" in `.blog-cta-block`) were showing a blue glow on hover instead of the intended orange gradient background.

**Expected behavior**:
- Normal state: blue text (#2a93c1), underlined
- Hover state: white text, orange gradient background (#f1420b), no transform

**Actual behavior**:
- Normal state: correct
- Hover state: blue box-shadow glow + translateY(-2px) lift (wrong)

---

## Root Cause

WordPress Additional CSS (the `wp-custom-css` inline style block in the page `<head>`) contained a broad rule introduced during the v2.1.0 CTA button fix:

```css
body.single-post .blog-cta-block a:hover {
    box-shadow: 0 0 0 3px #2a93c1, 0 0 18px rgba(42,147,193,0.55), ...;
    transform: translateY(-2px) !important;
    color: #ffffff !important;
}
```

This rule:
1. Uses 4 CSS qualifiers: `body.single-post` + `.blog-cta-block` + `a` + `:hover`
2. Loads AFTER the plugin's CSS in the HTML `<head>` (WordPress Additional CSS always comes last)
3. Therefore wins at equal specificity even when both sides use `!important`

The plugin's subscribe-specific rule (`a[href*="subscribe"]:hover`) also has 4 qualifiers, so both sides have equal specificity - and the Additional CSS wins by document order.

---

## Solution: v2.9.0 (Two-Part Fix)

### Part 1: JS adds `data-pb-subscribe` attribute to subscribe links

A new JS block runs in `wp_footer` on single posts (extending the existing v2.8.0 inline-style stripper). It queries `.blog-cta-block` for any link with "subscribe", "newsletter", or "neural-feed" in the href and sets `data-pb-subscribe="1"` on each.

```javascript
link.setAttribute('data-pb-subscribe', '1');
```

This attribute tag runs at DOMContentLoaded, before any hover interaction is possible.

### Part 2: CSS uses 5-qualifier selector to beat the Additional CSS rule

A new CSS block in the `purebrain-blog-cta-hover` style tag targets the tagged links:

```css
body.single-post .blog-cta-block p a[data-pb-subscribe]:hover,
body.single-post .blog-cta-block p a[data-pb-subscribe]:focus {
    box-shadow: 0 2px 8px rgba(241, 66, 11, 0.3) !important;
    transform: none !important;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;
    background-color: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
}
```

**Specificity count** for `body.single-post .blog-cta-block p a[data-pb-subscribe]:hover`:
- `body.single-post` = 1 class
- `.blog-cta-block` = 1 class
- `p` = 1 element
- `a[data-pb-subscribe]` = 1 element + 1 attribute = 2 qualifiers
- `:hover` = 1 pseudo-class

Total: (0, 2, 3, 1) = higher than Additional CSS's (0, 2, 1, 1) for `body.single-post .blog-cta-block a:hover`. Plugin wins regardless of document order.

---

## What Is NOT Changed

- All security hardening code (user enumeration blocking, security headers, cookie flags, proxy endpoints, rate limiting) is untouched
- The CTA button ("Start Your AI Partnership") behavior is unchanged
- The FAQ accordion is unchanged
- The blog nav menu (Home | Blog | AI Assessment) is unchanged
- The legal footer is unchanged

---

## Files Changed

| File | Change |
|------|--------|
| `tools/security/purebrain-security-plugin.php` | Version 2.8.0 -> 2.9.0, CSS section 4 added, JS `data-pb-subscribe` setter added |

---

## Verify Subscribe Link URLs

Subscribe links should point to: `https://purebrain.ai/blog/#neural-feed-subscribe`

The JS selector targets any `href` containing "subscribe", "newsletter", or "neural-feed" - this will correctly match the `#neural-feed-subscribe` anchor fragment.

---

## Deployment Instructions (for after security review + QA approval)

Deploy using the existing Playwright plugin deployment script pattern:

```bash
# Deploy the updated plugin via WordPress Plugin Editor
python3 tools/security/deploy_plugin_v290.py
```

If no deploy script exists yet for v2.9.0, the deployment follows the same pattern as v2.8.0/v2.7.0:
1. Log in to WordPress admin via Playwright
2. Navigate to Plugin Editor (purebrain-security plugin)
3. Replace plugin PHP content with the updated file
4. Click Update File
5. Flush GoDaddy cache
6. Verify live: check that subscribe link hover shows orange (not blue glow) on a blog post

---

## Team Workflow Status

- [x] full-stack-developer: Code prepared (v2.9.0 already in plugin file)
- [ ] security-engineer-tech: Review needed before deploy
- [ ] qa-engineer: Verification needed after deploy
