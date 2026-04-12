#!/usr/bin/env python3
"""
Debug script v2 for pay-test-sandbox-3 post-payment blank screen issue.
Uses clip-based screenshots to avoid Three.js timeout issues.
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

async def safe_screenshot(page, path, label=""):
    """Screenshot with clip to avoid Three.js timeout issues."""
    try:
        await page.screenshot(
            path=path,
            clip={"x": 0, "y": 0, "width": 1440, "height": 900},
            timeout=15000
        )
        print(f"[SHOT] {path}")
        return True
    except Exception as e:
        print(f"[SHOT-FAIL] {path}: {e}")
        # Try minimal screenshot
        try:
            await page.screenshot(path=path, clip={"x": 0, "y": 0, "width": 800, "height": 600}, timeout=20000)
            print(f"[SHOT-FALLBACK] {path}")
            return True
        except Exception as e2:
            print(f"[SHOT-TOTAL-FAIL] {path}: {e2}")
            return False

async def run():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox",
                  "--disable-web-security", "--disable-gpu",
                  "--disable-webgl", "--disable-3d-apis"]
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
            if msg.type in ('error', 'warning') or 'PB' in msg.text or 'ptc' in msg.text.lower() or 'payment' in msg.text.lower() or 'chatbox' in msg.text.lower():
                print(f"[CONSOLE:{msg.type.upper()}] {msg.text[:300]}")

        def on_page_error(err):
            entry = {"error": str(err), "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]}
            js_errors.append(entry)
            print(f"[PAGE-ERROR] {str(err)[:300]}")

        def on_request_failed(req):
            # Only log non-analytics failures
            url = req.url
            if 'google-analytics' not in url and 'gtm' not in url and 'secureserver' not in url and 'clarity' not in url:
                entry = {"url": url, "failure": req.failure}
                network_errors.append(entry)
                print(f"[NETWORK-FAIL] {url[:150]} -> {req.failure}")

        page.on("console", on_console)
        page.on("pageerror", on_page_error)
        page.on("requestfailed", on_request_failed)

        print(f"\n{'='*60}")
        print(f"STEP 1: Navigate to {PAGE_URL}")
        print(f"{'='*60}")

        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        await safe_screenshot(page, f"{OUT_DIR}/001-password-screen.png")

        print(f"\n{'='*60}")
        print(f"STEP 2: Enter password")
        print(f"{'='*60}")

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
            print("[WARN] No password input found - page may already be unlocked or different layout")

        # Wait for page to fully load
        await asyncio.sleep(12)

        await safe_screenshot(page, f"{OUT_DIR}/002-after-password.png")

        title = await page.title()
        print(f"[PAGE TITLE] {title}")

        # Check page body length
        body_len = await page.evaluate("document.body.innerHTML.length")
        print(f"[BODY LENGTH] {body_len:,} chars")

        print(f"\n{'='*60}")
        print(f"STEP 3: Deep page analysis")
        print(f"{'='*60}")

        structure = await page.evaluate("""(function() {
            var html = document.body.innerHTML;
            var result = {
                has_pricing: html.includes('Awakened') || html.includes('Partnered') || html.includes('Unified'),
                has_paypal_sdk: html.includes('paypal.com/sdk') || html.includes('paypalobjects'),
                has_launch_ppf: html.includes('launchPostPaymentFlow'),
                has_init_ptf: html.includes('initPayTestFlow'),
                has_on_payment: html.includes('onPaymentComplete'),
                has_ptc: html.includes('ptc-wrapper') || html.includes('ptcChatWrapper') || html.includes('ptc-input'),

                // What key functions exist globally?
                key_functions: {},

                // Look for inline scripts
                inline_script_count: document.querySelectorAll('script:not([src])').length,

                // PayPal iframes
                iframes: [],

                // Any containers
                containers: []
            };

            // Check global functions
            var funcs = ['onPaymentComplete', 'launchPostPaymentFlow', 'initPayTestFlow',
                        'openPayPalModal', 'openPayPalCheckout', 'handlePaymentSuccess',
                        'fireSeed', 'initPTC'];
            funcs.forEach(function(fn) {
                result.key_functions[fn] = typeof window[fn];
            });

            // iframes
            document.querySelectorAll('iframe').forEach(function(f) {
                result.iframes.push({src: (f.src||'').substring(0,120), name: f.name||''});
            });

            // Key containers
            var ids = ['ptcChatWrapper', 'ptc-wrapper', 'ptcFlow', 'postPaymentFlow',
                      'payTestFlow', 'ptcContainer', 'pricing-section', 'payment-section'];
            ids.forEach(function(id) {
                var el = document.getElementById(id);
                if (el) {
                    var s = window.getComputedStyle(el);
                    result.containers.push({id: id, display: s.display, children: el.children.length});
                }
            });

            return result;
        })()""")

        print(f"Page has pricing (Awakened/Partnered/Unified): {structure['has_pricing']}")
        print(f"Page has PayPal SDK: {structure['has_paypal_sdk']}")
        print(f"Page has launchPostPaymentFlow: {structure['has_launch_ppf']}")
        print(f"Page has initPayTestFlow: {structure['has_init_ptf']}")
        print(f"Page has onPaymentComplete: {structure['has_on_payment']}")
        print(f"Page has ptc elements: {structure['has_ptc']}")
        print(f"Inline scripts: {structure['inline_script_count']}")
        print(f"\nKEY FUNCTIONS:")
        for fn, ftype in structure['key_functions'].items():
            print(f"  {fn}: {ftype}")
        print(f"\nIFRAMES ({len(structure['iframes'])}):")
        for f in structure['iframes']:
            print(f"  {f['src'][:100]} (name={f['name']})")
        print(f"\nCONTAINERS:")
        for c in structure['containers']:
            print(f"  #{c['id']} display={c['display']} children={c['children']}")

        # Scroll through the page
        print(f"\n{'='*60}")
        print(f"STEP 4: Scroll to find pricing")
        print(f"{'='*60}")

        for scroll_y, label in [(1000, "1000"), (2000, "2000"), (3000, "3000"), (4000, "4000")]:
            await page.evaluate(f"window.scrollTo(0, {scroll_y})")
            await asyncio.sleep(1)
            await safe_screenshot(page, f"{OUT_DIR}/scroll-{label}.png")

        # NOW SIMULATE POST-PAYMENT
        print(f"\n{'='*60}")
        print(f"STEP 5: Simulate onPaymentComplete('Awakened', 'TEST-123', {{}})")
        print(f"{'='*60}")

        # Scroll to top first
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # Get function source before calling
        fn_sources = await page.evaluate("""(function() {
            var sources = {};
            ['onPaymentComplete', 'launchPostPaymentFlow', 'initPayTestFlow'].forEach(function(fn) {
                try {
                    if (typeof window[fn] === 'function') {
                        sources[fn] = window[fn].toString().substring(0, 1500);
                    } else {
                        sources[fn] = 'TYPE: ' + typeof window[fn];
                    }
                } catch(e) {
                    sources[fn] = 'ERROR: ' + e.toString();
                }
            });
            return sources;
        })()""")

        print(f"\n[onPaymentComplete SOURCE]:\n{fn_sources.get('onPaymentComplete', 'NOT FOUND')}\n")
        print(f"\n[launchPostPaymentFlow SOURCE]:\n{fn_sources.get('launchPostPaymentFlow', 'NOT FOUND')}\n")
        print(f"\n[initPayTestFlow SOURCE]:\n{fn_sources.get('initPayTestFlow', 'NOT FOUND')}\n")

        # Call simulation
        sim_result = await page.evaluate("""(function() {
            try {
                if (typeof window.onPaymentComplete === 'function') {
                    window.onPaymentComplete('Awakened', 'TEST-123', {});
                    return {called: true, error: null};
                } else {
                    return {called: false, error: 'onPaymentComplete is ' + typeof window.onPaymentComplete};
                }
            } catch(e) {
                return {called: false, error: e.toString(), stack: (e.stack||'').substring(0,800)};
            }
        })()""")

        print(f"\n[SIMULATION RESULT]: {json.dumps(sim_result, indent=2)}")

        await asyncio.sleep(4)
        await safe_screenshot(page, f"{OUT_DIR}/007-after-simulation.png")

        # Check what's visible now
        post_sim = await page.evaluate("""(function() {
            var result = {
                black_overlays: [],
                ptc_elements: [],
                body_overflow: window.getComputedStyle(document.body).overflow
            };

            // Find fixed/absolute black divs
            document.querySelectorAll('*').forEach(function(el) {
                var s = window.getComputedStyle(el);
                var bg = s.backgroundColor;
                var isBlack = bg === 'rgb(0, 0, 0)' || bg === 'rgba(0, 0, 0, 1)';
                var isCovered = (s.position === 'fixed' || s.position === 'absolute');
                if (isBlack && isCovered && el.tagName !== 'SCRIPT') {
                    result.black_overlays.push({
                        tag: el.tagName,
                        id: el.id||'',
                        cls: el.className.substring(0,80),
                        display: s.display,
                        position: s.position,
                        zIndex: s.zIndex,
                        width: s.width,
                        height: s.height,
                        top: s.top,
                        left: s.left
                    });
                }
            });

            // Find PTC elements
            ['ptcChatWrapper', 'ptc-wrapper', 'ptc-container', 'ptcFlow'].forEach(function(id) {
                var el = document.getElementById(id);
                if (el) {
                    var s = window.getComputedStyle(el);
                    result.ptc_elements.push({
                        id: id, display: s.display,
                        visibility: s.visibility,
                        children: el.children.length,
                        html_len: el.innerHTML.length,
                        position: s.position,
                        zIndex: s.zIndex
                    });
                }
            });
            document.querySelectorAll('[class*="ptc"], [id*="ptc"]').forEach(function(el) {
                if (el.id && result.ptc_elements.find(function(e) { return e.id === el.id; })) return;
                var s = window.getComputedStyle(el);
                result.ptc_elements.push({
                    id: el.id||'',
                    cls: el.className.substring(0,60),
                    display: s.display,
                    visibility: s.visibility,
                    children: el.children.length
                });
            });

            return result;
        })()""")

        print(f"\n[POST-SIMULATION STATE]")
        print(f"Body overflow: {post_sim['body_overflow']}")
        print(f"\nBLACK OVERLAYS ({len(post_sim['black_overlays'])}):")
        for o in post_sim['black_overlays']:
            print(f"  {o['tag']}#{o['id']}.{o['cls'][:60]}")
            print(f"    pos={o['position']} display={o['display']} z={o['zIndex']}")
            print(f"    size={o['width']}x{o['height']} at top={o['top']},left={o['left']}")

        print(f"\nPTC ELEMENTS ({len(post_sim['ptc_elements'])}):")
        for e in post_sim['ptc_elements']:
            print(f"  {e}")

        # Try launchPostPaymentFlow directly
        print(f"\n{'='*60}")
        print(f"STEP 6: Call launchPostPaymentFlow directly")
        print(f"{'='*60}")

        launch_result = await page.evaluate("""(function() {
            try {
                if (typeof window.launchPostPaymentFlow === 'function') {
                    window.launchPostPaymentFlow('Awakened', 'DIRECT-TEST');
                    return {called: true, error: null};
                }
                return {called: false, error: 'launchPostPaymentFlow is ' + typeof window.launchPostPaymentFlow};
            } catch(e) {
                return {called: false, error: e.toString(), stack: (e.stack||'').substring(0,800)};
            }
        })()""")
        print(f"[launchPostPaymentFlow RESULT]: {json.dumps(launch_result)}")

        await asyncio.sleep(3)
        await safe_screenshot(page, f"{OUT_DIR}/008-after-launch-ppf.png")

        # Inspect what the black screen looks like
        black_screen_state = await page.evaluate("""(function() {
            // Get the computed style of the body and top-level containers
            var result = {
                body_style: {},
                fixed_elements: []
            };

            var bodyS = window.getComputedStyle(document.body);
            result.body_style = {
                bg: bodyS.backgroundColor,
                overflow: bodyS.overflow,
                position: bodyS.position
            };

            // All fixed elements with their backgrounds
            document.querySelectorAll('*').forEach(function(el) {
                var s = window.getComputedStyle(el);
                if (s.position === 'fixed') {
                    result.fixed_elements.push({
                        tag: el.tagName,
                        id: el.id||'',
                        cls: (el.className||'').substring(0,80),
                        display: s.display,
                        zIndex: s.zIndex,
                        bg: s.backgroundColor,
                        width: s.width,
                        height: s.height,
                        top: s.top
                    });
                }
            });

            // Sort by z-index desc
            result.fixed_elements.sort(function(a,b) { return (parseInt(b.zIndex)||0) - (parseInt(a.zIndex)||0); });

            return result;
        })()""")

        print(f"\n[BLACK SCREEN ANALYSIS]")
        print(f"Body bg: {black_screen_state['body_style']}")
        print(f"Fixed elements (sorted by z-index):")
        for el in black_screen_state['fixed_elements']:
            print(f"  z={el['zIndex']} {el['tag']}#{el['id']}.{el['cls'][:50]} display={el['display']} bg={el['bg']} size={el['width']}x{el['height']}")

        # Try initPayTestFlow
        print(f"\n{'='*60}")
        print(f"STEP 7: Call initPayTestFlow directly")
        print(f"{'='*60}")

        init_result = await page.evaluate("""(function() {
            try {
                if (typeof window.initPayTestFlow === 'function') {
                    window.initPayTestFlow('Awakened', 'INIT-TEST');
                    return {called: true, error: null};
                }
                return {called: false, error: 'initPayTestFlow is ' + typeof window.initPayTestFlow};
            } catch(e) {
                return {called: false, error: e.toString(), stack: (e.stack||'').substring(0,800)};
            }
        })()""")
        print(f"[initPayTestFlow RESULT]: {json.dumps(init_result)}")

        await asyncio.sleep(3)
        await safe_screenshot(page, f"{OUT_DIR}/009-after-init-ptf.png")

        # Full console log summary
        print(f"\n{'='*60}")
        print(f"CONSOLE LOG SUMMARY")
        print(f"{'='*60}")

        print(f"\nALL ERRORS ({len([l for l in console_logs if l['type'] == 'error'])}):")
        for e in console_logs:
            if e['type'] == 'error':
                # Skip GA/analytics noise
                if 'google-analytics' not in e['text'] and 'secureserver' not in e['text'] and 'clarity' not in e['text']:
                    print(f"  [{e['time']}] {e['text'][:250]}")

        print(f"\nALL WARNINGS ({len([l for l in console_logs if l['type'] == 'warning'])}):")
        for e in console_logs:
            if e['type'] == 'warning':
                print(f"  [{e['time']}] {e['text'][:250]}")

        print(f"\nPB/PTC LOGS:")
        for e in console_logs:
            if e['type'] in ('log', 'info') and ('PB' in e['text'] or 'ptc' in e['text'].lower() or 'payment' in e['text'].lower() or 'chatbox' in e['text'].lower() or 'init' in e['text'].lower()):
                print(f"  [{e['time']}] {e['text'][:250]}")

        print(f"\nJS PAGE ERRORS ({len(js_errors)}):")
        for e in js_errors:
            print(f"  [{e['time']}] {e['error'][:300]}")

        # Save log
        log_path = f"{OUT_DIR}/console-log.json"
        with open(log_path, 'w') as f:
            json.dump({
                "console_logs": console_logs,
                "js_errors": js_errors,
                "network_errors": network_errors,
                "structure": structure,
                "post_sim": post_sim,
                "black_screen_state": black_screen_state,
                "function_sources": fn_sources
            }, f, indent=2)
        print(f"\n[LOG] Saved to {log_path}")

        await browser.close()
        print(f"\n[DONE] Screenshots: {OUT_DIR}/")

if __name__ == "__main__":
    asyncio.run(run())
