#!/usr/bin/env python3
"""
Invitation Page Audit - 2026-02-27
Focus: 10-point checklist including 3D brain animation, logo, countdown, pricing, etc.
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright

URL = "https://purebrain.ai/invitation/"
PASSWORD = "purebrain25"
SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/invitation-audit-2026-02-27"

FORCE_VISIBLE_JS = """
() => {
    const style = document.createElement('style');
    style.textContent = `
        .pb-fade-in, .pb-fade-up, [class*="fade"] {
            opacity: 1 !important;
            transform: none !important;
            visibility: visible !important;
        }
    `;
    document.head.appendChild(style);

    document.querySelectorAll('.pb-fade-in, .pb-fade-up').forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
        el.style.visibility = 'visible';
    });

    return document.querySelectorAll('.pb-fade-in').length;
}
"""

async def run_audit():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    findings = {}
    console_errors = []
    console_logs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Desktop audit
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # Capture console
        page.on("console", lambda msg: console_logs.append({"type": msg.type, "text": msg.text}))
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        print("Navigating to invitation page...")
        try:
            await page.goto(URL, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"Navigation warning: {e}")

        await page.wait_for_timeout(2000)

        # Check if password protected
        pw_input = await page.query_selector("input[type='password']")
        if pw_input:
            print("Page is password protected - entering password...")
            await pw_input.fill(PASSWORD)
            submit = await page.query_selector("input[type='submit']")
            if submit:
                await submit.click()
            await page.wait_for_timeout(8000)
            print("Password submitted, waiting for page load...")

        # Wait for any JS to settle
        await page.wait_for_timeout(3000)

        # Screenshot 1: Full initial desktop view
        await page.screenshot(path=f"{SCREENSHOTS_DIR}/01-desktop-initial.png", full_page=False)
        print("Screenshot 1: Initial desktop view taken")

        # Force animations visible
        fade_count = await page.evaluate(FORCE_VISIBLE_JS)
        print(f"Forced {fade_count} fade-in elements visible")
        await page.wait_for_timeout(1000)

        # Screenshot 2: Full page desktop (after force-visible)
        await page.screenshot(path=f"{SCREENSHOTS_DIR}/02-desktop-full-page.png", full_page=True)
        print("Screenshot 2: Full page desktop taken")

        # CHECK 1: 3D Brain Animation
        print("\n--- CHECK 1: 3D Brain Animation ---")
        threejs_check = await page.evaluate("""
        () => {
            // Check for Three.js canvas
            const canvases = document.querySelectorAll('canvas');
            const threeCanvas = Array.from(canvases).find(c => {
                const parent = c.closest('#neural-bg, .neural-bg, [id*="neural"], [class*="neural"], [id*="brain"], [class*="brain"], [id*="three"], [class*="three"]');
                return parent !== null;
            });

            // Check for Three.js global
            const hasThree = typeof THREE !== 'undefined';

            // Check for neural/brain related scripts
            const scripts = Array.from(document.scripts);
            const hasNeuralScript = scripts.some(s =>
                s.src && (s.src.includes('three') || s.src.includes('neural') || s.src.includes('brain'))
            );
            const hasInlineNeuralScript = scripts.some(s =>
                !s.src && s.textContent && (
                    s.textContent.includes('THREE') ||
                    s.textContent.includes('neural') ||
                    s.textContent.includes('NeuralBrain') ||
                    s.textContent.includes('WebGLRenderer')
                )
            );

            // Check for all canvas elements
            const allCanvases = Array.from(canvases).map(c => ({
                id: c.id,
                className: c.className,
                width: c.width,
                height: c.height,
                parent_id: c.parentElement ? c.parentElement.id : '',
                parent_class: c.parentElement ? (typeof c.parentElement.className === 'string' ? c.parentElement.className.substring(0, 60) : '') : ''
            }));

            return {
                canvasCount: canvases.length,
                allCanvases: allCanvases,
                hasThreeGlobal: hasThree,
                hasNeuralScript: hasNeuralScript,
                hasInlineNeuralScript: hasInlineNeuralScript,
                threeCanvasFound: threeCanvas !== null
            };
        }
        """)
        findings['three_js_check'] = threejs_check
        print(json.dumps(threejs_check, indent=2))

        # More detailed canvas inspection
        canvas_rendered = await page.evaluate("""
        () => {
            const canvases = document.querySelectorAll('canvas');
            return Array.from(canvases).map(c => {
                // Check if canvas has any rendered content (non-zero pixels)
                try {
                    const ctx = c.getContext('2d');
                    if (ctx) {
                        const data = ctx.getImageData(0, 0, Math.min(c.width, 100), Math.min(c.height, 100));
                        const nonZeroPixels = data.data.filter(v => v > 0).length;
                        return { id: c.id, type: '2d', width: c.width, height: c.height, hasContent: nonZeroPixels > 0 };
                    }
                    const webgl = c.getContext('webgl') || c.getContext('webgl2');
                    if (webgl) {
                        return { id: c.id, type: 'webgl', width: c.width, height: c.height, hasContent: 'webgl-active' };
                    }
                } catch(e) {
                    return { id: c.id, error: e.message };
                }
                return { id: c.id, type: 'unknown' };
            });
        }
        """)
        findings['canvas_rendered'] = canvas_rendered
        print("Canvas render state:", json.dumps(canvas_rendered, indent=2))

        # Check for neural background element
        neural_bg = await page.evaluate("""
        () => {
            const selectors = [
                '#neural-bg', '#neural-network-bg', '#brain-bg', '#threejs-canvas',
                '.neural-bg', '.brain-animation', '[data-animation="neural"]'
            ];
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el) {
                    const rect = el.getBoundingClientRect();
                    return { found: true, selector: sel, rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height } };
                }
            }
            // Broader search
            const heroSection = document.querySelector('.pb-hero, #pb-hero, [class*="hero"]');
            if (heroSection) {
                const heroCanvas = heroSection.querySelector('canvas');
                if (heroCanvas) {
                    return { found: true, selector: 'canvas inside .pb-hero', canvasId: heroCanvas.id };
                }
            }
            return { found: false };
        }
        """)
        findings['neural_bg_element'] = neural_bg
        print("Neural BG element:", json.dumps(neural_bg, indent=2))

        # CHECK 2: Logo
        print("\n--- CHECK 2: Logo ---")
        logo_check = await page.evaluate("""
        () => {
            // Check for logo image
            const logoImgs = document.querySelectorAll('img[src*="logo"], img[alt*="logo"], img[alt*="PureBrain"], .logo img, .pb-logo img');
            const logoLinks = document.querySelectorAll('a[href*="purebrain"] img, .site-logo img');

            // Check for SVG placeholder (hexagon)
            const svgElements = document.querySelectorAll('svg');
            const hexagonSvg = Array.from(svgElements).filter(s => {
                const paths = s.querySelectorAll('polygon, path');
                return paths.length > 0 && s.closest('.logo, .pb-logo, header, nav, .pb-hero');
            });

            return {
                logoImgCount: logoImgs.length,
                logoImgSrcs: Array.from(logoImgs).map(i => ({ src: i.src.substring(0, 100), alt: i.alt, width: i.naturalWidth, height: i.naturalHeight })),
                logoLinkCount: logoLinks.length,
                svgInHeaderCount: hexagonSvg.length,
                svgDetails: hexagonSvg.map(s => ({ parent: s.parentElement ? (typeof s.parentElement.className === 'string' ? s.parentElement.className.substring(0,50) : '') : '', innerHTML: s.innerHTML.substring(0, 100) }))
            };
        }
        """)
        findings['logo_check'] = logo_check
        print(json.dumps(logo_check, indent=2))

        # CHECK 3: Countdown Timer
        print("\n--- CHECK 3: Countdown Timer ---")
        countdown_check = await page.evaluate("""
        () => {
            // Look for countdown elements
            const countdownSelectors = [
                '.countdown', '#countdown', '[class*="countdown"]',
                '.timer', '#timer', '[class*="timer"]',
                '[class*="clock"]', '.pb-countdown'
            ];

            let countdowns = [];
            for (const sel of countdownSelectors) {
                const els = document.querySelectorAll(sel);
                els.forEach(el => {
                    countdowns.push({
                        selector: sel,
                        text: el.textContent.trim().substring(0, 100),
                        visible: el.offsetParent !== null
                    });
                });
            }

            // Also check for time display patterns
            const allText = document.body.innerText;
            const hasTimePattern = /\d{2}:\d{2}:\d{2}/.test(allText);
            const timeMatches = allText.match(/\d{2}:\d{2}:\d{2}/g);

            // Find inline deadline JS
            const scripts = Array.from(document.scripts);
            const deadlineScript = scripts.find(s => !s.src && s.textContent && s.textContent.includes('deadline'));

            return {
                countdownElements: countdowns,
                hasTimePattern: hasTimePattern,
                timeValues: timeMatches,
                deadlineScriptExists: deadlineScript !== undefined,
                deadlineSnippet: deadlineScript ? deadlineScript.textContent.substring(0, 300) : null
            };
        }
        """)
        findings['countdown_check'] = countdown_check
        print(json.dumps(countdown_check, indent=2))

        # CHECK 4: Pricing Tiers
        print("\n--- CHECK 4: Pricing Tiers ---")
        pricing_check = await page.evaluate("""
        () => {
            const priceSection = document.querySelector('.pb-pricing, #pb-pricing, [class*="pricing"]');
            if (!priceSection) return { found: false };

            const cards = priceSection.querySelectorAll('.pricing-card, .tier-card, [class*="card"], .pb-card');
            const tierNames = [];
            const tierPrices = [];

            // Scan for price patterns
            const priceText = priceSection.innerHTML;
            const dollarMatches = priceText.match(/\$\d+/g);

            // Look for tier name keywords
            const tiers = ['Awakened', 'Bonded', 'Partnered', 'Unified'];
            const foundTiers = tiers.filter(t => priceSection.innerText.includes(t));

            return {
                pricingSectionFound: true,
                cardCount: cards.length,
                dollarAmounts: dollarMatches,
                foundTierNames: foundTiers,
                pricingText: priceSection.innerText.substring(0, 500)
            };
        }
        """)
        findings['pricing_check'] = pricing_check
        print(json.dumps(pricing_check, indent=2))

        # CHECK 5: Jared Quote
        print("\n--- CHECK 5: Jared Quote ---")
        quote_check = await page.evaluate("""
        () => {
            const fullText = document.body.innerText;
            const targetQuote = 'We picked you because we believe in what you';
            const hasQuote = fullText.includes(targetQuote);

            // Find the element containing it
            const allEls = document.querySelectorAll('p, blockquote, q, .quote, [class*="quote"]');
            const quoteEl = Array.from(allEls).find(el => el.innerText && el.innerText.includes('We picked you'));

            return {
                quoteFound: hasQuote,
                quoteElementTag: quoteEl ? quoteEl.tagName : null,
                quoteElementClass: quoteEl ? (typeof quoteEl.className === 'string' ? quoteEl.className.substring(0,60) : '') : null,
                quoteText: quoteEl ? quoteEl.innerText.substring(0, 200) : null
            };
        }
        """)
        findings['quote_check'] = quote_check
        print(json.dumps(quote_check, indent=2))

        # CHECK 6: Michael Hancock Testimonial
        print("\n--- CHECK 6: Michael Hancock Testimonial ---")
        testimonial_check = await page.evaluate("""
        () => {
            const fullText = document.body.innerText;
            const hasMichael = fullText.includes('Michael') || fullText.includes('Hancock');

            const testimonialEls = document.querySelectorAll('.testimonial, [class*="testimonial"], .pb-proof, [class*="proof"]');
            const testimonialTexts = Array.from(testimonialEls).map(el => el.innerText.substring(0, 200));

            return {
                hasMichaelHancock: hasMichael,
                testimonialSectionFound: testimonialEls.length > 0,
                testimonialTexts: testimonialTexts
            };
        }
        """)
        findings['testimonial_check'] = testimonial_check
        print(json.dumps(testimonial_check, indent=2))

        # CHECK 7: CTA Buttons
        print("\n--- CHECK 7: CTA Buttons ---")
        cta_check = await page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('a, button');
            const ctaButtons = Array.from(buttons).filter(b => {
                const text = b.innerText || b.textContent || '';
                const href = b.getAttribute('href') || '';
                return (
                    text.includes('Claim') || text.includes('Join') || text.includes('Get') ||
                    text.includes('Start') || text.includes('Awaken') || text.includes('Secure') ||
                    href.includes('awakening')
                );
            });

            return {
                ctaButtonCount: ctaButtons.length,
                ctaButtons: ctaButtons.slice(0, 8).map(b => {
                    const computed = window.getComputedStyle(b);
                    return {
                        text: (b.innerText || b.textContent || '').trim().substring(0, 60),
                        href: b.getAttribute('href'),
                        bgColor: computed.backgroundColor,
                        color: computed.color,
                        display: computed.display,
                        visible: b.offsetParent !== null || b.offsetWidth > 0
                    };
                })
            };
        }
        """)
        findings['cta_check'] = cta_check
        print(json.dumps(cta_check, indent=2))

        # CHECK 8: "The Process" section with 4 steps
        print("\n--- CHECK 8: The Process Section ---")
        process_check = await page.evaluate("""
        () => {
            const fullText = document.body.innerText;
            const hasProcess = fullText.includes('The Process') || fullText.includes('process');
            const processSection = document.querySelector('.pb-awakening, [class*="awakening"], [class*="process"]');

            // Count step numbers
            const stepMatches = fullText.match(/Step \d|0[1-4]\.|Phase \d/g);

            return {
                hasProcessText: hasProcess,
                processSectionFound: processSection !== null,
                stepMatches: stepMatches,
                processText: processSection ? processSection.innerText.substring(0, 500) : null
            };
        }
        """)
        findings['process_check'] = process_check
        print(json.dumps(process_check, indent=2))

        # CHECK 9: Chat Mockup
        print("\n--- CHECK 9: Chat Mockup ---")
        chat_check = await page.evaluate("""
        () => {
            const chatEls = document.querySelectorAll('.chat, [class*="chat"], .mockup, [class*="mockup"], .pb-chat, [class*="conversation"]');
            const fullText = document.body.innerText;
            const hasChatContent = fullText.includes('Hello') || fullText.includes('How can') || fullText.includes('Tell me about');

            return {
                chatElementCount: chatEls.length,
                chatElements: Array.from(chatEls).slice(0, 5).map(el => ({
                    tag: el.tagName,
                    className: typeof el.className === 'string' ? el.className.substring(0, 60) : '',
                    text: el.innerText ? el.innerText.substring(0, 100) : ''
                })),
                hasChatContent: hasChatContent
            };
        }
        """)
        findings['chat_check'] = chat_check
        print(json.dumps(chat_check, indent=2))

        # CHECK 10: Console errors summary (already capturing via event)
        await page.wait_for_timeout(2000)

        # Scroll through page and take section screenshots
        print("\nTaking section screenshots...")

        # Get page height
        page_height = await page.evaluate("() => document.body.scrollHeight")
        print(f"Page height: {page_height}px")

        # Screenshot at key scroll positions
        scroll_positions = [0, 900, 1800, 2700, 3600, 4300, 5100]
        for i, pos in enumerate(scroll_positions):
            await page.evaluate(f"window.scrollTo(0, {pos})")
            await page.wait_for_timeout(500)
            await page.evaluate(FORCE_VISIBLE_JS)
            await page.wait_for_timeout(300)
            await page.screenshot(path=f"{SCREENSHOTS_DIR}/03-scroll-{i:02d}-y{pos}.png")

        print("Section screenshots done")

        # MOBILE AUDIT
        print("\n=== MOBILE AUDIT ===")
        mobile_context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        mobile_page = await mobile_context.new_page()
        mobile_page.on("console", lambda msg: console_logs.append({"type": msg.type + "-mobile", "text": msg.text}))

        try:
            await mobile_page.goto(URL, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"Mobile navigation warning: {e}")

        await mobile_page.wait_for_timeout(2000)

        pw_input_mobile = await mobile_page.query_selector("input[type='password']")
        if pw_input_mobile:
            await pw_input_mobile.fill(PASSWORD)
            submit = await mobile_page.query_selector("input[type='submit']")
            if submit:
                await submit.click()
            await mobile_page.wait_for_timeout(8000)

        await mobile_page.wait_for_timeout(2000)
        await mobile_page.evaluate(FORCE_VISIBLE_JS)
        await mobile_page.wait_for_timeout(1000)

        await mobile_page.screenshot(path=f"{SCREENSHOTS_DIR}/04-mobile-initial.png")
        print("Mobile initial screenshot taken")

        # Mobile 3D check
        mobile_threejs = await mobile_page.evaluate("""
        () => {
            const canvases = document.querySelectorAll('canvas');
            const hasThree = typeof THREE !== 'undefined';
            return {
                canvasCount: canvases.length,
                hasThreeGlobal: hasThree,
                canvases: Array.from(canvases).map(c => ({ id: c.id, w: c.width, h: c.height }))
            };
        }
        """)
        findings['mobile_threejs'] = mobile_threejs
        print("Mobile Three.js check:", json.dumps(mobile_threejs, indent=2))

        # Mobile full page
        await mobile_page.screenshot(path=f"{SCREENSHOTS_DIR}/05-mobile-full-page.png", full_page=True)
        print("Mobile full page screenshot taken")

        await mobile_context.close()
        await context.close()
        await browser.close()

    # Categorize console messages
    errors = [m for m in console_logs if m['type'] in ('error', 'pageerror')]
    warnings = [m for m in console_logs if m['type'] == 'warning']
    threejs_errors = [m for m in errors if 'three' in m['text'].lower() or 'webgl' in m['text'].lower() or 'shader' in m['text'].lower()]

    findings['console_summary'] = {
        'total_messages': len(console_logs),
        'error_count': len(errors),
        'warning_count': len(warnings),
        'threejs_specific_errors': threejs_errors,
        'all_errors': errors[:20],
        'page_errors': console_errors[:10]
    }

    return findings

if __name__ == "__main__":
    results = asyncio.run(run_audit())

    # Save findings
    output_path = "/home/jared/projects/AI-CIV/aether/exports/invitation-audit-findings-feb27.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nFindings saved to: {output_path}")
    print("Screenshots saved to:", "/home/jared/projects/AI-CIV/aether/exports/screenshots/invitation-audit-2026-02-27/")
