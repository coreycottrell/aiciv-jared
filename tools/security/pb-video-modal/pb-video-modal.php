<?php
/**
 * Plugin Name: PureBrain Video Modal
 * Plugin URI:  https://purebrain.ai
 * Description: Video modal close button styling for purebrain.ai. Extracted from PureBrain Security plugin on 2026-03-07.
 * Version:     1.0.0
 * Author:      Aether (AI) for Pure Technology
 * Author URI:  https://purebrain.ai
 * License:     Private - All Rights Reserved
 *
 * Extracted from purebrain-security-plugin.php (Task 5 of 14 — Security Plugin Extraction).
 * Original location: wp_head action (lines 5975–6070, VIDEO MODAL CLOSE BUTTON FIX v6.1.1).
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ============================================================
// v6.1.1 - VIDEO MODAL CLOSE BUTTON FIX (mobile consistency)
//
// PROBLEM: .video-modal__close uses position:absolute + top:-50px inside
// .video-modal__content. On mobile devices where the modal content renders
// near the top of the viewport, the button is positioned off-screen above
// the visible area and becomes completely invisible.
//
// ROOT CAUSE: The page CSS (in Elementor content) sets:
//   .video-modal__close { position: absolute; top: -50px; right: 0; z-index: 10; }
// This is a 50px gap ABOVE the content box. On a 375px phone in landscape or
// when content starts at top:0 of the flex container, that 50px goes off-screen.
//
// FIX: Override with position:fixed so the button is always pinned to the
// viewport upper-right corner (top:16px, right:16px) regardless of scroll
// position or content height. Visible dark circle background + 44x44px tap
// target. z-index:10010 ensures it renders above .video-modal (z:10003).
//
// Pages: 11 (homepage), 689 (pay-test-2), 688 (pay-test-sandbox-2)
// Only these pages have the video demo modal with .video-modal__close button.
// ============================================================
add_action( 'wp_head', function () {
    if ( ! is_front_page() && ! is_page( array( 688, 689 ) ) ) {
        return;
    }
    ?>
<style id="pb-video-modal-close-fix-v611">
/* ==========================================================
   v6.1.1 VIDEO MODAL CLOSE BUTTON — MOBILE FIX
   Root cause: position:absolute + top:-50px goes off-screen
   on small viewports. Solution: position:fixed to viewport.
   ========================================================== */

/* Override the Elementor page CSS which uses position:absolute + top:-50px */
html body .video-modal .video-modal__close,
html body #videoModal .video-modal__close {
    position: fixed !important;
    top: 16px !important;
    right: 16px !important;
    bottom: auto !important;
    left: auto !important;

    /* Visible background circle — readable on any content behind it */
    background: rgba(8, 10, 18, 0.88) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.28) !important;
    border-radius: 50% !important;

    /* Minimum 44x44px tap target (iOS/Android accessibility guideline) */
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    min-height: 44px !important;
    padding: 0 !important;

    /* Center the X glyph inside the circle */
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.5rem !important;
    line-height: 1 !important;

    /* Above .video-modal (z-index: 10003) and all other overlays */
    z-index: 10010 !important;

    color: #ffffff !important;
    cursor: pointer !important;
    transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease !important;

    /* Neutralize any inherited transform that could shift the fixed position */
    transform: none !important;
}

/* Hover: orange brand color */
html body .video-modal .video-modal__close:hover,
html body #videoModal .video-modal__close:hover {
    background: rgba(241, 66, 11, 0.92) !important;
    border-color: rgba(241, 66, 11, 0.55) !important;
    transform: scale(1.08) !important;
}

/* Extra-small screens (320px – 375px): slightly smaller button, tighter inset */
@media screen and (max-width: 375px) {
    html body .video-modal .video-modal__close,
    html body #videoModal .video-modal__close {
        top: 12px !important;
        right: 12px !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;
        font-size: 1.25rem !important;
    }
}
</style>
    <?php
}, 999 );
