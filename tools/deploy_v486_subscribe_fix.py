#!/usr/bin/env python3
"""
Neural Feed Subscribe Form Fix — Deploy v486
============================================
This script:
1. Reads the local v485 plugin file
2. Applies the doSubscribe() fix (fetch + AbortController + safety timer)
3. Bumps version to 4.8.6
4. Saves as v486 locally
5. Deploys to purebrain.ai via WordPress REST API (plugin file upload)

Root cause of "Subscribing..." stuck button:
  XMLHttpRequest .timeout + ontimeout did not fire reliably in some
  Cloudflare + browser combinations. The fetch() API with AbortController
  is the correct modern approach. A 20s safety net timer guarantees
  button reset regardless of network state.
"""

import os
import sys
import requests
import json
from pathlib import Path

# ─── Config ────────────────────────────────────────────────────────────────────
AETHER_ROOT = Path('/home/jared/projects/AI-CIV/aether')
SRC_FILE    = AETHER_ROOT / 'exports' / 'purebrain-security-plugin-v485.php'
DST_FILE    = AETHER_ROOT / 'exports' / 'purebrain-security-plugin-v486.php'

WP_URL      = 'https://purebrain.ai'
WP_USER     = 'Aether'
WP_PASS     = 'ZGuh 1W8k WpWM c9iy kqyd buPr'  # App password from .env

# Plugin file path relative to WordPress plugins directory on server
PLUGIN_SLUG = 'purebrain-security-hardening/purebrain-security-hardening.php'

# ─── OLD doSubscribe to find and replace ──────────────────────────────────────
OLD_DO_SUBSCRIBE = '''    // ── API: Subscribe ─────────────────────────────────────────
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

NEW_DO_SUBSCRIBE = '''    // ── API: Subscribe (v4.8.6 — fetch + AbortController + 20s safety net) ──
    // Previous XHR implementation: xhr.timeout + ontimeout did not fire reliably
    // in some Cloudflare + browser combinations, permanently disabling the button
    // and leaving users stuck on "Subscribing...". Multiple users reported this.
    //
    // Fix:
    //   1. fetch() + AbortController for clean 15s abort
    //   2. 20s JS setTimeout safety net: force-resets button regardless of network
    //   3. In-flight guard prevents double-submit while request is pending
    //   4. 503 gets specific "Service temporarily unavailable" message
    var _pbSubscribeInFlight = false;

    function doSubscribe(email, onSuccess, onError) {
        // Guard: ignore if already in-flight
        if (_pbSubscribeInFlight) return;
        _pbSubscribeInFlight = true;

        var controller = (typeof AbortController !== 'undefined')
            ? new AbortController()
            : null;

        // 20-second safety net: force-reset button state regardless of what
        // the network does. This fires even if fetch() never resolves/rejects.
        var safetyTimer = setTimeout(function() {
            if (!_pbSubscribeInFlight) return; // already resolved cleanly
            _pbSubscribeInFlight = false;
            if (controller) { try { controller.abort(); } catch(e) {} }
            onError('Request timed out. Please try again.');
        }, 20000);

        // 15-second AbortController (clean abort before safety net fires)
        var abortTimer = controller ? setTimeout(function() {
            try { controller.abort(); } catch(e) {}
        }, 15000) : null;

        function cleanup() {
            _pbSubscribeInFlight = false;
            clearTimeout(safetyTimer);
            if (abortTimer !== null) clearTimeout(abortTimer);
        }

        // fetch() with AbortController (all modern browsers + Chrome 66+)
        if (typeof fetch === 'function') {
            var fetchOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            };
            if (controller) fetchOptions.signal = controller.signal;

            fetch(SUBSCRIBE_URL, fetchOptions)
                .then(function(resp) {
                    if (resp.ok) {
                        // 200-299: treat as success regardless of JSON body
                        return resp.json()
                            .then(function() { cleanup(); onSuccess(); })
                            .catch(function() { cleanup(); onSuccess(); });
                    }
                    // Error status codes
                    if (resp.status === 429) {
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
            // Fallback: XMLHttpRequest for browsers without fetch() (very rare)
            var xhr = new XMLHttpRequest();
            xhr.open('POST', SUBSCRIBE_URL, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function() {
                if (xhr.readyState !== 4) return;
                if (xhr.status >= 200 && xhr.status < 300) {
                    cleanup(); onSuccess();
                } else if (xhr.status === 429) {
                    cleanup(); onError('Too many attempts. Please wait a moment.');
                } else if (xhr.status === 503) {
                    cleanup(); onError('Service temporarily unavailable. Please try again soon.');
                } else {
                    cleanup(); onError('Something went wrong. Please try again.');
                }
            };
            xhr.onerror = function() { cleanup(); onError('Network error. Please try again.'); };
            xhr.send(JSON.stringify({ email: email }));
        }
    }'''

# ─── Changelog entry to insert ────────────────────────────────────────────────
OLD_CHANGELOG_ANCHOR = ' *   v4.8.5 - Blog video background fix.'
NEW_CHANGELOG_ENTRY = (
    ' *   v4.8.6 - URGENT FIX: Neural Feed subscribe form stuck in "Subscribing..." state.\n'
    ' *            Root cause: XMLHttpRequest .timeout + ontimeout did not fire reliably\n'
    ' *            in some Cloudflare + browser combinations. Button was permanently\n'
    ' *            disabled. Multiple users reported form "does nothing".\n'
    ' *            Fix: Replace XHR with fetch() + AbortController (15s clean abort).\n'
    ' *            Add 20s JS setTimeout safety net that force-resets button to enabled\n'
    ' *            state regardless of what the network does. Add in-flight guard to\n'
    ' *            prevent double-submit. Add specific 503 error message.\n'
    ' *            No PHP endpoint changes. No other functionality affected.\n'
    ' *   v4.8.5 - Blog video background fix.'
)


def build_v486():
    """Read v485, apply fixes, write v486."""
    print(f'Reading: {SRC_FILE}')
    with open(SRC_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Bump version
    if ' * Version:     4.8.5' not in content:
        print('ERROR: Version string not found.')
        return False
    content = content.replace(' * Version:     4.8.5\n', ' * Version:     4.8.6\n', 1)
    print('  Version bumped to 4.8.6')

    # 2. Add changelog entry
    if OLD_CHANGELOG_ANCHOR not in content:
        print('ERROR: Changelog anchor not found.')
        return False
    content = content.replace(OLD_CHANGELOG_ANCHOR, NEW_CHANGELOG_ENTRY, 1)
    print('  Changelog entry added')

    # 3. Replace doSubscribe
    if OLD_DO_SUBSCRIBE not in content:
        print('ERROR: doSubscribe function not found. Checking for whitespace differences...')
        # Debug: show what's around that area
        idx = content.find('function doSubscribe')
        if idx >= 0:
            print(f'  Found doSubscribe at char {idx}. Showing context:')
            print(repr(content[idx:idx+200]))
        return False
    content = content.replace(OLD_DO_SUBSCRIBE, NEW_DO_SUBSCRIBE, 1)
    print('  doSubscribe function replaced with fetch() + AbortController version')

    # 4. Write output
    with open(DST_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  Written: {DST_FILE}')

    # 5. Sanity checks
    checks = [
        ('Version 4.8.6', ' * Version:     4.8.6'),
        ('v4.8.6 changelog', 'v4.8.6 - URGENT FIX'),
        ('AbortController', 'AbortController'),
        ('fetch() check', "typeof fetch === 'function'"),
        ('Safety timer', 'safetyTimer'),
        ('In-flight guard', '_pbSubscribeInFlight'),
        ('503 handling', 'resp.status === 503'),
        ('cleanup()', 'function cleanup()'),
        ('Original v485 not present', '4.8.5' not in content.split('4.8.6')[0]),
    ]
    all_pass = True
    for name, pattern in checks:
        if isinstance(pattern, bool):
            ok = pattern
        else:
            ok = pattern in content
        status = 'PASS' if ok else 'FAIL'
        print(f'  {status}: {name}')
        if not ok:
            all_pass = False

    return all_pass


def deploy_to_wordpress(plugin_content: str) -> bool:
    """Deploy plugin to WordPress via REST API plugin upload."""
    # WordPress REST API requires multipart upload for plugin files
    # We'll use the wp/v2/plugins endpoint (WP 5.5+)
    auth = (WP_USER, WP_PASS)

    # First: check current plugin status
    print(f'\nChecking current plugin status at {WP_URL}...')
    resp = requests.get(
        f'{WP_URL}/wp-json/wp/v2/plugins',
        auth=auth,
        timeout=30
    )
    if resp.status_code != 200:
        print(f'  Cannot list plugins (HTTP {resp.status_code}). Will try direct file write approach.')
        return deploy_via_plugin_file_api(plugin_content)

    plugins = resp.json()
    security_plugin = None
    for p in plugins:
        if 'purebrain' in p.get('plugin', '').lower() and 'security' in p.get('plugin', '').lower():
            security_plugin = p
            break

    if security_plugin:
        print(f'  Found plugin: {security_plugin.get("plugin")} v{security_plugin.get("version")}')
    else:
        print('  Security plugin not found in plugin list. Trying direct upload...')

    return deploy_via_plugin_file_api(plugin_content)


def deploy_via_plugin_file_api(plugin_content: str) -> bool:
    """Upload plugin zip via WP REST API."""
    import io
    import zipfile
    import tempfile

    auth = (WP_USER, WP_PASS)

    # Create zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('purebrain-security-hardening/purebrain-security-hardening.php', plugin_content)
    zip_buffer.seek(0)

    print(f'\nUploading plugin zip to {WP_URL}/wp-json/wp/v2/plugins ...')
    resp = requests.post(
        f'{WP_URL}/wp-json/wp/v2/plugins',
        auth=auth,
        files={'file': ('purebrain-security-hardening.zip', zip_buffer, 'application/zip')},
        timeout=60
    )

    print(f'  HTTP {resp.status_code}')
    if resp.status_code in (200, 201):
        data = resp.json()
        print(f'  Upload success. Plugin status: {data.get("status")}')
        # Activate if not active
        plugin_slug = data.get('plugin', 'purebrain-security-hardening/purebrain-security-hardening')
        if data.get('status') != 'active':
            print('  Activating plugin...')
            activate_resp = requests.put(
                f'{WP_URL}/wp-json/wp/v2/plugins/{plugin_slug.replace("/", "%2F")}',
                auth=auth,
                json={'status': 'active'},
                timeout=30
            )
            print(f'  Activation: HTTP {activate_resp.status_code}')
        return True
    else:
        try:
            err = resp.json()
            print(f'  Error: {err.get("message", resp.text[:200])}')
        except Exception:
            print(f'  Response: {resp.text[:300]}')
        return False


def verify_fix():
    """Test the live subscribe endpoint to confirm it responds."""
    print(f'\nVerifying endpoint: {WP_URL}/wp-json/pb-security/v1/subscribe ...')
    test_email = 'test-verify-fix@example.com'
    try:
        resp = requests.post(
            f'{WP_URL}/wp-json/pb-security/v1/subscribe',
            json={'email': test_email},
            timeout=20
        )
        print(f'  HTTP {resp.status_code}')
        if resp.status_code == 200:
            data = resp.json()
            print(f'  Response: {data}')
            if data.get('success'):
                print('  SUCCESS: Endpoint working correctly.')
                return True
            else:
                print(f'  WARNING: success=False. Message: {data}')
        elif resp.status_code == 503:
            print('  ERROR 503: BREVO_API_KEY is not defined in wp-config.php!')
            print('  ACTION NEEDED: Add this to wp-config.php:')
            print("    define( 'BREVO_API_KEY', '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' );")
            print("    define( 'PUREBRAIN_BEHIND_CLOUDFLARE', true );")
            return False
        elif resp.status_code == 429:
            print('  Rate limited (5/min). Endpoint is working — just rate limited by this IP.')
            return True
        else:
            print(f'  Unexpected status. Response: {resp.text[:200]}')
    except requests.exceptions.Timeout:
        print('  TIMEOUT: Endpoint did not respond in 20 seconds.')
        print('  This may be the root cause of the stuck button issue.')
    except Exception as e:
        print(f'  Error: {e}')
    return False


if __name__ == '__main__':
    print('=' * 60)
    print('Neural Feed Subscribe Fix — v485 → v486')
    print('=' * 60)

    # Step 1: Build v486
    print('\n[1/3] Building v486 plugin...')
    if not build_v486():
        print('\nBuild FAILED. Not deploying.')
        sys.exit(1)
    print('Build PASSED.')

    # Step 2: Verify the live endpoint before deploying
    print('\n[2/3] Testing live endpoint (pre-deploy)...')
    endpoint_ok = verify_fix()

    if not endpoint_ok:
        print('\nNOTE: Endpoint is not responding correctly before deploy.')
        print('This may be due to BREVO_API_KEY missing from wp-config.php.')
        print('Continuing with JS fix deploy anyway (fixes the stuck button).')
        print('The BREVO_API_KEY must also be added to wp-config.php separately.')

    # Step 3: Deploy
    print('\n[3/3] Deploying v486 to purebrain.ai...')
    with open(DST_FILE, 'r', encoding='utf-8') as f:
        plugin_content = f.read()

    deployed = deploy_to_wordpress(plugin_content)

    if deployed:
        print('\nDeployment SUCCEEDED.')
        print('\nPost-deploy verification...')
        verify_fix()
    else:
        print('\nDeployment via REST API failed.')
        print(f'Manual deployment needed: upload {DST_FILE} to WordPress.')
        print('Go to: WP Admin > Plugins > Add New > Upload Plugin')
        print(f'File: {DST_FILE}')

    print('\nDone.')
