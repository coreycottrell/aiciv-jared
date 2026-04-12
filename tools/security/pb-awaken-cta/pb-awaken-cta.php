<?php
/**
 * Plugin Name: PureBrain Awaken CTA
 * Plugin URI:  https://purebrain.ai
 * Description: Injects the "Awaken Your Personal AI Partner Today" CTA button between
 *              the Compare PureBrain section and the "See Why PureBrain is Different"
 *              section on pages 11 (homepage), 689 (pay-test-2), and 1232 (pay-test-sandbox-3).
 *              Uses JavaScript DOM injection — does NOT touch _elementor_data.
 * Version:     1.1.0
 * Author:      cto (Pure Technology)
 * License:     Proprietary
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// Target page IDs
define( 'PB_AWAKEN_CTA_PAGES', array( 11, 689, 1232 ) );

/**
 * Only load assets on the target pages.
 */
function pb_awaken_cta_is_target_page() {
    if ( ! is_page() ) {
        return false;
    }
    $page_id = get_queried_object_id();
    return in_array( (int) $page_id, PB_AWAKEN_CTA_PAGES, true );
}

// ============================================================
// CSS — button styles
// ============================================================
add_action( 'wp_head', function () {
    if ( ! pb_awaken_cta_is_target_page() ) {
        return;
    }
    ?>
<style id="pb-awaken-cta-css">
/* PureBrain Awaken CTA button — v1.1.0 */
.pb-awaken-cta-wrapper {
    text-align: center;
    padding: 48px 20px;
    position: relative;
    z-index: 2;
}
.pb-awaken-cta-btn {
    display: inline-block;
    padding: 18px 44px;
    background: #2a93c1;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-decoration: none !important;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    transition: background 0.3s ease, box-shadow 0.3s ease, transform 0.2s ease;
    box-shadow: 0 4px 20px rgba(42, 147, 193, 0.35);
    position: relative;
    overflow: hidden;
    z-index: 2;
}
.pb-awaken-cta-btn:hover,
.pb-awaken-cta-btn:focus {
    background: #f1420b !important;
    background-color: #f1420b !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-decoration: none !important;
    box-shadow: 0 4px 24px rgba(241, 66, 11, 0.40);
    transform: translateY(-2px);
    outline: none;
}
.pb-awaken-cta-btn:visited {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
/* Bottom sections z-index fix — ensures all sections render above video bg on mobile */
#pb-calc-cta,
.pb-awaken-cta-wrapper,
#pb-awaken-cta,
#pb-why-purebrain-paytest-link {
    position: relative !important;
    z-index: 2 !important;
}
/* Compare pills and See Why sections (no class/id, use adjacent sibling) */
#pb-calc-cta ~ div,
.pb-awaken-cta-wrapper ~ div {
    position: relative !important;
    z-index: 2 !important;
}
@media (max-width: 767px) {
    /* Force all bottom sections visible and above video on mobile */
    #pb-calc-cta,
    #pb-calc-cta ~ div,
    .pb-awaken-cta-wrapper,
    #pb-awaken-cta,
    .pb-awaken-cta-wrapper ~ div,
    .pb-awaken-cta-btn {
        position: relative !important;
        z-index: 2 !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    .pb-awaken-cta-btn {
        display: inline-block !important;
        padding: 16px 28px;
        font-size: 1rem;
    }
}
</style>
    <?php
} );

// ============================================================
// JS — DOM injection after Compare section
// ============================================================
add_action( 'wp_footer', function () {
    if ( ! pb_awaken_cta_is_target_page() ) {
        return;
    }
    ?>
<script id="pb-awaken-cta-js">
(function () {
    'use strict';

    function buildCTA() {
        var wrapper = document.createElement('div');
        wrapper.className = 'pb-awaken-cta-wrapper';
        wrapper.id = 'pb-awaken-cta';

        var btn = document.createElement('a');
        btn.href = '#awakening';
        btn.className = 'pb-awaken-cta-btn';
        btn.textContent = 'Awaken Your Personal AI Partner Today';
        btn.setAttribute('aria-label', 'Awaken Your Personal AI Partner Today — scroll to chatbox');

        wrapper.appendChild(btn);
        return wrapper;
    }

    function injectCTA() {
        // Guard: only inject once
        if (document.getElementById('pb-awaken-cta')) {
            return;
        }

        var cta = buildCTA();

        /*
         * Strategy: Find the "Compare" section OR the "See Why PureBrain is Different"
         * heading and insert the button immediately before the latter.
         *
         * Elementor pages use .elementor-section / .elementor-container structure.
         * We look for text content anchors that are stable across page edits.
         *
         * Priority order:
         *  1. Find "See Why PureBrain is Different" heading → insert CTA before its section
         *  2. Find the compare-pills wrapper → insert CTA immediately after it
         *  3. Fallback: insert before first h2/h3 containing "Why" or "Different"
         */

        // --- Helper: walk up to the nearest .elementor-section ancestor ---
        function getSection(el) {
            while (el && el !== document.body) {
                if (el.classList && (
                    el.classList.contains('elementor-section') ||
                    el.classList.contains('e-container') ||
                    el.classList.contains('elementor-top-section')
                )) {
                    return el;
                }
                el = el.parentElement;
            }
            return null;
        }

        // --- Strategy 1: Find "See Why PureBrain is Different" heading ---
        var allHeadings = document.querySelectorAll('h1, h2, h3, h4, h5');
        var targetHeading = null;
        for (var i = 0; i < allHeadings.length; i++) {
            var txt = allHeadings[i].textContent || '';
            if (txt.indexOf('See Why PureBrain') !== -1 || txt.indexOf('Why PureBrain is Different') !== -1) {
                targetHeading = allHeadings[i];
                break;
            }
        }

        if (targetHeading) {
            var section = getSection(targetHeading);
            if (section && section.parentNode) {
                section.parentNode.insertBefore(cta, section);
                return;
            }
            // Fallback within Strategy 1: insert before the heading's parent element
            if (targetHeading.parentNode) {
                targetHeading.parentNode.insertBefore(cta, targetHeading);
                return;
            }
        }

        // --- Strategy 2: Find the compare pills / compare grid container ---
        // The compare section often has class names or IDs with "compare"
        var compareSections = document.querySelectorAll(
            '[class*="compare"], [id*="compare"], [data-id*="compare"]'
        );
        var lastCompare = null;
        for (var j = 0; j < compareSections.length; j++) {
            var sec = getSection(compareSections[j]);
            if (sec) {
                lastCompare = sec;
            }
        }

        // Also try text-based: find a section whose text includes "Compare PureBrain"
        var allSections = document.querySelectorAll('.elementor-section, .e-container');
        for (var k = 0; k < allSections.length; k++) {
            var sText = allSections[k].textContent || '';
            if (sText.indexOf('Compare PureBrain') !== -1 || sText.indexOf('vs ChatGPT') !== -1 || sText.indexOf('vs Claude') !== -1) {
                lastCompare = allSections[k];
            }
        }

        if (lastCompare && lastCompare.parentNode && lastCompare.nextSibling) {
            lastCompare.parentNode.insertBefore(cta, lastCompare.nextSibling);
            return;
        }
        if (lastCompare && lastCompare.parentNode) {
            lastCompare.parentNode.appendChild(cta);
            return;
        }

        // --- Strategy 3: Last resort — insert before the page footer ---
        var footer = document.querySelector('footer, .site-footer, #footer');
        if (footer && footer.parentNode) {
            footer.parentNode.insertBefore(cta, footer);
            return;
        }

        // Absolute fallback: append to body
        document.body.appendChild(cta);
    }

    // Ensure all bottom sections are visible on mobile (z-index + display fix)
    function fixBottomSections() {
        var calcCta = document.getElementById('pb-calc-cta');
        var awakenCta = document.getElementById('pb-awaken-cta');
        var elements = [calcCta, awakenCta];

        // Also fix siblings (Compare pills, See Why divs)
        if (calcCta) {
            var sibling = calcCta.nextElementSibling;
            while (sibling) {
                elements.push(sibling);
                sibling = sibling.nextElementSibling;
            }
        }

        for (var i = 0; i < elements.length; i++) {
            if (elements[i]) {
                elements[i].style.position = 'relative';
                elements[i].style.zIndex = '2';
                elements[i].style.visibility = 'visible';
                elements[i].style.opacity = '1';
            }
        }
    }

    // Run on DOMContentLoaded (for Elementor pages, may need a slight delay)
    function init() {
        injectCTA();
        fixBottomSections();
        // Also retry after Elementor finishes rendering (it can be async)
        setTimeout(injectCTA, 500);
        setTimeout(function() { injectCTA(); fixBottomSections(); }, 1500);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
</script>
    <?php
} );
