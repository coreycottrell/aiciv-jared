#!/usr/bin/env python3
"""
Full E2E test of pay-test-sandbox-3 birth pipeline.
Documents every step with screenshots and console logs.
Tests real PayPal sandbox flow.
Date: 2026-03-04
"""

import asyncio
import json
import time
import os
import sys
from datetime import datetime

OUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-e2e-20260304"
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-3/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
PAYPAL_EMAIL = "sb-c89tj49549583@personal.example.com"
PAYPAL_PASSWORD = "Z0+6<dS"

# Test persona
TEST_NAME = "Test User"
TEST_EMAIL = "testuser@example.com"
TEST_COMPANY = "Test Corp"
TEST_AI_NAME = "Sage"
TEST_ROLE = "Marketing Director"
TEST_GOAL = "Streamline content creation and customer outreach"

os.makedirs(OUT_DIR, exist_ok=True)

console_logs = []
network_calls = []
js_errors = []
birth_api_calls = []
seed_calls = []
step_log = []

def log_step(step_num, description, status="OK", details=""):
    entry = {
        "step": step_num,
        "description": description,
        "status": status,
        "details": details,
        "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]
    }
    step_log.append(entry)
    icon = "OK" if status == "OK" else ("FAIL" if status == "FAIL" else "INFO")
    print(f"\n[{icon}] Step {step_num}: {description}")
    if details:
        print(f"       {details}")

async def safe_screenshot(page, filename, label=""):
    path = f"{OUT_DIR}/{filename}"
    try:
        await page.screenshot(
            path=path,
            clip={"x": 0, "y": 0, "width": 1440, "height": 900},
            timeout=20000
        )
        print(f"[SHOT] {filename} - {label}")
        return path
    except Exception as e:
        print(f"[SHOT-FAIL] {filename}: {e}")
        try:
            await page.screenshot(path=path, clip={"x": 0, "y": 0, "width": 800, "height": 600}, timeout=25000)
            print(f"[SHOT-FALLBACK] {filename}")
            return path
        except Exception as e2:
            print(f"[SHOT-TOTAL-FAIL] {filename}: {e2}")
            return None

async def wait_for_element(page, selectors, timeout=30, description="element"):
    """Try multiple selectors, return first found."""
    if isinstance(selectors, str):
        selectors = [selectors]
    deadline = time.time() + timeout
    while time.time() < deadline:
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    return el, sel
            except:
                pass
        await asyncio.sleep(1)
    return None, None

async def wait_ptc_input_active(page, timeout=90):
    """Wait for PTC input row to become active (not display:none)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        display = await page.evaluate("""(function(){
            var row = document.getElementById('ptc-input-row');
            if (!row) return 'not-found';
            return window.getComputedStyle(row).display;
        })()""")
        if display not in ("none", "not-found"):
            return True
        await asyncio.sleep(1)
    return False

async def ptc_send(page, text, timeout=20):
    """Send message in PTC chatbox."""
    ta = await page.query_selector("#ptc-input")
    if not ta:
        ta = await page.query_selector("textarea.ptc-input")
    if not ta:
        return False, "no textarea found"
    try:
        await ta.click(timeout=5000)
        await asyncio.sleep(0.3)
        await ta.fill("")
        await asyncio.sleep(0.2)
        await ta.type(text, delay=30)
        await asyncio.sleep(0.5)
        send = await page.query_selector("#ptc-send-btn")
        if send and await send.is_visible():
            await send.click()
            return True, "sent via button"
        await ta.press("Enter")
        return True, "sent via Enter"
    except Exception as e:
        return False, str(e)

async def get_latest_ai_message(page):
    """Get text of most recent AI message."""
    msgs = await page.query_selector_all(".ptc-msg--ai")
    if not msgs:
        return None
    last = msgs[-1]
    return await last.inner_text()

async def run():
    from playwright.async_api import async_playwright

    print(f"\n{'='*70}")
    print(f"SANDBOX-3 FULL E2E TEST")
    print(f"URL: {PAGE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", "--disable-setuid-sandbox",
                "--disable-web-security", "--disable-gpu",
                "--disable-webgl", "--disable-3d-apis",
                "--disable-dev-shm-usage"
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True
        )
        page = await context.new_page()

        # --- Event listeners ---
        def on_console(msg):
            entry = {
                "type": msg.type,
                "text": msg.text,
                "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]
            }
            console_logs.append(entry)
            # Print relevant logs
            text = msg.text
            if msg.type in ('error', 'warning') or any(kw in text.lower() for kw in
                ['pb-', 'ptc', 'payment', 'birth', 'seed', 'oauth', 'paypal', 'verify', 'chatbox', 'awakened', 'partnered', 'sanitize']):
                print(f"  [CONSOLE:{msg.type.upper()}] {text[:300]}")

        def on_page_error(err):
            entry = {"error": str(err), "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]}
            js_errors.append(entry)
            print(f"  [JS-ERROR] {str(err)[:300]}")

        def on_request(req):
            url = req.url
            if 'purebrain.ai' in url or 'api.purebrain' in url:
                if any(kw in url for kw in ['birth', 'seed', 'verify', 'log-pay', 'log-conv', 'intake']):
                    network_calls.append({
                        "type": "REQUEST",
                        "url": url,
                        "method": req.method,
                        "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    })
                    print(f"  [API-REQ] {req.method} {url[:120]}")

        def on_response(resp):
            url = resp.url
            if any(kw in url for kw in ['birth', 'seed', 'verify', 'log-pay', 'log-conv', 'intake']):
                entry = {
                    "type": "RESPONSE",
                    "url": url,
                    "status": resp.status,
                    "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]
                }
                network_calls.append(entry)
                print(f"  [API-RESP] {resp.status} {url[:120]}")
                if 'birth' in url:
                    birth_api_calls.append(entry)
                if 'seed' in url:
                    seed_calls.append(entry)

        def on_request_failed(req):
            url = req.url
            if 'google-analytics' not in url and 'gtm' not in url and 'clarity' not in url and 'secureserver' not in url:
                print(f"  [NET-FAIL] {url[:120]} -> {req.failure}")

        page.on("console", on_console)
        page.on("pageerror", on_page_error)
        page.on("request", on_request)
        page.on("response", on_response)
        page.on("requestfailed", on_request_failed)

        # ===== STEP 1: Navigate =====
        log_step(1, f"Navigate to {PAGE_URL}")
        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        await safe_screenshot(page, "001-initial-page.png", "Initial page load")

        title = await page.title()
        url_now = page.url
        log_step(1, "Page loaded", "OK", f"Title: {title} | URL: {url_now}")

        # Check if password protected
        pw_inp = await page.query_selector('input[type="password"]')
        log_step(1, "Password gate check", "INFO", f"Password input found: {pw_inp is not None}")

        # ===== STEP 2: Enter password (if needed) =====
        if pw_inp:
            log_step(2, "Enter page password")
            await pw_inp.fill(PAGE_PASSWORD)
            sub = await page.query_selector('input[type="submit"]')
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            await asyncio.sleep(12)  # Wait for 3D scene to load
            await safe_screenshot(page, "002-after-password.png", "After password accepted")
            log_step(2, "Password submitted, page loaded", "OK")
        else:
            log_step(2, "No password gate - page already accessible", "INFO")
            await asyncio.sleep(5)

        # ===== STEP 3: Analyze page structure =====
        log_step(3, "Deep page structure analysis")

        structure = await page.evaluate("""(function() {
            var html = document.body.innerHTML;
            return {
                has_pricing: html.includes('Awakened') || html.includes('Partnered') || html.includes('Unified'),
                has_paypal_sdk: html.includes('paypal.com/sdk') || html.includes('paypalobjects'),
                has_bypass_btn: html.includes('bypass') || html.includes('Bypass') || html.includes('sandbox'),
                has_begin_awakening: html.includes('Begin Awakening') || html.includes('begin-awakening'),
                has_ptc: html.includes('ptc-wrapper') || html.includes('ptc-input'),
                inline_scripts: document.querySelectorAll('script:not([src])').length,
                external_scripts: Array.from(document.querySelectorAll('script[src]')).map(function(s) { return s.src; }).filter(function(s) { return s.includes('purebrain') || s.includes('pay-test'); }),
                paypal_iframes: Array.from(document.querySelectorAll('iframe')).map(function(f) { return {src: (f.src||'').substring(0,150), name: f.name||''}; }),
                key_functions: (function() {
                    var fns = {};
                    ['onPaymentComplete','launchPostPaymentFlow','initPayTestFlow','openPayPalModal','checkForPaymentReturn','sanitizeText'];
                    ['onPaymentComplete','launchPostPaymentFlow','initPayTestFlow','openPayPalModal','checkForPaymentReturn','sanitizeText'].forEach(function(fn) {
                        fns[fn] = typeof window[fn];
                    });
                    return fns;
                })()
            };
        })()""")

        print(f"\n[PAGE STRUCTURE]")
        print(f"  Has pricing tiers: {structure['has_pricing']}")
        print(f"  Has PayPal SDK: {structure['has_paypal_sdk']}")
        print(f"  Has bypass button: {structure['has_bypass_btn']}")
        print(f"  Has Begin Awakening: {structure['has_begin_awakening']}")
        print(f"  Has PTC: {structure['has_ptc']}")
        print(f"  Inline scripts: {structure['inline_scripts']}")
        print(f"  External scripts: {structure['external_scripts']}")
        print(f"  PayPal iframes: {len(structure['paypal_iframes'])}")
        print(f"  Key functions:")
        for fn, ftype in structure['key_functions'].items():
            print(f"    {fn}: {ftype}")

        log_step(3, "Page structure analyzed", "OK",
                 f"Pricing: {structure['has_pricing']}, PayPal: {structure['has_paypal_sdk']}, sanitizeText: {structure['key_functions'].get('sanitizeText','unknown')}")

        # ===== STEP 4: Find and scroll to pricing section =====
        log_step(4, "Scroll to find pricing/payment section")

        for scroll_y in [500, 1000, 1500, 2000, 2500, 3000, 4000]:
            await page.evaluate(f"window.scrollTo(0, {scroll_y})")
            await asyncio.sleep(0.8)

            # Check if pricing is visible
            pricing_visible = await page.evaluate("""(function() {
                var selectors = ['.pricing-section', '#pricing', '.price-cards', '[class*="pricing"]',
                                 '.paypal-button-container', '[id*="paypal"]', '.begin-awakening',
                                 '[class*="pay-btn"]'];
                for (var i = 0; i < selectors.length; i++) {
                    var el = document.querySelector(selectors[i]);
                    if (el) {
                        var rect = el.getBoundingClientRect();
                        if (rect.top >= 0 && rect.top <= window.innerHeight) {
                            return {found: true, selector: selectors[i], top: rect.top};
                        }
                    }
                }
                return {found: false};
            })()""")
            if pricing_visible['found']:
                print(f"  [FOUND] Pricing visible at scroll={scroll_y}, selector={pricing_visible['selector']}")
                await safe_screenshot(page, f"003-pricing-y{scroll_y}.png", f"Pricing at y={scroll_y}")
                break
        else:
            await safe_screenshot(page, "003-pricing-scroll.png", "Pricing scroll result")

        # ===== STEP 5: Find payment buttons =====
        log_step(5, "Find payment/PayPal buttons")

        await asyncio.sleep(2)

        # Look for all payment-related elements
        payment_elements = await page.evaluate("""(function() {
            var result = [];
            // Various selectors that might be payment buttons
            var selectors = [
                '.paypal-button-container', '[id*="paypal"]', '[class*="paypal"]',
                '[data-funding-source]', '.zoid-outlet',
                'iframe[name*="paypal"]', 'iframe[title*="PayPal"]',
                '.begin-awakening', '[class*="begin"]', 'button[class*="awakening"]',
                '.pay-btn', '[class*="pay-btn"]', '[id*="pay-btn"]',
                '.pricing-btn', '[class*="cta"]'
            ];
            selectors.forEach(function(sel) {
                var els = document.querySelectorAll(sel);
                els.forEach(function(el) {
                    var rect = el.getBoundingClientRect();
                    var style = window.getComputedStyle(el);
                    result.push({
                        selector: sel,
                        tag: el.tagName,
                        id: el.id || '',
                        cls: (el.className || '').substring(0, 80),
                        text: (el.textContent || '').trim().substring(0, 80),
                        visible: style.display !== 'none' && style.visibility !== 'hidden',
                        rect: {top: Math.round(rect.top), left: Math.round(rect.left),
                               width: Math.round(rect.width), height: Math.round(rect.height)},
                        scrollY: window.scrollY
                    });
                });
            });
            return result;
        })()""")

        print(f"\n[PAYMENT ELEMENTS FOUND: {len(payment_elements)}]")
        for el in payment_elements[:20]:
            print(f"  {el['tag']}#{el['id']}.{el['cls'][:40]} visible={el['visible']} text='{el['text'][:40]}' rect={el['rect']}")

        log_step(5, f"Found {len(payment_elements)} payment-related elements", "INFO")

        # ===== STEP 6: Try to click "Begin Awakening" or PayPal button =====
        log_step(6, "Scroll and locate 'Awakened' tier PayPal button")

        # First scroll to find the Awakened tier
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # Take screenshot of current full page to understand layout
        await safe_screenshot(page, "004-full-page-top.png", "Full page top view")

        # Scroll slowly and capture at each tier level
        found_paypal_btn = False
        paypal_btn_y = None

        for scroll_y in range(0, 6000, 300):
            await page.evaluate(f"window.scrollTo(0, {scroll_y})")
            await asyncio.sleep(0.3)

            # Check for visible PayPal button iframes
            iframe_info = await page.evaluate("""(function() {
                var iframes = document.querySelectorAll('iframe');
                var visible = [];
                for (var i = 0; i < iframes.length; i++) {
                    var f = iframes[i];
                    var rect = f.getBoundingClientRect();
                    var src = f.src || '';
                    var name = f.name || '';
                    if ((src.includes('paypal') || name.includes('paypal') || name.includes('zoid')) &&
                        rect.width > 10 && rect.height > 10 &&
                        rect.top >= -100 && rect.top <= window.innerHeight + 100) {
                        visible.push({
                            src: src.substring(0, 100),
                            name: name,
                            rect: {top: Math.round(rect.top), left: Math.round(rect.left),
                                   width: Math.round(rect.width), height: Math.round(rect.height)}
                        });
                    }
                }
                return visible;
            })()""")

            if iframe_info:
                print(f"  [PAYPAL-IFRAME-VISIBLE] at scrollY={scroll_y}: {len(iframe_info)} iframes")
                for f in iframe_info:
                    print(f"    name={f['name']} rect={f['rect']} src={f['src'][:60]}")
                found_paypal_btn = True
                paypal_btn_y = scroll_y
                await safe_screenshot(page, f"005-paypal-btn-y{scroll_y}.png", "PayPal button visible")
                break

        if not found_paypal_btn:
            # Try checking for bypass buttons on sandbox pages
            bypass_info = await page.evaluate("""(function() {
                var all = Array.from(document.querySelectorAll('button, a, input[type="button"]'));
                return all.filter(function(el) {
                    var t = (el.textContent || el.value || '').toLowerCase();
                    return t.includes('bypass') || t.includes('sandbox') || t.includes('begin') || t.includes('awaken') || t.includes('pay');
                }).map(function(el) {
                    var rect = el.getBoundingClientRect();
                    return {
                        tag: el.tagName,
                        text: (el.textContent || el.value || '').trim().substring(0, 80),
                        id: el.id || '',
                        cls: (el.className || '').substring(0, 60),
                        rect: {top: Math.round(rect.top), scrollY: window.scrollY}
                    };
                });
            })()""")
            print(f"\n[BYPASS/PAY BUTTONS]: {len(bypass_info)}")
            for b in bypass_info:
                print(f"  {b['tag']}#{b['id']} text='{b['text']}' top={b['rect']['top']}")

        log_step(6, f"PayPal button search complete", "INFO",
                 f"Found: {found_paypal_btn}, at y={paypal_btn_y}")

        # ===== STEP 7: Click PayPal button to open modal =====
        log_step(7, "Click PayPal button / trigger payment modal")

        if found_paypal_btn and paypal_btn_y is not None:
            await page.evaluate(f"window.scrollTo(0, {paypal_btn_y})")
            await asyncio.sleep(1)

            # Get all visible PayPal iframes at this scroll position
            iframes = await page.frames
            paypal_frames = []
            for frame in iframes:
                try:
                    frame_url = frame.url
                    frame_name = frame.name
                    if 'paypal' in frame_url.lower() or 'paypal' in frame_name.lower() or 'zoid' in frame_name.lower():
                        # Try to find buttons in this frame
                        try:
                            btn = await frame.query_selector('button, [role="button"], .paypal-button')
                            if btn:
                                paypal_frames.append((frame, btn, frame_name, frame_url))
                        except:
                            pass
                except:
                    pass

            print(f"  [PAYPAL FRAMES WITH BUTTONS]: {len(paypal_frames)}")

            clicked = False
            for frame, btn, fname, furl in paypal_frames:
                try:
                    print(f"  [CLICK] Attempting click in frame: {fname} url={furl[:80]}")
                    await btn.click(timeout=5000)
                    clicked = True
                    print(f"  [CLICK-OK] Clicked PayPal button in frame: {fname}")
                    break
                except Exception as e:
                    print(f"  [CLICK-FAIL] {e}")

            if not clicked:
                # Try clicking directly on the iframe position in page
                print(f"  [DIRECT-CLICK] Trying direct coordinate click on PayPal button area")
                # Find iframe bounds and click center
                iframe_bounds = await page.evaluate(f"""(function() {{
                    var iframes = document.querySelectorAll('iframe');
                    for (var i = 0; i < iframes.length; i++) {{
                        var f = iframes[i];
                        if ((f.src||'').includes('paypal') || (f.name||'').includes('paypal') || (f.name||'').includes('zoid')) {{
                            var rect = f.getBoundingClientRect();
                            if (rect.width > 10 && rect.height > 10) {{
                                return {{
                                    x: Math.round(rect.left + rect.width/2),
                                    y: Math.round(rect.top + rect.height/2),
                                    found: true
                                }};
                            }}
                        }}
                    }}
                    return {{found: false}};
                }})()""")

                if iframe_bounds.get('found'):
                    await page.mouse.click(iframe_bounds['x'], iframe_bounds['y'])
                    print(f"  [DIRECT-CLICK] Clicked at ({iframe_bounds['x']}, {iframe_bounds['y']})")
                    clicked = True

            await asyncio.sleep(3)
            await safe_screenshot(page, "006-after-paypal-click.png", "After PayPal click")

            # Check for PayPal popup/modal
            popup_check = await page.evaluate("""(function() {
                return {
                    modal_visible: !!document.querySelector('.paypal-overlay, .zoid-visible, [class*="paypal-modal"]'),
                    new_iframes: Array.from(document.querySelectorAll('iframe')).filter(function(f) {
                        return (f.src||'').includes('checkout.paypal') || (f.name||'').includes('paypal_');
                    }).map(function(f) { return {src: (f.src||'').substring(0,100), name: f.name}; })
                };
            })()""")
            print(f"  [POST-CLICK]: modal={popup_check['modal_visible']}, new_iframes={popup_check['new_iframes']}")
        else:
            log_step(7, "PayPal button not found - checking for sandbox bypass", "WARN")
            # Check for sandbox bypass code input or begin-awakening button
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
            bypass_el, bypass_sel = await wait_for_element(
                page,
                ['[class*="bypass"]', '#bypass-code', '.sandbox-bypass', 'input[placeholder*="bypass"]',
                 'input[placeholder*="code"]', '.begin-awakening-btn', '[class*="begin-awakening"]'],
                timeout=5,
                description="bypass element"
            )
            if bypass_el:
                print(f"  [BYPASS-FOUND] {bypass_sel}")
                await safe_screenshot(page, "006-bypass-element.png", "Bypass element found")
            else:
                print(f"  [NO-BYPASS-FOUND] Will try simulation approach")

        # ===== STEP 8: Handle PayPal popup/new page =====
        log_step(8, "Handle PayPal sandbox login")

        # Wait for potential popup
        popup = None
        try:
            async with asyncio.timeout(10):
                popup = await context.wait_for_event("page", timeout=10000)
                print(f"  [POPUP-DETECTED] New page: {popup.url}")
        except (asyncio.TimeoutError, Exception) as e:
            print(f"  [NO-POPUP] {e}")

        if popup:
            await popup.wait_for_load_state("domcontentloaded", timeout=15000)
            await asyncio.sleep(2)
            await popup.screenshot(
                path=f"{OUT_DIR}/007-paypal-popup.png",
                clip={"x": 0, "y": 0, "width": 1440, "height": 900},
                timeout=15000
            )
            print(f"  [POPUP-URL] {popup.url}")

            # Try to login to PayPal sandbox
            email_field = await popup.query_selector('#email, input[name="login_email"], input[type="email"]')
            if email_field:
                log_step(8, "PayPal login form found - entering credentials", "OK")
                await email_field.fill(PAYPAL_EMAIL)
                await asyncio.sleep(0.5)

                # Try Next button first (PayPal 2-step)
                next_btn = await popup.query_selector('#btnNext, button[type="submit"], .btn-primary')
                if next_btn:
                    await next_btn.click()
                    await asyncio.sleep(2)
                    await popup.screenshot(
                        path=f"{OUT_DIR}/008-paypal-after-email.png",
                        clip={"x": 0, "y": 0, "width": 1440, "height": 900},
                        timeout=15000
                    )

                # Password field
                pw_field = await popup.query_selector('#password, input[name="login_password"], input[type="password"]')
                if pw_field:
                    await pw_field.fill(PAYPAL_PASSWORD)
                    await asyncio.sleep(0.3)
                    login_btn = await popup.query_selector('#btnLogin, button[type="submit"], .btn-primary')
                    if login_btn:
                        await login_btn.click()
                        await asyncio.sleep(5)
                        await popup.screenshot(
                            path=f"{OUT_DIR}/009-paypal-after-login.png",
                            clip={"x": 0, "y": 0, "width": 1440, "height": 900},
                            timeout=15000
                        )
                        login_url = popup.url
                        print(f"  [POST-LOGIN-URL] {login_url}")
                        log_step(8, f"PayPal login submitted", "INFO", f"URL: {login_url}")
            else:
                log_step(8, "PayPal login form NOT found in popup", "WARN", f"URL: {popup.url}")
                await popup.screenshot(
                    path=f"{OUT_DIR}/008-paypal-no-login.png",
                    clip={"x": 0, "y": 0, "width": 1440, "height": 900},
                    timeout=15000
                )
        else:
            log_step(8, "No PayPal popup detected - checking main page for inline modal", "INFO")
            # Check if PayPal loaded in an iframe on the main page
            await safe_screenshot(page, "008-main-page-no-popup.png", "Main page - no popup")

        # ===== STEP 9: Check for sandbox bypass route =====
        log_step(9, "Check for sandbox bypass / post-payment simulation")

        await asyncio.sleep(2)

        # Check if there's a sandbox bypass mechanism on the page
        bypass_state = await page.evaluate("""(function() {
            var html = document.body.innerHTML;
            return {
                has_bypass_input: html.includes('bypass') || html.includes('sandbox-code'),
                has_paypal_overlay: !!document.querySelector('.paypal-overlay, .zoid-visible'),
                has_sandbox_btn: Array.from(document.querySelectorAll('button')).filter(function(b) {
                    return (b.textContent||'').toLowerCase().includes('sandbox') || (b.textContent||'').toLowerCase().includes('bypass');
                }).map(function(b) { return {text: b.textContent.trim().substring(0,60), cls: b.className.substring(0,60)}; }),
                ptc_visible: !!document.querySelector('#ptc-input, .ptc-input, #ptc-wrapper'),
                post_payment_div: (function() {
                    var el = document.getElementById('pay-test-post-payment');
                    if (!el) return null;
                    var s = window.getComputedStyle(el);
                    return {display: s.display, children: el.children.length, visibility: s.visibility};
                })()
            };
        })()""")

        print(f"\n[BYPASS STATE]")
        print(f"  has_bypass_input: {bypass_state['has_bypass_input']}")
        print(f"  has_paypal_overlay: {bypass_state['has_paypal_overlay']}")
        print(f"  sandbox_buttons: {bypass_state['has_sandbox_btn']}")
        print(f"  ptc_visible: {bypass_state['ptc_visible']}")
        print(f"  post_payment_div: {bypass_state['post_payment_div']}")

        # Try simulating payment if no popup and no bypass found
        if not popup and not bypass_state['ptc_visible']:
            log_step(9, "Simulating onPaymentComplete to trigger chatbox", "INFO",
                     "Real PayPal not accessible - using JS simulation")

            sim_result = await page.evaluate("""(function() {
                try {
                    if (typeof window.onPaymentComplete === 'function') {
                        window.onPaymentComplete('Awakened', 'E2E-TEST-'+Date.now(), {});
                        return {called: true, fn_type: 'function'};
                    }
                    return {called: false, reason: 'onPaymentComplete is ' + typeof window.onPaymentComplete};
                } catch(e) {
                    return {called: false, reason: e.toString(), stack: (e.stack||'').substring(0,500)};
                }
            })()""")

            print(f"  [SIM-RESULT] {json.dumps(sim_result, indent=2)}")
            log_step(9, f"Payment simulation result", "OK" if sim_result.get('called') else "FAIL",
                     str(sim_result))

            await asyncio.sleep(3)
            await safe_screenshot(page, "009-after-simulation.png", "After payment simulation")

        # ===== STEP 10: Wait for PTC chatbox =====
        log_step(10, "Wait for PTC post-payment chatbox to appear")

        ptc_active = await wait_ptc_input_active(page, timeout=45)

        await safe_screenshot(page, "010-ptc-state.png", "PTC state after wait")

        if ptc_active:
            log_step(10, "PTC chatbox is ACTIVE (input visible)", "OK")
        else:
            log_step(10, "PTC chatbox did NOT become active within timeout", "FAIL")

        # Get the current chatbox state regardless
        chatbox_state = await page.evaluate("""(function() {
            var result = {
                ptc_input: null,
                ptc_wrapper: null,
                post_payment_div: null,
                all_messages: [],
                visible_text: '',
                fixed_elements: []
            };

            // Check PTC input
            var inp = document.getElementById('ptc-input') || document.querySelector('.ptc-input');
            if (inp) {
                var s = window.getComputedStyle(inp);
                result.ptc_input = {display: s.display, visibility: s.visibility};
            }

            // Check PTC wrapper
            var wrapper = document.getElementById('ptc-wrapper') || document.querySelector('.ptc-wrapper');
            if (wrapper) {
                var s = window.getComputedStyle(wrapper);
                result.ptc_wrapper = {display: s.display, visibility: s.visibility, children: wrapper.children.length};
            }

            // Check post-payment div
            var ppd = document.getElementById('pay-test-post-payment');
            if (ppd) {
                var s = window.getComputedStyle(ppd);
                result.post_payment_div = {
                    display: s.display,
                    visibility: s.visibility,
                    children: ppd.children.length,
                    inner_text: ppd.innerText.substring(0, 500),
                    inner_html_len: ppd.innerHTML.length
                };
            }

            // Get all AI messages
            document.querySelectorAll('.ptc-msg--ai').forEach(function(m) {
                result.all_messages.push({type: 'ai', text: m.innerText.substring(0, 200)});
            });
            document.querySelectorAll('.ptc-msg--user').forEach(function(m) {
                result.all_messages.push({type: 'user', text: m.innerText.substring(0, 200)});
            });

            // Get all visible text from chatbox area
            if (ppd) {
                result.visible_text = ppd.innerText.substring(0, 1000);
            }

            // Check for OAuth elements
            result.has_oauth_url = document.body.innerHTML.includes('claude.ai') || document.body.innerHTML.includes('oauth');
            result.has_portal_btn = !!document.querySelector('.ptc-portal-btn, [class*="portal-btn"], [class*="brain-stream"]');
            result.has_input_row = (function() {
                var row = document.getElementById('ptc-input-row');
                if (!row) return 'not-found';
                return window.getComputedStyle(row).display;
            })();

            return result;
        })()""")

        print(f"\n[CHATBOX STATE]")
        print(f"  ptc_input: {chatbox_state['ptc_input']}")
        print(f"  ptc_wrapper: {chatbox_state['ptc_wrapper']}")
        print(f"  post_payment_div: {chatbox_state['post_payment_div']}")
        print(f"  messages: {len(chatbox_state['all_messages'])}")
        print(f"  has_oauth_url: {chatbox_state['has_oauth_url']}")
        print(f"  has_portal_btn: {chatbox_state['has_portal_btn']}")
        print(f"  input_row_display: {chatbox_state['has_input_row']}")
        print(f"\n  VISIBLE TEXT:\n{chatbox_state['visible_text'][:500]}")
        for msg in chatbox_state['all_messages']:
            print(f"  [{msg['type'].upper()}] {msg['text'][:150]}")

        log_step(10, "Chatbox state captured", "OK",
                 f"Messages: {len(chatbox_state['all_messages'])}, PTC active: {ptc_active}")

        # ===== STEP 11: Interact with chatbox =====
        log_step(11, "Begin chatbox Q&A interaction")

        if ptc_active:
            # Get first AI message (should be asking for name)
            await asyncio.sleep(2)
            first_msg = await get_latest_ai_message(page)
            print(f"\n  [FIRST-AI-MSG]: {first_msg}")

            # Track Q&A sequence
            qa_sequence = []

            # Q1: Name
            log_step(11, f"Sending name: {TEST_NAME}")
            ok, how = await ptc_send(page, TEST_NAME)
            print(f"  [SEND NAME] ok={ok}, how={how}")
            await asyncio.sleep(4)
            await safe_screenshot(page, "011-name-sent.png", "After name sent")
            ai_resp = await get_latest_ai_message(page)
            qa_sequence.append({"q": f"Name: {TEST_NAME}", "ai_next": ai_resp})
            print(f"  [AI-AFTER-NAME]: {ai_resp}")

            # Q2: Email
            log_step(11, f"Sending email: {TEST_EMAIL}")
            ok, how = await ptc_send(page, TEST_EMAIL)
            print(f"  [SEND EMAIL] ok={ok}, how={how}")
            await asyncio.sleep(4)
            await safe_screenshot(page, "012-email-sent.png", "After email sent")
            ai_resp = await get_latest_ai_message(page)
            qa_sequence.append({"q": f"Email: {TEST_EMAIL}", "ai_next": ai_resp})
            print(f"  [AI-AFTER-EMAIL]: {ai_resp}")

            # Q3: Company (or AI name - depends on version)
            # Check what the AI is asking for
            if ai_resp and ('company' in ai_resp.lower() or 'organization' in ai_resp.lower() or 'business' in ai_resp.lower()):
                send_val = TEST_COMPANY
                q_label = "Company"
            elif ai_resp and ('name' in ai_resp.lower() and 'ai' in ai_resp.lower()):
                send_val = TEST_AI_NAME
                q_label = "AI name"
            else:
                send_val = TEST_COMPANY
                q_label = "Company (default)"

            log_step(11, f"Sending {q_label}: {send_val}")
            ok, how = await ptc_send(page, send_val)
            print(f"  [SEND {q_label.upper()}] ok={ok}, how={how}")
            await asyncio.sleep(4)
            await safe_screenshot(page, "013-third-answer-sent.png", "After third answer")
            ai_resp = await get_latest_ai_message(page)
            qa_sequence.append({"q": f"{q_label}: {send_val}", "ai_next": ai_resp})
            print(f"  [AI-AFTER-{q_label.upper()}]: {ai_resp}")

            # Q4: AI name (if not already asked)
            if ai_resp and ('ai' in ai_resp.lower() and 'name' in ai_resp.lower()):
                log_step(11, f"Sending AI name: {TEST_AI_NAME}")
                ok, how = await ptc_send(page, TEST_AI_NAME)
                await asyncio.sleep(4)
                await safe_screenshot(page, "014-ai-name-sent.png", "After AI name sent")
                ai_resp = await get_latest_ai_message(page)
                qa_sequence.append({"q": f"AI name: {TEST_AI_NAME}", "ai_next": ai_resp})
                print(f"  [AI-AFTER-AI-NAME]: {ai_resp}")

            # Q5: Role
            if ai_resp and 'role' in ai_resp.lower():
                log_step(11, f"Sending role: {TEST_ROLE}")
                ok, how = await ptc_send(page, TEST_ROLE)
                await asyncio.sleep(4)
                await safe_screenshot(page, "015-role-sent.png", "After role sent")
                ai_resp = await get_latest_ai_message(page)
                qa_sequence.append({"q": f"Role: {TEST_ROLE}", "ai_next": ai_resp})
                print(f"  [AI-AFTER-ROLE]: {ai_resp}")

            # Q6: Goal (if asked - may get replaced by OAuth overlay after BIRTH fires)
            if ai_resp and any(kw in ai_resp.lower() for kw in ['goal', 'hope', 'achieve', 'accomplish']):
                try:
                    log_step(11, f"Sending goal: {TEST_GOAL}")
                    ok, how = await ptc_send(page, TEST_GOAL)
                    await asyncio.sleep(4)
                    ai_resp = await get_latest_ai_message(page)
                    qa_sequence.append({"q": f"Goal: {TEST_GOAL}", "ai_next": ai_resp})
                    print(f"  [AI-AFTER-GOAL]: {ai_resp}")
                except Exception as e:
                    print(f"  [GOAL-SEND-EXCEPTION] {e} - likely BIRTH fired and overlaid UI")
                    qa_sequence.append({"q": f"Goal: {TEST_GOAL}", "ai_next": f"EXCEPTION: {e}"})

            await safe_screenshot(page, "016-after-qa.png", "After full Q&A")

            print(f"\n[QA SEQUENCE SUMMARY]")
            for i, qa in enumerate(qa_sequence, 1):
                print(f"  {i}. Sent: {qa['q']}")
                print(f"     AI replied: {(qa['ai_next'] or '')[:100]}")

            log_step(11, "Q&A sequence completed", "OK",
                     f"{len(qa_sequence)} exchanges completed")
        else:
            log_step(11, "Skipping Q&A - chatbox not active", "FAIL")

        # ===== STEP 12: Check for OAuth / portal button =====
        log_step(12, "Check for OAuth gate and portal button")

        await asyncio.sleep(3)
        await safe_screenshot(page, "017-check-oauth-portal.png", "Check OAuth/portal state")

        final_state = await page.evaluate("""(function() {
            var result = {
                oauth_elements: [],
                portal_buttons: [],
                brain_stream_buttons: [],
                current_messages: [],
                has_claude_ai_link: false,
                all_links: [],
                input_row: null
            };

            // Find OAuth-related elements
            document.querySelectorAll('a, button').forEach(function(el) {
                var href = el.href || '';
                var text = (el.textContent || '').trim();
                var cls = (el.className || '');

                if (href.includes('claude.ai') || href.includes('oauth') || text.toLowerCase().includes('authorize')) {
                    result.oauth_elements.push({
                        tag: el.tagName, text: text.substring(0,80), href: href.substring(0,150),
                        cls: cls.substring(0,60)
                    });
                    result.has_claude_ai_link = true;
                }

                if (cls.includes('portal') || text.toLowerCase().includes('brain stream') ||
                    text.toLowerCase().includes('enter') && text.toLowerCase().includes('brain')) {
                    result.portal_buttons.push({
                        tag: el.tagName, text: text.substring(0,80), href: href.substring(0,150),
                        cls: cls.substring(0,60),
                        disabled: el.disabled || cls.includes('disabled') || cls.includes('greyed'),
                        style: window.getComputedStyle(el).opacity
                    });
                }

                if (text.toLowerCase().includes('brain stream') || text.toLowerCase().includes('brain')) {
                    result.brain_stream_buttons.push({
                        tag: el.tagName, text: text.substring(0,80), href: href.substring(0,150)
                    });
                }
            });

            // Get all current messages
            document.querySelectorAll('.ptc-msg--ai, .ptc-msg--user').forEach(function(m) {
                result.current_messages.push({
                    type: m.className.includes('ai') ? 'ai' : 'user',
                    text: m.innerText.substring(0, 300)
                });
            });

            // Input row state
            var row = document.getElementById('ptc-input-row');
            if (row) {
                result.input_row = window.getComputedStyle(row).display;
            }

            // Check for "I have my key" button (OAuth stage)
            var i_have_key = Array.from(document.querySelectorAll('button, [role="button"]')).filter(function(el) {
                var t = (el.textContent||'').toLowerCase();
                return t.includes('have') && t.includes('key');
            });
            result.i_have_key_buttons = i_have_key.map(function(el) {
                return {text: el.textContent.trim().substring(0,80), cls: el.className.substring(0,60)};
            });

            return result;
        })()""")

        print(f"\n[FINAL STATE ANALYSIS]")
        print(f"  OAuth elements: {len(final_state['oauth_elements'])}")
        for o in final_state['oauth_elements']:
            print(f"    {o['tag']}: {o['text']} -> {o['href'][:80]}")

        print(f"  Portal buttons: {len(final_state['portal_buttons'])}")
        for p in final_state['portal_buttons']:
            print(f"    {p['tag']}: '{p['text']}' href={p['href'][:80]} disabled={p['disabled']} opacity={p['style']}")

        print(f"  Brain stream buttons: {len(final_state['brain_stream_buttons'])}")
        for b in final_state['brain_stream_buttons']:
            print(f"    {b['tag']}: '{b['text']}' href={b['href'][:80]}")

        print(f"  'I have my key' buttons: {len(final_state['i_have_key_buttons'])}")
        for b in final_state['i_have_key_buttons']:
            print(f"    '{b['text']}'")

        print(f"  Has claude.ai link: {final_state['has_claude_ai_link']}")
        print(f"  Input row: {final_state['input_row']}")

        print(f"\n  ALL CURRENT MESSAGES ({len(final_state['current_messages'])}):")
        for msg in final_state['current_messages']:
            print(f"  [{msg['type'].upper()}]: {msg['text'][:150]}")

        log_step(12, "OAuth/portal check complete", "OK",
                 f"oauth_elements={len(final_state['oauth_elements'])}, portal_buttons={len(final_state['portal_buttons'])}, has_claude_ai={final_state['has_claude_ai_link']}")

        # ===== STEP 13: Birth API status =====
        log_step(13, "Birth API call status summary")

        print(f"\n[BIRTH API CALLS]: {len(birth_api_calls)}")
        for call in birth_api_calls:
            print(f"  {call['type']} {call.get('status','')} {call['url'][:100]} @ {call['time']}")

        print(f"\n[SEED API CALLS]: {len(seed_calls)}")
        for call in seed_calls:
            print(f"  {call['type']} {call.get('status','')} {call['url'][:100]} @ {call['time']}")

        print(f"\n[ALL API CALLS]: {len(network_calls)}")
        for call in network_calls:
            print(f"  {call['type']} {call.get('status','')} {call.get('method','')} {call['url'][:100]} @ {call['time']}")

        # ===== FINAL SCREENSHOTS =====
        log_step(14, "Final comprehensive screenshots")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        await safe_screenshot(page, "018-final-top.png", "Final state - top")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        await safe_screenshot(page, "019-final-bottom.png", "Final state - bottom")

        # ===== CONSOLE LOG SUMMARY =====
        print(f"\n{'='*60}")
        print(f"CONSOLE LOG SUMMARY")
        print(f"{'='*60}")

        errors = [l for l in console_logs if l['type'] == 'error']
        warnings = [l for l in console_logs if l['type'] == 'warning']
        pb_logs = [l for l in console_logs if any(kw in l['text'].lower() for kw in
                   ['pb-', 'ptc', 'payment', 'birth', 'seed', 'oauth', 'awakened', 'chatbox', 'init'])]

        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            if not any(n in e['text'] for n in ['google-analytics', 'clarity', 'secureserver']):
                print(f"  [{e['time']}] {e['text'][:250]}")

        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings[:10]:
            print(f"  [{w['time']}] {w['text'][:200]}")

        print(f"\nPB/PTC LOGS ({len(pb_logs)}):")
        for l in pb_logs:
            print(f"  [{l['time']}] [{l['type'].upper()}] {l['text'][:250]}")

        print(f"\nJS PAGE ERRORS ({len(js_errors)}):")
        for e in js_errors:
            print(f"  [{e['time']}] {e['error'][:300]}")

        # Save full log
        log_data = {
            "test_date": datetime.now().isoformat(),
            "page_url": PAGE_URL,
            "step_log": step_log,
            "console_logs": console_logs,
            "js_errors": js_errors,
            "network_calls": network_calls,
            "birth_api_calls": birth_api_calls,
            "seed_calls": seed_calls,
            "page_structure": structure,
            "chatbox_state": chatbox_state,
            "final_state": final_state,
            "ptc_active": ptc_active
        }

        log_path = f"{OUT_DIR}/full-test-log.json"
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)
        print(f"\n[LOG SAVED] {log_path}")

        await browser.close()

        print(f"\n{'='*60}")
        print(f"TEST COMPLETE")
        print(f"Screenshots: {OUT_DIR}/")
        print(f"Log: {log_path}")
        print(f"{'='*60}")

        return log_data

if __name__ == "__main__":
    asyncio.run(run())
