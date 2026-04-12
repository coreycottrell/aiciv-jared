#!/usr/bin/env python3
"""
VIDEO FIX FINAL - 2026-03-01
CTO-directed fix for live video issues on purebrain.ai

ISSUES:
1. Watch Demo button: video opens but does NOT autoplay - modal HLS not initiating playback
2. Embedded video section: not playing at all

ROOT CAUSE (based on code review):
- openVideoModal() likely just shows the modal div but never calls HLS.loadSource() or video.play()
- The embedded section uses click-to-play (correct) but may have wrong HLS URL

FIXES:
1. Rewrite openVideoModal() to load HLS and autoplay Portal Demo video
2. Update pb-demo-section to use Pure Brain Demo Video URL (new upload)
3. Fix all awakening links to correct page-specific URLs

Pages:
- Homepage (11): https://purebrain.ai/#awakening
- Pay Test 2 (689): https://purebrain.ai/pay-test-2/#awakening
- Pay Test Sandbox 2 (688): https://purebrain.ai/pay-test-sandbox-2/#awakening
"""

import json
import base64
import time
import requests
import re
import sys
import traceback

WP_USER = "Aether"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"
AUTH = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Content-Type": "application/json"}
BASE_URL = "https://purebrain.ai/wp-json/wp/v2/pages"
CACHE_URL = "https://purebrain.ai/wp-json/elementor/v1/cache"

# Video assets
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
# TEMPLATE: openVideoModal (with HLS autoplay)
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
            if (video.readyState >= 3 && video.src) {{
                video.play().catch(function() {{ video.muted = true; video.play(); }});
                return;
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

# ============================================================
# TEMPLATE: closeVideoModal (with HLS cleanup)
# ============================================================
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

# ============================================================
# TEMPLATE: pbDemoPlay IIFE (for embedded section)
# ============================================================
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

# ============================================================
# TEMPLATE: pb-demo-section HTML
# ============================================================
def build_demo_section_html(awakening_url):
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


# ============================================================
# HELPERS
# ============================================================

def get_fn_bounds(html, fn_name):
    """Find start/end positions of a named function in HTML.
    Returns (start, end) or (None, None) if not found."""
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


def replace_function(html, fn_name, new_fn_str):
    """Replace an existing function in the HTML with new_fn_str."""
    start, end = get_fn_bounds(html, fn_name)
    if start is None:
        print(f"    WARNING: function {fn_name}() not found for replacement")
        return html, False
    old = html[start:end]
    print(f"    Replacing {fn_name}() ({len(old)} chars -> {len(new_fn_str)} chars)")
    return html[:start] + new_fn_str + html[end:], True


def replace_iife_by_marker(html, marker, new_iife_str):
    """Find an IIFE containing the marker text and replace it."""
    marker_pos = html.find(marker)
    if marker_pos == -1:
        return html, False

    # Find the IIFE start: look backwards for "(function()"
    iife_pos = html.rfind("(function()", 0, marker_pos)
    if iife_pos == -1:
        # try "(function ()"
        iife_pos = html.rfind("(function ()", 0, marker_pos)
    if iife_pos == -1:
        print(f"    WARNING: Cannot find IIFE start before marker '{marker[:40]}'")
        return html, False

    # Find the IIFE end: look for })(); after the marker
    iife_end_search = html.find("})();", marker_pos)
    if iife_end_search == -1:
        iife_end_search = html.find("})()", marker_pos)
    if iife_end_search == -1:
        print(f"    WARNING: Cannot find IIFE end after marker '{marker[:40]}'")
        return html, False

    iife_end = iife_end_search + len("})();")
    old_iife = html[iife_pos:iife_end]
    print(f"    Replacing pbDemoPlay IIFE ({len(old_iife)} chars -> {len(new_iife_str)} chars)")
    return html[:iife_pos] + new_iife_str + html[iife_end:], True


def fix_awakening_links(html, awakening_url):
    """Fix all awakening-related hrefs in the page to the correct URL."""
    changed = False

    # Pattern: any href containing "awakening" that isn't already correct
    def replace_awk(match):
        nonlocal changed
        current = match.group(0)
        if awakening_url in current:
            return current  # already correct
        changed = True
        return f'href="{awakening_url}"'

    new_html = re.sub(r'href=["\'][^"\']*awakening[^"\']*["\']', replace_awk, html)

    if changed:
        print(f"    Fixed awakening href(s) -> {awakening_url}")

    # Also fix pb-demo-section CTA link (may use #pb-chatbox or old URL)
    # Pattern: the "Begin your awakening" link inside pb-demo-section
    begin_pattern = re.compile(
        r'(Begin your awakening[^<]*</a>)',
        re.DOTALL
    )

    def fix_begin(match):
        nonlocal changed
        return match.group(0)  # just find and check

    # More targeted: find the pb-demo-section CTA anchor
    cta_pattern = re.compile(
        r'(<a\s[^>]*>Ready to try it yourself\?.*?</a>)',
        re.DOTALL
    )
    # Actually look for the cta paragraph
    cta_p_pattern = re.compile(
        r'(<p class="pb-demo-section__cta">.*?</p>)',
        re.DOTALL
    )
    cta_match = cta_p_pattern.search(new_html)
    if cta_match:
        old_cta = cta_match.group(0)
        new_cta = f'<p class="pb-demo-section__cta">Ready to try it yourself? <a href="{awakening_url}">Begin your awakening &rarr;</a></p>'
        if old_cta != new_cta:
            new_html = new_html[:cta_match.start()] + new_cta + new_html[cta_match.end():]
            print(f"    Fixed pb-demo-section CTA link -> {awakening_url}")
            changed = True

    return new_html, changed


def replace_demo_section(html, awakening_url):
    """Replace the entire pb-demo-section with the new version."""
    # Find the section start
    section_pattern = re.compile(r'<section[^>]*\bid="pb-demo-section"[^>]*>', re.DOTALL)
    match = section_pattern.search(html)
    if not match:
        # Also try class-based search
        section_pattern2 = re.compile(r'<section[^>]*\bpb-demo-section\b[^>]*>', re.DOTALL)
        match = section_pattern2.search(html)

    if not match:
        print(f"    pb-demo-section not found - cannot replace")
        return html, False

    section_start = match.start()

    # Find the end of this section by matching braces/tags
    # Count <section> depth from section_start
    depth = 0
    pos = section_start
    while pos < len(html):
        # Look for next <section or </section>
        next_open = html.find("<section", pos + 1)
        next_close = html.find("</section>", pos + 1)

        if next_close == -1:
            break

        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open
        else:
            if depth == 0:
                section_end = next_close + len("</section>")
                old_section = html[section_start:section_end]
                new_section = build_demo_section_html(awakening_url)
                print(f"    Replaced pb-demo-section ({len(old_section)} -> {len(new_section)} chars)")
                return html[:section_start] + new_section + html[section_end:], True
            depth -= 1
            pos = next_close

    print("    ERROR: Could not find pb-demo-section closing tag")
    return html, False


def insert_demo_section(html, awakening_url):
    """Insert pb-demo-section after the hero section (when not yet present)."""
    # Find hero close: the </section> after the "Watch Demo" button
    wd_pos = html.find("Watch Demo")
    if wd_pos == -1:
        print("    ERROR: 'Watch Demo' not found - cannot insert demo section")
        return html, False

    hero_close = html.find("</section>", wd_pos)
    if hero_close == -1:
        print("    ERROR: Hero </section> not found")
        return html, False

    insert_pos = hero_close + len("</section>")
    new_section = build_demo_section_html(awakening_url)
    html = html[:insert_pos] + new_section + html[insert_pos:]
    print(f"    Inserted pb-demo-section after hero (pos {insert_pos})")
    return html, True


def insert_pb_demo_script(html):
    """Insert pbDemoPlay IIFE into the script block."""
    # Find openVideoModal's script block end
    ovm_pos = html.find("function openVideoModal()")
    if ovm_pos != -1:
        script_close = html.find("</script>", ovm_pos)
    else:
        script_close = html.rfind("</script>")

    if script_close == -1:
        print("    ERROR: Cannot find </script> for IIFE insertion")
        return html, False

    html = html[:script_close] + "\n        " + PB_DEMO_PLAY_IIFE + "\n        " + html[script_close:]
    print(f"    Inserted pbDemoPlay IIFE before </script>")
    return html, True


def process_page(page_id, page_name, awakening_url):
    print(f"\n{'='*65}")
    print(f"PAGE: {page_name} (ID={page_id})")
    print(f"Target awakening URL: {awakening_url}")
    print('='*65)

    # Fetch
    resp = requests.get(f"{BASE_URL}/{page_id}?context=edit", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    page_data = resp.json()
    meta = page_data.get("meta", {})
    ed_str = meta.get("_elementor_data", "")
    el_data = json.loads(ed_str)

    # Find widget
    ci, wi, html = None, None, None
    for c_idx, container in enumerate(el_data):
        for w_idx, widget in enumerate(container.get("elements", [])):
            hc = widget.get("settings", {}).get("html", "")
            if len(hc) > 50000 and "Watch Demo" in hc:
                ci, wi, html = c_idx, w_idx, hc
                print(f"  Widget: el_data[{ci}].elements[{wi}] len={len(hc)}")
                break
        if html is not None:
            break

    if html is None:
        print("  ERROR: Main widget not found")
        return False

    # --- DIAGNOSTIC ---
    print(f"\n  CURRENT STATE:")
    print(f"  - openVideoModal: {'YES' if 'function openVideoModal' in html else 'NO'}")
    print(f"  - closeVideoModal: {'YES' if 'function closeVideoModal' in html else 'NO'}")
    print(f"  - pbDemoPlay: {'YES' if 'pbDemoPlay' in html else 'NO'}")
    print(f"  - pb-demo-section: {'YES' if 'pb-demo-section' in html else 'NO'}")
    print(f"  - Portal Demo HLS: {'YES' if 'eaf39ae1_Portal_demo' in html else 'NO'}")
    print(f"  - PureBrain Demo HLS: {'YES' if '75114256_Pure-Brain-Demo-Video' in html else 'NO'}")
    print(f"  - startModalHls (already fixed): {'YES' if 'startModalHls' in html else 'NO'}")
    awk_links = re.findall(r'href=["\'][^"\']*awakening[^"\']*["\']', html)
    print(f"  - Awakening links: {awk_links}")

    # --- FIXES ---
    any_change = False

    # FIX 1: openVideoModal - rewrite with HLS autoplay
    print(f"\n  [FIX 1] openVideoModal() -> HLS autoplay")
    if "function openVideoModal" in html:
        if "startModalHls" in html:
            print(f"    Already fixed (startModalHls found) - skipping")
        else:
            html, changed = replace_function(html, "openVideoModal", OPEN_VIDEO_MODAL_FN)
            any_change = any_change or changed
    else:
        print(f"    openVideoModal not found - skipping")

    # FIX 2: closeVideoModal - rewrite with HLS cleanup
    print(f"\n  [FIX 2] closeVideoModal() -> cleanup HLS")
    if "function closeVideoModal" in html:
        if "_pbModalHls" in html:
            print(f"    Already fixed (_pbModalHls found) - skipping")
        else:
            html, changed = replace_function(html, "closeVideoModal", CLOSE_VIDEO_MODAL_FN)
            any_change = any_change or changed
    else:
        print(f"    closeVideoModal not found - skipping")

    # FIX 3: pbDemoPlay IIFE - update to use PureBrain Demo Video URL
    print(f"\n  [FIX 3] pbDemoPlay IIFE -> Pure Brain Demo Video URL")
    if "pbDemoPlay" in html:
        if "75114256_Pure-Brain-Demo-Video" in html:
            print(f"    Already using Pure Brain Demo Video URL")
            # Still replace to update any other issues
        html, changed = replace_iife_by_marker(html, "window.pbDemoPlay", PB_DEMO_PLAY_IIFE)
        any_change = any_change or changed
    else:
        # Need to insert it
        html, changed = insert_pb_demo_script(html)
        any_change = any_change or changed

    # FIX 4: pb-demo-section HTML - replace or insert
    print(f"\n  [FIX 4] pb-demo-section HTML")
    if "pb-demo-section" in html:
        html, changed = replace_demo_section(html, awakening_url)
        any_change = any_change or changed
    else:
        html, changed = insert_demo_section(html, awakening_url)
        any_change = any_change or changed
        if changed:
            # Also need to add the script
            if "pbDemoPlay" not in html:
                html, sc = insert_pb_demo_script(html)
                any_change = any_change or sc

    # FIX 5: Awakening link URLs
    print(f"\n  [FIX 5] Awakening link URLs -> {awakening_url}")
    html, changed = fix_awakening_links(html, awakening_url)
    any_change = any_change or changed

    if not any_change:
        print(f"\n  No changes needed for {page_name}")
        return True

    # Deploy
    print(f"\n  Deploying (HTML len {len(html)})...")
    el_data[ci]["elements"][wi]["settings"]["html"] = html
    payload = {"meta": {"_elementor_data": json.dumps(el_data, separators=(',', ':'))}}
    resp = requests.post(f"{BASE_URL}/{page_id}", headers=HEADERS, json=payload, timeout=60)
    resp.raise_for_status()
    print(f"  Update: HTTP {resp.status_code}")

    # Clear cache
    resp = requests.delete(CACHE_URL, headers=HEADERS, timeout=30)
    print(f"  Cache clear: HTTP {resp.status_code}")
    time.sleep(3)

    # Touch page
    resp = requests.post(f"{BASE_URL}/{page_id}", headers=HEADERS, json={"status": "publish"}, timeout=30)
    print(f"  Touch: HTTP {resp.status_code}")
    time.sleep(5)

    # Verify
    verify_resp = requests.get(f"{BASE_URL}/{page_id}?context=edit", headers=HEADERS, timeout=30)
    verify_resp.raise_for_status()
    verify_ed = verify_resp.json().get("meta", {}).get("_elementor_data", "")

    print(f"\n  VERIFICATION:")
    checks = {
        "openVideoModal with HLS autoplay (startModalHls)": "startModalHls" in verify_ed,
        "closeVideoModal with HLS cleanup (_pbModalHls)": "_pbModalHls" in verify_ed,
        "pb-demo-section present": "pb-demo-section" in verify_ed,
        "pbDemoPlay script present": "pbDemoPlay" in verify_ed,
        "Pure Brain Demo Video URL": "75114256_Pure-Brain-Demo-Video" in verify_ed,
        f"Awakening URL ({awakening_url})": awakening_url in verify_ed,
    }

    all_pass = True
    for check, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"    {status}: {check}")

    return all_pass


def main():
    print("PureBrain Video Fix Final - 2026-03-01")
    print("BUILD -> SECURITY -> QA -> SHIP")
    print("")

    results = {}
    for page_id, page_name, awakening_url in PAGES:
        try:
            success = process_page(page_id, page_name, awakening_url)
            results[page_name] = "PASS" if success else "FAIL"
        except Exception as e:
            print(f"\nEXCEPTION on {page_name}: {e}")
            traceback.print_exc()
            results[page_name] = "ERROR"

    print("\n" + "="*65)
    print("FINAL RESULTS")
    print("="*65)
    for name, result in results.items():
        print(f"  {result}: {name}")

    all_pass = all(v == "PASS" for v in results.values())
    print(f"\nOverall: {'ALL PASSED' if all_pass else 'SOME FAILURES - review above'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
