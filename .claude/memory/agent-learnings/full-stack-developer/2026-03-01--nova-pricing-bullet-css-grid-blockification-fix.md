# Nova Pricing Bullet Alignment — CSS Grid Blockification + DOM Wrapping Fix

**Date**: 2026-03-01
**Agent**: full-stack-developer (via dept-systems-technology)
**Plugin version**: 4.7.6 (fixes failed v4.7.5 attempt)

## The Bug
On purebrain.ai pricing sections, the AI name ("Nova") appeared separated from the rest of the bullet text:
- "Nova   has a permanent home that's always on"
- "Nova   inherits wisdom from a family of AI minds"

## Root Cause Chain

### Step 1: The HTML structure
```html
<li class="pricing-card__feature pricing-card__feature--blue">
    <svg>...</svg>
    <span class="ai-name-dynamic">Your AI</span> has a permanent home that's always on
</li>
```

### Step 2: The flex problem
The li's inline CSS sets `display: flex`. In a flex container, the SVG, span, and text node each become separate flex items. The text node becomes its own flex item, causing "Nova" (in the span) to be visually separated from " has a permanent home..." (the text node).

### Step 3: Why v4.7.5 failed
v4.7.5 switched `.pricing-card__feature` to `display: grid` with `grid-template-columns: 24px 1fr`. The intent was to put SVG in column 1 and all text in column 2. But CSS grid blockifies all direct children — even a span with `display: inline !important` becomes block inside a grid container. So "Nova" span and " has a permanent home..." text node were still separate block-level grid cells, just in a single column. Still broken.

### Step 4: The correct fix (v4.7.6)
Use JS to wrap the span AND the following text node into a single `<span class="pb-bullet-text">` wrapper. Now:
- Column 1 (grid): SVG icon
- Column 2 (grid): `<span class="pb-bullet-text">` containing `<span class="ai-name-dynamic">Nova</span> has a permanent home...`
- Inside the wrapper, the span and text node are inline content — the blockification doesn't apply to them because they're not direct children of the grid container

## The Fix Code (in plugin wp_head hook)

```php
add_action( 'wp_head', function () {
    ?>
<style id="pb-pricing-bullet-fix">
.pricing-card__feature {
    display: grid !important;
    grid-template-columns: 24px 1fr !important;
    gap: 12px !important;
    align-items: start !important;
}
.pricing-card__feature svg {
    grid-column: 1 !important;
    grid-row: 1 !important;
    width: 20px !important;
    height: 20px !important;
    margin-top: 2px !important;
    flex-shrink: 0 !important;
}
.pricing-card__feature .pb-bullet-text {
    display: block !important;
    grid-column: 2 !important;
    grid-row: 1 !important;
}
.pricing-card__feature .pb-bullet-text .ai-name-dynamic {
    display: inline !important;
}
</style>
<script id="pb-pricing-bullet-fix-js">
(function() {
    function wrapPricingBullets() {
        var features = document.querySelectorAll('.pricing-card__feature');
        features.forEach(function(li) {
            var span = li.querySelector('.ai-name-dynamic');
            if (!span) return;
            if (span.parentElement.classList.contains('pb-bullet-text')) return;
            var wrapper = document.createElement('span');
            wrapper.className = 'pb-bullet-text';
            var nodes = Array.from(li.childNodes);
            var afterSvg = false;
            nodes.forEach(function(node) {
                if (node.nodeName.toLowerCase() === 'svg') { afterSvg = true; return; }
                if (afterSvg) { wrapper.appendChild(node); }
            });
            li.appendChild(wrapper);
        });
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', wrapPricingBullets);
    } else {
        wrapPricingBullets();
    }
    setTimeout(wrapPricingBullets, 500);
    setTimeout(wrapPricingBullets, 1500);
})();
</script>
    <?php
}, 20 );
```

## Verification Results
- span display: inline (correct)
- li display: grid with cols "24px 177.328px"
- pb-bullet-text wrapper present on both Nova bullets
- Text reads: "Nova has a permanent home that's always on" (continuous)

## Pages Affected
All pages with `.pricing-card__feature` class + `.ai-name-dynamic` span inside bullets:
- Homepage (purebrain.ai/) — main affected page
- pay-test-2 (ID: 689)
- pay-test-sandbox-2 (ID: 688)
- pay-test (ID: 439)
- invitation (ID: 987)
- pitch (ID: 1001)
- purebrain-4 (ID: 383)

## Cloudflare Cache Note
The homepage showed as "not fixed" in HTTP checks because Cloudflare serves a cached version. The fix IS active on the server — cache-busted URLs (?nocache=...) confirm the fix loads correctly. The cache will expire naturally or can be purged via Cloudflare dashboard.

## Key CSS Lesson
**CSS grid blockifies all direct children.** Even `display: inline !important` on a span that is a direct child of a grid container will compute as `block`. The correct approach: wrap inline siblings (span + text node) into a container element first, then put that container in the grid column.

## Plugin File
`exports/purebrain-security-plugin-v476.php`
