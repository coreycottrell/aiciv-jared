#!/usr/bin/env python3
"""
Set Yoast noindex properly by triggering React change events.
The key issue: Yoast v27 uses React, so we need to:
1. Select the option AND fire React's synthetic change event
2. OR use a React-compatible approach to set state

Approach: Use nativeInputValueSetter to trigger React synthetic events properly.
"""
import os, sys, time, re, base64, requests
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import datetime

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
WP_BASE_URL = 'https://purebrain.ai'
WP_ADMIN_URL = f'{WP_BASE_URL}/wp-admin'
WP_USER = 'Aether'
WP_PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '').strip("'\"")
WP_APP_PASSWORD = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '').strip("'\"")
SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/yoast-react')
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

DEV_PAGES = [
    (439, 'pay-test'),
    (468, 'pay-test-sandbox'),
    (150, 'elementor-150'),
    (311, 'paypal-buttons-embed'),
]


def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")


def ss(page, name):
    p = str(SCREENSHOT_DIR / f'{name}.png')
    try:
        page.screenshot(path=p, timeout=10000)
        log(f'  Screenshot: {p}')
    except Exception as e:
        log(f'  Screenshot failed: {e}')
    return p


def check_robots_live(slug):
    try:
        resp = requests.get(f'{WP_BASE_URL}/{slug}/', timeout=10)
        match = re.search(r'<meta name=["\']robots["\'] content=["\']([^"\']+)["\']', resp.text, re.I)
        return match.group(1) if match else 'NOT FOUND'
    except Exception as e:
        return f'Error: {e}'


def check_robots_api(page_id):
    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {encoded}"}
    try:
        resp = requests.get(
            f"{WP_BASE_URL}/wp-json/yoast/v1/get_head?url={WP_BASE_URL}/?p={page_id}",
            headers=headers, timeout=10
        )
        if resp.status_code == 200:
            head = resp.json().get("html", "")
            match = re.search(r'<meta name="robots" content="([^"]+)"', head)
            return match.group(1) if match else "NOT FOUND"
    except Exception:
        return "API Error"
    return "API Error"


def wp_login(page):
    page.goto(WP_ADMIN_URL, wait_until='domcontentloaded', timeout=60000)
    time.sleep(3)
    try:
        sso = page.locator('text=Log in with username and password')
        if sso.is_visible(timeout=3000):
            sso.click()
            time.sleep(2)
    except Exception:
        pass
    page.locator('#user_login').fill(WP_USER)
    page.locator('#user_pass').fill(WP_PASSWORD)
    page.locator('#wp-submit').click()
    page.wait_for_load_state('load', timeout=60000)
    time.sleep(4)
    return 'wp-admin' in page.url


def react_select_option(page, select_id, value):
    """
    Set a React-managed select to a specific value by triggering
    the native input setter (which React listens to via synthetic events).
    """
    result = page.evaluate(f"""
        (args) => {{
            const selectId = args.id;
            const targetValue = args.value;
            const sel = document.querySelector("#" + selectId);
            if (!sel) return {{error: "select not found: " + selectId}};

            // Get native setter
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLSelectElement.prototype, 'value'
            ).set;

            // Set value using native setter to trigger React synthetic event
            nativeInputValueSetter.call(sel, targetValue);

            // Dispatch change event
            const event = new Event('change', {{ bubbles: true }});
            sel.dispatchEvent(event);

            // Also dispatch input event
            const inputEvent = new Event('input', {{ bubbles: true }});
            sel.dispatchEvent(inputEvent);

            // Verify it changed
            return {{
                newValue: sel.value,
                selectedText: sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].text : "?"
            }};
        }}
    """, {"id": select_id, "value": value})
    return result


def set_noindex_for_page(page, page_id, slug):
    log(f'  Navigating to edit page {page_id}...')
    page.goto(f'{WP_ADMIN_URL}/post.php?post={page_id}&action=edit',
              wait_until='domcontentloaded', timeout=60000)
    time.sleep(5)

    # Open Yoast toolbar
    yoast_btn = page.locator('button[aria-label="Yoast SEO"]')
    if yoast_btn.count() > 0:
        sidebar = page.evaluate(
            'document.querySelector(".interface-complementary-area") ? '
            'document.querySelector(".interface-complementary-area").innerText : ""'
        )
        if "Advanced" not in sidebar or "Yoast SEO" not in sidebar:
            yoast_btn.first.click()
            time.sleep(2)

    # Expand Advanced section
    page.evaluate("""
        () => {
            const btns = document.querySelectorAll("button");
            for (const b of btns) {
                if ((b.innerText || "").trim() === "Advanced") {
                    b.scrollIntoView();
                    b.click();
                    return;
                }
            }
        }
    """)
    time.sleep(2)
    ss(page, f'{slug}_01_advanced')

    # Check current select value
    current = page.evaluate("""
        () => {
            const sel = document.querySelector("#yoast-meta-robots-noindex-sidebar");
            if (!sel) return "NOT FOUND";
            return {value: sel.value, text: sel.options[sel.selectedIndex]?.text};
        }
    """)
    log(f'  Current value: {current}')

    if isinstance(current, dict) and current.get('value') == '1':
        log('  Already set to noindex! Skipping.')
        return True

    if current == "NOT FOUND":
        log('  ERROR: Select not found')
        ss(page, f'{slug}_error')
        return False

    # Set via React-compatible method
    log('  Setting noindex via React synthetic event...')
    result = react_select_option(page, 'yoast-meta-robots-noindex-sidebar', '1')
    log(f'  React set result: {result}')
    time.sleep(1)
    ss(page, f'{slug}_02_noindex_set')

    # Wait for React to process the change
    time.sleep(2)

    # Verify it changed in the DOM
    after = page.evaluate("""
        () => {
            const sel = document.querySelector("#yoast-meta-robots-noindex-sidebar");
            if (!sel) return "NOT FOUND";
            return {value: sel.value, text: sel.options[sel.selectedIndex]?.text};
        }
    """)
    log(f'  After setting: {after}')

    return True


def save_page(page, slug):
    """Click Update/Save and wait for confirmation."""
    # First try the Update button
    save_btn = page.locator('button.editor-post-publish-button')
    if save_btn.is_visible(timeout=3000):
        save_btn.click()
        # Wait for save confirmation
        try:
            page.wait_for_selector('.components-snackbar:has-text("updated"), .editor-post-publish-panel__header-published, #message', timeout=15000)
            log('  Save confirmation received!')
        except Exception:
            time.sleep(5)
        ss(page, f'{slug}_saved')
        log('  Saved!')
        return True

    log('  WARNING: Save button not found')
    return False


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={'width': 1440, 'height': 900},
        device_scale_factor=2,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36'
    )
    page = ctx.new_page()
    page.set_default_timeout(30000)

    if not wp_login(page):
        log('Login failed!')
        sys.exit(1)
    log(f'Logged in: {page.url}')

    results = {}
    for page_id, slug in DEV_PAGES:
        log(f'\n=== /{slug}/ (ID={page_id}) ===')

        success = set_noindex_for_page(page, page_id, slug)
        if success:
            saved = save_page(page, slug)
            results[slug] = 'set+saved' if saved else 'set+save_failed'
        else:
            results[slug] = 'failed'

    log('\n=== SUMMARY ===')
    time.sleep(5)
    for pid, slug in DEV_PAGES:
        live = check_robots_live(slug)
        api = check_robots_api(pid)
        log(f'  /{slug}/:')
        log(f'    Result: {results.get(slug, "?")}')
        log(f'    Live: {live}')
        log(f'    API: {api}')

    browser.close()
