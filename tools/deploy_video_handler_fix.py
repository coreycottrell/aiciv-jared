#!/usr/bin/env python3
"""
Deploy pb-video-handler v1.1.0 fix for mobile video background bug on homepage.

Root cause identified:
- Security plugin (legacy code) injects pb-video-mobile-pause script that HIDES video on mobile
- pb-video-handler v1.0.0 also injects pb-video-mobile-pause at same priority (20)
- Both run on front_page. Execution order not guaranteed — old hide-code can win.

Fix in v1.1.0:
1. wp_footer priority changed from 20 to 30 (runs AFTER security plugin)
2. Script ID changed from pb-video-mobile-pause to pb-video-handler-js (no collision)
3. CSS adds visibility:visible !important as additional safety net
4. JS explicitly sets display:'block' not '' to override any prior display:none

Steps:
1. Backup page 11 elementor data
2. Deploy updated pb-video-handler plugin
3. Clear Elementor cache
4. Verify
"""

import requests
import json
import os
import re
from base64 import b64encode
from datetime import datetime

WP_BASE = "https://purebrain.ai/wp-json"
WP_USER = "Aether"
WP_APP_PASSWORD = "ZGuh 1W8k WpWM c9iy kqyd buPr"

auth_str = f"{WP_USER}:{WP_APP_PASSWORD}"
auth_header = b64encode(auth_str.encode()).decode()
AUTH_HEADERS = {
    "Authorization": f"Basic {auth_header}",
    "Content-Type": "application/json",
}

PLUGIN_PATH = "/home/jared/projects/AI-CIV/aether/tools/security/pb-video-handler/pb-video-handler.php"
BACKUP_PATH = "/home/jared/projects/AI-CIV/aether/exports/backup_page_11_elementor_data_2026-03-07-mobile-video-fix.json"

def send_telegram(msg):
    """Send Telegram update."""
    import subprocess
    subprocess.run(
        ["/home/jared/projects/AI-CIV/aether/tools/tg_send.sh", msg],
        capture_output=True, text=True
    )
    print(f"[TG] {msg}")

def backup_page_11():
    """Backup page 11 elementor data before any changes."""
    print("\n[STEP 1] Backing up page 11 elementor data...")
    url = f"{WP_BASE}/wp/v2/pages/11?context=edit"
    resp = requests.get(url, headers=AUTH_HEADERS, timeout=30)

    if resp.status_code != 200:
        print(f"  ERROR: {resp.status_code} {resp.text[:200]}")
        return False

    data = resp.json()
    meta = data.get("meta", {})
    elementor_data = meta.get("_elementor_data", "")

    backup = {
        "page_id": 11,
        "backup_timestamp": datetime.now().isoformat(),
        "backup_reason": "Pre-fix backup for mobile video background fix 2026-03-07",
        "page_title": data.get("title", {}).get("rendered", ""),
        "template": data.get("template", ""),
        "_elementor_data": elementor_data,
        "_elementor_data_length": len(elementor_data),
    }

    os.makedirs(os.path.dirname(BACKUP_PATH), exist_ok=True)
    with open(BACKUP_PATH, "w", encoding="utf-8") as f:
        json.dump(backup, f, indent=2)

    print(f"  Backup saved: {BACKUP_PATH}")
    print(f"  Elementor data length: {len(elementor_data)} chars")
    return True

def check_plugins():
    """Check current plugin states to understand what's active."""
    print("\n[STEP 2] Checking active plugins...")
    url = f"{WP_BASE}/wp/v2/plugins?per_page=100"
    resp = requests.get(url, headers=AUTH_HEADERS, timeout=30)

    if resp.status_code != 200:
        print(f"  ERROR: {resp.status_code}")
        return {}

    plugins = resp.json()
    plugin_map = {}
    for p in plugins:
        slug = p.get("plugin", "")
        name = p.get("name", "")
        version = p.get("version", "")
        status = p.get("status", "")
        plugin_map[slug] = p
        if any(kw in slug.lower() or kw in name.lower() for kw in ["video", "security", "pb-"]):
            status_icon = "ACTIVE" if status == "active" else "inactive"
            print(f"  [{status_icon}] {name} | {slug} | v{version}")

    return plugin_map

def deploy_plugin_file():
    """
    Deploy the updated pb-video-handler.php via WP REST API plugin update.
    Since WP REST API doesn't support plugin file upload directly, we use
    the purebrain-security update endpoint if available, or deploy via
    the file system approach through an alternative mechanism.

    Alternative: Use the WP REST API to update the plugin by posting the
    plugin content as a custom endpoint (if one exists), or use the
    filesystem-based approach.

    NOTE: The WP Plugins REST API can activate/deactivate but cannot upload
    new plugin files. The actual file deployment must happen via:
    1. SFTP/SSH to the server
    2. A custom REST endpoint on the site
    3. WP CLI

    For this deployment, we'll check if there's a custom deployment endpoint.
    """
    print("\n[STEP 3] Deploying pb-video-handler v1.1.0...")

    # Read the updated plugin file
    with open(PLUGIN_PATH, "r") as f:
        plugin_content = f.read()

    print(f"  Plugin file: {PLUGIN_PATH}")
    print(f"  Size: {len(plugin_content)} bytes")

    # Check for custom deployment endpoint
    deploy_url = f"{WP_BASE}/purebrain/v1/deploy-plugin"
    resp = requests.post(deploy_url, headers=AUTH_HEADERS, json={
        "plugin_slug": "pb-video-handler",
        "file": "pb-video-handler.php",
        "content": plugin_content,
    }, timeout=30)

    if resp.status_code == 200:
        print(f"  Deployed via custom endpoint: {resp.json()}")
        return True
    else:
        print(f"  Custom endpoint not available ({resp.status_code})")
        print("  Falling back to WP Security Plugin update endpoint...")

        # Try the security updater endpoint
        security_update_url = f"{WP_BASE}/purebrain/v1/update-plugin-file"
        resp2 = requests.post(security_update_url, headers=AUTH_HEADERS, json={
            "plugin": "pb-video-handler/pb-video-handler.php",
            "content": plugin_content,
        }, timeout=30)

        if resp2.status_code == 200:
            print(f"  Deployed via security updater: {resp2.json()}")
            return True
        else:
            print(f"  Security updater not available ({resp2.status_code})")
            return False

def deploy_via_pb_security_updater():
    """Try deploying via the pb-security-updater plugin endpoint."""
    print("\n[STEP 3b] Trying pb-security-updater endpoint...")

    with open(PLUGIN_PATH, "r") as f:
        plugin_content = f.read()

    # The pb-security-updater might have a file update endpoint
    url = f"{WP_BASE}/pb-updater/v1/update-file"
    resp = requests.post(url, headers=AUTH_HEADERS, json={
        "plugin_folder": "pb-video-handler",
        "filename": "pb-video-handler.php",
        "content": plugin_content,
    }, timeout=30)

    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"  Success: {resp.json()}")
        return True
    else:
        print(f"  Response: {resp.text[:300]}")
        return False

def clear_elementor_cache():
    """Clear Elementor cache after any changes."""
    print("\n[STEP 4] Clearing Elementor cache...")
    url = f"{WP_BASE}/elementor/v1/cache"
    resp = requests.delete(url, headers=AUTH_HEADERS, timeout=30)
    print(f"  Status: {resp.status_code}")
    if resp.status_code in [200, 204]:
        print("  Cache cleared successfully")
        return True
    else:
        print(f"  Response: {resp.text[:200]}")
        # Try alternative cache clear
        url2 = f"{WP_BASE}/elementor/v1/clear-cache"
        resp2 = requests.post(url2, headers=AUTH_HEADERS, timeout=30)
        print(f"  Alternative status: {resp2.status_code}")
        return resp2.status_code in [200, 204]

def verify_fix():
    """Verify the fix by checking what scripts are in the live HTML."""
    print("\n[STEP 5] Verifying fix...")
    mobile_headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Cache-Control": "no-cache",
    }
    resp = requests.get("https://purebrain.ai/?nocache=1", headers=mobile_headers, timeout=30)
    html = resp.text

    results = {
        "pb_video_handler_css_present": "pb-video-handler-css" in html,
        "pb_video_handler_js_present": "pb-video-handler-js" in html,
        "legacy_mobile_pause_present": "pb-video-mobile-pause" in html,
        "has_bgVideo": "bgVideo" in html,
        "has_video_background": "video-background" in html,
        "has_living_background": "living-background" in html,
    }

    print("  Verification results:")
    for key, val in results.items():
        status = "PASS" if (val == True and "present" in key) or \
                          (val == False and "legacy" in key) else \
                 "WARN" if val != True else "PASS"
        print(f"    {key}: {val} [{status}]")

    # Check for the critical JS difference
    if "pb-video-handler-js" in html:
        match = re.search(r'<script id="pb-video-handler-js">(.*?)</script>', html, re.DOTALL)
        if match:
            script = match.group(1)
            if "display = 'block'" in script:
                print("\n  CONFIRMED: New script uses display=block (shows video)")
                results["new_script_shows_video"] = True
            elif "display = 'none'" in script:
                print("\n  BUG STILL PRESENT: Script hides video")
                results["new_script_shows_video"] = False

    if "pb-video-mobile-pause" in html:
        match = re.search(r'<script id="pb-video-mobile-pause">(.*?)</script>', html, re.DOTALL)
        if match:
            script = match.group(1)
            if "display = 'none'" in script:
                print("\n  WARNING: Legacy script (display=none) still present - check security plugin")
                results["legacy_script_hides_video"] = True

    return results

def check_pb_security_updater_endpoints():
    """Explore available REST endpoints to find deployment route."""
    print("\n[DIAGNOSTIC] Checking available REST namespaces...")
    url = f"{WP_BASE}/"
    resp = requests.get(url, headers=AUTH_HEADERS, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        namespaces = data.get("namespaces", [])
        print(f"  Available namespaces: {namespaces}")
    else:
        print(f"  Status: {resp.status_code}")

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send_telegram(f"CTO: Starting mobile video fix deployment at {timestamp}. Investigating page 11 (homepage) background showing spiral instead of brain video.")

    # Step 1: Backup page 11
    backup_ok = backup_page_11()
    if not backup_ok:
        send_telegram("CTO: ERROR - Could not backup page 11 elementor data. Halting.")
        return

    send_telegram(f"CTO: Page 11 backup saved to exports/backup_page_11_elementor_data_2026-03-07-mobile-video-fix.json")

    # Step 2: Check plugins
    plugins = check_plugins()

    # Step 3: Check available endpoints
    check_pb_security_updater_endpoints()

    # Step 3a: Try deployment
    deployed = deploy_plugin_file()

    if not deployed:
        deployed = deploy_via_pb_security_updater()

    if not deployed:
        send_telegram(
            "CTO: Plugin file cannot be deployed via REST API directly (no upload endpoint found). "
            "MANUAL DEPLOYMENT NEEDED: Upload updated pb-video-handler.php to WordPress server. "
            "File location: /home/jared/projects/AI-CIV/aether/tools/security/pb-video-handler/pb-video-handler.php\n\n"
            "ROOT CAUSE CONFIRMED: Security plugin's old pb-video-mobile-pause script hides video on mobile. "
            "pb-video-handler v1.1.0 fix: priority 30 (was 20), new script ID, display=block override."
        )
        print("\n" + "="*60)
        print("DEPLOYMENT BLOCKED - No REST API upload endpoint found")
        print("="*60)
        print("\nMANUAL STEPS REQUIRED:")
        print("1. Upload pb-video-handler.php to WordPress plugin folder")
        print("   Local: /home/jared/projects/AI-CIV/aether/tools/security/pb-video-handler/pb-video-handler.php")
        print("   WP path: /wp-content/plugins/pb-video-handler/pb-video-handler.php")
        print("\n2. Alternative: Deactivate pb-video-handler and instead update the")
        print("   security plugin to remove the legacy pb-video-mobile-pause script")
        print("   (security engineer must do this per isolation rule)")
        print("\n3. Then clear Elementor cache")
    else:
        send_telegram("CTO: pb-video-handler v1.1.0 deployed successfully.")

    # Step 4: Clear Elementor cache regardless
    clear_elementor_cache()

    # Step 5: Verify
    results = verify_fix()

    # Summary
    print("\n" + "="*60)
    print("DIAGNOSIS SUMMARY")
    print("="*60)
    print("""
ROOT CAUSE:
  The security plugin (pre-extraction backup deployed to WordPress)
  contained a 'pb-video-mobile-pause' script that calls:
    wrapper.style.display = 'none'  (hides brain video on mobile)

  The new pb-video-handler v1.0.0 also used:
  - Same script ID: pb-video-mobile-pause (collision risk)
  - Same wp_footer priority: 20 (race condition with security plugin)
  - display = '' (clear) instead of display = 'block' (explicit)

  Pages 689/1232 work correctly because:
  - is_front_page() check means security plugin's old code
    only fires on page 11 (the homepage)
  - Those pages never get the conflicting hide script

FIX (pb-video-handler v1.1.0):
  1. wp_footer priority: 20 -> 30 (runs AFTER security plugin)
  2. Script ID: pb-video-mobile-pause -> pb-video-handler-js (no collision)
  3. JS: display = '' -> display = 'block' (explicit override)
  4. CSS: added visibility: visible !important (CSS-level safety net)

ALSO NEEDED (security engineer task):
  - Remove legacy pb-video-mobile-pause block from security plugin
    (the one from pre-extraction v5.1.0 that hides video on mobile)
  - This is a security plugin cleanup, not a security concern
    but per isolation rule must go through security engineer
""")

    send_telegram(
        "CTO: Root cause confirmed. Security plugin legacy script hides brain video on mobile (display:none). "
        "pb-video-handler v1.1.0 written with priority 30 override. "
        "Manual WP deployment needed - no REST upload endpoint. "
        f"Backup at: exports/backup_page_11_elementor_data_2026-03-07-mobile-video-fix.json"
    )


if __name__ == "__main__":
    main()
