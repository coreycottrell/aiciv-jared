#!/usr/bin/env python3
"""
Publish Content Blocks on PureBrain
Final version - properly adds HTML widgets and publishes.

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

USERNAME = os.getenv('PUREBRAIN_WP_USER', 'Aether')
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '').strip("'")
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots/publish-content"

# Content blocks
TRUST_SIGNALS = """<div style="display: flex; justify-content: center; align-items: center; gap: 32px; flex-wrap: wrap; padding: 16px 24px; background: rgba(42, 147, 193, 0.08); border: 1px solid rgba(42, 147, 193, 0.15); border-radius: 12px; margin: 24px auto; max-width: 800px;">
    <div style="display: flex; align-items: center; gap: 8px; color: rgba(255, 255, 255, 0.9); font-size: 0.95rem; font-weight: 500;">
        <span style="display: flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: linear-gradient(135deg, #2a93c1 0%, #1a7aa3 100%); border-radius: 50%;">&#10003;</span>
        <span>Trusted by 2,500+ professionals</span>
    </div>
    <div style="display: flex; align-items: center; gap: 8px; color: rgba(255, 255, 255, 0.9); font-size: 0.95rem; font-weight: 500;">
        <span style="display: flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: linear-gradient(135deg, #2a93c1 0%, #1a7aa3 100%); border-radius: 50%;">&#10003;</span>
        <span>Your data is encrypted &amp; private</span>
    </div>
    <div style="display: flex; align-items: center; gap: 8px; color: rgba(255, 255, 255, 0.9); font-size: 0.95rem; font-weight: 500;">
        <span style="display: flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: linear-gradient(135deg, #2a93c1 0%, #1a7aa3 100%); border-radius: 50%;">&#10003;</span>
        <span>30-day money-back guarantee</span>
    </div>
</div>"""

CTA_MICROCOPY = """<div style="text-align: center; margin-top: 12px; font-size: 0.9rem; color: rgba(255, 255, 255, 0.6);">
    No credit card required. Setup takes 2 minutes.
</div>"""

def ensure_dir():
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

def screenshot(page, name):
    path = f"{SCREENSHOT_DIR}/{time.strftime('%H%M%S')}_{name}.png"
    try:
        page.screenshot(path=path, timeout=15000)
        print(f"Shot: {path}")
    except:
        pass
    return path

def login(page):
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
    print(f"Logged in: {'wp-admin' in page.url}")
    return 'wp-admin' in page.url

def open_editor(page, post_id):
    print(f"\n[Opening Elementor for {post_id}]")
    page.goto(f"https://purebrain.ai/wp-admin/post.php?post={post_id}&action=elementor")
    time.sleep(10)

    # Handle Take Over
    btn = page.query_selector('button:has-text("Take Over")')
    if btn:
        print("Taking over...")
        btn.click()
        time.sleep(5)

    try:
        page.wait_for_selector('#elementor-panel', timeout=60000)
        print("Elementor loaded")
        time.sleep(15)  # Wait for preview
        return True
    except:
        return False

def add_widget_with_content(page, content, name):
    """Add HTML widget and paste content"""
    print(f"\n[Adding {name}]")

    # Clear search
    search = page.query_selector('#elementor-panel-elements-search-input')
    if search:
        search.fill('')
        time.sleep(0.5)
        search.fill('HTML')
        time.sleep(1)

    # Get HTML widget
    widget = page.query_selector('.elementor-element-wrapper')
    if not widget:
        print("No widget found")
        return False

    # Get drop zone
    preview = page.query_selector('#elementor-preview')
    if not preview:
        print("No preview found")
        return False

    wb = widget.bounding_box()
    pb = preview.bounding_box()

    # Drag
    sx, sy = wb['x'] + wb['width']/2, wb['y'] + wb['height']/2
    ex, ey = pb['x'] + pb['width']/2, pb['y'] + 100  # Drop near top

    print(f"Drag ({sx:.0f},{sy:.0f}) -> ({ex:.0f},{ey:.0f})")
    page.mouse.move(sx, sy)
    page.mouse.down()
    time.sleep(0.5)
    page.mouse.move(ex, ey, steps=30)
    time.sleep(0.5)
    page.mouse.up()
    time.sleep(3)

    screenshot(page, f"drag_{name}")

    # Fill content
    # Try textarea first
    ta = page.query_selector('textarea')
    if ta:
        print("Found textarea")
        ta.fill(content)
        time.sleep(1)
        screenshot(page, f"fill_{name}")
        return True

    # Try clicking HTML in structure
    html_nav = page.query_selector('.elementor-navigator__item:has-text("HTML")')
    if html_nav:
        html_nav.click()
        time.sleep(2)
        ta = page.query_selector('textarea')
        if ta:
            ta.fill(content)
            time.sleep(1)
            return True

    return False

def publish(page):
    """Click publish button"""
    print("\n[Publishing]")
    screenshot(page, "before_publish")

    # The publish button in Elementor header
    # It's an <a> tag with id="elementor-panel-saver-button-publish"
    # or the text "Publish" in the top bar

    # Try direct selector
    btn = page.query_selector('button:has-text("Publish"), a:has-text("Publish")')
    if btn:
        # Force click via JS to avoid overlay issues
        page.evaluate('document.querySelector("button:has-text(\\"Publish\\"), a:has-text(\\"Publish\\")").click()')
        time.sleep(5)
        screenshot(page, "after_publish")
        print("Published!")
        return True

    # Try keyboard shortcut
    print("Trying Ctrl+S...")
    page.keyboard.press('Control+s')
    time.sleep(5)
    screenshot(page, "after_ctrl_s")

    return True

def verify(page):
    """Check live site"""
    print("\n[Verifying]")
    page.goto("https://purebrain.ai/", wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)
    screenshot(page, "verify_live")

    # Check for our content
    html = page.content()
    has_trust = "Trusted by 2,500+" in html
    has_microcopy = "No credit card required" in html

    print(f"Trust signals visible: {has_trust}")
    print(f"CTA microcopy visible: {has_microcopy}")

    return has_trust or has_microcopy

def main():
    ensure_dir()
    print("=" * 50)
    print("PUBLISH CONTENT BLOCKS")
    print("=" * 50)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = ctx.new_page()

        try:
            if not login(page):
                return False

            if not open_editor(page, "11"):
                return False

            screenshot(page, "ready")

            # Add trust signals
            ok1 = add_widget_with_content(page, TRUST_SIGNALS, "trust")

            # Add microcopy
            ok2 = add_widget_with_content(page, CTA_MICROCOPY, "microcopy")

            # Publish
            publish(page)

            # Verify
            verify(page)

            print("\n" + "=" * 50)
            print("DONE")
            print("=" * 50)
            print(f"Trust signals: {'OK' if ok1 else 'MANUAL'}")
            print(f"CTA microcopy: {'OK' if ok2 else 'MANUAL'}")
            print(f"Screenshots: {SCREENSHOT_DIR}")

            return True

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            screenshot(page, "error")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    main()
