#!/usr/bin/env python3
"""
E2E Seed Logging Verification Test - 2026-03-03
Purpose: Verify seed files fire correctly:
  1. ONE seed after payment completion (PayPal verified)
  2. ONE seed after post-payment chat completion (conversation_complete)

Based on v6 script patterns (proven working 2026-03-02).
New sandbox buyer creds: sb-47x6s38597220@personal.example.com / testpass123
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

PAGE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-seed-test-20260303")
REPORT_PATH = Path("/home/jared/projects/AI-CIV/aether/exports/e2e-seed-verify-report-20260303.md")

PAYPAL_EMAIL = "sb-47x6s38597220@personal.example.com"
PAYPAL_PASSWORD = "testpass123"

LOG_FILES = {
    "pay_test": Path("/home/jared/projects/AI-CIV/aether/logs/purebrain_pay_test.jsonl"),
    "web_conversations": Path("/home/jared/projects/AI-CIV/aether/logs/purebrain_web_conversations.jsonl"),
    "payments": Path("/home/jared/projects/AI-CIV/aether/logs/purebrain_payments.jsonl"),
}

MONITORED_ENDPOINTS = [
    "api.purebrain.ai/api/intake/seed",
    "api.purebrain.ai/api/log-conversation",
    "api.purebrain.ai/api/log-pay-test",
    "api.purebrain.ai/api/verify-payment",
    "api.purebrain.ai/api/birth",
    "purebrain.ai/wp-json/purebrain",
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
console_logs = []
log_baselines = {}
counter = [0]


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(msg, cat="INFO"):
    entry = f"[{ts()}] [{cat}] {msg}"
    timeline.append(entry)
    print(entry, flush=True)


def record_baselines():
    for key, path in LOG_FILES.items():
        try:
            log_baselines[key] = sum(1 for _ in open(path))
        except Exception:
            log_baselines[key] = 0
    log(f"Baselines: {log_baselines}", "BASELINE")


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


async def ss(page, label):
    counter[0] += 1
    fname = f"{counter[0]:03d}-{label}.png"
    fpath = SCREENSHOT_DIR / fname
    try:
        await page.screenshot(path=str(fpath), timeout=18000, full_page=False)
        screenshots_taken.append(str(fpath))
        log(f"SS: {fname}", "SS")
        return str(fpath)
    except Exception as e:
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
            log(f"SS skipped [{label}]: {str(e)[:60]}", "WARN")
            return None


def attach_monitors(page, label="main"):
    async def on_resp(resp):
        url = resp.url
        for ep in MONITORED_ENDPOINTS:
            if ep in url:
                try:
                    body = (await resp.body()).decode("utf-8", errors="replace")[:500]
                except Exception:
                    body = "(unreadable)"
                entry = {"page": label, "ts": ts(), "method": resp.request.method,
                         "status": resp.status, "url": url, "body": body}
                network_calls.append(entry)
                if "seed" in url or "intake" in url:
                    seed_fires.append(entry)
                    log(f"SEED FIRE {resp.status}: {url}", "SEED")
                    log(f"  Body: {body[:200]}", "SEED")
                elif "birth" in url:
                    birth_calls.append(entry)
                    log(f"BIRTH {resp.status}: {url} -> {body[:100]}", "BIRTH")
                elif "verify-payment" in url:
                    verify_calls.append(entry)
                    log(f"VERIFY {resp.status}: {body[:150]}", "VERIFY")
                elif "log-pay-test" in url:
                    logpay_calls.append(entry)
                    log(f"LOG-PAY {resp.status}: {body[:120]}", "NET")
                elif "log-conversation" in url:
                    logconv_calls.append(entry)
                    log(f"LOG-CONV {resp.status}: {body[:80]}", "NET")
                else:
                    log(f"API {resp.status} {url[:80]}", "NET")

    async def on_con(msg):
        txt = msg.text
        if any(x in txt for x in [
            "seed", "Seed", "SEED", "birth", "Birth", "payment", "Payment",
            "fireSeed", "fire_seed", "oauth", "error", "Error", "ERROR",
            "PB-FIX", "intake", "verify", "portal", "log-pay", "ChatboxV",
            "awakening", "PB ", "handlePayment", "Stage", "stage",
            "conversation_complete", "post-payment", "ptc", "PTC",
        ]):
            log(f"CON[{label}][{msg.type}]: {txt[:200]}", "CON")
            console_logs.append({"page": label, "type": msg.type, "text": txt, "ts": ts()})

    page.on("response", on_resp)
    page.on("console", on_con)


async def wait_ptc_input_active(page, timeout=60):
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
    log(f"Timeout waiting for PTC input row ({timeout}s)", "WARN")
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
                return msgs[msgs.length-1].textContent.trim().substring(0,120);
            })()""") or ""
            log(f"AI response #{n}: {last[:100]}", "AI")
            return n
        await asyncio.sleep(0.5)
    log(f"Timeout for AI response (had {current_count})", "WARN")
    return current_count


async def ptc_send(page, text):
    ta = await page.query_selector("#ptc-input")
    if not ta:
        ta = await page.query_selector("textarea.ptc-input")
    if not ta:
        log(f"No textarea found for: {text[:40]}", "ERROR")
        return False
    try:
        await ta.click(timeout=5000)
        await asyncio.sleep(0.3)
        await ta.fill("")
        await asyncio.sleep(0.2)
        await ta.type(text, delay=30)
        await asyncio.sleep(0.5)
        send = await page.query_selector("#ptc-send-btn")
        if not send:
            send = await page.query_selector(".ptc-send-btn")
        if send and await send.is_visible():
            await send.click()
            log(f"Sent via #ptc-send-btn: {text[:50]}", "ACTION")
            return True
        await ta.press("Enter")
        log(f"Sent via Enter: {text[:50]}", "ACTION")
        return True
    except Exception as e:
        log(f"ptc_send error: {str(e)[:100]}", "ERROR")
        return False


async def attempt_paypal_login(paypal_page):
    """Attempt PayPal sandbox login with new credentials."""
    try:
        await paypal_page.wait_for_load_state("domcontentloaded", timeout=25000)
    except Exception:
        pass
    await asyncio.sleep(4)

    url = paypal_page.url
    log(f"PayPal popup URL: {url[:80]}", "INFO")
    await ss(paypal_page, "paypal-01-initial")

    page_text = await paypal_page.evaluate(
        "(function(){ return document.body ? document.body.innerText.substring(0,300) : ''; })()"
    )
    log(f"PayPal page text: {page_text[:150]}", "INFO")

    # Enter email
    e_inp = await paypal_page.query_selector(
        "#email, input[name='email'], input[type='email'], #login_email"
    )
    if e_inp:
        await e_inp.fill(PAYPAL_EMAIL)
        await asyncio.sleep(0.5)
        # Click Next button
        for ns in ["#btnNext", "button#btnNext", "button[type='submit']", ".button.actionContinue"]:
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
        log("No PayPal email field found", "WARN")
        await ss(paypal_page, "paypal-xx-no-email-field")
        return False

    # Enter password
    p_inp = await paypal_page.query_selector(
        "#password, input[name='password'], input[type='password'], #login_password"
    )
    if p_inp:
        await p_inp.fill(PAYPAL_PASSWORD)
        await asyncio.sleep(0.5)
        for ls in ["#btnLogin", "#signIn", "button#signIn", ".button.actionContinue"]:
            lb = await paypal_page.query_selector(ls)
            if lb:
                await lb.click()
                log(f"Login clicked: {ls}", "ACTION")
                break
        else:
            await p_inp.press("Enter")
        await asyncio.sleep(10)
        await ss(paypal_page, "paypal-03-password-submitted")

        url_after = paypal_page.url
        page_text = await paypal_page.evaluate(
            "(function(){ return document.body ? document.body.innerText.substring(0,300) : ''; })()"
        )
        log(f"After login URL: {url_after[:80]}", "INFO")
        log(f"After login text: {page_text[:150]}", "INFO")

        if "signin" in url_after.lower() and any(x in page_text.lower() for x in ["didn't match", "try again", "incorrect"]):
            log("PayPal login FAILED - credentials wrong", "WARN")
            try:
                await paypal_page.close()
            except Exception:
                pass
            return False

        if "hermes" in url_after or "checkout" in url_after or "approve" in url_after:
            log("PayPal login SUCCESS", "SUCCESS")
            # Try to confirm payment
            confirm = await paypal_page.evaluate("""(function(){
                var btns = Array.from(document.querySelectorAll('button, input[type=submit]'));
                var keywords = ['pay now', 'agree', 'approve', 'confirm', 'continue'];
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
            return True

        log(f"PayPal login result unknown. URL: {url_after[:60]}", "WARN")
        try:
            await paypal_page.close()
        except Exception:
            pass
        return False
    else:
        log("No PayPal password field", "WARN")
        try:
            await paypal_page.close()
        except Exception:
            pass
        return False


async def run():
    log("=== Seed Logging Verification Test - 2026-03-03 ===", "START")
    log(f"URL: {PAGE_URL}", "INFO")
    log(f"PayPal buyer: {PAYPAL_EMAIL}", "INFO")
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

        # =========================================================
        # PHASE 1: Load page + password
        # =========================================================
        log("=== PHASE 1: Load + Password ===", "PHASE")
        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(4)

        pw_inp = await page.query_selector("input[type='password']")
        if pw_inp:
            log("Password gate found", "ACTION")
            await pw_inp.fill(PAGE_PASSWORD)
            sub = await page.query_selector("input[type='submit']")
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            await asyncio.sleep(12)

            title = await page.evaluate("(function(){ return document.title; })()")
            log(f"Title after password: {title}", "INFO")
            if "verify" in title.lower() or "human" in title.lower():
                log("WAF CAPTCHA DETECTED - ABORTING", "ERROR")
                await ss(page, "waf-abort")
                await browser.close()
                return None, {}, {}
        else:
            log("No password gate found (already authenticated or bypass)", "INFO")

        await ss(page, "p01-after-password")

        # =========================================================
        # PHASE 2: Begin Awakening + Bypass Code
        # =========================================================
        log("=== PHASE 2: Begin Awakening + Bypass ===", "PHASE")

        begin = await page.evaluate("""(function(){
            var btn = document.querySelector('.chat-initial__btn');
            if (btn) { btn.click(); return 'clicked'; }
            return 'not-found';
        })()""")
        log(f"Begin Awakening: {begin}", "ACTION")
        await asyncio.sleep(7)
        await ss(page, "p02-after-begin")

        # Enter bypass code
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

        bypass_state = await page.evaluate("""(function(){
            return {
                hasProCta: !!document.getElementById('proCta'),
                openPayPalModal: typeof window.openPayPalModal,
                hasPricing: !!document.querySelector('.pricing-section'),
                hasBypassBtn: !!document.getElementById('pb-sandbox-bypass-btn'),
            };
        })()""")
        log(f"After bypass: {json.dumps(bypass_state)}", "INFO")

        # =========================================================
        # PHASE 3: Open PayPal Modal (Awakened tier = $149)
        # =========================================================
        log("=== PHASE 3: Open PayPal Modal ===", "PHASE")

        # Click proCta (Awakened tier)
        modal_open = await page.evaluate("""(function(){
            // Try proCta first
            var el = document.getElementById('proCta');
            if (el) { el.click(); return 'proCta-clicked'; }
            // Try direct function call
            if (typeof window.openPayPalModal === 'function') {
                window.openPayPalModal('Awakened');
                return 'openPayPalModal-called';
            }
            return 'not-found';
        })()""")
        log(f"Modal open: {modal_open}", "ACTION")
        await asyncio.sleep(6)
        await ss(page, "p04-modal-opened")

        modal_state = await page.evaluate("""(function(){
            var overlay = document.getElementById('pb-paypal-overlay');
            if (!overlay) return {found: false};
            return {
                found: true,
                active: overlay.classList.contains('pb-active'),
                tier: (document.getElementById('pb-paypal-tier-name') || {textContent:''}).textContent.trim(),
                price: (document.getElementById('pb-paypal-price-line') || {textContent:''}).textContent.trim().substring(0,30),
                hasBypassBtn: !!document.getElementById('pb-sandbox-bypass-btn'),
                sandboxBtnVisible: (function(){
                    var b = document.getElementById('pb-sandbox-bypass-btn');
                    return b ? window.getComputedStyle(b).display !== 'none' : false;
                })(),
                paypalIframes: document.querySelectorAll('iframe[src*=paypal], iframe[name*=paypal], iframe[name*=zoid]').length
            };
        })()""")
        log(f"Modal state: {json.dumps(modal_state)}", "INFO")

        # =========================================================
        # PHASE 3B: Attempt Real PayPal (new creds)
        # =========================================================
        log("=== PHASE 3B: Attempt Real PayPal Login ===", "PHASE")
        paypal_method = "none"
        paypal_login_result = "not_attempted"

        # Look for PayPal frames
        frames = [f for f in page.frames if "paypal" in f.url.lower() and "sandbox" in f.url.lower()]
        log(f"PayPal sandbox frames: {len(frames)}", "INFO")

        popup_received = []
        async def on_new_page(p):
            popup_received.append(p)
        ctx.on("page", on_new_page)

        if frames:
            for pf in frames:
                try:
                    btns = await pf.query_selector_all("button, [role=button]")
                    log(f"Frame {pf.url[:60]}: {len(btns)} buttons", "INFO")
                    if btns:
                        await btns[0].click()
                        log("Clicked PayPal button in iframe", "ACTION")
                        await asyncio.sleep(10)
                        break
                except Exception as e:
                    log(f"Frame click error: {str(e)[:60]}", "WARN")

        ctx.remove_listener("page", on_new_page)

        if popup_received:
            paypal_page = popup_received[0]
            attach_monitors(paypal_page, "paypal")
            log(f"PayPal popup opened: {paypal_page.url[:80]}", "SUCCESS")
            paypal_method = "real_paypal_popup"
            login_ok = await attempt_paypal_login(paypal_page)
            if login_ok:
                log("PayPal login SUCCESS - payment should complete", "SUCCESS")
                paypal_login_result = "login_success"
                await asyncio.sleep(15)
            else:
                log("PayPal login FAILED - falling back to sandbox bypass", "WARN")
                paypal_login_result = "login_failed"
        else:
            log("No PayPal popup opened - going to sandbox bypass", "INFO")
            paypal_method = "sandbox_bypass_direct"

        # =========================================================
        # PHASE 3C: Sandbox Bypass
        # =========================================================
        await asyncio.sleep(3)
        log("=== PHASE 3C: Sandbox Bypass ===", "PHASE")

        modal_still_open = await page.evaluate("""(function(){
            var overlay = document.getElementById('pb-paypal-overlay');
            return overlay ? overlay.classList.contains('pb-active') : false;
        })()""")
        log(f"Modal still open: {modal_still_open}", "INFO")
        await ss(page, "p05-before-sandbox-bypass")

        if modal_still_open:
            bypass_click = await page.evaluate("""(function(){
                var btn = document.getElementById('pb-sandbox-bypass-btn');
                if (btn) {
                    btn.scrollIntoView();
                    btn.click();
                    return 'clicked';
                }
                return 'not-found';
            })()""")
            log(f"Sandbox bypass button: {bypass_click}", "ACTION")

            if bypass_click == "clicked":
                paypal_method = f"sandbox_bypass (after {paypal_method})"
                log("Waiting 20s for payment verification + PTC init...", "INFO")
                await asyncio.sleep(20)
                await ss(page, "p05b-after-sandbox-bypass-click")

                # Check log deltas immediately after bypass
                d_bypass, n_bypass = check_deltas()
                log(f"Log deltas after bypass click: {d_bypass}", "LOG")
                for key, entries in n_bypass.items():
                    for e in entries:
                        log(f"POST-BYPASS-LOG[{key}]: {e[:250]}", "LOG")
            else:
                log("Sandbox bypass button not found!", "WARN")
        else:
            log("Modal closed (payment may have already triggered via real PayPal)", "INFO")

        # =========================================================
        # PHASE 4: Wait for Post-Payment Chatbox
        # =========================================================
        log("=== PHASE 4: Wait for PTC ===", "PHASE")
        await asyncio.sleep(5)
        await ss(page, "p06-post-payment-state")

        ptc_active = await wait_ptc_input_active(page, timeout=60)

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
                hasSendBtn: !!sendBtn,
                msgCount: msgs.length,
                firstMsg: msgs.length > 0 ? msgs[0].textContent.trim().substring(0,100) : '',
            };
        })()""")
        log(f"PTC state: {json.dumps(ptc_state)}", "INFO")
        await ss(page, "p07-ptc-initial-state")

        if not ptc_active:
            log("PTC never activated. Checking payment state...", "WARN")
            pay_state = await page.evaluate("""(function(){
                return {
                    paymentConfirmed: window.paymentConfirmed,
                    paymentTier: window.paymentTier,
                    paymentOrderId: window.paymentOrderId,
                };
            })()""")
            log(f"Payment state: {json.dumps(pay_state)}", "INFO")

        # =========================================================
        # PHASE 5: Q&A Flow
        # =========================================================
        log("=== PHASE 5: Post-Payment Q&A ===", "PHASE")

        ai_count = ptc_state.get("msgCount", 0)
        qa = [
            ("name", "Seed Test User"),
            ("email", "seedtest@purebrain.ai"),
            ("company", "PureBrain Test Corp"),
            ("role", "QA Engineer"),
            ("goal", "Verify seed logging fires correctly"),
        ]

        for label, answer in qa:
            log(f"Sending [{label}]: {answer}", "ACTION")
            ok = await ptc_send(page, answer)
            if ok:
                ai_count = await wait_for_new_ai(page, ai_count, timeout=25)
            else:
                log(f"Send failed for [{label}]", "WARN")
                # Check display state
                row_display = await page.evaluate("""(function(){
                    var r = document.getElementById('ptc-input-row');
                    return r ? window.getComputedStyle(r).display : 'not-found';
                })()""")
                log(f"  ptc-input-row display: {row_display}", "INFO")

            await ss(page, f"p08-qa-{label}")
            await asyncio.sleep(2)

            # Check if BIRTH has fired (which locks input)
            if birth_calls:
                log(f"BIRTH fired! Stopping Q&A at [{label}]", "BIRTH")
                break

        # Check log deltas after Q&A
        d_qa, n_qa = check_deltas()
        log(f"Log deltas after Q&A: {d_qa}", "LOG")
        for key, entries in n_qa.items():
            for e in entries:
                log(f"QA-LOG[{key}]: {e[:300]}", "LOG")

        # =========================================================
        # PHASE 6: Continue flow, wait for celebration/completion
        # =========================================================
        log("=== PHASE 6: Watching for Completion State ===", "PHASE")
        portal_found = False
        portal_info = {}
        celebration_found = False

        for i in range(25):
            # Check for portal button (OAuth state)
            portal = await page.evaluate("""(function(){
                var a = document.querySelector('.ptc-portal-btn');
                if (!a) {
                    var links = document.querySelectorAll('a[href]');
                    for (var l of links) {
                        if (l.href && (l.href.includes('portal') || l.href.includes('app.purebrain'))) {
                            return {found: true, href: l.href.substring(0,100), text: l.textContent.trim().substring(0,50)};
                        }
                    }
                }
                if (a) return {found: true, href: (a.href||'').substring(0,100), text: a.textContent.trim().substring(0,50)};
                return {found: false};
            })()""")
            if portal.get("found"):
                log(f"PORTAL BUTTON FOUND: {portal}", "SUCCESS")
                portal_found = True
                portal_info = portal
                await ss(page, "p09-portal-found")
                break

            # Check for celebration/completion text
            celebration = await page.evaluate("""(function(){
                var body = document.body.innerText.toLowerCase();
                var keywords = ['congratulations', 'welcome to', 'you\'re in', 'awakening complete',
                                'journey begins', 'celebrate', 'activated', 'linked'];
                for (var kw of keywords) {
                    if (body.includes(kw)) return kw;
                }
                return null;
            })()""")
            if celebration:
                log(f"CELEBRATION TEXT FOUND: '{celebration}'", "SUCCESS")
                celebration_found = True
                await ss(page, f"p09-celebration-{celebration.replace(' ','-')}")

            # Check input row
            row_display = await page.evaluate("""(function(){
                var r = document.getElementById('ptc-input-row');
                return r ? window.getComputedStyle(r).display : 'not-found';
            })()""")

            if row_display not in ("none", "not-found"):
                cur = await page.evaluate(
                    "(function(){ return document.querySelectorAll('.ptc-msg--ai').length; })()"
                ) or 0
                ok = await ptc_send(page, "Yes, continue please.")
                if ok:
                    new_c = await wait_for_new_ai(page, cur, timeout=20)
                    if new_c == cur:
                        log(f"[loop {i}] No AI response - stalled", "WARN")
                        if i > 10:
                            log("Stalled too long - stopping loop", "WARN")
                            break
                else:
                    log(f"[loop {i}] Send failed (input blocked by OAuth gate?)", "WARN")
                    await asyncio.sleep(5)
                    continue
            else:
                log(f"[loop {i}] Input not active (display={row_display}) - waiting...", "INFO")

            await ss(page, f"p10-loop-{i:02d}")
            await asyncio.sleep(3)

        # =========================================================
        # PHASE 7: Final State + Log Check
        # =========================================================
        log("=== PHASE 7: Final State + Verification ===", "PHASE")
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
                pageTitle: document.title.substring(0,60),
                pageUrl: window.location.href.substring(0,100),
                windowPaymentConfirmed: window.paymentConfirmed,
                windowPaymentTier: window.paymentTier,
            };
        })()""")
        log(f"FINAL STATE: {json.dumps(final_state, indent=2)}", "SUMMARY")

        final_d, final_n = check_deltas()
        log(f"FINAL log deltas: {final_d}", "LOG")
        for key, entries in final_n.items():
            for e in entries:
                log(f"FINAL-LOG[{key}]: {e[:350]}", "LOG")

        await browser.close()

    _write_report(final_state, final_d, final_n, portal_found, portal_info,
                  celebration_found, paypal_method, paypal_login_result)
    return final_state, final_d, final_n


def _write_report(fs, deltas, new_entries, portal_found, portal_info,
                  celebration_found, paypal_method, paypal_login_result):
    lines = [
        "# E2E Seed Logging Verification Report - 2026-03-03",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"**URL**: {PAGE_URL}",
        f"**PayPal buyer**: `{PAYPAL_EMAIL}`",
        "",
        "---",
        "",
        "## Executive Summary - Seed Logging Verification",
        "",
        "| Check | Result |",
        "|-------|--------|",
        f"| PayPal method used | `{paypal_method}` |",
        f"| PayPal login result | `{paypal_login_result}` |",
        f"| Seed fires (Playwright network) | {len(seed_fires)} |",
        f"| verify-payment calls | {len(verify_calls)} |",
        f"| birth pipeline calls | {len(birth_calls)} |",
        f"| log-pay-test API calls | {len(logpay_calls)} |",
        f"| log-conversation API calls | {len(logconv_calls)} |",
        f"| Portal button found | {'YES' if portal_found else 'NO'} |",
        f"| Celebration/completion text | {'YES' if celebration_found else 'NO'} |",
        f"| PTC messages received | {fs.get('ptcMsgCount', 0)} |",
        f"| Screenshots taken | {len(screenshots_taken)} |",
        "",
        "## Log File Changes (CRITICAL)",
        "",
        "These are the seed files we're verifying:",
        "",
        "| File | Baseline | New Lines | Fired? |",
        "|------|----------|-----------|--------|",
    ]
    for key, delta in deltas.items():
        fired = "YES" if isinstance(delta, int) and delta > 0 else "NO"
        lines.append(f"| {key} | {log_baselines.get(key, 0)} | {delta} | {fired} |")
    lines.append("")

    lines += ["## Seed Fire Analysis", ""]

    # Payment seed (pay_test)
    pt_delta = deltas.get("pay_test", 0)
    pm_delta = deltas.get("payments", 0)
    conv_delta = deltas.get("web_conversations", 0)

    lines.append("### Seed 1: Payment Completion")
    lines.append("")
    if isinstance(pt_delta, int) and pt_delta > 0:
        lines.append(f"**STATUS: FIRED** - {pt_delta} new line(s) in purebrain_pay_test.jsonl")
    else:
        lines.append("**STATUS: NOT FIRED** - No new lines in purebrain_pay_test.jsonl")
    if isinstance(pm_delta, int) and pm_delta > 0:
        lines.append(f"**Payment verification: FIRED** - {pm_delta} new line(s) in purebrain_payments.jsonl")
    lines.append("")

    lines.append("### Seed 2: Post-Payment Chat Completion")
    lines.append("")
    if isinstance(conv_delta, int) and conv_delta > 0:
        lines.append(f"**STATUS: FIRED** - {conv_delta} new line(s) in purebrain_web_conversations.jsonl")
        # Check for conversation_complete specifically
        cv_entries = new_entries.get("web_conversations", [])
        for entry in cv_entries:
            try:
                parsed = json.loads(entry)
                evt = parsed.get("metadata", {}).get("event_type", "")
                if evt == "conversation_complete":
                    lines.append(f"**conversation_complete EVENT CONFIRMED**")
            except Exception:
                pass
    else:
        lines.append("**STATUS: NOT FIRED** - No new lines in purebrain_web_conversations.jsonl")
    lines.append("")

    if new_entries:
        lines += ["## New Log Entries Detail", ""]
        for key, entries in new_entries.items():
            if entries:
                lines.append(f"### {key} ({len(entries)} new entries)")
                lines.append("")
                for e in entries:
                    try:
                        parsed = json.loads(e)
                        lines.append("```json")
                        lines.append(json.dumps(parsed, indent=2)[:1000])
                        lines.append("```")
                    except Exception:
                        lines.append("```")
                        lines.append(e[:500])
                        lines.append("```")
                lines.append("")

    lines += ["## Seed Fires (Playwright Network Monitor)", ""]
    if seed_fires:
        for sf in seed_fires:
            lines += [
                f"### SEED [{sf['ts']}]",
                f"- URL: `{sf['url']}`",
                f"- Status: `{sf['status']}`",
                f"- Body: `{sf['body'][:300]}`",
                "",
            ]
    else:
        lines += [
            "**0 seeds captured via Playwright network monitor.**",
            "",
            "Note: Seeds fire to `https://api.purebrain.ai/api/intake/seed` (Cloudflare tunnel).",
            "Cloudflare proxy absorbs outbound requests - Playwright cannot see tunnel internals.",
            "Verify seeds via Witness server logs directly.",
            "",
        ]

    if verify_calls:
        lines += ["## Verify-Payment Calls", ""]
        for vc in verify_calls:
            lines.append(f"- `{vc['ts']}` {vc['status']}: `{vc['body'][:200]}`")
        lines.append("")

    if birth_calls:
        lines += ["## Birth Pipeline Calls", ""]
        for bc in birth_calls:
            lines.append(f"- `{bc['ts']}` {bc['status']}: `{bc['url'][:80]}`")
            lines.append(f"  Body: `{bc['body'][:200]}`")
        lines.append("")

    if logpay_calls:
        lines += ["## Log-Pay-Test Calls", ""]
        for lc in logpay_calls:
            lines.append(f"- `{lc['ts']}` {lc['status']}: `{lc['body'][:200]}`")
        lines.append("")

    lines += ["## All API Calls", ""]
    for nc in network_calls:
        lines.append(f"- `{nc['ts']}` [{nc['page']}] `{nc['method']} {nc['status']}` `{nc['url'][:80]}`")
        if nc.get("body"):
            lines.append(f"  `{nc['body'][:100]}`")

    lines += ["", "## Console Logs (Relevant)", ""]
    for cl in console_logs:
        lines.append(f"- `{cl['ts']}` [{cl['page']}][{cl['type']}]: {cl['text'][:200]}")

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
    print(f"REPORT WRITTEN: {REPORT_PATH}")
    print(f"PayPal method: {paypal_method}")
    print(f"PayPal login: {paypal_login_result}")
    print(f"Seeds (Playwright): {len(seed_fires)}")
    print(f"Verify calls: {len(verify_calls)}")
    print(f"Birth calls: {len(birth_calls)}")
    print(f"Log-pay-test calls: {len(logpay_calls)}")
    print(f"Log deltas: {deltas}")
    print(f"Portal found: {portal_found}")
    print(f"Celebration: {celebration_found}")
    print(f"PTC messages: {fs.get('ptcMsgCount', 0)}")
    print(f"Screenshots: {len(screenshots_taken)}")


if __name__ == "__main__":
    asyncio.run(run())
