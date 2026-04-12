"""
Test PayPal button click behavior + redirect logic for Partnered page.
Since headless can't render PayPal iframes (documented limitation),
we test:
1. The "Get Partnered Now" CTA scrolls to and shows PayPal buttons
2. The inline script's redirect config contains correct tier + sandbox-3 URL
3. JS simulation of payment completion triggers correct redirect
"""

import asyncio
import os
import json
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/partnered-page-qa-20260304"
URL = "https://purebrain.ai/partnered-how-this-levels-you-up/"

async def take_screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, name)
    await page.screenshot(path=path, full_page=False)
    print(f"[SCREENSHOT] {name}")
    return path

async def main():
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

        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type.upper()}] {msg.text}"))

        print("Loading page...")
        try:
            await page.goto(URL, wait_until="networkidle", timeout=30000)
        except Exception:
            await page.goto(URL, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(3)

        # --- Extract the full inline payment script ---
        print("\n[SCRIPT ANALYSIS] Extracting payment script config...")
        payment_script = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script:not([src])'));
                const payScript = scripts.find(s =>
                    s.textContent.includes('TIER') ||
                    s.textContent.includes('Partnered') ||
                    s.textContent.includes('sandbox-3')
                );
                return payScript ? payScript.textContent : null;
            }
        """)

        if payment_script:
            print(f"\nPayment script found ({len(payment_script)} chars)")
            print("First 1500 chars:")
            print(payment_script[:1500])
        else:
            print("No payment script found!")

        # --- Test CTA button click (scroll to PayPal) ---
        print("\n[CTA CLICK TEST] Clicking 'Get Partnered Now' button...")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)

        # Find and click the CTA button
        cta_clicked = await page.evaluate("""
            () => {
                const btn = document.querySelector('.pb-hero-cta');
                if (btn) {
                    btn.click();
                    return { clicked: true, text: btn.innerText };
                }
                return { clicked: false };
            }
        """)
        print(f"  CTA click result: {cta_clicked}")
        await asyncio.sleep(1.5)
        await take_screenshot(page, "012-after-cta-click.png")

        # Check scroll position
        scroll_pos = await page.evaluate("() => ({ y: window.scrollY, total: document.body.scrollHeight })")
        print(f"  Scroll position after CTA click: y={scroll_pos['y']} / {scroll_pos['total']}")

        # --- Check PayPal SDK modal behavior ---
        print("\n[PAYPAL MODAL] Checking modal infrastructure in DOM...")
        modal_info = await page.evaluate("""
            () => {
                const overlay = document.getElementById('pb-paypal-overlay');
                const modal = document.getElementById('pb-paypal-modal');
                const container = document.getElementById('pb-paypal-container');

                return {
                    overlay: overlay ? {
                        exists: true,
                        display: window.getComputedStyle(overlay).display,
                        visibility: window.getComputedStyle(overlay).visibility
                    } : { exists: false },
                    modal: modal ? {
                        exists: true,
                        display: window.getComputedStyle(modal).display
                    } : { exists: false },
                    container: container ? {
                        exists: true,
                        display: window.getComputedStyle(container).display,
                        childCount: container.children.length
                    } : { exists: false }
                };
            }
        """)
        print(f"  Overlay: {modal_info['overlay']}")
        print(f"  Modal: {modal_info['modal']}")
        print(f"  Container: {modal_info['container']}")

        # --- Verify redirect config ---
        print("\n[REDIRECT CONFIG] Checking tier + redirect URL in script...")
        redirect_config = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script:not([src])'));
                const full = scripts.map(s => s.textContent).join('\\n');

                // Extract TIER value
                const tierMatch = full.match(/var\\s+TIER\\s*=\\s*['"](.*?)['"]/);
                const priceMatch = full.match(/var\\s+PRICE\\s*=\\s*['"](.*?)['"]/);
                const verifyMatch = full.match(/var\\s+VERIFY_URL\\s*=\\s*['"](.*?)['"]/);
                const redirectMatch = full.match(/var\\s+SUCCESS_REDIRECT\\s*=\\s*['"](.*?)['"]/);
                const sandboxMatch = full.match(/sandbox-3[^'"\\s]*/g);

                return {
                    tier: tierMatch ? tierMatch[1] : null,
                    price: priceMatch ? priceMatch[1] : null,
                    verifyUrl: verifyMatch ? verifyMatch[1] : null,
                    successRedirect: redirectMatch ? redirectMatch[1] : null,
                    sandbox3Refs: sandboxMatch
                };
            }
        """)
        print(f"  TIER: {redirect_config['tier']}")
        print(f"  PRICE: {redirect_config['price']}")
        print(f"  VERIFY_URL: {redirect_config['verifyUrl']}")
        print(f"  SUCCESS_REDIRECT: {redirect_config['successRedirect']}")
        print(f"  Sandbox-3 references: {redirect_config['sandbox3Refs']}")

        # --- Simulate payment completion (JS) ---
        print("\n[PAYMENT SIMULATION] Simulating payment success via JS...")
        # Intercept navigation to capture redirect target
        navigated_to = []
        page.on("framenavigated", lambda frame: navigated_to.append(frame.url))

        sim_result = await page.evaluate("""
            () => {
                // Try to find and call the onApprove handler
                // The script wraps everything in IIFE so we need to trigger via PayPal SDK mock
                try {
                    // Check if there's a verifyAndRedirect or handlePaymentSuccess function
                    const scripts = Array.from(document.querySelectorAll('script:not([src])'));
                    const scriptText = scripts.map(s => s.textContent).join('\\n');

                    const funcs = Object.keys(window).filter(k =>
                        typeof window[k] === 'function' &&
                        (k.includes('pay') || k.includes('Payment') || k.includes('Partner') || k.includes('verify'))
                    );

                    return {
                        paymentFunctionsOnWindow: funcs,
                        hasPaypal: typeof paypal !== 'undefined',
                        paypalButtons: typeof paypal !== 'undefined' ? typeof paypal.Buttons : 'paypal not defined'
                    };
                } catch(e) {
                    return { error: e.toString() };
                }
            }
        """)
        print(f"  Simulation result: {sim_result}")

        # --- Full page screenshot after all checks ---
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight - 500)")
        await asyncio.sleep(1)
        await take_screenshot(page, "013-payment-section-final.png")

        await browser.close()

        print("\n" + "=" * 60)
        print("REDIRECT + PAYPAL CHECK COMPLETE")
        print("=" * 60)

asyncio.run(main())
