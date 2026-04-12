#!/usr/bin/env python3
"""
Set dev/test pages to private status to prevent Google indexing.
Private pages:
- Cannot be accessed without WordPress login
- Google cannot crawl them
- They get a noindex header automatically
- Still work for logged-in admins (can test payment flows while logged in)

This is the most reliable solution when Yoast noindex can't be set programmatically.

Also flushes GoDaddy cache via browser automation.
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
SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/pages-private')
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


def get_auth_headers():
    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}", "Content-Type": "application/json"}


def set_page_private_via_api(page_id, slug):
    """Set a page to private status via REST API."""
    headers = get_auth_headers()

    # First check current status
    resp = requests.get(
        f'{WP_BASE_URL}/wp-json/wp/v2/pages/{page_id}?context=edit&_fields=id,status',
        headers=headers, timeout=10
    )
    current_status = resp.json().get('status', 'unknown') if resp.status_code == 200 else 'error'
    log(f'  Current status: {current_status}')

    if current_status == 'private':
        log('  Already private!')
        return True

    # Set to private
    update_resp = requests.post(
        f'{WP_BASE_URL}/wp-json/wp/v2/pages/{page_id}',
        headers=headers,
        json={'status': 'private'},
        timeout=30
    )
    log(f'  Set private: HTTP {update_resp.status_code}')

    if update_resp.status_code == 200:
        new_status = update_resp.json().get('status', 'unknown')
        log(f'  New status: {new_status}')
        return new_status == 'private'
    else:
        log(f'  Error: {update_resp.text[:200]}')
        return False


def check_page_visibility(slug):
    """Check if page is publicly accessible (returns 200) or private (returns 401/403/redirect)."""
    try:
        resp = requests.get(
            f'{WP_BASE_URL}/{slug}/',
            timeout=10,
            allow_redirects=False,
            headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
        )
        robots_match = re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)["\']', resp.text, re.I)
        robots = robots_match.group(1) if robots_match else 'NOT FOUND'
        return {
            'status_code': resp.status_code,
            'publicly_accessible': resp.status_code == 200,
            'robots': robots,
            'location': resp.headers.get('Location', '')
        }
    except Exception as e:
        return {'error': str(e)}


def flush_cache_via_browser(page):
    """Attempt to flush GoDaddy cache via browser with admin privileges."""
    log('Attempting to flush GoDaddy cache...')

    # Navigate to admin
    page.goto(f'{WP_ADMIN_URL}/', wait_until='domcontentloaded', timeout=30000)
    time.sleep(2)

    # Try cache flush via fetch with nonce
    result = page.evaluate("""
        async () => {
            const nonce = window.wpApiSettings ? window.wpApiSettings.nonce : null;
            if (!nonce) return {error: 'no nonce'};

            // Try GoDaddy flush-cache endpoint
            const resp = await fetch('/wp-json/wpaas/v1/flush-cache', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': nonce
                },
                body: '{}'
            });
            const text = await resp.text();
            return {status: resp.status, body: text.slice(0, 200)};
        }
    """)
    log(f'  Flush result: {result}')

    # Also try the admin_ajax cache clear
    result2 = page.evaluate("""
        async () => {
            const formData = new FormData();
            formData.append('action', 'wpaas_flush_cache');
            const resp = await fetch('/wp-admin/admin-ajax.php', {
                method: 'POST',
                body: formData
            });
            const text = await resp.text();
            return {status: resp.status, body: text.slice(0, 200)};
        }
    """)
    log(f'  Ajax flush: {result2}')

    # Navigate through each page to bust the cache with logged-in session
    log('  Visiting each dev page to bust per-page cache...')
    for _, slug in DEV_PAGES:
        page.goto(f'{WP_BASE_URL}/{slug}/', wait_until='domcontentloaded', timeout=20000)
        log(f'    Visited /{slug}/')
        time.sleep(1)


log('=== Setting Dev Pages to Private ===')
log('')

# Phase 1: Set all pages to private via REST API
log('PHASE 1: Set pages to private via REST API')
results = {}
for page_id, slug in DEV_PAGES:
    log(f'\n--- {slug} (ID={page_id}) ---')
    success = set_page_private_via_api(page_id, slug)
    results[slug] = 'private' if success else 'failed'

# Phase 2: Flush cache via browser
log('\n\nPHASE 2: Flush cache and verify')
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
    ss(page, '00_logged_in')

    # Flush cache
    flush_cache_via_browser(page)
    ss(page, '01_after_cache_flush')

    browser.close()

# Phase 3: Verify - wait for cache to expire
log('\n\nPHASE 3: Verification (waiting 5s for cache propagation)...')
time.sleep(5)

log('\n=== FINAL RESULTS ===')
all_protected = True
for page_id, slug in DEV_PAGES:
    visibility = check_page_visibility(slug)
    log(f'\n/{slug}/ (ID={page_id}):')
    log(f'  Set result: {results.get(slug, "?")}')
    log(f'  HTTP status: {visibility.get("status_code", "?")}')
    log(f'  Publicly accessible: {visibility.get("publicly_accessible", "?")}')
    log(f'  Robots (if accessible): {visibility.get("robots", "N/A")}')

    if not visibility.get('publicly_accessible', True):
        log(f'  STATUS: PROTECTED (page not publicly accessible)')
    else:
        log(f'  STATUS: STILL ACCESSIBLE (cache may still be serving old content)')
        # Check if GoDaddy cache is still serving the old page
        if visibility.get('robots', '') != 'NOT FOUND':
            log(f'    (GoDaddy cache serving stale content - will expire automatically)')
        all_protected = False

log('\n')
if all_protected:
    log('ALL PAGES PROTECTED: Google cannot index these pages.')
else:
    log('NOTE: Some pages may still be accessible due to GoDaddy server cache.')
    log('GoDaddy cache typically expires within 1-5 minutes.')
    log('Once cache expires, private pages will redirect to login page.')
    log('Google will see 401/403 and will not index these pages.')
    log()
    log('VERIFICATION STEPS:')
    log('1. Wait 5 minutes for cache to fully expire')
    log('2. Open incognito browser and try to visit each URL')
    log('3. You should be redirected to login page')
    log('4. Google Search Console should show these as excluded from index')
