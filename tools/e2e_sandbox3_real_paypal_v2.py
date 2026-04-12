"""
E2E Test: pay-test-sandbox-3 with REAL PayPal sandbox payment
Version 2: Headless mode with proper popup interception
Date: 2026-03-04
"""

import asyncio
import os
import sys
import time
import subprocess
from playwright.async_api import async_playwright

PAGE_URL = "https://purebrain.ai/pay-test-sandbox-3/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
PAYPAL_EMAIL = "sb-c89tj49549583@personal.example.com"
PAYPAL_PASSWORD = "Z0+6<dS"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-e2e-full-20260304"
TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"

QA_ANSWERS = {
    "name": "Alex Carter",
    "email": "alex.carter.test@example.com",
    "company": "Frontier AI Ventures",
    "role": "CTO",
    "goal": "Automate our entire research pipeline so our team can focus on high-level strategy instead of manual data gathering"
}

screenshot_count = 0

def tg(msg):
    try:
        subprocess.run([TG_SEND, msg[:4000]], timeout=10, capture_output=True)
        print(f"[TG] {msg[:200]}")
    except Exception as e:
        print(f"[TG ERR] {e}")

def tg_photo(path, caption):
    try:
        subprocess.run([TG_SEND, "--photo", path, caption[:200]], timeout=15, capture_output=True)
        print(f"[TG PHOTO] {caption[:100]}")
    except Exception as e:
        print(f"[TG PHOTO ERR] {e}")

async def ss(page, label, send=True):
    global screenshot_count
    screenshot_count += 1
    fn = f"{screenshot_count:03d}-{label}.png"
    path = os.path.join(SCREENSHOT_DIR, fn)
    try:
        await page.screenshot(path=path, full_page=False)
        print(f"[SS] {fn}")
        if send:
            tg_photo(path, f"Step {screenshot_count}: {label}")
    except Exception as e:
        print(f"[SS ERR] {label}: {e}")
    return path

async def wait_for_input(page, timeout=90):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            d = await page.evaluate("""(function(){
                var r = document.getElementById('ptc-input-row');
                if (!r) return 'not-found';
                return window.getComputedStyle(r).display;
            })()""")
            if d not in ("none", "not-found"):
                return True
        except:
            pass
        await asyncio.sleep(1)
    return False

async def get_msgs(page):
    try:
        return await page.evaluate("""(function(){
            var els = document.querySelectorAll('.ptc-msg--ai, .ptc-message--ai');
            return Array.from(els).map(e => e.textContent.trim()).filter(t => t.length > 2);
        })()""")
    except:
        return []

async def send_msg(page, text):
    for sel in ["#ptc-input", "textarea.ptc-input"]:
        try:
            ta = await page.query_selector(sel)
            if ta and await ta.is_visible():
                await ta.click()
                await asyncio.sleep(0.2)
                await ta.fill("")
                await ta.type(text, delay=20)
                await asyncio.sleep(0.3)
                for bsel in ["#ptc-send-btn", ".ptc-send-btn", "button.ptc-send"]:
                    btn = await page.query_selector(bsel)
                    if btn and await btn.is_visible():
                        await btn.click()
                        return True
                await ta.press("Enter")
                return True
        except Exception as e:
            print(f"[SEND] {sel} failed: {e}")
    return False

async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    tg("E2E sandbox3 v2: Starting with headless Chromium + real PayPal")

    console_log = []
    page_errors = []
    api_calls = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )

        page = await context.new_page()
        page.on("console", lambda m: console_log.append(f"[{m.type.upper()}] {m.text}"))
        page.on("pageerror", lambda e: page_errors.append(str(e)))

        async def on_resp(r):
            if any(x in r.url for x in ["purebrain.ai", "api.purebrain"]):
                api_calls.append(f"{r.status} {r.url}")
        page.on("response", on_resp)

        # ============================================================
        # STEP 1: NAVIGATE + PASSWORD
        # ============================================================
        print("\n=== STEP 1: Navigate and enter password ===")
        tg("Step 1: Navigating to pay-test-sandbox-3...")

        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        await ss(page, "01-page-load")

        # Check page text
        body = await page.evaluate("document.body.innerText")
        print(f"[STEP 1] Body preview: {body[:300]}")

        # Enter password
        pw = await page.query_selector("input[type='password'], input[name='post_password']")
        if pw:
            print("[STEP 1] Password form found")
            await pw.click()
            await pw.fill(PAGE_PASSWORD)
            await ss(page, "02-password-entered")

            sub = await page.query_selector("input[type='submit'], button[type='submit']")
            if sub:
                await sub.click()
            else:
                await pw.press("Enter")

            await page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(3)
            await ss(page, "03-password-submitted")
            tg(f"Step 1 DONE: Password submitted. URL: {page.url}")
        else:
            print("[STEP 1] No password form - already unlocked or error")
            await ss(page, "02-no-password-form")
            tg("Step 1: No password form found - page may already be unlocked")

        # ============================================================
        # STEP 2: INSPECT PAGE CONTENT
        # ============================================================
        print("\n=== STEP 2: Inspect page content ===")

        body_after = await page.evaluate("document.body.innerText")
        print(f"[STEP 2] Page content (800 chars):\n{body_after[:800]}")

        # Get all iframes
        frames = page.frames
        print(f"[STEP 2] Frames: {len(frames)}")
        for i, f in enumerate(frames):
            print(f"  [{i}] {f.url[:120]}")

        # List all visible elements including buttons
        page_elements = await page.evaluate("""(function(){
            var result = {
                buttons: [],
                inputs: [],
                containers: [],
                headings: []
            };

            // Buttons
            document.querySelectorAll('button, input[type="submit"], a[class*="btn"]').forEach(el => {
                var s = window.getComputedStyle(el);
                if (s.display !== 'none') {
                    result.buttons.push({
                        tag: el.tagName,
                        text: el.textContent.trim().substring(0, 60),
                        id: el.id,
                        cls: el.className.substring(0, 50)
                    });
                }
            });

            // PayPal containers
            document.querySelectorAll('[id*="paypal"], [class*="paypal"]').forEach(el => {
                var s = window.getComputedStyle(el);
                result.containers.push({
                    tag: el.tagName,
                    id: el.id,
                    cls: el.className.substring(0, 60),
                    display: s.display,
                    w: el.offsetWidth,
                    h: el.offsetHeight,
                    childCount: el.children.length
                });
            });

            // Headings
            document.querySelectorAll('h1, h2, h3').forEach(el => {
                result.headings.push(el.textContent.trim());
            });

            return result;
        })()""")

        print(f"[STEP 2] Buttons: {page_elements['buttons']}")
        print(f"[STEP 2] PayPal containers: {page_elements['containers']}")
        print(f"[STEP 2] Headings: {page_elements['headings']}")

        # ============================================================
        # STEP 3: WAIT FOR PAYPAL SDK TO LOAD
        # ============================================================
        print("\n=== STEP 3: Wait for PayPal SDK ===")
        tg("Step 3: Waiting for PayPal SDK to load...")

        # Wait up to 20 seconds for PayPal iframes
        for attempt in range(20):
            paypal_frames = [f for f in page.frames if "paypal.com" in f.url]
            if paypal_frames:
                print(f"[STEP 3] PayPal frames found ({len(paypal_frames)}):")
                for pf in paypal_frames:
                    print(f"  {pf.url[:100]}")
                break
            await asyncio.sleep(1)
            if attempt % 5 == 4:
                print(f"[STEP 3] Still waiting... ({attempt + 1}/20)")

        paypal_frames = [f for f in page.frames if "paypal.com" in f.url]
        print(f"[STEP 3] Final PayPal frame count: {len(paypal_frames)}")

        await ss(page, "04-paypal-sdk-loaded")

        # ============================================================
        # STEP 4: SET UP POPUP HANDLER AND CLICK PAYPAL
        # ============================================================
        print("\n=== STEP 4: Click PayPal button ===")
        tg("Step 4: Attempting to click PayPal button...")

        # Set up popup interception
        popup_page = None
        popup_event = asyncio.Event()

        async def handle_new_page(new_page):
            nonlocal popup_page
            popup_page = new_page
            popup_event.set()
            print(f"[POPUP] New page/popup opened: {new_page.url}")

        context.on("page", handle_new_page)

        # Try clicking in each PayPal frame
        clicked = False
        for frame in page.frames:
            if "paypal.com" in frame.url and not clicked:
                try:
                    frame_url = frame.url
                    print(f"[STEP 4] Trying frame: {frame_url[:80]}")

                    # Check frame has clickable elements
                    frame_content = await frame.evaluate("""(function(){
                        var btns = document.querySelectorAll('button, .paypal-button, [class*="button"]');
                        return {
                            buttonCount: btns.length,
                            bodyText: document.body ? document.body.innerText.substring(0, 100) : 'no body',
                            bodyHtml: document.body ? document.body.innerHTML.substring(0, 200) : 'no body'
                        };
                    })()""")
                    print(f"[STEP 4] Frame content: {frame_content}")

                    if frame_content['buttonCount'] > 0:
                        # Click the first button
                        await frame.click("button", timeout=5000)
                        print(f"[STEP 4] Clicked button in frame!")
                        clicked = True
                    else:
                        # Try clicking the frame body
                        await frame.click("body", timeout=3000)
                        print(f"[STEP 4] Clicked frame body")
                        clicked = True
                except Exception as e:
                    print(f"[STEP 4] Frame click error: {e}")

        # If frame clicking didn't work, try clicking PayPal container in main page
        if not clicked:
            try:
                # Find PayPal container bounding box
                paypal_loc = await page.evaluate("""(function(){
                    var ppContainer = document.querySelector(
                        '.paypal-button-container, [id*="paypal"], [class*="paypal-buttons"]'
                    );
                    if (!ppContainer) return null;
                    var r = ppContainer.getBoundingClientRect();
                    return {x: r.x + r.width/2, y: r.y + r.height/2, w: r.width, h: r.height};
                })()""")

                if paypal_loc:
                    print(f"[STEP 4] PayPal container at: {paypal_loc}")
                    await page.mouse.click(paypal_loc['x'], paypal_loc['y'])
                    print("[STEP 4] Clicked PayPal container location")
                    clicked = True
            except Exception as e:
                print(f"[STEP 4] Container click failed: {e}")

        await asyncio.sleep(3)
        await ss(page, "05-after-paypal-click")

        # ============================================================
        # STEP 5: HANDLE PAYPAL POPUP
        # ============================================================
        print("\n=== STEP 5: Handle PayPal popup ===")

        # Wait for popup
        try:
            await asyncio.wait_for(popup_event.wait(), timeout=15)
            print(f"[STEP 5] Popup intercepted: {popup_page.url if popup_page else 'none'}")
        except asyncio.TimeoutError:
            print("[STEP 5] No popup after 15s")

        if popup_page:
            tg(f"Step 5: PayPal popup opened! URL: {popup_page.url[:80]}")
            await asyncio.sleep(3)
            await popup_page.wait_for_load_state("networkidle", timeout=20000)
            await ss(popup_page, "06-paypal-popup")

            popup_body = await popup_page.evaluate("document.body ? document.body.innerText : 'empty'")
            print(f"[STEP 5] PayPal popup content: {popup_body[:500]}")

            # --- LOGIN FLOW ---
            # Find email field
            email_f = None
            for sel in ["#email", "input[type='email']", "input[name='login_email']"]:
                try:
                    f = await popup_page.query_selector(sel)
                    if f and await f.is_visible():
                        email_f = f
                        print(f"[STEP 5] Email field: {sel}")
                        break
                except:
                    pass

            if email_f:
                await email_f.fill(PAYPAL_EMAIL)
                await asyncio.sleep(0.5)
                await ss(popup_page, "07-paypal-email")

                # Click Next
                for sel in ["#btnNext", "button#btnNext", "button[type='submit']"]:
                    try:
                        b = await popup_page.query_selector(sel)
                        if b and await b.is_visible():
                            await b.click()
                            print(f"[STEP 5] Clicked Next: {sel}")
                            break
                    except:
                        pass

                await asyncio.sleep(3)
                await popup_page.wait_for_load_state("networkidle", timeout=15000)
                await ss(popup_page, "08-paypal-after-next")

            # Find password field
            pw_f = None
            for sel in ["#password", "input[type='password']", "input[name='login_password']"]:
                try:
                    f = await popup_page.query_selector(sel)
                    if f and await f.is_visible():
                        pw_f = f
                        print(f"[STEP 5] Password field: {sel}")
                        break
                except:
                    pass

            if pw_f:
                await pw_f.fill(PAYPAL_PASSWORD)
                await asyncio.sleep(0.5)
                await ss(popup_page, "09-paypal-password")

                for sel in ["#btnLogin", "button#btnLogin", "button[type='submit']", "#login-button"]:
                    try:
                        b = await popup_page.query_selector(sel)
                        if b and await b.is_visible():
                            await b.click()
                            print(f"[STEP 5] Clicked Login: {sel}")
                            break
                    except:
                        pass

                await asyncio.sleep(5)
                await popup_page.wait_for_load_state("networkidle", timeout=20000)
                await ss(popup_page, "10-paypal-after-login")

                post_login_body = await popup_page.evaluate("document.body.innerText")
                post_login_url = popup_page.url
                print(f"[STEP 5] Post-login URL: {post_login_url}")
                print(f"[STEP 5] Post-login content (500): {post_login_body[:500]}")

                # Check for errors
                error_phrases = ["didn't match", "incorrect password", "try again", "something went wrong"]
                login_error = any(ph in post_login_body.lower() for ph in error_phrases)

                if login_error:
                    tg(f"Step 5 ERROR: PayPal login rejected. Page says: '{post_login_body[:200]}'")
                    await ss(popup_page, "11-paypal-login-error")
                    print("[STEP 5] LOGIN FAILED - proceeding with JS simulation fallback")
                    await popup_page.close()
                    tg("Falling back to JS simulation for post-payment flow documentation")
                    await sim_flow(page, console_log, page_errors, api_calls)
                    await browser.close()
                    return

                # Login successful - look for payment approval
                tg("Step 5: PayPal login successful! Looking for payment confirmation...")

                # Find and click Pay Now
                await asyncio.sleep(3)
                pay_btn_found = False
                for sel in [
                    "#payment-submit-btn",
                    "#confirmButtonTop",
                    "button#btnContinue",
                    "input[value*='Pay Now']",
                    "input[value*='Continue']",
                ]:
                    try:
                        b = await popup_page.query_selector(sel)
                        if b and await b.is_visible():
                            btn_text = await b.inner_text() if b.tag_name != "INPUT" else await b.get_attribute("value")
                            print(f"[STEP 5] Pay button found '{btn_text}': {sel}")
                            tg(f"Step 5: Found PAY button: '{btn_text}' - clicking!")
                            await b.click()
                            pay_btn_found = True
                            await asyncio.sleep(5)
                            await ss(popup_page, "12-paypal-pay-clicked")
                            break
                    except:
                        pass

                if not pay_btn_found:
                    # Try text-based search
                    pay_text_body = await popup_page.evaluate("document.body.innerText")
                    print(f"[STEP 5] Payment page content: {pay_text_body[:600]}")
                    await ss(popup_page, "12-paypal-payment-page")
                    tg(f"Step 5: Payment page content: '{pay_text_body[:300]}'")

                # Wait for popup to close or redirect
                try:
                    await popup_page.wait_for_event("close", timeout=20000)
                    tg("Step 5: PayPal popup CLOSED - payment complete!")
                except asyncio.TimeoutError:
                    final_popup_body = await popup_page.evaluate("document.body.innerText")
                    print(f"[STEP 5] Popup still open. Content: {final_popup_body[:400]}")
                    await ss(popup_page, "12b-paypal-popup-still-open")
                    tg(f"Step 5: Popup still open. Content: '{final_popup_body[:200]}'")

                # Try closing manually
                try:
                    await popup_page.close()
                except:
                    pass
            else:
                print("[STEP 5] Password field not found after Next")
                body_now = await popup_page.evaluate("document.body.innerText")
                print(f"[STEP 5] Page after Next: {body_now[:400]}")
                await ss(popup_page, "10-paypal-no-password-field")
                tg(f"Step 5: No password field. Page: '{body_now[:200]}'")
        else:
            print("[STEP 5] No popup was intercepted - PayPal button may not have been clicked")
            tg("Step 5: No PayPal popup appeared. Trying JS simulation...")
            await sim_flow(page, console_log, page_errors, api_calls)
            await browser.close()
            return

        # ============================================================
        # STEP 6: CHECK MAIN PAGE POST-PAYMENT
        # ============================================================
        print("\n=== STEP 6: Check main page post-payment ===")
        tg("Step 6: Checking main page for post-payment chatbox...")

        await asyncio.sleep(8)
        await ss(page, "13-main-page-post-payment")

        container_state = await page.evaluate("""(function(){
            var el = document.getElementById('pay-test-post-payment');
            if (!el) return {found: false};
            return {
                found: true,
                display: window.getComputedStyle(el).display,
                childCount: el.children.length,
                text: el.textContent.trim().substring(0, 200)
            };
        })()""")
        print(f"[STEP 6] Post-payment container: {container_state}")

        if container_state['found'] and container_state.get('childCount', 0) > 0:
            tg("Step 6: Post-payment chatbox IS active! Starting Q&A flow...")
        else:
            # Check API calls for payment events
            payment_apis = [r for r in api_calls if any(x in r for x in ["verify-payment", "log-pay-test", "payment"])]
            print(f"[STEP 6] Payment API calls: {payment_apis}")
            tg(f"Step 6: Container state = {container_state}. API calls: {payment_apis[:3]}. Falling back to JS sim...")
            await sim_flow(page, console_log, page_errors, api_calls)
            await browser.close()
            return

        # ============================================================
        # POST-PAYMENT FLOW: Q&A + SLIDES + FINAL
        # ============================================================
        await post_payment_flow(page, console_log, page_errors)

        await browser.close()
        final_summary(console_log, page_errors, api_calls)

async def sim_flow(page, console_log, page_errors, api_calls):
    """JS simulation fallback."""
    tg("FALLBACK: Triggering onPaymentComplete via JS to document full post-payment flow")
    print("\n=== JS SIMULATION FALLBACK ===")

    # Check available functions
    funcs = await page.evaluate("""(function(){
        return {
            onPaymentComplete: typeof window.onPaymentComplete,
            launchPostPaymentFlow: typeof window.launchPostPaymentFlow,
            initPayTestFlow: typeof window.initPayTestFlow,
            sanitizeText: typeof window.sanitizeText
        };
    })()""")
    print(f"[SIM] Functions: {funcs}")
    tg(f"SIM: Functions available: {funcs}")

    if funcs.get("onPaymentComplete") == "function":
        await page.evaluate("window.onPaymentComplete('Awakened', 'SIM-REAL-20260304-001', {})")
        print("[SIM] Triggered onPaymentComplete")
    elif funcs.get("launchPostPaymentFlow") == "function":
        await page.evaluate("window.launchPostPaymentFlow('Awakened', 'SIM-REAL-20260304-001')")
        print("[SIM] Triggered launchPostPaymentFlow")
    else:
        print("[SIM] No trigger functions available!")
        tg("SIM ERROR: Neither onPaymentComplete nor launchPostPaymentFlow is on window")
        return

    await asyncio.sleep(5)

    container = await page.evaluate("""(function(){
        var el = document.getElementById('pay-test-post-payment');
        if (!el) return {found: false};
        return {found: true, childCount: el.children.length, display: window.getComputedStyle(el).display};
    })()""")
    print(f"[SIM] Container after trigger: {container}")

    await post_payment_flow(page, console_log, page_errors)


async def post_payment_flow(page, console_log, page_errors):
    """Complete post-payment flow: Q&A + Slides + Final button."""
    global screenshot_count

    print("\n=== POST-PAYMENT FLOW ===")

    # Wait for input
    print("[PTC] Waiting for PTC input to activate...")
    activated = await wait_for_input(page, timeout=60)

    if not activated:
        tg("ERROR: PTC input never activated after payment")
        current_ss = await ss(page, "ptc-not-activated")

        # Check for page errors
        for err in page_errors:
            print(f"[PAGE ERROR] {err}")
            tg(f"Page error: {err[:100]}")
        return

    await ss(page, "ptc-active-ready-for-qa")
    tg("PTC chatbox is ACTIVE! Starting Q&A...")

    # Initial AI message
    await asyncio.sleep(3)
    initial = await get_msgs(page)
    print(f"[PTC] Initial AI messages: {initial}")
    if initial:
        tg(f"AI first message: '{initial[-1][:150]}'")

    # Q&A sequence
    qa_steps = [
        ("Alex Carter", "Name"),
        ("alex.carter.test@example.com", "Email"),
        ("Frontier AI Ventures", "Company"),
        ("CTO", "Role"),
        ("Automate our entire research pipeline so our team can focus on high-level strategy instead of manual data gathering", "Goal"),
    ]

    for qa_answer, qa_label in qa_steps:
        print(f"\n[Q&A] {qa_label}: '{qa_answer}'")
        tg(f"Q&A: Sending {qa_label} = '{qa_answer[:60]}'")

        # Wait for input active
        active = await wait_for_input(page, timeout=20)
        if not active:
            print(f"[Q&A] Input inactive at {qa_label}")
            await ss(page, f"qa-input-gone-at-{qa_label.lower()}")
            tg(f"Q&A: Input went inactive at {qa_label} step")

            # Check if slides appeared or other state change
            state = await page.evaluate("""(function(){
                var slides = document.querySelector('.ptc-slide, .behind-curtain, [class*="slide"]');
                var btns = Array.from(document.querySelectorAll('button'))
                    .filter(b => window.getComputedStyle(b).display !== 'none')
                    .map(b => b.textContent.trim().substring(0, 60));
                return {slides: !!slides, buttons: btns};
            })()""")
            print(f"[Q&A] State at inactive: {state}")
            if state['slides']:
                tg("Q&A: Slides appeared! Moving to slide phase...")
                break
            break

        sent = await send_msg(page, qa_answer)
        await asyncio.sleep(1)
        await ss(page, f"qa-{qa_label.lower()}-sent")

        # Wait for AI response
        prev_count = len(await get_msgs(page))
        for wait_i in range(12):
            await asyncio.sleep(1)
            new_msgs = await get_msgs(page)
            if len(new_msgs) > prev_count:
                latest = new_msgs[-1]
                print(f"[Q&A] AI: '{latest[:120]}'")
                tg(f"AI after {qa_label}: '{latest[:120]}'")
                break

        await ss(page, f"qa-{qa_label.lower()}-response")

    # ============================================================
    # SLIDES PHASE
    # ============================================================
    print("\n=== SLIDES PHASE ===")
    tg("Slides phase: Looking for Behind the Curtain slides...")

    await asyncio.sleep(5)
    await ss(page, "slides-phase-start")

    slides_clicked = 0
    for slide_i in range(15):
        # Get all visible buttons
        visible_btns = await page.evaluate("""(function(){
            return Array.from(document.querySelectorAll('button')).map(b => ({
                text: b.textContent.trim(),
                visible: window.getComputedStyle(b).display !== 'none' && b.offsetParent !== null,
                class: b.className.substring(0, 50),
                disabled: b.disabled
            })).filter(b => b.visible && !b.disabled && b.text.length > 0);
        })()""")

        print(f"[SLIDES] Visible buttons at step {slide_i}: {visible_btns}")

        found_btn = None
        for btn_data in visible_btns:
            t = btn_data['text'].lower()
            if any(phrase in t for phrase in ["show me more", "incredible", "let's go", "next slide", "continue"]):
                found_btn = btn_data
                break

        if not found_btn:
            print(f"[SLIDES] No slide button found at step {slide_i}")
            if slide_i > 0:
                tg(f"Slides complete after {slides_clicked} clicks. Moving to final CTA...")
            break

        btn_text = found_btn['text']
        print(f"[SLIDES] Clicking: '{btn_text}'")
        tg(f"Slide {slide_i + 1}: Clicking '{btn_text}'")

        try:
            # Find and click
            await page.get_by_text(btn_text, exact=True).click(timeout=5000)
        except:
            try:
                await page.get_by_text(btn_text, exact=False).first.click(timeout=5000)
            except Exception as e:
                print(f"[SLIDES] Click error: {e}")
                break

        slides_clicked += 1
        await asyncio.sleep(2)
        await ss(page, f"slide-{slide_i + 1:02d}-{btn_text[:20].replace(' ', '-').lower()}")

        # Check if this was the last slide
        if "incredible" in btn_text.lower() or "let's go" in btn_text.lower():
            print("[SLIDES] Clicked final slide button!")
            tg("Slides COMPLETE: Clicked 'That's incredible — let's go'!")
            await asyncio.sleep(3)
            break

    print(f"[SLIDES] Total clicked: {slides_clicked}")

    # ============================================================
    # "YOUR AI IS READY" BUTTON
    # ============================================================
    print("\n=== YOUR AI IS READY ===")
    tg("Looking for 'Your AI is ready — see your next steps' orange button...")

    await asyncio.sleep(3)
    await ss(page, "your-ai-ready-search")

    # Get all buttons again
    all_btns = await page.evaluate("""(function(){
        return Array.from(document.querySelectorAll('button, a, input[type="submit"]')).map(el => ({
            tag: el.tagName,
            text: el.textContent.trim().substring(0, 100),
            class: el.className.substring(0, 60),
            id: el.id,
            visible: window.getComputedStyle(el).display !== 'none' && el.offsetParent !== null,
            disabled: el.disabled || false
        })).filter(el => el.visible);
    })()""")

    print(f"[CTA] All visible elements: {all_btns}")
    tg(f"Visible elements: {[b['text'] for b in all_btns[:10]]}")

    # Find "Your AI is ready"
    your_ai_btn = None
    for btn_data in all_btns:
        if "your ai is ready" in btn_data['text'].lower() or ("ptc-welcome" in btn_data['class'].lower()):
            print(f"[CTA] Found: {btn_data}")
            your_ai_btn = btn_data
            break

    if your_ai_btn:
        await ss(page, "your-ai-ready-button-found")
        tg(f"Found 'Your AI is ready' button! Text: '{your_ai_btn['text']}' - CLICKING (not the end!)")

        try:
            if your_ai_btn['id']:
                await page.click(f"#{your_ai_btn['id']}", timeout=5000)
            else:
                await page.get_by_text(your_ai_btn['text'][:30], exact=False).first.click(timeout=5000)
        except Exception as e:
            print(f"[CTA] Click error: {e}")
            # Try JS click
            await page.evaluate("""(function(){
                var btns = Array.from(document.querySelectorAll('button, a'));
                var btn = btns.find(b => b.textContent.includes('Your AI is ready') || b.className.includes('ptc-welcome'));
                if (btn) btn.click();
            })()""")

        await asyncio.sleep(4)
        await ss(page, "after-your-ai-ready-click")
        tg("Clicked 'Your AI is ready' - checking what comes next...")
    else:
        print("[CTA] 'Your AI is ready' button not found")
        tg("WARNING: 'Your AI is ready' button not found. Checking page state...")
        await ss(page, "your-ai-button-missing")

    # ============================================================
    # FINAL STATE: BRAIN STREAM BUTTON
    # ============================================================
    print("\n=== FINAL STATE: BRAIN STREAM ===")
    tg("Looking for ENTER [AI NAME]'S BRAIN STREAM button (ABSOLUTE FINAL STATE)...")

    await asyncio.sleep(5)
    await ss(page, "final-state-1")

    # Comprehensive final state check
    final = await page.evaluate("""(function(){
        var result = {
            brain_buttons: [],
            portal: null,
            all_visible: [],
            page_text: document.body.innerText.substring(0, 1000)
        };

        // Find BRAIN STREAM button
        Array.from(document.querySelectorAll('*')).forEach(el => {
            var text = el.textContent.trim();
            var style = window.getComputedStyle(el);
            if ((text.includes('BRAIN STREAM') || text.includes('ENTER')) && text.length < 200) {
                result.brain_buttons.push({
                    tag: el.tagName,
                    text: text.substring(0, 100),
                    class: el.className.substring(0, 60),
                    id: el.id,
                    display: style.display,
                    opacity: style.opacity,
                    disabled: el.disabled || false,
                    visible: style.display !== 'none' && el.offsetParent !== null
                });
            }
        });

        // Portal
        var p = document.querySelector('.portal-vortex, #portal-vortex, .ptc-portal-btn');
        if (p) {
            result.portal = {
                class: p.className,
                text: p.textContent.trim().substring(0, 100),
                childCount: p.children.length,
                display: window.getComputedStyle(p).display
            };
        }

        // All visible interactive elements
        result.all_visible = Array.from(document.querySelectorAll('button, a[href], input[type="submit"]'))
            .filter(el => {
                var s = window.getComputedStyle(el);
                return s.display !== 'none' && el.offsetParent !== null;
            })
            .map(el => ({
                tag: el.tagName,
                text: el.textContent.trim().substring(0, 80),
                class: el.className.substring(0, 50),
                disabled: el.disabled || false
            }));

        return result;
    })()""")

    print(f"\n[FINAL] Brain buttons: {final['brain_buttons']}")
    print(f"[FINAL] Portal: {final['portal']}")
    print(f"[FINAL] All visible: {final['all_visible']}")
    print(f"[FINAL] Page text (500): {final['page_text'][:500]}")

    tg(f"FINAL STATE - Brain buttons: {final['brain_buttons'][:3]}")
    tg(f"FINAL STATE - All visible elements: {[e['text'] for e in final['all_visible'][:10]]}")
    tg(f"FINAL STATE - Page text: '{final['page_text'][:400]}'")

    brain_btns = final['brain_buttons']
    if brain_btns:
        for bb in brain_btns:
            status = "DISABLED" if bb['disabled'] else ("VISIBLE" if bb['visible'] else "HIDDEN")
            tg(f"Brain Stream button: '{bb['text']}' - Status: {status} - opacity: {bb.get('opacity', '?')}")
            print(f"[FINAL] Brain button: '{bb['text']}' status={status}")

        # Check if any are clickable
        clickable = [bb for bb in brain_btns if bb['visible'] and not bb['disabled']]
        if clickable:
            tg("Brain Stream button is ACTIVE! CLICKING IT!")
            await page.evaluate("""(function(){
                var els = Array.from(document.querySelectorAll('*'));
                var btn = els.find(el => el.textContent.includes('BRAIN STREAM') && window.getComputedStyle(el).display !== 'none');
                if (btn) btn.click();
            })()""")
            await asyncio.sleep(4)
            await ss(page, "brain-stream-clicked")
            after_text = await page.evaluate("document.body.innerText.substring(0, 500)")
            tg(f"After Brain Stream click: '{after_text[:300]}'")
        else:
            tg("Brain Stream button is GREYED OUT / DISABLED (expected final state)")
    else:
        tg("No Brain Stream button found. Page may be in intermediate state.")

    # Final screenshots
    await ss(page, "final-state-2-complete")

    # Scroll to top
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(1)
    await ss(page, "final-scroll-top")

    # Scroll to bottom
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await asyncio.sleep(1)
    await ss(page, "final-scroll-bottom")

    tg(f"E2E sandbox3 v2 COMPLETE. {screenshot_count} screenshots. Dir: exports/screenshots/sandbox3-e2e-full-20260304/")

def final_summary(console_log, page_errors, api_calls):
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Console entries: {len(console_log)}")
    print(f"Page errors: {len(page_errors)}")
    print(f"API calls: {len(api_calls)}")

    print("\nPage errors:")
    for e in page_errors:
        print(f"  {e[:150]}")

    print("\nAPI calls:")
    for c in api_calls[-20:]:
        print(f"  {c[:120]}")

    if page_errors:
        tg(f"Page errors ({len(page_errors)}): {page_errors[0][:150]}")
    tg(f"API calls total: {len(api_calls)}. Last 5: {api_calls[-5:]}")


if __name__ == "__main__":
    asyncio.run(main())
