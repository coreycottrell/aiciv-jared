#!/usr/bin/env python3
"""Quick build script for v486 — minimal, just does the text replacements."""
from pathlib import Path

ROOT = Path('/home/jared/projects/AI-CIV/aether')
SRC  = ROOT / 'exports' / 'purebrain-security-plugin-v485.php'
DST  = ROOT / 'exports' / 'purebrain-security-plugin-v486.php'

content = SRC.read_text(encoding='utf-8')

# 1. Version bump
assert ' * Version:     4.8.5\n' in content, 'Version string not found'
content = content.replace(' * Version:     4.8.5\n', ' * Version:     4.8.6\n', 1)

# 2. Changelog
assert ' *   v4.8.5 - Blog video background fix.' in content, 'Changelog anchor not found'
content = content.replace(
    ' *   v4.8.5 - Blog video background fix.',
    ' *   v4.8.6 - URGENT FIX: Neural Feed subscribe form stuck in "Subscribing..." state.\n'
    ' *            Root cause: XMLHttpRequest .timeout + ontimeout did not fire reliably\n'
    ' *            in all Cloudflare + browser combinations, permanently disabling the\n'
    ' *            Subscribe button. Multiple users reported form "does nothing".\n'
    ' *            Fix: Replace XHR with fetch() + AbortController (15s clean abort).\n'
    ' *            Add 20s JS setTimeout safety net that force-resets button state\n'
    ' *            regardless of network outcome. Add in-flight guard (prevent\n'
    ' *            double-submit). Add specific 503 error message.\n'
    ' *            No PHP endpoint changes. No other functionality affected.\n'
    ' *   v4.8.5 - Blog video background fix.',
    1
)

# 3. Replace doSubscribe function
OLD = '''    // ── API: Subscribe ─────────────────────────────────────────
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

NEW = '''    // ── API: Subscribe (v4.8.6 — fetch + AbortController + 20s safety net) ──
    // BUG FIX: Previous XHR implementation set xhr.timeout but ontimeout did not
    // fire reliably in all Cloudflare + browser combinations. This left the button
    // permanently stuck on "Subscribing..." with disabled state. Multiple users
    // reported the form doing nothing on submit.
    //
    // Fix summary:
    //   1. Use fetch() + AbortController for a reliable 15s clean abort
    //   2. 20s JS setTimeout safety net: force-resets button to enabled state
    //      regardless of what fetch() / the network does — guaranteed recovery
    //   3. In-flight boolean guard prevents double-submit while pending
    //   4. HTTP 503 (BREVO_API_KEY missing from wp-config) now shows specific msg
    var _pbSubscribeInFlight = false; // v4.8.6: in-flight guard

    function doSubscribe(email, onSuccess, onError) {
        // Prevent double-submit
        if (_pbSubscribeInFlight) return;
        _pbSubscribeInFlight = true;

        var controller = (typeof AbortController !== \'undefined\')
            ? new AbortController()
            : null;

        // 20-second hard safety net: force button reset regardless of network
        var safetyTimer = setTimeout(function() {
            if (!_pbSubscribeInFlight) return;
            _pbSubscribeInFlight = false;
            if (controller) { try { controller.abort(); } catch(e) {} }
            onError(\'Request timed out. Please try again.\');
        }, 20000);

        // 15-second AbortController abort (fires before safety net)
        var abortTimer = controller ? setTimeout(function() {
            try { controller.abort(); } catch(e) {}
        }, 15000) : null;

        function cleanup() {
            _pbSubscribeInFlight = false;
            clearTimeout(safetyTimer);
            if (abortTimer !== null) clearTimeout(abortTimer);
        }

        if (typeof fetch === \'function\') {
            var opts = {
                method: \'POST\',
                headers: { \'Content-Type\': \'application/json\' },
                body: JSON.stringify({ email: email })
            };
            if (controller) opts.signal = controller.signal;

            fetch(SUBSCRIBE_URL, opts)
                .then(function(resp) {
                    if (resp.ok) {
                        cleanup();
                        onSuccess();
                        return;
                    }
                    cleanup();
                    if (resp.status === 429) {
                        onError(\'Too many attempts. Please wait a moment.\');
                    } else if (resp.status === 503) {
                        onError(\'Service temporarily unavailable. Please try again soon.\');
                    } else {
                        onError(\'Something went wrong. Please try again.\');
                    }
                })
                .catch(function(err) {
                    cleanup();
                    if (err && err.name === \'AbortError\') {
                        onError(\'Request timed out. Please try again.\');
                    } else {
                        onError(\'Network error. Please try again.\');
                    }
                });
        } else {
            // Fallback XHR for very old browsers without fetch()
            var xhr = new XMLHttpRequest();
            xhr.open(\'POST\', SUBSCRIBE_URL, true);
            xhr.setRequestHeader(\'Content-Type\', \'application/json\');
            xhr.onreadystatechange = function() {
                if (xhr.readyState !== 4) return;
                cleanup();
                if (xhr.status >= 200 && xhr.status < 300) {
                    onSuccess();
                } else if (xhr.status === 429) {
                    onError(\'Too many attempts. Please wait a moment.\');
                } else if (xhr.status === 503) {
                    onError(\'Service temporarily unavailable. Please try again soon.\');
                } else {
                    onError(\'Something went wrong. Please try again.\');
                }
            };
            xhr.onerror = function() { cleanup(); onError(\'Network error. Please try again.\'); };
            xhr.send(JSON.stringify({ email: email }));
        }
    }'''

assert OLD in content, 'doSubscribe function not found — check for whitespace differences'
content = content.replace(OLD, NEW, 1)

DST.write_text(content, encoding='utf-8')
print(f'Written: {DST}')
print(f'Lines: {len(content.splitlines())}')

# Sanity checks
checks = {
    'Version 4.8.6': ' * Version:     4.8.6',
    'v4.8.6 changelog': 'v4.8.6 - URGENT FIX',
    'AbortController': 'AbortController',
    'fetch() check': "typeof fetch === 'function'",
    'Safety timer': 'safetyTimer',
    'In-flight guard': '_pbSubscribeInFlight',
    '503 handling': 'resp.status === 503',
    'cleanup()': 'function cleanup()',
    'No old XHR timeout': 'xhr.timeout = 15000' not in content,
}
all_pass = True
for name, pattern in checks.items():
    ok = pattern if isinstance(pattern, bool) else (pattern in content)
    print(f'  {"PASS" if ok else "FAIL"}: {name}')
    if not ok: all_pass = False

print()
print('BUILD PASSED' if all_pass else 'BUILD FAILED — check above')
