#!/usr/bin/env python3
"""
Check: Is video-background fixed div covering content on mobile?
"""

import time
import json
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/pay-test-2-mobile-20260308"
PAGE_URL = "https://purebrain.ai/pay-test-2"
PASSWORD = "PureBrain.ai253443$$$"

def run_js(page, script, label=""):
    try:
        result = page.evaluate(script)
        if label:
            print(f"JS [{label}]: {json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result}")
        return result
    except Exception as e:
        print(f"JS ERROR [{label}]: {e}")
        return None

def take_screenshot(page, name, description=""):
    path = f"{SCREENSHOT_DIR}/{name}.png"
    page.screenshot(path=path, full_page=False)
    print(f"SCREENSHOT: {name} - {description}")
    return path

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        mobile_ctx = browser.new_context(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
        )
        page = mobile_ctx.new_page()
        page.goto(PAGE_URL, wait_until="networkidle", timeout=30000)
        time.sleep(2)

        pw_input = page.query_selector('input[id^="pwbox-"]')
        if pw_input:
            pw_input.fill(PASSWORD)
            page.click('input[type="submit"]')
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(3)

        print("=" * 60)
        print("VIDEO-BACKGROUND INVESTIGATION")
        print("=" * 60)

        # Check the video-background in detail
        vb_check = run_js(page, """
            (() => {
                const vb = document.querySelector('.video-background');
                if (!vb) return 'not found';
                const style = getComputedStyle(vb);
                const rect = vb.getBoundingClientRect();

                // Get ALL children of video-background
                const children = Array.from(vb.children).map(c => {
                    const cs = getComputedStyle(c);
                    const cr = c.getBoundingClientRect();
                    return {
                        tag: c.tagName,
                        id: c.id || '',
                        className: (c.className || '').substring(0, 60),
                        height: cr.height,
                        width: cr.width,
                        display: cs.display,
                        visibility: cs.visibility,
                        opacity: cs.opacity,
                        backgroundColor: cs.backgroundColor,
                        background: cs.background.substring(0, 80),
                        position: cs.position,
                        zIndex: cs.zIndex
                    };
                });

                return {
                    tag: vb.tagName,
                    id: vb.id,
                    className: vb.className.substring(0, 80),
                    position: style.position,
                    zIndex: style.zIndex,
                    top: style.top,
                    left: style.left,
                    height: style.height,
                    width: style.width,
                    rectTop: rect.top,
                    rectHeight: rect.height,
                    rectWidth: rect.width,
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity,
                    backgroundColor: style.backgroundColor,
                    background: style.background.substring(0, 100),
                    pointerEvents: style.pointerEvents,
                    children: children
                };
            })()
        """, "video-background element details")

        # The KEY question: is there a canvas or video inside video-background that's covering content?
        canvas_check = run_js(page, """
            (() => {
                const vb = document.querySelector('.video-background');
                if (!vb) return 'not found';

                const canvases = vb.querySelectorAll('canvas, video');
                return Array.from(canvases).map(el => {
                    const style = getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    return {
                        tag: el.tagName,
                        id: el.id || '',
                        className: (el.className || '').substring(0, 40),
                        position: style.position,
                        zIndex: style.zIndex,
                        display: style.display,
                        visibility: style.visibility,
                        opacity: style.opacity,
                        rectTop: rect.top,
                        rectHeight: rect.height,
                        rectWidth: rect.width,
                        backgroundColor: style.backgroundColor
                    };
                });
            })()
        """, "Canvas/video inside video-background")

        # Check what's at the coordinates where timeline-items should be
        # Timeline section is at offsetTop 9929, items are inside it
        # scroll to show timeline, then check what element is at center-screen
        page.evaluate("window.scrollTo(0, 9929 + 200)")  # scroll into timeline section
        time.sleep(0.3)

        elements_at_center = run_js(page, """
            (() => {
                // Check what elements are at the screen center (x=187, y=406)
                const x = 187, y = 406;
                const els = document.elementsFromPoint(x, y);
                return els.slice(0, 10).map(el => {
                    const style = getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    return {
                        tag: el.tagName,
                        id: el.id || '',
                        className: (el.className || '').substring(0, 60),
                        position: style.position,
                        zIndex: style.zIndex,
                        display: style.display,
                        visibility: style.visibility,
                        opacity: style.opacity,
                        backgroundColor: style.backgroundColor,
                        rectHeight: rect.height,
                        top: rect.top,
                        textPreview: el.textContent.trim().substring(0, 40)
                    };
                });
            })()
        """, "Elements at screen center when scrolled into timeline")

        # Now hide the video-background and see what appears
        run_js(page, """
            const vb = document.querySelector('.video-background');
            if (vb) {
                vb.style.display = 'none';
                vb.style.visibility = 'hidden';
                vb.style.opacity = '0';
            }
        """)
        time.sleep(0.3)
        take_screenshot(page, "026-video-bg-hidden-timeline", "Timeline with video-background HIDDEN")

        page.evaluate("window.scrollBy(0, 300)")
        time.sleep(0.2)
        take_screenshot(page, "027-video-bg-hidden-timeline-2", "Further into timeline with video-bg hidden")

        # Scroll to testimonials
        page.evaluate("window.scrollTo(0, 10826)")
        time.sleep(0.3)
        take_screenshot(page, "028-video-bg-hidden-testimonials", "Testimonials with video-background hidden")

        # Check the full z-index stack
        z_index_stack = run_js(page, """
            (() => {
                const allEls = Array.from(document.querySelectorAll('*'));
                const relevant = allEls.filter(el => {
                    const style = getComputedStyle(el);
                    const zIndex = parseInt(style.zIndex) || 0;
                    const position = style.position;
                    return (position === 'fixed' || position === 'absolute' || position === 'sticky') &&
                           style.display !== 'none' && style.visibility !== 'hidden';
                }).map(el => {
                    const style = getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    return {
                        tag: el.tagName,
                        id: el.id || '',
                        className: (el.className || '').substring(0, 50),
                        position: style.position,
                        zIndex: style.zIndex,
                        top: rect.top,
                        height: rect.height,
                        width: rect.width,
                        backgroundColor: style.backgroundColor,
                        opacity: style.opacity
                    };
                });
                // Sort by z-index
                relevant.sort((a, b) => (parseInt(b.zIndex) || 0) - (parseInt(a.zIndex) || 0));
                return relevant.slice(0, 20);
            })()
        """, "Full z-index stack (sorted by zIndex)")

        # Restore video-background and check if it matches what we found
        run_js(page, """
            const vb = document.querySelector('.video-background');
            if (vb) {
                vb.style.display = '';
                vb.style.visibility = '';
                vb.style.opacity = '';
            }
        """)

        # Check canvas specifically
        canvas_render = run_js(page, """
            (() => {
                // Is there a THREE.js canvas in the video-background?
                const vb = document.querySelector('.video-background');
                if (!vb) return 'not found';

                const allEls = Array.from(vb.querySelectorAll('*'));
                return allEls.map(el => {
                    const style = getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    return {
                        tag: el.tagName,
                        id: el.id,
                        className: (el.className || '').substring(0, 40),
                        position: style.position,
                        zIndex: style.zIndex,
                        height: rect.height,
                        width: rect.width,
                        display: style.display,
                        opacity: style.opacity,
                        backgroundColor: style.backgroundColor
                    };
                });
            })()
        """, "All elements inside video-background")

        browser.close()
        print("\n" + "=" * 60)
        print("VIDEO-BACKGROUND INVESTIGATION COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    main()
