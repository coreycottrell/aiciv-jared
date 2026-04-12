# CF Pages: WordPress Theme Preloader Stuck Spinner

**Date**: 2026-03-11
**Type**: gotcha
**Topic**: Cloudflare Pages static export — Artistics theme preloader never dismisses

---

## Root Cause

The Artistics WordPress theme renders a `div.theme-preloader` at the top of `<body>`.
On WordPress, the theme's `main.js` bundle runs on `window.load` and hides the preloader via jQuery fadeOut.

When a WordPress page is exported as a standalone static HTML file for Cloudflare Pages:
- The page carries `div.theme-preloader` in its HTML
- Only jQuery is included as an external script (`purebrain.ai/wp-includes/js/jquery/...`)
- The Artistics theme's own JS bundle (which dismisses the preloader) is NOT included
- Result: spinner shows indefinitely — page appears stuck

## Symptom

Page at `https://purebrain-staging.pages.dev/pay-test-2/` shows the blue/orange vortex loading animation and never progresses to content.

## Fix Pattern

Inject a small inline `<script>` immediately after the `div.theme-preloader` closing tag:

```html
<div class="theme-preloader" id="pb-theme-preloader">
    <!-- ... spinner content ... -->
</div>
<script>
// CF Pages fix: Artistics theme JS is not bundled in static export.
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
        // Safety fallback: hide after 3s if load event never fires
        setTimeout(hidePreloader, 3000);
    }
})();
</script>
```

Key points:
- Add `id="pb-theme-preloader"` to the div for reliable targeting
- Three dismissal paths: already-complete, window.load, 3s timeout
- 0.4s opacity fade matches Artistics theme behaviour

## Files Fixed

- `exports/cf-pages-deploy/pay-test-2/index.html`
- `exports/cf-pages-deploy/pay-test-sandbox-3/index.html`

## Prevention

Any time a WordPress page using the Artistics theme is exported to CF Pages static HTML,
apply this fix immediately after the preloader div. The preloader div can be identified by:
```
<div class="theme-preloader">
```
This appears near the top of `<body>`, right before `div#magic-cursor`.
