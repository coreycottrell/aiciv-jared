#!/usr/bin/env python3
"""
E2E PayPal Sandbox Real Test v5 - FINAL
Date: 2026-03-02

Verified selectors from source code inspection:
- Textarea: #ptc-input (class: ptc-input)
- Send btn: #ptc-send-btn (class: ptc-send-btn)
- Portal: .ptc-portal-btn (an <a> tag)
- AI messages: .ptc-msg--ai
- Input row: #ptc-input-row (hidden until needed)
- PTC wrapper: .ptc-wrapper

PayPal SDK renders inside iframes (zoid-paypal-buttons).
Fallback: sandbox bypass button (#pb-sandbox-bypass-btn).

Screenshots: uses CDP fallback if regular screenshot times out.
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
]

timeline = []
network_calls = []
screenshots_taken = []
seed_fires = []
birth_calls = []
verify_calls = []
logpay_calls = []
counter = [0]
console_logs = []
log_baselines = {}
paypal_method = "none"
paypal_popup_url = ""


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
    # Method 1: standard screenshot
    try:
        await page.screenshot(path=str(fpath), timeout=18000, full_page=False)
        screenshots_taken.append(str(fpath))
        log(f"SS: {fname}", "SS")
        return str(fpath)
    except Exception as e1:
        # Method 2: CDP
        try:
            import base64
            cdp = await page.context.new_cdp_session(page)
            result = await cdp.send("Page.captureScreenshot", {"format": "png"})
            fpath.write_bytes(base64.b64decode(result["data"]))
            screenshots_taken.append(str(fpath))
            log(f"SS (CDP): {fname}", "SS")
            await cdp.detach()
            return str(fpath)
        except Exception as e2:
            log(f"SS skipped [{label}]: {str(e1)[:50]}", "WARN")
            return None


def record_baselines():
    for key, path in LOG_FILES.items():
        try:
            log_baselines[key] = sum(1 for _ in open(path))
        except Exception:
            log_baselines[key] = 0
    log(f"Log baselines: {log_baselines}", "INFO")


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
        except Exception as e:
            deltas[key] = f"error"
    return deltas, new_entries


def attach_monitors(page, label="main"):
    async def on_resp(resp):
        url = resp.url
        for ep in MONITORED_ENDPOINTS:
            if ep in url:
                try:
                    body = (await resp.body()).decode("utf-8", errors="replace")[:300]
                except Exception:
                    body = "(unreadable)"
                entry = {"page": label, "ts": ts(), "method": resp.request.method,
                         "status": resp.status, "url": url, "body": body}
                network_calls.append(entry)
                if "seed" in url or "intake" in url:
                    seed_fires.append(entry)
                    log(f"SEED FIRE {resp.status}: {url} -> {body[:100]}", "SEED")
                elif "birth" in url:
                    birth_calls.append(entry)
                    log(f"BIRTH {resp.status}: {url} -> {body[:80]}", "BIRTH")
                elif "verify-payment" in url:
                    verify_calls.append(entry)
                    log(f"VERIFY {resp.status}: {url} -> {body[:100]}", "NET")
                elif "log-pay-test" in url:
                    logpay_calls.append(entry)
                    log(f"LOG-PAY {resp.status}: {url} -> {body[:100]}", "NET")
                else:
                    log(f"API {resp.status}: {url[:70]} -> {body[:60]}", "NET")

    async def on_con(msg):
        txt = msg.text
        if any(x in txt for x in ["seed", "Seed", "SEED", "birth", "Birth", "payment",
                                   "fireSeed", "oauth", "error", "Error", "PB-FIX",
                                   "intake", "verify", "portal", "log-pay", "ChatboxV",
                                   "awakening", "Awakening", "Payment"]):
            log(f"CON[{label}][{msg.type}]: {txt[:150]}", "CON")
            console_logs.append({"page": label, "type": msg.type, "text": txt, "ts": ts()})

    page.on("response", on_resp)
    page.on("console", on_con)


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
            log(f"AI response #{n}: {last}", "AI")
            return n
        await asyncio.sleep(0.5)
    log(f"Timeout waiting for AI (had {current_count})", "WARN")
    return current_count


async def ptc_send(page, text):
    """Send text in the post-payment chatbox."""
    # Try with known selectors first, then generic textarea
    selectors = ["#ptc-input", "textarea.ptc-input", "textarea"]
    send_selectors = ["#ptc-send-btn", ".ptc-send-btn", "button[type=submit]"]

    for sel in selectors:
        el = await page.query_selector(sel)
        if el:
            try:
                is_vis = await el.is_visible()
                is_en = await el.is_enabled()
                if not is_vis:
                    # Try to make visible by showing input row
                    await page.evaluate("""(function(){
                        var row = document.getElementById('ptc-input-row');
                        if (row) row.style.display = 'flex';
                    })()""")
                    await asyncio.sleep(0.3)
                    is_vis = await el.is_visible()
                if is_vis and is_en:
                    await el.click()
                    await asyncio.sleep(0.3)
                    await el.fill("")
                    await asyncio.sleep(0.2)
                    await el.type(text, delay=25)
                    await asyncio.sleep(0.5)
                    for ss_sel in send_selectors:
                        sbel = await page.query_selector(ss_sel)
                        if sbel and await sbel.is_visible():
                            await sbel.click()
                            log(f"Sent [{sel}+{ss_sel}]: {text[:50]}", "ACTION")
                            return True
                    await el.press("Enter")
                    log(f"Sent [{sel}+Enter]: {text[:50]}", "ACTION")
                    return True
            except Exception as e:
                log(f"ptc_send error on {sel}: {str(e)[:60]}", "WARN")

    log(f"ptc_send FAILED: {text[:50]}", "ERROR")
    return False


async def try_paypal_real(page, ctx):
    """Attempt to click PayPal iframe button and handle popup."""
    global paypal_method, paypal_popup_url

    frames = page.frames
    paypal_frames = [f for f in frames if "paypal" in f.url.lower() and "sandbox" in f.url.lower()]
    log(f"PayPal sandbox frames: {len(paypal_frames)}", "INFO")

    if not paypal_frames:
        log("No PayPal sandbox frames found", "INFO")
        return None

    popup_received = []
    async def on_new_page(p):
        popup_received.append(p)
    ctx.on("page", on_new_page)

    for pf in paypal_frames:
        try:
            btns = await pf.query_selector_all("button, [role=button], .paypal-button")
            log(f"PayPal frame {pf.url[:50]}: {len(btns)} buttons", "INFO")
            if btns:
                await btns[0].click()
                log("Clicked PayPal button in iframe", "ACTION")
                await asyncio.sleep(10)
                break
        except Exception as e:
            log(f"Iframe click error: {str(e)[:60]}", "WARN")

    ctx.remove_listener("page", on_new_page)

    if popup_received:
        paypal_method = "real_paypal_popup"
        paypal_popup_url = popup_received[0].url
        log(f"PayPal popup captured: {paypal_popup_url}", "SUCCESS")
        return popup_received[0]

    log("No PayPal popup from iframe click", "INFO")
    return None


async def do_paypal_login(paypal_page):
    """Log in to PayPal sandbox and approve payment."""
    try:
        await paypal_page.wait_for_load_state("domcontentloaded", timeout=30000)
    except Exception:
        pass
    await asyncio.sleep(4)

    url = paypal_page.url
    log(f"PayPal URL: {url}", "INFO")
    await ss(paypal_page, "paypal-01-initial")

    # Email
    e_inp = await paypal_page.query_selector("#email, input[name='email'], input[type='email'], #login_email")
    if e_inp:
        await e_inp.fill(PAYPAL_EMAIL)
        await asyncio.sleep(0.3)
        for ns in ["#btnNext", "button#btnNext", "button[type='submit']"]:
            nb = await paypal_page.query_selector(ns)
            if nb:
                await nb.click()
                break
        else:
            await e_inp.press("Enter")
        await asyncio.sleep(5)
        await ss(paypal_page, "paypal-02-after-email")
    else:
        log("PayPal email field not found", "WARN")

    # Password
    p_inp = await paypal_page.query_selector("#password, input[name='password'], input[type='password']")
    if p_inp:
        await p_inp.fill(PAYPAL_PASSWORD)
        await asyncio.sleep(0.3)
        for ls in ["#btnLogin", "#signIn", "button#signIn", "button[type='submit']"]:
            lb = await paypal_page.query_selector(ls)
            if lb:
                await lb.click()
                break
        else:
            await p_inp.press("Enter")
        await asyncio.sleep(12)
        await ss(paypal_page, "paypal-03-after-login")
    else:
        # Check combined form
        ef = await paypal_page.query_selector("input[type='email']")
        pf = await paypal_page.query_selector("input[type='password']")
        if ef and pf:
            await ef.fill(PAYPAL_EMAIL)
            await pf.fill(PAYPAL_PASSWORD)
            sub = await paypal_page.query_selector("button[type='submit']")
            if sub:
                await sub.click()
            await asyncio.sleep(12)
        else:
            log("No PayPal login form found", "WARN")

    url2 = paypal_page.url
    log(f"PayPal URL after login: {url2}", "INFO")
    await asyncio.sleep(5)

    page_text = await paypal_page.evaluate(
        "(function(){ return document.body ? document.body.innerText.substring(0, 300) : ''; })()"
    )
    log(f"PayPal page text: {page_text[:150]}", "INFO")

    # Confirm/approve
    confirm = await paypal_page.evaluate("""(function(){
        var btns = Array.from(document.querySelectorAll('button, input[type=submit], a[role=button]'));
        var targets = ['pay now', 'agree', 'continue', 'confirm', 'complete', 'approve'];
        for (var b of btns) {
            var t = (b.textContent || b.value || b.getAttribute('aria-label') || '').toLowerCase().trim();
            for (var tgt of targets) {
                if (t.includes(tgt)) { b.click(); return 'clicked: ' + t.substring(0,40); }
            }
        }
        return 'no-confirm. Visible btns: ' + btns.slice(0,4).map(function(b){
            return (b.textContent||'').trim().substring(0,15);
        }).join(', ');
    })()""")
    log(f"PayPal confirm: {confirm}", "ACTION")
    await asyncio.sleep(10)
    await ss(paypal_page, "paypal-04-confirmed")
    log(f"PayPal final URL: {paypal_page.url}", "INFO")


async def run():
    global paypal_method, paypal_popup_url

    log("=== E2E PayPal Sandbox Test v5 - FINAL RUN ===", "START")
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
                "--disable-renderer-backgrounding",
            ],
        )
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            ignore_https_errors=True,
        )
        page = await ctx.new_page()
        attach_monitors(page, "main")

        # ==============================
        # PHASE 1: Load + Password
        # ==============================
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
            log(f"Page title post-pw: {title}", "INFO")

            # Check for CAPTCHA
            if "verify" in title.lower():
                log("WAF CAPTCHA detected! IP rate-limited. Cannot proceed.", "ERROR")
                await ss(page, "waf-captcha")
                await browser.close()
                return None, {}, {}
        else:
            log("No password gate", "INFO")

        await ss(page, "p01-after-password")

        # ==============================
        # PHASE 2: Begin + Bypass
        # ==============================
        log("--- PHASE 2: Begin Awakening + Bypass ---", "PHASE")

        begin = await page.evaluate("""(function(){
            var btn = document.querySelector('.chat-initial__btn');
            if (btn) { btn.click(); return 'ok'; }
            return 'not-found';
        })()""")
        log(f"Begin click: {begin}", "ACTION")
        await asyncio.sleep(7)
        await ss(page, "p02-after-begin")

        await page.evaluate("""(function(){
            var inp = document.getElementById('userInput');
            if (inp) {
                inp.value = 'pb-full-bypass';
                inp.dispatchEvent(new Event('input', {bubbles: true}));
                inp.dispatchEvent(new Event('change', {bubbles: true}));
            }
            var sub = document.getElementById('submitBtn');
            if (sub) sub.click();
        })()""")
        await asyncio.sleep(10)
        await ss(page, "p03-after-bypass")

        bypass_state = await page.evaluate("""(function(){
            return {
                hasProCta: !!document.getElementById('proCta'),
                proCtaVisible: document.getElementById('proCta') ? (document.getElementById('proCta').offsetParent !== null) : false,
                openPayPalModal: typeof window.openPayPalModal,
                openPayPalCheckout: typeof window.openPayPalCheckout,
                hasPricing: !!document.querySelector('.pricing-section')
            };
        })()""")
        log(f"Bypass state: {bypass_state}", "INFO")

        # ==============================
        # PHASE 3: PayPal Modal
        # ==============================
        log("--- PHASE 3: Open PayPal Modal (proCta) ---", "PHASE")

        await page.evaluate("""(function(){
            var el = document.getElementById('proCta');
            if (el) { el.click(); return; }
            if (typeof window.openPayPalModal === 'function') {
                window.openPayPalModal('Awakened');
            }
        })()""")
        await asyncio.sleep(6)
        await ss(page, "p04-paypal-modal")

        modal_state = await page.evaluate("""(function(){
            var overlay = document.getElementById('pb-paypal-overlay');
            if (!overlay) return {found: false};
            return {
                found: true,
                active: overlay.classList.contains('pb-active'),
                tier: (document.getElementById('pb-paypal-tier-name') || {textContent:''}).textContent.trim(),
                price: (document.getElementById('pb-paypal-price-line') || {textContent:''}).textContent.trim().substring(0,20),
                hasBypassBtn: !!document.getElementById('pb-sandbox-bypass-btn'),
                paypalIframes: document.querySelectorAll('iframe[name*=paypal], iframe[src*=paypal]').length
            };
        })()""")
        log(f"Modal state: {json.dumps(modal_state)}", "INFO")

        # ==============================
        # PHASE 3B: Attempt Real PayPal
        # ==============================
        log("--- PHASE 3B: Attempt Real PayPal via iframe ---", "PHASE")
        paypal_popup = await try_paypal_real(page, ctx)

        if paypal_popup:
            log("--- PHASE 3C: PayPal Login ---", "PHASE")
            attach_monitors(paypal_popup, "paypal")
            await do_paypal_login(paypal_popup)
            await asyncio.sleep(8)
        else:
            log("--- PHASE 3C: FALLBACK - Sandbox Bypass ---", "PHASE")
            paypal_method = "sandbox_bypass"
            bypass_r = await page.evaluate("""(function(){
                var btn = document.getElementById('pb-sandbox-bypass-btn');
                if (btn) { btn.click(); return 'clicked'; }
                return 'not-found';
            })()""")
            log(f"Sandbox bypass: {bypass_r}", "ACTION")
            await asyncio.sleep(15)
            await ss(page, "p05-bypass-clicked")

        # ==============================
        # PHASE 4: Post-Payment State
        # ==============================
        log("--- PHASE 4: Post-Payment State ---", "PHASE")
        await asyncio.sleep(8)
        await ss(page, "p06-post-payment")

        # Immediate log delta check
        d1, n1 = check_deltas()
        log(f"Log deltas (immediate): {d1}", "LOG")
        for key, entries in n1.items():
            for e in entries:
                log(f"NEW-LOG[{key}]: {e[:200]}", "LOG")

        ptc_state = await page.evaluate("""(function(){
            var wrapper = document.querySelector('.ptc-wrapper');
            var inputRow = document.getElementById('ptc-input-row');
            var textarea = document.getElementById('ptc-input');
            var sendBtn = document.getElementById('ptc-send-btn');
            var msgs = document.querySelectorAll('.ptc-msg--ai');
            return {
                hasWrapper: !!wrapper,
                hasInputRow: !!inputRow,
                inputRowDisplay: inputRow ? window.getComputedStyle(inputRow).display : 'N/A',
                hasTextarea: !!textarea,
                hasSendBtn: !!sendBtn,
                msgCount: msgs.length,
                msgs: Array.from(msgs).slice(0,3).map(function(m){ return m.textContent.trim().substring(0,80); })
            };
        })()""")
        log(f"PTC state: {json.dumps(ptc_state)}", "INFO")

        ai_count = ptc_state.get("msgCount", 0)

        # ==============================
        # PHASE 5: Q&A
        # ==============================
        log("--- PHASE 5: Post-Payment Q&A ---", "PHASE")

        qa = [
            ("name", "Hannah Test"),
            ("email", "hannah@test.com"),
            ("company", "Test Corp"),
            ("role", "CTO"),
            ("goal", "Testing the full flow"),
        ]

        for label, answer in qa:
            log(f"Q&A [{label}]: {answer}", "ACTION")
            ok = await ptc_send(page, answer)
            if ok:
                ai_count = await wait_for_new_ai(page, ai_count)
            else:
                log(f"Send failed for [{label}]", "WARN")
            await ss(page, f"p07-qa-{label}")
            await asyncio.sleep(2)

        # Log check after Q&A
        d2, n2 = check_deltas()
        log(f"Log deltas (after Q&A): {d2}", "LOG")
        for key, entries in n2.items():
            old_count = len(n1.get(key, []))
            for e in entries[old_count:]:
                log(f"QA-LOG[{key}]: {e[:200]}", "LOG")

        # ==============================
        # PHASE 6: Continue to Portal
        # ==============================
        log("--- PHASE 6: Continue to Portal ---", "PHASE")
        portal_found = False
        portal_info = {}

        for i in range(20):
            # Check for portal button
            portal = await page.evaluate("""(function(){
                var a = document.querySelector('.ptc-portal-btn');
                if (!a) a = document.querySelector('a[href*="portal"]');
                if (!a) a = document.querySelector('a[href*="app.purebrain"]');
                if (a) return {found: true, href: (a.href||'').substring(0,100), text: a.textContent.trim().substring(0,40)};
                return {found: false};
            })()""")
            if portal.get("found"):
                log(f"PORTAL FOUND: {portal}", "SUCCESS")
                portal_found = True
                portal_info = portal
                await ss(page, "p08-portal-found")
                break

            # Check input row visibility
            inp_info = await page.evaluate("""(function(){
                var row = document.getElementById('ptc-input-row');
                var ta = document.getElementById('ptc-input');
                return {
                    rowFound: !!row,
                    rowDisplay: row ? window.getComputedStyle(row).display : 'none',
                    taFound: !!ta,
                    taVisible: ta ? (ta.offsetParent !== null) : false,
                    taDisabled: ta ? ta.disabled : true
                };
            })()""")

            row_active = (inp_info.get("rowDisplay", "none") != "none"
                          and inp_info.get("taFound")
                          and not inp_info.get("taDisabled"))

            if row_active:
                cur = await page.evaluate(
                    "(function(){ return document.querySelectorAll('.ptc-msg--ai').length; })()"
                ) or 0
                log(f"[loop {i}] Input active - sending continuation", "ACTION")
                ok = await ptc_send(page, "Yes, let's continue.")
                if ok:
                    new_c = await wait_for_new_ai(page, cur)
                    if new_c == cur:
                        log(f"[loop {i}] No AI response - stalled", "WARN")
                else:
                    log(f"[loop {i}] Send failed", "WARN")
                await ss(page, f"p09-loop-{i:02d}")
                await asyncio.sleep(2)
            else:
                log(f"[loop {i}] Input not active (display={inp_info.get('rowDisplay','?')})", "INFO")
                await asyncio.sleep(3)

        # ==============================
        # PHASE 7: Final State
        # ==============================
        log("--- PHASE 7: Final State ---", "PHASE")
        await asyncio.sleep(5)
        await ss(page, "p10-final")

        final_state = await page.evaluate("""(function(){
            var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai'));
            var portal = document.querySelector('.ptc-portal-btn');
            if (!portal) portal = document.querySelector('a[href*="portal"]');
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

    # Write report
    _report(final_state, final_d, final_n, portal_found, portal_info)
    return final_state, final_d, final_n


def _report(fs, deltas, new_entries, portal_found, portal_info):
    lines = [
        "# E2E PayPal Sandbox Test v5 - Final Report",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"**URL**: {PAGE_URL}",
        f"**PayPal sandbox buyer**: `{PAYPAL_EMAIL}`",
        f"**PayPal method used**: `{paypal_method}`",
        f"**PayPal popup URL**: `{paypal_popup_url or 'N/A - used sandbox bypass'}`",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"| Item | Result |",
        f"|------|--------|",
        f"| PayPal payment method | `{paypal_method}` |",
        f"| Seed fires (Playwright network) | {len(seed_fires)} |",
        f"| Birth calls captured | {len(birth_calls)} |",
        f"| Verify-payment calls | {len(verify_calls)} |",
        f"| Log-pay-test calls | {len(logpay_calls)} |",
        f"| Portal button found | {'YES' if portal_found else 'NO'} |",
        f"| Portal URL | `{portal_info.get('href', 'N/A')}` |",
        f"| PTC messages total | {fs.get('ptcMsgCount', 0)} |",
        f"| Screenshots taken | {len(screenshots_taken)} |",
        f"| API calls captured | {len(network_calls)} |",
        "",
        "## Log File Changes",
        "",
        "| File | Baseline | Delta | New Entries |",
        "|------|----------|-------|-------------|",
    ]
    for key, delta in deltas.items():
        lines.append(f"| {key} | {log_baselines.get(key, 0)} | {delta} | {'YES' if delta and delta != 'error' else 'no'} |")
    lines.append("")

    if new_entries:
        lines.append("### New Log Entries Detail")
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
                        lines.append(f"```")
                        lines.append(e[:500])
                        lines.append("```")
                lines.append("")

    lines += ["## Seed Fires", ""]
    if seed_fires:
        for sf in seed_fires:
            lines += [
                f"### SEED [{sf['ts']}]",
                f"- URL: `{sf['url']}`",
                f"- Status: `{sf['status']}`",
                f"- Response: `{sf['body'][:300]}`",
                "",
            ]
    else:
        lines += [
            "**0 seeds captured via Playwright network monitor.**",
            "",
            "Seeds fire to `api.purebrain.ai` (Cloudflare tunnel).",
            "The Cloudflare proxy may absorb these before Playwright sees them.",
            "**Action required**: Check Witness server logs at `104.248.239.98:8200`",
            "for inbound requests during this test window to confirm seeds ARE firing.",
            "",
        ]

    if birth_calls:
        lines += ["## Birth Calls", ""]
        for bc in birth_calls:
            lines += [f"- `{bc['ts']}` {bc['status']}: `{bc['url'][:80]}`", f"  `{bc['body'][:150]}`"]
        lines.append("")

    if verify_calls:
        lines += ["## Verify-Payment Calls", ""]
        for vc in verify_calls:
            lines += [f"- `{vc['ts']}` {vc['status']}: `{vc['body'][:150]}`"]
        lines.append("")

    if logpay_calls:
        lines += ["## Log-Pay-Test Calls", ""]
        for lc in logpay_calls:
            lines += [f"- `{lc['ts']}` {lc['status']}: `{lc['body'][:150]}`"]
        lines.append("")

    lines += ["## All API Calls", ""]
    for nc in network_calls:
        lines.append(f"- `{nc['ts']}` [{nc['page']}] `{nc['method']} {nc['status']}` `{nc['url'][:80]}`")
        lines.append(f"  `{nc['body'][:100]}`")

    lines += ["", "## Console Logs", ""]
    for cl in console_logs:
        lines.append(f"- `{cl['ts']}` [{cl['page']}][{cl['type']}]: {cl['text'][:150]}")

    lines += [
        "", "## PTC Messages", "",
    ]
    for i, msg in enumerate(fs.get("ptcMsgs", [])):
        lines.append(f"{i+1}. {msg}")

    lines += [
        "", "## Screenshots", "",
    ]
    for s in screenshots_taken:
        lines.append(f"- `{Path(s).name}`")

    lines += ["", "## Full Timeline", "", "```"]
    lines.extend(timeline)
    lines.append("```")

    REPORT_PATH.write_text("\n".join(lines))
    print(f"\n{'='*60}")
    print(f"REPORT: {REPORT_PATH}")
    print(f"SCREENSHOTS: {SCREENSHOT_DIR}")
    print(f"PayPal method: {paypal_method}")
    print(f"Seeds (Playwright): {len(seed_fires)}")
    print(f"Birth calls: {len(birth_calls)}")
    print(f"Verify calls: {len(verify_calls)}")
    print(f"Logpay calls: {len(logpay_calls)}")
    print(f"Log deltas: {deltas}")
    print(f"Portal found: {portal_found} -> {portal_info}")
    print(f"PTC messages: {fs.get('ptcMsgCount', 0)}")


if __name__ == "__main__":
    asyncio.run(run())
