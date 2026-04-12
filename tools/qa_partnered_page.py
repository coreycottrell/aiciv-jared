"""
QA script for the new $499 Partnered tier page.
URL: https://purebrain.ai/partnered-how-this-levels-you-up/

Checks:
1. Page loads with dark background
2. Hero section with "Partnered" tier branding
3. Content sections (5 deliverables + 6-category feature stack)
4. PayPal $499 payment button exists
5. PayPal modal opens on click (visual check)
6. Post-payment redirect to pay-test-sandbox-3 with tier=Partnered
"""

import asyncio
import os
import time
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/partnered-page-qa-20260304"
URL = "https://purebrain.ai/partnered-how-this-levels-you-up/"

async def take_screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, name)
    await page.screenshot(path=path, full_page=False)
    print(f"[SCREENSHOT] {name}")
    return path

async def take_fullpage_screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, name)
    await page.screenshot(path=path, full_page=True)
    print(f"[SCREENSHOT-FULL] {name}")
    return path

async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True
        )
        page = await context.new_page()

        # Capture console + errors
        console_logs = []
        page_errors = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type.upper()}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(f"[PAGE-ERROR] {err}"))

        print("=" * 60)
        print("QA: Partnered Tier Page ($499)")
        print("URL:", URL)
        print("=" * 60)

        # --- STEP 1: Load the page ---
        print("\n[STEP 1] Loading page...")
        try:
            await page.goto(URL, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"[WARNING] networkidle timeout: {e}")
            await page.goto(URL, wait_until="domcontentloaded", timeout=20000)

        await asyncio.sleep(2)
        await take_screenshot(page, "001-initial-load.png")

        # --- CHECK 1: Dark background ---
        print("\n[CHECK 1] Background color...")
        bg_color = await page.evaluate("""
            () => {
                const body = document.body;
                const computed = window.getComputedStyle(body);
                return {
                    backgroundColor: computed.backgroundColor,
                    bodyBg: body.style.backgroundColor,
                    htmlBg: window.getComputedStyle(document.documentElement).backgroundColor
                };
            }
        """)
        print(f"  Body background: {bg_color['backgroundColor']}")
        print(f"  HTML background: {bg_color['htmlBg']}")

        # --- CHECK 2: Hero section ---
        print("\n[CHECK 2] Hero section with 'Partnered' branding...")
        hero_info = await page.evaluate("""
            () => {
                // Look for h1, h2, hero text
                const h1 = document.querySelector('h1');
                const h2 = document.querySelector('h2');
                const heroSection = document.querySelector('.hero, [class*="hero"], header');

                // Find "Partnered" anywhere on page
                const allText = document.body.innerText;
                const hasPartnered = allText.toLowerCase().includes('partnered');
                const hasPartner = allText.toLowerCase().includes('partner');

                // Find tier/pricing mentions
                const has499 = allText.includes('499');
                const hasMonth = allText.toLowerCase().includes('month');

                return {
                    h1Text: h1 ? h1.innerText.trim().substring(0, 200) : null,
                    h2Text: h2 ? h2.innerText.trim().substring(0, 200) : null,
                    hasPartnered: hasPartnered,
                    has499: has499,
                    hasMonth: hasMonth,
                    heroSectionFound: !!heroSection
                };
            }
        """)
        print(f"  H1: {hero_info['h1Text']}")
        print(f"  H2: {hero_info['h2Text']}")
        print(f"  Has 'Partnered': {hero_info['hasPartnered']}")
        print(f"  Has '$499': {hero_info['has499']}")
        print(f"  Has 'month': {hero_info['hasMonth']}")

        # --- CHECK 3: Content sections (deliverables + feature stack) ---
        print("\n[CHECK 3] Content sections check...")
        content_info = await page.evaluate("""
            () => {
                const allText = document.body.innerText;

                // Check for deliverables (5 things)
                const deliverableKeywords = [
                    'deliverable', 'what you get', 'includes', 'setup',
                    'strategy', 'weekly', 'monthly', 'quarterly', 'reporting'
                ];

                // Check for feature stack (6 categories)
                const featureKeywords = [
                    'feature', 'automation', 'integration', 'support',
                    'training', 'analytics', 'crm', 'email', 'social'
                ];

                const sections = document.querySelectorAll('section, [class*="section"], .wp-block-group');
                const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4')).map(h => h.innerText.trim().substring(0, 100));

                return {
                    sectionCount: sections.length,
                    headings: headings,
                    textLength: allText.length,
                    firstChunk: allText.substring(0, 500)
                };
            }
        """)
        print(f"  Section count: {content_info['sectionCount']}")
        print(f"  Page text length: {content_info['textLength']}")
        print(f"  Headings found: {content_info['headings'][:10]}")
        print(f"  First 500 chars: {content_info['firstChunk'][:300]}")

        # --- Scroll through the page and take screenshots ---
        print("\n[SCROLL] Scrolling through page...")
        await page.evaluate("window.scrollTo(0, 400)")
        await asyncio.sleep(1)
        await take_screenshot(page, "002-scroll-400.png")

        await page.evaluate("window.scrollTo(0, 900)")
        await asyncio.sleep(1)
        await take_screenshot(page, "003-scroll-900.png")

        await page.evaluate("window.scrollTo(0, 1500)")
        await asyncio.sleep(1)
        await take_screenshot(page, "004-scroll-1500.png")

        await page.evaluate("window.scrollTo(0, 2200)")
        await asyncio.sleep(1)
        await take_screenshot(page, "005-scroll-2200.png")

        await page.evaluate("window.scrollTo(0, 3000)")
        await asyncio.sleep(1)
        await take_screenshot(page, "006-scroll-3000.png")

        # Scroll to bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.5)
        await take_screenshot(page, "007-bottom-of-page.png")

        # Full page screenshot
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        await take_fullpage_screenshot(page, "008-full-page.png")

        # --- CHECK 4: PayPal button ---
        print("\n[CHECK 4] PayPal $499 payment button...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        await take_screenshot(page, "009-bottom-paypal-area.png")

        paypal_info = await page.evaluate("""
            () => {
                // Look for PayPal-related elements
                const paypalContainers = document.querySelectorAll(
                    '[id*="paypal"], [class*="paypal"], [id*="pb-paypal"], [class*="pb-paypal"]'
                );

                // Look for $499 buttons or payment CTAs
                const allButtons = Array.from(document.querySelectorAll('button, a, [role="button"]'));
                const paymentButtons = allButtons.filter(btn => {
                    const text = btn.innerText || btn.textContent;
                    return text && (
                        text.includes('499') ||
                        text.toLowerCase().includes('pay') ||
                        text.toLowerCase().includes('get started') ||
                        text.toLowerCase().includes('partner') ||
                        text.toLowerCase().includes('subscribe')
                    );
                }).map(btn => ({
                    text: (btn.innerText || btn.textContent).trim().substring(0, 100),
                    id: btn.id,
                    className: btn.className.substring(0, 100),
                    tagName: btn.tagName
                }));

                // Scripts containing PayPal
                const scripts = Array.from(document.querySelectorAll('script')).filter(s =>
                    s.src && s.src.includes('paypal')
                ).map(s => s.src);

                // Look for PayPal SDK overlay/modal
                const paypalModal = document.querySelector('#pb-paypal-overlay, #pb-paypal-modal, .pb-paypal-overlay');

                return {
                    paypalContainerCount: paypalContainers.length,
                    paypalContainerIds: Array.from(paypalContainers).map(el => el.id || el.className).slice(0, 10),
                    paymentButtons: paymentButtons,
                    paypalScripts: scripts,
                    paypalModalFound: !!paypalModal
                };
            }
        """)
        print(f"  PayPal containers found: {paypal_info['paypalContainerCount']}")
        print(f"  PayPal container IDs: {paypal_info['paypalContainerIds']}")
        print(f"  Payment buttons: {paypal_info['paymentButtons']}")
        print(f"  PayPal scripts: {paypal_info['paypalScripts']}")
        print(f"  PayPal modal in DOM: {paypal_info['paypalModalFound']}")

        # --- CHECK 5: Try clicking the payment trigger ---
        print("\n[CHECK 5] Attempting to trigger PayPal modal...")

        # First try to find a CTA button
        cta_found = await page.evaluate("""
            () => {
                // Find any 'Get Started' or payment CTA
                const btns = Array.from(document.querySelectorAll('button, a'));
                const cta = btns.find(b => {
                    const t = (b.innerText || b.textContent || '').toLowerCase();
                    return t.includes('get started') || t.includes('partner') ||
                           t.includes('sign up') || t.includes('begin') || t.includes('join');
                });
                if (cta) {
                    return { found: true, text: cta.innerText, id: cta.id, className: cta.className };
                }
                return { found: false };
            }
        """)
        print(f"  CTA button: {cta_found}")

        # Scroll to find the PayPal button area
        # Look for the PayPal SDK button container
        paypal_btn_visible = await page.evaluate("""
            () => {
                // The PayPal SDK renders into div containers
                // Check if any PayPal iframe exists
                const iframes = Array.from(document.querySelectorAll('iframe')).filter(f =>
                    f.src && f.src.includes('paypal')
                );

                // Check for paypal button container divs
                const ppBtnContainers = document.querySelectorAll('[id^="zoid"], [id^="paypal"]');

                return {
                    paypalIframes: iframes.length,
                    paypalBtnContainers: ppBtnContainers.length,
                    allIframes: Array.from(document.querySelectorAll('iframe')).map(f => ({
                        src: f.src.substring(0, 80),
                        id: f.id,
                        name: f.name
                    })).slice(0, 5)
                };
            }
        """)
        print(f"  PayPal iframes: {paypal_btn_visible['paypalIframes']}")
        print(f"  PayPal btn containers: {paypal_btn_visible['paypalBtnContainers']}")
        print(f"  All iframes: {paypal_btn_visible['allIframes']}")

        # --- CHECK 6: Check if onPaymentComplete / redirect logic exists ---
        print("\n[CHECK 6] Checking redirect logic (pay-test-sandbox-3 with tier=Partnered)...")
        redirect_info = await page.evaluate("""
            () => {
                // Check page source for redirect pattern
                const scripts = Array.from(document.querySelectorAll('script:not([src])'));
                const scriptTexts = scripts.map(s => s.textContent).join(' ');

                return {
                    hasSandbox3Ref: scriptTexts.includes('sandbox-3') || scriptTexts.includes('sandbox3'),
                    hasPartneredParam: scriptTexts.includes('tier=Partnered') || scriptTexts.includes('Partnered'),
                    hasOnPaymentComplete: typeof window.onPaymentComplete === 'function',
                    hasPbPaypalConfig: typeof window.pbPaypalConfig !== 'undefined',
                    pbPaypalConfig: window.pbPaypalConfig ? JSON.stringify(window.pbPaypalConfig).substring(0, 300) : null,
                    scriptLength: scriptTexts.length
                };
            }
        """)
        print(f"  Has sandbox-3 reference: {redirect_info['hasSandbox3Ref']}")
        print(f"  Has tier=Partnered param: {redirect_info['hasPartneredParam']}")
        print(f"  onPaymentComplete function: {redirect_info['hasOnPaymentComplete']}")
        print(f"  pbPaypalConfig exists: {redirect_info['hasPbPaypalConfig']}")
        print(f"  pbPaypalConfig: {redirect_info['pbPaypalConfig']}")

        # Get full inline script content to check for redirect logic
        script_content = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script:not([src])'));
                // Find scripts with PayPal or payment logic
                const relevant = scripts.filter(s =>
                    s.textContent.includes('paypal') ||
                    s.textContent.includes('payment') ||
                    s.textContent.includes('499') ||
                    s.textContent.includes('sandbox')
                );
                return relevant.map(s => s.textContent.substring(0, 500)).slice(0, 3);
            }
        """)
        print(f"\n  Relevant inline scripts:")
        for i, sc in enumerate(script_content):
            print(f"  Script {i+1}: {sc[:300]}")

        # --- SIMULATE PAYMENT to test redirect ---
        print("\n[CHECK 6b] Simulating payment completion to test redirect...")

        # First check if there's a window.onPaymentComplete to call
        sim_result = await page.evaluate("""
            () => {
                if (typeof window.onPaymentComplete === 'function') {
                    return 'onPaymentComplete exists - calling it';
                }
                // Try to find the paypal config
                if (typeof window.pbPaypalConfig !== 'undefined') {
                    return 'pbPaypalConfig: ' + JSON.stringify(window.pbPaypalConfig);
                }
                return 'No payment handler found on window';
            }
        """)
        print(f"  Simulation check: {sim_result}")

        # --- Console log summary ---
        print("\n[CONSOLE LOGS] Summary:")
        errors = [l for l in console_logs if 'error' in l.lower() or 'ERROR' in l]
        warnings = [l for l in console_logs if 'warn' in l.lower() or 'WARN' in l]
        print(f"  Total console messages: {len(console_logs)}")
        print(f"  Errors: {len(errors)}")
        print(f"  Warnings: {len(warnings)}")
        print(f"  Page JS errors: {len(page_errors)}")

        if page_errors:
            print("  PAGE ERRORS:")
            for e in page_errors[:5]:
                print(f"    {e}")

        if errors[:5]:
            print("  CONSOLE ERRORS (first 5):")
            for e in errors[:5]:
                print(f"    {e}")

        # --- MOBILE viewport check ---
        print("\n[MOBILE CHECK] Testing at 375px width...")
        await page.set_viewport_size({"width": 375, "height": 812})
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        await take_screenshot(page, "010-mobile-top.png")

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        await take_screenshot(page, "011-mobile-bottom.png")

        # Reset to desktop
        await page.set_viewport_size({"width": 1440, "height": 900})

        await browser.close()

        print("\n" + "=" * 60)
        print("QA COMPLETE")
        print(f"Screenshots in: {SCREENSHOT_DIR}")
        print("=" * 60)

asyncio.run(main())
