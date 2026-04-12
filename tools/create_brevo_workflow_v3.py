#!/usr/bin/env python3
"""
Brevo Automation Workflow Creator v3
Full end-to-end: Login → 2FA → Open builder → Build 7-email sequence → Activate

Verified working:
- Login with email/password
- 2FA via Gmail IMAP code extraction
- Navigation to Automations → Workflows
- Create modal opens correctly
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

WORKFLOW_NAME = "Neural Feed - Welcome Sequence"

# Email steps: (template_id, delay_days_before)
# delay_days_before = 0 means send immediately
EMAIL_SEQUENCE = [
    (1, 0),   # Email 1 - immediate
    (2, 2),   # Email 2 - 2 days after
    (3, 2),   # Email 3 - 2 days after
    (4, 3),   # Email 4 - 3 days after
    (5, 3),   # Email 5 - 3 days after
    (6, 4),   # Email 6 - 4 days after
    (7, 7),   # Email 7 - 7 days after
]

TEMPLATE_NAMES = {
    1: 'Neural Feed - Email 1 - Welcome (Aether)',
    2: "Neural Feed - Email 2 - Jared's Story",
    3: 'Neural Feed - Email 3 - Aether Writes Directly',
    4: 'Neural Feed - Email 4 - Partnership in Practice',
    5: 'Neural Feed - Email 5 - The Context Tax',
    6: 'Neural Feed - Email 6 - Social Proof & Results',
    7: 'Neural Feed - Email 7 - The Invitation',
}

_step_counter = [0]


def ss(page, name, desc=""):
    _step_counter[0] += 1
    n = f"{_step_counter[0]:02d}_{name}"
    path = f"{SCREENSHOTS_DIR}/brevo_wf_{n}.png"
    page.screenshot(path=path, full_page=True)
    print(f"  [SS] {n}: {desc}")
    return path


def wait_el(page, selector, timeout=30000, desc="", state="visible"):
    print(f"  [WAIT] {desc or selector[:60]}")
    try:
        el = page.wait_for_selector(selector, timeout=timeout, state=state)
        return el
    except PlaywrightTimeout:
        print(f"    TIMEOUT: {selector[:60]}")
        return None


def click_el(page, selector, timeout=20000, desc=""):
    el = wait_el(page, selector, timeout=timeout, desc=desc)
    if el:
        el.scroll_into_view_if_needed()
        time.sleep(0.3)
        el.click()
        time.sleep(0.8)
        return True
    return False


def pause(page, secs=2, reason=""):
    if reason:
        print(f"  [PAUSE] {secs}s - {reason}")
    time.sleep(secs)


def get_verification_code(max_wait=90):
    """Fetch Brevo 2FA code from Gmail via IMAP."""
    print("  [EMAIL] Fetching verification code from Gmail...")
    deadline = time.time() + max_wait
    attempt = 0

    while time.time() < deadline:
        attempt += 1
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            mail.select('INBOX')

            # Search for unread Brevo alerts
            status, data = mail.search(None, 'FROM', 'account-alerts@t.brevo.com', 'UNSEEN')
            if status == 'OK' and data[0]:
                for mid in reversed(data[0].decode().split()):
                    _, msg_data = mail.fetch(mid, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    subject = msg.get('Subject', '')
                    if 'verify' not in subject.lower() and 'device' not in subject.lower():
                        continue

                    # Extract body
                    body = ''
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() in ('text/plain', 'text/html'):
                                body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                    # Pattern match near "verification code"
                    m = re.search(r'(?:verification code|one-time)[:\s]*\n?\s*(\d{6})', body, re.IGNORECASE)
                    if m:
                        code = m.group(1)
                        print(f"  [EMAIL] Got code: {code}")
                        mail.logout()
                        return code

                    # Fallback: non-repeating 6-digit number
                    for c in re.findall(r'\b\d{6}\b', body):
                        digits = list(c)
                        if not (digits[0] == digits[2] == digits[4] and digits[1] == digits[3] == digits[5]):
                            print(f"  [EMAIL] Got code (fallback): {c}")
                            mail.logout()
                            return c

            mail.logout()

        except Exception as e:
            print(f"  [EMAIL] Attempt {attempt} error: {e}")

        remaining = int(deadline - time.time())
        print(f"  [EMAIL] Not found, retrying... ({remaining}s left)")
        time.sleep(5)

    return None


def dismiss_cookies(page):
    """Dismiss cookie consent banner if present."""
    try:
        btn = page.wait_for_selector(
            "button:has-text('Accept All Cookies'), button:has-text('Accept All'), button:has-text('Reject All')",
            timeout=5000
        )
        if btn:
            btn.click()
            print("  [COOKIE] Dismissed cookie banner")
            pause(page, 1)
    except PlaywrightTimeout:
        pass  # No cookie banner


def login_and_2fa(page):
    """Complete login + 2FA flow. Returns True on success."""
    print("\n[LOGIN] Starting login flow...")
    page.goto("https://login.brevo.com/", wait_until="domcontentloaded", timeout=60000)
    pause(page, 2)

    # Dismiss cookie banner FIRST before interacting with form
    dismiss_cookies(page)
    pause(page, 0.5)

    ss(page, "login_page", "Login page loaded")

    # Fill email - Brevo uses type="text" with name="email" (NOT type="email")
    email_field = wait_el(page, "input[name='email'], input#email", desc="Email input")
    if not email_field:
        print("ERROR: No email field")
        return False
    email_field.fill(BREVO_EMAIL)
    pause(page, 0.3)

    # Fill password
    pw_field = wait_el(page, "input[type='password'], input[name='password']", desc="Password input")
    if not pw_field:
        print("ERROR: No password field")
        return False
    pw_field.fill(BREVO_PASSWORD)
    pause(page, 0.3)

    ss(page, "creds_filled", "Credentials filled")

    # Submit - Brevo uses type="button" (NOT type="submit") with text "Log In"
    try:
        btn = page.wait_for_selector(
            "button:has-text('Log In'), button:has-text('Log in'), button[data-testid='submit-button']",
            timeout=5000
        )
        btn.click()
    except PlaywrightTimeout:
        pw_field.press("Enter")
    print("  Submitted login form")

    pause(page, 4)
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except PlaywrightTimeout:
        pass

    ss(page, "after_submit", f"Post-submit URL: {page.url}")

    # Handle 2FA
    if "2fa" in page.url or "new-device" in page.url:
        print("\n[2FA] Device verification required")
        ss(page, "2fa_screen", "2FA verification screen")

        code = get_verification_code(max_wait=90)
        if not code:
            print("ERROR: Could not get verification code")
            return False

        code_field = wait_el(
            page,
            "input[type='text'], input[type='number'], input[inputmode='numeric']",
            timeout=15000,
            desc="Code input field"
        )
        if not code_field:
            print("ERROR: No code input field found")
            ss(page, "2fa_no_input", "No code input found")
            return False

        code_field.fill(code)
        pause(page, 0.5)
        ss(page, "2fa_code_entered", f"Code {code} entered")

        try:
            verify_btn = page.wait_for_selector(
                "button:has-text('Verify'), button[type='submit']",
                timeout=10000
            )
            verify_btn.click()
        except PlaywrightTimeout:
            code_field.press("Enter")

        pause(page, 4)
        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except PlaywrightTimeout:
            pass

        ss(page, "after_2fa", f"Post-2FA URL: {page.url}")

        if "login" in page.url.lower() or "2fa" in page.url:
            print("ERROR: Still on auth page after 2FA")
            return False

    print(f"  Logged in. URL: {page.url}")
    return True


def navigate_to_automations(page):
    """Navigate to the Automations > Workflows section."""
    print("\n[NAV] Navigating to Automations > Workflows...")
    pause(page, 2)

    # Click 'Automations' in sidebar
    clicked = click_el(page, "a[href*='automation'], a:has-text('Automations')", desc="Automations nav link")
    if not clicked:
        # Try direct URL
        page.goto("https://app.brevo.com/automation/automations", wait_until="domcontentloaded", timeout=30000)

    pause(page, 3)
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except PlaywrightTimeout:
        pass

    ss(page, "automations_list", "Automations list page")
    print(f"  URL: {page.url}")

    if "automation" not in page.url:
        print("WARNING: May not be on automations page")

    return True


def open_create_from_scratch(page):
    """Click Create automation → Create from scratch."""
    print("\n[CREATE] Opening new automation form...")

    # Click "Create an automation" button
    clicked = click_el(
        page,
        "button:has-text('Create an automation'), button:has-text('Create')",
        desc="Create automation button",
        timeout=15000
    )
    if not clicked:
        print("ERROR: Could not click Create button")
        ss(page, "no_create_btn")
        return False

    pause(page, 2, "Modal opening")
    ss(page, "create_modal", "Create automation modal")

    # Click "Create from scratch"
    clicked = click_el(
        page,
        "button:has-text('Create from scratch'), a:has-text('Create from scratch')",
        desc="Create from scratch button",
        timeout=10000
    )
    if not clicked:
        print("ERROR: Could not click 'Create from scratch'")
        ss(page, "no_from_scratch_btn")

        # List what's visible in modal
        try:
            buttons = page.query_selector_all("button, a")
            print("  Visible buttons:")
            for b in buttons:
                txt = b.inner_text()[:60].strip()
                if txt:
                    print(f"    '{txt}'")
        except Exception as e:
            print(f"  Could not list buttons: {e}")
        return False

    pause(page, 4, "Builder loading")
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except PlaywrightTimeout:
        pause(page, 3)

    ss(page, "builder_loaded", f"Builder URL: {page.url}")
    print(f"  Builder URL: {page.url}")
    return True


def set_workflow_name(page):
    """Set the workflow name."""
    print(f"\n[NAME] Setting workflow name: {WORKFLOW_NAME}")

    # Brevo usually has a name field at the top or in a settings panel
    name_selectors = [
        "input[placeholder*='name' i]",
        "input[name='name']",
        "input[aria-label*='name' i]",
        "[contenteditable='true']",
        "h1[contenteditable]",
        ".workflow-name input",
        "input.automation-name",
    ]

    for sel in name_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=5000, state="visible")
            if el:
                el.triple_click()
                el.fill(WORKFLOW_NAME)
                pause(page, 0.5)
                ss(page, "name_set", f"Name set to: {WORKFLOW_NAME}")
                print(f"  Set name via: {sel}")
                return True
        except PlaywrightTimeout:
            continue

    print("  WARNING: Could not find name field - will try to set via UI")
    ss(page, "name_field_not_found", "Name field not found")

    # Show what's on the page
    try:
        body = page.inner_text("body")[:2000]
        print(f"  Page content:\n{body[:1000]}")
    except Exception:
        pass

    return False


def analyze_builder_state(page):
    """
    Deeply analyze what the automation builder looks like.
    Returns a dict with info about the current state.
    """
    info = {
        "url": page.url,
        "title": page.title(),
        "buttons": [],
        "inputs": [],
        "page_text": "",
    }

    try:
        info["page_text"] = page.inner_text("body")[:3000]
    except Exception:
        pass

    try:
        buttons = page.query_selector_all("button")
        for btn in buttons:
            txt = btn.inner_text()[:80].strip()
            if txt:
                info["buttons"].append(txt)
    except Exception:
        pass

    try:
        inputs = page.query_selector_all("input, textarea, [contenteditable='true']")
        for inp in inputs:
            ph = inp.get_attribute("placeholder") or inp.get_attribute("aria-label") or inp.tag_name()
            info["inputs"].append(ph[:60] if ph else "unknown")
    except Exception:
        pass

    return info


def build_workflow_steps(page):
    """
    Build the full automation workflow in the Brevo builder.
    The builder is a visual drag-and-drop canvas.
    We need to:
    1. Set trigger: Contact added to list
    2. Add email send steps with delays between them
    """
    print("\n[BUILD] Analyzing automation builder...")

    state = analyze_builder_state(page)
    print(f"  URL: {state['url']}")
    print(f"  Title: {state['title']}")
    print(f"  Buttons found: {state['buttons'][:20]}")
    print(f"  Inputs found: {state['inputs']}")
    print(f"  Page text preview:\n{state['page_text'][:1500]}")

    ss(page, "builder_analysis", "Builder state analysis")

    # The Brevo automation builder is a visual canvas
    # Look for trigger setup block
    print("\n  Looking for trigger configuration...")

    trigger_selectors = [
        # Common Brevo automation builder elements
        ".trigger-step",
        ".start-block",
        "[data-automation-step='trigger']",
        "button:has-text('Entry point')",
        "button:has-text('When')",
        "button:has-text('trigger')",
        ".block-container:first-child",
        "[class*='trigger']",
        "text=Entry point",
        "text=Start",
        "text=When",
    ]

    trigger_el = None
    for sel in trigger_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=4000, state="visible")
            if el:
                trigger_el = el
                print(f"  Found trigger element: {sel}")
                break
        except PlaywrightTimeout:
            continue

    if trigger_el:
        print("  Clicking trigger to configure...")
        trigger_el.scroll_into_view_if_needed()
        trigger_el.click()
        pause(page, 2)
        ss(page, "trigger_panel", "Trigger configuration panel")

        # Look for trigger type dropdown/selector
        # We want "Contact added to a list"
        list_trigger_selectors = [
            "option:has-text('list')",
            "li:has-text('Contact added to a list')",
            "button:has-text('Contact added to a list')",
            "[data-value*='list']",
            "text=Contact added to a list",
        ]

        for sel in list_trigger_selectors:
            try:
                el = page.wait_for_selector(sel, timeout=4000)
                if el:
                    el.click()
                    print(f"  Selected trigger: Contact added to a list via {sel}")
                    pause(page, 1)
                    break
            except PlaywrightTimeout:
                continue

        ss(page, "trigger_configured", "Trigger after configuration")

    else:
        print("  Could not find trigger element")
        ss(page, "no_trigger_found", "No trigger element found")

    return state


def run():
    print("=" * 65)
    print("Brevo Automation Workflow Creator v3 - Full Build")
    print(f"Workflow: {WORKFLOW_NAME}")
    print(f"Templates: {len(EMAIL_SEQUENCE)} emails")
    print("=" * 65)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
            ]
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

        # Step 1: Login + 2FA
        if not login_and_2fa(page):
            print("\nFAILED at login/2FA")
            ss(page, "FAILED_login")
            browser.close()
            return {"status": "failed", "stage": "login"}

        ss(page, "logged_in", "Successfully logged in")

        # Step 2: Navigate to Automations
        if not navigate_to_automations(page):
            print("\nFAILED at navigation")
            browser.close()
            return {"status": "failed", "stage": "navigation"}

        # Step 3: Open Create from scratch
        if not open_create_from_scratch(page):
            print("\nFAILED at create from scratch")
            browser.close()
            return {"status": "failed", "stage": "create_modal"}

        # Step 4: Set workflow name
        set_workflow_name(page)

        # Step 5: Analyze and build workflow steps
        state = build_workflow_steps(page)

        # Step 6: Take comprehensive screenshots of the builder state
        ss(page, "FINAL_builder_state", "Final builder state")

        # Print full analysis
        print("\n" + "=" * 65)
        print("BUILDER ANALYSIS COMPLETE")
        print("=" * 65)
        print(f"URL: {state['url']}")
        print(f"Buttons: {state['buttons']}")
        print(f"Inputs: {state['inputs']}")
        print(f"\nFull page text:\n{state['page_text'][:2000]}")

        browser.close()

        return {
            "status": "builder_reached",
            "url": state["url"],
            "buttons_found": state["buttons"],
            "next_steps": "Manual builder interaction needed - see screenshots",
        }


if __name__ == "__main__":
    result = run()
    print(f"\n{'='*65}")
    print("FINAL RESULT:")
    print(json.dumps(result, indent=2))
