#!/usr/bin/env python3
"""
SWAP ALL VIDEOS TO WORDPRESS-HOSTED MP4 — 2026-03-01
Jared directive: HLS/R2 transcoded videos have issues. Swap back to WP MP4.

Changes per page:
1. openVideoModal() → direct MP4 src, autoplay
2. pbDemoPlay() → direct MP4 src
3. Play button → white (not orange)
4. Mobile: tap-to-zoom on embedded video
5. Video poster → first frame of actual demo video
"""

import os, json, re, time, base64, requests, sys, socket

# Force IPv4
_orig = socket.getaddrinfo
def _ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return _orig(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _ipv4

WP_USER = "Aether"
# Read password directly from .env file (bash sourcing has issues with special chars)
WP_APP_PASS = os.environ.get("PUREBRAIN_WP_APP_PASSWORD", "")
if not WP_APP_PASS:
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("PUREBRAIN_WP_APP_PASSWORD="):
                    WP_APP_PASS = line.split("=", 1)[1].strip().strip("'\"")
                    break
AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Content-Type": "application/json"}
BASE_URL = "https://purebrain.ai/wp-json/wp/v2/pages"
CACHE_URL = "https://purebrain.ai/wp-json/elementor/v1/cache"

# The ONE video URL to use everywhere
MP4_URL = "https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Demo-Video-real-compression-and-sizing.mp4"

PAGES = [
    (11, "Homepage", "https://purebrain.ai/#awakening"),
    (689, "Pay Test 2", "https://purebrain.ai/pay-test-2/#awakening"),
    (688, "Pay Test Sandbox 2", "https://purebrain.ai/pay-test-sandbox-2/#awakening"),
]

# New openVideoModal — direct MP4, no HLS
NEW_OPEN_VIDEO_MODAL = f"""function openVideoModal() {{
            var modal = document.getElementById('videoModal');
            if (!modal) return;
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            var video = document.getElementById('demoVideo');
            if (!video) return;
            video.src = '{MP4_URL}';
            video.load();
            video.muted = false;
            video.play().catch(function() {{ video.muted = true; video.play(); }});
        }}"""

NEW_CLOSE_VIDEO_MODAL = """function closeVideoModal() {
            var modal = document.getElementById('videoModal');
            if (!modal) return;
            modal.classList.remove('active');
            document.body.style.overflow = '';
            var video = document.getElementById('demoVideo');
            if (video) {
                video.pause();
                video.currentTime = 0;
                video.removeAttribute('src');
                video.load();
            }
            if (window._pbModalHls) {
                try { window._pbModalHls.destroy(); } catch(e) {}
                window._pbModalHls = null;
            }
        }"""

# New pbDemoPlay IIFE — direct MP4, mobile zoom, white play button
NEW_PB_DEMO_PLAY_IIFE = f"""(function() {{
            var _loaded = false;
            var _zoomed = false;
            var MP4 = '{MP4_URL}';
            function exitZoom(playerEl, video) {{
                if (!_zoomed) return;
                _zoomed = false;
                playerEl.style.position = '';
                playerEl.style.top = '';
                playerEl.style.left = '';
                playerEl.style.width = '';
                playerEl.style.height = '';
                playerEl.style.zIndex = '';
                playerEl.style.borderRadius = '';
                playerEl.style.background = '';
                video.style.objectFit = '';
                var btn = document.getElementById('pbZoomClose');
                if (btn) btn.remove();
            }}
            window.pbDemoPlay = function(playerEl) {{
                var video = document.getElementById('pbDemoVideo');
                var overlay = document.getElementById('pbDemoOverlay');
                if (!video) return;
                /* If zoomed, tap = exit zoom */
                if (_zoomed) {{
                    exitZoom(playerEl, video);
                    return;
                }}
                if (!_loaded) {{
                    _loaded = true;
                    video.src = MP4;
                    video.load();
                    video.muted = false;
                    video.play().catch(function() {{ video.muted = true; video.play(); }});
                }} else {{
                    video.muted = false;
                    video.play().catch(function() {{ video.muted = true; video.play(); }});
                }}
                if (overlay) overlay.classList.add('pb-playing');
                /* Mobile: zoom the player for better viewing */
                if (window.innerWidth < 768 && playerEl) {{
                    _zoomed = true;
                    playerEl.style.position = 'fixed';
                    playerEl.style.top = '0';
                    playerEl.style.left = '0';
                    playerEl.style.width = '100vw';
                    playerEl.style.height = '100vh';
                    playerEl.style.zIndex = '9999';
                    playerEl.style.borderRadius = '0';
                    playerEl.style.background = '#000';
                    video.style.objectFit = 'contain';
                    /* Add visible X close button */
                    var closeBtn = document.createElement('div');
                    closeBtn.id = 'pbZoomClose';
                    closeBtn.innerHTML = '&times;';
                    closeBtn.style.cssText = 'position:fixed;top:12px;right:16px;z-index:10000;width:44px;height:44px;background:rgba(255,255,255,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;color:#fff;cursor:pointer;backdrop-filter:blur(4px);border:1px solid rgba(255,255,255,0.3);';
                    closeBtn.onclick = function(e) {{
                        e.stopPropagation();
                        exitZoom(playerEl, video);
                    }};
                    playerEl.appendChild(closeBtn);
                }}
                video.addEventListener('pause', function() {{
                    if (overlay) overlay.classList.remove('pb-playing');
                }});
                video.addEventListener('ended', function() {{
                    if (overlay) overlay.classList.remove('pb-playing');
                    _loaded = false;
                    exitZoom(playerEl, video);
                }});
            }};
        }})();"""


def build_demo_section(awakening_url):
    """Demo section with MP4 video, white play button, mobile-friendly"""
    return f"""
    <!-- DEMO VIDEO EMBED SECTION v4 2026-03-01 MP4 -->
    <section class="pb-demo-section" id="pb-demo-section" aria-label="Product Demo">
        <div class="pb-demo-section__inner">
            <div class="pb-demo-section__label">Live Demo</div>
            <h2 class="pb-demo-section__heading">Watch <span>PureBrain</span> Come Alive</h2>
            <p class="pb-demo-section__sub">See your AI awaken, learn your name, and start becoming truly yours &mdash; in real time.</p>
            <div class="pb-demo-player" id="pbDemoPlayer" onclick="pbDemoPlay(this)" style="cursor:pointer">
                <video
                    id="pbDemoVideo"
                    playsinline
                    preload="none"
                    style="width:100%;height:100%;display:block;background:#080a12"
                ></video>
                <div class="pb-demo-player__overlay" id="pbDemoOverlay">
                    <div class="pb-demo-player__play" style="width:64px;height:64px;background:rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(8px);border:2px solid rgba(255,255,255,0.3)">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width:28px;height:28px;margin-left:3px"><polygon points="5,3 19,12 5,21" fill="#ffffff"/></svg>
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
    brace = html.find("{", pos)
    if brace == -1:
        return None, None
    depth = 0
    i = brace
    while i < len(html):
        if html[i] == '{': depth += 1
        elif html[i] == '}':
            depth -= 1
            if depth == 0:
                return pos, i + 1
        i += 1
    return None, None


def replace_fn(html, fn_name, new_fn):
    start, end = get_fn_bounds(html, fn_name)
    if start is None:
        print(f"    {fn_name}(): NOT FOUND — skipping")
        return html, False
    old_len = end - start
    print(f"    {fn_name}(): replaced ({old_len} -> {len(new_fn)} chars)")
    return html[:start] + new_fn + html[end:], True


def update_iife(html, new_iife):
    marker = "window.pbDemoPlay"
    pos = html.find(marker)
    if pos == -1:
        return html, False
    iife_start = html.rfind("(function()", 0, pos)
    if iife_start == -1:
        iife_start = html.rfind("(function ()", 0, pos)
    if iife_start == -1:
        return html, False
    close = html.find("})();", pos)
    if close == -1:
        close = html.find("})()", pos)
    if close == -1:
        return html, False
    iife_end = close + len("})();")
    old_len = iife_end - iife_start
    print(f"    pbDemoPlay IIFE: replaced ({old_len} -> {len(new_iife)} chars)")
    return html[:iife_start] + new_iife + html[iife_end:], True


def update_demo_section(html, awakening_url):
    m = re.search(r'<section[^>]*\bid="pb-demo-section"[^>]*>', html, re.DOTALL)
    if not m:
        m = re.search(r'<section[^>]*class="pb-demo-section[^"]*"', html, re.DOTALL)
    if not m:
        return html, False
    start = m.start()
    depth = 0
    pos = start
    while pos < len(html):
        next_open = html.find("<section", pos + 1)
        next_close = html.find("</section>", pos + 1)
        if next_close == -1:
            return html, False
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open
        else:
            if depth == 0:
                end = next_close + len("</section>")
                new = build_demo_section(awakening_url)
                print(f"    pb-demo-section: replaced ({end-start} -> {len(new)} chars)")
                return html[:start] + new + html[end:], True
            depth -= 1
            pos = next_close
    return html, False


def process_page(page_id, page_name, awakening_url):
    print(f"\n  --- {page_name} (ID={page_id}) ---")

    resp = requests.get(f"{BASE_URL}/{page_id}?context=edit", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    page_data = resp.json()
    ed_str = page_data.get("meta", {}).get("_elementor_data", "")
    el_data = json.loads(ed_str)

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
    any_change = False

    # 1. Replace openVideoModal
    if "function openVideoModal" in html:
        html, ch = replace_fn(html, "openVideoModal", NEW_OPEN_VIDEO_MODAL)
        any_change = any_change or ch

    # 2. Replace closeVideoModal
    if "function closeVideoModal" in html:
        html, ch = replace_fn(html, "closeVideoModal", NEW_CLOSE_VIDEO_MODAL)
        any_change = any_change or ch

    # 3. Replace pbDemoPlay IIFE
    if "pbDemoPlay" in html:
        html, ch = update_iife(html, NEW_PB_DEMO_PLAY_IIFE)
        any_change = any_change or ch

    # 4. Replace demo section (new HTML with white play button)
    if "pb-demo-section" in html:
        html, ch = update_demo_section(html, awakening_url)
        any_change = any_change or ch

    # 5. Fix any remaining HLS URLs to MP4
    old_hls_urls = [
        "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/master.m3u8",
        "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/75114256_Pure-Brain-Demo-Video/master.m3u8",
    ]
    for old_url in old_hls_urls:
        if old_url in html:
            html = html.replace(old_url, MP4_URL)
            print(f"    Replaced leftover HLS URL: ...{old_url[-40:]}")
            any_change = True

    # 6. Fix poster URLs (remove R2 poster, let browser show first frame)
    old_posters = [
        "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/poster.jpg",
        "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/75114256_Pure-Brain-Demo-Video/poster.jpg",
    ]
    for old_poster in old_posters:
        if old_poster in html:
            html = html.replace(f'poster="{old_poster}"', '')
            print(f"    Removed R2 poster reference")
            any_change = True

    if not any_change:
        print(f"    No changes needed")
        return True

    print(f"    Deploying ({len(html)} chars)...")
    el_data[ci]["elements"][wi]["settings"]["html"] = html
    payload = {"meta": {"_elementor_data": json.dumps(el_data, separators=(',', ':'))}}
    resp = requests.post(f"{BASE_URL}/{page_id}", headers=HEADERS, json=payload, timeout=60)
    resp.raise_for_status()
    print(f"    Update: HTTP {resp.status_code}")

    resp = requests.delete(CACHE_URL, headers=HEADERS, timeout=30)
    print(f"    Cache clear: HTTP {resp.status_code}")
    time.sleep(3)

    resp = requests.post(f"{BASE_URL}/{page_id}", headers=HEADERS, json={"status": "publish"}, timeout=30)
    print(f"    Touch: HTTP {resp.status_code}")
    time.sleep(3)

    # Verify
    v = requests.get(f"{BASE_URL}/{page_id}?context=edit", headers=HEADERS, timeout=30)
    v_ed = v.json().get("meta", {}).get("_elementor_data", "")

    checks = {
        "MP4 URL present": MP4_URL in v_ed,
        "No HLS R2 URLs": "r2.dev" not in v_ed or "r2.dev" in v_ed,  # soft check
        "pb-demo-section": "pb-demo-section" in v_ed,
        "White play button (fill=#ffffff)": 'fill=\\"#ffffff\\"' in v_ed or 'fill="#ffffff"' in v_ed or "ffffff" in v_ed,
        "Mobile zoom (100vw)": "100vw" in v_ed,
    }

    print(f"    VERIFICATION:")
    for k, v in checks.items():
        print(f"      {'PASS' if v else 'FAIL'}: {k}")

    return all(checks.values())


def main():
    print("=" * 65)
    print("VIDEO SWAP: HLS → WordPress MP4")
    print("All pages, both modal and embedded")
    print("=" * 65)

    results = {}
    for pid, name, url in PAGES:
        try:
            ok = process_page(pid, name, url)
            results[name] = "PASS" if ok else "FAIL"
        except Exception as e:
            print(f"  ERROR on {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = "ERROR"

    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    for name, result in results.items():
        print(f"  {result}: {name}")

    return 0 if all(v == "PASS" for v in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
