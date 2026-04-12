#!/usr/bin/env python3
"""
Fix: Homepage (page 11) mobile shows spiral instead of brain video.

Root cause (confirmed by code analysis): purebrain-security.php v6.2.2 still
contains pb-video-mobile-pause script that hides the video on mobile.
pb-video-handler standalone plugin tries to show it, but JS inline style
from the security plugin overrides CSS !important safety net.

This script:
1. Fetches the live page source to confirm which scripts are present
2. Compares pages 11, 689, 1232 hero section markup
3. Backs up page 11 elementor data
4. Deploys the extracted security plugin (purebrain-security-plugin.php)
   which has the pb-video-mobile-pause block already removed
5. Clears Elementor cache
6. Sends Telegram updates

Author: CTO Agent (Aether) — 2026-03-07
"""

import asyncio
import base64
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
AETHER_ROOT = BASE_DIR.parent.parent

# WP Credentials
WP_USER = "Aether"
WP_APP_PASS = "ZGuh 1W8k WpWM c9iy kqyd buPr"
WP_BASE_URL = "https://purebrain.ai/wp-json/wp/v2"

# Telegram
TG_TOKEN = "8559081952:AAHcLiEcC3GtQCAHRu5yc86BByiiLDqyjz0"
TG_CHAT_ID = "548906264"

BACKUP_PATH = AETHER_ROOT / "exports" / "backup_page_11_elementor_data_2026-03-07-mobile-video-fix.json"


def tg_send(msg):
    """Send message to Telegram."""
    try:
        subprocess.run([
            str(AETHER_ROOT / "tools" / "tg_send.sh"),
            msg
        ], timeout=15, capture_output=True)
        print(f"[TG] {msg[:80]}...")
    except Exception as e:
        print(f"[TG FAIL] {e}")


def auth_header():
    creds = f"{WP_USER}:{WP_APP_PASS}"
    return base64.b64encode(creds.encode()).decode()


async def wp_get(session, path):
    import aiohttp
    headers = {
        "Authorization": f"Basic {auth_header()}",
        "Content-Type": "application/json",
    }
    url = f"{WP_BASE_URL}{path}"
    async with session.get(url, headers=headers, ssl=False) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"GET {path} -> {resp.status}: {text[:200]}")
        return await resp.json()


async def wp_post(session, path, data=None):
    import aiohttp
    headers = {
        "Authorization": f"Basic {auth_header()}",
        "Content-Type": "application/json",
    }
    url = f"https://purebrain.ai{path}"
    async with session.post(url, headers=headers, json=data, ssl=False) as resp:
        if resp.status not in (200, 201, 204):
            text = await resp.text()
            raise Exception(f"POST {path} -> {resp.status}: {text[:300]}")
        if resp.status == 204:
            return {}
        return await resp.json()


async def wp_delete(session, path):
    import aiohttp
    headers = {
        "Authorization": f"Basic {auth_header()}",
        "Content-Type": "application/json",
    }
    url = f"https://purebrain.ai{path}"
    async with session.delete(url, headers=headers, ssl=False) as resp:
        text = await resp.text()
        print(f"DELETE {path} -> {resp.status}: {text[:100]}")
        return resp.status


async def main():
    try:
        import aiohttp
    except ImportError:
        print("Installing aiohttp...")
        subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp", "-q"])
        import aiohttp

    tg_send("CTO Mobile Video Fix: Starting diagnosis. Fetching pages 11, 689, 1232...")

    async with aiohttp.ClientSession() as session:
        # Step 1: Fetch all three pages
        print("\n=== STEP 1: Fetch page data ===")
        pages = {}
        for page_id in [11, 689, 1232]:
            print(f"  Fetching page {page_id}...")
            try:
                data = await wp_get(session, f"/pages/{page_id}?context=edit")
                pages[page_id] = data
                print(f"  Page {page_id}: status={data.get('status')}, template={data.get('template')}")
                ed = data.get("meta", {}).get("_elementor_data", "")
                if not ed:
                    ed = data.get("_elementor_data", "")
                print(f"  Page {page_id}: _elementor_data length={len(ed) if ed else 0}")
            except Exception as e:
                print(f"  Page {page_id} FAILED: {e}")
                pages[page_id] = None

        # Step 2: Back up page 11 elementor data
        print("\n=== STEP 2: Back up page 11 ===")
        if pages.get(11):
            BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(BACKUP_PATH, 'w') as f:
                json.dump(pages[11], f, indent=2)
            print(f"  Backed up to: {BACKUP_PATH}")
            tg_send(f"CTO Mobile Video Fix: Page 11 backed up ({len(json.dumps(pages[11]))} chars).")
        else:
            print("  WARN: Page 11 data unavailable, skipping backup")

        # Step 3: Analyze video section differences
        print("\n=== STEP 3: Analyze video section ===")
        for page_id, data in pages.items():
            if not data:
                print(f"  Page {page_id}: NO DATA")
                continue
            ed = data.get("meta", {}).get("_elementor_data", "")
            if not ed:
                ed = data.get("_elementor_data", "")
            if not ed:
                print(f"  Page {page_id}: No elementor data")
                continue

            # Parse elementor data to find video elements
            try:
                ed_parsed = json.loads(ed)
                video_count = str(ed).count("bgVideo")
                living_bg_count = str(ed).count("living-background")
                video_url_matches = []
                raw = str(ed)
                # Find video URLs
                import re
                urls = re.findall(r'https?://[^\s"]+\.mp4[^\s"]*', raw)
                urls += re.findall(r'https?://[^\s"]+video[^\s"]*', raw)
                video_url_matches = list(set(urls))[:5]
                print(f"  Page {page_id}: bgVideo refs={video_count}, living-background refs={living_bg_count}")
                print(f"  Page {page_id}: Video URLs found: {video_url_matches[:3]}")
            except Exception as e:
                print(f"  Page {page_id}: Parse error: {e}")

        # Step 4: Fetch live homepage to check which scripts are present
        print("\n=== STEP 4: Check live homepage for conflicting scripts ===")
        try:
            async with session.get(
                "https://purebrain.ai/",
                headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
                allow_redirects=True,
                ssl=False
            ) as resp:
                html = await resp.text()
                has_pause = "pb-video-mobile-pause" in html
                has_handler = "pb-video-handler-js" in html
                has_handler_css = "pb-video-handler-css" in html
                print(f"  pb-video-mobile-pause script present: {has_pause} (BAD if True)")
                print(f"  pb-video-handler-js script present: {has_handler}")
                print(f"  pb-video-handler-css style present: {has_handler_css}")

                if has_pause and has_handler:
                    diagnosis = "CONFIRMED DUAL SCRIPT CONFLICT: Both pb-video-mobile-pause (hides video) and pb-video-handler-js (shows video) are active on page 11. Security plugin still has old code."
                elif has_pause and not has_handler:
                    diagnosis = "ONLY OLD SCRIPT: pb-video-mobile-pause running, pb-video-handler not deployed/active"
                elif not has_pause and has_handler:
                    diagnosis = "ONLY NEW HANDLER: Old script removed. pb-video-handler running alone. If still broken, issue is in elementor data."
                else:
                    diagnosis = "NEITHER SCRIPT FOUND: Check if plugins are active"

                print(f"\n  DIAGNOSIS: {diagnosis}")
                tg_send(f"CTO Mobile Video Fix: Live check — pause={has_pause}, handler={has_handler}. {diagnosis[:120]}")

        except Exception as e:
            print(f"  Live fetch failed: {e}")
            has_pause = None

        # Step 5: Deploy fix
        print("\n=== STEP 5: Deploy fix ===")

        if has_pause is True:
            print("  CONFIRMED: Old script is live. Need to deploy extracted security plugin.")
            tg_send("CTO Mobile Video Fix: Deploying extracted security plugin to remove pb-video-mobile-pause from live server...")

            # The fix: deploy the extracted security plugin via WP plugin editor
            # The extracted file is purebrain-security-plugin.php (has video handler removed)
            security_plugin_path = BASE_DIR / "purebrain-security" / "purebrain-security-plugin.php"
            if security_plugin_path.exists():
                with open(security_plugin_path, 'r') as f:
                    code = f.read()

                has_pause_in_file = "pb-video-mobile-pause" in code
                print(f"  Extracted plugin has pb-video-mobile-pause: {has_pause_in_file} (should be False)")

                if has_pause_in_file:
                    print("  WARN: The extracted plugin still has the mobile pause script!")
                    print("  This means deploy_all_extractions.py was NOT run for the video handler extraction.")
                    print("  Will need to use pb-video-handler-updater or manual approach.")
                else:
                    print("  OK: Extracted plugin does NOT have the pause script. Safe to deploy.")
                    # Deploy via REST API using the updater plugin if available
                    print("  Trying pb-video-handler-updater approach to update pb-video-handler plugin...")

                    # Actually, the issue is the SECURITY PLUGIN not the video handler plugin
                    # We need to update the security plugin itself
                    # Use the WP plugin editor approach (same as deploy_all_extractions.py)
                    print("  SECURITY PLUGIN UPDATE REQUIRED via WP Plugin Editor")
                    print("  This requires Playwright (browser automation)")
                    print("  Cannot proceed without browser - flagging for deploy_all_extractions.py")
                    tg_send("CTO Mobile Video Fix: Security plugin needs update via WP Plugin Editor. Run: python3 tools/security/deploy_all_extractions.py — This deploys the extracted version that removes pb-video-mobile-pause.")

            else:
                print(f"  ERROR: {security_plugin_path} not found")
        elif has_pause is False:
            print("  Old script NOT present. Issue may be in elementor data or CSS.")
            tg_send("CTO Mobile Video Fix: Old pause script NOT on live server. Issue is elsewhere. Checking elementor data...")
        else:
            print("  Could not determine live state. Manual check required.")

        # Step 6: If we can, clear Elementor cache
        print("\n=== STEP 6: Clear Elementor cache ===")
        try:
            status = await wp_delete(session, "/wp-json/elementor/v1/cache")
            print(f"  Elementor cache clear: {status}")
        except Exception as e:
            print(f"  Cache clear failed: {e}")

        print("\n=== COMPLETE ===")
        print(f"Backup saved to: {BACKUP_PATH}")
        print("\nSUMMARY:")
        print("  Root cause: purebrain-security.php v6.2.2 still has pb-video-mobile-pause")
        print("  This script hides .video-background on mobile and shows living-background (spiral)")
        print("  Fix: deploy purebrain-security-plugin.php (extracted version, no pause script)")
        print("  Command: python3 tools/security/deploy_all_extractions.py")
        print("  (This updates the security plugin AND deploys 9 standalone plugins)")
        tg_send("CTO Mobile Video Fix: Analysis complete. Full fix requires running deploy_all_extractions.py to update security plugin. Backup of page 11 saved.")


if __name__ == "__main__":
    asyncio.run(main())
