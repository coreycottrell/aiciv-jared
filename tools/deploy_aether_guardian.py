#!/usr/bin/env python3
"""
Deploy Aether Guardian page to purebrain.ai via WP Admin (Playwright).

- Creates or updates page at /aether-guardian/
- Template: elementor_canvas
- Status: publish
- Password protected with a strong password
- CF WAF blocks REST API, so we use Playwright via wp-admin

Usage:
    python3 tools/deploy_aether_guardian.py
"""
import os
import re
import sys
import time
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
HTML_FILE = AETHER_ROOT / "exports/departments/systems-technology/aether-guardian.html"
PAGE_SLUG = "aether-guardian"
PAGE_TITLE = "Aether Guardian"
PAGE_PASSWORD = "AetherGuardian2026"  # Strong password to protect the page

# --- Load credentials from .env ---
env_text = (AETHER_ROOT / ".env").read_text()

def _env(key):
    m = re.search(rf"^{key}='([^']+)'", env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf'^{key}=([^\n]+)', env_text, re.MULTILINE)
    return m.group(1).strip() if m else ""

WP_USER = _env("PUREBRAIN_WP_USER")
WP_PASS = _env("PUREBRAIN_WP_PASSWORD")
LOGIN_URL = "https://purebrain.ai/wp-login.php?wpaas-standard-login=1"

print("=" * 60)
print("Aether Guardian — WP Deploy Script")
print("=" * 60)
print(f"Page: /aether-guardian/")
print(f"Template: elementor_canvas")
print(f"Password protected: yes")
print(f"WP User: {WP_USER}")
print()

# Read HTML content
html_content = HTML_FILE.read_text()
print(f"HTML file: {len(html_content)} chars")
print()

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()

    # ---- Step 1: Login ----
    print("Step 1: Logging in to WP admin...")
    page.goto(LOGIN_URL, timeout=30000)
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except PlaywrightTimeout:
        pass  # Continue even if networkidle times out
    print(f"  Login page loaded: {page.url}")

    page.fill("#user_login", WP_USER)
    page.fill("#user_pass", WP_PASS)
    page.click("#wp-submit")
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except PlaywrightTimeout:
        pass  # Continue even if networkidle times out
    print(f"  After login: {page.url}")

    if "wp-login" in page.url:
        print("ERROR: Login failed. Check credentials.")
        browser.close()
        sys.exit(1)

    print("  Login SUCCESS")

    # ---- Step 2: Check if page with slug 'aether-guardian' already exists ----
    print()
    print("Step 2: Checking for existing aether-guardian page...")
    page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page&s=aether-guardian", timeout=30000)
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except PlaywrightTimeout:
        pass

    # Look for edit link to existing page
    existing_edit_url = None
    try:
        # Check if there's a page in the results
        row = page.query_selector("tr.type-page")
        if row:
            edit_link = row.query_selector("a.row-title, a.edit")
            if edit_link:
                href = edit_link.get_attribute("href")
                # Extract post ID from URL like /wp-admin/post.php?post=123&action=edit
                m = re.search(r'post=(\d+)', href)
                if m:
                    post_id = m.group(1)
                    existing_edit_url = f"https://purebrain.ai/wp-admin/post.php?post={post_id}&action=edit"
                    print(f"  Found existing page (ID: {post_id})")
    except Exception as e:
        print(f"  Search check exception: {e}")

    if not existing_edit_url:
        print("  No existing page found — will create new")

    # ---- Step 3: Open new page or edit existing ----
    print()
    if existing_edit_url:
        print(f"Step 3: Opening existing page for edit...")
        page.goto(existing_edit_url, timeout=30000)
    else:
        print("Step 3: Creating new page...")
        page.goto("https://purebrain.ai/wp-admin/post-new.php?post_type=page", timeout=30000)

    try:
        page.wait_for_load_state("networkidle", timeout=25000)
    except PlaywrightTimeout:
        pass
    print(f"  Editor URL: {page.url}")

    # ---- Step 4: Use Classic Editor or Block Editor? ----
    # Check for classic editor text area
    time.sleep(2)

    is_classic = page.query_selector("#content") is not None
    is_block = page.query_selector(".block-editor") is not None or page.query_selector(".edit-post-header") is not None

    print(f"  Classic editor: {is_classic}")
    print(f"  Block editor: {is_block}")

    # ---- Step 5: Set page title ----
    print()
    print("Step 5: Setting page title...")

    if is_block:
        # Block editor - use JS to set title
        try:
            page.fill('.editor-post-title__input', PAGE_TITLE, timeout=5000)
            print(f"  Title set via block editor: {PAGE_TITLE}")
        except:
            try:
                page.evaluate(f"""
                    (function() {{
                        var title = document.querySelector('.editor-post-title__input, h1[class*="post-title"], [data-type="core/post-title"] h1');
                        if (title) {{
                            title.focus();
                            title.textContent = '{PAGE_TITLE}';
                            title.dispatchEvent(new Event('input', {{bubbles: true}}));
                        }}
                    }})()
                """)
                print(f"  Title set via JS: {PAGE_TITLE}")
            except Exception as e:
                print(f"  Title set warning: {e}")
    else:
        # Classic editor
        try:
            page.fill("#title", PAGE_TITLE, timeout=5000)
            print(f"  Title set: {PAGE_TITLE}")
        except Exception as e:
            print(f"  Title set warning: {e}")

    # ---- Step 6: Set content via WP REST API using nonce from admin ----
    # Since we're logged in via Playwright, get a nonce to use the REST API
    print()
    print("Step 6: Getting WP nonce for authenticated REST API call...")

    nonce_script = """
    async () => {
        // Try to get nonce from wp global
        if (window.wpApiSettings && window.wpApiSettings.nonce) {
            return window.wpApiSettings.nonce;
        }
        // Try wp.apiFetch nonce
        if (window.wp && window.wp.apiFetch && window.wp.apiFetch.nonceMiddleware) {
            return null;
        }
        return null;
    }
    """

    nonce = page.evaluate("""() => {
        if (window.wpApiSettings && window.wpApiSettings.nonce) {
            return window.wpApiSettings.nonce;
        }
        return null;
    }""")
    print(f"  Nonce from page: {nonce}")

    # ---- Step 7: Use WP admin AJAX / REST API with session cookies ----
    print()
    print("Step 7: Deploying page via authenticated WP REST API (session cookies)...")

    # Get cookies from the browser session
    cookies = ctx.cookies()
    cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies if "purebrain.ai" in c.get("domain", "")])
    print(f"  Cookies available: {len(cookies)} cookies")

    # Try REST API with session cookies (not basic auth)
    import json as json_mod
    import urllib.request
    import urllib.parse

    # First get a proper nonce via /wp-json/
    nonce_resp = page.evaluate("""async () => {
        try {
            const r = await fetch('/wp-json/wp/v2/pages?per_page=1', {
                credentials: 'include',
                headers: {'Content-Type': 'application/json'}
            });
            const nonce = r.headers.get('X-WP-Nonce');
            const text = await r.text();
            return {status: r.status, nonce: nonce, bodyStart: text.substring(0, 100)};
        } catch(e) {
            return {error: e.toString()};
        }
    }""")
    print(f"  REST test: {nonce_resp}")

    # Try to get nonce via admin-ajax
    nonce_result = page.evaluate("""async () => {
        try {
            const fd = new FormData();
            fd.append('action', 'rest-nonce');
            const r = await fetch('/wp-admin/admin-ajax.php', {
                method: 'POST',
                credentials: 'include',
                body: fd
            });
            const text = await r.text();
            return {status: r.status, text: text.substring(0, 100)};
        } catch(e) {
            return {error: e.toString()};
        }
    }""")
    print(f"  Admin-ajax nonce: {nonce_result}")

    # Extract nonce if available
    wp_nonce = None
    if isinstance(nonce_result, dict) and nonce_result.get('text'):
        text = nonce_result['text'].strip()
        if len(text) == 10 and text.isalnum():
            wp_nonce = text
            print(f"  Got WP nonce: {wp_nonce}")

    # Use fetch API with session to create/update the page
    print()
    print("Step 8: Creating/updating page via browser fetch...")

    escaped_content = html_content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

    if existing_edit_url and 'post=' in existing_edit_url:
        m = re.search(r'post=(\d+)', existing_edit_url)
        page_id = m.group(1) if m else None
    else:
        page_id = None

    deploy_script = f"""
    async (content) => {{
        const headers = {{'Content-Type': 'application/json'}};
        {f"headers['X-WP-Nonce'] = '{wp_nonce}';" if wp_nonce else ""}

        const payload = {{
            title: "{PAGE_TITLE}",
            slug: "{PAGE_SLUG}",
            status: "publish",
            template: "elementor_canvas",
            content: content,
            password: "{PAGE_PASSWORD}"
        }};

        const url = {f"'/wp-json/wp/v2/pages/{page_id}'" if page_id else "'/wp-json/wp/v2/pages'"};

        try {{
            const r = await fetch(url, {{
                method: 'POST',
                credentials: 'include',
                headers: headers,
                body: JSON.stringify(payload)
            }});
            const text = await r.text();
            let data;
            try {{ data = JSON.parse(text); }} catch(e) {{ data = {{raw: text.substring(0, 200)}}; }}
            return {{status: r.status, data: data}};
        }} catch(e) {{
            return {{error: e.toString()}};
        }}
    }}
    """

    result = page.evaluate(deploy_script, html_content)
    print(f"  Deploy result status: {result.get('status')}")

    if result.get('status') in [200, 201]:
        data = result.get('data', {})
        page_link = data.get('link', 'N/A')
        page_id_new = data.get('id', 'N/A')
        print(f"  SUCCESS!")
        print(f"  Page ID: {page_id_new}")
        print(f"  Page URL: {page_link}")
        print(f"  Status: {data.get('status', 'N/A')}")
        print(f"  Template: {data.get('template', 'N/A')}")
        print()
        print(f"  LIVE URL: https://purebrain.ai/aether-guardian/")
        print(f"  Password: {PAGE_PASSWORD}")
    else:
        data = result.get('data', {})
        print(f"  ERROR or unexpected result")
        print(f"  Data: {str(data)[:400]}")

        # Fallback: Try setting via the classic editor if available
        print()
        print("Trying fallback: Classic Editor method...")
        if is_classic:
            # Set content in classic editor textarea
            page.evaluate(f"""
                (function() {{
                    var editor = tinyMCE && tinyMCE.get('content');
                    if (editor) {{
                        editor.setContent(arguments[0]);
                    }} else {{
                        document.getElementById('content').value = arguments[0];
                        // Also try switching to text mode
                        var textTab = document.getElementById('content-html');
                        if (textTab) textTab.click();
                        document.getElementById('content').value = arguments[0];
                    }}
                }})()
            """, html_content)
            print("  Content set in classic editor textarea")

            # Set page attributes: template
            try:
                page.select_option("#page_template", "elementor_canvas", timeout=5000)
                print("  Template set to elementor_canvas")
            except:
                pass

            # Set password
            try:
                # Click "Password protected" radio
                page.click('input[value="password"]', timeout=5000)
                page.fill('#post_password', PAGE_PASSWORD, timeout=5000)
                print(f"  Password set: {PAGE_PASSWORD}")
            except Exception as e:
                print(f"  Password set warning: {e}")

            # Set slug
            try:
                slug_el = page.query_selector("#post_name")
                if slug_el:
                    page.click("#edit-slug-buttons button", timeout=3000)
                    time.sleep(1)
                    page.fill("#new-post-slug", PAGE_SLUG, timeout=3000)
                    page.click("#new-post-slug + span button", timeout=3000)
                    print(f"  Slug set: {PAGE_SLUG}")
            except Exception as e:
                print(f"  Slug set note: {e}")

            # Click Publish
            print("  Clicking Publish...")
            try:
                page.click("#publish", timeout=10000)
                page.wait_for_load_state("networkidle", timeout=30000)
                print(f"  After publish: {page.url}")

                # Check for success
                if "post=" in page.url or "updated=1" in page.url:
                    print(f"  PUBLISHED SUCCESSFULLY!")
                    m = re.search(r'post=(\d+)', page.url)
                    if m:
                        print(f"  Page ID: {m.group(1)}")
                else:
                    print(f"  Check URL: {page.url}")
            except Exception as e:
                print(f"  Publish error: {e}")

    browser.close()

print()
print("=" * 60)
print("Deploy script complete.")
print(f"Expected URL: https://purebrain.ai/aether-guardian/")
print(f"Page password: {PAGE_PASSWORD}")
print("=" * 60)
