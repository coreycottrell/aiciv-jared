#!/usr/bin/env python3
"""
Clear GoDaddy WordPress cache and verify noindex on dev pages.
"""
import os, time, re, base64, requests
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

SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/cache-final')
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

DEV_SLUGS = ['pay-test', 'pay-test-sandbox', 'elementor-150', 'paypal-buttons-embed']


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
        resp = requests.get(f'{WP_BASE_URL}/{slug}/', timeout=10,
                            headers={'Cache-Control': 'no-cache'})
        match = re.search(r'<meta name=["\']robots["\'] content=["\']([^"\']+)["\']', resp.text, re.I)
        return match.group(1) if match else 'NOT FOUND'
    except Exception as e:
        return f'Error: {e}'


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

    # Method 1: Try GoDaddy cache clear via admin bar click
    page.goto(f'{WP_ADMIN_URL}/', wait_until='domcontentloaded', timeout=30000)
    time.sleep(2)
    ss(page, '01_dashboard')

    # Hover over GoDaddy Quick Links in admin bar to see submenu
    gd_bar = page.locator('#wp-admin-bar-godaddy-tools, #wp-admin-bar-godaddy-quick-links')
    if gd_bar.count() > 0:
        gd_bar.first.hover()
        time.sleep(1)
        ss(page, '02_gd_hover')

        # Look for cache-related items in submenu
        submenu = page.evaluate("""
            () => {
                const gd = document.querySelector("#wp-admin-bar-godaddy-tools, #wp-admin-bar-godaddy-quick-links");
                if (!gd) return "no godaddy menu";
                return gd.innerHTML.slice(0, 2000);
            }
        """)
        log(f'GoDaddy menu HTML: {submenu[:500]}')

    # Method 2: Try GoDaddy cache clear via ajax (wpaas_flush_cache)
    log('Trying ajax cache flush...')
    cache_result = page.evaluate("""
        async () => {
            try {
                const nonce = window.wpApiSettings ? window.wpApiSettings.nonce : '';
                const resp = await fetch('/wp-admin/admin-ajax.php', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'action=wpaas_flush_cache'
                });
                return {status: resp.status, text: (await resp.text()).slice(0, 200)};
            } catch(e) {
                return {error: e.toString()};
            }
        }
    """)
    log(f'Ajax wpaas_flush_cache: {cache_result}')

    # Method 3: GoDaddy uses a specific "wp-admin/admin.php?page=godaddy-site-design"
    # Check all admin pages
    log('Checking admin sidebar links...')
    admin_links = page.evaluate("""
        () => {
            const links = document.querySelectorAll("#adminmenu a");
            return Array.from(links).map(a => ({text: (a.innerText||"").slice(0,30), href: a.getAttribute("href")||""}));
        }
    """)
    for link in admin_links:
        if any(k in (link['text'] + link['href']).lower() for k in ['godaddy', 'cache', 'perf']):
            log(f'  Relevant link: {link}')

    # Navigate to each dev page URL while logged in (may clear cache)
    log('Visiting each dev page URL to trigger cache refresh...')
    for slug in DEV_SLUGS:
        url = f'{WP_BASE_URL}/{slug}/'
        page.goto(url, wait_until='domcontentloaded', timeout=20000)
        time.sleep(1)
        robots = page.evaluate("""
            () => {
                const m = document.querySelector('meta[name="robots"]');
                return m ? m.getAttribute("content") : "NOT FOUND";
            }
        """)
        log(f'  {url}: robots = {robots}')

    ss(page, '03_final_check')

    browser.close()

log('\nFinal verification via HTTP (fresh requests):')
time.sleep(5)
for slug in DEV_SLUGS:
    robots = check_robots_live(slug)
    log(f'  /{slug}/: {robots}')
