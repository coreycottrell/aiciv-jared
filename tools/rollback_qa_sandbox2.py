#!/usr/bin/env python3
"""
Rollback QA Test: pay-test-sandbox-2 after plugin rollback to v4.6.4
Checks: password unlock, openWaitlistModal, pricing reveal, PayPal SDK, chatbox, console errors
"""

import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright

URL = "https://purebrain.ai/pay-test-sandbox-2/"
PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOT_PATH = "/home/jared/projects/AI-CIV/aether/docs/rollback-qa/sandbox-bonded.png"

results = {}

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
            headless=True,
        )

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        )

        page = await context.new_page()

        # Collect console messages
        console_errors = []
        console_all = []

        def on_console(msg):
            console_all.append({"type": msg.type, "text": msg.text})
            if msg.type in ("error", "warning"):
                console_errors.append({"type": msg.type, "text": msg.text})

        page.on("console", on_console)

        # ─── STEP 1: Navigate ────────────────────────────────────────────────
        print("\n[1] Navigating to pay-test-sandbox-2...")
        resp = await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        print(f"    HTTP status: {resp.status}")

        # ─── STEP 2: Enter password ──────────────────────────────────────────
        print("[2] Entering password...")
        try:
            pw_input = await page.wait_for_selector('input[id^="pwbox-"]', timeout=15000)
            await pw_input.fill(PASSWORD)
            # Submit the form
            await page.evaluate("""() => {
                const form = document.querySelector('.post-password-form');
                if (form) form.submit();
            }""")
            print("    Password submitted via form.submit()")
        except Exception as e:
            print(f"    Password field not found (page may already be unlocked): {e}")

        # Wait for domcontentloaded on new page + extra sleep for JS
        await page.wait_for_load_state("domcontentloaded")
        print("[3] Waiting 10 seconds for full page load + JS initialization...")
        await asyncio.sleep(10)

        current_url = page.url
        print(f"    Current URL: {current_url}")

        # ─── STEP 3: Check openWaitlistModal ────────────────────────────────
        print("\n[4] Checking openWaitlistModal...")
        modal_check = await page.evaluate("""() => {
            const defined = typeof window.openWaitlistModal !== 'undefined';
            const type_str = typeof window.openWaitlistModal;
            // Try to get function source to determine PayPal vs waitlist
            let source_hint = '';
            if (defined && typeof window.openWaitlistModal === 'function') {
                const src = window.openWaitlistModal.toString();
                if (src.includes('paypal') || src.includes('PayPal') || src.includes('pb-paypal')) {
                    source_hint = 'PayPal';
                } else if (src.includes('waitlist') || src.includes('Waitlist') || src.includes('joinWaitlist')) {
                    source_hint = 'waitlist';
                } else {
                    source_hint = 'unknown (first 200 chars: ' + src.substring(0, 200) + ')';
                }
            }
            return { defined, type_str, source_hint };
        }""")

        print(f"    openWaitlistModal defined: {modal_check['defined']}")
        print(f"    Type: {modal_check['type_str']}")
        print(f"    Hint (PayPal vs waitlist): {modal_check['source_hint']}")

        if modal_check['defined']:
            results['openWaitlistModal_defined'] = "PASS"
            results['openWaitlistModal_type'] = f"PASS ({modal_check['type_str']}, hint={modal_check['source_hint']})"
        else:
            results['openWaitlistModal_defined'] = "FAIL - not defined on window"
            results['openWaitlistModal_type'] = "FAIL - not defined"

        # ─── STEP 4: Reveal pricing section ─────────────────────────────────
        print("\n[5] Revealing pricing section...")
        reveal_result = await page.evaluate("""() => {
            const el = document.getElementById('pricing');
            if (!el) return { found: false };
            el.classList.add('active');
            el.style.display = 'block';
            el.style.opacity = '1';
            el.style.visibility = 'visible';
            // Also try pricing-section class
            const sections = document.querySelectorAll('.pricing-section, .pricing-cards, .pricing-container');
            sections.forEach(s => {
                s.style.display = 'block';
                s.style.opacity = '1';
                s.style.visibility = 'visible';
            });
            return {
                found: true,
                tag: el.tagName,
                classes: el.className,
                display: window.getComputedStyle(el).display,
                children_count: el.children.length
            };
        }""")
        print(f"    Pricing #pricing element found: {reveal_result.get('found')}")
        if reveal_result.get('found'):
            print(f"    Tag: {reveal_result.get('tag')}, Classes: {reveal_result.get('classes')}")
            print(f"    Display after reveal: {reveal_result.get('display')}")
            print(f"    Children: {reveal_result.get('children_count')}")
            results['pricing_reveal'] = "PASS" if reveal_result.get('found') else "FAIL - #pricing not found"
        else:
            # Try alternate selectors
            alt_check = await page.evaluate("""() => {
                const alt = document.querySelector('.pricing-section, [class*="pricing"], [id*="pricing"]');
                return alt ? { tag: alt.tagName, id: alt.id, classes: alt.className } : null;
            }""")
            print(f"    Alternate pricing selector: {alt_check}")
            results['pricing_reveal'] = "FAIL - #pricing element not found in DOM"

        # ─── STEP 5: Call openWaitlistModal('Bonded') ────────────────────────
        print("\n[6] Calling openWaitlistModal('Bonded')...")
        if modal_check['defined']:
            try:
                call_result = await page.evaluate("""() => {
                    try {
                        openWaitlistModal('Bonded');
                        return { called: true, error: null };
                    } catch(e) {
                        return { called: false, error: e.toString() };
                    }
                }""")
                print(f"    Called: {call_result['called']}, Error: {call_result['error']}")
                results['modal_call'] = "PASS" if call_result['called'] else f"FAIL - {call_result['error']}"
            except Exception as e:
                print(f"    Exception calling modal: {e}")
                results['modal_call'] = f"FAIL - exception: {e}"
        else:
            results['modal_call'] = "SKIP - openWaitlistModal not defined"

        # ─── STEP 6: Wait 5 seconds for PayPal SDK ──────────────────────────
        print("[7] Waiting 5 seconds for PayPal SDK to load...")
        await asyncio.sleep(5)

        # ─── STEP 7: Screenshot ──────────────────────────────────────────────
        print(f"\n[8] Taking screenshot -> {SCREENSHOT_PATH}")
        await page.screenshot(path=SCREENSHOT_PATH, full_page=False)
        print("    Screenshot saved.")
        results['screenshot'] = "PASS"

        # ─── STEP 8: Check PayPal buttons container ──────────────────────────
        print("\n[9] Checking PayPal buttons container (#pb-paypal-buttons-container)...")
        paypal_container_check = await page.evaluate("""() => {
            const container = document.getElementById('pb-paypal-buttons-container');
            if (!container) {
                // Try broader search
                const broader = document.querySelector('[id*="paypal-buttons"], [id*="pb-paypal"], .paypal-buttons');
                return {
                    found: false,
                    broader_found: !!broader,
                    broader_id: broader ? broader.id : null,
                    broader_class: broader ? broader.className : null
                };
            }
            const iframes = container.querySelectorAll('iframe');
            const children = container.children.length;
            const innerHTML_preview = container.innerHTML.substring(0, 300);
            return {
                found: true,
                iframe_count: iframes.length,
                children_count: children,
                innerHTML_preview: innerHTML_preview,
                display: window.getComputedStyle(container).display,
                visibility: window.getComputedStyle(container).visibility,
                height: window.getComputedStyle(container).height
            };
        }""")

        print(f"    Container found: {paypal_container_check.get('found')}")
        if paypal_container_check.get('found'):
            iframes = paypal_container_check.get('iframe_count', 0)
            children = paypal_container_check.get('children_count', 0)
            print(f"    iFrames: {iframes}, Children: {children}")
            print(f"    Display: {paypal_container_check.get('display')}, Visibility: {paypal_container_check.get('visibility')}")
            print(f"    Height: {paypal_container_check.get('height')}")
            if iframes > 0 or children > 0:
                results['paypal_container'] = f"PASS - {iframes} iframes, {children} children"
            else:
                results['paypal_container'] = f"FAIL - container found but empty (0 iframes, 0 children)"
        else:
            print(f"    Broader search: found={paypal_container_check.get('broader_found')}, id={paypal_container_check.get('broader_id')}")
            results['paypal_container'] = "FAIL - #pb-paypal-buttons-container not found"

        # ─── STEP 9: Check PayPal SDK script URL ────────────────────────────
        print("\n[10] Checking PayPal SDK script URL...")
        sdk_check = await page.evaluate("""() => {
            const scripts = Array.from(document.querySelectorAll('script[src]'));
            const paypalScripts = scripts.filter(s => s.src && s.src.includes('paypal'));
            return paypalScripts.map(s => ({
                src: s.src,
                async: s.async,
                defer: s.defer
            }));
        }""")

        if sdk_check:
            for script in sdk_check:
                print(f"    PayPal script: {script['src'][:120]}...")
                print(f"    async={script['async']}, defer={script['defer']}")
            results['paypal_sdk_loaded'] = f"PASS - {len(sdk_check)} PayPal script(s) found"
        else:
            print("    No PayPal scripts found in DOM")
            results['paypal_sdk_loaded'] = "FAIL - No script[src*='paypal'] found"

        # ─── STEP 10: Check console errors ──────────────────────────────────
        print(f"\n[11] Console errors ({len(console_errors)} total):")
        if console_errors:
            for err in console_errors[:10]:
                print(f"    [{err['type'].upper()}] {err['text'][:120]}")
            blocking_errors = [e for e in console_errors if e['type'] == 'error']
            if blocking_errors:
                results['console_errors'] = f"WARN - {len(blocking_errors)} JS errors (see output)"
            else:
                results['console_errors'] = f"PASS - {len(console_errors)} warnings only (no JS errors)"
        else:
            print("    No console errors.")
            results['console_errors'] = "PASS - zero console errors"

        # ─── STEP 11: Check chatbox elements ────────────────────────────────
        print("\n[12] Checking chatbox elements...")
        chat_check = await page.evaluate("""() => {
            const selectors = [
                '#chatMessages', '#userInput', '#submitBtn',
                '.chat-initial__btn', '.chat-initial',
                '#typingIndicator', '.typing-indicator',
                '.ptc-wrapper', '#pay-test-post-payment',
                '.ptc-messages', 'textarea[placeholder*="Message"]',
                '.ptc-send-btn',
                // Generic chat patterns
                '[id*="chat"]', '[class*="chat"]'
            ];
            const found = {};
            selectors.forEach(sel => {
                try {
                    const el = document.querySelector(sel);
                    found[sel] = el ? {
                        found: true,
                        display: window.getComputedStyle(el).display,
                        visibility: window.getComputedStyle(el).visibility,
                        tag: el.tagName
                    } : { found: false };
                } catch(e) {
                    found[sel] = { found: false, error: e.toString() };
                }
            });
            return found;
        }""")

        chat_found_count = 0
        key_elements = ['#chatMessages', '#userInput', '.chat-initial__btn', '.ptc-wrapper']
        key_results = {}
        for sel, info in chat_check.items():
            if info.get('found'):
                chat_found_count += 1
                if sel in key_elements:
                    print(f"    FOUND: {sel} ({info.get('tag')}) display={info.get('display')} vis={info.get('visibility')}")
                    key_results[sel] = info

        print(f"    Total chat-related elements found: {chat_found_count}")

        pre_chat_ok = chat_check.get('#chatMessages', {}).get('found') or chat_check.get('#userInput', {}).get('found') or chat_check.get('.chat-initial__btn', {}).get('found')
        post_chat_ok = chat_check.get('.ptc-wrapper', {}).get('found') or chat_check.get('#pay-test-post-payment', {}).get('found')

        if pre_chat_ok:
            results['chatbox_pre_payment'] = "PASS - pre-payment chat elements present"
        else:
            results['chatbox_pre_payment'] = "FAIL - no pre-payment chat elements found"

        if post_chat_ok:
            results['chatbox_post_payment'] = "PASS - post-payment chat elements present"
        else:
            results['chatbox_post_payment'] = "INFO - post-payment chat not visible (expected pre-purchase)"

        # ─── FINAL REPORT ────────────────────────────────────────────────────
        print("\n" + "="*60)
        print("ROLLBACK QA RESULTS - pay-test-sandbox-2 - v4.6.4")
        print("="*60)

        all_pass = True
        for check, status in results.items():
            icon = "PASS" if status.startswith("PASS") else ("WARN" if status.startswith("WARN") or status.startswith("INFO") else "FAIL")
            if icon == "FAIL":
                all_pass = False
            print(f"  [{icon}] {check}: {status}")

        print("="*60)
        print(f"OVERALL: {'PASS' if all_pass else 'FAIL - see failures above'}")
        print(f"Screenshot: {SCREENSHOT_PATH}")
        print("="*60)

        # Write JSON results
        results_path = "/home/jared/projects/AI-CIV/aether/docs/rollback-qa/results.json"
        with open(results_path, 'w') as f:
            json.dump({
                "url": URL,
                "timestamp": "2026-02-27",
                "plugin_version": "v4.6.4-rollback",
                "results": results,
                "console_errors_count": len(console_errors),
                "console_errors": console_errors[:20],
                "overall": "PASS" if all_pass else "FAIL"
            }, f, indent=2)
        print(f"Results JSON: {results_path}")

        await browser.close()

asyncio.run(run())
