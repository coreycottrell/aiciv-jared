# Homepage Preloader + Footer Logo Fix — Root Cause Analysis

**Date**: 2026-03-12
**Type**: gotcha / fix
**Severity**: Critical (main site homepage broken)

---

## Problem

purebrain.ai homepage had:
1. Empty/gap space at the top (preloader never dismissed)
2. Footer logo incorrectly sized/distorted
3. Outer HTML wrapper potentially adding spacing

Multiple previous fix attempts (v4.8.5, v4.9.0) had not resolved it.

---

## Root Cause (All Three Issues)

### Issue 1: Preloader Never Dismissed (MAIN CAUSE of empty space)

The CF Pages static export strips all Artistics theme JavaScript. The theme normally calls
a JS function on `window.load` to fade out `.theme-preloader`. Without the theme JS,
the preloader div just sits visible forever — causing the gap at the top.

**Fix**: Add `id="pb-theme-preloader"` to the preloader div + insert a self-contained
JS block immediately after it that dismisses on `window.load` (with 3s safety fallback).

This is exactly what pay-test-2 already had (hence why pay-test-2 worked).

Pay-test-2 code that was missing from homepage:
```html
<div class="theme-preloader" id="pb-theme-preloader" ...>
  ...
</div>
<script>
(function() {
    function hidePreloader() {
        var el = document.getElementById('pb-theme-preloader');
        if (!el) return;
        el.style.transition = 'opacity 0.4s ease';
        el.style.opacity = '0';
        setTimeout(function() { el.style.display = 'none'; }, 420);
    }
    if (document.readyState === 'complete') {
        hidePreloader();
    } else {
        window.addEventListener('load', hidePreloader);
        setTimeout(hidePreloader, 3000);
    }
})();
</script>
```

### Issue 2: Footer Logo Fixed Width

Homepage had `.footer__logo { height: 40px; width: 240px; }` — fixed width distorts logo.
Pay-test-2 has `.footer__logo { height: 36px; width: auto; }` — auto width scales correctly.

Two CSS rules needed fixing (there are two places where `.footer__logo` is defined).

### Issue 3: Outer HTML Shell No Reset

The homepage CF Pages file has a fake outer HTML wrapper (from the WP Export process)
with no CSS in its `<head>`. Added a nuclear reset CSS block to ensure no browser-default
margins/padding from the outer wrapper contaminate the page.

---

## File Structure of Homepage CF Pages File

The homepage `exports/cf-pages-deploy/index.html` has a TRIPLE-NESTED structure:

1. **Outer shell** (lines 1-25): Fake HTML from WP Export process — `elementor-11` stubs
2. **Inner WP page-id-1502** (line ~26 onward): The pay-test-2 page content with `body.page-id-1502`
3. **Innermost page-id-11** (line ~5105): The actual homepage content with `body.home.page-id-11`

Pay-test-2's CF Pages file DOES NOT have the outer shell — it starts directly with the WP content.

---

## Diagnostic Method

Compare `grep -n` for preloader patterns between pay-test-2 and homepage:
```bash
grep -n "pb-theme-preloader\|hidePreloader" /path/to/file
```
Pay-test-2 shows both lines; homepage showed zero.

---

## Fix Applied

File: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html`

1. Added `id="pb-theme-preloader"` to preloader div
2. Inserted JS dismiss script after preloader closing `</div>`
3. Added outer shell CSS reset to `<head>` of outer wrapper
4. Changed `.footer__logo` to `height:36px; width:auto` (both occurrences)

Deployed to `purebrain-staging` project — CNAME from purebrain.ai.

---

## Key Pattern: CF Pages + Artistics Theme

**WHENEVER deploying an Artistics theme WP export to CF Pages:**
- The theme-preloader will NOT auto-dismiss (theme JS is stripped)
- MUST add `id="pb-theme-preloader"` + self-contained dismiss script
- This is the #1 cause of "empty space at top of page" on CF Pages exports

---

## Verification

```bash
curl -s "https://purebrain.ai/" | grep -c "pb-theme-preloader\|hidePreloader\|outer-shell-reset"
# Should return 7
```
