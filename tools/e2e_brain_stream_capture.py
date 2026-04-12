#!/usr/bin/env python3
"""
Targeted capture: Full flow + proper brain stream button screenshots.
The chatbox is position:fixed with internal scroll - scroll ptc-messages to bottom.
"""

import asyncio
import os
import subprocess
import time

OUTPUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/e2e-sandbox3-payment-to-brain-stream"
TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"
URL = "https://purebrain.ai/pay-test-sandbox-3/"
PASSWORD = "PureBrain.ai253443$$$"


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

    tg("E2E Brain Stream v2: Full flow + proper brain stream screenshots")

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

        # SPEED: Full flow
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
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

        await click_text(["awaken your pure brain", "awaken"])
        await asyncio.sleep(4)
        await click_text(["begin awakening", "begin"])
        await asyncio.sleep(4)

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
                    return 'sent';
                }
            }
        }""")
        await asyncio.sleep(6)
        await click_text(["discover"], timeout=8)
        await asyncio.sleep(4)
        await click_text(["see what", "can do"], timeout=6)
        await asyncio.sleep(3)
        await click_text(["can do ->", "can do", "enter"], timeout=4)
        await asyncio.sleep(5)

        order_id = f"E2E-BS2-{int(time.time())}"
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
                break
            await asyncio.sleep(1)

        # Q&A fast
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
            print(f"[Q] '{answer[:40]}'")
            await asyncio.sleep(6)

        # Slides
        for s in range(10):
            await click_text(["show me more", "show more"], timeout=4)
            await asyncio.sleep(2)

        await click_text(["incredible", "let's go"], timeout=6)
        await asyncio.sleep(3)

        # Orange CTA
        await page.evaluate("""() => {
            var btn = document.getElementById('ptc-cta-btn');
            if (btn) { btn.click(); return; }
            var btns = Array.from(document.querySelectorAll('button, a'));
            btn = btns.find(b => b.textContent.toLowerCase().includes('ready') && b.offsetParent);
            if (btn) btn.click();
        }""")
        await asyncio.sleep(8)

        print("\n=== BRAIN STREAM CAPTURE ===")
        tg("E2E BS v2: Capturing brain stream button")

        # KEY INSIGHT: The chatbox is position:fixed. Its internal messages scroll independently.
        # The brain stream wrapper is at ~3744px WITHIN the scrollable messages div.
        # Solution: scroll ptc-messages to very bottom, then screenshot.

        # Step 1: Scroll the messages div to the absolute bottom
        scroll_result = await page.evaluate("""() => {
            var msgs = document.getElementById('ptc-messages');
            var wrapper = document.getElementById('pb-brain-stream-wrapper');
            var container = document.getElementById('pay-test-post-payment');

            var info = {
                msgsFound: !!msgs,
                wrapperFound: !!wrapper,
                containerFound: !!container
            };

            if (msgs) {
                msgs.scrollTop = msgs.scrollHeight;
                info.msgsScrollTop = msgs.scrollTop;
                info.msgsScrollHeight = msgs.scrollHeight;
                info.msgsClientHeight = msgs.clientHeight;
            }

            if (wrapper) {
                // Get position relative to the messages div
                var containerRect = msgs ? msgs.getBoundingClientRect() : null;
                var wrapperRect = wrapper.getBoundingClientRect();
                info.wrapperInViewport = {
                    top: wrapperRect.top,
                    bottom: wrapperRect.bottom,
                    left: wrapperRect.left,
                    right: wrapperRect.right,
                    width: wrapperRect.width,
                    height: wrapperRect.height
                };
                info.wrapperStyle = {
                    opacity: getComputedStyle(wrapper).opacity,
                    display: getComputedStyle(wrapper).display,
                    pointerEvents: getComputedStyle(wrapper).pointerEvents
                };
                info.viewportH = window.innerHeight;
                info.viewportW = window.innerWidth;
                info.isVisible = wrapperRect.top >= 0 && wrapperRect.bottom <= window.innerHeight;
            }

            return info;
        }""")
        print(f"[SCROLL] {scroll_result}")

        await asyncio.sleep(2)

        # Screenshot 1: After scrolling messages to bottom
        p1 = f"{OUTPUT_DIR}/F02-brain-stream-button-closeup-v2.png"
        await page.screenshot(path=p1, full_page=False)
        print(f"[SS1] {p1}")
        tg_photo(p1, "F02v2: Brain stream area after scrolling messages to bottom")

        # Check if wrapper is now in viewport
        wrapper_in_view = scroll_result.get('wrapperInViewport', {})
        w_top = wrapper_in_view.get('top', -1)
        w_bottom = wrapper_in_view.get('bottom', -1)
        viewport_h = scroll_result.get('viewportH', 900)

        print(f"[VIEWPORT CHECK] wrapper top={w_top:.0f}, bottom={w_bottom:.0f}, viewportH={viewport_h}")

        if w_top >= 0 and w_bottom <= viewport_h:
            print("[OK] Brain stream button IS in viewport now!")

            # Clip screenshot to show just the brain stream area
            clip_y = max(0, int(w_top) - 80)
            clip_h = min(viewport_h, int(w_bottom) + 80)

            p2 = f"{OUTPUT_DIR}/F02b-brain-stream-clipped.png"
            await page.screenshot(
                path=p2,
                clip={"x": 0, "y": clip_y, "width": 1440, "height": clip_h - clip_y}
            )
            print(f"[SS2 CLIP] {p2}")
            tg_photo(p2, f"F02b: Brain stream button close-up (clipped to y={clip_y}-{clip_h})")
        else:
            print(f"[WARN] Brain stream not in viewport (top={w_top:.0f}). Trying force scroll...")

            # Force scroll to make it visible
            force_result = await page.evaluate(f"""() => {{
                var msgs = document.getElementById('ptc-messages');
                var wrapper = document.getElementById('pb-brain-stream-wrapper');
                if (!wrapper || !msgs) return 'elements-missing';

                // Get wrapper position relative to msgs container
                // Since we can't easily get offsetTop within msgs, use a different approach:
                // Scroll msgs enough to put wrapper in viewport
                var containerRect = msgs.getBoundingClientRect();
                var wrapperRect = wrapper.getBoundingClientRect();

                // Calculate how much to scroll
                var scrollNeeded = wrapperRect.top - (window.innerHeight * 0.4);
                if (scrollNeeded > 0) {{
                    msgs.scrollTop += scrollNeeded;
                }}

                return {{
                    scrolled: scrollNeeded,
                    newWrapperTop: wrapper.getBoundingClientRect().top,
                    newWrapperBottom: wrapper.getBoundingClientRect().bottom
                }};
            }}""")
            print(f"[FORCE SCROLL] {force_result}")
            await asyncio.sleep(1)

            p3 = f"{OUTPUT_DIR}/F02c-brain-stream-force-scroll.png"
            await page.screenshot(path=p3, full_page=False)
            print(f"[SS3] {p3}")
            tg_photo(p3, "F02c: Brain stream after force scroll")

            # Get updated position
            new_pos = await page.evaluate("""() => {
                var w = document.getElementById('pb-brain-stream-wrapper');
                if (!w) return null;
                var r = w.getBoundingClientRect();
                return {top: r.top, bottom: r.bottom, height: r.height, visible: r.top >= 0 && r.bottom <= window.innerHeight};
            }""")
            print(f"[NEW POS] {new_pos}")

            if new_pos and new_pos.get('visible'):
                clip_y = max(0, int(new_pos['top']) - 60)
                clip_h = min(viewport_h, int(new_pos['bottom']) + 60)
                p4 = f"{OUTPUT_DIR}/F02d-brain-stream-clip-final.png"
                await page.screenshot(
                    path=p4,
                    clip={"x": 0, "y": clip_y, "width": 1440, "height": clip_h - clip_y}
                )
                print(f"[SS4 CLIP] {p4}")
                tg_photo(p4, "F02d: Brain stream FINAL clip")

        # Screenshot: Input disabled state
        await page.evaluate("""() => {
            var inp = document.getElementById('ptc-input');
            if (inp) {
                // Scroll to show input
                var msgs = document.getElementById('ptc-messages');
                if (msgs) msgs.scrollTop = msgs.scrollHeight;
            }
        }""")
        await asyncio.sleep(1)

        p_input = f"{OUTPUT_DIR}/F04-input-disabled-v2.png"
        await page.screenshot(path=p_input, full_page=False)
        print(f"[SS INPUT] {p_input}")
        tg_photo(p_input, "F04v2: Input disabled state + brain stream button area")

        # Verify button state
        final_state = await page.evaluate("""() => {
            var wrapper = document.getElementById('pb-brain-stream-wrapper');
            var btn = document.getElementById('pb-brain-stream-btn');
            var inp = document.getElementById('ptc-input');
            var send = document.getElementById('ptc-send-btn');

            return {
                wrapper: wrapper ? {
                    opacity: getComputedStyle(wrapper).opacity,
                    pointerEvents: getComputedStyle(wrapper).pointerEvents,
                    rect: (function() {
                        var r = wrapper.getBoundingClientRect();
                        return {top: Math.round(r.top), bottom: Math.round(r.bottom)};
                    })()
                } : null,
                btn: btn ? {
                    text: btn.textContent.trim(),
                    bg: getComputedStyle(btn).backgroundColor,
                    cursor: getComputedStyle(btn).cursor,
                    rect: (function() {
                        var r = btn.getBoundingClientRect();
                        return {top: Math.round(r.top), bottom: Math.round(r.bottom)};
                    })()
                } : null,
                input: inp ? {
                    disabled: inp.disabled,
                    placeholder: inp.placeholder
                } : null,
                send: send ? {
                    disabled: send.disabled,
                    opacity: getComputedStyle(send).opacity
                } : null
            };
        }""")
        print(f"[FINAL STATE] {final_state}")

        await browser.close()

        tg(f"E2E BS v2: DONE. Btn='{final_state.get('btn', {}).get('text', 'N/A') if final_state.get('btn') else 'N/A'[:50]}' | opacity={final_state.get('wrapper', {}).get('opacity', 'N/A') if final_state.get('wrapper') else 'N/A'}")


if __name__ == "__main__":
    asyncio.run(run())
