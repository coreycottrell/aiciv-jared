#!/usr/bin/env python3
"""Session 3 fix: Elad Gil - escape apostrophes in button text."""

import time
import json
from playwright.sync_api import sync_playwright

URL = "https://purebrain.ai/investment-opportunity/"
INVESTOR = "Elad Gil"
CODE = "GIL2026"
# Button texts with apostrophe escaped
HOT_BUTTONS = [
    ("Who\\'s on the team?", "Who is on the team?"),
    ("Revenue streams?", "What are the revenue streams?"),
]
QUESTION = "What is the current monthly recurring revenue?"


def run():
    print(f"\nSESSION 3: {INVESTOR} ({CODE})")
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
        page.on("request", lambda r: analytics_reqs.append(r.url) if any(k in r.url.lower() for k in ["gtag", "collect", "analytics", "pixel"]) else None)

        try:
            # 1. Navigate
            print(f"\n[1] Navigate")
            page.goto(URL, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(4000)
            print(f"    Title: {page.title()}")

            # 2. Enter code
            print(f"\n[2] Enter code: {CODE}")
            page.evaluate(f"() => {{ document.getElementById('gate-input').value = '{CODE}'; document.getElementById('gate-input').dispatchEvent(new Event('input', {{ bubbles: true }})); }}")
            page.wait_for_timeout(1000)

            # 3. Submit
            print(f"\n[3] Submit")
            page.evaluate("() => document.getElementById('gate-btn').click()")
            page.wait_for_timeout(4000)
            gate_ok = page.evaluate("() => !!document.querySelector('.entrance-layer.active')")
            print(f"    LOGIN: {'SUCCESS' if gate_ok else 'FAILED'}")

            # 4. Entrance layers
            print(f"\n[4] Entrance layers")
            for step in range(20):
                page.wait_for_timeout(2500)
                result = page.evaluate("""() => {
                    const active = document.querySelector('.entrance-layer.active');
                    if (!active) return { done: true };
                    const btns = active.querySelectorAll('.ent-nav-btn');
                    for (const btn of btns) {
                        const s = window.getComputedStyle(btn);
                        if (s.display !== 'none' && parseFloat(s.opacity) > 0.3 && btn.classList.contains('visible')) {
                            btn.click();
                            return { done: false, clicked: btn.innerText.trim(), layer: active.id };
                        }
                    }
                    return { done: false, waiting: true, layer: active.id };
                }""")
                if result.get("done"):
                    print(f"    Entrance complete! (step {step})")
                    break
                elif result.get("clicked"):
                    print(f"    [{result['layer']}] Clicked '{result['clicked']}'")

            page.wait_for_timeout(3000)

            # 5. Hot buttons - use argument passing instead of string interpolation
            print(f"\n[5] Hot buttons")
            btn_texts_to_click = ["Who's on the team?", "Revenue streams?"]
            btn_labels = ["Who is on the team?", "What are the revenue streams?"]

            for actual, label in zip(btn_texts_to_click, btn_labels):
                time.sleep(5)

                # Close info pane if open
                page.evaluate("""() => {
                    const close = document.getElementById('info-pane-close');
                    if (close) {
                        const overlay = document.getElementById('info-pane-overlay');
                        if (overlay && overlay.classList.contains('active')) close.click();
                    }
                }""")
                page.wait_for_timeout(1000)

                # Pass button text as argument (avoids quote escaping issues)
                result = page.evaluate("""(targetText) => {
                    const btns = document.querySelectorAll('.quick-btn');
                    for (const btn of btns) {
                        if (btn.innerText.trim() === targetText) {
                            btn.click();
                            return { found: true, text: btn.innerText.trim() };
                        }
                    }
                    return { found: false };
                }""", actual)

                if result.get("found"):
                    print(f"    CLICKED: '{result['text']}' (requested: '{label}')")
                    page.wait_for_timeout(6000)

                    response = page.evaluate("""() => {
                        const pane = document.getElementById('info-pane-overlay');
                        if (pane && pane.classList.contains('active')) {
                            return pane.innerText.substring(0, 400);
                        }
                        return '';
                    }""")
                    if response:
                        print(f"    Response: {response[:200]}")
                else:
                    print(f"    NOT FOUND: '{actual}'")

            # Close info pane
            page.evaluate("() => { const c = document.getElementById('info-pane-close'); if (c) c.click(); }")
            page.wait_for_timeout(2000)

            # 6. Chat
            print(f"\n[6] Chat: '{QUESTION}'")
            time.sleep(5)

            page.evaluate("""(q) => {
                const input = document.getElementById('text-input');
                if (input) {
                    input.focus();
                    input.value = q;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }""", QUESTION)
            page.wait_for_timeout(500)

            page.evaluate("""() => {
                const input = document.getElementById('text-input');
                if (input) {
                    const ev = new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true });
                    input.dispatchEvent(ev);
                    const sendBtn = document.querySelector('.send-btn, #send-btn, button[type="submit"]');
                    if (sendBtn) sendBtn.click();
                }
            }""")
            print(f"    Question submitted")
            page.wait_for_timeout(10000)

            response = page.evaluate("""() => {
                const msgs = document.querySelectorAll('.message, .chat-message, .ai-response, .chy-message');
                if (msgs.length) return msgs[msgs.length-1].innerText.substring(0, 300);
                return '';
            }""")
            if response:
                print(f"    Response: {response[:200]}")
            else:
                print(f"    No chat response element found")

            # 7. Schedule a Call
            print(f"\n[7] Schedule a Call")
            time.sleep(5)
            page.evaluate("() => { const c = document.getElementById('info-pane-close'); if (c) c.click(); }")
            page.wait_for_timeout(1000)

            sched = page.evaluate("""() => {
                const all = document.querySelectorAll('button, a, [role="button"]');
                for (const el of all) {
                    const text = (el.innerText || '').toLowerCase();
                    const s = window.getComputedStyle(el);
                    if ((text.includes('schedule') || text.includes('book')) && s.display !== 'none') {
                        el.click();
                        return { found: true, text: el.innerText.substring(0, 60) };
                    }
                }
                return { found: false };
            }""")
            if sched.get("found"):
                print(f"    Clicked: '{sched['text']}'")
                page.wait_for_timeout(3000)
            else:
                print(f"    Not found")

            # 8. Tracking
            print(f"\n[8] Tracking & Console")
            print(f"    Console: {len(console_msgs)} total, JS errors: {len(js_errors)}")
            print(f"    Analytics requests: {len(analytics_reqs)}")
            for a in analytics_reqs[:5]:
                print(f"      REQ: {a[:120]}")
            for e in js_errors[:3]:
                print(f"      ERROR: {e[:150]}")

        except Exception as e:
            print(f"\n  FATAL: {e}")
            import traceback
            traceback.print_exc()
        finally:
            page.wait_for_timeout(3000)
            browser.close()

    print(f"\n{'='*60}")
    print(f"SESSION 3 COMPLETE: {INVESTOR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    run()
