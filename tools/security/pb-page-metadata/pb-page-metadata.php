<?php
/**
 * Plugin Name: PureBrain Page Metadata
 * Plugin URI:  https://purebrain.ai
 * Description: Injects Twitter/X Card meta tags (twitter:card, twitter:site, twitter:title, twitter:description, twitter:image) on all pages. Pulls from Yoast SEO meta with OG fallback chain. Fixes plain-text link previews when sharing on X/Twitter.
 * Version:     1.0.0
 * Author:      Aether (AI) for Pure Technology
 * Author URI:  https://purebrain.ai
 * License:     Proprietary
 *
 * Extracted from purebrain-security-plugin.php (Task 8 of 14)
 * Extraction date: 2026-03-07
 * Source lines:  1048–1127 of purebrain-security-plugin.php
 *
 * Notes:
 *   - Original code lived in section g2b) of the security plugin (v6.1.0 addition).
 *   - Hook runs at wp_head priority 20 — after Yoast (priority 10) to avoid
 *     duplicate twitter: tags if Yoast ever starts outputting them natively.
 *   - Fallback chain: Yoast twitter-title > Yoast og-title > post/page title > site name
 *   - Image fallback chain: Yoast twitter-image > Yoast og-image > featured image > homepage OG image
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ============================================================
// TWITTER/X CARD META TAGS (v6.1.0)
//      Injects twitter:card meta tags on all pages so links
//      shared on X/Twitter show rich preview cards instead of
//      plain text. Pulls from Yoast SEO meta with OG fallback.
// PAGE METADATA (OG/Twitter) — extracted to pb-page-metadata plugin (2026-03-07)
// ============================================================

add_action( 'wp_head', function () {
    // Yoast already outputs og:* tags but NOT twitter:card by default
    // (Twitter Card support requires enabling in Yoast admin panel,
    // which is inaccessible via REST API). We inject directly here.

    $site_handle = '@purebrain_ai';

    // --- twitter:card type ---
    echo '<meta name="twitter:card" content="summary_large_image" />' . "\n";
    echo '<meta name="twitter:site" content="' . esc_attr( $site_handle ) . '" />' . "\n";

    // --- title: Yoast twitter-title > Yoast og-title > post/page title > site name ---
    $tw_title = '';
    if ( is_singular() ) {
        $post_id  = get_the_ID();
        $tw_title = get_post_meta( $post_id, '_yoast_wpseo_twitter-title', true );
        if ( empty( $tw_title ) ) {
            $tw_title = get_post_meta( $post_id, '_yoast_wpseo_opengraph-title', true );
        }
        if ( empty( $tw_title ) ) {
            $tw_title = get_the_title();
        }
    } elseif ( is_home() || is_front_page() ) {
        $tw_title = get_option( 'blogname' );
    } else {
        $tw_title = get_option( 'blogname' );
    }
    if ( ! empty( $tw_title ) ) {
        echo '<meta name="twitter:title" content="' . esc_attr( wp_strip_all_tags( $tw_title ) ) . '" />' . "\n";
    }

    // --- description: Yoast twitter-description > Yoast metadesc > site tagline ---
    $tw_desc = '';
    if ( is_singular() ) {
        $post_id = get_the_ID();
        $tw_desc = get_post_meta( $post_id, '_yoast_wpseo_twitter-description', true );
        if ( empty( $tw_desc ) ) {
            $tw_desc = get_post_meta( $post_id, '_yoast_wpseo_metadesc', true );
        }
    }
    if ( empty( $tw_desc ) ) {
        $tw_desc = get_option( 'blogdescription' );
    }
    if ( ! empty( $tw_desc ) ) {
        echo '<meta name="twitter:description" content="' . esc_attr( wp_strip_all_tags( $tw_desc ) ) . '" />' . "\n";
    }

    // --- image: Yoast twitter-image > Yoast og-image > featured image > site default ---
    $tw_image = '';
    if ( is_singular() ) {
        $post_id  = get_the_ID();
        $tw_image = get_post_meta( $post_id, '_yoast_wpseo_twitter-image', true );
        if ( empty( $tw_image ) ) {
            $tw_image = get_post_meta( $post_id, '_yoast_wpseo_opengraph-image', true );
        }
        if ( empty( $tw_image ) && has_post_thumbnail( $post_id ) ) {
            $thumb = wp_get_attachment_image_src( get_post_thumbnail_id( $post_id ), 'large' );
            if ( $thumb ) {
                $tw_image = $thumb[0];
            }
        }
    }
    // Site-wide fallback: homepage OG image
    if ( empty( $tw_image ) ) {
        $tw_image = get_post_meta( get_option( 'page_on_front' ), '_yoast_wpseo_twitter-image', true );
        if ( empty( $tw_image ) ) {
            $tw_image = get_post_meta( get_option( 'page_on_front' ), '_yoast_wpseo_opengraph-image', true );
        }
    }
    if ( ! empty( $tw_image ) ) {
        echo '<meta name="twitter:image" content="' . esc_url( $tw_image ) . '" />' . "\n";
    }
}, 20 ); // Priority 20 — after Yoast (priority 10) to avoid duplicate twitter: tags if Yoast ever starts outputting them
