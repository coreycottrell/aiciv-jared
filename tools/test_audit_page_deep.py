#!/usr/bin/env python3
"""
Deep CSS + layout inspection of the audit page.
Checks for orange bleed, CSS scoping, brand colors, footer area.
"""

import time
import json
from playwright.sync_api import sync_playwright

URL = "https://purebrain.ai/ai-partnership-audit/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle", timeout=30000)
    time.sleep(2)

    # 1. Check body and html background colors
    colors = page.evaluate("""() => {
        const body = document.body;
        const html = document.documentElement;
        const bodyStyle = window.getComputedStyle(body);
        const htmlStyle = window.getComputedStyle(html);

        // Check if orange is visible anywhere
        const allElements = document.querySelectorAll('*');
        const orangeElements = [];
        Array.from(allElements).forEach(el => {
            const cs = window.getComputedStyle(el);
            const bg = cs.backgroundColor;
            if (bg.includes('241, 66') || bg.includes('241,66')) {
                orangeElements.push({
                    tag: el.tagName,
                    id: el.id || '',
                    class: el.className.toString().substring(0, 60),
                    bg: bg,
                    visible: el.offsetParent !== null || el === document.body
                });
            }
        });

        return {
            bodyBg: bodyStyle.backgroundColor,
            bodyColor: bodyStyle.color,
            htmlBg: htmlStyle.backgroundColor,
            orangeElements: orangeElements.slice(0, 20)
        };
    }""")
    print("=== COLOR ANALYSIS ===")
    print(f"Body background: {colors['bodyBg']}")
    print(f"Body text color: {colors['bodyColor']}")
    print(f"HTML background: {colors['htmlBg']}")
    print(f"\nOrange elements found ({len(colors['orangeElements'])}):")
    for el in colors['orangeElements']:
        print(f"  <{el['tag']}> id='{el['id']}' class='{el['class'][:50]}' bg={el['bg']} visible={el['visible']}")

    # 2. Check what wraps the content and what its background is
    wrapper_info = page.evaluate("""() => {
        // Check the main content wrapper
        const candidates = [
            '#pb-audit-page',
            '.pb-audit-page',
            '.elementor-location-single',
            'main',
            '.site-main',
            '.entry-content',
            'body > div:first-child',
            '.elementor'
        ];
        const result = {};
        candidates.forEach(sel => {
            try {
                const el = document.querySelector(sel);
                if (el) {
                    const cs = window.getComputedStyle(el);
                    result[sel] = {
                        bg: cs.backgroundColor,
                        found: true,
                        height: el.offsetHeight,
                        zIndex: cs.zIndex
                    };
                } else {
                    result[sel] = {found: false};
                }
            } catch(e) {
                result[sel] = {error: e.message};
            }
        });
        return result;
    }""")
    print("\n=== WRAPPER BACKGROUNDS ===")
    for sel, info in wrapper_info.items():
        if info.get('found'):
            print(f"  {sel}: bg={info['bg']} height={info.get('height')}px")
        else:
            print(f"  {sel}: not found")

    # 3. Check footer area specifically
    footer_info = page.evaluate("""() => {
        const footer = document.querySelector('footer, .site-footer, .elementor-location-footer');
        if (!footer) return {found: false};
        const cs = window.getComputedStyle(footer);
        return {
            found: true,
            bg: cs.backgroundColor,
            height: footer.offsetHeight,
            visible: footer.offsetParent !== null
        };
    }""")
    print("\n=== FOOTER ===")
    print(json.dumps(footer_info, indent=2))

    # 4. Check the score display + rating buttons
    interactive = page.evaluate("""() => {
        // Find rating buttons (1-5 scale)
        const ratingBtns = document.querySelectorAll('.rating-btn, [data-rating], .audit-rating, button');
        const scoreDisplay = document.querySelector('.live-score, .score-display, #liveScore, [class*="score"]');
        const submitBtn = document.querySelector('button[type="submit"], input[type="submit"], .get-results-btn, [class*="submit"]');

        return {
            ratingButtonCount: ratingBtns.length,
            ratingBtnStyles: Array.from(ratingBtns).slice(0, 3).map(b => ({
                text: b.textContent.trim(),
                bg: window.getComputedStyle(b).backgroundColor,
                color: window.getComputedStyle(b).color,
                visible: b.offsetParent !== null
            })),
            hasScoreDisplay: !!scoreDisplay,
            scoreDisplayText: scoreDisplay ? scoreDisplay.textContent.trim() : '',
            hasSubmitBtn: !!submitBtn,
            submitBtnText: submitBtn ? submitBtn.textContent.trim() : ''
        };
    }""")
    print("\n=== INTERACTIVE ELEMENTS ===")
    print(json.dumps(interactive, indent=2))

    # 5. Check the CTA button styling (Get My Results)
    cta_info = page.evaluate("""() => {
        const cta = document.querySelector('.get-results-btn, button[class*="cta"], a[class*="cta"], .submit-btn, [class*="results"]');
        const allButtons = document.querySelectorAll('button, input[type="submit"]');
        return {
            mainCta: cta ? {
                text: cta.textContent.trim(),
                bg: window.getComputedStyle(cta).backgroundColor,
                color: window.getComputedStyle(cta).color,
                border: window.getComputedStyle(cta).border,
                visible: cta.offsetParent !== null
            } : null,
            allButtonStyles: Array.from(allButtons).map(b => ({
                text: b.textContent.trim().substring(0, 40),
                bg: window.getComputedStyle(b).backgroundColor,
                color: window.getComputedStyle(b).color,
                class: b.className.substring(0, 50)
            }))
        };
    }""")
    print("\n=== CTA BUTTON ANALYSIS ===")
    print(json.dumps(cta_info, indent=2))

    # 6. Check if orange strip at bottom is intentional brand stripe or a bug
    body_after = page.evaluate("""() => {
        // Check body::after pseudo element for orange stripe
        const bodyStyle = window.getComputedStyle(document.body, '::after');
        const htmlStyle = window.getComputedStyle(document.documentElement, '::after');
        return {
            bodyAfterBg: bodyStyle.backgroundColor,
            bodyAfterHeight: bodyStyle.height,
            bodyAfterContent: bodyStyle.content,
            htmlAfterBg: htmlStyle.backgroundColor
        };
    }""")
    print("\n=== BODY::AFTER (Orange stripe source?) ===")
    print(json.dumps(body_after, indent=2))

    # 7. Check PureBrain brand color usage
    brand_colors = page.evaluate("""() => {
        const allEls = document.querySelectorAll('*');
        const blueEls = [];
        const orangeEls = [];
        Array.from(allEls).forEach(el => {
            const cs = window.getComputedStyle(el);
            const color = cs.color;
            const bg = cs.backgroundColor;
            // Blue: #2a93c1 = rgb(42, 147, 193)
            if (color.includes('42, 147') || bg.includes('42, 147')) {
                blueEls.push({tag: el.tagName, class: el.className.toString().substring(0,40), where: color.includes('42, 147') ? 'color' : 'bg'});
            }
            // Orange: #f1420b = rgb(241, 66, 11)
            if (color.includes('241, 66') && el.offsetParent !== null) {
                orangeEls.push({tag: el.tagName, text: el.textContent.trim().substring(0,30), class: el.className.toString().substring(0,40)});
            }
        });
        return {
            blueCount: blueEls.length,
            blueSample: blueEls.slice(0, 5),
            orangeTextCount: orangeEls.length,
            orangeTextSample: orangeEls.slice(0, 5)
        };
    }""")
    print("\n=== BRAND COLOR USAGE ===")
    print(f"Blue (#2a93c1) elements: {brand_colors['blueCount']}")
    for el in brand_colors['blueSample']:
        print(f"  {el}")
    print(f"Orange text elements: {brand_colors['orangeTextCount']}")
    for el in brand_colors['orangeTextSample']:
        print(f"  {el}")

    ctx.close()
    browser.close()
    print("\n=== Done ===")
