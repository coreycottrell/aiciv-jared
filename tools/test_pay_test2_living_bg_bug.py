#!/usr/bin/env python3
"""
Targeted investigation: .living-background mobile CSS rule causing invisible content on pay-test-2
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

        # Test on mobile viewport (where bug occurs)
        mobile_ctx = browser.new_context(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        )
        page = mobile_ctx.new_page()

        print("=" * 60)
        print("TARGETED INVESTIGATION: .living-background mobile bug")
        print("=" * 60)

        page.goto(PAGE_URL, wait_until="networkidle", timeout=30000)
        time.sleep(2)

        pw_input = page.query_selector('input[id^="pwbox-"]')
        if pw_input:
            pw_input.fill(PASSWORD)
            page.click('input[type="submit"]')
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(3)

        print("\n--- INVESTIGATION 1: Find the full .living-background rules ---")

        living_bg_rules = run_js(page, """
            (() => {
                const results = [];
                Array.from(document.styleSheets).forEach(sheet => {
                    try {
                        Array.from(sheet.cssRules || []).forEach(rule => {
                            const ruleText = rule.cssText || '';
                            // Direct rules
                            if (ruleText.includes('living-background')) {
                                results.push({
                                    type: 'direct',
                                    cssText: ruleText.substring(0, 500)
                                });
                            }
                            // Media query rules
                            if (rule.cssRules) {
                                Array.from(rule.cssRules).forEach(innerRule => {
                                    const innerText = innerRule.cssText || '';
                                    if (innerText.includes('living-background')) {
                                        results.push({
                                            type: 'media',
                                            media: rule.conditionText || rule.media?.mediaText || 'unknown',
                                            cssText: innerText.substring(0, 1000)
                                        });
                                    }
                                });
                            }
                        });
                    } catch(e) {}
                });
                return results;
            })()
        """, "All .living-background CSS rules")

        print("\n--- INVESTIGATION 2: Check body classes and page ID ---")

        body_info = run_js(page, """
            (() => {
                const body = document.body;
                const classes = Array.from(body.classList);
                const pageIdClass = classes.find(c => c.startsWith('page-id-'));
                return {
                    bodyClasses: classes,
                    pageIdClass: pageIdClass || 'none',
                    isPageId689: body.classList.contains('page-id-689'),
                    isHome: body.classList.contains('home')
                };
            })()
        """, "Body class info")

        print("\n--- INVESTIGATION 3: Find .living-background element and compute its mobile style ---")

        living_bg_element = run_js(page, """
            (() => {
                const el = document.querySelector('.living-background');
                if (!el) return {error: '.living-background element NOT FOUND'};

                const style = getComputedStyle(el);
                const rect = el.getBoundingClientRect();

                return {
                    found: true,
                    tag: el.tagName,
                    id: el.id,
                    className: el.className.substring(0, 100),
                    rect: {
                        top: rect.top,
                        left: rect.left,
                        width: rect.width,
                        height: rect.height
                    },
                    computedStyle: {
                        display: style.display,
                        visibility: style.visibility,
                        position: style.position,
                        overflow: style.overflow,
                        overflowY: style.overflowY,
                        maxHeight: style.maxHeight,
                        height: style.height,
                        opacity: style.opacity,
                        zIndex: style.zIndex,
                        contain: style.contain
                    },
                    // Get inline styles
                    inlineStyle: el.style.cssText,
                    // Check all children
                    childCount: el.children.length,
                    // Sample first child
                    firstChildInfo: el.firstElementChild ? {
                        tag: el.firstElementChild.tagName,
                        className: el.firstElementChild.className.substring(0, 60),
                        height: el.firstElementChild.getBoundingClientRect().height
                    } : null
                };
            })()
        """, ".living-background element")

        print("\n--- INVESTIGATION 4: Check if the living-background * rule collapses ALL children ---")

        children_impact = run_js(page, """
            (() => {
                const el = document.querySelector('.living-background');
                if (!el) return {error: 'not found'};

                // Check what's happening to its direct children
                const directChildren = Array.from(el.children);
                return {
                    childCount: directChildren.length,
                    children: directChildren.slice(0, 5).map(child => {
                        const style = getComputedStyle(child);
                        const rect = child.getBoundingClientRect();
                        return {
                            tag: child.tagName,
                            className: child.className.substring(0, 60),
                            height: rect.height,
                            display: style.display,
                            visibility: style.visibility,
                            overflow: style.overflow,
                            maxHeight: style.maxHeight,
                            position: style.position
                        };
                    }),
                    // Check if the RULE applies display:none or similar to all *
                    ruleEffect: (() => {
                        // Look specifically for rules targeting .living-background * on mobile
                        const rules = [];
                        Array.from(document.styleSheets).forEach(sheet => {
                            try {
                                Array.from(sheet.cssRules || []).forEach(rule => {
                                    if (rule.media) {
                                        Array.from(rule.cssRules || []).forEach(innerRule => {
                                            if (innerRule.cssText && innerRule.cssText.includes('living-background *')) {
                                                rules.push({
                                                    media: rule.conditionText || 'unknown',
                                                    fullRule: innerRule.cssText.substring(0, 500)
                                                });
                                            }
                                        });
                                    }
                                    if (rule.cssText && rule.cssText.includes('living-background *')) {
                                        rules.push({
                                            type: 'direct',
                                            fullRule: rule.cssText.substring(0, 500)
                                        });
                                    }
                                });
                            } catch(e) {}
                        });
                        return rules;
                    })()
                };
            })()
        """, ".living-background children analysis")

        print("\n--- INVESTIGATION 5: THE SMOKING GUN - What is the full mobile rule? ---")

        smoking_gun = run_js(page, """
            (() => {
                const allRules = [];
                Array.from(document.styleSheets).forEach((sheet, si) => {
                    try {
                        Array.from(sheet.cssRules || []).forEach((rule, ri) => {
                            // Check media queries
                            if (rule.type === 4 && rule.cssRules) { // CSSMediaRule
                                const mediaText = rule.conditionText || rule.media?.mediaText || '';
                                if (mediaText.includes('767') || mediaText.includes('max-width')) {
                                    Array.from(rule.cssRules).forEach(innerRule => {
                                        const text = innerRule.cssText || '';
                                        if (text.includes('living-background') || text.includes('page-id-689')) {
                                            allRules.push({
                                                sheetIndex: si,
                                                ruleIndex: ri,
                                                media: mediaText,
                                                fullText: text.substring(0, 2000)
                                            });
                                        }
                                    });
                                }
                            }
                            // Check direct rules
                            const text = rule.cssText || '';
                            if (text.includes('page-id-689') && text.includes('living-background')) {
                                allRules.push({
                                    type: 'direct',
                                    fullText: text.substring(0, 2000)
                                });
                            }
                        });
                    } catch(e) {
                        allRules.push({error: e.message, sheetHref: sheet.href});
                    }
                });
                return allRules;
            })()
        """, "Smoking gun rules")

        print("\n--- INVESTIGATION 6: Does the .living-background * rule set height/display on all children? ---")

        # Test by temporarily removing the rule and seeing if content appears
        before_fix = run_js(page, """
            (() => {
                // Find WHAT HAPPENS NEXT and check its height
                const whn = Array.from(document.querySelectorAll('h2')).find(
                    el => el.textContent.trim().toUpperCase().includes('WHAT HAPPENS NEXT')
                );
                if (!whn) return {error: 'WHN not found'};

                const rect = whn.getBoundingClientRect();
                return {
                    whnHeight: rect.height,
                    whnTop: rect.top + window.scrollY,
                    whnVisible: rect.height > 0 && getComputedStyle(whn).display !== 'none'
                };
            })()
        """, "WHN visibility BEFORE fix attempt")

        # Now try removing the living-background from the relevant containers and see what happens
        fix_attempt = run_js(page, """
            (() => {
                // The theory: .living-background * { some property: value } on mobile is hiding content
                // Let's check if removing .living-background class from parent fixes content
                const lb = document.querySelector('.living-background');
                if (!lb) return {error: 'not found'};

                // Temporarily remove class to test
                lb.classList.remove('living-background');

                // Now check height of a content section that was invisible
                const whn = Array.from(document.querySelectorAll('h2')).find(
                    el => el.textContent.trim().toUpperCase().includes('WHAT HAPPENS NEXT')
                );
                const whnRect = whn ? whn.getBoundingClientRect() : null;

                // Check timeline section height
                const timeline = document.querySelector('.timeline-section');
                const timelineRect = timeline ? timeline.getBoundingClientRect() : null;

                // Check testimonials
                const testimonials = document.querySelector('.testimonials-section');
                const testimonialsRect = testimonials ? testimonials.getBoundingClientRect() : null;

                // Restore class
                lb.classList.add('living-background');

                return {
                    whnHeightAfterRemoval: whnRect ? whnRect.height : 'no element',
                    timelineHeightAfterRemoval: timelineRect ? timelineRect.height : 'no element',
                    testimonialsHeightAfterRemoval: testimonialsRect ? testimonialsRect.height : 'no element'
                };
            })()
        """, "Height after removing .living-background class (test)")

        print("\n--- INVESTIGATION 7: Get the FULL mobile CSS that targets living-background ---")

        full_mobile_css = run_js(page, """
            (() => {
                // Enumerate ALL stylesheets for the complete rule text
                const found = [];
                for (let si = 0; si < document.styleSheets.length; si++) {
                    const sheet = document.styleSheets[si];
                    try {
                        for (let ri = 0; ri < sheet.cssRules.length; ri++) {
                            const rule = sheet.cssRules[ri];
                            if (rule.type === 4) { // CSSMediaRule
                                const media = rule.conditionText || rule.media?.mediaText || '';
                                for (let ii = 0; ii < rule.cssRules.length; ii++) {
                                    const innerRule = rule.cssRules[ii];
                                    const text = innerRule.cssText || '';
                                    if (text.includes('living-background')) {
                                        found.push({
                                            sheetHref: sheet.href ? sheet.href.split('/').slice(-2).join('/') : 'inline',
                                            media: media,
                                            selectorText: innerRule.selectorText || '',
                                            fullCssText: text
                                        });
                                    }
                                }
                            }
                        }
                    } catch(e) {}
                }
                return found;
            })()
        """, "Full mobile CSS targeting living-background")

        print("\n--- INVESTIGATION 8: Screenshot comparison - before/after class removal ---")

        # Scroll to WHAT HAPPENS NEXT
        run_js(page, """
            const whn = Array.from(document.querySelectorAll('h2')).find(
                el => el.textContent.trim().toUpperCase().includes('WHAT HAPPENS NEXT')
            );
            if (whn) whn.scrollIntoView({behavior: 'instant', block: 'center'});
        """)
        time.sleep(0.5)
        take_screenshot(page, "012-targeted-whn-before", "WHAT HAPPENS NEXT before CSS fix")

        # Now scroll down one page
        page.evaluate("window.scrollBy(0, 812)")
        time.sleep(0.5)
        take_screenshot(page, "013-one-page-below-whn", "One page below WHN - what's there?")

        page.evaluate("window.scrollBy(0, 812)")
        time.sleep(0.5)
        take_screenshot(page, "014-two-pages-below-whn", "Two pages below WHN")

        # Apply temporary fix: inject CSS to override the mobile rule
        print("\n--- INVESTIGATION 9: Apply temporary CSS override and see what appears ---")

        run_js(page, """
            // Inject override CSS to undo whatever living-background * is doing on mobile
            const style = document.createElement('style');
            style.id = 'temp-fix';
            style.textContent = `
                .living-background,
                .living-background * {
                    height: auto !important;
                    max-height: none !important;
                    overflow: visible !important;
                    display: revert !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                }
            `;
            document.head.appendChild(style);
        """)
        time.sleep(0.5)

        # Scroll back to WHN
        run_js(page, """
            const whn = Array.from(document.querySelectorAll('h2')).find(
                el => el.textContent.trim().toUpperCase().includes('WHAT HAPPENS NEXT')
            );
            if (whn) whn.scrollIntoView({behavior: 'instant', block: 'center'});
        """)
        time.sleep(0.5)
        take_screenshot(page, "015-after-override-whn", "WHN area after CSS override injection")

        page.evaluate("window.scrollBy(0, 812)")
        time.sleep(0.5)
        take_screenshot(page, "016-after-override-below-whn", "One page below WHN after override")

        page.evaluate("window.scrollBy(0, 812)")
        time.sleep(0.5)
        take_screenshot(page, "017-after-override-far-below", "Two pages below WHN after override")

        # Check new heights after override
        after_fix = run_js(page, """
            (() => {
                const whn = Array.from(document.querySelectorAll('h2')).find(
                    el => el.textContent.trim().toUpperCase().includes('WHAT HAPPENS NEXT')
                );
                const timeline = document.querySelector('.timeline-section');
                const testimonials = document.querySelector('.testimonials-section');

                const whnRect = whn ? whn.getBoundingClientRect() : null;
                const timelineRect = timeline ? timeline.getBoundingClientRect() : null;
                const testimonialsRect = testimonials ? testimonials.getBoundingClientRect() : null;

                return {
                    whnHeight: whnRect ? whnRect.height : 'not found',
                    timelineHeight: timelineRect ? timelineRect.height : 'not found',
                    testimonialsHeight: testimonialsRect ? testimonialsRect.height : 'not found',
                    pageScrollHeight: document.documentElement.scrollHeight
                };
            })()
        """, "Heights AFTER CSS override")

        browser.close()
        print("\n" + "=" * 60)
        print("TARGETED INVESTIGATION COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    main()
