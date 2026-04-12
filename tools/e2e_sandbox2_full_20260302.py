"""
E2E Full Test: purebrain.ai/pay-test-sandbox-2/
Date: 2026-03-02
Tester: browser-vision-tester

Covers:
1. Password entry
2. Chatbox / Awakening flow
3. Natural AI conversation
4. Pricing reveal
5. PayPal checkout attempt (sandbox credentials)
6. Post-payment questionnaire
7. Birth pipeline observation

Network monitoring:
- api.purebrain.ai/api/log-conversation
- api.purebrain.ai/api/log-pay-test
- api.purebrain.ai/api/verify-payment
- 89.167.19.20:8443/api/birth/start
"""

import json
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox2-e2e-20260302"
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PASSWORD = "PureBrain.ai253443$$$"
PAYPAL_EMAIL = "sb-c89tj49549583@personal.example.com"
PAYPAL_PASSWORD = "Z0+6<dS"

network_log = []
console_log = []
screenshot_count = 0


def screenshot(page, label):
    global screenshot_count
    screenshot_count += 1
    filename = f"{screenshot_count:03d}-{label}.png"
    path = os.path.join(SCREENSHOTS_DIR, filename)
    page.screenshot(path=path, full_page=False)
    print(f"[SCREENSHOT] {filename}")
    return path


def log_network(request_or_response, kind="REQUEST"):
    url = request_or_response.url if hasattr(request_or_response, 'url') else str(request_or_response)
    interesting_patterns = [
        "api.purebrain.ai",
        "log-conversation",
        "log-pay-test",
        "verify-payment",
        "birth/start",
        "89.167.19.20",
        "paypal.com",
        "sandbox.paypal.com",
    ]
    for pattern in interesting_patterns:
        if pattern in url:
            entry = {
                "kind": kind,
                "url": url,
                "time": datetime.now().isoformat(),
            }
            if hasattr(request_or_response, 'method'):
                entry["method"] = request_or_response.method
            if hasattr(request_or_response, 'status'):
                entry["status"] = request_or_response.status
            network_log.append(entry)
            print(f"[NETWORK {kind}] {url}")
            break


def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ]
        )

        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            ignore_https_errors=True,
        )

        page = context.new_page()

        # Network monitoring
        page.on("request", lambda req: log_network(req, "REQUEST"))
        page.on("response", lambda res: log_network(res, "RESPONSE"))
        page.on("requestfailed", lambda req: network_log.append({
            "kind": "FAILED",
            "url": req.url,
            "failure": req.failure,
            "time": datetime.now().isoformat()
        }))

        # Console monitoring
        page.on("console", lambda msg: console_log.append({
            "type": msg.type,
            "text": msg.text,
            "time": datetime.now().isoformat()
        }))
        page.on("pageerror", lambda err: console_log.append({
            "type": "PAGE_ERROR",
            "text": str(err),
            "time": datetime.now().isoformat()
        }))

        results = {}

        # ===========================
        # STAGE 1: Navigate to page
        # ===========================
        print("\n=== STAGE 1: Navigate to page ===")
        try:
            page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            screenshot(page, "01-page-load")
            results["stage1_navigate"] = "PASS"
            results["stage1_title"] = page.title()
            print(f"Page title: {page.title()}")

            # Check if password form is present
            pw_field = page.query_selector("input[type='password'], input[id^='pwbox-']")
            results["stage1_password_form_present"] = pw_field is not None
            print(f"Password form present: {pw_field is not None}")

        except Exception as e:
            results["stage1_navigate"] = f"FAIL: {e}"
            print(f"FAIL stage 1: {e}")
            screenshot(page, "01-error")

        # ===========================
        # STAGE 2: Enter password
        # ===========================
        print("\n=== STAGE 2: Enter password ===")
        try:
            # Try multiple password field selectors
            pw_selectors = [
                "input[id^='pwbox-']",
                "input[type='password']",
                "#pwbox-688",
                "input[name='post_password']",
            ]
            pw_field = None
            for sel in pw_selectors:
                pw_field = page.query_selector(sel)
                if pw_field:
                    print(f"Found password field with: {sel}")
                    break

            if not pw_field:
                # Maybe we're already past the password gate?
                body_text = page.inner_text("body")[:500]
                print(f"No password field. Body starts: {body_text}")
                results["stage2_password"] = "SKIP - no password field found"
            else:
                pw_field.fill(PASSWORD)
                screenshot(page, "02-password-entered")

                # Submit the password form
                submit = page.query_selector("input[type='submit'][name='Submit']") or \
                         page.query_selector("button[type='submit']") or \
                         page.query_selector("input[type='submit']")
                if submit:
                    submit.click()
                else:
                    pw_field.press("Enter")

                page.wait_for_load_state("domcontentloaded", timeout=15000)
                time.sleep(3)
                screenshot(page, "03-after-password")
                results["stage2_password"] = "PASS"
                results["stage2_url_after"] = page.url
                print(f"URL after password: {page.url}")

        except Exception as e:
            results["stage2_password"] = f"FAIL: {e}"
            print(f"FAIL stage 2: {e}")
            screenshot(page, "02-error")

        # ===========================
        # STAGE 3: Check page content / sandbox banner
        # ===========================
        print("\n=== STAGE 3: Page content check ===")
        try:
            # Check for sandbox banner
            sandbox_banner = page.query_selector(".sandbox-banner, [class*='sandbox']")
            sandbox_text = page.evaluate("() => document.body.innerText").lower()
            results["stage3_sandbox_banner"] = "sandbox" in sandbox_text
            print(f"Sandbox text in page: {'sandbox' in sandbox_text}")

            # Check for chatbox
            chat_initial = page.query_selector(".chat-initial, .chat-initial__btn, #beginBtn")
            results["stage3_chatbox_present"] = chat_initial is not None
            print(f"Chat initial element present: {chat_initial is not None}")

            # Check pricing section visibility
            pricing_visible = page.evaluate("""
                () => {
                    const p = document.querySelector('.pricing-section, #pricing, .pricing-cards');
                    if (!p) return 'not_found';
                    const style = window.getComputedStyle(p);
                    return style.display + '|' + style.visibility;
                }
            """)
            results["stage3_pricing_visibility"] = pricing_visible
            print(f"Pricing section visibility: {pricing_visible}")

            screenshot(page, "04-page-content")
            results["stage3_check"] = "PASS"

        except Exception as e:
            results["stage3_check"] = f"FAIL: {e}"
            print(f"FAIL stage 3: {e}")
            screenshot(page, "04-error")

        # ===========================
        # STAGE 4: Click Awaken button
        # ===========================
        print("\n=== STAGE 4: Click Awaken / Begin button ===")
        try:
            begin_selectors = [
                ".chat-initial__btn",
                "#beginBtn",
                "button[onclick*='begin'], button[onclick*='awaken']",
                ".begin-btn",
                "button:has-text('Awaken')",
                "button:has-text('Begin')",
                "button:has-text('AWAKEN')",
                "[class*='begin'], [class*='awaken']",
            ]

            begin_btn = None
            for sel in begin_selectors:
                try:
                    begin_btn = page.query_selector(sel)
                    if begin_btn and begin_btn.is_visible():
                        print(f"Found begin button: {sel}")
                        break
                    begin_btn = None
                except:
                    pass

            if not begin_btn:
                # Try to find by text content
                buttons = page.query_selector_all("button")
                for btn in buttons:
                    try:
                        text = btn.inner_text().strip().lower()
                        if any(kw in text for kw in ["awaken", "begin", "start", "chat"]):
                            begin_btn = btn
                            print(f"Found button by text: {text}")
                            break
                    except:
                        pass

            if begin_btn:
                begin_btn.scroll_into_view_if_needed()
                time.sleep(0.5)
                screenshot(page, "05-before-begin-click")
                begin_btn.click()
                time.sleep(3)
                screenshot(page, "06-after-begin-click")
                results["stage4_begin_click"] = "PASS"
                print("Begin button clicked successfully")
            else:
                # Maybe chat is already open?
                results["stage4_begin_click"] = "SKIP - no begin button found, may already be in chat"
                print("No begin button found - checking if chat is already visible")
                screenshot(page, "05-no-begin-btn")

        except Exception as e:
            results["stage4_begin_click"] = f"FAIL: {e}"
            print(f"FAIL stage 4: {e}")
            screenshot(page, "05-error")

        # ===========================
        # STAGE 5: Observe AI chatbox + respond naturally
        # ===========================
        print("\n=== STAGE 5: AI chatbox interaction ===")
        try:
            # Wait for AI message to appear
            ai_msg_selectors = [".message--ai", ".ai-message", "[class*='ai-msg']", ".chat-message.ai"]
            ai_msg = None
            for sel in ai_msg_selectors:
                try:
                    page.wait_for_selector(sel, timeout=15000)
                    ai_msg = page.query_selector(sel)
                    if ai_msg:
                        print(f"AI message appeared: {sel}")
                        break
                except PlaywrightTimeout:
                    pass

            if ai_msg:
                ai_text = ai_msg.inner_text()[:200]
                results["stage5_first_ai_message"] = ai_text
                print(f"First AI message: {ai_text[:100]}...")
                screenshot(page, "07-ai-first-message")
            else:
                print("No AI message found yet, checking page state...")
                screenshot(page, "07-waiting-for-ai")
                results["stage5_first_ai_message"] = "TIMEOUT - no AI message appeared"

            # Find input field and respond
            time.sleep(2)
            input_selectors = ["#userInput", ".chat-input", "input[type='text']", "textarea"]
            chat_input = None
            for sel in input_selectors:
                chat_input = page.query_selector(sel)
                if chat_input and chat_input.is_visible():
                    print(f"Found chat input: {sel}")
                    break
                chat_input = None

            if chat_input:
                # Natural response to the AI
                chat_input.click()
                chat_input.fill("Hello, I'm interested in learning more about PureBrain AI.")

                # Find submit button
                submit_selectors = ["#submitBtn", "button[type='submit']", ".send-btn", "[class*='submit']"]
                submit_btn = None
                for sel in submit_selectors:
                    submit_btn = page.query_selector(sel)
                    if submit_btn and submit_btn.is_visible():
                        break
                    submit_btn = None

                screenshot(page, "08-before-send")

                if submit_btn:
                    submit_btn.click()
                else:
                    chat_input.press("Enter")

                time.sleep(5)  # Wait for AI to respond
                screenshot(page, "09-after-first-response")
                results["stage5_interaction1"] = "PASS"
                print("First message sent")

                # Get AI response
                ai_messages = page.query_selector_all(".message--ai, .ai-message")
                if len(ai_messages) > 0:
                    last_ai = ai_messages[-1].inner_text()[:200]
                    results["stage5_ai_response1"] = last_ai
                    print(f"AI responded: {last_ai[:100]}...")

                # Second exchange - provide name
                time.sleep(2)
                chat_input = page.query_selector("#userInput") or page.query_selector(".chat-input")
                if chat_input and chat_input.is_visible():
                    chat_input.click()
                    chat_input.fill("My name is Alex and I run a marketing agency.")
                    if submit_btn and submit_btn.is_visible():
                        submit_btn.click()
                    else:
                        chat_input.press("Enter")
                    time.sleep(5)
                    screenshot(page, "10-second-exchange")
                    results["stage5_interaction2"] = "PASS"

                    # Third exchange - express interest in pricing
                    ai_messages = page.query_selector_all(".message--ai, .ai-message")
                    if len(ai_messages) > 0:
                        last_ai = ai_messages[-1].inner_text()[:200]
                        results["stage5_ai_response2"] = last_ai
                        print(f"AI second response: {last_ai[:100]}...")

                    time.sleep(2)
                    chat_input = page.query_selector("#userInput") or page.query_selector(".chat-input")
                    if chat_input and chat_input.is_visible():
                        chat_input.click()
                        chat_input.fill("I'd like to see the pricing options available.")
                        if submit_btn and submit_btn.is_visible():
                            submit_btn.click()
                        else:
                            chat_input.press("Enter")
                        time.sleep(8)  # Longer wait for pricing reveal
                        screenshot(page, "11-third-exchange")
                        results["stage5_interaction3"] = "PASS"

            else:
                results["stage5_interaction1"] = "FAIL - no chat input found"
                print("No chat input found")
                screenshot(page, "08-no-input")

        except Exception as e:
            results["stage5_chatbox"] = f"FAIL: {e}"
            print(f"FAIL stage 5: {e}")
            screenshot(page, "09-error")

        # ===========================
        # STAGE 6: Check bypass code path
        # ===========================
        print("\n=== STAGE 6: Try bypass code to reveal pricing ===")
        try:
            # Try bypass code
            chat_input = page.query_selector("#userInput") or page.query_selector(".chat-input")
            if chat_input and chat_input.is_visible():
                chat_input.click()
                chat_input.fill("pb-full-bypass")

                submit_btn = page.query_selector("#submitBtn") or page.query_selector("button[type='submit']")
                if submit_btn and submit_btn.is_visible():
                    submit_btn.click()
                else:
                    chat_input.press("Enter")

                time.sleep(5)
                screenshot(page, "12-after-bypass")

                # Check if pricing is now visible
                pricing_visible = page.evaluate("""
                    () => {
                        const p = document.querySelector('.pricing-section, #pricing, .pricing-cards');
                        if (!p) return 'not_found';
                        const style = window.getComputedStyle(p);
                        return style.display + '|' + style.visibility;
                    }
                """)
                results["stage6_pricing_after_bypass"] = pricing_visible
                print(f"Pricing visibility after bypass: {pricing_visible}")

                # Scroll to pricing
                page.evaluate("() => { const p = document.querySelector('.pricing-section, #pricing, .pricing-cards'); if (p) p.scrollIntoView({behavior: 'smooth'}); }")
                time.sleep(2)
                screenshot(page, "13-pricing-section")
                results["stage6_bypass"] = "PASS"

            else:
                results["stage6_bypass"] = "SKIP - no chat input"

        except Exception as e:
            results["stage6_bypass"] = f"FAIL: {e}"
            print(f"FAIL stage 6: {e}")
            screenshot(page, "12-error")

        # ===========================
        # STAGE 7: PayPal checkout attempt
        # ===========================
        print("\n=== STAGE 7: Attempt PayPal checkout ===")
        try:
            # Look for pricing buttons
            pricing_btn_selectors = [
                ".pricing-card button",
                ".pricing-btn",
                "button[onclick*='Waitlist'], button[onclick*='waitlist']",
                "button[onclick*='PayPal'], button[onclick*='paypal']",
                "button[onclick*='openWaitlistModal']",
                "button[onclick*='openPayPalModal']",
            ]

            pricing_btn = None
            for sel in pricing_btn_selectors:
                try:
                    btns = page.query_selector_all(sel)
                    for btn in btns:
                        if btn.is_visible():
                            pricing_btn = btn
                            print(f"Found pricing button: {sel} - text: {btn.inner_text()[:50]}")
                            break
                    if pricing_btn:
                        break
                except:
                    pass

            if pricing_btn:
                # Get all pricing button details
                all_pricing_btns = []
                for sel in pricing_btn_selectors[:3]:
                    try:
                        btns = page.query_selector_all(sel)
                        for btn in btns:
                            try:
                                onclick = page.evaluate("(el) => el.getAttribute('onclick')", btn)
                                text = btn.inner_text()[:50]
                                all_pricing_btns.append({"text": text, "onclick": onclick})
                            except:
                                pass
                    except:
                        pass
                results["stage7_pricing_buttons"] = all_pricing_btns
                print(f"All pricing buttons: {json.dumps(all_pricing_btns, indent=2)}")

                screenshot(page, "14-before-paypal-click")
                pricing_btn.click()
                time.sleep(3)
                screenshot(page, "15-after-pricing-click")

                # Check if modal appeared
                modal_visible = page.evaluate("""
                    () => {
                        const modals = document.querySelectorAll('.modal, [class*="modal"], [id*="modal"], [class*="paypal"]');
                        return Array.from(modals).filter(m => {
                            const s = window.getComputedStyle(m);
                            return s.display !== 'none' && s.visibility !== 'hidden' && m.offsetHeight > 0;
                        }).map(m => m.className + '|' + m.id);
                    }
                """)
                results["stage7_modal_visible"] = modal_visible
                print(f"Visible modals after click: {modal_visible}")
                results["stage7_paypal_click"] = "PASS"

            else:
                results["stage7_paypal_click"] = "SKIP - no pricing buttons visible"
                print("No pricing buttons found - pricing may not be revealed yet")
                screenshot(page, "14-no-pricing-buttons")

        except Exception as e:
            results["stage7_paypal"] = f"FAIL: {e}"
            print(f"FAIL stage 7: {e}")
            screenshot(page, "14-error")

        # ===========================
        # STAGE 8: Handle PayPal modal / iframe
        # ===========================
        print("\n=== STAGE 8: PayPal modal / sandbox login ===")
        try:
            # Check for PayPal popup or iframe
            time.sleep(2)

            # Check for new page (popup)
            all_pages = context.pages
            print(f"Total pages open: {len(all_pages)}")
            results["stage8_pages_open"] = len(all_pages)

            if len(all_pages) > 1:
                # PayPal opened in a new tab/popup
                paypal_page = all_pages[-1]
                paypal_url = paypal_page.url
                results["stage8_paypal_url"] = paypal_url
                print(f"PayPal page URL: {paypal_url}")
                time.sleep(3)
                paypal_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "016-paypal-page.png"))
                print("[SCREENSHOT] 016-paypal-page.png")

                # Try to find email field in PayPal
                try:
                    email_field = paypal_page.wait_for_selector("#email, input[type='email']", timeout=10000)
                    if email_field:
                        email_field.fill(PAYPAL_EMAIL)
                        time.sleep(1)
                        paypal_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "017-paypal-email-entered.png"))

                        # Click Next
                        next_btn = paypal_page.query_selector("button#btnNext, button[type='submit']")
                        if next_btn:
                            next_btn.click()
                            time.sleep(3)
                            paypal_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "018-paypal-after-next.png"))

                            # Try password field
                            pw_field = paypal_page.query_selector("input[type='password'], #password")
                            if pw_field:
                                pw_field.fill(PAYPAL_PASSWORD)
                                time.sleep(1)
                                paypal_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "019-paypal-pw-entered.png"))

                                login_btn = paypal_page.query_selector("button#btnLogin, button[type='submit']")
                                if login_btn:
                                    login_btn.click()
                                    time.sleep(5)
                                    paypal_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "020-paypal-post-login.png"))
                                    results["stage8_paypal_login"] = "ATTEMPTED"
                                    print("PayPal sandbox login attempted")

                except PlaywrightTimeout:
                    print("No email field found on PayPal page")
                    results["stage8_paypal_login"] = "SKIP - no email field"

            else:
                # PayPal modal in same page
                paypal_iframe = page.query_selector("iframe[src*='paypal']")
                if paypal_iframe:
                    results["stage8_paypal_type"] = "iframe"
                    print("PayPal loaded in iframe")
                    screenshot(page, "16-paypal-iframe")
                else:
                    # Check for form-based fallback
                    paypal_form = page.query_selector("form[action*='paypal'], form[action*='webscr']")
                    if paypal_form:
                        results["stage8_paypal_type"] = "form_fallback"
                        action = page.evaluate("(f) => f.action", paypal_form)
                        print(f"PayPal form fallback found: {action}")
                        screenshot(page, "16-paypal-form")
                    else:
                        # Look for PayPal elements on page
                        paypal_elements = page.evaluate("""
                            () => {
                                const all = document.querySelectorAll('[class*="paypal"], [id*="paypal"]');
                                return Array.from(all).map(e => e.tagName + '.' + e.className + '#' + e.id).slice(0, 10);
                            }
                        """)
                        results["stage8_paypal_elements"] = paypal_elements
                        print(f"PayPal elements found: {paypal_elements}")
                        screenshot(page, "16-modal-state")

            results["stage8_paypal_modal"] = "COMPLETED"

        except Exception as e:
            results["stage8_paypal"] = f"FAIL: {e}"
            print(f"FAIL stage 8: {e}")
            screenshot(page, "16-error")

        # ===========================
        # STAGE 9: Post-payment flow check
        # ===========================
        print("\n=== STAGE 9: Post-payment flow / questionnaire ===")
        try:
            # Go back to main page and check state
            time.sleep(2)
            screenshot(page, "17-post-payment-check")

            # Check for questionnaire elements
            questionnaire_elements = page.evaluate("""
                () => {
                    const keywords = ['name', 'email', 'company', 'role', 'goal', 'questionnaire'];
                    const inputs = document.querySelectorAll('input, textarea, select');
                    const found = Array.from(inputs).filter(i => {
                        const attr = (i.placeholder + i.name + i.id + i.className).toLowerCase();
                        return keywords.some(kw => attr.includes(kw));
                    }).map(i => ({type: i.type, placeholder: i.placeholder, name: i.name, id: i.id}));
                    return found;
                }
            """)
            results["stage9_questionnaire_elements"] = questionnaire_elements
            print(f"Questionnaire elements: {questionnaire_elements}")

            # Check for birth pipeline indicators
            page_text = page.evaluate("() => document.body.innerText").lower()
            birth_indicators = [
                "linking intelligence",
                "birth",
                "initializing",
                "connecting",
                "your ai",
                "questionnaire",
            ]
            birth_found = [ind for ind in birth_indicators if ind in page_text]
            results["stage9_birth_indicators"] = birth_found
            print(f"Birth pipeline indicators found: {birth_found}")

            results["stage9_check"] = "PASS"

        except Exception as e:
            results["stage9_check"] = f"FAIL: {e}"
            print(f"FAIL stage 9: {e}")

        # ===========================
        # STAGE 10: Network call summary
        # ===========================
        print("\n=== STAGE 10: Network analysis ===")

        # Categorize network calls
        api_calls = {
            "log_conversation": [],
            "log_pay_test": [],
            "verify_payment": [],
            "birth_start": [],
            "paypal_sdk": [],
            "other_interesting": [],
        }

        for entry in network_log:
            url = entry.get("url", "")
            if "log-conversation" in url:
                api_calls["log_conversation"].append(entry)
            elif "log-pay-test" in url:
                api_calls["log_pay_test"].append(entry)
            elif "verify-payment" in url:
                api_calls["verify_payment"].append(entry)
            elif "birth/start" in url or "89.167.19.20" in url:
                api_calls["birth_start"].append(entry)
            elif "paypal" in url.lower() and "sdk" in url.lower():
                api_calls["paypal_sdk"].append(entry)
            else:
                api_calls["other_interesting"].append(entry)

        results["network_calls"] = api_calls
        print(f"API calls summary:")
        for key, calls in api_calls.items():
            print(f"  {key}: {len(calls)} calls")

        # Console errors
        errors = [c for c in console_log if c["type"] in ["error", "PAGE_ERROR"]]
        warnings = [c for c in console_log if c["type"] == "warning"]
        results["console_errors"] = errors
        results["console_warnings_count"] = len(warnings)
        results["console_errors_count"] = len(errors)
        print(f"Console: {len(errors)} errors, {len(warnings)} warnings")

        # Final screenshots
        screenshot(page, "18-final-state")

        # Scroll through whole page
        page.evaluate("() => window.scrollTo(0, 0)")
        time.sleep(1)
        screenshot(page, "19-top-of-page")
        page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        screenshot(page, "20-bottom-of-page")

        browser.close()

    # Save full results
    results_path = os.path.join(SCREENSHOTS_DIR, "e2e-results.json")
    with open(results_path, "w") as f:
        json.dump({
            "test_date": "2026-03-02",
            "url": PAGE_URL,
            "results": results,
            "network_log_full": network_log,
            "console_log": console_log,
            "screenshot_count": screenshot_count,
        }, f, indent=2)

    print(f"\n=== TEST COMPLETE ===")
    print(f"Screenshots: {screenshot_count}")
    print(f"Results saved: {results_path}")
    print(f"Network calls captured: {len(network_log)}")
    print(f"Console entries: {len(console_log)}")

    return results, network_log, console_log


if __name__ == "__main__":
    results, network_log, console_log = run_test()

    print("\n=== FINAL RESULTS SUMMARY ===")
    for key, val in results.items():
        if key not in ["network_calls", "console_errors"]:
            print(f"  {key}: {str(val)[:100]}")
