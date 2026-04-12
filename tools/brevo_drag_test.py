#!/usr/bin/env python3
"""
Targeted drag test - understand exactly where the canvas drop zone is
and which drag method works for Brevo's builder.
"""

import os, time, json
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
SESSION_FILE = '/home/jared/projects/AI-CIV/aether/tools/brevo_session.json'
SS_DIR = '/home/jared/projects/AI-CIV/aether/exports/screenshots'

with open(SESSION_FILE) as f:
    session = json.load(f)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    ctx = browser.new_context(
        viewport={'width': 1600, 'height': 900},
        device_scale_factor=2,
        user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36',
        storage_state=session,
    )
    page = ctx.new_page()

    print("Loading builder...")
    page.goto('https://app.brevo.com/automation/edit/4', wait_until='domcontentloaded', timeout=30000)
    time.sleep(4)

    # ── Map all key elements and their coordinates ────────────────────
    print("\n=== ELEMENT MAP ===")

    # Find the trigger card
    cards = page.query_selector_all('[class*="DragableCard"]')
    print(f"DragableCards: {len(cards)}")

    trigger_card = None
    for c in cards:
        try:
            txt = c.evaluate('el => el.textContent').strip()
        except Exception:
            txt = ''
        box = c.bounding_box()
        if box and 'Contact added to list' in txt:
            trigger_card = c
            print(f"  TRIGGER: '{txt[:40]}' box={box}")
            break

    # Find the canvas / drop zone
    print("\nCanvases:")
    for sel in ['[class*="canvas"]', '[class*="Canvas"]', '[class*="drop"]', '[class*="Drop"]']:
        els = page.query_selector_all(sel)
        for el in els[:3]:
            box = el.bounding_box()
            cls = (el.get_attribute('class') or '')[:60]
            if box:
                print(f"  {sel}: box={box} cls={cls[:50]}")

    # Also find the drop hint text element
    print("\nDrop hint location:")
    try:
        hint = page.locator('text=Drop a step here').first
        box = hint.bounding_box()
        print(f"  Drop hint box: {box}")
    except Exception as e:
        print(f"  Drop hint: {e}")

    # Get viewport size
    vp = page.viewport_size
    print(f"\nViewport: {vp}")

    page.screenshot(path=f'{SS_DIR}/drag_test_01_initial.png', full_page=False)

    # ── Attempt drag with pointer events API ──────────────────────────
    if trigger_card:
        tb = trigger_card.bounding_box()
        src_x = tb['x'] + tb['width'] / 2
        src_y = tb['y'] + tb['height'] / 2

        # The canvas drop zone - the dashed rectangle in the screenshot
        # From screenshot: it appears at roughly 55% from left, 20% from top of viewport
        # In 1600x900: x ~ 875, y ~ 160
        # But the hint text says "Drop a step here" is visible - let's use that
        try:
            hint_box = page.locator('text=Drop a step here').first.bounding_box()
            if hint_box:
                dst_x = hint_box['x'] + hint_box['width'] / 2
                dst_y = hint_box['y'] + hint_box['height'] / 2
                print(f"\nUsing hint box center: ({dst_x:.0f}, {dst_y:.0f})")
            else:
                dst_x, dst_y = 900, 200
        except Exception:
            dst_x, dst_y = 900, 200

        print(f"Drag: ({src_x:.0f},{src_y:.0f}) → ({dst_x:.0f},{dst_y:.0f})")

        # Method: Use Playwright's built-in locator drag_to (uses Locator, not ElementHandle)
        print("\nTrying Locator.drag_to...")
        try:
            # Use locator-based drag (works with Locator not ElementHandle)
            trigger_locator = page.locator('[class*="DragableCard"]:has-text("Contact added to list")').first
            hint_locator = page.locator('text=Drop a step here').first

            trigger_locator.drag_to(hint_locator)
            time.sleep(3)
            page.screenshot(path=f'{SS_DIR}/drag_test_02_locator_drag.png', full_page=False)
            print("  Locator drag_to completed")
        except Exception as e:
            print(f"  Locator drag_to error: {e}")

        # Check result
        time.sleep(2)
        body = page.evaluate('() => document.body.innerText')
        still_empty = 'Drop a step here' in body
        print(f"  Canvas still empty: {still_empty}")

        if still_empty:
            # Try using mouse with pointer capture
            print("\nTrying mouse drag with pointer events...")
            try:
                page.mouse.move(src_x, src_y)
                time.sleep(0.5)
                page.mouse.down()
                time.sleep(0.8)  # Longer hold before dragging

                # Slow drag
                steps = 30
                for i in range(1, steps + 1):
                    t = i / steps
                    cx = src_x + (dst_x - src_x) * t
                    cy = src_y + (dst_y - src_y) * t
                    page.mouse.move(cx, cy)
                    time.sleep(0.06)

                time.sleep(0.8)
                page.mouse.up()
                time.sleep(3)
                page.screenshot(path=f'{SS_DIR}/drag_test_03_mouse_drag.png', full_page=False)
            except Exception as e:
                print(f"  Mouse drag error: {e}")

            body2 = page.evaluate('() => document.body.innerText')
            print(f"  Canvas still empty after mouse drag: {'Drop a step here' in body2}")

    # Print full page text to see current state
    print("\nFull page text:")
    print(page.evaluate('() => document.body.innerText')[:2000])

    browser.close()
    print("\nDone. Screenshots saved.")
