#!/usr/bin/env python3
"""
Deep inspection of pay-test-2 to understand the current state after rollback.
Specifically: what openWaitlistModal does vs openPayPalModal, and what functions are available.
"""

import asyncio
import os

async def run_deep_inspect():
    from playwright.async_api import async_playwright

    URL = "https://purebrain.ai/pay-test-2/"
    PASSWORD = "PureBrain.ai253443$$$"
    all_console_msgs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900}
        )
        page = await context.new_page()

        def handle_console(msg):
            all_console_msgs.append(f"[{msg.type.upper()}] {msg.text}")

        page.on("console", handle_console)

        await page.goto(URL, wait_until="domcontentloaded")

        # Enter password
        try:
            pw_field = await page.wait_for_selector('input[id^="pwbox-"]', timeout=10000)
            await pw_field.fill(PASSWORD)
            await page.keyboard.press("Enter")
        except:
            try:
                pw_field = await page.wait_for_selector('input[type="password"]', timeout=5000)
                await pw_field.fill(PASSWORD)
                await page.keyboard.press("Enter")
            except:
                pass

        await asyncio.sleep(10)

        print("=== FUNCTION INVENTORY ===")
        fn_inventory = await page.evaluate("""
            () => {
                const fns = {};
                // Check all PayPal-related functions
                const toCheck = [
                    'openWaitlistModal',
                    'openPayPalModal',
                    'initPayPal',
                    'loadPayPalSDK',
                    'PB_PayPal',
                    'pb_paypal'
                ];
                toCheck.forEach(name => {
                    if (typeof window[name] !== 'undefined') {
                        if (typeof window[name] === 'function') {
                            fns[name] = 'FUNCTION: ' + window[name].toString().substring(0, 200);
                        } else {
                            fns[name] = 'VALUE: ' + JSON.stringify(window[name]).substring(0, 100);
                        }
                    } else {
                        fns[name] = 'NOT_DEFINED';
                    }
                });
                return fns;
            }
        """)
        for name, val in fn_inventory.items():
            print(f"\n[{name}]: {val[:300]}")

        print("\n\n=== PAYPAL PLUGIN GLOBAL OBJECTS ===")
        plugin_obj = await page.evaluate("""
            () => {
                // Check for pb_paypal_params or similar
                const globals = {};
                Object.keys(window).filter(k => k.toLowerCase().includes('paypal') || k.toLowerCase().includes('pb_pay')).forEach(k => {
                    try {
                        globals[k] = JSON.stringify(window[k]).substring(0, 200);
                    } catch(e) {
                        globals[k] = 'ERROR: ' + e.message;
                    }
                });
                return globals;
            }
        """)
        for name, val in plugin_obj.items():
            print(f"  {name}: {val}")

        print("\n\n=== PAYPAL SCRIPT TAGS ON PAGE ===")
        scripts = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script[src]'));
                return scripts.map(s => s.src).filter(s => s.toLowerCase().includes('paypal'));
            }
        """)
        for src in scripts:
            print(f"  {src}")

        print("\n\n=== ALL SCRIPTS (PayPal and plugin-related) ===")
        all_scripts = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script[src]'));
                return scripts.map(s => s.src).filter(s =>
                    s.includes('paypal') ||
                    s.includes('pb-paypal') ||
                    s.includes('purebrain') ||
                    s.includes('plugin')
                );
            }
        """)
        for src in all_scripts:
            print(f"  {src}")

        print("\n\n=== INLINE SCRIPT SNIPPETS (first 500 chars each, checking for paypal) ===")
        inline_scripts = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script:not([src])'));
                return scripts
                    .map(s => s.textContent)
                    .filter(t => t.toLowerCase().includes('paypal') || t.includes('openPayPalModal') || t.includes('pb-paypal'))
                    .map(t => t.substring(0, 500));
            }
        """)
        for i, script in enumerate(inline_scripts):
            print(f"\n  [Inline Script {i+1}]:")
            print(f"  {script[:500]}")

        print("\n\n=== DOM ELEMENTS CHECK ===")
        dom_check = await page.evaluate("""
            () => {
                const elements = [
                    'pb-paypal-modal',
                    'pb-paypal-buttons-container',
                    'pricing',
                    'waitlistModal',
                    'pb-paypal-tier-name',
                    'pb-paypal-tier-price'
                ];
                const result = {};
                elements.forEach(id => {
                    const el = document.getElementById(id);
                    if (el) {
                        const style = window.getComputedStyle(el);
                        result[id] = {
                            exists: true,
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity,
                            tagName: el.tagName,
                            className: el.className
                        };
                    } else {
                        result[id] = {exists: false};
                    }
                });
                return result;
            }
        """)
        for el_id, info in dom_check.items():
            if info.get("exists"):
                print(f"  #{el_id}: EXISTS - display:{info['display']}, visibility:{info['visibility']}, opacity:{info['opacity']}")
            else:
                print(f"  #{el_id}: NOT FOUND")

        print("\n\n=== NOW CALL openPayPalModal directly if it exists ===")
        result = await page.evaluate("""
            () => {
                if (typeof openPayPalModal === 'function') {
                    try {
                        openPayPalModal('Awakened', 79);
                        return 'called openPayPalModal(Awakened, 79) - success';
                    } catch(e) {
                        return 'called openPayPalModal - error: ' + e.message;
                    }
                }
                return 'openPayPalModal not available';
            }
        """)
        print(f"  {result}")

        await asyncio.sleep(5)

        print("\n\n=== AFTER openPayPalModal CALL - Modal State ===")
        modal_state = await page.evaluate("""
            () => {
                const modal = document.getElementById('pb-paypal-modal');
                if (!modal) return {exists: false};
                const style = window.getComputedStyle(modal);
                const container = document.getElementById('pb-paypal-buttons-container');
                const iframes = document.querySelectorAll('iframe[src*="paypal.com"]');
                const sandboxIframes = document.querySelectorAll('iframe[src*="sandbox.paypal.com"]');
                return {
                    modal_display: style.display,
                    modal_visibility: style.visibility,
                    modal_opacity: style.opacity,
                    modal_class: modal.className,
                    container_children: container ? container.children.length : 0,
                    container_iframes: container ? container.querySelectorAll('iframe').length : 0,
                    paypal_iframes: iframes.length,
                    sandbox_iframes: sandboxIframes.length,
                    paypal_iframe_srcs: Array.from(iframes).map(f => f.src.substring(0, 120))
                };
            }
        """)
        print(f"  Modal display: {modal_state.get('modal_display')}, visibility: {modal_state.get('modal_visibility')}, opacity: {modal_state.get('modal_opacity')}")
        print(f"  Modal class: {modal_state.get('modal_class')}")
        print(f"  Container children: {modal_state.get('container_children')}")
        print(f"  Container iframes: {modal_state.get('container_iframes')}")
        print(f"  PayPal iframes: {modal_state.get('paypal_iframes')}")
        print(f"  Sandbox iframes: {modal_state.get('sandbox_iframes')}")
        for src in modal_state.get('paypal_iframe_srcs', [])[:5]:
            print(f"    iframe src: {src}")

        print("\n\n=== SCREENSHOT (after openPayPalModal) ===")
        screenshot_path = "/home/jared/projects/AI-CIV/aether/docs/rollback-qa/pay-test-2-deep-inspect.png"
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"Screenshot: {screenshot_path}")

        print("\n\n=== ALL CONSOLE MESSAGES ===")
        for msg in all_console_msgs:
            print(f"  {msg}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_deep_inspect())
