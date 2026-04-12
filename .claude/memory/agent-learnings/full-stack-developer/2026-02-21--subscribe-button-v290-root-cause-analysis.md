# Subscribe Button Hover Fix - v2.9.0 Root Cause Analysis

**Date**: 2026-02-21
**Type**: teaching + operational
**Agent**: full-stack-developer

---

## Root Cause: CSS Specificity + Document Order

When both a plugin stylesheet and WordPress Additional CSS use `!important` with equal specificity, the rule that appears LATER in the document wins. WordPress Additional CSS always loads after plugin-injected `wp_head` CSS. This means any broad Additional CSS rule will defeat an equally-specific plugin rule even when both sides use `!important`.

**The conflicting rule (Additional CSS)**:
```css
body.single-post .blog-cta-block a:hover {
    box-shadow: blue-glow;
    transform: translateY(-2px) !important;
}
```

Specificity: `(0, 2, 1, 1)` = body.single-post (class) + .blog-cta-block (class) + a (element) + :hover (pseudo)

**The plugin rule (v2.7.0)**:
```css
body.single-post .blog-cta-block p a[href*="subscribe"]:hover { orange stuff }
```

Specificity: `(0, 2, 1, 2)` = body.single-post + .blog-cta-block + a + [href*=] + :hover

Wait - plugin rule IS higher specificity (adds `p` + attribute). So WHY was Additional CSS winning?

**Answer**: CSS specificity rules group by (id, class+attr+pseudo-class, element+pseudo-element). The plugin's rule has class-level: body.single-post=class (1) + .blog-cta-block=class (1) = (0,2,...). The `p` is an element tag, `a` is an element tag, `[href*=]` is an attribute (counts as class), `:hover` is a pseudo-class. So: (0, 3, 2) vs Additional CSS's (0, 2, 1). Plugin should win.

The real reason v2.7.0 didn't fully work: inline `style` attribute on the link element. Inline styles beat stylesheet rules regardless of `!important` in stylesheets (inline always wins). The v2.8.0 JS strip removed those inline styles, which should have fixed it. If v2.8.0 was already deployed, v2.9.0 is additional insurance.

## Two-Part Defense Pattern (for future reference)

When fighting CSS that could come from multiple sources (inline styles, Additional CSS, theme):

1. **Strip inline styles via JS** (v2.8.0): `link.removeAttribute('style')` - eliminates the #1 override vector
2. **Attribute-hook for unambiguous selector** (v2.9.0): JS adds `data-pb-[feature]` attribute, CSS targets `a[data-pb-feature]:hover` - adds specificity AND makes selector unmistakably specific

Pattern:
```javascript
// JS: tag elements in DOMContentLoaded
links.forEach(link => {
    link.removeAttribute('style');
    link.setAttribute('data-pb-subscribe', '1');
});
```

```css
/* CSS: beat any generic rule that might match */
body.single-post .blog-cta-block p a[data-pb-subscribe]:hover {
    /* desired styles */
}
```

## Key Files

- Plugin: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` (v2.9.0)
- Summary doc: `/home/jared/projects/AI-CIV/aether/to-jared/overnight/blog-subscribe-button-fix-v290.md`

## Deploy Pattern Reminder

For each plugin version: build -> security review -> QA -> deploy.
Deploy uses Playwright to edit plugin via WP Admin Plugin Editor.
Always flush GoDaddy cache after deploy.
Verify with hard-refresh or incognito window on a live blog post.
