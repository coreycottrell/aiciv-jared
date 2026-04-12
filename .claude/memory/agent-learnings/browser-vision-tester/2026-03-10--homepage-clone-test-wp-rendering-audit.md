# Memory: Homepage Clone Test - WordPress Rendering Audit

**Date**: 2026-03-10
**Agent**: browser-vision-tester
**Type**: pattern
**Topic**: Large HTML page on WordPress elementor_canvas - CSS survives intact when wp:html block used

## Context

Audited https://purebrain.ai/homepage-clone-test/ - a full standalone HTML page deployed as a WordPress page using elementor_canvas template and wp:html block wrapping.

## Key Findings

### What Worked

- WordPress did NOT break the CSS via wpautop injection
- Zero `<p>` tags injected into style blocks (checked 39 style blocks, 369,728 chars total)
- All bottom sections rendered correctly: testimonials, calculator CTA, compare pills, blue/orange buttons, footer, Aether bar
- Buttons retained full styling: blue button = rgb(42,147,193), orange button = rgb(241,66,11)
- elementor_canvas template + wp:html block = safe container for full standalone HTML

### Pattern: display:none Tab-Toggle Sections

Two sections were display:none by design:
- `.pricing-section` - toggled by `.active` class via JS
- `.comparison-section` - toggled by `.active` class via JS

Don't flag these as bugs - they're intentional tab behavior. Check for `.active` CSS rule to confirm.

### Page Architecture (9,240px total)

- 0-900px: Hero
- 964-2,838px: About + Demo sections
- 2,839-5,480px: Value pyramid, capabilities, awakening chat
- 5,335-6,480px: Value section
- 6,480-6,900px: Timeline section
- 6,900-7,946px: Testimonials
- 7,946-8,296px: Calculator CTA
- 8,296-8,500px: Compare pills
- 8,501-8,660px: Awaken blue CTA button
- 8,661-8,803px: See Why orange button
- 8,803px+: Pure Technology footer

### Visual Note: "Blank" Middle Area

Scroll positions 50-70% appear nearly black due to 3D brain canvas filling background with dark/transparent section overlays. This is intentional design, NOT missing content.

## When to Apply

- When auditing any standalone HTML deployed as WordPress page
- Check wp:html wrapping first to confirm CSS is protected
- Don't panic about display:none sections - check for .active toggle pattern
- Use full-page screenshot to see actual content vs viewport scrolling which can fool you

## Selector Notes

- `document.body.scrollHeight` = accurate total page height
- `elementsFromPoint(x, y)` works for detecting content at scroll positions
- Check `el.offsetTop` vs `window.scrollY` to locate sections precisely
