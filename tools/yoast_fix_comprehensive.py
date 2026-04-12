#!/usr/bin/env python3
"""
Comprehensive fix for PureBrain.ai dev pages noindex.

ROOT CAUSE DISCOVERED:
- Pages 439, 468, 150: Contain a full HTML document in their content field
  (including <head> with embedded robots meta tags)
  These need:
  1. Remove the embedded robots meta from content
  2. Set Yoast noindex via UI (which requires special save interception)

- Page 311: Normal content, just needs Yoast noindex set properly

APPROACH:
1. For pages with embedded robots meta:
   - Use REST API to update content, removing the <meta name='robots'...> tag
   - Then set Yoast noindex via a custom wp_postmeta update

2. For Yoast noindex persistence:
   - We need to intercept the Gutenberg save request
   - OR register the meta field properly
   - OR use a custom REST endpoint

The REAL fix is to either:
a) Delete these test pages entirely (cleanest solution)
b) Set them to "Draft" status (removes from Google)
c) Password protect them
d) Use custom PHP to set the noindex (requires WP access we don't have)
e) Remove embedded robots and add custom noindex header

Since we can't add PHP without file access, the best approach is:
- Set page status to "private" - prevents indexing (Google can't see private pages)
- Remove embedded robots meta from content
- Try Yoast noindex one more time with a different approach

UPDATE: Let's try the simplest approach that DEFINITELY works:
Set pages to "private" status - they won't be indexed by Google.
"""
import os, sys, time, re, base64, requests, json
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
SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/yoast-comprehensive')
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


def check_robots_live(slug):
    try:
        resp = requests.get(f'{WP_BASE_URL}/{slug}/', timeout=10,
                            headers={'Cache-Control': 'no-cache'})
        matches = re.findall(r'<meta[^>]*name=["\']robots["\'][^>]*>', resp.text, re.I)
        return matches
    except Exception as e:
        return [f'Error: {e}']


def check_robots_api(page_id):
    try:
        resp = requests.get(
            f"{WP_BASE_URL}/wp-json/yoast/v1/get_head?url={WP_BASE_URL}/?p={page_id}",
            headers=get_auth_headers(), timeout=10
        )
        if resp.status_code == 200:
            head = resp.json().get("html", "")
            match = re.search(r'<meta name="robots" content="([^"]+)"', head)
            return match.group(1) if match else "NOT FOUND"
    except Exception:
        return "API Error"
    return "API Error"


def remove_embedded_robots_from_content(page_id, slug):
    """Remove embedded <meta name='robots'...> tags from page content via REST API."""
    log(f'  Removing embedded robots meta from content (ID={page_id})...')
    headers = get_auth_headers()

    # Get current content
    resp = requests.get(
        f'{WP_BASE_URL}/wp-json/wp/v2/pages/{page_id}?context=edit&_fields=content',
        headers=headers, timeout=30
    )
    if resp.status_code != 200:
        log(f'  ERROR: Cannot get page content: HTTP {resp.status_code}')
        return False

    content_raw = resp.json().get('content', {}).get('raw', '')
    log(f'  Content length: {len(content_raw)} chars')

    # Count embedded robots meta tags
    matches = re.findall(r'<meta[^>]*name=["\']robots["\'][^>]*/?>', content_raw, re.I)
    log(f'  Found {len(matches)} embedded robots meta tags')
    for m in matches:
        log(f'    {m[:100]}')

    if not matches:
        log('  No embedded robots meta to remove')
        return True

    # Remove the embedded robots meta tags
    clean_content = re.sub(r'<meta[^>]*name=["\']robots["\'][^>]*/?>[\s]*', '', content_raw, flags=re.I)

    # Verify removal
    remaining = re.findall(r'<meta[^>]*name=["\']robots["\'][^>]*/?>', clean_content, re.I)
    log(f'  After removal: {len(remaining)} robots meta tags remain')

    # Update the content via REST API
    update_resp = requests.post(
        f'{WP_BASE_URL}/wp-json/wp/v2/pages/{page_id}',
        headers=headers,
        json={'content': clean_content},
        timeout=30
    )
    log(f'  Content update: HTTP {update_resp.status_code}')

    if update_resp.status_code == 200:
        # Verify
        new_content = update_resp.json().get('content', {}).get('raw', '')
        remaining2 = re.findall(r'<meta[^>]*name=["\']robots["\'][^>]*/?>', new_content, re.I)
        log(f'  Verified: {len(remaining2)} robots meta remaining in content')
        return True
    else:
        log(f'  ERROR: {update_resp.text[:200]}')
        return False


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


def set_yoast_noindex_and_capture_save(page, page_id, slug):
    """
    Set Yoast noindex via React, then intercept the save to add our meta.
    Key insight: Intercept the fetch call in the browser and modify the payload
    to include Yoast's meta fields before it's sent to the server.
    """
    log(f'  Opening edit page for {slug} (ID={page_id})...')

    # Setup request interception to add Yoast meta to the save payload
    save_intercepted = {'captured': False, 'payload': None, 'result': None}

    def handle_route(route):
        """Intercept the page save request and add Yoast meta."""
        if f'/wp-json/wp/v2/pages/{page_id}' in route.request.url:
            try:
                body = route.request.post_data
                if body:
                    try:
                        data = json.loads(body)
                    except Exception:
                        data = {}

                    # Add Yoast meta to the save payload
                    if 'meta' not in data:
                        data['meta'] = {}
                    # Note: this only works if the meta field is registered with REST API
                    # We'll try anyway
                    data['meta']['_yoast_wpseo_meta-robots-noindex'] = '1'

                    save_intercepted['captured'] = True
                    save_intercepted['payload'] = data

                    log(f'    INTERCEPTED save request, adding yoast meta')
                    log(f'    Modified payload keys: {list(data.keys())}')

                    route.continue_(post_data=json.dumps(data))
                    return
            except Exception as e:
                log(f'    Intercept error: {e}')

        route.continue_()

    page.route(f'**/wp-json/wp/v2/pages/{page_id}*', handle_route)

    page.goto(f'{WP_ADMIN_URL}/post.php?post={page_id}&action=edit',
              wait_until='domcontentloaded', timeout=60000)
    time.sleep(6)

    # Open Yoast sidebar
    yoast_btn = page.locator('button[aria-label="Yoast SEO"]')
    if yoast_btn.count() > 0:
        sidebar_text = page.evaluate(
            'document.querySelector(".interface-complementary-area") ? '
            'document.querySelector(".interface-complementary-area").innerText : ""'
        )
        if "Allow search engines" not in sidebar_text:
            yoast_btn.first.click()
            time.sleep(3)

    # Expand Advanced
    page.evaluate("""
        () => {
            const sidebar = document.querySelector(".interface-complementary-area");
            if (!sidebar) return;
            for (const b of sidebar.querySelectorAll("button")) {
                if ((b.innerText || "").trim() === "Advanced") {
                    if (b.getAttribute("aria-expanded") !== "true") { b.click(); }
                    return;
                }
            }
        }
    """)
    time.sleep(2)

    # Set noindex via React props (call onChange directly)
    set_result = page.evaluate("""
        () => {
            const sel = document.querySelector('#yoast-meta-robots-noindex-sidebar');
            if (!sel) return {error: 'not found'};
            if (sel.value === '1') return {method: 'already_set', value: sel.value};

            const propsKey = Object.keys(sel).find(k => k.startsWith('__reactProps'));
            if (propsKey && sel[propsKey] && sel[propsKey].onChange) {
                const nativeSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLSelectElement.prototype, 'value'
                ).set;
                nativeSetter.call(sel, '1');
                sel[propsKey].onChange({
                    target: sel,
                    currentTarget: sel,
                    type: 'change',
                    preventDefault: () => {},
                    stopPropagation: () => {},
                    nativeEvent: {target: sel}
                });
                return {method: 'react_onChange', newValue: sel.value};
            }
            return {error: 'no react props found'};
        }
    """)
    log(f'  Set result: {set_result}')
    time.sleep(2)

    ss(page, f'{slug}_01_noindex_set')

    # Check DOM value
    dom_val = page.evaluate("""
        () => {
            const sel = document.querySelector('#yoast-meta-robots-noindex-sidebar');
            return sel ? {value: sel.value, text: sel.options[sel.selectedIndex]?.text} : 'NOT FOUND';
        }
    """)
    log(f'  DOM value: {dom_val}')

    # Save the page
    log('  Saving page...')
    save_btn = page.locator('button.editor-post-publish-button')
    if save_btn.is_visible(timeout=3000):
        save_btn.click()
        try:
            page.wait_for_selector('.components-snackbar', timeout=15000)
            log('  Saved! (snackbar appeared)')
        except Exception:
            time.sleep(8)
    time.sleep(3)
    ss(page, f'{slug}_02_saved')

    # Unroute
    page.unroute(f'**/wp-json/wp/v2/pages/{page_id}*')

    log(f'  Intercept captured: {save_intercepted["captured"]}')
    return True


def try_direct_postmeta_via_php_ajax(page, page_id, slug):
    """
    Try to set the Yoast meta via a custom admin-ajax call.
    Uses the Yoast AJAX save action if it exists.
    """
    log(f'  Trying admin-ajax Yoast save for {slug}...')

    # Load admin page to get nonce
    page.goto(f'{WP_ADMIN_URL}/', wait_until='domcontentloaded', timeout=30000)
    time.sleep(2)

    # Try various AJAX actions that might write post meta
    result = page.evaluate(f"""
        async () => {{
            const postId = {page_id};
            const nonce = window.wpApiSettings ? window.wpApiSettings.nonce : null;

            if (!nonce) return {{error: 'no nonce'}};

            // Try 1: Classic Yoast AJAX save (older versions)
            const formData1 = new FormData();
            formData1.append('action', 'wpseo_set_post_noindex');
            formData1.append('post_id', postId);
            formData1.append('value', '1');
            formData1.append('nonce', nonce);

            const resp1 = await fetch('/wp-admin/admin-ajax.php', {{
                method: 'POST',
                body: formData1
            }});
            const text1 = await resp1.text();

            // Try 2: Generic update_post action with meta
            const formData2 = new FormData();
            formData2.append('action', 'heartbeat');
            formData2.append('data[wpseo-meta]', JSON.stringify({{
                'meta-robots-noindex': '1'
            }}));
            formData2.append('data[post_id]', postId);
            formData2.append('_nonce', nonce);

            const resp2 = await fetch('/wp-admin/admin-ajax.php', {{
                method: 'POST',
                body: formData2
            }});
            const text2 = await resp2.text();

            return {{
                ajax1: {{status: resp1.status, text: text1.slice(0, 100)}},
                ajax2: {{status: resp2.status, text: text2.slice(0, 100)}}
            }};
        }}
    """)
    log(f'  Ajax result: {result}')


log('=== Starting Comprehensive Yoast Noindex Fix ===')
log('')

# Phase 1: Remove embedded robots meta from content
log('PHASE 1: Remove embedded robots meta from page content')
for page_id, slug in DEV_PAGES:
    log(f'\n--- {slug} (ID={page_id}) ---')
    remove_embedded_robots_from_content(page_id, slug)

log('\nWaiting 3 seconds for changes to propagate...')
time.sleep(3)

# Phase 2: Check what the live pages show now
log('\nPHASE 1 RESULT: Live page robots after content cleanup:')
for page_id, slug in DEV_PAGES:
    tags = check_robots_live(slug)
    api = check_robots_api(page_id)
    log(f'  /{slug}/: {len(tags)} robots tag(s) | API: {api}')
    for t in tags:
        log(f'    {t[:150]}')

# Phase 3: Set Yoast noindex via UI
log('\nPHASE 2: Set Yoast noindex via browser UI')
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

    for page_id, slug in DEV_PAGES:
        log(f'\n--- Setting Yoast noindex for {slug} (ID={page_id}) ---')
        set_yoast_noindex_and_capture_save(page, page_id, slug)

        time.sleep(2)
        api_result = check_robots_api(page_id)
        log(f'  Post-save API robots: {api_result}')

    browser.close()

# Final verification
log('\n=== FINAL VERIFICATION ===')
time.sleep(5)
all_good = True
for page_id, slug in DEV_PAGES:
    live_tags = check_robots_live(slug)
    api_robots = check_robots_api(page_id)

    log(f'\n/{slug}/ (ID={page_id}):')
    log(f'  Live page robots tags: {len(live_tags)}')
    for t in live_tags:
        log(f'    {t[:150]}')
    log(f'  API robots: {api_robots}')

    # Check if noindex is set
    has_noindex = 'noindex' in api_robots.lower() or any('noindex' in t.lower() for t in live_tags)
    has_index_only = len(live_tags) == 1 and 'noindex' not in live_tags[0].lower()

    if has_noindex:
        log(f'  STATUS: NOINDEX SET')
    elif not live_tags or (len(live_tags) == 0):
        log(f'  STATUS: NO ROBOTS META (Yoast default - needs noindex)')
        all_good = False
    else:
        log(f'  STATUS: STILL INDEXABLE - needs manual fix')
        all_good = False

if all_good:
    log('\nALL PAGES: noindex set successfully!')
else:
    log('\nSome pages still need attention. See above for details.')
    log('\nFALLBACK OPTION: Set these pages to "Private" status to prevent indexing.')
    log('This is the most reliable approach when Yoast meta cannot be set programmatically.')
