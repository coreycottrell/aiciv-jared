#!/usr/bin/env python3
"""
Single investor session against purebrain.ai/investment-opportunity/
Usage: python3 investor_qa_session.py <session_num> (1, 2, or 3)
Reduced waits for faster execution while still firing JS tracking.
"""

import time
import json
import sys
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
WAIT = 5  # seconds between actions (reduced from 10)


def run_session(idx):
    cfg = SESSIONS[idx]
    investor = cfg["investor"]
    code = cfg["code"]
    hot_kw = cfg["hot_buttons"]
    question = cfg["question"]

    print(f"SESSION {idx+1}: {investor} ({code})")
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
        page.on("request", lambda r: analytics_reqs.append(r.url) if any(k in r.url.lower() for k in ["gtag", "collect", "analytics", "pixel", "track"]) else None)

        try:
            # 1. Navigate
            print(f"\n[1] Navigate")
            page.goto(URL, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(4000)
            print(f"    Title: {page.title()}")

            # 2. Enter code
            print(f"\n[2] Enter code: {code}")
            page.fill("#gate-input", code)
            page.wait_for_timeout(1000)

            # 3. Submit
            print(f"\n[3] Submit gate")
            page.evaluate("document.getElementById('gate-btn').click()")
            page.wait_for_timeout(5000)

            # Check gate state
            gate_gone = page.evaluate("""() => {
                const el = document.querySelector('.entrance-layer.active');
                return !!el;
            }""")
            print(f"    Entrance layer active: {gate_gone}")
            if gate_gone:
                print(f"    LOGIN SUCCESS")
            else:
                print(f"    Trying Enter key...")
                page.keyboard.press("Enter")
                page.wait_for_timeout(3000)
                gate_gone = page.evaluate("() => !!document.querySelector('.entrance-layer.active')")
                print(f"    Entrance layer after Enter: {gate_gone}")

            # 4. Navigate entrance layers
            print(f"\n[4] Entrance layers")
            for step in range(15):
                page.wait_for_timeout(2000)
                result = page.evaluate("""() => {
                    const active = document.querySelector('.entrance-layer.active');
                    if (!active) return { done: true };

                    // Find next/enter button
                    const btns = active.querySelectorAll('button');
                    for (const btn of btns) {
                        const s = window.getComputedStyle(btn);
                        const text = btn.innerText.toLowerCase();
                        if (s.display !== 'none' && parseFloat(s.opacity) > 0.2 && (text.includes('next') || text.includes('enter'))) {
                            btn.click();
                            return { done: false, clicked: btn.innerText.trim(), layerId: active.id };
                        }
                    }
                    return { done: false, noButton: true, layerId: active.id };
                }""")
                if result.get("done"):
                    print(f"    Entrance complete at step {step}")
                    break
                elif result.get("clicked"):
                    print(f"    Step {step}: Clicked '{result['clicked']}' on {result.get('layerId','?')}")
                else:
                    print(f"    Step {step}: No button found on {result.get('layerId','?')}, clicking layer")
                    page.evaluate("""() => {
                        const active = document.querySelector('.entrance-layer.active');
                        if (active) active.click();
                    }""")

            page.wait_for_timeout(3000)

            # 5. Analyze main interface
            print(f"\n[5] Main interface analysis")
            iface = page.evaluate("""() => {
                const allBtns = document.querySelectorAll('button, [role="button"], .hot-button, .question-btn, [data-question]');
                const btns = [];
                for (const b of allBtns) {
                    const s = window.getComputedStyle(b);
                    if (s.display !== 'none' && s.visibility !== 'hidden' && b.innerText.trim().length > 0) {
                        btns.push({
                            text: b.innerText.substring(0, 100).trim(),
                            id: b.id,
                            cls: b.className.toString().substring(0, 60),
                            tag: b.tagName
                        });
                    }
                }
                const inputs = [];
                for (const el of document.querySelectorAll('textarea, input[type="text"]:not(#gate-input), [contenteditable="true"]')) {
                    const s = window.getComputedStyle(el);
                    if (s.display !== 'none') {
                        inputs.push({ tag: el.tagName, id: el.id, ph: el.placeholder || '', type: el.type || '' });
                    }
                }
                return { buttons: btns, inputs: inputs };
            }""")
            print(f"    Visible buttons ({len(iface['buttons'])}):")
            for b in iface["buttons"][:30]:
                print(f"      [{b['tag']}] '{b['text'][:70]}' id={b['id']} cls={b['cls'][:30]}")
            print(f"    Visible inputs ({len(iface['inputs'])}):")
            for inp in iface["inputs"]:
                print(f"      [{inp['tag']}] id={inp['id']} type={inp['type']} ph='{inp['ph']}'")

            # 6. Click hot buttons
            print(f"\n[6] Hot buttons")
            for kw in hot_kw:
                time.sleep(WAIT)
                result = page.evaluate(f"""() => {{
                    const all = document.querySelectorAll('button, [role="button"], .hot-button, .question-btn, [data-question], span[onclick], div[onclick]');
                    for (const el of all) {{
                        const text = (el.innerText || el.textContent || '').toLowerCase();
                        const s = window.getComputedStyle(el);
                        if (text.includes('{kw.lower()}') && s.display !== 'none' && s.visibility !== 'hidden') {{
                            el.click();
                            return {{found: true, text: el.innerText.substring(0, 80)}};
                        }}
                    }}
                    return {{found: false}};
                }}""")
                if result.get("found"):
                    print(f"    CLICKED: '{result['text'][:60]}'")
                    page.wait_for_timeout(6000)
                else:
                    print(f"    NOT FOUND: '{kw}'")
                    # Try broader search
                    try:
                        page.click(f"text=/{kw}/i", timeout=3000)
                        print(f"    CLICKED via playwright selector")
                        page.wait_for_timeout(6000)
                    except:
                        print(f"    FAILED to find '{kw}'")

            # 7. Type question
            print(f"\n[7] Chat question: '{question}'")
            time.sleep(WAIT)
            chat = page.evaluate("""() => {
                for (const el of document.querySelectorAll('textarea, input[type="text"]:not(#gate-input), [contenteditable="true"]')) {
                    const s = window.getComputedStyle(el);
                    if (s.display !== 'none' && s.visibility !== 'hidden') {
                        el.focus();
                        return { found: true, tag: el.tagName, id: el.id, ph: el.placeholder || '' };
                    }
                }
                return { found: false };
            }""")
            if chat.get("found"):
                print(f"    Found: {chat}")
                if chat.get("id"):
                    page.click(f"#{chat['id']}")
                else:
                    page.click(chat["tag"].lower() + ":not(#gate-input)")
                page.keyboard.type(question, delay=30)
                page.wait_for_timeout(1000)
                page.keyboard.press("Enter")
                print(f"    Question submitted!")
                page.wait_for_timeout(8000)
                # Get response
                resp = page.evaluate("""() => {
                    const msgs = document.querySelectorAll('.message, .chat-message, .response, .ai-response, .chy-message');
                    if (msgs.length) return msgs[msgs.length-1].innerText.substring(0, 300);
                    return '';
                }""")
                if resp:
                    print(f"    Response: {resp[:200]}")
            else:
                print(f"    No chat input found")

            # 8. Schedule a Call
            print(f"\n[8] Schedule a Call")
            time.sleep(WAIT)
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
                print(f"    Modal appeared: {modal}")
            else:
                print(f"    Not found")

            # 9. Tracking summary
            print(f"\n[9] Tracking & Console")
            track = [m for m in console_msgs if any(k in m.lower() for k in ["portal", "investor", "track", "event", "hot_button"])]
            print(f"    Console msgs: {len(console_msgs)}, tracking: {len(track)}, JS errors: {len(js_errors)}")
            print(f"    Analytics requests: {len(analytics_reqs)}")
            for t in track[:5]:
                print(f"      {t[:150]}")
            for e in js_errors[:3]:
                print(f"      JS ERROR: {e[:150]}")
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
    print(f"SESSION {idx+1} COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    idx = int(sys.argv[1]) - 1 if len(sys.argv) > 1 else 0
    run_session(idx)
