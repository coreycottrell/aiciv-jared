#!/usr/bin/env python3
"""
Full E2E PayPal Sandbox Test - PureBrain Pay-Test-Sandbox-2
Date: 2026-03-02
REAL PayPal sandbox payment with actual sandbox credentials.

Memory context applied:
- JS click for off-viewport elements
- dispatchEvent for textarea triggers
- page.type() for chatbox inputs
- No full_page=True (WebGL crash)
- 10s screenshot timeout
- WAF-safe patterns
- Seed fire monitoring
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Page, BrowserContext

# ---- CONFIG ----
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-paypal-real-20260302")
REPORT_PATH = Path("/home/jared/projects/AI-CIV/aether/exports/e2e-paypal-real-report-20260302.md")

PAYPAL_EMAIL = "sb-c89tj49549583@personal.example.com"
PAYPAL_PASSWORD = "Z0+6<dS"

SEED_ENDPOINTS = [
    "api.purebrain.ai/api/intake/seed",
    "api.purebrain.ai/api/log-conversation",
    "api.purebrain.ai/api/log-pay-test",
    "api.purebrain.ai/api/verify-payment",
    "api.purebrain.ai/api/birth/start",
]

# ---- TIMELINE LOG ----
timeline = []
network_calls = []
screenshots_taken = []
seed_fires = []
screenshot_counter = [0]


def log(msg, category="ACTION"):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    entry = f"[{ts}] [{category}] {msg}"
    timeline.append(entry)
    print(entry)


async def screenshot(page, label):
    screenshot_counter[0] += 1
    n = screenshot_counter[0]
    fname = f"{n:03d}-{label}.png"
    fpath = SCREENSHOT_DIR / fname
    try:
        await page.screenshot(path=str(fpath), timeout=10000)
        screenshots_taken.append(str(fpath))
        log(f"Screenshot: {fname}", "SCREENSHOT")
        return str(fpath)
    except Exception as e:
        log(f"Screenshot FAILED {label}: {e}", "ERROR")
        return None


async def wait_for_ai_response(page, existing_count, timeout_s=30):
    """Wait for new AI message to appear in chatbox."""
    start = time.time()
    while time.time() - start < timeout_s:
        msgs = await page.query_selector_all(".ptc-msg--ai, .ptc-msg.ptc-msg--ai")
        if len(msgs) > existing_count:
            # Wait a bit more for full response
            await asyncio.sleep(2)
            msgs = await page.query_selector_all(".ptc-msg--ai, .ptc-msg.ptc-msg--ai")
            texts = []
            for m in msgs:
                t = await m.inner_text()
                texts.append(t.strip()[:80])
            log(f"AI has {len(msgs)} msgs now. Last: {texts[-1] if texts else 'none'}", "AI_RESPONSE")
            return len(msgs)
        await asyncio.sleep(0.5)
    log(f"Timeout waiting for AI response (had {existing_count} msgs)", "WARN")
    return existing_count


async def type_in_chatbox(page, text, textarea_sel="#ptc-input, textarea.ptc-input, .ptc-input"):
    """Type in the post-payment chatbox textarea using page.type() for React compatibility."""
    try:
        el = await page.query_selector(textarea_sel)
        if not el:
            # Try by role
            el = await page.query_selector("textarea")
        if el:
            await el.click()
            await asyncio.sleep(0.3)
            # Use page.fill to clear then type
            await el.fill("")
            await asyncio.sleep(0.2)
            await el.type(text, delay=30)
            await asyncio.sleep(0.3)
            return True
        else:
            log(f"Textarea not found for: {text[:30]}", "ERROR")
            return False
    except Exception as e:
        log(f"Type error: {e}", "ERROR")
        return False


async def submit_chatbox(page):
    """Submit the post-payment chatbox."""
    try:
        # Try send button first
        send_btn = await page.query_selector("#ptc-send, .ptc-send, button.ptc-send-btn, .ptc-send-btn")
        if send_btn:
            await send_btn.click()
            return True
        # Try Enter key on textarea
        el = await page.query_selector("textarea")
        if el:
            await el.press("Enter")
            return True
        return False
    except Exception as e:
        log(f"Submit error: {e}", "ERROR")
        return False


async def get_all_ai_messages(page):
    """Get all AI message texts from post-payment chatbox."""
    msgs = await page.query_selector_all(".ptc-msg--ai, .ptc-msg.ptc-msg--ai")
    texts = []
    for m in msgs:
        t = await m.inner_text()
        texts.append(t.strip())
    return texts


async def run_test():
    log("=== E2E PayPal Sandbox Real Test Starting ===", "START")
    log(f"Target: {PAGE_URL}", "CONFIG")
    log(f"Screenshots: {SCREENSHOT_DIR}", "CONFIG")

    async with async_playwright() as p:
        # Launch headed browser for PayPal popup support
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Network monitoring
        async def handle_request(request):
            url = request.url
            for ep in SEED_ENDPOINTS:
                if ep in url:
                    log(f"SEED REQUEST: {request.method} {url}", "NETWORK")

        async def handle_response(response):
            url = response.url
            for ep in SEED_ENDPOINTS:
                if ep in url:
                    try:
                        body = await response.body()
                        body_str = body.decode("utf-8", errors="replace")[:200]
                    except Exception:
                        body_str = "(could not read)"
                    entry = {
                        "url": url,
                        "method": response.request.method,
                        "status": response.status,
                        "body": body_str,
                        "ts": datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    }
                    network_calls.append(entry)
                    seed_fires.append(entry)
                    log(f"SEED RESPONSE: {response.status} {url} -> {body_str[:80]}", "SEED")

        page = await context.new_page()
        page.on("request", handle_request)
        page.on("response", handle_response)

        # Also monitor ALL network for full picture
        async def handle_all_response(response):
            url = response.url
            if any(x in url for x in ["purebrain.ai/api", "api.purebrain", "verify-payment", "birth", "seed", "intake"]):
                try:
                    body = await response.body()
                    body_str = body.decode("utf-8", errors="replace")[:200]
                except Exception:
                    body_str = "(unreadable)"
                entry = {
                    "url": url,
                    "method": response.request.method,
                    "status": response.status,
                    "body": body_str,
                    "ts": datetime.now().strftime("%H:%M:%S.%f")[:-3]
                }
                if entry not in network_calls:
                    network_calls.append(entry)
                    log(f"API CALL: {response.status} {url[:80]} | {body_str[:60]}", "NETWORK")

        page.on("response", handle_all_response)

        # Console monitoring
        async def handle_console(msg):
            text = msg.text
            if any(x in text for x in ["seed", "Seed", "SEED", "birth", "Birth", "payment", "Payment", "fireSeed", "oauth", "OAuth", "error", "Error", "warn", "PB-FIX", "intake"]):
                log(f"CONSOLE [{msg.type}]: {text[:120]}", "CONSOLE")

        page.on("console", handle_console)

        # ==================
        # PHASE 1: ACCESS PAGE + PASSWORD
        # ==================
        log("--- PHASE 1: Navigating to page ---", "PHASE")
        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        await screenshot(page, "p1a-initial-load")

        # Enter password
        pw_inp = await page.query_selector('input[type="password"]')
        if pw_inp:
            log("Password prompt found, entering password", "ACTION")
            await pw_inp.fill(PAGE_PASSWORD)
            await asyncio.sleep(0.5)
            sub = await page.query_selector('input[type="submit"]')
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            log("Password submitted", "ACTION")
            await asyncio.sleep(10)  # Full page render
        else:
            log("No password prompt - page may already be unlocked", "INFO")

        await screenshot(page, "p1b-after-password")

        # ==================
        # PHASE 2: CLICK BEGIN AWAKENING
        # ==================
        log("--- PHASE 2: Clicking 'Awaken Your PURE BRAIN' ---", "PHASE")

        # Check for .chat-initial__btn (Begin button)
        begin_btn = await page.query_selector(".chat-initial__btn")
        if begin_btn:
            log("Found .chat-initial__btn - clicking via JS", "ACTION")
            await page.evaluate("document.querySelector('.chat-initial__btn').click()")
            await asyncio.sleep(5)
        else:
            log("Begin button not found - checking page state", "WARN")
            # Try text search
            await page.evaluate("""
                var btns = document.querySelectorAll('button');
                for (var b of btns) {
                    if (b.textContent.includes('Awaken') || b.textContent.includes('Begin') || b.textContent.includes('PURE BRAIN')) {
                        b.click();
                        break;
                    }
                }
            """)
            await asyncio.sleep(5)

        await screenshot(page, "p2a-after-begin-click")

        # ==================
        # PHASE 2B: CHAT WITH AI
        # ==================
        log("--- PHASE 2B: AI Chat Conversation ---", "PHASE")

        # Wait for AI first message (awakening)
        await asyncio.sleep(3)

        # Check if we see the chatbox
        chatbox = await page.query_selector("#chatbox, .chatbox, #pb-chat, .pb-chat")
        if chatbox:
            log("Chatbox found", "INFO")
        else:
            log("Standard chatbox selector not found, proceeding anyway", "INFO")

        # Type first user message
        log("Typing: 'Hi! My name is TestUser. I run a marketing agency.'", "ACTION")
        user_inp = await page.query_selector("#userInput, .user-input, input[type='text']")
        if user_inp:
            await user_inp.fill("Hi! My name is TestUser. I run a marketing agency.")
            await asyncio.sleep(0.3)
            sub_btn = await page.query_selector("#submitBtn, button[type='submit']")
            if sub_btn:
                await sub_btn.click()
            else:
                await user_inp.press("Enter")
            log("First message sent", "ACTION")
            await asyncio.sleep(8)
        else:
            log("User input not found - may already be past chatbox or different UI", "WARN")

        await screenshot(page, "p2b-first-message-sent")

        # Second message
        user_inp = await page.query_selector("#userInput, .user-input, input[type='text']")
        if user_inp:
            log("Typing: 'I'd love to call you Nova. Does that feel right?'", "ACTION")
            await user_inp.fill("I'd love to call you Nova. Does that feel right?")
            await asyncio.sleep(0.3)
            sub_btn = await page.query_selector("#submitBtn, button[type='submit']")
            if sub_btn:
                await sub_btn.click()
            else:
                await user_inp.press("Enter")
            await asyncio.sleep(8)

        await screenshot(page, "p2c-second-message-nova")

        # Third message - ask for options
        user_inp = await page.query_selector("#userInput, .user-input, input[type='text']")
        if user_inp:
            log("Typing: 'I'm convinced. I want to get started with Nova. What are my options?'", "ACTION")
            await user_inp.fill("I'm convinced. I want to get started with Nova. What are my options?")
            await asyncio.sleep(0.3)
            sub_btn = await page.query_selector("#submitBtn, button[type='submit']")
            if sub_btn:
                await sub_btn.click()
            else:
                await user_inp.press("Enter")
            await asyncio.sleep(10)

        await screenshot(page, "p2d-pricing-should-appear")

        # Check if pricing appeared or we need bypass
        pricing_visible = await page.query_selector("#pricing, .pricing, #pricingSection, .pricing-section")
        proCta = await page.query_selector("#proCta, .pro-cta")
        if proCta:
            log("Pricing/proCta visible - no bypass needed", "INFO")
        else:
            log("Pricing not visible yet - trying bypass flow", "INFO")

        # ==================
        # PHASE 2C: BYPASS IF NEEDED + REACH PRICING
        # ==================
        log("--- PHASE 2C: Reaching Pricing (Bypass if needed) ---", "PHASE")

        # Check for bypass button
        bypass_input = await page.query_selector("#userInput")
        if bypass_input:
            # Try bypass code
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
            await asyncio.sleep(6)

        await screenshot(page, "p2e-post-bypass-check")

        # Scroll down to find pricing
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
        await screenshot(page, "p2f-scrolled-full")

        # Try clicking proCta to show pricing
        proCta = await page.query_selector("#proCta")
        if proCta:
            log("Clicking proCta via JS", "ACTION")
            await page.evaluate("document.getElementById('proCta').click()")
            await asyncio.sleep(5)
            await screenshot(page, "p2g-after-proCta-click")

        # ==================
        # PHASE 3: PAYPAL PAYMENT
        # ==================
        log("--- PHASE 3: Clicking Awakened tier ($79) ---", "PHASE")

        # Look for the Awakened tier button
        awakened_btn = None

        # Try various selectors
        selectors_to_try = [
            "button[onclick*=\"'Awakened'\"]",
            "button[onclick*='Awakened']",
            ".pricing-card:has-text('Awakened') button",
            "text=Get Awakened",
            "text=Awakened",
        ]

        for sel in selectors_to_try:
            try:
                el = await page.query_selector(sel)
                if el:
                    awakened_btn = el
                    log(f"Found Awakened button via: {sel}", "INFO")
                    break
            except Exception:
                pass

        # JS search fallback
        if not awakened_btn:
            log("Using JS to find Awakened button", "INFO")
            found = await page.evaluate("""
                var btns = document.querySelectorAll('button');
                var found = null;
                for (var b of btns) {
                    var txt = b.textContent;
                    var onclick = b.getAttribute('onclick') || '';
                    if (onclick.includes('Awakened') || txt.includes('Awakened')) {
                        found = {text: txt.trim().substring(0, 50), onclick: onclick.substring(0, 80)};
                        break;
                    }
                }
                return found;
            """)
            log(f"JS button search result: {found}", "INFO")

        await screenshot(page, "p3a-before-paypal-click")

        # Try clicking Awakened button
        clicked = await page.evaluate("""
            var btns = document.querySelectorAll('button');
            var clicked = false;
            for (var b of btns) {
                var onclick = b.getAttribute('onclick') || '';
                var txt = b.textContent || '';
                if (onclick.includes('Awakened') || (txt.includes('Awakened') && txt.includes('79'))) {
                    b.click();
                    clicked = true;
                    break;
                }
            }
            // Also try openPayPalModal directly
            if (!clicked && typeof openPayPalModal !== 'undefined') {
                openPayPalModal('Awakened');
                clicked = true;
            } else if (!clicked && typeof window.openPayPalModal !== 'undefined') {
                window.openPayPalModal('Awakened');
                clicked = true;
            } else if (!clicked && typeof openPayPalCheckout !== 'undefined') {
                openPayPalCheckout('Awakened');
                clicked = true;
            }
            return clicked;
        """)
        log(f"Awakened button click attempt: {clicked}", "ACTION")
        await asyncio.sleep(3)
        await screenshot(page, "p3b-after-awakened-click")

        # Check for PayPal modal
        paypal_modal = await page.query_selector(".paypal-modal, #paypal-modal, [id*='paypal'], [class*='paypal-btn']")
        if paypal_modal:
            log("PayPal modal found", "INFO")
        else:
            log("PayPal modal not visible via selector - checking for popup", "INFO")

        # Look for the PayPal pay button (gold button)
        log("Looking for 'Pay with PayPal' gold button", "ACTION")
        await asyncio.sleep(2)
        await screenshot(page, "p3c-paypal-modal-state")

        # Try to click the PayPal button in modal
        paypal_gold_btn = await page.evaluate("""
            // Check for PayPal SDK buttons
            var btn = document.querySelector('.paypal-button, [data-paypal-button], .paypal-buttons button, iframe[name*=paypal]');
            var clicked = false;

            // Try direct modal button
            var btns = document.querySelectorAll('button');
            for (var b of btns) {
                var txt = b.textContent.toLowerCase();
                if (txt.includes('pay with paypal') || txt.includes('checkout with paypal') || txt.includes('paypal')) {
                    b.click();
                    clicked = true;
                    break;
                }
            }
            return {clicked: clicked, hasiframe: !!document.querySelector('iframe[src*=paypal]')};
        """)
        log(f"PayPal gold button state: {paypal_gold_btn}", "INFO")

        # ==================
        # PHASE 3B: PAYPAL POPUP HANDLING
        # ==================
        log("--- PHASE 3B: PayPal Popup Login ---", "PHASE")
        await asyncio.sleep(3)
        await screenshot(page, "p3d-before-paypal-popup")

        # PayPal typically opens a popup. Watch for new page.
        all_pages = context.pages
        log(f"Open pages/popups before PayPal: {len(all_pages)}", "INFO")

        # Try sandbox bypass button if available (fallback for when PayPal SDK fails)
        sandbox_bypass = await page.query_selector("#pb-sandbox-bypass-btn, [id*=sandbox-bypass]")
        if sandbox_bypass:
            log("Sandbox bypass button found - will use if PayPal popup fails", "INFO")

        # Try clicking through PayPal flow
        # First: Click any visible "Pay with PayPal" button in modal
        paypal_btn_clicked = await page.evaluate("""
            var modal = document.querySelector('.pb-paypal-modal, .paypal-modal, [class*=paypal-modal]');
            if (modal) {
                var btn = modal.querySelector('button');
                if (btn) {
                    btn.click();
                    return 'modal-button-clicked: ' + btn.textContent.trim().substring(0, 30);
                }
            }

            // Check for iframe PayPal button
            var iframes = document.querySelectorAll('iframe');
            for (var iframe of iframes) {
                if (iframe.src && iframe.src.includes('paypal')) {
                    return 'paypal-iframe-found: ' + iframe.src.substring(0, 80);
                }
            }

            return 'no-paypal-elements-visible';
        """)
        log(f"PayPal button state: {paypal_btn_clicked}", "INFO")

        # Wait for popup
        popup_page = None
        try:
            popup_page = await context.wait_for_event("page", timeout=5000)
            log(f"PayPal popup opened: {popup_page.url}", "INFO")
        except Exception:
            log("No popup detected in 5s", "INFO")

        if popup_page:
            log("--- Handling PayPal Popup ---", "PHASE")
            await popup_page.wait_for_load_state("domcontentloaded", timeout=15000)
            await asyncio.sleep(3)

            # Screenshot popup
            try:
                popup_ss = SCREENSHOT_DIR / f"{screenshot_counter[0]+1:03d}-p3e-paypal-popup.png"
                screenshot_counter[0] += 1
                await popup_page.screenshot(path=str(popup_ss), timeout=10000)
                screenshots_taken.append(str(popup_ss))
                log(f"PayPal popup screenshot: {popup_ss.name}", "SCREENSHOT")
            except Exception as e:
                log(f"Popup screenshot failed: {e}", "WARN")

            # Enter PayPal email
            log(f"Entering PayPal email: {PAYPAL_EMAIL}", "ACTION")
            email_inp = await popup_page.query_selector("#email, input[type='email'], input[name='email'], #login_email")
            if email_inp:
                await email_inp.fill(PAYPAL_EMAIL)
                await asyncio.sleep(0.5)
                # Click Next button
                next_btn = await popup_page.query_selector("#btnNext, button[type='submit'], input[type='submit']")
                if next_btn:
                    await next_btn.click()
                    await asyncio.sleep(3)
                else:
                    await email_inp.press("Enter")
                    await asyncio.sleep(3)
                log("PayPal email entered", "ACTION")
            else:
                log("PayPal email input not found", "WARN")

            # Enter PayPal password
            log("Entering PayPal password", "ACTION")
            pw_inp2 = await popup_page.query_selector("#password, input[type='password'], input[name='password'], #login_password")
            if pw_inp2:
                await pw_inp2.fill(PAYPAL_PASSWORD)
                await asyncio.sleep(0.5)
                login_btn = await popup_page.query_selector("#btnLogin, #signIn, button[type='submit'], input[type='submit']")
                if login_btn:
                    await login_btn.click()
                    await asyncio.sleep(5)
                else:
                    await pw_inp2.press("Enter")
                    await asyncio.sleep(5)
                log("PayPal password entered and submitted", "ACTION")
            else:
                log("PayPal password input not found", "WARN")

            # Screenshot after login
            try:
                popup_ss2 = SCREENSHOT_DIR / f"{screenshot_counter[0]+1:03d}-p3f-paypal-after-login.png"
                screenshot_counter[0] += 1
                await popup_page.screenshot(path=str(popup_ss2), timeout=10000)
                screenshots_taken.append(str(popup_ss2))
                log(f"PayPal post-login screenshot: {popup_ss2.name}", "SCREENSHOT")
            except Exception as e:
                log(f"Post-login screenshot failed: {e}", "WARN")

            # Wait for PayPal review page + confirm payment
            await asyncio.sleep(5)
            paypal_url = popup_page.url
            log(f"PayPal popup URL: {paypal_url}", "INFO")

            # Click "Continue" or "Pay Now" or "Agree & Continue"
            confirm_btn = await popup_page.query_selector("#payment-submit-btn, #confirmButtonTop, button#continueButton, [data-testid='continue-button'], input[value*='Pay'], button:has-text('Pay'), button:has-text('Continue'), button:has-text('Agree')")
            if confirm_btn:
                log("Clicking PayPal Confirm/Pay button", "ACTION")
                await confirm_btn.click()
                await asyncio.sleep(8)
            else:
                # Try JS search
                confirm_clicked = await popup_page.evaluate("""
                    var btns = document.querySelectorAll('button, input[type=submit]');
                    for (var b of btns) {
                        var txt = (b.textContent || b.value || '').toLowerCase();
                        if (txt.includes('pay now') || txt.includes('agree') || txt.includes('continue') || txt.includes('confirm')) {
                            b.click();
                            return txt.substring(0, 30);
                        }
                    }
                    return 'no-confirm-button';
                """)
                log(f"PayPal confirm search: {confirm_clicked}", "INFO")
                await asyncio.sleep(8)

            # Final popup screenshot
            try:
                popup_ss3 = SCREENSHOT_DIR / f"{screenshot_counter[0]+1:03d}-p3g-paypal-payment-confirmed.png"
                screenshot_counter[0] += 1
                await popup_page.screenshot(path=str(popup_ss3), timeout=10000)
                screenshots_taken.append(str(popup_ss3))
                log(f"PayPal confirmed screenshot: {popup_ss3.name}", "SCREENSHOT")
            except Exception as e:
                log(f"PayPal confirmed screenshot failed: {e}", "WARN")

        else:
            # No popup - try sandbox bypass
            log("No PayPal popup. Using sandbox bypass button.", "ACTION")
            sandbox_bypass = await page.query_selector("#pb-sandbox-bypass-btn")
            if sandbox_bypass:
                log("Clicking sandbox bypass button", "ACTION")
                await page.evaluate("document.getElementById('pb-sandbox-bypass-btn').click()")
                await asyncio.sleep(15)
                await screenshot(page, "p3e-after-sandbox-bypass")
            else:
                log("Sandbox bypass button also not found", "WARN")

        # ==================
        # PHASE 4: POST-PAYMENT - QUESTIONNAIRE
        # ==================
        log("--- PHASE 4: Post-Payment Questionnaire ---", "PHASE")
        await asyncio.sleep(5)
        await screenshot(page, "p4a-post-payment-state")

        # Check for post-payment chatbox
        ptc_wrapper = await page.query_selector(".ptc-wrapper, #pay-test-post-payment, #ptc-wrapper")
        if ptc_wrapper:
            log("Post-payment chatbox (.ptc-wrapper) found!", "INFO")
        else:
            log("Post-payment chatbox not visible yet", "INFO")

        # Count initial AI messages
        ai_msgs = await get_all_ai_messages(page)
        log(f"Initial AI messages in PTC: {len(ai_msgs)}", "INFO")
        for i, m in enumerate(ai_msgs[:3]):
            log(f"  AI msg[{i}]: {m[:80]}", "AI_RESPONSE")

        ai_count = len(ai_msgs)

        # Answer questionnaire
        log("Waiting for questionnaire prompt...", "INFO")
        await asyncio.sleep(3)

        # Q1: Full Name
        log("Typing name: TestUser Smith", "ACTION")
        ok = await type_in_chatbox(page, "TestUser Smith")
        if ok:
            await submit_chatbox(page)
            ai_count = await wait_for_ai_response(page, ai_count, timeout_s=20)
        await screenshot(page, "p4b-after-name")

        # Q2: Email
        log("Typing email: testuser@purebrain-test.com", "ACTION")
        ok = await type_in_chatbox(page, "testuser@purebrain-test.com")
        if ok:
            await submit_chatbox(page)
            ai_count = await wait_for_ai_response(page, ai_count, timeout_s=20)
        await screenshot(page, "p4c-after-email")

        # Q3: Company
        log("Typing company: TestCorp Marketing", "ACTION")
        ok = await type_in_chatbox(page, "TestCorp Marketing")
        if ok:
            await submit_chatbox(page)
            ai_count = await wait_for_ai_response(page, ai_count, timeout_s=20)
        await screenshot(page, "p4d-after-company")

        # Q4: Role
        log("Typing role: CEO", "ACTION")
        ok = await type_in_chatbox(page, "CEO")
        if ok:
            await submit_chatbox(page)
            ai_count = await wait_for_ai_response(page, ai_count, timeout_s=20)
        await screenshot(page, "p4e-after-role")

        # Q5: Primary Goal
        log("Typing goal: Automate my marketing workflows", "ACTION")
        ok = await type_in_chatbox(page, "Automate my marketing workflows")
        if ok:
            await submit_chatbox(page)
            ai_count = await wait_for_ai_response(page, ai_count, timeout_s=25)
        await screenshot(page, "p4f-after-goal")

        # ==================
        # PHASE 5: BIRTH PIPELINE
        # ==================
        log("--- PHASE 5: Birth Pipeline / OAuth ---", "PHASE")
        await asyncio.sleep(5)
        await screenshot(page, "p5a-birth-pipeline-state")

        # Check for OAuth URL
        oauth_url_text = await page.evaluate("""
            var links = document.querySelectorAll('a[href*=oauth], a[href*=birth], a[href*=google]');
            var found = [];
            for (var l of links) found.push(l.href.substring(0, 100));

            // Also check text content
            var ptcMsgs = document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai');
            for (var m of ptcMsgs) {
                if (m.textContent.includes('oauth') || m.textContent.includes('google') || m.textContent.includes('linking')) {
                    found.push('MSG: ' + m.textContent.substring(0, 100));
                }
            }
            return found;
        """)
        log(f"OAuth/Birth elements: {oauth_url_text}", "INFO")

        # Wait for birth/linking message
        await asyncio.sleep(5)
        ai_msgs_now = await get_all_ai_messages(page)
        log(f"Total AI messages now: {len(ai_msgs_now)}", "INFO")
        for i, m in enumerate(ai_msgs_now):
            log(f"  PTC msg[{i}]: {m[:100]}", "AI_RESPONSE")

        await screenshot(page, "p5b-all-messages-state")

        # ==================
        # PHASE 6: FINAL MESSAGE + SECOND SEED
        # ==================
        log("--- PHASE 6: Navigating to Final Message ---", "PHASE")

        # Keep answering any remaining prompts
        max_exchanges = 10
        for exchange in range(max_exchanges):
            current_count = len(await get_all_ai_messages(page))
            inp = await page.query_selector("#ptc-input, textarea.ptc-input, .ptc-input, textarea")
            if not inp:
                log(f"No input found at exchange {exchange} - flow may be complete", "INFO")
                break

            inp_enabled = await inp.is_enabled()
            inp_visible = await inp.is_visible()
            if not (inp_enabled and inp_visible):
                log(f"Input not active at exchange {exchange}", "INFO")
                break

            placeholder = await inp.get_attribute("placeholder") or ""
            log(f"Exchange {exchange}: Input active (placeholder: {placeholder[:40]})", "INFO")

            # Type a continuation response
            await inp.fill("Yes, let's continue.")
            await asyncio.sleep(0.3)
            await submit_chatbox(page)
            await asyncio.sleep(8)

            new_count = len(await get_all_ai_messages(page))
            if new_count == current_count:
                log(f"No new messages at exchange {exchange} - flow stalled/complete", "INFO")
                break

            await screenshot(page, f"p6-exchange-{exchange:02d}")

        # Final screenshot
        await asyncio.sleep(5)
        await screenshot(page, "p6z-final-state")

        # Check for portal button
        portal_btn = await page.query_selector("a[href*='portal'], a[href*='app.purebrain'], button:has-text('Launch'), button:has-text('Portal')")
        if portal_btn:
            portal_txt = await portal_btn.inner_text()
            portal_href = await portal_btn.get_attribute("href") or ""
            log(f"PORTAL BUTTON FOUND: {portal_txt} -> {portal_href}", "SUCCESS")
        else:
            log("Portal button not found in final state", "INFO")

        # Final AI messages
        final_msgs = await get_all_ai_messages(page)
        log(f"FINAL: {len(final_msgs)} total AI messages in PTC", "SUMMARY")

        await browser.close()

    # ==================
    # GENERATE REPORT
    # ==================
    log("=== Test Complete - Generating Report ===", "END")

    report_lines = [
        "# E2E PayPal Real Test Report",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**URL**: {PAGE_URL}",
        f"**PayPal Account**: {PAYPAL_EMAIL}",
        "",
        "---",
        "",
        "## Network Calls (API Endpoints)",
        "",
    ]

    if network_calls:
        for nc in network_calls:
            report_lines.append(f"- **{nc['ts']}** `{nc['method']} {nc['status']}` {nc['url']}")
            report_lines.append(f"  - Response: `{nc['body'][:100]}`")
    else:
        report_lines.append("- No API calls captured")

    report_lines += [
        "",
        "## Seed Fires",
        "",
    ]

    if seed_fires:
        for sf in seed_fires:
            report_lines.append(f"- **{sf['ts']}** SEED: `{sf['status']}` {sf['url']}")
            report_lines.append(f"  - `{sf['body'][:150]}`")
    else:
        report_lines.append("- No seeds captured via network monitor")

    report_lines += [
        "",
        "## Screenshots Taken",
        "",
    ]
    for ss in screenshots_taken:
        report_lines.append(f"- `{ss}`")

    report_lines += [
        "",
        "## Full Timeline",
        "",
        "```",
    ]
    report_lines.extend(timeline)
    report_lines.append("```")

    REPORT_PATH.write_text("\n".join(report_lines))
    print(f"\nReport saved: {REPORT_PATH}")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print(f"\nSeed fires captured: {len(seed_fires)}")
    print(f"Total network calls: {len(network_calls)}")


if __name__ == "__main__":
    asyncio.run(run_test())
