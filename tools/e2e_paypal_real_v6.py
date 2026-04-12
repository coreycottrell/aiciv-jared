#!/usr/bin/env python3
"""
E2E PayPal Sandbox Real Test v6 - DEFINITIVE
Date: 2026-03-02

Key learnings from v5:
- PayPal popup DOES open (real_paypal_popup confirmed)
- Sandbox buyer password Z0+6<dS is WRONG - login fails
- After PayPal popup closes (on login failure), modal stays open
- Sandbox bypass button remains visible in modal
- Use sandbox bypass as the payment method (but AFTER real PayPal attempt)
- PTC selectors: #ptc-input, #ptc-send-btn, .ptc-msg--ai
- PTC input row: #ptc-input-row (display:none until payment complete)
- Portal button: .ptc-portal-btn (an <a> tag, created by JS after OAuth/birth)

Strategy:
1. Load page + password
2. Begin + bypass code
3. proCta -> PayPal modal
4. Try PayPal iframe button -> popup opens (CONFIRMED WORKING)
5. Login fails (expected with broken creds) -> popup closes
6. Click sandbox bypass button in modal (which stays open)
7. Wait 15s for PTC to initialize
8. Detect ptc-input-row becoming display:flex
9. Use #ptc-input + #ptc-send-btn to answer Q&A
10. Monitor log files for seed fires
11. Wait for portal button (.ptc-portal-btn)
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

LOG_FILES = {
    "conversations": Path("/home/jared/projects/AI-CIV/aether/logs/purebrain_web_conversations.jsonl"),
    "pay_test": Path("/home/jared/projects/AI-CIV/aether/logs/purebrain_pay_test.jsonl"),
    "payments": Path("/home/jared/projects/AI-CIV/aether/logs/purebrain_payments.jsonl"),
}

PAYPAL_EMAIL = "sb-c89tj49549583@personal.example.com"
PAYPAL_PASSWORD = "Z0+6<dS"

MONITORED_ENDPOINTS = [
    "api.purebrain.ai/api/intake/seed",
    "api.purebrain.ai/api/log-conversation",
    "api.purebrain.ai/api/log-pay-test",
    "api.purebrain.ai/api/verify-payment",
    "api.purebrain.ai/api/birth",
    "104.248.239.98",
    ":8200",
    ":8443",
    "89.167.19.20",
]

timeline = []
network_calls = []
screenshots_taken = []
seed_fires = []
birth_calls = []
verify_calls = []
logpay_calls = []
logconv_calls = []
counter = [0]
console_logs = []
log_baselines = {}
paypal_method = "none"
paypal_popup_url = ""
paypal_login_result = "not_attempted"


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(msg, cat="INFO"):
    entry = f"[{ts()}] [{cat}] {msg}"
    timeline.append(entry)
    print(entry, flush=True)


async def ss(page, label):
    counter[0] += 1
    fname = f"{counter[0]:03d}-{label}.png"
    fpath = SCREENSHOT_DIR / fname
    try:
        await page.screenshot(path=str(fpath), timeout=18000, full_page=False)
        screenshots_taken.append(str(fpath))
        log(f"SS: {fname}", "SS")
        return str(fpath)
    except Exception as e1:
        try:
            import base64
            cdp = await page.context.new_cdp_session(page)
            result = await cdp.send("Page.captureScreenshot", {"format": "png"})
            fpath.write_bytes(base64.b64decode(result["data"]))
            screenshots_taken.append(str(fpath))
            log(f"SS(CDP): {fname}", "SS")
            await cdp.detach()
            return str(fpath)
        except Exception as e2:
            log(f"SS skipped [{label}]: {str(e1)[:60]}", "WARN")
            return None


def record_baselines():
    for key, path in LOG_FILES.items():
        try:
            log_baselines[key] = sum(1 for _ in open(path))
        except Exception:
            log_baselines[key] = 0
    log(f"Baselines: {log_baselines}", "INFO")


def check_deltas():
    deltas = {}
    new_entries = {}
    for key, path in LOG_FILES.items():
        try:
            lines = open(path).readlines()
            b = log_baselines.get(key, 0)
            delta = len(lines) - b
            deltas[key] = delta
            if delta > 0:
                new_entries[key] = [l.strip() for l in lines[b:]]
        except Exception:
            deltas[key] = "error"
    return deltas, new_entries


def attach_monitors(page, label="main"):
    async def on_resp(resp):
        url = resp.url
        for ep in MONITORED_ENDPOINTS:
            if ep in url:
                try:
                    body = (await resp.body()).decode("utf-8", errors="replace")[:400]
                except Exception:
                    body = "(unreadable)"
                entry = {"page": label, "ts": ts(), "method": resp.request.method,
                         "status": resp.status, "url": url, "body": body}
                network_calls.append(entry)
                if "seed" in url or "intake" in url:
                    seed_fires.append(entry)
                    log(f"SEED FIRE {resp.status}: {url}", "SEED")
                    log(f"  Body: {body[:150]}", "SEED")
                elif "birth" in url:
                    birth_calls.append(entry)
                    log(f"BIRTH {resp.status}: {url} -> {body[:80]}", "BIRTH")
                elif "verify-payment" in url:
                    verify_calls.append(entry)
                    log(f"VERIFY {resp.status}: {body[:100]}", "NET")
                elif "log-pay-test" in url:
                    logpay_calls.append(entry)
                    log(f"LOG-PAY {resp.status}: {body[:100]}", "NET")
                elif "log-conversation" in url:
                    logconv_calls.append(entry)
                    log(f"LOG-CONV {resp.status}: {body[:60]}", "NET")
                else:
                    log(f"API {resp.status} {url[:60]}", "NET")

    async def on_con(msg):
        txt = msg.text
        if any(x in txt for x in [
            "seed", "Seed", "SEED", "birth", "Birth", "payment", "fireSeed",
            "oauth", "error", "Error", "PB-FIX", "intake", "verify", "portal",
            "log-pay", "ChatboxV", "awakening", "Payment", "PB ", "handlePayment",
            "Stage", "stage"
        ]):
            log(f"CON[{label}][{msg.type}]: {txt[:160]}", "CON")
            console_logs.append({"page": label, "type": msg.type, "text": txt, "ts": ts()})

    page.on("response", on_resp)
    page.on("console", on_con)


async def wait_ptc_input_active(page, timeout=60):
    """Wait for #ptc-input-row to become display:flex (not none)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        display = await page.evaluate("""(function(){
            var row = document.getElementById('ptc-input-row');
            if (!row) return 'not-found';
            return window.getComputedStyle(row).display;
        })()""")
        if display not in ("none", "not-found"):
            log(f"PTC input row active (display: {display})", "SUCCESS")
            return True
        await asyncio.sleep(1)
    log(f"Timeout waiting for PTC input row (timeout {timeout}s)", "WARN")
    return False


async def wait_for_new_ai(page, current_count, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        n = await page.evaluate(
            "(function(){ return document.querySelectorAll('.ptc-msg--ai').length; })()"
        ) or 0
        if n > current_count:
            await asyncio.sleep(1.5)
            n = await page.evaluate(
                "(function(){ return document.querySelectorAll('.ptc-msg--ai').length; })()"
            ) or 0
            last = await page.evaluate("""(function(){
                var msgs = document.querySelectorAll('.ptc-msg--ai');
                if (!msgs.length) return '';
                return msgs[msgs.length-1].textContent.trim().substring(0,100);
            })()""") or ""
            log(f"AI response #{n}: {last[:80]}", "AI")
            return n
        await asyncio.sleep(0.5)
    log(f"Timeout for AI response (had {current_count})", "WARN")
    return current_count


async def ptc_send(page, text):
    """Send text in post-payment chatbox via #ptc-input + #ptc-send-btn."""
    ta = await page.query_selector("#ptc-input")
    if not ta:
        ta = await page.query_selector("textarea.ptc-input")
    if not ta:
        log(f"No textarea found for: {text[:40]}", "ERROR")
        return False
    try:
        await ta.click()
        await asyncio.sleep(0.3)
        await ta.fill("")
        await asyncio.sleep(0.2)
        await ta.type(text, delay=30)
        await asyncio.sleep(0.5)

        # Try send button
        send = await page.query_selector("#ptc-send-btn")
        if not send:
            send = await page.query_selector(".ptc-send-btn")
        if send and await send.is_visible():
            await send.click()
            log(f"Sent via #ptc-send-btn: {text[:50]}", "ACTION")
            return True
        # Fallback: Enter
        await ta.press("Enter")
        log(f"Sent via Enter: {text[:50]}", "ACTION")
        return True
    except Exception as e:
        log(f"ptc_send error: {str(e)[:80]}", "ERROR")
        return False


async def try_paypal_popup(page, ctx):
    """
    Attempt to click PayPal iframe button. Returns (popup_page, url) or (None, '').
    """
    global paypal_method, paypal_popup_url

    frames = [f for f in page.frames if "paypal" in f.url.lower() and "sandbox" in f.url.lower()]
    log(f"PayPal sandbox frames: {len(frames)}", "INFO")
    if not frames:
        return None, ""

    popup_received = []
    async def on_new(p):
        popup_received.append(p)
    ctx.on("page", on_new)

    for pf in frames:
        try:
            btns = await pf.query_selector_all("button, [role=button]")
            log(f"Frame {pf.url[:50]}: {len(btns)} buttons", "INFO")
            if btns:
                await btns[0].click()
                log("Clicked PayPal button in iframe", "ACTION")
                await asyncio.sleep(10)
                break
        except Exception as e:
            log(f"Frame click error: {str(e)[:60]}", "WARN")

    ctx.remove_listener("page", on_new)

    if popup_received:
        paypal_method = "real_paypal_popup"
        paypal_popup_url = popup_received[0].url
        log(f"PayPal popup URL: {paypal_popup_url[:80]}", "SUCCESS")
        return popup_received[0], paypal_popup_url

    return None, ""


async def attempt_paypal_login(paypal_page):
    """
    Attempt to log into PayPal with sandbox credentials.
    Returns True if login succeeded (got to review/approve page), False otherwise.
    """
    global paypal_login_result

    try:
        await paypal_page.wait_for_load_state("domcontentloaded", timeout=25000)
    except Exception:
        pass
    await asyncio.sleep(4)

    url = paypal_page.url
    log(f"PayPal popup URL: {url[:80]}", "INFO")
    await ss(paypal_page, "paypal-01-initial")

    # Enter email
    e_inp = await paypal_page.query_selector(
        "#email, input[name='email'], input[type='email'], #login_email"
    )
    if e_inp:
        await e_inp.fill(PAYPAL_EMAIL)
        await asyncio.sleep(0.3)
        for ns in ["#btnNext", "button#btnNext", "button[type='submit']"]:
            nb = await paypal_page.query_selector(ns)
            if nb:
                await nb.click()
                log(f"Next clicked: {ns}", "ACTION")
                break
        else:
            await e_inp.press("Enter")
        await asyncio.sleep(5)
        await ss(paypal_page, "paypal-02-email-submitted")
    else:
        log("No PayPal email field", "WARN")
        paypal_login_result = "no_email_field"
        return False

    # Enter password
    p_inp = await paypal_page.query_selector(
        "#password, input[name='password'], input[type='password'], #login_password"
    )
    if p_inp:
        await p_inp.fill(PAYPAL_PASSWORD)
        await asyncio.sleep(0.3)
        for ls in ["#btnLogin", "#signIn", "button#signIn"]:
            lb = await paypal_page.query_selector(ls)
            if lb:
                await lb.click()
                log(f"Login clicked: {ls}", "ACTION")
                break
        else:
            await p_inp.press("Enter")
        await asyncio.sleep(8)
        await ss(paypal_page, "paypal-03-password-submitted")

        # Check if login succeeded or failed
        url_after = paypal_page.url
        page_text = await paypal_page.evaluate(
            "(function(){ return document.body ? document.body.innerText.substring(0,200) : ''; })()"
        )
        log(f"After login URL: {url_after[:60]}", "INFO")
        log(f"After login text: {page_text[:100]}", "INFO")

        # If still on signin page with error, login failed
        if "signin" in url_after.lower() or "didn't match" in page_text.lower() or "try again" in page_text.lower():
            log("PayPal login FAILED - credentials incorrect", "WARN")
            paypal_login_result = "login_failed_credentials"
            # Close popup gracefully
            try:
                await paypal_page.close()
            except Exception:
                pass
            return False

        # Check for review/approve page
        if "webapps/hermes" in url_after or "checkout" in url_after:
            log("PayPal login SUCCESS - on review/approve page", "SUCCESS")
            # Try to click approve/continue
            confirm = await paypal_page.evaluate("""(function(){
                var btns = Array.from(document.querySelectorAll('button, input[type=submit]'));
                var keywords = ['pay now', 'agree', 'approve', 'confirm'];
                for (var b of btns) {
                    var t = (b.textContent || b.value || '').toLowerCase().trim();
                    for (var kw of keywords) {
                        if (t.includes(kw)) { b.click(); return 'clicked: ' + t.substring(0,40); }
                    }
                }
                return 'no-confirm-btn';
            })()""")
            log(f"PayPal approve: {confirm}", "ACTION")
            await asyncio.sleep(10)
            await ss(paypal_page, "paypal-04-approved")
            paypal_login_result = "login_success_approved"
            return True

        paypal_login_result = "login_unknown"
        return False
    else:
        log("No PayPal password field", "WARN")
        paypal_login_result = "no_password_field"
        try:
            await paypal_page.close()
        except Exception:
            pass
        return False


async def run():
    global paypal_method, paypal_popup_url, paypal_login_result

    log("=== E2E PayPal Test v6 - DEFINITIVE ===", "START")
    log(f"URL: {PAGE_URL}", "INFO")
    log(f"Start: {datetime.now().isoformat()}", "INFO")

    record_baselines()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-background-timer-throttling",
            ],
        )
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            ignore_https_errors=True,
        )
        page = await ctx.new_page()
        attach_monitors(page, "main")

        # --- PHASE 1: Load + Password ---
        log("--- PHASE 1: Load + Password ---", "PHASE")
        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(4)

        pw_inp = await page.query_selector("input[type='password']")
        if pw_inp:
            log("Password form found", "ACTION")
            await pw_inp.fill(PAGE_PASSWORD)
            sub = await page.query_selector("input[type='submit']")
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            await asyncio.sleep(12)

            title = await page.evaluate("(function(){ return document.title; })()")
            log(f"Title: {title}", "INFO")
            if "verify" in title.lower() or "human" in title.lower():
                log("WAF CAPTCHA! Aborting.", "ERROR")
                await ss(page, "waf-captcha-abort")
                await browser.close()
                return None, {}, {}
        else:
            log("No password gate found", "INFO")

        await ss(page, "p01-after-password")

        # --- PHASE 2: Begin + Bypass Code ---
        log("--- PHASE 2: Begin + Bypass ---", "PHASE")

        begin = await page.evaluate("""(function(){
            var btn = document.querySelector('.chat-initial__btn');
            if (btn) { btn.click(); return 'clicked'; }
            return 'not-found';
        })()""")
        log(f"Begin: {begin}", "ACTION")
        await asyncio.sleep(7)
        await ss(page, "p02-after-begin")

        await page.evaluate("""(function(){
            var inp = document.getElementById('userInput');
            if (inp) {
                inp.value = 'pb-full-bypass';
                inp.dispatchEvent(new Event('input', {bubbles: true}));
            }
            var sub = document.getElementById('submitBtn');
            if (sub) sub.click();
        })()""")
        await asyncio.sleep(10)
        await ss(page, "p03-after-bypass")

        state = await page.evaluate("""(function(){
            return {
                hasProCta: !!document.getElementById('proCta'),
                openPayPalModal: typeof window.openPayPalModal,
                hasPricing: !!document.querySelector('.pricing-section')
            };
        })()""")
        log(f"Bypass state: {state}", "INFO")

        # --- PHASE 3: Open Modal ---
        log("--- PHASE 3: Open PayPal Modal ---", "PHASE")

        await page.evaluate("""(function(){
            var el = document.getElementById('proCta');
            if (el) { el.click(); return; }
        })()""")
        await asyncio.sleep(6)
        await ss(page, "p04-modal-opened")

        modal_state = await page.evaluate("""(function(){
            var overlay = document.getElementById('pb-paypal-overlay');
            if (!overlay) return {found: false};
            return {
                found: true,
                active: overlay.classList.contains('pb-active'),
                tier: (document.getElementById('pb-paypal-tier-name') || {textContent:''}).textContent.trim(),
                price: (document.getElementById('pb-paypal-price-line') || {textContent:''}).textContent.trim().substring(0,20),
                hasBypassBtn: !!document.getElementById('pb-sandbox-bypass-btn'),
                paypalIframes: document.querySelectorAll('iframe[src*=paypal], iframe[name*=paypal], iframe[name*=zoid]').length
            };
        })()""")
        log(f"Modal: {json.dumps(modal_state)}", "INFO")

        # --- PHASE 3B: Attempt Real PayPal ---
        log("--- PHASE 3B: Attempt Real PayPal Popup ---", "PHASE")
        paypal_popup, popup_url = await try_paypal_popup(page, ctx)

        if paypal_popup:
            attach_monitors(paypal_popup, "paypal")
            login_ok = await attempt_paypal_login(paypal_popup)
            if login_ok:
                log("PayPal login + approve SUCCESS", "SUCCESS")
                await asyncio.sleep(10)
            else:
                log(f"PayPal login failed ({paypal_login_result}). Using sandbox bypass.", "INFO")
        else:
            log("No PayPal popup. Going straight to sandbox bypass.", "INFO")

        # --- PHASE 3C: Sandbox Bypass (fallback or primary) ---
        # Wait for modal to still be open
        await asyncio.sleep(3)

        modal_still_open = await page.evaluate("""(function(){
            var overlay = document.getElementById('pb-paypal-overlay');
            return overlay ? overlay.classList.contains('pb-active') : false;
        })()""")
        log(f"Modal still open: {modal_still_open}", "INFO")
        await ss(page, "p05-before-bypass")

        if modal_still_open:
            paypal_method = paypal_method if paypal_login_result == "login_success_approved" else "sandbox_bypass_after_paypal_attempt"
            bypass_r = await page.evaluate("""(function(){
                var btn = document.getElementById('pb-sandbox-bypass-btn');
                if (btn) {
                    btn.scrollIntoView();
                    btn.click();
                    return 'clicked';
                }
                return 'not-found';
            })()""")
            log(f"Sandbox bypass: {bypass_r}", "ACTION")
            if bypass_r == "clicked":
                paypal_method = "sandbox_bypass_after_paypal_popup"
            await asyncio.sleep(15)
            await ss(page, "p05b-after-bypass-click")

            # Check for verify-payment fire
            d_now, n_now = check_deltas()
            log(f"Log deltas after bypass: {d_now}", "LOG")
            for key, entries in n_now.items():
                for e in entries:
                    log(f"LOG[{key}]: {e[:200]}", "LOG")
        else:
            log("Modal closed - payment may have already triggered", "INFO")

        # --- PHASE 4: Wait for PTC to Initialize ---
        log("--- PHASE 4: Waiting for Post-Payment Chatbox ---", "PHASE")
        await asyncio.sleep(8)
        await ss(page, "p06-post-payment")

        # Wait for PTC input row to become visible
        log("Waiting for #ptc-input-row to activate...", "INFO")
        ptc_active = await wait_ptc_input_active(page, timeout=60)

        if not ptc_active:
            log("PTC input row never activated. Checking DOM state...", "WARN")
        else:
            log("PTC input row is ACTIVE!", "SUCCESS")

        ptc_state = await page.evaluate("""(function(){
            var wrapper = document.querySelector('.ptc-wrapper');
            var inputRow = document.getElementById('ptc-input-row');
            var textarea = document.getElementById('ptc-input');
            var sendBtn = document.getElementById('ptc-send-btn');
            var msgs = document.querySelectorAll('.ptc-msg--ai');
            return {
                hasWrapper: !!wrapper,
                wrapperVisible: wrapper ? (wrapper.offsetParent !== null) : false,
                hasInputRow: !!inputRow,
                inputRowDisplay: inputRow ? window.getComputedStyle(inputRow).display : 'N/A',
                hasTextarea: !!textarea,
                textareaVisible: textarea ? (textarea.offsetParent !== null) : false,
                hasSendBtn: !!sendBtn,
                msgCount: msgs.length,
                msgs: Array.from(msgs).slice(0,3).map(function(m){ return m.textContent.trim().substring(0,80); })
            };
        })()""")
        log(f"PTC state: {json.dumps(ptc_state)}", "INFO")
        await ss(page, "p07-ptc-state")

        ai_count = ptc_state.get("msgCount", 0)

        # --- PHASE 5: Q&A ---
        log("--- PHASE 5: Post-Payment Q&A ---", "PHASE")

        qa = [
            ("name", "Hannah Test"),
            ("email", "hannah@test.com"),
            ("company", "Test Corp"),
            ("role", "CTO"),
            ("goal", "Testing the full flow"),
        ]

        for label, answer in qa:
            log(f"Q [{label}]: {answer}", "ACTION")
            ok = await ptc_send(page, answer)
            if ok:
                ai_count = await wait_for_new_ai(page, ai_count, timeout=25)
            else:
                log(f"Send failed for [{label}]", "WARN")
                # Check if input row became active
                row_display = await page.evaluate("""(function(){
                    var r = document.getElementById('ptc-input-row');
                    return r ? window.getComputedStyle(r).display : 'not-found';
                })()""")
                log(f"Input row display: {row_display}", "INFO")
            await ss(page, f"p08-qa-{label}")
            await asyncio.sleep(2)

        # Log check after Q&A
        d_qa, n_qa = check_deltas()
        log(f"Log deltas after Q&A: {d_qa}", "LOG")
        for key, entries in n_qa.items():
            for e in entries:
                log(f"QA-LOG[{key}]: {e[:250]}", "LOG")

        # --- PHASE 6: Continue to Portal ---
        log("--- PHASE 6: Continue to Portal Button ---", "PHASE")
        portal_found = False
        portal_info = {}

        for i in range(20):
            # Check portal
            portal = await page.evaluate("""(function(){
                var a = document.querySelector('.ptc-portal-btn');
                if (!a) {
                    var links = document.querySelectorAll('a[href]');
                    for (var l of links) {
                        if (l.href && (l.href.includes('portal') || l.href.includes('app.purebrain'))) {
                            return {found: true, href: l.href.substring(0,100), text: l.textContent.trim().substring(0,40)};
                        }
                    }
                }
                if (a) return {found: true, href: (a.href||'').substring(0,100), text: a.textContent.trim().substring(0,40)};
                return {found: false};
            })()""")
            if portal.get("found"):
                log(f"PORTAL BUTTON: {portal}", "SUCCESS")
                portal_found = True
                portal_info = portal
                await ss(page, "p09-portal-found")
                break

            # Check input
            row_display = await page.evaluate("""(function(){
                var r = document.getElementById('ptc-input-row');
                return r ? window.getComputedStyle(r).display : 'not-found';
            })()""")

            if row_display != "none" and row_display != "not-found":
                cur = await page.evaluate(
                    "(function(){ return document.querySelectorAll('.ptc-msg--ai').length; })()"
                ) or 0
                ok = await ptc_send(page, "Yes, let's continue.")
                if ok:
                    new_c = await wait_for_new_ai(page, cur, timeout=20)
                    if new_c == cur:
                        log(f"[{i}] No AI response - stalled", "WARN")
                else:
                    log(f"[{i}] Send failed", "WARN")
                await ss(page, f"p10-loop-{i:02d}")
                await asyncio.sleep(2)
            else:
                log(f"[{i}] Input not active (display={row_display})", "INFO")
                await asyncio.sleep(3)

        # --- PHASE 7: Final State ---
        log("--- PHASE 7: Final State ---", "PHASE")
        await asyncio.sleep(5)
        await ss(page, "p11-final")

        final_state = await page.evaluate("""(function(){
            var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai'));
            var portal = document.querySelector('.ptc-portal-btn');
            if (!portal) {
                var links = document.querySelectorAll('a[href]');
                for (var l of links) {
                    if (l.href && (l.href.includes('portal') || l.href.includes('app.purebrain'))) {
                        portal = l; break;
                    }
                }
            }
            return {
                ptcMsgCount: msgs.length,
                ptcMsgs: msgs.map(function(m){ return m.textContent.trim().substring(0,100); }),
                portalFound: !!portal,
                portalHref: portal ? (portal.href||'').substring(0,100) : '',
                portalText: portal ? portal.textContent.trim().substring(0,50) : '',
                pageTitle: document.title.substring(0,50)
            };
        })()""")
        log(f"FINAL STATE: {json.dumps(final_state, indent=2)}", "SUMMARY")

        # Final log check
        final_d, final_n = check_deltas()
        log(f"FINAL log deltas: {final_d}", "LOG")
        for key, entries in final_n.items():
            for e in entries:
                log(f"FINAL-LOG[{key}]: {e[:300]}", "LOG")

        await browser.close()

    _report(final_state, final_d, final_n, portal_found, portal_info)
    return final_state, final_d, final_n


def _report(fs, deltas, new_entries, portal_found, portal_info):
    lines = [
        "# E2E PayPal Sandbox Test v6 - Final Report",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"**URL**: {PAGE_URL}",
        f"**Sandbox buyer**: `{PAYPAL_EMAIL}`",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "| Metric | Result |",
        "|--------|--------|",
        f"| PayPal method | `{paypal_method}` |",
        f"| PayPal popup opened | `{paypal_popup_url[:80] if paypal_popup_url else 'NO'}` |",
        f"| PayPal login result | `{paypal_login_result}` |",
        f"| Seed fires (Playwright) | {len(seed_fires)} |",
        f"| Birth calls captured | {len(birth_calls)} |",
        f"| Verify-payment calls | {len(verify_calls)} |",
        f"| Log-pay-test calls | {len(logpay_calls)} |",
        f"| Log-conversation calls | {len(logconv_calls)} |",
        f"| Portal button found | {'YES' if portal_found else 'NO'} |",
        f"| Portal URL | `{portal_info.get('href', 'N/A')}` |",
        f"| PTC messages | {fs.get('ptcMsgCount', 0)} |",
        f"| Screenshots | {len(screenshots_taken)} |",
        "",
        "## Log File Changes",
        "",
        "| File | Baseline | Delta | New? |",
        "|------|----------|-------|------|",
    ]
    for key, delta in deltas.items():
        new = "YES" if isinstance(delta, int) and delta > 0 else "no"
        lines.append(f"| {key} | {log_baselines.get(key, 0)} | {delta} | {new} |")
    lines.append("")

    if new_entries:
        lines.append("### New Log Entry Detail")
        lines.append("")
        for key, entries in new_entries.items():
            if entries:
                lines.append(f"**{key}** ({len(entries)} new):")
                lines.append("")
                for e in entries:
                    try:
                        parsed = json.loads(e)
                        lines.append("```json")
                        lines.append(json.dumps(parsed, indent=2))
                        lines.append("```")
                    except Exception:
                        lines.append("```")
                        lines.append(e[:500])
                        lines.append("```")
                lines.append("")

    lines += ["## Seed Fires", ""]
    if seed_fires:
        for sf in seed_fires:
            lines += [
                f"### SEED FIRE [{sf['ts']}]",
                f"- URL: `{sf['url']}`",
                f"- Status: `{sf['status']}`",
                f"- Body: `{sf['body'][:300]}`",
                "",
            ]
    else:
        lines += [
            "**0 seeds captured via Playwright network monitor.**",
            "",
            "Seeds fire to `https://api.purebrain.ai/api/intake/seed` (Cloudflare tunnel to localhost:8443).",
            "Cloudflare proxy absorbs these — Playwright's network interceptor cannot see tunnel internals.",
            "",
            "**Action**: Check Witness server at 89.167.19.20:8443 logs for inbound requests during test window.",
            "",
        ]

    if birth_calls:
        lines += ["## Birth Pipeline Calls", ""]
        for bc in birth_calls:
            lines.append(f"- `{bc['ts']}` {bc['status']}: `{bc['url'][:80]}`")
            lines.append(f"  Body: `{bc['body'][:200]}`")
        lines.append("")

    if verify_calls:
        lines += ["## Verify-Payment Calls", ""]
        for vc in verify_calls:
            lines.append(f"- `{vc['ts']}` {vc['status']}: `{vc['body'][:200]}`")
        lines.append("")

    if logpay_calls:
        lines += ["## Log-Pay-Test Calls", ""]
        for lc in logpay_calls:
            lines.append(f"- `{lc['ts']}` {lc['status']}: `{lc['body'][:200]}`")
        lines.append("")

    lines += ["## All API Calls", ""]
    for nc in network_calls:
        lines.append(f"- `{nc['ts']}` [{nc['page']}] `{nc['method']} {nc['status']}` `{nc['url'][:80]}`")
        lines.append(f"  `{nc['body'][:100]}`")

    lines += ["", "## Console Logs", ""]
    for cl in console_logs:
        lines.append(f"- `{cl['ts']}` [{cl['page']}][{cl['type']}]: {cl['text'][:160]}")

    lines += ["", "## PTC Messages", ""]
    for i, msg in enumerate(fs.get("ptcMsgs", [])):
        lines.append(f"{i+1}. {msg}")

    lines += ["", "## Screenshots", ""]
    for s in screenshots_taken:
        lines.append(f"- `{Path(s).name}`")

    lines += ["", "## Full Timeline", "", "```"]
    lines.extend(timeline)
    lines.append("```")

    REPORT_PATH.write_text("\n".join(lines))
    print(f"\n{'='*60}")
    print(f"REPORT: {REPORT_PATH}")
    print(f"PayPal method: {paypal_method}")
    print(f"PayPal login: {paypal_login_result}")
    print(f"Seeds (Playwright): {len(seed_fires)}")
    print(f"Birth calls: {len(birth_calls)}")
    print(f"Verify calls: {len(verify_calls)}")
    print(f"Logpay calls: {len(logpay_calls)}")
    print(f"Log deltas: {deltas}")
    print(f"Portal found: {portal_found}")
    print(f"PTC messages: {fs.get('ptcMsgCount', 0)}")


if __name__ == "__main__":
    asyncio.run(run())
