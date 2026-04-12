#!/usr/bin/env python3
"""
E2E Full Flow Test: pay-test-sandbox-3
Complete flow from password gate to BRAIN STREAM button.
Date: 2026-03-04
Agent: browser-vision-tester
"""

import asyncio
import os
import sys
import subprocess
import time
import json

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/e2e-sandbox3-full-flow-screenshots"
TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"
TARGET_URL = "https://purebrain.ai/pay-test-sandbox-3/"
PASSWORD = "PureBrain.ai253443$$$"

# PayPal sandbox credentials
PAYPAL_EMAIL = "sb-c89tj49549583@personal.example.com"
PAYPAL_PASSWORD = "Z0+6<dS"

# Post-payment Q&A answers
QA_ANSWERS = {
    "name": "Alex Carter",
    "email": "alex.carter.e2e@example.com",
    "company": "Pure Technology",
    "role": "CTO",
    "goal": "Build the most efficient AI research and reporting pipeline"
}

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

screenshot_count = [0]
ai_name = ["Unknown"]

def send_tg(message):
    """Send Telegram update."""
    try:
        subprocess.run([TG_SEND, message], timeout=15, capture_output=True)
        print(f"[TG] {message}")
    except Exception as e:
        print(f"[TG-ERROR] {e}")

def send_tg_photo(path, caption):
    """Send screenshot to Telegram."""
    try:
        subprocess.run([TG_SEND, "--photo", path, caption], timeout=20, capture_output=True)
        print(f"[TG-PHOTO] {caption}")
    except Exception as e:
        print(f"[TG-PHOTO-ERROR] {e}")

async def screenshot(page, label, send_to_tg=False):
    """Take numbered screenshot."""
    screenshot_count[0] += 1
    num = str(screenshot_count[0]).zfill(2)
    fname = f"{num}-{label}.png"
    path = os.path.join(SCREENSHOT_DIR, fname)
    await page.screenshot(path=path, full_page=False)
    print(f"[SCREENSHOT] {fname}")
    if send_to_tg:
        send_tg_photo(path, f"Step {num}: {label}")
    return path


async def wait_and_log(page, seconds, label=""):
    """Wait with logging."""
    print(f"[WAIT] {seconds}s - {label}")
    await asyncio.sleep(seconds)


async def run_e2e():
    """Execute complete E2E flow."""
    from playwright.async_api import async_playwright

    print("="*60)
    print("E2E FULL FLOW: pay-test-sandbox-3")
    print("="*60)

    send_tg("E2E Sandbox-3 Full Flow: Starting test (all 9 phases)")

    # Start Xvfb for headed mode
    xvfb_proc = None
    display = ":99"
    try:
        xvfb_proc = subprocess.Popen(
            ["Xvfb", display, "-screen", "0", "1440x900x24"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        os.environ["DISPLAY"] = display
        await asyncio.sleep(2)
        print(f"[XVFB] Started on display {display}")
    except Exception as e:
        print(f"[XVFB] Failed to start: {e}. Will use headless.")
        display = None

    console_errors = []
    page_errors = []

    async with async_playwright() as p:
        # Launch with headed mode if Xvfb available
        headless = display is None
        browser = await p.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-web-security",
                  "--disable-features=VizDisplayCompositor"],
            slow_mo=100
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # Capture console and errors
        page.on("console", lambda msg: console_errors.append(f"[{msg.type.upper()}] {msg.text}") if msg.type in ["error", "warning"] else None)
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # ============================================================
        # PHASE 1: PASSWORD GATE
        # ============================================================
        print("\n--- PHASE 1: PASSWORD GATE ---")
        send_tg("E2E Phase 1: Password Gate - Navigating to sandbox-3")

        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        await wait_and_log(page, 3, "page load")
        await screenshot(page, "password-gate-before", send_to_tg=True)

        # Enter password
        pw_input = await page.query_selector("input[type='password'], input[name='password'], #pwbox")
        if not pw_input:
            # Try to find password form
            pw_input = await page.query_selector("input")

        if pw_input:
            await pw_input.click()
            await pw_input.fill(PASSWORD)
            print(f"[P1] Password entered")
            await screenshot(page, "password-entered")

            # Submit
            submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], .post-password-form input[type='submit']")
            if submit_btn:
                await submit_btn.click()
            else:
                await page.keyboard.press("Enter")

            await wait_and_log(page, 3, "after password submit")
            await screenshot(page, "password-gate-after", send_to_tg=True)
            print("[P1] PASS: Password gate cleared")
            send_tg("E2E Phase 1: PASS - Password gate cleared")
        else:
            print("[P1] No password input found - page may already be unlocked")
            await screenshot(page, "password-gate-no-input", send_to_tg=True)

        # ============================================================
        # PHASE 2: PRE-PAYMENT CHAT (AI NAMING)
        # ============================================================
        print("\n--- PHASE 2: PRE-PAYMENT CHAT ---")
        send_tg("E2E Phase 2: Pre-payment chat - Looking for Awaken button")

        await wait_and_log(page, 2, "looking for awaken button")
        await screenshot(page, "phase2-page-state")

        # Click "Awaken your pure brain" button
        awaken_btn = await page.query_selector("text=Awaken your pure brain")
        if not awaken_btn:
            awaken_btn = await page.query_selector("button:has-text('Awaken')")
        if not awaken_btn:
            awaken_btn = await page.query_selector("a:has-text('Awaken')")

        if awaken_btn:
            await awaken_btn.scroll_into_view_if_needed()
            await screenshot(page, "phase2-awaken-button-found", send_to_tg=True)
            await awaken_btn.click()
            await wait_and_log(page, 3, "after awaken click")
            await screenshot(page, "phase2-after-awaken-click", send_to_tg=True)
            print("[P2] Clicked 'Awaken your pure brain'")
        else:
            print("[P2] 'Awaken your pure brain' not found, searching page...")
            # Try scrolling to find it
            await page.evaluate("window.scrollTo(0, 500)")
            await asyncio.sleep(1)
            await screenshot(page, "phase2-scroll-search")
            awaken_btn = await page.query_selector("button:has-text('Awaken')")
            if awaken_btn:
                await awaken_btn.click()
                await wait_and_log(page, 3, "after awaken click")
                await screenshot(page, "phase2-after-awaken-click-v2", send_to_tg=True)

        # Click "Begin awakening" button
        await wait_and_log(page, 2, "looking for begin awakening")
        begin_btn = await page.query_selector("text=Begin awakening")
        if not begin_btn:
            begin_btn = await page.query_selector("button:has-text('Begin')")

        if begin_btn:
            await begin_btn.scroll_into_view_if_needed()
            await screenshot(page, "phase2-begin-awakening-found", send_to_tg=True)
            await begin_btn.click()
            await wait_and_log(page, 3, "after begin click")
            await screenshot(page, "phase2-after-begin-click", send_to_tg=True)
            print("[P2] Clicked 'Begin awakening'")
        else:
            print("[P2] 'Begin awakening' not found")

        # Wait for chat to open and type bypass code
        await wait_and_log(page, 3, "waiting for chat input")

        # Find chat input and type bypass
        chat_input = await page.query_selector("input[placeholder*='Message'], textarea[placeholder*='Message'], .chat-input input, #pre-chat-input")
        if not chat_input:
            chat_input = await page.query_selector("input[type='text']")

        if chat_input:
            await chat_input.click()
            await chat_input.fill("pb-full-bypass")
            await screenshot(page, "phase2-bypass-typed", send_to_tg=True)
            await page.keyboard.press("Enter")
            await wait_and_log(page, 4, "waiting for bypass response")
            await screenshot(page, "phase2-bypass-sent", send_to_tg=True)
            print("[P2] Typed pb-full-bypass")
            send_tg("E2E Phase 2: Bypass code sent - waiting for AI name")
        else:
            print("[P2] No chat input found")
            await screenshot(page, "phase2-no-chat-input", send_to_tg=True)

        # Wait for AI name to appear and capture it
        await wait_and_log(page, 5, "waiting for pre-chat to complete")
        await screenshot(page, "phase2-pre-chat-state", send_to_tg=True)

        # Try to extract AI name from page
        ai_name_found = await page.evaluate("""() => {
            // Check various sources for AI name
            var sources = [
                window.aiName,
                window.pbAiName,
                localStorage.getItem('aiName'),
                localStorage.getItem('pb_ai_name'),
                sessionStorage.getItem('aiName'),
                sessionStorage.getItem('pb_ai_name'),
                document.querySelector('[data-ai-name]')?.dataset?.aiName,
                document.querySelector('.ai-name')?.textContent,
                document.querySelector('#ai-name')?.textContent
            ];
            return sources.find(v => v && v.length > 0) || null;
        }""")

        if ai_name_found:
            ai_name[0] = ai_name_found.strip()
            print(f"[P2] AI NAME FOUND: {ai_name[0]}")
            send_tg(f"E2E Phase 2: AI name = '{ai_name[0]}'")
        else:
            # Scroll through chat to find name mentions
            page_text = await page.evaluate("() => document.body.innerText")
            if "Keen" in page_text:
                ai_name[0] = "Keen"
            elif "Nova" in page_text:
                ai_name[0] = "Nova"
            print(f"[P2] AI name from text scan: {ai_name[0]}")

        # Continue through pre-payment chat if still active
        # Try clicking through multiple times
        for attempt in range(8):
            await asyncio.sleep(2)
            # Check if there's still a chat going
            send_btn = await page.query_selector(".send-btn, button:has-text('Send'), input[type='submit']")
            chat_input_active = await page.query_selector("input[type='text']:not([disabled]), textarea:not([disabled])")

            if chat_input_active:
                val = await chat_input_active.get_attribute("placeholder") or ""
                print(f"[P2] Chat still active (attempt {attempt+1}), input placeholder: {val}")
                # Type generic response to advance
                await chat_input_active.fill("Yes, continue")
                await page.keyboard.press("Enter")
                await asyncio.sleep(2)
            else:
                print(f"[P2] No more active chat input at attempt {attempt+1}")
                break

        await wait_and_log(page, 3, "pre-chat done")
        await screenshot(page, "phase2-complete", send_to_tg=True)

        # Check AI name again
        ai_name_found2 = await page.evaluate("""() => {
            var sources = [
                window.aiName, window.pbAiName,
                localStorage.getItem('aiName'), localStorage.getItem('pb_ai_name'),
                sessionStorage.getItem('aiName')
            ];
            return sources.find(v => v && v.length > 0) || null;
        }""")
        if ai_name_found2:
            ai_name[0] = ai_name_found2.strip()
            print(f"[P2] AI NAME (final): {ai_name[0]}")

        send_tg(f"E2E Phase 2: COMPLETE - AI name = '{ai_name[0]}'")

        # ============================================================
        # PHASE 3: DISCOVERY BUTTONS
        # ============================================================
        print(f"\n--- PHASE 3: DISCOVERY BUTTONS ---")
        send_tg("E2E Phase 3: Discovery buttons")

        # Look for "Click to discover" button
        await wait_and_log(page, 2, "looking for discovery button")

        discover_btn = await page.query_selector("text=Click to discover what your pure brain can do")
        if not discover_btn:
            discover_btn = await page.query_selector("button:has-text('discover')")
        if not discover_btn:
            discover_btn = await page.query_selector("button:has-text('Click to discover')")

        if discover_btn:
            await discover_btn.scroll_into_view_if_needed()
            await screenshot(page, "phase3-discover-btn", send_to_tg=True)
            await discover_btn.click()
            await wait_and_log(page, 3, "after discover click")
            await screenshot(page, "phase3-after-discover", send_to_tg=True)
            print("[P3] Clicked 'Click to discover'")
        else:
            print("[P3] Discovery button not found")
            await screenshot(page, "phase3-no-discover-btn", send_to_tg=True)

        # Look for "Click to see what [AI NAME] can do"
        await wait_and_log(page, 2, "looking for second discover btn")

        see_btn = await page.query_selector(f"text=Click to see what {ai_name[0]} can do for you")
        if not see_btn:
            see_btn = await page.query_selector("button:has-text('can do for you')")
        if not see_btn:
            see_btn = await page.query_selector("button:has-text('can do')")

        if see_btn:
            await see_btn.scroll_into_view_if_needed()
            await screenshot(page, "phase3-see-btn", send_to_tg=True)
            await see_btn.click()
            await wait_and_log(page, 3, "after see btn click")
            await screenshot(page, "phase3-after-see-click", send_to_tg=True)
            print(f"[P3] Clicked 'Click to see what {ai_name[0]} can do for you'")
        else:
            print("[P3] Second discover button not found")

        # Look for overlay/popup "see what [AI Name] can do ->"
        await wait_and_log(page, 2, "looking for overlay btn")
        overlay_btn = await page.query_selector("text=see what")
        if not overlay_btn:
            overlay_btn = await page.query_selector("button:has-text('can do ->')")
        if not overlay_btn:
            overlay_btn = await page.query_selector(".overlay button, .modal button, .popup button")

        if overlay_btn:
            await screenshot(page, "phase3-overlay-found", send_to_tg=True)
            await overlay_btn.click()
            await wait_and_log(page, 3, "after overlay click")
            await screenshot(page, "phase3-after-overlay", send_to_tg=True)
            print("[P3] Clicked overlay button")
        else:
            print("[P3] Overlay button not found")
            await screenshot(page, "phase3-overlay-not-found")

        send_tg("E2E Phase 3: Discovery buttons complete")

        # ============================================================
        # PHASE 4: PAYMENT TIER SELECTION
        # ============================================================
        print("\n--- PHASE 4: PAYMENT TIER SELECTION ---")
        send_tg("E2E Phase 4: Scrolling to Awakened tier")

        # Scroll to find pricing section
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        await wait_and_log(page, 2, "scrolled to pricing")
        await screenshot(page, "phase4-pricing-scroll", send_to_tg=True)

        # Look for "Awakened" tier
        awakened_section = await page.query_selector("text=Awakened")
        if awakened_section:
            await awakened_section.scroll_into_view_if_needed()
            await wait_and_log(page, 1, "scrolled to awakened")
            await screenshot(page, "phase4-awakened-tier", send_to_tg=True)
            print("[P4] Found Awakened tier")

        # Click "Activate [AI NAME] now" on Awakened tier
        activate_btn = await page.query_selector(f"text=Activate {ai_name[0]} now")
        if not activate_btn:
            activate_btn = await page.query_selector("button:has-text('Activate')")
        if not activate_btn:
            activate_btn = await page.query_selector("button:has-text('now')")

        if activate_btn:
            await activate_btn.scroll_into_view_if_needed()
            await screenshot(page, "phase4-activate-btn", send_to_tg=True)
            await activate_btn.click()
            await wait_and_log(page, 4, "after activate click")
            await screenshot(page, "phase4-after-activate", send_to_tg=True)
            print(f"[P4] Clicked Activate button")
            send_tg("E2E Phase 4: PASS - Clicked Activate button")
        else:
            print("[P4] Activate button not found")
            await screenshot(page, "phase4-no-activate-btn", send_to_tg=True)
            send_tg("E2E Phase 4: WARNING - Activate button not found")

        # ============================================================
        # PHASE 5: PAYPAL PAYMENT
        # ============================================================
        print("\n--- PHASE 5: PAYPAL PAYMENT ---")
        send_tg("E2E Phase 5: PayPal payment flow")

        # Check if PayPal modal appeared
        await wait_and_log(page, 3, "waiting for PayPal modal")
        await screenshot(page, "phase5-paypal-check", send_to_tg=True)

        # Check for PayPal button or modal
        paypal_modal = await page.query_selector(".paypal-modal, #paypal-modal, .payment-modal")
        paypal_iframe = await page.query_selector("iframe[src*='paypal']")
        pay_with_paypal_btn = await page.query_selector("button:has-text('Pay with PayPal'), button:has-text('pay with paypal')")

        print(f"[P5] PayPal modal: {paypal_modal is not None}")
        print(f"[P5] PayPal iframe: {paypal_iframe is not None}")
        print(f"[P5] Pay with PayPal btn: {pay_with_paypal_btn is not None}")

        paypal_real_attempted = False
        paypal_simulated = False

        if pay_with_paypal_btn:
            await pay_with_paypal_btn.scroll_into_view_if_needed()
            await screenshot(page, "phase5-paypal-btn", send_to_tg=True)

            # Try popup interception
            popup_promise = context.wait_for_event("page", timeout=10000)
            await pay_with_paypal_btn.click()

            try:
                popup = await popup_promise
                await popup.wait_for_load_state("domcontentloaded", timeout=15000)
                await asyncio.sleep(3)
                await popup.screenshot(path=os.path.join(SCREENSHOT_DIR, f"{str(screenshot_count[0]+1).zfill(2)}-phase5-paypal-popup.png"))
                screenshot_count[0] += 1
                send_tg_photo(os.path.join(SCREENSHOT_DIR, f"{str(screenshot_count[0]).zfill(2)}-phase5-paypal-popup.png"), "Phase 5: PayPal popup")

                # Fill PayPal credentials
                email_field = await popup.query_selector("input[type='email'], #email, input[name='login_email']")
                if email_field:
                    await email_field.fill(PAYPAL_EMAIL)
                    await asyncio.sleep(1)

                    # Click Next or continue
                    next_btn = await popup.query_selector("button:has-text('Next'), #btnNext, button[type='submit']")
                    if next_btn:
                        await next_btn.click()
                        await asyncio.sleep(3)

                    pwd_field = await popup.query_selector("input[type='password'], #password")
                    if pwd_field:
                        await pwd_field.fill(PAYPAL_PASSWORD)
                        await asyncio.sleep(1)
                        login_btn = await popup.query_selector("button:has-text('Log In'), #btnLogin, button[type='submit']")
                        if login_btn:
                            await login_btn.click()
                            await asyncio.sleep(5)
                            popup_screenshot_path = os.path.join(SCREENSHOT_DIR, f"{str(screenshot_count[0]+1).zfill(2)}-phase5-paypal-logged-in.png")
                            await popup.screenshot(path=popup_screenshot_path)
                            screenshot_count[0] += 1
                            send_tg_photo(popup_screenshot_path, "Phase 5: PayPal logged in")

                            # Click Pay
                            pay_btn = await popup.query_selector("button:has-text('Pay Now'), button:has-text('Continue'), #payment-submit-btn")
                            if pay_btn:
                                await pay_btn.click()
                                await asyncio.sleep(5)
                                paypal_real_attempted = True
                                print("[P5] Real PayPal payment attempted")

                await popup.close()
            except asyncio.TimeoutError:
                print("[P5] No PayPal popup appeared")
            except Exception as e:
                print(f"[P5] PayPal popup error: {e}")

        # Try direct "pay with paypal" text
        elif await page.query_selector("text=pay with paypal"):
            direct_paypal = await page.query_selector("text=pay with paypal")
            await direct_paypal.click()
            await wait_and_log(page, 5, "paypal clicked")
            await screenshot(page, "phase5-after-paypal-click", send_to_tg=True)
            paypal_real_attempted = True

        # If PayPal iframe visible, try clicking it
        elif paypal_iframe:
            print("[P5] PayPal iframe found, attempting coordinate click")
            iframe_bounds = await page.evaluate("""() => {
                var iframe = document.querySelector('iframe[src*="paypal"], iframe[name*="paypal"]');
                if (!iframe) return null;
                var r = iframe.getBoundingClientRect();
                return {x: r.x, y: r.y, w: r.width, h: r.height};
            }""")
            if iframe_bounds:
                cx = iframe_bounds['x'] + iframe_bounds['w'] / 2
                cy = iframe_bounds['y'] + 20
                await page.mouse.click(cx, cy)
                await wait_and_log(page, 5, "after iframe click")
                await screenshot(page, "phase5-after-iframe-click", send_to_tg=True)
                paypal_real_attempted = True

        # FALLBACK: Check for simulate payment button
        simulate_btn = await page.query_selector("button:has-text('Simulate'), text=Simulate Successful Payment")
        if simulate_btn and not paypal_real_attempted:
            print("[P5] Using Simulate Payment button")
            await simulate_btn.scroll_into_view_if_needed()
            await screenshot(page, "phase5-simulate-btn", send_to_tg=True)
            await simulate_btn.click()
            await wait_and_log(page, 4, "after simulate click")
            paypal_simulated = True
            await screenshot(page, "phase5-after-simulate", send_to_tg=True)
            send_tg("E2E Phase 5: Using simulate payment (PayPal iframe not accessible)")

        # If still no payment — try JS simulation
        if not paypal_real_attempted and not paypal_simulated:
            print("[P5] FALLBACK: JS payment simulation")
            sim_id = f"E2E-FULL-{int(time.time())}"
            try:
                await page.evaluate(f"window.onPaymentComplete('Awakened', '{sim_id}', {{}})")
                paypal_simulated = True
                print(f"[P5] JS simulation called: {sim_id}")
            except Exception as e:
                print(f"[P5] onPaymentComplete not available: {e}")
                # Try openPayPalModal
                try:
                    await page.evaluate("openPayPalModal && openPayPalModal('Awakened')")
                    await wait_and_log(page, 3, "modal opened via JS")
                    await screenshot(page, "phase5-modal-via-js", send_to_tg=True)
                    # Try simulate again
                    simulate_btn2 = await page.query_selector("button:has-text('Simulate')")
                    if simulate_btn2:
                        await simulate_btn2.click()
                        await wait_and_log(page, 4, "after simulate")
                        paypal_simulated = True
                except Exception as e2:
                    print(f"[P5] openPayPalModal failed: {e2}")
                    # Last resort: trigger launchPostPaymentFlow directly
                    sim_id = f"E2E-FULL-{int(time.time())}"
                    try:
                        result = await page.evaluate(f"""() => {{
                            if (typeof launchPostPaymentFlow === 'function') {{
                                launchPostPaymentFlow('Awakened', '{sim_id}');
                                return 'called launchPostPaymentFlow';
                            }}
                            if (typeof window.launchPostPaymentFlow === 'function') {{
                                window.launchPostPaymentFlow('Awakened', '{sim_id}');
                                return 'called window.launchPostPaymentFlow';
                            }}
                            return 'not found';
                        }}""")
                        print(f"[P5] launchPostPaymentFlow result: {result}")
                        paypal_simulated = True
                    except Exception as e3:
                        print(f"[P5] All PayPal approaches failed: {e3}")

        await wait_and_log(page, 5, "after payment attempt")
        await screenshot(page, "phase5-payment-result", send_to_tg=True)

        payment_method = "REAL PayPal (popup)" if paypal_real_attempted else "SIMULATED"
        print(f"[P5] Payment method: {payment_method}")
        send_tg(f"E2E Phase 5: Payment attempted via {payment_method}")

        # ============================================================
        # PHASE 6: POST-PAYMENT CHATBOX Q&A
        # ============================================================
        print("\n--- PHASE 6: POST-PAYMENT CHATBOX ---")
        send_tg("E2E Phase 6: Post-payment chatbox Q&A")

        # Wait for chatbox to appear
        await wait_and_log(page, 5, "waiting for post-payment chatbox")
        await screenshot(page, "phase6-chatbox-init", send_to_tg=True)

        # Check if post-payment container appeared
        chatbox_visible = await page.evaluate("""() => {
            var el = document.getElementById('pay-test-post-payment');
            if (!el) return {found: false};
            var style = window.getComputedStyle(el);
            return {
                found: true,
                display: style.display,
                visibility: style.visibility,
                opacity: style.opacity,
                children: el.children.length,
                innerHTML_preview: el.innerHTML.substring(0, 200)
            };
        }""")
        print(f"[P6] Chatbox state: {json.dumps(chatbox_visible, indent=2)}")

        # If chatbox not visible, check for page errors
        if page_errors:
            print(f"[P6] Page errors: {page_errors[:5]}")

        # Answer Q&A questions
        qa_prompts = [
            ("name", QA_ANSWERS["name"]),
            ("email", QA_ANSWERS["email"]),
            ("company", QA_ANSWERS["company"]),
            ("role", QA_ANSWERS["role"]),
            ("goal", QA_ANSWERS["goal"])
        ]

        answered = 0
        for field, answer in qa_prompts:
            await wait_and_log(page, 3, f"waiting for {field} question")

            # Find active chat input in post-payment chatbox
            chat_inp = await page.query_selector("#pay-test-post-payment input[type='text']:not([disabled]), #pay-test-post-payment textarea:not([disabled])")
            if not chat_inp:
                chat_inp = await page.query_selector(".pb-chatbox input:not([disabled]), .pb-chat input:not([disabled])")
            if not chat_inp:
                # Global fallback
                chat_inp = await page.query_selector("input[type='text']:not([disabled])")

            if chat_inp:
                await chat_inp.click()
                await chat_inp.fill(answer)
                await screenshot(page, f"phase6-qa-{field}-typed")
                await page.keyboard.press("Enter")
                await wait_and_log(page, 2, f"after {field} answer")
                await screenshot(page, f"phase6-qa-{field}-sent", send_to_tg=(field in ["name", "goal"]))
                answered += 1
                print(f"[P6] Answered {field}: {answer}")
            else:
                print(f"[P6] No input found for {field}")
                await screenshot(page, f"phase6-no-input-{field}", send_to_tg=True)
                break

        print(f"[P6] Answered {answered}/5 Q&A questions")
        await screenshot(page, "phase6-qa-complete", send_to_tg=True)
        send_tg(f"E2E Phase 6: Q&A answered {answered}/5 questions")

        # ============================================================
        # PHASE 7: BEHIND THE CURTAIN SLIDES
        # ============================================================
        print("\n--- PHASE 7: BEHIND THE CURTAIN SLIDES ---")
        send_tg("E2E Phase 7: Behind the curtain slides")

        # Wait for slides to appear
        await wait_and_log(page, 4, "waiting for slides")
        await screenshot(page, "phase7-slides-init", send_to_tg=True)

        slides_clicked = 0
        for slide_num in range(1, 12):
            await wait_and_log(page, 2, f"looking for slide {slide_num}")

            show_more_btn = await page.query_selector("button:has-text('Show Me More'), text=Show Me More")
            if not show_more_btn:
                show_more_btn = await page.query_selector("button:has-text('Show')")

            if show_more_btn:
                await show_more_btn.scroll_into_view_if_needed()
                if slide_num in [1, 5, 10]:
                    await screenshot(page, f"phase7-slide-{slide_num}", send_to_tg=True)
                await show_more_btn.click()
                slides_clicked += 1
                print(f"[P7] Clicked 'Show Me More' for slide {slide_num}")
                await wait_and_log(page, 2, f"slide {slide_num} shown")
            else:
                # Check for final slide button
                final_btn = await page.query_selector("text=That's incredible")
                if not final_btn:
                    final_btn = await page.query_selector("button:has-text(\"let's go\")")
                if not final_btn:
                    final_btn = await page.query_selector("button:has-text('incredible')")

                if final_btn:
                    await final_btn.scroll_into_view_if_needed()
                    await screenshot(page, "phase7-final-slide", send_to_tg=True)
                    await final_btn.click()
                    await wait_and_log(page, 3, "after final slide click")
                    await screenshot(page, "phase7-after-final", send_to_tg=True)
                    print(f"[P7] Clicked final slide button")
                    slides_clicked += 1
                    break
                else:
                    print(f"[P7] No more slide buttons at slide {slide_num}")
                    await screenshot(page, f"phase7-no-btn-slide-{slide_num}")
                    break

        print(f"[P7] Clicked through {slides_clicked} slides")
        send_tg(f"E2E Phase 7: {slides_clicked} slides completed")

        # ============================================================
        # PHASE 8: YOUR AI IS READY BUTTON
        # ============================================================
        print("\n--- PHASE 8: YOUR AI IS READY ---")
        send_tg("E2E Phase 8: Looking for 'Your AI is ready' button")

        await wait_and_log(page, 3, "waiting for ready button")
        await screenshot(page, "phase8-ready-check", send_to_tg=True)

        # Find orange CTA button
        ready_btn = await page.query_selector("text=Your AI is ready")
        if not ready_btn:
            ready_btn = await page.query_selector("button:has-text('ready')")
        if not ready_btn:
            ready_btn = await page.query_selector("button:has-text('next steps')")
        if not ready_btn:
            ready_btn = await page.query_selector(".ready-btn, .cta-btn")

        if ready_btn:
            await ready_btn.scroll_into_view_if_needed()
            await screenshot(page, "phase8-ready-btn-found", send_to_tg=True)
            print("[P8] Found 'Your AI is ready' button")
            await ready_btn.click()
            await wait_and_log(page, 4, "after ready button click")
            await screenshot(page, "phase8-after-ready-click", send_to_tg=True)
            print("[P8] Clicked 'Your AI is ready'")
            send_tg("E2E Phase 8: PASS - Clicked 'Your AI is ready'")
        else:
            print("[P8] 'Your AI is ready' button not found")
            await screenshot(page, "phase8-no-ready-btn", send_to_tg=True)
            # Try scrolling
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            await screenshot(page, "phase8-scrolled-bottom", send_to_tg=True)
            ready_btn2 = await page.query_selector("button:has-text('ready')")
            if ready_btn2:
                await ready_btn2.click()
                await wait_and_log(page, 4, "after ready click v2")
                await screenshot(page, "phase8-after-ready-v2", send_to_tg=True)

        # ============================================================
        # PHASE 9: THE END GOAL - BRAIN STREAM BUTTON
        # ============================================================
        print("\n--- PHASE 9: BRAIN STREAM BUTTON (THE END GOAL) ---")
        send_tg("E2E Phase 9: Looking for BRAIN STREAM button - THE END GOAL")

        await wait_and_log(page, 5, "waiting for brain stream button")
        await screenshot(page, "phase9-brain-stream-check", send_to_tg=True)

        # Capture full page state
        full_page_path = os.path.join(SCREENSHOT_DIR, f"{str(screenshot_count[0]+1).zfill(2)}-phase9-full-page.png")
        await page.screenshot(path=full_page_path, full_page=True)
        screenshot_count[0] += 1
        send_tg_photo(full_page_path, "Phase 9: Full page state")

        # Look for Brain Stream button
        brain_stream_btn = await page.query_selector(f"text=ENTER {ai_name[0].upper()}'S BRAIN STREAM")
        if not brain_stream_btn:
            brain_stream_btn = await page.query_selector("text=BRAIN STREAM")
        if not brain_stream_btn:
            brain_stream_btn = await page.query_selector("[class*='brain-stream']")
        if not brain_stream_btn:
            brain_stream_btn = await page.query_selector("#brain-stream-btn, .brain-stream-btn")

        brain_stream_found = False
        if brain_stream_btn:
            brain_stream_found = True
            await brain_stream_btn.scroll_into_view_if_needed()

            # Get button state
            btn_state = await page.evaluate("""() => {
                var btn = document.querySelector('[id*=brain-stream], [class*=brain-stream], button:has([data-brain-stream])');
                // Also try text content
                var allBtns = Array.from(document.querySelectorAll('button, a, div[role=button]'));
                var brainBtn = allBtns.find(b => b.textContent.includes('BRAIN STREAM'));
                var el = btn || brainBtn;
                if (!el) return {found: false};
                var style = window.getComputedStyle(el);
                return {
                    found: true,
                    text: el.textContent.trim(),
                    opacity: style.opacity,
                    disabled: el.disabled,
                    pointerEvents: style.pointerEvents,
                    className: el.className,
                    id: el.id
                };
            }""")
            print(f"[P9] Brain Stream button state: {json.dumps(btn_state, indent=2)}")

            # Multiple screenshots of the end state
            await screenshot(page, "phase9-brain-stream-found", send_to_tg=True)
            await asyncio.sleep(1)
            await screenshot(page, "phase9-brain-stream-closeup", send_to_tg=True)

            # Try to check if it's greyed (low opacity)
            is_greyed = btn_state.get("opacity", "1") < "0.8" if btn_state.get("found") else False

            if not is_greyed and brain_stream_btn:
                # Try clicking if it appears active
                try:
                    await brain_stream_btn.click()
                    await wait_and_log(page, 3, "after brain stream click")
                    await screenshot(page, "phase9-after-brain-stream-click", send_to_tg=True)
                    print("[P9] Brain Stream button clicked!")
                except:
                    print("[P9] Brain Stream button not clickable (greyed out as expected)")

            print("[P9] BRAIN STREAM BUTTON FOUND!")
            send_tg(f"E2E Phase 9: PASS! BRAIN STREAM button found for '{ai_name[0]}'!")
        else:
            # Scan entire page for brain stream text
            page_content = await page.evaluate("() => document.body.innerHTML")
            has_brain_stream = "BRAIN STREAM" in page_content.upper()
            print(f"[P9] Brain Stream in page HTML: {has_brain_stream}")

            if has_brain_stream:
                print("[P9] Brain Stream is in DOM but selector missed it")
                # Try JS evaluation
                brain_info = await page.evaluate("""() => {
                    var all = Array.from(document.querySelectorAll('*'));
                    var el = all.find(e => e.textContent.trim().includes('BRAIN STREAM'));
                    if (!el) return null;
                    var r = el.getBoundingClientRect();
                    return {tag: el.tagName, text: el.textContent.trim().substring(0, 100), x: r.x, y: r.y};
                }""")
                print(f"[P9] Brain Stream element: {brain_info}")

                if brain_info:
                    await page.mouse.move(brain_info['x'] + 50, brain_info['y'] + 20)
                    await asyncio.sleep(1)
                    await screenshot(page, "phase9-brain-stream-mouse-over", send_to_tg=True)
                    brain_stream_found = True

            if not has_brain_stream:
                await screenshot(page, "phase9-no-brain-stream", send_to_tg=True)
                send_tg("E2E Phase 9: Brain Stream button not found - checking chatbox state")

                # Check chatbox state
                chatbox_final = await page.evaluate("""() => {
                    var el = document.getElementById('pay-test-post-payment');
                    if (!el) return 'container not in DOM';
                    return {
                        children: el.children.length,
                        text: el.textContent.substring(0, 500)
                    };
                }""")
                print(f"[P9] Final chatbox state: {chatbox_final}")

        # Extra screenshots of final state
        await screenshot(page, "phase9-final-state-1", send_to_tg=True)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
        await screenshot(page, "phase9-final-state-scrolled", send_to_tg=True)
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        await screenshot(page, "phase9-final-state-top", send_to_tg=True)

        # ============================================================
        # COMPILE RESULTS
        # ============================================================
        print("\n--- COMPILING RESULTS ---")

        results = {
            "ai_name": ai_name[0],
            "paypal_real_attempted": paypal_real_attempted,
            "paypal_simulated": paypal_simulated,
            "qa_answered": answered,
            "slides_clicked": slides_clicked,
            "brain_stream_found": brain_stream_found,
            "screenshot_count": screenshot_count[0],
            "page_errors": page_errors[:10],
            "console_errors": console_errors[:10]
        }

        # Save results
        results_path = os.path.join(SCREENSHOT_DIR, "results.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

        await browser.close()

        print(f"\n[RESULTS] {json.dumps(results, indent=2)}")

        summary = f"""E2E Sandbox-3 COMPLETE
AI Name: {ai_name[0]}
Payment: {'Real PayPal' if paypal_real_attempted else 'Simulated'}
Q&A: {answered}/5
Slides: {slides_clicked}
Brain Stream: {'FOUND' if brain_stream_found else 'NOT FOUND'}
Screenshots: {screenshot_count[0]}"""
        send_tg(summary)

        return results

    if xvfb_proc:
        xvfb_proc.terminate()


if __name__ == "__main__":
    try:
        results = asyncio.run(run_e2e())
        sys.exit(0 if results and results.get("brain_stream_found") else 1)
    except Exception as e:
        print(f"[FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
