# WP Page Title/Breadcrumb CSS Hide Pattern

**Date**: 2026-03-02
**Page**: 1196 (purebrain-for-staycation-breaks)
**Type**: pattern / gotcha

---

## Problem

WordPress renders `.entry-title` (page title) and `.rank-math-breadcrumb` (breadcrumb nav) OUTSIDE the `<!-- wp:html -->` block, injected by the theme above the actual page content. Password-protected pages prepend "Protected:" to the title. This creates unwanted dead space and a raw title above fully custom-designed page content.

## Solution

Inject a `<style>` block at the VERY TOP of the `<!-- wp:html -->` block — immediately after the `<!-- wp:html -->\n` marker, before `<!DOCTYPE html>`. CSS placed anywhere in the DOM body applies globally, so these selectors successfully hide the theme-rendered elements above the block.

## CSS Pattern

```html
<!-- wp:html -->
<style>
.entry-title,
h1.entry-title,
.page-title,
h1.page-title { display: none !important; }

.breadcrumb,
.breadcrumbs,
.rank-math-breadcrumb,
nav.breadcrumb,
.breadcrumb-wrapper,
#breadcrumbs,
.breadcrumbs-wrapper { display: none !important; }

.entry-header,
.page-header,
.post-header { display: none !important; margin: 0 !important; padding: 0 !important; height: 0 !important; }

.entry-content,
.page-content,
.post-content { margin-top: 0 !important; padding-top: 0 !important; }
</style>
<!DOCTYPE html>
...rest of page...
```

## Implementation Method

```python
WP_BLOCK_MARKER = '<!-- wp:html -->\n'
new_content = WP_BLOCK_MARKER + hide_css + content_raw[len(WP_BLOCK_MARKER):]
```

Then PUT via REST API: `POST https://purebrain.ai/wp-json/wp/v2/pages/{id}` with `{'content': new_content}`

## Safety

- Does NOT add `display:none` to actual page content elements
- Only targets `.entry-title`, `.entry-header`, breadcrumb wrappers
- These selectors are theme-generated wrappers, never present inside the wp:html block itself
- No Elementor cache clear needed — page uses wp:html block, not Elementor

## Selectors Covered

- RankMath breadcrumb: `.rank-math-breadcrumb`
- Generic breadcrumbs: `.breadcrumb`, `.breadcrumbs`, `nav.breadcrumb`, `.breadcrumb-wrapper`, `#breadcrumbs`
- Title: `.entry-title`, `h1.entry-title`, `.page-title`
- Header wrapper: `.entry-header`, `.page-header`, `.post-header`
- Dead space: `.entry-content { margin-top: 0 }`, `.entry-header { height: 0 }`
