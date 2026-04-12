#!/usr/bin/env python3
"""
Check timeline section items - DOM says visible but screenshots show empty
Is this a visual rendering issue (dark text on dark bg) or actual invisibility?
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
        print("TIMELINE VISUAL CHECK")
        print("=" * 60)

        # Get exact colors of timeline items
        timeline_colors = run_js(page, """
            (() => {
                const timeline = document.querySelector('.timeline-section');
                if (!timeline) return 'not found';

                // Get ALL text elements with their colors
                const items = [];
                timeline.querySelectorAll('.timeline-item, .timeline-item__time, .timeline-item__text').forEach(el => {
                    const style = getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    items.push({
                        className: el.className,
                        text: el.textContent.trim().substring(0, 30),
                        height: rect.height,
                        color: style.color,
                        backgroundColor: style.backgroundColor,
                        opacity: style.opacity,
                        visibility: style.visibility
                    });
                });
                return items;
            })()
        """, "Timeline item colors")

        # Check the timeline items with their full styling
        full_timeline = run_js(page, """
            (() => {
                const timeline = document.querySelector('.timeline-section');
                const grid = document.querySelector('.timeline-grid');
                if (!timeline || !grid) return {error: 'not found', timeline: !!timeline, grid: !!grid};

                const gridStyle = getComputedStyle(grid);
                const gridRect = grid.getBoundingClientRect();

                // Get timeline items
                const items = Array.from(document.querySelectorAll('.timeline-item'));
                return {
                    gridHeight: gridRect.height,
                    gridDisplay: gridStyle.display,
                    gridVisibility: gridStyle.visibility,
                    gridOpacity: gridStyle.opacity,
                    gridOverflow: gridStyle.overflow,
                    gridColor: gridStyle.color,
                    itemCount: items.length,
                    sampleItem: items.length > 0 ? {
                        height: items[0].getBoundingClientRect().height,
                        color: getComputedStyle(items[0]).color,
                        bg: getComputedStyle(items[0]).background,
                        opacity: getComputedStyle(items[0]).opacity,
                        visibility: getComputedStyle(items[0]).visibility,
                        text: items[0].textContent.trim().substring(0, 60)
                    } : null
                };
            })()
        """, "Full timeline grid check")

        # Get the ACTUAL computed color of timeline text
        timeline_visibility = run_js(page, """
            (() => {
                // Check if timeline items have their text color set to transparent or matching background
                const h2 = document.querySelector('.timeline-section h2');
                const timeItems = document.querySelectorAll('.timeline-item__time');
                const textItems = document.querySelectorAll('.timeline-item__text');

                const getColorInfo = (el) => {
                    if (!el) return null;
                    const style = getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    return {
                        tag: el.tagName,
                        text: el.textContent.trim().substring(0, 30),
                        color: style.color,
                        background: style.background.substring(0, 60),
                        backgroundColor: style.backgroundColor,
                        opacity: style.opacity,
                        visibility: style.visibility,
                        height: rect.height,
                        width: rect.width
                    };
                };

                return {
                    h2: getColorInfo(h2),
                    timeItems: Array.from(timeItems).map(getColorInfo),
                    textItems: Array.from(textItems).map(getColorInfo)
                };
            })()
        """, "Timeline color visibility")

        # Inject a bright red highlight to see if items are there but not colored
        run_js(page, """
            // Inject a bright style override to make timeline items VERY visible
            const style = document.createElement('style');
            style.id = 'debug-highlight';
            style.textContent = `
                .timeline-section .timeline-item {
                    background: rgba(255, 0, 0, 0.3) !important;
                    border: 2px solid red !important;
                }
                .timeline-section .timeline-item__time,
                .timeline-section .timeline-item__text,
                .timeline-section h2 {
                    color: white !important;
                    text-shadow: 0 0 4px red !important;
                }
                .testimonials-section .testimonial-card,
                .testimonials-section .testimonial-content {
                    background: rgba(0, 255, 0, 0.3) !important;
                    border: 2px solid lime !important;
                    color: white !important;
                }
            `;
            document.head.appendChild(style);
        """)

        # Scroll to timeline
        page.evaluate("window.scrollTo(0, 9929)")
        time.sleep(0.5)
        take_screenshot(page, "022-timeline-with-debug-highlight", "Timeline section with RED debug highlight")

        # Scroll into it
        page.evaluate("window.scrollBy(0, 300)")
        time.sleep(0.3)
        take_screenshot(page, "023-timeline-inside-debug", "Inside timeline with debug highlight")

        # Scroll to testimonials
        page.evaluate("window.scrollTo(0, 10826)")
        time.sleep(0.5)
        take_screenshot(page, "024-testimonials-debug-highlight", "Testimonials with GREEN debug highlight")

        page.evaluate("window.scrollBy(0, 400)")
        time.sleep(0.3)
        take_screenshot(page, "025-testimonials-inside-debug", "Inside testimonials debug")

        # Also check: is there a clip-path on the hero that's covering things?
        hero_clip = run_js(page, """
            (() => {
                const hero = document.querySelector('.hero');
                if (!hero) return 'not found';
                const style = getComputedStyle(hero);
                return {
                    position: style.position,
                    zIndex: style.zIndex,
                    overflow: style.overflow,
                    clipPath: style.clipPath,
                    height: hero.getBoundingClientRect().height,
                    inlineStyle: hero.style.cssText.substring(0, 200)
                };
            })()
        """, "Hero section - checking for overflow/clip issues")

        # Check if there's a fixed overlay covering content
        fixed_elements = run_js(page, """
            (() => {
                const fixedEls = [];
                document.querySelectorAll('*').forEach(el => {
                    const style = getComputedStyle(el);
                    if (style.position === 'fixed' && style.display !== 'none' && style.visibility !== 'hidden') {
                        const rect = el.getBoundingClientRect();
                        if (rect.height > 50 && rect.width > 50) {
                            fixedEls.push({
                                tag: el.tagName,
                                className: (el.className || '').substring(0, 60),
                                id: el.id || '',
                                zIndex: style.zIndex,
                                top: rect.top,
                                height: rect.height,
                                width: rect.width,
                                backgroundColor: style.backgroundColor,
                                opacity: style.opacity
                            });
                        }
                    }
                });
                return fixedEls;
            })()
        """, "Fixed positioned elements (potential overlay)")

        # Get the nav header info
        nav_check = run_js(page, """
            (() => {
                const nav = document.querySelector('nav, .navbar, header, .site-header, #masthead');
                if (!nav) return 'no nav found';
                const style = getComputedStyle(nav);
                const rect = nav.getBoundingClientRect();
                return {
                    tag: nav.tagName,
                    className: nav.className.substring(0, 60),
                    position: style.position,
                    height: rect.height,
                    zIndex: style.zIndex,
                    backgroundColor: style.backgroundColor
                };
            })()
        """, "Navigation header")

        browser.close()

        print("\n" + "=" * 60)
        print("TIMELINE VISUAL CHECK COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    main()
