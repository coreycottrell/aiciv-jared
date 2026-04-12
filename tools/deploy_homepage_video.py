#!/usr/bin/env python3
"""
Deploy embedded video section to purebrain.ai homepage (page 11)
and then to pay-test-2 (689) and pay-test-sandbox-2 (688).

Strategy:
- Homepage page 11: Insert new VIDEO DEMO SECTION between hero and marquee
- Pay-test pages: Search for same insertion marker or append before marquee
"""

import os
import json
import base64
import time
import requests
import sys

# Credentials
WP_USER = "Aether"
WP_PASS = os.environ.get("PUREBRAIN_WP_APP_PASSWORD", "")
if not WP_PASS:
    print("ERROR: PUREBRAIN_WP_APP_PASSWORD not set")
    sys.exit(1)

AUTH = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Content-Type": "application/json"}
BASE_URL = "https://purebrain.ai/wp-json/wp/v2/pages"
ELEMENTOR_CACHE_URL = "https://purebrain.ai/wp-json/elementor/v1/cache"

HLS_URL = "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/master.m3u8"
POSTER_URL = "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/poster.jpg"

# The new embedded video section to inject
# Uses pb-demo-embed__ prefix to avoid any collision with modal's demoVideo/videoModal IDs
VIDEO_SECTION_CSS = """
        /* ============================================
           DEMO VIDEO EMBED SECTION
           ============================================ */
        .pb-demo-section {
            padding: 80px 20px;
            background: linear-gradient(180deg, rgba(8,10,18,0) 0%, rgba(8,10,18,1) 8%, rgba(8,10,18,1) 92%, rgba(8,10,18,0) 100%);
            position: relative;
            z-index: 1;
        }

        .pb-demo-section__inner {
            max-width: 960px;
            margin: 0 auto;
            text-align: center;
        }

        .pb-demo-section__label {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(241, 66, 11, 0.12);
            border: 1px solid rgba(241, 66, 11, 0.3);
            border-radius: 100px;
            padding: 6px 16px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #f1420b;
            margin-bottom: 24px;
        }

        .pb-demo-section__label::before {
            content: '';
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #f1420b;
            border-radius: 50%;
            animation: pb-demo-pulse 1.8s ease-in-out infinite;
        }

        @keyframes pb-demo-pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.7); }
        }

        .pb-demo-section__heading {
            font-size: clamp(28px, 4vw, 44px);
            font-weight: 700;
            color: #ffffff;
            margin: 0 0 12px 0;
            line-height: 1.15;
            letter-spacing: -0.02em;
        }

        .pb-demo-section__heading span {
            background: linear-gradient(135deg, #f1420b 0%, #ff6b35 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .pb-demo-section__sub {
            font-size: 16px;
            color: rgba(255,255,255,0.55);
            margin: 0 0 40px 0;
            max-width: 520px;
            margin-left: auto;
            margin-right: auto;
        }

        .pb-demo-player {
            position: relative;
            width: 100%;
            padding-top: 56.25%; /* 16:9 */
            border-radius: 16px;
            overflow: hidden;
            background: #000;
            box-shadow: 0 0 0 1px rgba(255,255,255,0.08),
                        0 24px 80px rgba(0,0,0,0.7),
                        0 0 60px rgba(241,66,11,0.08);
            cursor: pointer;
        }

        .pb-demo-player video {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        .pb-demo-player__overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(0,0,0,0.3);
            transition: background 0.3s ease, opacity 0.3s ease;
            z-index: 2;
        }

        .pb-demo-player__overlay.pb-playing {
            opacity: 0;
            pointer-events: none;
        }

        .pb-demo-player__play {
            width: 72px;
            height: 72px;
            background: rgba(241,66,11,0.92);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s ease, background 0.2s ease;
            box-shadow: 0 0 0 12px rgba(241,66,11,0.15), 0 0 40px rgba(241,66,11,0.3);
        }

        .pb-demo-player:hover .pb-demo-player__play {
            transform: scale(1.08);
            background: #f1420b;
        }

        .pb-demo-player__play svg {
            width: 28px;
            height: 28px;
            fill: #fff;
            margin-left: 4px;
        }

        .pb-demo-section__cta {
            margin-top: 32px;
            font-size: 14px;
            color: rgba(255,255,255,0.45);
        }

        .pb-demo-section__cta a {
            color: #f1420b;
            text-decoration: none;
            font-weight: 600;
        }

        .pb-demo-section__cta a:hover {
            text-decoration: underline;
        }
"""

VIDEO_SECTION_HTML = f"""
    <!-- ============================================
         DEMO VIDEO EMBED SECTION
         ============================================ -->
    <section class="pb-demo-section" id="pb-demo-section" aria-label="Product Demo">
        <div class="pb-demo-section__inner">
            <div class="pb-demo-section__label">Live Demo</div>
            <h2 class="pb-demo-section__heading">Watch <span>PureBrain</span> Come Alive</h2>
            <p class="pb-demo-section__sub">See your AI awaken, learn your name, and start becoming truly yours — in real time.</p>
            <div class="pb-demo-player" id="pbDemoPlayer" onclick="pbDemoPlay(this)">
                <video
                    id="pbDemoVideo"
                    poster="{POSTER_URL}"
                    playsinline
                    muted
                    preload="none"
                ></video>
                <div class="pb-demo-player__overlay" id="pbDemoOverlay">
                    <div class="pb-demo-player__play">
                        <svg viewBox="0 0 24 24"><polygon points="5,3 19,12 5,21"/></svg>
                    </div>
                </div>
            </div>
            <p class="pb-demo-section__cta">Ready to try it yourself? <a href="#pb-chatbox" onclick="document.getElementById('pb-chatbox') && document.getElementById('pb-chatbox').scrollIntoView({{behavior:'smooth'}})">Begin your awakening</a></p>
        </div>
    </section>
"""

VIDEO_SECTION_SCRIPT = f"""
        /* ---- Embedded Demo Player (pb-demo-section) ---- */
        (function() {{
            var _pbDemoHls = null;
            var _pbDemoLoaded = false;
            window.pbDemoPlay = function(playerEl) {{
                var video = document.getElementById('pbDemoVideo');
                var overlay = document.getElementById('pbDemoOverlay');
                if (!video) return;
                if (!_pbDemoLoaded) {{
                    _pbDemoLoaded = true;
                    var hlsUrl = '{HLS_URL}';
                    function startEmbedHls(Hls) {{
                        if (_pbDemoHls) {{ _pbDemoHls.destroy(); }}
                        if (Hls.isSupported()) {{
                            _pbDemoHls = new Hls({{startLevel:-1, maxBufferLength:20}});
                            _pbDemoHls.loadSource(hlsUrl);
                            _pbDemoHls.attachMedia(video);
                            _pbDemoHls.on(Hls.Events.MANIFEST_PARSED, function() {{
                                video.muted = false;
                                video.play().catch(function() {{ video.muted = true; video.play(); }});
                            }});
                        }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                            video.src = hlsUrl;
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
                }}, {{once: false}});
                video.addEventListener('ended', function() {{
                    if (overlay) overlay.classList.remove('pb-playing');
                    _pbDemoLoaded = false;
                }});
            }};
        }})();
"""


def get_page_elementor_data(page_id):
    resp = requests.get(f"{BASE_URL}/{page_id}?context=edit", headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    meta = data.get("meta", {})
    ed = meta.get("_elementor_data", "")
    return json.loads(ed)


def clear_elementor_cache():
    resp = requests.delete(ELEMENTOR_CACHE_URL, headers=HEADERS)
    print(f"  Cache clear: {resp.status_code}")


def touch_page(page_id):
    resp = requests.post(f"{BASE_URL}/{page_id}", headers=HEADERS, json={"status": "publish"})
    print(f"  Touch page {page_id}: {resp.status_code}")


def update_page_elementor(page_id, el_data):
    payload = {"meta": {"_elementor_data": json.dumps(el_data, separators=(',', ':'))}}
    resp = requests.post(f"{BASE_URL}/{page_id}", headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.status_code


def inject_video_into_html(html_content, css_snippet, html_snippet, script_snippet):
    """
    Injects:
    1. CSS into the <style> block (find last </style> before </head> and insert before it)
    2. HTML section after the hero </section> and before the marquee
    3. Script snippet before the closing </script> of the last script block in the page
    """

    # --- 1. Inject CSS ---
    # Find the last </style> tag before the body
    head_end = html_content.find("</head>")
    if head_end == -1:
        print("  WARNING: No </head> found, trying last </style>")
        last_style_close = html_content.rfind("</style>")
    else:
        last_style_close = html_content.rfind("</style>", 0, head_end)

    if last_style_close == -1:
        print("  ERROR: Cannot find </style> to inject CSS")
        return None

    html_content = html_content[:last_style_close] + css_snippet + "\n        " + html_content[last_style_close:]
    print(f"  CSS injected at position {last_style_close}")

    # --- 2. Inject HTML section ---
    # Find hero close: the </section> after the "Watch Demo" button
    watch_demo_pos = html_content.find("Watch Demo")
    if watch_demo_pos == -1:
        print("  ERROR: Cannot find 'Watch Demo' marker")
        return None
    hero_close = html_content.find("</section>", watch_demo_pos)
    if hero_close == -1:
        print("  ERROR: Cannot find hero </section>")
        return None
    insert_after = hero_close + len("</section>")
    html_content = html_content[:insert_after] + "\n" + html_snippet + html_content[insert_after:]
    print(f"  HTML section injected after hero close at position {insert_after}")

    # --- 3. Inject script ---
    # Find the openVideoModal function's script block, then find its closing </script>
    # and insert pbDemoPlay before it
    open_vm_pos = html_content.find("function openVideoModal()")
    if open_vm_pos == -1:
        print("  WARNING: openVideoModal not found, looking for generic script close")
        script_close = html_content.rfind("</script>")
    else:
        script_close = html_content.find("</script>", open_vm_pos)

    if script_close == -1:
        print("  ERROR: Cannot find </script> for script injection")
        return None

    html_content = html_content[:script_close] + "\n" + script_snippet + "\n        " + html_content[script_close:]
    print(f"  Script injected at position {script_close}")

    return html_content


def deploy_to_page(page_id, page_name):
    print(f"\n{'='*60}")
    print(f"Deploying to: {page_name} (ID: {page_id})")
    print('='*60)

    # Get current elementor data
    print("  Fetching current Elementor data...")
    el_data = get_page_elementor_data(page_id)

    # Find the main HTML widget (first container, first widget)
    html_content = None
    container_idx = None
    widget_idx = None

    for ci, container in enumerate(el_data):
        for wi, widget in enumerate(container.get("elements", [])):
            settings = widget.get("settings", {})
            hc = settings.get("html", "")
            if len(hc) > 50000 and "Watch Demo" in hc:
                html_content = hc
                container_idx = ci
                widget_idx = wi
                print(f"  Found main widget: container[{ci}].elements[{wi}], HTML length: {len(hc)}")
                break
        if html_content:
            break

    if html_content is None:
        print(f"  ERROR: Could not find main HTML widget with 'Watch Demo' content")
        return False

    # Check if already deployed
    if "pb-demo-section" in html_content:
        print(f"  ALREADY DEPLOYED: pb-demo-section found in HTML. Skipping.")
        return True

    # Inject the video section
    print("  Injecting video section...")
    new_html = inject_video_into_html(html_content, VIDEO_SECTION_CSS, VIDEO_SECTION_HTML, VIDEO_SECTION_SCRIPT)

    if new_html is None:
        print("  ERROR: Injection failed")
        return False

    print(f"  New HTML length: {len(new_html)} (was {len(html_content)}, added {len(new_html)-len(html_content)} chars)")

    # Update elementor data
    el_data[container_idx]["elements"][widget_idx]["settings"]["html"] = new_html

    # Deploy
    print("  Updating WordPress page...")
    status = update_page_elementor(page_id, el_data)
    print(f"  Update status: {status}")

    # Clear cache
    print("  Clearing Elementor cache...")
    clear_elementor_cache()
    time.sleep(3)
    touch_page(page_id)
    time.sleep(5)

    # Verify
    print("  Verifying live page...")
    verify_url = f"https://purebrain.ai/wp-json/wp/v2/pages/{page_id}?context=edit"
    verify_resp = requests.get(verify_url, headers=HEADERS)
    verify_data = verify_resp.json()
    verify_ed = verify_data.get("meta", {}).get("_elementor_data", "")
    if "pb-demo-section" in verify_ed:
        print(f"  VERIFIED: pb-demo-section found in stored Elementor data")
        return True
    else:
        print(f"  ERROR: pb-demo-section NOT found in stored data after update")
        return False


def main():
    print("PureBrain Homepage Demo Video Embed Deployment")
    print("BUILD -> SECURITY -> QA -> SHIP pipeline")
    print("")

    pages = [
        (11, "Homepage (purebrain.ai)"),
        (689, "Pay Test 2"),
        (688, "Pay Test Sandbox 2"),
    ]

    results = {}
    for page_id, page_name in pages:
        success = deploy_to_page(page_id, page_name)
        results[page_name] = "PASS" if success else "FAIL"

    print("\n" + "="*60)
    print("DEPLOYMENT SUMMARY")
    print("="*60)
    for page_name, result in results.items():
        print(f"  {result}: {page_name}")

    all_pass = all(v == "PASS" for v in results.values())
    print(f"\nOverall: {'ALL PASSED' if all_pass else 'SOME FAILURES - review above'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
