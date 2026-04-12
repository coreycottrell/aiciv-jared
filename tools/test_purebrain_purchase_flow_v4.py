#!/usr/bin/env python3
"""
PureBrain.ai Complete Purchase Flow Test - Version 4
Tests the full user journey: Begin Awakening -> Chat -> Name AI -> Pricing -> Form -> PayPal

Key insight: The AI asks for YOUR name first, then asks you to name IT.
The pricing section appears WITHIN the chat after naming.

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
OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/purebrain-flow-test-v4")
AI_NAME = "TestBot"
USER_NAME = "Aether Test"
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


async def send_chat_message(page, message):
    """Send a message in the chat"""
    chat_selectors = [
        "input[placeholder*='response']",
        "input[placeholder*='Response']",
        "input[type='text']",
        "textarea",
    ]

    for selector in chat_selectors:
        try:
            elements = page.locator(selector)
            count = await elements.count()
            for i in range(count):
                chat_input = elements.nth(i)
                if await chat_input.is_visible(timeout=1000):
                    await chat_input.click()
                    await asyncio.sleep(0.3)
                    await chat_input.fill(message)
                    await page.keyboard.press("Enter")
                    print(f"  Sent: '{message}'")
                    return True
        except:
            continue
    return False


async def run_purchase_flow():
    """Execute the complete PureBrain purchase flow"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("PureBrain.ai Purchase Flow Test - V4")
    print(f"{'='*60}\n")
    print(f"User Name: {USER_NAME}")
    print(f"AI Name: {AI_NAME}")
    print(f"Test Data: {TEST_DATA}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    results = {
        "screenshots": [],
        "ai_name": AI_NAME,
        "user_name": USER_NAME,
        "tier_clicked": None,
        "form_result": None,
        "final_outcome": None,
        "console_errors": [],
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
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
            await page.goto(SITE_URL, wait_until="load", timeout=90000)
            await asyncio.sleep(5)
            results["screenshots"].append(await take_screenshot(page, "01_homepage"))

            # STEP 2: Scroll to BEGIN YOUR AWAKENING and click Begin Awakening
            print("\nSTEP 2: Start the awakening conversation")
            print("-" * 40)

            # Scroll to find the section
            for scroll_pos in range(0, 6000, 300):
                await page.evaluate(f"window.scrollTo(0, {scroll_pos})")
                await asyncio.sleep(0.3)
                try:
                    element = page.locator("text=BEGIN YOUR AWAKENING").first
                    if await element.is_visible(timeout=300):
                        print(f"  Found BEGIN YOUR AWAKENING section")
                        break
                except:
                    continue

            # Click Begin Awakening
            try:
                btn = page.locator("text=Begin Awakening").first
                if await btn.is_visible(timeout=3000):
                    await btn.click()
                    print("  Clicked 'Begin Awakening'")
                    await asyncio.sleep(5)
                    results["screenshots"].append(await take_screenshot(page, "02_chat_started"))
            except Exception as e:
                print(f"  Could not click Begin Awakening: {e}")

            # STEP 3: Chat conversation - give user name
            print("\nSTEP 3: Introduce yourself (give user name)")
            print("-" * 40)

            # Wait for initial AI response
            await asyncio.sleep(5)
            results["screenshots"].append(await take_screenshot(page, "03_initial_ai_message"))

            # The AI asks "What should I call you?" - respond with user name
            if await send_chat_message(page, f"My name is {USER_NAME}"):
                await asyncio.sleep(10)
                results["screenshots"].append(await take_screenshot(page, "04_gave_user_name"))

            # STEP 4: Continue conversation - answer AI questions
            print("\nSTEP 4: Continue conversation")
            print("-" * 40)

            # The AI might ask more questions, respond naturally
            if await send_chat_message(page, "I'm exploring AI solutions for business productivity"):
                await asyncio.sleep(10)
                results["screenshots"].append(await take_screenshot(page, "05_explained_interest"))

            # STEP 5: Name the AI when prompted
            print("\nSTEP 5: Name the AI")
            print("-" * 40)

            # Look for prompts about naming the AI
            # The AI might ask "What would you like to call me?"
            if await send_chat_message(page, f"I'll call you {AI_NAME}"):
                print(f"  Named AI: {AI_NAME}")
                await asyncio.sleep(10)
                results["screenshots"].append(await take_screenshot(page, "06_named_ai"))

            # STEP 6: Continue until pricing appears
            print("\nSTEP 6: Look for pricing/activation options")
            print("-" * 40)

            # Continue the conversation to trigger pricing
            if await send_chat_message(page, "How can we work together?"):
                await asyncio.sleep(10)
                results["screenshots"].append(await take_screenshot(page, "07_asking_about_options"))

            # Try a more direct message
            if await send_chat_message(page, "I'd like to activate our partnership"):
                await asyncio.sleep(10)
                results["screenshots"].append(await take_screenshot(page, "08_requesting_activation"))

            # STEP 7: Look for pricing elements on page
            print("\nSTEP 7: Search for pricing/payment options")
            print("-" * 40)

            # Take full page screenshot to see current state
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(0.5)
            full_page = OUTPUT_DIR / "FULLPAGE_after_chat.png"
            await page.screenshot(path=str(full_page), full_page=True)
            print(f"  Full page: {full_page}")

            # Scroll to find pricing
            pricing_found = False
            for scroll_pos in range(0, 8000, 300):
                await page.evaluate(f"window.scrollTo(0, {scroll_pos})")
                await asyncio.sleep(0.2)

                pricing_indicators = [
                    "text=BRING",
                    f"text=BRING {AI_NAME.upper()} FULLY ONLINE",
                    "text=FULLY ONLINE",
                    "text=$79",
                    "text=$149",
                    "text=$499",
                    "text=Get Started",
                    "text=Activate",
                ]

                for indicator in pricing_indicators:
                    try:
                        element = page.locator(indicator).first
                        if await element.is_visible(timeout=200):
                            print(f"  Found: {indicator} at scroll={scroll_pos}")
                            pricing_found = True
                            results["screenshots"].append(await take_screenshot(page, "09_pricing_found"))
                            break
                    except:
                        continue

                if pricing_found:
                    break

            if not pricing_found:
                print("  WARNING: Pricing not yet visible - may need more conversation")
                results["screenshots"].append(await take_screenshot(page, "09_current_state"))

            # STEP 8: Try to click pricing tier
            print("\nSTEP 8: Click pricing tier (if available)")
            print("-" * 40)

            tier_selectors = [
                "text=Get Started",
                f"text=Activate {AI_NAME} Now",
                f"text=Activate {AI_NAME}",
                "text=Activate Now",
                "button:has-text('Get Started')",
                "a:has-text('Get Started')",
                "button:has-text('Activate')",
            ]

            tier_clicked = False
            for selector in tier_selectors:
                try:
                    buttons = page.locator(selector)
                    count = await buttons.count()
                    if count > 0:
                        await buttons.first.click()
                        print(f"  Clicked: {selector}")
                        results["tier_clicked"] = selector
                        tier_clicked = True
                        await asyncio.sleep(3)
                        results["screenshots"].append(await take_screenshot(page, "10_tier_clicked"))
                        break
                except:
                    continue

            if not tier_clicked:
                print("  WARNING: Could not find tier buttons")
                results["tier_clicked"] = "NOT FOUND"

            # STEP 9: Look for form fields
            print("\nSTEP 9: Look for form fields")
            print("-" * 40)

            await asyncio.sleep(2)

            form_fields = {
                "name": ["input[name*='name']", "input[placeholder*='name']", "#name"],
                "email": ["input[type='email']", "input[name*='email']", "input[placeholder*='email']"],
                "company": ["input[name*='company']", "input[placeholder*='company']"],
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
                results["screenshots"].append(await take_screenshot(page, "11_form_filled"))
                results["form_result"] = f"Filled: {list(form_filled.keys())}"

                # Try to submit
                for selector in ["button[type='submit']", "text=Submit", "text=Continue"]:
                    try:
                        element = page.locator(selector).first
                        if await element.is_visible(timeout=2000):
                            await element.click()
                            print(f"  Submitted: {selector}")
                            await asyncio.sleep(5)
                            results["screenshots"].append(await take_screenshot(page, "12_submitted"))
                            results["form_result"] = "SUBMITTED"
                            break
                    except:
                        continue
            else:
                print("  No form fields found")
                results["form_result"] = "NO FORM FOUND"

            # STEP 10: Check for PayPal
            print("\nSTEP 10: Check for PayPal/payment")
            print("-" * 40)

            paypal_selectors = ["text=PayPal", "[class*='paypal']", "iframe[src*='paypal']"]
            for selector in paypal_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        print(f"  Found: {selector}")
                        results["final_outcome"] = f"PAYPAL FOUND: {selector}"
                        break
                except:
                    continue

            if not results["final_outcome"]:
                results["final_outcome"] = "FLOW INCOMPLETE - Pricing/PayPal not reached"

            results["screenshots"].append(await take_screenshot(page, "13_final_state"))

            # Final full page
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(0.5)
            final_full = OUTPUT_DIR / "FULLPAGE_final.png"
            await page.screenshot(path=str(final_full), full_page=True)
            print(f"\n  Final full page: {final_full}")

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
            try:
                results["screenshots"].append(await take_screenshot(page, "ERROR_state"))
            except:
                pass
            results["final_outcome"] = f"ERROR: {e}"

        finally:
            await browser.close()

    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"User Name: {results['user_name']}")
    print(f"AI Name: {results['ai_name']}")
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
