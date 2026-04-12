<?php
/**
 * Plugin Name: PureBrain Content Gate
 * Plugin URI:  https://purebrain.ai
 * Description: Content gating for PureBrain pages: WP password-form dark theme (page 859),
 *              portal bypass for password-protected pages, Brainiac Training JS gate bypass,
 *              AI Partnership Guide partial content gate (blur + email unlock), and the
 *              server-side guide-unlock REST endpoint.
 * Version:     1.0.0
 * Author:      Pure Technology
 * License:     Proprietary
 *
 * Extracted from purebrain-security-plugin.php (Task 12 of 14)
 * Extraction date: 2026-03-07
 *
 * Source line ranges (purebrain-security-plugin.php):
 *   g1a-ext  — Lines 693-768   : WP password form dark theme (page 859)
 *   g1a-ext2 — Lines 771-798   : Portal bypass filter (post_password_required)
 *   g1a-js   — Lines 801-828   : Brainiac Training JS gate bypass (wp_footer)
 *   h2       — Lines 1295-1324 : Guide unlock REST route registration
 *   p        — Lines 4842-5312 : AI Partnership Guide content gate (wp_head CSS + wp_footer JS)
 *   function — Lines 1590-1677 : purebrain_guide_unlock() callback
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ============================================================
// g1a-ext) PASSWORD FORM DARK THEME ON PAGE-859 (v4.9.1)
//     The WordPress password protection form renders BEFORE page content,
//     so it ignores the dark CSS inside the page's <!-- wp:html --> block.
//     This hook injects dark theme CSS for .post-password-form on page-id-859
//     via wp_head so it applies before the form renders.
// ============================================================

add_action( 'wp_head', function () {
    if ( ! is_page( 859 ) ) {
        return;
    }
    ?>
<style id="pb-password-form-dark-859">
/* Dark theme for WordPress password protection form on page 859 */
body.page-id-859,
body.page-id-859.tt-magic-cursor {
    background: #080a12 !important;
    background-color: #080a12 !important;
    color: #e8edf3 !important;
    min-height: 100vh;
}
body.page-id-859 .post-password-form {
    background: #0d1120 !important;
    padding: 40px !important;
    border-radius: 12px !important;
    max-width: 500px !important;
    margin: 100px auto !important;
    border: 1px solid rgba(42,147,193,0.25) !important;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5) !important;
}
body.page-id-859 .post-password-form p:first-child {
    color: #c4cdd8 !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
    margin-bottom: 20px !important;
}
body.page-id-859 .post-password-form label {
    color: #e8edf3 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    display: block !important;
    margin-bottom: 8px !important;
}
body.page-id-859 .post-password-form input[type="password"] {
    background: #1a1f36 !important;
    color: #ffffff !important;
    border: 1px solid rgba(42,147,193,0.3) !important;
    padding: 10px 14px !important;
    border-radius: 8px !important;
    width: 100% !important;
    font-size: 15px !important;
    outline: none !important;
    box-sizing: border-box !important;
}
body.page-id-859 .post-password-form input[type="password"]:focus {
    border-color: #2a93c1 !important;
    box-shadow: 0 0 0 2px rgba(42,147,193,0.2) !important;
}
body.page-id-859 .post-password-form input[type="submit"] {
    background: #f1420b !important;
    color: #ffffff !important;
    border: none !important;
    padding: 11px 28px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    margin-top: 12px !important;
    transition: background 0.2s !important;
}
body.page-id-859 .post-password-form input[type="submit"]:hover {
    background: #2a93c1 !important;
}
</style>
    <?php
} );

// ============================================================
// g1a-ext2) PORTAL BYPASS FOR PASSWORD-PROTECTED PAGES (v6.2.7)
//     Portal users are authenticated paying customers.
//     When they click "Brainiac Training" or "Refer & Earn" from the portal sidebar,
//     the link includes ?bypass=portal — skip the password form.
//     Applies to: brainiac-mastermind-training (ID 1115) and refer-and-earn (by slug).
// ============================================================
add_filter( 'post_password_required', function ( $required, $post ) {
    if ( ! $required ) {
        return false;
    }

    // Pages that support portal bypass
    $bypass_ids   = [ 1115, 1298 ];  // brainiac-mastermind-training, refer-and-earn
    $bypass_slugs = [ 'refer-and-earn' ];

    $is_bypassed_id   = in_array( (int) $post->ID, $bypass_ids, true );
    $is_bypassed_slug = in_array( $post->post_name, $bypass_slugs, true );

    if ( ! $is_bypassed_id && ! $is_bypassed_slug ) {
        return $required;
    }

    // Check for portal bypass parameter
    if ( isset( $_GET['bypass'] ) && $_GET['bypass'] === 'portal' ) {
        return false;
    }
    return $required;
}, 10, 2 );

// ============================================================
// g1a-js) BRAINIAC TRAINING JS GATE BYPASS (v6.2.7)
//      The training page uses a JS-based password gate (not WP password).
//      When ?bypass=portal is in the URL, auto-call signIn() to skip the gate.
// ============================================================
add_action( 'wp_footer', function () {
    if ( ! is_page( 1115 ) ) { return; }
    if ( ! isset( $_GET['bypass'] ) || $_GET['bypass'] !== 'portal' ) { return; }
    ?>
    <script>
    (function() {
        // Auto-bypass the JS password gate when coming from portal
        function autoBypass() {
            if (typeof signIn === 'function') {
                signIn();
            } else {
                // signIn not defined yet, retry shortly
                setTimeout(autoBypass, 100);
            }
        }
        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            setTimeout(autoBypass, 50);
        } else {
            document.addEventListener('DOMContentLoaded', function() { setTimeout(autoBypass, 50); });
        }
    })();
    </script>
    <?php
}, 999 );

// ============================================================
// h2) GUIDE UNLOCK REST ROUTE (v4.1.0)
//     Server-side Brevo proxy for the AI Partnership Guide content gate.
//     Accepts email + optional first name, adds contact to Brevo list 3.
//     BREVO_API_KEY read from wp-config.php constant (never exposed client-side).
//     Rate limit: 5 requests per IP per minute.
//     Route: POST /wp-json/purebrain/v1/guide-unlock
//     Body:  { "email": "user@example.com", "first_name": "Jane" }
// ============================================================

add_action( 'rest_api_init', function () {
    register_rest_route( 'purebrain/v1', '/guide-unlock', array(
        'methods'             => 'POST',
        'callback'            => 'pbcg_guide_unlock',
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
} );

/**
 * AI Partnership Guide unlock proxy (v4.1.0).
 * Adds email + optional first name to Brevo list 3 (The Neural Feed).
 * BREVO_API_KEY read from wp-config.php constant.
 * Rate limit: 5 requests per IP per minute.
 *
 * Renamed from purebrain_guide_unlock() to pbcg_guide_unlock() to avoid
 * collision if the parent security plugin is still active during transition.
 *
 * @param WP_REST_Request $request
 * @return WP_REST_Response|WP_Error
 */
function pbcg_guide_unlock( WP_REST_Request $request ) {
    // Rate limit: 5 per minute per IP
    // Re-uses purebrain_check_rate_limit() from the parent security plugin if available;
    // falls back to a no-op pass-through so this plugin works standalone.
    if ( function_exists( 'purebrain_check_rate_limit' ) ) {
        if ( ! purebrain_check_rate_limit( 'guide_unlock', 5, 60 ) ) {
            return new WP_Error( 'rate_limited', 'Too many requests. Please wait a moment.', array( 'status' => 429 ) );
        }
    }

    $email      = sanitize_email( $request->get_param( 'email' ) );
    $first_name = sanitize_text_field( (string) $request->get_param( 'first_name' ) );

    if ( empty( $email ) || ! is_email( $email ) ) {
        return new WP_Error( 'invalid_email', 'Please enter a valid email address.', array( 'status' => 400 ) );
    }

    // Get Brevo API key from wp-config.php constant
    $api_key = defined( 'BREVO_API_KEY' ) ? BREVO_API_KEY : '';

    if ( empty( $api_key ) ) {
        error_log( '[PureBrain Content Gate] BREVO_API_KEY not defined — guide-unlock endpoint returning 503' );
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
        error_log( '[PureBrain Content Gate] Guide unlock Brevo error: ' . $response->get_error_message() );
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

    error_log( '[PureBrain Content Gate] Guide unlock Brevo API error: HTTP ' . $http_code . ' - ' . $body );
    return new WP_Error(
        'brevo_error',
        'Could not complete unlock. Please try again.',
        array( 'status' => 502 )
    );
}

// ============================================================
// p) AI PARTNERSHIP GUIDE CONTENT GATE (v4.1.0)
//    Partial content gate on /ai-partnership-guide/ page.
//    Sections 1-3 visible freely (problem framing).
//    Sections 4-7 hidden behind gradient fade + blurred preview + email form.
//    Email form submits to POST /wp-json/purebrain/v1/guide-unlock (server-side proxy).
//    On success: content revealed, localStorage['pb_guide_unlocked'] = '1'.
//    Return visit: auto-reveals if localStorage key is present.
// ============================================================

add_action( 'wp_head', function () {
    // Only inject on the AI Partnership Guide page
    if ( ! is_page( 'ai-partnership-guide' ) ) {
        return;
    }
    ?>
<style id="pb-guide-gate-css">
/* ============================================================
   AI PARTNERSHIP GUIDE - CONTENT GATE (v4.1.0)
   ============================================================ */

/* Gate wrapper: wraps sections 4-7 */
#pb-guide-gate-wrapper {
    position: relative;
}

/* Blurred preview of gated content */
#pb-guide-gated-content {
    filter: blur(6px) !important;
    pointer-events: none !important;
    user-select: none !important;
    max-height: 320px !important;
    overflow: hidden !important;
    opacity: 0.5 !important;
    transition: filter 0.6s ease, opacity 0.6s ease, max-height 0.8s ease !important;
}

/* Unlocked state - full reveal */
#pb-guide-gated-content.pb-guide-unlocked {
    filter: none !important;
    pointer-events: auto !important;
    user-select: auto !important;
    max-height: none !important;
    overflow: visible !important;
    opacity: 1 !important;
}

/* Gradient fade overlay - sits above the blurred content */
#pb-guide-fade-overlay {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    height: 280px;
    background: linear-gradient(
        to bottom,
        rgba(8, 10, 18, 0) 0%,
        rgba(8, 10, 18, 0.5) 40%,
        rgba(8, 10, 18, 0.88) 70%,
        rgba(8, 10, 18, 1) 100%
    ) !important;
    pointer-events: none;
    z-index: 2;
}

/* Gate form container */
#pb-guide-gate-form-wrapper {
    position: relative;
    z-index: 10;
    margin: 0 auto 48px auto;
    max-width: 540px;
    background: rgba(13, 17, 23, 0.95);
    border: 1px solid rgba(42, 147, 193, 0.35);
    border-radius: 16px;
    padding: 40px 36px;
    text-align: center;
    box-shadow:
        0 0 0 1px rgba(42, 147, 193, 0.12),
        0 12px 48px rgba(0, 0, 0, 0.6),
        0 0 80px rgba(42, 147, 193, 0.06);
}

@media (max-width: 600px) {
    #pb-guide-gate-form-wrapper {
        margin-left: 16px;
        margin-right: 16px;
        padding: 28px 20px;
    }
}

/* Lock icon above the headline */
#pb-guide-gate-form-wrapper .pb-gate-lock-icon {
    font-size: 32px;
    margin-bottom: 14px;
    display: block;
    filter: drop-shadow(0 0 12px rgba(42, 147, 193, 0.4));
}

#pb-guide-gate-form-wrapper h3 {
    color: #ffffff !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    margin: 0 0 10px 0 !important;
    line-height: 1.3 !important;
}

#pb-guide-gate-form-wrapper p {
    color: #8b9bb4 !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
    margin: 0 0 24px 0 !important;
}

/* Form inputs */
#pb-guide-gate-form-wrapper .pb-gate-input {
    display: block;
    width: 100%;
    box-sizing: border-box;
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    font-size: 15px !important;
    padding: 13px 16px !important;
    margin-bottom: 12px !important;
    outline: none !important;
    transition: border-color 0.2s ease !important;
    font-family: inherit !important;
}

#pb-guide-gate-form-wrapper .pb-gate-input:focus {
    border-color: rgba(42, 147, 193, 0.6) !important;
    background: rgba(255, 255, 255, 0.09) !important;
}

#pb-guide-gate-form-wrapper .pb-gate-input::placeholder {
    color: rgba(255, 255, 255, 0.35) !important;
}

/* Submit button - orange bg, white text, hover blue */
#pb-guide-gate-form-wrapper .pb-gate-submit {
    display: block !important;
    width: 100% !important;
    background: #f1420b !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 14px 24px !important;
    cursor: pointer !important;
    transition: background 0.2s ease, transform 0.15s ease !important;
    letter-spacing: 0.03em !important;
    text-transform: uppercase !important;
    font-family: inherit !important;
    margin-top: 4px !important;
}

#pb-guide-gate-form-wrapper .pb-gate-submit:hover {
    background: #2a93c1 !important;
    transform: translateY(-1px) !important;
}

#pb-guide-gate-form-wrapper .pb-gate-submit:active {
    transform: translateY(0) !important;
}

#pb-guide-gate-form-wrapper .pb-gate-submit:disabled {
    opacity: 0.6 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* Privacy note */
#pb-guide-gate-form-wrapper .pb-gate-privacy {
    color: rgba(255, 255, 255, 0.3) !important;
    font-size: 12px !important;
    margin: 14px 0 0 0 !important;
}

/* Status messages */
#pb-guide-gate-form-wrapper .pb-gate-msg {
    font-size: 14px !important;
    margin-top: 12px !important;
    padding: 10px 14px !important;
    border-radius: 6px !important;
    display: none;
}

#pb-guide-gate-form-wrapper .pb-gate-msg.pb-gate-error {
    background: rgba(241, 66, 11, 0.12) !important;
    border: 1px solid rgba(241, 66, 11, 0.3) !important;
    color: #f87a5c !important;
}

#pb-guide-gate-form-wrapper .pb-gate-msg.pb-gate-success {
    background: rgba(42, 147, 193, 0.12) !important;
    border: 1px solid rgba(42, 147, 193, 0.3) !important;
    color: #6ec8e8 !important;
}

/* Full-gate area (includes fade overlay + form) */
#pb-guide-gate-area {
    position: relative;
    margin-top: -60px;
    padding-top: 20px;
}
</style>
    <?php
}, 25 );

add_action( 'wp_footer', function () {
    // Only inject on the AI Partnership Guide page
    if ( ! is_page( 'ai-partnership-guide' ) ) {
        return;
    }
    ?>
<script id="pb-guide-gate-js">
(function() {
    'use strict';

    var LS_KEY = 'pb_guide_unlocked';
    var UNLOCK_ENDPOINT = '/wp-json/purebrain/v1/guide-unlock';

    function isAlreadyUnlocked() {
        try {
            return localStorage.getItem(LS_KEY) === '1';
        } catch(e) {
            return false;
        }
    }

    function markUnlocked() {
        try {
            localStorage.setItem(LS_KEY, '1');
        } catch(e) {}
    }

    function revealContent() {
        var gated = document.getElementById('pb-guide-gated-content');
        var gateArea = document.getElementById('pb-guide-gate-area');
        if (gated) {
            gated.classList.add('pb-guide-unlocked');
        }
        if (gateArea) {
            gateArea.style.display = 'none';
        }
    }

    /**
     * Find the cutoff point: after the 3rd h2/h3 heading that marks a section.
     * The guide has 7 sections identified by h2 headings.
     * We show sections 1-3, gate sections 4-7.
     *
     * Strategy: Find all top-level h2 elements in the post content.
     * Insert the gate after the 3rd h2's section ends (before 4th h2).
     */
    function buildGate() {
        // Find the post content container - try multiple selectors
        var contentEl = (
            document.querySelector('.entry-content') ||
            document.querySelector('.post-content') ||
            document.querySelector('.elementor-widget-theme-post-content') ||
            document.querySelector('.wp-block-post-content') ||
            document.querySelector('article .content') ||
            document.querySelector('main .content') ||
            document.body
        );

        if (!contentEl) return;

        // Collect all h2 elements inside the content
        var headings = Array.prototype.slice.call(contentEl.querySelectorAll('h2'));

        // We need at least 4 headings to gate (show 3, hide the rest)
        if (headings.length < 4) {
            return; // Not enough structure to gate
        }

        // The 4th heading (index 3) is where the gated content begins
        var gateStartEl = headings[3];

        // Collect all sibling elements from gateStartEl onwards
        var allChildren = Array.prototype.slice.call(contentEl.children);
        var gateStartIdx = allChildren.indexOf(gateStartEl);
        if (gateStartIdx === -1) {
            // heading might be nested inside a wrapper - find its container
            // Walk up from gateStartEl until we find a direct child of contentEl
            var walker = gateStartEl;
            while (walker && walker.parentElement !== contentEl) {
                walker = walker.parentElement;
            }
            if (walker && walker.parentElement === contentEl) {
                gateStartIdx = allChildren.indexOf(walker);
            }
        }

        if (gateStartIdx === -1 || gateStartIdx >= allChildren.length) {
            return; // Could not find cutoff
        }

        // Elements to be gated (sections 4-7)
        var toGate = allChildren.slice(gateStartIdx);
        if (toGate.length === 0) return;

        // Create the gated content wrapper
        var gatedWrapper = document.createElement('div');
        gatedWrapper.id = 'pb-guide-gated-content';

        // Move gated elements into the wrapper
        toGate.forEach(function(el) {
            gatedWrapper.appendChild(el);
        });

        // Build the gate area (fade overlay + email form)
        var gateArea = document.createElement('div');
        gateArea.id = 'pb-guide-gate-area';

        // Fade overlay
        var fadeOverlay = document.createElement('div');
        fadeOverlay.id = 'pb-guide-fade-overlay';
        gateArea.appendChild(fadeOverlay);

        // Form wrapper
        var formWrapper = document.createElement('div');
        formWrapper.id = 'pb-guide-gate-form-wrapper';
        formWrapper.innerHTML = [
            '<span class="pb-gate-lock-icon">&#128274;</span>',
            '<h3>You\'re halfway through the guide</h3>',
            '<p>The next 4 sections cover the business case, readiness assessment, how to get started, and FAQ. Enter your email to unlock the full guide instantly.</p>',
            '<form id="pb-guide-gate-form" novalidate>',
            '  <input type="text" class="pb-gate-input" id="pb-gate-firstname" placeholder="First name (optional)" autocomplete="given-name" />',
            '  <input type="email" class="pb-gate-input" id="pb-gate-email" placeholder="Your email address" required autocomplete="email" />',
            '  <button type="submit" class="pb-gate-submit">Unlock the Full Guide</button>',
            '  <p class="pb-gate-privacy">No spam. Unsubscribe anytime. Your data is never shared.</p>',
            '  <div class="pb-gate-msg" id="pb-gate-msg"></div>',
            '</form>'
        ].join('');
        gateArea.appendChild(formWrapper);

        // Build the outer wrapper
        var outerWrapper = document.createElement('div');
        outerWrapper.id = 'pb-guide-gate-wrapper';
        outerWrapper.appendChild(gatedWrapper);
        outerWrapper.appendChild(gateArea);

        // Insert the outer wrapper at the gateStartIdx position in contentEl
        var refNode = allChildren[gateStartIdx]; // This element was moved into gatedWrapper
        // Since we moved it, we append outerWrapper to contentEl
        contentEl.appendChild(outerWrapper);

        // Attach form submit handler
        var form = document.getElementById('pb-guide-gate-form');
        if (form) {
            form.addEventListener('submit', handleFormSubmit);
        }
    }

    function handleFormSubmit(e) {
        e.preventDefault();

        var emailInput     = document.getElementById('pb-gate-email');
        var firstNameInput = document.getElementById('pb-gate-firstname');
        var submitBtn      = document.querySelector('.pb-gate-submit');
        var msgEl          = document.getElementById('pb-gate-msg');

        var email     = emailInput ? emailInput.value.trim() : '';
        var firstName = firstNameInput ? firstNameInput.value.trim() : '';

        // Basic client-side validation
        if (!email || !isValidEmail(email)) {
            showMessage(msgEl, 'Please enter a valid email address.', 'error');
            return;
        }

        // Disable submit while in-flight
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Unlocking...';
        }
        hideMessage(msgEl);

        // POST to our server-side proxy
        var payload = JSON.stringify({ email: email, first_name: firstName });

        var xhr = new XMLHttpRequest();
        xhr.open('POST', UNLOCK_ENDPOINT, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader('X-WP-Nonce', window.pbGuideNonce || '');

        xhr.onload = function() {
            var data = {};
            try { data = JSON.parse(xhr.responseText); } catch(ex) {}

            if (xhr.status === 200 && data.success) {
                // Success
                showMessage(msgEl, 'Check your email for your welcome note. Unlocking now...', 'success');
                markUnlocked();

                setTimeout(function() {
                    revealContent();
                }, 1200);
            } else if (xhr.status === 429) {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Unlock the Full Guide';
                }
                showMessage(msgEl, 'Too many requests. Please wait a moment and try again.', 'error');
            } else {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Unlock the Full Guide';
                }
                var errMsg = (data.message) ? data.message : 'Something went wrong. Please try again.';
                showMessage(msgEl, errMsg, 'error');
            }
        };

        xhr.onerror = function() {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Unlock the Full Guide';
            }
            showMessage(msgEl, 'Network error. Please check your connection and try again.', 'error');
        };

        xhr.send(payload);
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function showMessage(el, text, type) {
        if (!el) return;
        el.textContent = text;
        el.className = 'pb-gate-msg pb-gate-' + type;
        el.style.display = 'block';
    }

    function hideMessage(el) {
        if (!el) return;
        el.style.display = 'none';
    }

    // --- Init ---

    function init() {
        // Check if already unlocked from a previous visit
        if (isAlreadyUnlocked()) {
            // Content will be visible naturally - no gate needed
            // Still build the DOM structure so revealContent() won't error,
            // but immediately reveal
            buildGate();
            revealContent();
            return;
        }

        // Build the gate
        buildGate();
    }

    // Run on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
</script>
    <?php
}, 20 );
