#!/usr/bin/env python3
"""
Test script: purebrain.ai/training/ password gate
Tests: initial state, password entry, button click, gate disappear, video library appear
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/tools/screenshots/training-gate-test")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

async def test_training_gate():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # Capture console logs
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: console_msgs.append(f"[pageerror] {err}"))

        print("Navigating to https://purebrain.ai/training/...")
        await page.goto("https://purebrain.ai/training/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)

        # Step 1: Screenshot of initial gate
        shot1 = str(SCREENSHOT_DIR / "01-initial-gate.png")
        await page.screenshot(path=shot1, full_page=False)
        print(f"Screenshot 1 saved: {shot1}")

        # Check initial DOM state
        gate_visible = await page.is_visible("#training-gate", timeout=3000).catch_to_none() if hasattr(page, 'catch_to_none') else None
        try:
            gate_visible = await page.is_visible("#training-gate")
        except Exception:
            gate_visible = "selector not found"

        print(f"Gate #training-gate visible: {gate_visible}")

        # Check if window.handleGateSubmit is defined BEFORE interaction
        handle_gate_before = await page.evaluate("typeof window.handleGateSubmit")
        print(f"window.handleGateSubmit (before) = typeof: {handle_gate_before}")

        # Find the password input
        pw_input_count = await page.locator("input[type='password']").count()
        pw_text_count = await page.locator("input[type='text']").count()
        all_inputs = await page.locator("input").count()
        print(f"Password inputs: {pw_input_count}, Text inputs: {pw_text_count}, All inputs: {all_inputs}")

        # Step 2: Type the password
        print("Typing password: brainiac2026")
        # Try password input first, then text input, then any input
        typed = False
        for selector in ["input[type='password']", "input[type='text']", "#gate-password", ".gate-password", "input"]:
            try:
                count = await page.locator(selector).count()
                if count > 0:
                    await page.locator(selector).first.click()
                    await page.locator(selector).first.fill("brainiac2026")
                    print(f"  Typed into selector: {selector}")
                    typed = True
                    break
            except Exception as e:
                print(f"  Failed selector {selector}: {e}")

        if not typed:
            print("WARNING: Could not find any input field to type into")

        await page.wait_for_timeout(500)

        # Screenshot after typing
        shot2 = str(SCREENSHOT_DIR / "02-after-typing-password.png")
        await page.screenshot(path=shot2, full_page=False)
        print(f"Screenshot 2 saved: {shot2}")

        # Step 3: Click "Access Training Library" button
        print("Clicking Access Training Library button...")
        button_found = False
        for selector in [
            "button:has-text('Access Training Library')",
            "input[value='Access Training Library']",
            "button:has-text('Access')",
            ".gate-submit",
            "#gate-submit",
            "button[type='submit']",
            "input[type='submit']",
        ]:
            try:
                count = await page.locator(selector).count()
                if count > 0:
                    print(f"  Found button with selector: {selector}")
                    await page.locator(selector).first.click()
                    button_found = True
                    break
            except Exception as e:
                print(f"  Button selector {selector} failed: {e}")

        if not button_found:
            # Try JS click on handleGateSubmit
            print("  Trying direct JS call to handleGateSubmit...")
            try:
                await page.evaluate("window.handleGateSubmit && window.handleGateSubmit()")
            except Exception as e:
                print(f"  JS call failed: {e}")

        await page.wait_for_timeout(1500)

        # Step 4: Screenshot after button click
        shot3 = str(SCREENSHOT_DIR / "03-after-button-click.png")
        await page.screenshot(path=shot3, full_page=False)
        print(f"Screenshot 3 saved: {shot3}")

        # Step 5: Check if gate disappeared and video library appeared
        print("\n--- POST-CLICK STATE ANALYSIS ---")

        # Check window.handleGateSubmit after interaction
        handle_gate_after = await page.evaluate("typeof window.handleGateSubmit")
        print(f"window.handleGateSubmit (after) = typeof: {handle_gate_after}")

        # Check gate visibility
        try:
            gate_visible_after = await page.is_visible("#training-gate")
        except Exception:
            gate_visible_after = "selector not found"
        print(f"Gate visible after click: {gate_visible_after}")

        # Check if video library / content appeared
        page_html = await page.content()
        has_video = "video" in page_html.lower() or "iframe" in page_html.lower() or "youtube" in page_html.lower() or "vimeo" in page_html.lower()
        print(f"Video content detected in DOM: {has_video}")

        # Check for specific training library elements
        training_visible = False
        for sel in ["#training-library", ".training-library", ".video-library", ".training-content", ".videos-grid"]:
            try:
                c = await page.locator(sel).count()
                if c > 0:
                    print(f"  Training library element found: {sel} (count={c})")
                    training_visible = True
            except Exception:
                pass

        # Full page screenshot to see complete state
        shot4 = str(SCREENSHOT_DIR / "04-full-page-state.png")
        await page.screenshot(path=shot4, full_page=True)
        print(f"Screenshot 4 (full page) saved: {shot4}")

        # Console log summary
        print("\n--- CONSOLE LOGS ---")
        for msg in console_msgs[-20:]:
            print(f"  {msg}")

        # Final verdict
        print("\n--- VERDICT ---")
        if handle_gate_after == "function":
            print("window.handleGateSubmit IS defined as a function - IIFE scope fix WORKED")
        else:
            print(f"window.handleGateSubmit = {handle_gate_after} - still not accessible globally")

        await browser.close()

        return {
            "handle_gate_before": handle_gate_before,
            "handle_gate_after": handle_gate_after,
            "gate_visible_after": gate_visible_after,
            "has_video": has_video,
            "training_visible": training_visible,
            "screenshots": [shot1, shot2, shot3, shot4],
            "console_msgs": console_msgs,
        }

if __name__ == "__main__":
    result = asyncio.run(test_training_gate())
    print("\n=== FINAL RESULT ===")
    print(result)
