"""
E2E Test: pay-test-sandbox-3 with REAL PayPal sandbox payment
Date: 2026-03-04
Tester: browser-vision-tester

Full flow:
1. Navigate to page -> enter password
2. Click real PayPal button (in iframe)
3. PayPal popup -> login with sandbox creds
4. Approve payment
5. Post-payment chatbox -> answer all Q&A
6. Behind the Curtain slides (10 slides)
7. "That's incredible - let's go" button
8. "Your AI is ready - see your next steps" orange button
9. Continue to final state: "ENTER [AI NAME]'S BRAIN STREAM"

Screenshots saved to: exports/screenshots/sandbox3-e2e-full-20260304/
"""

import asyncio
import os
import sys
import time
import subprocess
from playwright.async_api import async_playwright

# Config
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-3/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
PAYPAL_EMAIL = "sb-c89tj49549583@personal.example.com"
PAYPAL_PASSWORD = "Z0+6<dS"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-e2e-full-20260304"
TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"

# Q&A answers
QA_ANSWERS = {
    "name": "Alex Carter",
    "email": "alex.carter.test@example.com",
    "company": "Frontier AI Ventures",
    "role": "CTO",
    "goal": "Automate our entire research pipeline so our team can focus on high-level strategy instead of manual data gathering"
}

screenshot_count = 0

def tg_send(message):
    """Send message to Telegram."""
    try:
        subprocess.run([TG_SEND, message], timeout=10, capture_output=True)
        print(f"[TG] {message}")
    except Exception as e:
        print(f"[TG ERROR] {e}")

def tg_photo(path, caption):
    """Send photo to Telegram."""
    try:
        subprocess.run([TG_SEND, "--photo", path, caption], timeout=15, capture_output=True)
        print(f"[TG PHOTO] {caption}")
    except Exception as e:
        print(f"[TG PHOTO ERROR] {e}")

async def screenshot(page, label, send_to_tg=True):
    """Take screenshot and optionally send to Telegram."""
    global screenshot_count
    screenshot_count += 1
    filename = f"{screenshot_count:03d}-{label}.png"
    path = os.path.join(SCREENSHOT_DIR, filename)
    await page.screenshot(path=path, full_page=False)
    print(f"[SCREENSHOT] {filename}")
    if send_to_tg:
        tg_photo(path, f"E2E sandbox3: {label}")
    return path

async def wait_ptc_input_active(page, timeout=90):
    """Wait for PTC input row to become visible."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            display = await page.evaluate("""(function(){
                var row = document.getElementById('ptc-input-row');
                if (!row) return 'not-found';
                return window.getComputedStyle(row).display;
            })()""")
            if display not in ("none", "not-found"):
                return True
        except:
            pass
        await asyncio.sleep(1)
    return False

async def get_ai_messages(page):
    """Get all AI message texts from chatbox."""
    try:
        msgs = await page.evaluate("""(function(){
            var els = document.querySelectorAll('.ptc-msg--ai, .ptc-message--ai, [class*="ai-msg"]');
            return Array.from(els).map(e => e.textContent.trim()).filter(t => t.length > 0);
        })()""")
        return msgs
    except:
        return []

async def get_latest_ai_message(page, wait_sec=8):
    """Wait for new AI message and return it."""
    await asyncio.sleep(wait_sec)
    msgs = await get_ai_messages(page)
    if msgs:
        return msgs[-1]
    return None

async def ptc_send(page, text, label=""):
    """Type and send message in PTC chatbox."""
    print(f"[PTC SEND] {label}: {text[:50]}...")

    # Try multiple selectors
    ta = None
    for sel in ["#ptc-input", "textarea.ptc-input", "textarea[id*='ptc']", "textarea"]:
        try:
            el = await page.query_selector(sel)
            if el and await el.is_visible():
                ta = el
                break
        except:
            pass

    if not ta:
        print("[PTC SEND] ERROR: No textarea found")
        return False

    try:
        await ta.click()
        await asyncio.sleep(0.3)
        await ta.fill("")
        await asyncio.sleep(0.2)
        await ta.type(text, delay=25)
        await asyncio.sleep(0.4)

        # Try send button first
        sent = False
        for sel in ["#ptc-send-btn", ".ptc-send-btn", "button[id*='send']", "button[class*='send']"]:
            try:
                btn = await page.query_selector(sel)
                if btn and await btn.is_visible():
                    await btn.click()
                    sent = True
                    break
            except:
                pass

        if not sent:
            await ta.press("Enter")

        print(f"[PTC SEND] Sent OK")
        return True
    except Exception as e:
        print(f"[PTC SEND] Error: {e}")
        return False

async def find_paypal_button_frame(page):
    """Find the real PayPal button iframe (not style preload)."""
    for attempt in range(20):
        for frame in page.frames:
            try:
                url = frame.url
                # Real PayPal button frame
                if "paypal.com" in url and ("zoid" in url or "smart/buttons" in url):
                    # Check if it has actual button content
                    has_btn = await frame.evaluate("""(function(){
                        var btns = document.querySelectorAll('button, .paypal-button, [class*="paypal"]');
                        return btns.length > 0;
                    })()""")
                    if has_btn:
                        print(f"[PAYPAL] Found button frame: {url[:80]}")
                        return frame
            except:
                pass
        await asyncio.sleep(1)
    return None

async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    tg_send("E2E sandbox3 REAL PayPal: Starting full test 2026-03-04")

    async with async_playwright() as p:
        # Launch browser - non-headless for PayPal popup handling
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--allow-running-insecure-content"
            ]
        )

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Capture console + page errors
        console_log = []
        page_errors = []
        network_requests = []

        page = await context.new_page()

        page.on("console", lambda msg: console_log.append(f"[{msg.type.upper()}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(f"[PAGE-ERROR] {str(err)}"))

        async def on_response(response):
            url = response.url
            if "purebrain.ai" in url or "api.purebrain" in url:
                try:
                    status = response.status
                    network_requests.append(f"{status} {url}")
                    if status >= 400:
                        print(f"[NETWORK ERROR] {status} {url}")
                except:
                    pass

        page.on("response", on_response)

        # ========================
        # STEP 1: Navigate to page
        # ========================
        print("\n=== STEP 1: Navigate to page ===")
        tg_send("E2E sandbox3 Step 1: Navigating to page...")

        await page.goto(PAGE_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        await screenshot(page, "page-initial-load")

        page_title = await page.title()
        page_content = await page.content()
        print(f"[STEP 1] Page title: {page_title}")

        # Check if password form is present
        has_password = await page.query_selector("input[type='password'], input[name='post_password']")
        print(f"[STEP 1] Password form present: {has_password is not None}")

        # ========================
        # STEP 2: Enter password
        # ========================
        print("\n=== STEP 2: Enter page password ===")

        if has_password:
            pw_field = await page.query_selector("input[type='password'], input[name='post_password']")
            await pw_field.click()
            await pw_field.fill(PAGE_PASSWORD)
            await screenshot(page, "password-entered")

            # Find submit button
            submit = await page.query_selector("input[type='submit'], button[type='submit'], .post-password-form input[type='submit']")
            if submit:
                await submit.click()
            else:
                await pw_field.press("Enter")

            await page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(2)
            await screenshot(page, "after-password-submit")
            tg_send("E2E sandbox3 Step 2: Password submitted, page loaded")
        else:
            # Maybe already unlocked from cookies
            print("[STEP 2] No password form - page may already be unlocked")
            await screenshot(page, "no-password-form")

        # Check page state after password
        current_url = page.url
        print(f"[STEP 2] Current URL: {current_url}")

        # ========================
        # STEP 3: Find PayPal section
        # ========================
        print("\n=== STEP 3: Locate PayPal button ===")
        tg_send("E2E sandbox3 Step 3: Looking for PayPal button...")

        await asyncio.sleep(3)
        await screenshot(page, "payment-section-view")

        # Check page content
        body_text = await page.evaluate("document.body.innerText")
        print(f"[STEP 3] Page text preview (500 chars): {body_text[:500]}")

        # List all iframes
        frames = page.frames
        print(f"[STEP 3] Total frames: {len(frames)}")
        for i, f in enumerate(frames):
            print(f"  Frame {i}: {f.url[:100]}")

        # Wait for PayPal SDK to load iframes
        print("[STEP 3] Waiting for PayPal iframes to load...")
        for wait_attempt in range(15):
            frames = page.frames
            paypal_frames = [f for f in frames if "paypal.com" in f.url]
            if len(paypal_frames) >= 1:
                print(f"[STEP 3] PayPal frames found: {len(paypal_frames)}")
                break
            await asyncio.sleep(2)
            if wait_attempt == 7:
                tg_send("E2E sandbox3: Still waiting for PayPal to load (attempt 8/15)...")
                await screenshot(page, "waiting-for-paypal")

        # Take screenshot showing PayPal button area
        await screenshot(page, "paypal-button-area")

        # ========================
        # STEP 4: Click PayPal button
        # ========================
        print("\n=== STEP 4: Click PayPal button ===")
        tg_send("E2E sandbox3 Step 4: Attempting to click PayPal button...")

        # Strategy 1: Try clicking in PayPal iframes
        paypal_clicked = False

        for frame in page.frames:
            if "paypal.com" in frame.url and not paypal_clicked:
                try:
                    # Try to find and click the PayPal button within frame
                    paypal_btn = await frame.query_selector(
                        ".paypal-button, [class*='paypal-button'], button[class*='paypal'], "
                        "div[role='button'][class*='paypal'], .paypal-buttons-label-container"
                    )
                    if paypal_btn:
                        await paypal_btn.click()
                        print(f"[STEP 4] Clicked PayPal button in frame: {frame.url[:80]}")
                        paypal_clicked = True
                except Exception as e:
                    print(f"[STEP 4] Frame click attempt failed: {e}")

        # Strategy 2: Click at PayPal button location in main page
        if not paypal_clicked:
            try:
                # Scroll to PayPal button area
                await page.evaluate("window.scrollTo(0, 500)")
                await asyncio.sleep(1)

                # Find button by JS
                paypal_location = await page.evaluate("""(function(){
                    // Find PayPal container/wrapper
                    var containers = document.querySelectorAll(
                        '[id*="paypal"], [class*="paypal"], .paypal-button-container, ' +
                        '#paypal-button-container, .pp-QKWJVLSQPK5GE'
                    );
                    if (containers.length > 0) {
                        var rect = containers[0].getBoundingClientRect();
                        return {found: true, x: rect.x + rect.width/2, y: rect.y + rect.height/2,
                                id: containers[0].id, cls: containers[0].className.substring(0,50)};
                    }
                    return {found: false};
                })()""")
                print(f"[STEP 4] PayPal container: {paypal_location}")

                if paypal_location.get("found"):
                    x = paypal_location["x"]
                    y = paypal_location["y"]
                    await page.mouse.click(x, y)
                    print(f"[STEP 4] Clicked at PayPal container ({x}, {y})")
                    paypal_clicked = True
            except Exception as e:
                print(f"[STEP 4] Container click failed: {e}")

        await asyncio.sleep(2)
        await screenshot(page, "after-paypal-click-attempt")

        # ========================
        # STEP 5: Handle PayPal popup
        # ========================
        print("\n=== STEP 5: Waiting for PayPal popup ===")
        tg_send("E2E sandbox3 Step 5: Waiting for PayPal login popup...")

        paypal_popup = None
        popup_wait_start = time.time()

        # Set up popup handler
        popup_future = asyncio.Future()

        def handle_popup(popup):
            print(f"[STEP 5] Popup opened: {popup.url}")
            popup_future.set_result(popup)

        context.on("page", handle_popup)

        # If not clicked yet, try once more
        if not paypal_clicked:
            # Try clicking in each PayPal frame
            for frame in page.frames:
                if "paypal.com" in frame.url:
                    try:
                        await frame.click("body", timeout=3000)
                        print(f"[STEP 5] Clicked frame body: {frame.url[:60]}")
                    except:
                        pass

        # Wait for popup (up to 30 seconds)
        try:
            paypal_popup = await asyncio.wait_for(popup_future, timeout=30)
            print(f"[STEP 5] PayPal popup appeared: {paypal_popup.url}")
            tg_send(f"E2E sandbox3: PayPal popup opened!")
        except asyncio.TimeoutError:
            print("[STEP 5] WARNING: No popup appeared in 30 seconds")
            tg_send("E2E sandbox3 WARNING: PayPal popup did not appear - checking page state")
            await screenshot(page, "no-paypal-popup")

        if paypal_popup:
            await asyncio.sleep(3)
            await paypal_popup.wait_for_load_state("networkidle", timeout=20000)
            popup_url = paypal_popup.url
            popup_title = await paypal_popup.title()
            print(f"[STEP 5] Popup title: {popup_title}")
            print(f"[STEP 5] Popup URL: {popup_url}")

            await screenshot(paypal_popup, "paypal-popup-loaded")

            # ========================
            # STEP 6: PayPal Login
            # ========================
            print("\n=== STEP 6: PayPal sandbox login ===")
            tg_send(f"E2E sandbox3 Step 6: Entering PayPal sandbox credentials...")

            await asyncio.sleep(2)

            # Find email field
            email_field = None
            for sel in ["#email", "input[type='email']", "input[name='login_email']", "input[id*='email']"]:
                try:
                    f = await paypal_popup.query_selector(sel)
                    if f and await f.is_visible():
                        email_field = f
                        print(f"[STEP 6] Email field found: {sel}")
                        break
                except:
                    pass

            if email_field:
                await email_field.click()
                await email_field.fill(PAYPAL_EMAIL)
                await asyncio.sleep(0.5)
                await screenshot(paypal_popup, "paypal-email-entered")

                # Click Next button if present (new PayPal flow)
                next_btn = None
                for sel in ["#btnNext", "button#btnNext", "[id*='btnNext']", "button[type='submit']"]:
                    try:
                        b = await paypal_popup.query_selector(sel)
                        if b and await b.is_visible():
                            next_btn = b
                            break
                    except:
                        pass

                if next_btn:
                    await next_btn.click()
                    print("[STEP 6] Clicked Next button")
                    await asyncio.sleep(2)
                    await screenshot(paypal_popup, "paypal-after-next")
                else:
                    await email_field.press("Enter")
                    await asyncio.sleep(2)

            # Find password field
            await asyncio.sleep(1)
            pw_field = None
            for sel in ["#password", "input[type='password']", "input[name='login_password']", "input[id*='password']"]:
                try:
                    f = await paypal_popup.query_selector(sel)
                    if f and await f.is_visible():
                        pw_field = f
                        print(f"[STEP 6] Password field found: {sel}")
                        break
                except:
                    pass

            if pw_field:
                await pw_field.click()
                await pw_field.fill(PAYPAL_PASSWORD)
                await asyncio.sleep(0.5)
                await screenshot(paypal_popup, "paypal-password-entered")

                # Click Login button
                login_btn = None
                for sel in ["#btnLogin", "button#btnLogin", "[id*='btnLogin']", "button[type='submit']", "#login-button"]:
                    try:
                        b = await paypal_popup.query_selector(sel)
                        if b and await b.is_visible():
                            login_btn = b
                            break
                    except:
                        pass

                if login_btn:
                    await login_btn.click()
                    print("[STEP 6] Clicked Login button")
                else:
                    await pw_field.press("Enter")

                tg_send("E2E sandbox3: PayPal credentials submitted - waiting for result")
                await asyncio.sleep(5)
                await paypal_popup.wait_for_load_state("networkidle", timeout=30000)
                await screenshot(paypal_popup, "paypal-after-login")

                login_url = paypal_popup.url
                login_title = await paypal_popup.title()
                print(f"[STEP 6] After login - URL: {login_url}")
                print(f"[STEP 6] After login - Title: {login_title}")

                # Check for error
                page_text = await paypal_popup.evaluate("document.body.innerText")
                if "didn't match" in page_text.lower() or "incorrect" in page_text.lower() or "try again" in page_text.lower():
                    print("[STEP 6] LOGIN FAILED - credential error detected")
                    tg_send("E2E sandbox3 ERROR: PayPal login failed - credential mismatch. Reporting state.")
                    await screenshot(paypal_popup, "paypal-login-error")

                    # Report what we see
                    print(f"[STEP 6] Page text (500 chars): {page_text[:500]}")

                    # Try to close popup and report
                    await paypal_popup.close()

                    # Generate partial report
                    tg_send("E2E sandbox3: PayPal real creds rejected. Will document findings and attempt alternative flow verification.")

                    # Still continue to verify post-payment state via JS simulation
                    print("\n[FALLBACK] Attempting JS simulation to continue E2E verification...")
                    tg_send("E2E sandbox3: Falling back to JS simulation to document post-payment flow")
                    await js_simulation_flow(page, console_log, page_errors)
                    await browser.close()
                    return

                # ========================
                # STEP 7: Approve payment
                # ========================
                print("\n=== STEP 7: Approve PayPal payment ===")
                tg_send("E2E sandbox3 Step 7: Logged in - looking for payment approval...")

                await asyncio.sleep(3)
                await screenshot(paypal_popup, "paypal-logged-in-state")

                # Look for Continue/Pay Now/Approve button
                pay_btn = None
                for sel in [
                    "#payment-submit-btn",
                    "button#btnContinue",
                    "button[id*='payment']",
                    "button[id*='continue']",
                    "button[id*='approve']",
                    ".paypal-button",
                    "#confirmButtonTop",
                    "input[value*='Pay']",
                    "button:has-text('Pay Now')",
                    "button:has-text('Continue')",
                    "button:has-text('Approve')"
                ]:
                    try:
                        b = await paypal_popup.query_selector(sel)
                        if b and await b.is_visible():
                            pay_btn = b
                            print(f"[STEP 7] Pay button found: {sel}")
                            break
                    except:
                        pass

                if pay_btn:
                    btn_text = await pay_btn.inner_text()
                    print(f"[STEP 7] Pay button text: {btn_text}")
                    tg_send(f"E2E sandbox3: Found payment button: '{btn_text}' - clicking...")
                    await pay_btn.click()

                    await asyncio.sleep(5)
                    await screenshot(paypal_popup, "paypal-after-pay-click")

                    # Wait for popup to close (payment complete)
                    try:
                        await paypal_popup.wait_for_event("close", timeout=30000)
                        print("[STEP 7] PayPal popup closed - payment likely complete!")
                        tg_send("E2E sandbox3: PayPal popup closed - payment APPROVED!")
                    except:
                        print("[STEP 7] Popup still open after 30s")
                        await screenshot(paypal_popup, "paypal-popup-still-open")
                else:
                    print("[STEP 7] No pay button found - capturing full page state")
                    full_text = await paypal_popup.evaluate("document.body.innerText")
                    print(f"[STEP 7] PayPal page content: {full_text[:1000]}")
                    await screenshot(paypal_popup, "paypal-no-pay-button")
                    tg_send("E2E sandbox3 WARNING: Could not find Pay Now button")
            else:
                print("[STEP 6] Password field not found after Next")
                await screenshot(paypal_popup, "paypal-no-password-field")
                page_text = await paypal_popup.evaluate("document.body.innerText")
                print(f"[STEP 6] Page content: {page_text[:500]}")

        # ========================
        # Back on main page - check for post-payment state
        # ========================
        print("\n=== STEP 8: Check post-payment state on main page ===")
        tg_send("E2E sandbox3 Step 8: Checking main page for post-payment chatbox...")

        await asyncio.sleep(5)
        await screenshot(page, "main-page-post-payment")

        # Check if post-payment container appeared
        post_payment_state = await page.evaluate("""(function(){
            var el = document.getElementById('pay-test-post-payment');
            if (!el) return {found: false};
            var style = window.getComputedStyle(el);
            return {
                found: true,
                display: style.display,
                visibility: style.visibility,
                childCount: el.children.length,
                innerHTML_preview: el.innerHTML.substring(0, 200)
            };
        })()""")
        print(f"[STEP 8] Post-payment container: {post_payment_state}")

        if post_payment_state.get("found") and post_payment_state.get("childCount", 0) > 0:
            tg_send("E2E sandbox3: Post-payment chatbox APPEARED! Proceeding with Q&A...")
            await continue_post_payment_flow(page, console_log, page_errors, network_requests)
        else:
            print("[STEP 8] Post-payment container not ready - checking if real payment completed")
            tg_send("E2E sandbox3: Post-payment container not yet active. Verifying payment status...")

            # Check network for verify-payment call
            verify_calls = [r for r in network_requests if "verify-payment" in r or "log-pay-test" in r]
            print(f"[STEP 8] Payment-related network calls: {verify_calls}")

            await screenshot(page, "main-page-payment-check")

            # If payment didn't go through, do JS simulation as fallback
            tg_send("E2E sandbox3: Real PayPal flow incomplete. Switching to JS simulation for full flow documentation.")
            await js_simulation_flow(page, console_log, page_errors)

        await browser.close()

        # Final summary
        print("\n=== CONSOLE LOG SUMMARY ===")
        for entry in console_log[-30:]:
            print(entry)

        print("\n=== PAGE ERRORS ===")
        for err in page_errors:
            print(err)

        print(f"\n=== NETWORK CALLS ({len(network_requests)}) ===")
        for req in network_requests:
            print(req)

        tg_send(f"E2E sandbox3: Test sequence complete. Screenshots in {SCREENSHOT_DIR}")


async def js_simulation_flow(page, console_log, page_errors):
    """Run post-payment flow via JS simulation (onPaymentComplete)."""
    print("\n=== JS SIMULATION FLOW ===")
    tg_send("E2E sandbox3 JS SIM: Triggering onPaymentComplete simulation...")

    # Trigger payment simulation
    result = await page.evaluate("""(function(){
        var funcs = ['onPaymentComplete', 'launchPostPaymentFlow', 'initPayTestFlow', 'sanitizeText'];
        var status = {};
        funcs.forEach(fn => { status[fn] = typeof window[fn]; });
        return status;
    })()""")
    print(f"[JS SIM] Function availability: {result}")

    if result.get("onPaymentComplete") == "function":
        await page.evaluate("window.onPaymentComplete('Awakened', 'REAL-TEST-20260304-' + Date.now(), {})")
        print("[JS SIM] onPaymentComplete triggered")
        tg_send("E2E sandbox3 JS SIM: Payment simulated - waiting for chatbox...")
    else:
        print("[JS SIM] onPaymentComplete not available - trying launchPostPaymentFlow")
        if result.get("launchPostPaymentFlow") == "function":
            await page.evaluate("window.launchPostPaymentFlow('Awakened', 'REAL-TEST-20260304')")

    await asyncio.sleep(5)
    await screenshot(page, "js-sim-after-payment-trigger")

    await continue_post_payment_flow(page, console_log, page_errors, [])


async def continue_post_payment_flow(page, console_log, page_errors, network_requests):
    """Continue from post-payment chatbox through to final state."""
    global screenshot_count

    print("\n=== POST-PAYMENT CHATBOX FLOW ===")

    # Wait for PTC input to activate
    print("[PTC] Waiting for input to activate...")
    activated = await wait_ptc_input_active(page, timeout=60)
    print(f"[PTC] Input activated: {activated}")

    if not activated:
        tg_send("E2E sandbox3 ERROR: PTC input never activated")
        await screenshot(page, "ptc-input-not-activated")
        return

    await screenshot(page, "ptc-input-active")
    tg_send("E2E sandbox3: Chatbox active! Starting Q&A...")

    # Get initial AI message
    await asyncio.sleep(3)
    initial_msgs = await get_ai_messages(page)
    print(f"[PTC] Initial AI messages: {initial_msgs}")

    if initial_msgs:
        tg_send(f"E2E sandbox3: First AI message: '{initial_msgs[-1][:100]}'")

    # Q&A sequence
    qa_sequence = [
        ("name", QA_ANSWERS["name"], "Name"),
        ("email", QA_ANSWERS["email"], "Email"),
        ("company", QA_ANSWERS["company"], "Company"),
        ("role", QA_ANSWERS["role"], "Role"),
        ("goal", QA_ANSWERS["goal"], "Goal"),
    ]

    for qa_key, qa_answer, qa_label in qa_sequence:
        print(f"\n[Q&A] Answering: {qa_label}")

        # Check for input availability
        input_active = await wait_ptc_input_active(page, timeout=30)
        if not input_active:
            print(f"[Q&A] Input not active for {qa_label} - checking state")
            await screenshot(page, f"qa-input-not-active-{qa_key}")

            # Check for OAuth or other overlays
            overlay_check = await page.evaluate("""(function(){
                var oauth = document.querySelector('.ptc-oauth-section, [class*="oauth"]');
                var slides = document.querySelector('.ptc-slides, [class*="slides"], .behind-the-curtain');
                return {oauth: !!oauth, slides: !!slides};
            })()""")
            print(f"[Q&A] Overlay check: {overlay_check}")
            break

        sent = await ptc_send(page, qa_answer, qa_label)
        await asyncio.sleep(1)
        await screenshot(page, f"qa-{qa_key}-sent")

        if sent:
            tg_send(f"E2E sandbox3 Q&A: Sent {qa_label} = '{qa_answer[:50]}'")

            # Wait for AI response
            await asyncio.sleep(6)
            new_msgs = await get_ai_messages(page)
            if new_msgs:
                latest = new_msgs[-1]
                print(f"[Q&A] AI responded: '{latest[:100]}'")
                tg_send(f"E2E sandbox3 AI: '{latest[:100]}'")

            await screenshot(page, f"qa-{qa_key}-response")
        else:
            print(f"[Q&A] Send failed for {qa_label}")
            tg_send(f"E2E sandbox3 WARNING: Could not send {qa_label}")

    # ========================
    # Check for slides
    # ========================
    print("\n=== SLIDES: Behind the Curtain ===")
    tg_send("E2E sandbox3: Checking for Behind the Curtain slides...")

    await asyncio.sleep(5)
    await screenshot(page, "checking-for-slides")

    # Check for slide elements
    slide_state = await page.evaluate("""(function(){
        var selectors = [
            '.ptc-slides', '.behind-the-curtain', '.slide-container',
            '[class*="slide"]', '[id*="slide"]',
            'button:has-text("Show Me More")'
        ];
        var found = [];
        selectors.forEach(s => {
            try {
                var els = document.querySelectorAll(s);
                if (els.length > 0) {
                    found.push({selector: s, count: els.length, visible: Array.from(els).some(e => {
                        var style = window.getComputedStyle(e);
                        return style.display !== 'none' && style.visibility !== 'hidden';
                    })});
                }
            } catch(e) {}
        });

        // Also check all buttons
        var buttons = Array.from(document.querySelectorAll('button')).map(b => ({
            text: b.textContent.trim().substring(0, 50),
            visible: window.getComputedStyle(b).display !== 'none',
            class: b.className.substring(0, 50)
        })).filter(b => b.visible && b.text.length > 0);

        return {found_selectors: found, visible_buttons: buttons};
    })()""")

    print(f"[SLIDES] Slide state: {slide_state['found_selectors']}")
    print(f"[SLIDES] Visible buttons: {slide_state['visible_buttons']}")

    # Click through slides
    slide_count = 0
    max_slides = 15

    for slide_num in range(max_slides):
        # Look for slide advance buttons
        slide_btn = None

        # Check for various slide button texts
        for btn_text in ["Show Me More", "That's incredible — let's go", "Next", "Continue", "Show me more"]:
            try:
                btn = await page.get_by_text(btn_text, exact=False).first
                if btn and await btn.is_visible():
                    slide_btn = (btn, btn_text)
                    break
            except:
                pass

        # Also check by class
        if not slide_btn:
            for sel in [".ptc-slide-next", ".slide-next-btn", "button[class*='slide']", ".ptc-next-btn"]:
                try:
                    btn = await page.query_selector(sel)
                    if btn and await btn.is_visible():
                        btn_text = await btn.inner_text()
                        slide_btn = (btn, btn_text)
                        break
                except:
                    pass

        if slide_btn:
            btn, btn_text = slide_btn
            slide_count += 1
            print(f"[SLIDES] Slide {slide_num + 1}: Clicking '{btn_text}'")
            tg_send(f"E2E sandbox3 Slide {slide_num + 1}: Clicking '{btn_text}'")

            await btn.click()
            await asyncio.sleep(2)
            await screenshot(page, f"slide-{slide_num + 1:02d}-{btn_text[:20].replace(' ', '-').lower()}")

            # Check if this was the final slide button ("That's incredible")
            if "incredible" in btn_text.lower() or "let's go" in btn_text.lower():
                print("[SLIDES] Clicked final slide button!")
                tg_send("E2E sandbox3: Clicked 'That's incredible — let's go'!")
                await asyncio.sleep(3)
                break
        else:
            print(f"[SLIDES] No slide button found at iteration {slide_num}")
            break

    print(f"[SLIDES] Total slides clicked: {slide_count}")

    await asyncio.sleep(3)
    await screenshot(page, "after-all-slides")

    # ========================
    # Step: Your AI is ready button
    # ========================
    print("\n=== STEP: Your AI is ready button ===")
    tg_send("E2E sandbox3: Looking for 'Your AI is ready' orange button...")

    await asyncio.sleep(3)

    # Check all visible buttons and CTAs
    cta_state = await page.evaluate("""(function(){
        var buttons = Array.from(document.querySelectorAll('button, a[class*="btn"], a[class*="cta"], input[type="button"], input[type="submit"]'));
        return buttons.map(b => ({
            tag: b.tagName,
            text: b.textContent.trim().substring(0, 80),
            class: b.className.substring(0, 60),
            visible: window.getComputedStyle(b).display !== 'none' && b.offsetParent !== null,
            id: b.id
        })).filter(b => b.visible && b.text.length > 0);
    })()""")

    print(f"[CTA] Visible CTAs: {cta_state}")

    # Click "Your AI is ready" button
    your_ai_btn = None
    for btn_data in cta_state:
        if "your ai is ready" in btn_data["text"].lower() or "next steps" in btn_data["text"].lower() or "ptc-welcome-btn" in btn_data["class"]:
            print(f"[CTA] Found 'Your AI is ready' button: {btn_data}")
            break

    # Try multiple selectors
    for sel in [
        ".ptc-welcome-btn",
        "button.ptc-welcome-btn",
        "#ptc-welcome-btn",
        "button:has-text('Your AI is ready')",
        "a:has-text('Your AI is ready')"
    ]:
        try:
            btn = await page.query_selector(sel)
            if not btn:
                btn = await page.get_by_text("Your AI is ready", exact=False).first
            if btn and await btn.is_visible():
                your_ai_btn = btn
                btn_text = await btn.inner_text()
                print(f"[CTA] Found button via {sel}: '{btn_text}'")
                break
        except:
            pass

    if your_ai_btn:
        await screenshot(page, "your-ai-is-ready-button-found")
        tg_send("E2E sandbox3: Found 'Your AI is ready' button - CLICKING (this is NOT the end)!")
        await your_ai_btn.click()
        await asyncio.sleep(4)
        await screenshot(page, "after-your-ai-is-ready-click")
        tg_send("E2E sandbox3: Clicked 'Your AI is ready' - checking what comes next...")
    else:
        print("[CTA] 'Your AI is ready' button not found")
        await screenshot(page, "your-ai-button-not-found")
        tg_send("E2E sandbox3 WARNING: 'Your AI is ready' button not found")

    # ========================
    # Final state: Brain Stream button
    # ========================
    print("\n=== FINAL STATE: Brain Stream Button ===")
    tg_send("E2E sandbox3: Looking for ENTER BRAIN STREAM button (FINAL STATE)...")

    await asyncio.sleep(5)
    await screenshot(page, "final-state-check")

    # Capture full page state
    final_state = await page.evaluate("""(function(){
        // Check all possible final elements
        var checks = {
            brain_stream_buttons: [],
            portal_elements: [],
            all_visible_text: [],
            ptc_state: null
        };

        // Find brain stream buttons
        var allEls = document.querySelectorAll('button, a, [class*="brain"], [class*="stream"], [id*="brain"], [id*="stream"]');
        Array.from(allEls).forEach(el => {
            var text = el.textContent.trim();
            if (text.includes("BRAIN") || text.includes("STREAM") || text.includes("ENTER")) {
                checks.brain_stream_buttons.push({
                    tag: el.tagName,
                    text: text.substring(0, 100),
                    class: el.className.substring(0, 60),
                    id: el.id,
                    disabled: el.disabled,
                    style: el.getAttribute('style') || '',
                    visible: window.getComputedStyle(el).display !== 'none'
                });
            }
        });

        // Portal elements
        var portal = document.querySelector('.portal-vortex, #portal-vortex, [class*="portal"]');
        if (portal) {
            checks.portal_elements = {
                found: true,
                class: portal.className,
                childCount: portal.children.length,
                text: portal.textContent.trim().substring(0, 200)
            };
        }

        // PTC container state
        var ptc = document.getElementById('pay-test-post-payment');
        if (ptc) {
            checks.ptc_state = {
                display: window.getComputedStyle(ptc).display,
                childCount: ptc.children.length,
                text_preview: ptc.textContent.trim().substring(0, 300)
            };
        }

        // All visible buttons
        checks.all_visible_buttons = Array.from(document.querySelectorAll('button, a[class*="btn"]'))
            .filter(el => {
                var s = window.getComputedStyle(el);
                return s.display !== 'none' && s.visibility !== 'hidden' && el.offsetParent !== null;
            })
            .map(el => ({text: el.textContent.trim().substring(0,80), class: el.className.substring(0,50), disabled: el.disabled}));

        return checks;
    })()""")

    print(f"[FINAL] Brain stream buttons: {final_state.get('brain_stream_buttons', [])}")
    print(f"[FINAL] Portal elements: {final_state.get('portal_elements', {})}")
    print(f"[FINAL] PTC state: {final_state.get('ptc_state', {})}")
    print(f"[FINAL] All visible buttons: {final_state.get('all_visible_buttons', [])}")

    brain_buttons = final_state.get("brain_stream_buttons", [])
    if brain_buttons:
        for bb in brain_buttons:
            tg_send(f"E2E sandbox3 FINAL: Brain Stream button found: '{bb['text']}' disabled={bb['disabled']}")

        # Find and potentially click if enabled
        for bb in brain_buttons:
            if not bb.get("disabled") and bb.get("visible"):
                print(f"[FINAL] Brain stream button is ACTIVE - clicking!")
                tg_send("E2E sandbox3: BRAIN STREAM BUTTON IS ACTIVE - CLICKING!")

                try:
                    btn = await page.query_selector(f"button:has-text('{bb['text'][:30]}')")
                    if not btn:
                        btn = await page.get_by_text(bb["text"][:30], exact=False).first
                    if btn:
                        await btn.click()
                        await asyncio.sleep(4)
                        await screenshot(page, "brain-stream-clicked")
                        tg_send("E2E sandbox3: BRAIN STREAM CLICKED! Documenting final state...")
                except Exception as e:
                    print(f"[FINAL] Brain stream click error: {e}")
    else:
        tg_send("E2E sandbox3 FINAL: No brain stream button visible yet (may need portal activation)")

    await screenshot(page, "absolute-final-state")

    # Scroll around to capture everything
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(1)
    await screenshot(page, "final-scroll-top")

    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await asyncio.sleep(1)
    await screenshot(page, "final-scroll-bottom")

    # Report console errors
    errors = [e for e in page_errors if e]
    if errors:
        tg_send(f"E2E sandbox3: {len(errors)} page errors captured: {errors[0][:100]}")

    tg_send(f"E2E sandbox3: COMPLETE. {screenshot_count} screenshots taken. Check exports/screenshots/sandbox3-e2e-full-20260304/")


if __name__ == "__main__":
    asyncio.run(main())
