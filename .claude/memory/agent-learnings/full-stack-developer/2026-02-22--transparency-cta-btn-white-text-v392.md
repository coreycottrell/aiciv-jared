# Memory: Transparency Section CTA Button White Text Fix — v3.9.2

**Date**: 2026-02-22
**Type**: teaching
**Topic**: Transparency CTA button invisible text (orange-on-orange) — root cause + fix pattern

---

## Problem

`.aether-transparency__cta-btn` text was invisible on blog posts on both purebrain.ai and jareddsanborn.com.

The button has `background: #f1420b` (orange). The text was rendering as orange text on orange background = invisible.

---

## Root Cause

The plugin's transparency CSS block (output via `wp_head` at priority 30) has:
```css
.aether-transparency__cta-btn {
    color: #ffffff !important;
}
```

But the Additional CSS (loaded via `wp_head` enqueue — typically priority ~8 but included via `wp_head` output) contains a broad rule:
```css
body.single-post a { color: #f1420b }
```

**CSS load order**: When both rules have `!important`, the LAST rule loaded wins (specificity tie broken by source order). Additional CSS loads AFTER the plugin's transparency CSS block at priority 30. The broad `body.single-post a` rule is less specific than `.aether-transparency__cta-btn` (0,1,0 vs 0,1,0) but load order favors Additional CSS — hence orange wins.

**The same problem occurred for in-text links** — solved in v3.9.1 with a `wp_head` priority 99 hook. The transparency CTA button was NOT excluded from that fix (used `:not(.blog-cta-button)` which only excludes `.blog-cta-button` class, not `.aether-transparency__cta-btn`).

---

## Fix: Two-Layer Approach

### Layer 1: REST API content injection (immediate)

Style block prepended to every post's content:
```html
<style id="pb-transparency-cta-v394">
body.single-post .aether-transparency .aether-transparency__cta-btn,
body.single-post .aether-transparency__cta .aether-transparency__cta-btn,
html body.single-post .aether-transparency__cta-btn,
.aether-transparency__cta-btn,
.aether-transparency__cta-btn a {
    color: #ffffff !important;
    text-decoration: none !important;
}
/* hover state too */
</style>
```

Deployed via: `tools/security/deploy_transparency_cta_fix_v392.py`

### Layer 2: Plugin source fix (permanent)

New `wp_head` hook at **priority 99** (fires AFTER everything in `<head>`) added to plugin:
```php
add_action( 'wp_head', function () {
    if ( ! is_single() ) { return; }
    // <style id="purebrain-transparency-cta-v392"> with max-specificity selectors
}, 99 );
```

Plugin bumped from v3.9.1 → v3.9.2.

---

## Results

| Site | Posts Updated | Live Verified |
|------|-------------|--------------|
| purebrain.ai | 9/9 | 2/2 checks PASS |
| jareddsanborn.com | 10/10 | 2/2 checks PASS |

---

## Key Lessons

### CSS Load Order Trap
- Plugin `wp_head` hooks at priority 30 can be overridden by WordPress Additional CSS
- **Fix**: Use `wp_head` at priority 99 for CSS that must win over Additional CSS
- Or: inject CSS directly into post content (loads inside body, always wins over head styles)

### Style ID Naming Convention
- Plugin head style: `purebrain-transparency-cta-v392` (plugin version number)
- Post content style: `pb-transparency-cta-v394` (content version, distinct from plugin)
- Keep distinct so idempotency checks don't confuse them

### The REST API Content Injection Pattern
- Broad pattern in this codebase: when wp-admin CAPTCHA blocks plugin deployment, inject fixes via REST API into post content
- WP Application Passwords work for REST API Basic Auth even when form login is blocked
- Template script: `tools/security/deploy_link_hover_v391.py`
- Always: idempotency check (skip if style ID already present), raw content fallback to rendered, 0.5s delay between posts

### Specificity for `.aether-transparency__cta-btn`
- The button is an `<a>` element
- `body.single-post a` = (0,1,0,1) specificity
- `.aether-transparency__cta-btn` = (0,1,0,0) specificity — LESS specific than the broad rule
- Need compound selectors: `body.single-post .aether-transparency .aether-transparency__cta-btn` = (0,3,0,1) — wins

---

## Files Modified

1. `tools/security/purebrain-security/purebrain-security-plugin.php` — v3.9.1 → v3.9.2
   - Added j4 section (transparency CTA white text hook at priority 99)
   - Updated version, description, changelog
2. `tools/security/deploy_transparency_cta_fix_v392.py` — new deployment script
3. All 9 purebrain.ai posts — `<style id="pb-transparency-cta-v394">` prepended
4. All 10 jareddsanborn.com posts — `<style id="pb-transparency-cta-v394">` prepended
