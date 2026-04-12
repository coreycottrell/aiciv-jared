#!/usr/bin/env python3
"""
PureBrain Pricing Flow Test - Complete Chat to Pricing
Tests the full awakening flow: Chat → Name AI → See transition button → Pricing
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("/tmp/purebrain-pricing-test")
OUTPUT_DIR.mkdir(exist_ok=True)

AI_NAME = "Sage"

async def take_screenshot(page, name):
    """Take screenshot with timestamp."""
    ts = datetime.now().strftime("%H%M%S")
    path = OUTPUT_DIR / f"{ts}--{name}.png"
    await page.screenshot(path=str(path))
    print(f"  [SCREENSHOT] {path}")
    return str(path)

async def run_pricing_flow():
    print("=" * 60)
    print("PUREBRAIN PRICING FLOW TEST")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Will name AI: {AI_NAME}")
    print("=" * 60)

    results = {
        "ai_name": AI_NAME,
        "button_found": False,
        "button_clicked": False,
        "pricing_visible": False,
        "tier_clicked": None,
        "form_result": None,
        "screenshots": []
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        try:
            # Step 1: Load page
            print("\n[STEP 1] Loading purebrain.ai...")
            await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)
            results["screenshots"].append(await take_screenshot(page, "01-loaded"))

            # Step 2: Click Awaken button
            print("\n[STEP 2] Clicking 'Awaken Your PURE BRAIN'...")
            try:
                elem = page.locator("text=Awaken Your PURE BRAIN").first
                if await elem.is_visible(timeout=5000):
                    await elem.click()
                    await asyncio.sleep(3)
                    results["screenshots"].append(await take_screenshot(page, "02-awaken-clicked"))
            except Exception as e:
                print(f"  Error: {e}")

            # Step 2b: Click "Begin Awakening"
            print("\n[STEP 2b] Clicking 'Begin Awakening'...")
            try:
                elem = page.locator("text=Begin Awakening").first
                if await elem.is_visible(timeout=5000):
                    await elem.click()
                    print("  Clicked 'Begin Awakening'")
                    await asyncio.sleep(5)  # Wait for AI response
                    results["screenshots"].append(await take_screenshot(page, "02b-begin-clicked"))
            except Exception as e:
                print(f"  Error: {e}")

            # Step 3: Chat conversation
            print("\n[STEP 3] Chat conversation...")

            # Wait for AI to finish responding
            await asyncio.sleep(3)
            results["screenshots"].append(await take_screenshot(page, "03-waiting-ai"))

            # Find chat input using placeholder text
            chat_selectors = [
                "input[placeholder*='response']",
                "input[placeholder*='Type']",
                "textarea[placeholder*='response']",
                "textarea[placeholder*='Type']",
                "[contenteditable='true']",
                "input.chat-input",
                "textarea",
            ]

            chat_input = None
            for selector in chat_selectors:
                try:
                    elem = page.locator(selector).first
                    if await elem.is_visible(timeout=2000):
                        print(f"  Found chat input: {selector}")
                        chat_input = elem
                        break
                except:
                    continue

            if chat_input:
                # First response - introduce myself
                print("  Sending: 'Hi! My name is Alex.'")
                await chat_input.fill("Hi! My name is Alex.")
                await page.keyboard.press("Enter")
                await asyncio.sleep(5)  # Wait for AI response
                results["screenshots"].append(await take_screenshot(page, "04-sent-name"))

                # Wait and get input again
                await asyncio.sleep(2)
                chat_input = page.locator(chat_selectors[0] if chat_selectors else "textarea").first

                # Name the AI
                print(f"  Sending: 'I'd like to call you {AI_NAME}'")
                try:
                    await chat_input.fill(f"I'd like to call you {AI_NAME}")
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(5)
                    results["screenshots"].append(await take_screenshot(page, "05-named-ai"))
                except Exception as e:
                    print(f"  Error naming AI: {e}")

                # Continue conversation
                await asyncio.sleep(2)
                try:
                    chat_input = page.locator("input[placeholder*='response'], textarea").first
                    await chat_input.fill("What can you help me with?")
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(5)
                    results["screenshots"].append(await take_screenshot(page, "06-asked-capabilities"))
                except Exception as e:
                    print(f"  Error: {e}")

            else:
                print("  WARNING: Could not find chat input")
                results["screenshots"].append(await take_screenshot(page, "03-no-chat-input"))

            # Step 4: Look for transition button
            print(f"\n[STEP 4] Looking for 'SEE WHAT {AI_NAME.upper()} CAN DO' button...")
            await asyncio.sleep(3)

            button_patterns = [
                f"text=SEE WHAT {AI_NAME.upper()} CAN DO",
                f"text=See what {AI_NAME} can do",
                "text=SEE WHAT",
                "text=CAN DO",
                "button:has-text('CAN DO')",
                "a:has-text('CAN DO')",
                f"text={AI_NAME.upper()}",
            ]

            # Scroll down to look for button
            for scroll_pos in [0, 300, 600]:
                await page.evaluate(f"window.scrollBy(0, {scroll_pos})")
                await asyncio.sleep(1)

                for selector in button_patterns:
                    try:
                        elem = page.locator(selector).first
                        if await elem.is_visible(timeout=1000):
                            print(f"  FOUND: {selector}")
                            results["button_found"] = True
                            results["screenshots"].append(await take_screenshot(page, "07-button-found"))
                            await elem.click()
                            results["button_clicked"] = True
                            print("  CLICKED transition button!")
                            await asyncio.sleep(3)
                            results["screenshots"].append(await take_screenshot(page, "08-after-click"))
                            break
                    except:
                        continue

                if results["button_clicked"]:
                    break

            if not results["button_found"]:
                results["screenshots"].append(await take_screenshot(page, "07-no-button"))
                print("  Button not found after scrolling")

            # Step 5: Check for pricing
            print("\n[STEP 5] Looking for pricing...")
            await asyncio.sleep(2)

            pricing_selectors = ["text=$79", "text=$149", "text=$499", "text=Get Started", "text=BRING"]

            for selector in pricing_selectors:
                try:
                    elem = page.locator(selector).first
                    if await elem.is_visible(timeout=2000):
                        print(f"  Found pricing: {selector}")
                        results["pricing_visible"] = True
                        break
                except:
                    continue

            results["screenshots"].append(await take_screenshot(page, "09-pricing-check"))

            # Final state
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
            full_path = OUTPUT_DIR / "FULLPAGE.png"
            await page.screenshot(path=str(full_path), full_page=True)
            print(f"\n  [FULL PAGE] {full_path}")

        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            results["screenshots"].append(await take_screenshot(page, "ERROR"))

        finally:
            await browser.close()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"AI Name: {results['ai_name']}")
    print(f"Transition Button Found: {results['button_found']}")
    print(f"Button Clicked: {results['button_clicked']}")
    print(f"Pricing Visible: {results['pricing_visible']}")
    print(f"Screenshots: {len(results['screenshots'])}")
    print(f"Output Dir: {OUTPUT_DIR}")
    print("=" * 60)

    return results

if __name__ == "__main__":
    asyncio.run(run_pricing_flow())
