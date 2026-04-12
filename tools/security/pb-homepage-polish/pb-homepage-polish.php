<?php
/**
 * Plugin Name: PureBrain Homepage Polish
 * Plugin URI:  https://purebrain.ai
 * Description: Fixes three persistent homepage issues: (1) preloader orange/light flash
 *              on first load — forces dark #080a12 background on the theme preloader via
 *              priority-1 wp_head so it fires before any theme CSS; (2) excessive empty
 *              space above the hero brain section — overrides align-items and padding on
 *              .hero; (3) footer Pure Technology logo wrong proportions — overrides the
 *              inline height:100px rule with correct height:40px + object-fit:contain.
 *              DO NOT merge into purebrain-security-plugin.php (security plugin is locked).
 * Version:     1.0.0
 * Author:      dept-systems-technology (Pure Technology)
 * License:     Proprietary
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ============================================================
// PRIORITY 1 — fires at the very top of <head> before any
// theme or Elementor CSS. This is the earliest possible hook.
// Fixes: preloader background + body dark base color.
// ============================================================
add_action( 'wp_head', function () {
    ?>
<style id="pb-homepage-polish-early" data-version="1.0.0">
/* ===========================================================
   PureBrain Homepage Polish v1.0.0 — EARLY (priority 1)
   Fires before theme CSS. Prevents orange flash on load.
   =========================================================== */

/* FIX 1: PRELOADER — dark background, no orange flash */
/* These rules fire before any theme CSS loads. */
html {
    background: #080a12 !important;
    background-color: #080a12 !important;
}
body {
    background: #080a12 !important;
    background-color: #080a12 !important;
}
.theme-preloader {
    background: #080a12 !important;
    background-color: #080a12 !important;
    background-image: none !important;
}
.theme-preloader .loading-container {
    background: #080a12 !important;
    background-color: #080a12 !important;
    background-image: none !important;
}
/* The magic cursor body class is added by theme JS — also cover it */
body.tt-magic-cursor,
body.home.tt-magic-cursor {
    background: #080a12 !important;
    background-color: #080a12 !important;
}
/* The [class*="magic"] rule in wp-custom-css turns body orange — nuclear override */
body[class*="magic"],
body[class*="cursor"] {
    background: #080a12 !important;
    background-color: #080a12 !important;
}
</style>
    <?php
}, 1 ); // Priority 1 = fires before default priority 10


// ============================================================
// PRIORITY 20 — fires after theme + Elementor CSS loaded.
// Fixes: hero alignment (top gap), footer logo proportions.
// ============================================================
add_action( 'wp_head', function () {
    ?>
<style id="pb-homepage-polish-late" data-version="1.0.0">
/* ===========================================================
   PureBrain Homepage Polish v1.0.0 — LATE (priority 20)
   Overrides inline CSS and Elementor section styles.
   =========================================================== */

/* FIX 2: HERO TOP GAP
   The .hero section uses align-items:center which vertically centers
   the brain content, creating equal empty space above and below.
   Override to flex-start so content sits near the top of viewport. */
.hero {
    align-items: flex-start !important;
    padding-top: 80px !important;
    padding-bottom: 60px !important;
}

/* Also cover any direct children that might add top margin */
.hero > *:first-child {
    margin-top: 0 !important;
}

/* FIX 3: FOOTER LOGO PROPORTIONS
   The inline CSS in the Elementor widget sets:
     .footer__logo { height: 100px; width: auto; }
   This makes the Pure Technology "Side by Side" logo too tall.
   Correct proportions: height 40px, preserve aspect ratio. */
.footer__logo {
    height: 40px !important;
    width: auto !important;
    max-width: 240px !important;
    object-fit: contain !important;
    object-position: left center !important;
}
/* Also target img inside footer__logo if it's a wrapper */
.footer__logo img {
    height: 40px !important;
    width: auto !important;
    max-width: 240px !important;
    object-fit: contain !important;
    object-position: left center !important;
}

/* FIX 2b: PRELOADER — belt-and-suspenders at priority 20 too
   In case theme CSS loaded and re-set the background between
   priority 1 and priority 20. */
.theme-preloader,
.theme-preloader .loading-container {
    background: #080a12 !important;
    background-color: #080a12 !important;
    background-image: none !important;
}
</style>
    <?php
}, 20 ); // Priority 20 = fires after Elementor inline CSS (priority 10 default)


// ============================================================
// INLINE SCRIPT — dismiss preloader with dark background
// immediately after DOM parses (before images/video load).
// ============================================================
add_action( 'wp_head', function () {
    ?>
<script id="pb-homepage-polish-js" data-version="1.0.0">
(function() {
    // Immediately set dark background on html/body to prevent
    // any flash between CSS parse and full stylesheet application.
    document.documentElement.style.setProperty('background', '#080a12', 'important');
    document.documentElement.style.setProperty('background-color', '#080a12', 'important');

    // Once DOM is ready, ensure preloader has dark bg (belt-and-suspenders).
    function applyPreloaderFix() {
        var preloaders = document.querySelectorAll(
            '.theme-preloader, .loading-container, .preloader, [class*="preloader"]'
        );
        preloaders.forEach(function(el) {
            el.style.setProperty('background', '#080a12', 'important');
            el.style.setProperty('background-color', '#080a12', 'important');
            el.style.setProperty('background-image', 'none', 'important');
        });
    }

    // Run immediately (synchronous — in <head>)
    if (document.readyState !== 'loading') {
        applyPreloaderFix();
    } else {
        document.addEventListener('DOMContentLoaded', applyPreloaderFix);
    }

    // Also run on document parse start (covers preloader div added by theme early)
    if (typeof document.currentScript !== 'undefined') {
        applyPreloaderFix();
    }
})();
</script>
    <?php
}, 1 ); // Priority 1 — earliest possible
