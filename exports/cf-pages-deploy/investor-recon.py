#!/usr/bin/env python3
"""Recon script - dump page structure at each stage."""

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/tmp/investor-stress-test"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # Capture all console
        page.on("console", lambda msg: print(f"  CONSOLE [{msg.type}]: {msg.text[:200]}"))

        print("=== STEP 1: Navigate ===")
        await page.goto("https://purebrain.ai/investment-opportunity/", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        # Dump landing page structure
        html = await page.content()
        with open(f"{SCREENSHOT_DIR}/recon_landing.html", "w") as f:
            f.write(html)
        print(f"  Landing HTML saved ({len(html)} chars)")

        # Find all inputs and buttons
        elements = await page.evaluate("""() => {
            const result = {inputs: [], buttons: [], textareas: []};
            document.querySelectorAll('input').forEach(el => {
                result.inputs.push({
                    tag: 'input', type: el.type, id: el.id, name: el.name,
                    placeholder: el.placeholder, className: el.className,
                    visible: el.offsetParent !== null
                });
            });
            document.querySelectorAll('button').forEach(el => {
                result.buttons.push({
                    tag: 'button', text: el.textContent.trim().substring(0, 50),
                    id: el.id, className: el.className,
                    visible: el.offsetParent !== null
                });
            });
            document.querySelectorAll('textarea').forEach(el => {
                result.textareas.push({
                    tag: 'textarea', id: el.id, placeholder: el.placeholder,
                    className: el.className, visible: el.offsetParent !== null
                });
            });
            return result;
        }""")
        print(f"  Inputs: {elements['inputs']}")
        print(f"  Buttons: {elements['buttons']}")
        print(f"  Textareas: {elements['textareas']}")

        print("\n=== STEP 2: Enter code JOHNSON2026 ===")
        # Fill the access code
        input_el = await page.query_selector("input[type='password']")
        if not input_el:
            input_el = await page.query_selector("input[type='text']")
        if not input_el:
            input_el = await page.query_selector("input")

        if input_el:
            await input_el.fill("JOHNSON2026")
            print("  Code filled")
        else:
            print("  ERROR: No input found!")

        # Click the Enter button
        enter_btn = await page.query_selector("button")
        if enter_btn:
            text = await enter_btn.text_content()
            print(f"  Clicking button: '{text.strip()}'")
            await enter_btn.click()
        else:
            print("  ERROR: No button found!")

        await asyncio.sleep(5)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/recon_after_enter.png")
        print("  Screenshot after enter saved")

        # Check for page changes / new elements
        new_url = page.url
        print(f"  URL after enter: {new_url}")

        elements2 = await page.evaluate("""() => {
            const result = {inputs: [], buttons: [], textareas: [], divs_with_class: []};
            document.querySelectorAll('input').forEach(el => {
                result.inputs.push({
                    type: el.type, id: el.id, placeholder: el.placeholder,
                    className: el.className, visible: el.offsetParent !== null
                });
            });
            document.querySelectorAll('button').forEach(el => {
                result.buttons.push({
                    text: el.textContent.trim().substring(0, 80),
                    id: el.id, className: el.className,
                    visible: el.offsetParent !== null, type: el.type
                });
            });
            document.querySelectorAll('textarea').forEach(el => {
                result.textareas.push({
                    id: el.id, placeholder: el.placeholder,
                    className: el.className, visible: el.offsetParent !== null
                });
            });
            // Look for chat-like containers
            document.querySelectorAll('[class*="chat"], [class*="message"], [class*="question"], [class*="hot"], [class*="avatar"], [id*="chat"], [id*="message"]').forEach(el => {
                result.divs_with_class.push({
                    tag: el.tagName, id: el.id, className: el.className.substring(0, 100)
                });
            });
            return result;
        }""")
        print(f"\n  After-enter elements:")
        print(f"  Inputs: {elements2['inputs']}")
        print(f"  Buttons: {elements2['buttons']}")
        print(f"  Textareas: {elements2['textareas']}")
        print(f"  Chat/Message divs: {elements2['divs_with_class']}")

        # Look for any visible text on the page that might indicate a gate/layer
        visible_text = await page.evaluate("""() => {
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            const texts = [];
            let node;
            while (node = walker.nextNode()) {
                const t = node.textContent.trim();
                if (t.length > 10 && t.length < 200 && node.parentElement.offsetParent !== null) {
                    texts.push(t);
                }
            }
            return texts.slice(0, 30);
        }""")
        print(f"\n  Visible text snippets: {visible_text}")

        # Check if there are multiple layers/sections
        sections = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('section, [class*="layer"], [class*="gate"], [class*="screen"], [class*="page"], [class*="step"], [class*="panel"]')).map(el => ({
                tag: el.tagName, id: el.id, className: el.className.substring(0, 100),
                visible: el.offsetParent !== null,
                display: getComputedStyle(el).display,
                opacity: getComputedStyle(el).opacity
            }));
        }""")
        print(f"\n  Sections/layers: {sections}")

        html2 = await page.content()
        with open(f"{SCREENSHOT_DIR}/recon_after_enter.html", "w") as f:
            f.write(html2)
        print(f"\n  After-enter HTML saved ({len(html2)} chars)")

        await browser.close()
        print("\n=== RECON COMPLETE ===")

asyncio.run(main())
