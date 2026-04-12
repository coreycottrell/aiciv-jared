#!/usr/bin/env python3
"""
PureBrain.ai Complete Purchase Flow Test
Tests the full user journey: Chat -> Name AI -> Pricing -> Form -> PayPal

browser-vision-tester agent
Date: 2026-02-17
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
SITE_URL = "https://purebrain.ai"
OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/purebrain-flow-test")
AI_NAME = "TestBot"
TEST_DATA = {
    "name": "Aether Integration Test",
    "email": "aether.test.flow@purebrain.ai",
    "company": "Pure Technology QA"
}

# Screenshot counter for ordering
screenshot_counter = 0


async def take_screenshot(page, label):
    """Take a screenshot with numbered prefix for ordering"""
    global screenshot_counter
    screenshot_counter += 1
    filename = f"{screenshot_counter:03d}_{label}_{datetime.now().strftime('%H%M%S')}.png"
    filepath = OUTPUT_DIR / filename
    await page.screenshot(path=str(filepath), full_page=False)
    print(f"  [Screenshot {screenshot_counter}] {label}: {filepath}")
    return str(filepath)


async def run_purchase_flow():
    """Execute the complete PureBrain purchase flow"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("PureBrain.ai Purchase Flow Test")
    print(f"{'='*60}\n")
    print(f"AI Name: {AI_NAME}")
    print(f"Test Data: {TEST_DATA}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    results = {
        "screenshots": [],
        "ai_name": AI_NAME,
        "tier_clicked": None,
        "form_result": None,
        "final_outcome": None,
        "console_errors": [],
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Headless mode for WSL2
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # Capture console errors
        page.on("console", lambda msg: results["console_errors"].append({
            "type": msg.type,
            "text": msg.text
        }) if msg.type == "error" else None)

        try:
            # STEP 1: Navigate to homepage
            print("STEP 1: Navigate to PureBrain.ai")
            print("-" * 40)
            await page.goto(SITE_URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(2)
            results["screenshots"].append(await take_screenshot(page, "01_homepage"))

            # STEP 2: Find and click the begin/start button
            print("\nSTEP 2: Find and click begin/start button")
            print("-" * 40)

            # Try multiple selectors for the begin button
            begin_selectors = [
                "text=Begin",
                "text=Start",
                "text=Get Started",
                "text=Try",
                "text=Chat",
                "button:has-text('Begin')",
                "button:has-text('Start')",
                "a:has-text('Begin')",
                "a:has-text('Start')",
                ".hero button",
                "[data-testid='begin-button']",
            ]

            clicked = False
            for selector in begin_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        await element.click()
                        print(f"  Clicked: {selector}")
                        clicked = True
                        await asyncio.sleep(3)
                        results["screenshots"].append(await take_screenshot(page, "02_after_begin_click"))
                        break
                except Exception as e:
                    continue

            if not clicked:
                print("  WARNING: Could not find begin button, looking for chat interface...")
                results["screenshots"].append(await take_screenshot(page, "02_no_begin_button"))

            # STEP 3: Have a brief conversation
            print("\nSTEP 3: Chat interaction")
            print("-" * 40)

            # Look for chat input
            chat_selectors = [
                "input[type='text']",
                "textarea",
                "[contenteditable='true']",
                "input[placeholder*='message']",
                "input[placeholder*='chat']",
                "input[placeholder*='type']",
                ".chat-input",
                "#chat-input",
            ]

            chat_found = False
            for selector in chat_selectors:
                try:
                    chat_input = page.locator(selector).first
                    if await chat_input.is_visible(timeout=3000):
                        await chat_input.fill("Hello! I'm interested in AI solutions for my business.")
                        print(f"  Typed message in: {selector}")
                        chat_found = True

                        # Try to submit
                        await page.keyboard.press("Enter")
                        await asyncio.sleep(5)  # Wait for response
                        results["screenshots"].append(await take_screenshot(page, "03_chat_message_sent"))

                        # Send another message
                        await chat_input.fill("What can you help me with?")
                        await page.keyboard.press("Enter")
                        await asyncio.sleep(5)
                        results["screenshots"].append(await take_screenshot(page, "04_chat_response"))
                        break
                except Exception as e:
                    continue

            if not chat_found:
                print("  WARNING: Could not find chat input")
                results["screenshots"].append(await take_screenshot(page, "03_no_chat_input"))

            # STEP 4: Name the AI
            print("\nSTEP 4: Name the AI")
            print("-" * 40)

            # Look for name input or prompt
            name_selectors = [
                "input[placeholder*='name']",
                "input[placeholder*='Name']",
                "input[aria-label*='name']",
                "text=name your",
                "text=Name your",
                "#ai-name",
                ".name-input",
            ]

            named = False
            for selector in name_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        if "input" in selector.lower():
                            await element.fill(AI_NAME)
                            await page.keyboard.press("Enter")
                        else:
                            await element.click()
                            await asyncio.sleep(1)
                            # Look for input that appeared
                            name_input = page.locator("input:visible").first
                            await name_input.fill(AI_NAME)
                            await page.keyboard.press("Enter")

                        print(f"  Named AI: {AI_NAME}")
                        named = True
                        await asyncio.sleep(3)
                        results["screenshots"].append(await take_screenshot(page, "05_ai_named"))
                        break
                except Exception as e:
                    continue

            if not named:
                print("  WARNING: Could not find name input, may need more chat first")
                # Continue chatting to get to naming
                if chat_found:
                    chat_input = page.locator("input[type='text'], textarea").first
                    await chat_input.fill("I'd like to name my AI assistant")
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(5)
                    results["screenshots"].append(await take_screenshot(page, "05_asking_to_name"))

            # STEP 5: Scroll to find pricing section
            print("\nSTEP 5: Find pricing section (scroll down)")
            print("-" * 40)

            # Scroll down to find pricing
            for scroll_position in range(0, 5000, 500):
                await page.evaluate(f"window.scrollTo(0, {scroll_position})")
                await asyncio.sleep(0.5)

                # Check for pricing indicators
                pricing_indicators = [
                    "text=BRING",
                    "text=FULLY ONLINE",
                    "text=$79",
                    "text=$149",
                    "text=$499",
                    "text=Get Started",
                    "text=Activate",
                    ".pricing",
                    "#pricing",
                ]

                for indicator in pricing_indicators:
                    try:
                        element = page.locator(indicator).first
                        if await element.is_visible(timeout=500):
                            print(f"  Found pricing indicator: {indicator}")
                            results["screenshots"].append(await take_screenshot(page, f"06_pricing_found_{scroll_position}"))
                            break
                    except:
                        continue
                else:
                    continue
                break

            results["screenshots"].append(await take_screenshot(page, "06_scrolled_for_pricing"))

            # STEP 6: Click on $79 tier
            print("\nSTEP 6: Click pricing tier ($79 or $149)")
            print("-" * 40)

            tier_selectors = [
                "text=Get Started",
                f"text=Activate {AI_NAME} Now",
                "text=Activate",
                "button:has-text('Get Started')",
                "a:has-text('Get Started')",
                ".pricing-card button",
                "[data-tier='79']",
                "[data-tier='149']",
            ]

            tier_clicked = False
            for selector in tier_selectors:
                try:
                    buttons = page.locator(selector)
                    count = await buttons.count()
                    if count > 0:
                        # Click the first one (usually $79)
                        await buttons.first.click()
                        print(f"  Clicked tier button: {selector}")
                        results["tier_clicked"] = "$79 (first tier)"
                        tier_clicked = True
                        await asyncio.sleep(3)
                        results["screenshots"].append(await take_screenshot(page, "07_tier_clicked"))
                        break
                except Exception as e:
                    continue

            if not tier_clicked:
                print("  WARNING: Could not find tier buttons")
                results["tier_clicked"] = "NOT FOUND"
                results["screenshots"].append(await take_screenshot(page, "07_no_tier_buttons"))

            # STEP 7: Fill in the form
            print("\nSTEP 7: Fill in form")
            print("-" * 40)

            form_fields = {
                "name": ["input[name*='name']", "input[placeholder*='name']", "#name", "input[id*='name']"],
                "email": ["input[type='email']", "input[name*='email']", "input[placeholder*='email']", "#email"],
                "company": ["input[name*='company']", "input[placeholder*='company']", "#company", "input[name*='organization']"],
            }

            form_filled = {}
            for field, selectors in form_fields.items():
                for selector in selectors:
                    try:
                        element = page.locator(selector).first
                        if await element.is_visible(timeout=2000):
                            await element.fill(TEST_DATA[field])
                            print(f"  Filled {field}: {TEST_DATA[field]}")
                            form_filled[field] = True
                            break
                    except:
                        continue

            if form_filled:
                results["screenshots"].append(await take_screenshot(page, "08_form_filled"))

                # STEP 8: Submit form
                print("\nSTEP 8: Submit form")
                print("-" * 40)

                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "text=Submit",
                    "text=Continue",
                    "text=Next",
                    "text=Proceed",
                    "button:has-text('Submit')",
                ]

                submitted = False
                for selector in submit_selectors:
                    try:
                        element = page.locator(selector).first
                        if await element.is_visible(timeout=2000):
                            await element.click()
                            print(f"  Clicked submit: {selector}")
                            submitted = True
                            await asyncio.sleep(5)
                            results["screenshots"].append(await take_screenshot(page, "09_form_submitted"))
                            results["form_result"] = "SUBMITTED"
                            break
                    except:
                        continue

                if not submitted:
                    print("  WARNING: Could not find submit button")
                    results["form_result"] = "NO SUBMIT BUTTON"
            else:
                print("  WARNING: No form fields found")
                results["form_result"] = "NO FORM FOUND"

            # STEP 9: Check for PayPal button or confirmation
            print("\nSTEP 9: Check for PayPal/confirmation")
            print("-" * 40)

            await asyncio.sleep(3)

            paypal_indicators = [
                "text=PayPal",
                "text=paypal",
                "[class*='paypal']",
                "iframe[src*='paypal']",
                "button:has-text('PayPal')",
                "img[alt*='PayPal']",
            ]

            confirmation_indicators = [
                "text=Thank you",
                "text=Confirmation",
                "text=Success",
                "text=payment",
                "text=checkout",
            ]

            paypal_found = False
            for selector in paypal_indicators:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        print(f"  Found PayPal: {selector}")
                        paypal_found = True
                        results["final_outcome"] = "PAYPAL BUTTON VISIBLE"
                        break
                except:
                    continue

            if not paypal_found:
                for selector in confirmation_indicators:
                    try:
                        element = page.locator(selector).first
                        if await element.is_visible(timeout=2000):
                            print(f"  Found confirmation: {selector}")
                            results["final_outcome"] = f"CONFIRMATION PAGE: {selector}"
                            break
                    except:
                        continue

            if not results["final_outcome"]:
                results["final_outcome"] = "UNKNOWN - CHECK SCREENSHOTS"

            results["screenshots"].append(await take_screenshot(page, "10_final_state"))

            # Capture full page
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
            full_page_path = OUTPUT_DIR / "FULL_PAGE_final.png"
            await page.screenshot(path=str(full_page_path), full_page=True)
            print(f"\n  [Full Page Screenshot] {full_page_path}")

        except Exception as e:
            print(f"\nERROR: {e}")
            results["screenshots"].append(await take_screenshot(page, "ERROR_state"))
            results["final_outcome"] = f"ERROR: {e}"

        finally:
            await browser.close()

    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"AI Name Used: {results['ai_name']}")
    print(f"Tier Clicked: {results['tier_clicked']}")
    print(f"Form Result: {results['form_result']}")
    print(f"Final Outcome: {results['final_outcome']}")
    print(f"Console Errors: {len(results['console_errors'])}")
    print(f"Screenshots: {len(results['screenshots'])}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    asyncio.run(run_purchase_flow())
