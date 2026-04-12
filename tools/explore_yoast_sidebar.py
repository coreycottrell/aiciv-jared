#!/usr/bin/env python3
"""Explore Yoast sidebar structure to find correct selectors for noindex."""
import os, time
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
WP_BASE_URL = 'https://purebrain.ai'
WP_ADMIN_URL = f'{WP_BASE_URL}/wp-admin'
WP_USER = 'Aether'
WP_PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '').strip("'\"")
SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/noindex-explore')
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def ss(page, name):
    p = str(SCREENSHOT_DIR / f'{name}.png')
    try:
        page.screenshot(path=p, timeout=10000)
        print(f'Screenshot: {p}')
    except Exception as e:
        print(f'Screenshot failed: {e}')
    return p


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
    print(f'Logged in, URL: {page.url}')

    # Go to paypal-buttons-embed edit (ID=311)
    page.goto(f'{WP_ADMIN_URL}/post.php?post=311&action=edit', wait_until='domcontentloaded', timeout=60000)
    time.sleep(5)
    ss(page, 'A_initial')

    # Click the Yoast SEO toggle in sidebar
    toggle = page.locator('.components-panel__body-toggle:has-text("Yoast SEO")')
    print(f'Yoast toggle count: {toggle.count()}')
    if toggle.count() > 0:
        aria = toggle.first.get_attribute('aria-expanded')
        print(f'  aria-expanded: {aria}')
        if aria != 'true':
            toggle.first.click()
            time.sleep(3)
    ss(page, 'B_yoast_toggled')

    # Find all interactive elements in sidebar
    btns = page.evaluate('''
        () => {
            const sidebar = document.querySelector(".interface-complementary-area, .edit-post-sidebar");
            if (!sidebar) return ["NO SIDEBAR"];
            return Array.from(sidebar.querySelectorAll("button, a, select")).map(el => ({
                tag: el.tagName,
                id: el.id || "",
                text: (el.innerText || "").slice(0, 60).replace(/\\n/g, " "),
                cls: (el.className || "").slice(0, 80),
                visible: el.getBoundingClientRect().height > 0,
                ariaExp: el.getAttribute("aria-expanded")
            }));
        }
    ''')
    print(f'Sidebar interactive elements: {len(btns)}')
    for b in btns:
        print(f'  {b}')

    # Check all selects anywhere on page
    all_selects = page.evaluate('''
        () => Array.from(document.querySelectorAll("select")).map(s => ({
            id: s.id, name: s.name,
            options: Array.from(s.options).map(o => o.value + ":" + o.text),
            visible: s.getBoundingClientRect().height > 0
        }))
    ''')
    print(f'\nAll selects on page: {all_selects}')

    # Try clicking "Search appearance" button via JS
    result = page.evaluate('''
        () => {
            const all = document.querySelectorAll("button");
            for (const b of all) {
                const txt = (b.innerText || "").trim();
                if (txt.startsWith("Search appearance") || txt === "Search appearance") {
                    b.scrollIntoView({behavior: "instant", block: "center"});
                    return {found: true, text: txt, id: b.id, cls: b.className.slice(0, 80), ariaExp: b.getAttribute("aria-expanded")};
                }
            }
            return {found: false};
        }
    ''')
    print(f'\nSearch appearance button via JS: {result}')
    time.sleep(1)
    ss(page, 'C_scrolled_to_search_appearance')

    # Click it via JS if found
    if result.get('found'):
        page.evaluate('''
            () => {
                const all = document.querySelectorAll("button");
                for (const b of all) {
                    const txt = (b.innerText || "").trim();
                    if (txt.startsWith("Search appearance")) {
                        b.click();
                        return true;
                    }
                }
                return false;
            }
        ''')
        time.sleep(2)
        ss(page, 'D_after_search_appearance_click')

        # Now check selects again
        all_selects2 = page.evaluate('''
            () => Array.from(document.querySelectorAll("select")).map(s => ({
                id: s.id, name: s.name,
                options: Array.from(s.options).map(o => o.value + ":" + o.text),
                visible: s.getBoundingClientRect().height > 0
            }))
        ''')
        print(f'\nAll selects AFTER clicking Search appearance: {all_selects2}')

    browser.close()
