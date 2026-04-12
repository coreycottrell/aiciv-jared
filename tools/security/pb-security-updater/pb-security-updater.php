<?php
/**
 * Plugin Name: PureBrain Security Updater (Temporary)
 * Description: ONE-TIME: Writes the updated purebrain-security-plugin.php on activation. DELETE IMMEDIATELY AFTER USE.
 * Version: 1.0.0
 * Author: Aether (AI) for Pure Technology
 */

if ( ! defined( 'ABSPATH' ) ) exit;

// Run on activation
register_activation_hook( __FILE__, 'pb_security_updater_run' );

function pb_security_updater_run() {
    $plugin_dir = WP_PLUGIN_DIR . '/purebrain-security/';
    $plugin_file = $plugin_dir . 'purebrain-security-plugin.php';

    $encoded_content = get_option( 'pb_security_updater_content', '' );
    if ( empty( $encoded_content ) ) {
        // Content not loaded yet - store status
        update_option( 'pb_security_updater_status', 'no_content' );
        return;
    }

    $content = base64_decode( $encoded_content );
    if ( $content === false ) {
        update_option( 'pb_security_updater_status', 'decode_failed' );
        return;
    }

    $result = file_put_contents( $plugin_file, $content );
    if ( $result !== false ) {
        update_option( 'pb_security_updater_status', 'success:' . $result );
    } else {
        update_option( 'pb_security_updater_status', 'write_failed' );
    }
}

// REST endpoint to receive the plugin content and status check
add_action( 'rest_api_init', function() {
    // Endpoint to upload content
    register_rest_route( 'pb-updater/v1', '/upload', array(
        'methods'             => 'POST',
        'callback'            => 'pb_security_updater_upload',
        'permission_callback' => function( $request ) {
            return current_user_can( 'install_plugins' );
        },
    ) );

    // Endpoint to trigger write
    register_rest_route( 'pb-updater/v1', '/write', array(
        'methods'             => 'POST',
        'callback'            => 'pb_security_updater_write',
        'permission_callback' => function( $request ) {
            return current_user_can( 'install_plugins' );
        },
    ) );

    // Endpoint to check status
    register_rest_route( 'pb-updater/v1', '/status', array(
        'methods'             => 'GET',
        'callback'            => function() {
            return array(
                'status'   => get_option( 'pb_security_updater_status', 'not_run' ),
                'has_data' => ! empty( get_option( 'pb_security_updater_content', '' ) ),
            );
        },
        'permission_callback' => function( $request ) {
            return current_user_can( 'install_plugins' );
        },
    ) );
} );

function pb_security_updater_upload( $request ) {
    $content = $request->get_param( 'content' );
    if ( empty( $content ) ) {
        return new WP_Error( 'no_content', 'No content provided', array( 'status' => 400 ) );
    }
    update_option( 'pb_security_updater_content', $content );
    return array( 'message' => 'Content stored, call /write to apply', 'size' => strlen( $content ) );
}

function pb_security_updater_write( $request ) {
    $plugin_dir  = WP_PLUGIN_DIR . '/purebrain-security/';
    $plugin_file = $plugin_dir . 'purebrain-security-plugin.php';

    $encoded = get_option( 'pb_security_updater_content', '' );
    if ( empty( $encoded ) ) {
        return new WP_Error( 'no_content', 'No content stored, call /upload first', array( 'status' => 400 ) );
    }

    $content = base64_decode( $encoded );
    if ( $content === false ) {
        return new WP_Error( 'decode_failed', 'Base64 decode failed', array( 'status' => 500 ) );
    }

    $result = file_put_contents( $plugin_file, $content );
    if ( $result !== false ) {
        update_option( 'pb_security_updater_status', 'success:' . $result );
        // Cleanup stored content
        delete_option( 'pb_security_updater_content' );
        return array(
            'message'       => 'Security plugin updated successfully',
            'bytes_written' => $result,
        );
    } else {
        update_option( 'pb_security_updater_status', 'write_failed' );
        return new WP_Error( 'write_failed', 'file_put_contents failed', array( 'status' => 500 ) );
    }
}
