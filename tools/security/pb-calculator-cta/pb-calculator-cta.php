<?php
/**
 * Plugin Name: PureBrain Calculator CTA
 * Description: Injects the "Free Tool / AI Tool Stack Calculator" CTA section on the homepage
 *              (page-id-11), pay-test-2 (689), and pay-test-sandbox-3 (1232).
 *              Uses JS DOM injection before the "Compare PureBrain" section.
 * Version:     2.0.0
 * Author:      Pure Technology
 * License:     Proprietary
 *
 * Changelog:
 *   v2.0.0 - Added homepage (page-id-11 / is_front_page) as a target page.
 *            Homepage already has the "Compare PureBrain" pills section in Elementor HTML,
 *            so the JS injection logic finds it and inserts the calc CTA immediately before it.
 *            Improved injection strategy: searches all elements (including divs) for
 *            "Compare PureBrain" text. Retry after 2000ms added for Elementor async rendering.
 *   v1.0.0 - Initial release: inject on pay-test-2 (689) and pay-test-sandbox-3 (1232).
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// Target page IDs: homepage (11), pay-test-2 (689), pay-test-sandbox-3 (1232)
define( 'PB_CALC_CTA_PAGES', array( 11, 689, 1232 ) );

function pb_calc_cta_is_target() {
    // Support homepage whether WP considers it is_front_page, is_home, or is_page(11)
    if ( is_front_page() || is_home() ) {
        return true;
    }
    return is_page() && in_array( (int) get_queried_object_id(), PB_CALC_CTA_PAGES, true );
}

add_action( 'wp_footer', function () {
    if ( ! pb_calc_cta_is_target() ) {
        return;
    }
    ?>
<script id="pb-calc-cta-injector">
(function(){
    'use strict';

    function getTopSection(el) {
        var cur = el;
        while (cur && cur !== document.body) {
            if (cur.classList &&
                (cur.classList.contains('elementor-top-section') ||
                 cur.classList.contains('elementor-section') ||
                 cur.classList.contains('e-container') ||
                 cur.tagName === 'SECTION')) {
                return cur;
            }
            cur = cur.parentElement;
        }
        return null;
    }

    function inject() {
        if (document.getElementById('pb-calc-cta')) return;

        var html = '<section id="pb-calc-cta" style="background:linear-gradient(135deg,#0d1120 0%,#1a1f35 100%);padding:60px 20px;text-align:center;border-top:1px solid rgba(42,147,193,0.2);border-bottom:1px solid rgba(42,147,193,0.2);">'
            + '<p style="color:#2a93c1;font-size:13px;font-weight:600;letter-spacing:2px;text-transform:uppercase;margin:0 0 12px 0;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif;">Free Tool</p>'
            + '<h2 style="color:#ffffff;font-size:28px;font-weight:700;margin:0 0 12px 0;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif;line-height:1.3;">How Much Are You Wasting on AI Tool Sprawl?</h2>'
            + '<p style="color:#8892a4;font-size:16px;margin:0 auto 28px auto;max-width:600px;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif;line-height:1.6;">Track hundreds of tools across 31 categories \u2014 and see exactly how much PureBrain saves you every month.</p>'
            + '<a href="https://purebrain.ai/ai-tool-stack-calculator/" style="display:inline-block;background:#f1420b;color:#ffffff !important;padding:14px 36px;border-radius:8px;text-decoration:none;font-weight:700;font-size:16px;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif;transition:all 0.3s;letter-spacing:0.3px;">Try the Free Calculator \u2192</a>'
            + '</section>';

        var wrapper = document.createElement('div');
        wrapper.innerHTML = html;
        var section = wrapper.firstChild;

        /* -------------------------------------------------------
         * Strategy 1: Find "Compare PureBrain" text and insert before
         * its containing Elementor section.
         * Works on homepage (page-id-11) where Compare PureBrain is
         * rendered inside an Elementor HTML widget.
         * Also works on any page that has Compare PureBrain content.
         * ------------------------------------------------------- */
        var allEls = document.querySelectorAll('p, span, h2, h3, h4, div');
        for (var i = 0; i < allEls.length; i++) {
            var t = (allEls[i].textContent || '').trim();
            if (t === 'Compare PureBrain' || t.indexOf('Compare PureBrain') !== -1) {
                var topSec = getTopSection(allEls[i]);
                if (topSec && topSec.parentNode) {
                    topSec.parentNode.insertBefore(section, topSec);
                    return;
                }
            }
        }

        /* -------------------------------------------------------
         * Strategy 2: Find "See Why PureBrain is Different" heading
         * (fallback for sandbox-3 and pay-test-2 which lack Compare section)
         * ------------------------------------------------------- */
        var allHeadings = document.querySelectorAll('h1, h2, h3, h4, h5');
        for (var j = 0; j < allHeadings.length; j++) {
            var htxt = allHeadings[j].textContent || '';
            if (htxt.indexOf('See Why PureBrain') !== -1 || htxt.indexOf('Why PureBrain is Different') !== -1) {
                var hSec = getTopSection(allHeadings[j]);
                if (hSec && hSec.parentNode) {
                    hSec.parentNode.insertBefore(section, hSec);
                    return;
                }
            }
        }

        /* -------------------------------------------------------
         * Strategy 3: Find the Awaken CTA section by ID
         * ------------------------------------------------------- */
        var awakenBtn = document.getElementById('pb-awaken-cta-section');
        if (awakenBtn && awakenBtn.parentNode) {
            awakenBtn.parentNode.insertBefore(section, awakenBtn);
            return;
        }

        /* -------------------------------------------------------
         * Strategy 4: Last resort — insert before site footer
         * ------------------------------------------------------- */
        var footer = document.querySelector('footer, .site-footer, #footer');
        if (footer && footer.parentNode) {
            footer.parentNode.insertBefore(section, footer);
            return;
        }

        // Absolute fallback
        document.body.appendChild(section);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            inject();
            setTimeout(inject, 800);
            setTimeout(inject, 2000);
        });
    } else {
        inject();
        setTimeout(inject, 800);
        setTimeout(inject, 2000);
    }
})();
</script>
<?php
}, 25 );
