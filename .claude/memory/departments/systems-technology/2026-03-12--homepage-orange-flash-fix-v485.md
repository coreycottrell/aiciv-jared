# Homepage Orange Flash Fix - v4.8.5

**Date**: 2026-03-12
**Type**: gotcha + fix
**Agent**: dept-systems-technology (ST#)

## Problem

purebrain.ai homepage showed a brief orange (#f1420b) flash on first load/refresh before
the real dark page rendered. The flash showed the orange body background, a hexagonal 3D
geometric element, and a partial arc in the top-left corner.

## Root Cause (Cascade Timing Bug)

**3-step failure sequence:**

1. The Artistics theme adds `tt-magic-cursor` class to `<body>` at SERVER RENDER TIME
   (it's in the static HTML, not added by JS)

2. The `wp-custom-css` Additional CSS block (line ~521 in the rendered page) contains:
   ```css
   [class*="magic"] { color: #f1420b !important; background-color: #f1420b !important; }
   ```
   This selector matches `body.tt-magic-cursor` and immediately paints body orange as
   the browser encounters this CSS rule.

3. The `pb-magic-cursor-body-override` fix (correct selectors, correct CSS) was in
   `wp_footer` — line 13023 in the rendered page. Browser had already painted orange
   by the time this fix loaded. Flash window = ~200-500ms.

**The `pb-magic-cursor-body-fix` style block (line 61, in `<head>`) existed but contained
ONLY COMMENTS — no actual CSS. It was a placeholder that was never filled in.**

## Fix (v4.8.5)

Added actual CSS to the `pb-magic-cursor-body-fix` style block at line 61 (in `<head>`,
BEFORE the Additional CSS block at line 521).

Key CSS design: use `html body.tt-magic-cursor` (specificity 0,0,2,1) which beats
`[class*="magic"]` (specificity 0,0,1,0) regardless of load order.

```css
html body.tt-magic-cursor {
    background-color: #080a12 !important;
}
html body.home.tt-magic-cursor,
html body.page-id-11.tt-magic-cursor {
    background: transparent !important;  /* video shows through */
}
```

## Files Changed

- `exports/cf-pages-deploy/index.html` — pb-magic-cursor-body-fix style block now has CSS
- `exports/cf-pages-deploy/pure-brain-agentic-ai-partner/index.html` — same fix
- `tools/security/purebrain-security-plugin.php` — v4.8.5, new `wp_head priority 2` hook

## Deployment

- CF Pages deployed via wrangler CLI (not GitHub push — git history has 2GB+ objects
  from old cache/venv commits that block GitHub push)
- Command: `CLOUDFLARE_API_TOKEN=... npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain`
- Verified live at https://purebrain.ai/ — v4.8.5 confirmed in response

## Key Lessons

1. **Static CF Pages HTML**: purebrain.ai is served from a static HTML snapshot.
   Plugin changes to live WordPress do NOT automatically update the CF Pages files.
   Both must be updated: the plugin AND the static HTML.

2. **The `pb-magic-cursor-body-fix` block was always a comment-only placeholder**.
   Future sessions: if you see this block in CF Pages HTML with only comments,
   that means the actual CSS fix needs to be added here.

3. **CSS specificity wins over load order** when using `html body.element` prefix:
   - `html body.tt-magic-cursor` = (0,0,2,1) specificity
   - `[class*="magic"]` = (0,0,1,0) specificity
   - Higher specificity wins regardless of which CSS block loads first

4. **Flash prevention pattern**: If a body class (added server-side) triggers an unwanted
   CSS rule, the override MUST be in `<head>` before the offending stylesheet, not in
   `<footer>`. Specificity alone is not enough if both rules are in `<footer>`.

5. **Git push has 2GB limit issue**: The git history contains massive commits (venv/cache).
   Use `wrangler pages deploy` for CF Pages deployments — it bypasses git entirely.

## Not Fixed (In Scope of This Session)

- Gap at top / truncated logo at bottom: Jared mentioned these as possible related issues.
  The screenshot showed only the orange flash state. These may be pre-existing cosmetic
  issues visible in the normal (post-flash) homepage render. Separate investigation needed.
