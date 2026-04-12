#!/usr/bin/env python3
"""
Phase 1: Login to Brevo and save authenticated session to disk.
Run this once. The saved session can then be reused by the workflow builder
without triggering 2FA again.
"""

import os
import re
import time
import json
import imaplib
import email as email_module
import email.utils
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
BREVO_EMAIL = 'purebrain@puremarketing.ai'
BREVO_PASSWORD = os.environ['BREVO_PASSWORD']
GMAIL_USER = os.environ['GMAIL_USERNAME']
GMAIL_APP_PASSWORD = os.environ['GOOGLE_APP_PASSWORD']

SESSION_FILE = '/home/jared/projects/AI-CIV/aether/tools/brevo_session.json'
SS_DIR = '/home/jared/projects/AI-CIV/aether/exports/screenshots'
os.makedirs(SS_DIR, exist_ok=True)


def extract_code_from_body(body):
    """Extract 6-digit code from email body. Returns code or None."""
    match = re.search(r'verification code[:\s]*\n?\s*(\d{6})', body, re.IGNORECASE)
    if match:
        return match.group(1)
    for c in re.findall(r'\b\d{6}\b', body):
        d = list(c)
        if not (d[0] == d[2] == d[4] and d[1] == d[3] == d[5]):
            return c
    return None


def get_2fa_code(max_wait=90, started_at=None):
    """
    Wait for a NEW Brevo verification email that arrived AFTER started_at.
    started_at: unix timestamp (time.time()) of when login was triggered.
    This prevents reusing old/consumed codes.
    """
    if started_at is None:
        started_at = time.time() - 10  # 10 second buffer

    print(f"  [IMAP] Waiting for NEW Brevo 2FA code (arrived after {time.strftime('%H:%M:%S', time.localtime(started_at))})...")
    deadline = time.time() + max_wait

    while time.time() < deadline:
        try:
            m = imaplib.IMAP4_SSL('imap.gmail.com')
            m.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            m.select('INBOX')

            # Search ALL recent Brevo verification emails (read and unread)
            # We'll filter by date ourselves
            import datetime
            today = datetime.date.today().strftime('%d-%b-%Y')
            _, data = m.search(None, f'FROM account-alerts@t.brevo.com SINCE {today}')

            if data[0]:
                msg_ids = data[0].decode().split()
                # Check most recent first
                for mid in reversed(msg_ids):
                    _, mdata = m.fetch(mid, '(RFC822 INTERNALDATE)')
                    # Get the internal date
                    internal_date_str = mdata[0][0].decode() if isinstance(mdata[0][0], bytes) else str(mdata[0][0])
                    # Extract date from INTERNALDATE response
                    date_match = re.search(r'INTERNALDATE "([^"]+)"', internal_date_str)

                    msg = email_module.message_from_bytes(mdata[0][1])
                    subj = msg.get('Subject', '')
                    if 'verify' not in subj.lower():
                        continue

                    # Get email date to check it's recent
                    msg_date_str = msg.get('Date', '')
                    print(f"  [IMAP] Found verification email: {subj} | Date: {msg_date_str}")

                    # Parse the email date
                    try:
                        msg_ts = email.utils.parsedate_to_datetime(msg_date_str).timestamp()
                        if msg_ts < started_at - 30:
                            print(f"  [IMAP] Email too old ({msg_date_str}) - skipping")
                            continue
                        print(f"  [IMAP] Email is recent enough (ts={msg_ts:.0f} vs started={started_at:.0f})")
                    except Exception as de:
                        print(f"  [IMAP] Date parse error: {de} - using anyway")

                    # Extract the body
                    body = ''
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() in ('text/plain', 'text/html'):
                                body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                    code = extract_code_from_body(body)
                    if code:
                        print(f"  [IMAP] Code extracted: {code}")
                        m.logout()
                        return code

            m.logout()
        except Exception as e:
            print(f"  [IMAP] Error: {e}")

        remaining = int(deadline - time.time())
        print(f"  [IMAP] Waiting for fresh email... ({remaining}s left)")
        time.sleep(5)

    return None


def main():
    print("=" * 60)
    print("Brevo Session Login - Phase 1")
    print("Establishes authenticated session and saves to disk")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        ctx = browser.new_context(
            viewport={'width': 1600, 'height': 900},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )
        page = ctx.new_page()

        # ── Navigate to login ──────────────────────────────────────────
        print("\n[1] Loading login page...")
        page.goto('https://login.brevo.com/', wait_until='domcontentloaded', timeout=60000)
        time.sleep(2)

        # Dismiss cookie banner
        try:
            page.wait_for_selector("button:has-text('Accept All Cookies')", timeout=4000).click()
            time.sleep(0.8)
            print("  Cookie banner dismissed")
        except PlaywrightTimeout:
            pass

        page.screenshot(path=f'{SS_DIR}/session_01_login.png', full_page=True)

        # ── Fill credentials ───────────────────────────────────────────
        print("[2] Filling credentials...")
        ef = page.wait_for_selector('input[name="email"], input#email', timeout=15000)
        ef.fill(BREVO_EMAIL)
        time.sleep(0.3)

        pf = page.wait_for_selector('input[type="password"]', timeout=10000)
        pf.fill(BREVO_PASSWORD)
        time.sleep(0.3)

        page.screenshot(path=f'{SS_DIR}/session_02_creds.png', full_page=True)

        # Submit
        login_triggered_at = time.time()  # Record when we triggered login (for fresh code detection)
        try:
            page.wait_for_selector(
                'button:has-text("Log In"), button[data-testid="submit-button"]',
                timeout=5000
            ).click()
        except PlaywrightTimeout:
            pf.press('Enter')
        print("  Submitted login form")
        print(f"  Login triggered at: {time.strftime('%H:%M:%S')}")

        time.sleep(4)
        try:
            page.wait_for_load_state('networkidle', timeout=20000)
        except PlaywrightTimeout:
            pass

        print(f"  URL after submit: {page.url}")
        page.screenshot(path=f'{SS_DIR}/session_03_after_submit.png', full_page=True)

        # ── Handle 2FA ─────────────────────────────────────────────────
        if '2fa' in page.url or 'new-device' in page.url:
            print("\n[3] 2FA device verification required")
            page.screenshot(path=f'{SS_DIR}/session_04_2fa.png', full_page=True)

            # Pass login_triggered_at so we only accept codes sent AFTER this moment
            code = get_2fa_code(max_wait=90, started_at=login_triggered_at)
            if not code:
                print("ERROR: Could not retrieve 2FA code from Gmail")
                browser.close()
                return False

            # Find the code input - it's type="text" (not type="number")
            # Try multiple selectors since the 2FA page might differ
            cf = None
            for sel in [
                'input[autocomplete="one-time-code"]',
                'input[inputmode="numeric"]',
                'input[type="number"]',
                'input[placeholder*="code" i]',
                'form input[type="text"]:not([name="email"])',
                'input[type="text"]:not([name="email"]):not([name="vendor-search-handler"])',
            ]:
                try:
                    cf = page.wait_for_selector(sel, timeout=3000, state='visible')
                    print(f"  Found code input via: {sel}")
                    break
                except PlaywrightTimeout:
                    continue

            if not cf:
                # Get ALL visible inputs and pick the right one
                inputs = page.query_selector_all('input:visible') if hasattr(page, 'query_selector_all') else []
                for inp in inputs:
                    t = inp.get_attribute('type') or 'text'
                    n = inp.get_attribute('name') or ''
                    if t in ('text', 'number') and n not in ('email', 'vendor-search-handler', 'password'):
                        cf = inp
                        print(f"  Found code input via fallback scan: type={t} name={n}")
                        break

            if not cf:
                print("ERROR: Cannot find 2FA code input field")
                # Print all inputs for debugging
                all_inputs = page.query_selector_all('input')
                print(f"  All inputs on page ({len(all_inputs)}):")
                for inp in all_inputs:
                    attrs = {a: inp.get_attribute(a) for a in ['type', 'name', 'id', 'placeholder', 'class'] if inp.get_attribute(a)}
                    print(f"    {attrs}")
                page.screenshot(path=f'{SS_DIR}/session_04b_2fa_debug.png', full_page=True)
                browser.close()
                return False

            cf.fill(code)
            time.sleep(0.5)
            page.screenshot(path=f'{SS_DIR}/session_05_code_entered.png', full_page=True)
            print(f"  Entered code: {code}")

            # Click Verify
            try:
                page.wait_for_selector(
                    'button:has-text("Verify"), button[data-testid="submit-button"]',
                    timeout=8000
                ).click()
                print("  Clicked Verify")
            except PlaywrightTimeout:
                cf.press('Enter')
                print("  Pressed Enter")

            # Wait for redirect away from 2fa page - may take up to 10 seconds
            for _ in range(15):
                time.sleep(1)
                if 'login' not in page.url.lower() and '2fa' not in page.url and 'new-device' not in page.url:
                    print(f"  Redirected to: {page.url}")
                    break
                print(f"  Still on 2FA page... waiting ({page.url[:60]})")
            else:
                # Try waiting for networkidle anyway
                try:
                    page.wait_for_url('**/app.brevo.com/**', timeout=15000)
                except PlaywrightTimeout:
                    pass

            print(f"  URL after 2FA: {page.url}")
            page.screenshot(path=f'{SS_DIR}/session_06_after_2fa.png', full_page=True)

            if '2fa' in page.url or 'new-device' in page.url:
                print("ERROR: Authentication failed - still on 2FA page (invalid code?)")
                browser.close()
                return False

        else:
            print("[3] No 2FA required - already authenticated")

        # ── Verify we're logged in ─────────────────────────────────────
        if 'login' in page.url.lower():
            print("ERROR: Not logged in")
            browser.close()
            return False

        print(f"\n[4] Successfully logged in!")
        print(f"    URL: {page.url}")

        # Wait a moment for session to fully establish
        time.sleep(3)
        page.goto('https://app.brevo.com/', wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        page.screenshot(path=f'{SS_DIR}/session_07_dashboard.png', full_page=True)
        print(f"    Dashboard URL: {page.url}")

        # ── Save session state ─────────────────────────────────────────
        print("\n[5] Saving session to disk...")
        storage_state = ctx.storage_state()
        with open(SESSION_FILE, 'w') as f:
            json.dump(storage_state, f)

        n_cookies = len(storage_state.get('cookies', []))
        n_origins = len(storage_state.get('origins', []))
        print(f"    Saved: {n_cookies} cookies, {n_origins} origins")
        print(f"    Session file: {SESSION_FILE}")

        browser.close()
        print("\n[SUCCESS] Session saved. Run the workflow builder next.")
        return True


if __name__ == '__main__':
    ok = main()
    exit(0 if ok else 1)
