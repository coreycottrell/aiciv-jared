#!/usr/bin/env python3
"""
Live QA test: 3 investor sessions against purebrain.ai/investment-opportunity/
Real Playwright browser sessions with JS execution for tracking.
"""

import time
import sys
from playwright.sync_api import sync_playwright

SESSIONS = [
    {
        "investor": "Edward Lando",
        "code": "LANDO2026",
        "hot_buttons": ["When do we break even?", "What is the competitive advantage?"],
        "question": "What is your 5-year vision for Pure Technology?"
    },
    {
        "investor": "David Ross",
        "code": "ROSS2026",
        "hot_buttons": ["How will you use the funds?", "What are the revenue projections?"],
        "question": "How does the AI agent architecture scale with more clients?"
    },
    {
        "investor": "Elad Gil",
        "code": "GIL2026",
        "hot_buttons": ["Who is on the team?", "What are the revenue streams?"],
        "question": "What is the current monthly recurring revenue?"
    },
]

URL = "https://purebrain.ai/investment-opportunity/"


def human_wait(seconds=10):
    """Human-like delay between actions."""
    time.sleep(seconds)


def run_session(session_config, session_num):
    """Run a single investor session."""
    investor = session_config["investor"]
    code = session_config["code"]
    hot_buttons = session_config["hot_buttons"]
    question = session_config["question"]

    print(f"\n{'='*70}")
    print(f"SESSION {session_num}: {investor} ({code})")
    print(f"{'='*70}")

    results = {
        "investor": investor,
        "code": code,
        "login_success": False,
        "entrance_complete": False,
        "hot_buttons_clicked": [],
        "hot_button_responses": [],
        "question_asked": None,
        "question_response": None,
        "schedule_call_works": None,
        "errors": [],
        "console_errors": [],
    }

    with sync_playwright() as p:
        # Launch real browser with JS enabled
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
            ]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Capture console messages
        page = context.new_page()
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: results["console_errors"].append(str(err)))

        try:
            # Step 1: Navigate
            print(f"\n[1] Navigating to {URL}")
            page.goto(URL, wait_until="networkidle", timeout=60000)
            human_wait(5)
            print(f"    Page title: {page.title()}")
            print(f"    URL: {page.url}")

            # Step 2: Find and fill the gate/login input
            print(f"\n[2] Looking for gate input field...")

            # Try multiple selectors for the gate input
            gate_input = None
            gate_selectors = [
                'input[type="text"]',
                'input[type="password"]',
                'input[placeholder*="code" i]',
                'input[placeholder*="access" i]',
                'input[placeholder*="investor" i]',
                'input[placeholder*="enter" i]',
                'input[name*="code" i]',
                'input[name*="access" i]',
                'input[id*="code" i]',
                'input[id*="gate" i]',
                'input[id*="access" i]',
                'input',
            ]

            for sel in gate_selectors:
                try:
                    elements = page.query_selector_all(sel)
                    for el in elements:
                        if el.is_visible():
                            gate_input = el
                            print(f"    Found input with selector: {sel}")
                            # Get attributes for debugging
                            attrs = page.evaluate("""(el) => {
                                return {
                                    type: el.type,
                                    placeholder: el.placeholder,
                                    name: el.name,
                                    id: el.id,
                                    className: el.className
                                }
                            }""", el)
                            print(f"    Input attrs: {attrs}")
                            break
                except:
                    pass
                if gate_input:
                    break

            if not gate_input:
                # Dump page structure for debugging
                body_text = page.inner_text("body")[:2000]
                print(f"    Page text preview: {body_text[:500]}")
                results["errors"].append("Could not find gate input field")
                # Try to see all inputs
                all_inputs = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('input, textarea')).map(el => ({
                        tag: el.tagName,
                        type: el.type,
                        placeholder: el.placeholder,
                        name: el.name,
                        id: el.id,
                        visible: el.offsetParent !== null,
                        className: el.className
                    }))
                }""")
                print(f"    All inputs on page: {all_inputs}")
            else:
                # Type the investor code
                print(f"    Typing investor code: {code}")
                gate_input.click()
                human_wait(2)
                gate_input.fill(code)
                human_wait(3)

                # Step 3: Submit the code
                print(f"\n[3] Submitting investor code...")
                # Try multiple submit methods
                submitted = False

                # Try pressing Enter
                page.keyboard.press("Enter")
                human_wait(5)

                # Check if we passed the gate (look for entrance layers or main content)
                page_content_after = page.inner_text("body")[:500]
                if code.lower() not in page.url.lower():
                    # Check if page state changed
                    print(f"    After Enter - checking page state...")

                # Try finding a submit button if Enter didn't work
                submit_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Enter")',
                    'button:has-text("Submit")',
                    'button:has-text("Access")',
                    'button:has-text("Go")',
                    'button:has-text("Unlock")',
                    '.submit',
                    'input[type="submit"]',
                ]
                for sel in submit_selectors:
                    try:
                        btn = page.query_selector(sel)
                        if btn and btn.is_visible():
                            print(f"    Found submit button: {sel}")
                            btn.click()
                            human_wait(5)
                            submitted = True
                            break
                    except:
                        pass

                results["login_success"] = True
                print(f"    Login attempted with code: {code}")

            # Step 4: Handle entrance layers
            print(f"\n[4] Handling entrance layers...")
            human_wait(5)

            # Click through any entrance/welcome layers
            for attempt in range(10):
                try:
                    # Look for clickable entrance elements
                    clickable_selectors = [
                        'button:has-text("Continue")',
                        'button:has-text("Enter")',
                        'button:has-text("Next")',
                        'button:has-text("Start")',
                        'button:has-text("Begin")',
                        '.entrance-layer',
                        '.welcome-layer',
                        '.overlay',
                        '[data-entrance]',
                        '.click-to-continue',
                        '.intro-screen',
                    ]
                    clicked = False
                    for sel in clickable_selectors:
                        try:
                            el = page.query_selector(sel)
                            if el and el.is_visible():
                                print(f"    Clicking entrance element: {sel}")
                                el.click()
                                human_wait(3)
                                clicked = True
                                break
                        except:
                            pass

                    if not clicked:
                        # Try clicking the body/main area (some portals use full-page click)
                        try:
                            page.click("body", position={"x": 720, "y": 450})
                            human_wait(2)
                        except:
                            pass
                        break
                except Exception as e:
                    print(f"    Entrance layer attempt {attempt}: {e}")
                    break

            results["entrance_complete"] = True
            print(f"    Entrance handling complete")

            # Check current page state
            current_text = page.inner_text("body")[:1000]
            print(f"\n    Current page text preview (first 500 chars):")
            print(f"    {current_text[:500]}")

            # Step 5: Click hot buttons
            print(f"\n[5] Clicking hot buttons...")
            for btn_text in hot_buttons:
                print(f"\n    Looking for hot button: '{btn_text}'")
                human_wait(10)

                clicked = False
                # Try exact and partial text matching
                try:
                    # Try button with exact text
                    btn = page.query_selector(f'button:has-text("{btn_text}")')
                    if not btn or not btn.is_visible():
                        # Try with partial text (first few words)
                        short_text = btn_text.split("?")[0].strip()
                        btn = page.query_selector(f'button:has-text("{short_text}")')
                    if not btn or not btn.is_visible():
                        # Try any clickable element with the text
                        btn = page.query_selector(f'text="{btn_text}"')
                    if not btn or not btn.is_visible():
                        # Try getting all buttons and matching
                        all_buttons = page.query_selector_all("button, .hot-button, .question-btn, [data-question], .btn, a.button")
                        for b in all_buttons:
                            try:
                                bt = b.inner_text().strip()
                                if btn_text.lower() in bt.lower() or bt.lower() in btn_text.lower():
                                    btn = b
                                    break
                            except:
                                pass

                    if btn and btn.is_visible():
                        btn.click()
                        clicked = True
                        print(f"    CLICKED: '{btn_text}'")
                        human_wait(8)

                        # Try to capture the response
                        try:
                            # Look for response areas
                            response_selectors = [
                                '.response', '.answer', '.chat-response',
                                '.message-content', '.ai-response', '.reply',
                                '.chat-message:last-child', '[data-response]',
                            ]
                            response_text = ""
                            for rsel in response_selectors:
                                try:
                                    resp_els = page.query_selector_all(rsel)
                                    if resp_els:
                                        response_text = resp_els[-1].inner_text()[:300]
                                        break
                                except:
                                    pass

                            if not response_text:
                                # Get latest text on page that might be a response
                                new_text = page.inner_text("body")[:2000]
                                response_text = f"Page updated (content length: {len(new_text)} chars)"

                            results["hot_button_responses"].append(response_text[:300])
                            print(f"    Response preview: {response_text[:200]}")
                        except Exception as e:
                            results["hot_button_responses"].append(f"Response capture error: {e}")
                    else:
                        print(f"    WARNING: Could not find button '{btn_text}'")
                        # List all visible buttons for debugging
                        all_btns = page.evaluate("""() => {
                            return Array.from(document.querySelectorAll('button, .btn, [role="button"]')).map(b => ({
                                text: b.innerText.substring(0, 80),
                                visible: b.offsetParent !== null,
                                className: b.className.substring(0, 60)
                            })).filter(b => b.visible)
                        }""")
                        print(f"    Visible buttons: {all_btns[:10]}")
                        results["errors"].append(f"Could not find hot button: {btn_text}")

                except Exception as e:
                    print(f"    Error clicking '{btn_text}': {e}")
                    results["errors"].append(f"Hot button error: {e}")

                results["hot_buttons_clicked"].append({"text": btn_text, "clicked": clicked})

            # Step 6: Type a question in chat
            print(f"\n[6] Typing question in chat: '{question}'")
            human_wait(10)

            chat_input = None
            chat_selectors = [
                'textarea',
                'input[type="text"]:not([type="password"])',
                '.chat-input',
                '[placeholder*="question" i]',
                '[placeholder*="ask" i]',
                '[placeholder*="type" i]',
                '[placeholder*="message" i]',
                '[contenteditable="true"]',
                'input[name*="chat" i]',
                'input[name*="message" i]',
            ]
            for sel in chat_selectors:
                try:
                    els = page.query_selector_all(sel)
                    for el in els:
                        if el.is_visible():
                            chat_input = el
                            print(f"    Found chat input: {sel}")
                            break
                except:
                    pass
                if chat_input:
                    break

            if chat_input:
                chat_input.click()
                human_wait(2)
                chat_input.fill(question)
                human_wait(3)
                page.keyboard.press("Enter")
                results["question_asked"] = question
                print(f"    Question submitted")
                human_wait(10)

                # Capture response
                try:
                    response_text = page.inner_text("body")[-500:]
                    results["question_response"] = f"Response received (page tail: {len(response_text)} chars)"
                    print(f"    Response area updated")
                except:
                    results["question_response"] = "Could not capture response"
            else:
                print(f"    WARNING: Could not find chat input")
                # List all text inputs
                all_inputs = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('input, textarea, [contenteditable]')).map(el => ({
                        tag: el.tagName,
                        type: el.type || 'N/A',
                        placeholder: el.placeholder || 'N/A',
                        visible: el.offsetParent !== null,
                        id: el.id,
                        className: el.className.substring(0, 60)
                    })).filter(el => el.visible)
                }""")
                print(f"    Visible inputs: {all_inputs}")
                results["errors"].append("Could not find chat input")

            # Step 7: Check Schedule a Call
            print(f"\n[7] Checking 'Schedule a Call' button...")
            human_wait(10)

            schedule_btn = None
            schedule_selectors = [
                'button:has-text("Schedule")',
                'button:has-text("Call")',
                'a:has-text("Schedule")',
                'a:has-text("Call")',
                '.schedule-call',
                '[data-action="schedule"]',
            ]
            for sel in schedule_selectors:
                try:
                    el = page.query_selector(sel)
                    if el and el.is_visible():
                        schedule_btn = el
                        print(f"    Found schedule button: {sel}")
                        break
                except:
                    pass

            if schedule_btn:
                schedule_btn.click()
                human_wait(5)
                # Check if modal appeared
                modal_selectors = ['.modal', '[role="dialog"]', '.popup', '.overlay', '.calendly', 'iframe']
                for msel in modal_selectors:
                    try:
                        mel = page.query_selector(msel)
                        if mel and mel.is_visible():
                            results["schedule_call_works"] = True
                            print(f"    Schedule modal/element appeared: {msel}")
                            break
                    except:
                        pass
                if results["schedule_call_works"] is None:
                    results["schedule_call_works"] = "Button clicked but no modal detected"
                    print(f"    Button clicked, checking for page changes...")
            else:
                results["schedule_call_works"] = "Button not found"
                print(f"    Schedule a Call button not found on page")

            # Collect console tracking info
            tracking_messages = [m for m in console_messages if any(kw in m.lower() for kw in [
                "track", "analytics", "portal_entry", "portal_exit", "investor",
                "click", "event", "gtag", "pixel", "segment"
            ])]
            print(f"\n[8] Console summary:")
            print(f"    Total console messages: {len(console_messages)}")
            print(f"    Tracking-related messages: {len(tracking_messages)}")
            for tm in tracking_messages[:10]:
                print(f"    - {tm[:150]}")
            print(f"    Console errors: {len(results['console_errors'])}")
            for ce in results["console_errors"][:5]:
                print(f"    - ERROR: {ce[:150]}")

        except Exception as e:
            print(f"\n    FATAL ERROR: {e}")
            results["errors"].append(f"Fatal: {e}")
            import traceback
            traceback.print_exc()

        finally:
            human_wait(5)
            browser.close()

    return results


def main():
    all_results = []

    for i, session in enumerate(SESSIONS, 1):
        result = run_session(session, i)
        all_results.append(result)
        if i < len(SESSIONS):
            print(f"\n--- Waiting 15 seconds before next session ---")
            time.sleep(15)

    # Final summary
    print(f"\n\n{'='*70}")
    print(f"FINAL SUMMARY - ALL SESSIONS")
    print(f"{'='*70}")

    for i, r in enumerate(all_results, 1):
        print(f"\nSession {i}: {r['investor']} ({r['code']})")
        print(f"  Login: {'SUCCESS' if r['login_success'] else 'FAILED'}")
        print(f"  Entrance: {'COMPLETE' if r['entrance_complete'] else 'INCOMPLETE'}")
        print(f"  Hot buttons: {len([b for b in r['hot_buttons_clicked'] if b['clicked']])}/{len(r['hot_buttons_clicked'])} clicked")
        for b in r["hot_buttons_clicked"]:
            print(f"    - '{b['text']}': {'CLICKED' if b['clicked'] else 'NOT FOUND'}")
        print(f"  Question: {'ASKED' if r['question_asked'] else 'NOT ASKED'}")
        print(f"  Schedule Call: {r['schedule_call_works']}")
        print(f"  Errors: {len(r['errors'])}")
        for e in r["errors"]:
            print(f"    - {e}")


if __name__ == "__main__":
    main()
