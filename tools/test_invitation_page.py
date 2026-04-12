"""
Invitation Page Visual Audit
URL: https://purebrain.ai/invitation/
Password: purebrain25

Tests all 7 major sections visually with screenshots.
"""

import asyncio
import os
from playwright.async_api import async_playwright

OUTPUT = "/home/jared/projects/AI-CIV/aether/exports/screenshots/invitation-audit-2026-02-26"
os.makedirs(OUTPUT, exist_ok=True)

TARGET_URL = "https://purebrain.ai/invitation/"
PASSWORD = "purebrain25"


async def run_audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page(
            viewport={"width": 1440, "height": 900}
        )

        print("[1] Navigating to invitation page...")
        resp = await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        print(f"    Status: {resp.status} - {page.url}")
        await asyncio.sleep(3)

        # Screenshot 01: Password form
        await page.screenshot(
            path=f"{OUTPUT}/01-password-form.png",
            full_page=False
        )
        print("[2] Screenshot 01: Password form captured")

        # Check if password form is present
        pw_input = page.locator("input[type='password']")
        pw_count = await pw_input.count()
        print(f"    Password inputs found: {pw_count}")

        if pw_count > 0:
            print("[3] Entering password...")
            await pw_input.first.fill(PASSWORD)
            await asyncio.sleep(0.5)

            # Submit the password form
            submit_btn = page.locator("input[type='submit']")
            submit_count = await submit_btn.count()
            print(f"    Submit buttons found: {submit_count}")

            if submit_count > 0:
                await submit_btn.first.click()
            else:
                await page.keyboard.press("Enter")

            print("[4] Waiting for page to load after password...")
            await asyncio.sleep(10)  # Elementor pages need time

            # Screenshot 02: After password - full page
            await page.screenshot(
                path=f"{OUTPUT}/02-after-password-viewport.png",
                full_page=False
            )
            print("[5] Screenshot 02: Post-password viewport captured")
        else:
            print("[3] No password form found - page may already be unlocked or has different structure")
            # Check what's on the page
            title = await page.title()
            print(f"    Page title: {title}")

        # Get full page height
        page_height = await page.evaluate("document.documentElement.scrollHeight")
        print(f"[6] Full page height: {page_height}px")

        # Screenshot 03: Full page
        await page.screenshot(
            path=f"{OUTPUT}/03-full-page.png",
            full_page=True
        )
        print("[7] Screenshot 03: Full page captured")

        # --- SECTION-BY-SECTION SCREENSHOTS ---

        # Section 1: Hero section
        print("[8] Capturing Hero section...")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1.5)
        await page.screenshot(
            path=f"{OUTPUT}/04-hero-section.png",
            full_page=False
        )

        # Check for hero elements
        hero_elements = await page.evaluate("""
            () => {
                const results = {};
                // Check for headline
                const h1s = document.querySelectorAll('h1, h2');
                results.headings = Array.from(h1s).slice(0, 5).map(h => ({
                    tag: h.tagName,
                    text: h.textContent.trim().substring(0, 80)
                }));
                // Check for countdown
                results.hasCountdown = !!document.querySelector('[class*="countdown"], [id*="countdown"], .timer, [class*="timer"]');
                results.countdownHTML = document.querySelector('[class*="countdown"], [id*="countdown"], .timer, [class*="timer"]')?.outerHTML?.substring(0, 200) || 'NOT FOUND';
                // Check for CTA button
                const ctaBtns = document.querySelectorAll('a[href*="awakening"], a[href*="#awakening"], .cta-btn, [class*="cta"]');
                results.ctaButtons = Array.from(ctaBtns).slice(0, 5).map(b => ({
                    text: b.textContent.trim().substring(0, 60),
                    href: b.getAttribute('href') || ''
                }));
                // Check for dots counter
                results.hasDotsCounter = !!document.querySelector('[class*="dot"], [class*="spot"], [class*="counter"]');
                results.dotsCounterHTML = document.querySelector('[class*="dot"], [class*="spot"], [class*="counter"]')?.outerHTML?.substring(0, 300) || 'NOT FOUND';
                return results;
            }
        """)
        print(f"    Headings found: {hero_elements['headings']}")
        print(f"    Has countdown: {hero_elements['hasCountdown']}")
        print(f"    Countdown HTML: {hero_elements['countdownHTML'][:100]}")
        print(f"    CTA buttons: {hero_elements['ctaButtons']}")
        print(f"    Has dots counter: {hero_elements['hasDotsCounter']}")

        # Section 2: Feature cards (scroll down ~100vh)
        print("[9] Capturing Feature Cards section...")
        await page.evaluate("window.scrollTo(0, window.innerHeight * 1.2)")
        await asyncio.sleep(2)
        await page.screenshot(
            path=f"{OUTPUT}/05-feature-cards.png",
            full_page=False
        )

        # Check for glassmorphism cards
        cards_info = await page.evaluate("""
            () => {
                const cards = document.querySelectorAll('[class*="card"], [class*="glass"], [class*="feature"]');
                return Array.from(cards).slice(0, 10).map(c => ({
                    classes: c.className.substring(0, 80),
                    text: c.textContent.trim().substring(0, 60)
                }));
            }
        """)
        print(f"    Cards found: {len(cards_info)}")
        for c in cards_info[:5]:
            print(f"      - {c['classes']}: {c['text'][:40]}")

        # Section 3: Awakening experience (scroll down ~200vh)
        print("[10] Capturing Awakening Experience section...")
        await page.evaluate("window.scrollTo(0, window.innerHeight * 2.5)")
        await asyncio.sleep(2)
        await page.screenshot(
            path=f"{OUTPUT}/06-awakening-section.png",
            full_page=False
        )

        # Check for timeline and chat mockup
        timeline_info = await page.evaluate("""
            () => {
                const results = {};
                results.hasTimeline = !!document.querySelector('[class*="timeline"], [class*="step"], [class*="process"]');
                const timeline = document.querySelector('[class*="timeline"], [class*="step"], [class*="process"]');
                results.timelineHTML = timeline?.outerHTML?.substring(0, 400) || 'NOT FOUND';
                results.hasChatMockup = !!document.querySelector('[class*="chat"], [class*="mockup"], [class*="conversation"]');
                return results;
            }
        """)
        print(f"    Has timeline: {timeline_info['hasTimeline']}")
        print(f"    Has chat mockup: {timeline_info['hasChatMockup']}")

        # Section 4: Pricing section (scroll to ~400vh area)
        print("[11] Capturing Pricing section...")
        await page.evaluate("window.scrollTo(0, window.innerHeight * 4)")
        await asyncio.sleep(2)
        await page.screenshot(
            path=f"{OUTPUT}/07-pricing-area-1.png",
            full_page=False
        )

        # Try scrolling more to find pricing
        await page.evaluate("window.scrollTo(0, window.innerHeight * 5)")
        await asyncio.sleep(1.5)
        await page.screenshot(
            path=f"{OUTPUT}/08-pricing-area-2.png",
            full_page=False
        )

        # Check for pricing cards
        pricing_info = await page.evaluate("""
            () => {
                const results = {};
                // Look for pricing section
                const pricingSection = document.querySelector('[class*="pricing"], #pricing');
                results.hasPricingSection = !!pricingSection;
                // Look for tier cards
                const tiers = document.querySelectorAll('[class*="pricing-card"], [class*="tier"], [class*="plan"]');
                results.tierCount = tiers.length;
                results.tiers = Array.from(tiers).map(t => ({
                    classes: t.className.substring(0, 80),
                    text: t.textContent.trim().substring(0, 100)
                }));
                // Look for "Bonded" or "recommended" highlight
                const allElements = document.querySelectorAll('[class*="recommend"], [class*="popular"], [class*="highlight"], [class*="featured"]');
                results.highlightedCard = Array.from(allElements).map(e => e.textContent.trim().substring(0, 80));
                // Check CTA button hrefs
                const ctaBtns = document.querySelectorAll('[class*="pricing"] a, [class*="tier"] a, [class*="plan"] a');
                results.ctaHrefs = Array.from(ctaBtns).slice(0, 8).map(b => ({
                    text: b.textContent.trim().substring(0, 40),
                    href: b.getAttribute('href') || ''
                }));
                return results;
            }
        """)
        print(f"    Has pricing section: {pricing_info['hasPricingSection']}")
        print(f"    Tier count: {pricing_info['tierCount']}")
        print(f"    Tiers: {pricing_info['tiers'][:4]}")
        print(f"    Highlighted cards: {pricing_info['highlightedCard']}")
        print(f"    CTA hrefs: {pricing_info['ctaHrefs']}")

        # Section 5: Testimonial section
        print("[12] Capturing Testimonial section...")
        await page.evaluate("window.scrollTo(0, window.innerHeight * 6)")
        await asyncio.sleep(2)
        await page.screenshot(
            path=f"{OUTPUT}/09-testimonial-area.png",
            full_page=False
        )

        # Check for Michael Hancock testimonial
        testimonial_info = await page.evaluate("""
            () => {
                const results = {};
                const testimonials = document.querySelectorAll('[class*="testimonial"], blockquote, [class*="review"]');
                results.testimonialCount = testimonials.length;
                results.testimonials = Array.from(testimonials).map(t => t.textContent.trim().substring(0, 120));
                // Search for "Michael" or "Hancock"
                const allText = document.body.textContent;
                results.hasMichaelHancock = allText.includes('Michael') && allText.includes('Hancock');
                results.hasMichael = allText.includes('Michael');
                return results;
            }
        """)
        print(f"    Testimonial count: {testimonial_info['testimonialCount']}")
        print(f"    Has Michael Hancock: {testimonial_info['hasMichaelHancock']}")
        print(f"    Testimonials preview: {testimonial_info['testimonials'][:3]}")

        # Section 6: Urgency/scarcity section
        print("[13] Capturing Urgency/Scarcity section...")
        await page.evaluate("window.scrollTo(0, window.innerHeight * 7.5)")
        await asyncio.sleep(2)
        await page.screenshot(
            path=f"{OUTPUT}/10-urgency-section.png",
            full_page=False
        )

        # Section 7: Final CTA and Jared signature
        print("[14] Capturing Final CTA section...")
        await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        await asyncio.sleep(2)
        await page.screenshot(
            path=f"{OUTPUT}/11-final-cta-section.png",
            full_page=False
        )

        # Check for Jared signature
        jared_info = await page.evaluate("""
            () => {
                const results = {};
                const allText = document.body.textContent;
                results.hasJaredSignature = allText.includes('Jared') || allText.includes('Sanborn');
                // Get last 500 chars of visible text for context
                const paras = document.querySelectorAll('p, h1, h2, h3, h4, span');
                const visibleText = Array.from(paras)
                    .map(p => p.textContent.trim())
                    .filter(t => t.length > 10)
                    .slice(-20)
                    .join(' | ');
                results.bottomText = visibleText.substring(0, 500);
                return results;
            }
        """)
        print(f"    Has Jared signature: {jared_info['hasJaredSignature']}")
        print(f"    Bottom text: {jared_info['bottomText'][:200]}")

        # --- BRAND COLOR + CSS AUDIT ---
        print("[15] Running brand color and CSS audit...")
        css_audit = await page.evaluate("""
            () => {
                const results = {};
                // Check computed styles for key elements
                const body = document.body;
                const computedBody = window.getComputedStyle(body);
                results.bodyBg = computedBody.backgroundColor;
                // Check for orange color occurrences in inline styles
                const allElements = document.querySelectorAll('[style*="f1420b"], [style*="2a93c1"], [style*="orange"], [style*="blue"]');
                results.brandColorElements = allElements.length;
                // Check for countdown timer specifically
                const countdownEls = document.querySelectorAll('[class*="countdown"]');
                results.countdownElements = Array.from(countdownEls).map(e => ({
                    class: e.className.substring(0, 60),
                    html: e.outerHTML.substring(0, 300)
                }));
                // Check all hrefs pointing to #awakening
                const awakeningLinks = document.querySelectorAll('a[href*="awakening"]');
                results.awakeningLinks = Array.from(awakeningLinks).map(a => ({
                    text: a.textContent.trim().substring(0, 50),
                    href: a.getAttribute('href')
                }));
                // Check for any broken image srcs
                const imgs = document.querySelectorAll('img');
                results.images = Array.from(imgs).slice(0, 10).map(img => ({
                    src: img.src ? img.src.substring(0, 80) : 'no src',
                    alt: img.alt || 'no alt',
                    naturalWidth: img.naturalWidth,
                    naturalHeight: img.naturalHeight
                }));
                return results;
            }
        """)
        print(f"    Body background: {css_audit['bodyBg']}")
        print(f"    Brand color elements: {css_audit['brandColorElements']}")
        print(f"    Countdown elements: {css_audit['countdownElements'][:3]}")
        print(f"    Awakening links: {css_audit['awakeningLinks'][:8]}")
        print(f"    Images (first 5): {css_audit['images'][:5]}")

        # --- CONSOLE LOGS ---
        print("[16] Checking console logs...")
        # Navigate back to top to capture console from full load
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # --- FINAL METADATA ---
        page_info = await page.evaluate("""
            () => ({
                title: document.title,
                url: window.location.href,
                scrollHeight: document.documentElement.scrollHeight,
                sections: Array.from(document.querySelectorAll('section, [class*="section"]')).length
            })
        """)
        print(f"\n    Page title: {page_info['title']}")
        print(f"    Final URL: {page_info['url']}")
        print(f"    Page height: {page_info['scrollHeight']}px")
        print(f"    Sections found: {page_info['sections']}")

        # Middle sections - scroll at intervals to find all content
        print("[17] Capturing middle page sections (scroll sweep)...")
        vh = 900  # viewport height
        scroll_positions = [
            (int(page_info['scrollHeight'] * 0.15), "15pct"),
            (int(page_info['scrollHeight'] * 0.30), "30pct"),
            (int(page_info['scrollHeight'] * 0.45), "45pct"),
            (int(page_info['scrollHeight'] * 0.60), "60pct"),
            (int(page_info['scrollHeight'] * 0.75), "75pct"),
            (int(page_info['scrollHeight'] * 0.90), "90pct"),
        ]
        for pos, label in scroll_positions:
            await page.evaluate(f"window.scrollTo(0, {pos})")
            await asyncio.sleep(1.5)
            await page.screenshot(
                path=f"{OUTPUT}/sweep-{label}.png",
                full_page=False
            )
            print(f"    Captured sweep at {label} ({pos}px)")

        await browser.close()

        print(f"\n[DONE] All screenshots saved to: {OUTPUT}")
        print(f"       Total screenshots: {len(os.listdir(OUTPUT))}")

        # Return structured data for analysis
        return {
            "page_info": page_info,
            "hero_elements": hero_elements,
            "cards_info": cards_info,
            "timeline_info": timeline_info,
            "pricing_info": pricing_info,
            "testimonial_info": testimonial_info,
            "jared_info": jared_info,
            "css_audit": css_audit,
        }


if __name__ == "__main__":
    data = asyncio.run(run_audit())
    print("\n=== STRUCTURED DATA SUMMARY ===")
    import json
    print(json.dumps(data, indent=2, default=str))
