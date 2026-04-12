#!/usr/bin/env python3
"""
Verify CTA Button Arrow Fix
Takes screenshot of purebrain.ai and checks the arrow color
"""

import asyncio
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/sandbox/wp-screenshots"

async def verify_cta_arrow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Disable cache to see fresh CSS
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            bypass_csp=True
        )
        page = await context.new_page()
        page.set_default_timeout(90000)

        print("=" * 60)
        print("VERIFYING CTA BUTTON ARROW FIX")
        print("=" * 60)

        # Clear cache by going with cache disabled
        await page.route("**/*", lambda route: route.continue_())

        await page.goto("https://purebrain.ai?nocache=1", wait_until="domcontentloaded", timeout=90000)
        await asyncio.sleep(5)  # Wait for JS to render

        # Take screenshot
        screenshot_path = f"{SCREENSHOT_DIR}/verify_cta_arrow_AFTER_fix.png"
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"\nScreenshot saved to {screenshot_path}")

        # Check the computed fill color of .btn__icon
        arrow_info = await page.evaluate(r'''
            () => {
                const icon = document.querySelector('.btn__icon');
                if (!icon) return { error: 'No .btn__icon found' };

                const style = window.getComputedStyle(icon);
                const path = icon.querySelector('path');
                const pathStyle = path ? window.getComputedStyle(path) : null;

                return {
                    iconFill: style.fill,
                    iconStroke: style.stroke,
                    iconColor: style.color,
                    pathFill: pathStyle ? pathStyle.fill : 'N/A',
                    pathStroke: pathStyle ? pathStyle.stroke : 'N/A',
                    pathColor: pathStyle ? pathStyle.color : 'N/A'
                };
            }
        ''')

        print("\n--- ARROW COMPUTED STYLES ---")
        if 'error' in arrow_info:
            print(f"ERROR: {arrow_info['error']}")
        else:
            print(f"  .btn__icon fill: {arrow_info['iconFill']}")
            print(f"  .btn__icon stroke: {arrow_info['iconStroke']}")
            print(f"  .btn__icon color: {arrow_info['iconColor']}")
            print(f"  path fill: {arrow_info['pathFill']}")
            print(f"  path stroke: {arrow_info['pathStroke']}")
            print(f"  path color: {arrow_info['pathColor']}")

            # Check if white
            is_white = (
                'rgb(255, 255, 255)' in str(arrow_info['iconFill']) or
                'rgb(255, 255, 255)' in str(arrow_info['pathFill']) or
                'white' in str(arrow_info['iconFill']).lower()
            )

            print("\n" + "=" * 60)
            if is_white:
                print("SUCCESS: Arrow is now WHITE!")
            else:
                print("WARNING: Arrow may not be white yet")
                print("The fill value should be rgb(255, 255, 255)")
            print("=" * 60)

        await browser.close()

if __name__ == "__main__":
    import os
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    asyncio.run(verify_cta_arrow())
