<?php
/**
 * Plugin Name: PureBrain 301 Redirects
 * Plugin URI:  https://purebrain.ai
 * Description: Manages permanent 301 redirects for old/renamed URLs on purebrain.ai. Extracted from PureBrain Security plugin (v6.1.0) on 2026-03-07 to keep the security plugin focused on security concerns only.
 * Version:     1.0.0
 * Author:      Aether (AI) for Pure Technology
 * Author URI:  https://purebrain.ai
 * License:     Private - All Rights Reserved
 *
 * Changelog:
 *   v1.0.0 - Initial extraction from PureBrain Security plugin.
 *            /ai-adoption-assessment → /ai-partnership-assessment/ (permanent 301).
 *            Old URL was returning 404. Permanent 301 so search engines transfer
 *            link equity to the canonical URL.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ============================================================
// 301 REDIRECTS FOR OLD SLUGS
//     /ai-adoption-assessment was returning 404. Permanent 301
//     so search engines transfer link equity to canonical URL.
// ============================================================

add_action( 'template_redirect', function () {
    $request_uri = isset( $_SERVER['REQUEST_URI'] ) ? $_SERVER['REQUEST_URI'] : '';
    $path        = trim( parse_url( $request_uri, PHP_URL_PATH ), '/' );

    $redirects = array(
        'ai-adoption-assessment' => '/ai-partnership-assessment/',
    );

    if ( isset( $redirects[ $path ] ) ) {
        wp_redirect( home_url( $redirects[ $path ] ), 301 );
        exit;
    }
}, 1 );
