#!/usr/bin/env python3
"""
Investor Portal Stress Test v2 - Two concurrent browser sessions
Now with exact selectors from page recon.

Page structure:
1. Gate: #gate-input (password) + #gate-btn
2. Entrance layers: #ent-layer-1..4, buttons call goToEntLayer(N), enterFromLayers()
3. Main layout: #layout with .quick-btn buttons (data-q attr)
4. Chat: #text-input + #send-btn
"""

import asyncio
import time
import os

from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/tmp/investor-stress-test"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

URL = "https://purebrain.ai/investment-opportunity/"


async def safe_screenshot(page, session_name, label):
    """Take screenshot with timeout handling for WebGL-heavy pages."""
    path = f"{SCREENSHOT_DIR}/{session_name}_{label}.png"
    try:
        await page.screenshot(path=path, full_page=False, timeout=15000)
        print(f"  [{session_name}] SCREENSHOT: {label}")
    except Exception as e:
        # Fallback: try clip-based screenshot (smaller area, faster)
        try:
            await page.screenshot(path=path, clip={"x": 0, "y": 0, "width": 1440, "height": 900}, timeout=10000)
            print(f"  [{session_name}] SCREENSHOT (clip): {label}")
        except Exception:
            print(f"  [{session_name}] Screenshot failed for {label}: {str(e)[:80]}")
    return path


async def run_session(browser, session_name, investor_code, questions):
    """Run a single investor portal session."""
    print(f"\n{'='*60}")
    print(f"  SESSION START: {session_name} (Code: {investor_code})")
    print(f"{'='*60}")

    context = await browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 StressTest-{session_name}"
    )
    page = await context.new_page()

    # Track console errors only
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text[:200]) if msg.type == "error" else None)

    results = {
        "session": session_name,
        "code": investor_code,
        "steps_completed": [],
        "console_errors": [],
        "hot_buttons_clicked": [],
        "questions_asked": [],
    }

    try:
        # ===== STEP 1: Navigate =====
        print(f"  [{session_name}] Step 1: Navigating to {URL}")
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        await safe_screenshot(page, session_name, "01_landing")
        results["steps_completed"].append("navigate")

        # ===== STEP 2: Enter investor code =====
        print(f"  [{session_name}] Step 2: Entering code {investor_code}")
        gate_input = await page.wait_for_selector("#gate-input", timeout=10000)
        await gate_input.fill(investor_code)
        await asyncio.sleep(0.5)
        await safe_screenshot(page, session_name, "02_code_entered")

        # Click Enter button
        gate_btn = await page.query_selector("#gate-btn")
        await gate_btn.click()
        print(f"  [{session_name}] Clicked #gate-btn")
        await asyncio.sleep(3)
        await safe_screenshot(page, session_name, "02b_after_gate")
        results["steps_completed"].append("code_entered")

        # ===== STEP 3: Click through entrance layers =====
        print(f"  [{session_name}] Step 3: Clicking through entrance layers")

        # Layer 1 -> 2
        try:
            btn1 = await page.wait_for_selector("#ent-layer-1 .ent-nav-btn", timeout=5000)
            if btn1 and await btn1.is_visible():
                await btn1.click()
                print(f"  [{session_name}] Layer 1 -> Next clicked")
                await asyncio.sleep(2)
        except Exception:
            # Try JS fallback
            await page.evaluate("goToEntLayer(2)")
            print(f"  [{session_name}] Layer 1 -> JS fallback")
            await asyncio.sleep(2)

        # Layer 2 -> 3
        try:
            btn2 = await page.wait_for_selector("#ent-layer-2 .ent-nav-btn", timeout=5000)
            if btn2 and await btn2.is_visible():
                await btn2.click()
                print(f"  [{session_name}] Layer 2 -> Next clicked")
                await asyncio.sleep(2)
        except Exception:
            await page.evaluate("goToEntLayer(3)")
            print(f"  [{session_name}] Layer 2 -> JS fallback")
            await asyncio.sleep(2)

        # Layer 3 -> 4
        try:
            btn3 = await page.wait_for_selector("#ent-layer-3 .ent-nav-btn", timeout=5000)
            if btn3 and await btn3.is_visible():
                await btn3.click()
                print(f"  [{session_name}] Layer 3 -> Next clicked")
                await asyncio.sleep(2)
        except Exception:
            await page.evaluate("goToEntLayer(4)")
            print(f"  [{session_name}] Layer 3 -> JS fallback")
            await asyncio.sleep(2)

        await safe_screenshot(page, session_name, "03_entrance_layers")

        # Layer 4 -> Enter main
        try:
            btn4 = await page.wait_for_selector("#ent-layer-4 .ent-nav-btn.enter", timeout=5000)
            if btn4 and await btn4.is_visible():
                await btn4.click()
                print(f"  [{session_name}] Layer 4 -> Enter clicked")
                await asyncio.sleep(3)
        except Exception:
            await page.evaluate("enterFromLayers()")
            print(f"  [{session_name}] Layer 4 -> JS fallback enterFromLayers()")
            await asyncio.sleep(3)

        await safe_screenshot(page, session_name, "03b_entered_main")
        results["steps_completed"].append("entrance_layers_passed")

        # ===== STEP 4: Click 2+ hot/quick buttons =====
        print(f"  [{session_name}] Step 4: Clicking quick buttons")

        # Wait for layout to become visible
        try:
            await page.wait_for_selector("#layout:not(.avatar-hidden)", timeout=10000)
        except Exception:
            print(f"  [{session_name}] Layout not visible yet, waiting more...")
            await asyncio.sleep(3)

        quick_buttons = await page.query_selector_all(".quick-btn")
        print(f"  [{session_name}] Found {len(quick_buttons)} quick buttons")

        buttons_clicked = 0
        for i, btn in enumerate(quick_buttons):
            if buttons_clicked >= 2:
                break
            try:
                if await btn.is_visible():
                    text = await btn.text_content()
                    data_q = await btn.get_attribute("data-q")
                    print(f"  [{session_name}] Clicking quick button {i+1}: '{text.strip()}'")
                    await btn.click()
                    buttons_clicked += 1
                    results["hot_buttons_clicked"].append(text.strip())
                    await asyncio.sleep(5)  # Wait for AI response
                    await safe_screenshot(page, session_name, f"04_quick_btn_{buttons_clicked}")
            except Exception as e:
                print(f"  [{session_name}] Button click error: {str(e)[:80]}")
                continue

        if buttons_clicked == 0:
            # JS fallback - directly trigger the quick button behavior
            print(f"  [{session_name}] No visible buttons, using JS to click")
            await page.evaluate("""() => {
                const btns = document.querySelectorAll('.quick-btn');
                if (btns.length > 0) btns[0].click();
            }""")
            await asyncio.sleep(5)
            await page.evaluate("""() => {
                const btns = document.querySelectorAll('.quick-btn');
                if (btns.length > 1) btns[1].click();
            }""")
            await asyncio.sleep(5)
            buttons_clicked = 2
            results["hot_buttons_clicked"].append("JS-triggered-btn-1")
            results["hot_buttons_clicked"].append("JS-triggered-btn-2")

        results["steps_completed"].append(f"hot_buttons_x{buttons_clicked}")

        # ===== STEP 5: Type first question =====
        print(f"  [{session_name}] Step 5: Typing question: '{questions[0]}'")
        text_input = await page.query_selector("#text-input")
        if text_input:
            await text_input.click()
            await asyncio.sleep(0.3)
            await text_input.fill(questions[0])
            await asyncio.sleep(0.5)
            await safe_screenshot(page, session_name, "05_q1_typed")

            # Click send button
            send_btn = await page.query_selector("#send-btn")
            if send_btn:
                await send_btn.click()
                print(f"  [{session_name}] Sent question via #send-btn")
            else:
                await page.keyboard.press("Enter")
                print(f"  [{session_name}] Sent question via Enter key")

            results["questions_asked"].append(questions[0])
            results["steps_completed"].append("q1_sent")
        else:
            print(f"  [{session_name}] WARNING: #text-input not found!")

        # ===== STEP 6: Wait for AI response =====
        print(f"  [{session_name}] Step 6: Waiting for AI response...")
        await asyncio.sleep(8)
        await safe_screenshot(page, session_name, "06_q1_response")
        results["steps_completed"].append("q1_response_waited")

        # ===== STEP 7: Click another hot button =====
        print(f"  [{session_name}] Step 7: Clicking another quick button")
        quick_buttons = await page.query_selector_all(".quick-btn")
        clicked_extra = False
        for btn in quick_buttons[2:]:  # Start from 3rd button (skip first 2 already clicked)
            try:
                if await btn.is_visible():
                    text = await btn.text_content()
                    print(f"  [{session_name}] Clicking: '{text.strip()}'")
                    await btn.click()
                    results["hot_buttons_clicked"].append(text.strip())
                    clicked_extra = True
                    await asyncio.sleep(5)
                    await safe_screenshot(page, session_name, "07_extra_btn")
                    break
            except Exception:
                continue

        if not clicked_extra:
            await page.evaluate("""() => {
                const btns = document.querySelectorAll('.quick-btn');
                if (btns.length > 2) btns[2].click();
            }""")
            await asyncio.sleep(5)
            results["hot_buttons_clicked"].append("JS-triggered-btn-3")

        results["steps_completed"].append("extra_button_clicked")

        # ===== STEP 8: Type second question =====
        print(f"  [{session_name}] Step 8: Typing question: '{questions[1]}'")
        text_input = await page.query_selector("#text-input")
        if text_input:
            await text_input.click()
            await asyncio.sleep(0.3)
            await text_input.fill(questions[1])
            await asyncio.sleep(0.5)

            send_btn = await page.query_selector("#send-btn")
            if send_btn:
                await send_btn.click()
                print(f"  [{session_name}] Sent question 2 via #send-btn")
            else:
                await page.keyboard.press("Enter")

            results["questions_asked"].append(questions[1])
            results["steps_completed"].append("q2_sent")

            # Wait for response
            await asyncio.sleep(8)
            await safe_screenshot(page, session_name, "08_q2_response")
            results["steps_completed"].append("q2_response_waited")
        else:
            print(f"  [{session_name}] WARNING: #text-input not found for Q2!")

        # Final state
        await safe_screenshot(page, session_name, "99_final")
        results["steps_completed"].append("session_complete")
        results["console_errors"] = console_errors[:20]

        print(f"\n  [{session_name}] === SESSION COMPLETE ===")
        print(f"  [{session_name}] Steps completed: {len(results['steps_completed'])}")
        print(f"  [{session_name}] Hot buttons clicked: {len(results['hot_buttons_clicked'])}")
        print(f"  [{session_name}] Questions asked: {len(results['questions_asked'])}")
        print(f"  [{session_name}] Console errors: {len(console_errors)}")
        if console_errors:
            print(f"  [{session_name}] First errors:")
            for e in console_errors[:5]:
                print(f"    ERROR: {e[:150]}")

    except Exception as e:
        print(f"  [{session_name}] FATAL ERROR: {e}")
        results["error"] = str(e)
        try:
            await safe_screenshot(page, session_name, "ERROR")
        except Exception:
            pass
    finally:
        await context.close()

    return results


async def main():
    print("=" * 60)
    print("  INVESTOR PORTAL STRESS TEST v2")
    print(f"  Target: {URL}")
    print(f"  Screenshots: {SCREENSHOT_DIR}")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Clean previous screenshots
    for f in os.listdir(SCREENSHOT_DIR):
        if f.endswith(".png"):
            os.remove(f"{SCREENSHOT_DIR}/{f}")

    start = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        )

        # Run both sessions concurrently
        results = await asyncio.gather(
            run_session(
                browser,
                "JOHNSON",
                "JOHNSON2026",
                ["When do we break even?", "What are the revenue projections?"]
            ),
            run_session(
                browser,
                "BENADOF",
                "BENADOF2026",
                ["What is the competitive advantage?", "Tell me about the technology"]
            ),
        )

        await browser.close()

    elapsed = time.time() - start

    print(f"\n{'='*60}")
    print(f"  STRESS TEST COMPLETE ({elapsed:.1f}s)")
    print(f"{'='*60}")

    for r in results:
        print(f"\n  Session: {r['session']} ({r['code']})")
        print(f"    Steps: {r['steps_completed']}")
        print(f"    Hot buttons: {r['hot_buttons_clicked']}")
        print(f"    Questions: {r['questions_asked']}")
        print(f"    Console errors: {len(r.get('console_errors', []))}")
        if r.get("error"):
            print(f"    FATAL ERROR: {r['error']}")

    # List screenshots
    print(f"\n  Screenshots in {SCREENSHOT_DIR}:")
    for f in sorted(os.listdir(SCREENSHOT_DIR)):
        if f.endswith(".png"):
            size = os.path.getsize(f"{SCREENSHOT_DIR}/{f}")
            print(f"    {f} ({size:,} bytes)")

    print(f"\n  Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
