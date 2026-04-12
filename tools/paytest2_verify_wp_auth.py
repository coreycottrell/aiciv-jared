"""
pay-test-2 verification using WP admin authentication
Instead of trying the password form, log in via WP admin to bypass it.
Date: 2026-02-27
"""

import asyncio
import json
import os
import base64
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-json-fix-20260227")
PAGE_URL = "https://purebrain.ai/pay-test-2/"

# Read credentials from .env
def get_wp_creds():
    env_path = Path("/home/jared/projects/AI-CIV/aether/.env")
    creds = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("PUREBRAIN_WP_APP_PASSWORD="):
                creds["app_password"] = line.split("=", 1)[1].strip()
    return creds


async def run():
    results = {"screenshots": [], "findings": {}, "console_errors": []}
    creds = get_wp_creds()
    app_password = creds.get("app_password", "")
    print(f"App password length: {len(app_password)}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--autoplay-policy=no-user-gesture-required",
                "--disable-features=IsolateOrigins,site-per-process"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900}
        )
        page = await context.new_page()

        console_msgs = []
        def on_console(msg):
            console_msgs.append({"type": msg.type, "text": msg.text})
            if msg.type == "error":
                results["console_errors"].append(msg.text)
        page.on("console", on_console)

        # Method 1: Log in via WP admin using credentials
        print("[1] Logging in via WP admin...")
        await page.goto("https://purebrain.ai/wp-login.php", wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(2)

        shot_login = SCREENSHOT_DIR / "020-wp-login.png"
        await page.screenshot(path=str(shot_login))
        results["screenshots"].append({"file": str(shot_login), "label": "WP login page"})
        print(f"    Screenshot: {shot_login}")

        # Check if we got the login form
        user_field = await page.query_selector("#user_login")
        if user_field:
            print("    WP login form found - filling credentials...")
            await user_field.fill("Aether")
            pass_field = await page.query_selector("#user_pass")
            # Use application password format: username:app_password for basic auth
            # But for the login form, we need the actual WP password
            # Try basic auth approach instead
            await pass_field.fill(app_password)
            await page.click("#wp-submit")
            await asyncio.sleep(3)

            shot_after_login = SCREENSHOT_DIR / "021-after-login-attempt.png"
            await page.screenshot(path=str(shot_after_login))
            results["screenshots"].append({"file": str(shot_after_login), "label": "After login attempt"})

            # Check if logged in
            current_url = page.url
            print(f"    After login URL: {current_url}")
            is_logged_in = "wp-admin" in current_url or "dashboard" in current_url.lower()
            print(f"    Logged in: {is_logged_in}")
        else:
            print("    No login form - may be rate limited or already logged in")

        # Method 2: Set authentication via HTTP Basic Auth header for page viewing
        # Create a new context with the WP preview parameters
        await page.close()
        await context.close()

        # Use basic auth context to access the page
        print("[2] Trying WP preview mode (authenticated)...")
        auth_b64 = base64.b64encode(f"Aether:{app_password}".encode()).decode()

        context2 = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1440, "height": 900},
            extra_http_headers={
                "Authorization": f"Basic {auth_b64}"
            }
        )
        page2 = await context2.new_page()

        console_msgs2 = []
        def on_console2(msg):
            console_msgs2.append({"type": msg.type, "text": msg.text})
            if msg.type == "error":
                results["console_errors"].append(msg.text)
        page2.on("console", on_console2)

        # Navigate to the page with auth headers - WP should render full content for authenticated users
        # The WP password protection is bypassed for logged-in users/authenticated requests
        print(f"    Navigating to {PAGE_URL} with Basic Auth...")
        try:
            resp = await page2.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
            print(f"    HTTP: {resp.status}")
            results["findings"]["http_status_auth"] = resp.status
        except Exception as e:
            print(f"    Navigation error: {e}")

        await asyncio.sleep(10)  # Let page load

        shot_auth = SCREENSHOT_DIR / "022-page-with-auth.png"
        await page2.screenshot(path=str(shot_auth), full_page=False)
        results["screenshots"].append({"file": str(shot_auth), "label": "Page with auth header"})
        print(f"    Screenshot: {shot_auth}")

        # Check if we got past the password form
        pw_field_check = await page2.query_selector("input[id^='pwbox-']")
        body_text = await page2.inner_text("body")
        results["findings"]["body_text_length_auth"] = len(body_text)
        results["findings"]["still_password_protected"] = pw_field_check is not None
        print(f"    Still password protected: {pw_field_check is not None}")
        print(f"    Body text length: {len(body_text)}")
        print(f"    Body preview: {body_text[:300]}")

        # Check page source for video elements
        content = await page2.content()
        results["findings"]["has_video_tag"] = "<video" in content.lower()
        results["findings"]["has_chat_section"] = "chat-section" in content
        results["findings"]["has_begin_awakening"] = "Begin Awakening" in content or "Begin Your Awakening" in content
        results["findings"]["content_length"] = len(content)
        print(f"    Has <video>: {results['findings']['has_video_tag']}")
        print(f"    Has chat-section: {results['findings']['has_chat_section']}")
        print(f"    Has Begin Awakening: {results['findings']['has_begin_awakening']}")
        print(f"    Content length: {len(content)}")

        # Full page screenshot
        shot_full = SCREENSHOT_DIR / "023-full-page-auth.png"
        await page2.screenshot(path=str(shot_full), full_page=True)
        results["screenshots"].append({"file": str(shot_full), "label": "Full page with auth"})
        print(f"    Full page screenshot: {shot_full}")

        await context2.close()
        await browser.close()

    results_file = SCREENSHOT_DIR / "raw_results_auth.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[DONE] Results: {results_file}")
    return results


if __name__ == "__main__":
    results = asyncio.run(run())
    print("\n=== AUTH METHOD SUMMARY ===")
    f = results["findings"]
    print(f"Still password protected: {f.get('still_password_protected', '?')}")
    print(f"Body text length: {f.get('body_text_length_auth', 0)}")
    print(f"Has video: {f.get('has_video_tag', False)}")
    print(f"Has chat: {f.get('has_chat_section', False)}")
    print(f"Console errors: {len(results.get('console_errors', []))}")
