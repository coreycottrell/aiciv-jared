#!/usr/bin/env python3
"""
QA Test: Pay-Test-2 Chatbox Flow After Plugin Rollback to v4.6.4
Checks:
  1. Chat section exists
  2. Chat input visible and enabled
  3. Typing "Hello" and submitting works
  4. AI response appears
  5. No pb-bypass-override script exists (standard chatbox flow is default)
  6. No pb-sandbox-override, pb-paypal-routing-fix, pb-session-timer-fix scripts

Strategy: WAF-safe approach - fetch page via WP REST API, serve locally, test with Playwright
"""

import asyncio
import base64
import http.server
import json
import os
import sys
import threading
import time
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

# Config
WP_APP_PASSWORD = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '')
WP_USER = 'Aether'
PAGE_ID = 689  # pay-test-2
SCREENSHOT_DIR = '/home/jared/projects/AI-CIV/aether/docs/rollback-qa'
SCREENSHOT_PATH = f'{SCREENSHOT_DIR}/chatbox-flow.png'
LOCAL_PORT = 8977
LOCAL_HTML_PATH = '/tmp/paytest2_rollback_qa.html'

results = {}


def fetch_page_via_rest_api():
    """Fetch pay-test-2 page content via WP REST API (WAF-safe)."""
    print("Fetching page content via WP REST API...")
    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()

    url = f"https://purebrain.ai/wp-json/wp/v2/pages/{PAGE_ID}?context=edit"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Basic {encoded}')
    req.add_header('User-Agent', 'Mozilla/5.0')

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    raw_content = data.get('content', {}).get('raw', '')
    if not raw_content:
        raise ValueError("No content.raw returned from WP REST API")

    print(f"  Fetched page content: {len(raw_content)} chars")

    # Strip wp:html markers if present
    html = raw_content
    if '<!-- wp:html -->' in html:
        html = html.replace('<!-- wp:html -->', '').replace('<!-- /wp:html -->', '')
        html = html.strip()

    return html


def save_html_locally(html):
    """Save HTML to local file for serving."""
    with open(LOCAL_HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  Saved HTML locally: {LOCAL_HTML_PATH}")


def start_local_server():
    """Start a simple HTTP server to serve the HTML file."""
    import os
    os.chdir('/tmp')

    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda self, *args: None  # suppress logs

    server = http.server.HTTPServer(('localhost', LOCAL_PORT), handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print(f"  Local server running at http://localhost:{LOCAL_PORT}/")
    return server


async def run_qa_test():
    """Run the full QA test suite."""
    global results

    print("\n" + "="*60)
    print("PAY-TEST-2 CHATBOX QA - POST-ROLLBACK TO v4.6.4")
    print("="*60 + "\n")

    # Step 1: Fetch page content
    print("[1/3] Fetching page content via WP REST API...")
    try:
        html = fetch_page_via_rest_api()
        save_html_locally(html)
        print("  PASS: Page content fetched and saved locally")
    except Exception as e:
        print(f"  FAIL: Could not fetch page: {e}")
        sys.exit(1)

    # Step 2: Check for removed scripts IN SOURCE
    print("\n[2/3] Checking for removed scripts in page source...")

    removed_scripts = {
        'pb-bypass-override': 'pb-bypass-override' in html,
        'pb-sandbox-override': 'pb-sandbox-override' in html,
        'pb-paypal-routing-fix': 'pb-paypal-routing-fix' in html,
        'pb-session-timer-fix': 'pb-session-timer-fix' in html,
    }

    print("\n  Script Removal Verification:")
    for script_id, found in removed_scripts.items():
        status = "FAIL (FOUND - should be removed!)" if found else "PASS (not in source)"
        print(f"    {script_id}: {status}")
        results[f'no_{script_id.replace("-", "_")}'] = not found

    # Also check standard chatbox flow IS present
    standard_flow_present = 'startConversation' in html or 'chat-initial' in html
    results['standard_chatbox_flow_present'] = standard_flow_present
    print(f"\n  Standard chatbox flow (startConversation/chat-initial) present: {'PASS' if standard_flow_present else 'FAIL'}")

    # Step 3: Start local server and run Playwright test
    print("\n[3/3] Starting local server and running Playwright browser test...")
    server = start_local_server()
    time.sleep(1)  # Brief pause for server startup

    local_url = f"http://localhost:{LOCAL_PORT}/paytest2_rollback_qa.html"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-web-security']
        )

        context = await browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36'
        )

        page = await context.new_page()

        # Capture console errors
        console_errors = []
        page.on('console', lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == 'error' else None)

        print(f"  Navigating to local URL: {local_url}")
        await page.goto(local_url, wait_until='domcontentloaded')
        print("  DOM content loaded - waiting 10 seconds for full page init...")
        await asyncio.sleep(10)

        # CHECK 1: Chat section exists
        print("\n  --- Browser Checks ---")
        chat_section_selectors = ['.chat-section', '.chat-container', '.chat-initial', '#chatInitial', '#chatInput', '#userInput']
        chat_exists = False
        found_selector = None
        for sel in chat_section_selectors:
            element = await page.query_selector(sel)
            if element:
                chat_exists = True
                found_selector = sel
                break

        results['chat_section_exists'] = chat_exists
        print(f"  CHECK 1 - Chat section exists: {'PASS' if chat_exists else 'FAIL'} (selector: {found_selector})")

        # CHECK 2: Begin Awakening button visible
        begin_btn = await page.query_selector('.chat-initial__btn')
        if begin_btn:
            btn_visible = await begin_btn.is_visible()
            btn_text = await begin_btn.inner_text()
            results['begin_btn_visible'] = btn_visible
            print(f"  CHECK 2 - Begin Awakening button: {'PASS' if btn_visible else 'FAIL'} (text: '{btn_text.strip()}')")
        else:
            results['begin_btn_visible'] = False
            print(f"  CHECK 2 - Begin Awakening button: FAIL (not found)")

        # Click Begin Awakening if it exists
        if results.get('begin_btn_visible'):
            print("  Clicking 'Begin Awakening' button...")
            await begin_btn.click()
            await asyncio.sleep(3)

        # CHECK 3: Chat input visible and enabled
        chat_input = await page.query_selector('#userInput')
        if chat_input:
            input_visible = await chat_input.is_visible()
            input_enabled = await chat_input.is_enabled()
            results['chat_input_visible'] = input_visible
            results['chat_input_enabled'] = input_enabled
            print(f"  CHECK 3a - Chat input visible: {'PASS' if input_visible else 'FAIL'}")
            print(f"  CHECK 3b - Chat input enabled: {'PASS' if input_enabled else 'FAIL'}")
        else:
            results['chat_input_visible'] = False
            results['chat_input_enabled'] = False
            print(f"  CHECK 3 - Chat input (#userInput): FAIL (not found)")

        # CHECK 4: Type "Hello" and submit
        if results.get('chat_input_visible'):
            print("  Typing 'Hello' into chat input...")
            await chat_input.fill('Hello')
            await asyncio.sleep(0.5)

            # Try Enter key first, then submit button
            submit_btn = await page.query_selector('#submitBtn')
            if submit_btn and await submit_btn.is_visible():
                print("  Clicking submit button (#submitBtn)...")
                await submit_btn.click()
            else:
                print("  Pressing Enter to submit...")
                await chat_input.press('Enter')

            results['message_submitted'] = True
            print(f"  CHECK 4 - Message submitted: PASS")
        else:
            results['message_submitted'] = False
            print(f"  CHECK 4 - Message submitted: FAIL (input not available)")

        # Wait 3 seconds for response
        print("  Waiting 3 seconds for AI response...")
        await asyncio.sleep(3)

        # Take screenshot
        print(f"  Taking screenshot -> {SCREENSHOT_PATH}")
        await page.screenshot(path=SCREENSHOT_PATH, full_page=False)
        print(f"  PASS: Screenshot saved")

        # CHECK 5: AI response appeared
        ai_messages = await page.query_selector_all('.message--ai')
        ai_count = len(ai_messages)

        # Also check typing indicator
        typing = await page.query_selector('.typing-indicator')
        typing_visible = False
        if typing:
            typing_visible = await typing.is_visible()

        ai_response_appeared = ai_count > 0
        results['ai_response_appeared'] = ai_response_appeared
        print(f"  CHECK 5 - AI response appeared: {'PASS' if ai_response_appeared else 'FAIL'} ({ai_count} messages, typing_visible={typing_visible})")

        if ai_count > 0:
            # Get text of first AI message
            first_msg = await ai_messages[0].inner_text()
            print(f"  First AI message: '{first_msg[:80]}...'")

        # CHECK 6: Verify no bypass override in page DOM (double check)
        bypass_in_dom = await page.evaluate("() => !!document.getElementById('pb-bypass-override')")
        sandbox_in_dom = await page.evaluate("() => !!document.getElementById('pb-sandbox-override')")
        paypal_fix_in_dom = await page.evaluate("() => !!document.getElementById('pb-paypal-routing-fix')")
        session_timer_in_dom = await page.evaluate("() => !!document.getElementById('pb-session-timer-fix')")

        results['no_bypass_override_dom'] = not bypass_in_dom
        results['no_sandbox_override_dom'] = not sandbox_in_dom
        results['no_paypal_fix_dom'] = not paypal_fix_in_dom
        results['no_session_timer_dom'] = not session_timer_in_dom

        print(f"\n  --- DOM Script ID Checks ---")
        print(f"  #pb-bypass-override in DOM: {'FAIL (found!)' if bypass_in_dom else 'PASS (absent)'}")
        print(f"  #pb-sandbox-override in DOM: {'FAIL (found!)' if sandbox_in_dom else 'PASS (absent)'}")
        print(f"  #pb-paypal-routing-fix in DOM: {'FAIL (found!)' if paypal_fix_in_dom else 'PASS (absent)'}")
        print(f"  #pb-session-timer-fix in DOM: {'FAIL (found!)' if session_timer_in_dom else 'PASS (absent)'}")

        # Get page title and any visible error text
        title = await page.title()
        print(f"\n  Page title: '{title}'")

        # Check console errors
        if console_errors:
            print(f"\n  Console errors during test ({len(console_errors)} total):")
            for err in console_errors[:5]:
                print(f"    {err[:100]}")
        else:
            print(f"\n  Console errors: None")

        await browser.close()

    server.shutdown()

    # Final summary
    print("\n" + "="*60)
    print("FINAL QA RESULTS SUMMARY")
    print("="*60)

    check_labels = {
        'chat_section_exists': 'Chat section exists',
        'begin_btn_visible': 'Begin Awakening button visible',
        'chat_input_visible': 'Chat input visible',
        'chat_input_enabled': 'Chat input enabled',
        'message_submitted': 'Message submitted successfully',
        'ai_response_appeared': 'AI response appeared',
        'standard_chatbox_flow_present': 'Standard chatbox flow (no bypass) is default',
        'no_pb_bypass_override': 'No pb-bypass-override in source',
        'no_pb_sandbox_override': 'No pb-sandbox-override in source',
        'no_pb_paypal_routing_fix': 'No pb-paypal-routing-fix in source',
        'no_pb_session_timer_fix': 'No pb-session-timer-fix in source',
        'no_bypass_override_dom': 'No #pb-bypass-override in DOM',
        'no_sandbox_override_dom': 'No #pb-sandbox-override in DOM',
        'no_paypal_fix_dom': 'No #pb-paypal-routing-fix in DOM',
        'no_session_timer_dom': 'No #pb-session-timer-fix in DOM',
    }

    passed = 0
    failed = 0

    for key, label in check_labels.items():
        val = results.get(key, None)
        if val is None:
            status = "SKIP"
        elif val:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1
        print(f"  [{status}] {label}")

    print(f"\n  Total: {passed} PASS, {failed} FAIL, {len(check_labels) - passed - failed} SKIP")

    overall = "PASS" if failed == 0 else "FAIL"
    print(f"\n  OVERALL RESULT: {overall}")
    print(f"  Screenshot: {SCREENSHOT_PATH}")
    print("="*60 + "\n")

    return overall, results


if __name__ == "__main__":
    overall, results = asyncio.run(run_qa_test())
    sys.exit(0 if overall == "PASS" else 1)
