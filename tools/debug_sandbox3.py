#!/usr/bin/env python3
"""
Debug script for pay-test-sandbox-3 post-payment blank screen issue.
Captures console logs, screenshots, and simulates post-payment flow.
"""

import asyncio
import json
import time
import os
from datetime import datetime

OUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-debug-20260303"
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-3/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"

console_logs = []
network_errors = []
js_errors = []

async def run():
    from playwright.async_api import async_playwright

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

        # Capture ALL console messages
        def on_console(msg):
            entry = {
                "type": msg.type,
                "text": msg.text,
                "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]
            }
            console_logs.append(entry)
            print(f"[CONSOLE:{msg.type.upper()}] {msg.text[:200]}")

        def on_page_error(err):
            entry = {"error": str(err), "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]}
            js_errors.append(entry)
            print(f"[PAGE-ERROR] {str(err)[:300]}")

        def on_request_failed(req):
            entry = {"url": req.url, "failure": req.failure, "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]}
            network_errors.append(entry)
            print(f"[NETWORK-FAIL] {req.url[:150]} -> {req.failure}")

        page.on("console", on_console)
        page.on("pageerror", on_page_error)
        page.on("requestfailed", on_request_failed)

        print(f"\n{'='*60}")
        print(f"STEP 1: Navigate to {PAGE_URL}")
        print(f"{'='*60}")

        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        # Screenshot: password screen
        shot1 = f"{OUT_DIR}/001-password-screen.png"
        await page.screenshot(path=shot1, timeout=10000)
        print(f"[SHOT] {shot1}")

        print(f"\n{'='*60}")
        print(f"STEP 2: Enter password")
        print(f"{'='*60}")

        # Enter password
        pw_inp = await page.query_selector('input[type="password"]')
        if pw_inp:
            await pw_inp.fill(PAGE_PASSWORD)
            sub = await page.query_selector('input[type="submit"]')
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            print("[OK] Password submitted")
        else:
            print("[WARN] No password input found - page may already be unlocked")

        await asyncio.sleep(8)

        # Screenshot: after password
        shot2 = f"{OUT_DIR}/002-after-password.png"
        await page.screenshot(path=shot2, timeout=10000)
        print(f"[SHOT] {shot2}")

        # Check page title and basic structure
        title = await page.title()
        print(f"[PAGE TITLE] {title}")

        print(f"\n{'='*60}")
        print(f"STEP 3: Inspect page structure")
        print(f"{'='*60}")

        # Check key elements
        structure = await page.evaluate("""(function() {
            var result = {
                has_pricing_section: false,
                pricing_tiers: [],
                paypal_buttons: [],
                paypal_iframes: [],
                post_payment_elements: [],
                key_functions: {},
                body_innerHTML_length: document.body.innerHTML.length,
                scripts_loaded: []
            };

            // Check for pricing tiers
            var tiers = document.querySelectorAll('[class*="tier"], [class*="pricing"], [class*="plan"]');
            tiers.forEach(function(t) {
                result.pricing_tiers.push({tag: t.tagName, cls: t.className.substring(0,80)});
            });
            result.has_pricing_section = tiers.length > 0;

            // Check for PayPal iframes
            var iframes = document.querySelectorAll('iframe');
            iframes.forEach(function(f) {
                result.paypal_iframes.push({src: (f.src||'').substring(0,100), name: f.name||''});
            });

            // Check for PayPal buttons/divs
            var ppDivs = document.querySelectorAll('[id*="paypal"], [class*="paypal"], div[data-funding-source]');
            ppDivs.forEach(function(d) {
                result.paypal_buttons.push({tag: d.tagName, id: d.id||'', cls: d.className.substring(0,80)});
            });

            // Check for post-payment elements
            var ptcEls = document.querySelectorAll('#ptc-wrapper, .ptc-wrapper, #pay-test-post-payment, #ptcChatWrapper, [id*="post-payment"], [class*="post-payment"]');
            ptcEls.forEach(function(e) {
                var style = window.getComputedStyle(e);
                result.post_payment_elements.push({
                    id: e.id||'',
                    cls: e.className.substring(0,80),
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity
                });
            });

            // Check for key functions
            var funcs = ['onPaymentComplete', 'launchPostPaymentFlow', 'initPayTestFlow', 'openPayPalModal', 'openPayPalCheckout'];
            funcs.forEach(function(fn) {
                result.key_functions[fn] = typeof window[fn];
            });

            // Check scripts
            var scripts = document.querySelectorAll('script[src]');
            scripts.forEach(function(s) {
                result.scripts_loaded.push(s.src.substring(0,100));
            });

            return result;
        })()""")

        print(f"\n[STRUCTURE ANALYSIS]")
        print(f"  Body HTML length: {structure['body_innerHTML_length']:,} chars")
        print(f"  Has pricing section: {structure['has_pricing_section']}")
        print(f"  Pricing tiers found: {len(structure['pricing_tiers'])}")
        for t in structure['pricing_tiers'][:5]:
            print(f"    - {t['tag']}.{t['cls'][:60]}")
        print(f"  PayPal iframes: {len(structure['paypal_iframes'])}")
        for f in structure['paypal_iframes']:
            print(f"    - {f['src'][:80]} (name={f['name']})")
        print(f"  PayPal button divs: {len(structure['paypal_buttons'])}")
        for b in structure['paypal_buttons']:
            print(f"    - {b['tag']}#{b['id']}.{b['cls'][:60]}")
        print(f"  Post-payment elements: {len(structure['post_payment_elements'])}")
        for e in structure['post_payment_elements']:
            print(f"    - #{e['id']}.{e['cls'][:60]} display={e['display']} vis={e['visibility']}")
        print(f"\n  KEY FUNCTIONS:")
        for fn, ftype in structure['key_functions'].items():
            print(f"    - {fn}: {ftype}")

        # Scroll to pricing section
        print(f"\n{'='*60}")
        print(f"STEP 4: Scroll to pricing section")
        print(f"{'='*60}")

        # Try to scroll to find pricing
        await page.evaluate("""(function() {
            // Try scrolling to a pricing section
            var selectors = ['[class*="pricing"]', '[class*="tier"]', '[class*="plan"]',
                            '[id*="pricing"]', '[id*="payment"]', 'section'];
            for (var s of selectors) {
                var el = document.querySelector(s);
                if (el) {
                    el.scrollIntoView({behavior: 'instant', block: 'start'});
                    break;
                }
            }
            // If nothing found, scroll down 2000px
            window.scrollTo(0, 2000);
        })()""")
        await asyncio.sleep(2)

        shot3 = f"{OUT_DIR}/003-scrolled-pricing.png"
        await page.screenshot(path=shot3, timeout=10000)
        print(f"[SHOT] {shot3}")

        # Scroll down more to find PayPal buttons
        await page.evaluate("window.scrollTo(0, 3000)")
        await asyncio.sleep(1)
        shot4 = f"{OUT_DIR}/004-scroll-3000.png"
        await page.screenshot(path=shot4, timeout=10000)
        print(f"[SHOT] {shot4}")

        await page.evaluate("window.scrollTo(0, 5000)")
        await asyncio.sleep(1)
        shot5 = f"{OUT_DIR}/005-scroll-5000.png"
        await page.screenshot(path=shot5, timeout=10000)
        print(f"[SHOT] {shot5}")

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        shot6 = f"{OUT_DIR}/006-bottom-page.png"
        await page.screenshot(path=shot6, timeout=10000)
        print(f"[SHOT] {shot6}")

        # Check deeper: does the page have the post-payment script embedded?
        print(f"\n{'='*60}")
        print(f"STEP 5: Deep page structure analysis")
        print(f"{'='*60}")

        deep = await page.evaluate("""(function() {
            var html = document.body.innerHTML;

            return {
                // Search for key code patterns
                has_launchPostPaymentFlow: html.includes('launchPostPaymentFlow'),
                has_initPayTestFlow: html.includes('initPayTestFlow'),
                has_onPaymentComplete: html.includes('onPaymentComplete'),
                has_paypal_sdk: html.includes('paypal.com/sdk'),
                has_ptc_wrapper: html.includes('ptc-wrapper') || html.includes('ptcChatWrapper'),
                has_pricing_tiers: html.includes('Awakened') || html.includes('Partnered') || html.includes('Unified'),

                // Check for black screen elements
                fullscreen_divs: (function() {
                    var result = [];
                    var divs = document.querySelectorAll('div');
                    divs.forEach(function(d) {
                        var s = window.getComputedStyle(d);
                        if (s.position === 'fixed' && s.zIndex > 999) {
                            result.push({
                                id: d.id||'',
                                cls: d.className.substring(0,80),
                                zIndex: s.zIndex,
                                bg: s.background,
                                display: s.display
                            });
                        }
                    });
                    return result;
                })(),

                // First 500 chars of inline scripts
                inline_scripts_count: document.querySelectorAll('script:not([src])').length,

                // Check chatbox container specifically
                chatbox_container: (function() {
                    var ids = ['ptcChatWrapper', 'ptc-wrapper', 'ptcFlow', 'postPaymentFlow', 'payTestFlow'];
                    var found = [];
                    ids.forEach(function(id) {
                        var el = document.getElementById(id);
                        if (el) {
                            var s = window.getComputedStyle(el);
                            found.push({id: id, display: s.display, visibility: s.visibility, zIndex: s.zIndex, children: el.children.length});
                        }
                    });
                    return found;
                })()
            };
        })()""")

        print(f"[DEEP ANALYSIS]")
        print(f"  has launchPostPaymentFlow: {deep['has_launchPostPaymentFlow']}")
        print(f"  has initPayTestFlow: {deep['has_initPayTestFlow']}")
        print(f"  has onPaymentComplete: {deep['has_onPaymentComplete']}")
        print(f"  has PayPal SDK: {deep['has_paypal_sdk']}")
        print(f"  has ptc-wrapper: {deep['has_ptc_wrapper']}")
        print(f"  has pricing tiers (Awakened/Partnered/Unified): {deep['has_pricing_tiers']}")
        print(f"  inline scripts count: {deep['inline_scripts_count']}")

        print(f"\n  FIXED/HIGH-Z DIVS:")
        if deep['fullscreen_divs']:
            for d in deep['fullscreen_divs']:
                print(f"    - #{d['id']}.{d['cls'][:60]} z={d['zIndex']} display={d['display']} bg={d['bg'][:60]}")
        else:
            print(f"    (none found)")

        print(f"\n  CHATBOX CONTAINERS:")
        if deep['chatbox_container']:
            for c in deep['chatbox_container']:
                print(f"    - #{c['id']} display={c['display']} vis={c['visibility']} z={c['zIndex']} children={c['children']}")
        else:
            print(f"    (none found)")

        # NOW: Simulate the post-payment flow
        print(f"\n{'='*60}")
        print(f"STEP 6: Simulate onPaymentComplete() call")
        print(f"{'='*60}")

        # Scroll back to top first
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # Run the simulation - capture errors
        sim_result = await page.evaluate("""(function() {
            try {
                if (typeof window.onPaymentComplete === 'function') {
                    window.onPaymentComplete('Awakened', 'TEST-123', {});
                    return {success: true, error: null};
                } else {
                    return {success: false, error: 'onPaymentComplete is ' + typeof window.onPaymentComplete};
                }
            } catch(e) {
                return {success: false, error: e.toString(), stack: e.stack ? e.stack.substring(0,500) : 'no stack'};
            }
        })()""")

        print(f"[SIMULATION RESULT] {json.dumps(sim_result, indent=2)}")

        await asyncio.sleep(3)

        shot7 = f"{OUT_DIR}/007-after-simulation.png"
        await page.screenshot(path=shot7, timeout=10000)
        print(f"[SHOT] {shot7}")

        # Check what happened - any new elements, black screen?
        post_sim = await page.evaluate("""(function() {
            // Check for the black overlay/screen
            var overlays = [];
            var allDivs = document.querySelectorAll('div, section');
            allDivs.forEach(function(d) {
                var s = window.getComputedStyle(d);
                var bg = s.backgroundColor || s.background;
                if ((s.position === 'fixed' || s.position === 'absolute') &&
                    (bg.includes('0, 0, 0') || bg.includes('#000') || bg === 'black')) {
                    overlays.push({
                        id: d.id||'',
                        cls: d.className.substring(0,80),
                        position: s.position,
                        display: s.display,
                        zIndex: s.zIndex,
                        bg: bg.substring(0,80),
                        width: s.width,
                        height: s.height
                    });
                }
            });

            // Check if launchPostPaymentFlow ran
            var ptcElements = [];
            var ids = ['ptcChatWrapper', 'ptc-wrapper', 'ptcFlow', 'postPaymentFlow',
                      'payTestFlow', 'ptcContainer'];
            ids.forEach(function(id) {
                var el = document.getElementById(id);
                if (el) {
                    var s = window.getComputedStyle(el);
                    ptcElements.push({id: id, display: s.display, children: el.children.length,
                                     innerHTML_len: el.innerHTML.length});
                }
            });

            // Also search by class
            var ptcByClass = document.querySelectorAll('[class*="ptc"], [class*="post-payment"], [class*="chatbox"]');
            var classBased = [];
            ptcByClass.forEach(function(e) {
                var s = window.getComputedStyle(e);
                classBased.push({cls: e.className.substring(0,80), display: s.display, children: e.children.length});
            });

            return {
                black_overlays: overlays,
                ptc_by_id: ptcElements,
                ptc_by_class: classBased.slice(0, 10)
            };
        })()""")

        print(f"\n[POST-SIMULATION STATE]")
        print(f"  Black overlays/fixed divs:")
        if post_sim['black_overlays']:
            for o in post_sim['black_overlays']:
                print(f"    - #{o['id']}.{o['cls'][:60]}")
                print(f"      pos={o['position']} display={o['display']} z={o['zIndex']}")
                print(f"      bg={o['bg'][:80]} size={o['width']}x{o['height']}")
        else:
            print(f"    (none found)")

        print(f"\n  PTC elements by ID:")
        if post_sim['ptc_by_id']:
            for e in post_sim['ptc_by_id']:
                print(f"    - #{e['id']} display={e['display']} children={e['children']} html_len={e['innerHTML_len']}")
        else:
            print(f"    (none found)")

        print(f"\n  PTC elements by class:")
        for c in post_sim['ptc_by_class']:
            print(f"    - .{c['cls'][:60]} display={c['display']} children={c['children']}")

        # Try to directly extract the launchPostPaymentFlow source to understand it
        print(f"\n{'='*60}")
        print(f"STEP 7: Extract launchPostPaymentFlow source code")
        print(f"{'='*60}")

        func_source = await page.evaluate("""(function() {
            try {
                if (typeof window.launchPostPaymentFlow === 'function') {
                    return window.launchPostPaymentFlow.toString().substring(0, 2000);
                }
                return 'FUNCTION NOT FOUND';
            } catch(e) {
                return 'ERROR: ' + e.toString();
            }
        })()""")
        print(f"[launchPostPaymentFlow SOURCE]:\n{func_source}\n")

        init_source = await page.evaluate("""(function() {
            try {
                if (typeof window.initPayTestFlow === 'function') {
                    return window.initPayTestFlow.toString().substring(0, 2000);
                }
                return 'FUNCTION NOT FOUND';
            } catch(e) {
                return 'ERROR: ' + e.toString();
            }
        })()""")
        print(f"[initPayTestFlow SOURCE]:\n{init_source}\n")

        on_payment_source = await page.evaluate("""(function() {
            try {
                if (typeof window.onPaymentComplete === 'function') {
                    return window.onPaymentComplete.toString().substring(0, 2000);
                }
                return 'FUNCTION NOT FOUND';
            } catch(e) {
                return 'ERROR: ' + e.toString();
            }
        })()""")
        print(f"[onPaymentComplete SOURCE]:\n{on_payment_source}\n")

        # Try launchPostPaymentFlow directly
        print(f"\n{'='*60}")
        print(f"STEP 8: Call launchPostPaymentFlow directly")
        print(f"{'='*60}")

        launch_result = await page.evaluate("""(function() {
            try {
                if (typeof window.launchPostPaymentFlow === 'function') {
                    window.launchPostPaymentFlow('Awakened', 'DIRECT-TEST');
                    return {called: true, error: null};
                }
                return {called: false, error: 'not found'};
            } catch(e) {
                return {called: false, error: e.toString(), stack: (e.stack||'').substring(0,500)};
            }
        })()""")
        print(f"[launchPostPaymentFlow DIRECT CALL]: {json.dumps(launch_result)}")

        await asyncio.sleep(3)

        shot8 = f"{OUT_DIR}/008-after-launch-ppf.png"
        await page.screenshot(path=shot8, timeout=10000)
        print(f"[SHOT] {shot8}")

        # Try initPayTestFlow directly
        init_result = await page.evaluate("""(function() {
            try {
                if (typeof window.initPayTestFlow === 'function') {
                    window.initPayTestFlow('Awakened', 'INIT-TEST');
                    return {called: true, error: null};
                }
                return {called: false, error: 'not found'};
            } catch(e) {
                return {called: false, error: e.toString(), stack: (e.stack||'').substring(0,500)};
            }
        })()""")
        print(f"[initPayTestFlow DIRECT CALL]: {json.dumps(init_result)}")

        await asyncio.sleep(3)

        shot9 = f"{OUT_DIR}/009-after-init-ptf.png"
        await page.screenshot(path=shot9, timeout=10000)
        print(f"[SHOT] {shot9}")

        # Final console log summary
        print(f"\n{'='*60}")
        print(f"CONSOLE LOG SUMMARY ({len(console_logs)} messages)")
        print(f"{'='*60}")

        errors = [l for l in console_logs if l['type'] in ('error', 'warning')]
        print(f"\nERRORS & WARNINGS ({len(errors)} total):")
        for e in errors:
            print(f"  [{e['time']}][{e['type'].upper()}] {e['text'][:200]}")

        print(f"\nJS PAGE ERRORS ({len(js_errors)} total):")
        for e in js_errors:
            print(f"  [{e['time']}] {e['error'][:300]}")

        print(f"\nNETWORK FAILURES ({len(network_errors)} total):")
        for e in network_errors:
            print(f"  [{e['time']}] {e['url'][:150]} -> {e['failure']}")

        # Save full console log to file
        log_path = f"{OUT_DIR}/console-log.json"
        with open(log_path, 'w') as f:
            json.dump({
                "console_logs": console_logs,
                "js_errors": js_errors,
                "network_errors": network_errors,
                "structure": structure,
                "deep": deep,
                "post_sim": post_sim,
                "function_sources": {
                    "onPaymentComplete": on_payment_source,
                    "launchPostPaymentFlow": func_source,
                    "initPayTestFlow": init_source
                }
            }, f, indent=2)
        print(f"\n[LOG FILE] {log_path}")

        await browser.close()
        print(f"\n[DONE] All screenshots in {OUT_DIR}/")

if __name__ == "__main__":
    asyncio.run(run())
