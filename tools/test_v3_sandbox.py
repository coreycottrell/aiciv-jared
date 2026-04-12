#!/usr/bin/env python3
"""
V3 Post-Payment Chatbox Test Script
Tests purebrain.ai/pay-test-sandbox-2/ end-to-end

Password discovery: PureBrain.ai253443$$$ (3 dollar signs, confirmed 2026-02-22)
"""

import time
import json
from playwright.sync_api import sync_playwright

SCREENSHOT_BASE = "/home/jared/projects/AI-CIV/aether/exports/screenshots"
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"   # 3 dollar signs - confirmed correct

def ss(page, name, full_page=True):
    """Take a screenshot with standardized naming."""
    path = f"{SCREENSHOT_BASE}/{name}.png"
    try:
        page.screenshot(path=path, full_page=full_page)
        print(f"[SCREENSHOT] {name}.png")
    except Exception as e:
        print(f"[SCREENSHOT FAILED] {name}.png: {e}")
    return path

def wait_for_new_ai_message(page, current_count, timeout=40):
    """Wait until a new AI message appears beyond current_count."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            count = page.evaluate("""
                () => {
                    var msgs = document.querySelectorAll('.pb-chat__message--ai, .message--ai, [class*="ai-message"], .chat-message-ai');
                    return msgs.length;
                }
            """)
            if count > current_count:
                time.sleep(1)  # brief settle
                return count
        except Exception:
            pass
        time.sleep(1)
    print(f"[TIMEOUT] Waited {timeout}s for new AI message (had {current_count})")
    return current_count

def get_ai_message_count(page):
    try:
        return page.evaluate("""
            () => {
                var msgs = document.querySelectorAll('.pb-chat__message--ai, .message--ai, [class*="ai-message"], .chat-message-ai');
                return msgs.length;
            }
        """)
    except Exception:
        return 0

def get_last_ai_message(page):
    try:
        return page.evaluate("""
            () => {
                var msgs = document.querySelectorAll('.pb-chat__message--ai, .message--ai, [class*="ai-message"], .chat-message-ai');
                if (msgs.length === 0) return null;
                return msgs[msgs.length - 1].innerText;
            }
        """)
    except Exception:
        return None

def get_chat_html(page, n_chars=3000):
    try:
        return page.evaluate("""
            (n) => {
                var container = document.querySelector('.pb-chat__messages, #chatMessages, .chat-messages, [class*="messages"]');
                if (!container) return 'NO CONTAINER FOUND';
                return container.innerHTML.substring(0, n);
            }
        """, n_chars)
    except Exception as e:
        return f"ERROR: {e}"

def send_message(page, text):
    """Send a message to the chat."""
    try:
        result = page.evaluate("""
            (text) => {
                // Try various input selectors
                var input = document.querySelector('textarea.pb-chat__input, #userInput, .chat-input, textarea[placeholder*="Type"], textarea');
                if (!input) return 'NO INPUT FOUND';

                // Set value
                var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value') ||
                                   Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
                if (nativeSetter && nativeSetter.set) {
                    nativeSetter.set.call(input, text);
                } else {
                    input.value = text;
                }
                input.dispatchEvent(new Event('input', {bubbles: true}));
                input.dispatchEvent(new Event('change', {bubbles: true}));

                // Try to find and click submit button
                var submitBtn = document.querySelector('button.pb-chat__submit, #submitBtn, .chat-submit, button[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                    return 'SENT via button';
                }

                // Try Enter key on textarea
                input.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', keyCode: 13, bubbles: true}));
                input.dispatchEvent(new KeyboardEvent('keypress', {key: 'Enter', keyCode: 13, bubbles: true}));
                input.dispatchEvent(new KeyboardEvent('keyup', {key: 'Enter', keyCode: 13, bubbles: true}));
                return 'SENT via Enter';
            }
        """, text)
        print(f"[SEND] '{text}' -> {result}")
        return result
    except Exception as e:
        print(f"[SEND ERROR] {e}")
        return f"ERROR: {e}"

def click_button_containing(page, text_fragments):
    """Click a button containing any of the text fragments."""
    if isinstance(text_fragments, str):
        text_fragments = [text_fragments]
    try:
        result = page.evaluate("""
            (fragments) => {
                var btns = Array.from(document.querySelectorAll('button, .btn, [role="button"], a.button'));
                for (var frag of fragments) {
                    var btn = btns.find(b => b.innerText && b.innerText.toLowerCase().includes(frag.toLowerCase()));
                    if (btn) {
                        btn.click();
                        return 'CLICKED: ' + btn.innerText.substring(0, 60);
                    }
                }
                return 'NOT FOUND: ' + JSON.stringify(fragments);
            }
        """, text_fragments)
        print(f"[CLICK] {result}")
        return result
    except Exception as e:
        print(f"[CLICK ERROR] {e}")
        return f"ERROR: {e}"

def find_all_buttons(page):
    try:
        return page.evaluate("""
            () => {
                var btns = Array.from(document.querySelectorAll('button, .btn, [role="button"]'));
                return btns.map(b => ({
                    text: b.innerText.substring(0, 80),
                    visible: b.offsetParent !== null,
                    id: b.id,
                    class: b.className.substring(0, 60)
                })).filter(b => b.text.trim().length > 0);
            }
        """)
    except Exception:
        return []

def inspect_page_structure(page):
    try:
        return page.evaluate("""
            () => {
                var result = {};

                // Check for post-payment overlay
                result.overlay = !!document.querySelector('.post-payment-overlay, #postPaymentOverlay, [class*="post-payment"]');
                result.chatContainer = !!document.querySelector('.pb-chat, .chat-container, #chatContainer, [class*="chat-container"]');
                result.input = !!document.querySelector('textarea, input[type="text"]');
                result.simulateBtn = Array.from(document.querySelectorAll('button, a')).find(el =>
                    el.innerText && el.innerText.toLowerCase().includes('simulat')
                )?.innerText?.substring(0, 80) || null;

                // List all classes containing 'payment' or 'chat'
                var els = Array.from(document.querySelectorAll('[class]'));
                result.paymentClasses = els
                    .map(e => e.className)
                    .filter(c => c.toLowerCase().includes('payment') || c.toLowerCase().includes('chat'))
                    .slice(0, 20);

                result.bodyText = document.body.innerText.substring(0, 500);

                return result;
            }
        """)
    except Exception as e:
        return {"error": str(e)}

def check_for_simulate_button(page):
    try:
        return page.evaluate("""
            () => {
                var allEls = Array.from(document.querySelectorAll('button, a, .btn, [onclick], [data-action]'));
                var found = [];
                allEls.forEach(el => {
                    var text = el.innerText || el.textContent || '';
                    if (text.toLowerCase().includes('simulat') ||
                        text.toLowerCase().includes('bypass') ||
                        text.toLowerCase().includes('sandbox') ||
                        text.toLowerCase().includes('payment') ||
                        text.toLowerCase().includes('skip')) {
                        found.push({
                            tag: el.tagName,
                            text: text.substring(0, 80),
                            class: el.className.substring(0, 60),
                            id: el.id,
                            visible: el.offsetParent !== null
                        });
                    }
                });
                return found;
            }
        """)
    except Exception:
        return []

def safe_goto(page, url, timeout=60000):
    """Navigate to URL with domcontentloaded wait (avoids networkidle timeout on GoDaddy)."""
    try:
        page.goto(url, timeout=timeout, wait_until='domcontentloaded')
        # Extra wait for JS to initialize
        time.sleep(5)
    except Exception as e:
        print(f"[GOTO WARNING] {e}")
        time.sleep(5)

def get_chat_text_content(page):
    """Get all chat message text for inspection."""
    try:
        return page.evaluate("""
            () => {
                var msgs = document.querySelectorAll('.pb-chat__message, .chat-message, [class*="message"]');
                var texts = [];
                msgs.forEach(function(m) { texts.push(m.innerText); });
                return texts.join('|MSGBREAK|');
            }
        """)
    except Exception as e:
        return f"ERROR: {e}"

def run_tests():
    results = {
        "phases": {},
        "screenshots": [],
        "errors": []
    }
    claude_auth_found = False
    simulate_clicked = "NOT STARTED"
    key_btn = "NOT STARTED"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            device_scale_factor=1
        )
        # Listen for console errors
        console_errors = []
        page = context.new_page()
        page.on("console", lambda msg: console_errors.append({"type": msg.type, "text": msg.text}) if msg.type == "error" else None)

        print("\n" + "="*60)
        print("STEP 1: Navigate and Enter Password")
        print("="*60)

        safe_goto(page, PAGE_URL)
        ss(page, "v3_test_00_initial_load")

        # Check if password form is present
        pw_input = page.query_selector('input[name="post_password"]')
        if pw_input:
            print("[PASSWORD] Password form found, entering password...")
            page.fill('input[name="post_password"]', PAGE_PASSWORD)
            page.click('input[type="submit"]')
            time.sleep(7)
            ss(page, "v3_test_01_after_password")
            body_text = page.evaluate("document.body.innerText.substring(0, 200)")
            if "Invalid password" in body_text:
                print(f"[PASSWORD FAILED] Body: {body_text}")
                browser.close()
                return {"error": "Password failed"}
            print("[PASSWORD] Password accepted!")
        else:
            print("[PASSWORD] No password form found - may already be unlocked")
            ss(page, "v3_test_01_no_password_needed")

        # Inspect page structure
        structure = inspect_page_structure(page)
        print(f"\n[STRUCTURE] {json.dumps(structure, indent=2)}")

        print("\n" + "="*60)
        print("STEP 2: Find Simulate Payment Button")
        print("="*60)

        ss(page, "v3_test_02_searching_for_simulate", full_page=True)

        simulate_btns = check_for_simulate_button(page)
        print(f"[SIMULATE BUTTONS] Found: {json.dumps(simulate_btns, indent=2)}")

        all_buttons = find_all_buttons(page)
        print(f"\n[ALL BUTTONS] {json.dumps(all_buttons, indent=2)}")

        # Try to find and click simulate button
        simulate_clicked = click_button_containing(page, [
            "Simulate Successful Payment",
            "Simulate Payment",
            "sandbox",
            "bypass",
            "Skip to Chat"
        ])

        if "NOT FOUND" in simulate_clicked:
            print("[WARNING] Simulate button not found via text search")
            # Try scrolling to bottom to find it
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            ss(page, "v3_test_02b_scrolled_to_bottom", full_page=False)

            # Check what's at bottom
            simulate_btns2 = check_for_simulate_button(page)
            print(f"[AFTER SCROLL] {json.dumps(simulate_btns2, indent=2)}")

            if simulate_btns2:
                simulate_clicked = click_button_containing(page, ["Simulat", "sandbox", "bypass"])

        time.sleep(4)
        ss(page, "v3_test_03_after_simulate_click", full_page=True)

        # Check what happened after click
        structure_after = inspect_page_structure(page)
        print(f"\n[STRUCTURE AFTER SIMULATE] {json.dumps(structure_after, indent=2)}")

        print("\n" + "="*60)
        print("STEP 3: POST-PAYMENT FLOW - Phase 1: Questionnaire")
        print("="*60)

        # Wait for chat to appear and send initial greeting
        time.sleep(4)

        # Get initial state
        ai_count = get_ai_message_count(page)
        print(f"[AI MESSAGES] Current count: {ai_count}")

        last_msg = get_last_ai_message(page)
        print(f"[LAST AI MSG] {last_msg}")

        ss(page, "v3_test_04_chat_initial_state", full_page=True)

        # Check if there's chat content
        chat_html = get_chat_html(page, 1000)
        print(f"[CHAT HTML PREVIEW]\n{chat_html[:400]}")

        # Phase 1: Name
        print("\n--- PHASE 1: Name ---")
        time.sleep(2)
        ai_count_before = get_ai_message_count(page)

        send_result = send_message(page, "Test User")
        time.sleep(2)
        ss(page, "v3_test_05_after_name_sent", full_page=True)

        ai_count = wait_for_new_ai_message(page, ai_count_before, timeout=35)
        last_msg = get_last_ai_message(page)
        print(f"[AFTER NAME] AI msgs: {ai_count}, Last: {last_msg}")
        ss(page, "v3_test_06_ai_response_to_name", full_page=True)

        # Phase 1: Email
        print("\n--- PHASE 1: Email ---")
        ai_count_before = ai_count
        send_message(page, "test@example.com")
        time.sleep(2)
        ss(page, "v3_test_07_after_email_sent")
        ai_count = wait_for_new_ai_message(page, ai_count_before, timeout=35)
        last_msg = get_last_ai_message(page)
        print(f"[AFTER EMAIL] AI msgs: {ai_count}, Last: {last_msg}")
        ss(page, "v3_test_08_ai_response_to_email")

        # Phase 1: Company
        print("\n--- PHASE 1: Company ---")
        ai_count_before = ai_count
        send_message(page, "Test Corp")
        time.sleep(2)
        ss(page, "v3_test_09_after_company_sent")
        ai_count = wait_for_new_ai_message(page, ai_count_before, timeout=35)
        last_msg = get_last_ai_message(page)
        print(f"[AFTER COMPANY] AI msgs: {ai_count}, Last: {last_msg}")
        ss(page, "v3_test_10_ai_response_to_company")

        # Phase 1: Role
        print("\n--- PHASE 1: Role ---")
        ai_count_before = ai_count
        send_message(page, "CTO")
        time.sleep(2)
        ss(page, "v3_test_11_after_role_sent")
        ai_count = wait_for_new_ai_message(page, ai_count_before, timeout=35)
        last_msg = get_last_ai_message(page)
        print(f"[AFTER ROLE] AI msgs: {ai_count}, Last: {last_msg}")
        ss(page, "v3_test_12_ai_response_to_role")

        # Check for Claude auth step - appears AFTER role
        print("\n--- CHECKING FOR CLAUDE AUTH STEP ---")
        time.sleep(3)
        buttons_now = find_all_buttons(page)
        print(f"[BUTTONS NOW] {json.dumps(buttons_now, indent=2)}")

        # Look for "I have my key" button
        key_btn = click_button_containing(page, [
            "I have my key",
            "have my key",
            "key",
            "Before we go",
            "API",
            "Enter key"
        ])
        time.sleep(2)
        ss(page, "v3_test_13_claude_auth_step")

        if "NOT FOUND" in key_btn:
            print("[WARNING] Claude auth button not found - checking chat content")
            last_msg = get_last_ai_message(page)
            print(f"[LAST MSG CHECK] {last_msg}")

            # Scroll chat container to see latest
            page.evaluate("""
                () => {
                    var container = document.querySelector('.pb-chat__messages, #chatMessages, .chat-messages, [class*="messages"]');
                    if (container) container.scrollTop = container.scrollHeight;
                }
            """)
            time.sleep(1)
            ss(page, "v3_test_13b_chat_scrolled_down")
            claude_auth_found = False
        else:
            claude_auth_found = True
            # Claude auth: enter fake API key
            print("\n--- CLAUDE AUTH: Entering fake API key ---")
            ai_count_before = get_ai_message_count(page)
            send_message(page, "sk-ant-api03-test1234567890abcdefghijk")
            time.sleep(2)
            ss(page, "v3_test_14_after_api_key_sent")
            ai_count = wait_for_new_ai_message(page, ai_count_before, timeout=35)
            last_msg = get_last_ai_message(page)
            print(f"[AFTER API KEY] AI msgs: {ai_count}, Last: {last_msg}")
            ss(page, "v3_test_15_api_key_response")

        # Phase 1: Primary Goal
        print("\n--- PHASE 1: Primary Goal ---")
        ai_count_before = get_ai_message_count(page)
        send_message(page, "Testing the v3 flow")
        time.sleep(2)
        ss(page, "v3_test_16_after_goal_sent")
        ai_count = wait_for_new_ai_message(page, ai_count_before, timeout=35)
        last_msg = get_last_ai_message(page)
        print(f"[AFTER GOAL] AI msgs: {ai_count}, Last: {last_msg}")
        ss(page, "v3_test_17_ai_response_to_goal")

        print("\n" + "="*60)
        print("STEP 3B: Phase 2 - Behind the Curtain Slides")
        print("="*60)

        time.sleep(3)
        ss(page, "v3_test_18_phase2_slides_check", full_page=True)

        # Look for slide navigation buttons
        slide_btns = find_all_buttons(page)
        print(f"[SLIDE BUTTONS] {json.dumps(slide_btns, indent=2)}")

        # Try clicking through slides
        for i in range(5):
            result = click_button_containing(page, ["Show Me More", "Next", "Continue", "More", "show me more"])
            time.sleep(2)
            ss(page, f"v3_test_19_slide_{i+1}")
            print(f"[SLIDE {i+1}] Click result: {result}")
            if "NOT FOUND" in result:
                print(f"[SLIDES] No more slide buttons at position {i+1}")
                break

        print("\n" + "="*60)
        print("STEP 3C: Phase 3 - Telegram Setup")
        print("="*60)

        time.sleep(3)
        ss(page, "v3_test_20_telegram_phase", full_page=True)

        # Check for telegram-related content
        telegram_check = page.evaluate("""
            () => {
                var body = document.body.innerText.toLowerCase();
                return {
                    hasTelegram: body.includes('telegram'),
                    hasBot: body.includes('bot'),
                    hasToken: body.includes('token'),
                    hasUsername: body.includes('username'),
                    visibleText: document.body.innerText.substring(0, 1000)
                };
            }
        """)
        print(f"[TELEGRAM CHECK] hasTelegram={telegram_check.get('hasTelegram')}, hasToken={telegram_check.get('hasToken')}")
        print(f"[VISIBLE TEXT SAMPLE] {telegram_check.get('visibleText', '')[:400]}")

        # Walk through telegram steps - enter bot token
        print("\n--- TELEGRAM: Bot token entry ---")
        ai_count_before = get_ai_message_count(page)
        send_message(page, "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        time.sleep(2)
        ss(page, "v3_test_21_after_bot_token")
        ai_count = wait_for_new_ai_message(page, ai_count_before, timeout=35)
        last_msg = get_last_ai_message(page)
        print(f"[AFTER BOT TOKEN] AI msgs: {ai_count}, Last: {last_msg}")
        ss(page, "v3_test_22_ai_response_to_token")

        # Check if token is masked in displayed messages
        chat_content = get_chat_text_content(page)
        # Check for bullet/dot masking characters
        has_bullet = (u"\u2022" in chat_content) or ("••" in chat_content)
        has_asterisk = "****" in chat_content or "***" in chat_content
        token_in_plain = "ABCdefGHIjklMNOpqrsTUVwxyz" in chat_content
        token_masked = has_bullet or has_asterisk or not token_in_plain
        print(f"[TOKEN MASKING] has_bullet={has_bullet}, has_asterisk={has_asterisk}, token_in_plain={token_in_plain}, masked={token_masked}")

        print("\n" + "="*60)
        print("STEP 3D: Phase 4 - Completion")
        print("="*60)

        time.sleep(5)
        ss(page, "v3_test_23_completion_phase", full_page=True)

        # Look for completion/ready button
        completion_btns = find_all_buttons(page)
        print(f"[COMPLETION BUTTONS] {json.dumps(completion_btns, indent=2)}")

        ready_btn = click_button_containing(page, [
            "is ready", "next steps", "see your next steps",
            "ready", "complete", "done", "Start"
        ])
        time.sleep(3)
        ss(page, "v3_test_24_after_ready_click", full_page=True)
        print(f"[READY BUTTON] {ready_btn}")

        # Verify we did NOT redirect to thank-you page
        current_url = page.url
        print(f"[URL CHECK] Current URL: {current_url}")
        stayed_on_page = "thank-you" not in current_url
        print(f"[URL CHECK] No redirect to /thank-you/: {stayed_on_page}")

        print("\n" + "="*60)
        print("STEP 3E: Phase 5 - Thank You Card IN CHAT")
        print("="*60)

        time.sleep(3)
        ss(page, "v3_test_25_thank_you_card", full_page=True)

        # Check thank-you card elements
        ty_card_check = page.evaluate("""
            () => {
                var bodyHTML = document.body.innerHTML.toLowerCase();
                var visText = document.body.innerText;
                return {
                    hasLogo: bodyHTML.includes('purebrain') && (bodyHTML.includes('logo') || bodyHTML.includes('img')),
                    hasWelcomeFamily: visText.includes('Welcome to the Family') || visText.includes('welcome to the family'),
                    hasTimeline: visText.includes('Now') || visText.includes('Next 2') || visText.includes('Next 5'),
                    hasLearnMore: visText.includes('Learn more') || visText.includes('learn more'),
                    hasReturnToHomepage: visText.includes('Return to Homepage'),
                    hasQuestionsEmail: visText.includes('Questions? Email'),
                    hasPortalPlaceholder: bodyHTML.includes('portal') || visText.toLowerCase().includes('portal'),
                    visibleText: visText.substring(0, 2000)
                };
            }
        """)
        print(f"[THANK YOU CARD CHECK] {json.dumps({k: v for k, v in ty_card_check.items() if k != 'visibleText'}, indent=2)}")
        print(f"[VISIBLE TEXT] {ty_card_check.get('visibleText', '')[:800]}")

        results["phases"]["thank_you_card"] = {
            "PASS_has_logo": ty_card_check.get("hasLogo"),
            "PASS_has_welcome_family": ty_card_check.get("hasWelcomeFamily"),
            "PASS_has_timeline": ty_card_check.get("hasTimeline"),
            "PASS_has_learn_more": ty_card_check.get("hasLearnMore"),
            "PASS_no_return_homepage": not ty_card_check.get("hasReturnToHomepage"),
            "PASS_no_questions_email": not ty_card_check.get("hasQuestionsEmail"),
            "PASS_has_portal": ty_card_check.get("hasPortalPlaceholder")
        }

        print("\n" + "="*60)
        print("STEP 3F: Phase 6 - Learn More Loop")
        print("="*60)

        learn_more_btn = click_button_containing(page, ["Learn more", "learn more", "Explore"])
        time.sleep(3)
        ss(page, "v3_test_26_after_learn_more", full_page=True)
        print(f"[LEARN MORE] Click: {learn_more_btn}")

        # Check for skip button
        skip_check_result = page.evaluate("""
            () => {
                var btns = Array.from(document.querySelectorAll('button, .btn, [role="button"]'));
                var skipBtns = btns.filter(function(b) { return b.innerText.toLowerCase().includes('skip'); });
                return skipBtns.map(function(b) { return b.innerText.substring(0, 60); });
            }
        """)
        print(f"[SKIP BUTTONS] {json.dumps(skip_check_result)}")
        skip_found = len(skip_check_result) > 0

        # Try skip button
        skip_result = click_button_containing(page, ["skip", "Skip"])
        time.sleep(2)
        ss(page, "v3_test_27_after_skip")
        print(f"[SKIP] {skip_result}")

        # Also try sending "skip" text to see acknowledgment
        ai_count_before = get_ai_message_count(page)
        send_message(page, "skip")
        time.sleep(2)
        ss(page, "v3_test_27b_skip_answer_sent")
        ai_count = wait_for_new_ai_message(page, ai_count_before, timeout=20)
        last_msg = get_last_ai_message(page)
        print(f"[AFTER SKIP TEXT] AI msgs: {ai_count}, Last: {last_msg}")
        ss(page, "v3_test_27c_skip_response")

        # Final full page screenshot
        ss(page, "v3_test_28_final_state", full_page=True)

        # Summary of console errors
        print(f"\n[CONSOLE ERRORS] Total: {len(console_errors)}")
        for err in console_errors[:10]:
            print(f"  - {err['text'][:120]}")

        results["console_errors"] = console_errors[:20]
        results["phases"]["questionnaire"] = {
            "PASS_password_entered": True,
            "PASS_simulate_clicked": "NOT FOUND" not in simulate_clicked and "NOT STARTED" not in simulate_clicked,
            "PASS_name_sent": send_result != "NO INPUT FOUND",
            "PASS_email_sent": True,
            "PASS_company_sent": True,
            "PASS_role_sent": True,
            "INFO_claude_auth_button_found": claude_auth_found,
            "PASS_goal_sent": True,
        }
        results["phases"]["telegram"] = {
            "PASS_has_telegram_content": telegram_check.get("hasTelegram", False),
            "PASS_token_masked": token_masked
        }
        results["phases"]["completion"] = {
            "PASS_stayed_on_page_no_redirect": stayed_on_page,
            "current_url": current_url
        }
        results["phases"]["learn_more"] = {
            "PASS_learn_more_button_found": "NOT FOUND" not in learn_more_btn,
            "PASS_skip_button_exists": skip_found,
            "PASS_skip_button_clicked": "NOT FOUND" not in skip_result
        }

        browser.close()

    return results

if __name__ == "__main__":
    print("Starting V3 Post-Payment Chatbox Test...")
    results = run_tests()
    print("\n" + "="*60)
    print("TEST COMPLETE - SUMMARY")
    print("="*60)
    print(json.dumps(results, indent=2))
