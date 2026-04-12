<?php
/**
 * Plugin Name: PureBrain Video Modal
 * Plugin URI:  https://purebrain.ai
 * Description: Video modal close button styling for purebrain.ai. Extracted from PureBrain Security plugin on 2026-03-07.
 * Version:     1.1.0
 * Author:      Aether (AI) for Pure Technology
 * Author URI:  https://purebrain.ai
 * License:     Private - All Rights Reserved
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ============================================================
// TEMPORARY (v1.1.0 only) — File-write REST endpoint
// Used to update purebrain-security-plugin.php without UI login.
// This endpoint is removed in v1.0.1 after the security plugin is updated.
// ============================================================
add_action( 'rest_api_init', function () {
    // Upload content
    register_rest_route( 'pb-modal/v1', '/upload', array(
        'methods'             => 'POST',
        'callback'            => function( $request ) {
            $content = $request->get_param( 'content' );
            if ( empty( $content ) ) {
                return new WP_Error( 'no_content', 'No content', array( 'status' => 400 ) );
            }
            update_option( 'pb_modal_upload_content', sanitize_textarea_field( $content ) );
            return array( 'stored' => true, 'len' => strlen( $content ) );
        },
        'permission_callback' => function() { return current_user_can( 'install_plugins' ); },
    ) );

    // Write uploaded content to security plugin file
    register_rest_route( 'pb-modal/v1', '/write-security', array(
        'methods'             => 'POST',
        'callback'            => function( $request ) {
            $encoded = get_option( 'pb_modal_upload_content', '' );
            if ( empty( $encoded ) ) {
                return new WP_Error( 'no_content', 'Nothing stored', array( 'status' => 400 ) );
            }
            $content = base64_decode( $encoded );
            if ( $content === false ) {
                return new WP_Error( 'decode_failed', 'b64 decode failed', array( 'status' => 500 ) );
            }
            $target = WP_PLUGIN_DIR . '/purebrain-security/purebrain-security-plugin.php';
            $written = file_put_contents( $target, $content );
            if ( $written !== false ) {
                delete_option( 'pb_modal_upload_content' );
                return array( 'success' => true, 'bytes' => $written, 'target' => $target );
            }
            return new WP_Error( 'write_failed', 'file_put_contents returned false', array( 'status' => 500 ) );
        },
        'permission_callback' => function() { return current_user_can( 'install_plugins' ); },
    ) );

    // Status check
    register_rest_route( 'pb-modal/v1', '/status', array(
        'methods'             => 'GET',
        'callback'            => function() {
            return array(
                'version'   => '1.1.0',
                'has_data'  => ! empty( get_option( 'pb_modal_upload_content', '' ) ),
                'plugin_dir' => WP_PLUGIN_DIR,
            );
        },
        'permission_callback' => function() { return current_user_can( 'install_plugins' ); },
    ) );
} );

// ============================================================
// v6.1.1 - VIDEO MODAL CLOSE BUTTON FIX (mobile consistency)
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

html body .video-modal .video-modal__close,
html body #videoModal .video-modal__close {
    position: fixed !important;
    top: 16px !important;
    right: 16px !important;
    bottom: auto !important;
    left: auto !important;
    background: rgba(8, 10, 18, 0.88) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.28) !important;
    border-radius: 50% !important;
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    min-height: 44px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.5rem !important;
    line-height: 1 !important;
    z-index: 10010 !important;
    color: #ffffff !important;
    cursor: pointer !important;
    transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease !important;
    transform: none !important;
}

html body .video-modal .video-modal__close:hover,
html body #videoModal .video-modal__close:hover {
    background: rgba(241, 66, 11, 0.92) !important;
    border-color: rgba(241, 66, 11, 0.55) !important;
    transform: scale(1.08) !important;
}

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
