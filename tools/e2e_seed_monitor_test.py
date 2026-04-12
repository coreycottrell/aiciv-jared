#!/usr/bin/env python3
"""
E2E Seed Monitor Test — pay-test-sandbox-2
Tests the complete flow: password → chatbox → bypass → payment → post-payment Q&A
Monitors all log files in real-time to verify seed fires.

Run with: xvfb-run --auto-servernum python3 tools/e2e_seed_monitor_test.py
Or headless: python3 tools/e2e_seed_monitor_test.py --headless
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Parse args
HEADLESS = '--headless' in sys.argv

LOG_DIR = '/home/jared/projects/AI-CIV/aether/logs'
SCREENSHOT_DIR = '/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-seed-monitor-20260302'
REPORT_FILE = '/home/jared/projects/AI-CIV/aether/exports/e2e-seed-monitor-report-20260302.md'

# Log files to monitor
LOG_FILES = {
    'conversations': os.path.join(LOG_DIR, 'purebrain_web_conversations.jsonl'),
    'pay_test': os.path.join(LOG_DIR, 'purebrain_pay_test.jsonl'),
    'payments': os.path.join(LOG_DIR, 'purebrain_payments.jsonl'),
}

# Track initial log file sizes
initial_sizes = {}
captured_events = []

def log(msg):
    ts = datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:12]
    print(f'[{ts}] {msg}', flush=True)

def capture_new_entries():
    """Check all log files for new entries since test start."""
    new_entries = []
    for name, path in LOG_FILES.items():
        if not os.path.exists(path):
            continue
        current_size = os.path.getsize(path)
        initial = initial_sizes.get(name, current_size)
        if current_size > initial:
            with open(path) as f:
                f.seek(initial)
                new_data = f.read()
                for line in new_data.strip().split('\n'):
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            entry['_source_log'] = name
                            new_entries.append(entry)
                        except json.JSONDecodeError:
                            pass
            initial_sizes[name] = current_size
    return new_entries


async def run_test():
    from playwright.async_api import async_playwright

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Record initial log file sizes
    for name, path in LOG_FILES.items():
        if os.path.exists(path):
            initial_sizes[name] = os.path.getsize(path)
        else:
            initial_sizes[name] = 0

    log(f'Starting E2E Seed Monitor Test (headless={HEADLESS})')
    log(f'Screenshots: {SCREENSHOT_DIR}')

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=['--no-sandbox', '--disable-web-security', '--disable-features=IsolateOrigins,site-per-process']
        )
        context = await browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36'
        )

        # Monitor network requests
        network_log = []
        page = await context.new_page()

        async def on_request(req):
            url = req.url
            if 'purebrain.ai/api/' in url or 'api.purebrain.ai' in url:
                network_log.append({
                    'time': datetime.now(timezone.utc).isoformat(),
                    'method': req.method,
                    'url': url,
                })
                log(f'  [NET] {req.method} {url}')

        async def on_response(resp):
            url = resp.url
            if 'purebrain.ai/api/' in url or 'api.purebrain.ai' in url:
                log(f'  [NET] <- {resp.status} {url}')

        page.on('request', on_request)
        page.on('response', on_response)

        # Capture console messages
        console_log = []
        page.on('console', lambda msg: console_log.append({
            'time': datetime.now(timezone.utc).isoformat(),
            'type': msg.type,
            'text': msg.text[:300]
        }))

        step = 0
        async def screenshot(name):
            nonlocal step
            step += 1
            path = os.path.join(SCREENSHOT_DIR, f'{step:03d}-{name}.png')
            try:
                await page.screenshot(path=path, timeout=8000)
                log(f'  [SCREENSHOT] {path}')
            except Exception as e:
                log(f'  [SCREENSHOT FAIL] {name}: {e}')

        # ── PHASE 0: Navigate + Password ────────────────────────────
        log('PHASE 0: Navigate to pay-test-sandbox-2')
        await page.goto('https://purebrain.ai/pay-test-sandbox-2/', wait_until='networkidle', timeout=30000)
        await screenshot('page-load')

        # Enter password
        pw_input = page.locator('input[name="post_password"]')
        if await pw_input.count() > 0:
            log('  Entering password...')
            await pw_input.fill('PureBrain.ai253443$$')
            submit = page.locator('input[type="submit"], button[type="submit"]')
            await submit.click()
            await page.wait_for_load_state('networkidle', timeout=15000)
            await asyncio.sleep(2)
            log('  Password accepted')
        else:
            log('  No password gate (already unlocked)')

        await screenshot('after-password')
        check_entries = capture_new_entries()
        if check_entries:
            log(f'  ** {len(check_entries)} new log entries after page load **')

        # ── PHASE 1: Begin Awakening ────────────────────────────────
        log('PHASE 1: Begin Awakening')
        await asyncio.sleep(3)  # Let page JS load

        begin_btn = page.locator('.chat-initial__btn')
        if await begin_btn.count() > 0:
            await begin_btn.click()
            log('  Clicked Begin Awakening')
            await asyncio.sleep(5)  # Wait for chatbox to open
        else:
            log('  [WARN] No .chat-initial__btn found')

        await screenshot('chatbox-open')

        # Enter bypass code
        log('  Entering bypass code...')
        textarea = page.locator('.chat-box textarea, #pb-chat-textarea, textarea')
        if await textarea.count() > 0:
            # Use page.type for React-style input handling
            await textarea.first.click()
            await page.keyboard.type('pb-full-bypass', delay=30)
            await asyncio.sleep(1)

            # Try send button or Enter
            send_btn = page.locator('.chat-box button[type="submit"], .chat-send-btn, button.send-btn')
            if await send_btn.count() > 0:
                await send_btn.first.click()
            else:
                await page.keyboard.press('Enter')

            log('  Bypass code submitted')
            await asyncio.sleep(8)  # Wait for 4 AI messages
        else:
            log('  [WARN] No textarea found')

        await screenshot('after-bypass')
        check_entries = capture_new_entries()
        if check_entries:
            log(f'  ** {len(check_entries)} new log entries after bypass **')
            for e in check_entries:
                captured_events.append(e)
                src = e.get('_source_log', '')
                ts = e.get('server_timestamp', '')[:19]
                log(f'    [{src}] {ts}')

        # ── PHASE 2: PayPal / Payment ───────────────────────────────
        log('PHASE 2: Trigger Payment')

        # Click Activate Now (#proCta)
        pro_cta = page.locator('#proCta')
        if await pro_cta.count() > 0:
            await page.evaluate('document.querySelector("#proCta").click()')
            log('  Clicked Activate Now')
            await asyncio.sleep(3)
        else:
            log('  [WARN] No #proCta found — trying JS click')
            await page.evaluate('''() => {
                const btns = document.querySelectorAll("button, a");
                for (const b of btns) {
                    if (b.textContent.includes("Activate")) { b.click(); return "clicked"; }
                }
                return "not found";
            }''')
            await asyncio.sleep(3)

        await screenshot('paypal-modal')

        # Click sandbox bypass button
        bypass_btn = page.locator('#pb-sandbox-bypass-btn')
        if await bypass_btn.count() > 0:
            log('  Found sandbox bypass button — clicking')
            await bypass_btn.click()
            log('  Sandbox bypass clicked — simulating payment')
            await asyncio.sleep(5)
        else:
            log('  [WARN] No sandbox bypass button — trying JS')
            result = await page.evaluate('''() => {
                const btn = document.getElementById("pb-sandbox-bypass-btn");
                if (btn) { btn.click(); return "clicked"; }
                // Try any button with "Simulate" text
                const btns = document.querySelectorAll("button");
                for (const b of btns) {
                    if (b.textContent.includes("Simulate")) { b.click(); return "clicked-simulate"; }
                }
                return "not-found";
            }''')
            log(f'  JS bypass result: {result}')
            await asyncio.sleep(5)

        await screenshot('after-payment')

        # Check for payment/verify entries
        check_entries = capture_new_entries()
        if check_entries:
            log(f'  ** {len(check_entries)} new log entries after payment **')
            for e in check_entries:
                captured_events.append(e)
                src = e.get('_source_log', '')
                etype = e.get('type', e.get('metadata', {}).get('event_type', ''))
                log(f'    [{src}] type={etype}')

        # ── PHASE 3: Post-Payment Chatbox Q&A ──────────────────────
        log('PHASE 3: Post-Payment Q&A Flow')
        await asyncio.sleep(5)  # Wait for post-payment chatbox to appear

        await screenshot('post-payment-chatbox')

        # Check if post-payment chatbox appeared
        ptc = page.locator('.ptc-wrapper, #pay-test-post-payment')
        if await ptc.count() > 0:
            log('  Post-payment chatbox visible!')
        else:
            log('  [WARN] Post-payment chatbox not found — waiting more...')
            await asyncio.sleep(10)
            await screenshot('waiting-for-ptc')

        # Q&A: Answer each question using page.type for proper event firing
        qa_pairs = [
            ('Hannah Test', 'name'),
            ('hannah@test.com', 'email'),
            ('Test Corp', 'company'),
            ('CTO', 'role'),
            ('Testing the full E2E flow for go-live validation', 'goal'),
        ]

        for answer, label in qa_pairs:
            log(f'  Q&A [{label}]: typing "{answer}"')
            await asyncio.sleep(3)  # Wait for question to appear

            # Find the active textarea in the post-payment chatbox
            ptc_textarea = page.locator('.ptc-wrapper textarea, #pay-test-post-payment textarea, .ptc-textarea')
            if await ptc_textarea.count() > 0:
                await ptc_textarea.first.click()
                await ptc_textarea.first.fill('')  # Clear first
                await page.keyboard.type(answer, delay=20)
                await asyncio.sleep(0.5)

                # Click send or press Enter
                ptc_send = page.locator('.ptc-wrapper button.send-btn, .ptc-send-btn, .ptc-wrapper button[type="submit"]')
                if await ptc_send.count() > 0:
                    await ptc_send.first.click()
                else:
                    await page.keyboard.press('Enter')

                log(f'    Submitted [{label}]')
                await asyncio.sleep(4)  # Wait for AI response

                # Check for new log entries
                check_entries = capture_new_entries()
                if check_entries:
                    log(f'    ** {len(check_entries)} new log entries after [{label}] **')
                    for e in check_entries:
                        captured_events.append(e)
            else:
                log(f'  [WARN] No textarea found for [{label}]')
                await screenshot(f'no-textarea-{label}')

            await screenshot(f'qa-{label}')

        # ── PHASE 4: Birth Init + Portal ────────────────────────────
        log('PHASE 4: Waiting for birth init + portal')
        await asyncio.sleep(10)

        await screenshot('birth-portal-wait')

        # Check for birth-related entries
        check_entries = capture_new_entries()
        if check_entries:
            log(f'  ** {len(check_entries)} new log entries during birth/portal wait **')
            for e in check_entries:
                captured_events.append(e)

        # Wait a bit more and do final capture
        await asyncio.sleep(10)
        await screenshot('final-state')

        # Final log capture
        check_entries = capture_new_entries()
        if check_entries:
            log(f'  ** {len(check_entries)} final log entries **')
            for e in check_entries:
                captured_events.append(e)

        # ── RESULTS ─────────────────────────────────────────────────
        log('')
        log('='*60)
        log('E2E TEST RESULTS')
        log('='*60)
        log(f'Total captured events: {len(captured_events)}')
        log(f'Network requests to API: {len(network_log)}')

        log('')
        log('Events by source:')
        by_source = {}
        for e in captured_events:
            src = e.get('_source_log', 'unknown')
            by_source[src] = by_source.get(src, 0) + 1
        for src, count in by_source.items():
            log(f'  {src}: {count}')

        log('')
        log('Network timeline:')
        for req in network_log:
            log(f'  {req["time"][:19]} {req["method"]} {req["url"]}')

        log('')
        log('Console highlights:')
        for c in console_log:
            if 'PB' in c['text'] or 'birth' in c['text'].lower() or 'seed' in c['text'].lower() or 'payment' in c['text'].lower():
                log(f'  [{c["type"]}] {c["text"][:200]}')

        # Close browser
        await browser.close()

    # ── Write Report ────────────────────────────────────────────────
    log(f'Writing report to {REPORT_FILE}')
    write_report(network_log, console_log)
    log('DONE')


def write_report(network_log, console_log):
    lines = [
        '# E2E Seed Monitor Test Report',
        f'**Date**: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}',
        f'**Page**: pay-test-sandbox-2',
        f'**Mode**: {"headless" if HEADLESS else "headed (xvfb)"}',
        '',
        '## Captured Events Timeline',
        '',
        '| # | Time | Source | Type/Event |',
        '|---|------|--------|------------|',
    ]

    for i, e in enumerate(captured_events, 1):
        src = e.get('_source_log', '')
        ts = e.get('server_timestamp', '')[:19]
        etype = e.get('type', '')
        evt = e.get('event', e.get('metadata', {}).get('event_type', ''))
        lines.append(f'| {i} | {ts} | {src} | {etype or evt} |')

    lines.extend([
        '',
        '## Network Requests (API only)',
        '',
        '| Time | Method | URL |',
        '|------|--------|-----|',
    ])
    for req in network_log:
        lines.append(f'| {req["time"][:19]} | {req["method"]} | {req["url"]} |')

    lines.extend([
        '',
        '## Console Highlights',
        '',
    ])
    for c in console_log:
        if 'PB' in c['text'] or 'birth' in c['text'].lower() or 'seed' in c['text'].lower() or 'payment' in c['text'].lower() or 'error' in c['type']:
            lines.append(f'- `[{c["type"]}]` {c["text"][:200]}')

    lines.extend([
        '',
        '## Summary',
        '',
        f'- Total events captured: {len(captured_events)}',
        f'- Conversations: {sum(1 for e in captured_events if e.get("_source_log") == "conversations")}',
        f'- Pay-test: {sum(1 for e in captured_events if e.get("_source_log") == "pay_test")}',
        f'- Payments: {sum(1 for e in captured_events if e.get("_source_log") == "payments")}',
        f'- Network API requests: {len(network_log)}',
        '',
        f'**Screenshots**: `{SCREENSHOT_DIR}`',
    ])

    with open(REPORT_FILE, 'w') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    asyncio.run(run_test())
