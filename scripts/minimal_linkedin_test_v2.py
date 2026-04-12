#!/usr/bin/env python3
"""
Minimal LinkedIn Chromium test v2 - Debug redirect loop.

Traces every request/response to understand the redirect chain.
"""

import sys
import time
import json

def main():
    li_at = sys.argv[1] if len(sys.argv) > 1 else None
    if not li_at:
        print("Usage: python3 minimal_linkedin_test_v2.py <li_at_cookie_value>")
        sys.exit(1)

    print("=" * 60)
    print("MINIMAL CHROMIUM LINKEDIN TEST v2 - REDIRECT DEBUG")
    print("=" * 60)

    from rebrowser_playwright.sync_api import sync_playwright

    pw = sync_playwright().start()

    browser = pw.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
    )
    print(f"Browser version: {browser.version}")

    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        locale='en-US',
        timezone_id='America/New_York',
    )
    page = context.new_page()

    # Track ALL requests and responses
    redirect_log = []

    def on_request(request):
        redirect_log.append({
            'type': 'REQUEST',
            'url': request.url[:120],
            'method': request.method,
            'is_navigation': request.is_navigation_request(),
        })

    def on_response(response):
        redirect_log.append({
            'type': 'RESPONSE',
            'url': response.url[:120],
            'status': response.status,
            'headers_location': response.headers.get('location', '')[:120] if response.status in (301, 302, 303, 307, 308) else '',
        })

    page.on('request', on_request)
    page.on('response', on_response)

    # Step 1: robots.txt for TLS
    print("\n[1] Navigating to robots.txt...")
    page.goto('https://www.linkedin.com/robots.txt', wait_until='domcontentloaded', timeout=30000)
    print(f"  OK - Status landed")

    # Step 2: Inject cookie
    print("\n[2] Injecting li_at cookie...")
    context.add_cookies([{
        'name': 'li_at',
        'value': li_at,
        'domain': '.linkedin.com',
        'path': '/',
        'httpOnly': True,
        'secure': True,
        'sameSite': 'None',
    }])

    # Also add JSESSIONID (sometimes needed)
    context.add_cookies([{
        'name': 'JSESSIONID',
        'value': '"ajax:0000000000000000000"',
        'domain': '.www.linkedin.com',
        'path': '/',
        'httpOnly': False,
        'secure': True,
        'sameSite': 'None',
    }])
    print("  OK - Cookies injected (li_at + JSESSIONID)")

    # Clear redirect log before the important navigation
    redirect_log.clear()

    # Step 3: Try /feed/ with manual redirect following
    print("\n[3] Navigating to linkedin.com/feed/ (tracing redirects)...")
    try:
        resp = page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
        print(f"  Final status: {resp.status}")
        print(f"  Final URL: {page.url}")
    except Exception as e:
        print(f"  ERROR: {e}")
        print(f"  Current URL: {page.url}")

    # Print redirect chain
    print(f"\n--- REDIRECT CHAIN ({len(redirect_log)} events) ---")
    for i, entry in enumerate(redirect_log[:60]):  # First 60 events
        if entry['type'] == 'RESPONSE' and entry.get('status') in (301, 302, 303, 307, 308):
            print(f"  [{i}] {entry['status']} {entry['url']}")
            print(f"       -> {entry['headers_location']}")
        elif entry['type'] == 'RESPONSE' and entry.get('status', 0) >= 400:
            print(f"  [{i}] {entry['status']} {entry['url']}")
        elif entry['type'] == 'REQUEST' and entry.get('is_navigation'):
            print(f"  [{i}] NAV REQUEST: {entry['url']}")

    # Step 4: Try using CDP to navigate and capture network
    print("\n\n[4] Trying alternative: Use page.evaluate to fetch /feed/ via JS...")
    redirect_log.clear()

    fetch_result = page.evaluate('''async () => {
        try {
            const resp = await fetch("https://www.linkedin.com/feed/", {
                method: "GET",
                credentials: "include",
                redirect: "follow",
            });
            return {
                status: resp.status,
                url: resp.url,
                redirected: resp.redirected,
                contentType: resp.headers.get("content-type"),
                bodyLen: (await resp.text()).length,
            };
        } catch(e) {
            return {error: e.message};
        }
    }''')
    print(f"  Fetch result: {json.dumps(fetch_result, indent=2)}")

    # Step 5: Try navigating to linkedin.com homepage first
    print("\n[5] Trying linkedin.com/ (homepage) instead of /feed/...")
    redirect_log.clear()
    try:
        resp = page.goto('https://www.linkedin.com/', wait_until='domcontentloaded', timeout=30000)
        print(f"  Status: {resp.status}")
        print(f"  Final URL: {page.url}")
        title = page.title()
        print(f"  Title: '{title}'")
    except Exception as e:
        print(f"  ERROR: {e}")
        print(f"  Current URL: {page.url}")

    # Print redirect chain for homepage
    print(f"\n--- HOMEPAGE REDIRECT CHAIN ({len(redirect_log)} events) ---")
    for i, entry in enumerate(redirect_log[:40]):
        if entry['type'] == 'RESPONSE' and entry.get('status') in (301, 302, 303, 307, 308):
            print(f"  [{i}] {entry['status']} {entry['url']}")
            print(f"       -> {entry['headers_location']}")
        elif entry['type'] == 'REQUEST' and entry.get('is_navigation'):
            print(f"  [{i}] NAV REQUEST: {entry['url']}")

    # Step 6: Check what cookies exist now
    all_cookies = context.cookies('https://www.linkedin.com')
    print(f"\n--- COOKIES ({len(all_cookies)}) ---")
    for c in sorted(all_cookies, key=lambda x: x['name']):
        print(f"  {c['name']}: {str(c['value'])[:40]}... (domain={c['domain']})")

    # Step 7: Check navigator properties
    print("\n--- NAVIGATOR CHECKS ---")
    checks = page.evaluate('''() => {
        return {
            webdriver: navigator.webdriver,
            languages: navigator.languages,
            platform: navigator.platform,
            hardwareConcurrency: navigator.hardwareConcurrency,
            userAgent: navigator.userAgent.substring(0, 100),
            cookieEnabled: navigator.cookieEnabled,
            doNotTrack: navigator.doNotTrack,
            plugins_length: navigator.plugins.length,
            chrome_defined: typeof window.chrome !== 'undefined',
            chrome_runtime: typeof window.chrome?.runtime !== 'undefined',
        };
    }''')
    for k, v in checks.items():
        print(f"  {k}: {v}")

    context.close()
    browser.close()
    pw.stop()
    print("\nDone.")


if __name__ == '__main__':
    main()
