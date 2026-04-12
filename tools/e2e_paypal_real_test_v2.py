#!/usr/bin/env python3
"""
Full E2E PayPal Sandbox Real Test v2 - PureBrain Pay-Test-Sandbox-2
Date: 2026-03-02
REAL PayPal sandbox payment.

Strategy:
- headless=True (no X11 needed)
- Intercept PayPal popup via context.wait_for_event("page")
- Full network monitoring of all seed endpoints
- Screenshots at every key stage
- Complete conversation flow through post-payment questionnaire

Memory patterns applied from 2026-03-02 memory:
- JS click for off-viewport elements
- dispatchEvent for textarea
- page.type() for chatbox
- No full_page=True
- 10s screenshot timeout
- WAF-safe: use live URL
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# ---- CONFIG ----
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-paypal-real-20260302")
REPORT_PATH = Path("/home/jared/projects/AI-CIV/aether/exports/e2e-paypal-real-report-20260302.md")

PAYPAL_EMAIL = "sb-c89tj49549583@personal.example.com"
PAYPAL_PASSWORD = "Z0+6<dS"

MONITORED_ENDPOINTS = [
    "api.purebrain.ai/api/intake/seed",
    "api.purebrain.ai/api/log-conversation",
    "api.purebrain.ai/api/log-pay-test",
    "api.purebrain.ai/api/verify-payment",
    "api.purebrain.ai/api/birth",
    "purebrain.ai/wp-json",
]

timeline = []
network_calls = []
screenshots_taken = []
seed_fires = []
counter = [0]
console_logs = []


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(msg, cat="ACTION"):
    entry = f"[{ts()}] [{cat}] {msg}"
    timeline.append(entry)
    print(entry)


async def ss(page, label):
    counter[0] += 1
    n = counter[0]
    fname = f"{n:03d}-{label}.png"
    fpath = SCREENSHOT_DIR / fname
    try:
        await page.screenshot(path=str(fpath), timeout=10000)
        screenshots_taken.append(str(fpath))
        log(f"Screenshot: {fname}", "SS")
        return str(fpath)
    except Exception as e:
        log(f"Screenshot failed [{label}]: {e}", "WARN")
        return None


def attach_monitors(page, label="main"):
    """Attach network + console monitors to a page."""

    async def on_response(resp):
        url = resp.url
        for ep in MONITORED_ENDPOINTS:
            if ep in url:
                try:
                    body = await resp.body()
                    body_txt = body.decode("utf-8", errors="replace")[:300]
                except Exception:
                    body_txt = "(unreadable)"
                entry = {
                    "page": label,
                    "ts": ts(),
                    "method": resp.request.method,
                    "status": resp.status,
                    "url": url,
                    "body": body_txt,
                }
                network_calls.append(entry)
                if "seed" in url or "intake" in url:
                    seed_fires.append(entry)
                    log(f"SEED FIRE: {resp.status} {url} -> {body_txt[:100]}", "SEED")
                else:
                    log(f"API: {resp.status} {url[:80]} | {body_txt[:60]}", "NET")

    async def on_console(msg):
        txt = msg.text
        if any(x in txt for x in ["seed", "Seed", "SEED", "birth", "Birth", "payment", "Payment",
                                     "fireSeed", "oauth", "OAuth", "error", "Error", "PB-FIX",
                                     "intake", "linking", "awaken", "ChatboxV"]):
            log(f"CONSOLE[{label}][{msg.type}]: {txt[:120]}", "CON")
            console_logs.append({"page": label, "type": msg.type, "text": txt, "ts": ts()})

    page.on("response", on_response)
    page.on("console", on_console)


async def wait_for_ai(page, current_count, sel=".ptc-msg--ai, .ptc-msg.ptc-msg--ai", timeout=30):
    """Wait for at least one new AI message."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        msgs = await page.query_selector_all(sel)
        if len(msgs) > current_count:
            await asyncio.sleep(2)
            msgs = await page.query_selector_all(sel)
            texts = []
            for m in msgs:
                t = await m.inner_text()
                texts.append(t.strip()[:80])
            last = texts[-1] if texts else "?"
            log(f"AI response ({len(msgs)} total). Last: {last}", "AI")
            return len(msgs)
        await asyncio.sleep(0.5)
    log(f"Timeout waiting for AI (had {current_count} msgs)", "WARN")
    return current_count


async def ptc_send(page, text):
    """Send a message in post-payment chatbox using page.type()."""
    # Try various selectors
    for sel in ["#ptc-input", "textarea.ptc-input", ".ptc-input", "textarea"]:
        el = await page.query_selector(sel)
        if el:
            try:
                visible = await el.is_visible()
                enabled = await el.is_enabled()
                if visible and enabled:
                    await el.click()
                    await asyncio.sleep(0.2)
                    await el.fill("")
                    await el.type(text, delay=20)
                    await asyncio.sleep(0.3)

                    # Submit
                    for sbtn in ["#ptc-send", ".ptc-send", ".ptc-send-btn", "button[type=submit]"]:
                        sbel = await page.query_selector(sbtn)
                        if sbel:
                            await sbel.click()
                            log(f"PTC sent via {sel} + {sbtn}: {text[:40]}", "ACTION")
                            return True

                    # Try Enter
                    await el.press("Enter")
                    log(f"PTC sent via {sel} + Enter: {text[:40]}", "ACTION")
                    return True
            except Exception as e:
                log(f"ptc_send error on {sel}: {e}", "WARN")
    log(f"PTC send failed: {text[:40]}", "ERROR")
    return False


async def run():
    log("=== E2E PayPal Real Sandbox Test v2 Starting ===", "START")
    log(f"Target: {PAGE_URL}", "INFO")
    log(f"PayPal Account: {PAYPAL_EMAIL}", "INFO")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            ignore_https_errors=True,
        )

        page = await ctx.new_page()
        attach_monitors(page, "main")

        # ==================
        # PHASE 1: PAGE ACCESS + PASSWORD
        # ==================
        log("=== PHASE 1: Page Access ===", "PHASE")
        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        await ss(page, "p1a-initial")

        pw_inp = await page.query_selector('input[type="password"]')
        if pw_inp:
            log("Password prompt - entering", "ACTION")
            await pw_inp.fill(PAGE_PASSWORD)
            sub = await page.query_selector('input[type="submit"]')
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            await asyncio.sleep(10)
            log("Password submitted, waiting for page render", "ACTION")
        else:
            log("No password prompt", "INFO")

        await ss(page, "p1b-after-password")

        # ==================
        # PHASE 2: CHAT WITH AI
        # ==================
        log("=== PHASE 2: Chat with AI ===", "PHASE")

        # Click Begin Awakening
        begin_found = await page.evaluate("""
            var btn = document.querySelector('.chat-initial__btn');
            if (btn) { btn.click(); return 'chat-initial__btn clicked'; }
            var btns = document.querySelectorAll('button');
            for (var b of btns) {
                if (b.textContent.includes('Awaken') || b.textContent.includes('PURE BRAIN')) {
                    b.click();
                    return 'awaken-btn: ' + b.textContent.trim().substring(0,30);
                }
            }
            return 'not-found';
        """)
        log(f"Begin click: {begin_found}", "ACTION")
        await asyncio.sleep(6)
        await ss(page, "p2a-after-begin")

        # Check for AI first message in pre-payment chatbox
        first_msg = await page.evaluate("""
            var msgs = document.querySelectorAll('.chat-message, .ai-message, [class*=ai-msg], .message-ai');
            var texts = [];
            for (var m of msgs) texts.push(m.textContent.trim().substring(0, 60));
            return texts;
        """)
        log(f"Pre-payment AI msgs: {first_msg}", "AI")

        # Send first message
        log("Sending: Hi! My name is TestUser. I run a marketing agency.", "ACTION")
        await page.evaluate("""
            var inp = document.getElementById('userInput');
            if (inp) {
                inp.value = 'Hi! My name is TestUser. I run a marketing agency.';
                inp.dispatchEvent(new Event('input', {bubbles: true}));
            }
            var sub = document.getElementById('submitBtn');
            if (sub) sub.click();
        """)
        await asyncio.sleep(8)
        await ss(page, "p2b-first-msg")

        # Second message
        log("Sending: I'd love to call you Nova. Does that feel right?", "ACTION")
        await page.evaluate("""
            var inp = document.getElementById('userInput');
            if (inp) {
                inp.value = "I'd love to call you Nova. Does that feel right?";
                inp.dispatchEvent(new Event('input', {bubbles: true}));
            }
            var sub = document.getElementById('submitBtn');
            if (sub) sub.click();
        """)
        await asyncio.sleep(8)
        await ss(page, "p2c-nova-msg")

        # Check AI messages
        chat_state = await page.evaluate("""
            var msgs = document.querySelectorAll('.chat-message, .ai-message, [class*=ai-msg], .message-ai, .chat-msg-ai');
            var data = {count: msgs.length, texts: []};
            for (var i = 0; i < Math.min(msgs.length, 3); i++) data.texts.push(msgs[i].textContent.trim().substring(0,80));
            return data;
        """)
        log(f"Chat state: {chat_state}", "INFO")

        # Third message - ask for pricing
        log("Sending: I'm convinced. I want to get started. What are my options?", "ACTION")
        await page.evaluate("""
            var inp = document.getElementById('userInput');
            if (inp) {
                inp.value = "I'm convinced. I want to get started. What are my options?";
                inp.dispatchEvent(new Event('input', {bubbles: true}));
            }
            var sub = document.getElementById('submitBtn');
            if (sub) sub.click();
        """)
        await asyncio.sleep(10)
        await ss(page, "p2d-pricing-msg")

        # ==================
        # PHASE 2B: BYPASS TO PRICING
        # ==================
        log("=== PHASE 2B: Bypass Code + Pricing ===", "PHASE")

        # Check if pricing visible or need bypass
        pricing_check = await page.evaluate("""
            return {
                hasProCta: !!document.getElementById('proCta'),
                hasPricing: !!document.querySelector('#pricing, .pricing, .pricing-section'),
                hasBypassBtn: !!document.getElementById('pb-sandbox-bypass-btn'),
                hasUserInput: !!document.getElementById('userInput')
            }
        """)
        log(f"Page state: {pricing_check}", "INFO")

        if pricing_check.get("hasUserInput"):
            log("Sending bypass code: pb-full-bypass", "ACTION")
            await page.evaluate("""
                var inp = document.getElementById('userInput');
                if (inp) {
                    inp.value = 'pb-full-bypass';
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                }
                var sub = document.getElementById('submitBtn');
                if (sub) sub.click();
            """)
            await asyncio.sleep(8)
            await ss(page, "p2e-after-bypass")

        # Click proCta
        await page.evaluate("var el = document.getElementById('proCta'); if (el) el.click()")
        await asyncio.sleep(5)
        await ss(page, "p2f-after-proCta")

        # Get page state
        page_state = await page.evaluate("""
            return {
                hasProCta: !!document.getElementById('proCta'),
                hasPricing: !!document.querySelector('#pricing, .pricing, .pricing-section, [id*=pricing]'),
                hasBypassBtn: !!document.getElementById('pb-sandbox-bypass-btn'),
                hasPayPalModal: !!document.querySelector('[class*=paypal-modal], [id*=paypal-modal]'),
                paypalFunctions: {
                    openPayPalModal: typeof openPayPalModal,
                    openPayPalCheckout: typeof openPayPalCheckout,
                    windowOpenPayPalModal: typeof window.openPayPalModal,
                }
            }
        """)
        log(f"Post-bypass page state: {page_state}", "INFO")

        # ==================
        # PHASE 3: PAYPAL PAYMENT
        # ==================
        log("=== PHASE 3: PayPal Awakened Tier ($79) ===", "PHASE")

        # Find and list pricing buttons
        pricing_btns = await page.evaluate("""
            var btns = document.querySelectorAll('button');
            var found = [];
            for (var b of btns) {
                var txt = b.textContent.trim();
                var onclick = b.getAttribute('onclick') || '';
                if (onclick.includes('PayPal') || onclick.includes('paypal') || onclick.includes('Awakened') ||
                    txt.includes('Awakened') || txt.includes('$79') || onclick.includes('Modal') || onclick.includes('modal')) {
                    found.push({text: txt.substring(0,40), onclick: onclick.substring(0,80)});
                }
            }
            return found;
        """)
        log(f"Pricing buttons found: {json.dumps(pricing_btns, indent=2)}", "INFO")

        await ss(page, "p3a-before-awakened-click")

        # Try to trigger PayPal for Awakened tier
        # Strategy: try multiple methods
        paypal_triggered = await page.evaluate("""
            var result = {method: null, error: null};
            try {
                // Method 1: Direct openPayPalModal
                if (typeof openPayPalModal !== 'undefined') {
                    openPayPalModal('Awakened');
                    result.method = 'openPayPalModal(Awakened)';
                    return result;
                }
                // Method 2: window.openPayPalModal
                if (typeof window.openPayPalModal !== 'undefined') {
                    window.openPayPalModal('Awakened');
                    result.method = 'window.openPayPalModal(Awakened)';
                    return result;
                }
                // Method 3: openPayPalCheckout
                if (typeof openPayPalCheckout !== 'undefined') {
                    openPayPalCheckout('Awakened');
                    result.method = 'openPayPalCheckout(Awakened)';
                    return result;
                }
                // Method 4: openWaitlistModal (mapped to paypal in fix)
                if (typeof window.openWaitlistModal !== 'undefined') {
                    window.openWaitlistModal('Awakened');
                    result.method = 'window.openWaitlistModal(Awakened) [scope-fixed]';
                    return result;
                }
                // Method 5: Click button with onclick containing Awakened
                var btns = document.querySelectorAll('button');
                for (var b of btns) {
                    var onclick = b.getAttribute('onclick') || '';
                    if (onclick.includes('Awakened')) {
                        b.click();
                        result.method = 'clicked button with Awakened onclick: ' + onclick.substring(0,50);
                        return result;
                    }
                }
                result.error = 'No method found';
                return result;
            } catch(e) {
                result.error = e.toString();
                return result;
            }
        """)
        log(f"PayPal trigger result: {paypal_triggered}", "ACTION")
        await asyncio.sleep(3)
        await ss(page, "p3b-after-paypal-trigger")

        # Check for modal
        modal_state = await page.evaluate("""
            var modal = document.querySelector('[class*=paypal-modal], [id*=paypal-modal], .pb-paypal-modal');
            if (!modal) return {found: false};
            var style = window.getComputedStyle(modal);
            return {
                found: true,
                display: style.display,
                visibility: style.visibility,
                html: modal.innerHTML.substring(0, 200)
            };
        """)
        log(f"PayPal modal state: {modal_state}", "INFO")

        # Wait for PayPal popup page
        log("Listening for PayPal popup page...", "ACTION")
        paypal_page = None

        # The "Pay with PayPal" gold button might be in an iframe OR trigger a popup
        # First check if there's a button in the modal
        modal_btn_state = await page.evaluate("""
            var modal = document.querySelector('[class*=paypal-modal], .pb-paypal-modal, #paypal-modal');
            if (!modal) return 'no-modal';
            var btns = modal.querySelectorAll('button');
            var info = [];
            for (var b of btns) info.push({text: b.textContent.trim().substring(0,30), visible: b.offsetParent !== null});
            return info;
        """)
        log(f"Modal buttons: {modal_btn_state}", "INFO")

        # Click the PayPal button in modal (should open popup)
        # This might open a new page
        popup_future = asyncio.ensure_future(ctx.wait_for_event("page", timeout=10000))
        await asyncio.sleep(0.5)

        paypal_btn_result = await page.evaluate("""
            var result = {clicked: false, html: ''};
            // Look in modal first
            var modal = document.querySelector('[class*=paypal-modal], .pb-paypal-modal, #paypal-modal');
            if (modal) {
                var btns = modal.querySelectorAll('button, a');
                for (var b of btns) {
                    var txt = (b.textContent || '').toLowerCase();
                    if (txt.includes('paypal') || txt.includes('pay') || txt.includes('checkout')) {
                        b.click();
                        result.clicked = true;
                        result.html = 'clicked: ' + b.textContent.trim().substring(0,30);
                        return result;
                    }
                }
                // Click first button in modal
                if (btns.length > 0) {
                    btns[0].click();
                    result.clicked = true;
                    result.html = 'first-modal-btn: ' + btns[0].textContent.trim().substring(0,30);
                    return result;
                }
            }
            // Try PayPal SDK iframe buttons
            var iframes = document.querySelectorAll('iframe[src*=paypal], iframe[name*=paypal]');
            result.html = 'iframes: ' + iframes.length;

            // Try form submit (fallback)
            var forms = document.querySelectorAll('form[action*=paypal]');
            if (forms.length > 0) {
                forms[0].submit();
                result.clicked = true;
                result.html = 'form-submit: ' + forms[0].action.substring(0,60);
                return result;
            }
            return result;
        """)
        log(f"PayPal button click: {paypal_btn_result}", "ACTION")

        await ss(page, "p3c-after-modal-click")

        # Check if popup opened
        try:
            paypal_page = await popup_future
            log(f"PayPal popup opened! URL: {paypal_page.url}", "SUCCESS")
        except Exception:
            log("No PayPal popup in 10s - checking for inline flow or bypass", "INFO")
            paypal_page = None

        if paypal_page:
            log("=== PHASE 3B: PayPal Popup Login ===", "PHASE")
            attach_monitors(paypal_page, "paypal-popup")

            await paypal_page.wait_for_load_state("domcontentloaded", timeout=20000)
            await asyncio.sleep(3)
            paypal_url = paypal_page.url
            log(f"PayPal URL: {paypal_url}", "INFO")

            # Screenshot popup
            counter[0] += 1
            pp_ss1 = SCREENSHOT_DIR / f"{counter[0]:03d}-p3d-paypal-popup.png"
            try:
                await paypal_page.screenshot(path=str(pp_ss1), timeout=10000)
                screenshots_taken.append(str(pp_ss1))
                log(f"PayPal popup SS: {pp_ss1.name}", "SS")
            except Exception as e:
                log(f"PayPal SS failed: {e}", "WARN")

            # Handle PayPal login
            # Step 1: Email
            email_inp = await paypal_page.query_selector("#email, input[name='email'], input[type='email'], #login_email")
            if email_inp:
                log(f"Entering PayPal email: {PAYPAL_EMAIL}", "ACTION")
                await email_inp.fill(PAYPAL_EMAIL)
                await asyncio.sleep(0.5)
                # Next button
                for next_sel in ["#btnNext", "button#btnNext", "input#btnNext", "#next", "button[type='submit']"]:
                    nb = await paypal_page.query_selector(next_sel)
                    if nb:
                        await nb.click()
                        log(f"Clicked Next via {next_sel}", "ACTION")
                        break
                else:
                    await email_inp.press("Enter")
                    log("Pressed Enter for next", "ACTION")
                await asyncio.sleep(4)
            else:
                log("PayPal email input not found", "WARN")
                # Screenshot to see what's there
                counter[0] += 1
                pp_ss_debug = SCREENSHOT_DIR / f"{counter[0]:03d}-p3d-debug-paypal-page.png"
                try:
                    await paypal_page.screenshot(path=str(pp_ss_debug), timeout=10000)
                    screenshots_taken.append(str(pp_ss_debug))
                except Exception:
                    pass

            # Screenshot after email
            counter[0] += 1
            pp_ss2 = SCREENSHOT_DIR / f"{counter[0]:03d}-p3e-paypal-after-email.png"
            try:
                await paypal_page.screenshot(path=str(pp_ss2), timeout=10000)
                screenshots_taken.append(str(pp_ss2))
                log(f"After email SS: {pp_ss2.name}", "SS")
            except Exception as e:
                log(f"SS failed: {e}", "WARN")

            # Step 2: Password
            pw_inp2 = await paypal_page.query_selector(
                "#password, input[name='password'], input[type='password'], #login_password"
            )
            if pw_inp2:
                log("Entering PayPal password", "ACTION")
                await pw_inp2.fill(PAYPAL_PASSWORD)
                await asyncio.sleep(0.5)
                for login_sel in ["#btnLogin", "#signIn", "button#signIn", "button[type='submit']", "input[type='submit']"]:
                    lb = await paypal_page.query_selector(login_sel)
                    if lb:
                        await lb.click()
                        log(f"Clicked login via {login_sel}", "ACTION")
                        break
                else:
                    await pw_inp2.press("Enter")
                    log("Pressed Enter for login", "ACTION")
                await asyncio.sleep(8)
            else:
                log("PayPal password input not found - maybe combined form?", "WARN")
                # Try combined email+pass form
                email_field = await paypal_page.query_selector("input[type='email']")
                pass_field = await paypal_page.query_selector("input[type='password']")
                if email_field and pass_field:
                    await email_field.fill(PAYPAL_EMAIL)
                    await pass_field.fill(PAYPAL_PASSWORD)
                    submit = await paypal_page.query_selector("button[type='submit']")
                    if submit:
                        await submit.click()
                    await asyncio.sleep(8)

            paypal_url2 = paypal_page.url
            log(f"PayPal URL after login: {paypal_url2}", "INFO")

            counter[0] += 1
            pp_ss3 = SCREENSHOT_DIR / f"{counter[0]:03d}-p3f-paypal-after-login.png"
            try:
                await paypal_page.screenshot(path=str(pp_ss3), timeout=10000)
                screenshots_taken.append(str(pp_ss3))
                log(f"After login SS: {pp_ss3.name}", "SS")
            except Exception as e:
                log(f"SS failed: {e}", "WARN")

            # Step 3: Confirm payment
            await asyncio.sleep(5)
            paypal_url3 = paypal_page.url
            log(f"PayPal URL after auth: {paypal_url3}", "INFO")

            # Look for review/confirm page
            page_text = await paypal_page.evaluate("document.body ? document.body.innerText.substring(0,300) : 'no body'")
            log(f"PayPal page text: {page_text[:150]}", "INFO")

            # Click "Continue" / "Pay Now" / "Agree & Continue"
            confirm_result = await paypal_page.evaluate("""
                var btns = document.querySelectorAll('button, input[type=submit], a[role=button]');
                for (var b of btns) {
                    var txt = (b.textContent || b.value || b.getAttribute('aria-label') || '').toLowerCase().trim();
                    if (txt.includes('pay now') || txt.includes('agree') || txt.includes('continue') ||
                        txt.includes('confirm') || txt.includes('pay ') || txt.includes('complete')) {
                        var info = txt.substring(0,30);
                        b.click();
                        return 'clicked: ' + info;
                    }
                }
                return 'no-confirm-button-found';
            """)
            log(f"PayPal confirm: {confirm_result}", "ACTION")
            await asyncio.sleep(8)

            counter[0] += 1
            pp_ss4 = SCREENSHOT_DIR / f"{counter[0]:03d}-p3g-paypal-confirmed.png"
            try:
                await paypal_page.screenshot(path=str(pp_ss4), timeout=10000)
                screenshots_taken.append(str(pp_ss4))
                log(f"PayPal confirmed SS: {pp_ss4.name}", "SS")
            except Exception as e:
                log(f"SS failed: {e}", "WARN")

            paypal_final_url = paypal_page.url
            log(f"PayPal final URL: {paypal_final_url}", "INFO")

            # Wait for redirect back to purebrain or success
            await asyncio.sleep(5)

        else:
            # No popup - try the sandbox bypass button
            log("No PayPal popup - trying sandbox bypass button", "ACTION")
            bypass_result = await page.evaluate("""
                var btn = document.getElementById('pb-sandbox-bypass-btn');
                if (btn) {
                    btn.click();
                    return 'sandbox-bypass-clicked';
                }
                return 'no-bypass-btn';
            """)
            log(f"Sandbox bypass: {bypass_result}", "ACTION")
            await asyncio.sleep(15)
            await ss(page, "p3h-after-bypass")

        # ==================
        # PHASE 4: POST-PAYMENT QUESTIONNAIRE
        # ==================
        log("=== PHASE 4: Post-Payment State ===", "PHASE")
        await asyncio.sleep(5)
        await ss(page, "p4a-post-payment")

        # Check for PTC wrapper
        ptc_check = await page.evaluate("""
            return {
                hasPtcWrapper: !!document.querySelector('.ptc-wrapper, #pay-test-post-payment, #ptc-wrapper'),
                hasPtcInput: !!document.querySelector('#ptc-input, textarea.ptc-input, .ptc-input'),
                ptcMsgCount: document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai').length,
                ptcMsgs: Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai')).slice(0,2).map(m=>m.textContent.trim().substring(0,60)),
                title: document.title.substring(0,40)
            }
        """)
        log(f"Post-payment state: {ptc_check}", "INFO")

        ai_count = ptc_check.get("ptcMsgCount", 0)

        # Answer questionnaire
        qa_pairs = [
            ("full name", "TestUser Smith"),
            ("email", "testuser@purebrain-test.com"),
            ("company", "TestCorp Marketing"),
            ("role", "CEO"),
            ("goal", "Automate my marketing workflows"),
        ]

        for q_label, answer in qa_pairs:
            log(f"Answering [{q_label}]: {answer}", "ACTION")
            ok = await ptc_send(page, answer)
            if ok:
                ai_count = await wait_for_ai(page, ai_count, timeout=20)
            else:
                log(f"Could not send [{q_label}]", "WARN")
            await ss(page, f"p4-qa-{q_label.replace(' ','-')}")
            await asyncio.sleep(2)

        # ==================
        # PHASE 5: BIRTH PIPELINE
        # ==================
        log("=== PHASE 5: Birth Pipeline / OAuth ===", "PHASE")
        await asyncio.sleep(5)
        await ss(page, "p5a-birth-state")

        birth_state = await page.evaluate("""
            var allMsgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai'));
            var msgs = allMsgs.map(m=>m.textContent.trim().substring(0,80));
            var links = Array.from(document.querySelectorAll('a[href*=oauth], a[href*=google], a[href*=birth], a[href*=auth]')).map(a=>a.href.substring(0,100));
            return {msgCount: allMsgs.length, lastMsgs: msgs.slice(-3), oauthLinks: links};
        """)
        log(f"Birth state: {birth_state}", "INFO")

        # ==================
        # PHASE 6: CONTINUE TO FINAL MESSAGE
        # ==================
        log("=== PHASE 6: Continue to Final Message ===", "PHASE")

        # Keep responding to prompts until portal button appears or no more input
        for i in range(12):
            inp_state = await page.evaluate("""
                var el = document.querySelector('#ptc-input, textarea.ptc-input, .ptc-input, textarea');
                if (!el) return {found: false};
                return {
                    found: true,
                    visible: el.offsetParent !== null,
                    disabled: el.disabled,
                    placeholder: el.getAttribute('placeholder') || '',
                    value: el.value || ''
                }
            """)

            if not inp_state.get("found") or inp_state.get("disabled"):
                log(f"[{i}] No active input - flow complete or stalled", "INFO")
                break

            if not inp_state.get("visible"):
                log(f"[{i}] Input not visible", "INFO")
                break

            current_count = (await page.evaluate("document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai').length")) or 0
            log(f"[{i}] Active input (placeholder: {inp_state.get('placeholder','')[:30]}) - sending continuation", "ACTION")

            ok = await ptc_send(page, "Yes, let's continue.")
            if ok:
                new_count = await wait_for_ai(page, current_count, timeout=20)
                if new_count == current_count:
                    log(f"[{i}] No new AI response - stalled", "INFO")
                    break
            else:
                break

            await ss(page, f"p6-exchange-{i:02d}")
            await asyncio.sleep(2)

            # Check for portal button
            portal = await page.evaluate("""
                var a = document.querySelector('a[href*=portal], a[href*=purebrain.ai/app], a[href*=app.purebrain]');
                var b = document.querySelector('button.ptc-launch-btn, .ptc-portal-btn, [class*=portal-btn]');
                if (a) return {found: true, type: 'link', href: a.href, text: a.textContent.trim().substring(0,30)};
                if (b) return {found: true, type: 'button', text: b.textContent.trim().substring(0,30)};
                return {found: false};
            """)
            if portal.get("found"):
                log(f"PORTAL FOUND: {portal}", "SUCCESS")
                await ss(page, "p6z-portal-found")
                break

        # Final state
        await asyncio.sleep(5)
        await ss(page, "p7-final-state")

        final_state = await page.evaluate("""
            var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai')).map(m=>m.textContent.trim().substring(0,100));
            var portal = document.querySelector('a[href*=portal], a[href*=app.purebrain], .ptc-portal-btn');
            return {
                totalMsgs: msgs.length,
                msgs: msgs,
                portalFound: !!portal,
                portalHref: portal ? (portal.href || '') : '',
                pageTitle: document.title.substring(0,50)
            }
        """)
        log(f"FINAL STATE: {json.dumps(final_state, indent=2)}", "SUMMARY")

        await browser.close()

    # ==================
    # REPORT GENERATION
    # ==================
    log("=== Generating Report ===", "END")

    lines = [
        "# E2E PayPal Real Sandbox Test Report",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**URL**: {PAGE_URL}",
        f"**PayPal Buyer**: {PAYPAL_EMAIL}",
        "",
        "---",
        "",
        "## Summary",
        f"- Screenshots taken: {len(screenshots_taken)}",
        f"- Network API calls captured: {len(network_calls)}",
        f"- Seed fires captured: {len(seed_fires)}",
        f"- Console logs captured: {len(console_logs)}",
        "",
        "## Seed Fires",
        "",
    ]

    if seed_fires:
        for sf in seed_fires:
            lines.append(f"### SEED [{sf['ts']}]")
            lines.append(f"- Method: `{sf['method']}` Status: `{sf['status']}`")
            lines.append(f"- URL: `{sf['url']}`")
            lines.append(f"- Response: `{sf['body'][:200]}`")
            lines.append("")
    else:
        lines.append("**No seeds captured via Playwright network monitor.**")
        lines.append("")
        lines.append("NOTE: Seeds may still fire - check Witness server logs for entries around this test time.")
        lines.append("")

    lines += [
        "## All Network Calls",
        "",
    ]
    for nc in network_calls:
        lines.append(f"- `{nc['ts']}` [{nc['page']}] `{nc['method']} {nc['status']}` `{nc['url'][:80]}`")
        lines.append(f"  - `{nc['body'][:100]}`")

    lines += [
        "",
        "## Console Logs (Filtered)",
        "",
    ]
    for cl in console_logs:
        lines.append(f"- `{cl['ts']}` [{cl['page']}][{cl['type']}]: {cl['text'][:120]}")

    lines += [
        "",
        "## Screenshots",
        "",
    ]
    for s in screenshots_taken:
        lines.append(f"- `{s}`")

    lines += [
        "",
        "## Full Timeline",
        "",
        "```",
    ]
    lines.extend(timeline)
    lines.append("```")

    REPORT_PATH.write_text("\n".join(lines))
    print(f"\n{'='*60}")
    print(f"Report: {REPORT_PATH}")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print(f"Seed fires: {len(seed_fires)}")
    print(f"Network calls: {len(network_calls)}")


if __name__ == "__main__":
    asyncio.run(run())
