#!/usr/bin/env python3
"""
E2E Brain Stream v4: Diagnose the exact DOM structure and capture brain stream.
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

    tg("E2E BS v4: DOM diagnosis + brain stream capture")

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

        # Full speed run
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
                    return;
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

        order_id = f"E2E-BS4-{int(time.time())}"
        await page.evaluate(f"""() => {{
            if (typeof window.onPaymentComplete === 'function')
                window.onPaymentComplete('Awakened', '{order_id}', {{}});
        }}""")
        await asyncio.sleep(8)

        for i in range(20):
            ok = await page.evaluate("""() => {
                var r = document.getElementById('ptc-input-row');
                return r && getComputedStyle(r).display !== 'none';
            }""")
            if ok:
                print(f"[CHATBOX] Ready at {i}s")
                break
            await asyncio.sleep(1)

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
            await asyncio.sleep(6)

        for s in range(10):
            r = await click_text(["show me more", "show more"], timeout=4)
            if not r:
                break
            await asyncio.sleep(2)

        await click_text(["incredible", "let's go"], timeout=6)
        await asyncio.sleep(3)

        await page.evaluate("""() => {
            var btn = document.getElementById('ptc-cta-btn');
            if (btn) { btn.click(); return; }
            var btns = Array.from(document.querySelectorAll('button, a'));
            btn = btns.find(b => b.textContent.toLowerCase().includes('ready') && b.offsetParent);
            if (btn) btn.click();
        }""")
        await asyncio.sleep(8)

        # === DOM DIAGNOSIS ===
        print("\n=== DOM DIAGNOSIS ===")
        dom_structure = await page.evaluate("""() => {
            var container = document.getElementById('pay-test-post-payment');
            if (!container) return {error: 'no container'};

            function getRect(el) {
                var r = el.getBoundingClientRect();
                return {top: Math.round(r.top), bottom: Math.round(r.bottom),
                        left: Math.round(r.left), right: Math.round(r.right),
                        width: Math.round(r.width), height: Math.round(r.height)};
            }

            var msgs = document.getElementById('ptc-messages');
            var inputRow = document.getElementById('ptc-input-row');
            var ctaArea = document.getElementById('ptc-cta-area') ||
                          document.querySelector('[class*=cta-area], [class*=cta]');
            var wrapper = document.getElementById('pb-brain-stream-wrapper');
            var btn = document.getElementById('pb-brain-stream-btn');
            var inp = document.getElementById('ptc-input');
            var send = document.getElementById('ptc-send-btn');

            return {
                container: getRect(container),
                containerPosition: getComputedStyle(container).position,
                msgs: msgs ? {
                    rect: getRect(msgs),
                    scrollTop: msgs.scrollTop,
                    scrollHeight: msgs.scrollHeight,
                    clientHeight: msgs.clientHeight,
                    overflow: getComputedStyle(msgs).overflow,
                    overflowY: getComputedStyle(msgs).overflowY
                } : null,
                inputRow: inputRow ? {rect: getRect(inputRow), display: getComputedStyle(inputRow).display} : null,
                ctaArea: ctaArea ? {rect: getRect(ctaArea), id: ctaArea.id, class: ctaArea.className.substring(0, 50)} : null,
                wrapper: wrapper ? {
                    rect: getRect(wrapper),
                    opacity: getComputedStyle(wrapper).opacity,
                    pointerEvents: getComputedStyle(wrapper).pointerEvents,
                    parentId: wrapper.parentElement ? wrapper.parentElement.id : null,
                    parentClass: wrapper.parentElement ? wrapper.parentElement.className.substring(0, 50) : null
                } : null,
                btn: btn ? {
                    rect: getRect(btn),
                    text: btn.textContent.trim(),
                    opacity: getComputedStyle(btn).opacity,
                    cursor: getComputedStyle(btn).cursor
                } : null,
                inputDisabled: inp ? inp.disabled : null,
                sendDisabled: send ? send.disabled : null,
                sendOpacity: send ? getComputedStyle(send).opacity : null,
                viewportH: window.innerHeight
            };
        }""")

        print("CONTAINER:", dom_structure.get('container'))
        print("MSGS:", dom_structure.get('msgs'))
        print("INPUT ROW:", dom_structure.get('inputRow'))
        print("CTA AREA:", dom_structure.get('ctaArea'))
        print("WRAPPER:", dom_structure.get('wrapper'))
        print("BTN:", dom_structure.get('btn'))
        print("INPUT disabled:", dom_structure.get('inputDisabled'))
        print("SEND disabled:", dom_structure.get('sendDisabled'))
        print("SEND opacity:", dom_structure.get('sendOpacity'))

        # The key insight from the debug:
        # - container is position:fixed covering the viewport
        # - msgs is the scrollable div inside
        # - wrapper is AFTER msgs in the DOM, positioned after the input row
        # - The wrapper's getBoundingClientRect top=329 means it IS at y=329 in viewport
        # But we're seeing the Welcome card there, not the brain stream button

        # Let me check what element IS at y=329-571 in the viewport
        element_at_y = await page.evaluate("""() => {
            var results = [];
            // Check what elements are at different y positions
            var yPositions = [230, 280, 330, 406, 450, 500, 570, 620, 640, 700, 750];
            for (var y of yPositions) {
                var el = document.elementFromPoint(720, y);  // Center of viewport x=720
                if (el) {
                    results.push({y: y, tag: el.tagName, id: el.id, class: el.className.substring(0, 40),
                                  text: el.textContent.trim().substring(0, 60)});
                }
            }
            return results;
        }""")
        print("\nELEMENTS AT Y POSITIONS:")
        for el in element_at_y:
            print(f"  y={el['y']}: {el['tag']}#{el['id']} .{el['class'][:30]} | '{el['text'][:40]}'")

        # NOW let's see: is the brain stream wrapper OUTSIDE the chatbox container?
        # Check where exactly the wrapper is in the DOM tree
        wrapper_position = await page.evaluate("""() => {
            var wrapper = document.getElementById('pb-brain-stream-wrapper');
            if (!wrapper) return {error: 'not found'};

            // Walk up the DOM tree
            var path = [];
            var el = wrapper;
            while (el && el !== document.body) {
                path.push({
                    tag: el.tagName,
                    id: el.id,
                    class: el.className ? el.className.substring(0, 40) : '',
                    position: getComputedStyle(el).position,
                    display: getComputedStyle(el).display,
                    overflow: getComputedStyle(el).overflow
                });
                el = el.parentElement;
            }
            return path;
        }""")
        print("\nWRAPPER DOM PATH:")
        for item in wrapper_position:
            print(f"  {item['tag']}#{item['id']} position={item['position']} overflow={item['overflow']}")

        tg(f"E2E BS v4: DOM diagnosis complete. Wrapper parent: {wrapper_position[1].get('id') if len(wrapper_position) > 1 else 'N/A'}. Btn text='{dom_structure.get('btn', {}).get('text', 'N/A')[:50] if dom_structure.get('btn') else 'N/A'}'")

        # === CAPTURE STRATEGY BASED ON DIAGNOSIS ===
        # The wrapper is at top=329 in viewport, but we're seeing the welcome card there.
        # This means the welcome card is ABOVE y=329, and the brain stream wrapper
        # starts at y=329. But the screenshots show welcome card at y=230-620...
        #
        # THEORY: The wrapper IS the post-payment card container (not just the button).
        # The welcome card is INSIDE the wrapper, and the brain stream link button
        # is also inside the wrapper.
        #
        # The "Click to Connect to Your AI's Brain Stream" link at top=406
        # would be visible in the screenshots but appears greyed (0.35 opacity wrapper)
        # and has same dark background as surrounding elements.
        #
        # Let me temporarily boost the wrapper opacity to see it clearly, then restore.

        await page.evaluate("""() => {
            // Scroll to show the wrapper fully
            var wrapper = document.getElementById('pb-brain-stream-wrapper');
            var msgs = document.getElementById('ptc-messages');
            if (wrapper && msgs) {
                wrapper.scrollIntoView({behavior: 'instant', block: 'center'});
            }
        }""")
        await asyncio.sleep(1)

        # Take screenshot - this is the definitive brain stream state screenshot
        f_brain = f"{OUTPUT_DIR}/F_BRAIN_STREAM_DEFINITIVE.png"
        await page.screenshot(path=f_brain)
        print(f"\n[SS] DEFINITIVE: {f_brain}")
        tg_photo(f_brain, "F_DEFINITIVE: Brain stream wrapper state (greyed)")

        # Now take the clip of just the brain stream section
        wrapper_rect = dom_structure.get('wrapper', {}).get('rect', {})
        if wrapper_rect:
            w_top = wrapper_rect.get('top', 0)
            w_bottom = wrapper_rect.get('bottom', 900)
            # Clip to show just the wrapper area
            clip_y = max(0, w_top - 20)
            clip_h = min(900, w_bottom + 20) - clip_y
            if clip_h > 0:
                f_clip = f"{OUTPUT_DIR}/F_BRAIN_STREAM_CLIP.png"
                await page.screenshot(path=f_clip, clip={"x": 0, "y": clip_y, "width": 1440, "height": clip_h})
                print(f"[SS CLIP] {f_clip}")
                tg_photo(f_clip, f"F_CLIP: Brain stream clipped section (y={clip_y}-{clip_y+clip_h})")

        # Final: take the complete chatbox state at message bottom
        await page.evaluate("""() => {
            var msgs = document.getElementById('ptc-messages');
            if (msgs) msgs.scrollTop = msgs.scrollHeight;
        }""")
        await asyncio.sleep(1)
        f_bottom = f"{OUTPUT_DIR}/F_MESSAGES_BOTTOM.png"
        await page.screenshot(path=f_bottom)
        print(f"[SS] {f_bottom}")
        tg_photo(f_bottom, "F_BOTTOM: Messages scrolled to absolute bottom")

        await browser.close()

        print("\n=== COMPLETE ===")
        tg("E2E BS v4: DONE")


if __name__ == "__main__":
    asyncio.run(run())
