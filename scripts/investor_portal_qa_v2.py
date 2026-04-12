#!/usr/bin/env python3
"""
Live QA test v2: 3 investor sessions against purebrain.ai/investment-opportunity/
Fixed: Use evaluate() instead of inner_text() to avoid timeout on heavy JS pages.
"""

import time
import json
from playwright.sync_api import sync_playwright

SESSIONS = [
    {
        "investor": "Edward Lando",
        "code": "LANDO2026",
        "hot_buttons": ["break even", "competitive advantage"],
        "question": "What is your 5-year vision for Pure Technology?"
    },
    {
        "investor": "David Ross",
        "code": "ROSS2026",
        "hot_buttons": ["use the funds", "revenue projections"],
        "question": "How does the AI agent architecture scale with more clients?"
    },
    {
        "investor": "Elad Gil",
        "code": "GIL2026",
        "hot_buttons": ["team", "revenue streams"],
        "question": "What is the current monthly recurring revenue?"
    },
]

URL = "https://purebrain.ai/investment-opportunity/"


def safe_text(page, selector="body", timeout=5000):
    """Get text content safely without hanging."""
    try:
        return page.evaluate(f"""() => {{
            const el = document.querySelector('{selector}');
            return el ? el.innerText.substring(0, 3000) : 'element not found';
        }}""")
    except Exception as e:
        return f"[evaluate error: {e}]"


def safe_html(page, selector="body"):
    """Get HTML safely."""
    try:
        return page.evaluate(f"""() => {{
            const el = document.querySelector('{selector}');
            return el ? el.innerHTML.substring(0, 5000) : 'not found';
        }}""")
    except Exception as e:
        return f"[error: {e}]"


def find_all_clickables(page):
    """Find all clickable elements with their text."""
    try:
        return page.evaluate("""() => {
            const elements = document.querySelectorAll('button, a, [role="button"], [onclick], .btn, .hot-button, .question-btn, [data-question]');
            return Array.from(elements).map(el => ({
                tag: el.tagName,
                text: (el.innerText || el.textContent || '').substring(0, 100).trim(),
                id: el.id || '',
                className: (el.className || '').toString().substring(0, 80),
                visible: el.offsetParent !== null || el.getClientRects().length > 0,
                href: el.href || '',
                rect: (() => { const r = el.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; })()
            })).filter(el => el.text.length > 0);
        }""")
    except Exception as e:
        return [{"error": str(e)}]


def find_all_inputs(page):
    """Find all input elements."""
    try:
        return page.evaluate("""() => {
            const elements = document.querySelectorAll('input, textarea, [contenteditable="true"]');
            return Array.from(elements).map(el => ({
                tag: el.tagName,
                type: el.type || 'N/A',
                placeholder: el.placeholder || '',
                id: el.id || '',
                name: el.name || '',
                className: (el.className || '').toString().substring(0, 80),
                visible: el.offsetParent !== null || el.getClientRects().length > 0,
                rect: (() => { const r = el.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; })()
            }));
        }""")
    except Exception as e:
        return [{"error": str(e)}]


def human_wait(seconds=10):
    time.sleep(seconds)


def run_session(session_config, session_num):
    investor = session_config["investor"]
    code = session_config["code"]
    hot_button_keywords = session_config["hot_buttons"]
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
        "question_asked": None,
        "schedule_call_works": None,
        "errors": [],
        "console_errors": [],
        "tracking_events": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = context.new_page()
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: results["console_errors"].append(str(err)))

        # Track network requests for analytics
        network_requests = []
        page.on("request", lambda req: network_requests.append(req.url) if any(kw in req.url.lower() for kw in ["track", "analytics", "event", "pixel", "gtag", "collect"]) else None)

        try:
            # STEP 1: Navigate
            print(f"\n[1] Navigating to {URL}")
            page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            # Wait for page JS to initialize
            page.wait_for_timeout(5000)
            print(f"    Page title: {page.title()}")
            print(f"    URL: {page.url}")

            # STEP 2: Find gate input
            print(f"\n[2] Finding gate input...")
            gate = page.query_selector("#gate-input")
            if not gate:
                gate = page.query_selector('input[type="password"]')
            if not gate:
                gate = page.query_selector('input[placeholder*="Access" i]')

            if gate:
                print(f"    Found gate input (#gate-input)")
                gate.click()
                page.wait_for_timeout(1000)
                gate.type(code, delay=100)  # Type with human-like delay
                print(f"    Typed code: {code}")
                page.wait_for_timeout(2000)
            else:
                inputs = find_all_inputs(page)
                print(f"    GATE NOT FOUND. Available inputs: {json.dumps(inputs, indent=2)}")
                results["errors"].append("Gate input not found")
                browser.close()
                return results

            # STEP 3: Submit code
            print(f"\n[3] Submitting code...")

            # Look for submit button first
            submit_btn = page.query_selector('#gate-submit, button[type="submit"], .gate-btn, .submit-btn')
            if submit_btn:
                print(f"    Found submit button, clicking...")
                submit_btn.click()
            else:
                print(f"    No submit button found, pressing Enter...")
                page.keyboard.press("Enter")

            # Wait for transition - the page likely has heavy animations
            print(f"    Waiting for page transition (15s)...")
            page.wait_for_timeout(15000)

            # Check if URL changed or page content changed
            current_url = page.url
            print(f"    Current URL: {current_url}")

            # Check page state via evaluate (won't hang)
            page_state = page.evaluate("""() => {
                return {
                    title: document.title,
                    bodyClasses: document.body.className,
                    visibleSections: Array.from(document.querySelectorAll('section, .section, .panel, .layer, .screen')).map(s => ({
                        id: s.id,
                        className: s.className.toString().substring(0, 80),
                        visible: window.getComputedStyle(s).display !== 'none' && window.getComputedStyle(s).visibility !== 'hidden',
                        text: s.innerText ? s.innerText.substring(0, 100) : ''
                    })),
                    gateVisible: !!document.querySelector('#gate-input') && window.getComputedStyle(document.querySelector('#gate-input')).display !== 'none',
                    bodyTextLength: document.body.innerText ? document.body.innerText.length : 0
                };
            }""")
            print(f"    Page state: {json.dumps(page_state, indent=2)[:500]}")

            if page_state.get("gateVisible", True):
                print(f"    WARNING: Gate still visible - code may not have been accepted")
                results["errors"].append("Gate still visible after submit")
            else:
                results["login_success"] = True
                print(f"    LOGIN SUCCESS - gate no longer visible")

            # STEP 4: Handle entrance layers
            print(f"\n[4] Handling entrance layers...")

            for attempt in range(15):
                page.wait_for_timeout(3000)

                # Check for entrance/overlay elements
                entrance_state = page.evaluate("""() => {
                    const overlays = document.querySelectorAll('.entrance, .overlay, .intro, .welcome, .layer, [data-entrance], .entrance-layer, .click-continue');
                    const visible = Array.from(overlays).filter(el => {
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
                    });
                    return {
                        overlayCount: visible.length,
                        overlays: visible.map(el => ({
                            tag: el.tagName,
                            id: el.id,
                            className: el.className.toString().substring(0, 80),
                            text: (el.innerText || '').substring(0, 200)
                        }))
                    };
                }""")

                if entrance_state["overlayCount"] == 0:
                    # Try clicking anywhere in case the page needs interaction
                    if attempt < 3:
                        page.mouse.click(720, 450)
                        print(f"    Attempt {attempt+1}: Clicked center of page")
                    else:
                        print(f"    No more entrance layers detected")
                        break
                else:
                    print(f"    Entrance layer found: {entrance_state['overlays']}")
                    # Click it
                    page.mouse.click(720, 450)
                    print(f"    Clicked through entrance layer")

            results["entrance_complete"] = True

            # After entrance, wait and check what we have
            page.wait_for_timeout(5000)
            print(f"\n    Post-entrance page analysis:")
            clickables = find_all_clickables(page)
            visible_clickables = [c for c in clickables if c.get("visible", False)]
            print(f"    Total clickable elements: {len(clickables)}")
            print(f"    Visible clickable elements: {len(visible_clickables)}")
            for vc in visible_clickables[:20]:
                print(f"      - [{vc['tag']}] '{vc['text'][:60]}' (id={vc.get('id','')}, class={vc.get('className','')[:40]})")

            inputs_now = find_all_inputs(page)
            visible_inputs = [i for i in inputs_now if i.get("visible", False)]
            print(f"    Visible inputs: {len(visible_inputs)}")
            for vi in visible_inputs:
                print(f"      - [{vi['tag']}] type={vi['type']} placeholder='{vi.get('placeholder','')}' id={vi.get('id','')}")

            # STEP 5: Click hot buttons
            print(f"\n[5] Clicking hot buttons...")
            for kw in hot_button_keywords:
                print(f"\n    Looking for button matching: '{kw}'")
                human_wait(10)

                # Find matching button
                clicked = False
                for vc in visible_clickables:
                    if kw.lower() in vc.get("text", "").lower():
                        # Click by coordinates
                        rect = vc.get("rect", {})
                        cx = rect.get("x", 0) + rect.get("w", 0) / 2
                        cy = rect.get("y", 0) + rect.get("h", 0) / 2
                        if cx > 0 and cy > 0:
                            print(f"    FOUND: '{vc['text'][:60]}' at ({cx:.0f}, {cy:.0f})")
                            page.mouse.click(cx, cy)
                            clicked = True
                            print(f"    CLICKED!")
                            page.wait_for_timeout(8000)

                            # Refresh clickables list after click (page may update)
                            clickables = find_all_clickables(page)
                            visible_clickables = [c for c in clickables if c.get("visible", False)]
                            break

                if not clicked:
                    # Try using page.click with text matching
                    try:
                        page.click(f"text=/{kw}/i", timeout=5000)
                        clicked = True
                        print(f"    CLICKED via text selector!")
                        page.wait_for_timeout(8000)
                    except:
                        print(f"    WARNING: Could not find button for '{kw}'")
                        results["errors"].append(f"Hot button not found: {kw}")

                results["hot_buttons_clicked"].append({"keyword": kw, "clicked": clicked})

            # STEP 6: Type question in chat
            print(f"\n[6] Typing question: '{question}'")
            human_wait(10)

            # Refresh inputs list
            inputs_now = find_all_inputs(page)
            visible_inputs = [i for i in inputs_now if i.get("visible", False)]

            chat_input = None
            # Look for textarea or text input that's not the gate
            for vi in visible_inputs:
                if vi["tag"] == "TEXTAREA" or (vi["type"] == "text" and vi.get("id") != "gate-input"):
                    chat_input = vi
                    break
            # Also check contenteditable
            if not chat_input:
                for vi in visible_inputs:
                    if vi.get("tag") == "DIV":  # contenteditable divs
                        chat_input = vi
                        break

            if chat_input:
                selector = f"#{chat_input['id']}" if chat_input.get("id") else f"{chat_input['tag'].lower()}[placeholder*='{chat_input.get('placeholder', '')[:20]}']"
                print(f"    Found chat input: {chat_input['tag']} id={chat_input.get('id','')} placeholder='{chat_input.get('placeholder','')}'")

                # Click by coordinates
                rect = chat_input.get("rect", {})
                cx = rect.get("x", 0) + rect.get("w", 0) / 2
                cy = rect.get("y", 0) + rect.get("h", 0) / 2
                if cx > 0 and cy > 0:
                    page.mouse.click(cx, cy)
                    page.wait_for_timeout(1000)
                    page.keyboard.type(question, delay=50)
                    page.wait_for_timeout(2000)
                    page.keyboard.press("Enter")
                    results["question_asked"] = question
                    print(f"    Question submitted!")
                    page.wait_for_timeout(10000)
                else:
                    # Try by selector
                    try:
                        el = page.query_selector(f"textarea, input[type='text']:not(#gate-input)")
                        if el:
                            el.click()
                            page.wait_for_timeout(500)
                            el.type(question, delay=50)
                            page.keyboard.press("Enter")
                            results["question_asked"] = question
                            print(f"    Question submitted (via selector)!")
                            page.wait_for_timeout(10000)
                    except Exception as e:
                        print(f"    Error typing question: {e}")
                        results["errors"].append(f"Chat input error: {e}")
            else:
                print(f"    WARNING: No chat input found")
                print(f"    Available inputs: {json.dumps(visible_inputs, indent=2)}")
                results["errors"].append("Chat input not found")

            # STEP 7: Schedule a Call
            print(f"\n[7] Checking 'Schedule a Call'...")
            human_wait(10)

            # Refresh clickables
            clickables = find_all_clickables(page)
            visible_clickables = [c for c in clickables if c.get("visible", False)]

            schedule_found = False
            for vc in visible_clickables:
                text = vc.get("text", "").lower()
                if "schedule" in text or "call" in text or "book" in text or "calendly" in text:
                    rect = vc.get("rect", {})
                    cx = rect.get("x", 0) + rect.get("w", 0) / 2
                    cy = rect.get("y", 0) + rect.get("h", 0) / 2
                    print(f"    Found: '{vc['text'][:60]}' at ({cx:.0f}, {cy:.0f})")
                    page.mouse.click(cx, cy)
                    schedule_found = True
                    page.wait_for_timeout(5000)

                    # Check for modal/iframe
                    modal_check = page.evaluate("""() => {
                        const modals = document.querySelectorAll('.modal, [role="dialog"], .popup, iframe[src*="calendly"], .calendly-inline-widget');
                        const visible = Array.from(modals).filter(el => {
                            const style = window.getComputedStyle(el);
                            return style.display !== 'none';
                        });
                        return {
                            found: visible.length > 0,
                            elements: visible.map(el => ({tag: el.tagName, src: el.src || '', className: el.className.toString().substring(0, 80)}))
                        };
                    }""")
                    results["schedule_call_works"] = modal_check["found"]
                    print(f"    Modal/dialog check: {json.dumps(modal_check)}")
                    break

            if not schedule_found:
                results["schedule_call_works"] = "Button not found"
                print(f"    Schedule button not found among visible elements")

            # STEP 8: Console & tracking summary
            tracking_msgs = [m for m in console_messages if any(kw in m.lower() for kw in [
                "track", "analytics", "portal", "investor", "event", "gtag", "pixel"
            ])]
            results["tracking_events"] = tracking_msgs[:20]

            print(f"\n[8] Console & Tracking Summary:")
            print(f"    Total console messages: {len(console_messages)}")
            print(f"    Tracking messages: {len(tracking_msgs)}")
            for tm in tracking_msgs[:10]:
                print(f"      {tm[:200]}")
            print(f"    Console errors: {len(results['console_errors'])}")
            for ce in results["console_errors"][:5]:
                print(f"      ERROR: {ce[:200]}")
            print(f"    Analytics network requests: {len(network_requests)}")
            for nr in network_requests[:10]:
                print(f"      {nr[:150]}")

            # Final page state
            final_state = page.evaluate("""() => {
                return {
                    url: window.location.href,
                    title: document.title,
                    bodyTextLength: document.body.innerText ? document.body.innerText.length : 0,
                };
            }""")
            print(f"\n    Final state: {json.dumps(final_state)}")

        except Exception as e:
            print(f"\n    FATAL ERROR: {e}")
            results["errors"].append(f"Fatal: {e}")
            import traceback
            traceback.print_exc()

        finally:
            page.wait_for_timeout(5000)
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
    print(f"FINAL SUMMARY - ALL 3 SESSIONS")
    print(f"{'='*70}")

    for i, r in enumerate(all_results, 1):
        print(f"\nSession {i}: {r['investor']} ({r['code']})")
        print(f"  Login: {'SUCCESS' if r['login_success'] else 'FAILED'}")
        print(f"  Entrance: {'COMPLETE' if r['entrance_complete'] else 'INCOMPLETE'}")
        hb_clicked = len([b for b in r['hot_buttons_clicked'] if b['clicked']])
        hb_total = len(r['hot_buttons_clicked'])
        print(f"  Hot buttons: {hb_clicked}/{hb_total} clicked")
        for b in r["hot_buttons_clicked"]:
            print(f"    - '{b['keyword']}': {'CLICKED' if b['clicked'] else 'NOT FOUND'}")
        print(f"  Question: {'ASKED - ' + str(r['question_asked'][:50]) if r['question_asked'] else 'NOT ASKED'}")
        print(f"  Schedule Call: {r['schedule_call_works']}")
        print(f"  Tracking events: {len(r.get('tracking_events', []))}")
        print(f"  Errors: {len(r['errors'])}")
        for e in r["errors"]:
            print(f"    - {e[:150]}")
        print(f"  Console errors: {len(r['console_errors'])}")


if __name__ == "__main__":
    main()
