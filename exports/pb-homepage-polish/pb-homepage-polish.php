<?php
/**
 * Plugin Name: PureBrain Homepage Polish
 * Plugin URI:  https://purebrain.ai
 * Description: Homepage hero space fix, orange-flash preloader fix, footer logo proportions.
 *              Separate from security plugin per Jared's rule.
 * Version:     1.0.0
 * Author:      Aether (AI) for Pure Technology
 *
 * CHANGELOG
 * ---------
 * v1.0.0 - 2026-03-12
 *   THREE FIXES:
 *
 *   FIX 1 — HERO TOP SPACE:
 *     The Elementor e-con-boxed container (elementor-element-c4d524c) on page 11
 *     carries Elementor default padding (--e-con-gap, typically 20-30px top/bottom)
 *     plus the e-con-inner div adds its own padding. The hero section itself has
 *     min-height:100vh and padding:60px 24px with align-items:center — so any
 *     extra padding ABOVE it shifts the visual center point, creating blank dark
 *     space above the brain.
 *     Fix: Zero out padding on the outer Elementor container and its inner wrapper
 *     on the homepage only. The hero section's own 60px padding is preserved.
 *
 *   FIX 2 — ORANGE FLASH ON FIRST LOAD:
 *     The Awaiken theme outputs a .theme-preloader div before body content.
 *     Since body.home / body.page-id-11 is set to transparent (to let the brain
 *     video show through), the preloader inherits no background and the Awaiken
 *     theme CSS gives .theme-preloader an orange/amber default background.
 *     On first load, before JS hides the preloader, the orange flashes.
 *     Fix: Inject CSS via wp_head at priority 1 (first possible) setting
 *     .theme-preloader { background: #080a12 !important; } — dark, matches html bg.
 *     The hexagonal spinner animation is preserved; only the background changes.
 *
 *   FIX 3 — FOOTER PURE TECHNOLOGY LOGO PROPORTIONS:
 *     The .footer__logo CSS class in the homepage HTML sets both a fixed height (40px)
 *     AND a fixed width (240px). If the logo image is not exactly 6:1 aspect ratio,
 *     it stretches. The Pure Technology "side-by-side" logo is wider than 240px at 40px
 *     height, causing distortion.
 *     Fix: Override .footer__logo to use height:auto + max-height:48px + width:auto
 *     + max-width:200px + object-fit:contain. This lets the image scale proportionally.
 *     Scoped to body.home and body.page-id-11 to avoid affecting other pages.
 *
 * RULES:
 * - Does NOT touch the security plugin.
 * - Does NOT use display:none on any functional element.
 * - Does NOT break the chatbox, bypass flow, or any existing features.
 * - Scoped to homepage (body.home / body.page-id-11) to prevent side effects.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ============================================================
// FIX 2: PRELOADER ORANGE FLASH — Priority 1 (earliest load)
//   Must fire BEFORE the Awaiken theme CSS to override the orange bg.
//   The theme-preloader is rendered immediately after <body> opens,
//   so we need this CSS to be the very first style the browser sees.
// ============================================================
add_action( 'wp_head', function () {
    if ( ! ( is_front_page() || is_page( 11 ) ) ) {
        return;
    }
    ?>
<style id="pb-homepage-preloader-fix">
/* FIX 2: Preloader orange flash prevention (pb-homepage-polish v1.0.0)
   The Awaiken theme gives .theme-preloader an orange/amber bg by default.
   Since body.home is transparent (for brain video to show), this flashes.
   Force dark background matching html { background: #080a12 }. */
body.home .theme-preloader,
body.page-id-11 .theme-preloader {
    background: #080a12 !important;
    background-color: #080a12 !important;
}
/* Ensure the loading spinner colors stay as brand colors (not affected by bg fix) */
body.home .theme-preloader .loading,
body.page-id-11 .theme-preloader .loading {
    border-color: transparent !important;
    border-top-color: #f1420b !important;
    border-right-color: #2a93c1 !important;
}
</style>
    <?php
}, 1 );

// ============================================================
// FIX 1: HERO TOP SPACE — Remove Elementor container padding
//   The e-con-boxed container adds default padding via Elementor
//   CSS variables. Zero it out on homepage only.
//   Also removes any inherited Elementor section margin-top.
// ============================================================
add_action( 'wp_head', function () {
    if ( ! ( is_front_page() || is_page( 11 ) ) ) {
        return;
    }
    ?>
<style id="pb-homepage-hero-space-fix">
/* FIX 1: Remove Elementor container padding that creates hero top space
   (pb-homepage-polish v1.0.0)
   Target: elementor-element-c4d524c (the outer e-con-boxed on page 11) */
body.home .elementor-element-c4d524c,
body.page-id-11 .elementor-element-c4d524c {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    --e-con-gap: 0px !important;
}
/* Also zero the inner container wrapper */
body.home .elementor-element-c4d524c > .e-con-inner,
body.page-id-11 .elementor-element-c4d524c > .e-con-inner {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    margin-top: 0 !important;
    gap: 0 !important;
}
/* Zero any elementor-section top margin on the homepage */
body.home .elementor.elementor-11 > .elementor-section,
body.page-id-11 .elementor.elementor-11 > .elementor-section,
body.home .elementor-11 .elementor-element,
body.page-id-11 .elementor-11 .elementor-element {
    --e-con-gap: 0px !important;
}
/* Ensure the top-level elementor wrapper itself has no top spacing */
body.home .elementor.elementor-11,
body.page-id-11 .elementor.elementor-11 {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
</style>
    <?php
}, 10 );

// ============================================================
// FIX 3: FOOTER LOGO PROPORTIONS
//   The .footer__logo class forces width:240px + height:40px,
//   distorting the Pure Technology side-by-side logo.
//   Override with proportional sizing.
// ============================================================
add_action( 'wp_head', function () {
    if ( ! ( is_front_page() || is_page( 11 ) ) ) {
        return;
    }
    ?>
<style id="pb-homepage-footer-logo-fix">
/* FIX 3: Footer Pure Technology logo proportions (pb-homepage-polish v1.0.0)
   Original CSS: .footer__logo { height: 40px; width: 240px } — distorts logo.
   Fix: proportional sizing with max constraints. */
body.home .footer__logo,
body.page-id-11 .footer__logo {
    height: auto !important;
    width: auto !important;
    max-height: 48px !important;
    max-width: 200px !important;
    object-fit: contain !important;
}
</style>
    <?php
}, 10 );
