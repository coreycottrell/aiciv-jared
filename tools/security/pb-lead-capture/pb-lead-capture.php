<?php
/**
 * Plugin Name: PureBrain Lead Capture
 * Plugin URI:  https://purebrain.ai
 * Description: Email/lead capture for PureBrain.ai — in-content subscribe box,
 *              post-read CTA bar, AI Partnership Guide content gate, and Investor
 *              Intelligence lead form. All Brevo API calls are server-side proxies;
 *              BREVO_API_KEY is read from wp-config.php and never exposed client-side.
 * Version:     1.0.0
 * Author:      Pure Technology / Aether
 * License:     Proprietary
 *
 * Extracted from purebrain-security-plugin.php (Task 9 of 14)
 * Extraction date: 2026-03-07
 *
 * Dependencies:
 *   - BREVO_API_KEY defined in wp-config.php
 *   - PUREBRAIN_BEHIND_CLOUDFLARE (optional) defined in wp-config.php
 *   - WP transients API (rate limiting)
 *   - WP HTTP API (wp_remote_post)
 *   - WP REST API (register_rest_route)
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit; // Prevent direct file access
}

// ============================================================
// HELPER: Get real client IP (Cloudflare-aware)
// LOW-002 (v3.8.0): Only trust CF-Connecting-IP when
// PUREBRAIN_BEHIND_CLOUDFLARE is defined in wp-config.php.
// ============================================================

function pblc_get_client_ip() {
    if ( defined( 'PUREBRAIN_BEHIND_CLOUDFLARE' ) && PUREBRAIN_BEHIND_CLOUDFLARE ) {
        if ( ! empty( $_SERVER['HTTP_CF_CONNECTING_IP'] ) ) {
            return sanitize_text_field( $_SERVER['HTTP_CF_CONNECTING_IP'] );
        }
    }
    return isset( $_SERVER['REMOTE_ADDR'] ) ? $_SERVER['REMOTE_ADDR'] : 'unknown';
}

// ============================================================
// HELPER: Per-IP rate limiter using WP transients
// ============================================================

function pblc_check_rate_limit( $key, $max_requests = 30, $window_seconds = 60 ) {
    $client_ip     = pblc_get_client_ip();
    $transient_key = 'pb_rl_' . md5( $key . '_' . $client_ip );
    $count         = (int) get_transient( $transient_key );
    if ( $count >= $max_requests ) {
        return false;
    }
    set_transient( $transient_key, $count + 1, $window_seconds );
    return true;
}

// ============================================================
// HELPER: Telegram notification (investor lead alerts)
// ============================================================

function pblc_notify_telegram( $message ) {
    $token = '8559081952:AAHcLiEcC3GtQCAHRu5yc86BByiiLDqyjz0';
    $chat  = '548906264';
    wp_remote_post( "https://api.telegram.org/bot{$token}/sendMessage", array(
        'body'    => array( 'chat_id' => $chat, 'text' => $message ),
        'timeout' => 5,
    ) );
}

// ============================================================
// REST ROUTES (registered on rest_api_init)
//
//   h)  POST /wp-json/pb-security/v1/subscribe
//         Blog lead capture — adds email to Brevo list 3 (The Neural Feed).
//
//   h2) POST /wp-json/purebrain/v1/guide-unlock
//         AI Partnership Guide content gate — adds email + optional first name
//         to Brevo list 3.
//
//   h3) POST /wp-json/purebrain/v1/investor-lead
//         Investor Intelligence page — adds email to Brevo list 20 (Investor
//         Brief Requests) and notifies Jared via email + Telegram.
// ============================================================

add_action( 'rest_api_init', function () {

    // ── h) Brevo subscribe proxy (blog lead capture forms) ──────
    // v3.5.0
    // Route: POST /wp-json/pb-security/v1/subscribe
    // Body:  { "email": "user@example.com" }
    // Rate:  5 requests per IP per minute
    register_rest_route( 'pb-security/v1', '/subscribe', array(
        'methods'             => 'POST',
        'callback'            => 'pblc_brevo_subscribe',
        'permission_callback' => '__return_true', // Public - lead capture form
        'args' => array(
            'email' => array(
                'required'          => true,
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_email',
                'validate_callback' => function( $value ) {
                    return is_email( $value );
                },
            ),
        ),
    ) );

    // ── h2) AI Partnership Guide unlock proxy ───────────────────
    // v4.1.0
    // Route: POST /wp-json/purebrain/v1/guide-unlock
    // Body:  { "email": "user@example.com", "first_name": "Jane" }
    // Rate:  5 requests per IP per minute
    register_rest_route( 'purebrain/v1', '/guide-unlock', array(
        'methods'             => 'POST',
        'callback'            => 'pblc_guide_unlock',
        'permission_callback' => '__return_true', // Public - lead capture form
        'args' => array(
            'email' => array(
                'required'          => true,
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_email',
                'validate_callback' => function( $value ) {
                    return is_email( $value );
                },
            ),
            'first_name' => array(
                'required'          => false,
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_text_field',
            ),
        ),
    ) );

    // ── h3) Investor Brief lead capture ─────────────────────────
    // v6.2.3
    // Route: POST /wp-json/purebrain/v1/investor-lead
    // Body:  { "email": "user@example.com" }
    // Rate:  5 requests per IP per minute
    // Adds to Brevo list 20 (Investor Brief Requests).
    // Notifies Jared via wp_mail + Telegram.
    register_rest_route( 'purebrain/v1', '/investor-lead', array(
        'methods'             => 'POST',
        'callback'            => 'pblc_investor_lead',
        'permission_callback' => '__return_true', // Public - lead capture form
        'args' => array(
            'email' => array(
                'required'          => true,
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_email',
                'validate_callback' => 'is_email',
            ),
        ),
    ) );

} );

// ============================================================
// CALLBACK: Brevo subscribe proxy (v3.5.0)
// Adds email to Brevo list 3 (The Neural Feed).
// BREVO_API_KEY read from wp-config.php constant.
// Rate limit: 5 requests per IP per minute.
//
// @param WP_REST_Request $request
// @return WP_REST_Response|WP_Error
// ============================================================

function pblc_brevo_subscribe( WP_REST_Request $request ) {
    // Strict rate limit: 5 per minute per IP (form endpoint, not a bulk API)
    if ( ! pblc_check_rate_limit( 'brevo_subscribe', 5, 60 ) ) {
        return new WP_Error( 'rate_limited', 'Too many requests. Please wait a moment.', array( 'status' => 429 ) );
    }

    $email = sanitize_email( $request->get_param( 'email' ) );

    if ( empty( $email ) || ! is_email( $email ) ) {
        return new WP_Error( 'invalid_email', 'Please enter a valid email address.', array( 'status' => 400 ) );
    }

    // Get Brevo API key from wp-config.php constant
    // Define BREVO_API_KEY in wp-config.php:
    //   define( 'BREVO_API_KEY', 'xkeysib-...' );
    $api_key = defined( 'BREVO_API_KEY' ) ? BREVO_API_KEY : '';

    // MED-003 (v3.8.0): Fail CLOSED — return 503 immediately when API key is absent.
    if ( empty( $api_key ) ) {
        error_log( '[PureBrain Lead Capture] BREVO_API_KEY not defined in wp-config.php — subscribe endpoint returning 503' );
        return new WP_Error(
            'configuration_error',
            'Service unavailable - API key not configured',
            array( 'status' => 503 )
        );
    }

    // Brevo API v3: create contact and add to list 3
    $brevo_url  = 'https://api.brevo.com/v3/contacts';
    $brevo_body = wp_json_encode( array(
        'email'         => $email,
        'listIds'       => array( 3 ),
        'updateEnabled' => true, // Update existing contact if email exists
    ) );

    $response = wp_remote_post( $brevo_url, array(
        'body'    => $brevo_body,
        'headers' => array(
            'Content-Type' => 'application/json',
            'api-key'      => $api_key,
            'Accept'       => 'application/json',
        ),
        'timeout'   => 15,
        'sslverify' => true,
    ) );

    if ( is_wp_error( $response ) ) {
        error_log( '[PureBrain Lead Capture] Brevo subscribe error: ' . $response->get_error_message() );
        return new WP_Error( 'upstream_failed', 'Subscription service unavailable. Please try again.', array( 'status' => 503 ) );
    }

    $http_code = wp_remote_retrieve_response_code( $response );
    $body      = wp_remote_retrieve_body( $response );
    $decoded   = json_decode( $body, true );

    // Brevo returns 201 (created) or 204 (updated existing) on success
    if ( $http_code === 201 || $http_code === 204 ) {
        return rest_ensure_response( array(
            'success' => true,
            'message' => 'subscribed',
        ) );
    }

    // 400 with "Contact already exist" is actually fine (updateEnabled should handle it,
    // but belt-and-suspenders check)
    if ( $http_code === 400 && ! empty( $decoded['message'] ) ) {
        $msg = strtolower( $decoded['message'] );
        if ( strpos( $msg, 'already exist' ) !== false || strpos( $msg, 'duplicate' ) !== false ) {
            return rest_ensure_response( array(
                'success' => true,
                'message' => 'already_subscribed',
            ) );
        }
    }

    error_log( '[PureBrain Lead Capture] Brevo API error: HTTP ' . $http_code . ' - ' . $body );
    return new WP_Error(
        'brevo_error',
        'Could not complete subscription. Please try again.',
        array( 'status' => 502 )
    );
}


// ============================================================
// CALLBACK: AI Partnership Guide unlock proxy (v4.1.0)
// Adds email + optional first name to Brevo list 3 (The Neural Feed).
// BREVO_API_KEY read from wp-config.php constant.
// Rate limit: 5 requests per IP per minute.
//
// @param WP_REST_Request $request
// @return WP_REST_Response|WP_Error
// ============================================================

function pblc_guide_unlock( WP_REST_Request $request ) {
    // Rate limit: 5 per minute per IP
    if ( ! pblc_check_rate_limit( 'guide_unlock', 5, 60 ) ) {
        return new WP_Error( 'rate_limited', 'Too many requests. Please wait a moment.', array( 'status' => 429 ) );
    }

    $email      = sanitize_email( $request->get_param( 'email' ) );
    $first_name = sanitize_text_field( (string) $request->get_param( 'first_name' ) );

    if ( empty( $email ) || ! is_email( $email ) ) {
        return new WP_Error( 'invalid_email', 'Please enter a valid email address.', array( 'status' => 400 ) );
    }

    // Get Brevo API key from wp-config.php constant
    $api_key = defined( 'BREVO_API_KEY' ) ? BREVO_API_KEY : '';

    if ( empty( $api_key ) ) {
        error_log( '[PureBrain Lead Capture] BREVO_API_KEY not defined — guide-unlock endpoint returning 503' );
        return new WP_Error(
            'configuration_error',
            'Service unavailable - API key not configured',
            array( 'status' => 503 )
        );
    }

    // Build Brevo contact payload
    $brevo_payload = array(
        'email'         => $email,
        'listIds'       => array( 3 ), // The Neural Feed
        'updateEnabled' => true,
    );

    // Include FIRSTNAME attribute if provided
    if ( ! empty( $first_name ) ) {
        $brevo_payload['attributes'] = array(
            'FIRSTNAME' => $first_name,
        );
    }

    $brevo_url  = 'https://api.brevo.com/v3/contacts';
    $brevo_body = wp_json_encode( $brevo_payload );

    $response = wp_remote_post( $brevo_url, array(
        'body'    => $brevo_body,
        'headers' => array(
            'Content-Type' => 'application/json',
            'api-key'      => $api_key,
            'Accept'       => 'application/json',
        ),
        'timeout'   => 15,
        'sslverify' => true,
    ) );

    if ( is_wp_error( $response ) ) {
        error_log( '[PureBrain Lead Capture] Guide unlock Brevo error: ' . $response->get_error_message() );
        return new WP_Error( 'upstream_failed', 'Subscription service unavailable. Please try again.', array( 'status' => 503 ) );
    }

    $http_code = wp_remote_retrieve_response_code( $response );
    $body      = wp_remote_retrieve_body( $response );
    $decoded   = json_decode( $body, true );

    // Brevo returns 201 (created) or 204 (updated) on success
    if ( $http_code === 201 || $http_code === 204 ) {
        return rest_ensure_response( array(
            'success' => true,
            'message' => 'unlocked',
        ) );
    }

    // Handle "already exists" gracefully
    if ( $http_code === 400 && ! empty( $decoded['message'] ) ) {
        $msg = strtolower( $decoded['message'] );
        if ( strpos( $msg, 'already exist' ) !== false || strpos( $msg, 'duplicate' ) !== false ) {
            return rest_ensure_response( array(
                'success' => true,
                'message' => 'already_subscribed',
            ) );
        }
    }

    error_log( '[PureBrain Lead Capture] Guide unlock Brevo API error: HTTP ' . $http_code . ' - ' . $body );
    return new WP_Error(
        'brevo_error',
        'Could not complete unlock. Please try again.',
        array( 'status' => 502 )
    );
}


// ============================================================
// CALLBACK: Investor Brief Lead Capture (v6.2.3)
// Adds email to Brevo list 20 (Investor Brief Requests).
// Notifies Jared via wp_mail + Telegram on every submission.
// BREVO_API_KEY read from wp-config.php constant.
// Rate limit: 5 requests per IP per minute.
//
// @param WP_REST_Request $request
// @return WP_REST_Response|WP_Error
// ============================================================

function pblc_investor_lead( WP_REST_Request $request ) {
    // Rate limit: 5 per minute per IP
    if ( ! pblc_check_rate_limit( 'investor_lead', 5, 60 ) ) {
        return new WP_Error( 'rate_limited', 'Too many requests. Please wait a moment.', array( 'status' => 429 ) );
    }

    $email = sanitize_email( $request->get_param( 'email' ) );

    if ( empty( $email ) || ! is_email( $email ) ) {
        return new WP_Error( 'invalid_email', 'Please enter a valid email address.', array( 'status' => 400 ) );
    }

    // Get Brevo API key from wp-config.php constant
    $api_key = defined( 'BREVO_API_KEY' ) ? BREVO_API_KEY : '';

    if ( empty( $api_key ) ) {
        error_log( '[PureBrain Lead Capture] BREVO_API_KEY not defined — investor-lead endpoint returning 503' );
        return new WP_Error(
            'configuration_error',
            'Service unavailable - API key not configured',
            array( 'status' => 503 )
        );
    }

    // Add to Brevo list 20 (Investor Brief Requests)
    $brevo_payload = array(
        'email'         => $email,
        'listIds'       => array( 20 ), // Investor Brief Requests
        'updateEnabled' => true,
        'attributes'    => array(
            'SOURCE' => 'Investor Intelligence Page',
        ),
    );

    $brevo_url  = 'https://api.brevo.com/v3/contacts';
    $brevo_body = wp_json_encode( $brevo_payload );

    $response = wp_remote_post( $brevo_url, array(
        'body'    => $brevo_body,
        'headers' => array(
            'Content-Type' => 'application/json',
            'api-key'      => $api_key,
            'Accept'       => 'application/json',
        ),
        'timeout'   => 15,
        'sslverify' => true,
    ) );

    if ( is_wp_error( $response ) ) {
        error_log( '[PureBrain Lead Capture] Investor lead Brevo error: ' . $response->get_error_message() );
        return new WP_Error( 'upstream_failed', 'Service unavailable. Please try again.', array( 'status' => 503 ) );
    }

    $http_code = wp_remote_retrieve_response_code( $response );
    $body      = wp_remote_retrieve_body( $response );
    $decoded   = json_decode( $body, true );

    // Brevo returns 201 (created) or 204 (updated) on success
    if ( $http_code === 201 || $http_code === 204 ) {
        // Notify Jared immediately — new investor brief request
        wp_mail(
            'jared@puretechnology.nyc',
            '[PureBrain] New Investor Brief Request: ' . $email,
            "New investor brief request submitted on PureBrain.ai\n\n" .
            "Email: " . $email . "\n" .
            "Source: Investor Intelligence Page\n" .
            "Time: " . current_time( 'Y-m-d H:i:s T' ) . "\n\n" .
            "This contact has been added to Brevo list 20 (Investor Brief Requests).\n\n" .
            "— PureBrain.ai notification",
            array(
                'Content-Type: text/plain; charset=UTF-8',
                'From: PureBrain Notifications <no-reply@purebrain.ai>',
            )
        );
        pblc_notify_telegram( "📩 New Investor Brief Request\nEmail: " . $email . "\nSource: Investor Intelligence Page\nTime: " . current_time( 'Y-m-d H:i:s T' ) . "\nAdded to Brevo list 20." );
        return rest_ensure_response( array(
            'success' => true,
            'message' => 'captured',
        ) );
    }

    // Handle duplicate gracefully
    if ( $http_code === 400 && ! empty( $decoded['message'] ) ) {
        $msg = strtolower( $decoded['message'] );
        if ( strpos( $msg, 'already exist' ) !== false || strpos( $msg, 'duplicate' ) !== false ) {
            // Still notify Jared — duplicate re-submission is a warm signal
            wp_mail(
                'jared@puretechnology.nyc',
                '[PureBrain] Investor Brief Re-Request (Already on List): ' . $email,
                "Investor brief form re-submitted — already in Brevo list 20.\n\n" .
                "Email: " . $email . "\n" .
                "Source: Investor Intelligence Page\n" .
                "Time: " . current_time( 'Y-m-d H:i:s T' ) . "\n\n" .
                "Note: This contact was already on the list (warm re-engagement signal).\n\n" .
                "— PureBrain.ai notification",
                array(
                    'Content-Type: text/plain; charset=UTF-8',
                    'From: PureBrain Notifications <no-reply@purebrain.ai>',
                )
            );
            pblc_notify_telegram( "📩 Investor Brief Re-Request (already on list)\nEmail: " . $email . "\nSource: Investor Intelligence Page\nTime: " . current_time( 'Y-m-d H:i:s T' ) . "\nNote: Warm re-engagement signal." );
            return rest_ensure_response( array(
                'success' => true,
                'message' => 'already_captured',
            ) );
        }
    }

    error_log( '[PureBrain Lead Capture] Investor lead Brevo API error: HTTP ' . $http_code . ' - ' . $body );
    return new WP_Error(
        'brevo_error',
        'Could not capture lead. Please try again.',
        array( 'status' => 502 )
    );
}


// ============================================================
// LEAD CAPTURE STYLES (v3.5.0)
//    Injects CSS for both lead capture elements on single posts.
//    1. In-content subscribe box (#pb-lead-inline)
//    2. Post-read floating CTA bar (#pb-lead-bar)
//    Only on body.single-post pages.
//    wp_head priority 25.
// ============================================================

add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-lead-capture-css">
/* ============================================================
   LEAD CAPTURE STYLES v3.5.0
   Two capture points: inline box (50% scroll) + CTA bar (85% scroll)
   Both only on body.single-post.
   ============================================================ */

/* ----------------------------------------------------------
   1. IN-CONTENT SUBSCRIBE BOX
   Appears inline within post content after 50% scroll.
   Slides in from slightly below, fades in.
   ---------------------------------------------------------- */
#pb-lead-inline {
    display: none;
    position: relative;
    margin: 36px auto 36px auto !important;
    max-width: 600px !important;
    background: #0d1117 !important;
    border: 1px solid #2a93c1 !important;
    border-radius: 12px !important;
    padding: 28px 32px 24px 32px !important;
    box-shadow: 0 4px 24px rgba(42, 147, 193, 0.15), 0 1px 4px rgba(0,0,0,0.5) !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    animation: pb-slide-in 0.45s ease forwards;
    box-sizing: border-box !important;
}

#pb-lead-inline.pb-visible {
    display: block !important;
}

@keyframes pb-slide-in {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

#pb-lead-inline .pb-lead-close {
    position: absolute !important;
    top: 12px !important;
    right: 14px !important;
    background: none !important;
    border: none !important;
    color: #6b7280 !important;
    font-size: 20px !important;
    line-height: 1 !important;
    cursor: pointer !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
}

#pb-lead-inline .pb-lead-close:hover {
    color: #9ca3af !important;
    background: rgba(255,255,255,0.05) !important;
}

#pb-lead-inline .pb-lead-eyebrow {
    display: block !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #2a93c1 !important;
    margin-bottom: 8px !important;
}

#pb-lead-inline .pb-lead-headline {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #e5e7eb !important;
    margin: 0 0 16px 0 !important;
    line-height: 1.4 !important;
}

#pb-lead-inline .pb-lead-form {
    display: flex !important;
    gap: 10px !important;
    flex-wrap: wrap !important;
}

#pb-lead-inline .pb-lead-email {
    flex: 1 1 220px !important;
    min-width: 0 !important;
    padding: 10px 14px !important;
    background: #111827 !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
    color: #e5e7eb !important;
    font-size: 14px !important;
    outline: none !important;
    box-sizing: border-box !important;
}

#pb-lead-inline .pb-lead-email:focus {
    border-color: #2a93c1 !important;
    box-shadow: 0 0 0 2px rgba(42,147,193,0.2) !important;
}

#pb-lead-inline .pb-lead-submit {
    flex: 0 0 auto !important;
    padding: 10px 20px !important;
    background: #f1420b !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    transition: background 0.2s !important;
}

#pb-lead-inline .pb-lead-submit:hover:not(:disabled) {
    background: #d63a09 !important;
}

#pb-lead-inline .pb-lead-submit:disabled {
    opacity: 0.6 !important;
    cursor: not-allowed !important;
}

#pb-lead-inline .pb-lead-success {
    display: none;
    margin: 12px 0 0 0 !important;
    font-size: 14px !important;
    color: #34d399 !important;
    font-weight: 500 !important;
}

#pb-lead-inline .pb-lead-error {
    display: none;
    margin: 8px 0 0 0 !important;
    font-size: 13px !important;
    color: #f87171 !important;
}

/* ----------------------------------------------------------
   2. POST-READ CTA BAR
   Fixed bottom bar. Slides up after 85% scroll.
   ---------------------------------------------------------- */
#pb-lead-bar {
    display: none;
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 9990 !important;
    background: #0d1117 !important;
    border-top: 1px solid #2a93c1 !important;
    box-shadow: 0 -4px 24px rgba(0,0,0,0.5) !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    animation: pb-bar-slide-up 0.4s ease forwards;
}

#pb-lead-bar.pb-visible {
    display: block !important;
}

@keyframes pb-bar-slide-up {
    from {
        transform: translateY(100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

#pb-lead-bar .pb-bar-close {
    position: absolute !important;
    top: 10px !important;
    right: 14px !important;
    background: none !important;
    border: none !important;
    color: #6b7280 !important;
    font-size: 22px !important;
    line-height: 1 !important;
    cursor: pointer !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    z-index: 1 !important;
}

#pb-lead-bar .pb-bar-close:hover {
    color: #9ca3af !important;
}

#pb-lead-bar .pb-bar-inner {
    display: flex !important;
    align-items: center !important;
    gap: 20px !important;
    max-width: 960px !important;
    margin: 0 auto !important;
    padding: 16px 52px 16px 20px !important;
    flex-wrap: wrap !important;
}

#pb-lead-bar .pb-bar-text {
    flex: 1 1 280px !important;
    min-width: 0 !important;
}

#pb-lead-bar .pb-bar-headline {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #e5e7eb !important;
    margin: 0 0 4px 0 !important;
    line-height: 1.3 !important;
}

#pb-lead-bar .pb-bar-subline {
    font-size: 13px !important;
    color: #9ca3af !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}

#pb-lead-bar .pb-bar-form {
    display: flex !important;
    gap: 10px !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    flex: 1 1 300px !important;
    min-width: 0 !important;
}

#pb-lead-bar .pb-bar-email {
    flex: 1 1 180px !important;
    min-width: 0 !important;
    padding: 9px 13px !important;
    background: #111827 !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
    color: #e5e7eb !important;
    font-size: 14px !important;
    outline: none !important;
    box-sizing: border-box !important;
}

#pb-lead-bar .pb-bar-email:focus {
    border-color: #2a93c1 !important;
    box-shadow: 0 0 0 2px rgba(42,147,193,0.2) !important;
}

#pb-lead-bar .pb-bar-submit {
    flex: 0 0 auto !important;
    padding: 9px 18px !important;
    background: #f1420b !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    transition: background 0.2s !important;
}

#pb-lead-bar .pb-bar-submit:hover:not(:disabled) {
    background: #d63a09 !important;
}

#pb-lead-bar .pb-bar-submit:disabled {
    opacity: 0.6 !important;
    cursor: not-allowed !important;
}

#pb-lead-bar .pb-bar-error {
    display: none;
    width: 100% !important;
    margin: 6px 0 0 0 !important;
    font-size: 13px !important;
    color: #f87171 !important;
}

#pb-lead-bar .pb-bar-success {
    display: none;
    padding: 14px 20px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #34d399 !important;
    text-align: center !important;
}

/* ----------------------------------------------------------
   Responsive: stack bar form vertically on narrow screens
   ---------------------------------------------------------- */
@media (max-width: 600px) {
    #pb-lead-bar .pb-bar-inner {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 12px !important;
        padding: 16px 44px 16px 16px !important;
    }

    #pb-lead-bar .pb-bar-text {
        width: 100% !important;
    }

    #pb-lead-bar .pb-bar-form {
        width: 100% !important;
    }

    #pb-lead-bar .pb-bar-submit {
        width: 100% !important;
        text-align: center !important;
    }

    #pb-lead-inline {
        padding: 20px 18px 18px 18px !important;
    }
}
</style>
    <?php
}, 25 );


// ============================================================
// LEAD CAPTURE MARKUP + JAVASCRIPT (v3.5.0)
//    Injects both lead capture elements and scroll-triggered
//    JavaScript on single blog posts only.
//    wp_footer priority 25 — after other footer hooks but before
//    the nav menu JS (priority default 10).
// ============================================================

add_action( 'wp_footer', function () {
    if ( ! is_single() ) {
        return;
    }
    $subscribe_url = esc_url( rest_url( 'pb-security/v1/subscribe' ) );
    ?>
<!-- Lead Capture: In-Content Subscribe Box -->
<div id="pb-lead-inline" role="complementary" aria-label="Subscribe to The Neural Feed" aria-live="polite">
    <button class="pb-lead-close" type="button" aria-label="Dismiss subscription offer">&times;</button>
    <span class="pb-lead-eyebrow">The Neural Feed</span>
    <p class="pb-lead-headline">Enjoying this? Aether writes more like this every day in The Neural Feed.</p>
    <div class="pb-lead-form">
        <input class="pb-lead-email" type="email" placeholder="your@email.com" autocomplete="email" aria-label="Email address" />
        <button class="pb-lead-submit" type="button">Subscribe</button>
    </div>
    <p class="pb-lead-success">Welcome to The Neural Feed. Check your inbox &#x2014; Aether is waiting.</p>
    <p class="pb-lead-error"></p>
</div>

<!-- Lead Capture: Post-Read CTA Bar -->
<div id="pb-lead-bar" role="complementary" aria-label="Subscribe to The Neural Feed" aria-live="polite">
    <button class="pb-bar-close" type="button" aria-label="Dismiss">&times;</button>
    <div class="pb-bar-inner">
        <div class="pb-bar-text">
            <p class="pb-bar-headline">You made it to the end. That means you take AI seriously. So does Aether.</p>
            <p class="pb-bar-subline">Get The Neural Feed &#x2014; AI partnership insights from inside the partnership. Free.</p>
        </div>
        <div class="pb-bar-form">
            <input class="pb-bar-email" type="email" placeholder="your@email.com" autocomplete="email" aria-label="Email address" />
            <button class="pb-bar-submit" type="button">Get The Neural Feed</button>
            <p class="pb-bar-error"></p>
        </div>
        <p class="pb-bar-success">Welcome to The Neural Feed. Check your inbox &#x2014; Aether is waiting.</p>
    </div>
</div>

<script id="purebrain-lead-capture-js">
(function() {
    'use strict';

    var SUBSCRIBE_URL = '<?php echo $subscribe_url; ?>';

    // ── localStorage keys ──────────────────────────────────────
    var LS_SUBSCRIBED       = 'pb_subscribed';        // Set when user subscribes
    var LS_INLINE_DISMISSED = 'pb_inline_dismissed';  // Timestamp of inline dismiss
    var LS_BAR_DISMISSED    = 'pb_bar_dismissed';     // Timestamp of bar dismiss
    var INLINE_DISMISS_TTL  = 7  * 24 * 60 * 60 * 1000; // 7 days in ms
    var BAR_DISMISS_TTL     = 14 * 24 * 60 * 60 * 1000; // 14 days in ms

    // ── State ──────────────────────────────────────────────────
    var inlineShown    = false;
    var barShown       = false;
    var inlineConverted = false; // Track whether user subscribed via inline form

    // ── Helper: check dismissal TTL ───────────────────────────
    function isDismissed(key, ttl) {
        try {
            var ts = localStorage.getItem(key);
            if (!ts) return false;
            return (Date.now() - parseInt(ts, 10)) < ttl;
        } catch(e) {
            return false;
        }
    }

    // ── Helper: read localStorage flag ────────────────────────
    function getFlag(key) {
        try { return localStorage.getItem(key); } catch(e) { return null; }
    }

    // ── Helper: set localStorage flag ────────────────────────
    function setFlag(key, value) {
        try { localStorage.setItem(key, value); } catch(e) {}
    }

    // ── Helper: calculate scroll depth % ──────────────────────
    function scrollDepth() {
        var scrollTop  = window.scrollY || document.documentElement.scrollTop || 0;
        var docHeight  = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        if (docHeight <= 0) return 100;
        return Math.min(100, Math.round((scrollTop / docHeight) * 100));
    }

    // ── Helper: inject inline box before CTA block ────────────
    // Finds the .blog-cta-block and inserts the inline box before it.
    // Falls back to appending after .post-content if no CTA block found.
    function injectInlineBox() {
        var box = document.getElementById('pb-lead-inline');
        if (!box) return;

        var ctaBlock = document.querySelector('.blog-cta-block');
        var postContent = document.querySelector('.post-content');

        if (ctaBlock && ctaBlock.parentNode) {
            ctaBlock.parentNode.insertBefore(box, ctaBlock);
        } else if (postContent) {
            postContent.appendChild(box);
        } else {
            // Last resort: put it before the legal footer
            var footer = document.getElementById('purebrain-legal-footer');
            if (footer && footer.parentNode) {
                footer.parentNode.insertBefore(box, footer);
            }
        }
    }

    // ── Show / hide inline box ─────────────────────────────────
    function showInline() {
        if (inlineShown) return;
        inlineShown = true;
        var box = document.getElementById('pb-lead-inline');
        if (box) {
            box.classList.add('pb-visible');
            box.querySelector('.pb-lead-email') && box.querySelector('.pb-lead-email').focus();
        }
    }

    function hideInline() {
        var box = document.getElementById('pb-lead-inline');
        if (box) {
            box.classList.remove('pb-visible');
            box.style.display = 'none';
        }
    }

    // ── Show / hide bar ────────────────────────────────────────
    function showBar() {
        if (barShown) return;
        // Don't show bar if user already subscribed via inline form
        if (inlineConverted) return;
        barShown = true;
        var bar = document.getElementById('pb-lead-bar');
        if (bar) {
            bar.classList.add('pb-visible');
        }
    }

    function hideBar() {
        var bar = document.getElementById('pb-lead-bar');
        if (bar) {
            bar.classList.remove('pb-visible');
            bar.style.display = 'none';
        }
    }

    // ── API: Subscribe ─────────────────────────────────────────
    function doSubscribe(email, onSuccess, onError) {
        var body = JSON.stringify({ email: email });
        var xhr  = new XMLHttpRequest();
        xhr.open('POST', SUBSCRIBE_URL, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.timeout = 15000;
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== 4) return;
            if (xhr.status === 200 || xhr.status === 201) {
                try {
                    var resp = JSON.parse(xhr.responseText);
                    if (resp && resp.success) {
                        onSuccess();
                        return;
                    }
                } catch(e) {}
                onSuccess(); // Treat any 200/201 as success
            } else if (xhr.status === 429) {
                onError('Too many attempts. Please wait a moment.');
            } else {
                onError('Something went wrong. Please try again.');
            }
        };
        xhr.ontimeout = function() {
            onError('Request timed out. Please try again.');
        };
        xhr.onerror = function() {
            onError('Network error. Please try again.');
        };
        xhr.send(body);
    }

    // ── Wire up inline form ────────────────────────────────────
    function initInlineForm() {
        var box        = document.getElementById('pb-lead-inline');
        if (!box) return;

        var closeBtn   = box.querySelector('.pb-lead-close');
        var emailInput = box.querySelector('.pb-lead-email');
        var submitBtn  = box.querySelector('.pb-lead-submit');
        var successMsg = box.querySelector('.pb-lead-success');
        var errorMsg   = box.querySelector('.pb-lead-error');

        closeBtn && closeBtn.addEventListener('click', function() {
            setFlag(LS_INLINE_DISMISSED, String(Date.now()));
            hideInline();
        });

        function handleInlineSubmit() {
            var email = emailInput ? emailInput.value.trim() : '';
            if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                if (errorMsg) {
                    errorMsg.textContent = 'Please enter a valid email address.';
                    errorMsg.style.display = 'block';
                }
                return;
            }

            if (errorMsg) errorMsg.style.display = 'none';
            if (submitBtn) submitBtn.disabled = true;
            if (submitBtn) submitBtn.textContent = 'Subscribing\u2026';

            doSubscribe(email, function() {
                // Success
                setFlag(LS_SUBSCRIBED, 'true');
                inlineConverted = true;
                if (box.querySelector('.pb-lead-form')) {
                    box.querySelector('.pb-lead-form').style.display = 'none';
                }
                if (successMsg) successMsg.style.display = 'block';
                // Hide the bar since user just subscribed
                hideBar();
            }, function(errText) {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Subscribe';
                }
                if (errorMsg) {
                    errorMsg.textContent = errText;
                    errorMsg.style.display = 'block';
                }
            });
        }

        submitBtn && submitBtn.addEventListener('click', handleInlineSubmit);
        emailInput && emailInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') handleInlineSubmit();
        });
    }

    // ── Wire up bar form ───────────────────────────────────────
    function initBarForm() {
        var bar        = document.getElementById('pb-lead-bar');
        if (!bar) return;

        var closeBtn   = bar.querySelector('.pb-bar-close');
        var emailInput = bar.querySelector('.pb-bar-email');
        var submitBtn  = bar.querySelector('.pb-bar-submit');
        var successMsg = bar.querySelector('.pb-bar-success');
        var errorMsg   = bar.querySelector('.pb-bar-error');
        var formDiv    = bar.querySelector('.pb-bar-form');

        closeBtn && closeBtn.addEventListener('click', function() {
            setFlag(LS_BAR_DISMISSED, String(Date.now()));
            hideBar();
        });

        function handleBarSubmit() {
            var email = emailInput ? emailInput.value.trim() : '';
            if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                if (errorMsg) {
                    errorMsg.textContent = 'Please enter a valid email address.';
                    errorMsg.style.display = 'block';
                }
                return;
            }

            if (errorMsg) errorMsg.style.display = 'none';
            if (submitBtn) submitBtn.disabled = true;
            if (submitBtn) submitBtn.textContent = 'Joining\u2026';

            doSubscribe(email, function() {
                setFlag(LS_SUBSCRIBED, 'true');
                if (formDiv) formDiv.style.display = 'none';
                var textDiv = bar.querySelector('.pb-bar-text');
                if (textDiv) textDiv.style.display = 'none';
                if (successMsg) successMsg.style.display = 'block';
                // Auto-dismiss bar after 4 seconds on success
                setTimeout(function() { hideBar(); }, 4000);
            }, function(errText) {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Get The Neural Feed';
                }
                if (errorMsg) {
                    errorMsg.textContent = errText;
                    errorMsg.style.display = 'block';
                }
            });
        }

        submitBtn && submitBtn.addEventListener('click', handleBarSubmit);
        emailInput && emailInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') handleBarSubmit();
        });
    }

    // ── Main scroll handler ────────────────────────────────────
    function onScroll() {
        var depth = scrollDepth();

        // 50% threshold: show inline box
        if (depth >= 50 && !inlineShown) {
            // Only show if not already subscribed and not recently dismissed
            if (!getFlag(LS_SUBSCRIBED) && !isDismissed(LS_INLINE_DISMISSED, INLINE_DISMISS_TTL)) {
                showInline();
            }
        }

        // 85% threshold: show bar
        if (depth >= 85 && !barShown) {
            // Only show if not already subscribed and not recently dismissed
            if (!getFlag(LS_SUBSCRIBED) && !isDismissed(LS_BAR_DISMISSED, BAR_DISMISS_TTL)) {
                showBar();
            }
        }
    }

    // ── Init ──────────────────────────────────────────────────
    function init() {
        // Only run on single post pages (double-check body class)
        if (!document.body.classList.contains('single-post')) return;

        // Early exit: already subscribed, no need to set anything up
        if (getFlag(LS_SUBSCRIBED)) return;

        // Inject inline box into the DOM at correct position
        injectInlineBox();

        // Wire up form event handlers
        initInlineForm();
        initBarForm();

        // Attach scroll listener (passive for performance)
        window.addEventListener('scroll', onScroll, { passive: true });

        // Check on init in case page is already scrolled (e.g. anchor link)
        onScroll();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
</script>
    <?php
}, 25 );
