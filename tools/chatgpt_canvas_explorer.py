#!/usr/bin/env python3
"""
ChatGPT Canvas Feature Explorer

Uses Playwright to navigate ChatGPT and document the Canvas feature
for competitive analysis.
"""

import asyncio
import os
import time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Screenshot directory
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/docs/chatgpt-canvas-research")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

async def take_screenshot(page, name: str, description: str = ""):
    """Take a screenshot with timestamp and description."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{name}.png"
    filepath = SCREENSHOT_DIR / filename
    await page.screenshot(path=str(filepath), full_page=False)
    print(f"Screenshot saved: {filepath}")
    if description:
        # Save description alongside
        desc_file = SCREENSHOT_DIR / f"{timestamp}_{name}.txt"
        desc_file.write_text(description)
    return filepath

async def explore_canvas_headless():
    """Main exploration routine for ChatGPT Canvas - headless mode for CI/server environments."""
    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = await context.new_page()

        print("=" * 60)
        print("ChatGPT Canvas Feature Explorer (Headless Mode)")
        print("=" * 60)

        # Navigate to ChatGPT
        print("\n[1] Navigating to ChatGPT...")
        await page.goto("https://chatgpt.com", wait_until='networkidle')
        await asyncio.sleep(3)

        # Take initial screenshot
        await take_screenshot(page, "01_initial_load", "Initial ChatGPT load - login page expected")

        # Get page content for analysis
        content = await page.content()
        print(f"\n[2] Page loaded. Content length: {len(content)} chars")

        # Check what we see
        title = await page.title()
        print(f"Page title: {title}")

        # Look for key UI elements
        print("\n[3] Analyzing page structure...")

        # Look for login elements
        login_elements = await page.locator('[data-testid*="login"], [class*="login"], button:has-text("Log in")').all()
        print(f"  Login elements found: {len(login_elements)}")

        # Look for any interactive elements
        buttons = await page.locator('button').all()
        print(f"  Buttons found: {len(buttons)}")

        for i, btn in enumerate(buttons[:10]):
            try:
                text = await btn.text_content()
                if text and text.strip():
                    print(f"    Button {i}: {text.strip()[:50]}")
            except:
                pass

        await take_screenshot(page, "02_page_analysis", "Page structure analysis")

        await browser.close()
        print("\nHeadless exploration complete. Screenshots saved to:", SCREENSHOT_DIR)
        print("\nNOTE: Full Canvas exploration requires authenticated session.")
        print("For complete analysis, use WebFetch to research Canvas documentation.")

async def explore_canvas_headed():
    """Main exploration routine for ChatGPT Canvas - headed mode requiring display."""
    async with async_playwright() as p:
        # Launch browser with visible window for manual login
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            # Try to load saved state if exists
            storage_state="chatgpt_state.json" if os.path.exists("chatgpt_state.json") else None
        )

        page = await context.new_page()

        print("=" * 60)
        print("ChatGPT Canvas Feature Explorer")
        print("=" * 60)

        # Navigate to ChatGPT
        print("\n[1] Navigating to ChatGPT...")
        await page.goto("https://chatgpt.com")
        await asyncio.sleep(3)

        # Take initial screenshot
        await take_screenshot(page, "01_initial_load", "Initial ChatGPT load")

        print("\n[!] MANUAL STEP: Please log in if needed")
        print("    Press Enter when logged in and ready to continue...")
        input()

        # Save auth state for future runs
        await context.storage_state(path="chatgpt_state.json")
        print("Auth state saved for future runs")

        await take_screenshot(page, "02_logged_in", "ChatGPT after login")

        # Try to trigger Canvas with a code request
        print("\n[2] Attempting to trigger Canvas with code request...")

        # Find the chat input
        chat_input = page.locator('div[contenteditable="true"]').first
        if await chat_input.count() == 0:
            chat_input = page.locator('textarea').first

        # Type a code request that should trigger Canvas
        code_prompt = "Write a Python function to calculate fibonacci numbers with memoization"
        await chat_input.fill(code_prompt)
        await take_screenshot(page, "03_code_prompt_entered", f"Entered prompt: {code_prompt}")

        # Submit the prompt
        await page.keyboard.press("Enter")
        print("Prompt submitted, waiting for response...")

        # Wait for response
        await asyncio.sleep(15)  # Give time for Canvas to potentially appear
        await take_screenshot(page, "04_code_response", "Response to code prompt")

        # Check for Canvas elements
        print("\n[3] Checking for Canvas UI elements...")

        # Look for common Canvas selectors
        canvas_selectors = [
            '[data-testid="canvas"]',
            '[class*="canvas"]',
            '[class*="Canvas"]',
            'div[class*="code-block"]',
            'div[class*="editor"]',
        ]

        for selector in canvas_selectors:
            elements = await page.locator(selector).all()
            if elements:
                print(f"  Found {len(elements)} elements matching: {selector}")

        # Try another prompt - document creation
        print("\n[4] Trying document creation prompt...")

        # Start new chat
        new_chat_btn = page.locator('a[href="/"]').first
        if await new_chat_btn.count() > 0:
            await new_chat_btn.click()
            await asyncio.sleep(2)

        # Document prompt
        chat_input = page.locator('div[contenteditable="true"]').first
        if await chat_input.count() == 0:
            chat_input = page.locator('textarea').first

        doc_prompt = "Write a detailed project proposal document for a mobile app startup"
        await chat_input.fill(doc_prompt)
        await take_screenshot(page, "05_doc_prompt_entered", f"Entered prompt: {doc_prompt}")

        await page.keyboard.press("Enter")
        await asyncio.sleep(15)
        await take_screenshot(page, "06_doc_response", "Response to document prompt")

        # Look for edit/canvas buttons in the response
        print("\n[5] Looking for Canvas/Edit buttons...")

        edit_buttons = await page.locator('button').all()
        for i, btn in enumerate(edit_buttons[:20]):  # Check first 20 buttons
            text = await btn.text_content()
            if text:
                print(f"  Button {i}: {text[:50]}")

        # Try explicit Canvas trigger
        print("\n[6] Looking for explicit Canvas triggers...")

        # Check for any element containing "canvas" in class or text
        canvas_related = await page.locator('//*[contains(@class, "canvas") or contains(text(), "Canvas") or contains(text(), "canvas")]').all()
        print(f"  Found {len(canvas_related)} Canvas-related elements")

        await take_screenshot(page, "07_final_state", "Final page state before manual exploration")

        print("\n" + "=" * 60)
        print("MANUAL EXPLORATION MODE")
        print("=" * 60)
        print("""
The browser will stay open for manual exploration.
Try these prompts to trigger Canvas:
1. "Edit this code" on any code block
2. "Create a document about X"
3. Look for "Open in Canvas" or edit buttons

Screenshots are saved to:
""")
        print(f"  {SCREENSHOT_DIR}")
        print("""
Commands:
- Type 's' and Enter to take a screenshot
- Type 'q' and Enter to quit
        """)

        while True:
            cmd = input("> ").strip().lower()
            if cmd == 'q':
                break
            elif cmd == 's':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                desc = input("Description: ").strip()
                await take_screenshot(page, f"manual_{timestamp}", desc)
            else:
                print("Commands: 's' = screenshot, 'q' = quit")

        await browser.close()
        print("\nBrowser closed. Screenshots saved to:", SCREENSHOT_DIR)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--headed':
        # Requires X11/display
        asyncio.run(explore_canvas_headed())
    else:
        # Default to headless for CI/server environments
        asyncio.run(explore_canvas_headless())
