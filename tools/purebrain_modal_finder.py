#!/usr/bin/env python3
"""
PureBrain Modal/Form Finder
Specifically targets forms and modals to identify orange text issues
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

SCREENSHOT_DIR = "/tmp"

async def save_screenshot(page, label):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"purebrain-modal-{timestamp}-{label}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    await page.screenshot(path=filepath, full_page=False)
    print(f"Saved: {filepath}")
    return filepath

async def find_modals_and_forms():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(60000)

        print("=" * 60)
        print("PUREBRAIN MODAL AND FORM FINDER")
        print("=" * 60)

        await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        screenshots = []

        # Scroll to the "BEGIN YOUR AWAKENING" section where the form appears
        print("\n[1] Looking for the Begin Your Awakening form...")

        # First, scroll to find the form
        await page.evaluate("window.scrollTo(0, 2800)")
        await asyncio.sleep(2)
        screenshots.append(await save_screenshot(page, "01-awakening-form-area"))

        # Look for a form element
        forms = await page.locator("form").all()
        print(f"  Found {len(forms)} forms on page")

        for i, form in enumerate(forms):
            try:
                box = await form.bounding_box()
                if box:
                    print(f"  Form {i+1}: at y={box['y']}, height={box['height']}")
                    await form.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    screenshots.append(await save_screenshot(page, f"02-form-{i+1}"))
            except Exception as e:
                print(f"  Form {i+1} error: {e}")

        # Look for inputs with labels
        print("\n[2] Looking for form input labels...")
        inputs = await page.locator("input, textarea").all()
        print(f"  Found {len(inputs)} input fields")

        for i, inp in enumerate(inputs):
            try:
                # Get placeholder or label
                placeholder = await inp.get_attribute("placeholder")
                name = await inp.get_attribute("name")
                itype = await inp.get_attribute("type")
                print(f"  Input {i+1}: type={itype}, name={name}, placeholder={placeholder}")
            except Exception as e:
                print(f"  Input {i+1} error: {e}")

        # Look for labels
        labels = await page.locator("label").all()
        print(f"\n  Found {len(labels)} labels")
        for i, label in enumerate(labels):
            try:
                text = await label.inner_text()
                if text.strip():
                    print(f"  Label {i+1}: '{text.strip()}'")
            except:
                pass

        # Try clicking on buttons that might open modals
        print("\n[3] Looking for modal triggers...")

        # Look for "Awaken Your PURE BRAIN" button
        awaken_btns = await page.locator("text=Awaken").all()
        print(f"  Found {len(awaken_btns)} 'Awaken' buttons")

        for i, btn in enumerate(awaken_btns[:3]):
            try:
                txt = await btn.inner_text()
                print(f"  Button {i+1}: '{txt}'")
                if await btn.is_visible():
                    # Click and wait
                    await btn.click()
                    await asyncio.sleep(2)
                    screenshots.append(await save_screenshot(page, f"03-after-awaken-click-{i+1}"))

                    # Check if a modal appeared
                    modal = page.locator("[class*='modal'], [class*='popup'], [role='dialog'], .elementor-popup-modal")
                    if await modal.count() > 0:
                        print(f"  Modal appeared!")
                        screenshots.append(await save_screenshot(page, f"04-modal-{i+1}"))

                    # Press escape to close any modal
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"  Button {i+1} error: {e}")

        # Look for "Begin Awakening" button
        print("\n[4] Looking for 'Begin Awakening' button...")
        begin_btns = await page.locator("text=Begin Awakening").all()
        print(f"  Found {len(begin_btns)} 'Begin Awakening' buttons")

        for i, btn in enumerate(begin_btns[:2]):
            try:
                if await btn.is_visible():
                    await btn.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    screenshots.append(await save_screenshot(page, f"05-begin-awakening-btn-{i+1}"))
                    await btn.click()
                    await asyncio.sleep(2)
                    screenshots.append(await save_screenshot(page, f"06-after-begin-click-{i+1}"))

                    # Press escape to close any modal
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"  Begin btn {i+1} error: {e}")

        # Look for "Get Started" or similar
        print("\n[5] Looking for other CTAs...")
        cta_texts = ["Get Started", "Join", "Start", "Contact", "Watch Demo"]

        for cta_text in cta_texts:
            try:
                btns = await page.locator(f"text={cta_text}").all()
                if len(btns) > 0:
                    print(f"  Found '{cta_text}' - {len(btns)} instances")
                    btn = btns[0]
                    if await btn.is_visible():
                        await btn.click()
                        await asyncio.sleep(2)
                        screenshots.append(await save_screenshot(page, f"07-after-{cta_text.replace(' ', '-').lower()}"))
                        await page.keyboard.press("Escape")
                        await asyncio.sleep(1)
            except Exception as e:
                print(f"  {cta_text} error: {e}")

        # Specifically look at the "BEGIN YOUR AWAKENING" form section
        print("\n[6] Scrolling to form section...")
        await page.evaluate("window.scrollTo(0, 2700)")
        await asyncio.sleep(2)
        screenshots.append(await save_screenshot(page, "08-form-section"))

        # Get all elements with orange color (computed style)
        print("\n[7] Analyzing orange colored elements...")
        orange_elements = await page.evaluate('''
            () => {
                const orangeRgb = 'rgb(241, 66, 11)';  // #f1420b
                const orangeRgbAlt = 'rgb(241, 66, 11)';
                const elements = [];

                document.querySelectorAll('*').forEach(el => {
                    const style = window.getComputedStyle(el);
                    const color = style.color;
                    const bgColor = style.backgroundColor;

                    if (color.includes('241') || bgColor.includes('241')) {
                        elements.push({
                            tag: el.tagName,
                            text: el.innerText?.substring(0, 50),
                            classes: el.className,
                            color: color,
                            bgColor: bgColor
                        });
                    }
                });

                return elements.slice(0, 30);
            }
        ''')

        print(f"  Found {len(orange_elements)} elements with orange styling")
        for el in orange_elements[:20]:
            if el['text'] and el['text'].strip():
                print(f"    {el['tag']}: '{el['text'][:30]}' color={el['color']}")

        print("\n" + "=" * 60)
        print("MODAL/FORM FINDER COMPLETE")
        print("=" * 60)
        for s in screenshots:
            print(f"  {s}")

        await browser.close()
        return screenshots

if __name__ == "__main__":
    asyncio.run(find_modals_and_forms())
