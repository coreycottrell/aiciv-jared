#!/usr/bin/env python3
"""
Set Yoast noindex via "Advanced" section in Yoast SEO sidebar.
From screenshot analysis:
- Click Yoast SEO toolbar button => opens Yoast sidebar
- The sidebar has "Advanced" section (visible in right sidebar)
- Click "Advanced" to expand it
- Find robots noindex select (yoast-meta-robots-noindex-sidebar)
- Options: 0=Yes(default), 1=No(noindex), 2=Yes(explicitly index)
- Set to value 1 (No = noindex)
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
SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/yoast-noindex-correct')
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Value 1 = "No" = noindex (CORRECT - blocks search engines from showing page)
NOINDEX_VALUE = '1'

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
    """Check live page robots meta."""
    try:
        resp = requests.get(f'{WP_BASE_URL}/{slug}/', timeout=10)
        match = re.search(r'<meta name=["\']robots["\'] content=["\']([^"\']+)["\']', resp.text, re.I)
        return match.group(1) if match else 'NOT FOUND'
    except Exception as e:
        return f'Error: {e}'


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


def set_noindex_for_page(page, page_id, slug):
    """
    Navigate to edit page, open Yoast Advanced section, set noindex.
    The robots select ID is: yoast-meta-robots-noindex-sidebar
    Value 1 = "No" = noindex
    """
    log(f'  Navigating to edit page {page_id}...')
    page.goto(f'{WP_ADMIN_URL}/post.php?post={page_id}&action=edit',
              wait_until='domcontentloaded', timeout=60000)
    time.sleep(5)
    ss(page, f'{slug}_01_loaded')

    # Open Yoast SEO sidebar via toolbar button
    log('  Opening Yoast SEO sidebar...')
    yoast_btn = page.locator('button[aria-label="Yoast SEO"]')
    if yoast_btn.count() > 0:
        sidebar_text = page.evaluate(
            'document.querySelector(".interface-complementary-area") ? '
            'document.querySelector(".interface-complementary-area").innerText : ""'
        )
        if "Yoast SEO" not in sidebar_text or "Advanced" not in sidebar_text:
            yoast_btn.first.click()
            time.sleep(2)
            log('  Clicked Yoast toolbar button')

    ss(page, f'{slug}_02_yoast_sidebar')

    # Find and click "Advanced" toggle in sidebar
    advanced_clicked = page.evaluate("""
        () => {
            const sidebar = document.querySelector(".interface-complementary-area");
            if (!sidebar) return "no sidebar";
            const btns = sidebar.querySelectorAll("button");
            for (const b of btns) {
                const txt = (b.innerText || "").trim();
                if (txt === "Advanced" || txt === "Advanced ") {
                    b.scrollIntoView({behavior: "instant", block: "center"});
                    b.click();
                    return "clicked: " + b.id + " class=" + b.className.slice(0, 40);
                }
            }
            return "not found";
        }
    """)
    log(f'  Advanced click result: {advanced_clicked}')
    time.sleep(2)
    ss(page, f'{slug}_03_advanced_clicked')

    # Look for the robots index select
    all_selects = page.evaluate("""
        () => {
            const selects = Array.from(document.querySelectorAll("select"));
            return selects.map(function(s) {
                return {
                    id: s.id,
                    name: s.getAttribute("name"),
                    options: Array.from(s.options).map(function(o) { return o.value + "=" + o.text; }),
                    value: s.value,
                    visible: s.getBoundingClientRect().height > 0
                };
            });
        }
    """)
    log(f'  All selects: {all_selects}')

    # Find the robots index select (yoast-meta-robots-noindex-sidebar)
    robots_select = None
    for s in all_selects:
        if s.get('id') == 'yoast-meta-robots-noindex-sidebar' and s.get('visible', False):
            robots_select = s
            break
        # Fallback: find by id containing 'noindex'
        if s.get('id') and 'noindex' in s['id'].lower() and s.get('visible', False):
            robots_select = s
            break

    if robots_select:
        log(f'  Found robots select: {robots_select}')
        sel_id = robots_select['id']
        sel_el = page.locator(f'select#{sel_id}').first

        # Check current value
        current_val = sel_el.input_value()
        log(f'  Current value: {current_val}')

        if current_val == NOINDEX_VALUE:
            log(f'  Already set to noindex (value={NOINDEX_VALUE})!')
            return True

        # Set to noindex: value='1' = "No" = noindex
        sel_el.select_option(value=NOINDEX_VALUE)
        new_val = sel_el.input_value()
        log(f'  Set to value {NOINDEX_VALUE} (No = noindex). Confirmed: {new_val}')
        time.sleep(1)
        ss(page, f'{slug}_04_noindex_set')
        return True
    else:
        log(f'  ERROR: Could not find yoast-meta-robots-noindex-sidebar select')
        ss(page, f'{slug}_04_error')
        return False


def save_page(page, slug):
    for sel in ['button.editor-post-publish-button', 'button[aria-label="Update"]',
                'input#publish']:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click()
                time.sleep(5)
                ss(page, f'{slug}_saved')
                log('  Saved!')
                return True
        except Exception:
            continue
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
            save_page(page, slug)
            results[slug] = 'set'
        else:
            results[slug] = 'failed'

    log('\n=== SUMMARY ===')
    time.sleep(3)
    for pid, slug in DEV_PAGES:
        live_robots = check_robots_live(slug)
        api_robots = check_robots_via_api(pid)
        log(f'  /{slug}/:')
        log(f'    Result: {results.get(slug, "?")}')
        log(f'    Live robots: {live_robots}')
        log(f'    API robots: {api_robots}')

    browser.close()
