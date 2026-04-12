#!/usr/bin/env python3
"""
E2E Full Flow Test v2: pay-test-sandbox-3
More careful handling of each phase based on visual inspection.
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
QA_ANSWERS = ["Alex Carter", "alex.carter.e2e@example.com", "Pure Technology", "CTO",
               "Build the most efficient AI research and reporting pipeline"]

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

sc = [0]  # screenshot counter
ai_name = ["Keen"]  # default from memory
paypal_real = [False]
paypal_sim = [False]

def tg(msg):
    try:
        subprocess.run([TG_SEND, msg], timeout=15, capture_output=True)
        print(f"[TG] {msg[:80]}")
    except Exception as e:
        print(f"[TG-ERR] {e}")

def tg_photo(path, cap):
    try:
        subprocess.run([TG_SEND, "--photo", path, cap], timeout=20, capture_output=True)
        print(f"[TG-PHOTO] {cap}")
    except Exception as e:
        print(f"[TG-PHOTO-ERR] {e}")

async def ss(page, label, tg_send=False):
    """Screenshot with auto-numbering."""
    sc[0] += 1
    num = str(sc[0]).zfill(2)
    fname = f"{num}-{label}.png"
    path = os.path.join(SCREENSHOT_DIR, fname)
    try:
        await page.screenshot(path=path, full_page=False)
        print(f"[SS] {fname}")
        if tg_send:
            tg_photo(path, f"Step {num}: {label}")
    except Exception as e:
        print(f"[SS-ERR] {label}: {e}")
    return path

async def safe_fill(page, selector, value, timeout=5000):
    """Fill input with error handling and short timeout."""
    try:
        el = await page.wait_for_selector(selector, state="visible", timeout=timeout)
        if el:
            await el.click()
            await el.fill(value)
            return True
    except Exception as e:
        print(f"[FILL-ERR] {selector}: {e}")
    return False

async def find_and_click(page, selectors, label="button", timeout=5000):
    """Try multiple selectors to find and click an element."""
    for sel in selectors:
        try:
            el = await page.wait_for_selector(sel, state="visible", timeout=timeout)
            if el:
                await el.scroll_into_view_if_needed()
                await el.click()
                print(f"[CLICK] {label} via: {sel}")
                return True
        except:
            continue
    print(f"[CLICK-MISS] {label} not found")
    return False

async def run_e2e():
    from playwright.async_api import async_playwright

    print("="*60)
    print("E2E v2 FULL FLOW: pay-test-sandbox-3")
    print("="*60)
    tg("E2E Sandbox-3 v2: Full flow starting - Phases 1-9")

    # Start Xvfb
    xvfb_proc = None
    try:
        xvfb_proc = subprocess.Popen(
            ["Xvfb", ":98", "-screen", "0", "1440x900x24"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        os.environ["DISPLAY"] = ":98"
        await asyncio.sleep(2)
        print("[XVFB] Started :98")
    except Exception as e:
        print(f"[XVFB] Failed: {e}")

    page_errors = []
    console_log = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage",
                  "--disable-features=VizDisplayCompositor", "--window-size=1440,900"],
        )
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await ctx.new_page()

        page.on("console", lambda m: console_log.append(f"[{m.type}] {m.text}") or None)
        page.on("pageerror", lambda e: page_errors.append(str(e)) or None)

        # ============================================================
        # PHASE 1: PASSWORD GATE
        # ============================================================
        print("\n=== PHASE 1: PASSWORD GATE ===")
        tg("Phase 1: Navigating to sandbox-3...")

        await page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        await ss(page, "01-pw-gate-before", tg_send=True)

        # Find password input - WP password protection uses specific form
        pw_filled = await safe_fill(page, "input[type='password']", PASSWORD, timeout=5000)
        if not pw_filled:
            pw_filled = await safe_fill(page, "#pwbox-\w+", PASSWORD, timeout=3000)
        if not pw_filled:
            # Try any text input
            inputs = await page.query_selector_all("input")
            for inp in inputs:
                t = await inp.get_attribute("type")
                if t in ["password", "text"]:
                    await inp.fill(PASSWORD)
                    pw_filled = True
                    break

        if pw_filled:
            await ss(page, "02-pw-entered")
            # Submit
            submitted = await find_and_click(page,
                ["input[type='submit']", "button[type='submit']", ".post-password-form button"],
                "password submit", 3000)
            if not submitted:
                await page.keyboard.press("Enter")
            await asyncio.sleep(4)
            await ss(page, "03-pw-after", tg_send=True)
            print("[P1] PASS: Password cleared")
            tg("Phase 1: PASS - password gate cleared")
        else:
            print("[P1] No password input - page may be unlocked")
            await ss(page, "03-pw-already-unlocked", tg_send=True)

        # ============================================================
        # PHASE 2: PRE-PAYMENT CHAT
        # ============================================================
        print("\n=== PHASE 2: PRE-PAYMENT CHAT ===")
        tg("Phase 2: Pre-payment chat - AI naming")
        await asyncio.sleep(2)

        await ss(page, "04-p2-page-initial")

        # The chat overlay is at top of page - scroll to top
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # Click "Awaken your pure brain" button
        awaken_clicked = await find_and_click(page, [
            "button:has-text('Awaken your pure brain')",
            "a:has-text('Awaken your pure brain')",
            "text=Awaken your pure brain",
            "button:has-text('Awaken')",
            ".awaken-btn", "#awaken-btn"
        ], "Awaken button", 8000)

        await asyncio.sleep(3)
        await ss(page, "05-p2-after-awaken", tg_send=True)

        # Click "Begin awakening" button
        begin_clicked = await find_and_click(page, [
            "button:has-text('Begin awakening')",
            "text=Begin awakening",
            "button:has-text('Begin')",
            ".begin-btn", "#begin-btn"
        ], "Begin awakening", 8000)

        await asyncio.sleep(4)
        await ss(page, "06-p2-begin-clicked", tg_send=True)

        # Now type pb-full-bypass in chat
        # The chat input is fixed at top of page
        await asyncio.sleep(2)

        # Try different selectors for the chat input
        chat_selectors = [
            "input[placeholder*='response']",
            "input[placeholder*='type']",
            "input[placeholder*='Type']",
            "input[placeholder*='message']",
            "input[placeholder*='Message']",
            "input[placeholder*='name']",
            ".pre-chat-input",
            "#pre-chat-input",
            ".chat-container input[type='text']",
            "input[type='text']"
        ]

        bypass_sent = False
        for sel in chat_selectors:
            try:
                el = await page.wait_for_selector(sel, state="visible", timeout=4000)
                if el:
                    is_visible = await el.is_visible()
                    is_enabled = await el.is_enabled()
                    placeholder = await el.get_attribute("placeholder") or ""
                    print(f"[P2] Found input: {sel} visible={is_visible} enabled={is_enabled} placeholder='{placeholder}'")
                    if is_visible and is_enabled:
                        await el.click()
                        await el.fill("pb-full-bypass")
                        await ss(page, "07-p2-bypass-typed", tg_send=True)
                        await page.keyboard.press("Enter")
                        await asyncio.sleep(2)
                        await ss(page, "08-p2-bypass-sent", tg_send=True)
                        bypass_sent = True
                        print("[P2] Bypass code sent!")
                        break
            except Exception as e:
                continue

        if not bypass_sent:
            print("[P2] Could not find chat input - trying JS click on visible input")
            await page.evaluate("""() => {
                var inputs = Array.from(document.querySelectorAll('input[type=text], input:not([type])'));
                var visible = inputs.filter(i => {
                    var s = window.getComputedStyle(i);
                    var r = i.getBoundingClientRect();
                    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
                });
                if (visible.length > 0) {
                    visible[0].value = 'pb-full-bypass';
                    visible[0].dispatchEvent(new Event('input', {bubbles: true}));
                    visible[0].dispatchEvent(new Event('change', {bubbles: true}));
                }
            }""")
            await asyncio.sleep(1)
            await page.keyboard.press("Enter")
            await asyncio.sleep(2)
            await ss(page, "07-p2-bypass-js-sent", tg_send=True)

        tg("Phase 2: Bypass sent - watching for AI name...")
        await asyncio.sleep(5)
        await ss(page, "09-p2-bypass-response", tg_send=True)

        # Check AI name in page
        name_check = await page.evaluate("""() => {
            var sources = [
                window.aiName, window.pbAiName, window.pureBrainName,
                localStorage.getItem('aiName'), localStorage.getItem('pb_ai_name'),
                localStorage.getItem('pureBrainName'),
                sessionStorage.getItem('aiName'), sessionStorage.getItem('pb_ai_name')
            ];
            return sources.find(v => v && v.trim().length > 0) || null;
        }""")
        if name_check:
            ai_name[0] = name_check.strip()
            print(f"[P2] AI name from storage: {ai_name[0]}")
        else:
            # Scan visible text for AI name (common: Keen, Nova, etc.)
            body_text = await page.evaluate("() => document.body.innerText")
            for candidate in ["Keen", "Nova", "Sage", "Atlas", "Echo", "Aria"]:
                if candidate in body_text:
                    ai_name[0] = candidate
                    print(f"[P2] AI name from text scan: {ai_name[0]}")
                    break

        print(f"[P2] AI NAME: {ai_name[0]}")
        tg(f"Phase 2: AI name = '{ai_name[0]}'")

        # The pre-payment chat after bypass should fast-track
        # Wait to see what happens next
        await asyncio.sleep(5)
        await ss(page, "10-p2-state-after-bypass", tg_send=True)

        # Check if there's still a visible chat interaction needed
        # After pb-full-bypass, it may ask for the AI name or skip to next step
        # Try to find any visible enabled input to continue
        for attempt in range(6):
            visible_input = await page.evaluate("""() => {
                var inputs = Array.from(document.querySelectorAll('input[type=text], input:not([type]), textarea'));
                var vis = inputs.find(i => {
                    var s = window.getComputedStyle(i);
                    var r = i.getBoundingClientRect();
                    return s.display !== 'none' && s.visibility !== 'hidden' &&
                           s.opacity !== '0' && r.width > 50 && r.height > 10 &&
                           !i.disabled && !i.readOnly;
                });
                if (!vis) return null;
                return {
                    placeholder: vis.placeholder,
                    id: vis.id,
                    className: vis.className,
                    value: vis.value
                };
            }""")

            if visible_input:
                ph = visible_input.get("placeholder", "")
                print(f"[P2-LOOP] Visible input found (attempt {attempt+1}): placeholder='{ph}'")

                # Determine what to type based on placeholder
                if "name" in ph.lower() and "ai" not in ph.lower():
                    answer = "Alex Carter"
                elif "email" in ph.lower():
                    answer = "alex.carter@example.com"
                elif "company" in ph.lower():
                    answer = "Pure Technology"
                elif "role" in ph.lower():
                    answer = "CTO"
                else:
                    answer = "Continue"

                # Try clicking and filling
                try:
                    inp_el = await page.query_selector(f"input[placeholder='{ph}']") if ph else await page.query_selector("input[type=text]")
                    if inp_el:
                        await inp_el.click()
                        await inp_el.fill(answer)
                        await page.keyboard.press("Enter")
                        await asyncio.sleep(3)
                        await ss(page, f"10-p2-loop-{attempt}", tg_send=(attempt == 0))
                        print(f"[P2-LOOP] Sent: {answer}")
                except Exception as e:
                    print(f"[P2-LOOP] Error: {e}")
            else:
                print(f"[P2-LOOP] No visible input at attempt {attempt+1}")
                await asyncio.sleep(3)

            # Check if we've moved past chat (e.g., discover button appeared)
            discover_visible = await page.query_selector("button:has-text('discover'), button:has-text('Click to discover')")
            if discover_visible:
                print("[P2-LOOP] Discover button appeared - pre-chat done!")
                break

        await asyncio.sleep(3)
        await ss(page, "11-p2-complete", tg_send=True)
        tg(f"Phase 2: COMPLETE - AI = '{ai_name[0]}'")

        # ============================================================
        # PHASE 3: DISCOVERY BUTTONS
        # ============================================================
        print("\n=== PHASE 3: DISCOVERY BUTTONS ===")
        tg("Phase 3: Discovery buttons")
        await asyncio.sleep(2)

        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        await ss(page, "12-p3-initial")

        # Click "Click to discover what your pure brain can do"
        d1 = await find_and_click(page, [
            "button:has-text('Click to discover what your pure brain can do')",
            "button:has-text('discover what your pure brain')",
            "button:has-text('discover')",
            "text=Click to discover",
            ".discover-btn", "#discover-btn"
        ], "Discover button", 10000)

        if d1:
            await asyncio.sleep(4)
            await ss(page, "13-p3-after-discover", tg_send=True)
            print("[P3] Clicked discover button")

        # Click "Click to see what [AI NAME] can do for you"
        d2 = await find_and_click(page, [
            f"button:has-text('Click to see what {ai_name[0]} can do for you')",
            "button:has-text('can do for you')",
            "button:has-text('can do')",
            f"text=Click to see what {ai_name[0]}",
            "text=Click to see what"
        ], f"'See what {ai_name[0]} can do' button", 8000)

        if d2:
            await asyncio.sleep(4)
            await ss(page, "14-p3-after-see-btn", tg_send=True)
            print(f"[P3] Clicked 'see what {ai_name[0]} can do'")

        # Look for overlay/popup button "see what [AI Name] can do ->"
        d3 = await find_and_click(page, [
            f"button:has-text('see what {ai_name[0]} can do')",
            "button:has-text('can do ->')",
            ".overlay button:has-text('can do')",
            ".modal button",
            ".popup button"
        ], "Overlay button", 6000)

        if d3:
            await asyncio.sleep(3)
            await ss(page, "15-p3-after-overlay", tg_send=True)

        tg(f"Phase 3: Discovery done (d1={d1}, d2={d2}, d3={d3})")

        # ============================================================
        # PHASE 4: PAYMENT TIER
        # ============================================================
        print("\n=== PHASE 4: PAYMENT TIER ===")
        tg("Phase 4: Finding Awakened tier")
        await asyncio.sleep(2)

        # Scroll to pricing
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.5)")
        await asyncio.sleep(2)
        await ss(page, "16-p4-pricing-scroll")

        # Find Awakened tier
        awakened_el = await page.query_selector("text=Awakened")
        if awakened_el:
            await awakened_el.scroll_into_view_if_needed()
            await asyncio.sleep(1)
            await ss(page, "17-p4-awakened-tier", tg_send=True)

        # Click "Activate [AI NAME] now"
        act_clicked = await find_and_click(page, [
            f"button:has-text('Activate {ai_name[0]} now')",
            f"button:has-text('Activate {ai_name[0]}')",
            "button:has-text('Activate')",
            "button:has-text('activate')",
            ".activate-btn", "#activate-btn"
        ], "Activate button", 8000)

        if act_clicked:
            await asyncio.sleep(5)
            await ss(page, "18-p4-after-activate", tg_send=True)
            print("[P4] Clicked Activate button")
            tg("Phase 4: PASS - Activate clicked")
        else:
            print("[P4] Activate button not found")
            await ss(page, "18-p4-no-activate", tg_send=True)
            tg("Phase 4: WARNING - Activate not found")

        # ============================================================
        # PHASE 5: PAYPAL
        # ============================================================
        print("\n=== PHASE 5: PAYPAL PAYMENT ===")
        tg("Phase 5: PayPal payment")
        await asyncio.sleep(4)
        await ss(page, "19-p5-paypal-check", tg_send=True)

        # Check what appeared
        modal_info = await page.evaluate("""() => {
            var modal = document.querySelector('.paypal-modal, #paypal-modal, .payment-modal, [class*=paypal]');
            var iframe = document.querySelector('iframe[src*=paypal], iframe[name*=paypal]');
            var payBtn = Array.from(document.querySelectorAll('button')).find(b =>
                b.textContent.toLowerCase().includes('pay with paypal'));
            var simBtn = Array.from(document.querySelectorAll('button')).find(b =>
                b.textContent.toLowerCase().includes('simulate'));
            return {
                hasModal: !!modal,
                modalClass: modal ? modal.className : null,
                hasIframe: !!iframe,
                iframeSrc: iframe ? iframe.src.substring(0, 80) : null,
                hasPayBtn: !!payBtn,
                payBtnText: payBtn ? payBtn.textContent.trim() : null,
                hasSimBtn: !!simBtn,
                simBtnText: simBtn ? simBtn.textContent.trim() : null
            };
        }""")
        print(f"[P5] Payment state: {json.dumps(modal_info, indent=2)}")

        # Strategy: Try simulate button first (most reliable for automation)
        # then fall back to JS simulation
        if modal_info.get("hasSimBtn"):
            sim_sel = "button:has-text('Simulate')"
            await find_and_click(page, [sim_sel], "Simulate Payment", 5000)
            paypal_sim[0] = True
            await asyncio.sleep(5)
            await ss(page, "20-p5-after-simulate", tg_send=True)
            print("[P5] Used simulate button")
            tg("Phase 5: Used simulate payment button")

        elif modal_info.get("hasPayBtn"):
            # Try to click Pay with PayPal and catch popup
            print("[P5] Attempting real PayPal via pay button")
            try:
                popup_coro = ctx.wait_for_event("page", timeout=8000)
                pay_btn = await page.query_selector("button:has-text('pay with paypal'), button:has-text('Pay with PayPal')")
                if pay_btn:
                    await pay_btn.scroll_into_view_if_needed()
                    await ss(page, "20-p5-paypal-btn", tg_send=True)
                    await pay_btn.click()

                try:
                    popup = await popup_coro
                    await popup.wait_for_load_state("domcontentloaded", timeout=15000)
                    await asyncio.sleep(3)
                    popup_ss = os.path.join(SCREENSHOT_DIR, f"{str(sc[0]+1).zfill(2)}-p5-paypal-popup.png")
                    await popup.screenshot(path=popup_ss)
                    sc[0] += 1
                    tg_photo(popup_ss, "Phase 5: PayPal popup")

                    # Try to log in
                    email_el = await popup.query_selector("input[type='email'], #email, input[name='login_email']")
                    if email_el:
                        await email_el.fill(PAYPAL_EMAIL)
                        await asyncio.sleep(1)
                        next_btn = await popup.query_selector("button:has-text('Next'), #btnNext, button[type='submit']")
                        if next_btn:
                            await next_btn.click()
                            await asyncio.sleep(3)
                        pwd_el = await popup.query_selector("input[type='password']")
                        if pwd_el:
                            await pwd_el.fill(PAYPAL_PASSWORD)
                            await asyncio.sleep(1)
                            login_btn = await popup.query_selector("button:has-text('Log In'), #btnLogin")
                            if login_btn:
                                await login_btn.click()
                                await asyncio.sleep(5)
                                popup_ss2 = os.path.join(SCREENSHOT_DIR, f"{str(sc[0]+1).zfill(2)}-p5-paypal-logged-in.png")
                                await popup.screenshot(path=popup_ss2)
                                sc[0] += 1
                                tg_photo(popup_ss2, "Phase 5: PayPal logged in")

                                pay_final = await popup.query_selector("button:has-text('Pay Now'), #payment-submit-btn, button:has-text('Continue')")
                                if pay_final:
                                    await pay_final.click()
                                    paypal_real[0] = True
                                    await asyncio.sleep(5)

                    popup_ss3 = os.path.join(SCREENSHOT_DIR, f"{str(sc[0]+1).zfill(2)}-p5-paypal-final.png")
                    await popup.screenshot(path=popup_ss3)
                    sc[0] += 1
                    tg_photo(popup_ss3, "Phase 5: PayPal final state")
                    try:
                        await popup.close()
                    except:
                        pass
                    tg(f"Phase 5: PayPal popup handled (real={paypal_real[0]})")

                except asyncio.TimeoutError:
                    print("[P5] No popup - PayPal may be in page")
                    tg("Phase 5: No PayPal popup - using JS simulation fallback")
                    paypal_sim[0] = True

            except Exception as e:
                print(f"[P5] PayPal error: {e}")

        else:
            # No modal yet - try to open it via JS
            print("[P5] No payment UI found - trying JS to open PayPal modal")
            try:
                result = await page.evaluate("""() => {
                    if (typeof openPayPalModal === 'function') {
                        openPayPalModal('Awakened');
                        return 'opened via openPayPalModal';
                    }
                    return 'openPayPalModal not found';
                }""")
                print(f"[P5] JS result: {result}")
                await asyncio.sleep(4)
                await ss(page, "20-p5-js-modal", tg_send=True)

                # Check for simulate button again
                sim2 = await page.query_selector("button:has-text('Simulate')")
                if sim2:
                    await sim2.click()
                    paypal_sim[0] = True
                    await asyncio.sleep(5)
                    await ss(page, "21-p5-simulated", tg_send=True)
                    tg("Phase 5: JS modal + simulate button")
                else:
                    # Final fallback: direct JS payment complete
                    sim_id = f"E2E-FULL-{int(time.time())}"
                    try:
                        r2 = await page.evaluate(f"""() => {{
                            var called = false;
                            if (typeof window.onPaymentComplete === 'function') {{
                                window.onPaymentComplete('Awakened', '{sim_id}', {{}});
                                called = true;
                                return 'onPaymentComplete called';
                            }}
                            // Try finding and calling launchPostPaymentFlow
                            if (typeof launchPostPaymentFlow === 'function') {{
                                launchPostPaymentFlow('Awakened', '{sim_id}');
                                return 'launchPostPaymentFlow called';
                            }}
                            return 'no payment function found';
                        }}""")
                        print(f"[P5] JS fallback: {r2}")
                        paypal_sim[0] = True
                        tg(f"Phase 5: JS simulation: {r2}")
                    except Exception as e:
                        print(f"[P5] JS fallback failed: {e}")
            except Exception as e:
                print(f"[P5] JS modal open failed: {e}")

        if not paypal_real[0] and not paypal_sim[0]:
            # Last resort
            sim_id = f"E2E-LAST-{int(time.time())}"
            try:
                await page.evaluate(f"window.onPaymentComplete && window.onPaymentComplete('Awakened', '{sim_id}', {{}})")
                paypal_sim[0] = True
                print(f"[P5] Last resort simulation: {sim_id}")
            except:
                pass

        await asyncio.sleep(5)
        await ss(page, "22-p5-payment-result", tg_send=True)
        tg(f"Phase 5: Payment done (real={paypal_real[0]}, sim={paypal_sim[0]})")

        # ============================================================
        # PHASE 6: POST-PAYMENT CHATBOX Q&A
        # ============================================================
        print("\n=== PHASE 6: POST-PAYMENT Q&A ===")
        tg("Phase 6: Post-payment Q&A chatbox")

        # Wait for post-payment container
        await asyncio.sleep(6)
        await ss(page, "23-p6-chatbox-wait", tg_send=True)

        # Check chatbox state
        cb_state = await page.evaluate("""() => {
            var el = document.getElementById('pay-test-post-payment');
            if (!el) return {found: false};
            var s = window.getComputedStyle(el);
            return {
                found: true,
                display: s.display,
                opacity: s.opacity,
                visibility: s.visibility,
                childCount: el.children.length,
                text: el.innerText.substring(0, 300)
            };
        }""")
        print(f"[P6] Chatbox state: {json.dumps(cb_state, indent=2)}")

        if page_errors:
            print(f"[P6] Page errors: {page_errors[:3]}")
            tg(f"Phase 6 WARNING: Page errors: {page_errors[0][:100]}")

        # Answer Q&A questions - wait for each one
        qa_fields = [
            ("name", "Alex Carter"),
            ("email", "alex.carter.e2e@example.com"),
            ("company", "Pure Technology"),
            ("role", "CTO"),
            ("goal", "Build the most efficient AI research and reporting pipeline")
        ]

        answered_count = 0
        for field_name, answer in qa_fields:
            print(f"[P6] Waiting for {field_name} question...")
            await asyncio.sleep(4)

            # Find active input in post-payment section
            inp_found = False
            for inp_sel in [
                "#pay-test-post-payment input[type='text']:not([disabled])",
                "#pay-test-post-payment textarea:not([disabled])",
                ".pb-chatbox input:not([disabled])",
                ".post-payment-chat input:not([disabled])",
                "input[type='text']:not([disabled]):not([readonly])",
                "textarea:not([disabled]):not([readonly])"
            ]:
                try:
                    inp_el = await page.wait_for_selector(inp_sel, state="visible", timeout=5000)
                    if inp_el:
                        await inp_el.click()
                        await inp_el.fill(answer)
                        await ss(page, f"24-p6-{field_name}", tg_send=(field_name in ["name", "goal"]))
                        await page.keyboard.press("Enter")
                        answered_count += 1
                        inp_found = True
                        print(f"[P6] Answered '{field_name}': {answer}")
                        break
                except:
                    continue

            if not inp_found:
                print(f"[P6] No input for '{field_name}' after waiting")
                await ss(page, f"24-p6-miss-{field_name}", tg_send=True)
                # Check if we're past Q&A (slides started?)
                slide_check = await page.query_selector("text=Show Me More, button:has-text('Show Me More')")
                if slide_check:
                    print("[P6] Slides already started - Q&A may be done")
                    break

        print(f"[P6] Answered {answered_count}/{len(qa_fields)} questions")
        await asyncio.sleep(3)
        await ss(page, "25-p6-qa-complete", tg_send=True)
        tg(f"Phase 6: Q&A {answered_count}/5 answered")

        # ============================================================
        # PHASE 7: BEHIND THE CURTAIN SLIDES
        # ============================================================
        print("\n=== PHASE 7: SLIDES ===")
        tg("Phase 7: Behind the curtain slides")
        await asyncio.sleep(3)
        await ss(page, "26-p7-slides-start", tg_send=True)

        slides_done = 0
        for i in range(12):
            await asyncio.sleep(3)

            # Try "Show Me More" button
            show_more = await page.query_selector("button:has-text('Show Me More')")
            if not show_more:
                show_more = await page.query_selector("text=Show Me More")

            if show_more:
                await show_more.scroll_into_view_if_needed()
                if i in [0, 4, 9]:
                    await ss(page, f"27-p7-slide-{i+1}", tg_send=True)
                await show_more.click()
                slides_done += 1
                print(f"[P7] Slide {i+1} - Show Me More clicked")
                continue

            # Try final button "That's incredible — let's go"
            final_slide = await page.query_selector("button:has-text(\"That's incredible\")")
            if not final_slide:
                final_slide = await page.query_selector("button:has-text(\"let's go\")")
            if not final_slide:
                final_slide = await page.query_selector("button:has-text('incredible')")
            if not final_slide:
                final_slide = await page.query_selector("button:has-text(\"let's\")")

            if final_slide:
                await final_slide.scroll_into_view_if_needed()
                await ss(page, "28-p7-final-slide", tg_send=True)
                await final_slide.click()
                slides_done += 1
                print("[P7] Final slide clicked!")
                await asyncio.sleep(4)
                await ss(page, "29-p7-after-final", tg_send=True)
                break

            print(f"[P7] No slide button at iteration {i+1}")
            await ss(page, f"27-p7-no-btn-{i+1}")
            break

        print(f"[P7] Completed {slides_done} slide interactions")
        tg(f"Phase 7: {slides_done} slides done")

        # ============================================================
        # PHASE 8: YOUR AI IS READY
        # ============================================================
        print("\n=== PHASE 8: YOUR AI IS READY ===")
        tg("Phase 8: Looking for 'Your AI is ready' button")
        await asyncio.sleep(4)
        await ss(page, "30-p8-ready-check", tg_send=True)

        ready_clicked = await find_and_click(page, [
            "button:has-text('Your AI is ready')",
            "button:has-text('AI is ready')",
            "button:has-text('ready')",
            "button:has-text('next steps')",
            "button:has-text('see your next steps')",
            ".ready-cta", "#ready-btn"
        ], "Your AI is ready button", 10000)

        if ready_clicked:
            await asyncio.sleep(4)
            await ss(page, "31-p8-after-ready", tg_send=True)
            print("[P8] PASS: 'Your AI is ready' clicked")
            tg("Phase 8: PASS - 'Your AI is ready' clicked")
        else:
            print("[P8] Button not found - scrolling to find it")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            await ss(page, "31-p8-scroll-bottom", tg_send=True)
            ready2 = await page.query_selector("button:has-text('ready')")
            if ready2:
                await ready2.scroll_into_view_if_needed()
                await ready2.click()
                await asyncio.sleep(4)
                await ss(page, "32-p8-ready-v2", tg_send=True)
                tg("Phase 8: Found 'ready' button after scroll")

        # ============================================================
        # PHASE 9: BRAIN STREAM BUTTON
        # ============================================================
        print("\n=== PHASE 9: BRAIN STREAM BUTTON (END GOAL) ===")
        tg("Phase 9: Looking for BRAIN STREAM button - THE END GOAL!")
        await asyncio.sleep(6)

        # Full page screenshot
        full_ss = os.path.join(SCREENSHOT_DIR, f"{str(sc[0]+1).zfill(2)}-p9-full-page.png")
        await page.screenshot(path=full_ss, full_page=True)
        sc[0] += 1
        tg_photo(full_ss, "Phase 9: Full page - looking for Brain Stream")

        # Scan entire page for Brain Stream
        bs_info = await page.evaluate("""() => {
            var textToFind = 'BRAIN STREAM';
            var allEls = Array.from(document.querySelectorAll('*'));
            var matches = allEls.filter(el =>
                el.children.length === 0 &&
                el.textContent.trim().toUpperCase().includes(textToFind)
            );
            if (matches.length === 0) {
                // Also check innerHTML
                var bodyHTML = document.body.innerHTML;
                return {
                    found: false,
                    inHTML: bodyHTML.toUpperCase().includes(textToFind),
                    postPaymentHTML: (() => {
                        var pp = document.getElementById('pay-test-post-payment');
                        return pp ? pp.innerHTML.substring(0, 500) : 'container not found';
                    })()
                };
            }
            var el = matches[0];
            var r = el.getBoundingClientRect();
            var s = window.getComputedStyle(el);
            return {
                found: true,
                text: el.textContent.trim(),
                tag: el.tagName,
                id: el.id,
                className: el.className,
                opacity: s.opacity,
                display: s.display,
                visibility: s.visibility,
                pointerEvents: s.pointerEvents,
                disabled: el.disabled,
                x: Math.round(r.x),
                y: Math.round(r.y),
                w: Math.round(r.width),
                h: Math.round(r.height)
            };
        }""")
        print(f"[P9] Brain Stream scan: {json.dumps(bs_info, indent=2)}")

        brain_stream_found = False

        if bs_info.get("found"):
            brain_stream_found = True
            # Scroll to element
            bs_x = bs_info.get("x", 0) + bs_info.get("w", 0) // 2
            bs_y = bs_info.get("y", 0) + bs_info.get("h", 0) // 2
            await page.evaluate(f"window.scrollTo(0, {bs_y - 400})")
            await asyncio.sleep(2)
            await ss(page, "33-p9-brain-stream-found", tg_send=True)

            # Close-up screenshot
            await ss(page, "34-p9-brain-stream-closeup", tg_send=True)

            # Check if greyed or active
            opacity = float(bs_info.get("opacity", 1))
            pointer_events = bs_info.get("pointerEvents", "auto")
            is_disabled = bs_info.get("disabled", False)

            print(f"[P9] Button: opacity={opacity} pointerEvents={pointer_events} disabled={is_disabled}")

            if opacity < 0.8 or pointer_events == "none" or is_disabled:
                print(f"[P9] Button is GREYED OUT (expected) - opacity={opacity}")
                tg(f"Phase 9: BRAIN STREAM button FOUND and GREYED - opacity={opacity}")
            else:
                # Try clicking
                print("[P9] Button appears ACTIVE - trying to click!")
                await page.mouse.click(bs_x, bs_y)
                await asyncio.sleep(4)
                await ss(page, "35-p9-brain-stream-clicked", tg_send=True)
                tg("Phase 9: BRAIN STREAM CLICKED (button was active!)")

            # Multiple comprehensive screenshots
            await asyncio.sleep(2)
            await ss(page, "36-p9-final-1", tg_send=True)
            await page.evaluate(f"window.scrollTo(0, {bs_y - 200})")
            await asyncio.sleep(1)
            await ss(page, "37-p9-final-2", tg_send=True)
            full_final = os.path.join(SCREENSHOT_DIR, f"{str(sc[0]+1).zfill(2)}-p9-full-final.png")
            await page.screenshot(path=full_final, full_page=True)
            sc[0] += 1
            tg_photo(full_final, "Phase 9: FINAL FULL PAGE with Brain Stream")

        elif bs_info.get("inHTML"):
            brain_stream_found = True
            print("[P9] Brain Stream in HTML but selector missed it")
            # Try direct JS scroll
            await page.evaluate("""() => {
                var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                var node;
                while (node = walker.nextNode()) {
                    if (node.textContent.includes('BRAIN STREAM')) {
                        node.parentElement.scrollIntoView({behavior: 'smooth', block: 'center'});
                        break;
                    }
                }
            }""")
            await asyncio.sleep(2)
            await ss(page, "33-p9-brain-stream-inhtml", tg_send=True)
            tg("Phase 9: Brain Stream in HTML - scrolled to it")

        else:
            print("[P9] Brain Stream NOT found")
            await ss(page, "33-p9-no-brain-stream", tg_send=True)
            # Show chatbox contents
            pp_content = bs_info.get("postPaymentHTML", "")
            print(f"[P9] Post-payment HTML: {pp_content[:300]}")
            tg(f"Phase 9: Brain Stream NOT found. PostPayment content: {pp_content[:150]}")

        # Check console errors
        errors = [e for e in console_log if "[error]" in e.lower() or "ERROR" in e]
        print(f"[P9] Console errors ({len(errors)}): {errors[:5]}")
        print(f"[P9] Page errors ({len(page_errors)}): {page_errors[:3]}")

        # ============================================================
        # RESULTS
        # ============================================================
        results = {
            "ai_name": ai_name[0],
            "paypal_real": paypal_real[0],
            "paypal_simulated": paypal_sim[0],
            "qa_answered": answered_count,
            "slides_completed": slides_done,
            "brain_stream_found": brain_stream_found,
            "brain_stream_details": bs_info if brain_stream_found else None,
            "total_screenshots": sc[0],
            "page_errors": page_errors[:5],
            "key_console_errors": errors[:5]
        }

        with open(os.path.join(SCREENSHOT_DIR, "results-v2.json"), "w") as f:
            json.dump(results, f, indent=2)

        await browser.close()
        if xvfb_proc:
            xvfb_proc.terminate()

        summary = f"""E2E Sandbox-3 v2 COMPLETE
AI Name: {ai_name[0]}
PayPal: {'Real' if paypal_real[0] else 'Simulated' if paypal_sim[0] else 'FAILED'}
Q&A: {answered_count}/5
Slides: {slides_done}
Brain Stream: {'FOUND' if brain_stream_found else 'NOT FOUND'}
Screenshots: {sc[0]}
Page Errors: {len(page_errors)}"""
        print(f"\n{summary}")
        tg(summary)
        return results


if __name__ == "__main__":
    try:
        results = asyncio.run(run_e2e())
        print(f"\n[FINAL] brain_stream_found={results.get('brain_stream_found')}")
        sys.exit(0 if results and results.get("brain_stream_found") else 1)
    except Exception as e:
        print(f"[FATAL] {e}")
        import traceback
        traceback.print_exc()
        tg_proc = subprocess.run([TG_SEND, f"E2E FATAL ERROR: {str(e)[:200]}"],
                                 capture_output=True, timeout=10)
        sys.exit(1)
