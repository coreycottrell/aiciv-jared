#!/usr/bin/env python3
"""
Build purebrain-security-plugin-v486.php
Fix: Neural Feed subscribe form stuck in "Subscribing..." state.

Root cause: XHR `.timeout` property was set but the XHR request could hang
indefinitely in certain Cloudflare/browser environments where ontimeout never
fires. This produced a permanently disabled button.

Fix:
  1. Replace XMLHttpRequest with fetch() + AbortController for proper timeout.
  2. Add a hardcoded 20s JS setTimeout safety net that force-resets button state
     regardless of what fetch/network does.
  3. Guard against double-submit via an in-flight flag.
  4. Add 503 handling with human-readable message (BREVO_API_KEY missing from wp-config).
  5. Bump version 4.8.5 → 4.8.6 and update changelog.
"""

import re

SRC = '/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v485.php'
DST = '/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v486.php'

with open(SRC, 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Bump version number ────────────────────────────────────────────────────
content = content.replace(' * Version:     4.8.5\n', ' * Version:     4.8.6\n', 1)

# ── 2. Add changelog entry ────────────────────────────────────────────────────
old_changelog_anchor = ' *   v4.8.5 - Blog video background fix.'
new_changelog_entry = (
    ' *   v4.8.6 - URGENT FIX: Neural Feed subscribe form stuck in "Subscribing..." state.\n'
    ' *            Root cause: XMLHttpRequest .timeout was set but ontimeout callback did\n'
    ' *            not fire reliably in all Cloudflare + browser combinations, leaving the\n'
    ' *            button permanently disabled with "Subscribing..." text.\n'
    ' *            Fix 1: Replace XHR with fetch() + AbortController (explicit 15s abort).\n'
    ' *            Fix 2: Add 20s JS setTimeout safety net — force-resets button to\n'
    ' *            "Subscribe" (inline) / "Get The Neural Feed" (bar) regardless of network.\n'
    ' *            Fix 3: In-flight guard prevents double-submit while request is pending.\n'
    ' *            Fix 4: 503 now shows "Service temporarily unavailable. Try again soon."\n'
    ' *            instead of the generic "Something went wrong" message.\n'
    ' *            No changes to PHP endpoint, Brevo integration, or other functionality.\n'
    ' *   v4.8.5 - Blog video background fix.'
)
content = content.replace(old_changelog_anchor, new_changelog_entry, 1)

# ── 3. Replace the doSubscribe function ──────────────────────────────────────
old_do_subscribe = '''    // ── API: Subscribe ─────────────────────────────────────────
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
    }'''

new_do_subscribe = '''    // ── API: Subscribe (v4.8.6 — fetch + AbortController, 20s safety net) ────
    // Previous XHR implementation used xhr.timeout but ontimeout did not fire
    // reliably in some Cloudflare + browser combinations, permanently disabling
    // the button. fetch() + AbortController is more reliable. A 20s JS setTimeout
    // safety net force-resets button state regardless of what the network does.
    var _pbSubscribeInFlight = false; // guard against double-submit
    function doSubscribe(email, onSuccess, onError) {
        if (_pbSubscribeInFlight) return; // already in progress
        _pbSubscribeInFlight = true;

        var controller = (typeof AbortController !== 'undefined') ? new AbortController() : null;
        var signal     = controller ? controller.signal : undefined;

        // Hard safety net: force-reset button after 20s no matter what
        var safetyTimer = setTimeout(function() {
            if (_pbSubscribeInFlight) {
                _pbSubscribeInFlight = false;
                if (controller) { try { controller.abort(); } catch(e) {} }
                onError('Request timed out. Please try again.');
            }
        }, 20000);

        // 15s abort via AbortController (clean approach)
        var abortTimer = controller ? setTimeout(function() {
            try { controller.abort(); } catch(e) {}
        }, 15000) : null;

        function cleanup() {
            _pbSubscribeInFlight = false;
            clearTimeout(safetyTimer);
            if (abortTimer) clearTimeout(abortTimer);
        }

        // Use fetch() if available, fall back to XHR for very old browsers
        if (typeof fetch === 'function') {
            fetch(SUBSCRIBE_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email }),
                signal: signal
            })
            .then(function(resp) {
                if (resp.ok) { // 200-299
                    return resp.json().then(function(data) {
                        cleanup();
                        onSuccess();
                    }).catch(function() {
                        // Response not JSON but status was OK — treat as success
                        cleanup();
                        onSuccess();
                    });
                } else if (resp.status === 429) {
                    cleanup();
                    onError('Too many attempts. Please wait a moment.');
                } else if (resp.status === 503) {
                    cleanup();
                    onError('Service temporarily unavailable. Please try again soon.');
                } else {
                    cleanup();
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
        } else {
            // Fallback: XMLHttpRequest for very old browsers
            var xhr = new XMLHttpRequest();
            xhr.open('POST', SUBSCRIBE_URL, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function() {
                if (xhr.readyState !== 4) return;
                if (xhr.status >= 200 && xhr.status < 300) {
                    cleanup();
                    onSuccess();
                } else if (xhr.status === 429) {
                    cleanup();
                    onError('Too many attempts. Please wait a moment.');
                } else if (xhr.status === 503) {
                    cleanup();
                    onError('Service temporarily unavailable. Please try again soon.');
                } else {
                    cleanup();
                    onError('Something went wrong. Please try again.');
                }
            };
            xhr.onerror = function() { cleanup(); onError('Network error. Please try again.'); };
            xhr.send(JSON.stringify({ email: email }));
        }
    }'''

if old_do_subscribe in content:
    content = content.replace(old_do_subscribe, new_do_subscribe, 1)
    print('SUCCESS: doSubscribe function replaced.')
else:
    print('ERROR: Could not find old doSubscribe function. Check for whitespace differences.')
    import sys
    sys.exit(1)

# ── 4. Write output ───────────────────────────────────────────────────────────
with open(DST, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Written: {DST}')

# ── 5. Quick sanity checks ───────────────────────────────────────────────────
checks = [
    ('Version 4.8.6', ' * Version:     4.8.6'),
    ('v4.8.6 changelog entry', '   v4.8.6 - URGENT FIX'),
    ('AbortController present', 'AbortController'),
    ('fetch() present', "typeof fetch === 'function'"),
    ('safety timer present', 'safetyTimer'),
    ('in-flight guard present', '_pbSubscribeInFlight'),
    ('503 handling present', 'resp.status === 503'),
    ('cleanup function present', 'function cleanup()'),
]

all_pass = True
for name, pattern in checks:
    if pattern in content:
        print(f'  PASS: {name}')
    else:
        print(f'  FAIL: {name} — pattern not found: {pattern!r}')
        all_pass = False

if all_pass:
    print('\nAll checks passed. v486 ready for deployment.')
else:
    print('\nSome checks failed. Review before deploying.')
