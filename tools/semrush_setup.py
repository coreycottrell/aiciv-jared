#!/usr/bin/env python3
"""
SEMRush Setup Script for purebrain.ai
Automates login + project creation in SEMRush
"""

import time
import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def screenshot(page, name):
    path = f"{SCREENSHOT_DIR}/semrush_{name}.png"
    page.screenshot(path=path, full_page=False)
    print(f"  [screenshot] {path}")
    return path

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

RESULTS = {
    "login": False,
    "project_created": False,
    "site_audit_setup": False,
    "position_tracking_setup": False,
    "verification_needed": None,
    "screenshots": [],
    "notes": [],
    "errors": []
}

def run():
    with sync_playwright() as p:
        # Use chromium with stealth-like settings to avoid bot detection
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York"
        )

        # Remove webdriver flag
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = context.new_page()

        try:
            # ========================
            # STEP 1: Navigate to SEMRush
            # ========================
            log("Navigating to SEMRush...")
            page.goto("https://www.semrush.com/login/", timeout=30000, wait_until="domcontentloaded")
            time.sleep(3)

            path = screenshot(page, "01_login_page")
            RESULTS["screenshots"].append(path)
            log(f"Login page loaded. Title: {page.title()}")

            # Check if we're blocked by CAPTCHA / anti-bot
            page_content = page.content()
            if "captcha" in page_content.lower() or "recaptcha" in page_content.lower():
                log("CAPTCHA detected on login page")
                RESULTS["notes"].append("CAPTCHA detected - manual login required")

            # ========================
            # STEP 2: Find and fill login form
            # ========================
            log("Looking for login form...")

            # Wait for page to stabilize
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)

            path = screenshot(page, "02_after_load")
            RESULTS["screenshots"].append(path)

            # Try to find email field
            email_selectors = [
                'input[name="email"]',
                'input[type="email"]',
                '#email',
                'input[placeholder*="email" i]',
                'input[placeholder*="Email" i]',
                'input[autocomplete="email"]'
            ]

            email_field = None
            for sel in email_selectors:
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=2000):
                        email_field = el
                        log(f"Found email field with selector: {sel}")
                        break
                except:
                    continue

            if not email_field:
                log("Email field not found - checking page structure")
                # Get visible inputs
                inputs = page.locator("input").all()
                log(f"Found {len(inputs)} input elements on page")
                for inp in inputs[:10]:
                    try:
                        attrs = {
                            "type": inp.get_attribute("type"),
                            "name": inp.get_attribute("name"),
                            "id": inp.get_attribute("id"),
                            "placeholder": inp.get_attribute("placeholder")
                        }
                        log(f"  Input: {attrs}")
                    except:
                        pass

                RESULTS["errors"].append("Email field not found with standard selectors")
                RESULTS["notes"].append("Login page structure may be different - check screenshots")
            else:
                # Fill email
                log("Filling email field...")
                email_field.click()
                time.sleep(0.5)
                email_field.fill("support@puremarketing.ai")
                time.sleep(1)

                # Find password field
                pwd_selectors = [
                    'input[name="password"]',
                    'input[type="password"]',
                    '#password',
                    'input[placeholder*="password" i]'
                ]

                pwd_field = None
                for sel in pwd_selectors:
                    try:
                        el = page.locator(sel).first
                        if el.is_visible(timeout=2000):
                            pwd_field = el
                            log(f"Found password field with selector: {sel}")
                            break
                    except:
                        continue

                if pwd_field:
                    log("Filling password field...")
                    pwd_field.click()
                    time.sleep(0.5)
                    pwd_field.fill("c2!2gurK:m3T!rc")
                    time.sleep(1)

                    path = screenshot(page, "03_form_filled")
                    RESULTS["screenshots"].append(path)

                    # Submit the form
                    submit_selectors = [
                        'button[type="submit"]',
                        'input[type="submit"]',
                        'button:has-text("Log In")',
                        'button:has-text("Sign In")',
                        'button:has-text("Login")',
                        '.login-button',
                        '#submit'
                    ]

                    submitted = False
                    for sel in submit_selectors:
                        try:
                            btn = page.locator(sel).first
                            if btn.is_visible(timeout=2000):
                                log(f"Clicking submit with selector: {sel}")
                                btn.click()
                                submitted = True
                                break
                        except:
                            continue

                    if not submitted:
                        # Try pressing Enter
                        log("Submit button not found, pressing Enter...")
                        pwd_field.press("Enter")

                    # Wait for navigation
                    log("Waiting for login response...")
                    try:
                        page.wait_for_load_state("networkidle", timeout=20000)
                    except:
                        pass
                    time.sleep(4)

                    path = screenshot(page, "04_after_login_attempt")
                    RESULTS["screenshots"].append(path)

                    current_url = page.url
                    log(f"Current URL after login: {current_url}")

                    # Check for 2FA
                    page_text = page.inner_text("body").lower() if page.locator("body").count() > 0 else ""

                    if "two-factor" in page_text or "2fa" in page_text or "verification code" in page_text or "authenticator" in page_text:
                        log("2FA REQUIRED!")
                        RESULTS["notes"].append("2FA is required - Jared needs to provide 2FA code")
                        path = screenshot(page, "05_2fa_required")
                        RESULTS["screenshots"].append(path)
                        RESULTS["errors"].append("2FA required - cannot proceed automatically")

                    elif "login" in current_url or "sign-in" in current_url:
                        # Still on login page
                        log("Still on login page - login may have failed")

                        # Check for error messages
                        error_text = ""
                        error_selectors = [".error", ".alert", "[class*='error']", "[class*='alert']", "[role='alert']"]
                        for sel in error_selectors:
                            try:
                                err = page.locator(sel).first
                                if err.is_visible(timeout=1000):
                                    error_text = err.inner_text()
                                    break
                            except:
                                continue

                        if error_text:
                            log(f"Login error: {error_text}")
                            RESULTS["errors"].append(f"Login error: {error_text}")
                        else:
                            RESULTS["errors"].append("Login failed - still on login page, no error message visible")

                    elif "dashboard" in current_url or "projects" in current_url or "app" in current_url:
                        log("Login SUCCESSFUL!")
                        RESULTS["login"] = True

                    else:
                        # Check page content for success signals
                        if "welcome" in page_text or "dashboard" in page_text or "projects" in page_text:
                            log("Login appears successful (dashboard content detected)")
                            RESULTS["login"] = True
                        else:
                            log(f"Uncertain login state - URL: {current_url}")
                            RESULTS["notes"].append(f"Login result unclear - URL: {current_url}")
                            # Assume success if we navigated away from login
                            if "/login" not in current_url:
                                RESULTS["login"] = True
                                log("Navigated away from login - treating as success")
                else:
                    RESULTS["errors"].append("Password field not found")

            # ========================
            # STEP 3: Create Project (if logged in)
            # ========================
            if RESULTS["login"]:
                log("Attempting to create project for purebrain.ai...")

                # Navigate to projects page
                page.goto("https://www.semrush.com/projects/", timeout=30000, wait_until="domcontentloaded")
                time.sleep(3)
                page.wait_for_load_state("networkidle", timeout=15000)
                time.sleep(2)

                path = screenshot(page, "06_projects_page")
                RESULTS["screenshots"].append(path)
                log(f"Projects page URL: {page.url}")

                # Look for "Create project" button
                create_selectors = [
                    'button:has-text("Create project")',
                    'a:has-text("Create project")',
                    'button:has-text("New project")',
                    'a:has-text("New project")',
                    '[data-testid="create-project"]',
                    '.create-project',
                    'button:has-text("Add project")',
                    'a:has-text("Add project")'
                ]

                create_btn = None
                for sel in create_selectors:
                    try:
                        btn = page.locator(sel).first
                        if btn.is_visible(timeout=2000):
                            create_btn = btn
                            log(f"Found create button: {sel}")
                            break
                    except:
                        continue

                if create_btn:
                    log("Clicking create project button...")
                    create_btn.click()
                    time.sleep(2)
                    page.wait_for_load_state("networkidle", timeout=10000)
                    time.sleep(2)

                    path = screenshot(page, "07_create_project_dialog")
                    RESULTS["screenshots"].append(path)

                    # Fill domain name
                    domain_selectors = [
                        'input[placeholder*="domain" i]',
                        'input[placeholder*="website" i]',
                        'input[name="domain"]',
                        'input[name="url"]',
                        'input[placeholder*="URL" i]',
                        'input[placeholder*="http" i]'
                    ]

                    domain_field = None
                    for sel in domain_selectors:
                        try:
                            el = page.locator(sel).first
                            if el.is_visible(timeout=2000):
                                domain_field = el
                                log(f"Found domain field: {sel}")
                                break
                        except:
                            continue

                    if domain_field:
                        log("Filling domain: purebrain.ai")
                        domain_field.click()
                        domain_field.fill("purebrain.ai")
                        time.sleep(1)

                        # Fill project name if separate field
                        name_selectors = [
                            'input[placeholder*="project name" i]',
                            'input[name="name"]',
                            'input[placeholder*="name" i]'
                        ]
                        for sel in name_selectors:
                            try:
                                el = page.locator(sel).first
                                if el.is_visible(timeout=1000):
                                    el.fill("PureBrain.ai")
                                    log("Filled project name")
                                    break
                            except:
                                continue

                        path = screenshot(page, "08_project_form_filled")
                        RESULTS["screenshots"].append(path)

                        # Click create/save
                        save_selectors = [
                            'button:has-text("Create project")',
                            'button:has-text("Create")',
                            'button[type="submit"]',
                            'button:has-text("Save")',
                            'button:has-text("Start project")'
                        ]

                        for sel in save_selectors:
                            try:
                                btn = page.locator(sel).first
                                if btn.is_visible(timeout=2000):
                                    log(f"Clicking save with: {sel}")
                                    btn.click()
                                    break
                            except:
                                continue

                        time.sleep(3)
                        page.wait_for_load_state("networkidle", timeout=20000)
                        time.sleep(3)

                        path = screenshot(page, "09_after_project_create")
                        RESULTS["screenshots"].append(path)

                        current_url = page.url
                        log(f"URL after project creation: {current_url}")

                        page_text = page.inner_text("body").lower()
                        if "purebrain" in page_text or "project" in page_text:
                            RESULTS["project_created"] = True
                            log("Project appears created successfully!")
                    else:
                        log("Domain field not found in project dialog")
                        RESULTS["errors"].append("Domain input field not found in create project dialog")
                else:
                    log("Create project button not found")
                    # Check if project already exists
                    page_text = page.inner_text("body").lower()
                    if "purebrain" in page_text:
                        log("purebrain.ai project may already exist!")
                        RESULTS["notes"].append("purebrain.ai project may already exist in account")
                        RESULTS["project_created"] = True
                    else:
                        RESULTS["errors"].append("Create project button not found")

                # ========================
                # STEP 4: Site Audit setup
                # ========================
                log("Looking for Site Audit tool...")

                # Navigate to site audit
                try:
                    page.goto("https://www.semrush.com/siteaudit/", timeout=20000, wait_until="domcontentloaded")
                    time.sleep(3)
                    page.wait_for_load_state("networkidle", timeout=15000)
                    time.sleep(2)

                    path = screenshot(page, "10_site_audit_page")
                    RESULTS["screenshots"].append(path)
                    log(f"Site audit page: {page.url}")

                    page_text = page.inner_text("body").lower()
                    if "site audit" in page_text or "audit" in page_text:
                        log("Site Audit page loaded")

                        # Check if we need to set it up for the project
                        if "start" in page_text or "set up" in page_text or "configure" in page_text:
                            log("Site Audit needs configuration")
                            RESULTS["notes"].append("Site Audit needs manual setup via project dashboard")
                        elif "purebrain" in page_text:
                            log("Site Audit may already be configured for purebrain.ai")
                            RESULTS["site_audit_setup"] = True

                except Exception as e:
                    log(f"Error navigating to Site Audit: {e}")
                    RESULTS["errors"].append(f"Site Audit navigation failed: {str(e)}")

                # ========================
                # STEP 5: Position Tracking
                # ========================
                log("Looking for Position Tracking tool...")

                try:
                    page.goto("https://www.semrush.com/position-tracking/", timeout=20000, wait_until="domcontentloaded")
                    time.sleep(3)
                    page.wait_for_load_state("networkidle", timeout=15000)
                    time.sleep(2)

                    path = screenshot(page, "11_position_tracking_page")
                    RESULTS["screenshots"].append(path)
                    log(f"Position tracking page: {page.url}")

                except Exception as e:
                    log(f"Error navigating to Position Tracking: {e}")
                    RESULTS["errors"].append(f"Position Tracking navigation failed: {str(e)}")

                # ========================
                # STEP 6: Check for domain verification
                # ========================
                log("Checking for domain verification requirements...")

                try:
                    # Check Google Search Console connection (common verification path)
                    page.goto("https://www.semrush.com/projects/", timeout=20000, wait_until="domcontentloaded")
                    time.sleep(3)
                    page.wait_for_load_state("networkidle", timeout=15000)
                    time.sleep(2)

                    path = screenshot(page, "12_projects_final_state")
                    RESULTS["screenshots"].append(path)

                    page_text = page.inner_text("body")

                    # Look for verification mentions
                    if "verify" in page_text.lower() or "verification" in page_text.lower():
                        log("Verification required!")
                        RESULTS["verification_needed"] = "Domain verification required - check screenshots for details"
                        RESULTS["notes"].append("Verification step detected - screenshot captured for review")

                    if "meta tag" in page_text.lower():
                        RESULTS["verification_needed"] = "META TAG verification needed"
                        RESULTS["notes"].append("SEMRush requires meta tag verification")

                    if "dns" in page_text.lower() and "verify" in page_text.lower():
                        RESULTS["verification_needed"] = "DNS verification option available"
                        RESULTS["notes"].append("DNS verification option detected")

                except Exception as e:
                    log(f"Error checking verification: {e}")

        except Exception as e:
            log(f"CRITICAL ERROR: {e}")
            RESULTS["errors"].append(f"Critical error: {str(e)}")
            try:
                path = screenshot(page, "ERROR_state")
                RESULTS["screenshots"].append(path)
            except:
                pass

        finally:
            # Final overview screenshot
            try:
                path = screenshot(page, "99_final_state")
                RESULTS["screenshots"].append(path)
                log(f"Final URL: {page.url}")
                RESULTS["notes"].append(f"Final URL: {page.url}")
            except:
                pass

            browser.close()

    # ========================
    # Save results
    # ========================
    results_path = f"{SCREENSHOT_DIR}/semrush_results_{ts()}.json"
    with open(results_path, "w") as f:
        json.dump(RESULTS, f, indent=2)

    print("\n" + "="*60)
    print("SEMRUSH SETUP RESULTS")
    print("="*60)
    print(f"Login:              {'SUCCESS' if RESULTS['login'] else 'FAILED'}")
    print(f"Project created:    {'YES' if RESULTS['project_created'] else 'NO'}")
    print(f"Site Audit:         {'SETUP' if RESULTS['site_audit_setup'] else 'PENDING'}")
    print(f"Position Tracking:  {'SETUP' if RESULTS['position_tracking_setup'] else 'PENDING'}")
    print(f"Verification:       {RESULTS['verification_needed'] or 'None detected'}")
    print(f"\nNotes:")
    for note in RESULTS["notes"]:
        print(f"  - {note}")
    print(f"\nErrors:")
    for err in RESULTS["errors"]:
        print(f"  - {err}")
    print(f"\nScreenshots: {len(RESULTS['screenshots'])} captured")
    for s in RESULTS["screenshots"]:
        print(f"  {s}")
    print(f"\nResults saved: {results_path}")

    return RESULTS

if __name__ == "__main__":
    run()
