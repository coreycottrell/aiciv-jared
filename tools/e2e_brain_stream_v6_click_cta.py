#!/usr/bin/env python3
"""
E2E Brain Stream v6: Click the orange CTA button (ptc-welcome-btn) properly.

KEY FINDING from v5:
- The orange "Your AI is ready - see your next steps" button is at y=709-767
  OUTSIDE #ptc-messages, in the fixed container but below the input row
- click_text() uses offsetParent check which may reject it
- Need to click it directly by ID or by text content without offsetParent check
- After clicking, the Welcome card appears IN #ptc-messages
- The Welcome card contains: "Your AI's Brain Stream (portal) will be ready for you to log in."
- THAT is the brain stream end state for sandbox-3

Plan:
1. Run full flow to the orange CTA state
2. Click CTA using direct JS (no offsetParent check)
3. Wait for Welcome card to appear in #ptc-messages
4. Capture the complete Welcome card with Brain Stream timeline
5. Capture input disabled + send greyed state
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

    tg("E2E BS v6: Click orange CTA + capture brain stream Welcome card")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()

        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        async def click_text(fragments, timeout=12, allow_outside=False):
            deadline = time.time() + timeout
            while time.time() < deadline:
                r = await page.evaluate(f"""() => {{
                    var frags = {repr(fragments)};
                    var els = Array.from(document.querySelectorAll('button, a'));
                    for (var f of frags) {{
                        var el = els.find(e => e.textContent.toLowerCase().includes(f.toLowerCase())
                                          && {'true' if allow_outside else 'e.offsetParent !== null'}
                                          && !e.disabled);
                        if (el) {{ el.click(); return el.textContent.trim(); }}
                    }}
                    return null;
                }}""")
                if r:
                    print(f"[CLICK] '{r}'")
                    return r
                await asyncio.sleep(1)
            return None

        # === SPEED RUN: Full flow ===
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

        order_id = f"E2E-BS6-{int(time.time())}"
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
            print(f"[QA] '{answer[:40]}'")
            await asyncio.sleep(6)

        for s in range(10):
            r = await click_text(["show me more", "show more"], timeout=4)
            if not r:
                break
            await asyncio.sleep(2)

        await click_text(["incredible", "let's go"], timeout=6)
        await asyncio.sleep(3)

        # === CLICK ORANGE CTA - Multiple strategies ===
        print("\n[CTA] Attempting orange CTA click...")

        # Strategy 1: Direct ID
        cta_result = await page.evaluate("""() => {
            var btn = document.getElementById('ptc-cta-btn');
            if (btn) {
                btn.click();
                return {clicked: true, method: 'by-id', text: btn.textContent.trim()};
            }
            return {clicked: false};
        }""")
        print(f"[CTA S1] by-id: {cta_result}")

        if not cta_result.get('clicked'):
            # Strategy 2: By class name
            cta_result = await page.evaluate("""() => {
                var btn = document.querySelector('.ptc-cta-btn, [class*=cta-btn], [class*=welcome-btn]');
                if (btn) {
                    btn.click();
                    return {clicked: true, method: 'by-class', text: btn.textContent.trim()};
                }
                return {clicked: false};
            }""")
            print(f"[CTA S2] by-class: {cta_result}")

        if not cta_result.get('clicked'):
            # Strategy 3: By text content (no offsetParent check)
            cta_result = await page.evaluate("""() => {
                var allBtns = Array.from(document.querySelectorAll('button, a'));
                var btn = allBtns.find(b =>
                    b.textContent.toLowerCase().includes('ready') ||
                    b.textContent.toLowerCase().includes('next steps') ||
                    b.textContent.toLowerCase().includes('see your')
                );
                if (btn) {
                    btn.click();
                    return {clicked: true, method: 'by-text', text: btn.textContent.trim()};
                }
                // List all visible buttons
                return {clicked: false, buttons: allBtns.map(b => b.textContent.trim().substring(0, 40)).filter(t => t.length > 2)};
            }""")
            print(f"[CTA S3] by-text: {cta_result}")

        if not cta_result.get('clicked'):
            # Strategy 4: Playwright native click at coordinates (y=738 is middle of button at 709-767)
            try:
                await page.click('button:has-text("ready")', timeout=3000)
                print("[CTA S4] Playwright click by text succeeded")
                cta_result = {'clicked': True, 'method': 'playwright'}
            except:
                try:
                    # Click by coordinates
                    await page.mouse.click(694, 738)
                    print("[CTA S4b] Click by coordinates (694, 738)")
                    cta_result = {'clicked': True, 'method': 'coordinates'}
                except:
                    print("[CTA S4] All click strategies failed")

        print(f"[CTA] Final result: {cta_result}")
        await asyncio.sleep(12)  # Wait for Welcome card animation

        # Check if Welcome card appeared
        welcome_check = await page.evaluate("""() => {
            var msgs = document.getElementById('ptc-messages');
            var container = document.getElementById('pay-test-post-payment');

            // Search ALL text in page for Welcome
            var all = Array.from(document.querySelectorAll('*'));
            var welcomeEls = all.filter(e =>
                e.childElementCount === 0 &&
                e.textContent.includes('Welcome to the Family')
            );
            var brainEls = all.filter(e =>
                e.childElementCount === 0 &&
                e.textContent.toLowerCase().includes('brain stream')
            );

            return {
                msgsScrollHeight: msgs ? msgs.scrollHeight : null,
                msgsScrollTop: msgs ? msgs.scrollTop : null,
                welcomeFound: welcomeEls.length > 0,
                welcomeCount: welcomeEls.length,
                brainStreamFound: brainEls.length > 0,
                brainTexts: brainEls.map(e => e.textContent.trim().substring(0, 80))
            };
        }""")
        print(f"\n[WELCOME CHECK] {welcome_check}")

        # F01-v6: Full screenshot after CTA click attempt
        f01 = f"{OUTPUT_DIR}/F01-v6-after-cta-click.png"
        await page.screenshot(path=f01)
        print(f"[SS] F01-v6")
        tg_photo(f01, f"F01-v6: After orange CTA click. Welcome found={welcome_check.get('welcomeFound')}. Brain stream found={welcome_check.get('brainStreamFound')}")

        # If welcome card found, scroll to show it fully
        if welcome_check.get('welcomeFound') or welcome_check.get('brainStreamFound'):
            # Scroll to center the welcome card
            scroll_res = await page.evaluate("""() => {
                var msgs = document.getElementById('ptc-messages');
                if (!msgs) return 'no msgs';

                // Find Welcome heading
                var all = Array.from(msgs.querySelectorAll('*'));

                // Try to find the welcome card container
                var welcomeCard = null;
                for (var el of all) {
                    if (el.textContent.includes('Welcome to the Family') && el.children.length > 0) {
                        welcomeCard = el;
                        break;
                    }
                }

                if (welcomeCard) {
                    welcomeCard.scrollIntoView({behavior: 'instant', block: 'start'});
                    var r = welcomeCard.getBoundingClientRect();
                    return {found: true, rect: {top: Math.round(r.top), bottom: Math.round(r.bottom), height: Math.round(r.height)}};
                }

                // If not in msgs, search everywhere
                all = Array.from(document.querySelectorAll('*'));
                welcomeCard = all.find(e => e.textContent.includes('Welcome to the Family') && e.children.length > 2);
                if (welcomeCard) {
                    welcomeCard.scrollIntoView({behavior: 'instant', block: 'start'});
                    var r = welcomeCard.getBoundingClientRect();
                    return {found: true, outside_msgs: true, rect: {top: Math.round(r.top), bottom: Math.round(r.bottom)}};
                }

                return {found: false};
            }""")
            print(f"[SCROLL TO WELCOME] {scroll_res}")
            await asyncio.sleep(1)

            f02 = f"{OUTPUT_DIR}/F02-v6-welcome-card-brain-stream-timeline.png"
            await page.screenshot(path=f02)
            print(f"[SS] F02-v6")
            tg_photo(f02, "F02-v6: Welcome card with Brain Stream timeline - THE END STATE")

            # Scroll to show Brain Stream specifically
            bs_scroll = await page.evaluate("""() => {
                var all = Array.from(document.querySelectorAll('*'));
                var bsEl = all.find(e =>
                    e.textContent.toLowerCase().includes('brain stream') &&
                    e.textContent.toLowerCase().includes('portal') &&
                    e.children.length === 0
                );
                if (bsEl) {
                    bsEl.scrollIntoView({behavior: 'instant', block: 'center'});
                    var r = bsEl.getBoundingClientRect();
                    return {found: true, text: bsEl.textContent.trim(), rect: {top: Math.round(r.top), bottom: Math.round(r.bottom)}};
                }
                return {found: false};
            }""")
            print(f"[BRAIN STREAM TEXT] {bs_scroll}")
            await asyncio.sleep(1)

            if bs_scroll.get('found'):
                f03 = f"{OUTPUT_DIR}/F03-v6-brain-stream-text-visible.png"
                await page.screenshot(path=f03)
                print(f"[SS] F03-v6")
                tg_photo(f03, f"F03-v6: Brain Stream text visible: '{bs_scroll.get('text', '')[:60]}'")

        else:
            print("[WARN] Welcome card not found even after CTA click")
            # Dump all buttons on page
            all_btns = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('button, a')).map(b => ({
                    text: b.textContent.trim().substring(0, 50),
                    id: b.id,
                    class: b.className ? b.className.substring(0, 40) : '',
                    offsetParent: !!b.offsetParent
                })).filter(b => b.text.length > 2);
            }""")
            print(f"[ALL BUTTONS] {all_btns}")

        # === FINAL STATE ===
        final = await page.evaluate("""() => {
            var inp = document.getElementById('ptc-input');
            var send = document.getElementById('ptc-send-btn');
            var msgs = document.getElementById('ptc-messages');

            // Scan for brain stream in messages
            var brainInMsgs = false;
            if (msgs) {
                brainInMsgs = msgs.textContent.toLowerCase().includes('brain stream');
            }

            return {
                input: inp ? {disabled: inp.disabled, placeholder: inp.placeholder} : null,
                send: send ? {disabled: send.disabled, opacity: getComputedStyle(send).opacity} : null,
                msgsScrollHeight: msgs ? msgs.scrollHeight : null,
                brainStreamInMessages: brainInMsgs
            };
        }""")
        print(f"\n=== FINAL STATE ===")
        print(f"Input disabled: {final.get('input', {}).get('disabled')}")
        print(f"Input placeholder: {final.get('input', {}).get('placeholder')}")
        print(f"Send opacity: {final.get('send', {}).get('opacity')}")
        print(f"Brain stream in #ptc-messages: {final.get('brainStreamInMessages')}")
        print(f"Messages height: {final.get('msgsScrollHeight')}")

        # F-FINAL: Scroll to bottom + screenshot
        await page.evaluate("""() => {
            var msgs = document.getElementById('ptc-messages');
            if (msgs) msgs.scrollTop = msgs.scrollHeight;
        }""")
        await asyncio.sleep(1)

        f_final = f"{OUTPUT_DIR}/F-FINAL-v6-complete-end-state.png"
        await page.screenshot(path=f_final)
        print(f"[SS] F-FINAL-v6")
        tg_photo(f_final, f"F-FINAL-v6: Complete end state. Input disabled={final.get('input', {}).get('disabled')}. Brain stream in msgs={final.get('brainStreamInMessages')}")

        await browser.close()

        tg(f"E2E BS v6 DONE. Welcome found={welcome_check.get('welcomeFound')}. Brain in msgs={final.get('brainStreamInMessages')}. Input disabled={final.get('input', {}).get('disabled')}")
        print("\n=== E2E BS v6 COMPLETE ===")


if __name__ == "__main__":
    asyncio.run(run())
