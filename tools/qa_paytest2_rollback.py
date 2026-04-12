#!/usr/bin/env python3
"""
QA Test: pay-test-2 Production PayPal Verification
Tests that production PayPal is active after plugin rollback to v4.6.4
"""

import asyncio
import os
import sys
import re

async def run_qa():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Installing playwright...")
        os.system("pip install playwright && python3 -m playwright install chromium")
        from playwright.async_api import async_playwright

    SCREENSHOT_PATH = "/home/jared/projects/AI-CIV/aether/docs/rollback-qa/pay-test-2-awakened.png"
    URL = "https://purebrain.ai/pay-test-2/"
    PASSWORD = "PureBrain.ai253443$$$"

    results = {}
    paypal_console_msgs = []
    all_console_msgs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900}
        )
        page = await context.new_page()

        # Collect console messages
        def handle_console(msg):
            text = msg.text
            all_console_msgs.append(f"[{msg.type.upper()}] {text}")
            if any(kw in text.lower() for kw in ["paypal", "error"]) or "PayPal" in text:
                paypal_console_msgs.append(f"[{msg.type.upper()}] {text}")

        page.on("console", handle_console)

        print("\n=== STEP 1: Navigate to pay-test-2 ===")
        response = await page.goto(URL, wait_until="domcontentloaded")
        print(f"HTTP Status: {response.status}")

        print("\n=== STEP 2: Enter password ===")
        # Wait for password field
        try:
            pw_field = await page.wait_for_selector('input[id^="pwbox-"]', timeout=10000)
            await pw_field.fill(PASSWORD)
            await page.keyboard.press("Enter")
            print("Password submitted")
        except Exception as e:
            print(f"Password field error: {e}")
            # Try alternative selector
            try:
                pw_field = await page.wait_for_selector('input[type="password"]', timeout=5000)
                await pw_field.fill(PASSWORD)
                await page.keyboard.press("Enter")
                print("Password submitted via alternative selector")
            except Exception as e2:
                print(f"Alternative password field also failed: {e2}")

        print("\n=== STEP 3: Wait for full page load (domcontentloaded + 10s) ===")
        await asyncio.sleep(10)
        print("10-second wait complete")

        print("\n=== STEP 4: Check openWaitlistModal is defined and is PayPal version ===")
        try:
            fn_src = await page.evaluate("typeof openWaitlistModal !== 'undefined' ? openWaitlistModal.toString() : 'UNDEFINED'")
            if fn_src == "UNDEFINED":
                results["openWaitlistModal_defined"] = "FAIL - function not defined"
                print("FAIL: openWaitlistModal is not defined")
            else:
                # Check if it contains PayPal-related content
                fn_lower = fn_src.lower()
                is_paypal_version = (
                    "normalise" in fn_lower or
                    "prices" in fn_lower or
                    "paypal" in fn_lower or
                    "pb-paypal" in fn_lower
                )
                if is_paypal_version:
                    results["openWaitlistModal_defined"] = "PASS - PayPal version confirmed"
                    print(f"PASS: openWaitlistModal is PayPal version")
                    # Show snippet
                    snippet = fn_src[:500].replace('\n', ' ')
                    print(f"  Snippet: {snippet}...")
                else:
                    results["openWaitlistModal_defined"] = "FAIL - function defined but NOT PayPal version"
                    print(f"FAIL: openWaitlistModal defined but appears to be waitlist/non-PayPal version")
                    print(f"  Snippet: {fn_src[:300]}...")
        except Exception as e:
            results["openWaitlistModal_defined"] = f"FAIL - error: {e}"
            print(f"FAIL: Error checking openWaitlistModal: {e}")

        print("\n=== STEP 5: Reveal pricing section ===")
        try:
            await page.evaluate("""
                const pricing = document.getElementById('pricing');
                if (pricing) {
                    pricing.classList.add('active');
                    pricing.style.display = 'block';
                    pricing.style.opacity = '1';
                    pricing.style.visibility = 'visible';
                }
            """)
            print("Pricing section revealed via JS")
        except Exception as e:
            print(f"Warning: Could not reveal pricing section: {e}")

        await asyncio.sleep(1)

        print("\n=== STEP 6: Call openWaitlistModal('Awakened') ===")
        try:
            await page.evaluate("openWaitlistModal('Awakened')")
            print("openWaitlistModal('Awakened') called")
        except Exception as e:
            print(f"Error calling openWaitlistModal: {e}")
            # Try without argument
            try:
                await page.evaluate("openWaitlistModal()")
                print("openWaitlistModal() called without argument")
            except Exception as e2:
                print(f"Also failed without argument: {e2}")

        print("\n=== STEP 7: Wait 5 seconds for PayPal SDK ===")
        await asyncio.sleep(5)
        print("5-second wait complete")

        print("\n=== STEP 8: Take screenshot ===")
        await page.screenshot(path=SCREENSHOT_PATH, full_page=False)
        print(f"Screenshot saved: {SCREENSHOT_PATH}")

        print("\n=== STEP 9: Check PayPal buttons container ===")
        try:
            container_check = await page.evaluate("""
                () => {
                    const container = document.getElementById('pb-paypal-buttons-container');
                    if (!container) return {exists: false, children: 0, html: ''};
                    const iframes = container.querySelectorAll('iframe');
                    const children = container.children.length;
                    return {
                        exists: true,
                        children: children,
                        iframes: iframes.length,
                        html: container.innerHTML.substring(0, 300)
                    };
                }
            """)
            if not container_check["exists"]:
                results["paypal_buttons_container"] = "FAIL - #pb-paypal-buttons-container not found in DOM"
                print("FAIL: #pb-paypal-buttons-container does not exist")
            elif container_check["children"] == 0 and container_check["iframes"] == 0:
                results["paypal_buttons_container"] = "FAIL - container exists but has no children/iframes"
                print(f"FAIL: #pb-paypal-buttons-container has 0 children")
                print(f"  HTML snippet: {container_check['html'][:200]}")
            else:
                results["paypal_buttons_container"] = f"PASS - {container_check['children']} children, {container_check['iframes']} iframes"
                print(f"PASS: #pb-paypal-buttons-container has {container_check['children']} children, {container_check['iframes']} iframes")
                print(f"  HTML snippet: {container_check['html'][:200]}")
        except Exception as e:
            results["paypal_buttons_container"] = f"FAIL - error: {e}"
            print(f"FAIL: Error checking PayPal buttons container: {e}")

        print("\n=== STEP 10: Check PayPal modal visibility ===")
        try:
            modal_check = await page.evaluate("""
                () => {
                    const modal = document.getElementById('pb-paypal-modal');
                    if (!modal) return {exists: false};
                    const style = window.getComputedStyle(modal);
                    return {
                        exists: true,
                        display: style.display,
                        visibility: style.visibility,
                        opacity: style.opacity,
                        classlist: modal.className
                    };
                }
            """)
            if not modal_check["exists"]:
                results["paypal_modal_visible"] = "FAIL - #pb-paypal-modal not found in DOM"
                print("FAIL: #pb-paypal-modal does not exist")
            else:
                is_visible = (
                    modal_check["display"] != "none" and
                    modal_check["visibility"] != "hidden" and
                    modal_check["opacity"] != "0"
                )
                if is_visible:
                    results["paypal_modal_visible"] = f"PASS - display:{modal_check['display']}, visibility:{modal_check['visibility']}"
                    print(f"PASS: #pb-paypal-modal is visible (display:{modal_check['display']}, visibility:{modal_check['visibility']})")
                else:
                    results["paypal_modal_visible"] = f"FAIL - not visible (display:{modal_check['display']}, visibility:{modal_check['visibility']}, opacity:{modal_check['opacity']})"
                    print(f"FAIL: #pb-paypal-modal not visible (display:{modal_check['display']}, visibility:{modal_check['visibility']}, opacity:{modal_check['opacity']})")
                print(f"  Classes: {modal_check['classlist']}")
        except Exception as e:
            results["paypal_modal_visible"] = f"FAIL - error: {e}"
            print(f"FAIL: Error checking PayPal modal: {e}")

        print("\n=== STEP 11: Check for PayPal iframes (production, NOT sandbox) ===")
        try:
            iframe_check = await page.evaluate("""
                () => {
                    const iframes = Array.from(document.querySelectorAll('iframe'));
                    const paypalIframes = iframes.filter(f => f.src && f.src.includes('paypal.com'));
                    const sandboxIframes = iframes.filter(f => f.src && f.src.includes('sandbox.paypal.com'));
                    const prodIframes = paypalIframes.filter(f => !f.src.includes('sandbox.paypal.com'));
                    return {
                        total_iframes: iframes.length,
                        paypal_total: paypalIframes.length,
                        sandbox_iframes: sandboxIframes.length,
                        production_iframes: prodIframes.length,
                        paypal_srcs: paypalIframes.map(f => f.src.substring(0, 100))
                    };
                }
            """)
            print(f"  Total iframes: {iframe_check['total_iframes']}")
            print(f"  PayPal iframes (total): {iframe_check['paypal_total']}")
            print(f"  Sandbox PayPal iframes: {iframe_check['sandbox_iframes']}")
            print(f"  Production PayPal iframes: {iframe_check['production_iframes']}")
            for src in iframe_check['paypal_srcs'][:5]:
                print(f"    - {src}")

            if iframe_check['production_iframes'] > 0:
                results["paypal_production_iframes"] = f"PASS - {iframe_check['production_iframes']} production PayPal iframe(s) found"
                print(f"PASS: {iframe_check['production_iframes']} production PayPal iframes found")
            elif iframe_check['paypal_total'] > 0 and iframe_check['sandbox_iframes'] > 0:
                results["paypal_production_iframes"] = f"FAIL - Only SANDBOX PayPal iframes found ({iframe_check['sandbox_iframes']} sandbox iframes)"
                print(f"FAIL: Only SANDBOX PayPal iframes found - production NOT confirmed")
            else:
                results["paypal_production_iframes"] = "FAIL - No PayPal iframes found at all"
                print("FAIL: No PayPal iframes found (SDK may not have rendered)")
        except Exception as e:
            results["paypal_production_iframes"] = f"FAIL - error: {e}"
            print(f"FAIL: Error checking PayPal iframes: {e}")

        print("\n=== STEP 12: Console messages containing PayPal or error ===")
        if paypal_console_msgs:
            print(f"Found {len(paypal_console_msgs)} PayPal/error console messages:")
            for msg in paypal_console_msgs:
                print(f"  {msg}")
        else:
            print("No PayPal or error console messages captured")

        await browser.close()

    print("\n" + "="*60)
    print("FINAL RESULTS SUMMARY")
    print("="*60)
    all_pass = True
    for check, result in results.items():
        status = "PASS" if result.startswith("PASS") else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"  [{status}] {check}: {result}")

    print("="*60)
    if all_pass:
        print("OVERALL: PASS - Production PayPal confirmed working")
    else:
        print("OVERALL: FAIL - See above for details")
    print("="*60)

    return results

if __name__ == "__main__":
    asyncio.run(run_qa())
