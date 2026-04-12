<?php
/**
 * Plugin Name: PureBrain IndexNow
 * Plugin URI:  https://purebrain.ai
 * Description: IndexNow search engine notification for purebrain.ai. Pings search engines when content is published or updated. Note: Extracted from purebrain-security-plugin.php (Task 7 of 14)
 * Version:     1.0.0
 * Author:      Pure Technology
 * License:     Proprietary
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ============================================================
// INDEXNOW KEY FILE SERVER (v6.0.0)
// Serves the IndexNow verification file at /{key}.txt
// Without this, IndexNow API returns 403 Forbidden because it
// can't verify we own the site. The key file just contains the
// key string itself. Intercepts on init before WordPress routing.
// ============================================================

add_action( 'init', function () {
    $key = '823869521fbf4f33b93e67c781571e20';
    $request_uri = isset( $_SERVER['REQUEST_URI'] ) ? $_SERVER['REQUEST_URI'] : '';
    // Strip query string for comparison
    $path = strtok( $request_uri, '?' );
    if ( $path === '/' . $key . '.txt' ) {
        status_header( 200 );
        header( 'Content-Type: text/plain; charset=utf-8' );
        header( 'Cache-Control: public, max-age=86400' );
        echo $key;
        exit;
    }
}, 1 );

// ============================================================
// INDEXNOW INTEGRATION (v4.3.0)
// Notifies Bing, Yandex, and other IndexNow-compatible search
// engines instantly when content is published or updated.
//
// API Key: 823869521fbf4f33b93e67c781571e20
// Verification file: https://purebrain.ai/823869521fbf4f33b93e67c781571e20.txt
//
// The key file must exist at the site root and contain the key.
// Create it via WP Admin > Plugins > PureBrain Security (see
// tools/security/indexnow-setup.php) or manually upload:
//   File path (on server): {WEBROOT}/823869521fbf4f33b93e67c781571e20.txt
//   File contents:         823869521fbf4f33b93e67c781571e20
//
// Fires on: publish_post (new posts), post_updated (edits to
// already-published posts), and save_post (catch-all for pages).
// Only fires for public, published posts/pages.
// ============================================================

define( 'PUREBRAIN_INDEXNOW_KEY', '823869521fbf4f33b93e67c781571e20' );

/**
 * Submit a single URL to the IndexNow API.
 *
 * @param string $url The fully-qualified URL to submit.
 * @return bool True on success (HTTP 200/202), false on failure.
 */
function purebrain_indexnow_submit( $url ) {
    $key     = PUREBRAIN_INDEXNOW_KEY;
    $host    = wp_parse_url( home_url(), PHP_URL_HOST );

    $body = wp_json_encode( array(
        'host'    => $host,
        'key'     => $key,
        'keyLocation' => home_url( '/' . $key . '.txt' ),
        'urlList' => array( esc_url_raw( $url ) ),
    ) );

    $response = wp_remote_post(
        'https://api.indexnow.org/IndexNow',
        array(
            'headers'   => array( 'Content-Type' => 'application/json; charset=utf-8' ),
            'body'      => $body,
            'timeout'   => 10,
            'sslverify' => true,
        )
    );

    if ( is_wp_error( $response ) ) {
        // Silent fail — IndexNow ping is best-effort, non-critical
        return false;
    }

    $status = wp_remote_retrieve_response_code( $response );
    // IndexNow returns 200 (OK) or 202 (Accepted) on success
    return in_array( (int) $status, array( 200, 202 ), true );
}

/**
 * Fire IndexNow ping when a new post is published.
 * Hook: publish_post fires once when status transitions TO 'publish'.
 *
 * @param int $post_id Post ID.
 */
add_action( 'publish_post', function ( $post_id ) {
    // Bail on autosaves and revisions
    if ( wp_is_post_revision( $post_id ) || wp_is_post_autosave( $post_id ) ) {
        return;
    }

    $post = get_post( $post_id );
    if ( ! $post || $post->post_status !== 'publish' ) {
        return;
    }

    purebrain_indexnow_submit( get_permalink( $post_id ) );
} );

/**
 * Fire IndexNow ping when an already-published post is saved/updated.
 * Hook: save_post fires on every save; we check old + new status to
 * target "published → published" (i.e. edits to live content) as well
 * as new publications for pages (post_type = 'page').
 *
 * @param int     $post_id Post ID.
 * @param WP_Post $post    Post object after save.
 * @param bool    $update  Whether this is an update (true) or new post (false).
 */
add_action( 'save_post', function ( $post_id, $post, $update ) {
    // Bail on autosaves, revisions, and bulk edits
    if (
        wp_is_post_revision( $post_id ) ||
        wp_is_post_autosave( $post_id ) ||
        ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE )
    ) {
        return;
    }

    // Only ping for published content
    if ( $post->post_status !== 'publish' ) {
        return;
    }

    // For 'post' type: publish_post hook above handles new publications.
    // Here we handle: (a) edits to published posts, (b) pages being published/updated.
    $allowed_types = array( 'post', 'page' );
    if ( ! in_array( $post->post_type, $allowed_types, true ) ) {
        return;
    }

    purebrain_indexnow_submit( get_permalink( $post_id ) );
}, 10, 3 );
