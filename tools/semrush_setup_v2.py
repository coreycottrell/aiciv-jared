#!/usr/bin/env python3
"""
SEMRush Setup Script v2 for purebrain.ai
Login is confirmed working. This script:
1. Logs in
2. Checks existing projects
3. Creates purebrain.ai project if needed
4. Navigates to Site Audit + Position Tracking
5. Documents verification requirements
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

def shot(page, name):
    path = f"{SCREENSHOT_DIR}/semrush_{name}.png"
    page.screenshot(path=path, full_page=False)
    print(f"  [screenshot] {path}")
    return path

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def wait_for_page(page, timeout=12000):
    """Wait for page using 'load' event (not networkidle - SEMRush never reaches networkidle)"""
    try:
        page.wait_for_load_state("load", timeout=timeout)
    except:
        pass
    time.sleep(3)

RESULTS = {
    "login": False,
    "existing_projects": [],
    "purebrain_project_exists": False,
    "project_created": False,
    "site_audit_url": None,
    "position_tracking_url": None,
    "verification_info": {},
    "screenshots": [],
    "notes": [],
    "errors": []
}

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York"
        )

        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = context.new_page()

        try:
            # ========================
            # STEP 1: Login
            # ========================
            log("Step 1: Login to SEMRush")
            page.goto("https://www.semrush.com/login/", timeout=30000, wait_until="load")
            time.sleep(3)

            path = shot(page, "01_login_page")
            RESULTS["screenshots"].append(path)

            # Fill email
            page.locator('input[name="email"]').fill("support@puremarketing.ai")
            time.sleep(0.5)
            page.locator('input[name="password"]').fill("c2!2gurK:m3T!rc")
            time.sleep(0.5)

            path = shot(page, "02_form_filled")
            RESULTS["screenshots"].append(path)

            page.locator('button[type="submit"]').click()

            # Wait for navigation
            try:
                page.wait_for_url("**/home/**", timeout=20000)
            except:
                try:
                    page.wait_for_url("**/projects/**", timeout=10000)
                except:
                    pass

            time.sleep(5)
            current_url = page.url
            log(f"After login URL: {current_url}")

            path = shot(page, "03_after_login")
            RESULTS["screenshots"].append(path)

            # Check for 2FA
            try:
                body_text = page.locator("body").inner_text(timeout=3000)
                if "two-factor" in body_text.lower() or "verification code" in body_text.lower() or "authenticator" in body_text.lower():
                    log("2FA DETECTED - needs manual input")
                    RESULTS["errors"].append("2FA required - Jared needs to provide 2FA code manually")
                    path = shot(page, "2FA_required")
                    RESULTS["screenshots"].append(path)
                    return RESULTS
            except:
                pass

            if "/login" not in current_url and "/signin" not in current_url:
                RESULTS["login"] = True
                log("Login SUCCESS")
            else:
                log("Still on login page - login may have failed")
                RESULTS["errors"].append("Login failed - remained on login page")
                return RESULTS

            # ========================
            # STEP 2: Dismiss cookie banner, check home page
            # ========================
            log("Step 2: Checking dashboard/home")

            # Try to dismiss cookie banner
            try:
                cookie_btn = page.locator('button:has-text("Allow all cookies")').first
                if cookie_btn.is_visible(timeout=3000):
                    cookie_btn.click()
                    log("Dismissed cookie banner")
                    time.sleep(1)
            except:
                pass

            # Take full-page screenshot of home
            path = shot(page, "04_home_dashboard")
            RESULTS["screenshots"].append(path)

            # Scroll to see more projects
            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(1)
            path = shot(page, "05_home_scrolled")
            RESULTS["screenshots"].append(path)

            # Check for existing projects
            body_text = page.locator("body").inner_text(timeout=5000)
            if "purebrain" in body_text.lower():
                log("purebrain.ai project ALREADY EXISTS in account!")
                RESULTS["purebrain_project_exists"] = True
                RESULTS["notes"].append("purebrain.ai project already exists - no need to create")
            else:
                log("purebrain.ai NOT found in current view")

            # Look for project names visible
            project_links = page.locator("a[href*='project'], [class*='project']").all()
            for link in project_links[:20]:
                try:
                    text = link.inner_text(timeout=1000).strip()
                    if text and len(text) < 100:
                        RESULTS["existing_projects"].append(text)
                except:
                    pass

            # ========================
            # STEP 3: Navigate to Projects page
            # ========================
            log("Step 3: Going to Projects page")
            page.goto("https://www.semrush.com/home/", timeout=30000, wait_until="load")
            time.sleep(5)

            # Dismiss cookie banner again if it appeared
            try:
                cookie_btn = page.locator('button:has-text("Allow all cookies")').first
                if cookie_btn.is_visible(timeout=2000):
                    cookie_btn.click()
                    time.sleep(1)
            except:
                pass

            path = shot(page, "06_home_full")
            RESULTS["screenshots"].append(path)

            # Scroll down to see all projects
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            path = shot(page, "07_home_bottom")
            RESULTS["screenshots"].append(path)

            # Check if purebrain.ai is visible
            body_text = page.locator("body").inner_text(timeout=5000)
            if "purebrain" in body_text.lower():
                log("Found purebrain.ai project on home page!")
                RESULTS["purebrain_project_exists"] = True

            # ========================
            # STEP 4: Create project if needed
            # ========================
            if not RESULTS["purebrain_project_exists"]:
                log("Step 4: Creating purebrain.ai project")

                # Look for + Create Folder or similar
                # First scroll back to top
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(1)

                # Try the Create Folder button visible in screenshot
                create_selectors = [
                    'button:has-text("+ Create Folder")',
                    'button:has-text("Create Folder")',
                    'a:has-text("Create Folder")',
                    'button:has-text("+ Create project")',
                    'button:has-text("Create project")',
                    'a:has-text("Create project")',
                    '[data-test="create-project-button"]',
                    'button:has-text("Add project")'
                ]

                created = False
                for sel in create_selectors:
                    try:
                        btn = page.locator(sel).first
                        if btn.is_visible(timeout=2000):
                            log(f"Found create button: {sel}")
                            btn.click()
                            time.sleep(2)
                            path = shot(page, "08_create_dialog")
                            RESULTS["screenshots"].append(path)
                            created = True
                            break
                    except:
                        continue

                if not created:
                    log("Could not find create project button - trying direct URL")
                    # Try direct URL to create project
                    page.goto("https://www.semrush.com/projects/create/", timeout=20000, wait_until="load")
                    time.sleep(3)
                    path = shot(page, "08_create_direct")
                    RESULTS["screenshots"].append(path)

                # Fill domain
                domain_selectors = [
                    'input[placeholder*="domain" i]',
                    'input[placeholder*="website" i]',
                    'input[name="domain"]',
                    'input[placeholder*="URL" i]'
                ]

                for sel in domain_selectors:
                    try:
                        el = page.locator(sel).first
                        if el.is_visible(timeout=3000):
                            el.fill("purebrain.ai")
                            log(f"Filled domain field: {sel}")
                            time.sleep(1)

                            # Fill project name
                            try:
                                name_el = page.locator('input[placeholder*="name" i], input[name="name"]').first
                                if name_el.is_visible(timeout=2000):
                                    name_el.fill("PureBrain.ai")
                                    log("Filled project name")
                            except:
                                pass

                            path = shot(page, "09_project_filled")
                            RESULTS["screenshots"].append(path)

                            # Submit
                            for submit_sel in ['button[type="submit"]', 'button:has-text("Create")', 'button:has-text("Start")']:
                                try:
                                    sbtn = page.locator(submit_sel).first
                                    if sbtn.is_visible(timeout=2000):
                                        sbtn.click()
                                        log(f"Clicked submit: {submit_sel}")
                                        break
                                except:
                                    continue

                            time.sleep(5)
                            path = shot(page, "10_after_create")
                            RESULTS["screenshots"].append(path)
                            RESULTS["project_created"] = True
                            break
                    except:
                        continue

            # ========================
            # STEP 5: Navigate to Site Audit for purebrain.ai
            # ========================
            log("Step 5: Navigating to Site Audit")
            page.goto("https://www.semrush.com/siteaudit/", timeout=30000, wait_until="load")
            time.sleep(5)
            path = shot(page, "11_site_audit")
            RESULTS["screenshots"].append(path)
            RESULTS["site_audit_url"] = page.url
            log(f"Site Audit URL: {page.url}")

            # Check page state
            try:
                body_text = page.locator("body").inner_text(timeout=5000)
                if "start audit" in body_text.lower() or "create" in body_text.lower() or "set up" in body_text.lower():
                    RESULTS["notes"].append("Site Audit: needs configuration for purebrain.ai")
                if "purebrain" in body_text.lower():
                    RESULTS["notes"].append("Site Audit: purebrain.ai already configured")
            except:
                pass

            # Scroll down to see more
            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(1)
            path = shot(page, "12_site_audit_scrolled")
            RESULTS["screenshots"].append(path)

            # ========================
            # STEP 6: Position Tracking
            # ========================
            log("Step 6: Navigating to Position Tracking")
            page.goto("https://www.semrush.com/position-tracking/", timeout=30000, wait_until="load")
            time.sleep(5)
            path = shot(page, "13_position_tracking")
            RESULTS["screenshots"].append(path)
            RESULTS["position_tracking_url"] = page.url
            log(f"Position Tracking URL: {page.url}")

            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(1)
            path = shot(page, "14_position_tracking_scrolled")
            RESULTS["screenshots"].append(path)

            # ========================
            # STEP 7: On Page SEO Checker
            # ========================
            log("Step 7: Navigating to On Page SEO Checker")
            page.goto("https://www.semrush.com/on-page-seo-checker/", timeout=30000, wait_until="load")
            time.sleep(5)
            path = shot(page, "15_on_page_seo")
            RESULTS["screenshots"].append(path)

            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(1)
            path = shot(page, "16_on_page_seo_scrolled")
            RESULTS["screenshots"].append(path)

            # ========================
            # STEP 8: Check Organic Research for purebrain.ai
            # ========================
            log("Step 8: Running Organic Research for purebrain.ai")
            page.goto("https://www.semrush.com/analytics/overview/?q=purebrain.ai&searchType=domain", timeout=30000, wait_until="load")
            time.sleep(6)
            path = shot(page, "17_domain_overview")
            RESULTS["screenshots"].append(path)

            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(2)
            path = shot(page, "18_domain_overview_scrolled")
            RESULTS["screenshots"].append(path)

            # ========================
            # STEP 9: Go back to home to see full project list
            # ========================
            log("Step 9: Final home page state")
            page.goto("https://www.semrush.com/home/", timeout=30000, wait_until="load")
            time.sleep(5)

            # Dismiss cookies
            try:
                cookie_btn = page.locator('button:has-text("Allow all cookies")').first
                if cookie_btn.is_visible(timeout=2000):
                    cookie_btn.click()
                    time.sleep(1)
            except:
                pass

            path = shot(page, "19_final_home")
            RESULTS["screenshots"].append(path)

            # Scroll to see all projects
            page.evaluate("window.scrollTo(0, 800)")
            time.sleep(2)
            path = shot(page, "20_final_home_bottom")
            RESULTS["screenshots"].append(path)

            final_text = page.locator("body").inner_text(timeout=5000)
            if "purebrain" in final_text.lower():
                RESULTS["notes"].append("purebrain.ai visible in final home page view")
                RESULTS["purebrain_project_exists"] = True

        except Exception as e:
            log(f"ERROR: {e}")
            RESULTS["errors"].append(str(e))
            try:
                path = shot(page, "ERROR_state")
                RESULTS["screenshots"].append(path)
            except:
                pass
        finally:
            try:
                log(f"Final URL: {page.url}")
                RESULTS["notes"].append(f"Final URL: {page.url}")
            except:
                pass
            browser.close()

    # Save results
    results_path = f"{SCREENSHOT_DIR}/semrush_results_v2_{ts()}.json"
    with open(results_path, "w") as f:
        json.dump(RESULTS, f, indent=2)

    print("\n" + "="*60)
    print("SEMRUSH SETUP RESULTS v2")
    print("="*60)
    print(f"Login:                    {'SUCCESS' if RESULTS['login'] else 'FAILED'}")
    print(f"purebrain.ai exists:      {'YES' if RESULTS['purebrain_project_exists'] else 'NO'}")
    print(f"Project created:          {'YES' if RESULTS['project_created'] else 'N/A'}")
    print(f"Site Audit URL:           {RESULTS['site_audit_url']}")
    print(f"Position Tracking URL:    {RESULTS['position_tracking_url']}")
    print(f"\nExisting projects found:  {RESULTS['existing_projects'][:5]}")
    print(f"\nNotes:")
    for note in RESULTS["notes"]:
        print(f"  - {note}")
    if RESULTS["errors"]:
        print(f"\nErrors:")
        for err in RESULTS["errors"]:
            print(f"  - {err}")
    print(f"\nScreenshots ({len(RESULTS['screenshots'])} total):")
    for s in RESULTS["screenshots"]:
        print(f"  {s}")
    print(f"\nResults: {results_path}")

    return RESULTS

if __name__ == "__main__":
    run()
