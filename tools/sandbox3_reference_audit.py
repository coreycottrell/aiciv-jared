#!/usr/bin/env python3
"""
Sandbox 3 Reference Audit
Captures visual reference screenshots of:
1. Video section (demo video)
2. Brain video background (cosmic/space)
3. Footer/logo area
4. Overall page layout and backgrounds

Saves to: /home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-reference-20260304/
"""

import asyncio
import os
import json
import time
from playwright.async_api import async_playwright

OUTPUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-reference-20260304"
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-3/"
PASSWORD = "PureBrain.ai253443$$$"
TG_CONFIG = "/home/jared/projects/AI-CIV/aether/config/telegram_config.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def tg_send(message):
    """Send Telegram update."""
    try:
        with open(TG_CONFIG) as f:
            token = json.load(f)['bot_token']
        import subprocess
        subprocess.run([
            'curl', '-s', f'https://api.telegram.org/bot{token}/sendMessage',
            '-d', 'chat_id=548906264',
            '--data-urlencode', f'text={message}'
        ], capture_output=True)
    except Exception as e:
        print(f"TG send failed: {e}")

def save_info(filename, data):
    """Save JSON info file."""
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {path}")
    return path

async def main():
    print("Starting Sandbox 3 Reference Audit...")
    tg_send("👁️ Sandbox 3 reference audit: launching Playwright, navigating to page...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        # === STEP 1: Navigate and enter password ===
        print("Step 1: Navigating to page...")
        await page.goto(PAGE_URL, wait_until='networkidle', timeout=60000)
        await asyncio.sleep(3)

        # Take initial screenshot (password gate)
        ss_path = os.path.join(OUTPUT_DIR, "00-password-gate.png")
        await page.screenshot(path=ss_path, full_page=False)
        print(f"Screenshot: {ss_path}")

        # Enter password
        pwd_input = await page.query_selector('input[type="password"]')
        if pwd_input:
            await pwd_input.fill(PASSWORD)
            await asyncio.sleep(0.5)
            submit_btn = await page.query_selector('input[type="submit"], button[type="submit"], .post-password-form button')
            if submit_btn:
                await submit_btn.click()
            else:
                await pwd_input.press('Enter')
            print("Password submitted")
            await asyncio.sleep(4)
        else:
            print("No password gate found - page may already be unlocked")

        # Wait for full page load
        await page.wait_for_load_state('networkidle', timeout=30000)
        await asyncio.sleep(3)

        tg_send("👁️ Sandbox 3: Password entered, page unlocked. Capturing full page overview...")

        # === STEP 2: Full page overview screenshots ===
        print("Step 2: Full page overview...")

        # Full page screenshot (tall)
        ss_path = os.path.join(OUTPUT_DIR, "01-full-page-overview.png")
        await page.screenshot(path=ss_path, full_page=True)
        print(f"Full page screenshot: {ss_path}")

        # Viewport screenshot (what user sees first)
        ss_path = os.path.join(OUTPUT_DIR, "02-viewport-top.png")
        await page.screenshot(path=ss_path, full_page=False)
        print(f"Viewport screenshot: {ss_path}")

        # === STEP 3: Get page dimensions and structure ===
        print("Step 3: Analyzing page structure...")
        page_info = await page.evaluate("""(function(){
            var sections = [];
            document.querySelectorAll('.elementor-section, section, [class*="section"]').forEach(function(el, i){
                if(i > 50) return;
                var rect = el.getBoundingClientRect();
                var style = window.getComputedStyle(el);
                sections.push({
                    tag: el.tagName,
                    id: el.id,
                    class: el.className.substring(0, 100),
                    y: Math.round(el.offsetTop),
                    height: Math.round(el.offsetHeight),
                    bgColor: style.backgroundColor,
                    bgImage: style.backgroundImage ? style.backgroundImage.substring(0, 200) : 'none'
                });
            });

            // Get page dimensions
            var body = document.body;
            var html = document.documentElement;
            var height = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);

            return {
                pageHeight: height,
                pageWidth: window.innerWidth,
                sections: sections
            };
        })()""")

        save_info("page-structure.json", page_info)
        print(f"Page height: {page_info['pageHeight']}px, sections found: {len(page_info['sections'])}")

        # === STEP 4: Find and capture video elements ===
        print("Step 4: Finding video elements...")
        video_info = await page.evaluate("""(function(){
            var videos = [];
            document.querySelectorAll('video, iframe[src*="youtube"], iframe[src*="vimeo"], iframe[src*="loom"], iframe[src*="wistia"], [class*="video"]').forEach(function(el){
                var rect = el.getBoundingClientRect();
                var style = window.getComputedStyle(el);
                var info = {
                    tag: el.tagName,
                    id: el.id,
                    class: el.className.substring(0, 200),
                    src: el.src || el.getAttribute('src') || '',
                    dataSrc: el.getAttribute('data-src') || '',
                    type: '',
                    width: el.offsetWidth,
                    height: el.offsetHeight,
                    y: Math.round(el.offsetTop),
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity,
                    position: style.position,
                    zIndex: style.zIndex
                };

                if(el.tagName === 'VIDEO'){
                    // Get video sources
                    var srcs = [];
                    el.querySelectorAll('source').forEach(function(s){
                        srcs.push({src: s.src, type: s.type});
                    });
                    info.sources = srcs;
                    info.videoSrc = el.src;
                    info.autoplay = el.autoplay;
                    info.loop = el.loop;
                    info.muted = el.muted;
                    info.poster = el.poster;
                    info.readyState = el.readyState;
                    info.type = 'VIDEO_ELEMENT';
                } else if(el.tagName === 'IFRAME'){
                    info.type = 'IFRAME_EMBED';
                }

                videos.push(info);
            });
            return videos;
        })()""")

        save_info("video-elements.json", video_info)
        print(f"Found {len(video_info)} video/iframe elements")
        for v in video_info:
            print(f"  - {v['tag']} id={v['id']} class={v['class'][:60]} y={v['y']} src={v.get('src','')[:80]}")

        tg_send(f"👁️ Sandbox 3: Found {len(video_info)} video/iframe elements. Capturing sections...")

        # === STEP 5: Scroll through page and capture key sections ===
        print("Step 5: Capturing page sections...")
        page_height = page_info['pageHeight']

        # Define scroll positions to capture
        scroll_positions = [
            (0, "top-hero"),
            (500, "hero-mid"),
            (1000, "section-1000"),
            (1500, "section-1500"),
            (2000, "section-2000"),
            (2500, "section-2500"),
            (3000, "section-3000"),
            (3500, "section-3500"),
            (4000, "section-4000"),
        ]

        # Add dynamic positions based on page height
        if page_height > 5000:
            for y in range(5000, min(page_height, 12000), 1000):
                scroll_positions.append((y, f"section-{y}"))

        for scroll_y, label in scroll_positions:
            if scroll_y > page_height:
                break
            await page.evaluate(f"window.scrollTo(0, {scroll_y})")
            await asyncio.sleep(1.5)
            ss_path = os.path.join(OUTPUT_DIR, f"03-scroll-{scroll_y:05d}-{label}.png")
            await page.screenshot(path=ss_path, full_page=False)
            print(f"Captured: scroll y={scroll_y} -> {label}")

        # === STEP 6: Find and capture the demo video section specifically ===
        print("Step 6: Targeting demo video section...")

        # Look for video wrapper or demo section
        video_section_info = await page.evaluate("""(function(){
            // Look for common video wrapper patterns
            var selectors = [
                '#pb-demo-video',
                '.pb-demo-video',
                '[id*="video"]',
                '[class*="demo-video"]',
                '[class*="watch-demo"]',
                'iframe',
                'video',
                '.elementor-widget-video',
                '[class*="video-wrapper"]'
            ];

            var results = [];
            for(var s of selectors){
                var els = document.querySelectorAll(s);
                els.forEach(function(el){
                    var rect = el.getBoundingClientRect();
                    results.push({
                        selector: s,
                        tag: el.tagName,
                        id: el.id || '',
                        class: el.className ? el.className.toString().substring(0, 150) : '',
                        y: Math.round(el.offsetTop),
                        height: el.offsetHeight,
                        width: el.offsetWidth,
                        src: el.src || el.getAttribute('src') || '',
                        innerHTML_preview: el.innerHTML ? el.innerHTML.substring(0, 300) : ''
                    });
                });
            }
            return results;
        })()""")

        save_info("video-section-search.json", video_section_info)

        # Find the main demo video and scroll to it
        demo_video_y = None
        for item in video_section_info:
            if item['y'] > 100 and item['height'] > 200:
                demo_video_y = item['y']
                print(f"Found potential video section: {item['tag']} id={item['id']} y={item['y']} h={item['height']}")
                break

        if demo_video_y:
            await page.evaluate(f"window.scrollTo(0, {max(0, demo_video_y - 100)})")
            await asyncio.sleep(2)
            ss_path = os.path.join(OUTPUT_DIR, "04-demo-video-section.png")
            await page.screenshot(path=ss_path, full_page=False)
            print(f"Demo video section screenshot: {ss_path}")

        # === STEP 7: Capture background video (brain/cosmic) ===
        print("Step 7: Capturing background video (brain/cosmic)...")

        bg_video_info = await page.evaluate("""(function(){
            var results = [];
            // Look for background videos (usually position:fixed or position:absolute with z-index)
            document.querySelectorAll('video').forEach(function(el){
                var style = window.getComputedStyle(el);
                results.push({
                    id: el.id,
                    class: el.className ? el.className.toString().substring(0,200) : '',
                    position: style.position,
                    zIndex: style.zIndex,
                    width: el.offsetWidth,
                    height: el.offsetHeight,
                    y: Math.round(el.offsetTop),
                    src: el.src,
                    autoplay: el.autoplay,
                    loop: el.loop,
                    muted: el.muted,
                    readyState: el.readyState,
                    sources: Array.from(el.querySelectorAll('source')).map(s => ({src: s.src, type: s.type})),
                    parentClass: el.parentElement ? el.parentElement.className.toString().substring(0,150) : '',
                    parentId: el.parentElement ? el.parentElement.id : ''
                });
            });
            return results;
        })()""")

        save_info("background-video-info.json", bg_video_info)

        print(f"Found {len(bg_video_info)} video elements:")
        for v in bg_video_info:
            print(f"  - id={v['id']} class={v['class'][:60]} pos={v['position']} z={v['zIndex']} y={v['y']} src={v['src'][:80]}")

        # Scroll to top to capture background video
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(2)

        ss_path = os.path.join(OUTPUT_DIR, "05-top-with-bg-video.png")
        await page.screenshot(path=ss_path, full_page=False)
        print(f"Top with bg video: {ss_path}")

        # === STEP 8: Capture footer/logo area ===
        print("Step 8: Capturing footer/logo area...")

        footer_info = await page.evaluate("""(function(){
            var results = [];
            var selectors = ['footer', '.site-footer', '#footer', '[class*="footer"]', '.elementor-location-footer', '[id*="footer"]'];
            for(var s of selectors){
                var els = document.querySelectorAll(s);
                els.forEach(function(el){
                    results.push({
                        selector: s,
                        tag: el.tagName,
                        id: el.id,
                        class: el.className ? el.className.toString().substring(0,150) : '',
                        y: Math.round(el.offsetTop),
                        height: el.offsetHeight
                    });
                });
            }
            return results;
        })()""")

        save_info("footer-info.json", footer_info)

        if footer_info:
            footer_y = footer_info[0]['y']
            await page.evaluate(f"window.scrollTo(0, {max(0, footer_y - 100)})")
            await asyncio.sleep(2)
            ss_path = os.path.join(OUTPUT_DIR, "06-footer-area.png")
            await page.screenshot(path=ss_path, full_page=False)
            print(f"Footer area: {ss_path}")
        else:
            # Scroll to bottom
            await page.evaluate(f"window.scrollTo(0, {page_height})")
            await asyncio.sleep(2)
            ss_path = os.path.join(OUTPUT_DIR, "06-page-bottom.png")
            await page.screenshot(path=ss_path, full_page=False)
            print(f"Page bottom: {ss_path}")

        # === STEP 9: Capture logo area ===
        print("Step 9: Capturing logo area...")

        logo_info = await page.evaluate("""(function(){
            var results = [];
            var selectors = ['.site-logo', '#site-logo', '[class*="logo"]', 'img[class*="logo"]', '.pb-logo', '[id*="logo"]', 'header .logo', '.elementor-site-logo'];
            for(var s of selectors){
                var els = document.querySelectorAll(s);
                els.forEach(function(el){
                    results.push({
                        selector: s,
                        tag: el.tagName,
                        id: el.id,
                        class: el.className ? el.className.toString().substring(0,100) : '',
                        y: Math.round(el.offsetTop),
                        src: el.src || el.getAttribute('src') || '',
                        alt: el.alt || ''
                    });
                });
            }
            return results;
        })()""")

        save_info("logo-info.json", logo_info)

        # === STEP 10: Full CSS background analysis ===
        print("Step 10: Full CSS background analysis...")

        bg_analysis = await page.evaluate("""(function(){
            // Analyze backgrounds of major sections
            var results = [];
            var allSections = document.querySelectorAll('.elementor-section, .elementor-container, section, [class*="pb-"], [id*="pb-"]');
            allSections.forEach(function(el, i){
                if(i > 100) return;
                var style = window.getComputedStyle(el);
                var bgColor = style.backgroundColor;
                var bgImage = style.backgroundImage;
                var hasInterestingBg = bgColor !== 'rgba(0, 0, 0, 0)' || (bgImage && bgImage !== 'none');

                if(hasInterestingBg){
                    results.push({
                        tag: el.tagName,
                        id: el.id,
                        class: el.className ? el.className.toString().substring(0,150) : '',
                        y: Math.round(el.offsetTop),
                        height: el.offsetHeight,
                        bgColor: bgColor,
                        bgImage: bgImage ? bgImage.substring(0,200) : 'none',
                        position: style.position,
                        zIndex: style.zIndex,
                        overflow: style.overflow
                    });
                }
            });

            // Also check body and html
            var bodyStyle = window.getComputedStyle(document.body);
            var htmlStyle = window.getComputedStyle(document.documentElement);
            results.unshift({
                tag: 'BODY',
                bgColor: bodyStyle.backgroundColor,
                bgImage: bodyStyle.backgroundImage ? bodyStyle.backgroundImage.substring(0,200) : 'none'
            });
            results.unshift({
                tag: 'HTML',
                bgColor: htmlStyle.backgroundColor,
                bgImage: htmlStyle.backgroundImage ? htmlStyle.backgroundImage.substring(0,200) : 'none'
            });

            return results;
        })()""")

        save_info("background-analysis.json", bg_analysis)
        print(f"Found {len(bg_analysis)} elements with non-transparent backgrounds")

        # === STEP 11: Capture specific video section from page HTML ===
        print("Step 11: Capturing video player HTML structure...")

        video_html = await page.evaluate("""(function(){
            // Get the innerHTML around any video or iframe elements
            var results = [];

            // iframes (embedded videos)
            document.querySelectorAll('iframe').forEach(function(el){
                var parent = el.closest('.elementor-widget, [class*="video"], [class*="embed"]') || el.parentElement;
                results.push({
                    type: 'iframe',
                    src: el.src,
                    width: el.width,
                    height: el.height,
                    parentHTML: parent ? parent.outerHTML.substring(0,2000) : el.outerHTML.substring(0,2000),
                    y: Math.round(el.offsetTop)
                });
            });

            // video elements
            document.querySelectorAll('video').forEach(function(el){
                results.push({
                    type: 'video',
                    src: el.src,
                    outerHTML: el.outerHTML.substring(0,2000),
                    y: Math.round(el.offsetTop),
                    readyState: el.readyState,
                    networkState: el.networkState,
                    error: el.error ? el.error.message : null
                });
            });

            return results;
        })()""")

        save_info("video-html-structure.json", video_html)

        # === STEP 12: Check specifically for HLS or R2 video sources ===
        print("Step 12: Checking for HLS/R2 sources...")

        hls_check = await page.evaluate("""(function(){
            var results = {
                hlsVideos: [],
                r2Videos: [],
                allVideoSrcs: []
            };

            document.querySelectorAll('video').forEach(function(v){
                if(v.src) results.allVideoSrcs.push(v.src);
                v.querySelectorAll('source').forEach(function(s){
                    results.allVideoSrcs.push(s.src);
                    if(s.src.includes('.m3u8')) results.hlsVideos.push(s.src);
                    if(s.src.includes('r2.')) results.r2Videos.push(s.src);
                });
                if(v.src && v.src.includes('.m3u8')) results.hlsVideos.push(v.src);
                if(v.src && v.src.includes('r2.')) results.r2Videos.push(v.src);
            });

            // Check for hls.js script
            results.hasHlsScript = !!document.querySelector('script[src*="hls"]');
            results.hasHlsJsLoaded = typeof window.Hls !== 'undefined';

            return results;
        })()""")

        save_info("hls-r2-check.json", hls_check)

        # === STEP 13: Capture at different viewport widths ===
        print("Step 13: Capturing mobile view...")

        # Set mobile viewport
        await page.set_viewport_size({'width': 390, 'height': 844})
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(2)

        ss_path = os.path.join(OUTPUT_DIR, "07-mobile-390-top.png")
        await page.screenshot(path=ss_path, full_page=False)
        print(f"Mobile view: {ss_path}")

        # Full page on mobile
        ss_path = os.path.join(OUTPUT_DIR, "08-mobile-390-full.png")
        await page.screenshot(path=ss_path, full_page=True)
        print(f"Mobile full: {ss_path}")

        # Reset to desktop
        await page.set_viewport_size({'width': 1440, 'height': 900})
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(2)

        # === STEP 14: Check console logs for any errors ===
        print("Step 14: Checking console logs...")
        console_logs = []
        page.on('console', lambda msg: console_logs.append({'type': msg.type, 'text': msg.text}))

        # Trigger page re-evaluation by scrolling
        await page.evaluate("window.scrollTo(0, 1000)")
        await asyncio.sleep(1)
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # === STEP 15: Final summary screenshot ===
        print("Step 15: Final viewport screenshot...")
        ss_path = os.path.join(OUTPUT_DIR, "09-final-viewport.png")
        await page.screenshot(path=ss_path, full_page=False)

        # === STEP 16: Scroll to video section and capture with close-ups ===
        print("Step 16: Targeted close-up captures...")

        # Find all distinct background sections for close-up
        for i, section in enumerate(bg_analysis[:20]):
            if section.get('tag') in ('HTML', 'BODY'):
                continue
            y = section.get('y', 0)
            if y > 0 and section.get('height', 0) > 100:
                await page.evaluate(f"window.scrollTo(0, {max(0, y - 50)})")
                await asyncio.sleep(0.8)
                ss_path = os.path.join(OUTPUT_DIR, f"10-section-{i:02d}-y{y}-closeup.png")
                await page.screenshot(path=ss_path, full_page=False)

                if i >= 15:  # Limit to first 15 interesting sections
                    break

        await browser.close()

        # === FINAL: Count screenshots and summarize ===
        screenshots = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.png')]
        json_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')]

        summary = {
            "status": "COMPLETE",
            "screenshots_captured": len(screenshots),
            "data_files": json_files,
            "output_dir": OUTPUT_DIR,
            "video_elements_found": len(video_info),
            "background_videos_found": len(bg_video_info),
            "page_height": page_info['pageHeight']
        }

        save_info("audit-summary.json", summary)

        print("\n=== AUDIT COMPLETE ===")
        print(f"Screenshots: {len(screenshots)}")
        print(f"Data files: {json_files}")
        print(f"Output dir: {OUTPUT_DIR}")

        tg_msg = f"""👁️ SANDBOX 3 REFERENCE AUDIT COMPLETE

Screenshots: {len(screenshots)} captured
Video elements: {len(video_info)} found
Background videos: {len(bg_video_info)} found
Page height: {page_info['pageHeight']}px
Output: exports/screenshots/sandbox3-reference-20260304/

Data files: {', '.join(json_files)}

Ready for analysis."""

        tg_send(tg_msg)
        return summary

if __name__ == "__main__":
    result = asyncio.run(main())
    print(json.dumps(result, indent=2))
