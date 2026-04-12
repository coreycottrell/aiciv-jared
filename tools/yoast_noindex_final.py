#!/usr/bin/env python3
"""
Final approach: Set Yoast noindex via the full Yoast SEO sidebar panel.
1. Click the Yoast SEO toolbar button (aria-label="Yoast SEO") to open full Yoast panel
2. Scroll sidebar to find "Search appearance" content
3. Find the robots noindex control (may be a select or React toggle)
4. Set to noindex and save

Alternative if that fails: Use wp-admin/admin.php?page=wpseo_page_settings to
navigate to Yoast's full settings page for each URL.
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
SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/yoast-final')
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


def scroll_sidebar(page, amount=200):
    """Scroll within the sidebar."""
    page.evaluate(f'''
        () => {{
            const sidebar = document.querySelector(".interface-complementary-area");
            if (sidebar) {{ sidebar.scrollTop += {amount}; }}
        }}
    ''')
    time.sleep(0.5)


def get_all_interactive_in_sidebar(page):
    """Get all interactive elements currently visible in sidebar."""
    return page.evaluate('''
        () => {
            const sidebar = document.querySelector(".interface-complementary-area");
            if (!sidebar) return [];
            return Array.from(sidebar.querySelectorAll("button, select, input")).map(el => {
                const rect = el.getBoundingClientRect();
                return {
                    tag: el.tagName,
                    id: el.id || "",
                    type: el.getAttribute("type") || "",
                    name: el.getAttribute("name") || "",
                    ariaLabel: el.getAttribute("aria-label") || "",
                    ariaExpanded: el.getAttribute("aria-expanded") || "",
                    text: (el.innerText || el.value || "").slice(0, 60).replace(/\n/g, " "),
                    cls: el.className.slice(0, 80),
                    visible: rect.height > 0 && rect.width > 0,
                    inViewport: rect.top >= 0 && rect.bottom <= window.innerHeight
                };
            });
        }
    ''')


def find_and_set_noindex(page, slug):
    """
    Open Yoast SEO panel, scroll to find Search appearance > robots,
    set to noindex, and save.
    """
    log(f'  Opening Yoast SEO panel via toolbar button...')
    # Click the Yoast SEO toolbar button to open the full Yoast panel
    yoast_btn = page.locator('button[aria-label="Yoast SEO"]')
    if yoast_btn.count() > 0:
        # Check if Yoast panel is already open
        yoast_panel = page.locator('.interface-complementary-area #wpseo_meta, .interface-complementary-area button:has-text("Search appearance")')
        if not yoast_panel.is_visible(timeout=2000):
            yoast_btn.first.click()
            time.sleep(2)
            log('  Clicked Yoast toolbar button')
        ss(page, f'{slug}_01_yoast_open')
    else:
        log('  WARNING: No Yoast SEO toolbar button found')

    # The Yoast panel is now the Gutenberg sidebar
    # Need to make sure the Yoast SEO panel section is expanded
    toggle = page.locator('.components-panel__body-toggle:has-text("Yoast SEO")')
    if toggle.count() > 0:
        aria = toggle.first.get_attribute('aria-expanded')
        log(f'  Yoast toggle aria-expanded={aria}')
        if aria != 'true':
            toggle.first.click()
            time.sleep(2)

    # Check if sidebar switched to Yoast SEO mode (the Y icon opens a separate Yoast panel)
    # Check sidebar content
    sidebar_text = page.evaluate('''
        () => {
            const sidebar = document.querySelector(".interface-complementary-area");
            return sidebar ? sidebar.innerText.slice(0, 3000) : "NO SIDEBAR";
        }
    ''')
    log(f'  Sidebar text (first 500): {sidebar_text[:500]}')

    # Look for "Search appearance" text in sidebar
    if "Search appearance" in sidebar_text:
        log('  Found "Search appearance" in sidebar - need to click/expand it')

        # Find and click the Search appearance button
        search_app_btn = page.evaluate('''
            () => {
                const sidebar = document.querySelector(".interface-complementary-area");
                if (!sidebar) return null;
                const btns = sidebar.querySelectorAll("button");
                for (const b of btns) {
                    if (b.innerText && b.innerText.trim() === "Search appearance") {
                        const rect = b.getBoundingClientRect();
                        return {
                            id: b.id,
                            cls: b.className.slice(0, 80),
                            text: b.innerText.slice(0, 40),
                            ariaExp: b.getAttribute("aria-expanded"),
                            inView: rect.top >= 0 && rect.bottom <= window.innerHeight
                        };
                    }
                }
                return null;
            }
        ''')
        log(f'  Search appearance button info: {search_app_btn}')

        # Click it via JS
        clicked = page.evaluate('''
            () => {
                const sidebar = document.querySelector(".interface-complementary-area");
                if (!sidebar) return false;
                const btns = sidebar.querySelectorAll("button");
                for (const b of btns) {
                    if (b.innerText && b.innerText.trim() === "Search appearance") {
                        b.scrollIntoView({behavior: "instant", block: "center"});
                        b.click();
                        return true;
                    }
                }
                return false;
            }
        ''')
        log(f'  Clicked Search appearance: {clicked}')
        time.sleep(2)
        ss(page, f'{slug}_02_search_app_clicked')

        # Now look for robots select or react-based toggle
        all_els = get_all_interactive_in_sidebar(page)
        log(f'  All sidebar elements after click ({len(all_els)}):')
        for el in all_els:
            if any(k in (el['id'] + el['name'] + el['ariaLabel'] + el['text'] + el['cls']).lower()
                   for k in ['robot', 'noindex', 'index', 'search', 'allow', 'crawl', 'visib']):
                log(f'    RELEVANT: {el}')

        # Check for selects
        all_selects = page.evaluate('''
            () => Array.from(document.querySelectorAll("select")).map(s => ({
                id: s.id, name: s.name,
                options: Array.from(s.options).map(o => o.value + "=" + o.text),
                visible: s.getBoundingClientRect().height > 0,
                value: s.value
            }))
        ''')
        log(f'  All selects: {all_selects}')

    # Scroll sidebar and look for robots select appearing
    log('  Scrolling sidebar to find robots dropdown...')
    for scroll_step in range(8):
        scroll_sidebar(page, 150)

        # Check for robots-related selects
        robots_selects = page.evaluate('''
            () => {
                const all_selects = document.querySelectorAll("select");
                const result = [];
                for (const s of all_selects) {
                    const id = s.id || "";
                    const name = s.getAttribute("name") || "";
                    const cls = s.className || "";
                    if (id.includes("robot") || name.includes("robot") ||
                        id.includes("noindex") || name.includes("noindex") ||
                        id.includes("index") || cls.includes("robot")) {
                        result.push({
                            id: id, name: name,
                            options: Array.from(s.options).map(o => o.value + "=" + o.text),
                            value: s.value,
                            visible: s.getBoundingClientRect().height > 0
                        });
                    }
                }
                return result;
            }
        ''')
        if robots_selects:
            log(f'  Found robots selects at scroll {scroll_step}: {robots_selects}')
            break

        # Also check for button-based robots toggle
        robots_btn = page.evaluate('''
            () => {
                const btns = document.querySelectorAll("button");
                const result = [];
                for (const b of btns) {
                    const txt = (b.innerText || "").toLowerCase();
                    const lbl = (b.getAttribute("aria-label") || "").toLowerCase();
                    if (txt.includes("allow search") || txt.includes("noindex") ||
                        lbl.includes("allow search") || lbl.includes("noindex") ||
                        txt.includes("show this page in search") || txt.includes("search engine")) {
                        result.push({
                            text: b.innerText.slice(0, 60),
                            ariaLabel: b.getAttribute("aria-label") || "",
                            cls: b.className.slice(0, 60),
                            visible: b.getBoundingClientRect().height > 0
                        });
                    }
                }
                return result;
            }
        ''')
        if robots_btn:
            log(f'  Found robots button at scroll {scroll_step}: {robots_btn}')
            break

    ss(page, f'{slug}_03_after_scroll')

    # Final attempt: Find the select by option content ("No" option in robots select)
    robots_select_found = page.evaluate('''
        () => {
            const all_selects = document.querySelectorAll("select");
            for (const s of all_selects) {
                const opts = Array.from(s.options).map(o => o.text.toLowerCase());
                if (opts.some(o => o === "no" || o === "noindex") &&
                    opts.some(o => o === "yes" || o === "index" || o === "default")) {
                    return {
                        id: s.id, name: s.getAttribute("name"),
                        options: Array.from(s.options).map(o => ({v: o.value, t: o.text})),
                        value: s.value
                    };
                }
            }
            return null;
        }
    ''')
    if robots_select_found:
        log(f'  Found robots select by options: {robots_select_found}')
        sel_id = robots_select_found['id']
        sel_name = robots_select_found.get('name', '')
        selector = f'select#{sel_id}' if sel_id else f'select[name="{sel_name}"]'
        sel_el = page.locator(selector).first
        sel_el.select_option(value='2')
        log('  Set to noindex (value=2)')
        time.sleep(1)
        ss(page, f'{slug}_04_noindex_set')
        return True

    log('  Could not find robots select - trying to dump page HTML for analysis')
    # Get the full Yoast sidebar HTML
    yoast_html = page.evaluate('''
        () => {
            const sidebar = document.querySelector(".interface-complementary-area");
            return sidebar ? sidebar.innerHTML.slice(0, 10000) : "NO SIDEBAR";
        }
    ''')
    html_path = f'/tmp/yoast_html_{slug}.html'
    with open(html_path, 'w') as f:
        f.write(yoast_html)
    log(f'  Yoast HTML saved to {html_path}')

    # Search for robots-related patterns in HTML
    for pattern in ['robots', 'noindex', 'index', 'Allow search', 'wpseo-robots']:
        import re as re_module
        hits = [(m.start(), yoast_html[max(0, m.start()-30):m.end()+100])
                for m in re_module.finditer(pattern, yoast_html, re_module.I)]
        if hits:
            log(f'  Pattern "{pattern}" found {len(hits)} times:')
            for pos, ctx in hits[:2]:
                log(f'    {ctx[:200]}')

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


def save_page(page, slug):
    """Click Update/Save button."""
    for sel in ['button.editor-post-publish-button', 'button[aria-label="Update"]',
                'button:has-text("Update")', 'input#publish']:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click()
                time.sleep(5)
                ss(page, f'{slug}_saved')
                log('  Page saved!')
                return True
        except Exception:
            continue
    log('  WARNING: Could not find save button')
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
        log(f'\n=== Processing /{slug}/ (ID={page_id}) ===')

        current = check_robots_via_api(page_id)
        log(f'  Current robots: {current}')

        if 'noindex' in current:
            log('  Already noindexed!')
            results[slug] = 'already_done'
            continue

        page.goto(f'{WP_ADMIN_URL}/post.php?post={page_id}&action=edit',
                  wait_until='domcontentloaded', timeout=60000)
        time.sleep(5)

        success = find_and_set_noindex(page, slug)
        if success:
            save_page(page, slug)
            results[slug] = 'set'
        else:
            results[slug] = 'failed'

    log('\n=== FINAL SUMMARY ===')
    for pid, slug in DEV_PAGES:
        robots = check_robots_via_api(pid)
        log(f'  /{slug}/: result={results.get(slug, "?")} | robots={robots}')

    browser.close()
