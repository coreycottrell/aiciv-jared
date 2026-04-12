#!/usr/bin/env python3
"""
E2E PayPal Sandbox Real Test v3 - PureBrain Pay-Test-Sandbox-2
Date: 2026-03-02
Target: Full flow with real PayPal sandbox payment + complete post-payment Q&A

Fixes from v2:
- Wrapped all page.evaluate() JS in IIFEs to fix "Illegal return statement"
- Screenshot timeout handling: skip silently on Three.js page
- WAF-safe: use live URL, user agent Chrome 122
- Log file baseline comparison for seed verification

Memory applied:
- JS click for off-viewport elements (proCta)
- dispatchEvent for userInput (bypass code)
- page.type() for post-payment chatbox
- No full_page=True (Three.js causes timeout)
- 10s screenshot timeout
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

# Log files to monitor
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
    "178.156.229.207",
    ":8200",
    ":8099",
    ":8443",
]

timeline = []
network_calls = []
screenshots_taken = []
seed_fires = []
counter = [0]
console_logs = []

# Baseline line counts at test start
log_baselines = {}


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(msg, cat="ACTION"):
    entry = f"[{ts()}] [{cat}] {msg}"
    timeline.append(entry)
    print(entry, flush=True)


async def ss(page, label):
    counter[0] += 1
    n = counter[0]
    fname = f"{n:03d}-{label}.png"
    fpath = SCREENSHOT_DIR / fname
    try:
        await page.screenshot(path=str(fpath), timeout=12000)
        screenshots_taken.append(str(fpath))
        log(f"Screenshot: {fname}", "SS")
        return str(fpath)
    except Exception as e:
        log(f"Screenshot skipped [{label}]: {str(e)[:80]}", "WARN")
        return None


def record_log_baselines():
    for key, path in LOG_FILES.items():
        try:
            log_baselines[key] = sum(1 for _ in open(path))
        except Exception:
            log_baselines[key] = 0
    log(f"Log baselines: {log_baselines}", "INFO")


def check_log_deltas():
    deltas = {}
    new_entries = {}
    for key, path in LOG_FILES.items():
        try:
            lines = open(path).readlines()
            baseline = log_baselines.get(key, 0)
            delta = len(lines) - baseline
            deltas[key] = delta
            if delta > 0:
                new_entries[key] = [l.strip() for l in lines[baseline:]]
        except Exception as e:
            deltas[key] = f"error: {e}"
    return deltas, new_entries


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
                    log(f"SEED FIRE: {resp.status} {url} -> {body_txt[:120]}", "SEED")
                elif "birth" in url:
                    log(f"BIRTH CALL: {resp.status} {url} -> {body_txt[:80]}", "BIRTH")
                else:
                    log(f"API: {resp.status} {url[:80]} | {body_txt[:60]}", "NET")

    async def on_console(msg):
        txt = msg.text
        if any(x in txt for x in [
            "seed", "Seed", "SEED", "birth", "Birth", "payment", "Payment",
            "fireSeed", "oauth", "OAuth", "error", "Error", "PB-FIX",
            "intake", "linking", "awaken", "ChatboxV", "[PB ", "verify",
            "portal", "Portal", "launch", "log-pay", "log-conv"
        ]):
            log(f"CONSOLE[{label}][{msg.type}]: {txt[:150]}", "CON")
            console_logs.append({"page": label, "type": msg.type, "text": txt, "ts": ts()})

    page.on("response", on_response)
    page.on("console", on_console)


async def wait_for_ai_msg(page, current_count, timeout=30):
    sel = ".ptc-msg--ai, .ptc-msg.ptc-msg--ai"
    deadline = time.time() + timeout
    while time.time() < deadline:
        msgs = await page.query_selector_all(sel)
        if len(msgs) > current_count:
            await asyncio.sleep(1.5)
            msgs = await page.query_selector_all(sel)
            texts = []
            for m in msgs:
                t = await m.inner_text()
                texts.append(t.strip()[:80])
            last = texts[-1] if texts else "?"
            log(f"AI response ({len(msgs)} total). Last: {last[:80]}", "AI")
            return len(msgs)
        await asyncio.sleep(0.5)
    log(f"Timeout waiting for AI (had {current_count} msgs)", "WARN")
    return current_count


async def ptc_send(page, text):
    for sel in ["#ptc-input", "textarea.ptc-input", ".ptc-input", "textarea"]:
        el = await page.query_selector(sel)
        if el:
            try:
                visible = await el.is_visible()
                enabled = await el.is_enabled()
                if visible and enabled:
                    await el.click()
                    await asyncio.sleep(0.3)
                    await el.fill("")
                    await asyncio.sleep(0.2)
                    await el.type(text, delay=30)
                    await asyncio.sleep(0.5)

                    # Try submit button
                    for sbtn in ["#ptc-send", ".ptc-send", ".ptc-send-btn", "button[type=submit]"]:
                        sbel = await page.query_selector(sbtn)
                        if sbel:
                            await sbel.click()
                            log(f"PTC sent via {sel} + {sbtn}: {text[:50]}", "ACTION")
                            return True
                    # Fallback: Enter key
                    await el.press("Enter")
                    log(f"PTC sent via {sel} + Enter: {text[:50]}", "ACTION")
                    return True
            except Exception as e:
                log(f"ptc_send error on {sel}: {str(e)[:60]}", "WARN")
    log(f"PTC send FAILED: {text[:50]}", "ERROR")
    return False


async def run():
    log("=== E2E PayPal Real Sandbox Test v3 Starting ===", "START")
    log(f"Target: {PAGE_URL}", "INFO")
    log(f"PayPal Account: {PAYPAL_EMAIL}", "INFO")

    record_log_baselines()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )

        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            ignore_https_errors=True,
        )

        page = await ctx.new_page()
        attach_monitors(page, "main")

        # ==================================================
        # PHASE 1: PAGE ACCESS + PASSWORD
        # ==================================================
        log("=== PHASE 1: Page Access + Password ===", "PHASE")
        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(4)
        await ss(page, "p1a-initial")

        pw_inp = await page.query_selector('input[type="password"]')
        if pw_inp:
            log("Password prompt found - entering", "ACTION")
            await pw_inp.fill(PAGE_PASSWORD)
            sub = await page.query_selector('input[type="submit"]')
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            await asyncio.sleep(12)
            log("Password submitted, page rendering", "ACTION")
        else:
            log("No password prompt", "INFO")

        # Skip screenshot here (Three.js font loading timeout risk)
        # Instead just check DOM
        title = await page.evaluate("(function(){ return document.title; })()")
        log(f"Page title after pw: {title}", "INFO")

        # ==================================================
        # PHASE 2: CHATBOX + BYPASS CODE
        # ==================================================
        log("=== PHASE 2: Chat with AI + Bypass ===", "PHASE")

        await ss(page, "p2a-pre-chat")

        begin_found = await page.evaluate("""
            (function(){
                var btn = document.querySelector('.chat-initial__btn');
                if (btn) { btn.click(); return 'chat-initial__btn clicked'; }
                var btns = document.querySelectorAll('button');
                for (var i=0; i<btns.length; i++) {
                    var b = btns[i];
                    if (b.textContent.includes('Awaken') || b.textContent.includes('PURE BRAIN')) {
                        b.click();
                        return 'awaken-btn: ' + b.textContent.trim().substring(0,30);
                    }
                }
                return 'not-found';
            })()
        """)
        log(f"Begin Awakening click: {begin_found}", "ACTION")
        await asyncio.sleep(6)
        await ss(page, "p2b-after-begin")

        # Send bypass code
        log("Sending bypass code: pb-full-bypass", "ACTION")
        await page.evaluate("""
            (function(){
                var inp = document.getElementById('userInput');
                if (inp) {
                    inp.value = 'pb-full-bypass';
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                }
                var sub = document.getElementById('submitBtn');
                if (sub) sub.click();
            })()
        """)
        await asyncio.sleep(10)
        await ss(page, "p2c-after-bypass")

        # Check post-bypass state
        bypass_state = await page.evaluate("""
            (function(){
                var msgs = document.querySelectorAll('.chat-message, .ai-message, [class*=chat-msg], [class*=ai-msg]');
                var proCta = document.getElementById('proCta');
                var pricingSection = document.querySelector('.pricing-section, #pricing-section, [id*=pricing]');
                return {
                    msgCount: msgs.length,
                    hasProCta: !!proCta,
                    proCtaText: proCta ? proCta.textContent.trim().substring(0,30) : '',
                    hasPricing: !!pricingSection,
                    openPayPalModal: typeof window.openPayPalModal,
                    openPayPalCheckout: typeof window.openPayPalCheckout
                };
            })()
        """)
        log(f"Post-bypass state: {bypass_state}", "INFO")

        # ==================================================
        # PHASE 3: OPEN PAYPAL MODAL - Click "Activate Now"
        # ==================================================
        log("=== PHASE 3: Open PayPal Modal via proCta ===", "PHASE")

        # JS click on proCta (may be off-viewport)
        await page.evaluate("""
            (function(){
                var el = document.getElementById('proCta');
                if (el) el.click();
            })()
        """)
        await asyncio.sleep(5)
        await ss(page, "p3a-after-proCta")

        modal_state = await page.evaluate("""
            (function(){
                var overlay = document.getElementById('pb-paypal-overlay');
                var modal = document.querySelector('.pb-paypal-modal, [id*=paypal-modal], [class*=paypal-modal]');
                var bypassBtn = document.getElementById('pb-sandbox-bypass-btn');
                var iframes = document.querySelectorAll('iframe[src*=paypal]');
                if (overlay) {
                    return {
                        overlayFound: true,
                        overlayActive: overlay.classList.contains('pb-active'),
                        overlayDisplay: window.getComputedStyle(overlay).display,
                        bypassBtn: bypassBtn ? bypassBtn.textContent.trim().substring(0,40) : null,
                        iframeCount: iframes.length,
                        html: overlay.innerHTML.substring(0,300)
                    };
                }
                if (modal) {
                    var btns = modal.querySelectorAll('button');
                    return {
                        overlayFound: false,
                        modalFound: true,
                        display: window.getComputedStyle(modal).display,
                        btns: Array.from(btns).map(function(b){ return b.textContent.trim().substring(0,30); }),
                        html: modal.innerHTML.substring(0,300)
                    };
                }
                return {overlayFound: false, modalFound: false};
            })()
        """)
        log(f"Modal state: {modal_state}", "INFO")

        # ==================================================
        # PHASE 3B: PAYPAL PAYMENT - Real or bypass
        # ==================================================
        log("=== PHASE 3B: PayPal Payment ===", "PHASE")

        paypal_page = None

        # First try to click the "Pay with PayPal" button which opens a popup
        # Listen for popup before clicking
        popup_task = asyncio.ensure_future(ctx.wait_for_event("page", timeout=15000))

        paypal_btn_result = await page.evaluate("""
            (function(){
                var result = {clicked: false, method: '', html: ''};

                // Look in overlay / modal
                var container = document.getElementById('pb-paypal-overlay') ||
                                document.querySelector('.pb-paypal-modal') ||
                                document.querySelector('[id*=paypal-modal]');

                if (container) {
                    // Look for "Pay with PayPal" gold button or any CTA
                    var btns = container.querySelectorAll('button, a, input[type=submit]');
                    for (var i=0; i<btns.length; i++) {
                        var b = btns[i];
                        var txt = (b.textContent || b.value || '').toLowerCase().trim();
                        var id = (b.id || '').toLowerCase();
                        // Skip bypass button for now - try real PayPal
                        if (id === 'pb-sandbox-bypass-btn') continue;
                        if (txt.includes('paypal') || txt.includes('pay') || txt.includes('checkout') ||
                            txt.includes('credit') || txt.includes('debit') || id.includes('paypal')) {
                            b.click();
                            result.clicked = true;
                            result.method = 'modal-paypal-btn';
                            result.html = 'clicked: ' + b.textContent.trim().substring(0,40);
                            return result;
                        }
                    }
                    result.html = 'container found, btns: ' + Array.from(btns).map(function(b){return b.textContent.trim().substring(0,20)+' id='+b.id;}).join(' | ');
                }

                // Try PayPal SDK iframes
                var iframes = document.querySelectorAll('iframe[src*=paypal], iframe[name*=paypal]');
                result.html += ' | iframes: ' + iframes.length;

                // Try form with paypal action
                var forms = document.querySelectorAll('form[action*=paypal]');
                if (forms.length > 0) {
                    forms[0].submit();
                    result.clicked = true;
                    result.method = 'form-submit';
                    result.html = 'form: ' + forms[0].action.substring(0,60);
                    return result;
                }

                return result;
            })()
        """)
        log(f"PayPal real button attempt: {paypal_btn_result}", "ACTION")

        await ss(page, "p3b-after-paypal-btn-attempt")

        # Wait briefly for popup
        try:
            paypal_page = await asyncio.wait_for(asyncio.shield(popup_task), timeout=8)
            log(f"PayPal popup opened! URL: {paypal_page.url}", "SUCCESS")
        except asyncio.TimeoutError:
            popup_task.cancel()
            log("No PayPal popup in 8s", "INFO")
            paypal_page = None

        if paypal_page:
            # ==================================================
            # PHASE 3C: PAYPAL POPUP LOGIN
            # ==================================================
            log("=== PHASE 3C: PayPal Popup Login ===", "PHASE")
            attach_monitors(paypal_page, "paypal")

            try:
                await paypal_page.wait_for_load_state("domcontentloaded", timeout=25000)
            except Exception:
                pass
            await asyncio.sleep(4)

            paypal_url = paypal_page.url
            log(f"PayPal URL: {paypal_url}", "INFO")

            await ss(paypal_page, "p3c-paypal-popup")

            # Enter email
            email_inp = await paypal_page.query_selector(
                "#email, input[name='email'], input[type='email'], #login_email"
            )
            if email_inp:
                log(f"Entering PayPal email: {PAYPAL_EMAIL}", "ACTION")
                await email_inp.fill(PAYPAL_EMAIL)
                await asyncio.sleep(0.5)
                for ns in ["#btnNext", "button#btnNext", "#next", "button[type='submit']"]:
                    nb = await paypal_page.query_selector(ns)
                    if nb:
                        await nb.click()
                        log(f"Next clicked via {ns}", "ACTION")
                        break
                else:
                    await email_inp.press("Enter")
                await asyncio.sleep(5)
            else:
                log("PayPal email input not found", "WARN")

            await ss(paypal_page, "p3d-paypal-after-email")

            # Enter password
            pw_inp2 = await paypal_page.query_selector(
                "#password, input[name='password'], input[type='password'], #login_password"
            )
            if pw_inp2:
                log("Entering PayPal password", "ACTION")
                await pw_inp2.fill(PAYPAL_PASSWORD)
                await asyncio.sleep(0.5)
                for ls in ["#btnLogin", "#signIn", "button#signIn", "button[type='submit']"]:
                    lb = await paypal_page.query_selector(ls)
                    if lb:
                        await lb.click()
                        log(f"Login clicked via {ls}", "ACTION")
                        break
                else:
                    await pw_inp2.press("Enter")
                await asyncio.sleep(10)
            else:
                # Check for combined form
                e_field = await paypal_page.query_selector("input[type='email']")
                p_field = await paypal_page.query_selector("input[type='password']")
                if e_field and p_field:
                    await e_field.fill(PAYPAL_EMAIL)
                    await p_field.fill(PAYPAL_PASSWORD)
                    submit = await paypal_page.query_selector("button[type='submit']")
                    if submit:
                        await submit.click()
                    await asyncio.sleep(10)
                    log("Used combined email+password form", "ACTION")
                else:
                    log("PayPal login form not found", "WARN")

            paypal_url2 = paypal_page.url
            log(f"PayPal URL after login: {paypal_url2}", "INFO")
            await ss(paypal_page, "p3e-paypal-after-login")

            # Confirm / Approve payment
            await asyncio.sleep(5)
            page_text = await paypal_page.evaluate(
                "(function(){ return document.body ? document.body.innerText.substring(0,400) : 'no body'; })()"
            )
            log(f"PayPal page text: {page_text[:200]}", "INFO")

            confirm_result = await paypal_page.evaluate("""
                (function(){
                    var btns = document.querySelectorAll('button, input[type=submit], a[role=button]');
                    for (var i=0; i<btns.length; i++) {
                        var b = btns[i];
                        var txt = ((b.textContent || b.value || b.getAttribute('aria-label')) || '').toLowerCase().trim();
                        if (txt.includes('pay now') || txt.includes('agree') || txt.includes('continue') ||
                            txt.includes('confirm') || txt.includes('pay ') || txt.includes('complete') ||
                            txt.includes('approve')) {
                            var info = txt.substring(0,30);
                            b.click();
                            return 'clicked: ' + info;
                        }
                    }
                    return 'no-confirm-btn-found. Buttons: ' +
                        Array.from(document.querySelectorAll('button')).slice(0,5).map(function(b){
                            return b.textContent.trim().substring(0,20);
                        }).join(', ');
                })()
            """)
            log(f"PayPal confirm: {confirm_result}", "ACTION")
            await asyncio.sleep(10)

            await ss(paypal_page, "p3f-paypal-post-confirm")
            paypal_final_url = paypal_page.url
            log(f"PayPal final URL: {paypal_final_url}", "INFO")

            # Wait for popup to close (indicates redirect back to purebrain)
            await asyncio.sleep(5)

        else:
            # Fallback: use sandbox bypass button
            log("=== PHASE 3C: FALLBACK - Sandbox Bypass Button ===", "PHASE")
            bypass_result = await page.evaluate("""
                (function(){
                    var btn = document.getElementById('pb-sandbox-bypass-btn');
                    if (btn) { btn.click(); return 'sandbox-bypass-clicked'; }
                    return 'no-bypass-btn';
                })()
            """)
            log(f"Sandbox bypass: {bypass_result}", "ACTION")
            await asyncio.sleep(15)
            await ss(page, "p3c-fallback-bypass")

        # ==================================================
        # PHASE 4: POST-PAYMENT STATE
        # ==================================================
        log("=== PHASE 4: Post-Payment Chatbox ===", "PHASE")
        await asyncio.sleep(8)
        await ss(page, "p4a-post-payment")

        # Check log deltas right after payment
        log("Checking log file deltas (post-payment)...", "INFO")
        deltas, new_entries = check_log_deltas()
        log(f"Log deltas: {deltas}", "INFO")
        for key, entries in new_entries.items():
            for entry in entries:
                log(f"NEW LOG [{key}]: {entry[:200]}", "LOG")

        ptc_state = await page.evaluate("""
            (function(){
                var wrapper = document.querySelector('.ptc-wrapper, #pay-test-post-payment, #ptc-wrapper');
                var input = document.querySelector('#ptc-input, textarea.ptc-input, .ptc-input, textarea');
                var msgs = document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai');
                var msgTexts = Array.from(msgs).slice(0,3).map(function(m){ return m.textContent.trim().substring(0,80); });
                return {
                    hasWrapper: !!wrapper,
                    hasInput: !!input,
                    inputVisible: input ? (input.offsetParent !== null) : false,
                    msgCount: msgs.length,
                    msgs: msgTexts
                };
            })()
        """)
        log(f"PTC state: {ptc_state}", "INFO")

        ai_count = ptc_state.get("msgCount", 0)

        # ==================================================
        # PHASE 5: POST-PAYMENT Q&A
        # ==================================================
        log("=== PHASE 5: Post-Payment Q&A ===", "PHASE")

        qa_pairs = [
            ("name", "Hannah Test"),
            ("email", "hannah@test.com"),
            ("company", "Test Corp"),
            ("role", "CTO"),
            ("goal", "Testing the full flow end to end"),
        ]

        for q_label, answer in qa_pairs:
            log(f"Sending [{q_label}]: {answer}", "ACTION")
            ok = await ptc_send(page, answer)
            if ok:
                ai_count = await wait_for_ai_msg(page, ai_count, timeout=25)
            else:
                log(f"Could not send [{q_label}] - chatbox may not be ready", "WARN")
            await ss(page, f"p5-qa-{q_label}")
            await asyncio.sleep(2)

        # Check log deltas after Q&A
        log("Checking log file deltas (post-QA)...", "INFO")
        deltas2, new_entries2 = check_log_deltas()
        log(f"Log deltas post-QA: {deltas2}", "INFO")
        for key, entries in new_entries2.items():
            for entry in entries:
                log(f"NEW LOG [{key}]: {entry[:200]}", "LOG")

        # ==================================================
        # PHASE 6: CONTINUE TO PORTAL BUTTON
        # ==================================================
        log("=== PHASE 6: Continue to Portal Button ===", "PHASE")
        await asyncio.sleep(5)

        # Keep going until portal appears or no more input
        for i in range(15):
            inp_state = await page.evaluate("""
                (function(){
                    var el = document.querySelector('#ptc-input, textarea.ptc-input, .ptc-input, textarea');
                    if (!el) return {found: false};
                    return {
                        found: true,
                        visible: el.offsetParent !== null,
                        disabled: el.disabled,
                        placeholder: el.getAttribute('placeholder') || '',
                    };
                })()
            """)

            if not inp_state.get("found") or inp_state.get("disabled") or not inp_state.get("visible"):
                log(f"[loop {i}] No active input - checking for portal button", "INFO")

                # Check for portal button anyway
                portal = await page.evaluate("""
                    (function(){
                        var a = document.querySelector('a[href*=portal], a[href*=purebrain.ai/app], a[href*=app.purebrain]');
                        var b = document.querySelector('button.ptc-launch-btn, .ptc-portal-btn, [class*=portal-btn], [class*=launch-btn]');
                        if (a) return {found: true, type: 'link', href: a.href.substring(0,80), text: a.textContent.trim().substring(0,40)};
                        if (b) return {found: true, type: 'button', text: b.textContent.trim().substring(0,40)};
                        return {found: false};
                    })()
                """)
                if portal.get("found"):
                    log(f"PORTAL BUTTON FOUND: {portal}", "SUCCESS")
                    await ss(page, "p6-portal-found")
                break

            current_count = await page.evaluate(
                "(function(){ return document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai').length; })()"
            ) or 0

            log(f"[loop {i}] Active input (placeholder: {inp_state.get('placeholder','')[:30]}) - continuing", "ACTION")
            ok = await ptc_send(page, "Yes, let's continue.")
            if ok:
                new_count = await wait_for_ai_msg(page, current_count, timeout=20)
                if new_count == current_count:
                    log(f"[loop {i}] No new AI response - stalled", "WARN")
                    break
            else:
                break

            await ss(page, f"p6-loop-{i:02d}")
            await asyncio.sleep(2)

            # Check for portal button
            portal = await page.evaluate("""
                (function(){
                    var a = document.querySelector('a[href*=portal], a[href*=purebrain.ai/app], a[href*=app.purebrain]');
                    var b = document.querySelector('button.ptc-launch-btn, .ptc-portal-btn, [class*=portal-btn], [class*=launch-btn]');
                    if (a) return {found: true, type: 'link', href: a.href.substring(0,80), text: a.textContent.trim().substring(0,40)};
                    if (b) return {found: true, type: 'button', text: b.textContent.trim().substring(0,40)};
                    return {found: false};
                })()
            """)
            if portal.get("found"):
                log(f"PORTAL BUTTON FOUND: {portal}", "SUCCESS")
                await ss(page, "p6-portal-found")
                break

        # ==================================================
        # PHASE 7: FINAL STATE
        # ==================================================
        log("=== PHASE 7: Final State ===", "PHASE")
        await asyncio.sleep(5)
        await ss(page, "p7-final")

        final_state = await page.evaluate("""
            (function(){
                var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai'));
                var portal = document.querySelector('a[href*=portal], a[href*=app.purebrain], .ptc-portal-btn, [class*=portal-btn]');
                var preMsgs = Array.from(document.querySelectorAll('.chat-message, .ai-message'));
                return {
                    ptcMsgCount: msgs.length,
                    ptcMsgs: msgs.map(function(m){ return m.textContent.trim().substring(0,100); }),
                    portalFound: !!portal,
                    portalInfo: portal ? {href: portal.href || '', text: portal.textContent.trim().substring(0,40)} : null,
                    preChatMsgCount: preMsgs.length,
                    pageTitle: document.title.substring(0,50)
                };
            })()
        """)
        log(f"FINAL STATE: {json.dumps(final_state, indent=2)}", "SUMMARY")

        # Final log delta check
        final_deltas, final_new_entries = check_log_deltas()
        log(f"FINAL log deltas: {final_deltas}", "INFO")
        for key, entries in final_new_entries.items():
            for entry in entries:
                log(f"FINAL LOG [{key}]: {entry[:200]}", "LOG")

        await browser.close()

    # ==================================================
    # REPORT
    # ==================================================
    log("=== Generating Report ===", "END")
    _write_report(final_state, final_deltas, final_new_entries)


def _write_report(final_state, final_deltas, final_new_entries):
    lines = [
        "# E2E PayPal Real Sandbox Test v3 - Report",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"**URL**: {PAGE_URL}",
        f"**PayPal Buyer**: {PAYPAL_EMAIL}",
        "",
        "---",
        "",
        "## Summary",
        f"- Screenshots taken: {len(screenshots_taken)}",
        f"- Network API calls captured: {len(network_calls)}",
        f"- Seed fires captured (Playwright): {len(seed_fires)}",
        f"- Console logs captured: {len(console_logs)}",
        "",
        "## Log File Deltas (New Entries Since Test Start)",
        "",
    ]

    lines.append(f"| Log File | Baseline | New Entries |")
    lines.append(f"|----------|----------|-------------|")
    for key, delta in final_deltas.items():
        lines.append(f"| {key} | {log_baselines.get(key, 0)} | {delta} |")
    lines.append("")

    if final_new_entries:
        lines.append("### New Log Entries")
        lines.append("")
        for key, entries in final_new_entries.items():
            lines.append(f"**{key}** ({len(entries)} new):")
            for entry in entries:
                try:
                    parsed = json.loads(entry)
                    lines.append(f"```json")
                    lines.append(json.dumps(parsed, indent=2))
                    lines.append(f"```")
                except Exception:
                    lines.append(f"```")
                    lines.append(entry[:500])
                    lines.append(f"```")
            lines.append("")

    lines += [
        "## Seed Fires (Playwright Network Monitor)",
        "",
    ]
    if seed_fires:
        for sf in seed_fires:
            lines.append(f"### SEED [{sf['ts']}]")
            lines.append(f"- Method: `{sf['method']}` Status: `{sf['status']}`")
            lines.append(f"- URL: `{sf['url']}`")
            lines.append(f"- Response: `{sf['body'][:300]}`")
            lines.append("")
    else:
        lines.append("**0 seeds captured via Playwright network monitor.**")
        lines.append("")
        lines.append("> Note: Seeds firing to api.purebrain.ai (Cloudflare tunnel) may not be interceptable")
        lines.append("> in headless Playwright. Check Witness server logs (104.248.239.98) for inbound requests.")
        lines.append("")

    lines += [
        "## All API Network Calls",
        "",
    ]
    for nc in network_calls:
        lines.append(f"- `{nc['ts']}` [{nc['page']}] `{nc['method']} {nc['status']}` `{nc['url'][:80]}`")
        lines.append(f"  `{nc['body'][:120]}`")

    lines += [
        "",
        "## Console Logs (Filtered)",
        "",
    ]
    for cl in console_logs:
        lines.append(f"- `{cl['ts']}` [{cl['page']}][{cl['type']}]: {cl['text'][:150]}")

    lines += [
        "",
        "## Final Page State",
        "",
        "```json",
        json.dumps(final_state, indent=2),
        "```",
        "",
        "## Screenshots",
        "",
    ]
    for s in screenshots_taken:
        fname = Path(s).name
        lines.append(f"- `{fname}`")

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
    print(f"Seed fires (Playwright): {len(seed_fires)}")
    print(f"Network calls: {len(network_calls)}")
    print(f"Log deltas: {final_deltas}")


if __name__ == "__main__":
    asyncio.run(run())
