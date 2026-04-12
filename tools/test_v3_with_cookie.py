#!/usr/bin/env python3
"""
V3 Post-Payment Chatbox Full Flow Test
Uses cookie-based auth to bypass GoDaddy WAF.
Tests: purebrain.ai/pay-test-sandbox-2/
"""

import time
import json
import re
import requests
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"

results = {}

def ss(page, label, full_page=False):
    path = f"{SCREENSHOT_DIR}/v3_test_{label}.png"
    page.screenshot(path=path, full_page=full_page)
    print(f"  [SS] {path}")
    return path

def get_text(page):
    try:
        return page.evaluate("() => document.body.innerText")
    except:
        return ""

def get_visible_input(page):
    """Find and return the first visible text input or textarea."""
    for sel in ['textarea:visible', 'input[type=text]:visible', '#userInput', 'textarea', 'input[type=text]']:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                return el
        except:
            pass
    return None

def wait_for_ai_response(page, seconds=15):
    """Wait for AI to respond."""
    time.sleep(seconds)

def get_wp_postpass_cookie():
    """Get WordPress post-pass cookie via requests (bypasses GoDaddy WAF)."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': PAGE_URL,
    })

    # POST to WP login for post password
    resp = session.post(
        'https://purebrain.ai/wp-login.php?action=postpass',
        data={
            'post_password': PAGE_PASSWORD,
            'redirect_to': PAGE_URL,
            'Submit': 'Enter',
        },
        allow_redirects=False
    )

    print(f"  WP postpass response: {resp.status_code}")
    cookies_dict = {}
    for name, value in session.cookies.items():
        cookies_dict[name] = value
        print(f"  Cookie: {name[:40]}...")

    return cookies_dict


def run_test():
    print("\n" + "="*60)
    print("V3 POST-PAYMENT CHATBOX FLOW TEST (Cookie Auth)")
    print("="*60)

    # Step 1: Get WP cookie via requests
    print("\n[STEP 1] Getting WP post-pass cookie...")
    wp_cookies = get_wp_postpass_cookie()

    if not any('wp-postpass' in k for k in wp_cookies):
        print("  ERROR: Could not get wp-postpass cookie!")
        results['step1_auth'] = 'FAIL - no postpass cookie obtained'
    else:
        results['step1_auth'] = 'PASS - wp-postpass cookie obtained'

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # Inject cookies into Playwright context
        print("\n[STEP 2] Injecting auth cookies into browser...")
        playwright_cookies = []
        for name, value in wp_cookies.items():
            playwright_cookies.append({
                'name': name,
                'value': value,
                'domain': 'purebrain.ai',
                'path': '/',
                'secure': True,
                'httpOnly': False,
            })
        context.add_cookies(playwright_cookies)
        print(f"  Injected {len(playwright_cookies)} cookies")

        page = context.new_page()

        # Capture console errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)

        # Navigate directly (cookie should bypass password gate)
        print("\n[STEP 3] Navigating to page with auth cookie...")
        page.goto(PAGE_URL, timeout=30000)
        page.wait_for_load_state('domcontentloaded', timeout=15000)
        time.sleep(5)

        # Verify page is unlocked
        page_text = get_text(page)
        is_pw_gate = 'password-protected' in page_text or 'Invalid password' in page_text
        is_captcha = 'verify you are human' in page_text.lower()

        print(f"  Password gate: {is_pw_gate}")
        print(f"  CAPTCHA: {is_captcha}")
        print(f"  Page text preview: {page_text[:200]}")

        ss(page, "01_after_cookie_nav", full_page=False)

        if is_pw_gate or is_captcha:
            print("  ERROR: Still blocked! Saving full page...")
            ss(page, "01_still_blocked", full_page=True)
            results['step2_nav'] = 'FAIL - still blocked after cookie injection'
            browser.close()
            return results, console_errors
        else:
            results['step2_nav'] = 'PASS - page unlocked'
            print("  Page unlocked successfully!")

        ss(page, "02_page_unlocked", full_page=True)

        # ============================================================
        # Find the "Simulate Successful Payment" button
        # ============================================================
        print("\n[STEP 4] Looking for Simulate Payment button or sandbox entry...")

        # Take screenshot of page first
        ss(page, "03_looking_for_simulate", full_page=False)

        # Enumerate all visible text on page
        page_text = get_text(page)
        print(f"  Page text (first 500): {page_text[:500]}")

        # Look for sandbox-specific text
        has_sandbox_banner = 'SANDBOX MODE' in page_text or 'sandbox' in page_text.lower()
        print(f"  Has sandbox indicator: {has_sandbox_banner}")

        # Find all buttons
        all_btns_info = page.evaluate("""
            () => {
                var btns = document.querySelectorAll('button');
                var result = [];
                for (var i = 0; i < btns.length; i++) {
                    var b = btns[i];
                    result.push({
                        text: b.innerText.trim().substring(0, 80),
                        id: b.id || '',
                        visible: b.offsetParent !== null,
                        display: window.getComputedStyle(b).display
                    });
                }
                return result;
            }
        """)
        print(f"  All buttons on page:")
        for b in all_btns_info:
            if b['visible']:
                print(f"    VISIBLE: '{b['text'][:60]}' id={b['id'][:30]}")

        # Check if sandbox-2 page has the post-payment overlay pre-activated
        # or if we need to find a different trigger
        overlay_state = page.evaluate("""
            () => {
                var sels = [
                    '#post-payment-overlay', '.post-payment-overlay',
                    '#sandbox-overlay', '.sandbox-overlay',
                    '#chat-overlay', '.chat-overlay',
                ];
                var result = {};
                for (var i = 0; i < sels.length; i++) {
                    var el = document.querySelector(sels[i]);
                    if (el) {
                        var s = window.getComputedStyle(el);
                        result[sels[i]] = {
                            display: s.display,
                            opacity: s.opacity,
                            zIndex: s.zIndex
                        };
                    }
                }
                return result;
            }
        """)
        print(f"  Overlay state: {json.dumps(overlay_state)}")

        # Check for the simulate payment in JS source (might be in page source)
        page_html = page.content()
        simulate_in_html = 'simulate' in page_html.lower() or 'Simulate' in page_html
        print(f"  'simulate' in page HTML: {simulate_in_html}")
        if simulate_in_html:
            idx = page_html.lower().find('simulate')
            print(f"  Context: ...{page_html[max(0,idx-50):idx+100]}...")

        # Look for the Begin Awakening button
        begin_btn = page.query_selector('button:has-text("Begin Awakening")')
        if begin_btn and begin_btn.is_visible():
            print("\n[STEP 5] Found 'Begin Awakening' - this is the entry point!")
            begin_btn.scroll_into_view_if_needed()
            ss(page, "04_begin_btn_visible")
            begin_btn.click()
            print("  Clicked Begin Awakening")
            time.sleep(5)
            ss(page, "05_after_begin_click")
            results['step4_entry'] = 'PASS - Begin Awakening clicked'
        else:
            print("  No Begin Awakening button visible - checking for sandbox direct entry...")

            # Maybe sandbox-2 opens the post-payment overlay directly?
            # Try triggering via JS
            print("  Trying to trigger post-payment overlay via JS...")
            page.evaluate("""
                () => {
                    // Try common ways post-payment gets activated
                    if (window.showPostPaymentOverlay) {
                        window.showPostPaymentOverlay();
                    } else if (window.activatePaymentSuccess) {
                        window.activatePaymentSuccess();
                    } else if (window.pbPaymentSuccess) {
                        window.pbPaymentSuccess();
                    }
                }
            """)
            time.sleep(3)
            ss(page, "04_after_js_trigger")
            results['step4_entry'] = 'PARTIAL - tried JS trigger'

        # ============================================================
        # Phase 1: Questionnaire
        # ============================================================
        print("\n[PHASE 1] Questionnaire...")

        # Wait for AI greeting
        print("  Waiting up to 20s for AI greeting...")
        try:
            page.wait_for_selector('textarea, #userInput', timeout=20000)
            ss(page, "06_input_appeared")
            print("  Input appeared!")
            results['phase1_input_appeared'] = 'PASS'
        except:
            print("  No textarea appeared after 20s")
            ss(page, "06_no_input", full_page=True)
            results['phase1_input_appeared'] = 'FAIL - no input appeared'

        # Type name
        inp = get_visible_input(page)
        if inp:
            page_text_before = get_text(page)
            print(f"  Chat state: {page_text_before[-300:]}")
            inp.click()
            inp.fill("Test User")
            ss(page, "07_name_typed")
            inp.press("Enter")
            print("  Name submitted")
            wait_for_ai_response(page, 12)
            ss(page, "08_after_name")

            # Email
            inp = get_visible_input(page)
            if inp:
                inp.click()
                inp.fill("test@example.com")
                ss(page, "09_email_typed")
                inp.press("Enter")
                print("  Email submitted")
                wait_for_ai_response(page, 12)
                ss(page, "10_after_email")

                # Company
                inp = get_visible_input(page)
                if inp:
                    inp.click()
                    inp.fill("Test Corp")
                    ss(page, "11_company_typed")
                    inp.press("Enter")
                    print("  Company submitted")
                    wait_for_ai_response(page, 12)
                    ss(page, "12_after_company")

                    # Role
                    inp = get_visible_input(page)
                    if inp:
                        inp.click()
                        inp.fill("CTO")
                        ss(page, "13_role_typed")
                        inp.press("Enter")
                        print("  Role submitted")
                        wait_for_ai_response(page, 12)
                        ss(page, "14_after_role")
                        results['phase1_questionnaire'] = 'IN PROGRESS'
        else:
            results['phase1_questionnaire'] = 'FAIL - no input found'

        # ============================================================
        # Claude Auth Step
        # ============================================================
        print("\n[CLAUDE AUTH] Looking for auth step...")
        time.sleep(10)
        ss(page, "15_claude_auth_check")

        page_text = get_text(page)
        auth_found = {
            'before_deeper': 'Before we go deeper' in page_text,
            'i_have_key': 'I have my key' in page_text,
            'claude_mention': 'Claude' in page_text and 'key' in page_text.lower(),
            'api_key': 'API key' in page_text,
        }
        print(f"  Auth indicators: {auth_found}")
        print(f"  Recent page text: {page_text[-500:]}")

        # Try to find "I have my key" button
        key_btn = None
        for sel in ['button:has-text("I have my key")', 'button:has-text("have my key")']:
            try:
                btn = page.query_selector(sel)
                if btn and btn.is_visible():
                    key_btn = btn
                    break
            except:
                pass

        if key_btn:
            ss(page, "16_key_btn_visible")
            key_btn.click()
            print("  Clicked 'I have my key'")
            time.sleep(3)
            ss(page, "17_after_key_click")

            inp = get_visible_input(page)
            if inp:
                inp.click()
                inp.fill("sk-ant-api03-test1234567890abcdefghijk")
                ss(page, "18_api_key_typed")
                inp.press("Enter")
                print("  Fake API key submitted")
                wait_for_ai_response(page, 10)
                ss(page, "19_after_api_key")
                results['claude_auth'] = 'PASS - key submitted'
        else:
            print("  'I have my key' button not visible yet")
            results['claude_auth'] = 'NOT YET VISIBLE'

        # Primary goal
        print("\n[PHASE 1 CONTINUED] Primary goal...")
        time.sleep(10)
        ss(page, "20_primary_goal_check")

        inp = get_visible_input(page)
        if inp:
            inp.click()
            inp.fill("Testing the v3 flow")
            ss(page, "21_primary_goal_typed")
            inp.press("Enter")
            print("  Primary goal submitted")
            wait_for_ai_response(page, 15)
            ss(page, "22_after_primary_goal")
            results['phase1_questionnaire'] = 'PASS'

        # ============================================================
        # Phase 2: Behind the Curtain
        # ============================================================
        print("\n[PHASE 2] Behind the Curtain slides...")
        time.sleep(10)
        ss(page, "23_phase2_check")

        page_text = get_text(page)
        print(f"  Page text contains 'Show Me More': {'Show Me More' in page_text}")
        print(f"  Page text preview: {page_text[-400:]}")

        slides_clicked = 0
        for i in range(12):
            btn = None
            try:
                btn = page.query_selector('button:has-text("Show Me More")')
                if not btn or not btn.is_visible():
                    btn = page.query_selector('button:has-text("Show me more")')
            except:
                pass

            if btn and btn.is_visible():
                btn.click()
                slides_clicked += 1
                print(f"  Clicked slide {slides_clicked}")
                time.sleep(2)
                if slides_clicked in [1, 3, 5, 7, 10]:
                    ss(page, f"24_slide_{slides_clicked}")
            else:
                print(f"  No 'Show Me More' button (after {slides_clicked} slides)")
                break

        ss(page, "25_after_slides")
        if slides_clicked > 0:
            results['phase2_slides'] = f'PASS - {slides_clicked} slides clicked'
        else:
            results['phase2_slides'] = 'FAIL - no slides'

        # ============================================================
        # Phase 3: Telegram
        # ============================================================
        print("\n[PHASE 3] Telegram setup...")
        time.sleep(10)
        ss(page, "26_telegram_check")

        page_text = get_text(page)
        print(f"  Telegram in text: {'telegram' in page_text.lower()}")
        print(f"  Page text: {page_text[-500:]}")

        # Walk through telegram prompts
        for i in range(3):
            inp = get_visible_input(page)
            if inp:
                responses = ["I'm ready", "@testuser_pb", "sounds good"]
                inp.click()
                inp.fill(responses[i] if i < len(responses) else "ok")
                ss(page, f"27_telegram_step_{i+1}")
                inp.press("Enter")
                print(f"  Telegram step {i+1} submitted")
                wait_for_ai_response(page, 10)
                ss(page, f"28_telegram_step_{i+1}_response")
            else:
                print(f"  No input for telegram step {i+1}")
                break

        # Submit fake bot token
        fake_token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
        inp = get_visible_input(page)
        if inp:
            inp.click()
            inp.fill(fake_token)
            ss(page, "29_bot_token_typed")
            inp.press("Enter")
            print(f"  Bot token submitted")
            wait_for_ai_response(page, 12)
            ss(page, "30_after_bot_token")

            # Check masking
            page_text = get_text(page)
            token_visible = "ABCdefGHIjklMNOpqrsTUVwxyz" in page_text
            has_masking = page_text.count('*') > 5 or '\u2022\u2022' in page_text

            print(f"  Token raw visible: {token_visible}")
            print(f"  Has masking chars: {has_masking}")

            if not token_visible:
                results['phase3_telegram'] = 'PASS - token hidden'
            else:
                results['phase3_telegram'] = 'FAIL - raw token visible!'

        # ============================================================
        # Phase 4: Completion
        # ============================================================
        print("\n[PHASE 4] Completion...")
        time.sleep(15)
        ss(page, "31_phase4_check")

        page_text = get_text(page)
        print(f"  Page text: {page_text[-500:]}")

        # Look for completion button
        completion_btn = None
        for sel in [
            'button:has-text("is ready")',
            'button:has-text("next steps")',
            'button:has-text("see your next")',
            'button:has-text("Next Steps")',
        ]:
            try:
                btn = page.query_selector(sel)
                if btn and btn.is_visible():
                    completion_btn = btn
                    print(f"  Found completion btn: '{btn.inner_text().strip()[:60]}'")
                    break
            except:
                pass

        # Also check all visible buttons
        all_btns = page.evaluate("""
            () => {
                var btns = document.querySelectorAll('button');
                var r = [];
                for (var i = 0; i < btns.length; i++) {
                    if (btns[i].offsetParent) r.push(btns[i].innerText.trim().substring(0, 80));
                }
                return r;
            }
        """)
        print(f"  Visible buttons: {all_btns}")

        if completion_btn:
            ss(page, "32_completion_btn")
            completion_btn.scroll_into_view_if_needed()
            completion_btn.click()
            print("  Clicked completion button")
            time.sleep(5)
            ss(page, "33_after_completion")

            current_url = page.url
            if '/thank-you' in current_url:
                results['phase4_completion'] = 'FAIL - redirected to /thank-you!'
            else:
                results['phase4_completion'] = f'PASS - stayed on page'
        else:
            ss(page, "32_no_completion_btn", full_page=True)
            results['phase4_completion'] = 'INCOMPLETE'

        # ============================================================
        # Phase 5: Thank You Card in Chat
        # ============================================================
        print("\n[PHASE 5] Thank You Card...")
        time.sleep(5)
        ss(page, "34_thankyou_card")

        page_text = get_text(page)
        page_html = page.evaluate("() => document.body.innerHTML")
        thankyou = {
            'welcome_family': 'Welcome to the Family' in page_text,
            'timeline_now': 'Now' in page_text,
            'timeline_2min': '2 min' in page_text or 'Next 2' in page_text,
            'timeline_5min': '5 min' in page_text or 'Next 5' in page_text,
            'portal': 'Portal' in page_text or 'portal' in page_text,
            'learn_more_btn': 'Learn more' in page_text,
            'no_return_homepage': 'Return to Homepage' not in page_text,
            'no_questions_email': 'Questions? Email' not in page_text,
            'has_logo': 'purebrain' in page_html.lower(),
        }
        print("  Thank you card check:")
        for k, v in thankyou.items():
            icon = "OK" if v else "MISSING"
            print(f"    [{icon}] {k}")

        if thankyou['welcome_family'] and thankyou['no_return_homepage']:
            results['phase5_thankyou'] = 'PASS'
        elif thankyou['no_return_homepage'] or thankyou['no_questions_email']:
            results['phase5_thankyou'] = f'PARTIAL'
        else:
            results['phase5_thankyou'] = 'FAIL - card not visible'

        # ============================================================
        # Phase 6: Learn More Loop
        # ============================================================
        print("\n[PHASE 6] Learn More loop...")

        learn_more = None
        for sel in ['button:has-text("Learn more")', 'a:has-text("Learn more")', 'button:has-text("Learn More")']:
            try:
                btn = page.query_selector(sel)
                if btn and btn.is_visible():
                    learn_more = btn
                    break
            except:
                pass

        if learn_more:
            ss(page, "35_learn_more_visible")
            learn_more.click()
            print("  Clicked Learn more")
            time.sleep(5)
            ss(page, "36_after_learn_more")

            # Try skip
            skip = None
            for sel in ['button:has-text("Skip")', '[class*="skip"]']:
                try:
                    btn = page.query_selector(sel)
                    if btn and btn.is_visible():
                        skip = btn
                        break
                except:
                    pass

            if skip:
                skip.click()
                print("  Clicked skip")
                time.sleep(3)
                ss(page, "37_after_skip")
                results['phase6_learn_more'] = 'PASS - skip works'
            else:
                inp = get_visible_input(page)
                if inp:
                    inp.fill("Just exploring")
                    inp.press("Enter")
                    time.sleep(5)
                    ss(page, "37_answered_loop")
                    results['phase6_learn_more'] = 'PASS - answered'
                else:
                    results['phase6_learn_more'] = 'PARTIAL'
        else:
            ss(page, "35_no_learn_more", full_page=True)
            results['phase6_learn_more'] = 'INCOMPLETE'

        # Final
        ss(page, "99_final", full_page=True)

        print(f"\n[CONSOLE ERRORS] {len(console_errors)}:")
        for err in console_errors[:10]:
            print(f"  {err[:150]}")

        browser.close()

    # Summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    for phase, result in results.items():
        status = "PASS" if "PASS" in result else ("FAIL" if "FAIL" in result else "...")
        print(f"  [{status}] {phase}: {result}")

    return results, console_errors


if __name__ == "__main__":
    results, errors = run_test()
