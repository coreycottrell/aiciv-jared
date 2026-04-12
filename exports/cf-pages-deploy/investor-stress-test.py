#!/usr/bin/env python3
"""
Investor Portal Stress Test - Two concurrent browser sessions
Session 1: Claire Hughes Johnson (JOHNSON2026)
Session 2: Walter Benadof (BENADOF2026)
"""

import asyncio
import time
import os

from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/tmp/investor-stress-test"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

URL = "https://purebrain.ai/investment-opportunity/"


async def screenshot(page, session_name, label):
    """Take a screenshot with descriptive label."""
    path = f"{SCREENSHOT_DIR}/{session_name}_{label}.png"
    await page.screenshot(path=path, full_page=False)
    print(f"  [SCREENSHOT] {path}")
    return path


async def wait_and_log(page, session_name, seconds=3):
    """Wait and log."""
    print(f"  [{session_name}] Waiting {seconds}s...")
    await asyncio.sleep(seconds)


async def find_and_click_hot_buttons(page, session_name, count=2):
    """Find interactive Q&A hot buttons and click them."""
    clicked = 0

    # Try various selectors for hot buttons / Q&A buttons
    selectors = [
        "button.hot-button",
        ".hot-button",
        "button.question-btn",
        ".question-btn",
        "button.qa-btn",
        ".qa-button",
        "[data-type='hot-button']",
        ".investor-question",
        ".quick-question",
        # Common patterns for interactive Q&A buttons
        "button:has-text('revenue')",
        "button:has-text('market')",
        "button:has-text('team')",
        "button:has-text('technology')",
        "button:has-text('traction')",
        "button:has-text('vision')",
        "button:has-text('funding')",
        "button:has-text('competitive')",
        "button:has-text('product')",
        "button:has-text('growth')",
        # Broader selectors
        ".chat-suggestions button",
        ".suggestions button",
        ".prompt-buttons button",
        ".quick-actions button",
    ]

    for selector in selectors:
        if clicked >= count:
            break
        try:
            elements = await page.query_selector_all(selector)
            for el in elements:
                if clicked >= count:
                    break
                if await el.is_visible():
                    text = await el.text_content()
                    print(f"  [{session_name}] Clicking hot button: '{text.strip()[:50] if text else 'no text'}'")
                    await el.click()
                    clicked += 1
                    await screenshot(page, session_name, f"hot_button_{clicked}")
                    await asyncio.sleep(4)  # Wait for response
        except Exception:
            continue

    if clicked == 0:
        # Fallback: look for any clickable buttons in main content area
        print(f"  [{session_name}] No specific hot buttons found, trying generic button search...")
        try:
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                if clicked >= count:
                    break
                if await btn.is_visible():
                    text = await btn.text_content()
                    text_clean = text.strip() if text else ""
                    # Skip navigation/generic buttons
                    if text_clean and len(text_clean) > 3 and text_clean.lower() not in ["close", "x", "menu", "submit", "send"]:
                        print(f"  [{session_name}] Clicking button: '{text_clean[:50]}'")
                        await btn.click()
                        clicked += 1
                        await screenshot(page, session_name, f"hot_button_{clicked}")
                        await asyncio.sleep(4)
        except Exception as e:
            print(f"  [{session_name}] Button search error: {e}")

    print(f"  [{session_name}] Clicked {clicked} hot buttons total")
    return clicked


async def type_question(page, session_name, question):
    """Find the chat input and type a question."""
    print(f"  [{session_name}] Typing question: '{question}'")

    input_selectors = [
        "textarea",
        "input[type='text']",
        ".chat-input",
        ".message-input",
        "#user-input",
        "#chat-input",
        "input[placeholder*='question']",
        "input[placeholder*='ask']",
        "textarea[placeholder*='question']",
        "textarea[placeholder*='ask']",
        "input[placeholder*='type']",
        "textarea[placeholder*='type']",
    ]

    for selector in input_selectors:
        try:
            el = await page.query_selector(selector)
            if el and await el.is_visible():
                await el.click()
                await asyncio.sleep(0.5)
                await el.fill(question)
                await screenshot(page, session_name, f"typed_{question[:20].replace(' ', '_')}")

                # Try to submit - press Enter or click send button
                await page.keyboard.press("Enter")
                print(f"  [{session_name}] Submitted question via Enter")
                await asyncio.sleep(6)  # Wait for AI response
                await screenshot(page, session_name, f"response_{question[:20].replace(' ', '_')}")
                return True
        except Exception:
            continue

    # Fallback: try clicking a send button after typing
    print(f"  [{session_name}] Could not find input field with standard selectors, trying page evaluation...")
    try:
        # Use JS to find input elements
        result = await page.evaluate("""() => {
            const inputs = document.querySelectorAll('input, textarea');
            return Array.from(inputs).map(el => ({
                tag: el.tagName,
                type: el.type,
                placeholder: el.placeholder,
                id: el.id,
                className: el.className,
                visible: el.offsetParent !== null
            }));
        }""")
        print(f"  [{session_name}] Found inputs: {result}")
    except Exception as e:
        print(f"  [{session_name}] JS eval error: {e}")

    return False


async def enter_investor_code(page, session_name, code):
    """Find the investor code input and enter the code."""
    print(f"  [{session_name}] Looking for investor code input...")

    code_selectors = [
        "input[type='text']",
        "input[type='password']",
        "input[placeholder*='code']",
        "input[placeholder*='Code']",
        "input[placeholder*='investor']",
        "input[placeholder*='access']",
        "#investor-code",
        "#access-code",
        ".code-input input",
        "input.code-input",
    ]

    for selector in code_selectors:
        try:
            el = await page.query_selector(selector)
            if el and await el.is_visible():
                await el.click()
                await asyncio.sleep(0.3)
                await el.fill(code)
                print(f"  [{session_name}] Entered code '{code}' via selector '{selector}'")
                await screenshot(page, session_name, "code_entered")

                # Try to submit the code
                await page.keyboard.press("Enter")
                await asyncio.sleep(2)

                # Also try clicking a submit/enter button
                submit_selectors = [
                    "button[type='submit']",
                    "button:has-text('Enter')",
                    "button:has-text('Submit')",
                    "button:has-text('Access')",
                    "button:has-text('Go')",
                    ".submit-btn",
                    ".enter-btn",
                ]
                for sub_sel in submit_selectors:
                    try:
                        sub_btn = await page.query_selector(sub_sel)
                        if sub_btn and await sub_btn.is_visible():
                            await sub_btn.click()
                            print(f"  [{session_name}] Clicked submit button: '{sub_sel}'")
                            break
                    except Exception:
                        continue

                await asyncio.sleep(3)
                await screenshot(page, session_name, "after_code_submit")
                return True
        except Exception:
            continue

    print(f"  [{session_name}] Could not find code input, dumping page state...")
    try:
        inputs = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('input, textarea')).map(el => ({
                tag: el.tagName, type: el.type, placeholder: el.placeholder,
                id: el.id, className: el.className, visible: el.offsetParent !== null
            }));
        }""")
        print(f"  [{session_name}] Page inputs: {inputs}")
    except Exception as e:
        print(f"  [{session_name}] Error: {e}")

    return False


async def click_through_gates(page, session_name):
    """Click through any entrance layers/gates after code entry."""
    print(f"  [{session_name}] Looking for entrance gates/layers to click through...")

    gate_selectors = [
        "button:has-text('Enter')",
        "button:has-text('Continue')",
        "button:has-text('Proceed')",
        "button:has-text('Start')",
        "button:has-text('Begin')",
        "button:has-text('Open')",
        "button:has-text('Accept')",
        ".enter-button",
        ".gate-button",
        ".welcome-btn",
        ".start-btn",
        "a:has-text('Enter')",
        "a:has-text('Continue')",
    ]

    gates_clicked = 0
    for _ in range(3):  # Try up to 3 gate layers
        clicked_this_round = False
        for selector in gate_selectors:
            try:
                el = await page.query_selector(selector)
                if el and await el.is_visible():
                    text = await el.text_content()
                    print(f"  [{session_name}] Clicking gate: '{text.strip()[:30] if text else selector}'")
                    await el.click()
                    gates_clicked += 1
                    clicked_this_round = True
                    await asyncio.sleep(2)
                    await screenshot(page, session_name, f"gate_{gates_clicked}")
                    break
            except Exception:
                continue
        if not clicked_this_round:
            break

    print(f"  [{session_name}] Clicked through {gates_clicked} gates")
    return gates_clicked


async def run_session(browser, session_name, investor_code, questions):
    """Run a single investor session."""
    print(f"\n{'='*60}")
    print(f"  SESSION: {session_name} (Code: {investor_code})")
    print(f"{'='*60}")

    context = await browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) StressTest-{session_name}"
    )
    page = await context.new_page()

    # Capture console logs
    console_logs = []
    page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

    try:
        # Step 1: Navigate
        print(f"  [{session_name}] Step 1: Navigating to {URL}")
        await page.goto(URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        await screenshot(page, session_name, "01_landing")

        # Step 2: Enter investor code
        print(f"  [{session_name}] Step 2: Entering investor code")
        code_entered = await enter_investor_code(page, session_name, investor_code)
        if not code_entered:
            print(f"  [{session_name}] WARNING: Could not enter code, trying to continue anyway...")

        # Step 3: Click through gates
        print(f"  [{session_name}] Step 3: Clicking through entrance gates")
        await click_through_gates(page, session_name)
        await screenshot(page, session_name, "03_after_gates")

        # Step 4: Click 2+ hot buttons
        print(f"  [{session_name}] Step 4: Clicking hot buttons")
        buttons_clicked = await find_and_click_hot_buttons(page, session_name, count=2)

        # Step 5: Type first question
        print(f"  [{session_name}] Step 5: Typing first question")
        q1_success = await type_question(page, session_name, questions[0])

        # Step 6: Wait for AI response (already waited in type_question)
        print(f"  [{session_name}] Step 6: Response captured")

        # Step 7: Click another hot button
        print(f"  [{session_name}] Step 7: Clicking another hot button")
        await find_and_click_hot_buttons(page, session_name, count=1)

        # Step 8: Type second question
        print(f"  [{session_name}] Step 8: Typing second question")
        q2_success = await type_question(page, session_name, questions[1])

        # Final screenshot
        await screenshot(page, session_name, "99_final_state")

        # Summary
        print(f"\n  [{session_name}] SESSION COMPLETE")
        print(f"  [{session_name}] Code entered: {code_entered}")
        print(f"  [{session_name}] Hot buttons clicked: {buttons_clicked}")
        print(f"  [{session_name}] Q1 submitted: {q1_success}")
        print(f"  [{session_name}] Q2 submitted: {q2_success}")
        print(f"  [{session_name}] Console logs: {len(console_logs)} entries")

        # Print errors from console
        errors = [l for l in console_logs if l.startswith("[error]")]
        if errors:
            print(f"  [{session_name}] CONSOLE ERRORS ({len(errors)}):")
            for e in errors[:10]:
                print(f"    {e[:200]}")

        return {
            "session": session_name,
            "code_entered": code_entered,
            "buttons_clicked": buttons_clicked,
            "q1_success": q1_success,
            "q2_success": q2_success,
            "console_logs": len(console_logs),
            "console_errors": len(errors),
        }

    except Exception as e:
        print(f"  [{session_name}] ERROR: {e}")
        await screenshot(page, session_name, "ERROR")
        return {"session": session_name, "error": str(e)}
    finally:
        await context.close()


async def main():
    print("=" * 60)
    print("  INVESTOR PORTAL STRESS TEST")
    print(f"  Target: {URL}")
    print(f"  Screenshots: {SCREENSHOT_DIR}")
    print("=" * 60)

    start = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

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
        print(f"  {r}")

    # List all screenshots
    print(f"\n  Screenshots saved to {SCREENSHOT_DIR}:")
    for f in sorted(os.listdir(SCREENSHOT_DIR)):
        if f.endswith(".png"):
            size = os.path.getsize(f"{SCREENSHOT_DIR}/{f}")
            print(f"    {f} ({size:,} bytes)")


if __name__ == "__main__":
    asyncio.run(main())
