#!/usr/bin/env python3
"""
V3 Post-Payment Chatbox Full Flow Test
Tests: purebrain.ai/pay-test-sandbox-2/
Tests all 6 phases of the post-payment flow.
"""

import time
import json
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$"

results = {}

def ss(page, label, full_page=False):
    """Take a screenshot with a given label."""
    path = f"{SCREENSHOT_DIR}/v3_test_{label}.png"
    page.screenshot(path=path, full_page=full_page)
    print(f"  [SCREENSHOT] {path}")
    return path

def get_page_text(page):
    """Get visible text from page body."""
    try:
        return page.evaluate("() => document.body.innerText")
    except:
        return ""

def run_test():
    print("\n" + "="*60)
    print("V3 POST-PAYMENT CHATBOX FLOW TEST")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # Capture console errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)

        # ============================================================
        # STEP 1: Navigate and enter password
        # ============================================================
        print("\n[STEP 1] Navigate to page and enter password...")
        page.goto(PAGE_URL, timeout=30000)
        page.wait_for_load_state('domcontentloaded', timeout=15000)

        ss(page, "00_initial_load")

        # Find and fill password field
        pw_field = page.query_selector('input[name="post_password"]')
        if pw_field:
            print("  Found password field - entering password...")
            page.fill('input[name="post_password"]', PAGE_PASSWORD)
            page.click('input[type="submit"]')
            page.wait_for_load_state('domcontentloaded', timeout=15000)
            time.sleep(3)
            ss(page, "01_after_password", full_page=False)
            print("  Password entered - page loaded")
            results['step1_password'] = 'PASS'
        else:
            # Maybe already unlocked or different page
            ss(page, "01_no_password_field")
            print("  No password field found - page may already be unlocked")
            results['step1_password'] = 'SKIPPED - no password field'

        # Check current page state
        page_title = page.title()
        page_url = page.url
        print(f"  Page title: {page_title}")
        print(f"  Current URL: {page_url}")

        ss(page, "01b_page_state", full_page=True)

        # ============================================================
        # STEP 2: Find and click "Simulate Successful Payment" button
        # ============================================================
        print("\n[STEP 2] Finding sandbox simulate payment button...")

        # Scroll to bottom to find the button
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        ss(page, "02_scrolled_to_bottom", full_page=False)

        # Scroll back to top and search for button
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        # Look for simulate button with various selectors
        simulate_btn = None
        selectors_to_try = [
            'button:has-text("Simulate")',
            'button:has-text("Simulate Successful Payment")',
            'a:has-text("Simulate")',
            '[id*="simulate"]',
            '[class*="simulate"]',
            'button:has-text("sandbox")',
            '.sandbox-btn',
            '#sandbox-bypass',
            'button:has-text("Skip")',
            'button:has-text("Test Payment")',
        ]

        for sel in selectors_to_try:
            try:
                btn = page.query_selector(sel)
                if btn and btn.is_visible():
                    simulate_btn = btn
                    print(f"  Found simulate button with selector: {sel}")
                    break
            except:
                pass

        if not simulate_btn:
            # Try searching all buttons for relevant text
            print("  Searching all buttons on page...")
            all_buttons = page.query_selector_all('button, input[type="button"], a[href="#"]')
            for btn in all_buttons:
                try:
                    text = btn.inner_text().strip()
                    if text and len(text) < 100:
                        print(f"    Found button: '{text}'")
                        if any(word in text.lower() for word in ['simulate', 'payment', 'sandbox', 'test', 'bypass', 'skip']):
                            simulate_btn = btn
                            print(f"  --> This looks like our button!")
                            break
                except:
                    pass

        if simulate_btn:
            # Scroll button into view
            simulate_btn.scroll_into_view_if_needed()
            ss(page, "02_simulate_btn_found")
            simulate_btn.click()
            print("  Clicked simulate button!")
            time.sleep(5)
            page.wait_for_load_state('domcontentloaded', timeout=10000)
            ss(page, "02_after_simulate_click", full_page=False)
            results['step2_simulate'] = 'PASS'
        else:
            print("  WARNING: Could not find simulate button - taking full page screenshot for analysis")
            ss(page, "02_no_simulate_btn_found", full_page=True)
            results['step2_simulate'] = 'FAIL - button not found'

            # Try to find if there's a chatbox already visible or other entry point
            overlay = page.query_selector('.post-payment-overlay, #post-payment-container, [id*="post-payment"], [class*="post-payment"]')
            if overlay:
                print("  Found post-payment overlay already visible")
                results['step2_simulate'] = 'PASS - overlay already visible'

        # ============================================================
        # PHASE 1: Questionnaire
        # ============================================================
        print("\n[PHASE 1] Questionnaire flow...")

        # Wait for chat/overlay to appear
        time.sleep(3)
        ss(page, "03_phase1_initial", full_page=False)

        # Look for chat container
        chat_selectors = [
            '.post-payment-overlay',
            '#post-payment-container',
            '[id*="post-payment"]',
            '[class*="post-payment"]',
            '.chat-overlay',
            '.chat-container',
            '#chat-container',
        ]

        for sel in chat_selectors:
            el = page.query_selector(sel)
            if el:
                print(f"  Found chat container: {sel}")
                break

        # Screenshot current state
        ss(page, "03b_looking_for_chat")

        # Check overlay state
        overlay_state = page.evaluate("""
            () => {
                var selectors = ['.post-payment-overlay', '#post-payment-container', '[id*="post-payment"]', '[class*="post-payment"]'];
                for (var i = 0; i < selectors.length; i++) {
                    var sel = selectors[i];
                    var el = document.querySelector(sel);
                    if (el) {
                        var style = window.getComputedStyle(el);
                        return {found: true, selector: sel, display: style.display, visibility: style.visibility, opacity: style.opacity};
                    }
                }
                return {found: false};
            }
        """)
        print(f"  Overlay state: {overlay_state}")

        # Get AI messages
        ai_messages = page.evaluate("""
            () => {
                var elements = document.querySelectorAll('.ai-message, .bot-message, .chat-message, [class*="ai-msg"], [class*="bot-msg"]');
                var texts = [];
                for (var i = 0; i < elements.length; i++) {
                    var text = elements[i].innerText.trim();
                    if (text) texts.push(text.substring(0, 200));
                }
                return texts;
            }
        """)
        print(f"  AI messages found: {ai_messages[:3] if ai_messages else 'none'}")

        # Try to find input - may need to wait for AI greeting first
        print("  Waiting for AI greeting (up to 15s)...")
        try:
            page.wait_for_selector('textarea, input[type="text"]', timeout=15000)
            print("  Input field appeared!")
        except:
            print("  No input field appeared after 15s")

        ss(page, "04_phase1_after_wait", full_page=False)

        # Try to type name
        chat_input = page.query_selector('textarea, input[type="text"]')
        if chat_input and chat_input.is_visible():
            print("  Typing test name...")
            chat_input.click()
            chat_input.fill("Test User")

            ss(page, "05_name_typed")

            # Submit with Enter
            chat_input.press("Enter")
            print("  Name submitted")
            time.sleep(5)
            ss(page, "06_after_name_submit")

            # Wait for email prompt
            print("  Waiting for email prompt...")
            time.sleep(8)
            ss(page, "07_waiting_for_email_prompt")

            # Type email
            chat_input = page.query_selector('textarea, input[type="text"]')
            if chat_input and chat_input.is_visible():
                chat_input.click()
                chat_input.fill("test@example.com")
                ss(page, "08_email_typed")
                chat_input.press("Enter")
                print("  Email submitted")
                time.sleep(8)
                ss(page, "09_after_email_submit")

                # Type company
                chat_input = page.query_selector('textarea, input[type="text"]')
                if chat_input and chat_input.is_visible():
                    chat_input.click()
                    chat_input.fill("Test Corp")
                    ss(page, "10_company_typed")
                    chat_input.press("Enter")
                    print("  Company submitted")
                    time.sleep(8)
                    ss(page, "11_after_company_submit")

                    # Type role
                    chat_input = page.query_selector('textarea, input[type="text"]')
                    if chat_input and chat_input.is_visible():
                        chat_input.click()
                        chat_input.fill("CTO")
                        ss(page, "12_role_typed")
                        chat_input.press("Enter")
                        print("  Role submitted")
                        time.sleep(5)
                        ss(page, "13_after_role_submit")
                        results['phase1_questionnaire'] = 'IN PROGRESS'

        else:
            print("  No chat input available - checking full page state")
            ss(page, "05_no_input_found", full_page=True)
            results['phase1_questionnaire'] = 'FAIL - no input field'

        # ============================================================
        # CLAUDE AUTH STEP (KEY NEW FEATURE)
        # ============================================================
        print("\n[KEY FEATURE] Looking for Claude auth step...")
        time.sleep(10)
        ss(page, "14_looking_for_claude_auth", full_page=False)

        page_text = get_page_text(page)
        auth_found = {
            'before_we_go_deeper': 'Before we go deeper' in page_text,
            'i_have_my_key': 'I have my key' in page_text,
            'claude_auth': 'Claude' in page_text and 'key' in page_text.lower(),
            'api_key': 'API key' in page_text or 'api key' in page_text.lower(),
        }
        print(f"  Claude auth indicators: {auth_found}")

        # Try to find and click "I have my key" button
        key_btn_selectors = [
            'button:has-text("I have my key")',
            'button:has-text("have my key")',
            '[class*="auth-btn"]',
            'button:has-text("key")',
        ]

        key_btn = None
        for sel in key_btn_selectors:
            try:
                btn = page.query_selector(sel)
                if btn and btn.is_visible():
                    key_btn = btn
                    print(f"  Found key button: {sel}")
                    break
            except:
                pass

        if key_btn:
            ss(page, "15_claude_auth_visible")
            key_btn.click()
            print("  Clicked 'I have my key' button")
            time.sleep(3)
            ss(page, "16_after_key_btn_click")

            # Type fake API key
            chat_input = page.query_selector('textarea, input[type="text"]')
            if chat_input and chat_input.is_visible():
                chat_input.click()
                chat_input.fill("sk-ant-api03-test1234567890abcdefghijk")
                ss(page, "17_api_key_typed")
                chat_input.press("Enter")
                print("  Fake API key submitted")
                time.sleep(8)
                ss(page, "18_after_api_key_submit")
                results['claude_auth_step'] = 'PASS'
            else:
                ss(page, "17_no_input_for_key", full_page=True)
                results['claude_auth_step'] = 'FAIL - no input after key button'
        else:
            print("  Claude auth button not found yet - continuing...")
            results['claude_auth_step'] = 'NOT YET VISIBLE'

        # ============================================================
        # Continue questionnaire - Primary Goal
        # ============================================================
        print("\n[PHASE 1 CONTINUED] Looking for primary goal question...")
        time.sleep(10)
        ss(page, "19_primary_goal_area", full_page=False)

        chat_input = page.query_selector('textarea, input[type="text"]')
        if chat_input and chat_input.is_visible():
            chat_input.click()
            chat_input.fill("Testing the v3 flow")
            ss(page, "20_primary_goal_typed")
            chat_input.press("Enter")
            print("  Primary goal submitted")
            time.sleep(10)
            ss(page, "21_after_primary_goal")
            results['phase1_questionnaire'] = 'PASS'

        # ============================================================
        # PHASE 2: Behind the Curtain (slides)
        # ============================================================
        print("\n[PHASE 2] Behind the Curtain slides...")
        time.sleep(10)
        ss(page, "22_phase2_initial", full_page=False)

        # Look for slide navigation
        page_text = get_page_text(page)
        slide_indicators = {
            'has_show_more': 'Show Me More' in page_text,
            'has_slide_text': 'of 10' in page_text or 'Behind the Curtain' in page_text,
            'has_slide_content': any(w in page_text for w in ['Slide', 'slide', 'curtain']),
        }
        print(f"  Slide indicators: {slide_indicators}")

        # Click through slides
        slides_clicked = 0
        for i in range(12):  # Try up to 12 times
            show_more = None
            try:
                show_more = page.query_selector('button:has-text("Show Me More")')
                if not show_more:
                    show_more = page.query_selector('button:has-text("More")')
                if not show_more:
                    show_more = page.query_selector('[class*="slide-next"], [class*="next-btn"]')
            except:
                pass

            if show_more and show_more.is_visible():
                show_more.click()
                slides_clicked += 1
                print(f"  Clicked 'Show Me More' (slide {slides_clicked})")
                time.sleep(2)
                if slides_clicked in [1, 3, 5]:
                    ss(page, f"23_slide_{slides_clicked}")
            else:
                print(f"  No more 'Show Me More' buttons (after {slides_clicked} slides)")
                break

        if slides_clicked > 0:
            ss(page, "24_slides_done", full_page=False)
            results['phase2_slides'] = f'PASS - clicked through {slides_clicked} slides'
        else:
            ss(page, "24_no_slides_found", full_page=True)
            results['phase2_slides'] = 'FAIL - no slides found'

        # ============================================================
        # PHASE 3: Telegram Setup
        # ============================================================
        print("\n[PHASE 3] Telegram Setup...")
        time.sleep(10)
        ss(page, "25_phase3_telegram_initial", full_page=False)

        page_text = get_page_text(page)
        telegram_indicators = {
            'has_telegram': 'telegram' in page_text.lower(),
            'has_bot_token': 'bot token' in page_text.lower(),
            'has_username': 'username' in page_text.lower(),
            'has_step': 'Step' in page_text or 'step' in page_text,
        }
        print(f"  Telegram indicators: {telegram_indicators}")

        # Walk through telegram steps
        telegram_responses = [
            "Yes, I'm ready",
            "sounds good",
            "@testuser_pb",
        ]

        for i, response in enumerate(telegram_responses):
            chat_input = page.query_selector('textarea, input[type="text"]')
            if chat_input and chat_input.is_visible():
                chat_input.click()
                chat_input.fill(response)
                ss(page, f"26_telegram_step_{i+1}_typed")
                chat_input.press("Enter")
                print(f"  Telegram step {i+1} submitted: {response}")
                time.sleep(8)
                ss(page, f"27_telegram_step_{i+1}_response")
            else:
                # Look for clickable buttons
                btns = page.query_selector_all('button:visible')
                if btns:
                    print(f"  Step {i+1}: Found {len(btns)} buttons")
                    for btn in btns[:5]:
                        print(f"    Button: '{btn.inner_text().strip()[:50]}'")
                break

        # Check for dynamic AI name suggestion
        print("  Checking for dynamic AI name suggestion...")
        page_text = get_page_text(page)
        # Look for @handle patterns
        import re
        handle_matches = re.findall(r'@[a-zA-Z0-9_]+', page_text)
        print(f"  Handle patterns found: {handle_matches[:5]}")

        # Submit bot token (fake)
        fake_token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
        chat_input = page.query_selector('textarea, input[type="text"]')
        if chat_input and chat_input.is_visible():
            chat_input.click()
            chat_input.fill(fake_token)
            ss(page, "28_bot_token_typed")
            chat_input.press("Enter")
            print(f"  Fake bot token submitted")
            time.sleep(10)
            ss(page, "29_after_bot_token")

            # Verify token is masked in chat
            page_text = get_page_text(page)
            token_masked = {
                'masked': 'ABCdefGHIjklMNOpqrsTUVwxyz' not in page_text,
                'has_bullets': '****' in page_text or '\u2022\u2022\u2022\u2022' in page_text,
                'raw_visible': 'ABCdefGHIjklMNOpqrsTUVwxyz' in page_text,
            }
            print(f"  Token masking check: {token_masked}")

            if token_masked['masked'] and not token_masked['raw_visible']:
                results['phase3_telegram'] = 'PASS - token masked correctly'
            elif not token_masked['raw_visible']:
                results['phase3_telegram'] = 'PARTIAL - token hidden but masking style unclear'
            else:
                results['phase3_telegram'] = 'FAIL - raw token visible in chat!'

        # ============================================================
        # PHASE 4: Completion
        # ============================================================
        print("\n[PHASE 4] Completion phase...")
        time.sleep(15)
        ss(page, "30_phase4_completion", full_page=False)

        page_text = get_page_text(page)
        completion_indicators = {
            'has_ready': 'ready' in page_text.lower(),
            'has_next_steps': 'next steps' in page_text.lower(),
            'has_complete': 'complete' in page_text.lower(),
        }
        print(f"  Completion indicators: {completion_indicators}")

        # Look for completion button
        completion_btn = None
        btn_texts_to_find = ['is ready', 'next steps', 'see your next', 'ready \u2014', 'ready -']

        all_btns = page.query_selector_all('button, .chat-btn, [class*="cta-btn"]')
        for btn in all_btns:
            try:
                txt = btn.inner_text().strip()
                if any(phrase.lower() in txt.lower() for phrase in btn_texts_to_find):
                    completion_btn = btn
                    print(f"  Found completion button: '{txt}'")
                    break
            except:
                pass

        if completion_btn and completion_btn.is_visible():
            ss(page, "31_completion_btn_visible")
            completion_btn.scroll_into_view_if_needed()
            completion_btn.click()
            print("  Clicked completion button")
            time.sleep(5)
            ss(page, "32_after_completion_click", full_page=False)

            # Verify no redirect to /thank-you/
            current_url = page.url
            print(f"  Current URL after click: {current_url}")

            if '/thank-you' in current_url or '/thankyou' in current_url:
                results['phase4_completion'] = 'FAIL - redirected to thank-you page!'
            else:
                results['phase4_completion'] = f'PASS - stayed on page (url: {current_url})'
        else:
            print("  No completion button found yet")
            ss(page, "31_no_completion_btn", full_page=True)
            results['phase4_completion'] = 'INCOMPLETE - completion button not found'

        # ============================================================
        # PHASE 5: Thank You Card (IN CHAT)
        # ============================================================
        print("\n[PHASE 5] Thank You Card verification...")
        time.sleep(5)
        ss(page, "33_phase5_thankyou_card", full_page=False)

        page_text = get_page_text(page)
        page_html = page.evaluate("() => document.body.innerHTML")
        thankyou_checks = {
            'has_welcome_family': 'Welcome to the Family' in page_text,
            'has_timeline_now': 'Now' in page_text,
            'has_timeline_2min': '2 min' in page_text or '2mins' in page_text or 'Next 2' in page_text,
            'has_timeline_5min': '5 min' in page_text or '5mins' in page_text or 'Next 5' in page_text,
            'has_portal': 'Portal' in page_text or 'portal' in page_text,
            'has_learn_more': 'Learn more' in page_text,
            'no_return_homepage': 'Return to Homepage' not in page_text,
            'no_questions_email': 'Questions? Email' not in page_text,
            'has_logo': 'purebrain' in page_html.lower() or 'pure-brain' in page_html.lower(),
        }
        print(f"  Thank you card checks:")
        for k, v in thankyou_checks.items():
            print(f"    {k}: {v}")

        checks_pass = [
            thankyou_checks.get('has_welcome_family'),
            thankyou_checks.get('no_return_homepage'),
            thankyou_checks.get('no_questions_email'),
        ]

        if all(checks_pass):
            results['phase5_thankyou_card'] = 'PASS'
        elif any(checks_pass):
            failures = [k for k, v in thankyou_checks.items() if not v and not k.startswith('no_')]
            results['phase5_thankyou_card'] = f'PARTIAL - missing: {failures}'
        else:
            results['phase5_thankyou_card'] = 'FAIL - thank you card not visible'

        # ============================================================
        # PHASE 6: Learn More Loop
        # ============================================================
        print("\n[PHASE 6] Learn More loop...")

        learn_more_btn = None
        try:
            learn_more_btn = page.query_selector('button:has-text("Learn more")')
            if not learn_more_btn:
                learn_more_btn = page.query_selector('a:has-text("Learn more")')
        except:
            pass

        if learn_more_btn and learn_more_btn.is_visible():
            ss(page, "34_learn_more_btn_visible")
            learn_more_btn.click()
            print("  Clicked 'Learn more' button")
            time.sleep(5)
            ss(page, "35_after_learn_more_click", full_page=False)

            # Try skip button
            skip_btn = None
            try:
                skip_btn = page.query_selector('button:has-text("Skip")')
                if not skip_btn:
                    skip_btn = page.query_selector('[class*="skip"]')
            except:
                pass

            if skip_btn and skip_btn.is_visible():
                skip_btn.click()
                print("  Clicked skip button")
                time.sleep(5)
                ss(page, "36_after_skip_click")
                results['phase6_learn_more'] = 'PASS - skip works'
            else:
                # Answer a question instead
                chat_input = page.query_selector('textarea, input[type="text"]')
                if chat_input and chat_input.is_visible():
                    chat_input.fill("Just exploring")
                    chat_input.press("Enter")
                    time.sleep(5)
                    ss(page, "36_learn_more_answered")
                    results['phase6_learn_more'] = 'PASS - answered question'
                else:
                    ss(page, "36_learn_more_no_input", full_page=True)
                    results['phase6_learn_more'] = 'PARTIAL - no input or skip found'
        else:
            ss(page, "34_no_learn_more_btn", full_page=True)
            results['phase6_learn_more'] = 'INCOMPLETE - learn more button not found'

        # ============================================================
        # FINAL: Console errors summary
        # ============================================================
        print(f"\n[CONSOLE ERRORS] {len(console_errors)} errors captured:")
        for err in console_errors[:10]:
            print(f"  {err[:200]}")

        # Final full page screenshot
        ss(page, "99_final_state", full_page=True)

        browser.close()

    # ============================================================
    # RESULTS SUMMARY
    # ============================================================
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    for phase, result in results.items():
        status = "PASS" if "PASS" in result else ("FAIL" if "FAIL" in result else "...")
        print(f"  [{status}] {phase}: {result}")

    print(f"\nConsole errors: {len(console_errors)}")
    print(f"Screenshots saved to: {SCREENSHOT_DIR}/v3_test_*.png")

    return results, console_errors

if __name__ == "__main__":
    results, errors = run_test()
