<?php
/**
 * Plugin Name: PureBrain Video Handler
 * Plugin URI:  https://purebrain.ai
 * Description: Homepage video viewport handler. Manages the background video on mobile (z-index layering, living-background hiding, play/pause on visibility change). Extracted from purebrain-security-plugin v5.1.x.
 * Version:     1.5.0
 * Author:      Pure Technology
 * License:     Proprietary
 *
 * Extracted from purebrain-security-plugin.php (Task 3 of 14 — Security Plugin Extraction).
 *
 * Changelog:
 *   v1.3.0 - Fix: Mobile shows poster/hexagon image instead of video on all pages.
 *            Root cause: .video-background__video used width:auto/height:auto with
 *            top:50%/left:50%/transform trick. On mobile Safari and Android, this
 *            can result in the video not rendering its frame (shows poster instead).
 *            Fix: Override .video-background__video to width:100%/height:100%/
 *            top:0/left:0/object-fit:cover — universally supported on all browsers.
 *            Also extended CSS and JS to cover pay-test-2 (page-id-689),
 *            pay-test-sandbox-3 (page-id-688), and page-id-1232 which also use
 *            the video background.
 *   v1.2.0 - Fix: JS was not loading on homepage because is_front_page() returned false
 *            despite page 11 being configured as front page in WordPress settings.
 *            Root cause unknown (possibly caching plugin or Elementor Canvas interference).
 *            Fix: Removed PHP is_front_page() gate entirely. JS now loads on ALL pages
 *            and detects homepage via body.home / body.page-id-11 class in JS.
 *            This matches how the CSS already works (no PHP gate, uses body class selectors).
 *            Added setProperty with !important in JS to beat any competing inline styles.
 *            Added 500ms retry to handle late-loading Elementor canvas animations.
 *   v1.1.0 - Bug fix: mobile shows spiral/vortex instead of brain video.
 *   v1.0.0 - Initial extraction from security plugin.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ============================================================
// CSS: Mobile homepage video layering (priority 30 in wp_head)
// ============================================================

add_action( 'wp_head', function () {
    ?>
<style id="pb-video-handler-css">
/* v1.3.0: Fix .video-background__video sizing on ALL pages and ALL viewports.
   width:auto/height:auto with the transform centering trick fails on mobile —
   browser shows the poster/hexagon image instead of rendering the video frame.
   width:100%/height:100%/object-fit:cover is universally supported. */
.video-background__video {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    transform: none !important;
    min-width: unset !important;
    min-height: unset !important;
}

/* Mobile: bring video above html bg layer and hide living-background overlay.
   Covers homepage, pay-test-2 (689), pay-test-sandbox-3 (688), and page 1232. */
@media (max-width: 767px) {
    body.home .video-background,
    body.page-id-11 .video-background,
    body.page-id-689 .video-background,
    body.page-id-688 .video-background,
    body.page-id-1232 .video-background,
    body.page-id-319 .video-background {
        z-index: 0 !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    body.home .living-background,
    body.page-id-11 .living-background,
    body.page-id-689 .living-background,
    body.page-id-688 .living-background,
    body.page-id-1232 .living-background,
    body.page-id-319 .living-background {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        z-index: -999 !important;
    }
    body.home .living-background *,
    body.page-id-11 .living-background *,
    body.page-id-689 .living-background *,
    body.page-id-688 .living-background *,
    body.page-id-1232 .living-background *,
    body.page-id-319 .living-background * {
        display: none !important;
        visibility: hidden !important;
    }
    body.home #content,
    body.home .site-content,
    body.home .elementor,
    body.page-id-11 #content,
    body.page-id-11 .site-content,
    body.page-id-11 .elementor,
    body.page-id-689 #content,
    body.page-id-689 .site-content,
    body.page-id-689 .elementor,
    body.page-id-688 #content,
    body.page-id-688 .site-content,
    body.page-id-688 .elementor,
    body.page-id-1232 #content,
    body.page-id-1232 .site-content,
    body.page-id-1232 .elementor,
    body.page-id-319 #content,
    body.page-id-319 .site-content,
    body.page-id-319 .elementor {
        position: relative;
        z-index: 1;
    }


    /* v1.4.0 MOBILE: Hide vortex hexagon rings + particles on mobile.
       These CSS-animated hexagons (.portal-vortex > .vortex-ring) cover the
       entire viewport on mobile, hiding the video background behind them.
       Also hide hero__particles dots and shrink the hero logo. */
    .portal-vortex,
    .vortex-ring {
        display: none !important;
        visibility: hidden !important;
    }
    .hero__particles {
        display: none !important;
    }
    .hero__logo {
        width: 70px !important;
        height: 70px !important;
        margin-bottom: 15px !important;
    }
    .hero__logo-glow {
        opacity: 0.1 !important;
        filter: blur(20px) !important;
    }
}
</style>
    <?php
}, 30 );

// ============================================================
// JS: Video viewport handler — runs on ALL pages, detects
// homepage via body class (v1.2.0)
// Priority 30 ensures this runs AFTER the security plugin (20).
// ============================================================

add_action( 'wp_footer', function () {
    ?>
<script id="pb-video-handler-js">
(function() {
    'use strict';

    // Only run on video-background pages (detected by body class, not PHP)
    var body = document.body;
    var videoPageIds = ['home', 'page-id-11', 'page-id-689', 'page-id-688', 'page-id-1232', 'page-id-319'];
    var isVideoPage = videoPageIds.some(function(cls) { return body.classList.contains(cls); });
    if (!isVideoPage) return;

    var mq = window.matchMedia('(max-width: 767px)');

    function handleVideoViewport(isMobile) {
        var vid = document.getElementById('bgVideo');
        var wrapper = vid ? vid.closest('.video-background') : null;
        var livingBg = document.querySelector('.living-background');
        if (!vid) return;

        // Always ensure the video wrapper is visible
        if (wrapper) {
            wrapper.style.setProperty('display', 'block', 'important');
            wrapper.style.setProperty('visibility', 'visible', 'important');
        } else {
            vid.style.setProperty('display', 'block', 'important');
            vid.style.setProperty('visibility', 'visible', 'important');
        }

        if (isMobile) {
            // Mobile: REMOVE vortex hexagon rings from DOM entirely
            // CSS display:none !important wasn't working on iOS Safari,
            // so we physically remove the elements to guarantee they're gone.
            var portalVortex = document.querySelector('.portal-vortex');
            if (portalVortex) { portalVortex.remove(); }
            // Also remove hero particles (tiny dots)
            var heroParticles = document.querySelector('.hero__particles');
            if (heroParticles) { heroParticles.remove(); }
            // Shrink hero logo
            var heroLogo = document.querySelector('.hero__logo');
            if (heroLogo) {
                heroLogo.style.setProperty('width', '70px', 'important');
                heroLogo.style.setProperty('height', '70px', 'important');
            }

            // Mobile: bring video above html background layer
            if (wrapper) {
                wrapper.style.setProperty('z-index', '0', 'important');
            }
            // FORCE hide living-background with !important inline styles
            if (livingBg) {
                livingBg.style.setProperty('display', 'none', 'important');
                livingBg.style.setProperty('visibility', 'hidden', 'important');
                livingBg.style.setProperty('opacity', '0', 'important');
                livingBg.style.setProperty('z-index', '-999', 'important');
            }
            // Also hide all children (canvas, orbs, etc.)
            var livingChildren = document.querySelectorAll('.living-background *');
            for (var i = 0; i < livingChildren.length; i++) {
                livingChildren[i].style.setProperty('display', 'none', 'important');
                livingChildren[i].style.setProperty('visibility', 'hidden', 'important');
            }
            // Ensure page content sits above the video
            var siteContent = document.getElementById('content') ||
                              document.querySelector('.site-content') ||
                              document.querySelector('.elementor') ||
                              document.querySelector('#site-content');
            if (siteContent) {
                siteContent.style.position = 'relative';
                siteContent.style.zIndex = '1';
            }
        } else {
            // Desktop/tablet: restore original z-index and show living-background
            if (wrapper) {
                wrapper.style.setProperty('z-index', '-1', 'important');
            }
            if (livingBg) {
                livingBg.style.removeProperty('display');
                livingBg.style.removeProperty('visibility');
                livingBg.style.removeProperty('opacity');
                livingBg.style.removeProperty('z-index');
            }
            var livingChildren = document.querySelectorAll('.living-background *');
            for (var i = 0; i < livingChildren.length; i++) {
                livingChildren[i].style.removeProperty('display');
                livingChildren[i].style.removeProperty('visibility');
            }
        }

        // Play video on all viewports (muted autoplay works on mobile with playsinline)
        if (document.visibilityState !== 'hidden') {
            // On mobile, if video hasn't started, calling load() then play() forces it
            if (vid.readyState === 0 || vid.paused) {
                if (vid.readyState === 0) { vid.load(); }
                vid.play().catch(function() {});
            }
        }
    }

    // Run immediately
    handleVideoViewport(mq.matches);

    // Retry after 500ms to catch late-loading Elementor canvas animations
    setTimeout(function() { handleVideoViewport(mq.matches); }, 500);

    // Retry after 1500ms as final safety net
    setTimeout(function() { handleVideoViewport(mq.matches); }, 1500);

    // React to viewport size changes
    if (mq.addEventListener) {
        mq.addEventListener('change', function(e) { handleVideoViewport(e.matches); });
    } else if (mq.addListener) {
        mq.addListener(function(e) { handleVideoViewport(e.matches); });
    }

    // Handle page visibility change (switching tabs)
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            var vid = document.getElementById('bgVideo');
            if (vid && vid.paused) {
                vid.play().catch(function() {});
            }
        }
    });
})();
</script>
    <?php
}, 30 );
