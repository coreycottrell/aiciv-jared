"""
Invitation Page Visual Audit - v2 (fixed className issue)
URL: https://purebrain.ai/invitation/
Password: purebrain25
"""

import asyncio
import os
import json
from playwright.async_api import async_playwright

OUTPUT = "/home/jared/projects/AI-CIV/aether/exports/screenshots/invitation-audit-2026-02-26"
os.makedirs(OUTPUT, exist_ok=True)

TARGET_URL = "https://purebrain.ai/invitation/"
PASSWORD = "purebrain25"


async def run_audit():
    results = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        # Capture console errors
        console_errors = []
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        page.on("console", lambda msg: console_errors.append({
            "type": msg.type,
            "text": msg.text[:200]
        }) if msg.type in ["error", "warning"] else None)

        print("[1] Navigating to invitation page...")
        resp = await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        print(f"    Status: {resp.status} - {page.url}")
        await asyncio.sleep(3)

        # Screenshot: password form
        await page.screenshot(path=f"{OUTPUT}/01-password-form.png", full_page=False)
        print("[2] Screenshot 01: Password form captured")

        pw_input = page.locator("input[type='password']")
        pw_count = await pw_input.count()
        print(f"    Password inputs found: {pw_count}")

        if pw_count > 0:
            await pw_input.first.fill(PASSWORD)
            await asyncio.sleep(0.5)
            submit_btn = page.locator("input[type='submit']")
            submit_count = await submit_btn.count()
            if submit_count > 0:
                await submit_btn.first.click()
            else:
                await page.keyboard.press("Enter")

            print("[3] Waiting 10s for Elementor page to load...")
            await asyncio.sleep(10)

        await page.screenshot(path=f"{OUTPUT}/02-after-password-viewport.png", full_page=False)
        print("[4] Screenshot 02: Post-password viewport captured")

        page_height = await page.evaluate("document.documentElement.scrollHeight")
        print(f"[5] Full page height: {page_height}px")

        await page.screenshot(path=f"{OUTPUT}/03-full-page.png", full_page=True)
        print("[6] Screenshot 03: Full page captured")

        # Hero section
        print("[7] Capturing Hero section...")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1.5)
        await page.screenshot(path=f"{OUTPUT}/04-hero-section.png", full_page=False)

        hero_data = await page.evaluate("""
            () => {
                const results = {};
                const h1s = document.querySelectorAll('h1, h2');
                results.headings = Array.from(h1s).slice(0, 6).map(h => ({
                    tag: h.tagName,
                    text: h.textContent.trim().substring(0, 80)
                }));
                const cd = document.querySelector('[class*="countdown"], [id*="countdown"], .timer, [class*="timer"]');
                results.hasCountdown = !!cd;
                results.countdownHtml = cd ? cd.outerHTML.substring(0, 300) : 'NOT FOUND';

                const ctaBtns = document.querySelectorAll('a[href*="awakening"]');
                results.awakeningCTAs = Array.from(ctaBtns).map(b => ({
                    text: b.textContent.trim().substring(0, 50),
                    href: b.getAttribute('href') || ''
                }));

                // Dots counter - any element with number + "spots" text
                const allText = document.body.innerHTML;
                results.has25Spots = allText.includes('25 Spots') || allText.includes('25 spots') || allText.includes('25 spot');
                results.hasDotsVisual = !!document.querySelector('[class*="dot-grid"], [class*="spots-grid"], [class*="dots"]');

                return results;
            }
        """)
        results['hero'] = hero_data
        print(f"    H1: {hero_data['headings'][0] if hero_data['headings'] else 'NONE'}")
        print(f"    Has countdown: {hero_data['hasCountdown']}")
        print(f"    Awakening CTAs: {hero_data['awakeningCTAs']}")
        print(f"    Has 25 spots text: {hero_data['has25Spots']}")

        # Feature cards section
        print("[8] Capturing Feature Cards section...")
        await page.evaluate("window.scrollTo(0, window.innerHeight * 1.2)")
        await asyncio.sleep(2)
        await page.screenshot(path=f"{OUTPUT}/05-feature-cards.png", full_page=False)

        cards_data = await page.evaluate("""
            () => {
                // Use classList.value (string) to avoid SVGAnimatedString issue
                const cards = document.querySelectorAll('[class*="card"], [class*="glass"], [class*="feature"]');
                const filtered = Array.from(cards).filter(c => {
                    const cls = (typeof c.className === 'string') ? c.className : (c.className.baseVal || '');
                    return cls.length > 0;
                });
                return filtered.slice(0, 12).map(c => {
                    const cls = (typeof c.className === 'string') ? c.className : (c.className.baseVal || '');
                    return {
                        classes: cls.substring(0, 80),
                        text: c.textContent.trim().substring(0, 80)
                    };
                });
            }
        """)
        results['cards'] = cards_data
        print(f"    Cards found: {len(cards_data)}")
        for c in cards_data[:5]:
            print(f"      [{c['classes'][:40]}]: {c['text'][:50]}")

        # Awakening experience section
        print("[9] Capturing Awakening Experience section...")
        await page.evaluate("window.scrollTo(0, window.innerHeight * 2.5)")
        await asyncio.sleep(2)
        await page.screenshot(path=f"{OUTPUT}/06-awakening-section.png", full_page=False)

        awakening_data = await page.evaluate("""
            () => {
                const results = {};
                const steps = document.querySelectorAll('[class*="step"], [class*="timeline"], [class*="process"]');
                results.stepCount = steps.length;
                results.stepTexts = Array.from(steps).slice(0, 8).map(s => s.textContent.trim().substring(0, 60));
                const chatMockup = document.querySelector('[class*="chat-mockup"], [class*="mockup"], [class*="demo-chat"]');
                results.hasChatMockup = !!chatMockup;
                results.chatMockupHtml = chatMockup ? chatMockup.outerHTML.substring(0, 300) : 'NOT FOUND';
                return results;
            }
        """)
        results['awakening'] = awakening_data
        print(f"    Steps found: {awakening_data['stepCount']}")
        print(f"    Step texts: {awakening_data['stepTexts']}")
        print(f"    Has chat mockup: {awakening_data['hasChatMockup']}")

        # Pricing section - multiple scroll positions
        print("[10] Capturing Pricing section...")
        for i, pct in enumerate([3, 3.5, 4, 4.5, 5]):
            await page.evaluate(f"window.scrollTo(0, window.innerHeight * {pct})")
            await asyncio.sleep(1.5)
            await page.screenshot(path=f"{OUTPUT}/07-pricing-{i+1}.png", full_page=False)
            print(f"    Pricing screenshot {i+1} at {pct}x viewport")

        pricing_data = await page.evaluate("""
            () => {
                const results = {};
                // Find pricing section
                const ps = document.querySelector('[class*="pricing"]');
                results.hasPricingSection = !!ps;

                // Find all tier cards - look for elements containing price text like $79
                const allEls = document.querySelectorAll('*');
                const priceEls = [];
                for (const el of allEls) {
                    if (el.children.length === 0 || el.children.length < 5) {
                        const txt = el.textContent.trim();
                        if ((txt.includes('$79') || txt.includes('$149') || txt.includes('$499') || txt.includes('$999')) && txt.length < 500) {
                            const cls = (typeof el.className === 'string') ? el.className : (el.className.baseVal || '');
                            if (!priceEls.some(p => p.text === txt)) {
                                priceEls.push({ text: txt.substring(0, 100), classes: cls.substring(0, 60) });
                            }
                        }
                    }
                }
                results.priceElements = priceEls.slice(0, 8);

                // Find recommended/highlighted card
                const highlighted = document.querySelectorAll('[class*="recommend"], [class*="popular"], [class*="featured"], [class*="highlight"]');
                results.highlightedClasses = Array.from(highlighted).map(h => {
                    const cls = (typeof h.className === 'string') ? h.className : '';
                    return { cls: cls.substring(0, 60), text: h.textContent.trim().substring(0, 80) };
                });

                // Bonded text presence
                const bodyText = document.body.textContent;
                results.hasBonded = bodyText.includes('Bonded');
                results.hasAwakened = bodyText.includes('Awakened');
                results.hasPartnered = bodyText.includes('Partnered');
                results.hasUnified = bodyText.includes('Unified');

                // CTA buttons pointing to awakening
                const ctaLinks = document.querySelectorAll('a[href*="awakening"]');
                results.ctaCount = ctaLinks.length;
                results.ctaLinks = Array.from(ctaLinks).map(a => ({
                    text: a.textContent.trim().substring(0, 40),
                    href: a.getAttribute('href')
                }));

                return results;
            }
        """)
        results['pricing'] = pricing_data
        print(f"    Has pricing section: {pricing_data['hasPricingSection']}")
        print(f"    Price elements: {pricing_data['priceElements']}")
        print(f"    Tiers - Awakened:{pricing_data['hasAwakened']} Bonded:{pricing_data['hasBonded']} Partnered:{pricing_data['hasPartnered']} Unified:{pricing_data['hasUnified']}")
        print(f"    Highlighted cards: {pricing_data['highlightedClasses']}")
        print(f"    CTA links ({pricing_data['ctaCount']}): {pricing_data['ctaLinks']}")

        # Testimonial section
        print("[11] Capturing Testimonial section...")
        await page.evaluate("window.scrollTo(0, window.innerHeight * 6)")
        await asyncio.sleep(2)
        await page.screenshot(path=f"{OUTPUT}/08-testimonial-area.png", full_page=False)

        testimonial_data = await page.evaluate("""
            () => {
                const results = {};
                const bodyText = document.body.textContent;
                results.hasMichael = bodyText.includes('Michael');
                results.hasHancock = bodyText.includes('Hancock');

                const tBlocks = document.querySelectorAll('[class*="testimonial"], blockquote, [class*="quote"]');
                results.testimonialBlockCount = tBlocks.length;
                results.testimonialTexts = Array.from(tBlocks).map(t => t.textContent.trim().substring(0, 150));

                return results;
            }
        """)
        results['testimonial'] = testimonial_data
        print(f"    Has Michael: {testimonial_data['hasMichael']}")
        print(f"    Has Hancock: {testimonial_data['hasHancock']}")
        print(f"    Testimonial blocks: {testimonial_data['testimonialBlockCount']}")
        print(f"    Testimonial texts: {testimonial_data['testimonialTexts'][:3]}")

        # Urgency section
        print("[12] Capturing Urgency/Scarcity section...")
        await page.evaluate("window.scrollTo(0, window.innerHeight * 7.5)")
        await asyncio.sleep(2)
        await page.screenshot(path=f"{OUTPUT}/09-urgency-section.png", full_page=False)

        # Final CTA
        print("[13] Capturing Final CTA + Jared signature...")
        await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        await asyncio.sleep(2)
        await page.screenshot(path=f"{OUTPUT}/10-final-cta-bottom.png", full_page=False)

        final_data = await page.evaluate("""
            () => {
                const bodyText = document.body.textContent;
                return {
                    hasJared: bodyText.includes('Jared'),
                    hasSanborn: bodyText.includes('Sanborn'),
                    lastChars: bodyText.trim().slice(-500)
                };
            }
        """)
        results['final_cta'] = final_data
        print(f"    Has Jared: {final_data['hasJared']}")
        print(f"    Has Sanborn: {final_data['hasSanborn']}")
        print(f"    Last 200 chars: {final_data['lastChars'][-200:]}")

        # Full CSS + brand color audit
        print("[14] Running brand color audit...")
        css_audit = await page.evaluate("""
            () => {
                const results = {};
                const bodyBg = window.getComputedStyle(document.body).backgroundColor;
                results.bodyBg = bodyBg;

                // Check for dark background near #0a0a0a
                // rgb(10,10,10) = #0a0a0a
                results.hasDarkBg = bodyBg.includes('10, 10, 10') || bodyBg.includes('0, 0, 0') || bodyBg.includes('rgba(0');

                // All stylesheets - find orange/blue mentions
                let cssText = '';
                try {
                    for (const sheet of document.styleSheets) {
                        try {
                            for (const rule of sheet.cssRules) {
                                if (rule.cssText && (rule.cssText.includes('#f1420b') || rule.cssText.includes('#2a93c1') || rule.cssText.includes('0a0a0a'))) {
                                    cssText += rule.cssText.substring(0, 100) + ' | ';
                                }
                            }
                        } catch(e) {}
                    }
                } catch(e) {}
                results.brandColorCSSRules = cssText.substring(0, 1000);

                // Countdown timer status
                const countdownNum = document.querySelector('.pb-countdown-item, [class*="countdown-item"], [class*="countdown"] span');
                results.countdownVisible = countdownNum ? countdownNum.textContent.trim() : 'NOT VISIBLE';

                // Check first hero CTA button href
                const firstCTABtn = document.querySelector('a[href*="awakening"]');
                results.firstCTAHref = firstCTABtn ? firstCTABtn.getAttribute('href') : 'NOT FOUND';

                // Check for any broken images (naturalWidth === 0)
                const imgs = document.querySelectorAll('img');
                const brokenImgs = Array.from(imgs).filter(img => img.naturalWidth === 0 && img.src);
                results.brokenImages = brokenImgs.map(img => img.src.substring(0, 100));
                results.totalImages = imgs.length;

                // Check for any console errors in page
                results.pageHasErrors = !!document.querySelector('[class*="error"], [class*="broken"], [data-error]');

                return results;
            }
        """)
        results['css_audit'] = css_audit
        print(f"    Body background: {css_audit['bodyBg']}")
        print(f"    Has dark bg: {css_audit['hasDarkBg']}")
        print(f"    Brand color CSS rules: {css_audit['brandColorCSSRules'][:200]}")
        print(f"    Countdown visible: {css_audit['countdownVisible']}")
        print(f"    First CTA href: {css_audit['firstCTAHref']}")
        print(f"    Total images: {css_audit['totalImages']}")
        print(f"    Broken images: {css_audit['brokenImages']}")

        # Full sweep screenshots at 10% intervals
        print("[15] Full page scroll sweep (10% intervals)...")
        for pct in range(0, 100, 10):
            scroll_pos = int(page_height * pct / 100)
            await page.evaluate(f"window.scrollTo(0, {scroll_pos})")
            await asyncio.sleep(1.2)
            await page.screenshot(path=f"{OUTPUT}/sweep-{pct:03d}pct.png", full_page=False)
            print(f"    Sweep {pct}% at {scroll_pos}px")

        # Console errors summary
        results['console_errors'] = console_errors
        print(f"\n[16] Console errors captured: {len(console_errors)}")
        for e in console_errors[:10]:
            print(f"    [{e['type']}] {e['text'][:100]}")

        # Page metadata
        meta = await page.evaluate("""
            () => ({
                title: document.title,
                url: window.location.href,
                scrollHeight: document.documentElement.scrollHeight,
                sectionCount: document.querySelectorAll('section').length,
                totalLinks: document.querySelectorAll('a').length,
                totalImages: document.querySelectorAll('img').length
            })
        """)
        results['meta'] = meta
        print(f"\n    Page title: {meta['title']}")
        print(f"    URL: {meta['url']}")
        print(f"    Page height: {meta['scrollHeight']}px")
        print(f"    Sections: {meta['sectionCount']}")
        print(f"    Total links: {meta['totalLinks']}")
        print(f"    Total images: {meta['totalImages']}")

        await browser.close()

    screenshot_list = sorted(os.listdir(OUTPUT))
    print(f"\n[DONE] Screenshots saved: {len(screenshot_list)}")
    print(f"       Directory: {OUTPUT}")

    return results


if __name__ == "__main__":
    data = asyncio.run(run_audit())
    print("\n=== FULL STRUCTURED DATA ===")
    print(json.dumps(data, indent=2, default=str))
