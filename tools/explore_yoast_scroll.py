#!/usr/bin/env python3
"""Scroll sidebar to find Yoast noindex control."""
import os, time
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
WP_BASE_URL = 'https://purebrain.ai'
WP_ADMIN_URL = f'{WP_BASE_URL}/wp-admin'
WP_USER = 'Aether'
WP_PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '').strip("'\"")
SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/noindex-scroll')
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def ss(page, name):
    p = str(SCREENSHOT_DIR / f'{name}.png')
    try:
        page.screenshot(path=p, timeout=10000)
        print(f'Screenshot: {p}')
    except Exception as e:
        print(f'Screenshot failed: {e}')


def scroll_sidebar(page, amount):
    """Scroll within the sidebar panel."""
    page.evaluate(f'''
        () => {{
            const sidebar = document.querySelector(".interface-complementary-area");
            if (sidebar) sidebar.scrollTop += {amount};
        }}
    ''')
    time.sleep(1)


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

    # Go to paypal-buttons-embed (simpler page, ID=311)
    page.goto(f'{WP_ADMIN_URL}/post.php?post=311&action=edit', wait_until='domcontentloaded', timeout=60000)
    time.sleep(5)

    # Expand Yoast SEO panel if collapsed
    toggle = page.locator('.components-panel__body-toggle:has-text("Yoast SEO")')
    if toggle.count() > 0:
        if toggle.first.get_attribute('aria-expanded') != 'true':
            toggle.first.click()
            time.sleep(2)

    ss(page, '01_yoast_expanded')

    # Scroll sidebar down progressively and take screenshots
    for i, scroll_amount in enumerate([100, 200, 300, 400, 500, 600]):
        scroll_sidebar(page, 100)
        ss(page, f'02_scroll_{i}_{scroll_amount}')

        # Check for new selects or buttons
        all_interactive = page.evaluate('''
            () => {
                const sidebar = document.querySelector(".interface-complementary-area");
                if (!sidebar) return [];
                const viewport = sidebar.getBoundingClientRect();
                return Array.from(sidebar.querySelectorAll("button, select, input[type=radio], input[type=checkbox]")).map(el => {
                    const rect = el.getBoundingClientRect();
                    return {
                        tag: el.tagName,
                        id: el.id || "",
                        type: el.type || "",
                        text: (el.innerText || "").slice(0, 40).replace(/\n/g, " "),
                        inViewport: rect.top >= 0 && rect.bottom <= window.innerHeight
                    };
                });
            }
        ''')
        visible = [x for x in all_interactive if x['inViewport']]
        print(f'\nScroll {scroll_amount}: Visible elements ({len(visible)}):')
        for v in visible:
            print(f'  {v}')

    # Dump the full sidebar HTML to find the noindex control
    sidebar_html = page.evaluate('''
        () => {
            const sidebar = document.querySelector(".interface-complementary-area");
            return sidebar ? sidebar.innerHTML : "NO SIDEBAR";
        }
    ''')

    # Search for noindex/robots related HTML
    import re
    noindex_hits = []
    for pattern in ['noindex', 'robots', 'robot', 'index', 'Allow search', 'visibility', 'crawl']:
        matches = [(m.start(), sidebar_html[max(0,m.start()-50):m.end()+100]) for m in re.finditer(pattern, sidebar_html, re.I)]
        if matches:
            print(f'\nPattern "{pattern}" found {len(matches)} times:')
            for pos, ctx in matches[:2]:
                print(f'  pos={pos}: {ctx[:150]}')

    # Save sidebar HTML for inspection
    html_path = '/tmp/yoast_sidebar.html'
    with open(html_path, 'w') as f:
        f.write(sidebar_html)
    print(f'\nFull sidebar HTML saved to {html_path} ({len(sidebar_html)} chars)')

    browser.close()
