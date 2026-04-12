#!/usr/bin/env python3
"""
COMPLETE VIDEO FIX DEPLOYMENT - 2026-03-01
CTO-directed emergency fix for live video issues on purebrain.ai

TWO-PART FIX:
  Part A: Plugin v4.7.4 - Add R2 to CSP (connect-src + media-src)
  Part B: Elementor data - Fix openVideoModal() to autoplay HLS, update embedded video section

DEPLOYMENT METHOD:
  Plugin: WP Admin plugin-editor.php (IPv4 forced, session cookie method)
  Elementor: REST API /wp/v2/pages/{id}

Usage:
  cd /home/jared/projects/AI-CIV/aether
  source .env && python3 tools/deploy_video_fix_complete.py

  OR (credentials inline):
  PUREBRAIN_WP_APP_PASSWORD="FlFr2VOtlHiHaJWjzW96OHUJ" python3 tools/deploy_video_fix_complete.py
"""

import os
import json
import base64
import time
import requests
import re
import sys
import socket
import traceback

# ============================================================
# CREDENTIALS
# ============================================================
WP_USER = "Aether"
WP_APP_PASS = os.environ.get("PUREBRAIN_WP_APP_PASSWORD", "FlFr2VOtlHiHaJWjzW96OHUJ")
WP_ADMIN_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"  # Used for plugin editor

AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Content-Type": "application/json"}

BASE_URL = "https://purebrain.ai/wp-json/wp/v2/pages"
CACHE_URL = "https://purebrain.ai/wp-json/elementor/v1/cache"

# ============================================================
# VIDEO ASSETS
# ============================================================
PORTAL_HLS = "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/master.m3u8"
PORTAL_POSTER = "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/poster.jpg"
PUREBRAIN_HLS = "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/75114256_Pure-Brain-Demo-Video/master.m3u8"
HLS_JS_CDN = "https://cdn.jsdelivr.net/npm/hls.js@1.5.7/dist/hls.min.js"

PAGES = [
    (11, "Homepage", "https://purebrain.ai/#awakening"),
    (689, "Pay Test 2", "https://purebrain.ai/pay-test-2/#awakening"),
    (688, "Pay Test Sandbox 2", "https://purebrain.ai/pay-test-sandbox-2/#awakening"),
]

# ============================================================
# PART A: BUILD v4.7.4 PLUGIN
# ============================================================

SOURCE_PLUGIN = "/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v473.php"
TARGET_PLUGIN = "/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v474.php"


def build_plugin_v474():
    print("\n" + "="*65)
    print("PART A: Building plugin v4.7.4 with CSP video fix")
    print("="*65)

    with open(SOURCE_PLUGIN, "r") as f:
        content = f.read()

    changes = []

    # 1. Version number
    old = " * Version:     4.7.3"
    new = " * Version:     4.7.4"
    if old in content:
        content = content.replace(old, new)
        changes.append("Version: 4.7.3 -> 4.7.4")
    else:
        print("  WARNING: Version string not found as expected")

    # 2. Changelog entry
    old = " *   v4.7.3 - CHATBOX DISCOVER BUTTON UX FIX"
    new = """ *   v4.7.4 - CSP FIX: Cloudflare R2 video bucket added to connect-src + media-src.
 *            Root cause of video failures on homepage/pay-test-2/pay-test-sandbox-2:
 *            HLS.js uses XHR/fetch to download .m3u8 + .ts files from R2. Without
 *            pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev in connect-src, CSP blocked
 *            all these requests. Video readyState stayed at 0 (HAVE_NOTHING), never played.
 *            Fix: R2 bucket URL added to connect-src. media-src added for blob: MSE URLs.
 *   v4.7.3 - CHATBOX DISCOVER BUTTON UX FIX"""
    if old in content:
        content = content.replace(old, new)
        changes.append("Changelog entry added")
    else:
        print("  WARNING: Changelog marker not found")

    # 3. Add R2 to connect-src
    old = '        .     "https://89.167.19.20:8443; "'
    new = ('        .     "https://89.167.19.20:8443 "\n'
           '         // Cloudflare R2: HLS.js fetches .m3u8 manifest + .ts video segments via XHR/fetch\n'
           '         // Without this, CSP blocks all HLS requests -> video never plays (readyState=0)\n'
           '         .     "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev; "')
    if old in content:
        content = content.replace(old, new)
        changes.append("R2 added to connect-src")
    else:
        print("  WARNING: connect-src end marker not found, trying alternative")
        # Try without the leading spaces
        old_alt = '"https://89.167.19.20:8443; "'
        if old_alt in content:
            content = content.replace(
                old_alt,
                '"https://89.167.19.20:8443 "\n'
                '         .     "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev; "'
            )
            changes.append("R2 added to connect-src (alt pattern)")

    # 4. Add media-src directive
    old = '         // Workers: PayPal SDK creates Web Workers from blob URLs\n         . "worker-src \'self\' blob:; "'
    new = ('         // Workers: PayPal SDK creates Web Workers from blob URLs\n'
           '         . "worker-src \'self\' blob:; "\n'
           '         // Media: HLS.js MSE creates blob: URLs for video buffers; R2 serves the source media\n'
           '         . "media-src \'self\' blob: https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev; "')
    if old in content:
        content = content.replace(old, new)
        changes.append("media-src directive added")
    else:
        print("  WARNING: worker-src marker not found for media-src insertion")
        # Try simpler pattern
        old_simple = '"worker-src \'self\' blob:; "'
        if old_simple in content:
            content = content.replace(
                old_simple,
                '"worker-src \'self\' blob:; "\n'
                '         . "media-src \'self\' blob: https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev; "'
            )
            changes.append("media-src directive added (simple pattern)")

    print(f"  Changes applied: {len(changes)}")
    for c in changes:
        print(f"    - {c}")

    # Verify critical changes
    assert "4.7.4" in content, "Version not updated!"
    assert "r2.dev" in content, "R2 not in CSP!"
    assert "media-src" in content, "media-src not added!"

    with open(TARGET_PLUGIN, "w") as f:
        f.write(content)

    print(f"  Written: {TARGET_PLUGIN} ({len(content)} chars)")
    return content


# ============================================================
# PART A2: DEPLOY PLUGIN VIA WP ADMIN (IPv4 forced)
# ============================================================

def force_ipv4():
    """Force all socket connections to use IPv4 (avoids Cloudflare IPv6 rate limiting)"""
    original_getaddrinfo = socket.getaddrinfo

    def ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
        return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

    socket.getaddrinfo = ipv4_only
    print("  IPv4 forced (avoids CF IPv6 rate limiting)")


def deploy_plugin(plugin_content):
    print("\n" + "="*65)
    print("PART A2: Deploying plugin v4.7.4 via WP Admin")
    print("="*65)

    force_ipv4()

    session = requests.Session()
    login_url = "https://purebrain.ai/wp-login.php"

    # Step 1: Login
    print("  Step 1: Logging into WP Admin...")
    login_data = {
        "log": "Aether",
        "pwd": WP_ADMIN_PASS,
        "wp-submit": "Log In",
        "redirect_to": "/wp-admin/",
        "testcookie": "1",
    }
    session.cookies.set("wordpress_test_cookie", "WP Cookie check")

    resp = session.post(login_url, data=login_data, timeout=30, allow_redirects=True)
    print(f"  Login status: {resp.status_code}")

    if "dashboard" not in resp.url and "wp-admin" not in resp.url:
        print(f"  WARNING: Login redirect to {resp.url} - may not be logged in")
        # Check for auth cookies
        wp_cookies = [c.name for c in session.cookies if "wordpress_logged_in" in c.name]
        if not wp_cookies:
            print("  ERROR: No wordpress_logged_in cookie found - login likely failed")
            return False
        print(f"  Auth cookies found: {wp_cookies}")

    # Step 2: Get plugin editor page to extract nonce
    print("  Step 2: Fetching plugin editor for nonce...")
    editor_url = ("https://purebrain.ai/wp-admin/plugin-editor.php"
                  "?file=purebrain-security%2Fpurebrain-security-plugin.php"
                  "&plugin=purebrain-security%2Fpurebrain-security-plugin.php")
    resp = session.get(editor_url, timeout=30)
    print(f"  Editor page status: {resp.status_code}")

    # Extract nonce from the form
    nonce_match = re.search(r'<input[^>]+id="nonce"[^>]+name="nonce"[^>]+value="([^"]+)"', resp.text)
    if not nonce_match:
        # Try alternate pattern
        nonce_match = re.search(r'name="nonce"\s+value="([^"]+)"', resp.text)
    if not nonce_match:
        nonce_match = re.search(r'"nonce":"([a-f0-9]+)"', resp.text)
        if nonce_match:
            # This is the block editor nonce (wrong one!) - look harder for form nonce
            print(f"  Found block editor nonce (incorrect) - looking for form nonce")
            nonce_match = None

    if not nonce_match:
        print("  ERROR: Could not extract form nonce from plugin editor page")
        print(f"  Response snippet: {resp.text[2000:2500]}")
        return False

    nonce = nonce_match.group(1)
    print(f"  Nonce extracted: {nonce[:8]}...")

    # Step 3: Post updated plugin content
    print("  Step 3: Posting plugin v4.7.4 content...")
    post_data = {
        "newcontent": plugin_content,
        "action": "update",
        "file": "purebrain-security/purebrain-security-plugin.php",
        "plugin": "purebrain-security/purebrain-security-plugin.php",
        "nonce": nonce,
    }

    resp = session.post(editor_url, data=post_data, timeout=60)
    print(f"  Post status: {resp.status_code}")

    if resp.status_code == 200:
        if "File edited successfully" in resp.text or "notice-success" in resp.text:
            print("  SUCCESS: Plugin editor confirmed update")
        elif "Error" in resp.text or "error" in resp.text:
            # Look for specific error
            err_match = re.search(r'<div[^>]*class="[^"]*notice-error[^"]*"[^>]*>(.*?)</div>', resp.text, re.DOTALL)
            if err_match:
                print(f"  ERROR in response: {err_match.group(1)[:200]}")
            else:
                print(f"  Response seems OK (200) but no success message found")
                print(f"  Looking for success indicators...")
                if "4.7.4" in resp.text:
                    print("  Version 4.7.4 found in response - likely deployed!")
    else:
        print(f"  ERROR: HTTP {resp.status_code}")
        return False

    # Step 4: Verify via REST API
    time.sleep(3)
    print("  Step 4: Verifying plugin version via REST API...")
    verify_resp = requests.get(
        "https://purebrain.ai/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin",
        headers=HEADERS,
        timeout=30
    )
    if verify_resp.status_code == 200:
        plugin_data = verify_resp.json()
        version = plugin_data.get("version", "unknown")
        print(f"  Verified plugin version: {version}")
        return version == "4.7.4"
    else:
        print(f"  Verify HTTP: {verify_resp.status_code}")
        # Try checking via plugin list
        list_resp = requests.get(
            "https://purebrain.ai/wp-json/wp/v2/plugins",
            headers=HEADERS,
            timeout=30
        )
        if list_resp.status_code == 200:
            plugins = list_resp.json()
            for p in plugins:
                if "purebrain" in p.get("plugin", "").lower():
                    print(f"  Plugin: {p.get('plugin')} v{p.get('version')}")
        return False


# ============================================================
# PART B: FIX ELEMENTOR DATA
# ============================================================

OPEN_VIDEO_MODAL_FN = f"""function openVideoModal() {{
            var modal = document.getElementById('videoModal');
            if (!modal) return;
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            var video = document.getElementById('demoVideo');
            if (!video) return;
            var hlsUrl = '{PORTAL_HLS}';
            function startModalHls(Hls) {{
                if (window._pbModalHls) {{ try {{ window._pbModalHls.destroy(); }} catch(e) {{}} window._pbModalHls = null; }}
                if (Hls.isSupported()) {{
                    window._pbModalHls = new Hls({{startLevel: -1, maxBufferLength: 30}});
                    window._pbModalHls.loadSource(hlsUrl);
                    window._pbModalHls.attachMedia(video);
                    window._pbModalHls.on(Hls.Events.MANIFEST_PARSED, function() {{
                        video.play().catch(function() {{ video.muted = true; video.play(); }});
                    }});
                }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                    video.src = hlsUrl;
                    video.load();
                    video.play().catch(function() {{ video.muted = true; video.play(); }});
                }}
            }}
            if (typeof Hls !== 'undefined') {{
                startModalHls(Hls);
            }} else {{
                var s = document.createElement('script');
                s.src = '{HLS_JS_CDN}';
                s.onload = function() {{ if (typeof Hls !== 'undefined') startModalHls(Hls); }};
                document.head.appendChild(s);
            }}
        }}"""

CLOSE_VIDEO_MODAL_FN = """function closeVideoModal() {
            var modal = document.getElementById('videoModal');
            if (!modal) return;
            modal.classList.remove('active');
            document.body.style.overflow = '';
            var video = document.getElementById('demoVideo');
            if (video) {
                video.pause();
                video.currentTime = 0;
                try { video.removeAttribute('src'); video.load(); } catch(e) {}
            }
            if (window._pbModalHls) {
                try { window._pbModalHls.destroy(); } catch(e) {}
                window._pbModalHls = null;
            }
        }"""

PB_DEMO_PLAY_IIFE = f"""(function() {{
            var _pbDemoHls = null;
            var _pbDemoLoaded = false;
            var PB_HLS_URL = '{PUREBRAIN_HLS}';
            window.pbDemoPlay = function(playerEl) {{
                var video = document.getElementById('pbDemoVideo');
                var overlay = document.getElementById('pbDemoOverlay');
                if (!video) return;
                if (!_pbDemoLoaded) {{
                    _pbDemoLoaded = true;
                    function startEmbedHls(Hls) {{
                        if (_pbDemoHls) {{ try {{ _pbDemoHls.destroy(); }} catch(e) {{}} _pbDemoHls = null; }}
                        if (Hls.isSupported()) {{
                            _pbDemoHls = new Hls({{startLevel: -1, maxBufferLength: 20}});
                            _pbDemoHls.loadSource(PB_HLS_URL);
                            _pbDemoHls.attachMedia(video);
                            _pbDemoHls.on(Hls.Events.MANIFEST_PARSED, function() {{
                                video.muted = false;
                                video.play().catch(function() {{ video.muted = true; video.play(); }});
                            }});
                        }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                            video.src = PB_HLS_URL;
                            video.load();
                            video.muted = false;
                            video.play().catch(function() {{ video.muted = true; video.play(); }});
                        }}
                    }}
                    if (typeof Hls !== 'undefined') {{
                        startEmbedHls(Hls);
                    }} else {{
                        var s = document.createElement('script');
                        s.src = '{HLS_JS_CDN}';
                        s.onload = function() {{ if (typeof Hls !== 'undefined') startEmbedHls(Hls); }};
                        document.head.appendChild(s);
                    }}
                }} else {{
                    video.muted = false;
                    video.play().catch(function() {{ video.muted = true; video.play(); }});
                }}
                if (overlay) overlay.classList.add('pb-playing');
                video.addEventListener('pause', function() {{
                    if (overlay) overlay.classList.remove('pb-playing');
                }});
                video.addEventListener('ended', function() {{
                    if (overlay) overlay.classList.remove('pb-playing');
                    _pbDemoLoaded = false;
                }});
            }};
        }})();"""


def build_demo_section(awakening_url):
    return f"""
    <!-- DEMO VIDEO EMBED SECTION v3 2026-03-01 -->
    <section class="pb-demo-section" id="pb-demo-section" aria-label="Product Demo">
        <div class="pb-demo-section__inner">
            <div class="pb-demo-section__label">Live Demo</div>
            <h2 class="pb-demo-section__heading">Watch <span>PureBrain</span> Come Alive</h2>
            <p class="pb-demo-section__sub">See your AI awaken, learn your name, and start becoming truly yours &mdash; in real time.</p>
            <div class="pb-demo-player" id="pbDemoPlayer" onclick="pbDemoPlay(this)">
                <video
                    id="pbDemoVideo"
                    poster="{PORTAL_POSTER}"
                    playsinline
                    preload="none"
                ></video>
                <div class="pb-demo-player__overlay" id="pbDemoOverlay">
                    <div class="pb-demo-player__play">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><polygon points="5,3 19,12 5,21"/></svg>
                    </div>
                </div>
            </div>
            <p class="pb-demo-section__cta">Ready to try it yourself? <a href="{awakening_url}">Begin your awakening &rarr;</a></p>
        </div>
    </section>
"""


def get_fn_bounds(html, fn_name):
    pos = html.find(f"function {fn_name}()")
    if pos == -1:
        return None, None
    brace_pos = html.find("{", pos)
    if brace_pos == -1:
        return None, None
    depth = 0
    i = brace_pos
    while i < len(html):
        if html[i] == '{':
            depth += 1
        elif html[i] == '}':
            depth -= 1
            if depth == 0:
                return pos, i + 1
        i += 1
    return None, None


def replace_fn(html, fn_name, new_fn):
    start, end = get_fn_bounds(html, fn_name)
    if start is None:
        print(f"    {fn_name}(): NOT FOUND")
        return html, False
    old = html[start:end]
    print(f"    {fn_name}(): replaced ({len(old)} -> {len(new_fn)} chars)")
    return html[:start] + new_fn + html[end:], True


def update_demo_section(html, awakening_url):
    # Find and replace the pb-demo-section
    m = re.search(r'<section[^>]*\bid="pb-demo-section"[^>]*>', html, re.DOTALL)
    if not m:
        m = re.search(r'<section[^>]*class="pb-demo-section[^"]*"', html, re.DOTALL)
    if not m:
        return html, False, "not found"

    start = m.start()
    # Find closing </section>
    depth = 0
    pos = start
    while pos < len(html):
        next_open = html.find("<section", pos + 1)
        next_close = html.find("</section>", pos + 1)
        if next_close == -1:
            return html, False, "unclosed"
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open
        else:
            if depth == 0:
                end = next_close + len("</section>")
                old = html[start:end]
                new = build_demo_section(awakening_url)
                print(f"    pb-demo-section: replaced ({len(old)} -> {len(new)} chars)")
                return html[:start] + new + html[end:], True, "replaced"
            depth -= 1
            pos = next_close

    return html, False, "parse error"


def insert_demo_section(html, awakening_url):
    wd_pos = html.find("Watch Demo")
    if wd_pos == -1:
        return html, False
    close_pos = html.find("</section>", wd_pos)
    if close_pos == -1:
        return html, False
    insert = close_pos + len("</section>")
    new_section = build_demo_section(awakening_url)
    print(f"    pb-demo-section: inserted after hero at pos {insert}")
    return html[:insert] + new_section + html[insert:], True


def update_pb_demo_iife(html):
    # Find the IIFE by marker
    marker = "window.pbDemoPlay"
    pos = html.find(marker)
    if pos == -1:
        return html, False

    # Find IIFE start
    iife_start = html.rfind("(function()", 0, pos)
    if iife_start == -1:
        iife_start = html.rfind("(function ()", 0, pos)
    if iife_start == -1:
        print(f"    pbDemoPlay IIFE start not found")
        return html, False

    # Find IIFE end
    close = html.find("})();", pos)
    if close == -1:
        close = html.find("})()", pos)
    if close == -1:
        print(f"    pbDemoPlay IIFE end not found")
        return html, False

    iife_end = close + len("})();")
    old = html[iife_start:iife_end]
    print(f"    pbDemoPlay IIFE: replaced ({len(old)} -> {len(PB_DEMO_PLAY_IIFE)} chars)")
    return html[:iife_start] + PB_DEMO_PLAY_IIFE + html[iife_end:], True


def insert_pb_demo_script(html):
    ovm_pos = html.find("function openVideoModal()")
    if ovm_pos != -1:
        close = html.find("</script>", ovm_pos)
    else:
        close = html.rfind("</script>")
    if close == -1:
        return html, False
    html = html[:close] + "\n        " + PB_DEMO_PLAY_IIFE + "\n        " + html[close:]
    print(f"    pbDemoPlay IIFE: inserted before </script>")
    return html, True


def fix_awakening_links(html, awakening_url):
    changed = False

    def replacer(m):
        nonlocal changed
        old_val = m.group(0)
        if awakening_url in old_val:
            return old_val
        changed = True
        print(f"    Awakening link: {old_val[:80]} -> {awakening_url}")
        return f'href="{awakening_url}"'

    html = re.sub(r'href=["\'][^"\']*awakening[^"\']*["\']', replacer, html)

    # Fix CTA paragraph in pb-demo-section
    cta_re = re.compile(r'<p class="pb-demo-section__cta">.*?</p>', re.DOTALL)
    cta_m = cta_re.search(html)
    if cta_m:
        new_cta = f'<p class="pb-demo-section__cta">Ready to try it yourself? <a href="{awakening_url}">Begin your awakening &rarr;</a></p>'
        if cta_m.group(0) != new_cta:
            html = html[:cta_m.start()] + new_cta + html[cta_m.end():]
            print(f"    pb-demo-section CTA: updated -> {awakening_url}")
            changed = True

    return html, changed


def process_page(page_id, page_name, awakening_url):
    print(f"\n  --- {page_name} (ID={page_id}) ---")

    # Fetch
    resp = requests.get(f"{BASE_URL}/{page_id}?context=edit", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    page_data = resp.json()
    ed_str = page_data.get("meta", {}).get("_elementor_data", "")
    el_data = json.loads(ed_str)

    # Find widget
    ci, wi, html = None, None, None
    for c_idx, container in enumerate(el_data):
        for w_idx, widget in enumerate(container.get("elements", [])):
            hc = widget.get("settings", {}).get("html", "")
            if len(hc) > 50000 and "Watch Demo" in hc:
                ci, wi, html = c_idx, w_idx, hc
                break
        if html:
            break

    if html is None:
        print(f"    ERROR: Main widget not found")
        return False

    print(f"    Widget at [{ci}][{wi}] len={len(html)}")

    # State check
    print(f"    State: openVideoModal={'YES' if 'function openVideoModal' in html else 'NO'}"
          f" | pbDemoPlay={'YES' if 'pbDemoPlay' in html else 'NO'}"
          f" | pb-demo-section={'YES' if 'pb-demo-section' in html else 'NO'}"
          f" | startModalHls={'FIXED' if 'startModalHls' in html else 'needs fix'}")

    any_change = False

    # Fix openVideoModal
    if "function openVideoModal" in html:
        if "startModalHls" not in html:
            html, ch = replace_fn(html, "openVideoModal", OPEN_VIDEO_MODAL_FN)
            any_change = any_change or ch
        else:
            print(f"    openVideoModal: already has startModalHls - skipping")

    # Fix closeVideoModal
    if "function closeVideoModal" in html:
        if "_pbModalHls" not in html:
            html, ch = replace_fn(html, "closeVideoModal", CLOSE_VIDEO_MODAL_FN)
            any_change = any_change or ch
        else:
            print(f"    closeVideoModal: already has _pbModalHls - skipping")

    # Update/insert pbDemoPlay IIFE
    if "pbDemoPlay" in html:
        html, ch = update_pb_demo_iife(html)
        any_change = any_change or ch
    else:
        html, ch = insert_pb_demo_script(html)
        any_change = any_change or ch

    # Update/insert pb-demo-section
    if "pb-demo-section" in html:
        html, ch, reason = update_demo_section(html, awakening_url)
        any_change = any_change or ch
        print(f"    pb-demo-section: {reason}")
    else:
        html, ch = insert_demo_section(html, awakening_url)
        any_change = any_change or ch
        if ch:
            # Need script too
            if "pbDemoPlay" not in html:
                html, sc = insert_pb_demo_script(html)
                any_change = any_change or sc

    # Fix awakening links
    html, ch = fix_awakening_links(html, awakening_url)
    any_change = any_change or ch

    if not any_change:
        print(f"    No changes needed")
        return True

    print(f"    Deploying ({len(html)} chars)...")
    el_data[ci]["elements"][wi]["settings"]["html"] = html
    payload = {"meta": {"_elementor_data": json.dumps(el_data, separators=(',', ':'))}}
    resp = requests.post(f"{BASE_URL}/{page_id}", headers=HEADERS, json=payload, timeout=60)
    resp.raise_for_status()
    print(f"    Update: HTTP {resp.status_code}")

    # Cache clear
    resp = requests.delete(CACHE_URL, headers=HEADERS, timeout=30)
    print(f"    Cache clear: HTTP {resp.status_code}")
    time.sleep(3)

    # Touch
    resp = requests.post(f"{BASE_URL}/{page_id}", headers=HEADERS, json={"status": "publish"}, timeout=30)
    print(f"    Touch: HTTP {resp.status_code}")
    time.sleep(5)

    # Verify
    v_resp = requests.get(f"{BASE_URL}/{page_id}?context=edit", headers=HEADERS, timeout=30)
    v_ed = v_resp.json().get("meta", {}).get("_elementor_data", "")

    results = {
        "openVideoModal with HLS (startModalHls)": "startModalHls" in v_ed,
        "closeVideoModal with cleanup (_pbModalHls)": "_pbModalHls" in v_ed,
        "pbDemoPlay IIFE": "pbDemoPlay" in v_ed,
        "Pure Brain Demo Video URL": "75114256_Pure-Brain-Demo-Video" in v_ed,
        "pb-demo-section present": "pb-demo-section" in v_ed,
        f"Correct awakening URL": awakening_url in v_ed,
    }

    print(f"    VERIFICATION:")
    all_pass = True
    for k, v in results.items():
        icon = "PASS" if v else "FAIL"
        if not v:
            all_pass = False
        print(f"      {icon}: {k}")

    return all_pass


def fix_elementor_all_pages():
    print("\n" + "="*65)
    print("PART B: Fixing Elementor data on all 3 pages")
    print("="*65)

    results = {}
    for page_id, page_name, awakening_url in PAGES:
        try:
            ok = process_page(page_id, page_name, awakening_url)
            results[page_name] = "PASS" if ok else "FAIL"
        except Exception as e:
            print(f"  EXCEPTION on {page_name}: {e}")
            traceback.print_exc()
            results[page_name] = "ERROR"

    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print("="*65)
    print("PUREBRAIN VIDEO FIX - COMPLETE DEPLOYMENT")
    print("2026-03-01 | CTO-directed emergency fix")
    print("="*65)

    all_results = {}

    # PART A: Build plugin
    try:
        plugin_content = build_plugin_v474()
        all_results["Plugin v4.7.4 build"] = "PASS"
    except Exception as e:
        print(f"EXCEPTION building plugin: {e}")
        traceback.print_exc()
        all_results["Plugin v4.7.4 build"] = "ERROR"
        print("\nCannot continue without plugin build. Aborting.")
        return 1

    # PART A2: Deploy plugin
    try:
        plugin_deployed = deploy_plugin(plugin_content)
        all_results["Plugin v4.7.4 deploy"] = "PASS" if plugin_deployed else "FAIL"
        if not plugin_deployed:
            print("\nWARNING: Plugin deployment may have failed. Continuing with Elementor fixes.")
    except Exception as e:
        print(f"EXCEPTION deploying plugin: {e}")
        traceback.print_exc()
        all_results["Plugin v4.7.4 deploy"] = "ERROR"
        print("Continuing with Elementor fixes despite plugin deploy error...")

    # PART B: Fix Elementor data
    try:
        page_results = fix_elementor_all_pages()
        all_results.update(page_results)
    except Exception as e:
        print(f"EXCEPTION in Elementor fixes: {e}")
        traceback.print_exc()
        all_results["Elementor fixes"] = "ERROR"

    # Final summary
    print("\n" + "="*65)
    print("FINAL SUMMARY")
    print("="*65)
    for name, result in all_results.items():
        print(f"  {result}: {name}")

    all_pass = all(v == "PASS" for v in all_results.values())
    print(f"\nOverall: {'ALL PASSED' if all_pass else 'REVIEW FAILURES ABOVE'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
