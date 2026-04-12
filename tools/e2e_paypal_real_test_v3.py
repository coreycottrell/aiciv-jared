#!/usr/bin/env python3
"""
Full E2E PayPal Sandbox Real Test v3 - PureBrain Pay-Test-Sandbox-2
Date: 2026-03-02

Fixes from v2:
- All page.evaluate() wrapped in IIFE: (() => { ... })()
- Screenshot timeout raised to 20000ms (WebGL/Three.js font loading)
- Added screenshot clip area (avoid WebGL canvas timeout)
- Better error recovery
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


async def ss(page, label, clip=None):
    """Take screenshot, skip on timeout rather than crashing."""
    counter[0] += 1
    n = counter[0]
    fname = f"{n:03d}-{label}.png"
    fpath = SCREENSHOT_DIR / fname
    try:
        kwargs = {"path": str(fpath), "timeout": 20000}
        if clip:
            kwargs["clip"] = clip
        await page.screenshot(**kwargs)
        screenshots_taken.append(str(fpath))
        log(f"Screenshot: {fname}", "SS")
        return str(fpath)
    except Exception as e:
        log(f"Screenshot skipped [{label}]: {e!s:.60}", "WARN")
        # Don't increment counter again - just note it failed
        return None


def attach_monitors(page, label="main"):
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
                    "page": label, "ts": ts(),
                    "method": resp.request.method, "status": resp.status,
                    "url": url, "body": body_txt,
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
                                     "intake", "linking", "awaken", "ChatboxV", "verify"]):
            log(f"CON[{label}][{msg.type}]: {txt[:120]}", "CON")
            console_logs.append({"page": label, "type": msg.type, "text": txt, "ts": ts()})

    page.on("response", on_response)
    page.on("console", on_console)


async def wait_for_ai(page, current_count, timeout=30):
    sel = ".ptc-msg--ai, .ptc-msg.ptc-msg--ai"
    deadline = time.time() + timeout
    while time.time() < deadline:
        msgs = await page.query_selector_all(sel)
        if len(msgs) > current_count:
            await asyncio.sleep(2)
            msgs = await page.query_selector_all(sel)
            texts = [await m.inner_text() for m in msgs]
            last = texts[-1].strip()[:80] if texts else "?"
            log(f"AI response ({len(msgs)} total). Last: {last}", "AI")
            return len(msgs)
        await asyncio.sleep(0.5)
    log(f"Timeout waiting for AI (had {current_count})", "WARN")
    return current_count


async def ptc_send(page, text):
    for sel in ["#ptc-input", "textarea.ptc-input", ".ptc-input", "textarea"]:
        el = await page.query_selector(sel)
        if el:
            try:
                if not await el.is_visible() or not await el.is_enabled():
                    continue
                await el.click()
                await asyncio.sleep(0.2)
                await el.fill("")
                await el.type(text, delay=20)
                await asyncio.sleep(0.3)
                for sbtn in ["#ptc-send", ".ptc-send", ".ptc-send-btn", "button[type=submit]"]:
                    sb = await page.query_selector(sbtn)
                    if sb:
                        await sb.click()
                        log(f"PTC sent ({sel}+{sbtn}): {text[:40]}", "ACTION")
                        return True
                await el.press("Enter")
                log(f"PTC sent ({sel}+Enter): {text[:40]}", "ACTION")
                return True
            except Exception as e:
                log(f"ptc_send err {sel}: {e!s:.40}", "WARN")
    log(f"PTC send failed: {text[:40]}", "ERROR")
    return False


async def run():
    log("=== E2E PayPal Real Sandbox Test v3 ===", "START")
    log(f"URL: {PAGE_URL}", "INFO")
    log(f"PayPal: {PAYPAL_EMAIL}", "INFO")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage",
                  "--disable-gpu", "--disable-software-rasterizer"],
        )
        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            ignore_https_errors=True,
        )
        page = await ctx.new_page()
        attach_monitors(page, "main")

        # ==================
        # PHASE 1: ACCESS + PASSWORD
        # ==================
        log("=== PHASE 1: Page Access ===", "PHASE")
        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        await ss(page, "p1a-initial")

        pw_inp = await page.query_selector('input[type="password"]')
        if pw_inp:
            log("Password prompt found", "INFO")
            await pw_inp.fill(PAGE_PASSWORD)
            sub = await page.query_selector('input[type="submit"]')
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            await asyncio.sleep(10)
            log("Password submitted", "ACTION")
        else:
            log("No password prompt (or page already unlocked)", "INFO")

        await ss(page, "p1b-after-password")

        # ==================
        # PHASE 2: CLICK BEGIN AWAKENING
        # ==================
        log("=== PHASE 2: Begin Awakening ===", "PHASE")

        begin_found = await page.evaluate("""(() => {
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
        })()""")
        log(f"Begin click: {begin_found}", "ACTION")
        await asyncio.sleep(6)
        await ss(page, "p2a-after-begin")

        # First user message
        log("Msg 1: Hi! My name is TestUser. I run a marketing agency.", "ACTION")
        await page.evaluate("""(() => {
            var inp = document.getElementById('userInput');
            if (inp) {
                inp.value = 'Hi! My name is TestUser. I run a marketing agency.';
                inp.dispatchEvent(new Event('input', {bubbles: true}));
            }
            var sub = document.getElementById('submitBtn');
            if (sub) sub.click();
        })()""")
        await asyncio.sleep(8)
        await ss(page, "p2b-msg1-sent")

        # Get AI response
        chat_state = await page.evaluate("""(() => {
            var msgs = document.querySelectorAll('.chat-message, .ai-message, [class*=ai-msg], .message-ai, .chat-msg-ai');
            var data = {count: msgs.length, texts: []};
            for (var i = 0; i < Math.min(msgs.length, 2); i++) data.texts.push(msgs[i].textContent.trim().substring(0,80));
            return data;
        })()""")
        log(f"Pre-PTC AI msgs: {chat_state}", "AI")

        # Second message - name the AI
        log("Msg 2: I'd love to call you Nova. Does that feel right?", "ACTION")
        await page.evaluate("""(() => {
            var inp = document.getElementById('userInput');
            if (inp) {
                inp.value = "I'd love to call you Nova. Does that feel right?";
                inp.dispatchEvent(new Event('input', {bubbles: true}));
            }
            var sub = document.getElementById('submitBtn');
            if (sub) sub.click();
        })()""")
        await asyncio.sleep(8)
        await ss(page, "p2c-nova-msg")

        # Third message - ask for options
        log("Msg 3: I'm convinced. I want to get started. What are my options?", "ACTION")
        await page.evaluate("""(() => {
            var inp = document.getElementById('userInput');
            if (inp) {
                inp.value = "I'm convinced. I want to get started. What are my options?";
                inp.dispatchEvent(new Event('input', {bubbles: true}));
            }
            var sub = document.getElementById('submitBtn');
            if (sub) sub.click();
        })()""")
        await asyncio.sleep(10)
        await ss(page, "p2d-pricing-request")

        # ==================
        # PHASE 2B: BYPASS + PRICING
        # ==================
        log("=== PHASE 2B: Bypass + Pricing ===", "PHASE")

        page_check = await page.evaluate("""(() => {
            return {
                hasUserInput: !!document.getElementById('userInput'),
                hasProCta: !!document.getElementById('proCta'),
                hasBypass: !!document.getElementById('pb-sandbox-bypass-btn'),
                hasPricing: !!document.querySelector('#pricing, .pricing, [id*=pricing]'),
            };
        })()""")
        log(f"Page check: {page_check}", "INFO")

        if page_check.get("hasUserInput"):
            log("Sending bypass code", "ACTION")
            await page.evaluate("""(() => {
                var inp = document.getElementById('userInput');
                if (inp) {
                    inp.value = 'pb-full-bypass';
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                }
                var sub = document.getElementById('submitBtn');
                if (sub) sub.click();
            })()""")
            await asyncio.sleep(8)
            await ss(page, "p2e-after-bypass")

        # Click proCta to show pricing
        await page.evaluate("(() => { var el = document.getElementById('proCta'); if (el) el.click(); })()")
        await asyncio.sleep(5)
        await ss(page, "p2f-after-proCta")

        # Check PayPal functions available
        fn_check = await page.evaluate("""(() => {
            return {
                openPayPalModal: typeof openPayPalModal,
                windowOpenPayPalModal: typeof window.openPayPalModal,
                openPayPalCheckout: typeof openPayPalCheckout,
                windowOpenPayPalCheckout: typeof window.openPayPalCheckout,
                openWaitlistModal: typeof openWaitlistModal,
                windowOpenWaitlistModal: typeof window.openWaitlistModal,
            };
        })()""")
        log(f"PayPal functions: {fn_check}", "INFO")

        # List all pricing buttons
        pricing_btns = await page.evaluate("""(() => {
            var btns = document.querySelectorAll('button');
            var found = [];
            for (var b of btns) {
                var txt = b.textContent.trim();
                var onclick = b.getAttribute('onclick') || '';
                if (onclick.includes('PayPal') || onclick.includes('paypal') || onclick.includes('Modal') ||
                    onclick.includes('Awakened') || txt.includes('Awakened') || txt.includes('$79') ||
                    txt.includes('Get ') || onclick.includes('modal') || onclick.includes('Checkout')) {
                    found.push({text: txt.substring(0,40), onclick: onclick.substring(0,100)});
                }
            }
            return found;
        })()""")
        log(f"Pricing buttons: {json.dumps(pricing_btns)}", "INFO")

        # ==================
        # PHASE 3: PAYPAL AWAKENED TIER
        # ==================
        log("=== PHASE 3: PayPal $79 Awakened Tier ===", "PHASE")
        await ss(page, "p3a-before-paypal")

        # Try to open PayPal for Awakened tier
        paypal_trigger = await page.evaluate("""(() => {
            // Method 1: openPayPalModal
            if (typeof openPayPalModal === 'function') {
                try { openPayPalModal('Awakened'); return 'openPayPalModal(Awakened)'; } catch(e) { return 'err1:'+e; }
            }
            // Method 2: window.openPayPalModal
            if (typeof window.openPayPalModal === 'function') {
                try { window.openPayPalModal('Awakened'); return 'w.openPayPalModal(Awakened)'; } catch(e) { return 'err2:'+e; }
            }
            // Method 3: openPayPalCheckout
            if (typeof openPayPalCheckout === 'function') {
                try { openPayPalCheckout('Awakened'); return 'openPayPalCheckout(Awakened)'; } catch(e) { return 'err3:'+e; }
            }
            // Method 4: window.openPayPalCheckout
            if (typeof window.openPayPalCheckout === 'function') {
                try { window.openPayPalCheckout('Awakened'); return 'w.openPayPalCheckout(Awakened)'; } catch(e) { return 'err4:'+e; }
            }
            // Method 5: openWaitlistModal (scoped to PayPal via PB-FIX)
            if (typeof window.openWaitlistModal === 'function') {
                try { window.openWaitlistModal('Awakened'); return 'w.openWaitlistModal(Awakened)'; } catch(e) { return 'err5:'+e; }
            }
            // Method 6: click button with Awakened in onclick
            var btns = document.querySelectorAll('button');
            for (var b of btns) {
                var onclick = b.getAttribute('onclick') || '';
                if (onclick.includes('Awakened')) {
                    b.click();
                    return 'clicked-btn-onclick-Awakened: ' + onclick.substring(0,50);
                }
            }
            return 'no-paypal-method-found';
        })()""")
        log(f"PayPal trigger: {paypal_trigger}", "ACTION")
        await asyncio.sleep(3)
        await ss(page, "p3b-after-trigger")

        # Check modal
        modal_check = await page.evaluate("""(() => {
            var modal = document.querySelector('[class*=paypal-modal], [id*=paypal-modal], .pb-paypal-modal');
            if (!modal) return {found: false};
            var style = window.getComputedStyle(modal);
            var btns = Array.from(modal.querySelectorAll('button, a')).map(b => ({
                text: b.textContent.trim().substring(0,30),
                tag: b.tagName,
                onclick: (b.getAttribute('onclick') || '').substring(0,50)
            }));
            return {
                found: true,
                display: style.display,
                visibility: style.visibility,
                buttonCount: btns.length,
                buttons: btns,
                innerHtml: modal.innerHTML.substring(0,300)
            };
        })()""")
        log(f"Modal state: {json.dumps(modal_check)}", "INFO")

        await ss(page, "p3c-modal-state")

        # ==================
        # PHASE 3B: CLICK PAY WITH PAYPAL
        # ==================
        log("=== PHASE 3B: Click Pay with PayPal ===", "PHASE")

        # Set up popup listener BEFORE clicking
        popup_page = None
        popup_event = asyncio.ensure_future(ctx.wait_for_event("page", timeout=12000))
        await asyncio.sleep(0.5)

        # Click the PayPal button in modal
        modal_click = await page.evaluate("""(() => {
            // Try modal first
            var modal = document.querySelector('[class*=paypal-modal], [id*=paypal-modal], .pb-paypal-modal');
            if (modal) {
                // Find PayPal button
                var btns = modal.querySelectorAll('button, a, form');
                for (var b of btns) {
                    var txt = (b.textContent || '').toLowerCase();
                    if (txt.includes('paypal') || txt.includes('pay') || txt.includes('checkout')) {
                        b.click();
                        return 'modal-btn: ' + txt.substring(0,30);
                    }
                }
                // Click first button
                if (btns.length > 0) {
                    btns[0].click();
                    return 'modal-first-btn: ' + (btns[0].textContent || '').substring(0,30);
                }
            }
            // Check for PayPal form (fallback)
            var form = document.querySelector('form[action*=paypal]');
            if (form) {
                form.submit();
                return 'paypal-form-submit: ' + form.action.substring(0,60);
            }
            // Check iframes
            var iframes = document.querySelectorAll('iframe');
            return 'no-modal-btn iframes:' + iframes.length;
        })()""")
        log(f"Modal click: {modal_click}", "ACTION")

        # Wait for popup
        try:
            popup_page = await popup_event
            log(f"PayPal popup opened: {popup_page.url}", "SUCCESS")
        except Exception as e:
            log(f"No popup in 12s: {e!s:.40}", "INFO")
            popup_page = None

        if popup_page:
            # ==================
            # PHASE 3C: PAYPAL LOGIN IN POPUP
            # ==================
            log("=== PHASE 3C: PayPal Login ===", "PHASE")
            attach_monitors(popup_page, "paypal")
            await popup_page.wait_for_load_state("domcontentloaded", timeout=20000)
            await asyncio.sleep(3)

            paypal_url = popup_page.url
            log(f"PayPal popup URL: {paypal_url}", "INFO")

            # Screenshot popup
            counter[0] += 1
            pp_ss = SCREENSHOT_DIR / f"{counter[0]:03d}-p3d-paypal-popup.png"
            try:
                await popup_page.screenshot(path=str(pp_ss), timeout=15000)
                screenshots_taken.append(str(pp_ss))
                log(f"PayPal popup SS: {pp_ss.name}", "SS")
            except Exception as e:
                log(f"PayPal popup SS failed: {e!s:.50}", "WARN")

            # Get page source info
            page_info = await popup_page.evaluate("""(() => {
                return {
                    title: document.title.substring(0,50),
                    hasEmailInp: !!document.querySelector('#email, input[name=email], input[type=email], #login_email'),
                    hasPassInp: !!document.querySelector('#password, input[name=password], input[type=password]'),
                    url: window.location.href.substring(0,80),
                    bodyText: document.body ? document.body.innerText.substring(0,200) : 'no body'
                };
            })()""")
            log(f"PayPal page info: {page_info}", "INFO")

            # Enter email
            for email_sel in ["#email", "input[name='email']", "input[type='email']", "#login_email"]:
                email_el = await popup_page.query_selector(email_sel)
                if email_el:
                    log(f"Entering email via {email_sel}: {PAYPAL_EMAIL}", "ACTION")
                    await email_el.fill(PAYPAL_EMAIL)
                    await asyncio.sleep(0.5)

                    # Check for Next button
                    next_clicked = False
                    for nb_sel in ["#btnNext", "#next", "button#nextBtn", "button[type='submit']", "input[type='submit']"]:
                        nb = await popup_page.query_selector(nb_sel)
                        if nb:
                            await nb.click()
                            log(f"Clicked Next: {nb_sel}", "ACTION")
                            next_clicked = True
                            break
                    if not next_clicked:
                        await email_el.press("Enter")
                        log("Pressed Enter for next", "ACTION")
                    await asyncio.sleep(4)
                    break

            # Screenshot after email
            counter[0] += 1
            pp_ss2 = SCREENSHOT_DIR / f"{counter[0]:03d}-p3e-paypal-after-email.png"
            try:
                await popup_page.screenshot(path=str(pp_ss2), timeout=15000)
                screenshots_taken.append(str(pp_ss2))
                log(f"After email SS: {pp_ss2.name}", "SS")
            except Exception as e:
                log(f"After email SS failed: {e!s:.40}", "WARN")

            # Enter password
            for pw_sel in ["#password", "input[name='password']", "input[type='password']", "#login_password"]:
                pw_el = await popup_page.query_selector(pw_sel)
                if pw_el:
                    log(f"Entering password via {pw_sel}", "ACTION")
                    await pw_el.fill(PAYPAL_PASSWORD)
                    await asyncio.sleep(0.5)
                    login_clicked = False
                    for lb_sel in ["#btnLogin", "#signIn", "button#signIn", "button[type='submit']", "input[type='submit']"]:
                        lb = await popup_page.query_selector(lb_sel)
                        if lb:
                            await lb.click()
                            log(f"Clicked Login: {lb_sel}", "ACTION")
                            login_clicked = True
                            break
                    if not login_clicked:
                        await pw_el.press("Enter")
                        log("Pressed Enter for login", "ACTION")
                    await asyncio.sleep(8)
                    break

            paypal_url2 = popup_page.url
            log(f"PayPal URL after login: {paypal_url2}", "INFO")

            counter[0] += 1
            pp_ss3 = SCREENSHOT_DIR / f"{counter[0]:03d}-p3f-paypal-after-login.png"
            try:
                await popup_page.screenshot(path=str(pp_ss3), timeout=15000)
                screenshots_taken.append(str(pp_ss3))
                log(f"After login SS: {pp_ss3.name}", "SS")
            except Exception as e:
                log(f"After login SS failed: {e!s:.40}", "WARN")

            # Step 3: Confirm payment on review page
            await asyncio.sleep(5)
            log("Looking for Confirm/Pay button on PayPal review page", "ACTION")

            paypal_page_text = await popup_page.evaluate("(() => document.body ? document.body.innerText.substring(0,400) : '')()")
            log(f"PayPal review text: {paypal_page_text[:200]}", "INFO")

            confirm_result = await popup_page.evaluate("""(() => {
                var btns = document.querySelectorAll('button, input[type=submit], a[role=button]');
                for (var b of btns) {
                    var txt = (b.textContent || b.value || b.getAttribute('aria-label') || '').toLowerCase().trim();
                    if (txt.includes('pay now') || txt.includes('agree') || txt.includes('continue') ||
                        txt.includes('confirm') || txt.includes('complete') || txt.includes('pay ')) {
                        b.click();
                        return 'clicked: ' + txt.substring(0,30);
                    }
                }
                return 'no-confirm-btn';
            })()""")
            log(f"PayPal confirm: {confirm_result}", "ACTION")
            await asyncio.sleep(10)

            counter[0] += 1
            pp_ss4 = SCREENSHOT_DIR / f"{counter[0]:03d}-p3g-paypal-confirmed.png"
            try:
                await popup_page.screenshot(path=str(pp_ss4), timeout=15000)
                screenshots_taken.append(str(pp_ss4))
                log(f"PayPal confirmed SS: {pp_ss4.name}", "SS")
            except Exception as e:
                log(f"SS failed: {e!s:.40}", "WARN")

            paypal_final_url = popup_page.url
            log(f"PayPal final URL: {paypal_final_url}", "INFO")
            await asyncio.sleep(3)

        else:
            # No popup - use sandbox bypass
            log("No PayPal popup - using sandbox bypass button", "ACTION")
            bypass_result = await page.evaluate("""(() => {
                var btn = document.getElementById('pb-sandbox-bypass-btn');
                if (btn) { btn.click(); return 'sandbox-bypass-clicked'; }
                return 'no-bypass-btn-found';
            })()""")
            log(f"Sandbox bypass: {bypass_result}", "ACTION")
            await asyncio.sleep(15)
            await ss(page, "p3h-after-sandbox-bypass")

        # ==================
        # PHASE 4: POST-PAYMENT QUESTIONNAIRE
        # ==================
        log("=== PHASE 4: Post-Payment Questionnaire ===", "PHASE")
        await asyncio.sleep(8)
        await ss(page, "p4a-post-payment-state")

        ptc_check = await page.evaluate("""(() => {
            return {
                hasPtcWrapper: !!document.querySelector('.ptc-wrapper, #pay-test-post-payment, #ptc-wrapper'),
                hasPtcInput: !!document.querySelector('#ptc-input, textarea.ptc-input, .ptc-input'),
                ptcMsgCount: document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai').length,
                ptcMsgs: Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai'))
                    .slice(0,3).map(m => m.textContent.trim().substring(0,60)),
            };
        })()""")
        log(f"PTC state: {ptc_check}", "INFO")

        ai_count = ptc_check.get("ptcMsgCount", 0)
        log(f"Starting Q&A with {ai_count} AI msgs", "INFO")

        qa_pairs = [
            ("name", "TestUser Smith"),
            ("email", "testuser@purebrain-test.com"),
            ("company", "TestCorp Marketing"),
            ("role", "CEO"),
            ("goal", "Automate my marketing workflows"),
        ]

        for q_label, answer in qa_pairs:
            log(f"Q&A [{q_label}]: {answer}", "ACTION")
            ok = await ptc_send(page, answer)
            if ok:
                ai_count = await wait_for_ai(page, ai_count, timeout=20)
            await ss(page, f"p4-{q_label}")
            await asyncio.sleep(2)

        # ==================
        # PHASE 5: BIRTH PIPELINE CHECK
        # ==================
        log("=== PHASE 5: Birth Pipeline Check ===", "PHASE")
        await asyncio.sleep(5)
        await ss(page, "p5a-birth-check")

        birth_check = await page.evaluate("""(() => {
            var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai'))
                .map(m => m.textContent.trim().substring(0,100));
            var links = Array.from(document.querySelectorAll('a[href*=oauth], a[href*=google], a[href*=birth]'))
                .map(a => a.href.substring(0,100));
            return {msgCount: msgs.length, lastMsgs: msgs.slice(-3), oauthLinks: links};
        })()""")
        log(f"Birth check: {birth_check}", "INFO")

        # ==================
        # PHASE 6: CONTINUE TO FINAL / SECOND SEED
        # ==================
        log("=== PHASE 6: Continue to Final Message ===", "PHASE")

        for i in range(15):
            inp_check = await page.evaluate("""(() => {
                var el = document.querySelector('#ptc-input, textarea.ptc-input, .ptc-input, textarea');
                if (!el) return {found: false};
                return {found: true, visible: el.offsetParent !== null, disabled: el.disabled,
                        placeholder: (el.getAttribute('placeholder') || '').substring(0,40)};
            })()""")

            if not inp_check.get("found") or inp_check.get("disabled") or not inp_check.get("visible"):
                log(f"[ex{i}] No active input - checking for portal", "INFO")
                break

            cur = await page.evaluate("(() => document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai').length)()")
            log(f"[ex{i}] Active input, {cur} AI msgs. Sending continuation.", "ACTION")

            ok = await ptc_send(page, "Yes, let's continue.")
            if ok:
                new_c = await wait_for_ai(page, cur, timeout=20)
                if new_c == cur:
                    log(f"[ex{i}] No new AI msg - stalled", "INFO")
                    break
            else:
                break

            await ss(page, f"p6-ex{i:02d}")
            await asyncio.sleep(2)

            # Check for portal button
            portal = await page.evaluate("""(() => {
                var a = document.querySelector('a[href*=portal], a[href*=app.purebrain], a[href*=purebrain.ai/app]');
                var btn = document.querySelector('.ptc-launch-btn, .ptc-portal-btn, [class*=portal]');
                if (a) return {found: true, type: 'link', href: a.href.substring(0,80), text: a.textContent.trim().substring(0,30)};
                if (btn) return {found: true, type: 'button', text: btn.textContent.trim().substring(0,30)};
                return {found: false};
            })()""")
            if portal.get("found"):
                log(f"PORTAL BUTTON FOUND: {portal}", "SUCCESS")
                await ss(page, f"p6-portal-found-ex{i:02d}")
                break

        # Final screenshots
        await asyncio.sleep(5)
        await ss(page, "p7a-final-state")

        final = await page.evaluate("""(() => {
            var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai'))
                .map(m => m.textContent.trim().substring(0,100));
            var portal = document.querySelector('a[href*=portal], a[href*=app.purebrain], .ptc-portal-btn');
            return {
                totalMsgs: msgs.length,
                msgs: msgs,
                portalFound: !!portal,
                portalHref: portal ? (portal.href || portal.textContent || '').substring(0,80) : '',
                pageTitle: document.title.substring(0,50)
            };
        })()""")
        log(f"FINAL STATE: msgs={final['totalMsgs']}, portal={final['portalFound']}", "SUMMARY")
        for i, m in enumerate(final.get("msgs", [])):
            log(f"  PTC msg[{i}]: {m}", "AI")

        await browser.close()

    # ==================
    # REPORT
    # ==================
    log("=== Generating Report ===", "END")

    lines = [
        "# E2E PayPal Real Sandbox Test - Full Report",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**URL**: {PAGE_URL}",
        f"**PayPal Buyer**: {PAYPAL_EMAIL}",
        "",
        "---",
        "",
        "## Summary",
        f"- Screenshots: {len(screenshots_taken)}",
        f"- API calls captured: {len(network_calls)}",
        f"- Seed fires: {len(seed_fires)}",
        f"- Console entries: {len(console_logs)}",
        "",
        "## Seed Fires",
        "",
    ]
    if seed_fires:
        for sf in seed_fires:
            lines.append(f"### SEED - {sf['ts']}")
            lines.append(f"- `{sf['method']} {sf['status']}` `{sf['url']}`")
            lines.append(f"- Response: `{sf['body'][:200]}`")
            lines.append("")
    else:
        lines += [
            "**No seeds captured by Playwright network monitor.**",
            "",
            "IMPORTANT: Seeds may still fire (check Witness server logs for this time window).",
            "Mixed-content HTTP seeds are blocked by browser security even in headless mode.",
            "",
        ]

    lines += ["## Network Calls", ""]
    for nc in network_calls:
        lines.append(f"- `{nc['ts']}` [{nc['page']}] `{nc['method']} {nc['status']}` `{nc['url'][:80]}`")
        lines.append(f"  `{nc['body'][:100]}`")

    lines += ["", "## Console Logs (Filtered)", ""]
    for cl in console_logs:
        lines.append(f"- `{cl['ts']}` [{cl['page']}][{cl['type']}]: {cl['text'][:120]}")

    lines += ["", "## Screenshots", ""]
    for s in screenshots_taken:
        lines.append(f"- `{s}`")

    lines += ["", "## Full Timeline", "", "```"]
    lines.extend(timeline)
    lines.append("```")

    REPORT_PATH.write_text("\n".join(lines))
    print(f"\n{'='*60}")
    print(f"COMPLETE. Report: {REPORT_PATH}")
    print(f"Screenshots dir: {SCREENSHOT_DIR}")
    print(f"Seeds fired: {len(seed_fires)}")
    print(f"API calls: {len(network_calls)}")
    print(f"Console entries: {len(console_logs)}")
    if seed_fires:
        print("\nSEED FIRES:")
        for sf in seed_fires:
            print(f"  {sf['ts']} {sf['status']} {sf['url']}")
            print(f"  -> {sf['body'][:100]}")


if __name__ == "__main__":
    asyncio.run(run())
