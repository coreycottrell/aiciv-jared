#!/usr/bin/env python3
"""
Inject Content Blocks into PureBrain Elementor HTML Widgets
Uses the HTML editor panel to insert content directly.

Date: 2026-02-17
Author: browser-vision-tester agent
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

# Configuration
USERNAME = os.getenv('PUREBRAIN_WP_USER', 'Aether')
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '').strip("'")
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots/inject-content"

# Content blocks - minimal inline versions for highest compatibility
TRUST_SIGNALS_HTML = """<div style="display: flex; justify-content: center; align-items: center; gap: 32px; flex-wrap: wrap; padding: 16px 24px; background: rgba(42, 147, 193, 0.08); border: 1px solid rgba(42, 147, 193, 0.15); border-radius: 12px; margin: 24px auto; max-width: 800px;">
    <div style="display: flex; align-items: center; gap: 8px; color: rgba(255, 255, 255, 0.9); font-size: 0.95rem; font-weight: 500;">
        <span style="display: flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: linear-gradient(135deg, #2a93c1 0%, #1a7aa3 100%); border-radius: 50%;">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" style="width: 12px; height: 12px;">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
        </span>
        <span>Trusted by 2,500+ professionals</span>
    </div>
    <div style="display: flex; align-items: center; gap: 8px; color: rgba(255, 255, 255, 0.9); font-size: 0.95rem; font-weight: 500;">
        <span style="display: flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: linear-gradient(135deg, #2a93c1 0%, #1a7aa3 100%); border-radius: 50%;">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" style="width: 12px; height: 12px;">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
        </span>
        <span>Your data is encrypted &amp; private</span>
    </div>
    <div style="display: flex; align-items: center; gap: 8px; color: rgba(255, 255, 255, 0.9); font-size: 0.95rem; font-weight: 500;">
        <span style="display: flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: linear-gradient(135deg, #2a93c1 0%, #1a7aa3 100%); border-radius: 50%;">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" style="width: 12px; height: 12px;">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
        </span>
        <span>30-day money-back guarantee</span>
    </div>
</div>"""

CTA_MICROCOPY_HTML = """<div style="text-align: center; margin-top: 12px; font-size: 0.85rem; color: rgba(255, 255, 255, 0.6);">
    No credit card required. Setup takes 2 minutes.
</div>"""

def ensure_screenshot_dir():
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

def take_screenshot(page, name):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    try:
        page.screenshot(path=path, timeout=20000)
        print(f"Screenshot: {path}")
    except:
        pass
    return path

def wp_login(page):
    print("\n[Login]")
    page.goto("https://purebrain.ai/wp-admin", wait_until='load', timeout=60000)

    link = page.query_selector('text="Log in with username and password"')
    if link:
        link.click()
        time.sleep(2)

    page.wait_for_selector('#user_login', timeout=30000)
    page.fill('#user_login', USERNAME)
    page.fill('#user_pass', PASSWORD)
    page.click('#wp-submit')
    page.wait_for_load_state('load', timeout=60000)
    time.sleep(5)
    return 'wp-admin' in page.url

def open_elementor(page, post_id):
    print(f"\n[Opening Elementor for post {post_id}]")
    page.goto(f"https://purebrain.ai/wp-admin/post.php?post={post_id}&action=elementor")
    time.sleep(10)

    # Handle Take Over
    btn = page.query_selector('button:has-text("Take Over")')
    if btn:
        btn.click()
        time.sleep(5)

    try:
        page.wait_for_selector('#elementor-panel', timeout=60000)
        # Wait for preview to load
        time.sleep(10)
        return True
    except:
        return False

def add_html_widget_and_fill(page, html_content, widget_name):
    """Add HTML widget and fill with content"""
    print(f"\n[Adding {widget_name}]")

    # Search for HTML widget
    search = page.query_selector('#elementor-panel-elements-search-input')
    if search:
        search.fill('')
        time.sleep(0.3)
        search.fill('HTML')
        time.sleep(1)

    # Find HTML widget
    html_widget = page.query_selector('.elementor-element-wrapper')
    if not html_widget:
        print("HTML widget not found")
        return False

    widget_box = html_widget.bounding_box()
    if not widget_box:
        return False

    # Get preview iframe for drop target
    preview = page.query_selector('#elementor-preview')
    if not preview:
        return False

    preview_box = preview.bounding_box()

    # Drag to center of preview
    start_x = widget_box['x'] + widget_box['width'] / 2
    start_y = widget_box['y'] + widget_box['height'] / 2
    end_x = preview_box['x'] + preview_box['width'] / 2
    end_y = preview_box['y'] + preview_box['height'] / 2

    print(f"Dragging from ({start_x:.0f}, {start_y:.0f}) to ({end_x:.0f}, {end_y:.0f})")

    page.mouse.move(start_x, start_y)
    page.mouse.down()
    time.sleep(0.3)
    page.mouse.move(end_x, end_y, steps=20)
    time.sleep(0.3)
    page.mouse.up()
    time.sleep(2)

    take_screenshot(page, f"after_drag_{widget_name}")

    # Check if edit panel opened
    html_textarea = page.query_selector('textarea.elementor-control-tag-area, textarea[data-setting="html"]')
    if html_textarea:
        print("Found HTML textarea, filling content...")
        html_textarea.fill(html_content)
        time.sleep(1)
        take_screenshot(page, f"filled_{widget_name}")
        return True

    # Alternative: look for CodeMirror
    codemirror = page.query_selector('.CodeMirror')
    if codemirror:
        print("Found CodeMirror, using JS to set content...")
        page.evaluate(f'''() => {{
            const cm = document.querySelector('.CodeMirror').CodeMirror;
            cm.setValue({repr(html_content)});
        }}''')
        time.sleep(1)
        take_screenshot(page, f"filled_{widget_name}")
        return True

    # If edit panel didn't open, try clicking on the widget in structure
    html_in_structure = page.query_selector('.elementor-navigator__element__title:has-text("HTML")')
    if html_in_structure:
        print("Clicking HTML in structure panel...")
        html_in_structure.click()
        time.sleep(2)

        # Try again to find textarea
        html_textarea = page.query_selector('textarea')
        if html_textarea:
            html_textarea.fill(html_content)
            take_screenshot(page, f"filled_via_structure_{widget_name}")
            return True

    print("Could not fill HTML content")
    return False

def save_changes(page):
    """Click the publish/update button"""
    print("\n[Saving changes]")

    publish_btn = page.query_selector('#elementor-panel-saver-button-publish')
    if publish_btn:
        publish_btn.click()
        time.sleep(5)
        take_screenshot(page, "after_publish")
        return True

    # Try alternative
    update_btn = page.query_selector('button:has-text("Update")')
    if update_btn:
        update_btn.click()
        time.sleep(5)
        return True

    return False

def main():
    ensure_screenshot_dir()

    print("=" * 60)
    print("INJECT CONTENT BLOCKS INTO PUREBRAIN")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            if not wp_login(page):
                print("Login failed")
                return False

            if not open_elementor(page, "11"):
                print("Could not open Elementor")
                return False

            take_screenshot(page, "01_elementor_loaded")

            # Wait for preview to fully load
            print("Waiting for preview to load...")
            time.sleep(15)
            take_screenshot(page, "02_preview_loaded")

            # Add Trust Signals
            success1 = add_html_widget_and_fill(page, TRUST_SIGNALS_HTML, "trust_signals")

            # Clear search and add CTA Microcopy
            search = page.query_selector('#elementor-panel-elements-search-input')
            if search:
                search.fill('')
                time.sleep(0.5)

            success2 = add_html_widget_and_fill(page, CTA_MICROCOPY_HTML, "cta_microcopy")

            # Save changes
            if success1 or success2:
                save_changes(page)

            print("\n" + "=" * 60)
            print("RESULTS")
            print("=" * 60)
            print(f"Trust Signals: {'Added' if success1 else 'Manual required'}")
            print(f"CTA Microcopy: {'Added' if success2 else 'Manual required'}")
            print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")

            if not (success1 and success2):
                print("""
MANUAL STEPS:
1. Go to https://purebrain.ai/wp-admin/post.php?post=11&action=elementor
2. Click "Take Over" if prompted
3. Wait for page to fully load
4. Search "HTML" in widgets
5. Drag HTML widget to desired location
6. Paste content from exports/purebrain-content-blocks/
7. Click Publish
""")

            return True

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            take_screenshot(page, "error")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
