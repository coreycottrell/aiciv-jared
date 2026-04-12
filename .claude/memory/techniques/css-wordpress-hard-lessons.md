# CSS & WordPress Hard Lessons

Patterns learned the hard way through production incidents. Reference before deploying CSS or HTML to WordPress.

## overflow-x: hidden Kills position: sticky (2026-02-24)
- **Root cause**: `overflow-x: hidden` on `html` or `body` creates a new scroll context, preventing `position: sticky` from working
- **Fix**: Use `overflow-x: clip` instead - clips overflow without creating a new scroll context
- **Incident**: Calculator page sidebar wouldn't stick. CSS Grid + `grid-row: 1/-1` + sticky also unreliable. Flexbox layout + `overflow-x: clip` solved it.

## WordPress elementor_canvas Still Loads Theme CSS (2026-02-24)
- The "Elementor Canvas" template is NOT a truly blank page - it still loads:
  - Theme preloader overlay (covers entire page, white bg)
  - magic-cursor CSS
  - all.min.css from theme
- **Impact**: Self-contained HTML pages appear white/broken because theme preloader covers content
- **Fix (Nuclear 3-layer defense)**:
  1. CSS: `!important` overrides on body bg + preloader `display:none`
  2. Preloader: `[class*="preloader"] { display:none !important }`
  3. JS: `forceDark()` function with multiple timeouts to ensure dark bg persists
- **Plugin approach**: Deploy via purebrain-custom-styling plugin for persistence

## wp:html Block Prevents wpautop Destruction (2026-02-23)
- WordPress `wpautop` filter injects `<p>` tags into `<style>` and `<script>` blocks
- **ALWAYS** wrap self-contained HTML in `<!-- wp:html -->` blocks when deploying via REST API
- This broke calculator (page 777) AND website analysis (page 816) in the same session
- Pattern: `<!-- wp:html -->\n{full HTML content}\n<!-- /wp:html -->`

## CSS Specificity for WordPress Themes (2026-02-21-22)
- WordPress theme CSS has high specificity - custom styles MUST be scoped
- Wrap ALL custom CSS under a unique ID: `#pb-audit-page .class { }`
- Use `!important` on critical layout/color properties
- Body background needs: `body.page { background-color: #080a12 !important; }`
- `:root` CSS variables may not work if theme overrides them - use hard values as fallback
