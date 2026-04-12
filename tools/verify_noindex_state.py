#!/usr/bin/env python3
"""
Verify that the Yoast noindex is actually saved for the dev pages.
Opens each page in editor, checks the current robots select value.
"""
import os, sys, time, re
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import datetime

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
WP_BASE_URL = 'https://purebrain.ai'
WP_ADMIN_URL = f'{WP_BASE_URL}/wp-admin'
WP_USER = 'Aether'
WP_PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '').strip("'\"")
SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/verify-noindex')
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


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={'width': 1440, 'height': 900},
        device_scale_factor=2,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36'
    )
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

    for page_id, slug in DEV_PAGES:
        log(f'\n=== Verifying /{slug}/ (ID={page_id}) ===')

        page.goto(f'{WP_ADMIN_URL}/post.php?post={page_id}&action=edit',
                  wait_until='domcontentloaded', timeout=60000)
        time.sleep(5)

        # Open Yoast toolbar
        yoast_btn = page.locator('button[aria-label="Yoast SEO"]')
        if yoast_btn.count() > 0:
            sidebar_text = page.evaluate(
                'document.querySelector(".interface-complementary-area") ? '
                'document.querySelector(".interface-complementary-area").innerText : ""'
            )
            if "Advanced" not in sidebar_text:
                yoast_btn.first.click()
                time.sleep(2)

        # Click Advanced
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

        # Check the robots select value
        sel_value = page.evaluate("""
            () => {
                const sel = document.querySelector("#yoast-meta-robots-noindex-sidebar");
                if (!sel) return "SELECT NOT FOUND";
                const currentOpt = sel.options[sel.selectedIndex];
                return {
                    value: sel.value,
                    text: currentOpt ? currentOpt.text : "?",
                    allOptions: Array.from(sel.options).map(o => o.value + "=" + o.text)
                };
            }
        """)
        log(f'  Robots select: {sel_value}')

        # Take screenshot
        ss(page, f'{slug}_verify')

        # Interpretation
        if isinstance(sel_value, dict):
            val = sel_value.get('value', '?')
            txt = sel_value.get('text', '?')
            if val == '1':
                log(f'  STATUS: NOINDEX set (value=1, text="{txt}")')
            elif val == '0':
                log(f'  STATUS: Using default (value=0 = "Yes, default") - INDEXABLE')
            elif val == '2':
                log(f'  STATUS: Explicitly indexed (value=2 = "Yes") - INDEXABLE')
            else:
                log(f'  STATUS: Unknown (value={val})')
        else:
            log(f'  STATUS: Could not read select: {sel_value}')

    browser.close()
