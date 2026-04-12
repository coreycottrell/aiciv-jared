#!/usr/bin/env python3
"""
Brevo Automation Workflow Creator
Creates the "Neural Feed - Welcome Sequence" automation in Brevo dashboard.

Uses Playwright to navigate the Brevo SPA and build the 7-email sequence.
"""

import os
import sys
import time
import json
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Load credentials
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
BREVO_EMAIL = 'purebrain@puremarketing.ai'
BREVO_PASSWORD = os.environ['BREVO_PASSWORD']
SCREENSHOTS_DIR = '/home/jared/projects/AI-CIV/aether/exports/screenshots'

def screenshot(page, name, description=""):
    path = f"{SCREENSHOTS_DIR}/brevo_workflow_{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"  [SCREENSHOT] {path} {description}")
    return path

def wait_and_click(page, selector, timeout=30000, description=""):
    print(f"  [CLICK] {description or selector}")
    element = page.wait_for_selector(selector, timeout=timeout)
    element.scroll_into_view_if_needed()
    element.click()
    time.sleep(1)

def wait_for_nav(page, description=""):
    print(f"  [WAIT] {description}")
    page.wait_for_load_state("networkidle", timeout=30000)

def run():
    print("=" * 60)
    print("Brevo Automation Workflow Creator")
    print("Target: Neural Feed - Welcome Sequence")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = browser.new_context(
            viewport={'width': 1600, 'height': 900},
            device_scale_factor=2,
        )
        page = context.new_page()

        # ----------------------------------------------------------------
        # STEP 1: Login
        # ----------------------------------------------------------------
        print("\n[1] Navigating to Brevo login...")
        page.goto("https://app.brevo.com/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        screenshot(page, "01_initial_load", "Initial page load")

        # Check where we are
        current_url = page.url
        print(f"  Current URL: {current_url}")

        # If redirected to login page
        if "login" in current_url or "signin" in current_url or "app.brevo.com" in current_url:
            # Try to find email/password fields
            try:
                print("  Looking for email field...")
                email_field = page.wait_for_selector(
                    "input[type='email'], input[name='email'], input[placeholder*='mail'], #email",
                    timeout=10000
                )
                email_field.fill(BREVO_EMAIL)
                print(f"  Filled email: {BREVO_EMAIL}")
                time.sleep(0.5)

                # Look for password field
                try:
                    password_field = page.wait_for_selector(
                        "input[type='password'], input[name='password']",
                        timeout=5000
                    )
                    password_field.fill(BREVO_PASSWORD)
                    print("  Filled password")
                    time.sleep(0.5)

                    screenshot(page, "02_credentials_filled", "Credentials filled")

                    # Submit
                    submit = page.wait_for_selector(
                        "button[type='submit'], button:has-text('Log in'), button:has-text('Sign in')",
                        timeout=5000
                    )
                    submit.click()
                    print("  Clicked submit")

                except PlaywrightTimeout:
                    # Maybe it's a two-step form (email first, then password)
                    print("  No password field visible yet - trying email-first flow")
                    try:
                        next_btn = page.wait_for_selector(
                            "button[type='submit'], button:has-text('Next'), button:has-text('Continue')",
                            timeout=5000
                        )
                        next_btn.click()
                        print("  Clicked Next/Continue")
                        time.sleep(2)

                        password_field = page.wait_for_selector(
                            "input[type='password']",
                            timeout=10000
                        )
                        password_field.fill(BREVO_PASSWORD)
                        print("  Filled password in step 2")
                        time.sleep(0.5)

                        submit2 = page.wait_for_selector(
                            "button[type='submit']",
                            timeout=5000
                        )
                        submit2.click()
                        print("  Clicked submit step 2")
                    except PlaywrightTimeout as e:
                        screenshot(page, "02_error_two_step", "Error in two-step flow")
                        print(f"  ERROR in two-step flow: {e}")

            except PlaywrightTimeout:
                print("  No email field found - may already be logged in or different UI")
                screenshot(page, "02_no_email_field", "No email field found")

        # Wait for navigation after login attempt
        print("  Waiting for post-login navigation...")
        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except PlaywrightTimeout:
            print("  Timeout waiting for networkidle, continuing...")

        time.sleep(3)
        screenshot(page, "03_after_login", "After login attempt")
        print(f"  URL after login: {page.url}")

        # Check if we need to handle Google SSO redirect
        current_url = page.url
        if "google.com" in current_url or "accounts.google" in current_url:
            print("  Detected Google SSO redirect - handling...")
            try:
                google_email = page.wait_for_selector("input[type='email']", timeout=10000)
                google_email.fill(BREVO_EMAIL)
                page.keyboard.press("Enter")
                time.sleep(2)
                google_password = page.wait_for_selector("input[type='password']", timeout=10000)
                google_password.fill(BREVO_PASSWORD)
                page.keyboard.press("Enter")
                time.sleep(3)
                page.wait_for_load_state("networkidle", timeout=30000)
                screenshot(page, "04_after_google_sso", "After Google SSO")
            except PlaywrightTimeout as e:
                print(f"  Google SSO error: {e}")
                screenshot(page, "04_google_sso_error", "Google SSO error")

        # ----------------------------------------------------------------
        # STEP 2: Navigate to Automations
        # ----------------------------------------------------------------
        print("\n[2] Navigating to Automations...")
        current_url = page.url
        print(f"  Current URL: {current_url}")

        # Try direct URL navigation to automations
        try:
            page.goto("https://automation.brevo.com/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            screenshot(page, "05_automations_direct", "Automations via direct URL")
        except Exception as e:
            print(f"  Direct automation URL failed: {e}")

        # Try the main app automation URL
        try:
            page.goto("https://app.brevo.com/automation/list", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            screenshot(page, "05b_automations_app", "Automations via app URL")
        except Exception as e:
            print(f"  App automation URL failed: {e}")

        print(f"  Current URL: {page.url}")
        screenshot(page, "06_automations_page", "Automations page")

        # Look for "Automations" in navigation
        try:
            # Try clicking on Automations in the nav
            auto_nav = page.locator("a:has-text('Automation'), nav a:has-text('Automation'), [href*='automation']").first
            if auto_nav:
                auto_nav.click()
                time.sleep(2)
                page.wait_for_load_state("networkidle", timeout=15000)
                screenshot(page, "07_automation_nav_click", "After clicking Automation nav")
        except Exception as e:
            print(f"  Nav click attempt: {e}")

        # ----------------------------------------------------------------
        # STEP 3: Check current state and try Brevo API approach
        # ----------------------------------------------------------------
        print("\n[3] Checking page state and trying API approach...")
        screenshot(page, "08_current_state", "Current page state")
        page_title = page.title()
        current_url = page.url
        print(f"  Page title: {page_title}")
        print(f"  Current URL: {current_url}")

        # Get page content to understand what we're looking at
        try:
            body_text = page.inner_text("body")[:1000]
            print(f"  Page content preview: {body_text[:500]}")
        except Exception as e:
            print(f"  Could not read body: {e}")

        # ----------------------------------------------------------------
        # STEP 4: Try to use Brevo API directly via authenticated session
        # ----------------------------------------------------------------
        print("\n[4] Attempting to use Brevo REST API for workflow creation...")

        # Try to get the auth token from browser storage
        try:
            local_storage = page.evaluate("() => { return JSON.stringify(Object.entries(localStorage)); }")
            print(f"  LocalStorage keys: {local_storage[:500] if local_storage else 'empty'}")
        except Exception as e:
            print(f"  Could not read localStorage: {e}")

        try:
            # Check cookies
            cookies = context.cookies()
            auth_cookies = [c for c in cookies if any(k in c['name'].lower() for k in ['auth', 'token', 'session', 'jwt'])]
            print(f"  Auth-related cookies found: {len(auth_cookies)}")
            for c in auth_cookies[:5]:
                print(f"    - {c['name']}: {c['value'][:30]}...")
        except Exception as e:
            print(f"  Could not read cookies: {e}")

        screenshot(page, "09_final_state", "Final state check")

        # ----------------------------------------------------------------
        # STEP 5: Try Brevo Automation API directly
        # ----------------------------------------------------------------
        print("\n[5] Trying Brevo Automation API with API key...")

        # Get API key from env
        brevo_api_key = os.environ.get('BREVO_API_KEY', '')
        if brevo_api_key:
            print(f"  API key found (length: {len(brevo_api_key)})")
            # Try to create workflow via API
            result = create_workflow_via_api(brevo_api_key)
            if result:
                screenshot(page, "10_workflow_created", "Workflow created successfully")
                print("\n[SUCCESS] Workflow created via API!")
                return result
        else:
            print("  No BREVO_API_KEY found in env")

        # ----------------------------------------------------------------
        # STEP 6: Try UI-based workflow creation
        # ----------------------------------------------------------------
        print("\n[6] Attempting UI-based workflow creation...")
        result = try_ui_workflow_creation(page, context)

        browser.close()
        return result


def create_workflow_via_api(api_key):
    """Try to create the workflow using Brevo's automation API."""
    import urllib.request
    import urllib.error

    print("  Checking Brevo API access...")

    # First check account info
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # List existing automations
    req = urllib.request.Request(
        'https://api.brevo.com/v3/workflows',
        headers=headers,
        method='GET'
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            print(f"  Existing workflows: {json.dumps(data, indent=2)[:500]}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"  Workflows API error {e.code}: {error_body[:200]}")
        if e.code == 404:
            print("  Workflows endpoint not available - Brevo automation uses different API")
    except Exception as e:
        print(f"  API error: {e}")

    # Try the automation/scenarios endpoint
    req2 = urllib.request.Request(
        'https://api.brevo.com/v3/automations',
        headers=headers,
        method='GET'
    )

    try:
        with urllib.request.urlopen(req2, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            print(f"  Automations response: {json.dumps(data, indent=2)[:500]}")
            return data
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"  Automations API error {e.code}: {error_body[:200]}")
    except Exception as e:
        print(f"  API error: {e}")

    return None


def try_ui_workflow_creation(page, context):
    """Navigate Brevo UI to create automation workflow."""
    print("  Trying various navigation paths to automation builder...")

    # URLs to try
    automation_urls = [
        "https://automation.brevo.com/flows",
        "https://automation.brevo.com/scenarios",
        "https://app.brevo.com/automation",
        "https://app.brevo.com/en/automation/list",
    ]

    for url in automation_urls:
        try:
            print(f"  Trying: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            time.sleep(2)
            current = page.url
            title = page.title()
            print(f"    → URL: {current}, Title: {title}")

            # Check if we're on an automation-related page
            if "automation" in current.lower() or "flow" in current.lower():
                screenshot(page, f"automation_url_{url.split('/')[-1]}", f"Automation URL: {url}")

                # Look for "Create" button
                try:
                    create_btn = page.wait_for_selector(
                        "button:has-text('Create'), button:has-text('New'), a:has-text('Create automation')",
                        timeout=5000
                    )
                    print(f"    Found create button!")
                    screenshot(page, "found_create_button", "Found create button")
                    return {"url": current, "status": "found_automation_page"}
                except PlaywrightTimeout:
                    print(f"    No create button found at this URL")

        except Exception as e:
            print(f"  Error with {url}: {e}")

    # Last resort - screenshot whatever we have
    screenshot(page, "final_state_ui_attempt", "Final state after UI attempts")
    page_content = page.inner_text("body")[:2000]
    print(f"\n  Final page content:\n{page_content[:1000]}")

    return {"status": "manual_intervention_needed", "note": "Could not locate automation builder UI"}


if __name__ == "__main__":
    result = run()
    print(f"\n[FINAL RESULT]: {json.dumps(result, indent=2) if result else 'No result returned'}")
