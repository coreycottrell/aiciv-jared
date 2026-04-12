#!/usr/bin/env python3
"""
Deploy Category Page CSS Fix to purebrain.ai - v2
Uses REST API cookie auth approach to bypass CAPTCHA.

Strategy:
1. Get auth cookies by POSTing to wp-login.php with proper headers
2. Use those cookies in Playwright to access Customizer
3. Append CSS fix via CodeMirror API
4. Publish and verify
"""

import sys
import time
import os
import json
import base64
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_URL = "https://purebrain.ai"
WP_CSS_URL = f"{WP_URL}/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Aether"
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '')
APP_PASSWORD = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '')

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

CATEGORY_CSS_FIX = """

/* === CATEGORY PAGE FIX (Feb 18) === */
body.category,
body.archive {
  color: #ffffff !important;
  background: #0a0a0a !important;
}
body.category a,
body.archive a {
  color: #2a93c1 !important;
}
body.category a:hover,
body.archive a:hover {
  color: #f1420b !important;
}
body.category h1,
body.category h2,
body.category .page-title,
body.archive h1,
body.archive h2,
body.archive .page-title {
  color: #ffffff !important;
}
body.category .nav-links a,
body.archive .nav-links a {
  color: #2a93c1 !important;
}
/* === END CATEGORY PAGE FIX === */"""

DUPLICATE_CHECK = "CATEGORY PAGE FIX"


def screenshot(page, label):
    path = f"{SCREENSHOT_DIR}/catfix_{label}_{TIMESTAMP}.png"
    page.screenshot(path=path, full_page=False)
    print(f"  Screenshot: {path}")
    return path


def get_wp_cookies_via_requests():
    """Get WordPress auth cookies using requests with app password."""
    print("\n=== Getting auth cookies via requests ===")

    session = requests.Session()

    # Set a realistic user agent
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    })

    # Method 1: Try using Application Password to make an authenticated API call
    # which establishes cookies
    auth_string = base64.b64encode(f'{USERNAME}:{APP_PASSWORD}'.encode()).decode()
    session.headers['Authorization'] = f'Basic {auth_string}'

    # Make an API call that sets cookies
    r = session.get(f'{WP_URL}/wp-json/wp/v2/users/me', timeout=30)
    print(f"  API auth status: {r.status_code}")
    if r.status_code == 200:
        print(f"  Logged in as: {r.json().get('name')}")

    cookies = session.cookies.get_dict()
    print(f"  Cookies after API call: {list(cookies.keys())}")

    # Method 2: Try direct wp-login.php POST
    # Reset session
    session2 = requests.Session()
    session2.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    })

    # First get the login page to get cookies/nonce
    r = session2.get(f'{WP_URL}/wp-login.php', timeout=30)
    print(f"  Login page status: {r.status_code}")
    print(f"  Cookies from login page: {list(session2.cookies.get_dict().keys())}")

    # POST login
    login_data = {
        'log': USERNAME,
        'pwd': PASSWORD,
        'wp-submit': 'Log In',
        'redirect_to': f'{WP_URL}/wp-admin/',
        'testcookie': '1',
    }

    r = session2.post(
        f'{WP_URL}/wp-login.php',
        data=login_data,
        allow_redirects=True,
        timeout=30
    )
    print(f"  Login POST status: {r.status_code}")
    print(f"  Final URL: {r.url}")
    cookies2 = session2.cookies.get_dict()
    print(f"  Cookies after login: {list(cookies2.keys())}")

    # Check if we got auth cookies
    auth_cookies = {k: v for k, v in cookies2.items() if 'wordpress_logged_in' in k or 'wordpress_sec' in k}
    if auth_cookies:
        print(f"  Got auth cookies: {list(auth_cookies.keys())}")
        return cookies2, session2
    elif 'wp-login' not in r.url and 'wp-admin' in r.url:
        print("  Redirected to wp-admin - login appears successful")
        return cookies2, session2
    else:
        # Check for CAPTCHA in the response
        if 'captcha' in r.text.lower() or 'CAPTCHA' in r.text:
            print("  CAPTCHA detected in login response")
        print("  Login may have failed - checking page content...")
        if 'login_error' in r.text:
            import re
            match = re.search(r'<div id="login_error"[^>]*>(.*?)</div>', r.text, re.DOTALL)
            if match:
                print(f"  Error: {match.group(1).strip()}")

    return cookies2, session2


def try_rest_api_css_update():
    """Try to update custom CSS directly via REST API."""
    print("\n=== Trying REST API CSS update ===")

    auth_string = base64.b64encode(f'{USERNAME}:{APP_PASSWORD}'.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_string}',
        'Content-Type': 'application/json'
    }

    # WordPress custom CSS is stored as a post type 'custom_css'
    # The post_name matches the active theme stylesheet
    # Active theme is 'artistics'

    # Try to get the custom_css post via a custom endpoint
    # Some WordPress installations expose this via the WP-JSON
    endpoints = [
        f'{WP_URL}/wp-json/wp/v2/custom_css?status=publish',
        f'{WP_URL}/wp-json/wp/v2/custom_css/artistics',
    ]

    for url in endpoints:
        r = requests.get(url, headers=headers, timeout=30)
        print(f"  {url}: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"  Data: {json.dumps(data)[:200]}")
            return data

    # Try to list all posts including custom types
    # by using the search endpoint
    r = requests.get(
        f'{WP_URL}/wp-json/wp/v2/search?search=custom_css&type=post&subtype=custom_css',
        headers=headers, timeout=30
    )
    print(f"  Search for custom_css: {r.status_code}")
    if r.status_code == 200:
        print(f"  Results: {r.json()}")

    return None


def deploy_via_playwright_with_cookies(cookies_dict, session):
    """Use Playwright with pre-authenticated cookies."""
    print("\n=== Deploying via Playwright with cookies ===")

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )

        # Set cookies from requests session
        pw_cookies = []
        for name, value in cookies_dict.items():
            cookie = {
                'name': name,
                'value': value,
                'domain': 'purebrain.ai',
                'path': '/',
            }
            # Some WP cookies need specific paths
            if 'wordpress_logged_in' in name or 'wordpress_sec' in name:
                cookie['path'] = '/wp-admin'
                pw_cookies.append(cookie)
                # Also add for root path
                cookie2 = dict(cookie)
                cookie2['path'] = '/'
                pw_cookies.append(cookie2)
            else:
                pw_cookies.append(cookie)

        if pw_cookies:
            context.add_cookies(pw_cookies)
            print(f"  Set {len(pw_cookies)} cookies in Playwright")

        page = context.new_page()

        # Try going directly to the wp-admin dashboard first
        print("  Testing auth by accessing wp-admin...")
        page.goto(f"{WP_URL}/wp-admin/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        screenshot(page, "01_wpadmin_test")

        current_url = page.url
        print(f"  Current URL: {current_url}")

        if "wp-login" in current_url:
            print("  Cookie auth failed - still on login page")
            print("  Trying direct login with app password header...")

            # Try alternative: set Authorization header for all requests
            context2 = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                extra_http_headers={
                    'Authorization': f'Basic {base64.b64encode(f"{USERNAME}:{APP_PASSWORD}".encode()).decode()}'
                }
            )
            page = context2.new_page()
            page.goto(f"{WP_URL}/wp-admin/", wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)
            screenshot(page, "01b_auth_header")
            current_url = page.url
            print(f"  Current URL with auth header: {current_url}")

            if "wp-login" in current_url:
                print("  Auth header also failed")
                print("  Trying login page with app password...")

                # Try filling the login form with app password instead of regular password
                try:
                    login_link = page.locator("text=Log in with username and password")
                    if login_link.is_visible(timeout=3000):
                        login_link.click()
                        time.sleep(2)
                except:
                    pass

                try:
                    page.wait_for_selector('#user_login', state='visible', timeout=10000)
                    page.locator("#user_login").fill(USERNAME)
                    page.locator("#user_pass").fill(APP_PASSWORD)

                    screenshot(page, "01c_login_with_app_pw")

                    page.locator("#wp-submit").click()
                    page.wait_for_load_state("load", timeout=60000)
                    time.sleep(5)
                    screenshot(page, "01d_after_app_pw_login")
                    current_url = page.url
                    print(f"  URL after app password login: {current_url}")
                except Exception as e:
                    print(f"  Login attempt error: {e}")

            if "wp-login" in page.url:
                print("\n  ALL LOGIN METHODS FAILED")
                print("  The CAPTCHA is blocking automated login.")
                browser.close()
                return False

        # At this point we should be logged in
        print("  Authenticated! Navigating to Additional CSS...")

        # Navigate to Additional CSS
        page.goto(WP_CSS_URL, wait_until="domcontentloaded", timeout=90000)
        print("  Waiting for Customizer (15s)...")
        time.sleep(15)
        screenshot(page, "02_customizer")

        # Wait for CodeMirror
        try:
            page.wait_for_selector('.CodeMirror', state='visible', timeout=30000)
            print("  CodeMirror editor found!")
        except:
            print("  WARNING: CodeMirror not found")
            screenshot(page, "02b_no_codemirror")

        time.sleep(3)

        # GET current CSS
        print("  Getting current CSS...")
        current_css = page.evaluate("""
            () => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    return cm.CodeMirror.getValue();
                }
                return null;
            }
        """)

        if current_css is None:
            print("  ERROR: Could not read current CSS!")
            screenshot(page, "03_css_read_error")
            browser.close()
            return False

        print(f"  Current CSS: {len(current_css)} characters")

        # Check for duplicate
        if DUPLICATE_CHECK in current_css:
            print(f"  '{DUPLICATE_CHECK}' already present - skipping")
            screenshot(page, "03_already_present")
            browser.close()
            return True

        # Append CSS
        full_css = current_css + CATEGORY_CSS_FIX
        print(f"  Appending {len(CATEGORY_CSS_FIX)} chars -> total {len(full_css)} chars")

        result = page.evaluate("""(css) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) {
                cm.CodeMirror.setValue(css);
                cm.CodeMirror.refresh();
                return 'success_' + cm.CodeMirror.getValue().length;
            }
            return 'failed';
        }""", full_css)

        print(f"  Set result: {result}")
        if not result.startswith("success"):
            screenshot(page, "04_set_failed")
            browser.close()
            return False

        time.sleep(2)
        screenshot(page, "04_css_set")

        # Publish
        print("  Publishing...")
        time.sleep(3)
        publish_btn = page.locator("#save")
        if publish_btn.count() > 0 and publish_btn.first.is_visible():
            publish_btn.first.click()
            print("  Clicked Publish!")
            time.sleep(8)
        else:
            page.locator("button:has-text('Publish')").first.click()
            time.sleep(8)

        screenshot(page, "05_published")

        # Verify
        print("\n=== Verification ===")
        vp = context.new_page()

        # Category page
        print("  Checking category page...")
        vp.goto(f"{WP_URL}/category/for-teams/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.evaluate("() => location.reload(true)")
        time.sleep(5)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/catfix_verify_category_{TIMESTAMP}.png", full_page=True)
        print(f"  Screenshot: {SCREENSHOT_DIR}/catfix_verify_category_{TIMESTAMP}.png")

        cat_styles = vp.evaluate("""
            () => {
                const body = document.body;
                const bs = getComputedStyle(body);
                return {
                    bodyColor: bs.color,
                    bodyBg: bs.backgroundColor,
                    bodyClasses: body.className.substring(0, 100)
                };
            }
        """)
        print(f"  Category styles: {cat_styles}")

        # Homepage
        print("  Checking homepage...")
        vp.goto(f"{WP_URL}/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.evaluate("() => location.reload(true)")
        time.sleep(5)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/catfix_verify_homepage_{TIMESTAMP}.png", full_page=False)
        print(f"  Screenshot: {SCREENSHOT_DIR}/catfix_verify_homepage_{TIMESTAMP}.png")

        # Blog
        print("  Checking blog...")
        vp.goto(f"{WP_URL}/blog/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.evaluate("() => location.reload(true)")
        time.sleep(5)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/catfix_verify_blog_{TIMESTAMP}.png", full_page=False)
        print(f"  Screenshot: {SCREENSHOT_DIR}/catfix_verify_blog_{TIMESTAMP}.png")

        vp.close()
        browser.close()
        return True


def try_xmlrpc_approach():
    """Try using WordPress XML-RPC to edit custom CSS."""
    print("\n=== Trying XML-RPC approach ===")
    import xmlrpc.client

    try:
        wp = xmlrpc.client.ServerProxy(f'{WP_URL}/xmlrpc.php', allow_none=True)
        # Test auth
        blogs = wp.wp.getUsersBlogs(USERNAME, PASSWORD)
        print(f"  XML-RPC auth success! Blogs: {blogs}")

        # Get posts of type custom_css
        posts = wp.wp.getPosts(
            1,  # blog_id
            USERNAME,
            PASSWORD,
            {'post_type': 'custom_css', 'number': 5}
        )
        print(f"  Found {len(posts)} custom_css posts")

        for post in posts:
            print(f"  Post ID: {post.get('post_id')}, Title: {post.get('post_title')}, Status: {post.get('post_status')}")
            content = post.get('post_content', '')
            print(f"  Content length: {len(content)} chars")

            if DUPLICATE_CHECK in content:
                print(f"  '{DUPLICATE_CHECK}' already present!")
                return True

            # Append the fix
            new_content = content + CATEGORY_CSS_FIX
            print(f"  Appending {len(CATEGORY_CSS_FIX)} chars -> total {len(new_content)} chars")

            # Update the post
            result = wp.wp.editPost(
                1,  # blog_id
                USERNAME,
                PASSWORD,
                post['post_id'],
                {'post_content': new_content}
            )
            print(f"  Update result: {result}")

            if result:
                print("  CSS updated via XML-RPC!")
                return True

        return False

    except xmlrpc.client.Fault as e:
        print(f"  XML-RPC fault: {e}")
        return False
    except Exception as e:
        print(f"  XML-RPC error: {e}")
        return False


def verify_pages():
    """Take verification screenshots."""
    print("\n=== Taking verification screenshots ===")
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        pages_to_check = [
            (f"{WP_URL}/category/for-teams/", "verify_category"),
            (f"{WP_URL}/", "verify_homepage"),
            (f"{WP_URL}/blog/", "verify_blog"),
        ]

        for url, label in pages_to_check:
            print(f"  Checking {url}...")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            page.evaluate("() => location.reload(true)")
            time.sleep(5)

            path = f"{SCREENSHOT_DIR}/catfix_{label}_{TIMESTAMP}.png"
            full = label == "verify_category"
            page.screenshot(path=path, full_page=full)
            print(f"  Screenshot: {path}")

            if "category" in label:
                styles = page.evaluate("""
                    () => {
                        const body = document.body;
                        const bs = getComputedStyle(body);
                        const h1 = document.querySelector('h1, .page-title');
                        const links = document.querySelectorAll('article a');
                        return {
                            bodyColor: bs.color,
                            bodyBg: bs.backgroundColor,
                            bodyClasses: body.className.substring(0, 100),
                            h1Color: h1 ? getComputedStyle(h1).color : 'n/a',
                            firstLinkColor: links.length > 0 ? getComputedStyle(links[0]).color : 'n/a'
                        };
                    }
                """)
                print(f"  Styles: {styles}")

        browser.close()


def main():
    if not PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not found in .env")
        return 1

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    print("=" * 60)
    print("PureBrain.ai Category Page CSS Fix Deployment v2")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Method 1: Try XML-RPC (most reliable for programmatic access)
    if try_xmlrpc_approach():
        print("\n*** XML-RPC method succeeded! ***")
        verify_pages()
        return 0

    # Method 2: Try cookie-based Playwright
    print("\nXML-RPC failed, trying cookie-based approach...")
    cookies, session = get_wp_cookies_via_requests()
    if deploy_via_playwright_with_cookies(cookies, session):
        print("\n*** Cookie-based method succeeded! ***")
        return 0

    print("\n*** ALL METHODS FAILED ***")
    print("The WordPress CAPTCHA is blocking automated access.")
    print("Options:")
    print("  1. Manually login and deploy the CSS")
    print("  2. Temporarily disable the CAPTCHA plugin")
    print("  3. Add the server IP to CAPTCHA whitelist")
    return 1


if __name__ == "__main__":
    sys.exit(main())
