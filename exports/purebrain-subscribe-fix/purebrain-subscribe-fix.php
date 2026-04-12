<?php
/**
 * Plugin Name: PureBrain Subscribe Fix
 * Description: Fixes Neural Feed subscribe form stuck "Subscribing..." state — replaces XHR+timeout with fetch()+AbortController override
 * Version: 1.0.0
 * Author: Aether / Pure Technology
 */
if ( ! defined( 'ABSPATH' ) ) exit;

add_action( 'wp_footer', function() {
    if ( ! is_single() ) return; // Only on blog posts
    ?>
    <script id="purebrain-subscribe-fix-js">
    /* PureBrain Subscribe Fix v1.0.0
     * Overrides doSubscribe() injected by security plugin.
     * Uses fetch() + AbortController for reliable Cloudflare+browser compat.
     * Safety net setTimeout ensures button is NEVER permanently stuck.
     */
    (function() {
        if (typeof doSubscribe !== 'function') return;
        var _pbSubscribeInFlight = false;
        doSubscribe = function(email, onSuccess, onError) {
            if (_pbSubscribeInFlight) return;
            _pbSubscribeInFlight = true;
            var controller = (typeof AbortController !== 'undefined') ? new AbortController() : null;
            var safetyTimer = setTimeout(function() {
                if (!_pbSubscribeInFlight) return;
                _pbSubscribeInFlight = false;
                if (controller) { try { controller.abort(); } catch(e) {} }
                onError('Request timed out. Please try again.');
            }, 20000);
            var abortTimer = controller ? setTimeout(function() {
                try { controller.abort(); } catch(e) {}
            }, 15000) : null;
            function cleanup() {
                _pbSubscribeInFlight = false;
                clearTimeout(safetyTimer);
                if (abortTimer !== null) clearTimeout(abortTimer);
            }
            var opts = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            };
            if (controller) opts.signal = controller.signal;
            fetch(SUBSCRIBE_URL, opts)
                .then(function(resp) {
                    cleanup();
                    if (resp.ok) { onSuccess(); return; }
                    if (resp.status === 429) {
                        onError('Too many attempts. Please wait a moment.');
                    } else if (resp.status === 503) {
                        onError('Service temporarily unavailable. Please try again soon.');
                    } else {
                        onError('Something went wrong. Please try again.');
                    }
                })
                .catch(function(err) {
                    cleanup();
                    if (err && err.name === 'AbortError') {
                        onError('Request timed out. Please try again.');
                    } else {
                        onError('Network error. Please try again.');
                    }
                });
        };
    })();
    </script>
    <?php
}, 99999 ); // Priority 99999 — fires well after security plugin's default priority
