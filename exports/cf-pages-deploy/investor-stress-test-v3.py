#!/usr/bin/env python3
"""
Investor Portal Stress Test v3 - Completes all interactions, minimal screenshots.
Focuses on completing the full workflow rather than capturing every step.
"""

import asyncio
import time
import os

from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/tmp/investor-stress-test"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

URL = "https://purebrain.ai/investment-opportunity/"


async def safe_screenshot(page, session_name, label):
    path = f"{SCREENSHOT_DIR}/{session_name}_{label}.png"
    try:
        await page.screenshot(path=path, full_page=False, timeout=8000)
        return path
    except Exception:
        return None


async def run_session(browser, session_name, investor_code, questions):
    print(f"\n{'='*60}")
    print(f"  {session_name} ({investor_code}) - STARTING")
    print(f"{'='*60}")

    context = await browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 StressTest-{session_name}"
    )
    page = await context.new_page()

    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text[:200]) if msg.type == "error" else None)

    results = {"session": session_name, "code": investor_code, "steps": [], "errors": []}

    try:
        # STEP 1: Navigate
        print(f"  [{session_name}] Navigating...")
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        await safe_screenshot(page, session_name, "01_landing")
        results["steps"].append("1_navigate")

        # STEP 2: Enter code
        print(f"  [{session_name}] Entering code {investor_code}...")
        gate_input = await page.wait_for_selector("#gate-input", timeout=10000)
        await gate_input.fill(investor_code)
        await asyncio.sleep(0.5)

        gate_btn = await page.query_selector("#gate-btn")
        await gate_btn.click()
        print(f"  [{session_name}] Gate button clicked")
        await asyncio.sleep(4)
        results["steps"].append("2_code_entered")

        # STEP 3: Click through ALL entrance layers via JS (faster, no animation wait)
        print(f"  [{session_name}] Navigating entrance layers via JS...")
        for layer_num in [2, 3, 4]:
            await page.evaluate(f"goToEntLayer({layer_num})")
            await asyncio.sleep(1.5)
            print(f"  [{session_name}] Layer {layer_num} passed")

        # Enter from layers
        await page.evaluate("enterFromLayers()")
        print(f"  [{session_name}] enterFromLayers() called")
        await asyncio.sleep(4)
        await safe_screenshot(page, session_name, "03_in_portal")
        results["steps"].append("3_entrance_complete")

        # STEP 4: Click 2 quick buttons
        print(f"  [{session_name}] Clicking quick buttons...")

        # Get button info via JS
        buttons_info = await page.evaluate("""() => {
            const btns = document.querySelectorAll('.quick-btn');
            return Array.from(btns).map((b, i) => ({
                index: i,
                text: b.textContent.trim(),
                dataQ: b.getAttribute('data-q'),
                visible: b.offsetParent !== null
            }));
        }""")
        print(f"  [{session_name}] Found {len(buttons_info)} quick buttons")

        # Click first two via JS
        for i in range(min(2, len(buttons_info))):
            btn_text = buttons_info[i]["text"]
            print(f"  [{session_name}] Clicking button {i+1}: '{btn_text}'")
            await page.evaluate(f"""() => {{
                const btns = document.querySelectorAll('.quick-btn');
                if (btns[{i}]) btns[{i}].click();
            }}""")
            results["steps"].append(f"4_btn_{i+1}_{btn_text[:20]}")
            await asyncio.sleep(6)  # Wait for AI response

        await safe_screenshot(page, session_name, "04_after_buttons")

        # STEP 5: Type first question
        print(f"  [{session_name}] Typing: '{questions[0]}'")
        await page.evaluate(f"""() => {{
            const input = document.getElementById('text-input');
            if (input) {{
                input.value = {repr(questions[0])};
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }}""")
        await asyncio.sleep(0.5)

        # Click send
        await page.evaluate("""() => {
            const btn = document.getElementById('send-btn');
            if (btn) btn.click();
        }""")
        print(f"  [{session_name}] Q1 sent")
        results["steps"].append(f"5_q1_sent")

        # STEP 6: Wait for response
        await asyncio.sleep(10)
        await safe_screenshot(page, session_name, "06_q1_response")
        results["steps"].append("6_q1_response")

        # Check if there's a response element
        response_check = await page.evaluate("""() => {
            // Look for any response/message elements
            const messages = document.querySelectorAll('.message, .response, .chat-message, [class*="response"], [class*="answer"]');
            return Array.from(messages).map(m => m.textContent.trim().substring(0, 100));
        }""")
        if response_check:
            print(f"  [{session_name}] Response elements found: {len(response_check)}")
            for r in response_check[:3]:
                print(f"    -> {r[:80]}")

        # STEP 7: Click another quick button
        print(f"  [{session_name}] Clicking 3rd quick button...")
        if len(buttons_info) > 2:
            btn_text = buttons_info[2]["text"]
            print(f"  [{session_name}] Button 3: '{btn_text}'")
            await page.evaluate("""() => {
                const btns = document.querySelectorAll('.quick-btn');
                if (btns[2]) btns[2].click();
            }""")
            results["steps"].append(f"7_btn_3_{btn_text[:20]}")
            await asyncio.sleep(6)

        await safe_screenshot(page, session_name, "07_btn3_response")

        # STEP 8: Type second question
        print(f"  [{session_name}] Typing: '{questions[1]}'")
        await page.evaluate(f"""() => {{
            const input = document.getElementById('text-input');
            if (input) {{
                input.value = {repr(questions[1])};
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }}""")
        await asyncio.sleep(0.5)

        await page.evaluate("""() => {
            const btn = document.getElementById('send-btn');
            if (btn) btn.click();
        }""")
        print(f"  [{session_name}] Q2 sent")
        results["steps"].append("8_q2_sent")

        # Wait for response
        await asyncio.sleep(10)
        await safe_screenshot(page, session_name, "08_q2_response")
        results["steps"].append("8_q2_response")

        # Final screenshot
        await safe_screenshot(page, session_name, "99_final")
        results["steps"].append("COMPLETE")

        print(f"\n  [{session_name}] SESSION COMPLETE - {len(results['steps'])} steps")
        results["console_error_count"] = len(console_errors)
        if console_errors:
            results["errors"] = console_errors[:10]

    except Exception as e:
        print(f"  [{session_name}] ERROR: {e}")
        results["fatal_error"] = str(e)
        await safe_screenshot(page, session_name, "ERROR")
    finally:
        await context.close()

    return results


async def main():
    print("=" * 60)
    print("  INVESTOR PORTAL STRESS TEST v3")
    print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Clean old screenshots
    for f in os.listdir(SCREENSHOT_DIR):
        if f.startswith(("JOHNSON_", "BENADOF_")) and f.endswith(".png"):
            os.remove(f"{SCREENSHOT_DIR}/{f}")

    start = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage",
                   "--disable-software-rasterizer"]
        )

        results = await asyncio.gather(
            run_session(
                browser, "JOHNSON", "JOHNSON2026",
                ["When do we break even?", "What are the revenue projections?"]
            ),
            run_session(
                browser, "BENADOF", "BENADOF2026",
                ["What is the competitive advantage?", "Tell me about the technology"]
            ),
        )

        await browser.close()

    elapsed = time.time() - start

    print(f"\n{'='*60}")
    print(f"  RESULTS ({elapsed:.1f}s)")
    print(f"{'='*60}")

    for r in results:
        print(f"\n  {r['session']} ({r['code']}):")
        print(f"    Steps: {' > '.join(r['steps'])}")
        if r.get("fatal_error"):
            print(f"    FATAL: {r['fatal_error']}")
        if r.get("errors"):
            print(f"    Console errors ({r.get('console_error_count', 0)}):")
            for e in r["errors"][:5]:
                print(f"      {e[:120]}")

    print(f"\n  Screenshots:")
    for f in sorted(os.listdir(SCREENSHOT_DIR)):
        if f.startswith(("JOHNSON_", "BENADOF_")) and f.endswith(".png"):
            size = os.path.getsize(f"{SCREENSHOT_DIR}/{f}")
            print(f"    {f} ({size:,} bytes)")


if __name__ == "__main__":
    asyncio.run(main())
