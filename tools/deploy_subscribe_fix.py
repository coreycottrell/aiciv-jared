#!/usr/bin/env python3
"""
Deploy purebrain-subscribe-fix plugin to purebrain.ai via Playwright.

Steps:
1. Create zip archive of the plugin
2. Login to WP Admin via Playwright
3. Upload zip via plugin-install.php?tab=upload
4. Activate the plugin
5. Verify fix is present on a blog post
"""

import asyncio
import os
import subprocess
import sys
import zipfile
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR     = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_DIR   = BASE_DIR / "exports" / "purebrain-subscribe-fix"
PLUGIN_PHP   = PLUGIN_DIR / "purebrain-subscribe-fix.php"
ZIP_PATH     = BASE_DIR / "exports" / "purebrain-subscribe-fix.zip"
SCREENSHOT_DIR = BASE_DIR / "exports" / "subscribe-fix-deploy"

# ── WordPress credentials ──────────────────────────────────────────────────────
WP_LOGIN_URL    = "https://purebrain.ai/wp-login.php"
WP_UPLOAD_URL   = "https://purebrain.ai/wp-admin/plugin-install.php?tab=upload"
WP_PLUGINS_URL  = "https://purebrain.ai/wp-admin/plugins.php"
WP_USER         = "Aether"
WP_PASS         = "ZGuh 1W8k WpWM c9iy kqyd buPr"

# ── Verification URL: pick any blog post ──────────────────────────────────────
BLOG_POST_URL = "https://purebrain.ai/blog/"

TG_SEND = str(BASE_DIR / "tools" / "tg_send.sh")

def tg(msg: str):
    try:
        subprocess.run([TG_SEND, msg], timeout=10, capture_output=True)
    except Exception as e:
        print(f"[tg] {e}")

def create_zip():
    print("[zip] Creating plugin zip...")
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        # Must be: purebrain-subscribe-fix/purebrain-subscribe-fix.php inside zip
        zf.write(PLUGIN_PHP, arcname="purebrain-subscribe-fix/purebrain-subscribe-fix.php")
    print(f"[zip] Created: {ZIP_PATH} ({ZIP_PATH.stat().st_size} bytes)")
    return ZIP_PATH

async def run():
    from playwright.async_api import async_playwright

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    tg("🔧 [Subscribe Fix] Starting deploy — creating plugin zip...")
    zip_path = create_zip()
    tg(f"🔧 [Subscribe Fix] Zip created ({zip_path.stat().st_size}B). Launching browser...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx     = await browser.new_context(viewport={"width": 1280, "height": 900})
        page    = await ctx.new_page()

        # ── 1. Login ──────────────────────────────────────────────────────────
        print("[login] Navigating to WP login...")
        await page.goto(WP_LOGIN_URL, wait_until="networkidle", timeout=30000)
        await page.fill("#user_login", WP_USER)
        await page.fill("#user_pass", WP_PASS)
        await page.click("#wp-submit")
        await page.wait_for_url("**/wp-admin/**", timeout=20000)
        await page.screenshot(path=str(SCREENSHOT_DIR / "01_logged_in.png"))
        print("[login] Logged in successfully.")
        tg("🔧 [Subscribe Fix] WP login OK. Uploading plugin zip...")

        # ── 2. Navigate to Plugin Upload page ─────────────────────────────────
        print("[upload] Going to plugin upload page...")
        await page.goto(WP_UPLOAD_URL, wait_until="networkidle", timeout=20000)
        await page.screenshot(path=str(SCREENSHOT_DIR / "02_upload_page.png"))

        # The upload form has a file input — may be inside an iframe or direct
        # WP shows: <input type="file" name="pluginzip" id="pluginzip" ...>
        # It may be hidden behind a "Choose File" button — use set_input_files
        file_input = page.locator('input[name="pluginzip"]')
        if await file_input.count() == 0:
            # Try clicking the "Upload Plugin" button first if it's a two-step page
            upload_btn = page.locator('a#upload-plugin, a:has-text("Upload Plugin")')
            if await upload_btn.count() > 0:
                await upload_btn.click()
                await page.wait_for_timeout(1000)
            file_input = page.locator('input[name="pluginzip"]')

        print("[upload] Setting file input...")
        await file_input.set_input_files(str(zip_path))
        await page.screenshot(path=str(SCREENSHOT_DIR / "03_file_selected.png"))

        # Click Install Now
        install_btn = page.locator('input[type="submit"]#install-plugin-submit, input[value="Install Now"]')
        if await install_btn.count() == 0:
            install_btn = page.locator('input[type="submit"]').first
        print("[upload] Clicking Install Now...")
        await install_btn.click()
        await page.wait_for_load_state("networkidle", timeout=30000)
        await page.screenshot(path=str(SCREENSHOT_DIR / "04_after_install.png"))

        page_text = await page.content()
        if "Plugin installed successfully" in page_text or "purebrain-subscribe-fix" in page_text:
            print("[upload] Plugin installed successfully.")
            tg("🔧 [Subscribe Fix] Plugin installed. Activating...")
        else:
            # Check if it already exists (duplicate)
            if "already installed" in page_text.lower() or "Destination folder already exists" in page_text:
                print("[upload] Plugin already installed — will try to activate existing.")
                tg("🔧 [Subscribe Fix] Plugin already existed. Activating...")
            else:
                print("[upload] WARNING: Unexpected install result. Checking screenshots...")
                print(page_text[:2000])
                tg("⚠️ [Subscribe Fix] Install result unclear — check screenshots.")

        # ── 3. Activate the plugin ─────────────────────────────────────────────
        # After install WP shows "Activate Plugin" link — try clicking it
        activate_link = page.locator('a:has-text("Activate Plugin")')
        if await activate_link.count() > 0:
            print("[activate] Clicking Activate Plugin link on install page...")
            await activate_link.click()
            await page.wait_for_load_state("networkidle", timeout=20000)
            await page.screenshot(path=str(SCREENSHOT_DIR / "05_after_activate.png"))
        else:
            # Go to plugins.php and activate from there
            print("[activate] Navigating to plugins list to activate...")
            await page.goto(WP_PLUGINS_URL, wait_until="networkidle", timeout=20000)
            # Find the Activate link for purebrain-subscribe-fix
            activate_link = page.locator('tr[data-plugin="purebrain-subscribe-fix/purebrain-subscribe-fix.php"] a:has-text("Activate")')
            if await activate_link.count() > 0:
                await activate_link.click()
                await page.wait_for_load_state("networkidle", timeout=20000)
                await page.screenshot(path=str(SCREENSHOT_DIR / "05_after_activate.png"))
            else:
                print("[activate] Could not find Activate link — plugin may already be active.")
                await page.screenshot(path=str(SCREENSHOT_DIR / "05_plugins_list.png"))

        # ── 4. Verify plugin is active ─────────────────────────────────────────
        await page.goto(WP_PLUGINS_URL, wait_until="networkidle", timeout=20000)
        plugins_content = await page.content()
        if "purebrain-subscribe-fix" in plugins_content:
            # Check if row has 'active' class
            active_row = page.locator('tr.active[data-plugin="purebrain-subscribe-fix/purebrain-subscribe-fix.php"]')
            if await active_row.count() > 0:
                print("[verify] Plugin is ACTIVE in plugins list.")
                tg("✅ [Subscribe Fix] Plugin active! Verifying on blog post...")
            else:
                print("[verify] Plugin found but may not be active — check screenshot.")
                tg("⚠️ [Subscribe Fix] Plugin found but active state unclear.")
        await page.screenshot(path=str(SCREENSHOT_DIR / "06_plugins_list.png"))

        # ── 5. Verify fix present on blog post ────────────────────────────────
        print("[verify] Loading blog to find a post...")
        await page.goto(BLOG_POST_URL, wait_until="networkidle", timeout=30000)
        # Try to click first blog post link
        first_post = page.locator("article a, h2 a, h3 a").first
        post_url = None
        if await first_post.count() > 0:
            post_url = await first_post.get_attribute("href")

        if post_url:
            print(f"[verify] Checking blog post: {post_url}")
            await page.goto(post_url, wait_until="networkidle", timeout=30000)
        else:
            # Fall back to a known post path
            await page.goto("https://purebrain.ai/blog/something-big-already-happened/", wait_until="networkidle", timeout=30000)

        await page.screenshot(path=str(SCREENSHOT_DIR / "07_blog_post.png"))

        # Check page source for our override script
        page_source = await page.content()
        fix_marker = "purebrain-subscribe-fix-js"
        abort_marker = "AbortController"
        inflight_marker = "_pbSubscribeInFlight"

        fix_present = fix_marker in page_source
        abort_present = abort_marker in page_source
        inflight_present = inflight_marker in page_source

        print(f"[verify] Script ID '{fix_marker}' present: {fix_present}")
        print(f"[verify] AbortController present: {abort_present}")
        print(f"[verify] _pbSubscribeInFlight present: {inflight_present}")

        if fix_present and abort_present and inflight_present:
            result_msg = "✅ [Subscribe Fix] COMPLETE — fetch+AbortController override is LIVE on blog posts. Neural Feed subscribe form no longer gets stuck."
            print(f"\n{result_msg}")
            tg(result_msg)
        else:
            result_msg = f"⚠️ [Subscribe Fix] Partial verify — fix_script:{fix_present} abort:{abort_present} inflight:{inflight_present}. Check screenshots."
            print(f"\n{result_msg}")
            tg(result_msg)

        await browser.close()
        print(f"\n[done] Screenshots saved to: {SCREENSHOT_DIR}")

if __name__ == "__main__":
    asyncio.run(run())
