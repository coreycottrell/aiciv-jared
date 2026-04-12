#!/usr/bin/env python3
"""
Live QA test v3: 3 investor sessions against purebrain.ai/investment-opportunity/
Fixed: Use #gate-btn for submit, click "Next" buttons through entrance layers.
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


def find_all_clickables(page):
    try:
        return page.evaluate("""() => {
            const elements = document.querySelectorAll('button, a, [role="button"], [onclick], .btn, .hot-button, .question-btn, [data-question]');
            return Array.from(elements).map(el => ({
                tag: el.tagName,
                text: (el.innerText || el.textContent || '').substring(0, 100).trim(),
                id: el.id || '',
                className: (el.className || '').toString().substring(0, 80),
                visible: el.offsetParent !== null || el.getClientRects().length > 0,
                display: window.getComputedStyle(el).display,
                opacity: window.getComputedStyle(el).opacity,
                rect: (() => { const r = el.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; })()
            })).filter(el => el.text.length > 0);
        }""")
    except Exception as e:
        return [{"error": str(e)}]


def find_all_inputs(page):
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
                display: window.getComputedStyle(el).display,
                rect: (() => { const r = el.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; })()
            }));
        }""")
    except Exception as e:
        return [{"error": str(e)}]


def click_element_by_id(page, element_id, label=""):
    """Click element by ID using JS."""
    try:
        result = page.evaluate(f"""() => {{
            const el = document.getElementById('{element_id}');
            if (el) {{
                el.click();
                return true;
            }}
            return false;
        }}""")
        if result:
            print(f"    Clicked #{element_id} ({label})")
        return result
    except Exception as e:
        print(f"    Error clicking #{element_id}: {e}")
        return False


def click_visible_button_matching(page, text_pattern):
    """Click first visible button matching text pattern."""
    try:
        result = page.evaluate(f"""() => {{
            const btns = document.querySelectorAll('button, a, [role="button"]');
            for (const btn of btns) {{
                const text = (btn.innerText || btn.textContent || '').toLowerCase();
                const style = window.getComputedStyle(btn);
                const visible = style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity) > 0;
                const inView = btn.getBoundingClientRect().width > 0;
                if (visible && inView && text.includes('{text_pattern.lower()}')) {{
                    btn.click();
                    return {{clicked: true, text: btn.innerText.substring(0, 80)}};
                }}
            }}
            return {{clicked: false}};
        }}""")
        return result
    except Exception as e:
        return {"clicked": False, "error": str(e)}


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
        "question_response": None,
        "schedule_call_works": None,
        "errors": [],
        "console_errors": [],
        "tracking_events": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = context.new_page()
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: results["console_errors"].append(str(err)))

        network_requests = []
        page.on("request", lambda req: network_requests.append(req.url) if any(kw in req.url.lower() for kw in ["track", "analytics", "event", "pixel", "gtag", "collect"]) else None)

        try:
            # STEP 1: Navigate
            print(f"\n[1] Navigating to {URL}")
            page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            print(f"    Title: {page.title()}")

            # STEP 2: Enter investor code
            print(f"\n[2] Entering investor code: {code}")
            gate = page.query_selector("#gate-input")
            if gate:
                gate.click()
                page.wait_for_timeout(500)
                gate.fill("")  # Clear first
                gate.type(code, delay=80)
                page.wait_for_timeout(1000)
                print(f"    Code typed into #gate-input")
            else:
                results["errors"].append("Gate input not found")
                browser.close()
                return results

            # STEP 3: Click the gate button (#gate-btn)
            print(f"\n[3] Clicking gate submit button (#gate-btn)...")
            click_element_by_id(page, "gate-btn", "Enter button")
            page.wait_for_timeout(5000)

            # Verify gate accepted
            gate_state = page.evaluate("""() => {
                const gate = document.getElementById('gate-input');
                const gateScreen = document.querySelector('.gate-screen, #gate-screen, .gate-container, #gate-container');
                let gateScreenVisible = false;
                if (gateScreen) {
                    const style = window.getComputedStyle(gateScreen);
                    gateScreenVisible = style.display !== 'none' && style.visibility !== 'hidden';
                }
                const inputVisible = gate ? window.getComputedStyle(gate).display !== 'none' : false;
                // Check entrance layers
                const entranceLayers = document.querySelectorAll('.entrance-layer');
                const activeLayer = Array.from(entranceLayers).find(l => l.classList.contains('active'));
                return {
                    inputVisible,
                    gateScreenVisible,
                    entranceLayerActive: activeLayer ? activeLayer.id : null,
                    entranceLayerCount: entranceLayers.length,
                };
            }""")
            print(f"    Gate state after submit: {json.dumps(gate_state)}")

            if gate_state.get("entranceLayerActive"):
                results["login_success"] = True
                print(f"    LOGIN SUCCESS - entrance layers activated")
            else:
                print(f"    Gate may not have accepted code, trying Enter key as fallback...")
                page.keyboard.press("Enter")
                page.wait_for_timeout(5000)

                gate_state2 = page.evaluate("""() => {
                    const entranceLayers = document.querySelectorAll('.entrance-layer');
                    const activeLayer = Array.from(entranceLayers).find(l => l.classList.contains('active'));
                    return { entranceLayerActive: activeLayer ? activeLayer.id : null };
                }""")
                if gate_state2.get("entranceLayerActive"):
                    results["login_success"] = True
                    print(f"    LOGIN SUCCESS after Enter key")
                else:
                    results["errors"].append("Could not pass gate")
                    print(f"    FAILED to pass gate")

            # STEP 4: Navigate through entrance layers
            print(f"\n[4] Navigating entrance layers...")

            for step in range(20):
                page.wait_for_timeout(3000)

                # Check current entrance state
                ent_state = page.evaluate("""() => {
                    const layers = document.querySelectorAll('.entrance-layer');
                    const activeLayer = Array.from(layers).find(l => l.classList.contains('active'));
                    if (!activeLayer) return { done: true, activeId: null };

                    // Find visible "Next" or "Enter" button within active layer
                    const btns = activeLayer.querySelectorAll('button, .ent-nav-btn');
                    const visibleBtns = Array.from(btns).filter(b => {
                        const s = window.getComputedStyle(b);
                        return s.display !== 'none' && s.visibility !== 'hidden' && parseFloat(s.opacity) > 0.3;
                    });

                    return {
                        done: false,
                        activeId: activeLayer.id,
                        activeClass: activeLayer.className,
                        text: activeLayer.innerText ? activeLayer.innerText.substring(0, 150) : '',
                        buttons: visibleBtns.map(b => ({
                            text: b.innerText.substring(0, 50),
                            class: b.className.substring(0, 50)
                        }))
                    };
                }""")

                if ent_state.get("done", False):
                    print(f"    All entrance layers complete!")
                    break

                print(f"    Layer: {ent_state.get('activeId', '?')} | Buttons: {ent_state.get('buttons', [])}")

                # Click the "Next" or "Enter" button within the active layer
                clicked = page.evaluate("""() => {
                    const layers = document.querySelectorAll('.entrance-layer');
                    const activeLayer = Array.from(layers).find(l => l.classList.contains('active'));
                    if (!activeLayer) return 'no_active_layer';

                    // Find visible navigation button
                    const btns = activeLayer.querySelectorAll('button, .ent-nav-btn');
                    for (const btn of btns) {
                        const s = window.getComputedStyle(btn);
                        const visible = s.display !== 'none' && s.visibility !== 'hidden' && parseFloat(s.opacity) > 0.3;
                        const text = btn.innerText.toLowerCase();
                        if (visible && (text.includes('next') || text.includes('enter') || text.includes('continue'))) {
                            btn.click();
                            return 'clicked: ' + btn.innerText.substring(0, 30);
                        }
                    }

                    // If no nav button, try clicking the layer itself
                    activeLayer.click();
                    return 'clicked_layer';
                }""")
                print(f"    Action: {clicked}")

            results["entrance_complete"] = True
            page.wait_for_timeout(5000)

            # STEP 4b: Check what's now visible
            print(f"\n    Post-entrance analysis:")
            post_state = page.evaluate("""() => {
                // Check if main interface is visible
                const mainContent = document.querySelector('.main-content, #main-content, .portal-content, .interface, #interface, .chat-container');
                const hotButtons = document.querySelectorAll('.hot-button, .question-btn, [data-question], .suggested-question, .quick-question');
                const chatInput = document.querySelector('textarea, input[type="text"]:not(#gate-input), .chat-input, [contenteditable="true"]');

                return {
                    mainContentFound: !!mainContent,
                    mainContentId: mainContent ? mainContent.id : null,
                    hotButtonCount: hotButtons.length,
                    hotButtons: Array.from(hotButtons).map(b => ({
                        text: (b.innerText || b.textContent || '').substring(0, 100),
                        visible: window.getComputedStyle(b).display !== 'none',
                        className: b.className.toString().substring(0, 60)
                    })),
                    chatInputFound: !!chatInput,
                    chatInputTag: chatInput ? chatInput.tagName : null,
                    chatInputId: chatInput ? chatInput.id : null,
                    chatInputPlaceholder: chatInput ? chatInput.placeholder : null,
                };
            }""")
            print(f"    Main content: {post_state.get('mainContentFound')}")
            print(f"    Hot buttons found: {post_state.get('hotButtonCount')}")
            for hb in post_state.get("hotButtons", []):
                print(f"      - '{hb['text'][:80]}' (visible={hb['visible']})")
            print(f"    Chat input: {post_state.get('chatInputFound')} (tag={post_state.get('chatInputTag')}, id={post_state.get('chatInputId')}, placeholder={post_state.get('chatInputPlaceholder')})")

            # Also get ALL visible clickable elements
            clickables = find_all_clickables(page)
            vis_click = [c for c in clickables if c.get("visible") and c.get("display") != "none"]
            print(f"    All visible clickables ({len(vis_click)}):")
            for vc in vis_click[:25]:
                print(f"      [{vc['tag']}] '{vc['text'][:60]}' id={vc.get('id','')} class={vc.get('className','')[:40]}")

            all_inputs = find_all_inputs(page)
            vis_inputs = [i for i in all_inputs if i.get("visible") and i.get("display") != "none"]
            print(f"    All visible inputs ({len(vis_inputs)}):")
            for vi in vis_inputs:
                print(f"      [{vi['tag']}] type={vi['type']} id={vi.get('id','')} placeholder='{vi.get('placeholder','')}'")

            # STEP 5: Click hot buttons
            print(f"\n[5] Clicking hot buttons...")
            for kw in hot_button_keywords:
                print(f"\n    Looking for: '{kw}'")
                time.sleep(10)

                # Try clicking via JS text match (most reliable)
                result = page.evaluate(f"""() => {{
                    // Search all elements with text matching
                    const all = document.querySelectorAll('button, a, [role="button"], .hot-button, .question-btn, [data-question], .suggested-question, span, div[onclick]');
                    for (const el of all) {{
                        const text = (el.innerText || el.textContent || '').toLowerCase();
                        if (text.includes('{kw.lower()}')) {{
                            const style = window.getComputedStyle(el);
                            if (style.display !== 'none' && style.visibility !== 'hidden') {{
                                el.click();
                                return {{clicked: true, text: el.innerText.substring(0, 80), tag: el.tagName}};
                            }}
                        }}
                    }}
                    return {{clicked: false}};
                }}""")

                if result.get("clicked"):
                    print(f"    CLICKED: [{result['tag']}] '{result['text'][:60]}'")
                    results["hot_buttons_clicked"].append({"keyword": kw, "clicked": True})
                    page.wait_for_timeout(8000)
                else:
                    # Try with Playwright text selector
                    try:
                        page.click(f"text=/{kw}/i", timeout=5000)
                        print(f"    CLICKED via text selector")
                        results["hot_buttons_clicked"].append({"keyword": kw, "clicked": True})
                        page.wait_for_timeout(8000)
                    except:
                        print(f"    NOT FOUND: '{kw}'")
                        results["hot_buttons_clicked"].append({"keyword": kw, "clicked": False})
                        results["errors"].append(f"Hot button not found: {kw}")

            # STEP 6: Type question in chat
            print(f"\n[6] Typing question: '{question}'")
            time.sleep(10)

            # Re-check inputs after hot button clicks
            chat_found = page.evaluate("""() => {
                // Look for textarea or text input (not gate)
                const candidates = document.querySelectorAll('textarea, input[type="text"]:not(#gate-input), .chat-input, [contenteditable="true"]');
                for (const el of candidates) {
                    const style = window.getComputedStyle(el);
                    if (style.display !== 'none' && style.visibility !== 'hidden') {
                        return {
                            found: true,
                            tag: el.tagName,
                            id: el.id,
                            placeholder: el.placeholder || '',
                            selector: el.id ? '#' + el.id : el.tagName.toLowerCase()
                        };
                    }
                }
                return { found: false };
            }""")

            if chat_found.get("found"):
                sel = chat_found["selector"]
                print(f"    Found chat input: {chat_found}")
                try:
                    if chat_found.get("id"):
                        page.click(f"#{chat_found['id']}")
                    else:
                        page.click(chat_found["tag"].lower())
                    page.wait_for_timeout(500)
                    page.keyboard.type(question, delay=40)
                    page.wait_for_timeout(1000)
                    page.keyboard.press("Enter")
                    results["question_asked"] = question
                    print(f"    Question submitted!")
                    page.wait_for_timeout(12000)

                    # Try to capture response
                    response = page.evaluate("""() => {
                        // Look for recent chat messages or response areas
                        const msgs = document.querySelectorAll('.message, .chat-message, .response, .ai-response, .chy-message, [data-message]');
                        if (msgs.length > 0) {
                            const last = msgs[msgs.length - 1];
                            return last.innerText ? last.innerText.substring(0, 300) : '';
                        }
                        return '';
                    }""")
                    if response:
                        results["question_response"] = response[:300]
                        print(f"    Response: {response[:200]}")
                    else:
                        print(f"    No response element found")
                except Exception as e:
                    print(f"    Error: {e}")
                    results["errors"].append(f"Chat error: {e}")
            else:
                print(f"    No chat input found on page")
                results["errors"].append("Chat input not found")

            # STEP 7: Schedule a Call
            print(f"\n[7] Checking 'Schedule a Call'...")
            time.sleep(10)

            sched_result = page.evaluate("""() => {
                const all = document.querySelectorAll('button, a, [role="button"]');
                for (const el of all) {
                    const text = (el.innerText || el.textContent || '').toLowerCase();
                    if (text.includes('schedule') || text.includes('book a call') || text.includes('calendly')) {
                        const style = window.getComputedStyle(el);
                        if (style.display !== 'none') {
                            el.click();
                            return { found: true, clicked: true, text: el.innerText.substring(0, 80) };
                        }
                    }
                }
                return { found: false };
            }""")

            if sched_result.get("clicked"):
                print(f"    Clicked: '{sched_result.get('text', '')}'")
                page.wait_for_timeout(5000)
                # Check for modal
                modal = page.evaluate("""() => {
                    const m = document.querySelectorAll('.modal, [role="dialog"], .popup, iframe[src*="calendly"], .calendly-inline-widget, .schedule-modal');
                    const visible = Array.from(m).filter(el => window.getComputedStyle(el).display !== 'none');
                    return { found: visible.length > 0, count: visible.length };
                }""")
                results["schedule_call_works"] = modal.get("found", False)
                print(f"    Modal appeared: {modal}")
            else:
                results["schedule_call_works"] = "Button not found"
                print(f"    Schedule button not found")

            # STEP 8: Summary
            tracking_msgs = [m for m in console_messages if any(kw in m.lower() for kw in [
                "track", "portal_entry", "portal_exit", "investor", "hot_button", "chat", "analytic"
            ])]
            results["tracking_events"] = tracking_msgs[:20]

            print(f"\n[8] Console & Tracking:")
            print(f"    Total console msgs: {len(console_messages)}")
            print(f"    Tracking-related: {len(tracking_msgs)}")
            for tm in tracking_msgs[:10]:
                print(f"      {tm[:200]}")
            print(f"    JS errors: {len(results['console_errors'])}")
            for ce in results["console_errors"][:5]:
                print(f"      {ce[:200]}")
            print(f"    Analytics requests: {len(network_requests)}")
            for nr in network_requests[:5]:
                print(f"      {nr[:150]}")

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
            print(f"\n{'='*40}")
            print(f"--- Waiting 15 seconds before next session ---")
            print(f"{'='*40}")
            time.sleep(15)

    print(f"\n\n{'='*70}")
    print(f"FINAL SUMMARY - ALL 3 SESSIONS")
    print(f"{'='*70}")

    for i, r in enumerate(all_results, 1):
        print(f"\n--- Session {i}: {r['investor']} ({r['code']}) ---")
        print(f"  Login:     {'SUCCESS' if r['login_success'] else 'FAILED'}")
        print(f"  Entrance:  {'COMPLETE' if r['entrance_complete'] else 'INCOMPLETE'}")
        hb_c = len([b for b in r['hot_buttons_clicked'] if b['clicked']])
        hb_t = len(r['hot_buttons_clicked'])
        print(f"  Hot btns:  {hb_c}/{hb_t} clicked")
        for b in r["hot_buttons_clicked"]:
            print(f"    - '{b['keyword']}': {'CLICKED' if b['clicked'] else 'NOT FOUND'}")
        if r["question_asked"]:
            print(f"  Question:  ASKED - '{r['question_asked'][:50]}'")
            if r.get("question_response"):
                print(f"  Response:  {r['question_response'][:100]}")
        else:
            print(f"  Question:  NOT ASKED")
        print(f"  Schedule:  {r['schedule_call_works']}")
        print(f"  Tracking:  {len(r.get('tracking_events', []))} events")
        print(f"  Analytics: {len(network_requests)} requests" if 'network_requests' in dir() else "")
        print(f"  Errors:    {len(r['errors'])}")
        for e in r["errors"]:
            print(f"    - {e[:150]}")
        print(f"  JS Errors: {len(r['console_errors'])}")
        for ce in r["console_errors"][:3]:
            print(f"    - {ce[:150]}")


if __name__ == "__main__":
    main()
