#!/usr/bin/env python3
"""
Definitive Yoast noindex setter.

Strategy:
1. Open each page in Gutenberg editor
2. Inject a direct REST API call FROM the browser context (so the nonce is valid)
   This bypasses the React UI entirely and writes directly to WordPress
3. The nonce comes from the page itself (window.wpApiSettings.nonce)
4. Send POST to /wp-json/wp/v2/pages/{id} with Yoast's registered meta field

This approach works because:
- The nonce is valid (from the logged-in browser session)
- We're using the same mechanism Gutenberg uses to save
- We can include whatever custom fields the Yoast plugin registers

Alternative if REST fails: Use wp-admin/admin-post.php or admin-ajax.php with
the wpseo_save_post action that Yoast hooks into.
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
SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/yoast-definitive')
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

DEV_PAGES = [
    (439, 'pay-test', 'pages'),
    (468, 'pay-test-sandbox', 'pages'),
    (150, 'elementor-150', 'pages'),
    (311, 'paypal-buttons-embed', 'pages'),
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


def set_noindex_via_browser_ajax(page, page_id, post_type, slug):
    """
    Open the edit page, get the nonce from the window, then use fetch()
    from the browser context to make an authenticated REST API call.
    This ensures the nonce is valid and Yoast's meta gets saved.
    """
    log(f'  Loading edit page for ID={page_id}...')
    page.goto(f'{WP_ADMIN_URL}/post.php?post={page_id}&action=edit',
              wait_until='domcontentloaded', timeout=60000)
    time.sleep(6)
    ss(page, f'{slug}_01_editor')

    # Get nonce and REST URL from window context
    nonce_info = page.evaluate("""
        () => {
            return {
                nonce: window.wpApiSettings ? window.wpApiSettings.nonce : null,
                root: window.wpApiSettings ? window.wpApiSettings.root : null,
                versionString: window.wpApiSettings ? window.wpApiSettings.versionString : null
            };
        }
    """)
    log(f'  Nonce info: nonce={nonce_info.get("nonce", "NONE")[:10]}..., root={nonce_info.get("root")}')

    if not nonce_info.get('nonce'):
        log('  ERROR: No nonce found - cannot proceed with browser REST call')
        return False

    nonce = nonce_info['nonce']

    # Method 1: Try sending via REST API with nonce (the Gutenberg way)
    log('  Attempting REST API save with nonce...')
    result = page.evaluate(f"""
        async () => {{
            const nonce = "{nonce}";
            const postId = {page_id};

            try {{
                // First, try the standard WP REST API with nonce
                const resp1 = await fetch('/wp-json/wp/v2/pages/' + postId, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': nonce
                    }},
                    body: JSON.stringify({{
                        meta: {{
                            '_yoast_wpseo_meta-robots-noindex': 1
                        }}
                    }})
                }});
                const data1 = await resp1.json();
                return {{
                    status: resp1.status,
                    meta_keys: data1.meta ? Object.keys(data1.meta) : [],
                    yoast_robots: data1.yoast_head_json ? data1.yoast_head_json.robots : null
                }};
            }} catch(e) {{
                return {{error: e.toString()}};
            }}
        }}
    """)
    log(f'  REST save result: {result}')

    return result


def set_noindex_via_admin_ajax(page, page_id, slug):
    """
    Try setting Yoast noindex via admin-ajax.php with the wpseo actions.
    This uses the classic WordPress form submission approach that older Yoast used.
    """
    log(f'  Trying admin-ajax approach for {slug}...')

    # Get nonce from admin page
    page.goto(f'{WP_ADMIN_URL}/post.php?post={page_id}&action=edit',
              wait_until='domcontentloaded', timeout=60000)
    time.sleep(5)

    # Try to find a wpseo nonce in the page
    ajax_result = page.evaluate(f"""
        async () => {{
            const postId = {page_id};

            // Look for any wpseo-related nonces in the page
            const nonces = {{}};

            // Check wpseoScriptData
            if (window.wpseoScriptData) {{
                nonces.wpseo = window.wpseoScriptData;
            }}

            // Check for classic editor yoast metabox nonce
            const yoastNonceEl = document.querySelector('#yoast_wpseo_meta-robots-noindex');
            const nonceField = document.querySelector('input[name="yoast_nonce"], input[name="_wpnonce_wpseo_ajax"]');

            // Try the REST API approach with wp nonce
            const wpNonce = window.wpApiSettings ? window.wpApiSettings.nonce : null;

            if (wpNonce) {{
                // Try to PATCH with nonce - this is how Gutenberg saves
                const resp = await fetch('/wp-json/wp/v2/pages/' + postId, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': wpNonce
                    }},
                    body: JSON.stringify({{
                        // Try several possible field names
                        meta: {{'_yoast_wpseo_meta-robots-noindex': '1'}},
                    }})
                }});
                const data = await resp.json();
                return {{
                    status: resp.status,
                    success: !data.code,
                    nonce_used: wpNonce.substring(0, 8),
                    yoast_robots: data.yoast_head_json ? data.yoast_head_json.robots : 'check separately',
                    meta: data.meta ? JSON.stringify(data.meta).substring(0, 200) : 'no meta field'
                }};
            }}

            return {{error: 'no nonce found', wpApiSettings: !!window.wpApiSettings}};
        }}
    """)
    log(f'  Ajax result: {ajax_result}')
    return ajax_result


def set_noindex_via_ui_with_react(page, page_id, slug):
    """
    Set noindex via UI using proper React event dispatching.
    The key: use nativeInputValueSetter AND trigger React's fiber reconciler.
    """
    log(f'  Loading edit page for {slug} (ID={page_id})...')
    page.goto(f'{WP_ADMIN_URL}/post.php?post={page_id}&action=edit',
              wait_until='domcontentloaded', timeout=60000)
    time.sleep(6)

    # Step 1: Ensure Yoast sidebar is open
    log('  Opening Yoast sidebar...')
    yoast_btn = page.locator('button[aria-label="Yoast SEO"]')
    if yoast_btn.count() > 0:
        sidebar_text = page.evaluate(
            'document.querySelector(".interface-complementary-area") ? '
            'document.querySelector(".interface-complementary-area").innerText : ""'
        )
        if "Advanced" not in sidebar_text or "Allow search engines" not in sidebar_text:
            yoast_btn.first.click()
            time.sleep(3)
            log('  Clicked Yoast toolbar button')

    ss(page, f'{slug}_01_sidebar')

    # Step 2: Click Advanced section
    log('  Expanding Advanced section...')
    advanced_result = page.evaluate("""
        () => {
            const sidebar = document.querySelector(".interface-complementary-area");
            if (!sidebar) return "NO SIDEBAR";

            // Find Advanced button
            const btns = sidebar.querySelectorAll("button");
            for (const b of btns) {
                const txt = (b.innerText || "").trim();
                if (txt === "Advanced") {
                    const expanded = b.getAttribute("aria-expanded");
                    if (expanded !== "true") {
                        b.scrollIntoView({behavior: "instant", block: "center"});
                        b.click();
                        return "clicked (was collapsed)";
                    } else {
                        return "already expanded";
                    }
                }
            }
            return "Advanced button not found";
        }
    """)
    log(f'  Advanced result: {advanced_result}')
    time.sleep(2)
    ss(page, f'{slug}_02_advanced')

    # Step 3: Find the robots select
    select_info = page.evaluate("""
        () => {
            const sel = document.querySelector('#yoast-meta-robots-noindex-sidebar');
            if (!sel) {
                // Try all selects
                const all = Array.from(document.querySelectorAll('select')).map(s => ({
                    id: s.id, name: s.name, optCount: s.options.length,
                    opts: Array.from(s.options).map(o => o.value + '=' + o.text).join(', ')
                }));
                return {error: 'select not found', allSelects: all};
            }
            return {
                id: sel.id,
                currentValue: sel.value,
                currentText: sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].text : '?',
                options: Array.from(sel.options).map(o => o.value + '=' + o.text)
            };
        }
    """)
    log(f'  Select info: {select_info}')

    if isinstance(select_info, dict) and 'error' in select_info:
        log('  ERROR: Select not found. Dumping sidebar structure...')
        sidebar_html = page.evaluate("""
            () => {
                const s = document.querySelector(".interface-complementary-area");
                return s ? s.innerText.slice(0, 2000) : "NO SIDEBAR";
            }
        """)
        log(f'  Sidebar text: {sidebar_html[:500]}')
        ss(page, f'{slug}_error')
        return False

    current_val = select_info.get('currentValue', '?')
    if current_val == '1':
        log(f'  Already set to noindex (value=1)!')
        return True

    # Step 4: Set value using React-compatible approach
    log('  Setting noindex via React synthetic events...')
    set_result = page.evaluate("""
        () => {
            const sel = document.querySelector('#yoast-meta-robots-noindex-sidebar');
            if (!sel) return {error: 'select not found'};

            // Get React fiber to find the onChange handler
            const fiberKey = Object.keys(sel).find(k => k.startsWith('__reactFiber') || k.startsWith('__reactInternalInstance'));
            const propsKey = Object.keys(sel).find(k => k.startsWith('__reactProps'));

            let reactInfo = {fiberKey: fiberKey || 'not found', propsKey: propsKey || 'not found'};

            if (propsKey && sel[propsKey]) {
                const props = sel[propsKey];
                const hasOnChange = !!props.onChange;
                reactInfo.hasOnChange = hasOnChange;

                if (hasOnChange) {
                    // Create a synthetic event-like object and call onChange directly
                    const syntheticEvent = {
                        target: sel,
                        currentTarget: sel,
                        type: 'change',
                        preventDefault: () => {},
                        stopPropagation: () => {}
                    };

                    // Set the actual value first
                    const nativeSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLSelectElement.prototype, 'value'
                    ).set;
                    nativeSetter.call(sel, '1');

                    // Update the target value in the synthetic event
                    syntheticEvent.target = sel;

                    // Call React's onChange handler directly
                    props.onChange(syntheticEvent);

                    return {
                        method: 'react-props-onChange',
                        newValue: sel.value,
                        reactInfo: reactInfo
                    };
                }
            }

            // Fallback: use nativeInputValueSetter approach
            const nativeSetter = Object.getOwnPropertyDescriptor(
                window.HTMLSelectElement.prototype, 'value'
            ).set;
            nativeSetter.call(sel, '1');

            // Fire all relevant events
            ['input', 'change'].forEach(evtName => {
                const evt = new Event(evtName, {bubbles: true, cancelable: true});
                sel.dispatchEvent(evt);
            });

            return {
                method: 'native-setter-events',
                newValue: sel.value,
                reactInfo: reactInfo
            };
        }
    """)
    log(f'  React set result: {set_result}')
    time.sleep(2)
    ss(page, f'{slug}_03_noindex_set')

    # Verify current state in DOM
    verify = page.evaluate("""
        () => {
            const sel = document.querySelector('#yoast-meta-robots-noindex-sidebar');
            return sel ? {value: sel.value, text: sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].text : '?'} : 'NOT FOUND';
        }
    """)
    log(f'  DOM verify: {verify}')

    return True


def save_page_and_wait(page, slug):
    """Save the page and wait for confirmation."""
    log('  Saving page...')

    # Click the Save/Update button in the top bar
    saved = False
    for selector in [
        'button.editor-post-publish-button',
        'button[aria-label="Save"]',
        'button[aria-label="Update"]',
        '.editor-post-save-draft'
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=2000):
                btn.click()
                log(f'  Clicked save: {selector}')
                # Wait for save confirmation
                try:
                    page.wait_for_selector(
                        '.components-snackbar:has-text("updated"), '
                        '.components-snackbar:has-text("saved"), '
                        '.editor-post-publish-panel__header-published',
                        timeout=15000
                    )
                    log('  Save confirmed via snackbar!')
                    saved = True
                except Exception:
                    time.sleep(5)
                    log('  No snackbar found, waited 5s')
                    saved = True  # Assume saved if button was clickable
                ss(page, f'{slug}_saved')
                break
        except Exception:
            continue

    if not saved:
        log('  WARNING: Could not find save button')
    return saved


def flush_godaddy_cache_via_api(session_page):
    """Flush GoDaddy cache using their REST API."""
    log('Flushing GoDaddy cache via API...')

    # Get nonce from admin page
    nonce_info = session_page.evaluate("""
        () => ({
            nonce: window.wpApiSettings ? window.wpApiSettings.nonce : null
        })
    """)

    nonce = nonce_info.get('nonce')
    if not nonce:
        log('  No nonce available for cache flush')
        return False

    result = session_page.evaluate(f"""
        async () => {{
            const nonce = "{nonce}";
            try {{
                const resp = await fetch('/wp-json/wpaas/v1/flush-cache', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': nonce
                    }},
                    body: JSON.stringify({{}})
                }});
                const text = await resp.text();
                return {{status: resp.status, body: text.substring(0, 200)}};
            }} catch(e) {{
                return {{error: e.toString()}};
            }}
        }}
    """)
    log(f'  Cache flush result: {result}')
    return True


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
    ss(page, '00_logged_in')

    results = {}
    for page_id, slug, post_type in DEV_PAGES:
        log(f'\n=== Processing /{slug}/ (ID={page_id}) ===')

        # Pre-check
        pre_robots = check_robots_api(page_id)
        log(f'  Pre-check robots: {pre_robots}')

        if 'noindex' in pre_robots.lower():
            log(f'  Already noindexed!')
            results[slug] = 'already_done'
            continue

        # Try UI approach with React event dispatch
        success = set_noindex_via_ui_with_react(page, page_id, slug)

        if success:
            # Save the page
            save_page_and_wait(page, slug)

            # Wait and check
            time.sleep(3)
            post_robots = check_robots_api(page_id)
            log(f'  Post-save robots (API): {post_robots}')

            if 'noindex' in post_robots.lower():
                results[slug] = 'SUCCESS'
                log(f'  SUCCESS: noindex confirmed!')
            else:
                log(f'  Save completed but robots still shows: {post_robots}')
                log(f'  Trying browser-ajax approach as fallback...')

                # Try the browser REST API approach with nonce
                ajax_result = set_noindex_via_browser_ajax(page, page_id, post_type, slug)
                log(f'  Browser REST result: {ajax_result}')

                time.sleep(2)
                post_robots2 = check_robots_api(page_id)
                log(f'  Post-ajax robots (API): {post_robots2}')

                if 'noindex' in post_robots2.lower():
                    results[slug] = 'SUCCESS_via_ajax'
                else:
                    results[slug] = 'PERSISTING_ISSUE'
        else:
            results[slug] = 'UI_FAILED'

    # Flush GoDaddy cache
    log('\n=== Flushing GoDaddy cache ===')
    page.goto(f'{WP_ADMIN_URL}/', wait_until='domcontentloaded', timeout=30000)
    time.sleep(2)
    flush_godaddy_cache_via_api(page)

    log('\n=== FINAL SUMMARY ===')
    for pid, slug, _ in DEV_PAGES:
        robots = check_robots_api(pid)
        log(f'  /{slug}/ (ID={pid}):')
        log(f'    Script result: {results.get(slug, "?")}')
        log(f'    Final robots: {robots}')

    browser.close()
