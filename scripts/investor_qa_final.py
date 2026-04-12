#!/usr/bin/env python3
"""
Final investor portal QA - all 3 sessions.
Known page structure:
- Gate: #gate-input (password), #gate-btn (submit)
- Entrance: 4 layers (.entrance-layer), Next/Enter buttons with fade-in delays
- Main: quick-btn buttons, #text-input for chat
- Info pane overlay appears after button click, close with #info-pane-close
"""

import time
import json
import sys
from playwright.sync_api import sync_playwright

# Map requested buttons to ACTUAL button text on the page
SESSIONS = [
    {
        "investor": "Edward Lando",
        "code": "LANDO2026",
        "hot_buttons": [
            ("The raise?", "When do we break even?"),  # actual_text, requested_text
            ("Competitive advantage?", "What is the competitive advantage?"),
        ],
        "question": "What is your 5-year vision for Pure Technology?"
    },
    {
        "investor": "David Ross",
        "code": "ROSS2026",
        "hot_buttons": [
            ("Use of funds?", "How will you use the funds?"),
            ("Revenue projections?", "What are the revenue projections?"),
        ],
        "question": "How does the AI agent architecture scale with more clients?"
    },
    {
        "investor": "Elad Gil",
        "code": "GIL2026",
        "hot_buttons": [
            ("Who's on the team?", "Who is on the team?"),
            ("Revenue streams?", "What are the revenue streams?"),
        ],
        "question": "What is the current monthly recurring revenue?"
    },
]

URL = "https://purebrain.ai/investment-opportunity/"


def run_session(idx):
    cfg = SESSIONS[idx]
    investor = cfg["investor"]
    code = cfg["code"]
    hot_buttons = cfg["hot_buttons"]
    question = cfg["question"]

    print(f"\nSESSION {idx+1}: {investor} ({code})")
    print(f"{'='*60}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"
        )
        page = ctx.new_page()

        console_msgs = []
        js_errors = []
        analytics_reqs = []
        page.on("console", lambda m: console_msgs.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda e: js_errors.append(str(e)))
        page.on("request", lambda r: analytics_reqs.append(r.url) if any(k in r.url.lower() for k in ["gtag", "collect", "analytics", "pixel", "event"]) else None)

        try:
            # 1. Navigate
            print(f"\n[1] Navigate to {URL}")
            page.goto(URL, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(4000)
            print(f"    Title: {page.title()}")

            # 2. Enter code via JS (avoids any overlay issues)
            print(f"\n[2] Enter code: {code}")
            page.evaluate(f"""() => {{
                const input = document.getElementById('gate-input');
                input.value = '{code}';
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}""")
            page.wait_for_timeout(1000)
            print(f"    Code set in #gate-input")

            # 3. Submit gate
            print(f"\n[3] Submit gate (#gate-btn)")
            page.evaluate("() => document.getElementById('gate-btn').click()")
            page.wait_for_timeout(4000)

            gate_ok = page.evaluate("() => !!document.querySelector('.entrance-layer.active')")
            if gate_ok:
                print(f"    LOGIN SUCCESS - entrance layers activated")
            else:
                print(f"    WARNING: No entrance layer active, retrying...")
                # Try typing normally and pressing Enter
                page.fill("#gate-input", code)
                page.press("#gate-input", "Enter")
                page.wait_for_timeout(4000)
                gate_ok = page.evaluate("() => !!document.querySelector('.entrance-layer.active')")
                print(f"    Retry result: {gate_ok}")

            # 4. Navigate entrance layers (4 layers)
            print(f"\n[4] Entrance layers")
            for step in range(20):
                page.wait_for_timeout(2500)

                result = page.evaluate("""() => {
                    const active = document.querySelector('.entrance-layer.active');
                    if (!active) return { done: true };

                    // Find nav button (may need to wait for fade-in)
                    const btns = active.querySelectorAll('.ent-nav-btn');
                    for (const btn of btns) {
                        const s = window.getComputedStyle(btn);
                        // Check if button has faded in enough to be clickable
                        if (s.display !== 'none' && parseFloat(s.opacity) > 0.3 && btn.classList.contains('visible')) {
                            btn.click();
                            return { done: false, clicked: btn.innerText.trim(), layer: active.id };
                        }
                    }
                    // Button not yet visible - wait for fade-in
                    return { done: false, waiting: true, layer: active.id };
                }""")

                if result.get("done"):
                    print(f"    Entrance complete! (step {step})")
                    break
                elif result.get("clicked"):
                    print(f"    [{result['layer']}] Clicked '{result['clicked']}'")
                elif result.get("waiting"):
                    pass  # Button still fading in, loop will retry

            page.wait_for_timeout(3000)

            # 5. Click hot buttons
            print(f"\n[5] Hot buttons")
            for actual_text, requested_text in hot_buttons:
                time.sleep(5)  # Human-like wait

                # First close any open info pane
                page.evaluate("""() => {
                    const close = document.getElementById('info-pane-close');
                    if (close) {
                        const overlay = document.getElementById('info-pane-overlay');
                        if (overlay && overlay.classList.contains('active')) {
                            close.click();
                        }
                    }
                }""")
                page.wait_for_timeout(1000)

                # Click the button by exact text match
                result = page.evaluate(f"""() => {{
                    const btns = document.querySelectorAll('.quick-btn');
                    for (const btn of btns) {{
                        if (btn.innerText.trim() === '{actual_text}') {{
                            btn.click();
                            return {{ found: true, text: btn.innerText.trim() }};
                        }}
                    }}
                    return {{ found: false }};
                }}""")

                if result.get("found"):
                    print(f"    CLICKED: '{result['text']}' (requested: '{requested_text}')")
                    page.wait_for_timeout(6000)

                    # Read the info pane response
                    response = page.evaluate("""() => {
                        const pane = document.getElementById('info-pane-overlay');
                        if (pane && pane.classList.contains('active')) {
                            const content = pane.querySelector('.info-pane-content, .info-content, #info-pane-content');
                            if (content) return content.innerText.substring(0, 400);
                            return pane.innerText.substring(0, 400);
                        }
                        return '';
                    }""")
                    if response:
                        print(f"    Response (first 200 chars): {response[:200]}")
                    else:
                        print(f"    No info pane response detected")
                else:
                    print(f"    NOT FOUND: '{actual_text}'")

            # Close info pane before chat
            page.evaluate("""() => {
                const close = document.getElementById('info-pane-close');
                if (close) close.click();
            }""")
            page.wait_for_timeout(2000)

            # 6. Type question in chat
            print(f"\n[6] Chat: '{question}'")
            time.sleep(5)

            # Use JS to focus and type (avoids overlay click interception)
            typed = page.evaluate(f"""() => {{
                const input = document.getElementById('text-input');
                if (!input) return {{ found: false }};
                input.focus();
                input.value = `{question}`;
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return {{ found: true }};
            }}""")

            if typed.get("found"):
                print(f"    Text set in #text-input")
                # Trigger Enter via JS to submit
                page.evaluate("""() => {
                    const input = document.getElementById('text-input');
                    const event = new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true });
                    input.dispatchEvent(event);
                    // Also try form submit or click send button
                    const form = input.closest('form');
                    if (form) form.dispatchEvent(new Event('submit', { bubbles: true }));
                    const sendBtn = document.querySelector('.send-btn, #send-btn, button[type="submit"]');
                    if (sendBtn) sendBtn.click();
                }""")
                print(f"    Enter dispatched")
                page.wait_for_timeout(10000)

                # Check for response
                response = page.evaluate("""() => {
                    const msgs = document.querySelectorAll('.message, .chat-message, .ai-response, .chy-message, .response-message, .chat-bubble');
                    if (msgs.length > 0) {
                        return msgs[msgs.length - 1].innerText.substring(0, 300);
                    }
                    // Try getting chat container text
                    const container = document.querySelector('.chat-messages, .messages-container, #chat-messages, #messages');
                    if (container) return container.innerText.substring(container.innerText.length - 300);
                    return '';
                }""")
                if response:
                    print(f"    Response: {response[:200]}")
                else:
                    print(f"    No chat response element found")
            else:
                print(f"    Chat input #text-input not found")

            # 7. Schedule a Call
            print(f"\n[7] Schedule a Call")
            time.sleep(5)

            # Close any overlay first
            page.evaluate("""() => {
                const close = document.getElementById('info-pane-close');
                if (close) close.click();
            }""")
            page.wait_for_timeout(1000)

            sched = page.evaluate("""() => {
                const all = document.querySelectorAll('button, a, [role="button"]');
                for (const el of all) {
                    const text = (el.innerText || '').toLowerCase();
                    const s = window.getComputedStyle(el);
                    if ((text.includes('schedule') || text.includes('book') || text.includes('calendly')) && s.display !== 'none') {
                        el.click();
                        return { found: true, text: el.innerText.substring(0, 60) };
                    }
                }
                return { found: false };
            }""")
            if sched.get("found"):
                print(f"    Clicked: '{sched['text']}'")
                page.wait_for_timeout(3000)
                modal = page.evaluate("""() => {
                    const m = document.querySelectorAll('.modal, [role="dialog"], iframe[src*="calendly"], .calendly-inline-widget, .schedule-modal');
                    return Array.from(m).filter(el => window.getComputedStyle(el).display !== 'none').length > 0;
                }""")
                print(f"    Modal/widget appeared: {modal}")
            else:
                print(f"    Schedule button not found")

            # 8. Tracking summary
            print(f"\n[8] Tracking & Console")
            track = [m for m in console_msgs if any(k in m.lower() for k in ["portal", "investor", "track", "event", "hot_button", "chat_message", "question"])]
            print(f"    Console: {len(console_msgs)} total, {len(track)} tracking, {len(js_errors)} errors")
            print(f"    Analytics HTTP requests: {len(analytics_reqs)}")
            for t in track[:8]:
                print(f"      TRACK: {t[:200]}")
            for e in js_errors[:3]:
                print(f"      ERROR: {e[:200]}")
            for a in analytics_reqs[:5]:
                print(f"      REQ: {a[:120]}")

        except Exception as e:
            print(f"\n  FATAL: {e}")
            import traceback
            traceback.print_exc()
        finally:
            page.wait_for_timeout(3000)
            browser.close()

    print(f"\n{'='*60}")
    print(f"SESSION {idx+1} COMPLETE: {investor}")
    print(f"{'='*60}")


def main():
    for i in range(3):
        run_session(i)
        if i < 2:
            print(f"\n--- 10 second pause between sessions ---")
            time.sleep(10)

    print(f"\n\n{'='*60}")
    print(f"ALL 3 SESSIONS COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_session(int(sys.argv[1]) - 1)
    else:
        main()
