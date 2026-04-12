#!/usr/bin/env python3
"""
Minimal LinkedIn Chromium test.

NO init scripts.
NO stealth.
NO anti-detection.
NO profile.
NO proxy.

Just: launch chromium -> inject li_at cookie -> navigate to linkedin.com/feed/
"""

import sys
import time
import json

def main():
    li_at = sys.argv[1] if len(sys.argv) > 1 else None
    if not li_at:
        print("Usage: python3 minimal_linkedin_test.py <li_at_cookie_value>")
        sys.exit(1)

    print("=" * 60)
    print("MINIMAL CHROMIUM LINKEDIN TEST")
    print("=" * 60)
    print(f"li_at cookie length: {len(li_at)}")
    print()

    # Step 1: Import rebrowser-playwright
    print("[1/7] Importing rebrowser_playwright...")
    try:
        from rebrowser_playwright.sync_api import sync_playwright
        print("  OK - rebrowser_playwright imported")
    except ImportError:
        print("  FAIL - rebrowser_playwright not found, trying regular playwright")
        from playwright.sync_api import sync_playwright
        print("  OK - regular playwright imported")

    # Step 2: Launch minimal browser
    print("\n[2/7] Launching Chromium (MINIMAL - no stealth, no init scripts)...")
    pw = sync_playwright().start()

    browser = pw.chromium.launch(
        headless=True,
        args=[
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
        ]
    )
    print(f"  OK - Browser launched, version: {browser.version}")

    # Step 3: Create a fresh context (NO init scripts)
    print("\n[3/7] Creating fresh browser context (NO init scripts, NO stealth)...")
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        locale='en-US',
        timezone_id='America/New_York',
    )
    page = context.new_page()
    print("  OK - Context and page created")

    # Step 4: Navigate to robots.txt first (TLS handshake)
    print("\n[4/7] Navigating to linkedin.com/robots.txt (TLS establishment)...")
    try:
        resp = page.goto('https://www.linkedin.com/robots.txt', wait_until='domcontentloaded', timeout=30000)
        print(f"  Status: {resp.status}")
        body_len = len(page.content())
        print(f"  Body length: {body_len}")
        title = page.title()
        print(f"  Title: '{title}'")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Step 5: Inject li_at cookie
    print("\n[5/7] Injecting li_at cookie via context.add_cookies()...")
    context.add_cookies([{
        'name': 'li_at',
        'value': li_at,
        'domain': '.linkedin.com',
        'path': '/',
        'httpOnly': True,
        'secure': True,
        'sameSite': 'None',
    }])
    print("  OK - Cookie injected")

    # Verify cookie was set
    cookies = context.cookies('https://www.linkedin.com')
    li_at_cookies = [c for c in cookies if c['name'] == 'li_at']
    print(f"  Verification: {len(li_at_cookies)} li_at cookie(s) found in context")

    # Step 6: Navigate to feed
    print("\n[6/7] Navigating to linkedin.com/feed/...")
    try:
        resp = page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
        print(f"  HTTP Status: {resp.status}")
        final_url = page.url
        print(f"  Final URL: {final_url}")
    except Exception as e:
        print(f"  Navigation ERROR: {e}")
        final_url = page.url
        print(f"  Current URL after error: {final_url}")

    # Step 7: Wait and inspect
    print("\n[7/7] Waiting 10 seconds for page to render...")
    time.sleep(10)

    print("\n--- PAGE INSPECTION ---")
    final_url = page.url
    title = page.title()
    body_len = page.evaluate('document.body.innerHTML.length')
    scripts_count = page.evaluate('document.scripts.length')
    has_feed = page.evaluate('document.querySelector("[data-id]") !== null || document.querySelector(".feed-shared-update-v2") !== null')

    # Check for common indicators
    is_login_page = page.evaluate('''() => {
        return document.querySelector('input[name="session_key"]') !== null
            || document.querySelector('.login__form') !== null
            || window.location.href.includes('/login')
            || window.location.href.includes('/checkpoint')
    }''')

    is_authwall = page.evaluate('''() => {
        return window.location.href.includes('authwall')
            || document.querySelector('.authwall') !== null
    }''')

    # Get visible text sample
    visible_text = page.evaluate('''() => {
        const el = document.body;
        if (!el) return "NO BODY";
        const text = el.innerText || el.textContent || "";
        return text.substring(0, 500);
    }''')

    # Check navigator.webdriver
    webdriver_flag = page.evaluate('navigator.webdriver')

    print(f"  Final URL: {final_url}")
    print(f"  Page Title: '{title}'")
    print(f"  Body innerHTML length: {body_len}")
    print(f"  Scripts count: {scripts_count}")
    print(f"  Has feed elements: {has_feed}")
    print(f"  Is login page: {is_login_page}")
    print(f"  Is authwall: {is_authwall}")
    print(f"  navigator.webdriver: {webdriver_flag}")
    print(f"\n  Visible text (first 500 chars):")
    print(f"  ---")
    for line in visible_text.split('\n')[:20]:
        stripped = line.strip()
        if stripped:
            print(f"    {stripped}")
    print(f"  ---")

    # Check all cookies after navigation
    all_cookies = context.cookies('https://www.linkedin.com')
    cookie_names = [c['name'] for c in all_cookies]
    print(f"\n  Cookies after navigation: {len(all_cookies)} total")
    print(f"  Cookie names: {', '.join(sorted(set(cookie_names)))}")

    # Take a screenshot for analysis
    screenshot_path = '/tmp/linkedin_minimal_test.png'
    page.screenshot(path=screenshot_path, full_page=False)
    print(f"\n  Screenshot saved: {screenshot_path}")

    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSIS:")
    if '/feed' in final_url and not is_login_page and not is_authwall:
        print("  RESULT: SUCCESS - Landed on feed page")
        if has_feed:
            print("  Feed content detected - session is valid")
        else:
            print("  WARNING: On feed URL but no feed elements detected")
    elif is_authwall:
        print("  RESULT: BLOCKED - Hit authwall (cookie not accepted)")
    elif is_login_page:
        print("  RESULT: BLOCKED - Redirected to login (cookie expired or rejected)")
    elif '/checkpoint' in final_url:
        print("  RESULT: BLOCKED - Hit checkpoint/challenge")
    else:
        print(f"  RESULT: UNKNOWN - Ended up at {final_url}")
    print("=" * 60)

    # Cleanup
    context.close()
    browser.close()
    pw.stop()
    print("\nBrowser closed. Test complete.")


if __name__ == '__main__':
    main()
