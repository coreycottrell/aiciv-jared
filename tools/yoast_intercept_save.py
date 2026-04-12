#!/usr/bin/env python3
"""
Intercept what Gutenberg actually sends to the REST API when saving with Yoast.
We'll set the noindex via React, then intercept the save request to see
what payload Gutenberg is sending.
"""
import os, sys, time
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Route
import json
import datetime

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
WP_BASE_URL = 'https://purebrain.ai'
WP_ADMIN_URL = f'{WP_BASE_URL}/wp-admin'
WP_USER = 'Aether'
WP_PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '').strip("'\"")
SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/yoast-intercept')
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

captured_requests = []


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

    # Intercept all REST API requests to capture save payload
    def handle_request(request):
        if 'wp-json/wp/v2/pages/439' in request.url and request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = request.post_data
                captured_requests.append({
                    'url': request.url,
                    'method': request.method,
                    'body': body
                })
                log(f'  CAPTURED: {request.method} {request.url}')
                log(f'  BODY: {body[:500] if body else "NO BODY"}')
            except Exception as e:
                log(f'  Error capturing request: {e}')

    page.on('request', handle_request)

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

    # Load pay-test editor
    page.goto(f'{WP_ADMIN_URL}/post.php?post=439&action=edit',
              wait_until='domcontentloaded', timeout=60000)
    time.sleep(6)

    # Open Yoast sidebar
    yoast_btn = page.locator('button[aria-label="Yoast SEO"]')
    if yoast_btn.count() > 0:
        yoast_btn.first.click()
        time.sleep(3)

    # Expand Advanced
    page.evaluate("""
        () => {
            const sidebar = document.querySelector(".interface-complementary-area");
            if (!sidebar) return;
            const btns = sidebar.querySelectorAll("button");
            for (const b of btns) {
                if ((b.innerText || "").trim() === "Advanced") {
                    const expanded = b.getAttribute("aria-expanded");
                    if (expanded !== "true") { b.click(); }
                    return;
                }
            }
        }
    """)
    time.sleep(2)

    # Set noindex via React props
    set_result = page.evaluate("""
        () => {
            const sel = document.querySelector('#yoast-meta-robots-noindex-sidebar');
            if (!sel) return {error: 'not found'};
            const propsKey = Object.keys(sel).find(k => k.startsWith('__reactProps'));
            if (propsKey && sel[propsKey] && sel[propsKey].onChange) {
                const nativeSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLSelectElement.prototype, 'value'
                ).set;
                nativeSetter.call(sel, '1');
                sel[propsKey].onChange({target: sel, currentTarget: sel, type: 'change'});
                return {method: 'react', newValue: sel.value};
            }
            return {error: 'no react props'};
        }
    """)
    log(f'Set result: {set_result}')
    time.sleep(2)
    ss(page, 'after_set')

    # Now save and capture the request
    log('Clicking save button...')
    save_btn = page.locator('button.editor-post-publish-button')
    if save_btn.is_visible(timeout=3000):
        save_btn.click()
        # Wait for save
        try:
            page.wait_for_selector('.components-snackbar', timeout=15000)
            log('Snackbar appeared')
        except Exception:
            time.sleep(8)
    time.sleep(3)
    ss(page, 'after_save')

    log(f'\n=== CAPTURED {len(captured_requests)} requests ===')
    for req in captured_requests:
        log(f'URL: {req["url"]}')
        log(f'METHOD: {req["method"]}')
        body = req.get('body', '')
        if body:
            try:
                parsed = json.loads(body)
                log(f'BODY (parsed): {json.dumps(parsed, indent=2)[:2000]}')
            except Exception:
                log(f'BODY (raw): {body[:1000]}')
        log('---')

    browser.close()
