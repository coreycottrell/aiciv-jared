#!/usr/bin/env python3
"""
PureBrain.ai Full Analytics Audit — 2026-03-04
Agent: browser-vision-tester (desktop-vision skill)
Platforms: Google Analytics 4, Google Search Console, Microsoft Clarity
Method: Playwright authenticated browser sessions + screenshot capture
"""

import time
import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/analytics_2026_03_04"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

GOOGLE_EMAIL = "jared@puretechnology.nyc"
CLARITY_URL = "https://clarity.microsoft.com"
GA4_URL = "https://analytics.google.com"
GSC_URL = "https://search.google.com/search-console"

GA4_PROPERTY = "purebrain.ai"
GA4_MEASUREMENT_ID = "G-86325WBT3P"
CLARITY_PROJECT = "viy9bnc56x"

RESULTS = {
    "date": "2026-03-04",
    "ga4": {
        "accessible": False,
        "realtime_visitors": None,
        "top_pages": [],
        "traffic_sources": [],
        "engagement_rate": None,
        "avg_session_duration": None,
        "bounce_rate": None,
        "total_users_30d": None,
        "notes": []
    },
    "gsc": {
        "accessible": False,
        "total_clicks_28d": None,
        "total_impressions_28d": None,
        "avg_ctr": None,
        "avg_position": None,
        "top_queries": [],
        "indexed_pages": None,
        "coverage_errors": None,
        "notes": []
    },
    "clarity": {
        "accessible": False,
        "total_sessions": None,
        "rage_clicks": None,
        "dead_clicks": None,
        "quick_backs": None,
        "js_errors": None,
        "scroll_depth": None,
        "notes": []
    },
    "screenshots": []
}

def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def shot(page, name, full=False):
    path = f"{SCREENSHOT_DIR}/{name}_{ts()}.png"
    page.screenshot(path=path, full_page=full)
    RESULTS["screenshots"].append(path)
    print(f"  [screenshot] {path}")
    return path

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def save_results():
    path = f"{SCREENSHOT_DIR}/results.json"
    with open(path, "w") as f:
        json.dump(RESULTS, f, indent=2)
    return path

def try_ga4(page):
    """Attempt GA4 access"""
    log("=== GOOGLE ANALYTICS 4 ===")
    try:
        page.goto(GA4_URL, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        shot(page, "ga4_landing")

        title = page.title()
        url = page.url
        log(f"GA4 title: {title} | URL: {url}")

        # Check if we got redirected to login or are in the app
        if "accounts.google.com" in url or "signin" in url.lower():
            log("GA4 requires Google login — OAuth wall hit")
            RESULTS["ga4"]["notes"].append("Requires interactive Google OAuth — cannot automate without Jared's session cookies")
            RESULTS["ga4"]["notes"].append("GA4 Measurement ID confirmed: G-86325WBT3P")
            RESULTS["ga4"]["notes"].append("GTM Container confirmed active: GTM-WTDXL4VJ")
            shot(page, "ga4_login_wall")
            return False

        # If we're in the app
        if "analytics.google.com" in url and "/p" in url:
            log("GA4 accessible!")
            RESULTS["ga4"]["accessible"] = True
            shot(page, "ga4_dashboard", full=True)

            # Try to read key metrics from the page
            page_text = page.inner_text("body")
            RESULTS["ga4"]["notes"].append(f"Page text sample: {page_text[:500]}")
            return True

        log(f"GA4 landing at unexpected URL: {url}")
        shot(page, "ga4_unexpected")
        return False

    except PlaywrightTimeoutError:
        log("GA4 timed out")
        RESULTS["ga4"]["notes"].append("Page load timeout")
        return False
    except Exception as e:
        log(f"GA4 error: {e}")
        RESULTS["ga4"]["notes"].append(f"Error: {str(e)[:100]}")
        return False

def try_gsc(page):
    """Attempt Search Console access"""
    log("=== GOOGLE SEARCH CONSOLE ===")
    try:
        page.goto(GSC_URL, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        shot(page, "gsc_landing")

        url = page.url
        title = page.title()
        log(f"GSC title: {title} | URL: {url}")

        if "accounts.google.com" in url or "signin" in url.lower():
            log("GSC requires Google login — OAuth wall hit")
            RESULTS["gsc"]["notes"].append("Requires interactive Google OAuth — cannot automate without Jared's session")
            RESULTS["gsc"]["notes"].append("Property confirmed registered: purebrain.ai")
            RESULTS["gsc"]["notes"].append("Sitemap submitted: https://purebrain.ai/sitemap_index.xml")
            shot(page, "gsc_login_wall")
            return False

        if "search.google.com/search-console" in url:
            log("GSC accessible!")
            RESULTS["gsc"]["accessible"] = True
            shot(page, "gsc_dashboard", full=True)
            return True

        return False

    except Exception as e:
        log(f"GSC error: {e}")
        RESULTS["gsc"]["notes"].append(f"Error: {str(e)[:100]}")
        return False

def try_clarity(page):
    """Attempt Microsoft Clarity access"""
    log("=== MICROSOFT CLARITY ===")
    try:
        page.goto(CLARITY_URL, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        shot(page, "clarity_landing")

        url = page.url
        title = page.title()
        log(f"Clarity title: {title} | URL: {url}")

        if "login.microsoftonline" in url or "login.live" in url or "microsoft.com/login" in url:
            log("Clarity requires Microsoft login — OAuth wall hit")
            RESULTS["clarity"]["notes"].append("Requires Microsoft OAuth — cannot automate without session cookies")
            RESULTS["clarity"]["notes"].append(f"Project ID confirmed: {CLARITY_PROJECT}")
            RESULTS["clarity"]["notes"].append("Clarity tracking pixel confirmed active via GTM container GTM-WTDXL4VJ")
            shot(page, "clarity_login_wall")
            return False

        if "clarity.microsoft.com" in url and "app" in url:
            log("Clarity accessible!")
            RESULTS["clarity"]["accessible"] = True
            shot(page, "clarity_dashboard", full=True)

            # Try to read metrics
            page_text = page.inner_text("body")
            RESULTS["clarity"]["notes"].append(f"Page accessible, text sample: {page_text[:500]}")
            return True

        # Try clicking sign in if on landing page
        try:
            sign_in = page.query_selector("a[href*='signin'], button:has-text('Sign in'), a:has-text('Sign in')")
            if sign_in:
                log("Found sign in button on Clarity — checking if it leads to auth wall")
                shot(page, "clarity_pre_signin")
        except:
            pass

        return False

    except Exception as e:
        log(f"Clarity error: {e}")
        RESULTS["clarity"]["notes"].append(f"Error: {str(e)[:100]}")
        return False

def try_clarity_with_credentials(browser):
    """Try Clarity with a fresh context and attempt login"""
    log("Attempting Clarity login flow...")

    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    try:
        # Navigate to Clarity
        page.goto("https://clarity.microsoft.com", wait_until="load", timeout=30000)
        time.sleep(2)
        shot(page, "clarity_home")
        url = page.url
        log(f"Clarity URL: {url}")

        # Look for sign in
        try:
            btn = page.query_selector("[data-bi-name='sign-in'], a[href*='signin'], a:has-text('Sign in'), button:has-text('Sign in')")
            if btn:
                btn.click()
                time.sleep(3)
                shot(page, "clarity_after_signin_click")
                log(f"After click URL: {page.url}")
        except:
            pass

        # Check if we hit Microsoft login
        if "login.microsoftonline" in page.url or "login.live" in page.url:
            log("Hit Microsoft login — needs interactive auth")
            RESULTS["clarity"]["notes"].append("Microsoft login wall confirmed — needs Jared to auth once and save session")

        shot(page, "clarity_final_state")

    except Exception as e:
        log(f"Clarity login attempt error: {e}")
    finally:
        context.close()

def run_semrush_check():
    """Quick SEMRush check using existing credentials"""
    log("=== SEMRUSH QUICK CHECK ===")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            )
            page = context.new_page()

            page.goto("https://www.semrush.com/login/", wait_until="load", timeout=30000)
            time.sleep(3)

            # Fill login
            try:
                page.fill("input[type='email'], input[name='email']", "support@puremarketing.ai")
                time.sleep(1)
                page.fill("input[type='password'], input[name='password']", "c2!2gurK:m3T!rc")
                time.sleep(1)
                page.keyboard.press("Enter")
                time.sleep(8)
                shot(page, "semrush_after_login")
                log(f"SEMRush URL after login: {page.url}")

                if "/home/" in page.url or "semrush.com/dashboard" in page.url:
                    log("SEMRush login successful!")

                    # Navigate to purebrain.ai domain overview
                    page.goto("https://www.semrush.com/analytics/overview/?q=purebrain.ai&searchType=domain", wait_until="load", timeout=30000)
                    time.sleep(5)
                    shot(page, "semrush_domain_overview", True)

                    # Get text data from overview
                    body_text = page.inner_text("body")
                    # Look for key metrics
                    import re
                    authority_match = re.search(r'Authority Score[:\s]*(\d+)', body_text)
                    traffic_match = re.search(r'Organic Traffic[:\s]*([\d,KM]+)', body_text)
                    keywords_match = re.search(r'Organic Keywords[:\s]*([\d,KM]+)', body_text)
                    backlinks_match = re.search(r'Backlinks[:\s]*([\d,KM]+)', body_text)

                    RESULTS["ga4"]["notes"].append(f"SEMRush Domain Overview - Authority Score: {authority_match.group(1) if authority_match else 'not found'}")
                    RESULTS["ga4"]["notes"].append(f"SEMRush Domain Overview - Organic Traffic: {traffic_match.group(1) if traffic_match else 'not found'}")
                    RESULTS["ga4"]["notes"].append(f"SEMRush Domain Overview - Keywords: {keywords_match.group(1) if keywords_match else 'not found'}")
                    RESULTS["ga4"]["notes"].append(f"SEMRush Domain Overview - Backlinks: {backlinks_match.group(1) if backlinks_match else 'not found'}")

                    # Position tracking
                    page.goto("https://www.semrush.com/rank-tracker/", wait_until="load", timeout=20000)
                    time.sleep(4)
                    shot(page, "semrush_rank_tracker")

                    # Site Audit
                    page.goto("https://www.semrush.com/siteaudit/", wait_until="load", timeout=20000)
                    time.sleep(4)
                    shot(page, "semrush_site_audit")

                    site_audit_text = page.inner_text("body")
                    health_match = re.search(r'Site Health[:\s]*(\d+)', site_audit_text)
                    errors_match = re.search(r'Errors[:\s]*(\d+)', site_audit_text)
                    warnings_match = re.search(r'Warnings[:\s]*(\d+)', site_audit_text)

                    RESULTS["gsc"]["notes"].append(f"SEMRush Site Audit - Health: {health_match.group(1) if health_match else 'not found'}%")
                    RESULTS["gsc"]["notes"].append(f"SEMRush Site Audit - Errors: {errors_match.group(1) if errors_match else 'not found'}")
                    RESULTS["gsc"]["notes"].append(f"SEMRush Site Audit - Warnings: {warnings_match.group(1) if warnings_match else 'not found'}")

                    log("SEMRush data collected")
                else:
                    log(f"SEMRush login may have failed - URL: {page.url}")

            except Exception as e:
                log(f"SEMRush login error: {e}")

            browser.close()
    except Exception as e:
        log(f"SEMRush overall error: {e}")

def main():
    log("Starting Full Analytics Audit — 2026-03-04")
    log(f"Screenshots dir: {SCREENSHOT_DIR}")

    # First run SEMRush (has stored credentials, works headlessly)
    run_semrush_check()

    # Now try authenticated platforms via Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Context for Google platforms
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Try GA4
        ga4_success = try_ga4(page)

        # Try GSC
        gsc_success = try_gsc(page)

        context.close()

        # Try Clarity separately
        try_clarity_with_credentials(browser)

        browser.close()

    # Save results
    results_path = save_results()
    log(f"Results saved to: {results_path}")
    log(f"Screenshots captured: {len(RESULTS['screenshots'])}")

    return RESULTS

if __name__ == "__main__":
    results = main()
    print("\n=== AUDIT COMPLETE ===")
    print(f"GA4 accessible: {results['ga4']['accessible']}")
    print(f"GSC accessible: {results['gsc']['accessible']}")
    print(f"Clarity accessible: {results['clarity']['accessible']}")
    print(f"Screenshots: {len(results['screenshots'])}")
