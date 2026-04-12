#!/usr/bin/env python3
"""Install (upload + activate) pb-video-handler plugin via WP Admin UI."""

import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
env_text = (AETHER_ROOT / ".env").read_text()


def _env(key):
    m = re.search(rf"^{key}='([^']+)'", env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf"^{key}=([^\n]+)", env_text, re.MULTILINE)
    return m.group(1).strip() if m else ""


WP_USER = _env("PUREBRAIN_WP_USER")
WP_PASS = _env("PUREBRAIN_WP_PASSWORD")

LOGIN_URL = "https://purebrain.ai/wp-login.php?wpaas-standard-login=1"
UPLOAD_URL = "https://purebrain.ai/wp-admin/plugin-install.php?tab=upload"
ZIP_PATH = str((AETHER_ROOT / "exports/pb-video-handler.zip").absolute())
SCREENSHOT_DIR = str((AETHER_ROOT / "exports/screenshots").absolute())


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        # Login
        print("[Step 1] Logging in...")
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        time.sleep(2)
        print(f"  URL: {page.url}")

        # Open upload page
        print("[Step 2] Opening plugin upload page...")
        page.goto(UPLOAD_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        page.screenshot(path=f"{SCREENSHOT_DIR}/pb_vh_upload_page.png")

        has_pluginfile = page.evaluate("() => !!document.querySelector('#pluginzip')")
        print(f"  Upload form present: {has_pluginfile}")
        if not has_pluginfile:
            print("  Body:", page.inner_text("body")[:400])
            browser.close()
            return False

        # Set file input
        print("[Step 3] Attaching zip file...")
        page.locator("#pluginzip").set_input_files(ZIP_PATH)
        time.sleep(1)

        # Submit
        print("[Step 4] Installing plugin...")
        page.click("#install-plugin-submit")
        try:
            page.wait_for_load_state("domcontentloaded", timeout=60000)
        except Exception:
            pass
        time.sleep(5)

        page.screenshot(path=f"{SCREENSHOT_DIR}/pb_vh_install_result.png")
        page_text = page.inner_text("body")
        print(f"  Page text (600 chars): {page_text[:600]}")

        installed = (
            "installed successfully" in page_text.lower()
            or "Plugin installed" in page_text
        )
        already = (
            "already installed" in page_text.lower()
            or "same version" in page_text.lower()
        )

        if installed:
            print("  INSTALLED successfully!")
            # Activate
            print("[Step 5] Activating plugin...")
            activate_link = page.get_by_text("Activate Plugin")
            if activate_link.count() > 0:
                activate_link.first.click()
                page.wait_for_load_state("domcontentloaded", timeout=30000)
                time.sleep(3)
                page.screenshot(path=f"{SCREENSHOT_DIR}/pb_vh_activate_result.png")
                page_text2 = page.inner_text("body")
                if "activated" in page_text2.lower() or "Plugin activated" in page_text2:
                    print("  ACTIVATED successfully!")
                else:
                    print(f"  Activation page: {page_text2[:300]}")
            else:
                print("  No activate link found; checking plugins page...")
        elif already:
            print("  Plugin already exists — will update via editor.")
        else:
            print("  Unexpected result.")

        browser.close()
        return installed or already


if __name__ == "__main__":
    ok = run()
    print("\nResult:", "OK" if ok else "FAIL")
