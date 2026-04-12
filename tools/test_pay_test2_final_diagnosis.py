#!/usr/bin/env python3
"""
Final diagnosis: What EXACTLY is invisible after WHAT HAPPENS NEXT on pay-test-2 mobile
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
        print("FINAL DIAGNOSIS")
        print("=" * 60)

        # Find WHAT HAPPENS NEXT section precisely and check what comes DIRECTLY after it
        whn_diagnosis = run_js(page, """
            (() => {
                // Find the actual h2 with WHAT HAPPENS NEXT
                const h2s = document.querySelectorAll('h2');
                let whnH2 = null;
                for (const h2 of h2s) {
                    if (h2.textContent.trim().toLowerCase().includes('what happens next')) {
                        whnH2 = h2;
                        break;
                    }
                }
                if (!whnH2) return {error: 'h2 not found'};

                // Walk up to containing section
                let section = whnH2.parentElement;
                while (section && section.tagName !== 'SECTION' && section.tagName !== 'BODY') {
                    section = section.parentElement;
                }

                // Get the next siblings after this section
                const nextElements = [];
                let next = section ? section.nextElementSibling : null;
                let count = 0;
                while (next && count < 5) {
                    const style = getComputedStyle(next);
                    const rect = next.getBoundingClientRect();
                    nextElements.push({
                        tag: next.tagName,
                        id: next.id || '',
                        className: (next.className || '').substring(0, 80),
                        rectHeight: rect.height,
                        offsetHeight: next.offsetHeight,
                        scrollHeight: next.scrollHeight,
                        display: style.display,
                        visibility: style.visibility,
                        overflow: style.overflow,
                        maxHeight: style.maxHeight,
                        height: style.height,
                        opacity: style.opacity,
                        // Check its first child
                        firstChildHeight: next.firstElementChild ?
                            next.firstElementChild.getBoundingClientRect().height : null,
                        textPreview: next.textContent.trim().substring(0, 50)
                    });
                    next = next.nextElementSibling;
                    count++;
                }

                // Also get the WHN section info
                const whnRect = section ? section.getBoundingClientRect() : null;
                const whnStyle = section ? getComputedStyle(section) : null;

                return {
                    whnSectionInfo: section ? {
                        tag: section.tagName,
                        id: section.id || '',
                        className: (section.className || '').substring(0, 80),
                        rectHeight: whnRect.height,
                        display: whnStyle.display,
                        visibility: whnStyle.visibility,
                        overflow: whnStyle.overflow,
                        maxHeight: whnStyle.maxHeight,
                        height: whnStyle.height
                    } : null,
                    nextSiblings: nextElements
                };
            })()
        """, "WHN section and next siblings")

        print("\n--- Check timeline section specifically ---")

        timeline_check = run_js(page, """
            (() => {
                const timeline = document.querySelector('.timeline-section');
                if (!timeline) return {error: 'timeline-section not found'};

                const style = getComputedStyle(timeline);
                const rect = timeline.getBoundingClientRect();

                // Check ALL children of timeline
                const children = Array.from(timeline.querySelectorAll('*')).slice(0, 10);
                const childrenInfo = children.map(el => ({
                    tag: el.tagName,
                    className: (el.className || '').substring(0, 40),
                    height: el.getBoundingClientRect().height,
                    display: getComputedStyle(el).display,
                    visibility: getComputedStyle(el).visibility
                }));

                return {
                    display: style.display,
                    visibility: style.visibility,
                    overflow: style.overflow,
                    maxHeight: style.maxHeight,
                    height: style.height,
                    rectHeight: rect.height,
                    offsetHeight: timeline.offsetHeight,
                    scrollHeight: timeline.scrollHeight,
                    children: childrenInfo
                };
            })()
        """, "Timeline section deep check")

        print("\n--- Check what's INSIDE the timeline section ---")

        # Let's check if the timeline section items have visible text
        timeline_text = run_js(page, """
            (() => {
                const timeline = document.querySelector('.timeline-section');
                if (!timeline) return 'not found';

                const allText = [];
                const textEls = timeline.querySelectorAll('h2, h3, h4, p, li, span');
                textEls.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    const style = getComputedStyle(el);
                    if (el.textContent.trim().length > 0) {
                        allText.push({
                            tag: el.tagName,
                            text: el.textContent.trim().substring(0, 40),
                            height: rect.height,
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity
                        });
                    }
                });
                return allText.slice(0, 10);
            })()
        """, "Timeline text elements")

        print("\n--- Check WHN container for its own content ---")

        whn_content = run_js(page, """
            (() => {
                const h2s = document.querySelectorAll('h2');
                let whnH2 = null;
                for (const h2 of h2s) {
                    if (h2.textContent.trim().toLowerCase().includes('what happens next')) {
                        whnH2 = h2;
                        break;
                    }
                }
                if (!whnH2) return {error: 'not found'};

                // Find the container section
                let section = whnH2.parentElement;
                while (section && section.tagName !== 'SECTION' && section.tagName !== 'BODY') {
                    section = section.parentElement;
                }

                // Get all text within the WHN section
                const allText = [];
                if (section) {
                    section.querySelectorAll('h1,h2,h3,h4,p,li,button').forEach(el => {
                        const rect = el.getBoundingClientRect();
                        const style = getComputedStyle(el);
                        if (el.textContent.trim()) {
                            allText.push({
                                tag: el.tagName,
                                text: el.textContent.trim().substring(0, 50),
                                height: rect.height,
                                display: style.display,
                                visibility: style.visibility
                            });
                        }
                    });
                }

                return {
                    sectionTag: section ? section.tagName : 'none',
                    sectionId: section ? section.id : 'none',
                    sectionClass: section ? section.className.substring(0, 60) : 'none',
                    sectionHeight: section ? section.getBoundingClientRect().height : 0,
                    contentElements: allText
                };
            })()
        """, "WHN section content")

        print("\n--- Scroll to WHN and capture each viewport ---")

        # Scroll to WHN
        run_js(page, """
            const h2s = document.querySelectorAll('h2');
            for (const h2 of h2s) {
                if (h2.textContent.trim().toLowerCase().includes('what happens next')) {
                    h2.scrollIntoView({behavior:'instant', block:'start'});
                    break;
                }
            }
        """)
        time.sleep(0.5)
        take_screenshot(page, "018-whn-top", "WHN scrolled to top of viewport")

        # Scroll through the WHN section content
        for i in range(1, 6):
            page.evaluate(f"window.scrollBy(0, 400)")
            time.sleep(0.3)
            take_screenshot(page, f"019-whn-content-{i}", f"WHN content scroll {i*400}px after WHN")

        print("\n--- Check if timeline/testimonials are INSIDE the value-section ---")

        section_map = run_js(page, """
            (() => {
                const sections = document.querySelectorAll('section');
                return Array.from(sections).map(sec => {
                    const rect = sec.getBoundingClientRect();
                    const style = getComputedStyle(sec);
                    // Get first heading inside
                    const firstHeading = sec.querySelector('h1,h2,h3,h4');
                    return {
                        id: sec.id || '',
                        className: (sec.className || '').substring(0, 60),
                        rectHeight: rect.height,
                        display: style.display,
                        visibility: style.visibility,
                        overflow: style.overflow,
                        firstHeading: firstHeading ? firstHeading.textContent.trim().substring(0, 40) : 'none'
                    };
                });
            })()
        """, "All sections map")

        print("\n--- Inspect value-section specifically (id=value) ---")

        value_section = run_js(page, """
            (() => {
                const vs = document.querySelector('#value');
                if (!vs) return {error: '#value not found'};
                const style = getComputedStyle(vs);
                const rect = vs.getBoundingClientRect();
                // Get direct children
                const children = Array.from(vs.children).map(c => {
                    const cs = getComputedStyle(c);
                    const cr = c.getBoundingClientRect();
                    return {
                        tag: c.tagName,
                        className: (c.className || '').substring(0, 40),
                        height: cr.height,
                        display: cs.display,
                        overflow: cs.overflow,
                        maxHeight: cs.maxHeight
                    };
                });
                return {
                    rectHeight: rect.height,
                    display: style.display,
                    overflow: style.overflow,
                    maxHeight: style.maxHeight,
                    children: children
                };
            })()
        """, "#value section")

        # Now THE KEY: scroll to where timeline should be and what we actually see
        page.evaluate("window.scrollTo(0, 9929)")  # offsetTop of timeline
        time.sleep(0.5)
        take_screenshot(page, "020-at-timeline-position", "At timeline section offsetTop position")

        page.evaluate("window.scrollTo(0, 10826)")  # offsetTop of testimonials
        time.sleep(0.5)
        take_screenshot(page, "021-at-testimonials-position", "At testimonials section offsetTop")

        # Check the WHN section's FULL content - the "value-section" which has id="value"
        print("\n--- Is WHAT HAPPENS NEXT inside value-section? ---")

        whn_location = run_js(page, """
            (() => {
                const h2s = document.querySelectorAll('h2');
                let whnH2 = null;
                for (const h2 of h2s) {
                    if (h2.textContent.trim().toLowerCase().includes('what happens next')) {
                        whnH2 = h2;
                        break;
                    }
                }
                if (!whnH2) return 'not found';

                // Walk up to find all ancestor IDs and classes
                const ancestors = [];
                let el = whnH2.parentElement;
                let depth = 0;
                while (el && el !== document.body && depth < 10) {
                    const style = getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    ancestors.push({
                        depth: depth,
                        tag: el.tagName,
                        id: el.id || '',
                        className: (el.className || '').substring(0, 60),
                        rectHeight: rect.height,
                        display: style.display,
                        overflow: style.overflow,
                        maxHeight: style.maxHeight,
                        position: style.position,
                        height: style.height
                    });
                    el = el.parentElement;
                    depth++;
                }
                return ancestors;
            })()
        """, "WHN ancestor chain (full)")

        browser.close()

        print("\n" + "=" * 60)
        print("FINAL DIAGNOSIS COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    main()
