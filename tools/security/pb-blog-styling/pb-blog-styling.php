<?php
/**
 * Plugin Name: PureBrain Blog Styling
 * Plugin URI:  https://purebrain.ai
 * Description: Blog post styling, transparency section, blog nav, and blog listing features.
 *              Extracted from purebrain-security-plugin.php (Task 14 of 14).
 *              FAQ handled by pb-blog-faq. Lead capture by pb-lead-capture. Social sharing by pb-social-sharing.
 * Version:     1.2.0
 * Author:      Aether (Pure Technology)
 * License:     Proprietary
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ============================================================
// v5.1.3: INLINE CTA BUTTON TEMPLATE LOCK
// Source: lines 969-1013
// ============================================================
add_action( 'wp_footer', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="pb-inline-cta-template-lock">
body.single-post .pb-inline-cta a,
body.single-post .pb-inline-cta a:link,
body.single-post .pb-inline-cta a:visited {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-decoration: none !important;
}
body.single-post .pb-inline-cta a:hover {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
html body #pb-agent-manager-post .pb-inline-cta a,
html body #pb-agent-manager-post .pb-inline-cta a:link,
html body #pb-agent-manager-post .pb-inline-cta a:visited,
html body #pb-agent-manager-post .pb-inline-cta a:hover,
html body #pb-agent-manager-post .pb-inline-cta a:active,
html body #pb-agent-manager-post .pb-inline-cta a:focus {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-decoration: none !important;
}
html body #pb-agent-manager-post .pb-inline-cta a:hover {
    background: linear-gradient(135deg, #d13608 0%, #a32800 100%) !important;
}
</style>
    <?php
}, 5 );

// FAQ — handled by pb-blog-faq plugin
// (j)        FAQ Accordion CSS + JS         — add_action( 'wp_head',   ..., 15 )
// (j2)       FAQ Accordion Extended CSS + JS — add_action( 'wp_head',   ..., 16 )
// (j-schema) FAQPage JSON-LD Schema          — add_action( 'wp_footer', ..., 14 )

// ============================================================
// v1.2.0: DARK BLUE BACKGROUND BEHIND BLOG TEXT
// 60% opacity dark blue panel behind post content area only (updated from 43%)
// ============================================================
add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-blog-text-bg">
/* Dark blue background at 60% opacity behind blog text content only (v1.2.0) */
body.single-post .post-content {
    background: rgba(10, 15, 35, 0.60) !important;
    border-radius: 12px !important;
    padding: 2rem 2.5rem !important;
    box-sizing: border-box !important;
}
body.single-post .page-single-post {
    background: transparent !important;
}
@media (max-width: 767px) {
    body.single-post .post-content {
        padding: 1.25rem 1rem !important;
        border-radius: 8px !important;
    }
}
</style>
    <?php
}, 15 );

// ============================================================
// i) BLOG POST IMAGE CONSTRAIN (v5/1.9.0)
// Source: lines 2692-2837
// ============================================================
add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-blog-desktop-padding">
@media (min-width: 768px) {
    body.single-post .page-single-post .container > .row {
        margin-left: 0 !important;
        margin-right: 0 !important;
    }
    body.single-post .page-single-post .container > .row > .col-md-12 {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    body.single-post .post-single-image {
        max-width: 680px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        margin-bottom: 36px !important;
        margin-top: 8px !important;
        border-radius: 14px !important;
        overflow: visible !important;
        display: block !important;
        box-shadow: 0 6px 30px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.07) !important;
    }
    body.single-post .post-single-image figure {
        margin: 0 !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        aspect-ratio: auto !important;
        height: auto !important;
    }
    body.single-post .post-single-image img {
        border-radius: 14px !important;
        display: block !important;
        width: 100% !important;
        height: auto !important;
        aspect-ratio: auto !important;
        object-fit: fill !important;
    }
    body.single-post .post-content {
        max-width: 680px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    body.single-post .page-single-post .container {
        padding-left: 30px !important;
        padding-right: 30px !important;
        box-sizing: border-box !important;
    }
    body.single-post .page-header .container {
        padding-left: 30px !important;
        padding-right: 30px !important;
        box-sizing: border-box !important;
    }
}
@media (min-width: 1025px) {
    body.single-post .page-single-post {
        padding-top: 20px !important;
    }
    body.single-post .page-single-post .container {
        max-width: 1100px !important;
        padding-left: 60px !important;
        padding-right: 60px !important;
    }
    body.single-post .post-single-image {
        max-width: 760px !important;
        margin-bottom: 48px !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.55), 0 0 0 1px rgba(255, 255, 255, 0.07) !important;
    }
    body.single-post .post-single-image figure {
        border-radius: 16px !important;
    }
    body.single-post .post-single-image img {
        border-radius: 16px !important;
    }
    body.single-post .post-content {
        max-width: 760px !important;
    }
    body.single-post .page-header .container {
        max-width: 1100px !important;
        padding-left: 60px !important;
        padding-right: 60px !important;
    }
}
@media (min-width: 1400px) {
    body.single-post .page-single-post .container {
        padding-left: 80px !important;
        padding-right: 80px !important;
    }
    body.single-post .page-header .container {
        padding-left: 80px !important;
        padding-right: 80px !important;
    }
}
</style>
    <?php
}, 20 );

// ============================================================
// j) BLOG CTA BUTTON STYLES (v2.1.0 -> v2.9.0)
// Source: lines 2839-3000
// ============================================================
add_action( 'wp_head', function () {
    ?>
<style id="purebrain-blog-cta-hover">
body.single-post .blog-cta-block p a[href*="awakening"],
.blog-cta-block p a[href*="awakening"] {
    display: inline-block !important;
    padding: 14px 32px !important;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;
    background-color: #f1420b !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    border-radius: 8px !important;
    text-decoration: none !important;
    letter-spacing: 0.5px !important;
    box-shadow: none !important;
    transition: background 0.25s ease, box-shadow 0.25s ease, transform 0.2s ease !important;
    position: relative !important;
}
body.single-post .blog-cta-block p a[href*="awakening"]:hover,
body.single-post .blog-cta-block p a[href*="awakening"]:focus,
.blog-cta-block p a[href*="awakening"]:hover,
.blog-cta-block p a[href*="awakening"]:focus {
    background: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
    background-color: #2a93c1 !important;
    color: #ffffff !important;
    box-shadow: 0 0 0 3px rgba(42, 147, 193, 0.5), 0 0 18px rgba(42, 147, 193, 0.35), 0 6px 20px rgba(0, 0, 0, 0.3) !important;
    transform: translateY(-2px) !important;
    text-decoration: none !important;
    outline: none !important;
}
body.single-post .blog-cta-block p a[href*="subscribe"],
body.single-post .blog-cta-block p a[href*="newsletter"],
body.single-post .blog-cta-block p a[href*="neural-feed"],
.blog-cta-block p a[href*="subscribe"],
.blog-cta-block p a[href*="newsletter"],
.blog-cta-block p a[href*="neural-feed"] {
    color: #2a93c1 !important;
    text-decoration: underline !important;
    text-decoration-color: rgba(42, 147, 193, 0.4) !important;
    background: none !important;
    background-color: transparent !important;
    padding: 3px 0 !important;
    display: inline !important;
    border-radius: 5px !important;
    box-shadow: none !important;
    transform: none !important;
    font-weight: inherit !important;
    font-size: inherit !important;
    letter-spacing: inherit !important;
    transition: color 0.2s ease, text-decoration-color 0.2s ease, background 0.2s ease, padding 0.15s ease !important;
}
body.single-post .blog-cta-block p a[href*="subscribe"]:hover,
body.single-post .blog-cta-block p a[href*="subscribe"]:focus,
body.single-post .blog-cta-block p a[href*="newsletter"]:hover,
body.single-post .blog-cta-block p a[href*="newsletter"]:focus,
body.single-post .blog-cta-block p a[href*="neural-feed"]:hover,
body.single-post .blog-cta-block p a[href*="neural-feed"]:focus,
.blog-cta-block p a[href*="subscribe"]:hover,
.blog-cta-block p a[href*="newsletter"]:hover,
.blog-cta-block p a[href*="neural-feed"]:hover {
    color: #ffffff !important;
    text-decoration: none !important;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;
    background-color: #f1420b !important;
    padding: 3px 10px !important;
    border-radius: 5px !important;
    box-shadow: 0 2px 8px rgba(241, 66, 11, 0.3) !important;
    transform: none !important;
}
.blog-cta-block a,
body.single-post .blog-cta-block a {
    transition: box-shadow 0.25s ease, transform 0.2s ease, color 0.1s ease !important;
    position: relative !important;
}
body.single-post .blog-cta-block p a[data-pb-subscribe]:hover,
body.single-post .blog-cta-block p a[data-pb-subscribe]:focus {
    box-shadow: 0 2px 8px rgba(241, 66, 11, 0.3) !important;
    transform: none !important;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;
    background-color: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
}
</style>
    <?php
} );

// ============================================================
// j2) BLOG TAG PILLS + CTA BUTTON WHITE TEXT (v3.9.0)
// Source: lines 3002-3091
// ============================================================
add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-tag-pills-cta-fix">
body.single-post .blog-cta-block a,
body.single-post .blog-cta-block p a,
.blog-cta-block a[href*="awakening"],
body.single-post .blog-cta-block a[href*="awakening"] {
    color: #ffffff !important;
}
body.single-post .blog-cta-block a[href*="awakening"]:hover,
body.single-post .blog-cta-block p a[href*="awakening"]:hover,
.blog-cta-block a[href*="awakening"]:hover {
    color: #ffffff !important;
}
body.single-post .post-tags .tag-links a,
body.single-post .post-tags .tag-links a[rel="tag"],
body.single-post .tags-links a[rel="tag"],
body.single-post a[rel="tag"] {
    display: inline-block !important;
    background-color: #2a93c1 !important;
    background: #2a93c1 !important;
    color: #ffffff !important;
    padding: 4px 12px !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    letter-spacing: 0.03em !important;
    margin: 2px 3px !important;
    transition: background-color 0.2s ease, color 0.2s ease !important;
    border: none !important;
    line-height: 1.5 !important;
}
body.single-post .post-tags .tag-links a:hover,
body.single-post .post-tags .tag-links a[rel="tag"]:hover,
body.single-post .tags-links a[rel="tag"]:hover,
body.single-post a[rel="tag"]:hover {
    background-color: #f1420b !important;
    background: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
}
body.single-post .post-tags .tag-links,
body.single-post .tags-links {
    color: rgba(224, 230, 240, 0.5) !important;
    font-size: 13px !important;
}
</style>
    <?php
} );

// ============================================================
// j3) BLOG IN-TEXT LINK HOVER FIX (v3.9.1)
// Source: lines 3093-3135
// ============================================================
add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-link-hover-fix">
body.single-post .entry-content a:not(.blog-cta-button):not([rel="tag"]),
body.single-post .elementor-widget-theme-post-content a:not(.blog-cta-button):not([rel="tag"]) {
    transition: background-color 0.2s ease, color 0.2s ease !important;
}
body.single-post .entry-content a:not(.blog-cta-button):not([rel="tag"]):hover,
body.single-post .elementor-widget-theme-post-content a:not(.blog-cta-button):not([rel="tag"]):hover {
    background-color: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
    border-radius: 3px !important;
    padding: 1px 4px !important;
}
</style>
    <?php
} );

// ============================================================
// j4) TRANSPARENCY SECTION CTA BUTTON WHITE TEXT FIX (v3.9.2)
// Source: lines 3137-3182
// ============================================================
add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-transparency-cta-v392">
body.single-post .aether-transparency .aether-transparency__cta-btn,
body.single-post .aether-transparency__cta .aether-transparency__cta-btn,
html body.single-post .aether-transparency__cta-btn {
    color: #ffffff !important;
    text-decoration: none !important;
}
body.single-post .aether-transparency .aether-transparency__cta-btn:hover,
body.single-post .aether-transparency__cta .aether-transparency__cta-btn:hover,
html body.single-post .aether-transparency__cta-btn:hover {
    color: #ffffff !important;
    text-decoration: none !important;
}
</style>
    <?php
}, 99 );

// ============================================================
// j4b) TRANSPARENCY CTA HOVER WHITE TEXT FIX (v5.1.2)
// Source: lines 3184-3213
// ============================================================
add_action( 'wp_footer', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-transparency-cta-hover-v512">
html body.single-post .aether-transparency__cta-btn,
html body.single-post .aether-transparency__cta-btn:link,
html body.single-post .aether-transparency__cta-btn:visited,
html body.single-post .aether-transparency__cta-btn:hover,
html body.single-post .aether-transparency__cta-btn:active {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-decoration: none !important;
}
</style>
    <?php
}, 20 );

// ============================================================
// k) BLOG NAV MENU CSS (v2.4.0 -> v4.1.1)
// Source: lines 3216-3325
// ============================================================
add_action( 'wp_head', function () {
    if ( ! ( is_single() || is_category() || is_archive() || is_tag() ) ) {
        return;
    }
    ?>
<style id="purebrain-blog-nav-menu">
.pb-blog-nav {
    display: flex;
    align-items: center;
    margin-left: auto;
    gap: 0;
    flex-shrink: 0;
}
.pb-blog-nav a {
    color: rgba(224, 230, 240, 0.7) !important;
    text-decoration: none !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    line-height: 1 !important;
    padding: 4px 10px !important;
    transition: color 0.2s ease !important;
    white-space: nowrap !important;
    background: none !important;
    box-shadow: none !important;
    transform: none !important;
}
html body .pb-blog-nav a:hover,
html body .pb-blog-nav a:focus {
    color: #f1420b !important;
    text-decoration: none !important;
    background: none !important;
    box-shadow: none !important;
    transform: none !important;
}
.pb-blog-nav .pb-nav-sep {
    color: rgba(224, 230, 240, 0.3);
    font-size: 12px;
    line-height: 1;
    user-select: none;
    pointer-events: none;
}
@media (max-width: 480px) {
    .pb-blog-nav { display: none !important; }
}
@media (min-width: 481px) and (max-width: 767px) {
    .pb-blog-nav a {
        font-size: 11px !important;
        padding: 4px 6px !important;
    }
}
</style>
    <?php
}, 10 );

// ============================================================
// l) STRIP INLINE STYLES + TAG NEWSLETTER LINKS (v2.8.0 -> v2.9.0)
// Source: lines 3327-3370
// ============================================================
add_action( 'wp_footer', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<script id="purebrain-strip-newsletter-inline-styles">
(function() {
    'use strict';
    function initSubscribeLinks() {
        var ctaBlock = document.querySelector('.blog-cta-block');
        if (!ctaBlock) return;
        var newsletterLinks = ctaBlock.querySelectorAll(
            'a[href*="subscribe"], a[href*="newsletter"], a[href*="neural-feed"]'
        );
        newsletterLinks.forEach(function(link) {
            link.removeAttribute('style');
            link.setAttribute('data-pb-subscribe', '1');
        });
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSubscribeLinks);
    } else {
        initSubscribeLinks();
    }
})();
</script>
    <?php
}, 20 );

// Lead Capture — handled by pb-lead-capture plugin
// CSS:        add_action( 'wp_head',   ..., 25 ) — style id="purebrain-lead-capture-css"
// Markup + JS: add_action( 'wp_footer', ..., 25 ) — id="pb-lead-inline", id="pb-lead-bar", id="purebrain-lead-capture-js"

// ============================================================
// AETHER TRANSPARENCY SECTION — CSS (v3.6.0)
// Source: lines 4124-4444
// ============================================================
add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    $raw = get_option( 'purebrain_transparency_data', '' );
    if ( empty( $raw ) ) {
        return;
    }
    ?>
<style id="purebrain-transparency-css">
.aether-transparency {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0d0f1a;
    border: 1px solid rgba(42, 147, 193, 0.25);
    border-left: 4px solid #2a93c1;
    border-radius: 10px;
    padding: 28px 32px;
    margin: 48px 0 32px 0;
    color: #e0e6f0;
    max-width: 100%;
    position: relative;
    overflow: hidden;
    box-sizing: border-box;
}
.aether-transparency::before {
    content: '';
    position: absolute; top: 0; right: 0;
    width: 220px; height: 220px;
    background: radial-gradient(circle at top right, rgba(42, 147, 193, 0.06) 0%, transparent 70%);
    pointer-events: none;
}
.aether-transparency__header {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 20px; padding-bottom: 16px;
    border-bottom: 1px solid rgba(42, 147, 193, 0.15);
}
.aether-transparency__badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(42, 147, 193, 0.12); border: 1px solid rgba(42, 147, 193, 0.3);
    border-radius: 20px; padding: 4px 12px; font-size: 11px; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase; color: #2a93c1; white-space: nowrap;
}
.aether-transparency__badge-dot {
    width: 6px; height: 6px; background: #2a93c1; border-radius: 50%;
    animation: pb-transparency-pulse 2.4s ease-in-out infinite; flex-shrink: 0;
}
@keyframes pb-transparency-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
.aether-transparency__title { font-size: 13px; color: rgba(224, 230, 240, 0.5); font-weight: 400; letter-spacing: 0.02em; }
.aether-transparency__summary { font-size: 15px; line-height: 1.65; color: #c8d4e8; margin-bottom: 24px; font-style: italic; }
.aether-transparency__summary strong { color: #e0e6f0; font-style: normal; }
.aether-transparency__stats { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 24px; }
.aether-transparency__stat { flex: 1; min-width: 120px; background: rgba(8, 10, 18, 0.6); border: 1px solid rgba(42, 147, 193, 0.15); border-radius: 8px; padding: 12px 16px; text-align: center; box-sizing: border-box; }
.aether-transparency__stat-number { display: block; font-size: 22px; font-weight: 700; color: #2a93c1; line-height: 1.1; margin-bottom: 4px; }
.aether-transparency__stat-label { display: block; font-size: 11px; color: rgba(224, 230, 240, 0.5); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 500; }
.aether-transparency__table-wrap { margin-bottom: 24px; overflow-x: auto; -webkit-overflow-scrolling: touch; }
.aether-transparency__table-label { font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(224, 230, 240, 0.4); margin-bottom: 10px; }
.aether-transparency__table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
.aether-transparency__table thead tr { border-bottom: 1px solid rgba(42, 147, 193, 0.2); }
.aether-transparency__table th { text-align: left; padding: 8px 12px; font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: rgba(224, 230, 240, 0.45); white-space: nowrap; }
.aether-transparency__table td { padding: 9px 12px; color: #c8d4e8; border-bottom: 1px solid rgba(255, 255, 255, 0.04); vertical-align: top; }
.aether-transparency__table tbody tr:last-child td { border-bottom: none; }
.aether-transparency__table tbody tr:hover td { background: rgba(42, 147, 193, 0.04); }
.aether-transparency__table td:first-child { color: #e0e6f0; font-weight: 500; }
.aether-transparency__table td.value-cell { color: #2a93c1; font-weight: 600; white-space: nowrap; }
.aether-transparency__highlight { background: rgba(241, 66, 11, 0.07); border: 1px solid rgba(241, 66, 11, 0.2); border-left: 3px solid #f1420b; border-radius: 6px; padding: 14px 16px; margin-bottom: 24px; display: flex; gap: 12px; align-items: flex-start; }
.aether-transparency__highlight-icon { font-size: 16px; line-height: 1; flex-shrink: 0; margin-top: 1px; }
.aether-transparency__highlight-label { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #f1420b; display: block; margin-bottom: 4px; }
.aether-transparency__highlight-text { font-size: 13.5px; line-height: 1.55; color: #c8d4e8; margin: 0; }
.aether-transparency__cta { border-top: 1px solid rgba(42, 147, 193, 0.15); padding-top: 20px; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px; }
.aether-transparency__cta-text { font-size: 14px; color: #ffffff !important; line-height: 1.5; flex: 1; min-width: 200px; }
.aether-transparency__cta-text strong { color: #ffffff !important; }
.aether-transparency__cta-btn { display: inline-block; background: #f1420b; color: #ffffff !important; text-decoration: none !important; font-size: 13px; font-weight: 700; letter-spacing: 0.04em; padding: 11px 22px; border-radius: 6px; white-space: nowrap; transition: background 0.2s ease, box-shadow 0.2s ease; flex-shrink: 0; }
.aether-transparency__cta-btn:hover { background: #d93600 !important; box-shadow: 0 4px 16px rgba(241, 66, 11, 0.35); color: #ffffff !important; }
.aether-transparency__sig { margin-top: 16px; font-size: 12px; color: rgba(224, 230, 240, 0.3); text-align: right; font-style: italic; }
@media (max-width: 640px) {
    .aether-transparency { padding: 20px 18px; }
    .aether-transparency__stats { gap: 8px; }
    .aether-transparency__stat { min-width: 100px; padding: 10px 12px; }
    .aether-transparency__stat-number { font-size: 18px; }
    .aether-transparency__cta { flex-direction: column; align-items: flex-start; }
    .aether-transparency__cta-btn { width: 100%; text-align: center; }
}
</style>
    <?php
}, 30 );

// ============================================================
// AETHER TRANSPARENCY SECTION — HTML RENDER (v3.6.0)
// Source: lines 4446-4619
// ============================================================
add_action( 'wp_footer', function () {
    if ( ! is_single() ) {
        return;
    }
    $raw = get_option( 'purebrain_transparency_data', '' );
    if ( empty( $raw ) ) {
        return;
    }
    $data = json_decode( $raw, true );
    if ( ! is_array( $data ) ) {
        return;
    }
    $week_of     = isset( $data['week_of'] )     ? $data['week_of']     : '';
    $summary     = isset( $data['summary'] )     ? $data['summary']     : '';
    $biggest_win = isset( $data['biggest_win'] ) ? $data['biggest_win'] : '';
    $cta_url     = home_url( '/ai-partnership-assessment/' );
    $default_cta = 'This is what AI partnership looks like. Not a chatbot. Not a tool you prompt once and forget. A team that ships real work, every day, alongside you.';
    $cta_text    = ( ! empty( $data['cta_text'] ) ) ? $data['cta_text'] : $default_cta;
    $stats             = isset( $data['stats'] ) && is_array( $data['stats'] ) ? $data['stats'] : array();
    $stat_agents       = isset( $stats['specialist_agents'] ) ? (string) $stats['specialist_agents'] : '0';
    $stat_domains      = isset( $stats['work_domains'] )      ? (string) $stats['work_domains']      : '0';
    $stat_deliverables = isset( $stats['deliverables'] )      ? $stats['deliverables']               : '0';
    $stat_hours        = isset( $stats['human_hours'] )       ? $stats['human_hours']                : '0';
    $breakdown         = isset( $data['work_breakdown'] ) && is_array( $data['work_breakdown'] ) ? $data['work_breakdown'] : array();
    if ( empty( $week_of ) || empty( $summary ) ) {
        return;
    }
    ?>
<div id="pb-transparency-section" style="display:none;">
<div class="aether-transparency" role="complementary" aria-label="Aether Weekly Transparency Report">
  <div class="aether-transparency__header">
    <span class="aether-transparency__badge">
      <span class="aether-transparency__badge-dot"></span>
      Aether Transparency Report
    </span>
    <span class="aether-transparency__title">Week of <?php echo esc_html( $week_of ); ?></span>
  </div>
  <p class="aether-transparency__summary"><?php echo esc_html( $summary ); ?></p>
  <div class="aether-transparency__stats">
    <div class="aether-transparency__stat">
      <span class="aether-transparency__stat-number"><?php echo esc_html( $stat_agents ); ?></span>
      <span class="aether-transparency__stat-label">Specialist Agents</span>
    </div>
    <div class="aether-transparency__stat">
      <span class="aether-transparency__stat-number"><?php echo esc_html( $stat_domains ); ?></span>
      <span class="aether-transparency__stat-label">Work Domains</span>
    </div>
    <div class="aether-transparency__stat">
      <span class="aether-transparency__stat-number"><?php echo esc_html( $stat_deliverables ); ?></span>
      <span class="aether-transparency__stat-label">Deliverables Shipped</span>
    </div>
    <div class="aether-transparency__stat">
      <span class="aether-transparency__stat-number"><?php echo esc_html( $stat_hours ); ?></span>
      <span class="aether-transparency__stat-label">Est. Human Hours</span>
    </div>
  </div>
  <?php if ( ! empty( $breakdown ) ) : ?>
  <div class="aether-transparency__table-wrap">
    <p class="aether-transparency__table-label">Work Breakdown</p>
    <table class="aether-transparency__table">
      <thead><tr><th>Domain</th><th>What Got Done</th><th>Effort Level</th><th>Value Estimate</th></tr></thead>
      <tbody>
        <?php foreach ( $breakdown as $row ) : ?>
        <tr>
          <td><?php echo esc_html( isset( $row['domain'] )      ? $row['domain']      : '' ); ?></td>
          <td><?php echo esc_html( isset( $row['description'] ) ? $row['description'] : '' ); ?></td>
          <td><?php echo esc_html( isset( $row['effort'] )      ? $row['effort']      : '' ); ?></td>
          <td class="value-cell"><?php echo esc_html( isset( $row['value'] ) ? $row['value'] : '' ); ?></td>
        </tr>
        <?php endforeach; ?>
      </tbody>
    </table>
  </div>
  <?php endif; ?>
  <?php if ( ! empty( $biggest_win ) ) : ?>
  <div class="aether-transparency__highlight">
    <span class="aether-transparency__highlight-icon">&#9655;</span>
    <div>
      <span class="aether-transparency__highlight-label">Biggest Win</span>
      <p class="aether-transparency__highlight-text"><?php echo esc_html( $biggest_win ); ?></p>
    </div>
  </div>
  <?php endif; ?>
  <div class="aether-transparency__cta">
    <p class="aether-transparency__cta-text"><?php echo esc_html( $cta_text ); ?></p>
    <a href="<?php echo esc_url( $cta_url ); ?>" class="aether-transparency__cta-btn" style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;">Start Your AI Partnership</a>
  </div>
  <p class="aether-transparency__sig">&#x2014; Aether &nbsp;|&nbsp; The invisible essential</p>
</div>
</div>

<script id="purebrain-transparency-inject">
(function() {
    'use strict';
    function injectTransparencySection() {
        var wrapper = document.getElementById('pb-transparency-section');
        if (!wrapper) return;
        var inner = wrapper.firstElementChild;
        if (!inner) return;
        var ctaBlock    = document.querySelector('.blog-cta-block');
        var postContent = document.querySelector('.post-content');
        if (ctaBlock && ctaBlock.parentNode) {
            ctaBlock.parentNode.insertBefore(inner, ctaBlock);
        } else if (postContent && postContent.parentNode) {
            postContent.parentNode.insertBefore(inner, postContent.nextSibling);
        } else {
            var legalFooter = document.getElementById('purebrain-legal-footer');
            if (legalFooter && legalFooter.parentNode) legalFooter.parentNode.insertBefore(inner, legalFooter);
        }
        if (wrapper.parentNode) wrapper.parentNode.removeChild(wrapper);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectTransparencySection);
    } else {
        injectTransparencySection();
    }
})();
</script>
    <?php
}, 28 );

// ============================================================
// k) BLOG NAV MENU JS (v2.4.0 -> v4.1.1)
// Source: lines 4621-4672
// ============================================================
add_action( 'wp_footer', function () {
    if ( ! ( is_single() || is_category() || is_archive() || is_tag() ) ) {
        return;
    }
    $home_url       = esc_url( home_url( '/' ) );
    $subscribe_url  = esc_url( home_url( '/blog/#neural-feed-subscribe' ) );
    $assessment_url = esc_url( home_url( '/ai-adoption-review/' ) );
    ?>
<script id="purebrain-blog-nav-menu-js">
(function() {
    'use strict';
    function initBlogNav() {
        var container = document.querySelector('nav.navbar .container');
        if (!container) {
            container = document.querySelector('.navbar-inner') ||
                        document.querySelector('header nav') ||
                        document.querySelector('.site-header .container') ||
                        document.querySelector('header .container');
        }
        if (!container) return;
        if (document.querySelector('.pb-blog-nav')) return;
        var nav = document.createElement('div');
        nav.className = 'pb-blog-nav';
        nav.setAttribute('role', 'navigation');
        nav.setAttribute('aria-label', 'Quick navigation');
        nav.innerHTML =
            '<a href="<?php echo $home_url; ?>">Home</a>' +
            '<span class="pb-nav-sep" aria-hidden="true">|</span>' +
            '<a href="<?php echo $subscribe_url; ?>">Subscribe</a>' +
            '<span class="pb-nav-sep" aria-hidden="true">|</span>' +
            '<a href="<?php echo $assessment_url; ?>">Free AI Assessment</a>';
        container.appendChild(nav);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBlogNav);
    } else {
        initBlogNav();
    }
})();
</script>
    <?php
} );

// ============================================================
// n) BLOG LISTING READ MORE CSS (v4.0.0)
// Source: lines 4700-4764
// ============================================================
add_action( 'wp_head', function () {
    if ( ! is_page( 319 ) && ! is_home() ) {
        return;
    }
    ?>
<style id="purebrain-read-more-btn">
.wp-block-latest-posts__list-item .wp-block-latest-posts__read-more,
.wp-block-latest-posts li .wp-block-latest-posts__read-more {
    display: inline-block !important; margin-top: 12px !important; padding: 8px 20px !important;
    background: #f1420b !important; color: #ffffff !important; font-weight: 700 !important;
    font-size: 0.78rem !important; letter-spacing: 0.08em !important; text-transform: uppercase !important;
    border-radius: 6px !important; text-decoration: none !important;
    transition: background 0.2s ease, transform 0.15s ease !important; box-shadow: none !important;
}
.wp-block-latest-posts__list-item .wp-block-latest-posts__read-more:hover,
.wp-block-latest-posts li .wp-block-latest-posts__read-more:hover {
    background: #2a93c1 !important; color: #ffffff !important; text-decoration: none !important; transform: translateY(-1px) !important;
}
.pb-read-more-btn {
    display: inline-block !important; margin-top: 14px !important; padding: 8px 20px !important;
    background: #f1420b !important; color: #ffffff !important; font-weight: 700 !important;
    font-size: 0.78rem !important; letter-spacing: 0.08em !important; text-transform: uppercase !important;
    border-radius: 6px !important; text-decoration: none !important;
    transition: background 0.2s ease, transform 0.15s ease !important; box-shadow: none !important;
}
.pb-read-more-btn:hover {
    background: #2a93c1 !important; color: #ffffff !important; text-decoration: none !important; transform: translateY(-1px) !important;
}
</style>
    <?php
} );

// ============================================================
// n) BLOG LISTING READ MORE JS (v4.0.0)
// Source: lines 4766-4839
// ============================================================
add_action( 'wp_footer', function () {
    if ( ! is_page( 319 ) && ! is_home() ) {
        return;
    }
    ?>
<script id="purebrain-read-more-btn-js">
(function() {
    'use strict';
    function enforceReadMoreButtons() {
        var postItems = document.querySelectorAll('.wp-block-latest-posts__list-item, .wp-block-latest-posts li');
        if (!postItems.length) return;
        postItems.forEach(function(item) {
            var existingReadMore = item.querySelector('.wp-block-latest-posts__read-more, .pb-read-more-btn, a[class*="read-more"]');
            if (existingReadMore) return;
            var postLink = item.querySelector('a');
            if (!postLink) return;
            var postUrl = postLink.getAttribute('href');
            if (!postUrl) return;
            var excerptEl = item.querySelector('.wp-block-latest-posts__post-excerpt, .wp-block-latest-posts__post-full-content');
            var btn = document.createElement('a');
            btn.href = postUrl; btn.className = 'pb-read-more-btn'; btn.textContent = 'READ MORE';
            btn.setAttribute('aria-label', 'Read the full post');
            if (excerptEl) { excerptEl.parentNode.insertBefore(btn, excerptEl.nextSibling); } else { item.appendChild(btn); }
        });
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', enforceReadMoreButtons);
    } else {
        enforceReadMoreButtons();
    }
    setTimeout(enforceReadMoreButtons, 800);
})();
</script>
    <?php
}, 5 );

// ============================================================
// o) BLOG LISTING POSTS PER PAGE CAP (v4.0.0)
// Source: lines 5315-5334
// ============================================================
add_action( 'pre_get_posts', function ( $query ) {
    if ( is_admin() ) return;
    if ( is_page( 319 ) && ! $query->is_main_query() ) {
        $query->set( 'posts_per_page', 10 );
    }
} );


// ============================================================
// v1.2.0: VIDEO BACKGROUND FOR BLOG POSTS
// Injects a <video> background element (same video as landing pages)
// behind the blog post content. Layered below GIF via z-index: -3.
// Respects prefers-reduced-motion via CSS.
// ============================================================
add_action( 'wp_body_open', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<!-- Video Background (pb-blog-styling v1.2.0) -->
<div class="pb-video-bg-wrap">
    <video autoplay muted loop playsinline webkit-playsinline preload="none">
        <source src="https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/PureResearch.ai-1.mp4" type="video/mp4">
    </video>
</div>
<style id="pb-video-bg-css">
.pb-video-bg-wrap {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: -3;
    overflow: hidden;
    pointer-events: none;
}
.pb-video-bg-wrap video {
    position: absolute;
    top: 50%; left: 50%;
    min-width: 100%; min-height: 100%;
    width: auto; height: auto;
    transform: translate(-50%, -50%);
    object-fit: cover;
    opacity: 0.18;
}
@media (prefers-reduced-motion: reduce) {
    .pb-video-bg-wrap video { display: none; }
}
</style>
    <?php
} );

// Social Sharing — handled by pb-social-sharing plugin
// CSS: add_action( 'wp_head',   ..., 30 ) — style id="purebrain-social-share-css"
// JS:  add_action( 'wp_footer', ..., 25 ) — id="pb-social-share-js"
