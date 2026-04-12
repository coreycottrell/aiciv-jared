# Subscribe Button Hover: Additional CSS Conflict Root Cause & Fix

**Date**: 2026-02-21
**Agent**: full-stack-developer
**Type**: teaching + technique
**Topic**: WordPress Additional CSS loads after plugin CSS, causing equal-specificity override of subscribe link hover styles

---

## The Root Cause

WordPress page `<head>` load order on purebrain.ai blog posts:
```
pos=20895: purebrain-blog-cta-hover  ← plugin CSS (injected via wp_head)
pos=40426: wp-custom-css             ← WordPress Additional CSS (Customizer)
```

Additional CSS **always loads after plugin CSS**. When both have `!important` rules at equal specificity, **the last one in the document wins** — that's the Additional CSS.

The conflicting Additional CSS block (lines 2069-2095):
```css
body.single-post .blog-cta-block a:hover,
body.single-post .blog-cta-block p a:hover {
    box-shadow: 0 0 0 3px #2a93c1, ... !important;  /* blue glow */
    transform: translateY(-2px) !important;
    color: #ffffff !important;
}
```
Specificity: 0,3,3 — matches BOTH the CTA button AND subscribe links.

The plugin CSS had `a[href*="subscribe"]:hover` with specificity 0,4,3 which SHOULD beat 0,3,3... BUT additional CSS also has `body.single-post .blog-cta-block p a:hover` (without `href*`) at 0,3,3. Since the subscribe link IS a `.blog-cta-block p a`, this rule applies at 0,3,3 while the plugin's subscribe-specific rule is at 0,4,3. In theory plugin wins; in practice CDN/browser cache may serve old plugin without the subscribe-specific rule (pre-v2.5.0 plugin), or the rule genuinely doesn't override on some properties.

**Belt-and-suspenders fix**: Both narrow the Additional CSS AND boost plugin specificity.

---

## Two-Part Fix

### Part 1: Narrow the Additional CSS (deploy_additional_css_fix.py)
Replace the broad `body.single-post .blog-cta-block a:hover` with `body.single-post .blog-cta-block a[href*="awakening"]:hover` — CTA button only.

OLD:
```css
body.single-post .blog-cta-block a:hover,
body.single-post .blog-cta-block p a:hover { blue glow; translateY; }
```

NEW:
```css
body.single-post .blog-cta-block a[href*="awakening"]:hover,
body.single-post .blog-cta-block p a[href*="awakening"]:hover { blue glow; translateY; }
```

This is the **correct long-term fix** — scopes the CTA button effect to links that actually contain "awakening".

### Part 2: Plugin v2.9.0 — data-pb-subscribe high-specificity hook

JS (in wp_footer, runs on DOMContentLoaded) adds `data-pb-subscribe="1"` to all subscribe links inside `.blog-cta-block`. CSS then targets this attribute:

```css
body.single-post .blog-cta-block p a[data-pb-subscribe]:hover {
    box-shadow: 0 2px 8px rgba(241, 66, 11, 0.3) !important;
    transform: none !important;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;
    color: #ffffff !important;
}
```

Specificity: `body`(0,0,1) + `.single-post`(0,1,0) + `.blog-cta-block`(0,1,0) + `p`(0,0,1) + `a`(0,0,1) + `[data-pb-subscribe]`(0,1,0) + `:hover`(0,1,0) = **0,4,3**

vs conflicting Additional CSS `body.single-post .blog-cta-block p a:hover` = **0,3,3**

Plugin wins because JS adds the data attribute after page load, but CSS still gets applied because browsers re-evaluate CSS when attributes change.

**Important**: The data attribute is added by JS *after* the page loads, so it's not in the raw HTML. But CSS attribute selectors work with dynamically set attributes — once JS sets `data-pb-subscribe="1"`, the CSS rule immediately applies.

---

## Post Content Status (verified 2026-02-21)

All 7 posts checked (IDs: 381, 316, 373, 172, 98, 565, 480):
- All subscribe links point to `https://purebrain.ai/blog/#neural-feed-subscribe?utm_...` ✓
- No inline styles on subscribe links ✓ (cleaned by v2.8.0)

---

## Files

- Plugin: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` (v2.9.0)
- Additional CSS deploy: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_additional_css_fix.py`
- Plugin deploy: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v290.py`

---

## Deployment Order (when approved)

1. Run `deploy_plugin_v290.py` — deploys plugin v2.9.0
2. Run `deploy_additional_css_fix.py` — narrows Additional CSS hover rule
3. Hard-refresh a blog post to verify (Ctrl+Shift+R to bypass browser cache)

---

## Verification Commands

```bash
python3 -c "
import urllib.request, re
req = urllib.request.Request(
    'https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/',
    headers={'Cache-Control': 'no-cache'}
)
html = urllib.request.urlopen(req).read().decode()
print('v2.9.0:', '2.9.0' in html)
print('data-pb-subscribe CSS:', '[data-pb-subscribe]' in html)
print('setAttribute JS:', 'setAttribute' in html and 'data-pb-subscribe' in html)
print('narrow CSS in additional:', 'a[href*=\"awakening\"]:hover' in html)
"
```
