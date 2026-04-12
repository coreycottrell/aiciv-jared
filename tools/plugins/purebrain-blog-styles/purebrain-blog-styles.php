<?php
/**
 * Plugin Name: PureBrain Blog Styles
 * Description: Blog post styling — semi-transparent background behind text content, and other blog-specific CSS.
 * Version:     1.0.0
 * Author:      Aether (AI) for Pure Technology
 */

if ( ! defined( 'ABSPATH' ) ) exit;

add_action( 'wp_head', function () {
    if ( ! is_single() ) return; // Only on single blog posts
    ?>
    <style id="pb-blog-styles">
    /* Semi-transparent background behind blog text content — 43% opacity */
    body.single-post .post-content .pb-blog-post,
    body.single-post .post-content article {
        background: rgba(10, 14, 26, 0.43);
        border-radius: 12px;
        padding: 32px 36px;
        margin: 0 auto;
        backdrop-filter: blur(2px);
        -webkit-backdrop-filter: blur(2px);
    }
    /* Mobile: tighter padding */
    @media (max-width: 767px) {
        body.single-post .post-content .pb-blog-post,
        body.single-post .post-content article {
            padding: 20px 16px;
            border-radius: 8px;
        }
    }
    </style>
    <?php
}, 999 );
