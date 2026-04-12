#!/usr/bin/env python3
"""
Set Yoast noindex via the Yoast SEO toolbar icon (full panel).
The Yoast Y icon in Gutenberg toolbar opens a full Yoast modal
with proper Advanced tab containing the robots index select.
"""
import os, time, re, base64, requests
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
WP_BASE_URL = 'https://purebrain.ai'
WP_ADMIN_URL = f'{WP_BASE_URL}/wp-admin'
WP_USER = 'Aether'
WP_PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '').strip("'\"")
WP_APP_PASSWORD = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '').strip("'\"")
SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/yoast-toolbar')
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
TS = 'run'

DEV_PAGES = [
    (439, 'pay-test'),
    (468, 'pay-test-sandbox'),
    (150, 'elementor-150'),
    (311, 'paypal-buttons-embed'),
]


def log(msg):
    import datetime
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")


def ss(page, name):
    p = str(SCREENSHOT_DIR / f'{name}.png')
    try:
        page.screenshot(path=p, timeout=10000)
        log(f'  Screenshot: {p}')
    except Exception as e:
        log(f'  Screenshot failed: {e}')
    return p


def check_robots_via_api(page_id):
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
    except Exception as e:
        return f"Error: {e}"
    return "API Error"


def dump_sidebar_content(page):
    """Dump all text + interactive elements from sidebar for debugging."""
    result = page.evaluate('''
        () => {
            const sidebar = document.querySelector(".interface-complementary-area");
            if (!sidebar) return {text: "NO SIDEBAR", elements: []};
            const els = Array.from(sidebar.querySelectorAll("button, select, input")).map(el => ({
                tag: el.tagName,
                id: el.id,
                type: el.getAttribute("type") || "",
                text: (el.innerText || el.value || "").slice(0, 50),
                cls: el.className.slice(0, 60),
                ariaLabel: el.getAttribute("aria-label") || "",
                ariaExpanded: el.getAttribute("aria-expanded") || ""
            }));
            return {text: sidebar.innerText.slice(0, 2000), elements: els};
        }
    ''')
    return result


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=2)
    page = ctx.new_page()
    page.set_default_timeout(30000)

    # Login
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
    log(f'Logged in: {page.url}')

    results = {}

    for page_id, slug in DEV_PAGES:
        log(f'\n=== Processing /{slug}/ (ID={page_id}) ===')

        current_robots = check_robots_via_api(page_id)
        log(f'  Current robots: {current_robots}')

        if 'noindex' in current_robots:
            log('  Already noindexed!')
            results[slug] = 'already_done'
            continue

        # Navigate to edit page
        page.goto(f'{WP_ADMIN_URL}/post.php?post={page_id}&action=edit',
                  wait_until='domcontentloaded', timeout=60000)
        time.sleep(5)
        ss(page, f'{slug}_01_loaded')

        # Strategy: Look for the Yoast icon button in the toolbar
        # It's usually a button with aria-label containing "Yoast" or showing "Y" letter
        log('  Looking for Yoast toolbar button...')

        yoast_toolbar_btn = None
        toolbar_btns = page.locator('.edit-post-header-toolbar button, .editor-header button, .interface-interface-skeleton__header button')
        log(f'  Header buttons count: {toolbar_btns.count()}')

        # Try by aria-label
        for label in ['Yoast SEO', 'Yoast', 'SEO']:
            btn = page.locator(f'button[aria-label*="{label}"]')
            if btn.count() > 0:
                log(f'  Found button with aria-label "{label}": {btn.count()} buttons')
                yoast_toolbar_btn = btn.first
                break

        # List all toolbar buttons for debugging
        all_header_btns = page.evaluate('''
            () => {
                const header = document.querySelector(".editor-header, .interface-interface-skeleton__header, .edit-post-header");
                if (!header) return [];
                return Array.from(header.querySelectorAll("button")).map(b => ({
                    text: (b.innerText || "").slice(0, 40),
                    ariaLabel: b.getAttribute("aria-label") || "",
                    id: b.id || "",
                    cls: b.className.slice(0, 60)
                }));
            }
        ''')
        log(f'  All header buttons: {all_header_btns}')

        # Also check the top bar area
        topbar_content = page.evaluate('''
            () => {
                const all = document.querySelectorAll(".edit-post-header *, .editor-header *");
                return Array.from(all).filter(el => el.tagName === "BUTTON").map(el => ({
                    text: (el.innerText || "").slice(0, 30),
                    ariaLabel: el.getAttribute("aria-label") || "",
                    title: el.getAttribute("title") || ""
                }));
            }
        ''')
        log(f'  Top bar buttons: {topbar_content[:10]}')

        # Look for the Yoast icon in the post editor tools
        # In the screenshot, it was a "Y" looking icon in the toolbar
        # It might be accessible via the Yoast module button

        # Try clicking the "Improve your post with Yoast SEO" button first (sidebar)
        # First expand Yoast SEO panel
        toggle = page.locator('.components-panel__body-toggle:has-text("Yoast SEO")')
        if toggle.count() > 0 and toggle.first.get_attribute('aria-expanded') != 'true':
            toggle.first.click()
            time.sleep(2)

        improve_btn = page.locator('button:has-text("Improve your post with Yoast SEO"), button.yst-button:has-text("Improve")')
        if improve_btn.is_visible(timeout=3000):
            log('  Found "Improve your post" button - clicking...')
            improve_btn.click()
            time.sleep(3)
            ss(page, f'{slug}_02_improve_clicked')

            # Check if a modal opened
            modal = page.locator('.yst-modal, [role="dialog"], .components-modal__frame')
            if modal.is_visible(timeout=3000):
                log('  Modal opened!')
                ss(page, f'{slug}_03_modal')

                # Look for Advanced tab in modal
                adv = modal.locator('button:has-text("Advanced"), a:has-text("Advanced")')
                if adv.is_visible(timeout=3000):
                    adv.click()
                    time.sleep(2)
                    ss(page, f'{slug}_04_modal_advanced')

                    # Look for robots select
                    robot_sel = modal.locator('select#wpseo-robots-index, select[id*="robots"]')
                    if robot_sel.is_visible(timeout=3000):
                        log('  Found robots select in modal!')
                        opts = page.evaluate('''() => {
                            const s = document.querySelector("select#wpseo-robots-index, select[id*='robots']");
                            return s ? Array.from(s.options).map(o => o.value + ":" + o.text) : [];
                        }''')
                        log(f'  Options: {opts}')
                        robot_sel.select_option(value='2')
                        log('  Selected noindex')

        # Try a different approach - open the Yoast SEO full screen by clicking the Y icon
        # The Y icon is visible in the top toolbar (from earlier screenshots)
        log('  Trying to find Yoast icon in top toolbar...')
        # From screenshot, the Y icon seems to be near the top right
        # Let's check all img/svg elements in the header
        header_imgs = page.evaluate('''
            () => {
                const header = document.querySelector(".editor-header, .interface-interface-skeleton__header");
                if (!header) return "no header";
                return header.innerHTML.slice(0, 3000);
            }
        ''')
        log(f'  Header HTML (first 1000): {header_imgs[:1000]}')

        ss(page, f'{slug}_diagnostic')
        results[slug] = 'needs_manual'

    log('\n=== SUMMARY ===')
    for s, r in results.items():
        robots = check_robots_via_api(DEV_PAGES[[p[1] for p in DEV_PAGES].index(s)][0])
        log(f'  /{s}/: result={r}, robots={robots}')

    browser.close()
