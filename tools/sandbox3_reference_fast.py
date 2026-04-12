#!/usr/bin/env python3
"""
Fast targeted Sandbox 3 reference screenshot captures.
Gets: demo video section, brain bg video, footer, and key close-ups.
"""

import asyncio
import os
import json

OUTPUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-reference-20260304"
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-3/"
PASSWORD = "PureBrain.ai253443$$$"

async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()

        # Capture console errors
        errors = []
        page.on('console', lambda m: errors.append({'type': m.type, 'text': m.text}) if m.type in ('error','warning') else None)

        print("Navigating...")
        await page.goto(PAGE_URL, wait_until='domcontentloaded', timeout=45000)
        await asyncio.sleep(2)

        # Enter password
        pwd = await page.query_selector('input[type="password"]')
        if pwd:
            await pwd.fill(PASSWORD)
            submit = await page.query_selector('input[type="submit"]')
            if submit:
                await submit.click()
            else:
                await pwd.press('Enter')
            await asyncio.sleep(5)
            await page.wait_for_load_state('domcontentloaded', timeout=20000)
            await asyncio.sleep(3)
            print("Password submitted, page unlocked")

        # =========================================
        # 1. Hero / Brain video background area
        # =========================================
        print("Capturing hero with bg video...")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1.5)
        await page.screenshot(path=f"{OUTPUT_DIR}/A1-hero-brain-bg-desktop.png", full_page=False)

        # Check if bgVideo is playing
        bg_state = await page.evaluate("""(function(){
            var v = document.getElementById('bgVideo');
            if(!v) return null;
            return {
                src: v.currentSrc || v.src,
                sources: Array.from(v.querySelectorAll('source')).map(s => ({src: s.src, type: s.type})),
                autoplay: v.autoplay,
                loop: v.loop,
                muted: v.muted,
                readyState: v.readyState,
                paused: v.paused,
                width: v.videoWidth,
                height: v.videoHeight,
                parentClass: v.parentElement ? v.parentElement.className : '',
                containerStyle: v.parentElement ? window.getComputedStyle(v.parentElement).position + '/' + window.getComputedStyle(v.parentElement).zIndex : '',
                error: v.error ? v.error.code : null
            };
        })()""")
        print(f"bgVideo state: {json.dumps(bg_state, indent=2)}")

        # =========================================
        # 2. About section (first section after hero)
        # =========================================
        print("Capturing about section...")
        await page.evaluate("window.scrollTo(0, 900)")
        await asyncio.sleep(1.5)
        await page.screenshot(path=f"{OUTPUT_DIR}/A2-about-section.png", full_page=False)

        # =========================================
        # 3. Demo video section (y=2162 from data)
        # =========================================
        print("Capturing demo video section...")
        await page.evaluate("window.scrollTo(0, 2062)")
        await asyncio.sleep(2)
        await page.screenshot(path=f"{OUTPUT_DIR}/A3-demo-video-top.png", full_page=False)

        await page.evaluate("window.scrollTo(0, 2400)")
        await asyncio.sleep(1.5)
        await page.screenshot(path=f"{OUTPUT_DIR}/A4-demo-video-mid.png", full_page=False)

        await page.evaluate("window.scrollTo(0, 2800)")
        await asyncio.sleep(1.5)
        await page.screenshot(path=f"{OUTPUT_DIR}/A5-demo-video-bottom.png", full_page=False)

        # Get demo section video state
        demo_state = await page.evaluate("""(function(){
            // demoVideo (modal player)
            var dm = document.getElementById('demoVideo');
            // pbDemoVideo (embedded in section)
            var pb = document.getElementById('pbDemoVideo');
            // videoModal div
            var modal = document.getElementById('videoModal');
            // pb-demo-section
            var section = document.getElementById('pb-demo-section');

            return {
                demoVideoModal: {
                    exists: !!dm,
                    src: dm ? dm.currentSrc : null,
                    sources: dm ? Array.from(dm.querySelectorAll('source')).map(s=>({src:s.src,type:s.type})) : [],
                    readyState: dm ? dm.readyState : null
                },
                pbDemoVideo: {
                    exists: !!pb,
                    src: pb ? pb.currentSrc : null,
                    sources: pb ? Array.from(pb.querySelectorAll('source')).map(s=>({src:s.src,type:s.type})) : [],
                    readyState: pb ? pb.readyState : null,
                    width: pb ? pb.offsetWidth : null,
                    height: pb ? pb.offsetHeight : null
                },
                videoModal: {
                    exists: !!modal,
                    display: modal ? window.getComputedStyle(modal).display : null
                },
                demoSection: {
                    exists: !!section,
                    y: section ? Math.round(section.offsetTop) : null,
                    height: section ? section.offsetHeight : null,
                    bgImage: section ? window.getComputedStyle(section).backgroundImage.substring(0,200) : null,
                    innerHTML_preview: section ? section.innerHTML.substring(0,1000) : null
                }
            };
        })()""")

        with open(f"{OUTPUT_DIR}/demo-video-state.json", 'w') as f:
            json.dump(demo_state, f, indent=2)
        print(f"Demo section y={demo_state['demoSection'].get('y')} h={demo_state['demoSection'].get('height')}")
        print(f"pbDemoVideo: {demo_state['pbDemoVideo']}")

        # Try to capture the embedded demo video element close-up
        pb_demo = await page.query_selector('#pbDemoVideo')
        if pb_demo:
            await pb_demo.scroll_into_view_if_needed()
            await asyncio.sleep(1)
            parent = await page.query_selector('.pb-demo-section__video-wrapper, .pb-demo-section__player, [class*="pb-demo"]')
            if parent:
                await parent.screenshot(path=f"{OUTPUT_DIR}/A6-pb-demo-video-element.png")
                print("Captured pbDemoVideo element screenshot")
            else:
                # Screenshot the video element area
                box = await pb_demo.bounding_box()
                if box:
                    await page.screenshot(
                        path=f"{OUTPUT_DIR}/A6-pb-demo-video-element.png",
                        clip={"x": max(0, box['x']-50), "y": max(0, box['y']-50),
                              "width": box['width']+100, "height": box['height']+100}
                    )
                    print(f"Captured pbDemoVideo bounding box: {box}")

        # =========================================
        # 4. Scroll through rest of page
        # =========================================
        print("Capturing remaining page sections...")
        for y in [3500, 4500, 5500, 6500, 7500, 8500]:
            await page.evaluate(f"window.scrollTo(0, {y})")
            await asyncio.sleep(1)
            await page.screenshot(path=f"{OUTPUT_DIR}/A7-scroll-{y}.png", full_page=False)

        # =========================================
        # 5. Footer area
        # =========================================
        print("Capturing footer...")
        footer = await page.query_selector('footer, .site-footer, #footer, [class*="footer"]')
        if footer:
            await footer.scroll_into_view_if_needed()
            await asyncio.sleep(1.5)
            await footer.screenshot(path=f"{OUTPUT_DIR}/A8-footer-element.png")
            print("Captured footer element screenshot")
        else:
            # Try page bottom
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)
            await page.screenshot(path=f"{OUTPUT_DIR}/A8-page-bottom.png", full_page=False)
            print("Captured page bottom (no footer found)")

        # Footer info
        footer_info = await page.evaluate("""(function(){
            var els = document.querySelectorAll('footer, .site-footer, #footer, [class*="footer-"], .plugin-footer, [class*="pb-footer"]');
            var results = [];
            els.forEach(function(el){
                results.push({
                    tag: el.tagName,
                    id: el.id,
                    class: el.className ? el.className.toString().substring(0,200) : '',
                    y: Math.round(el.offsetTop),
                    height: el.offsetHeight,
                    innerHTML: el.innerHTML.substring(0,500)
                });
            });
            return results;
        })()""")
        with open(f"{OUTPUT_DIR}/footer-detail.json", 'w') as f:
            json.dump(footer_info, f, indent=2)

        # =========================================
        # 6. Logo area
        # =========================================
        print("Capturing logo/header...")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        logo_info = await page.evaluate("""(function(){
            var logos = [];
            document.querySelectorAll('img[src*="logo"], img[alt*="logo"], img[alt*="Logo"], .site-logo img, header img, nav img, [class*="logo"] img').forEach(function(el){
                logos.push({
                    src: el.src,
                    alt: el.alt,
                    class: el.className,
                    parentClass: el.parentElement ? el.parentElement.className.toString().substring(0,100) : '',
                    y: Math.round(el.offsetTop),
                    width: el.offsetWidth,
                    height: el.offsetHeight
                });
            });

            // Also check nav
            var navLinks = [];
            document.querySelectorAll('nav a, .nav-link, .menu-item a').forEach(function(el, i){
                if(i < 20) navLinks.push({text: el.textContent.trim(), href: el.href});
            });

            return {logos: logos, navLinks: navLinks};
        })()""")
        with open(f"{OUTPUT_DIR}/logo-nav-info.json", 'w') as f:
            json.dump(logo_info, f, indent=2)
        print(f"Logos found: {len(logo_info['logos'])}")

        # Nav/header screenshot
        nav = await page.query_selector('nav, header, .site-header, .navbar')
        if nav:
            box = await nav.bounding_box()
            if box:
                await page.screenshot(
                    path=f"{OUTPUT_DIR}/A9-nav-header.png",
                    clip={"x": 0, "y": 0, "width": 1440, "height": min(200, box['height']+50)}
                )

        # =========================================
        # 7. Full page screenshot
        # =========================================
        print("Capturing full page...")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        await page.screenshot(path=f"{OUTPUT_DIR}/A10-full-page.png", full_page=True)
        print("Full page captured")

        # =========================================
        # 8. CSS analysis for key elements
        # =========================================
        css_analysis = await page.evaluate("""(function(){
            var results = {};

            // Body and html bg
            results.body = {
                bg: window.getComputedStyle(document.body).backgroundColor,
                bgImage: window.getComputedStyle(document.body).backgroundImage
            };

            // Hero section
            var hero = document.getElementById('hero');
            if(hero){
                results.hero = {
                    bg: window.getComputedStyle(hero).backgroundColor,
                    bgImage: window.getComputedStyle(hero).backgroundImage,
                    position: window.getComputedStyle(hero).position,
                    overflow: window.getComputedStyle(hero).overflow
                };
            }

            // Video background container
            var videoBg = document.querySelector('.video-background');
            if(videoBg){
                results.videoBgContainer = {
                    position: window.getComputedStyle(videoBg).position,
                    zIndex: window.getComputedStyle(videoBg).zIndex,
                    width: videoBg.offsetWidth,
                    height: videoBg.offsetHeight,
                    top: window.getComputedStyle(videoBg).top,
                    left: window.getComputedStyle(videoBg).left
                };
            }

            // Video overlay
            var overlay = document.getElementById('videoOverlay');
            if(overlay){
                results.videoOverlay = {
                    bg: window.getComputedStyle(overlay).backgroundColor,
                    opacity: window.getComputedStyle(overlay).opacity,
                    position: window.getComputedStyle(overlay).position,
                    zIndex: window.getComputedStyle(overlay).zIndex
                };
            }

            // Demo section
            var demoSection = document.getElementById('pb-demo-section');
            if(demoSection){
                results.pbDemoSection = {
                    bg: window.getComputedStyle(demoSection).backgroundColor,
                    bgImage: window.getComputedStyle(demoSection).backgroundImage.substring(0,200),
                    padding: window.getComputedStyle(demoSection).padding,
                    innerHTML_start: demoSection.innerHTML.substring(0,2000)
                };
            }

            // PbDemoVideo details
            var pbvid = document.getElementById('pbDemoVideo');
            if(pbvid){
                var p = pbvid.parentElement;
                results.pbDemoVideoParent = {
                    tag: p ? p.tagName : null,
                    id: p ? p.id : null,
                    class: p ? p.className.substring(0,200) : null,
                    position: p ? window.getComputedStyle(p).position : null,
                    width: p ? p.offsetWidth : null,
                    height: p ? p.offsetHeight : null
                };
            }

            // Plugin footer
            var pluginFooter = document.querySelector('.purebrain-plugin-footer, .pb-plugin-footer, [class*="purebrain"][class*="footer"]');
            if(pluginFooter){
                results.pluginFooter = {
                    innerHTML: pluginFooter.innerHTML.substring(0,500),
                    class: pluginFooter.className.substring(0,100)
                };
            }

            return results;
        })()""")

        with open(f"{OUTPUT_DIR}/css-analysis.json", 'w') as f:
            json.dump(css_analysis, f, indent=2)
        print("CSS analysis saved")

        # Console errors
        with open(f"{OUTPUT_DIR}/console-errors.json", 'w') as f:
            json.dump(errors[:50], f, indent=2)
        print(f"Console errors/warnings: {len(errors)}")

        await browser.close()

        # Summary
        screenshots = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.png')]
        data_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')]
        print(f"\nDONE: {len(screenshots)} screenshots, {len(data_files)} data files")
        print(f"Output: {OUTPUT_DIR}")

        return {
            "screenshots": sorted(screenshots),
            "data_files": sorted(data_files),
            "bg_video_src": bg_state.get('sources', []) if bg_state else [],
            "demo_video": demo_state
        }

if __name__ == "__main__":
    result = asyncio.run(main())
    print(json.dumps({
        "screenshots_count": len(result["screenshots"]),
        "data_files": result["data_files"]
    }, indent=2))
