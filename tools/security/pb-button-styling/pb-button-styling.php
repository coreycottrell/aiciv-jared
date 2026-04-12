<?php
/**
 * Plugin Name: PureBrain Button Styling
 * Plugin URI:  https://purebrain.ai
 * Description: Button hover states and CTA styling for purebrain.ai. Calculator buttons → blue hover. Comparison buttons → orange hover. Extracted from PureBrain Security plugin on 2026-03-07.
 * Version:     1.0.0
 * Author:      Aether (AI) for Pure Technology
 * Author URI:  https://purebrain.ai
 * License:     Private - All Rights Reserved
 *
 * Extracted from purebrain-security-plugin.php (Task 4 of 14 — Security Plugin Extraction).
 * Original location: wp_head action (lines 6072–6097, BUTTON HOVER CSS v6.2.2).
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// =============================================================================
// BUTTON HOVER CSS (v6.2.2 — merged from v4.8.4)
// Calculator → blue hover, Comparisons → orange hover. All pages.
// =============================================================================
add_action( 'wp_head', function () {
    ?>
<style id="pb-button-hover-v622">
/* "Try the Free Calculator" button hover → blue */
html body a[href*="ai-tool-stack-calculator"]:hover {
    background: #2a93c1 !important;
    background-color: #2a93c1 !important;
    color: #ffffff !important;
    transition: all 0.3s ease !important;
}

/* "See All Comparisons" button hover → orange */
html body a[href="/compare/"]:hover,
html body a[href="https://purebrain.ai/compare/"]:hover {
    background: #f1420b !important;
    background-color: #f1420b !important;
    color: #ffffff !important;
    transition: all 0.3s ease !important;
}
</style>
    <?php
} );
