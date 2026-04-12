#!/usr/bin/env python3
"""
Full E2E PayPal Sandbox Real Test v4 - PureBrain Pay-Test-Sandbox-2
Date: 2026-03-02

v4 focus:
- Click REAL "Pay with PayPal" gold button (iframe-rendered by PayPal SDK)
- Handle PayPal login popup
- Monitor ALL seed fire endpoints including birth/start
- Capture OAuth URL + "Authorize Keen's AI Brain" button
- Continue through to final message / portal button

Key context:
- PayPal SDK renders inside iframe
- Modal shows "Pay with PayPal" + SEPA + Debit/Credit
- Below those: "Simulate Successful Payment (Test Only)" [Sandbox only]
- For REAL test: need to click iframe PayPal button -> popup -> login
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

PAGE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-paypal-real-20260302")
REPORT_PATH = Path("/home/jared/projects/AI-CIV/aether/exports/e2e-paypal-real-report-20260302.md")

PAYPAL_EMAIL = "sb-c89tj49549583@personal.example.com"
PAYPAL_PASSWORD = "Z0+6<dS"

MONITORED = [
    "api.purebrain.ai/api/intake/seed",
    "api.purebrain.ai/api/log-conversation",
    "api.purebrain.ai/api/log-pay-test",
    "api.purebrain.ai/api/verify-payment",
    "api.purebrain.ai/api/birth",
    "purebrain.ai/wp-json/purebrain",
]

timeline = []
network_calls = []
seed_fires = []
console_logs = []
screenshots_taken = []
c = [0]


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(msg, cat="ACTION"):
    entry = f"[{ts()}] [{cat}] {msg}"
    timeline.append(entry)
    print(entry)


async def ss(page, label):
    c[0] += 1
    n = c[0]
    fname = f"{n:03d}-{label}.png"
    fpath = SCREENSHOT_DIR / fname
    try:
        await page.screenshot(path=str(fpath), timeout=20000)
        screenshots_taken.append(str(fpath))
        log(f"SS: {fname}", "SS")
        return str(fpath)
    except Exception as e:
        log(f"SS skip [{label}]: {str(e)[:50]}", "WARN")
        return None


def monitor(page, label):
    async def on_resp(resp):
        url = resp.url
        for ep in MONITORED:
            if ep in url:
                try:
                    body = (await resp.body()).decode("utf-8", errors="replace")[:300]
                except Exception:
                    body = "(unreadable)"
                e = {"page": label, "ts": ts(), "method": resp.request.method,
                     "status": resp.status, "url": url, "body": body}
                network_calls.append(e)
                if "seed" in url or "intake" in url:
                    seed_fires.append(e)
                    log(f"SEED: {resp.status} {url} | {body[:80]}", "SEED")
                else:
                    log(f"API: {resp.status} {url[:60]} | {body[:60]}", "NET")

    async def on_con(msg):
        txt = msg.text
        if any(x in txt for x in ["seed", "birth", "payment", "Payment", "fireSeed",
                                     "oauth", "PB-FIX", "intake", "verify", "error", "Error"]):
            log(f"CON[{label}][{msg.type}]: {txt[:120]}", "CON")
            console_logs.append({"page": label, "type": msg.type, "text": txt, "ts": ts()})

    page.on("response", on_resp)
    page.on("console", on_con)


async def wait_ai(page, n, timeout=35):
    sel = ".ptc-msg--ai, .ptc-msg.ptc-msg--ai"
    deadline = time.time() + timeout
    while time.time() < deadline:
        msgs = await page.query_selector_all(sel)
        if len(msgs) > n:
            await asyncio.sleep(2)
            msgs2 = await page.query_selector_all(sel)
            txts = [(await m.inner_text()).strip()[:80] for m in msgs2]
            log(f"AI response ({len(msgs2)} total): {txts[-1] if txts else '?'}", "AI")
            return len(msgs2)
        await asyncio.sleep(0.5)
    log(f"AI timeout (had {n})", "WARN")
    return n


async def ptc_type_send(page, text):
    for sel in ["#ptc-input", "textarea.ptc-input", ".ptc-input", "textarea"]:
        el = await page.query_selector(sel)
        if el:
            try:
                if not await el.is_visible() or not await el.is_enabled():
                    continue
                await el.click()
                await el.fill("")
                await el.type(text, delay=20)
                await asyncio.sleep(0.3)
                for sbtn in ["#ptc-send", ".ptc-send", ".ptc-send-btn", "button[type=submit]"]:
                    sb = await page.query_selector(sbtn)
                    if sb:
                        await sb.click()
                        log(f"PTC: sent via {sel}+{sbtn}: {text[:40]}", "ACTION")
                        return True
                await el.press("Enter")
                log(f"PTC: sent via {sel}+Enter: {text[:40]}", "ACTION")
                return True
            except Exception as e:
                log(f"ptc_type_send err ({sel}): {str(e)[:40]}", "WARN")
    return False


async def run():
    log("=== E2E PayPal Real Test v4 ===", "START")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        )
        page = await ctx.new_page()
        monitor(page, "main")

        # PHASE 1: PASSWORD
        log("=== PHASE 1: Page + Password ===", "PHASE")
        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        await ss(page, "p1-initial")

        pw_inp = await page.query_selector('input[type="password"]')
        if pw_inp:
            await pw_inp.fill(PAGE_PASSWORD)
            sub = await page.query_selector('input[type="submit"]')
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            await asyncio.sleep(10)
        await ss(page, "p1-unlocked")

        # PHASE 2: PRE-PAYMENT CHATBOX
        log("=== PHASE 2: Pre-payment chat ===", "PHASE")

        # Click Begin
        r = await page.evaluate("""(() => {
            var b = document.querySelector('.chat-initial__btn');
            if (b) { b.click(); return 'clicked .chat-initial__btn'; }
            return 'not-found';
        })()""")
        log(f"Begin: {r}", "ACTION")
        await asyncio.sleep(5)
        await ss(page, "p2-begin-clicked")

        # 3 messages
        msgs_to_send = [
            "Hi! My name is TestUser. I run a marketing agency.",
            "I'd love to call you Nova. Does that feel right?",
            "I'm convinced. I want to get started. What are my options?",
        ]
        for i, msg in enumerate(msgs_to_send):
            log(f"Sending msg {i+1}: {msg[:50]}", "ACTION")
            await page.evaluate("""(msg) => {
                var inp = document.getElementById('userInput');
                if (inp) {
                    inp.value = msg;
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                }
                var sub = document.getElementById('submitBtn');
                if (sub) sub.click();
            }""", msg)
            await asyncio.sleep(9)

        await ss(page, "p2-msgs-sent")

        # Bypass
        log("Sending bypass code", "ACTION")
        await page.evaluate("""(() => {
            var inp = document.getElementById('userInput');
            if (inp) { inp.value = 'pb-full-bypass'; inp.dispatchEvent(new Event('input', {bubbles: true})); }
            var sub = document.getElementById('submitBtn');
            if (sub) sub.click();
        })()""")
        await asyncio.sleep(8)

        # proCta
        await page.evaluate("(() => { var e = document.getElementById('proCta'); if (e) e.click(); })()")
        await asyncio.sleep(5)
        await ss(page, "p2-pricing-visible")

        # Check PayPal functions
        fn_state = await page.evaluate("""(() => {
            return {
                openPayPalModal: typeof openPayPalModal,
                openPayPalCheckout: typeof openPayPalCheckout,
                windowOpenPayPalModal: typeof window.openPayPalModal,
            };
        })()""")
        log(f"PayPal fns: {fn_state}", "INFO")

        # PHASE 3: OPEN PAYPAL MODAL FOR AWAKENED
        log("=== PHASE 3: PayPal Modal - Awakened ($79) ===", "PHASE")

        trigger_result = await page.evaluate("""(() => {
            if (typeof openPayPalModal === 'function') {
                openPayPalModal('Awakened');
                return 'openPayPalModal(Awakened)';
            }
            if (typeof window.openPayPalModal === 'function') {
                window.openPayPalModal('Awakened');
                return 'window.openPayPalModal(Awakened)';
            }
            return 'no-fn';
        })()""")
        log(f"Trigger: {trigger_result}", "ACTION")
        await asyncio.sleep(5)
        await ss(page, "p3-modal-open")

        # Inspect modal + iframe content
        modal_info = await page.evaluate("""(() => {
            var modal = document.querySelector('[class*=paypal-modal], [id*=paypal-modal], .pb-paypal-modal');
            if (!modal) return {found: false};
            var iframes = modal.querySelectorAll('iframe');
            var iframeInfo = Array.from(iframes).map(f => ({src: f.src.substring(0,80), name: f.name || '', id: f.id || ''}));
            var buttons = Array.from(modal.querySelectorAll('button')).map(b => ({
                text: b.textContent.trim().substring(0,40),
                id: b.id || '',
                class: b.className.substring(0,40)
            }));
            return {found: true, iframes: iframeInfo, buttons: buttons, html: modal.innerHTML.substring(0,500)};
        })()""")
        log(f"Modal info: {json.dumps(modal_info)}", "INFO")

        # Strategy: Try clicking the "Pay with PayPal" iframe button
        # PayPal SDK renders in an iframe - we need to either:
        # A) Find and click the iframe button directly
        # B) If iframe, get the PayPal popup URL from the modal

        paypal_page = None
        popup_future = asyncio.ensure_future(ctx.wait_for_event("page", timeout=15000))
        await asyncio.sleep(0.5)

        # Try to click PayPal button - it's rendered inside an iframe
        click_result = await page.evaluate("""(() => {
            // Check for PayPal hosted button iframe
            var modal = document.querySelector('[class*=paypal-modal], [id*=paypal-modal], .pb-paypal-modal');
            if (!modal) return 'no-modal';

            // Look for clickable PayPal elements
            var allBtns = modal.querySelectorAll('button, [role=button]');
            for (var b of allBtns) {
                var txt = (b.textContent || '').toLowerCase();
                // Click "Pay with PayPal" but NOT simulate
                if ((txt.includes('pay with paypal') || txt.includes('paypal')) && !txt.includes('simulate') && !txt.includes('test')) {
                    b.click();
                    return 'clicked PayPal btn: ' + txt.substring(0,30);
                }
            }

            // Try iframe approach - get the iframe containing PayPal buttons
            var iframes = document.querySelectorAll('iframe');
            var paypalIframe = null;
            for (var iframe of iframes) {
                if (iframe.src.includes('paypal') || iframe.name.includes('paypal') || iframe.title.toLowerCase().includes('paypal')) {
                    paypalIframe = iframe;
                    break;
                }
            }
            if (paypalIframe) {
                return 'paypal-iframe-found: ' + paypalIframe.src.substring(0,80);
            }

            // Get all buttons in modal for inspection
            return 'no-paypal-btn. buttons: ' + Array.from(allBtns).map(b=>b.textContent.trim().substring(0,20)).join(' | ');
        })()""")
        log(f"PayPal click attempt: {click_result}", "ACTION")

        # Also try clicking via iframe content
        # Get all iframes on page
        all_iframes = page.frames
        log(f"Page frames count: {len(all_iframes)}", "INFO")
        for frame in all_iframes:
            fname = frame.name
            furl = frame.url
            if "paypal" in furl.lower() or "paypal" in fname.lower():
                log(f"PayPal iframe found: {furl[:80]}", "INFO")
                try:
                    # Try to click the PayPal button inside this frame
                    pp_click = await frame.evaluate("""(() => {
                        var btns = document.querySelectorAll('button, [role=button], [data-fundingSource]');
                        for (var b of btns) {
                            var txt = (b.textContent || b.getAttribute('aria-label') || '').toLowerCase();
                            if (txt.includes('paypal') || b.getAttribute('data-fundingSource') === 'paypal') {
                                b.click();
                                return 'iframe-PayPal-btn-clicked: ' + txt.substring(0,30);
                            }
                        }
                        return 'no-paypal-in-iframe. btn count: ' + btns.length;
                    })()""")
                    log(f"Iframe click: {pp_click}", "ACTION")
                except Exception as e:
                    log(f"Iframe click error: {str(e)[:50]}", "WARN")

        # Wait for PayPal popup
        try:
            paypal_page = await popup_future
            log(f"PayPal popup opened: {paypal_page.url[:80]}", "SUCCESS")
        except Exception:
            log("No popup in 15s - will use simulate button", "INFO")

        if paypal_page:
            log("=== PHASE 3B: Real PayPal Sandbox Login ===", "PHASE")
            monitor(paypal_page, "paypal")
            await paypal_page.wait_for_load_state("domcontentloaded", timeout=20000)
            await asyncio.sleep(3)

            pp_url = paypal_page.url
            log(f"PayPal URL: {pp_url[:80]}", "INFO")

            counter_before = c[0]
            c[0] += 1
            pp_ss1 = SCREENSHOT_DIR / f"{c[0]:03d}-pp1-popup-initial.png"
            try:
                await paypal_page.screenshot(path=str(pp_ss1), timeout=15000)
                screenshots_taken.append(str(pp_ss1))
                log(f"PayPal popup SS: {pp_ss1.name}", "SS")
            except Exception as e:
                log(f"SS fail: {str(e)[:40]}", "WARN")

            # Login step 1: Email
            for sel in ["#email", "input[name='email']", "input[type='email']", "#login_email"]:
                el = await paypal_page.query_selector(sel)
                if el:
                    log(f"Entering email ({sel}): {PAYPAL_EMAIL}", "ACTION")
                    await el.fill(PAYPAL_EMAIL)
                    await asyncio.sleep(0.5)
                    for ns in ["#btnNext", "#next", "button[type='submit']", "input[type='submit']"]:
                        nb = await paypal_page.query_selector(ns)
                        if nb:
                            await nb.click()
                            log(f"Next clicked: {ns}", "ACTION")
                            break
                    else:
                        await el.press("Enter")
                    await asyncio.sleep(4)
                    break

            # Intermediate screenshot
            c[0] += 1
            pp_ss2 = SCREENSHOT_DIR / f"{c[0]:03d}-pp2-after-email.png"
            try:
                await paypal_page.screenshot(path=str(pp_ss2), timeout=15000)
                screenshots_taken.append(str(pp_ss2))
                log(f"After email SS: {pp_ss2.name}", "SS")
            except Exception as e:
                log(f"SS fail: {str(e)[:40]}", "WARN")

            # Login step 2: Password
            for sel in ["#password", "input[name='password']", "input[type='password']", "#login_password"]:
                el = await paypal_page.query_selector(sel)
                if el:
                    log(f"Entering password ({sel})", "ACTION")
                    await el.fill(PAYPAL_PASSWORD)
                    await asyncio.sleep(0.5)
                    for ls in ["#btnLogin", "#signIn", "button[type='submit']", "input[type='submit']"]:
                        lb = await paypal_page.query_selector(ls)
                        if lb:
                            await lb.click()
                            log(f"Login clicked: {ls}", "ACTION")
                            break
                    else:
                        await el.press("Enter")
                    await asyncio.sleep(8)
                    break

            pp_url2 = paypal_page.url
            log(f"URL after login: {pp_url2[:80]}", "INFO")

            c[0] += 1
            pp_ss3 = SCREENSHOT_DIR / f"{c[0]:03d}-pp3-after-login.png"
            try:
                await paypal_page.screenshot(path=str(pp_ss3), timeout=15000)
                screenshots_taken.append(str(pp_ss3))
                log(f"After login SS: {pp_ss3.name}", "SS")
            except Exception as e:
                log(f"SS fail: {str(e)[:40]}", "WARN")

            # Payment confirmation
            await asyncio.sleep(5)
            confirm_r = await paypal_page.evaluate("""(() => {
                var btns = document.querySelectorAll('button, input[type=submit], [role=button]');
                for (var b of btns) {
                    var txt = (b.textContent || b.value || b.getAttribute('aria-label') || '').toLowerCase().trim();
                    if (txt.includes('pay now') || txt.includes('agree') || txt.includes('continue') ||
                        txt.includes('confirm') || txt.includes('complete') || txt.includes('pay ')) {
                        b.click();
                        return 'confirmed: ' + txt.substring(0,30);
                    }
                }
                return 'no-confirm: ' + document.body.innerText.substring(0,100);
            })()""")
            log(f"Confirm: {confirm_r}", "ACTION")
            await asyncio.sleep(10)

            c[0] += 1
            pp_ss4 = SCREENSHOT_DIR / f"{c[0]:03d}-pp4-payment-done.png"
            try:
                await paypal_page.screenshot(path=str(pp_ss4), timeout=15000)
                screenshots_taken.append(str(pp_ss4))
                log(f"Payment done SS: {pp_ss4.name}", "SS")
            except Exception as e:
                log(f"SS fail: {str(e)[:40]}", "WARN")

            log(f"PayPal final URL: {paypal_page.url[:80]}", "INFO")
            await asyncio.sleep(3)

        else:
            # No popup - click simulate button
            log("No PayPal popup - clicking Simulate Successful Payment", "ACTION")
            sim_r = await page.evaluate("""(() => {
                var btns = document.querySelectorAll('button');
                for (var b of btns) {
                    if (b.textContent.includes('Simulate Successful')) {
                        b.click();
                        return 'simulate-clicked: ' + b.textContent.trim().substring(0,40);
                    }
                }
                return 'simulate-not-found';
            })()""")
            log(f"Simulate: {sim_r}", "ACTION")
            await asyncio.sleep(15)
            await ss(page, "p3-simulate-used")

        # PHASE 4: POST-PAYMENT QUESTIONNAIRE
        log("=== PHASE 4: Post-payment Q&A ===", "PHASE")
        await asyncio.sleep(8)
        await ss(page, "p4-initial")

        ptc_state = await page.evaluate("""(() => {
            var msgs = document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai');
            return {
                count: msgs.length,
                msgs: Array.from(msgs).slice(0,3).map(m => m.textContent.trim().substring(0,60)),
                hasInput: !!document.querySelector('#ptc-input, textarea.ptc-input, .ptc-input'),
            };
        })()""")
        log(f"PTC initial: {ptc_state}", "INFO")

        ai_n = ptc_state["count"]

        qa = [
            ("TestUser Smith", "name"),
            ("testuser@purebrain-test.com", "email"),
            ("TestCorp Marketing", "company"),
            ("CEO", "role"),
            ("Automate my marketing workflows", "goal"),
        ]

        for answer, label in qa:
            log(f"Q&A [{label}]: {answer}", "ACTION")
            ok = await ptc_type_send(page, answer)
            if ok:
                ai_n = await wait_ai(page, ai_n, timeout=25)
            else:
                log(f"Could not send [{label}]", "WARN")
            await asyncio.sleep(2)
            await ss(page, f"p4-{label}")

        # PHASE 5: BIRTH PIPELINE + OAUTH
        log("=== PHASE 5: Birth Pipeline + OAuth ===", "PHASE")
        await asyncio.sleep(5)
        await ss(page, "p5-birth-state")

        birth_state = await page.evaluate("""(() => {
            var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai'))
                .map(m => m.textContent.trim().substring(0,100));

            // Look for OAuth links or birth-related elements
            var links = [];
            document.querySelectorAll('a').forEach(a => {
                if (a.href && (a.href.includes('oauth') || a.href.includes('google') || a.href.includes('birth'))) {
                    links.push(a.href.substring(0,100));
                }
            });

            // Look for auth buttons
            var authBtns = [];
            document.querySelectorAll('button, a').forEach(b => {
                var txt = (b.textContent || '').trim();
                if (txt.includes('Authorize') || txt.includes('Auth') || txt.includes('key') || txt.includes('Google')) {
                    authBtns.push({text: txt.substring(0,40), tag: b.tagName, href: b.href || ''});
                }
            });

            return {msgCount: msgs.length, lastMsgs: msgs.slice(-3), oauthLinks: links, authBtns: authBtns};
        })()""")
        log(f"Birth state: {json.dumps(birth_state)}", "INFO")

        # Click "Authorize Keen's AI Brain" if present
        auth_result = await page.evaluate("""(() => {
            var links = document.querySelectorAll('a, button');
            for (var l of links) {
                var txt = (l.textContent || '').trim();
                if (txt.includes('Authorize') || txt.includes('Keen') || txt.includes('Brain')) {
                    var href = l.href || '';
                    l.click();
                    return 'clicked: ' + txt.substring(0,40) + ' href: ' + href.substring(0,60);
                }
            }
            return 'no-auth-btn';
        })()""")
        log(f"Auth btn: {auth_result}", "ACTION")
        await asyncio.sleep(5)
        await ss(page, "p5-after-auth-click")

        # PHASE 6: CONTINUE THROUGH REMAINING MESSAGES
        log("=== PHASE 6: Continue to Final Message ===", "PHASE")

        for i in range(15):
            inp_state = await page.evaluate("""(() => {
                var el = document.querySelector('#ptc-input, textarea.ptc-input, .ptc-input, textarea');
                if (!el) return {found: false};
                return {found: true, visible: el.offsetParent !== null, disabled: el.disabled};
            })()""")

            if not inp_state.get("found") or inp_state.get("disabled") or not inp_state.get("visible"):
                log(f"[{i}] No active input", "INFO")
                break

            cur_n = await page.evaluate("(() => document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai').length)()")
            log(f"[{i}] Sending continuation (ai_n={cur_n})", "ACTION")

            ok = await ptc_type_send(page, "Yes, let's continue.")
            if ok:
                new_n = await wait_ai(page, cur_n, timeout=25)
                if new_n == cur_n:
                    log(f"[{i}] Stalled", "INFO")
                    break
            else:
                break

            await ss(page, f"p6-ex{i:02d}")
            await asyncio.sleep(2)

            # Check portal button
            portal = await page.evaluate("""(() => {
                var els = document.querySelectorAll('a, button');
                for (var el of els) {
                    var txt = (el.textContent || '').trim().toLowerCase();
                    var href = (el.href || el.getAttribute('href') || '');
                    if (href.includes('portal') || href.includes('app.purebrain') || txt.includes('launch portal') || txt.includes('go to portal')) {
                        return {found: true, text: (el.textContent || '').trim().substring(0,40), href: href.substring(0,80)};
                    }
                }
                return {found: false};
            })()""")
            if portal.get("found"):
                log(f"PORTAL FOUND: {portal}", "SUCCESS")
                await ss(page, f"p6-portal-ex{i}")
                break

        # Final state
        await asyncio.sleep(5)
        await ss(page, "p7-final")

        final = await page.evaluate("""(() => {
            var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai'))
                .map(m => m.textContent.trim().substring(0,100));
            var els = document.querySelectorAll('a, button');
            var portal = null;
            for (var el of els) {
                var href = (el.href || el.getAttribute('href') || '');
                var txt = (el.textContent || '').trim();
                if (href.includes('portal') || href.includes('app.purebrain') || txt.includes('Portal') || txt.includes('Launch')) {
                    portal = {text: txt.substring(0,40), href: href.substring(0,80)};
                    break;
                }
            }
            return {totalMsgs: msgs.length, msgs: msgs, portal: portal};
        })()""")
        log(f"FINAL: {final['totalMsgs']} msgs, portal={final['portal']}", "SUMMARY")
        for i, m in enumerate(final.get("msgs", [])):
            log(f"  msg[{i}]: {m}", "AI")

        await browser.close()

    # GENERATE REPORT
    log("=== Generating Report ===", "END")
    report_lines = [
        "# E2E PayPal Real Sandbox - Full Report v4",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Target**: {PAGE_URL}",
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
    ]

    if seed_fires:
        report_lines += ["## SEED FIRES (Captured)", ""]
        for sf in seed_fires:
            report_lines += [
                f"### {sf['ts']} - SEED FIRED",
                f"- `{sf['method']} {sf['status']}` `{sf['url']}`",
                f"- Response: `{sf['body'][:200]}`",
                "",
            ]
    else:
        report_lines += [
            "## Seed Fires",
            "",
            "**None captured by Playwright network monitor.**",
            "Seeds may still fire - check Witness server logs for this time window.",
            "",
        ]

    report_lines += ["## Network API Calls", ""]
    for nc in network_calls:
        report_lines.append(f"- [{nc['ts']}] [{nc['page']}] `{nc['method']} {nc['status']}` `{nc['url'][:80]}`")
        report_lines.append(f"  `{nc['body'][:100]}`")

    report_lines += ["", "## Console Logs", ""]
    for cl in console_logs:
        report_lines.append(f"- [{cl['ts']}] [{cl['page']}][{cl['type']}]: {cl['text'][:120]}")

    report_lines += ["", "## Screenshots", ""]
    for s in screenshots_taken:
        report_lines.append(f"- `{s}`")

    report_lines += ["", "## Timeline", "", "```"]
    report_lines.extend(timeline)
    report_lines.append("```")

    REPORT_PATH.write_text("\n".join(report_lines))

    print(f"\n{'='*60}")
    print(f"Report: {REPORT_PATH}")
    print(f"Seeds: {len(seed_fires)}")
    print(f"Net calls: {len(network_calls)}")
    print(f"Screenshots: {len(screenshots_taken)}")
    if seed_fires:
        print("\nSEED FIRES:")
        for sf in seed_fires:
            print(f"  {sf['ts']} {sf['status']} {sf['url']}")
            print(f"  -> {sf['body'][:100]}")


if __name__ == "__main__":
    asyncio.run(run())
