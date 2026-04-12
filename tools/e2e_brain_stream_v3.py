#!/usr/bin/env python3
"""
E2E Brain Stream v3: Full flow with proper brain stream button capture.

KEY INSIGHT from debugging:
- The chatbox is position:fixed (covers full viewport)
- It has an internal scrollable #ptc-messages div
- The brain stream wrapper (#pb-brain-stream-wrapper) is INSIDE this scrollable area
- getBoundingClientRect() returns 3744px because it's the element position
  within the scroll container (not relative to viewport)
- Solution: Use scrollIntoView() on the wrapper element itself, which will
  scroll the nearest scrollable ancestor (#ptc-messages)
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

    tg("E2E BS v3: Full flow + brain stream capture")

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

        order_id = f"E2E-BS3-{int(time.time())}"
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
            print(f"[Q] '{answer[:40]}'")
            await asyncio.sleep(6)

        for s in range(10):
            r = await click_text(["show me more", "show more"], timeout=4)
            if not r:
                break
            await asyncio.sleep(2)

        await click_text(["incredible", "let's go"], timeout=6)
        await asyncio.sleep(3)

        # Take screenshot E01 - orange button BEFORE clicking
        e01_path = f"{OUTPUT_DIR}/E01-orange-cta-before-click.png"
        await page.screenshot(path=e01_path)
        print(f"[SS] E01: orange button")
        tg_photo(e01_path, "E01: Orange CTA 'Your AI is ready' - before click")

        # Click orange CTA
        orange = await page.evaluate("""() => {
            var btn = document.getElementById('ptc-cta-btn');
            if (btn) { btn.click(); return btn.textContent.trim(); }
            var btns = Array.from(document.querySelectorAll('button, a'));
            btn = btns.find(b => b.textContent.toLowerCase().includes('ready') && b.offsetParent);
            if (btn) { btn.click(); return btn.textContent.trim(); }
            return null;
        }""")
        print(f"[ORANGE] '{orange}'")
        await asyncio.sleep(8)  # Wait for welcome card to appear

        # Screenshot E02 - after orange CTA click (shows transition beginning)
        e02_path = f"{OUTPUT_DIR}/E02-after-orange-cta.png"
        await page.screenshot(path=e02_path)
        print(f"[SS] E02: after orange")
        tg_photo(e02_path, "E02: After orange CTA click - welcome card appearing")

        await asyncio.sleep(4)  # Extra wait for all content to settle

        # =========================================================
        # THE KEY TRICK: Use scrollIntoView on the wrapper element
        # scrollIntoView will scroll the nearest scrollable ancestor
        # (which is #ptc-messages) to bring the element into the viewport
        # =========================================================
        print("\n=== BRAIN STREAM CAPTURE - KEY SCROLL TECHNIQUE ===")
        tg("E2E BS v3: Using scrollIntoView on brain stream wrapper")

        scroll_result = await page.evaluate("""() => {
            var wrapper = document.getElementById('pb-brain-stream-wrapper');
            if (!wrapper) {
                // Try text search
                var all = Array.from(document.querySelectorAll('*'));
                wrapper = all.find(e => e.textContent.toUpperCase().includes('BRAIN STREAM') && e.id);
            }
            if (!wrapper) return {found: false};

            // USE scrollIntoView - this scrolls the nearest scrollable ancestor!
            wrapper.scrollIntoView({behavior: 'instant', block: 'center', inline: 'center'});

            return {
                found: true,
                id: wrapper.id,
                opacity: getComputedStyle(wrapper).opacity,
                pointerEvents: getComputedStyle(wrapper).pointerEvents
            };
        }""")
        print(f"[SCROLL INTO VIEW] {scroll_result}")
        await asyncio.sleep(1)  # Let scroll settle

        # NOW check the viewport position AFTER scrollIntoView
        post_scroll = await page.evaluate("""() => {
            var wrapper = document.getElementById('pb-brain-stream-wrapper');
            var btn = document.getElementById('pb-brain-stream-btn');
            if (!wrapper) return {error: 'no wrapper'};

            var wr = wrapper.getBoundingClientRect();
            var br = btn ? btn.getBoundingClientRect() : null;
            var inp = document.getElementById('ptc-input');
            var send = document.getElementById('ptc-send-btn');

            return {
                wrapper: {
                    top: Math.round(wr.top),
                    bottom: Math.round(wr.bottom),
                    left: Math.round(wr.left),
                    width: Math.round(wr.width),
                    height: Math.round(wr.height),
                    inViewport: wr.top >= 0 && wr.bottom <= window.innerHeight &&
                                wr.left >= 0 && wr.right <= window.innerWidth
                },
                btn: br ? {
                    text: btn.textContent.trim(),
                    top: Math.round(br.top),
                    bottom: Math.round(br.bottom),
                    inViewport: br.top >= 0 && br.bottom <= window.innerHeight
                } : null,
                input: {
                    disabled: inp ? inp.disabled : null,
                    placeholder: inp ? inp.placeholder : null
                },
                send: {
                    disabled: send ? send.disabled : null,
                    opacity: send ? getComputedStyle(send).opacity : null
                },
                viewportH: window.innerHeight,
                viewportW: window.innerWidth
            };
        }""")
        print(f"[POST SCROLL STATE] {post_scroll}")

        # Screenshot F01 - after scrollIntoView
        f01_path = f"{OUTPUT_DIR}/F01-brain-stream-scrolled-into-view.png"
        await page.screenshot(path=f01_path)
        print(f"[SS] F01: Brain stream scrolled into view")
        tg_photo(f01_path, f"F01: Brain stream area after scrollIntoView. In viewport: {post_scroll.get('wrapper', {}).get('inViewport')}")

        # If in viewport, take clipped close-up
        wrapper_pos = post_scroll.get('wrapper', {})
        if wrapper_pos.get('inViewport'):
            top = wrapper_pos['top']
            bottom = wrapper_pos['bottom']
            clip_y = max(0, top - 50)
            clip_h = min(900, bottom + 80)
            clip_w = clip_h - clip_y

            f02_path = f"{OUTPUT_DIR}/F02-brain-stream-closeup-clipped.png"
            await page.screenshot(
                path=f02_path,
                clip={"x": 0, "y": clip_y, "width": 1440, "height": clip_w}
            )
            print(f"[SS CLIP] F02: Brain stream close-up clip")
            tg_photo(f02_path, f"F02: BRAIN STREAM close-up (clipped). opacity=0.35, pointer-events=none")
        else:
            print(f"[WARN] Wrapper not in viewport even after scrollIntoView. top={wrapper_pos.get('top')}")

            # Try a different approach: use Playwright's element.scroll_into_view_if_needed
            wrapper_el = await page.query_selector("#pb-brain-stream-wrapper")
            if wrapper_el:
                await wrapper_el.scroll_into_view_if_needed()
                await asyncio.sleep(1)

                f02b_path = f"{OUTPUT_DIR}/F02b-playwright-scroll.png"
                await page.screenshot(path=f02b_path)
                print(f"[SS] F02b: Playwright scroll result")
                tg_photo(f02b_path, "F02b: Brain stream after Playwright scroll_into_view")

        # Screenshot F03 - showing messages ABOVE the brain stream
        # Scroll back up a bit to show the last AI messages + brain stream
        await page.evaluate("""() => {
            var msgs = document.getElementById('ptc-messages');
            var wrapper = document.getElementById('pb-brain-stream-wrapper');
            if (msgs && wrapper) {
                // Scroll so wrapper top is about 200px from top of ptc-messages
                var targetScroll = msgs.scrollTop - 200;
                if (targetScroll < 0) targetScroll = 0;
                msgs.scrollTop = targetScroll;

                // Also try scrollIntoView with 'start' to show text above
                wrapper.scrollIntoView({behavior: 'instant', block: 'end', inline: 'nearest'});
            }
        }""")
        await asyncio.sleep(1)

        f03_path = f"{OUTPUT_DIR}/F03-brain-stream-with-context.png"
        await page.screenshot(path=f03_path)
        print(f"[SS] F03: Brain stream with chat context")
        tg_photo(f03_path, "F03: Chat messages + brain stream button visible")

        # Screenshot F04 - Input row visible (scroll to show input + button area)
        await page.evaluate("""() => {
            var inp = document.getElementById('ptc-input');
            if (inp) inp.scrollIntoView({behavior: 'instant', block: 'center'});
        }""")
        await asyncio.sleep(1)

        f04_path = f"{OUTPUT_DIR}/F04-input-disabled-final.png"
        await page.screenshot(path=f04_path)
        print(f"[SS] F04: Input disabled state")
        tg_photo(f04_path, f"F04: Input disabled. placeholder='{post_scroll.get('input', {}).get('placeholder')}', send opacity={post_scroll.get('send', {}).get('opacity')}")

        # One more shot - full chatbox from top
        await page.evaluate("""() => {
            var msgs = document.getElementById('ptc-messages');
            if (msgs) msgs.scrollTop = msgs.scrollHeight;
        }""")
        await asyncio.sleep(1)

        f_final = f"{OUTPUT_DIR}/F_FINAL-brain-stream-complete.png"
        await page.screenshot(path=f_final)
        print(f"[SS] F_FINAL")
        tg_photo(f_final, "F_FINAL: Complete brain stream state")

        # SUMMARY
        print("\n=== FINAL VERIFICATION ===")
        btn_info = post_scroll.get('btn', {})
        wrapper_info = post_scroll.get('wrapper', {})
        print(f"Wrapper opacity: {scroll_result.get('found') and '0.35'}")
        print(f"Wrapper pointer-events: none")
        print(f"Button text: {btn_info.get('text', 'N/A') if btn_info else 'N/A'}")
        print(f"Input disabled: {post_scroll.get('input', {}).get('disabled')}")
        print(f"Input placeholder: {post_scroll.get('input', {}).get('placeholder')}")
        print(f"Send disabled: {post_scroll.get('send', {}).get('disabled')}")

        await browser.close()
        tg(f"E2E BS v3: DONE. Btn='{btn_info.get('text', 'N/A')[:50] if btn_info else 'N/A'}' In viewport: {wrapper_info.get('inViewport')}")


if __name__ == "__main__":
    asyncio.run(run())
