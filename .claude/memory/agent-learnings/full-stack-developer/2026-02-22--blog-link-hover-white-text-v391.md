# Memory: Blog In-Text Link Hover Fix — v3.9.1

**Date**: 2026-02-22
**Type**: teaching
**Topic**: Blog in-content link hover: orange background + white text (not invisible orange-on-orange)

---

## Problem Solved

In-text links in blog posts on purebrain.ai and jareddsanborn.com were orange (#f1420b) by default.
On hover, a broad CSS rule added an orange background — making the text invisible (orange text on orange background).

**Root cause**: `body.single-post a { color: #f1420b }` + some hover rule adding `background-color: #f1420b` = invisible.

**Fix**: On hover, keep orange background but change text to WHITE (#ffffff).

---

## CSS Solution

```css
/* Transition on default state */
body.single-post .entry-content a:not(.blog-cta-button):not([rel="tag"]),
body.single-post .elementor-widget-theme-post-content a:not(.blog-cta-button):not([rel="tag"]) {
    transition: background-color 0.2s ease, color 0.2s ease !important;
}

/* Hover: orange background, WHITE text */
body.single-post .entry-content a:not(.blog-cta-button):not([rel="tag"]):hover,
body.single-post .elementor-widget-theme-post-content a:not(.blog-cta-button):not([rel="tag"]):hover {
    background-color: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
    border-radius: 3px !important;
    padding: 1px 4px !important;
}
```

**Selector strategy**:
- `.entry-content` = standard WordPress post content
- `.elementor-widget-theme-post-content` = Elementor Pro theme post content widget
- `:not(.blog-cta-button)` = excludes CTA button
- `:not([rel="tag"])` = excludes tag pills (styled by v3.9.0)
- `.blog-cta-block` links are protected by their own higher-specificity plugin rules (v2.5.0-v2.9.0) that will override this generic rule

---

## Deployment Approach

**Two-layer deployment**:

1. **REST API injection** (immediate, works even when GoDaddy CAPTCHA blocks wp-admin):
   - Prepend `<style id="pb-link-hover-v391">...</style>` to every post's content
   - Script: `tools/security/deploy_link_hover_v391.py`
   - Uses `PUREBRAIN_WP_APP_PASSWORD` and `WORDPRESS_APP_PASSWORD` from .env
   - WP Application Passwords work for REST API Basic Auth even when form login is blocked

2. **Plugin update** (for future posts, permanent):
   - Added to plugin as `purebrain-security-plugin.php v3.9.1`
   - Section: `j3) BLOG IN-TEXT LINK HOVER FIX`
   - Style ID in plugin: `purebrain-link-hover-fix`
   - Plugin file: `tools/security/purebrain-security/purebrain-security-plugin.php`

---

## Results

| Site | Posts Updated | Verification |
|------|--------------|-------------|
| purebrain.ai | 9/9 | PASS (4/4 checks per post) |
| jareddsanborn.com | 10/10 | PASS (4/4 checks per post) |

---

## Key Lessons

### `:not()` Complex Selector Limitation
- CSS3 `:not()` only accepts SIMPLE selectors (single class, attribute, element, etc.)
- `:not(.blog-cta-block a)` is INVALID (descendant combinator inside `:not()`)
- For excluding descendants: add a higher-specificity reset rule after, OR accept that the
  existing plugin rules for those elements already have higher specificity and will win

### Specificity Battle for `.blog-cta-block` Links
- My new rule: specificity ~0,2,1,0 (body.single-post + entry-content + a)
- Existing CTA button rule: `body.single-post .blog-cta-block p a[href*="awakening"]:hover` = 0,4,1,1
- Existing newsletter rule: `body.single-post .blog-cta-block p a[href*="subscribe"]:hover` = 0,4,1,1
- Since all use `!important`, higher specificity wins → existing rules correctly override my new rule
- No reset rule needed

### Raw Content vs Rendered Content
- WordPress REST API `GET /wp-json/wp/v2/posts?per_page=100` returns posts
- Some posts show `content.raw = ""` (empty) but `content.rendered` has content
- Use rendered content as fallback for PATCH — WP will process it correctly
- Script handles this: tries raw first, falls back to rendered

### CDN Cache Note
- Cloudflare caches page HTML for 31 days
- Style block injected into DB immediately but cached pages may serve old HTML
- Hard refresh (Cmd+Shift+R) or incognito to verify live
- Live verification confirmed style block appears in served HTML (CDN picked it up)

---

## Files Modified

1. `tools/security/purebrain-security/purebrain-security-plugin.php` — v3.9.0 → v3.9.1, added j3 section
2. `tools/security/deploy_link_hover_v391.py` — new deployment script
3. All 9 purebrain.ai posts — `<style id="pb-link-hover-v391">` prepended
4. All 10 jareddsanborn.com posts — `<style id="pb-link-hover-v391">` prepended

---

## Blog Footer Template Assessment

`tools/security/deploy_link_hover_v391.py` assessed — NO CHANGES NEEDED:
- `.pt-social-share a` links: scoped to their own class, not in `.entry-content` → unaffected
- CTA button `<a href="...awakening...">`: inside `.blog-cta-block`, protected by existing higher-specificity plugin CSS
- Newsletter link `<a href="...blog...">`: inside `.blog-cta-block`, protected by existing higher-specificity plugin CSS
- Template is correct as-is
