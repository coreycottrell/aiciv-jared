# Mission Section Position Fix: JS DOM Insertion

**Date**: 2026-02-24
**Type**: teaching
**Topic**: wp_footer hook priority cannot place content before theme HTML — must use JS DOM insertion

---

## The Problem

`wp_footer` hooks fire INSIDE the `wp_footer()` PHP function call. The theme template calls `wp_footer()` AFTER it has already rendered its own footer HTML (`<footer>`, `#site-footer`). This means:

- wp_footer priority 1 still outputs AFTER the theme's footer HTML
- No PHP-only solution can place content before the theme footer
- The mission section was appearing below the Pure Technology footer AND below the Privacy/Terms bar

## The Fix

Use JS DOM insertion: render the element hidden (`display:none`), then use `insertBefore()` to move it before the theme footer.

```php
// Priority 5: Render hidden
add_action('wp_footer', function() {
    echo '<div id="pb-mission-section" style="display:none;">...</div>';
}, 5);

// Priority 6: JS moves it before theme footer
add_action('wp_footer', function() {
    ?>
    <script>
    (function() {
        function placeMissionSection() {
            var section = document.getElementById('pb-mission-section');
            var anchor = document.querySelector('footer.site-footer') ||
                         document.querySelector('#site-footer') ||
                         document.querySelector('.site-footer') ||
                         document.querySelector('footer:not(#pb-aether-footer)') ||
                         document.getElementById('purebrain-legal-footer');
            if (anchor && anchor.parentNode) {
                anchor.parentNode.insertBefore(section, anchor);
            }
            section.style.display = '';
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', placeMissionSection);
        } else {
            placeMissionSection();
        }
    })();
    </script>
    <?php
}, 6);
```

## Key Lessons

1. **wp_footer hook priority controls order WITHIN wp_footer(), NOT before theme HTML.** Theme HTML is rendered before `wp_footer()` is called.
2. **JS DOM insertion is the correct tool** for placing content relative to theme elements.
3. **The transparency section already uses this pattern** (`display:none` + JS `insertBefore` before `.blog-cta-block`).
4. **Raw HTML source order doesn't match rendered DOM order** when JS moves elements. Verification scripts checking HTML source position will show false negatives.
5. **Footer selector cascade**: `footer.site-footer` → `#site-footer` → `.site-footer` → `footer:not(#pb-aether-footer)` → `#purebrain-legal-footer`. Always exclude `#pb-aether-footer` (the fixed Aether credit bar) from the `footer` query.

## Slug-Based Page Detection

`is_page()` accepts BOTH slugs and IDs in the same array. Always include both for future-proofing:

```php
$targets = array(
    'pay-test', 'pay-test-2', 'pay-test-sandbox', 'pay-test-sandbox-2',
    439, 468, 688, 689,
);
if (!is_front_page() && !is_page($targets)) { return; }
```

## Pay Test Page IDs Reference

- 439: pay-test
- 468: pay-test-sandbox
- 688: pay-test-sandbox-2
- 689: pay-test-2

## Plugin Version

This fix landed in v5.4.0 (with v5.5.0 building on top same day).
File: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`
Deploy script: `tools/security/deploy_plugin_v540_purebrain.py`
