#!/usr/bin/env python3
"""
QA Test v2: Pay-Test-2 Chatbox Flow After Plugin Rollback to v4.6.4
Fixes: Wait for input to become enabled before checking (JS disables it during AI intro sequence)
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
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_APP_PASSWORD = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '')
WP_USER = 'Aether'
PAGE_ID = 689
SCREENSHOT_PATH = '/home/jared/projects/AI-CIV/aether/docs/rollback-qa/chatbox-flow.png'
LOCAL_PORT = 8979
LOCAL_HTML_PATH = '/tmp/paytest2_rollback_qa.html'

results = {}


def fetch_page_content():
    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    url = f"https://purebrain.ai/wp-json/wp/v2/pages/{PAGE_ID}?context=edit"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Basic {encoded}')
    req.add_header('User-Agent', 'Mozilla/5.0')
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    raw = data.get('content', {}).get('raw', '')
    html = raw.replace('<!-- wp:html -->', '').replace('<!-- /wp:html -->', '').strip()
    return html


def start_server(html):
    with open(LOCAL_HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    os.chdir('/tmp')
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda self, *args: None
    server = http.server.HTTPServer(('localhost', LOCAL_PORT), handler)
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()
    time.sleep(1)
    return server


async def run_tests():
    print("\n" + "="*60)
    print("PAY-TEST-2 CHATBOX QA - POST-ROLLBACK v4.6.4 (v2)")
    print("="*60 + "\n")

    # 1. Fetch page
    print("[STEP 1] Fetching page via WP REST API (WAF-safe)...")
    try:
        html = fetch_page_content()
        print(f"  PASS: Fetched {len(html):,} chars")
    except Exception as e:
        print(f"  FAIL: {e}")
        sys.exit(1)

    # 2. Source-level script checks
    print("\n[STEP 2] Source-level removed script checks:")
    checks_source = {
        'no_pb_bypass_override': 'pb-bypass-override' not in html,
        'no_pb_sandbox_override': 'pb-sandbox-override' not in html,
        'no_pb_paypal_routing_fix': 'pb-paypal-routing-fix' not in html,
        'no_pb_session_timer_fix': 'pb-session-timer-fix' not in html,
        'standard_chatbox_flow_present': ('startConversation' in html or 'chat-initial' in html),
    }
    labels_source = {
        'no_pb_bypass_override': 'pb-bypass-override NOT in source',
        'no_pb_sandbox_override': 'pb-sandbox-override NOT in source',
        'no_pb_paypal_routing_fix': 'pb-paypal-routing-fix NOT in source',
        'no_pb_session_timer_fix': 'pb-session-timer-fix NOT in source',
        'standard_chatbox_flow_present': 'Standard chatbox flow (startConversation) present',
    }
    for key, val in checks_source.items():
        results[key] = val
        print(f"  {'PASS' if val else 'FAIL'}: {labels_source[key]}")

    # 3. Start server + Playwright
    print("\n[STEP 3] Browser automation checks...")
    server = start_server(html)
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

        console_errors = []
        page.on('console', lambda m: console_errors.append(m.text) if m.type == 'error' else None)

        # Navigate + wait
        await page.goto(local_url, wait_until='domcontentloaded')
        print("  Waiting 10s for full page initialization...")
        await asyncio.sleep(10)

        # CHECK 1: Chat section exists
        found_chat = None
        for sel in ['.chat-section', '.chat-container', '.chat-initial', '#chatInitial', '#userInput']:
            el = await page.query_selector(sel)
            if el:
                found_chat = sel
                break
        results['chat_section_exists'] = bool(found_chat)
        print(f"  {'PASS' if found_chat else 'FAIL'}: Chat section exists (found: {found_chat})")

        # CHECK 2: Begin Awakening button
        btn = await page.query_selector('.chat-initial__btn')
        btn_visible = bool(btn) and await btn.is_visible()
        results['begin_btn_visible'] = btn_visible
        btn_text = (await btn.inner_text()).strip() if btn else '(not found)'
        print(f"  {'PASS' if btn_visible else 'FAIL'}: Begin Awakening button visible (text: '{btn_text}')")

        # Click it
        if btn_visible:
            await btn.click()
            print("  Clicked 'Begin Awakening' - waiting for AI intro sequence + input to enable...")
            try:
                # Wait up to 20s for input to become enabled (AI has to deliver opening messages)
                await page.wait_for_function(
                    "() => { const el = document.getElementById('userInput'); return el && !el.disabled; }",
                    timeout=20000
                )
                print("  Input became enabled (AI intro sequence complete)")
            except Exception:
                print("  NOTE: Input did not become enabled within 20s (may still be in intro)")

        # CHECK 3: Input visible and enabled (after waiting)
        chat_input = await page.query_selector('#userInput')
        input_visible = bool(chat_input) and await chat_input.is_visible()
        input_enabled = bool(chat_input) and await chat_input.is_enabled()
        results['chat_input_visible'] = input_visible
        results['chat_input_enabled'] = input_enabled
        print(f"  {'PASS' if input_visible else 'FAIL'}: Chat input (#userInput) visible")
        print(f"  {'PASS' if input_enabled else 'FAIL'}: Chat input (#userInput) enabled")

        # CHECK 4: Type "Hello" and submit
        if input_visible and chat_input:
            await chat_input.fill('Hello')
            await asyncio.sleep(0.3)
            submit_btn = await page.query_selector('#submitBtn')
            if submit_btn and await submit_btn.is_visible():
                await submit_btn.click()
                print("  Submitted via #submitBtn click")
            else:
                await chat_input.press('Enter')
                print("  Submitted via Enter key")
            results['message_submitted'] = True
            print("  PASS: Message 'Hello' submitted")
        else:
            results['message_submitted'] = False
            print("  FAIL: Could not submit message (input not available)")

        # Wait 3s for response
        await asyncio.sleep(3)

        # Screenshot
        await page.screenshot(path=SCREENSHOT_PATH, full_page=False)
        print(f"  PASS: Screenshot saved -> {SCREENSHOT_PATH}")

        # CHECK 5: AI response appeared
        ai_msgs = await page.query_selector_all('.message--ai')
        ai_count = len(ai_msgs)
        results['ai_response_appeared'] = ai_count > 0
        print(f"  {'PASS' if ai_count > 0 else 'FAIL'}: AI response appeared ({ai_count} total messages visible)")
        if ai_count > 0:
            first = await ai_msgs[0].inner_text()
            print(f"    First AI message: '{first[:70]}'")

        # CHECK 6: DOM-level script ID checks
        bypass_dom = await page.evaluate("() => !!document.getElementById('pb-bypass-override')")
        sandbox_dom = await page.evaluate("() => !!document.getElementById('pb-sandbox-override')")
        paypal_dom = await page.evaluate("() => !!document.getElementById('pb-paypal-routing-fix')")
        timer_dom = await page.evaluate("() => !!document.getElementById('pb-session-timer-fix')")

        results['no_bypass_override_dom'] = not bypass_dom
        results['no_sandbox_override_dom'] = not sandbox_dom
        results['no_paypal_fix_dom'] = not paypal_dom
        results['no_session_timer_dom'] = not timer_dom
        print(f"\n  DOM script ID verification:")
        print(f"  {'PASS' if not bypass_dom else 'FAIL'}: #pb-bypass-override absent from DOM")
        print(f"  {'PASS' if not sandbox_dom else 'FAIL'}: #pb-sandbox-override absent from DOM")
        print(f"  {'PASS' if not paypal_dom else 'FAIL'}: #pb-paypal-routing-fix absent from DOM")
        print(f"  {'PASS' if not timer_dom else 'FAIL'}: #pb-session-timer-fix absent from DOM")

        # Console errors
        if console_errors:
            print(f"\n  Console errors ({len(console_errors)}): {console_errors[:3]}")
        else:
            print(f"\n  Console errors: None")

        await browser.close()
    server.shutdown()

    # Final summary
    all_checks = {
        'chat_section_exists': 'Chat section exists',
        'begin_btn_visible': 'Begin Awakening button visible',
        'chat_input_visible': 'Chat input visible',
        'chat_input_enabled': 'Chat input enabled (after AI intro)',
        'message_submitted': 'Message submitted successfully',
        'ai_response_appeared': 'AI response appeared',
        'standard_chatbox_flow_present': 'Standard chatbox flow (no bypass override) is default',
        'no_pb_bypass_override': 'pb-bypass-override NOT in source',
        'no_pb_sandbox_override': 'pb-sandbox-override NOT in source',
        'no_pb_paypal_routing_fix': 'pb-paypal-routing-fix NOT in source',
        'no_pb_session_timer_fix': 'pb-session-timer-fix NOT in source',
        'no_bypass_override_dom': '#pb-bypass-override absent from DOM',
        'no_sandbox_override_dom': '#pb-sandbox-override absent from DOM',
        'no_paypal_fix_dom': '#pb-paypal-routing-fix absent from DOM',
        'no_session_timer_dom': '#pb-session-timer-fix absent from DOM',
    }

    print("\n" + "="*60)
    print("FINAL QA RESULTS - PAY-TEST-2 ROLLBACK v4.6.4")
    print("="*60)
    passed = failed = 0
    for key, label in all_checks.items():
        val = results.get(key)
        if val is True:
            print(f"  PASS: {label}")
            passed += 1
        elif val is False:
            print(f"  FAIL: {label}")
            failed += 1
        else:
            print(f"  SKIP: {label}")

    overall = "PASS" if failed == 0 else "FAIL"
    print(f"\n  Score: {passed}/{passed+failed} checks passing")
    print(f"  OVERALL: {overall}")
    print(f"  Screenshot: {SCREENSHOT_PATH}")
    print("="*60 + "\n")
    return overall


if __name__ == '__main__':
    result = asyncio.run(run_tests())
    sys.exit(0 if result == 'PASS' else 1)
