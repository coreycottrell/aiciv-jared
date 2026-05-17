"""
QA script for sandbox-3 pay test page.
Checks: dark bg, pricing tiers, "How This Levels You Up" links, PayPal modal, chatbox.
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

URL = "https://purebrain.ai/pay-test-sandbox-3/"
PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-qa-20260304")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

results = {}
screenshots = []

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()

        console_logs = []
        page_errors = []

        page.on("console", lambda msg: console_logs.append(f"[{msg.type.upper()}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # ---- Step 1: Navigate (triggers password protection) ----
        print("Navigating to sandbox-3...")
        await page.goto(URL, wait_until="domcontentloaded")
        await asyncio.sleep(2)

        # Check if password form is present
        pw_input = await page.query_selector('input[type="password"]')
        if pw_input:
            print("Password form detected - entering password...")
            await pw_input.fill(PASSWORD)
            submit = await page.query_selector('input[type="submit"], button[type="submit"]')
            if submit:
                await submit.click()
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(3)
            else:
                await pw_input.press("Enter")
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(3)
        else:
            print("No password form - page may be open or already authenticated")
            await asyncio.sleep(3)

        # ---- Step 2: Screenshot initial page load ----
        ss_path = SCREENSHOT_DIR / "01_initial_load.png"
        await page.screenshot(path=str(ss_path), full_page=False)
        screenshots.append(str(ss_path))
        print(f"Screenshot: {ss_path}")

        # ---- Step 3: Check background color ----
        bg_color = await page.evaluate("""
            () => {
                const body = document.body;
                return window.getComputedStyle(body).backgroundColor;
            }
        """)
        print(f"Body background: {bg_color}")
        results["dark_background"] = bg_color

        # ---- Step 4: Reveal pricing section ----
        print("Attempting to reveal pricing section...")
        reveal_result = await page.evaluate("""
            () => {
                // Try various reveal functions
                if (typeof window.showPricing === 'function') {
                    window.showPricing();
                    return 'showPricing() called';
                } else if (typeof window.revealPricing === 'function') {
                    window.revealPricing();
                    return 'revealPricing() called';
                } else if (typeof window.closeCelebrationAndShowPricing === 'function') {
                    window.closeCelebrationAndShowPricing();
                    return 'closeCelebrationAndShowPricing() called';
                } else {
                    // Force pricing visible
                    const pricing = document.querySelector('#pricing');
                    if (pricing) {
                        pricing.style.display = 'block';
                        pricing.style.visibility = 'visible';
                        pricing.style.opacity = '1';
                        return 'forced #pricing visible';
                    }
                    return 'no pricing element found';
                }
            }
        """)
        print(f"Pricing reveal: {reveal_result}")
        await asyncio.sleep(2)

        # Scroll to pricing section
        await page.evaluate("""
            () => {
                const el = document.querySelector('#pricing, .pricing-section, [class*="pricing"]');
                if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
                else window.scrollTo(0, document.body.scrollHeight / 2);
            }
        """)
        await asyncio.sleep(1.5)

        ss_path = SCREENSHOT_DIR / "02_pricing_section.png"
        await page.screenshot(path=str(ss_path), full_page=False)
        screenshots.append(str(ss_path))
        print(f"Screenshot: {ss_path}")

        # ---- Step 5: Check pricing tiers ----
        page_text = await page.evaluate("() => document.body.innerText")

        tier_checks = {
            "Awakened_$297": "$297" in page_text and "Awakened" in page_text,
            "Partnered_$499": "$499" in page_text and "Partnered" in page_text,
            "Unified_$999": "$999" in page_text and "Unified" in page_text,
        }
        print(f"Tier checks: {tier_checks}")
        results["tiers"] = tier_checks

        # ---- Step 6: Check "How This Levels You Up" links ----
        levels_up_links = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a'));
                return links
                    .filter(a => a.textContent && a.textContent.includes('How This Levels You Up'))
                    .map(a => ({ text: a.textContent.trim(), href: a.href }));
            }
        """)
        print(f"How This Levels You Up links: {json.dumps(levels_up_links, indent=2)}")
        results["levels_up_links"] = levels_up_links

        # Also check by text content (in case it's slightly different)
        all_links = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a'));
                return links
                    .filter(a => a.textContent && (
                        a.textContent.includes('Level') ||
                        a.textContent.includes('level') ||
                        a.href.includes('levels-you-up') ||
                        a.href.includes('partnered-how') ||
                        a.href.includes('unified-how')
                    ))
                    .map(a => ({ text: a.textContent.trim(), href: a.href }));
            }
        """)
        print(f"Related links found: {json.dumps(all_links, indent=2)}")
        results["related_links"] = all_links

        # Screenshot after scrolling down to find the specific buttons area
        # First find the $499 button area
        await page.evaluate("""
            () => {
                // Find the Partnered tier card
                const allText = Array.from(document.querySelectorAll('*'));
                for (const el of allText) {
                    if (el.children.length === 0 && el.textContent && el.textContent.includes('$499')) {
                        el.scrollIntoView({ behavior: 'instant', block: 'center' });
                        break;
                    }
                }
            }
        """)
        await asyncio.sleep(1)
        ss_path = SCREENSHOT_DIR / "03_partnered_tier_area.png"
        await page.screenshot(path=str(ss_path), full_page=False)
        screenshots.append(str(ss_path))
        print(f"Screenshot: {ss_path}")

        # Scroll to $999 Unified tier
        await page.evaluate("""
            () => {
                const allText = Array.from(document.querySelectorAll('*'));
                for (const el of allText) {
                    if (el.children.length === 0 && el.textContent && el.textContent.includes('$999')) {
                        el.scrollIntoView({ behavior: 'instant', block: 'center' });
                        break;
                    }
                }
            }
        """)
        await asyncio.sleep(1)
        ss_path = SCREENSHOT_DIR / "04_unified_tier_area.png"
        await page.screenshot(path=str(ss_path), full_page=False)
        screenshots.append(str(ss_path))
        print(f"Screenshot: {ss_path}")

        # Full page screenshot of pricing
        ss_path = SCREENSHOT_DIR / "05_pricing_fullpage.png"
        await page.screenshot(path=str(ss_path), full_page=True)
        screenshots.append(str(ss_path))
        print(f"Screenshot: {ss_path}")

        # ---- Step 7: Check PayPal $499 modal ----
        print("Looking for $499 PayPal button...")
        # Scroll back to pricing to find the button
        await page.evaluate("""
            () => {
                const el = document.querySelector('#pricing, .pricing-section');
                if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
            }
        """)
        await asyncio.sleep(1)

        # Find the $499 CTA button
        paypal_499_found = await page.evaluate("""
            () => {
                // Look for PayPal buttons in the $499 card
                const buttons = Array.from(document.querySelectorAll('button, a, [id*="paypal"], [class*="paypal"]'));
                const pricingCards = Array.from(document.querySelectorAll('.pricing-card, [class*="pricing"], [class*="tier"]'));

                // Check DOM for PayPal button containers
                const paypalDivs = document.querySelectorAll('[id*="paypal-button"]');
                return {
                    paypalDivCount: paypalDivs.length,
                    paypalDivIds: Array.from(paypalDivs).map(d => d.id),
                    pricingCardCount: pricingCards.length
                };
            }
        """)
        print(f"PayPal button info: {json.dumps(paypal_499_found, indent=2)}")
        results["paypal_buttons"] = paypal_499_found

        # ---- Step 8: Check chatbox ----
        chatbox_check = await page.evaluate("""
            () => {
                const chatbox = document.querySelector('#chatbox, .chatbox, [id*="chat"], [class*="chatbox"]');
                const payTestArea = document.querySelector('#pay-test-area, .pay-test, [id*="pay-test"]');
                return {
                    chatbox_found: !!chatbox,
                    chatbox_id: chatbox ? chatbox.id : null,
                    chatbox_class: chatbox ? chatbox.className : null,
                    pay_test_area: !!payTestArea
                };
            }
        """)
        print(f"Chatbox check: {json.dumps(chatbox_check, indent=2)}")
        results["chatbox"] = chatbox_check

        # ---- Step 9: Full DOM dump for manual inspection ----
        # Check what's around the pricing section more carefully
        pricing_html = await page.evaluate("""
            () => {
                const pricing = document.querySelector('#pricing');
                if (pricing) {
                    return pricing.innerHTML.substring(0, 5000);
                }
                return 'No #pricing element found';
            }
        """)

        # Save pricing HTML to file for inspection
        with open(str(SCREENSHOT_DIR / "pricing_html_dump.txt"), "w") as f:
            f.write(pricing_html)
        print(f"Pricing HTML saved (first 5000 chars)")
        print(f"Pricing HTML preview: {pricing_html[:500]}")

        # ---- Step 10: Try clicking $499 CTA button ----
        print("Looking for $499 tier CTA button to test modal...")

        # Try to find and click the $499 button
        button_click_result = await page.evaluate("""
            () => {
                // Find the pricing card containing $499
                const cards = document.querySelectorAll('.pricing-card, [class*="pricing-card"], [class*="tier-card"]');
                let partneredCard = null;

                for (const card of cards) {
                    if (card.textContent.includes('499') || card.textContent.includes('Partnered')) {
                        partneredCard = card;
                        break;
                    }
                }

                if (!partneredCard) {
                    // Try finding any element with $499 text
                    return { error: 'No partnered card found', cardCount: cards.length };
                }

                const btn = partneredCard.querySelector('button, a[href*="paypal"], [class*="btn"], [class*="cta"]');
                if (btn) {
                    return { found: true, btnText: btn.textContent.trim(), btnTag: btn.tagName };
                }
                return { found: false, cardFound: true, cardText: partneredCard.textContent.substring(0, 200) };
            }
        """)
        print(f"Button search: {json.dumps(button_click_result, indent=2)}")
        results["button_search"] = button_click_result

        # Screenshot final state
        ss_path = SCREENSHOT_DIR / "06_final_state.png"
        await page.screenshot(path=str(ss_path), full_page=False)
        screenshots.append(str(ss_path))

        # ---- Collect console logs and errors ----
        results["console_logs"] = console_logs[:20]
        results["page_errors"] = page_errors[:10]
        results["screenshots"] = screenshots

        await browser.close()

    # Print summary
    print("\n" + "="*60)
    print("QA RESULTS SUMMARY")
    print("="*60)
    print(json.dumps(results, indent=2, default=str))

    # Save results
    with open(str(SCREENSHOT_DIR / "qa_results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nAll screenshots saved to: {SCREENSHOT_DIR}")
    print("Results saved to qa_results.json")

asyncio.run(main())
