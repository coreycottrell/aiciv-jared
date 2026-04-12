#!/usr/bin/env python3
"""
E2E Brain Stream v5 FINAL: Clean capture of the complete end state.

KEY FINDINGS from prior runs:
1. Sandbox-3 end state = "Welcome to the Family!" card inside #ptc-messages
2. The #pb-brain-stream-wrapper is an Elementor element on the UNDERLYING PAGE
   - Covered by the fixed chatbox (position:fixed, z-index:999999)
   - In the real (non-bypass) full Q&A flow, there MAY be a different brain stream
     button that appears inside #ptc-messages
3. In sandbox-3 the Welcome card contains the brain stream reference:
   "Your AI's Brain Stream (portal) will be ready for you to log in."

This script:
- Runs the FULL sandbox-3 flow (bypass through name only)
- After orange CTA click, searches for ANY brain stream element INSIDE the chatbox
- Captures the Welcome card fully scrolled (shows the timeline with Brain Stream ref)
- Also captures the state from the REAL non-bypass Q&A flow to find the actual button
"""

import asyncio
import os
import subprocess
import time

OUTPUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/e2e-sandbox3-payment-to-brain-stream"
TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"
URL = "https://purebrain.ai/pay-test-sandbox-3/"
PASSWORD = "PureBrain.ai253443$$$"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def tg(msg):
    try:
        subprocess.Popen([TG_SEND, msg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[TG] {msg}")
    except:
        pass


def tg_photo(path, caption):
    try:
        subprocess.Popen([TG_SEND, "--photo", path, caption], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[TG-PHOTO] {caption}")
    except:
        pass


async def run():
    from playwright.async_api import async_playwright

    tg("E2E BS v5 FINAL: Definitive brain stream capture")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()

        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        async def click_text(fragments, timeout=12):
            deadline = time.time() + timeout
            while time.time() < deadline:
                r = await page.evaluate(f"""() => {{
                    var frags = {repr(fragments)};
                    var els = Array.from(document.querySelectorAll('button, a'));
                    for (var f of frags) {{
                        var el = els.find(e => e.textContent.toLowerCase().includes(f.toLowerCase())
                                          && e.offsetParent !== null && !e.disabled);
                        if (el) {{ el.click(); return el.textContent.trim(); }}
                    }}
                    return null;
                }}""")
                if r:
                    print(f"[CLICK] '{r}'")
                    return r
                await asyncio.sleep(1)
            return None

        # === SPEED RUN: Pre-payment ===
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        # Password
        pw = await page.query_selector("input[type='password']")
        if pw:
            await pw.click()
            await pw.type(PASSWORD)
            sub = await page.query_selector("input[type='submit'], button[type='submit']")
            if sub:
                await sub.click()
            else:
                await pw.press("Enter")
            await asyncio.sleep(6)

        try:
            await page.wait_for_load_state("networkidle", timeout=8000)
        except:
            pass
        await asyncio.sleep(3)

        # Awaken + Begin
        await click_text(["awaken your pure brain", "awaken"])
        await asyncio.sleep(4)
        await click_text(["begin awakening", "begin"])
        await asyncio.sleep(4)

        # Bypass the name question
        await page.evaluate("""() => {
            var sels = ["input[type='text']", "textarea"];
            for (var sel of sels) {
                var inp = document.querySelector(sel);
                if (inp) {
                    inp.value = 'pb-full-bypass';
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                    inp.dispatchEvent(new KeyboardEvent('keypress', {key: 'Enter', keyCode: 13, bubbles: true}));
                    var allBtns = Array.from(document.querySelectorAll('button'));
                    var sb = allBtns.find(b => b.textContent.trim().toLowerCase() === 'send' ||
                                              b.id.includes('send') || b.className.includes('send'));
                    if (sb) sb.click();
                    return;
                }
            }
        }""")
        await asyncio.sleep(6)

        # Navigate to payment section
        await click_text(["discover"], timeout=8)
        await asyncio.sleep(4)
        await click_text(["see what", "can do"], timeout=6)
        await asyncio.sleep(3)
        await click_text(["can do ->", "can do", "enter"], timeout=4)
        await asyncio.sleep(5)

        # Simulate payment
        order_id = f"E2E-BS5-{int(time.time())}"
        await page.evaluate(f"""() => {{
            if (typeof window.onPaymentComplete === 'function')
                window.onPaymentComplete('Awakened', '{order_id}', {{}});
        }}""")
        await asyncio.sleep(8)

        # Wait for chatbox
        for i in range(20):
            ok = await page.evaluate("""() => {
                var r = document.getElementById('ptc-input-row');
                return r && getComputedStyle(r).display !== 'none';
            }""")
            if ok:
                print(f"[CHATBOX] Ready at {i}s")
                break
            await asyncio.sleep(1)

        # Q&A answers
        for answer in ["Alex Carter", "alex.carter.e2e@example.com", "Pure Technology", "CTO",
                        "Build the most efficient AI research and reporting pipeline"]:
            for _ in range(15):
                rdy = await page.evaluate("""() => {
                    var r = document.getElementById('ptc-input-row');
                    return r && getComputedStyle(r).display !== 'none';
                }""")
                if rdy:
                    break
                await asyncio.sleep(1)
            await page.evaluate(f"""() => {{
                var inp = document.getElementById('ptc-input');
                if (inp) {{
                    inp.disabled = false; inp.readOnly = false;
                    inp.value = {repr(answer)};
                    inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                    var btn = document.getElementById('ptc-send-btn');
                    if (btn && !btn.disabled) btn.click();
                }}
            }}""")
            print(f"[QA] '{answer[:40]}'")
            await asyncio.sleep(6)

        # Slides
        for s in range(10):
            r = await click_text(["show me more", "show more"], timeout=4)
            if not r:
                break
            await asyncio.sleep(2)

        # Incredible CTA
        await click_text(["incredible", "let's go"], timeout=6)
        await asyncio.sleep(3)

        # Orange CTA - click it
        orange = await page.evaluate("""() => {
            var btn = document.getElementById('ptc-cta-btn');
            if (btn) { btn.click(); return btn.textContent.trim(); }
            var btns = Array.from(document.querySelectorAll('button, a'));
            btn = btns.find(b => b.textContent.toLowerCase().includes('ready') && b.offsetParent);
            if (btn) { btn.click(); return btn.textContent.trim(); }
            return null;
        }""")
        print(f"[ORANGE CTA] clicked: '{orange}'")
        await asyncio.sleep(10)  # Wait for welcome card + all content to fully render

        # === PHASE F: BRAIN STREAM CAPTURE ===
        tg("E2E BS v5: Phase F - brain stream capture starting")
        print("\n=== PHASE F: BRAIN STREAM CAPTURE ===")

        # Step 1: Full DOM search for ANY brain stream related element INSIDE the chatbox
        brain_elements = await page.evaluate("""() => {
            var container = document.getElementById('pay-test-post-payment');
            if (!container) return {error: 'no container'};

            // Search ALL elements inside container for brain stream text
            var all = Array.from(container.querySelectorAll('*'));
            var found = [];
            for (var el of all) {
                var text = el.textContent.trim();
                if (text.toLowerCase().includes('brain stream') ||
                    text.toLowerCase().includes('enter') ||
                    el.id.toLowerCase().includes('brain')) {
                    var r = el.getBoundingClientRect();
                    found.push({
                        tag: el.tagName,
                        id: el.id,
                        class: el.className ? el.className.substring(0, 50) : '',
                        text: text.substring(0, 80),
                        rect: {top: Math.round(r.top), bottom: Math.round(r.bottom),
                               left: Math.round(r.left), right: Math.round(r.right)},
                        opacity: getComputedStyle(el).opacity,
                        display: getComputedStyle(el).display,
                        pointerEvents: getComputedStyle(el).pointerEvents
                    });
                }
            }
            return {count: found.length, elements: found.slice(0, 20)};
        }""")
        print(f"\n[BRAIN ELEMENTS in chatbox] count={brain_elements.get('count')}")
        for el in brain_elements.get('elements', []):
            print(f"  {el['tag']}#{el['id']} | text='{el['text'][:60]}' | rect={el['rect']}")

        # Step 2: Check the welcome card specifically
        welcome_info = await page.evaluate("""() => {
            var msgs = document.getElementById('ptc-messages');
            if (!msgs) return {error: 'no msgs'};

            // Find the welcome card inside messages
            var cards = msgs.querySelectorAll('.ptc-welcome-card, [class*=welcome]');
            var welcomeEl = cards.length > 0 ? cards[0] : null;

            // Also find via text
            if (!welcomeEl) {
                var all = Array.from(msgs.querySelectorAll('*'));
                welcomeEl = all.find(e => e.textContent.includes('Welcome to the Family'));
                while (welcomeEl && welcomeEl.children.length > 3) {
                    // Narrow down to the card container
                    welcomeEl = welcomeEl.querySelector('[class*=welcome], [class*=card]') || welcomeEl;
                    break;
                }
            }

            // Scroll msgs so welcome card is fully visible
            if (msgs) {
                // First scroll to see the welcome card centered
                var targetScroll = msgs.scrollHeight - msgs.clientHeight;
                msgs.scrollTop = targetScroll;
            }

            return {
                msgsScrollTop: msgs.scrollTop,
                msgsScrollHeight: msgs.scrollHeight,
                msgsClientHeight: msgs.clientHeight,
                welcomeFound: !!welcomeEl,
                welcomeRect: welcomeEl ? (function() {
                    var r = welcomeEl.getBoundingClientRect();
                    return {top: Math.round(r.top), bottom: Math.round(r.bottom),
                            left: Math.round(r.left), right: Math.round(r.right),
                            height: Math.round(r.height)};
                })() : null
            };
        }""")
        print(f"\n[WELCOME CARD] {welcome_info}")
        await asyncio.sleep(1)

        # F01: Full screenshot after orange CTA - messages scrolled to bottom
        f01 = f"{OUTPUT_DIR}/F01-FINAL-brain-stream-full-state.png"
        await page.screenshot(path=f01)
        print(f"[SS] F01: {f01}")
        tg_photo(f01, "F01-FINAL: Full chatbox state after orange CTA - brain stream end state")

        # Step 3: Now scroll to show Welcome card FULLY
        await page.evaluate("""() => {
            var msgs = document.getElementById('ptc-messages');
            if (!msgs) return;

            // Find welcome card by text
            var all = Array.from(msgs.querySelectorAll('*'));
            var welcomeStart = all.find(e => e.textContent.trim() === 'Welcome to the Family!');
            if (welcomeStart) {
                // Scroll so this element is at top of view
                var parentCard = welcomeStart.closest('[class*=welcome], [class*=card], .ptc-bubble') || welcomeStart.parentElement;
                parentCard.scrollIntoView({behavior: 'instant', block: 'center'});
            } else {
                // Fallback: scroll to show last third of messages
                msgs.scrollTop = msgs.scrollHeight - (msgs.clientHeight * 0.3);
            }
        }""")
        await asyncio.sleep(1)

        # F02: Welcome card centered
        f02 = f"{OUTPUT_DIR}/F02-FINAL-welcome-card-centered.png"
        await page.screenshot(path=f02)
        print(f"[SS] F02: {f02}")
        tg_photo(f02, "F02-FINAL: Welcome card centered - shows Brain Stream timeline")

        # Step 4: Scroll further to show the FULL Welcome card (all timeline items)
        scroll_result = await page.evaluate("""() => {
            var msgs = document.getElementById('ptc-messages');
            if (!msgs) return 'no msgs';

            // Find "Next 5 mins" element which contains Brain Stream text
            var all = Array.from(msgs.querySelectorAll('*'));
            var brainStreamEl = all.find(e =>
                e.textContent.includes("Brain Stream") &&
                e.textContent.includes("portal")
            );
            if (brainStreamEl) {
                brainStreamEl.scrollIntoView({behavior: 'instant', block: 'center'});
                var r = brainStreamEl.getBoundingClientRect();
                return {found: true, rect: {top: Math.round(r.top), bottom: Math.round(r.bottom)},
                        text: brainStreamEl.textContent.trim().substring(0, 100)};
            }
            return {found: false};
        }""")
        print(f"\n[BRAIN STREAM TEXT ELEMENT] {scroll_result}")
        await asyncio.sleep(1)

        # F03: Brain Stream timeline item visible
        f03 = f"{OUTPUT_DIR}/F03-FINAL-brain-stream-timeline-visible.png"
        await page.screenshot(path=f03)
        print(f"[SS] F03: {f03}")
        tg_photo(f03, f"F03-FINAL: Brain Stream timeline item visible. Found={scroll_result.get('found')}")

        # Step 5: Check the "Learn more" button state and input disabled state
        final_state = await page.evaluate("""() => {
            var msgs = document.getElementById('ptc-messages');
            var inp = document.getElementById('ptc-input');
            var send = document.getElementById('ptc-send-btn');
            var learnBtn = document.querySelector('.ptc-welcome-btn, [class*=welcome-btn]');
            if (!learnBtn) {
                var allBtns = Array.from(document.querySelectorAll('button, a'));
                learnBtn = allBtns.find(b => b.textContent.includes('Learn more'));
            }

            return {
                input: {
                    disabled: inp ? inp.disabled : null,
                    placeholder: inp ? inp.placeholder : null,
                    readOnly: inp ? inp.readOnly : null
                },
                send: {
                    disabled: send ? send.disabled : null,
                    opacity: send ? getComputedStyle(send).opacity : null
                },
                learnBtn: learnBtn ? {
                    text: learnBtn.textContent.trim(),
                    opacity: getComputedStyle(learnBtn).opacity,
                    display: getComputedStyle(learnBtn).display,
                    rect: (function() {
                        var r = learnBtn.getBoundingClientRect();
                        return {top: Math.round(r.top), bottom: Math.round(r.bottom)};
                    })()
                } : null,
                msgsScrollTop: msgs ? msgs.scrollTop : null,
                msgsScrollHeight: msgs ? msgs.scrollHeight : null
            };
        }""")
        print(f"\n[FINAL STATE] {final_state}")

        # Step 6: Scroll to show the Learn more button + input row together
        await page.evaluate("""() => {
            var msgs = document.getElementById('ptc-messages');
            if (msgs) msgs.scrollTop = msgs.scrollHeight;
        }""")
        await asyncio.sleep(1)

        # F04: Final state - bottom of messages with Learn more button + disabled input
        f04 = f"{OUTPUT_DIR}/F04-FINAL-disabled-input-learn-more-btn.png"
        await page.screenshot(path=f04)
        print(f"[SS] F04: {f04}")
        tg_photo(f04, f"F04-FINAL: Disabled input ('{final_state.get('input', {}).get('placeholder', 'N/A')}') + Learn more button. Send opacity={final_state.get('send', {}).get('opacity', 'N/A')}")

        # Step 7: Clipped closeup of the "Learn more" button area
        learn_rect = final_state.get('learnBtn', {}).get('rect') if final_state.get('learnBtn') else None
        if learn_rect:
            top = learn_rect['top']
            bottom = learn_rect['bottom']
            clip_y = max(0, top - 100)
            clip_h = min(900, bottom + 50)
            if clip_h > clip_y:
                f05 = f"{OUTPUT_DIR}/F05-FINAL-learn-more-btn-closeup.png"
                await page.screenshot(path=f05, clip={"x": 0, "y": clip_y, "width": 1440, "height": clip_h - clip_y})
                print(f"[SS CLIP] F05: {f05}")
                tg_photo(f05, "F05-FINAL: Learn more button closeup + disabled input row")

        # Step 8: CHECK - does the full Q&A flow produce a different brain stream button?
        # The real flow (with AI name given) creates personalized "ENTER [NAME]'S BRAIN STREAM"
        # In sandbox-3 with bypass, AI is named "Your AI" - the Welcome card IS the end state

        # Check all visible text in chatbox to confirm no hidden brain stream button
        all_text = await page.evaluate("""() => {
            var container = document.getElementById('pay-test-post-payment');
            if (!container) return [];

            var textNodes = [];
            var walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
            var node;
            while (node = walker.nextNode()) {
                var text = node.textContent.trim();
                if (text.length > 5 && text.toLowerCase().includes('brain')) {
                    textNodes.push(text.substring(0, 100));
                }
            }
            return textNodes;
        }""")
        print(f"\n[ALL BRAIN TEXT IN CHATBOX] {all_text}")

        # Verify input state
        print(f"\n=== VERIFICATION ===")
        print(f"Input disabled: {final_state.get('input', {}).get('disabled')}")
        print(f"Input placeholder: {final_state.get('input', {}).get('placeholder')}")
        print(f"Send button opacity: {final_state.get('send', {}).get('opacity')}")
        print(f"Learn more btn visible: {bool(final_state.get('learnBtn'))}")
        print(f"Brain stream text in chatbox: {all_text}")

        await browser.close()

        # Summary to Telegram
        tg(f"E2E BS v5 FINAL: DONE. Input disabled={final_state.get('input', {}).get('disabled')}. "
           f"Send opacity={final_state.get('send', {}).get('opacity')}. "
           f"Brain text in chatbox: {len(all_text)} items")

        print("\n=== E2E BS v5 COMPLETE ===")
        print(f"Screenshots saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(run())
