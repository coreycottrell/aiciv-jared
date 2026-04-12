#!/usr/bin/env python3
"""
VIDEO FIX v2 - 2026-03-01
MISSION: Fix video on all 3 pages:
1. Diagnose current state
2. Fix Watch Demo button to use correct #awakening anchor
3. Fix embedded video section (autoplay on scroll + new Pure Brain Demo Video URL)
4. Fix Begin Awakening links to correct anchors

Pages:
- Homepage (ID 11): https://purebrain.ai/#awakening
- Pay Test 2 (ID 689): https://purebrain.ai/pay-test-2/#awakening
- Pay Test Sandbox 2 (ID 688): https://purebrain.ai/pay-test-sandbox-2/#awakening

Video URLs:
- Portal Demo (Watch Demo modal): https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/master.m3u8
- Pure Brain Demo (embedded section): https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/75114256_Pure-Brain-Demo-Video/master.m3u8
"""

import os
import json
import base64
import time
import requests
import re
import sys

WP_USER = "Aether"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"

AUTH = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Content-Type": "application/json"}
BASE_URL = "https://purebrain.ai/wp-json/wp/v2/pages"
CACHE_URL = "https://purebrain.ai/wp-json/elementor/v1/cache"

PORTAL_HLS = "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/master.m3u8"
PORTAL_POSTER = "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/poster.jpg"
PUREBRAIN_HLS = "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/75114256_Pure-Brain-Demo-Video/master.m3u8"

PAGES = [
    (11, "Homepage", "https://purebrain.ai/#awakening"),
    (689, "Pay Test 2", "https://purebrain.ai/pay-test-2/#awakening"),
    (688, "Pay Test Sandbox 2", "https://purebrain.ai/pay-test-sandbox-2/#awakening"),
]


def get_page_data(page_id):
    resp = requests.get(f"{BASE_URL}/{page_id}?context=edit", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def update_page(page_id, el_data):
    payload = {"meta": {"_elementor_data": json.dumps(el_data, separators=(',', ':'))}}
    resp = requests.post(f"{BASE_URL}/{page_id}", headers=HEADERS, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.status_code


def clear_cache():
    resp = requests.delete(CACHE_URL, headers=HEADERS, timeout=30)
    print(f"  Cache clear: HTTP {resp.status_code}")


def touch_page(page_id):
    resp = requests.post(f"{BASE_URL}/{page_id}", headers=HEADERS, json={"status": "publish"}, timeout=30)
    print(f"  Touch page {page_id}: HTTP {resp.status_code}")


def find_main_widget(el_data):
    """Find the main HTML widget containing 'Watch Demo'"""
    for ci, container in enumerate(el_data):
        elements = container.get("elements", [])
        for wi, widget in enumerate(elements):
            settings = widget.get("settings", {})
            hc = settings.get("html", "")
            if len(hc) > 50000 and "Watch Demo" in hc:
                return ci, wi, hc
    return None, None, None


def diagnose_html(html, page_name, awakening_url):
    """Diagnose current state of the page HTML"""
    print(f"\n  --- DIAGNOSIS: {page_name} ---")
    print(f"  HTML length: {len(html)}")
    print(f"  pb-demo-section: {'YES' if 'pb-demo-section' in html else 'NO'}")
    print(f"  Watch Demo present: {'YES' if 'Watch Demo' in html else 'NO'}")
    print(f"  openVideoModal: {'YES' if 'openVideoModal' in html else 'NO'}")

    # Find HLS URLs
    hls_urls = list(set(re.findall(r'https://[^\s"\'\\]+\.m3u8', html)))
    print(f"  HLS URLs: {hls_urls}")

    # Find awakening links
    awk_links = list(set(re.findall(r'href=["\'][^"\']*awakening[^"\']*["\']', html)))
    print(f"  Awakening links: {awk_links}")

    # Check if Watch Demo button has correct link
    wd_match = re.search(r'Watch Demo.{0,500}', html)
    if wd_match:
        print(f"  Watch Demo context: {wd_match.group()[:200]}")

    # Check if embedded video uses PureBrain Demo URL
    print(f"  Uses Pure Brain Demo Video: {'YES' if '75114256_Pure-Brain-Demo-Video' in html else 'NO'}")
    print(f"  Uses Portal Demo: {'YES' if 'eaf39ae1_Portal_demo' in html else 'NO'}")

    return {
        "has_demo_section": "pb-demo-section" in html,
        "has_watch_demo": "Watch Demo" in html,
        "has_open_modal": "openVideoModal" in html,
        "hls_urls": hls_urls,
        "awk_links": awk_links,
    }


def fix_watch_demo_link(html, page_id, awakening_url):
    """
    Fix: Make Watch Demo button open modal correctly (it should call openVideoModal()).
    The Watch Demo button currently may have a broken href. We need it to:
    - Call openVideoModal() onclick (keeping existing pattern)
    - But also ensure the #awakening anchor exists in the page

    Also fix: 'Begin your awakening' links to point to correct page-specific URL.
    """
    changed = False

    # Fix "Begin awakening" / "Begin your awakening" links to point to correct URL
    # Pattern: href="#awakening" or href="/#awakening" or href="https://purebrain.ai/#awakening"
    # We want: href="{awakening_url}"

    # Replace any relative or absolute awakening hrefs with the correct page-specific URL
    old_patterns = [
        r'href="#awakening"',
        r'href="/#awakening"',
        r'href="https://purebrain\.ai/#awakening"',
        r'href=\'#awakening\'',
        r'href=\'/#awakening\'',
    ]

    for pattern in old_patterns:
        new_html = re.sub(pattern, f'href="{awakening_url}"', html)
        if new_html != html:
            print(f"  Fixed awakening link: {pattern} -> {awakening_url}")
            html = new_html
            changed = True

    # Also fix any pb-demo-section CTA that points to #pb-chatbox (wrong for pay-test pages)
    if "pb-chatbox" in html and page_id in [689, 688]:
        # For pay-test pages, the #awakening section IS the chatbox, so use the awakening URL
        old_cta = 'href="#pb-chatbox" onclick="document.getElementById(\'pb-chatbox\') && document.getElementById(\'pb-chatbox\').scrollIntoView({behavior:\'smooth\'})"'
        new_cta = f'href="{awakening_url}"'
        if old_cta in html:
            html = html.replace(old_cta, new_cta)
            print(f"  Fixed pb-chatbox link -> {awakening_url}")
            changed = True

    return html, changed


def fix_embedded_video(html, page_id, awakening_url):
    """
    Fix the embedded video section to use:
    1. The Pure Brain Demo Video URL (new, just uploaded)
    2. Autoplay on intersection observer (plays when scrolled into view)
    3. Correct awakening link for this specific page
    """
    if "pb-demo-section" not in html:
        print(f"  pb-demo-section NOT found - will add it")
        return add_embedded_video(html, page_id, awakening_url), True

    print(f"  pb-demo-section found - will update it")

    # Find the pb-demo-section and replace it entirely
    # Find start of section
    section_start = html.find('<section class="pb-demo-section"')
    if section_start == -1:
        print("  ERROR: Cannot find pb-demo-section start tag")
        return html, False

    # Find end of section
    # Count nested sections
    search_from = section_start + len('<section class="pb-demo-section"')
    depth = 1
    pos = search_from
    while depth > 0 and pos < len(html):
        next_open = html.find('<section', pos)
        next_close = html.find('</section>', pos)

        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 1
        else:
            depth -= 1
            if depth == 0:
                section_end = next_close + len('</section>')
                break
            pos = next_close + 1

    if depth != 0:
        print("  ERROR: Could not find section end")
        return html, False

    old_section = html[section_start:section_end]
    new_section = build_video_section(page_id, awakening_url)

    html = html[:section_start] + new_section + html[section_end:]
    print(f"  Replaced pb-demo-section ({len(old_section)} chars -> {len(new_section)} chars)")

    # Also update the pbDemoPlay script if present
    html = update_pb_demo_script(html)

    return html, True


def add_embedded_video(html, page_id, awakening_url):
    """Add the embedded video section to a page that doesn't have it yet"""
    # Find hero close: the </section> after the "Watch Demo" button
    watch_demo_pos = html.find("Watch Demo")
    if watch_demo_pos == -1:
        print("  ERROR: Cannot find 'Watch Demo' marker for section insertion")
        return html

    hero_close = html.find("</section>", watch_demo_pos)
    if hero_close == -1:
        print("  ERROR: Cannot find hero </section>")
        return html

    insert_after = hero_close + len("</section>")
    new_section = "\n" + build_video_section(page_id, awakening_url)
    html = html[:insert_after] + new_section + html[insert_after:]
    print(f"  Added pb-demo-section after hero (position {insert_after})")

    # Also inject the script
    open_vm_pos = html.find("function openVideoModal()")
    if open_vm_pos != -1:
        script_close = html.find("</script>", open_vm_pos)
        if script_close != -1:
            html = html[:script_close] + "\n" + build_pb_demo_script() + "\n        " + html[script_close:]
            print(f"  Injected pbDemoPlay script before </script>")

    return html


def build_video_section(page_id, awakening_url):
    """Build the complete video section HTML"""
    return f"""
    <!-- ============================================
         DEMO VIDEO EMBED SECTION (v2 - 2026-03-01)
         ============================================ -->
    <section class="pb-demo-section" id="pb-demo-section" aria-label="Product Demo">
        <div class="pb-demo-section__inner">
            <div class="pb-demo-section__label">Live Demo</div>
            <h2 class="pb-demo-section__heading">Watch <span>PureBrain</span> Come Alive</h2>
            <p class="pb-demo-section__sub">See your AI awaken, learn your name, and start becoming truly yours — in real time.</p>
            <div class="pb-demo-player" id="pbDemoPlayer" onclick="pbDemoPlay(this)">
                <video
                    id="pbDemoVideo"
                    poster="https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/poster.jpg"
                    playsinline
                    preload="none"
                ></video>
                <div class="pb-demo-player__overlay" id="pbDemoOverlay">
                    <div class="pb-demo-player__play">
                        <svg viewBox="0 0 24 24"><polygon points="5,3 19,12 5,21"/></svg>
                    </div>
                </div>
            </div>
            <p class="pb-demo-section__cta">Ready to try it yourself? <a href="{awakening_url}">Begin your awakening &rarr;</a></p>
        </div>
    </section>
"""


def build_pb_demo_script():
    """Build the pbDemoPlay script"""
    return f"""
        /* ---- Embedded Demo Player v2 (pb-demo-section) 2026-03-01 ---- */
        (function() {{
            var _pbDemoHls = null;
            var _pbDemoLoaded = false;
            var HLS_URL = '{PUREBRAIN_HLS}';
            window.pbDemoPlay = function(playerEl) {{
                var video = document.getElementById('pbDemoVideo');
                var overlay = document.getElementById('pbDemoOverlay');
                if (!video) return;
                if (!_pbDemoLoaded) {{
                    _pbDemoLoaded = true;
                    function startEmbedHls(Hls) {{
                        if (_pbDemoHls) {{ _pbDemoHls.destroy(); }}
                        if (Hls.isSupported()) {{
                            _pbDemoHls = new Hls({{startLevel:-1, maxBufferLength:20}});
                            _pbDemoHls.loadSource(HLS_URL);
                            _pbDemoHls.attachMedia(video);
                            _pbDemoHls.on(Hls.Events.MANIFEST_PARSED, function() {{
                                video.muted = false;
                                video.play().catch(function() {{ video.muted = true; video.play(); }});
                            }});
                        }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                            video.src = HLS_URL;
                            video.muted = false;
                            video.play().catch(function() {{ video.muted = true; video.play(); }});
                        }}
                    }}
                    if (typeof Hls !== 'undefined') {{
                        startEmbedHls(Hls);
                    }} else {{
                        var s = document.createElement('script');
                        s.src = 'https://cdn.jsdelivr.net/npm/hls.js@1.5.7/dist/hls.min.js';
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
        }})();
"""


def update_pb_demo_script(html):
    """Replace the pbDemoPlay script in the page with the updated version"""
    # Find the existing pbDemoPlay script
    script_marker = "/* ---- Embedded Demo Player"
    script_start = html.find(script_marker)
    if script_start == -1:
        print("  pbDemoPlay script not found in existing HTML - looking for IIFE marker")
        script_marker = "window.pbDemoPlay = function"
        script_start = html.find(script_marker)
        if script_start == -1:
            print("  WARNING: pbDemoPlay script not found, cannot update")
            return html
        # Back up to find the IIFE start
        iife_start = html.rfind("(function()", 0, script_start)
        if iife_start != -1:
            script_start = iife_start

    # Find the end of this script block (the closing })(); of the IIFE)
    iife_close = html.find("})();", script_start)
    if iife_close == -1:
        print("  WARNING: Cannot find IIFE close })()")
        return html

    script_end = iife_close + len("})();")
    old_script = html[script_start:script_end]
    new_script = build_pb_demo_script().strip()

    html = html[:script_start] + new_script + html[script_end:]
    print(f"  Updated pbDemoPlay script ({len(old_script)} -> {len(new_script)} chars)")

    return html


def fix_watch_demo_button_href(html, page_id, awakening_url):
    """
    The Watch Demo button should open the video modal. It currently uses openVideoModal().
    But: When clicked, the modal video should AUTOPLAY.

    Current issue: video opens but does not play.
    The openVideoModal() function needs to autoplay the demoVideo.

    Strategy: Find openVideoModal() and ensure it calls demoVideo.play() after setup.
    """
    if "openVideoModal" not in html:
        print("  openVideoModal not found in HTML")
        return html, False

    # Find the openVideoModal function and fix it to autoplay
    # Current pattern (from memory): opens modal, but doesn't trigger play
    old_open_modal = html.find("function openVideoModal()")
    if old_open_modal == -1:
        return html, False

    # Extract the function body
    func_start = old_open_modal
    brace_open = html.find("{", func_start)
    if brace_open == -1:
        return html, False

    depth = 1
    pos = brace_open + 1
    while depth > 0 and pos < len(html):
        c = html[pos]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        pos += 1
    func_end = pos

    old_func_body = html[func_start:func_end]
    print(f"  openVideoModal function found ({len(old_func_body)} chars)")
    print(f"  Function body: {old_func_body[:500]}")

    # Build new openVideoModal that autoplays the HLS demo
    new_open_modal = f"""function openVideoModal() {{
            var modal = document.getElementById('videoModal');
            if (modal) {{
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
                var video = document.getElementById('demoVideo');
                if (video) {{
                    var hlsUrl = '{PORTAL_HLS}';
                    function startModalHls(Hls) {{
                        if (window._modalHls) {{ window._modalHls.destroy(); window._modalHls = null; }}
                        if (Hls.isSupported()) {{
                            window._modalHls = new Hls({{startLevel:-1}});
                            window._modalHls.loadSource(hlsUrl);
                            window._modalHls.attachMedia(video);
                            window._modalHls.on(Hls.Events.MANIFEST_PARSED, function() {{
                                video.play().catch(function(e) {{ video.muted = true; video.play(); }});
                            }});
                        }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                            video.src = hlsUrl;
                            video.play().catch(function(e) {{ video.muted = true; video.play(); }});
                        }}
                    }}
                    if (typeof Hls !== 'undefined') {{
                        startModalHls(Hls);
                    }} else {{
                        var s = document.createElement('script');
                        s.src = 'https://cdn.jsdelivr.net/npm/hls.js@1.5.7/dist/hls.min.js';
                        s.onload = function() {{ if (typeof Hls !== 'undefined') startModalHls(Hls); }};
                        document.head.appendChild(s);
                    }}
                }}
            }}
        }}"""

    html = html[:func_start] + new_open_modal + html[func_end:]
    print(f"  openVideoModal rewritten with HLS autoplay")

    # Also fix closeVideoModal to stop the video and destroy HLS
    close_modal_start = html.find("function closeVideoModal()")
    if close_modal_start != -1:
        close_brace = html.find("{", close_modal_start)
        if close_brace != -1:
            depth = 1
            pos = close_brace + 1
            while depth > 0 and pos < len(html):
                c = html[pos]
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                pos += 1
            close_func_end = pos

            new_close_modal = """function closeVideoModal() {
            var modal = document.getElementById('videoModal');
            if (modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
                var video = document.getElementById('demoVideo');
                if (video) {
                    video.pause();
                    video.currentTime = 0;
                    video.removeAttribute('src');
                    video.load();
                }
                if (window._modalHls) {
                    window._modalHls.destroy();
                    window._modalHls = null;
                }
            }
        }"""
            html = html[:close_modal_start] + new_close_modal + html[close_func_end:]
            print(f"  closeVideoModal also updated")

    return html, True


def process_page(page_id, page_name, awakening_url):
    print(f"\n{'='*70}")
    print(f"PROCESSING: {page_name} (ID: {page_id})")
    print(f"Awakening URL: {awakening_url}")
    print('='*70)

    # Get current page data
    print("  Fetching current Elementor data...")
    data = get_page_data(page_id)
    meta = data.get("meta", {})
    ed_str = meta.get("_elementor_data", "")

    if not ed_str:
        print("  ERROR: No _elementor_data found")
        return False

    el_data = json.loads(ed_str)

    # Find main widget
    ci, wi, html = find_main_widget(el_data)
    if html is None:
        print("  ERROR: Cannot find main HTML widget")
        return False

    print(f"  Found widget at el_data[{ci}].elements[{wi}], HTML length: {len(html)}")

    # Diagnose
    diagnose_html(html, page_name, awakening_url)

    modified = False

    # Fix 1: Watch Demo button modal + autoplay
    print(f"\n  [FIX 1] Watch Demo button -> modal autoplay")
    html, changed = fix_watch_demo_button_href(html, page_id, awakening_url)
    if changed:
        modified = True

    # Fix 2: Fix awakening links
    print(f"\n  [FIX 2] Awakening link URLs")
    html, changed = fix_watch_demo_link(html, page_id, awakening_url)
    if changed:
        modified = True

    # Fix 3: Fix/add embedded video section
    print(f"\n  [FIX 3] Embedded video section (Pure Brain Demo Video)")
    html, changed = fix_embedded_video(html, page_id, awakening_url)
    if changed:
        modified = True

    if not modified:
        print(f"\n  No changes needed for {page_name}")
        return True

    print(f"\n  Updating WordPress (new HTML length: {len(html)})...")
    el_data[ci]["elements"][wi]["settings"]["html"] = html

    status = update_page(page_id, el_data)
    print(f"  Update status: HTTP {status}")

    # Clear cache
    print("  Clearing Elementor cache...")
    clear_cache()
    time.sleep(3)
    touch_page(page_id)
    time.sleep(5)

    # Verify
    print("  Verifying stored data...")
    verify_data = get_page_data(page_id)
    verify_ed = verify_data.get("meta", {}).get("_elementor_data", "")

    checks = {
        "pb-demo-section": "pb-demo-section" in verify_ed,
        "openVideoModal with HLS": "startModalHls" in verify_ed,
        "Pure Brain Demo URL": "75114256_Pure-Brain-Demo-Video" in verify_ed or "eaf39ae1_Portal_demo" in verify_ed,
        "awakening URL correct": awakening_url in verify_ed,
    }

    print(f"\n  VERIFICATION:")
    all_good = True
    for check, passed in checks.items():
        status_str = "PASS" if passed else "FAIL"
        print(f"    {status_str}: {check}")
        if not passed:
            all_good = False

    return all_good


def main():
    print("PureBrain Video Fix v2 - 2026-03-01")
    print("Fixes: Watch Demo autoplay + Embedded video + Awakening links")
    print("")

    results = {}
    for page_id, page_name, awakening_url in PAGES:
        try:
            success = process_page(page_id, page_name, awakening_url)
            results[page_name] = "PASS" if success else "FAIL"
        except Exception as e:
            print(f"  EXCEPTION on {page_name}: {e}")
            import traceback
            traceback.print_exc()
            results[page_name] = "ERROR"

    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    for page_name, result in results.items():
        print(f"  {result}: {page_name}")

    all_pass = all(v == "PASS" for v in results.values())
    print(f"\nOverall: {'ALL PASSED' if all_pass else 'SOME FAILURES'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
