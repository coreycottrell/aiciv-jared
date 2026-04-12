#!/usr/bin/env python3
"""
Fix PureBrain.ai Google Indexing Issues
Date: 2026-02-19

This script does two things:

1. PLAYWRIGHT - Login to WordPress and check/fix Settings > Reading
   "Discourage search engines from indexing this site" checkbox.
   Uses device_scale_factor=2 + vision for CAPTCHA handling.

2. REST API - Set Yoast noindex on 4 dev/test pages:
   - /pay-test/           (page ID 439)
   - /pay-test-sandbox/   (page ID 468)
   - /elementor-150/      (find by slug)
   - /paypal-buttons-embed/ (find by slug)

Usage:
    xvfb-run python3 tools/fix_google_indexing.py

Credentials: loaded from /home/jared/projects/AI-CIV/aether/.env

DO NOT RUN without Jared's approval.
"""

import base64
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ENV_PATH = "/home/jared/projects/AI-CIV/aether/.env"
load_dotenv(ENV_PATH)

WP_BASE_URL = "https://purebrain.ai"
WP_ADMIN_URL = f"{WP_BASE_URL}/wp-admin"
WP_API_BASE = f"{WP_BASE_URL}/wp-json/wp/v2"

WP_USER = "Aether"
WP_APP_PASSWORD = os.getenv("PUREBRAIN_WP_APP_PASSWORD", "").strip("'\"")
WP_PASSWORD = os.getenv("PUREBRAIN_WP_PASSWORD", "").strip("'\"")

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/tools/screenshots/indexing-fix")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
CAPTCHA_ANSWER_FILE = "/tmp/indexing_fix_captcha_answer.txt"

# Dev/test pages to noindex via Yoast
# Format: (page_id_or_None, slug)
# IDs known: 439=pay-test, 468=pay-test-sandbox
# IDs unknown (will search by slug): elementor-150, paypal-buttons-embed
DEV_PAGES = [
    (439,  "pay-test"),
    (468,  "pay-test-sandbox"),
    (None, "elementor-150"),
    (None, "paypal-buttons-embed"),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    """Print with timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def screenshot(page, name: str) -> str:
    """Take a screenshot and return its path."""
    path = str(SCREENSHOT_DIR / f"{name}_{TIMESTAMP}.png")
    page.screenshot(path=path)
    log(f"  Screenshot: {path}")
    return path


def get_auth_header() -> dict:
    """Build Basic-auth header using application password."""
    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


def api_get(endpoint: str, params: dict = None) -> dict | list | None:
    """GET from WP REST API with auth."""
    url = f"{WP_API_BASE}/{endpoint}"
    resp = requests.get(url, headers=get_auth_header(), params=params, timeout=30)
    if resp.status_code == 200:
        return resp.json()
    log(f"  API GET {endpoint} -> {resp.status_code}: {resp.text[:200]}")
    return None


def api_post(endpoint: str, data: dict) -> dict | None:
    """POST to WP REST API with auth."""
    url = f"{WP_API_BASE}/{endpoint}"
    resp = requests.post(url, headers=get_auth_header(), json=data, timeout=30)
    if resp.status_code in (200, 201):
        return resp.json()
    log(f"  API POST {endpoint} -> {resp.status_code}: {resp.text[:300]}")
    return None


# ---------------------------------------------------------------------------
# Phase 1: Playwright - Fix Settings > Reading
# ---------------------------------------------------------------------------

def find_captcha_image(page):
    """Locate the CAPTCHA image element. Returns locator or None."""
    # The CAPTCHA image is usually the only non-WordPress-logo image in the form
    captcha_info = page.evaluate("""
        () => {
            const imgs = document.querySelectorAll('form img, #loginform img');
            for (const img of imgs) {
                const src = img.getAttribute('src') || '';
                if (!src.includes('w-logo') && !src.includes('wordpress-logo') && !src.includes('gravatar')) {
                    const rect = img.getBoundingClientRect();
                    return {
                        src: src,
                        alt: img.getAttribute('alt') || '',
                        x: Math.round(rect.x),
                        y: Math.round(rect.y),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height)
                    };
                }
            }
            return null;
        }
    """)
    return captcha_info


def read_captcha_with_vision(page, captcha_info: dict) -> str | None:
    """
    Save cropped CAPTCHA image and use Claude vision (Read tool) to read it.
    Since we can't call the Read tool from inside a script, we:
    1. Save the CAPTCHA element screenshot to a known path
    2. Save the full page screenshot
    3. Print clear instructions for a human to read and write answer to file
    4. Wait up to 180s for the answer file to appear
    """
    captcha_only_path = str(SCREENSHOT_DIR / f"captcha_SOLVE_ME_{TIMESTAMP}.png")
    full_page_path = str(SCREENSHOT_DIR / f"captcha_full_page_{TIMESTAMP}.png")

    # Full page first
    page.screenshot(path=full_page_path)
    log(f"  Full page saved: {full_page_path}")

    # Try to screenshot just the CAPTCHA element
    try:
        form_imgs = page.locator("form img")
        for i in range(form_imgs.count()):
            img = form_imgs.nth(i)
            src = img.get_attribute("src") or ""
            if "w-logo" not in src and "wordpress-logo" not in src and "gravatar" not in src:
                img.screenshot(path=captcha_only_path)
                log(f"  CAPTCHA element saved: {captcha_only_path}")
                break
    except Exception as e:
        log(f"  Warning: could not isolate CAPTCHA element: {e}")
        captcha_only_path = full_page_path

    # Also try downloading raw CAPTCHA image for best quality
    if captcha_info and captcha_info.get("src"):
        src = captcha_info["src"]
        if not src.startswith("http"):
            src = f"{WP_BASE_URL}{src}"
        try:
            r = requests.get(src, timeout=10)
            if r.status_code == 200:
                raw_path = str(SCREENSHOT_DIR / f"captcha_raw_{TIMESTAMP}.png")
                Path(raw_path).write_bytes(r.content)
                log(f"  CAPTCHA raw downloaded: {raw_path}")
                captcha_only_path = raw_path  # prefer raw for sharpness
        except Exception as e:
            log(f"  Raw download failed: {e}")

    # Prompt for human/vision reading
    log("")
    log("=" * 60)
    log("CAPTCHA REQUIRES READING")
    log("=" * 60)
    log(f"View the CAPTCHA image at:")
    log(f"  {captcha_only_path}")
    log(f"Then write the answer to:")
    log(f"  {CAPTCHA_ANSWER_FILE}")
    log("Example: echo '42' > " + CAPTCHA_ANSWER_FILE)
    log("Waiting up to 180 seconds...")
    log("=" * 60)

    # Wait for answer file
    start = time.time()
    while time.time() - start < 180:
        if os.path.exists(CAPTCHA_ANSWER_FILE):
            answer = Path(CAPTCHA_ANSWER_FILE).read_text().strip()
            if answer:
                os.remove(CAPTCHA_ANSWER_FILE)
                log(f"  Got CAPTCHA answer: '{answer}'")
                return answer
        time.sleep(1)

    log("  TIMEOUT: No CAPTCHA answer received in 180s")
    return None


def wp_login(page) -> bool:
    """
    Login to WordPress admin. Returns True on success.
    Handles GoDaddy SSO bypass and CAPTCHA.
    """
    log("Navigating to wp-admin...")
    page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    screenshot(page, "01_login_initial")

    # GoDaddy SSO bypass
    try:
        sso_link = page.locator("text=Log in with username and password")
        if sso_link.is_visible(timeout=5000):
            log("  GoDaddy SSO detected - clicking username/password link...")
            sso_link.click()
            time.sleep(2)
            screenshot(page, "02_after_sso_click")
    except Exception:
        pass  # No SSO - proceed normally

    # Wait for login form
    try:
        page.wait_for_selector("#user_login", state="visible", timeout=30000)
    except Exception:
        log("  ERROR: Login form not found")
        screenshot(page, "02_no_login_form")
        return False

    log("  Filling credentials...")
    page.locator("#user_login").fill(WP_USER)
    page.locator("#user_pass").fill(WP_PASSWORD)
    time.sleep(1)
    screenshot(page, "03_credentials_filled")

    # Check for CAPTCHA
    captcha_info = find_captcha_image(page)
    if captcha_info:
        log(f"  CAPTCHA detected: {captcha_info}")
        answer = read_captcha_with_vision(page, captcha_info)
        if not answer:
            return False

        # Fill CAPTCHA answer - find the text input that is NOT user_login
        all_text_inputs = page.locator("input[type='text']")
        filled = False
        for i in range(all_text_inputs.count()):
            inp = all_text_inputs.nth(i)
            inp_id = inp.get_attribute("id") or ""
            inp_name = inp.get_attribute("name") or ""
            if inp_id != "user_login" and inp_name not in ("log",):
                inp.fill(answer)
                log(f"  Filled CAPTCHA input: id='{inp_id}' name='{inp_name}'")
                filled = True
                break

        # Also try by name attribute directly
        if not filled:
            captcha_inp = page.locator("input[name='wpsec_captcha_answer']")
            if captcha_inp.count() > 0:
                captcha_inp.fill(answer)
                log("  Filled CAPTCHA via name=wpsec_captcha_answer")
                filled = True

        if not filled:
            log("  ERROR: Could not find CAPTCHA input field")
            return False

        time.sleep(1)
        screenshot(page, "04_captcha_filled")
    else:
        log("  No CAPTCHA detected - proceeding without it")

    # Submit login form
    log("  Submitting login...")
    page.locator("#wp-submit").click()
    page.wait_for_load_state("load", timeout=60000)
    time.sleep(5)
    screenshot(page, "05_login_result")

    current_url = page.url
    log(f"  Post-login URL: {current_url}")

    if "wp-login" in current_url:
        error_el = page.locator("#login_error")
        if error_el.count() > 0:
            log(f"  LOGIN FAILED: {error_el.first.inner_text().strip()}")
        else:
            log("  LOGIN FAILED: Still on login page")
        return False

    if "wp-admin" in current_url or "dashboard" in current_url:
        log("  LOGIN SUCCESS!")
        return True

    log(f"  LOGIN RESULT UNCLEAR: URL={current_url}")
    return False


def check_fix_search_engine_visibility(page) -> dict:
    """
    Navigate to Settings > Reading and check/fix search engine visibility.
    Returns dict with result info.
    """
    log("\n--- Phase 1: Settings > Reading ---")

    reading_url = f"{WP_ADMIN_URL}/options-reading.php"
    log(f"Navigating to: {reading_url}")
    page.goto(reading_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    screenshot(page, "06_reading_settings")

    # Find the "blog_public" checkbox
    # WordPress: checked = discourage indexing (0), unchecked = allow indexing (1)
    # The checkbox name is "blog_public" - when UNCHECKED, it submits blog_public=0
    # WordPress is counterintuitive: blog_public=1 means PUBLIC (allow indexing)
    # The visible checkbox "Discourage search engines" - CHECKED = bad (discouraging)

    checkbox = page.locator("#blog_public")
    if checkbox.count() == 0:
        log("  ERROR: #blog_public checkbox not found on page")
        screenshot(page, "06_error_no_checkbox")
        return {"status": "error", "message": "Checkbox not found"}

    is_checked = checkbox.is_checked()
    log(f"  'Discourage search engines' checkbox is_checked = {is_checked}")

    if is_checked:
        # Checkbox is CHECKED = "Discourage search engines" = BAD for indexing
        log("  PROBLEM FOUND: 'Discourage search engines' is CHECKED - need to uncheck!")
        checkbox.uncheck()
        time.sleep(1)
        screenshot(page, "07_checkbox_unchecked")

        # Save changes
        save_btn = page.locator("input[type='submit']")
        if save_btn.count() > 0:
            save_btn.first.click()
            page.wait_for_load_state("load", timeout=30000)
            time.sleep(3)
            screenshot(page, "08_settings_saved")
            log("  Settings saved!")

            # Verify the fix
            page.goto(reading_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            checkbox_after = page.locator("#blog_public")
            is_checked_after = checkbox_after.is_checked()
            log(f"  Verification - checkbox is_checked = {is_checked_after}")

            if not is_checked_after:
                log("  SUCCESS: Search engine visibility FIXED - site is now indexable!")
                return {"status": "fixed", "message": "Was checked (discouraging), now unchecked (allowing indexing)"}
            else:
                log("  WARNING: Checkbox still appears checked after save - manual check needed")
                return {"status": "warning", "message": "Save may have failed - verify manually"}
        else:
            log("  ERROR: Save button not found")
            return {"status": "error", "message": "Save button not found"}
    else:
        # Checkbox is UNCHECKED = "NOT discouraging" = site is indexable = GOOD
        log("  ALREADY CORRECT: 'Discourage search engines' is unchecked - site is indexable")
        screenshot(page, "07_already_correct")
        return {"status": "already_correct", "message": "Site is already set to allow search engine indexing"}


# ---------------------------------------------------------------------------
# Phase 2: REST API - Noindex dev pages via Yoast
# ---------------------------------------------------------------------------

def find_page_by_slug(slug: str) -> int | None:
    """Search for a page by slug via REST API. Returns page ID or None."""
    log(f"  Searching for page with slug '{slug}'...")

    # Try pages endpoint first
    for post_type in ("pages", "posts"):
        results = api_get(post_type, params={"slug": slug, "per_page": 1})
        if results and len(results) > 0:
            page_id = results[0]["id"]
            log(f"  Found in {post_type}: ID={page_id}")
            return page_id

    log(f"  Page with slug '{slug}' not found via REST API")
    return None


def get_yoast_meta_for_page(page_id: int, post_type: str = "pages") -> dict:
    """Get current Yoast metadata for a page."""
    result = api_get(f"{post_type}/{page_id}")
    if result:
        yoast = result.get("yoast_head_json", {})
        return {
            "title": result.get("title", {}).get("rendered", ""),
            "slug": result.get("slug", ""),
            "status": result.get("status", ""),
            "yoast_robots_noindex": result.get("yoast_head_json", {}).get("robots", {}).get("index", ""),
        }
    return {}


def set_yoast_noindex(page_id: int, post_type: str = "pages", slug: str = "") -> dict:
    """
    Set Yoast SEO noindex on a page via REST API.
    Uses the yoast_meta field which Yoast exposes in the REST API.

    Yoast SEO REST API field: meta.yoast_wpseo_meta-robots-noindex
    Value: "1" = noindex, "0" or "" = follow global setting
    """
    log(f"\n  Setting noindex on page ID={page_id} (slug='{slug}')...")

    # First, verify the page exists and get current state
    current = api_get(f"{post_type}/{page_id}")
    if not current:
        log(f"  ERROR: Page ID={page_id} not found via REST API")
        return {"status": "error", "message": f"Page {page_id} not found"}

    page_title = current.get("title", {}).get("rendered", "Unknown")
    page_slug = current.get("slug", "unknown")
    log(f"  Found: '{page_title}' (/{page_slug}/)")

    # Check current Yoast noindex state
    yoast_meta = current.get("meta", {})
    current_noindex = yoast_meta.get("yoast_wpseo_meta-robots-noindex", "")
    log(f"  Current noindex value: '{current_noindex}'")

    if current_noindex == "1":
        log(f"  Already set to noindex - skipping")
        return {
            "status": "already_noindex",
            "page_id": page_id,
            "slug": page_slug,
            "title": page_title,
        }

    # Set noindex via REST API
    update_data = {
        "meta": {
            "yoast_wpseo_meta-robots-noindex": "1"
        }
    }

    result = api_post(f"{post_type}/{page_id}", update_data)
    if result:
        new_noindex = result.get("meta", {}).get("yoast_wpseo_meta-robots-noindex", "?")
        log(f"  Updated! New noindex value: '{new_noindex}'")
        return {
            "status": "set_noindex",
            "page_id": page_id,
            "slug": page_slug,
            "title": page_title,
            "new_value": new_noindex,
        }
    else:
        log(f"  REST API update failed - will try Yoast alternative meta field")
        # Try alternative Yoast field names
        for field_name in [
            "_yoast_wpseo_meta-robots-noindex",
            "yoast_wpseo_meta-robots-noindex",
        ]:
            alt_data = {"meta": {field_name: "1"}}
            alt_result = api_post(f"{post_type}/{page_id}", alt_data)
            if alt_result:
                log(f"  Success with field '{field_name}'")
                return {
                    "status": "set_noindex",
                    "page_id": page_id,
                    "slug": page_slug,
                    "title": page_title,
                    "field_used": field_name,
                }

        return {
            "status": "error",
            "page_id": page_id,
            "slug": page_slug,
            "message": "REST API update failed for all Yoast field variants",
        }


def phase2_noindex_dev_pages() -> list[dict]:
    """
    Set Yoast noindex on all 4 dev/test pages via REST API.
    Returns list of result dicts.
    """
    log("\n--- Phase 2: Noindex Dev Pages via REST API ---")

    if not WP_APP_PASSWORD:
        log("ERROR: PUREBRAIN_WP_APP_PASSWORD not found in .env")
        return [{"status": "error", "message": "No app password"}]

    # Quick API connectivity test
    log("Testing REST API connectivity...")
    test = api_get("users/me")
    if test:
        log(f"  API OK - logged in as: {test.get('name', '?')} (ID={test.get('id', '?')})")
    else:
        log("  WARNING: REST API /users/me failed - app password may be wrong")
        log(f"  Using: User='{WP_USER}', AppPassword='{WP_APP_PASSWORD[:8]}...'")

    results = []
    for (page_id, slug) in DEV_PAGES:
        log(f"\nProcessing: /{slug}/  (ID={page_id})")

        # Resolve ID if unknown
        if page_id is None:
            page_id = find_page_by_slug(slug)
            if page_id is None:
                log(f"  SKIP: Could not find page with slug '{slug}'")
                results.append({
                    "status": "not_found",
                    "slug": slug,
                    "message": "Page not found by slug",
                })
                continue

        # Try as a page first, then as a post
        result = set_yoast_noindex(page_id, post_type="pages", slug=slug)
        if result.get("status") == "error" and "not found" in result.get("message", ""):
            log(f"  Not found as page, trying as post...")
            result = set_yoast_noindex(page_id, post_type="posts", slug=slug)

        results.append(result)
        time.sleep(1)  # Rate limiting

    return results


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_indexing_status(page) -> dict:
    """
    Quick verification checks:
    1. Homepage robots meta tag
    2. Dev pages robots meta tag
    """
    log("\n--- Verification ---")
    results = {}

    # Check homepage robots
    log("Checking homepage robots meta...")
    page.goto(f"{WP_BASE_URL}/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    robots_meta = page.evaluate("""
        () => {
            const meta = document.querySelector('meta[name="robots"]');
            return meta ? meta.getAttribute('content') : 'NOT FOUND';
        }
    """)
    log(f"  Homepage robots: {robots_meta}")
    results["homepage_robots"] = robots_meta
    screenshot(page, "09_verify_homepage")

    # Check dev pages robots
    dev_page_results = {}
    for (_, slug) in DEV_PAGES:
        url = f"{WP_BASE_URL}/{slug}/"
        log(f"Checking {url}...")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            time.sleep(2)

            page_robots = page.evaluate("""
                () => {
                    const meta = document.querySelector('meta[name="robots"]');
                    return meta ? meta.getAttribute('content') : 'NOT FOUND (page may 404)';
                }
            """)
            page_status = page.evaluate("() => document.title")
            log(f"  robots: {page_robots} | title: {page_status[:50]}")
            dev_page_results[slug] = page_robots

        except Exception as e:
            log(f"  Error: {e}")
            dev_page_results[slug] = f"Error: {e}"

    results["dev_pages"] = dev_page_results
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    log("=" * 60)
    log(f"PureBrain.ai Google Indexing Fix")
    log(f"Started: {datetime.now()}")
    log("=" * 60)

    # Validate credentials
    if not WP_APP_PASSWORD:
        log("FATAL: PUREBRAIN_WP_APP_PASSWORD not set in .env")
        return 1
    if not WP_PASSWORD:
        log("FATAL: PUREBRAIN_WP_PASSWORD not set in .env")
        return 1

    log(f"WP_USER: {WP_USER}")
    log(f"WP_APP_PASSWORD: {WP_APP_PASSWORD[:8]}...{WP_APP_PASSWORD[-4:]}")
    log(f"WP_PASSWORD: {WP_PASSWORD[:4]}...{WP_PASSWORD[-4:]}")

    # Create screenshot directory
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    log(f"Screenshots: {SCREENSHOT_DIR}")

    # Clean up stale CAPTCHA answer file
    if os.path.exists(CAPTCHA_ANSWER_FILE):
        os.remove(CAPTCHA_ANSWER_FILE)

    # -----------------------------------------------------------------------
    # Phase 2 first (REST API - no CAPTCHA needed)
    # -----------------------------------------------------------------------
    phase2_results = phase2_noindex_dev_pages()

    # -----------------------------------------------------------------------
    # Phase 1: Playwright - Fix Settings > Reading
    # -----------------------------------------------------------------------
    phase1_result = {}
    verify_result = {}

    with sync_playwright() as p:
        # device_scale_factor=2 for CAPTCHA readability
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        page.set_default_timeout(30000)

        try:
            logged_in = wp_login(page)
            if not logged_in:
                log("FATAL: Could not log in to WordPress admin")
                browser.close()
                return 1

            phase1_result = check_fix_search_engine_visibility(page)
            verify_result = verify_indexing_status(page)

        except Exception as e:
            log(f"FATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            try:
                screenshot(page, "ERROR_state")
            except Exception:
                pass
            browser.close()
            return 1
        finally:
            browser.close()

    # -----------------------------------------------------------------------
    # Final Report
    # -----------------------------------------------------------------------
    log("\n" + "=" * 60)
    log("FINAL REPORT")
    log("=" * 60)

    log("\n[Phase 1] Settings > Reading (Search Engine Visibility)")
    log(f"  Status:  {phase1_result.get('status', 'unknown')}")
    log(f"  Detail:  {phase1_result.get('message', '')}")

    log("\n[Phase 2] Yoast Noindex on Dev Pages")
    for r in phase2_results:
        status = r.get("status", "unknown")
        slug   = r.get("slug", "?")
        pid    = r.get("page_id", "?")
        msg    = r.get("message", "")
        log(f"  /{slug}/ (ID={pid}): {status}  {msg}")

    log("\n[Verification] Robots Meta Tags")
    log(f"  Homepage: {verify_result.get('homepage_robots', 'N/A')}")
    for slug, robots in verify_result.get("dev_pages", {}).items():
        log(f"  /{slug}/: {robots}")

    log("\n[Screenshots]")
    for f in sorted(SCREENSHOT_DIR.glob(f"*_{TIMESTAMP}.png")):
        log(f"  {f}")

    log("\n" + "=" * 60)
    log("DONE")
    log("=" * 60)

    # Return success if phase1 was fixed or already correct
    p1_status = phase1_result.get("status", "error")
    if p1_status in ("fixed", "already_correct"):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
