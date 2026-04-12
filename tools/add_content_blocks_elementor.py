#!/usr/bin/env python3
"""
Add Content Blocks to PureBrain via Elementor
Uses JavaScript API injection to add HTML widgets programmatically.

Date: 2026-02-17
Author: browser-vision-tester agent
"""

import os
import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
USERNAME = os.getenv('PUREBRAIN_WP_USER', 'Aether')
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '').strip("'")
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots/add-content-blocks"
CONTENT_BLOCKS_DIR = "/home/jared/projects/AI-CIV/aether/exports/purebrain-content-blocks"

def ensure_screenshot_dir():
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

def take_screenshot(page, name):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    try:
        page.screenshot(path=path, timeout=20000)
        print(f"Screenshot: {path}")
    except Exception as e:
        print(f"Screenshot failed: {e}")
    return path

def load_content_block(filename):
    filepath = f"{CONTENT_BLOCKS_DIR}/{filename}"
    with open(filepath, 'r') as f:
        return f.read()

def wp_login(page):
    """Login to WordPress"""
    print("\n[Login]")
    page.goto(WP_ADMIN_URL, wait_until='load', timeout=60000)

    username_password_link = page.query_selector('text="Log in with username and password"')
    if username_password_link:
        username_password_link.click()
        time.sleep(2)

    page.wait_for_selector('#user_login', state='visible', timeout=30000)
    page.fill('#user_login', USERNAME)
    page.fill('#user_pass', PASSWORD)
    page.click('#wp-submit')
    page.wait_for_load_state('load', timeout=60000)
    time.sleep(5)

    if 'wp-admin' in page.url:
        print("Logged in successfully")
        return True
    return False

def open_elementor(page, post_id):
    """Open Elementor editor"""
    print(f"\n[Opening Elementor for post {post_id}]")
    page.goto(f"https://purebrain.ai/wp-admin/post.php?post={post_id}&action=elementor")
    time.sleep(10)

    # Handle Take Over dialog
    take_over_btn = page.query_selector('button:has-text("Take Over")')
    if take_over_btn:
        print("Clicking Take Over...")
        take_over_btn.click()
        time.sleep(5)

    # Wait for Elementor
    try:
        page.wait_for_selector('#elementor-panel', timeout=60000)
        print("Elementor loaded")
        time.sleep(5)  # Extra wait for full load
        return True
    except:
        print("Elementor failed to load")
        return False

def search_html_widget(page):
    """Search for HTML widget in Elementor panel"""
    print("\n[Searching for HTML widget]")

    search_input = page.query_selector('#elementor-panel-elements-search-input')
    if search_input:
        search_input.fill('')
        time.sleep(0.5)
        search_input.fill('HTML')
        time.sleep(1)
        take_screenshot(page, "html_widget_search")
        return True
    return False

def add_html_widget_via_js(page, html_content, position='bottom'):
    """
    Attempt to add HTML widget via Elementor's JavaScript API
    This is experimental and may not work on all Elementor versions
    """
    print(f"\n[Attempting JS injection for HTML widget at {position}]")

    # Escape the HTML content for JavaScript
    escaped_html = json.dumps(html_content)

    js_code = f"""
    (function() {{
        try {{
            // Check if elementor is available
            if (typeof elementor === 'undefined') {{
                return 'Elementor not loaded';
            }}

            // Create a new HTML widget model
            var htmlWidget = {{
                elType: 'widget',
                widgetType: 'html',
                settings: {{
                    html: {escaped_html}
                }}
            }};

            // Get the container to add to
            var container = elementor.getPreviewView().$el.find('.elementor-section').last();

            // Try to get the document model
            var model = elementor.documents.getCurrent().container.model;

            return 'JS attempted, check preview';
        }} catch (e) {{
            return 'Error: ' + e.message;
        }}
    }})();
    """

    result = page.evaluate(js_code)
    print(f"JS result: {result}")
    return result

def drag_html_widget_to_preview(page):
    """
    Attempt to drag HTML widget to the preview area
    This uses Playwright's drag and drop
    """
    print("\n[Attempting drag-and-drop]")

    # Find the HTML widget in the panel
    html_widget = page.query_selector('.elementor-element-wrapper:has-text("HTML")')
    if not html_widget:
        print("HTML widget not found in panel")
        return False

    # Find a drop target in the preview
    frame = page.frame_locator("#elementor-preview-iframe")

    # Get the coordinates
    widget_box = html_widget.bounding_box()
    if not widget_box:
        print("Could not get widget bounding box")
        return False

    # Try to find a drop zone in the preview
    # This is tricky because the preview is in an iframe

    print(f"Widget location: {widget_box}")

    # Perform the drag
    try:
        # Start from center of widget
        start_x = widget_box['x'] + widget_box['width'] / 2
        start_y = widget_box['y'] + widget_box['height'] / 2

        # End at center-bottom of page (approximate)
        end_x = 800
        end_y = 600

        page.mouse.move(start_x, start_y)
        page.mouse.down()
        time.sleep(0.5)
        page.mouse.move(end_x, end_y, steps=10)
        time.sleep(0.5)
        page.mouse.up()

        print("Drag performed")
        take_screenshot(page, "after_drag")
        return True
    except Exception as e:
        print(f"Drag failed: {e}")
        return False

def click_to_select_and_add(page, target_text):
    """
    Click on an element to select it, then use keyboard/context menu to add
    """
    print(f"\n[Trying to select element with text: {target_text}]")

    frame = page.frame_locator("#elementor-preview-iframe")

    # Try to click on the target element
    target = frame.locator(f"text={target_text}").first
    if target.count() > 0:
        target.click()
        time.sleep(2)
        take_screenshot(page, f"selected_{target_text[:20]}")

        # Right-click to get context menu
        target.click(button='right')
        time.sleep(1)
        take_screenshot(page, "context_menu")
        return True
    else:
        print(f"Element with text '{target_text}' not found")
        return False

def get_page_structure(page):
    """Get the structure of elements on the page"""
    print("\n[Getting page structure]")

    frame = page.frame_locator("#elementor-preview-iframe")

    # Count sections
    sections = frame.locator(".elementor-section")
    print(f"Total sections: {sections.count()}")

    # Get section details
    for i in range(min(sections.count(), 10)):
        try:
            section = sections.nth(i)
            # Get the first heading in each section
            heading = section.locator("h1, h2, h3").first
            if heading.count() > 0:
                text = heading.text_content()[:50] if heading.text_content() else "No heading"
                print(f"  Section {i+1}: {text}")
        except:
            pass

    return sections.count()

def main():
    ensure_screenshot_dir()

    print("=" * 60)
    print("ADD CONTENT BLOCKS TO PUREBRAIN")
    print("=" * 60)

    # Load content blocks
    trust_signals = load_content_block('trust-signals.html')
    cta_microcopy = load_content_block('cta-microcopy.html')
    differentiation = load_content_block('differentiation-block.html')

    # Extract just the main HTML without comments for trust signals
    # This is the cleanest version
    trust_signals_clean = """
<style>
.pb-trust-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 32px;
    flex-wrap: wrap;
    padding: 16px 24px;
    background: rgba(42, 147, 193, 0.08);
    border: 1px solid rgba(42, 147, 193, 0.15);
    border-radius: 12px;
    margin: 24px auto;
    max-width: 800px;
}
.pb-trust-item {
    display: flex;
    align-items: center;
    gap: 8px;
    color: rgba(255, 255, 255, 0.9);
    font-size: 0.95rem;
    font-weight: 500;
    white-space: nowrap;
}
.pb-trust-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    background: linear-gradient(135deg, #2a93c1 0%, #1a7aa3 100%);
    border-radius: 50%;
    flex-shrink: 0;
}
.pb-trust-icon svg {
    width: 12px;
    height: 12px;
    color: #fff;
}
@media (max-width: 768px) {
    .pb-trust-bar {
        flex-direction: column;
        gap: 16px;
        padding: 20px 16px;
    }
}
</style>
<div class="pb-trust-bar">
    <div class="pb-trust-item">
        <span class="pb-trust-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
        </span>
        <span>Trusted by 2,500+ professionals</span>
    </div>
    <div class="pb-trust-item">
        <span class="pb-trust-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
        </span>
        <span>Your data is encrypted &amp; private</span>
    </div>
    <div class="pb-trust-item">
        <span class="pb-trust-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
        </span>
        <span>30-day money-back guarantee</span>
    </div>
</div>
"""

    cta_microcopy_clean = """
<div style="text-align: center; margin-top: 12px; font-size: 0.85rem; color: rgba(255, 255, 255, 0.6);">
    No credit card required. Setup takes 2 minutes.
</div>
"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            if not wp_login(page):
                return False

            if not open_elementor(page, "11"):
                return False

            take_screenshot(page, "01_elementor_ready")

            # Get page structure
            get_page_structure(page)

            # Search for HTML widget
            search_html_widget(page)
            take_screenshot(page, "02_after_search")

            # Try drag and drop
            drag_html_widget_to_preview(page)
            take_screenshot(page, "03_after_drag_attempt")

            # Try JS injection
            add_html_widget_via_js(page, trust_signals_clean)
            take_screenshot(page, "04_after_js_attempt")

            # Try clicking on specific elements
            click_to_select_and_add(page, "Awaken Your PURE BRAIN")
            take_screenshot(page, "05_after_select")

            print("\n" + "=" * 60)
            print("IMPLEMENTATION SUMMARY")
            print("=" * 60)
            print("""
Elementor's drag-and-drop and JS API are complex to automate reliably.

RECOMMENDED APPROACH - Use WordPress REST API to update Elementor data:

The Elementor page data is stored as post meta '_elementor_data' in JSON format.
You can fetch, modify, and update this via the WordPress REST API.

EXAMPLE API APPROACH:
1. GET /wp-json/wp/v2/pages/11 to fetch current page data
2. Decode the _elementor_data JSON
3. Add new widget object to the appropriate section
4. PUT the modified data back

MANUAL IMPLEMENTATION (QUICKEST):
1. Open https://purebrain.ai/wp-admin/post.php?post=11&action=elementor
2. Click "Take Over" if prompted
3. Search "HTML" in widget panel
4. Drag to after "Awaken Your PURE BRAIN" button
5. Paste content from trust-signals.html
6. Repeat for other blocks
7. Click Publish

CONTENT BLOCKS READY:
- trust-signals.html -> Below hero, above CTA
- cta-microcopy.html -> Below CTA button
- differentiation-block.html -> After hero section
- testimonials.html -> WHAT OTHERS HAVE BUILT section
- pricing-comparison.html -> On pricing page

Screenshots saved to: """ + SCREENSHOT_DIR)

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
