#!/usr/bin/env python3
"""
SEMRush Current State Audit - 2026-02-23
Checks current status of purebrain.ai in SEMRush:
- Login
- Projects / dashboard overview
- Site audit status and issues
- Position tracking data
- Domain overview (organic traffic, backlinks, authority)
- On-page SEO checker
- Backlink analytics
- Any pending recommendations
"""

import time
import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

EMAIL = "support@puremarketing.ai"
PASSWORD = "c2!2gurK:m3T!rc"

def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def shot(page, name):
    path = f"{SCREENSHOT_DIR}/semrush_audit23_{name}.png"
    page.screenshot(path=path, full_page=False)
    print(f"  [screenshot] {name}")
    return path

def shot_full(page, name):
    path = f"{SCREENSHOT_DIR}/semrush_audit23_{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"  [screenshot-full] {name}")
    return path

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

RESULTS = {
    "date": "2026-02-23",
    "login": False,
    "projects": [],
    "purebrain_exists": False,
    "site_audit": {
        "configured": False,
        "health_score": None,
        "issues": [],
        "errors": 0,
        "warnings": 0,
        "notices": 0,
        "url": None
    },
    "position_tracking": {
        "configured": False,
        "keywords_tracked": 0,
        "positions": [],
        "url": None
    },
    "domain_overview": {
        "authority_score": None,
        "organic_traffic": None,
        "organic_keywords": None,
        "backlinks": None,
        "referring_domains": None
    },
    "backlinks": {
        "total": None,
        "referring_domains": None,
        "top_anchors": []
    },
    "screenshots": [],
    "notes": [],
    "errors": []
}

def dismiss_cookie(page):
    try:
        for txt in ["Allow all", "Accept all", "Accept cookies", "I agree"]:
            btn = page.locator(f'button:has-text("{txt}")').first
            if btn.is_visible(timeout=1500):
                btn.click()
                log(f"Dismissed cookie banner: {txt}")
                time.sleep(0.5)
                return
    except:
        pass

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ]
        )

        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York"
        )

        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            window.chrome = {runtime: {}};
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

            page.locator('input[name="email"]').fill(EMAIL)
            time.sleep(0.5)
            page.locator('input[name="password"]').fill(PASSWORD)
            time.sleep(0.5)

            path = shot(page, "02_form_filled")
            RESULTS["screenshots"].append(path)

            page.locator('button[type="submit"]').click()

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
            body_text = page.locator("body").inner_text(timeout=5000)
            if any(x in body_text.lower() for x in ["two-factor", "verification code", "authenticator", "confirm your email"]):
                log("2FA or verification DETECTED")
                RESULTS["errors"].append("2FA/verification required")
                path = shot(page, "2FA_required")
                RESULTS["screenshots"].append(path)
                browser.close()
                return RESULTS

            if "/login" not in current_url and "/signin" not in current_url:
                RESULTS["login"] = True
                log("Login SUCCESS")
            else:
                log("Login FAILED - still on login page")
                RESULTS["errors"].append("Login failed")
                browser.close()
                return RESULTS

            # ========================
            # STEP 2: Home / Projects Dashboard
            # ========================
            log("Step 2: Home dashboard - checking projects")
            dismiss_cookie(page)

            path = shot(page, "04_home_dashboard")
            RESULTS["screenshots"].append(path)

            # Scroll to see all projects
            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(1)
            path = shot(page, "05_home_scrolled")
            RESULTS["screenshots"].append(path)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            path = shot(page, "06_home_bottom")
            RESULTS["screenshots"].append(path)

            body_text = page.locator("body").inner_text(timeout=5000)
            if "purebrain" in body_text.lower():
                RESULTS["purebrain_exists"] = True
                RESULTS["notes"].append("purebrain.ai project IS visible in home dashboard")
                log("purebrain.ai found in dashboard!")
            else:
                RESULTS["notes"].append("purebrain.ai NOT found in home dashboard view")
                log("purebrain.ai NOT found - may need scrolling or project doesn't exist")

            # Try to extract project names from page
            try:
                headings = page.locator("h2, h3, [class*='project'], [class*='folder']").all()
                for h in headings[:30]:
                    try:
                        txt = h.inner_text(timeout=500).strip()
                        if txt and 3 < len(txt) < 80:
                            RESULTS["projects"].append(txt)
                    except:
                        pass
            except:
                pass

            # ========================
            # STEP 3: Site Audit for purebrain.ai
            # ========================
            log("Step 3: Site Audit check")
            page.goto("https://www.semrush.com/siteaudit/", timeout=30000, wait_until="load")
            time.sleep(5)
            dismiss_cookie(page)

            path = shot(page, "07_site_audit_list")
            RESULTS["screenshots"].append(path)
            RESULTS["site_audit"]["url"] = page.url

            body_text = page.locator("body").inner_text(timeout=5000)

            if "purebrain" in body_text.lower():
                RESULTS["site_audit"]["configured"] = True
                RESULTS["notes"].append("Site Audit: purebrain.ai is configured!")
                log("Site Audit: purebrain.ai found!")

                # Try to click into purebrain.ai audit
                try:
                    pb_link = page.locator('a:has-text("purebrain"), a:has-text("PureBrain")').first
                    if pb_link.is_visible(timeout=3000):
                        pb_link.click()
                        time.sleep(5)
                        path = shot(page, "08_site_audit_purebrain")
                        RESULTS["screenshots"].append(path)

                        # Extract audit data
                        audit_text = page.locator("body").inner_text(timeout=5000)

                        # Look for health score
                        import re
                        score_match = re.search(r'(\d+)%?\s*(?:health|score|Site Health)', audit_text, re.IGNORECASE)
                        if score_match:
                            RESULTS["site_audit"]["health_score"] = score_match.group(1)
                            log(f"Health score: {score_match.group(1)}")

                        # Scroll to see more
                        page.evaluate("window.scrollTo(0, 500)")
                        time.sleep(1)
                        path = shot(page, "09_site_audit_detail")
                        RESULTS["screenshots"].append(path)

                        page.evaluate("window.scrollTo(0, 1000)")
                        time.sleep(1)
                        path = shot(page, "10_site_audit_issues")
                        RESULTS["screenshots"].append(path)

                except Exception as e:
                    log(f"Could not click into purebrain audit: {e}")
            else:
                log("Site Audit: purebrain.ai NOT configured yet")
                RESULTS["notes"].append("Site Audit: needs setup for purebrain.ai")

                # Scroll to see all configured projects
                page.evaluate("window.scrollTo(0, 500)")
                time.sleep(1)
                path = shot(page, "08_site_audit_scrolled")
                RESULTS["screenshots"].append(path)

            # ========================
            # STEP 4: Position Tracking
            # ========================
            log("Step 4: Position Tracking check")
            page.goto("https://www.semrush.com/position-tracking/", timeout=30000, wait_until="load")
            time.sleep(5)
            dismiss_cookie(page)

            path = shot(page, "11_position_tracking")
            RESULTS["screenshots"].append(path)
            RESULTS["position_tracking"]["url"] = page.url

            body_text = page.locator("body").inner_text(timeout=5000)
            if "purebrain" in body_text.lower():
                RESULTS["position_tracking"]["configured"] = True
                RESULTS["notes"].append("Position Tracking: purebrain.ai IS configured!")
                log("Position Tracking: purebrain.ai found!")

                try:
                    pb_link = page.locator('a:has-text("purebrain"), a:has-text("PureBrain")').first
                    if pb_link.is_visible(timeout=3000):
                        pb_link.click()
                        time.sleep(5)
                        path = shot(page, "12_position_detail")
                        RESULTS["screenshots"].append(path)

                        page.evaluate("window.scrollTo(0, 500)")
                        time.sleep(1)
                        path = shot(page, "13_position_scrolled")
                        RESULTS["screenshots"].append(path)
                except Exception as e:
                    log(f"Could not click into position tracking: {e}")
            else:
                RESULTS["notes"].append("Position Tracking: NOT configured for purebrain.ai")
                log("Position Tracking: purebrain.ai NOT configured")

                page.evaluate("window.scrollTo(0, 500)")
                time.sleep(1)
                path = shot(page, "12_position_scrolled")
                RESULTS["screenshots"].append(path)

            # ========================
            # STEP 5: Domain Overview for purebrain.ai
            # ========================
            log("Step 5: Domain Overview for purebrain.ai")
            page.goto(
                "https://www.semrush.com/analytics/overview/?q=purebrain.ai&searchType=domain",
                timeout=30000, wait_until="load"
            )
            time.sleep(6)
            dismiss_cookie(page)

            path = shot(page, "14_domain_overview")
            RESULTS["screenshots"].append(path)

            # Extract domain stats
            body_text = page.locator("body").inner_text(timeout=5000)

            import re
            # Authority score
            auth_match = re.search(r'Authority Score[:\s]*(\d+)', body_text, re.IGNORECASE)
            if auth_match:
                RESULTS["domain_overview"]["authority_score"] = auth_match.group(1)

            # Organic traffic
            traffic_match = re.search(r'Organic(?:\s+Search)?\s+Traffic[:\s]*([0-9,K.]+)', body_text, re.IGNORECASE)
            if traffic_match:
                RESULTS["domain_overview"]["organic_traffic"] = traffic_match.group(1)

            # Keywords
            kw_match = re.search(r'Organic(?:\s+Search)?\s+Keywords[:\s]*([0-9,K.]+)', body_text, re.IGNORECASE)
            if kw_match:
                RESULTS["domain_overview"]["organic_keywords"] = kw_match.group(1)

            # Backlinks
            bl_match = re.search(r'Backlinks[:\s]*([0-9,K.]+)', body_text, re.IGNORECASE)
            if bl_match:
                RESULTS["domain_overview"]["backlinks"] = bl_match.group(1)

            log(f"Domain stats: {RESULTS['domain_overview']}")

            # Scroll to see more
            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(2)
            path = shot(page, "15_domain_overview_mid")
            RESULTS["screenshots"].append(path)

            page.evaluate("window.scrollTo(0, 1100)")
            time.sleep(2)
            path = shot(page, "16_domain_overview_bottom")
            RESULTS["screenshots"].append(path)

            # ========================
            # STEP 6: Organic Research Keywords
            # ========================
            log("Step 6: Organic Research - Keywords")
            page.goto(
                "https://www.semrush.com/analytics/organic/overview/?q=purebrain.ai&searchType=domain",
                timeout=30000, wait_until="load"
            )
            time.sleep(5)
            dismiss_cookie(page)

            path = shot(page, "17_organic_research")
            RESULTS["screenshots"].append(path)

            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(1)
            path = shot(page, "18_organic_research_scrolled")
            RESULTS["screenshots"].append(path)

            # ========================
            # STEP 7: Backlink Analytics
            # ========================
            log("Step 7: Backlink Analytics")
            page.goto(
                "https://www.semrush.com/analytics/backlinks/overview/?q=purebrain.ai&searchType=domain",
                timeout=30000, wait_until="load"
            )
            time.sleep(5)
            dismiss_cookie(page)

            path = shot(page, "19_backlinks")
            RESULTS["screenshots"].append(path)

            body_text = page.locator("body").inner_text(timeout=5000)
            bl_match = re.search(r'(\d[\d,]*)\s*Backlinks', body_text)
            if bl_match:
                RESULTS["backlinks"]["total"] = bl_match.group(1)

            ref_match = re.search(r'(\d[\d,]*)\s*Referring Domains', body_text)
            if ref_match:
                RESULTS["backlinks"]["referring_domains"] = ref_match.group(1)

            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(1)
            path = shot(page, "20_backlinks_scrolled")
            RESULTS["screenshots"].append(path)

            # ========================
            # STEP 8: On-Page SEO Checker
            # ========================
            log("Step 8: On-Page SEO Checker")
            page.goto("https://www.semrush.com/on-page-seo-checker/", timeout=30000, wait_until="load")
            time.sleep(5)
            dismiss_cookie(page)

            path = shot(page, "21_on_page_seo")
            RESULTS["screenshots"].append(path)

            body_text = page.locator("body").inner_text(timeout=5000)
            if "purebrain" in body_text.lower():
                RESULTS["notes"].append("On-Page SEO Checker: purebrain.ai configured")
            else:
                RESULTS["notes"].append("On-Page SEO Checker: needs setup")

            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(1)
            path = shot(page, "22_on_page_seo_scrolled")
            RESULTS["screenshots"].append(path)

            # ========================
            # STEP 9: Keyword Gap Analysis
            # ========================
            log("Step 9: Keyword Gap / Magic Tool check")
            page.goto(
                "https://www.semrush.com/analytics/keywordmagic/?q=ai+partner+for+business&db=us",
                timeout=30000, wait_until="load"
            )
            time.sleep(5)
            dismiss_cookie(page)

            path = shot(page, "23_keyword_magic")
            RESULTS["screenshots"].append(path)

            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(1)
            path = shot(page, "24_keyword_magic_results")
            RESULTS["screenshots"].append(path)

            # ========================
            # STEP 10: Final home state
            # ========================
            log("Step 10: Final home state")
            page.goto("https://www.semrush.com/home/", timeout=30000, wait_until="load")
            time.sleep(5)
            dismiss_cookie(page)

            path = shot_full(page, "25_final_home_full")
            RESULTS["screenshots"].append(path)

        except Exception as e:
            log(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            RESULTS["errors"].append(str(e))
            try:
                path = shot(page, "ERROR_state")
                RESULTS["screenshots"].append(path)
            except:
                pass
        finally:
            try:
                RESULTS["notes"].append(f"Final URL: {page.url}")
            except:
                pass
            browser.close()

    # Save results JSON
    results_path = f"{SCREENSHOT_DIR}/semrush_audit23_results_{ts()}.json"
    with open(results_path, "w") as f:
        json.dump(RESULTS, f, indent=2)

    print("\n" + "="*60)
    print("SEMRUSH AUDIT RESULTS - 2026-02-23")
    print("="*60)
    print(f"Login:                    {'SUCCESS' if RESULTS['login'] else 'FAILED'}")
    print(f"purebrain.ai exists:      {'YES' if RESULTS['purebrain_exists'] else 'NO (needs project create)'}")
    print(f"Site Audit configured:    {'YES' if RESULTS['site_audit']['configured'] else 'NO'}")
    print(f"  Health Score:           {RESULTS['site_audit']['health_score'] or 'N/A'}")
    print(f"Position Tracking:        {'YES' if RESULTS['position_tracking']['configured'] else 'NO'}")
    print(f"\nDomain Overview (purebrain.ai):")
    print(f"  Authority Score:        {RESULTS['domain_overview']['authority_score'] or 'N/A'}")
    print(f"  Organic Traffic:        {RESULTS['domain_overview']['organic_traffic'] or 'N/A'}")
    print(f"  Organic Keywords:       {RESULTS['domain_overview']['organic_keywords'] or 'N/A'}")
    print(f"  Backlinks:              {RESULTS['domain_overview']['backlinks'] or RESULTS['backlinks']['total'] or 'N/A'}")
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
    print(f"\nFull results: {results_path}")

    return RESULTS

if __name__ == "__main__":
    run()
