<?php
/**
 * Plugin Name: PureBrain Cache Control
 * Plugin URI:  https://purebrain.ai
 * Description: Cache exclusion rules for dynamic pages (pay-test, chatbox, sandbox). Prevents WP Super Cache and Cloudflare from caching payment flows, live chatbox sessions, and training content.
 * Version:     1.0.0
 * Author:      Pure Technology
 * License:     Proprietary
 *
 * Extracted from purebrain-security-plugin.php (Task 6 of 14)
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// =============================================================================
// WP SUPER CACHE CONFIGURATION (v6.2.0)
// =============================================================================
// Adds cache exclusion rules for dynamic pages (pay-test, chatbox, sandbox pages).
// Ensures WP Super Cache never serves stale content for pages with:
//   - PayPal payment flows
//   - Live chatbox sessions
//   - Dynamic pricing/bypass logic
//   - Password-gated training content
// =============================================================================

/**
 * Exclude dynamic/payment pages from WP Super Cache.
 *
 * Hook: do_cacheaction('wp_cache_check_cookies') is internal to WP Super Cache.
 * The correct public filter to prevent caching specific pages is to use
 * WordPress's `posts_results` or the `wp_super_cache_exclude` approach.
 *
 * WP Super Cache reads $cache_rejected_uri from wp-cache-config.php.
 * Since we cannot write to that file directly, we use the `wp_cache_themes_exclude`
 * filter and the `WPSC_LEGACY_CACHE` constant bypass approach.
 *
 * Method: On dynamic pages, output a `Vary: Cookie` header which signals
 * WP Super Cache + Cloudflare to NOT cache the response. We also use
 * the `wp_cache_key_cookie_regexps` filter to exclude all sessions.
 */
add_action( 'init', function () {
    // Define pages that must NEVER be cached.
    // These contain PayPal flows, live chatbox, dynamic pricing, bypass logic.
    $dynamic_pages = array(
        // Pay Test pages (PayPal sandbox + live payment flows)
        439,   // pay-test (original)
        468,   // pay-test variant
        688,   // pay-test-sandbox-2
        689,   // pay-test-2
        1232,  // pay-test-sandbox-3
        // Training pages (password-gated content)
        1115,  // brainiac-mastermind-training
        1251,  // training-redirect
        // Video test page
        1118,  // video-test
    );

    // Check if current request is for a dynamic page
    $is_dynamic = false;

    // Check by page ID (after WP is loaded)
    if ( function_exists( 'is_page' ) ) {
        if ( is_page( $dynamic_pages ) ) {
            $is_dynamic = true;
        }
    }

    // Also check by URI slug patterns (catches requests before full WP routing)
    $request_uri = isset( $_SERVER['REQUEST_URI'] ) ? $_SERVER['REQUEST_URI'] : '';
    $dynamic_slugs = array(
        '/pay-test',
        '/pay-test-2',
        '/pay-test-sandbox',
        '/pay-test-sandbox-2',
        '/pay-test-sandbox-3',
        '/training',
        '/brainiac-mastermind-training',
        '/video-test',
    );
    foreach ( $dynamic_slugs as $slug ) {
        if ( strpos( $request_uri, $slug ) === 0 ) {
            $is_dynamic = true;
            break;
        }
    }

    if ( $is_dynamic ) {
        // Send cache-busting headers BEFORE WP Super Cache checks them.
        // WP Super Cache respects Cache-Control: no-cache / no-store.
        // Cloudflare also respects these and marks response as BYPASS.
        if ( ! headers_sent() ) {
            header( 'Cache-Control: no-cache, no-store, must-revalidate, max-age=0', true );
            header( 'Pragma: no-cache', true );
            header( 'Expires: Thu, 01 Jan 1970 00:00:00 GMT', true );
            header( 'Vary: Cookie', true );
        }

        // Define constant that WP Super Cache checks to skip caching this request.
        // This is the official WP Super Cache bypass mechanism.
        if ( ! defined( 'DONOTCACHEPAGE' ) ) {
            define( 'DONOTCACHEPAGE', true );
        }
    }
}, 1 ); // Priority 1 = fires early, before WP Super Cache checks at priority 10


/**
 * Configure WP Super Cache exclusion for dynamic pages via filter.
 *
 * This runs AFTER WordPress is initialized and wp_super_cache is loaded.
 * The filter 'wp_super_cache_exclude' (if available) allows programmatic exclusion.
 */
add_filter( 'wpsc_never_cache_page_ids', function ( $page_ids ) {
    // Add our dynamic pages to WP Super Cache's never-cache list
    $never_cache = array( 439, 468, 688, 689, 1115, 1118, 1232, 1251 );
    return array_unique( array_merge( (array) $page_ids, $never_cache ) );
} );


/**
 * Ensure logged-in users are NEVER served cached pages.
 * WP Super Cache has this on by default, but we enforce it explicitly.
 */
add_action( 'init', function () {
    if ( is_user_logged_in() && ! headers_sent() ) {
        if ( ! defined( 'DONOTCACHEPAGE' ) ) {
            define( 'DONOTCACHEPAGE', true );
        }
    }
}, 2 );
