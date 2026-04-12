#!/usr/bin/env python3
"""
Investor Portal Stress Test v4 - Fixed gate transition + layer navigation.
Uses proper waiting for JS function availability.
"""

import asyncio
import time
import os
import json

from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/tmp/investor-stress-test"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
URL = "https://purebrain.ai/investment-opportunity/"


async def snap(page, name, label):
    path = f"{SCREENSHOT_DIR}/{name}_{label}.png"
    try:
        await page.screenshot(path=path, full_page=False, timeout=8000)
        return True
    except Exception:
        return False


async def wait_for_js_function(page, func_name, timeout=15):
    """Wait until a JS function is defined on window."""
    for _ in range(timeout * 2):
        exists = await page.evaluate(f"typeof window.{func_name} === 'function'")
        if exists:
            return True
        await asyncio.sleep(0.5)
    return False


async def run_session(browser, name, code, questions):
    print(f"\n  [{name}] Starting session (code: {code})")

    ctx = await browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 StressTest/{name}"
    )
    page = await ctx.new_page()

    errors = []
    page.on("console", lambda m: errors.append(m.text[:200]) if m.type == "error" else None)

    log = []

    try:
        # 1. Navigate
        print(f"  [{name}] 1/8 Navigate")
        await page.goto(URL, wait_until="networkidle", timeout=45000)
        await asyncio.sleep(2)
        await snap(page, name, "01_gate")
        log.append("navigate")

        # 2. Enter code + click gate
        print(f"  [{name}] 2/8 Enter code")
        await page.fill("#gate-input", code)
        await asyncio.sleep(0.3)
        await snap(page, name, "02_code_filled")

        # Use the actual tryGate function
        await page.click("#gate-btn")
        print(f"  [{name}] Gate button clicked, waiting for transition...")
        log.append("code_submitted")

        # Wait for goToEntLayer to become available (signals gate passed)
        available = await wait_for_js_function(page, "goToEntLayer", timeout=20)
        if available:
            print(f"  [{name}] Gate passed! Entrance layers loaded.")
        else:
            print(f"  [{name}] WARNING: goToEntLayer not available after 20s, checking page state...")
            # Check if we went directly to main
            layout_visible = await page.evaluate("document.getElementById('layout') && !document.getElementById('layout').classList.contains('avatar-hidden')")
            if layout_visible:
                print(f"  [{name}] Already in main layout!")
            else:
                # Try clicking gate btn again
                await page.click("#gate-btn")
                await asyncio.sleep(5)
                available = await wait_for_js_function(page, "goToEntLayer", timeout=10)

        await snap(page, name, "02b_after_gate")
        log.append("gate_passed")

        # 3. Click through entrance layers
        print(f"  [{name}] 3/8 Entrance layers")

        # Check if entrance layers exist and are visible
        ent_layer_1_visible = await page.evaluate("""
            document.getElementById('ent-layer-1') &&
            getComputedStyle(document.getElementById('ent-layer-1')).display !== 'none'
        """)

        if ent_layer_1_visible:
            for layer_num in [2, 3, 4]:
                try:
                    await page.evaluate(f"window.goToEntLayer({layer_num})")
                    print(f"  [{name}] -> Layer {layer_num}")
                    await asyncio.sleep(1.5)
                except Exception as e:
                    print(f"  [{name}] Layer {layer_num} error: {str(e)[:60]}")
                    # Try clicking the button instead
                    try:
                        btn = await page.query_selector(f"#ent-layer-{layer_num-1} .ent-nav-btn")
                        if btn:
                            await btn.click()
                            await asyncio.sleep(1.5)
                    except Exception:
                        pass

            # Enter from layers
            try:
                await page.evaluate("window.enterFromLayers()")
                print(f"  [{name}] -> Entered main portal")
            except Exception:
                try:
                    enter_btn = await page.query_selector("#ent-layer-4 .ent-nav-btn.enter")
                    if enter_btn:
                        await enter_btn.click()
                except Exception:
                    pass

            await asyncio.sleep(4)
        else:
            print(f"  [{name}] No entrance layers visible, may have gone directly to main")
            await asyncio.sleep(2)

        await snap(page, name, "03_in_portal")
        log.append("entrance_done")

        # 4. Click 2 quick buttons
        print(f"  [{name}] 4/8 Quick buttons")

        # Wait for layout to be visible
        for _ in range(20):
            layout_ready = await page.evaluate("""
                document.getElementById('layout') &&
                !document.getElementById('layout').classList.contains('avatar-hidden')
            """)
            if layout_ready:
                break
            await asyncio.sleep(0.5)

        btn_info = await page.evaluate("""() => {
            const btns = document.querySelectorAll('.quick-btn');
            return Array.from(btns).map(b => b.textContent.trim());
        }""")
        print(f"  [{name}] Found {len(btn_info)} quick buttons: {btn_info[:5]}")

        for i in range(min(2, len(btn_info))):
            print(f"  [{name}] Clicking: '{btn_info[i]}'")
            await page.evaluate(f"document.querySelectorAll('.quick-btn')[{i}].click()")
            log.append(f"btn_{btn_info[i][:15]}")
            await asyncio.sleep(6)

        await snap(page, name, "04_after_buttons")

        # 5. Type first question
        print(f"  [{name}] 5/8 Q1: '{questions[0]}'")
        # Use nativeInputValueSetter to properly set value
        await page.evaluate(f"""() => {{
            const input = document.getElementById('text-input');
            if (input) {{
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value').set;
                nativeInputValueSetter.call(input, {json.dumps(questions[0])});
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }}""")
        await asyncio.sleep(0.3)
        await page.evaluate("document.getElementById('send-btn').click()")
        print(f"  [{name}] Q1 sent")
        log.append(f"q1_sent")

        # 6. Wait for AI response
        print(f"  [{name}] 6/8 Waiting for response...")
        await asyncio.sleep(12)
        await snap(page, name, "06_q1_response")

        # Try to capture response text
        resp = await page.evaluate("""() => {
            const msgs = document.querySelectorAll('[class*="message"], [class*="response"], [class*="bubble"], [class*="answer"], [class*="reply"]');
            return Array.from(msgs).map(m => m.textContent.trim().substring(0, 150)).filter(t => t.length > 20);
        }""")
        if resp:
            print(f"  [{name}] Response found: {resp[-1][:100]}...")
        log.append("q1_response")

        # 7. Click another quick button
        print(f"  [{name}] 7/8 Extra button")
        if len(btn_info) > 2:
            print(f"  [{name}] Clicking: '{btn_info[2]}'")
            await page.evaluate("document.querySelectorAll('.quick-btn')[2].click()")
            log.append(f"btn_{btn_info[2][:15]}")
            await asyncio.sleep(6)
            await snap(page, name, "07_btn3")

        # 8. Type second question
        print(f"  [{name}] 8/8 Q2: '{questions[1]}'")
        await page.evaluate(f"""() => {{
            const input = document.getElementById('text-input');
            if (input) {{
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value').set;
                nativeInputValueSetter.call(input, {json.dumps(questions[1])});
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }}""")
        await asyncio.sleep(0.3)
        await page.evaluate("document.getElementById('send-btn').click()")
        print(f"  [{name}] Q2 sent")
        log.append("q2_sent")

        await asyncio.sleep(12)
        await snap(page, name, "08_q2_response")

        resp2 = await page.evaluate("""() => {
            const msgs = document.querySelectorAll('[class*="message"], [class*="response"], [class*="bubble"], [class*="answer"], [class*="reply"]');
            return Array.from(msgs).map(m => m.textContent.trim().substring(0, 150)).filter(t => t.length > 20);
        }""")
        if resp2:
            print(f"  [{name}] Response found: {resp2[-1][:100]}...")
        log.append("q2_response")

        await snap(page, name, "99_final")
        log.append("COMPLETE")

        print(f"  [{name}] SESSION COMPLETE: {len(log)} steps")
        print(f"  [{name}] Console errors: {len(errors)}")

    except Exception as e:
        print(f"  [{name}] FATAL: {e}")
        log.append(f"ERROR:{str(e)[:80]}")
        await snap(page, name, "ERROR")
    finally:
        await ctx.close()

    return {"session": name, "code": code, "steps": log, "errors": errors[:10]}


async def main():
    print(f"INVESTOR PORTAL STRESS TEST v4 - {time.strftime('%H:%M:%S')}")
    print(f"Target: {URL}\n")

    # Clean
    for f in os.listdir(SCREENSHOT_DIR):
        if f.startswith(("JOHNSON_", "BENADOF_")) and f.endswith(".png"):
            os.remove(f"{SCREENSHOT_DIR}/{f}")

    t0 = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        )

        results = await asyncio.gather(
            run_session(browser, "JOHNSON", "JOHNSON2026",
                       ["When do we break even?", "What are the revenue projections?"]),
            run_session(browser, "BENADOF", "BENADOF2026",
                       ["What is the competitive advantage?", "Tell me about the technology"]),
        )

        await browser.close()

    elapsed = time.time() - t0

    print(f"\n{'='*60}")
    print(f"RESULTS ({elapsed:.1f}s)")
    print(f"{'='*60}")

    for r in results:
        print(f"\n{r['session']} ({r['code']}):")
        print(f"  Steps: {' -> '.join(r['steps'])}")
        if r['errors']:
            print(f"  Errors ({len(r['errors'])}):")
            for e in r['errors'][:5]:
                print(f"    {e[:120]}")

    print(f"\nScreenshots:")
    for f in sorted(os.listdir(SCREENSHOT_DIR)):
        if f.startswith(("JOHNSON_", "BENADOF_")) and f.endswith(".png"):
            sz = os.path.getsize(f"{SCREENSHOT_DIR}/{f}")
            print(f"  {f} ({sz:,}b)")


if __name__ == "__main__":
    asyncio.run(main())
