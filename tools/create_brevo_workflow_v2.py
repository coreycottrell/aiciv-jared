#!/usr/bin/env python3
"""
Brevo Automation Workflow Creator v2
Full flow: Login → 2FA via email → Navigate to Automation → Build workflow

This script:
1. Logs into Brevo with email/password
2. Reads the 2FA verification code from Gmail via IMAP
3. Completes 2FA device verification
4. Navigates to the Automation section
5. Creates the Neural Feed Welcome Sequence workflow
6. Activates it
"""

import os
import sys
import time
import re
import json
import imaplib
import email
import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Load credentials
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
BREVO_EMAIL = 'purebrain@puremarketing.ai'
BREVO_PASSWORD = os.environ['BREVO_PASSWORD']
GMAIL_USER = os.environ['GMAIL_USERNAME']
GMAIL_APP_PASSWORD = os.environ['GOOGLE_APP_PASSWORD']
SCREENSHOTS_DIR = '/home/jared/projects/AI-CIV/aether/exports/screenshots'

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Workflow definition
WORKFLOW_NAME = "Neural Feed - Welcome Sequence"
WORKFLOW_STEPS = [
    {'type': 'email', 'template_id': 1, 'template_name': 'Neural Feed - Email 1 - Welcome (Aether)', 'delay_days': 0},
    {'type': 'wait', 'delay_days': 2},
    {'type': 'email', 'template_id': 2, 'template_name': 'Neural Feed - Email 2 - Jared\'s Story', 'delay_days': 2},
    {'type': 'wait', 'delay_days': 2},
    {'type': 'email', 'template_id': 3, 'template_name': 'Neural Feed - Email 3 - Aether Writes Directly', 'delay_days': 2},
    {'type': 'wait', 'delay_days': 3},
    {'type': 'email', 'template_id': 4, 'template_name': 'Neural Feed - Email 4 - Partnership in Practice', 'delay_days': 3},
    {'type': 'wait', 'delay_days': 3},
    {'type': 'email', 'template_id': 5, 'template_name': 'Neural Feed - Email 5 - The Context Tax', 'delay_days': 3},
    {'type': 'wait', 'delay_days': 4},
    {'type': 'email', 'template_id': 6, 'template_name': 'Neural Feed - Email 6 - Social Proof & Results', 'delay_days': 4},
    {'type': 'wait', 'delay_days': 7},
    {'type': 'email', 'template_id': 7, 'template_name': 'Neural Feed - Email 7 - The Invitation', 'delay_days': 7},
]


def ss(page, name, desc=""):
    """Take a screenshot."""
    path = f"{SCREENSHOTS_DIR}/brevo_workflow_{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"  [SS] {name}: {desc}")
    return path


def get_brevo_verification_code(max_wait=120):
    """
    Read Gmail IMAP to find the Brevo device verification code.
    Waits up to max_wait seconds for the email to arrive.
    Returns the 6-digit code as a string, or None if not found.
    """
    print(f"  [EMAIL] Checking Gmail for Brevo verification code...")
    start = time.time()

    while time.time() - start < max_wait:
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            mail.select('INBOX')

            # Search for Brevo verification emails in the last few minutes
            # Use UNSEEN to find the one we haven't read yet
            status, data = mail.search(None, 'FROM', 'account-alerts@t.brevo.com', 'UNSEEN')
            if status == 'OK' and data[0]:
                msg_ids = data[0].decode().split()
                print(f"  [EMAIL] Found {len(msg_ids)} unread Brevo alert(s)")

                # Get the most recent
                for mid in reversed(msg_ids):
                    status2, msg_data = mail.fetch(mid, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    subject = msg.get('Subject', '')

                    if 'verify' in subject.lower() or 'device' in subject.lower():
                        print(f"  [EMAIL] Found verification email: {subject}")

                        # Extract body
                        body = ''
                        if msg.is_multipart():
                            for part in msg.walk():
                                ct = part.get_content_type()
                                if ct in ('text/plain', 'text/html'):
                                    body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        else:
                            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                        # Find the verification code - look for pattern near "verification code"
                        # The code appears right after the phrase
                        match = re.search(
                            r'(?:verification code|one-time)[:\s]*\n?\s*(\d{6})',
                            body, re.IGNORECASE
                        )
                        if match:
                            code = match.group(1)
                            print(f"  [EMAIL] Extracted code: {code}")
                            mail.logout()
                            return code

                        # Fallback: find any 6-digit number that isn't repeated
                        codes = re.findall(r'\b(\d{6})\b', body)
                        if codes:
                            # Filter out repeated/pattern codes like 474747
                            unique_codes = []
                            for c in codes:
                                digits = list(c)
                                if not (digits[0] == digits[2] == digits[4] and digits[1] == digits[3] == digits[5]):
                                    unique_codes.append(c)
                            if unique_codes:
                                code = unique_codes[0]
                                print(f"  [EMAIL] Found code (fallback): {code}")
                                mail.logout()
                                return code

            mail.logout()

        except Exception as e:
            print(f"  [EMAIL] Error: {e}")

        print(f"  [EMAIL] Code not found yet, waiting 5s... ({int(time.time()-start)}s elapsed)")
        time.sleep(5)

    print(f"  [EMAIL] Timed out waiting for verification code")
    return None


def wait_for_element(page, selector, timeout=30000, description=""):
    """Wait for element and return it."""
    print(f"  [WAIT] {description or selector}")
    try:
        el = page.wait_for_selector(selector, timeout=timeout)
        return el
    except PlaywrightTimeout:
        print(f"  [TIMEOUT] Could not find: {selector}")
        return None


def run():
    print("=" * 65)
    print("Brevo Automation Workflow Creator v2")
    print(f"Target: {WORKFLOW_NAME}")
    print("=" * 65)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            viewport={'width': 1600, 'height': 900},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )
        page = context.new_page()
        page.set_default_timeout(30000)

        # ----------------------------------------------------------------
        # STEP 1: Login
        # ----------------------------------------------------------------
        print("\n[STEP 1] Login to Brevo")
        page.goto("https://login.brevo.com/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        ss(page, "01_login_page", "Login page")

        # Fill email
        email_field = wait_for_element(page, "input[type='email'], input[name='email']", description="Email field")
        if not email_field:
            print("ERROR: Could not find email field")
            ss(page, "error_no_email_field")
            browser.close()
            return None

        email_field.fill(BREVO_EMAIL)
        print(f"  Filled email: {BREVO_EMAIL}")
        time.sleep(0.3)

        # Fill password
        password_field = wait_for_element(page, "input[type='password']", description="Password field")
        if not password_field:
            print("ERROR: Could not find password field")
            ss(page, "error_no_password_field")
            browser.close()
            return None

        password_field.fill(BREVO_PASSWORD)
        print("  Filled password")
        time.sleep(0.3)

        ss(page, "02_credentials_filled", "Credentials filled")

        # Click Login button
        login_btn = wait_for_element(page, "button[type='submit']", description="Login button")
        if login_btn:
            login_btn.click()
            print("  Clicked Login")
        else:
            page.keyboard.press("Enter")
            print("  Pressed Enter to submit")

        time.sleep(3)
        page.wait_for_load_state("networkidle", timeout=20000)
        ss(page, "03_after_submit", "After submit")
        print(f"  URL after submit: {page.url}")

        # ----------------------------------------------------------------
        # STEP 2: Handle 2FA device verification
        # ----------------------------------------------------------------
        if "2fa" in page.url or "new-device" in page.url or "verify" in page.url.lower():
            print("\n[STEP 2] 2FA Device Verification detected")
            ss(page, "04_2fa_page", "2FA page")

            # Get code from email
            code = get_brevo_verification_code(max_wait=90)

            if not code:
                print("ERROR: Could not get verification code from email")
                ss(page, "error_no_2fa_code")
                browser.close()
                return None

            print(f"  Using verification code: {code}")

            # Enter the code
            code_field = wait_for_element(
                page,
                "input[type='text'], input[type='number'], input[placeholder*='code'], input[name*='code']",
                timeout=15000,
                description="Verification code input"
            )
            if not code_field:
                print("ERROR: Could not find code input field")
                ss(page, "error_no_code_field")
                browser.close()
                return None

            code_field.fill(code)
            time.sleep(0.5)
            ss(page, "05_code_entered", f"Code {code} entered")

            # Click Verify
            verify_btn = wait_for_element(
                page,
                "button:has-text('Verify'), button[type='submit']",
                description="Verify button"
            )
            if verify_btn:
                verify_btn.click()
                print("  Clicked Verify")
            else:
                page.keyboard.press("Enter")

            time.sleep(3)
            try:
                page.wait_for_load_state("networkidle", timeout=30000)
            except PlaywrightTimeout:
                pass

            ss(page, "06_after_2fa", "After 2FA verification")
            print(f"  URL after 2FA: {page.url}")

        else:
            print("\n[STEP 2] No 2FA required (already verified or logged in)")

        # Check if we're actually logged in now
        if "login" in page.url.lower():
            print("ERROR: Still on login page after attempted 2FA")
            ss(page, "error_still_on_login")
            browser.close()
            return None

        print(f"  Successfully logged in! URL: {page.url}")
        ss(page, "07_logged_in", "Logged in successfully")

        # ----------------------------------------------------------------
        # STEP 3: Navigate to Automation
        # ----------------------------------------------------------------
        print("\n[STEP 3] Navigating to Automation section")

        # Wait for the main app to load
        time.sleep(3)

        # Try clicking Automation in the navigation
        automation_found = False

        # Method 1: Look for nav links
        try:
            # Brevo's main nav
            nav_selectors = [
                "a[href*='automation']",
                "[data-key='automation']",
                "a:has-text('Automation')",
                "li:has-text('Automation') a",
            ]
            for sel in nav_selectors:
                try:
                    el = page.wait_for_selector(sel, timeout=5000)
                    if el:
                        el.click()
                        print(f"  Clicked automation nav via: {sel}")
                        automation_found = True
                        time.sleep(2)
                        break
                except PlaywrightTimeout:
                    continue
        except Exception as e:
            print(f"  Nav method 1 error: {e}")

        # Method 2: Direct URL
        if not automation_found or "automation" not in page.url.lower():
            print("  Trying direct URL navigation...")
            try:
                page.goto("https://automation.brevo.com/", wait_until="domcontentloaded", timeout=30000)
                time.sleep(3)
                print(f"  URL: {page.url}")
            except Exception as e:
                print(f"  Direct URL error: {e}")

        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except PlaywrightTimeout:
            pass

        ss(page, "08_automation_page", "Automation section")
        print(f"  Automation URL: {page.url}")

        # Capture page content to understand what we see
        try:
            page_text = page.inner_text("body")[:2000]
            print(f"  Page content preview:\n{page_text[:800]}")
        except Exception as e:
            print(f"  Could not read page text: {e}")

        # ----------------------------------------------------------------
        # STEP 4: Find and click "Create" button for new workflow
        # ----------------------------------------------------------------
        print("\n[STEP 4] Looking for workflow creation button")

        create_selectors = [
            "button:has-text('Create a workflow')",
            "button:has-text('Create workflow')",
            "button:has-text('Create')",
            "a:has-text('Create')",
            "[data-test='create-automation']",
            "button.create-btn",
            ".new-automation",
        ]

        create_btn = None
        for sel in create_selectors:
            try:
                el = page.wait_for_selector(sel, timeout=5000)
                if el:
                    create_btn = el
                    print(f"  Found create button: {sel}")
                    ss(page, "09_found_create_btn", f"Found create via: {sel}")
                    break
            except PlaywrightTimeout:
                continue

        if not create_btn:
            print("  Could not find create button - taking full page screenshot for analysis")
            ss(page, "09_no_create_btn", "No create button found")

            # Print all buttons and links visible
            try:
                buttons = page.query_selector_all("button, a[href]")
                print(f"  Visible buttons/links ({len(buttons)}):")
                for btn in buttons[:20]:
                    txt = btn.inner_text()[:50]
                    href = btn.get_attribute('href') or ''
                    if txt.strip():
                        print(f"    - '{txt}' href='{href}'")
            except Exception as e:
                print(f"  Could not list elements: {e}")

            browser.close()
            return {
                "status": "blocked_2fa_or_navigation",
                "message": "Could not find automation creation UI after login",
                "url": page.url,
                "screenshots_dir": SCREENSHOTS_DIR,
            }

        # Click create
        create_btn.scroll_into_view_if_needed()
        create_btn.click()
        print("  Clicked Create button")
        time.sleep(3)

        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except PlaywrightTimeout:
            pass

        ss(page, "10_after_create_click", "After clicking Create")
        print(f"  URL after Create: {page.url}")

        # ----------------------------------------------------------------
        # STEP 5: Configure workflow - set name and trigger
        # ----------------------------------------------------------------
        print("\n[STEP 5] Configuring workflow")

        # Look for name field
        try:
            name_field = page.wait_for_selector(
                "input[placeholder*='name'], input[name*='name'], input[aria-label*='name']",
                timeout=10000
            )
            name_field.triple_click()
            name_field.fill(WORKFLOW_NAME)
            print(f"  Set workflow name: {WORKFLOW_NAME}")
        except PlaywrightTimeout:
            print("  Could not find name field")

        ss(page, "11_workflow_name", "Workflow named")

        # Look for trigger configuration
        # Brevo automation trigger: "Contact added to a list"
        print("  Looking for trigger setup...")

        trigger_selectors = [
            "button:has-text('trigger')",
            "[data-test='trigger']",
            ".trigger-block",
            "button:has-text('Add trigger')",
            "button:has-text('Choose trigger')",
        ]

        for sel in trigger_selectors:
            try:
                el = page.wait_for_selector(sel, timeout=5000, state="visible")
                if el:
                    el.click()
                    print(f"  Clicked trigger via: {sel}")
                    time.sleep(2)
                    ss(page, "12_trigger_clicked", "Trigger clicked")
                    break
            except PlaywrightTimeout:
                continue

        # ----------------------------------------------------------------
        # STEP 6: Capture current state and analyze
        # ----------------------------------------------------------------
        print("\n[STEP 6] Analyzing current automation builder state")
        ss(page, "13_builder_state", "Automation builder state")

        try:
            page_text = page.inner_text("body")[:3000]
            print(f"  Builder content:\n{page_text[:1500]}")
        except Exception as e:
            print(f"  Could not read page: {e}")

        browser.close()

        return {
            "status": "partial",
            "message": "Logged in and reached automation builder - manual completion needed",
            "screenshots": [
                f"{SCREENSHOTS_DIR}/brevo_workflow_*.png"
            ]
        }


if __name__ == "__main__":
    result = run()
    print(f"\n{'='*65}")
    print("RESULT:")
    print(json.dumps(result, indent=2) if result else "No result")
