#!/usr/bin/env python3
"""
PureBrain.ai Complete Purchase Flow Test - Version 2
Tests the full user journey: Chat -> Name AI -> Pricing -> Form -> PayPal

Improved based on visual analysis of the page structure.

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
OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/purebrain-flow-test-v2")
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


async def get_page_html(page):
    """Get visible text content for debugging"""
    content = await page.evaluate("document.body.innerText")
    return content[:2000]


async def run_purchase_flow():
    """Execute the complete PureBrain purchase flow"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("PureBrain.ai Purchase Flow Test - V2")
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
            # Use 'load' instead of 'networkidle' for faster loading
            await page.goto(SITE_URL, wait_until="load", timeout=90000)
            await asyncio.sleep(5)  # Wait for dynamic content
            results["screenshots"].append(await take_screenshot(page, "01_homepage"))

            # STEP 2: Click the "Awaken Your PURE BRAIN" button
            print("\nSTEP 2: Click 'Awaken Your PURE BRAIN' button")
            print("-" * 40)

            awaken_selectors = [
                "text=Awaken Your PURE BRAIN",
                "button:has-text('Awaken')",
                "a:has-text('Awaken')",
                ".cta-button",
                "[class*='awaken']",
            ]

            clicked = False
            for selector in awaken_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=3000):
                        await element.click()
                        print(f"  Clicked: {selector}")
                        clicked = True
                        await asyncio.sleep(3)
                        results["screenshots"].append(await take_screenshot(page, "02_after_awaken_click"))
                        break
                except Exception as e:
                    continue

            if not clicked:
                print("  WARNING: Could not find Awaken button")
                results["screenshots"].append(await take_screenshot(page, "02_no_awaken_button"))

            # STEP 3: Scroll to "BEGIN YOUR AWAKENING" section
            print("\nSTEP 3: Scroll to chat section (BEGIN YOUR AWAKENING)")
            print("-" * 40)

            # Scroll down to find the chat section
            for scroll_pos in range(0, 8000, 400):
                await page.evaluate(f"window.scrollTo(0, {scroll_pos})")
                await asyncio.sleep(0.3)

                # Check for chat-related elements
                chat_indicators = [
                    "text=BEGIN YOUR AWAKENING",
                    "text=Begin Your Awakening",
                    "text=Begin Awakening",
                    "[placeholder*='message']",
                    "[placeholder*='type']",
                    "textarea",
                    ".chat-input",
                    "#chat",
                    "[class*='chat']",
                ]

                for indicator in chat_indicators:
                    try:
                        element = page.locator(indicator).first
                        if await element.is_visible(timeout=500):
                            print(f"  Found chat section: {indicator} at scroll={scroll_pos}")
                            results["screenshots"].append(await take_screenshot(page, f"03_chat_section_found"))
                            break
                    except:
                        continue
                else:
                    continue
                break

            # Take screenshot at current position
            results["screenshots"].append(await take_screenshot(page, "03_scrolled_to_chat"))

            # STEP 4: Find and interact with chat
            print("\nSTEP 4: Chat interaction")
            print("-" * 40)

            # Try various chat input selectors
            chat_selectors = [
                "textarea",
                "input[type='text']",
                "[placeholder*='message']",
                "[placeholder*='type']",
                "[placeholder*='say']",
                "[placeholder*='ask']",
                ".chat-input input",
                ".chat-input textarea",
                "[contenteditable='true']",
                "#message-input",
                "[aria-label*='message']",
            ]

            chat_found = False
            for selector in chat_selectors:
                try:
                    chat_input = page.locator(selector).first
                    if await chat_input.is_visible(timeout=2000):
                        # Click first to focus
                        await chat_input.click()
                        await asyncio.sleep(0.5)

                        # Type message
                        await chat_input.fill("Hello! I'm interested in AI solutions for my business.")
                        print(f"  Found chat input: {selector}")
                        chat_found = True
                        results["screenshots"].append(await take_screenshot(page, "04_message_typed"))

                        # Submit
                        await page.keyboard.press("Enter")
                        print("  Sent first message")
                        await asyncio.sleep(8)  # Wait for AI response
                        results["screenshots"].append(await take_screenshot(page, "05_first_response"))

                        # Second message
                        await chat_input.fill("What can you help me with?")
                        await page.keyboard.press("Enter")
                        await asyncio.sleep(8)
                        results["screenshots"].append(await take_screenshot(page, "06_second_response"))
                        break
                except Exception as e:
                    continue

            if not chat_found:
                print("  WARNING: Could not find chat input")
                # Print page content for debugging
                content = await get_page_html(page)
                print(f"  Page content snippet: {content[:500]}...")
                results["screenshots"].append(await take_screenshot(page, "04_no_chat_input"))

            # STEP 5: Name the AI
            print("\nSTEP 5: Name the AI")
            print("-" * 40)

            # Send message about naming
            if chat_found:
                try:
                    chat_input = page.locator("textarea, input[type='text']").first
                    await chat_input.fill(f"I'll name my AI: {AI_NAME}")
                    await page.keyboard.press("Enter")
                    print(f"  Sent naming message: {AI_NAME}")
                    await asyncio.sleep(8)
                    results["screenshots"].append(await take_screenshot(page, "07_ai_named"))
                except Exception as e:
                    print(f"  Error naming: {e}")

            # Also look for a dedicated name input
            name_selectors = [
                "input[placeholder*='name']",
                "input[placeholder*='Name']",
                "[aria-label*='name']",
                "#ai-name",
                ".name-input",
            ]

            for selector in name_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        await element.fill(AI_NAME)
                        await page.keyboard.press("Enter")
                        print(f"  Named AI in dedicated field: {selector}")
                        await asyncio.sleep(3)
                        results["screenshots"].append(await take_screenshot(page, "07_ai_named_field"))
                        break
                except:
                    continue

            # STEP 6: Scroll down to find pricing section
            print("\nSTEP 6: Find pricing section (scroll down)")
            print("-" * 40)

            # Take a full page screenshot first to see everything
            full_page = OUTPUT_DIR / "FULLPAGE_before_pricing.png"
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(0.5)
            await page.screenshot(path=str(full_page), full_page=True)
            print(f"  Full page screenshot: {full_page}")

            # Scroll down to find pricing
            pricing_found = False
            for scroll_pos in range(0, 12000, 400):
                await page.evaluate(f"window.scrollTo(0, {scroll_pos})")
                await asyncio.sleep(0.3)

                pricing_indicators = [
                    "text=BRING",
                    f"text=BRING {AI_NAME.upper()} FULLY ONLINE",
                    "text=FULLY ONLINE",
                    "text=$79",
                    "text=$149",
                    "text=$499",
                    "text=/month",
                    "text=Get Started",
                    "text=Activate",
                    ".pricing",
                    "#pricing",
                    "[class*='pricing']",
                    "[class*='tier']",
                ]

                for indicator in pricing_indicators:
                    try:
                        element = page.locator(indicator).first
                        if await element.is_visible(timeout=300):
                            print(f"  Found pricing: {indicator} at scroll={scroll_pos}")
                            pricing_found = True
                            results["screenshots"].append(await take_screenshot(page, f"08_pricing_found"))
                            break
                    except:
                        continue

                if pricing_found:
                    break

            if not pricing_found:
                print("  WARNING: Could not find pricing section")
                results["screenshots"].append(await take_screenshot(page, "08_no_pricing"))

            # STEP 7: Click on pricing tier
            print("\nSTEP 7: Click pricing tier")
            print("-" * 40)

            tier_selectors = [
                "text=Get Started",
                f"text=Activate {AI_NAME} Now",
                f"text=Activate {AI_NAME}",
                "text=Activate Now",
                "text=Activate",
                "text=Select Plan",
                "text=Choose Plan",
                "button:has-text('Get Started')",
                "a:has-text('Get Started')",
                "button:has-text('Activate')",
                ".pricing-card button",
                "[data-tier]",
            ]

            tier_clicked = False
            for selector in tier_selectors:
                try:
                    buttons = page.locator(selector)
                    count = await buttons.count()
                    if count > 0:
                        await buttons.first.click()
                        print(f"  Clicked tier: {selector}")
                        results["tier_clicked"] = f"First match of: {selector}"
                        tier_clicked = True
                        await asyncio.sleep(3)
                        results["screenshots"].append(await take_screenshot(page, "09_tier_clicked"))
                        break
                except Exception as e:
                    continue

            if not tier_clicked:
                print("  WARNING: Could not find tier buttons")
                results["tier_clicked"] = "NOT FOUND"
                results["screenshots"].append(await take_screenshot(page, "09_no_tier"))

            # STEP 8: Fill in the form
            print("\nSTEP 8: Look for and fill form")
            print("-" * 40)

            await asyncio.sleep(2)

            form_fields = {
                "name": ["input[name*='name']", "input[placeholder*='name']", "#name", "input[id*='name']", "input[placeholder*='Your name']"],
                "email": ["input[type='email']", "input[name*='email']", "input[placeholder*='email']", "#email", "input[placeholder*='Email']"],
                "company": ["input[name*='company']", "input[placeholder*='company']", "#company", "input[name*='organization']", "input[placeholder*='Company']"],
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
                results["screenshots"].append(await take_screenshot(page, "10_form_filled"))
                results["form_result"] = f"Filled: {list(form_filled.keys())}"

                # Try to submit
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "text=Submit",
                    "text=Continue",
                    "text=Next",
                    "text=Proceed to Payment",
                    "text=Pay",
                    "button:has-text('Submit')",
                ]

                for selector in submit_selectors:
                    try:
                        element = page.locator(selector).first
                        if await element.is_visible(timeout=2000):
                            await element.click()
                            print(f"  Submitted form: {selector}")
                            await asyncio.sleep(5)
                            results["screenshots"].append(await take_screenshot(page, "11_form_submitted"))
                            results["form_result"] = "SUBMITTED"
                            break
                    except:
                        continue
            else:
                print("  WARNING: No form fields found")
                results["form_result"] = "NO FORM FOUND"

            # STEP 9: Check for PayPal/payment button
            print("\nSTEP 9: Check for PayPal/payment")
            print("-" * 40)

            await asyncio.sleep(2)

            paypal_indicators = [
                "text=PayPal",
                "text=paypal",
                "[class*='paypal']",
                "iframe[src*='paypal']",
                "button:has-text('PayPal')",
                "img[alt*='PayPal']",
                "text=Pay with PayPal",
                "text=Checkout",
                "text=payment",
            ]

            paypal_found = False
            for selector in paypal_indicators:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        print(f"  Found PayPal/payment: {selector}")
                        paypal_found = True
                        results["final_outcome"] = f"PAYPAL/PAYMENT FOUND: {selector}"
                        break
                except:
                    continue

            if not paypal_found:
                # Check for any confirmation
                confirmation = [
                    "text=Thank you",
                    "text=Confirmation",
                    "text=Success",
                    "text=Complete",
                    "text=order",
                ]
                for selector in confirmation:
                    try:
                        element = page.locator(selector).first
                        if await element.is_visible(timeout=1000):
                            print(f"  Found confirmation: {selector}")
                            results["final_outcome"] = f"CONFIRMATION: {selector}"
                            break
                    except:
                        continue

            if not results["final_outcome"]:
                results["final_outcome"] = "UNKNOWN - CHECK SCREENSHOTS"

            results["screenshots"].append(await take_screenshot(page, "12_final_state"))

            # Final full page screenshot
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(0.5)
            final_full = OUTPUT_DIR / "FULLPAGE_final.png"
            await page.screenshot(path=str(final_full), full_page=True)
            print(f"\n  Final full page: {final_full}")

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
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
