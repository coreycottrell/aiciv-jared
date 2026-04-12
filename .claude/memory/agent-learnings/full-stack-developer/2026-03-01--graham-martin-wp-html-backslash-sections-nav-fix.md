# Graham Martin Mini-Site: wp:html Backslash Bug + Sections Nav Fix

**Date**: 2026-03-01
**Type**: gotcha + technique
**Pages**: WP 1150, 1153, 1154, 1155, 1156

---

## Bug 1: wp:html Comment Rendering as Orange Text

### Root Cause
When content was deployed via WP REST API, the `<!-- wp:html -->` markers were stored with a backslash escape as `<\!-- wp:html -->`. WordPress Gutenberg requires the exact HTML comment syntax `<!-- wp:html -->` — the backslash breaks it, so WordPress treats it as literal text content and renders it visibly (orange because the site has orange as link/text color).

### What it looked like in storage
```
<\!-- wp:html --><!DOCTYPE html>...<!-- /wp:html -->
```
vs what it should be:
```
<!-- wp:html --><!DOCTYPE html>...<!-- /wp:html -->
```

### Fix
Re-deploy all pages using Python's `json.dumps()` for proper JSON encoding, wrapping HTML content with correct `<!-- wp:html -->` markers. The `!` in HTML comments must NOT be escaped.

### Detection
```bash
curl -s -u "Aether:${PUREBRAIN_WP_APP_PASSWORD}" "https://purebrain.ai/wp-json/wp/v2/pages/{ID}?context=edit" | python3 -c "
import json,sys; d=json.load(sys.stdin); raw=d['content']['raw']; print(repr(raw[:30]))
"
# Bad:  '<\\!-- wp:html -->'
# Good: '<!-- wp:html -->'
```

---

## Bug 2: Sections Nav (#gm-mini-nav) Visible on Page Load

### Root Cause
The `#gm-mini-nav` (fixed second nav bar with site section pill links) was always visible on desktop, appearing between the main nav and hero. This pushed the visual focus away from the hero headline and put navigation as the first thing users see.

### Fix
Added CSS to make `#gm-mini-nav` start hidden (opacity: 0, transform: translateY(-100%)), then added a scroll listener that adds `.gm-nav-visible` class once the user scrolls past the hero section (hero's bottom edge passes 80px from viewport top).

```css
#gm-mini-nav {
  /* existing styles... */
  opacity: 0;
  transform: translateY(-100%);
  transition: opacity 0.35s ease, transform 0.35s ease;
  pointer-events: none;
}
#gm-mini-nav.gm-nav-visible {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
```

```js
(function(){
  var miniNav = document.getElementById('gm-mini-nav');
  var hero = document.getElementById('gm-hero');
  if (!miniNav || !hero) return;
  function checkScroll() {
    var heroBottom = hero.getBoundingClientRect().bottom;
    if (heroBottom <= 80) {
      miniNav.classList.add('gm-nav-visible');
    } else {
      miniNav.classList.remove('gm-nav-visible');
    }
  }
  window.addEventListener('scroll', checkScroll, { passive: true });
  checkScroll();
})();
```

### Pattern
This scroll-reveal nav pattern is reusable for any site where a secondary nav bar should only appear after the hero. The `80px` threshold gives enough space for the main nav to still be visible when the mini-nav slides in.

---

## Files Modified
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-investor-page.html`
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-casino-ai.html`
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-chairman-intelligence.html`
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-virya-intelligence.html`
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-responsible-gambling.html`

## Deployment Result
All 5 pages: HTTP 200. Both bugs fixed.
