#!/usr/bin/env python3
"""
Mobile layout bug investigation for purebrain.ai/pay-test-2
Specifically: content below "WHAT HAPPENS NEXT" section invisible on mobile
"""

import time
import json
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/pay-test-2-mobile-20260308"
PAGE_URL = "https://purebrain.ai/pay-test-2"
PASSWORD = "PureBrain.ai253443$$$"

def take_screenshot(page, name, description=""):
    path = f"{SCREENSHOT_DIR}/{name}.png"
    page.screenshot(path=path, full_page=False)
    print(f"SCREENSHOT: {name} - {description}")
    return path

def run_js(page, script, label=""):
    try:
        result = page.evaluate(script)
        if label:
            print(f"JS [{label}]: {json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result}")
        return result
    except Exception as e:
        print(f"JS ERROR [{label}]: {e}")
        return None

def main():
    with sync_playwright() as pw:
        # Use iPhone viewport (375x812)
        browser = pw.chromium.launch(headless=True)

        mobile_ctx = browser.new_context(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            device_scale_factor=2,
        )

        page = mobile_ctx.new_page()

        print("=" * 60)
        print("STEP 1: Navigate to pay-test-2")
        print("=" * 60)

        page.goto(PAGE_URL, wait_until="networkidle", timeout=30000)
        time.sleep(2)
        take_screenshot(page, "001-initial-load", "Initial page load (before password)")

        # Check if password form is present
        pw_input = page.query_selector('input[id^="pwbox-"]')
        if pw_input:
            print("Password form detected - entering password...")
            pw_input.fill(PASSWORD)
            page.click('input[type="submit"]')
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(3)
            take_screenshot(page, "002-after-password", "After password entry")
        else:
            print("No password form - page already unlocked or different state")
            take_screenshot(page, "002-no-password-form", "No password form found")

        print("\n" + "=" * 60)
        print("STEP 2: Scroll through full page - capture at multiple positions")
        print("=" * 60)

        # Get total page height
        page_height = run_js(page, "document.documentElement.scrollHeight", "page height")
        viewport_height = 812
        print(f"Page height: {page_height}px, viewport: {viewport_height}px")

        # Scroll positions to capture
        positions = [0, 400, 800, 1200, 1600, 2000, 2400, 2800, 3200, 3600, 4000]
        if page_height:
            positions.append(page_height - viewport_height)

        for i, pos in enumerate(positions):
            if pos < 0:
                pos = 0
            if page_height and pos > page_height:
                break
            page.evaluate(f"window.scrollTo(0, {pos})")
            time.sleep(0.5)
            take_screenshot(page, f"003-scroll-{i:02d}-y{pos}", f"Scroll position y={pos}")

        # Scroll back to top
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5)

        print("\n" + "=" * 60)
        print("STEP 3: Find 'WHAT HAPPENS NEXT' section")
        print("=" * 60)

        what_happens_next = run_js(page, """
            (() => {
                // Search for the section by text content
                const allElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, div, span');
                let found = null;
                for (const el of allElements) {
                    if (el.textContent && el.textContent.trim().toUpperCase().includes('WHAT HAPPENS NEXT')) {
                        const rect = el.getBoundingClientRect();
                        const style = getComputedStyle(el);
                        found = {
                            tag: el.tagName,
                            className: el.className,
                            id: el.id,
                            text: el.textContent.trim().substring(0, 100),
                            rect: {top: rect.top, bottom: rect.bottom, height: rect.height},
                            display: style.display,
                            visibility: style.visibility,
                            offsetTop: el.offsetTop,
                            dataId: el.getAttribute('data-id')
                        };
                        break;
                    }
                }
                return found || 'NOT FOUND';
            })()
        """, "WHAT HAPPENS NEXT element")

        print("\n" + "=" * 60)
        print("STEP 4: Check all sections for hidden/collapsed elements")
        print("=" * 60)

        hidden_elements = run_js(page, """
            (() => {
                const results = [];
                const els = document.querySelectorAll('section, .elementor-section, .elementor-element, .elementor-widget-container, [data-id]');
                els.forEach(el => {
                    const style = getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    const isHidden = (
                        rect.height === 0 ||
                        style.display === 'none' ||
                        style.visibility === 'hidden' ||
                        style.opacity === '0' ||
                        (style.overflow === 'hidden' && rect.height < 10) ||
                        style.maxHeight === '0px' ||
                        style.maxHeight === '0'
                    );
                    if (isHidden) {
                        results.push({
                            tag: el.tagName,
                            className: (el.className || '').substring(0, 80),
                            id: el.id || '',
                            dataId: el.getAttribute('data-id') || '',
                            display: style.display,
                            visibility: style.visibility,
                            overflow: style.overflow,
                            height: rect.height,
                            maxHeight: style.maxHeight,
                            offsetTop: el.offsetTop
                        });
                    }
                });
                return results;
            })()
        """, "Hidden elements")

        print("\n" + "=" * 60)
        print("STEP 5: Find all sections AFTER 'WHAT HAPPENS NEXT'")
        print("=" * 60)

        sections_after = run_js(page, """
            (() => {
                // Find what-happens-next section
                let whnEl = null;
                let whnOffsetTop = 0;
                const allEls = document.querySelectorAll('*');
                for (const el of allEls) {
                    if (el.children.length === 0 && el.textContent &&
                        el.textContent.trim().toUpperCase().includes('WHAT HAPPENS NEXT')) {
                        whnEl = el;
                        whnOffsetTop = el.offsetTop;
                        break;
                    }
                }

                if (!whnEl) {
                    // Try broader search
                    const allText = document.body.innerHTML;
                    return {error: 'WHAT HAPPENS NEXT not found in DOM', bodyLength: allText.length};
                }

                // Now get all sections/major elements after this point
                const results = {
                    whnSection: {
                        tag: whnEl.tagName,
                        className: (whnEl.className || '').substring(0, 60),
                        offsetTop: whnOffsetTop,
                        rect: (() => {
                            const r = whnEl.getBoundingClientRect();
                            return {top: r.top, bottom: r.bottom};
                        })()
                    },
                    sectionsAfter: []
                };

                // Get all elementor sections/widgets
                const sections = document.querySelectorAll('.elementor-section, .elementor-container, section');
                sections.forEach(sec => {
                    if (sec.offsetTop > whnOffsetTop + 100) {
                        const style = getComputedStyle(sec);
                        const rect = sec.getBoundingClientRect();
                        results.sectionsAfter.push({
                            tag: sec.tagName,
                            className: (sec.className || '').substring(0, 80),
                            id: sec.id || '',
                            dataId: sec.getAttribute('data-id') || '',
                            offsetTop: sec.offsetTop,
                            rectHeight: rect.height,
                            display: style.display,
                            visibility: style.visibility,
                            overflow: style.overflow,
                            maxHeight: style.maxHeight,
                            position: style.position,
                            zIndex: style.zIndex,
                            opacity: style.opacity
                        });
                    }
                });

                return results;
            })()
        """, "Sections after WHAT HAPPENS NEXT")

        print("\n" + "=" * 60)
        print("STEP 6: Check parent containers for overflow issues")
        print("=" * 60)

        overflow_chain = run_js(page, """
            (() => {
                // Find what-happens-next section and walk up the DOM
                let whnEl = null;
                const allEls = document.querySelectorAll('*');
                for (const el of allEls) {
                    if (el.children.length === 0 && el.textContent &&
                        el.textContent.trim().toUpperCase().includes('WHAT HAPPENS NEXT')) {
                        whnEl = el;
                        break;
                    }
                }

                if (!whnEl) return {error: 'element not found'};

                const chain = [];
                let current = whnEl.parentElement;
                while (current && current !== document.body) {
                    const style = getComputedStyle(current);
                    const rect = current.getBoundingClientRect();
                    const hasIssue = (
                        style.overflow === 'hidden' ||
                        style.overflowY === 'hidden' ||
                        style.maxHeight !== 'none' ||
                        style.height === '0px' ||
                        style.maxHeight === '0px'
                    );
                    if (hasIssue || chain.length < 5) {
                        chain.push({
                            tag: current.tagName,
                            className: (current.className || '').substring(0, 60),
                            id: current.id || '',
                            rectHeight: rect.height,
                            height: style.height,
                            maxHeight: style.maxHeight,
                            overflow: style.overflow,
                            overflowY: style.overflowY,
                            position: style.position,
                            hasIssue: hasIssue
                        });
                    }
                    current = current.parentElement;
                }
                return chain;
            })()
        """, "Parent overflow chain from WHAT HAPPENS NEXT")

        print("\n" + "=" * 60)
        print("STEP 7: Check if content exists below WHAT HAPPENS NEXT (scrollHeight)")
        print("=" * 60)

        layout_metrics = run_js(page, """
            (() => {
                const body = document.body;
                const html = document.documentElement;

                // Find all text content and their positions
                const allTextEls = [];
                document.querySelectorAll('h1,h2,h3,h4,p,li,button,a').forEach(el => {
                    const rect = el.getBoundingClientRect();
                    const style = getComputedStyle(el);
                    const scrollY = window.scrollY;
                    allTextEls.push({
                        tag: el.tagName,
                        text: el.textContent.trim().substring(0, 60),
                        absoluteTop: rect.top + scrollY,
                        height: rect.height,
                        display: style.display,
                        visibility: style.visibility,
                        opacity: style.opacity
                    });
                });

                // Sort by position
                allTextEls.sort((a, b) => a.absoluteTop - b.absoluteTop);

                return {
                    bodyScrollHeight: body.scrollHeight,
                    htmlScrollHeight: html.scrollHeight,
                    bodyClientHeight: body.clientHeight,
                    windowScrollY: window.scrollY,
                    viewportHeight: window.innerHeight,
                    elements: allTextEls
                };
            })()
        """, "Full layout metrics")

        # Scroll to bottom to capture what's there
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        time.sleep(1)
        take_screenshot(page, "004-bottom-of-page", "Very bottom of page")

        # Now let's specifically scroll to find WHAT HAPPENS NEXT and capture before/after
        print("\n" + "=" * 60)
        print("STEP 8: Scroll to WHAT HAPPENS NEXT section and capture")
        print("=" * 60)

        run_js(page, """
            (() => {
                const allEls = document.querySelectorAll('*');
                for (const el of allEls) {
                    if (el.children.length === 0 && el.textContent &&
                        el.textContent.trim().toUpperCase().includes('WHAT HAPPENS NEXT')) {
                        el.scrollIntoView({behavior: 'instant', block: 'center'});
                        return true;
                    }
                }
                return false;
            })()
        """, "Scroll to WHAT HAPPENS NEXT")
        time.sleep(1)
        take_screenshot(page, "005-what-happens-next-section", "WHAT HAPPENS NEXT section visible")

        # Scroll one viewport down from there
        page.evaluate("window.scrollBy(0, 812)")
        time.sleep(0.5)
        take_screenshot(page, "006-one-viewport-after-whn", "One viewport below WHAT HAPPENS NEXT")

        page.evaluate("window.scrollBy(0, 812)")
        time.sleep(0.5)
        take_screenshot(page, "007-two-viewports-after-whn", "Two viewports below WHAT HAPPENS NEXT")

        print("\n" + "=" * 60)
        print("STEP 9: Deep DOM inspection - find ALL content and visibility")
        print("=" * 60)

        deep_inspection = run_js(page, """
            (() => {
                // Check for the SPECIFIC issue - content that exists but is invisible
                const results = {
                    totalElements: document.querySelectorAll('*').length,
                    elementorSections: [],
                    hiddenByCSS: [],
                    zeroHeight: []
                };

                // All elementor sections with their visibility state
                document.querySelectorAll('.elementor-section').forEach((sec, i) => {
                    const style = getComputedStyle(sec);
                    const rect = sec.getBoundingClientRect();
                    results.elementorSections.push({
                        index: i,
                        dataId: sec.getAttribute('data-id') || '',
                        offsetTop: sec.offsetTop,
                        rectHeight: rect.height,
                        display: style.display,
                        visibility: style.visibility,
                        overflow: style.overflow,
                        maxHeight: style.maxHeight,
                        opacity: style.opacity,
                        isVisible: style.display !== 'none' && style.visibility !== 'hidden' && rect.height > 0
                    });
                });

                // Elements with display:none anywhere on page
                document.querySelectorAll('*').forEach(el => {
                    const style = getComputedStyle(el);
                    if (style.display === 'none' && el.offsetTop > 500) {
                        results.hiddenByCSS.push({
                            tag: el.tagName,
                            className: (el.className || '').substring(0, 60),
                            id: el.id || '',
                            dataId: el.getAttribute('data-id') || '',
                            offsetTop: el.offsetTop,
                            textSnippet: el.textContent.trim().substring(0, 40)
                        });
                    }
                });

                // Elements with 0 height
                document.querySelectorAll('.elementor-element, section, .elementor-section').forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.height === 0 && el.innerHTML.trim().length > 0) {
                        const style = getComputedStyle(el);
                        results.zeroHeight.push({
                            tag: el.tagName,
                            className: (el.className || '').substring(0, 60),
                            id: el.id || '',
                            dataId: el.getAttribute('data-id') || '',
                            offsetTop: el.offsetTop,
                            innerHTML: el.innerHTML.substring(0, 100),
                            overflow: style.overflow,
                            maxHeight: style.maxHeight,
                            position: style.position
                        });
                    }
                });

                return results;
            })()
        """, "Deep DOM inspection")

        print("\n" + "=" * 60)
        print("STEP 10: Check for mobile-specific CSS rules causing issues")
        print("=" * 60)

        mobile_css_check = run_js(page, """
            (() => {
                // Check if there are any CSS rules hiding content at mobile breakpoints
                const results = {
                    styleSheets: [],
                    mobileRules: []
                };

                // Scan all stylesheets for mobile rules with display:none or overflow:hidden
                Array.from(document.styleSheets).forEach((sheet, sheetIdx) => {
                    try {
                        const rules = Array.from(sheet.cssRules || []);
                        rules.forEach((rule, ruleIdx) => {
                            const ruleText = rule.cssText || '';
                            // Look for media queries that might hide content
                            if (rule.media) {
                                const innerRules = Array.from(rule.cssRules || []);
                                innerRules.forEach(innerRule => {
                                    const innerText = innerRule.cssText || '';
                                    if (innerText.includes('display: none') ||
                                        innerText.includes('overflow: hidden') ||
                                        innerText.includes('max-height: 0') ||
                                        innerText.includes('height: 0') ||
                                        innerText.includes('visibility: hidden')) {
                                        results.mobileRules.push({
                                            media: rule.conditionText,
                                            rule: innerText.substring(0, 200)
                                        });
                                    }
                                });
                            }
                        });
                    } catch(e) {
                        // Cross-origin stylesheet
                    }
                });

                return results;
            })()
        """, "Mobile CSS rules")

        print("\n" + "=" * 60)
        print("STEP 11: Compare with purebrain.ai (working page) on mobile")
        print("=" * 60)

        # Now navigate to the homepage to compare
        print("Navigating to purebrain.ai for comparison...")
        page.goto("https://purebrain.ai", wait_until="networkidle", timeout=20000)
        time.sleep(2)
        take_screenshot(page, "008-purebrain-homepage-top", "PureBrain.ai homepage top (working)")

        homepage_height = run_js(page, "document.documentElement.scrollHeight", "homepage scroll height")
        print(f"Homepage scroll height: {homepage_height}px")

        # Scroll to bottom of homepage
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        time.sleep(1)
        take_screenshot(page, "009-purebrain-homepage-bottom", "PureBrain.ai homepage bottom")

        # Back to pay-test-2
        print("\nNavigating back to pay-test-2...")
        time.sleep(3)  # Avoid WAF rate limiting
        page.goto(PAGE_URL, wait_until="networkidle", timeout=20000)
        time.sleep(2)

        # Check if need password again
        pw_input2 = page.query_selector('input[id^="pwbox-"]')
        if pw_input2:
            print("Password required again...")
            pw_input2.fill(PASSWORD)
            page.click('input[type="submit"]')
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(3)

        take_screenshot(page, "010-pay-test-2-return", "Pay-test-2 return visit")

        print("\n" + "=" * 60)
        print("STEP 12: Final targeted check - what's AT the WHAT HAPPENS NEXT boundary")
        print("=" * 60)

        boundary_check = run_js(page, """
            (() => {
                // Find WHAT HAPPENS NEXT and get surrounding context
                let whnEl = null;
                let whnOffsetTop = 0;

                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );

                while (walker.nextNode()) {
                    const node = walker.currentNode;
                    if (node.textContent.trim().toUpperCase().includes('WHAT HAPPENS NEXT')) {
                        whnEl = node.parentElement;
                        whnOffsetTop = whnEl.offsetTop;
                        break;
                    }
                }

                if (!whnEl) return {error: 'not found via TreeWalker'};

                // Walk UP to find the section containing it
                let sectionEl = whnEl;
                while (sectionEl && !sectionEl.classList.contains('elementor-section') && sectionEl !== document.body) {
                    sectionEl = sectionEl.parentElement;
                }

                const sectionStyle = sectionEl ? getComputedStyle(sectionEl) : {};
                const sectionRect = sectionEl ? sectionEl.getBoundingClientRect() : {};

                // Find NEXT sibling sections after the WHAT HAPPENS NEXT section
                const nextSiblings = [];
                if (sectionEl) {
                    let nextEl = sectionEl.nextElementSibling;
                    let count = 0;
                    while (nextEl && count < 10) {
                        const style = getComputedStyle(nextEl);
                        const rect = nextEl.getBoundingClientRect();
                        nextSiblings.push({
                            tag: nextEl.tagName,
                            className: (nextEl.className || '').substring(0, 80),
                            id: nextEl.id || '',
                            dataId: nextEl.getAttribute('data-id') || '',
                            offsetTop: nextEl.offsetTop,
                            rectHeight: rect.height,
                            display: style.display,
                            visibility: style.visibility,
                            overflow: style.overflow,
                            maxHeight: style.maxHeight,
                            opacity: style.opacity,
                            textSnippet: nextEl.textContent.trim().substring(0, 80)
                        });
                        nextEl = nextEl.nextElementSibling;
                        count++;
                    }
                }

                return {
                    whnElement: {
                        tag: whnEl.tagName,
                        className: (whnEl.className || '').substring(0, 60),
                        offsetTop: whnOffsetTop
                    },
                    containingSection: sectionEl ? {
                        tag: sectionEl.tagName,
                        className: (sectionEl.className || '').substring(0, 80),
                        dataId: sectionEl.getAttribute('data-id') || '',
                        offsetTop: sectionEl.offsetTop,
                        height: sectionRect.height,
                        display: sectionStyle.display,
                        overflow: sectionStyle.overflow,
                        maxHeight: sectionStyle.maxHeight
                    } : null,
                    nextSiblings: nextSiblings
                };
            })()
        """, "WHAT HAPPENS NEXT boundary check")

        # One final comprehensive screenshot at key positions
        print("\nCapturing final reference screenshots...")

        # Find and scroll to where WHAT HAPPENS NEXT ends
        run_js(page, """
            (() => {
                let whnEl = null;
                const allEls = document.querySelectorAll('*');
                for (const el of allEls) {
                    if (el.children.length === 0 && el.textContent &&
                        el.textContent.trim().toUpperCase().includes('WHAT HAPPENS NEXT')) {
                        whnEl = el;
                        break;
                    }
                }
                if (whnEl) {
                    // Find containing section
                    let sec = whnEl;
                    while (sec && !sec.classList.contains('elementor-section')) {
                        sec = sec.parentElement;
                    }
                    if (sec) {
                        // Scroll to bottom of this section
                        window.scrollTo(0, sec.offsetTop + sec.offsetHeight);
                    }
                }
            })()
        """)
        time.sleep(0.5)
        take_screenshot(page, "011-after-whn-section-boundary", "Immediately after WHAT HAPPENS NEXT section")

        browser.close()

        print("\n" + "=" * 60)
        print("INVESTIGATION COMPLETE")
        print(f"Screenshots saved to: {SCREENSHOT_DIR}")
        print("=" * 60)

if __name__ == "__main__":
    main()
