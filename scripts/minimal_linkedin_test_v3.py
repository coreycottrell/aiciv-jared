#!/usr/bin/env python3
"""
Minimal LinkedIn test v3 - Capture Set-Cookie headers from 302 responses.
"""

import sys
import time
import json

def main():
    li_at = sys.argv[1] if len(sys.argv) > 1 else None
    if not li_at:
        print("Usage: python3 minimal_linkedin_test_v3.py <li_at_cookie_value>")
        sys.exit(1)

    print("=" * 60)
    print("MINIMAL CHROMIUM LINKEDIN TEST v3 - COOKIE HEADER DEBUG")
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

    # Use CDP to intercept network at a lower level
    cdp = context.new_cdp_session(page)

    request_log = []
    response_log = []

    def on_request_will_be_sent(params):
        req_id = params.get('requestId', '')
        url = params.get('request', {}).get('url', '')
        headers = params.get('request', {}).get('headers', {})
        request_log.append({
            'id': req_id,
            'url': url[:150],
            'cookie_header': headers.get('cookie', headers.get('Cookie', ''))[:200],
        })

    def on_response_received(params):
        resp = params.get('response', {})
        url = resp.get('url', '')
        status = resp.get('status', 0)
        headers = resp.get('headers', {})
        # Collect Set-Cookie headers
        set_cookies = headers.get('set-cookie', headers.get('Set-Cookie', ''))
        response_log.append({
            'url': url[:150],
            'status': status,
            'set_cookie': set_cookies[:500] if set_cookies else '',
            'location': headers.get('location', headers.get('Location', '')),
        })

    cdp.on('Network.requestWillBeSent', on_request_will_be_sent)
    cdp.on('Network.responseReceived', on_response_received)
    cdp.send('Network.enable')

    # Step 1: robots.txt
    print("\n[1] robots.txt for TLS...")
    page.goto('https://www.linkedin.com/robots.txt', wait_until='domcontentloaded', timeout=30000)
    print("  OK")

    # Check what cookies LinkedIn set from robots.txt
    cookies_after_robots = context.cookies('https://www.linkedin.com')
    print(f"\n  Cookies after robots.txt ({len(cookies_after_robots)}):")
    for c in sorted(cookies_after_robots, key=lambda x: x['name']):
        print(f"    {c['name']}: {str(c['value'])[:50]}... (domain={c['domain']}, path={c['path']})")

    # Step 2: Inject li_at
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

    # Also inject JSESSIONID
    context.add_cookies([{
        'name': 'JSESSIONID',
        'value': '"ajax:0000000000000000000"',
        'domain': '.www.linkedin.com',
        'path': '/',
        'httpOnly': False,
        'secure': True,
        'sameSite': 'None',
    }])
    print("  OK")

    # Verify all cookies before navigation
    cookies_before = context.cookies('https://www.linkedin.com')
    print(f"\n  Cookies before /feed/ navigation ({len(cookies_before)}):")
    for c in sorted(cookies_before, key=lambda x: x['name']):
        print(f"    {c['name']}: {str(c['value'])[:50]}... (domain={c['domain']}, secure={c['secure']}, sameSite={c.get('sameSite','')}, httpOnly={c['httpOnly']})")

    # Clear logs
    request_log.clear()
    response_log.clear()

    # Step 3: Navigate to /feed/ - will fail but we capture data
    print("\n[3] Navigating to /feed/ (expecting redirect loop - capturing data)...")
    try:
        resp = page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=15000)
        print(f"  Unexpected success! Status: {resp.status}, URL: {page.url}")
    except Exception as e:
        print(f"  Expected error: {str(e)[:80]}")

    # Analyze the redirect loop
    print(f"\n--- REQUEST LOG (first 5 of {len(request_log)}) ---")
    for i, req in enumerate(request_log[:5]):
        print(f"\n  Request #{i}:")
        print(f"    URL: {req['url']}")
        print(f"    Cookies sent: {req['cookie_header'][:200] if req['cookie_header'] else 'NONE'}")

    print(f"\n--- RESPONSE LOG (first 5 of {len(response_log)}) ---")
    for i, resp in enumerate(response_log[:5]):
        if resp['status'] in (301, 302, 303, 307, 308) or resp['url'].find('feed') >= 0:
            print(f"\n  Response #{i}:")
            print(f"    URL: {resp['url']}")
            print(f"    Status: {resp['status']}")
            print(f"    Location: {resp['location']}")
            if resp['set_cookie']:
                print(f"    Set-Cookie: {resp['set_cookie'][:300]}")
            else:
                print(f"    Set-Cookie: NONE")

    # Step 4: Try with curl-like approach using CDP Fetch
    print("\n\n[4] Trying CDP Fetch.enable to intercept first redirect...")
    cdp.send('Fetch.enable', {
        'patterns': [{'urlPattern': '*linkedin.com/feed*', 'requestStage': 'Response'}]
    })

    intercepted = []
    def on_request_paused(params):
        req_id = params.get('requestId')
        status = params.get('responseStatusCode', 0)
        headers = params.get('responseHeaders', [])
        url = params.get('request', {}).get('url', '')
        set_cookie_headers = [h['value'] for h in headers if h['name'].lower() == 'set-cookie']
        location_headers = [h['value'] for h in headers if h['name'].lower() == 'location']
        cookie_sent = ''
        for h in params.get('request', {}).get('headers', {}).items() if isinstance(params.get('request', {}).get('headers'), dict) else []:
            if h[0].lower() == 'cookie':
                cookie_sent = h[1][:200]

        intercepted.append({
            'url': url[:150],
            'status': status,
            'set_cookies': set_cookie_headers,
            'location': location_headers,
            'cookies_sent': cookie_sent,
        })

        # Continue the request (don't block)
        try:
            cdp.send('Fetch.continueResponse', {'requestId': req_id})
        except:
            try:
                cdp.send('Fetch.continueRequest', {'requestId': req_id})
            except:
                pass

    cdp.on('Fetch.requestPaused', on_request_paused)

    # Navigate again
    try:
        page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=10000)
    except:
        pass

    print(f"\n--- INTERCEPTED RESPONSES ({len(intercepted)}) ---")
    for i, inter in enumerate(intercepted[:5]):
        print(f"\n  Intercept #{i}:")
        print(f"    URL: {inter['url']}")
        print(f"    Status: {inter['status']}")
        print(f"    Location: {inter['location']}")
        print(f"    Set-Cookie count: {len(inter['set_cookies'])}")
        for sc in inter['set_cookies'][:3]:
            print(f"      {sc[:150]}")
        print(f"    Cookies sent: {inter['cookies_sent'][:200] if inter['cookies_sent'] else 'unknown'}")

    # Step 5: Try with curl directly to compare
    print("\n\n[5] Comparing with curl (same cookie)...")
    import subprocess
    curl_result = subprocess.run([
        'curl', '-s', '-o', '/dev/null',
        '-w', 'HTTP %{http_code} -> %{redirect_url}\nFinal URL: %{url_effective}\n',
        '-b', f'li_at={li_at}',
        '-L', '--max-redirs', '3',
        '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'https://www.linkedin.com/feed/'
    ], capture_output=True, text=True, timeout=30)
    print(f"  {curl_result.stdout}")
    if curl_result.stderr:
        print(f"  stderr: {curl_result.stderr[:200]}")

    # Also try curl with verbose to see redirect headers
    print("\n  Curl verbose (first redirect only):")
    curl_v = subprocess.run([
        'curl', '-s', '-D', '-',
        '-o', '/dev/null',
        '-b', f'li_at={li_at}',
        '--max-redirs', '0',
        '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'https://www.linkedin.com/feed/'
    ], capture_output=True, text=True, timeout=30)
    for line in curl_v.stdout.split('\n'):
        line = line.strip()
        if line and (line.startswith('HTTP') or line.lower().startswith('location') or line.lower().startswith('set-cookie')):
            # Truncate cookie values for readability
            if line.lower().startswith('set-cookie'):
                print(f"    {line[:120]}")
            else:
                print(f"    {line}")

    context.close()
    browser.close()
    pw.stop()
    print("\nDone.")


if __name__ == '__main__':
    main()
