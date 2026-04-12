#!/usr/bin/env python3
"""
Find the canvas/THREE.js element covering content and diagnose z-index stack
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
        print("CANVAS/THREE.JS OVERLAY INVESTIGATION")
        print("=" * 60)

        # Find ALL canvas elements
        all_canvases = run_js(page, """
            (() => {
                const canvases = document.querySelectorAll('canvas');
                return Array.from(canvases).map(c => {
                    const style = getComputedStyle(c);
                    const rect = c.getBoundingClientRect();
                    const parent = c.parentElement;
                    const parentStyle = parent ? getComputedStyle(parent) : null;
                    return {
                        id: c.id || '',
                        className: (c.className || '').substring(0, 40),
                        position: style.position,
                        zIndex: style.zIndex,
                        top: rect.top,
                        left: rect.left,
                        height: rect.height,
                        width: rect.width,
                        display: style.display,
                        opacity: style.opacity,
                        pointerEvents: style.pointerEvents,
                        parentTag: parent ? parent.tagName : 'none',
                        parentClass: parent ? (parent.className || '').substring(0, 60) : 'none',
                        parentPosition: parentStyle ? parentStyle.position : 'none',
                        parentZIndex: parentStyle ? parentStyle.zIndex : 'none'
                    };
                });
            })()
        """, "All canvas elements on page")

        # Scroll to timeline and check elementsFromPoint more carefully
        page.evaluate("window.scrollTo(0, 9929 + 400)")
        time.sleep(0.5)

        # Sample multiple points in the timeline area
        points_check = run_js(page, """
            (() => {
                // Check 3 points in the viewport: top, middle, bottom
                const points = [
                    {x: 187, y: 150, label: 'top-third'},
                    {x: 187, y: 406, label: 'middle'},
                    {x: 187, y: 600, label: 'bottom-third'},
                ];

                return points.map(pt => {
                    const els = document.elementsFromPoint(pt.x, pt.y);
                    return {
                        point: pt.label,
                        topElements: els.slice(0, 5).map(el => ({
                            tag: el.tagName,
                            id: el.id || '',
                            className: (el.className || '').substring(0, 50),
                            position: getComputedStyle(el).position,
                            zIndex: getComputedStyle(el).zIndex,
                            opacity: getComputedStyle(el).opacity,
                            backgroundColor: getComputedStyle(el).backgroundColor,
                            height: el.getBoundingClientRect().height
                        }))
                    };
                });
            })()
        """, "Elements at multiple points in timeline area")

        # Hide ALL canvases and take screenshot
        run_js(page, """
            document.querySelectorAll('canvas').forEach(c => {
                c.style.display = 'none';
                c.style.visibility = 'hidden';
            });
        """)
        time.sleep(0.3)
        take_screenshot(page, "029-all-canvases-hidden", "Timeline with ALL canvases hidden")

        page.evaluate("window.scrollBy(0, 300)")
        time.sleep(0.2)
        take_screenshot(page, "030-all-canvases-hidden-2", "Further into timeline, all canvases hidden")

        # Also hide video-background
        run_js(page, """
            const vb = document.querySelector('.video-background');
            if (vb) vb.style.display = 'none';
        """)

        page.evaluate("window.scrollTo(0, 9929 + 100)")
        time.sleep(0.3)
        take_screenshot(page, "031-canvas-and-videobg-hidden", "Canvas AND video-bg both hidden")

        page.evaluate("window.scrollBy(0, 400)")
        time.sleep(0.2)
        take_screenshot(page, "032-canvas-and-videobg-hidden-2", "Deeper into timeline, both hidden")

        page.evaluate("window.scrollTo(0, 10826)")
        time.sleep(0.3)
        take_screenshot(page, "033-testimonials-canvas-videobg-hidden", "Testimonials, canvas+videobg hidden")

        page.evaluate("window.scrollBy(0, 400)")
        time.sleep(0.2)
        take_screenshot(page, "034-testimonials-cards-visible", "Testimonial cards area")

        # Restore everything
        run_js(page, """
            document.querySelectorAll('canvas').forEach(c => {
                c.style.display = '';
                c.style.visibility = '';
            });
            const vb = document.querySelector('.video-background');
            if (vb) vb.style.display = '';
        """)

        # Check the timeline-section's own background
        timeline_bg = run_js(page, """
            (() => {
                const timeline = document.querySelector('.timeline-section');
                const testimonials = document.querySelector('.testimonials-section');

                const getInfo = (el) => {
                    if (!el) return null;
                    const style = getComputedStyle(el);
                    return {
                        backgroundColor: style.backgroundColor,
                        background: style.background.substring(0, 100),
                        opacity: style.opacity,
                        zIndex: style.zIndex,
                        position: style.position,
                        isolation: style.isolation
                    };
                };

                return {
                    timeline: getInfo(timeline),
                    testimonials: getInfo(testimonials)
                };
            })()
        """, "Timeline and testimonials background styles")

        # THE FIX TEST: Add a solid background to sections AFTER value-section
        run_js(page, """
            const style = document.createElement('style');
            style.textContent = `
                .timeline-section,
                .testimonials-section,
                #pb-calc-cta {
                    background: #080a12 !important;
                    position: relative !important;
                    z-index: 2 !important;
                }
            `;
            document.head.appendChild(style);
        """)

        page.evaluate("window.scrollTo(0, 9929 + 100)")
        time.sleep(0.3)
        take_screenshot(page, "035-with-bg-fix-timeline", "Timeline with background fix applied")

        page.evaluate("window.scrollBy(0, 300)")
        time.sleep(0.2)
        take_screenshot(page, "036-with-bg-fix-timeline-2", "Timeline 300px deeper with bg fix")

        page.evaluate("window.scrollTo(0, 10826)")
        time.sleep(0.3)
        take_screenshot(page, "037-with-bg-fix-testimonials", "Testimonials with background fix")

        page.evaluate("window.scrollBy(0, 400)")
        time.sleep(0.2)
        take_screenshot(page, "038-with-bg-fix-testimonials-2", "Testimonials cards with background fix")

        browser.close()
        print("\n" + "=" * 60)
        print("CANVAS OVERLAY INVESTIGATION COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    main()
