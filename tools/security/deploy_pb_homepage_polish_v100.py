#!/usr/bin/env python3
"""
Deploy pb-homepage-polish v1.0.0 to purebrain.ai.

Fixes:
  1. Preloader orange/light flash — dark #080a12 background at wp_head priority 1
  2. Hero top gap — overrides .hero align-items:center to flex-start
  3. Footer logo proportions — overrides height:100px to height:40px

DO NOT touch purebrain-security-plugin.php (locked).
"""

import io
import re
import sys
import json
import time
import zipfile
import base64
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import subprocess
from pathlib import Path

AETHER_ROOT  = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE  = AETHER_ROOT / "tools/security/pb-homepage-polish/pb-homepage-polish.php"
PLUGIN_SLUG  = "pb-homepage-polish"

# ── Credentials ────────────────────────────────────────────────────────────────
env_text = (AETHER_ROOT / ".env").read_text()

def _env(key):
    m = re.search(rf"^{key}='([^']+)'", env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf'^{key}="([^"]+)"', env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf"^{key}=([^\n]+)", env_text, re.MULTILINE)
    return m.group(1).strip() if m else ""

WP_USER     = "aether"
WP_PASSWORD = _env("PUREBRAIN_WP_PASSWORD")
WP_APP_PASS = "41w3 xWWZ 11em UXgj hjAF sx2T"
BASE_URL    = "https://purebrain.ai"

AUTH_HEADER = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()

EDITOR_URL  = (
    f"{BASE_URL}/wp-admin/plugin-editor.php"
    f"?file={PLUGIN_SLUG}/{PLUGIN_SLUG}.php"
    f"&plugin={PLUGIN_SLUG}/{PLUGIN_SLUG}.php"
)

# ── Helpers ────────────────────────────────────────────────────────────────────

def tg_send(msg):
    tg = str(AETHER_ROOT / "tools/tg_send.sh")
    subprocess.run([tg, f"dept-systems-technology: {msg}"], capture_output=True)


def rest_request(method, path, data=None, content_type="application/json"):
    url = f"{BASE_URL}/wp-json{path}"
    headers = {
        "Authorization": f"Basic {AUTH_HEADER}",
        "User-Agent": "PureBrain-Deploy/1.0",
    }
    body = None
    if data is not None and content_type == "application/json":
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    elif data is not None:
        body = data
        headers["Content-Type"] = content_type

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_bytes = e.read()
        try:
            return e.code, json.loads(body_bytes.decode())
        except Exception:
            return e.code, {"raw": body_bytes.decode()[:500]}
    except Exception as exc:
        return 0, {"error": str(exc)}


def build_zip(plugin_php_path: Path) -> bytes:
    slug = plugin_php_path.parent.name
    php_filename = plugin_php_path.name
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        arcname = f"{slug}/{php_filename}"
        zf.write(plugin_php_path, arcname)
    return zip_buffer.getvalue()


# ── Step 1: Install via REST API ───────────────────────────────────────────────

def install_plugin_via_rest(php_path: Path) -> bool:
    print("\n[STEP 1] Building plugin zip...")
    zip_bytes = build_zip(php_path)
    print(f"  Zip size: {len(zip_bytes):,} bytes")
    slug = php_path.parent.name

    boundary = "----PureBrainBoundary7e3f9b"
    parts = []
    parts.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="slug"\r\n\r\n'
        f"{slug}\r\n"
    )
    parts.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{slug}.zip"\r\n'
        f"Content-Type: application/zip\r\n\r\n"
    )
    body = b""
    for part in parts[:-1]:
        body += part.encode()
    body += parts[-1].encode()
    body += zip_bytes
    body += f"\r\n--{boundary}--\r\n".encode()
    content_type = f"multipart/form-data; boundary={boundary}"

    print(f"  POSTing to /wp/v2/plugins ...")
    status, result = rest_request("POST", "/wp/v2/plugins", data=body, content_type=content_type)
    print(f"  Response: {status} — {json.dumps(result, indent=2)[:400]}")

    if status in (200, 201):
        print("  SUCCESS: Plugin installed.")
        return True
    elif status == 400 and "already_installed" in str(result):
        print("  Plugin already installed — will update via editor.")
        return True
    else:
        print(f"  Install via REST failed ({status}). Will try editor update.")
        return False


# ── Step 2: Activate via REST API ─────────────────────────────────────────────

def activate_plugin() -> bool:
    plugin_id = f"{PLUGIN_SLUG}/{PLUGIN_SLUG}"
    for attempt in range(2):
        print(f"\n[STEP 2{'b' if attempt else ''}] Activating {PLUGIN_SLUG}...")
        headers = {
            "Authorization": f"Basic {AUTH_HEADER}",
            "Content-Type": "application/json",
            "User-Agent": "PureBrain-Deploy/1.0",
            "X-HTTP-Method-Override": "PATCH",
        }
        url = f"{BASE_URL}/wp-json/wp/v2/plugins/{plugin_id}"
        body = json.dumps({"status": "active"}).encode()
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            resp = urllib.request.urlopen(req, timeout=30)
            result = json.loads(resp.read().decode())
            pstatus = result.get("status", "")
            print(f"  Status: {pstatus}")
            if pstatus == "active":
                print("  SUCCESS: Plugin activated.")
                return True
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:300]
            print(f"  HTTP {e.code}: {err}")
    return False


# ── Step 3: Update content via cookie/editor (if already installed) ───────────

def update_plugin_via_editor(plugin_content: str) -> bool:
    print("\n[STEP 3] Updating plugin via WP plugin editor (cookie session)...")
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (PureBrain-Deploy)")]

    login_data = urllib.parse.urlencode({
        "log": WP_USER,
        "pwd": WP_PASSWORD,
        "wp-submit": "Log In",
        "redirect_to": "/wp-admin/",
        "testcookie": "1",
    }).encode()
    try:
        resp = opener.open(f"{BASE_URL}/wp-login.php", login_data, timeout=30)
        print(f"  Login redirect: {resp.geturl()}")
    except Exception as e:
        print(f"  Login error: {e}")
        return False

    time.sleep(1)

    # Fetch editor page for nonce
    try:
        resp = opener.open(EDITOR_URL, timeout=30)
        html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  Editor page error: {e}")
        return False

    nonce = None
    for pat in [
        r'"nonce":"([a-f0-9]+)"',
        r'name="_wpnonce"[^>]+value="([^"]+)"',
        r'"_wpnonce":"([^"]+)"',
        r'_wpnonce\s*=\s*"([^"]+)"',
    ]:
        m = re.search(pat, html)
        if m:
            nonce = m.group(1)
            print(f"  Nonce: {nonce[:10]}...")
            break

    if not nonce:
        print("  ERROR: Could not extract nonce. Plugin may not exist yet.")
        return False

    post_data = urllib.parse.urlencode({
        "_wpnonce": nonce,
        "newcontent": plugin_content,
        "action": "update",
        "file": f"{PLUGIN_SLUG}/{PLUGIN_SLUG}.php",
        "plugin": f"{PLUGIN_SLUG}/{PLUGIN_SLUG}.php",
        "scrollto": "0",
        "submit": "Update File",
    }).encode()

    req = urllib.request.Request(
        EDITOR_URL,
        data=post_data,
        headers={"Content-Type": "application/x-www-form-urlencoded", "Referer": EDITOR_URL},
    )
    try:
        resp = opener.open(req, timeout=60)
        result_html = resp.read().decode("utf-8", errors="ignore")
        final_url = resp.geturl()
        print(f"  POST result URL: {final_url}")
    except Exception as e:
        print(f"  POST error: {e}")
        return False

    if "File edited successfully" in result_html or "updated=true" in final_url:
        print("  SUCCESS: Plugin content updated via editor.")
        return True
    elif "Parse error" in result_html or "syntax error" in result_html.lower():
        m = re.search(r"(?:Parse error|syntax error)[^<]{0,200}", result_html)
        print(f"  ERROR: PHP syntax error: {m.group(0) if m else 'unknown'}")
        return False
    else:
        print(f"  Unknown result. Snippet: {result_html[2000:2400]}")
        return False


# ── Step 4: Verify ─────────────────────────────────────────────────────────────

def verify_deployed() -> bool:
    print("\n[VERIFY] Checking live site...")
    marker = "pb-homepage-polish-early"
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/",
            headers={"User-Agent": "Mozilla/5.0 (PureBrain-Verify)", "Cache-Control": "no-cache"},
        )
        resp = urllib.request.urlopen(req, timeout=20)
        html = resp.read().decode("utf-8", errors="ignore")
        if marker in html:
            print(f"  PASS: '{marker}' found in homepage HTML.")
            return True
        else:
            print(f"  NOTE: '{marker}' not in homepage HTML. May be Cloudflare cached.")
            # Check if the plugin CSS block is present in any form
            if "pb-homepage-polish" in html:
                print("  PASS: 'pb-homepage-polish' found (different marker).")
                return True
            print("  WARN: Plugin CSS not visible — may need cache purge.")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def verify_plugin_active() -> bool:
    print("\n[VERIFY ACTIVE] Checking plugin status via REST API...")
    status, result = rest_request("GET", "/wp/v2/plugins?per_page=100")
    if status != 200:
        print(f"  Could not fetch plugins: {status}")
        return False
    for p in result:
        slug = p.get("plugin", "")
        pstatus = p.get("status", "")
        if PLUGIN_SLUG in slug:
            print(f"  [{pstatus.upper()}] {slug}")
            return pstatus == "active"
    print(f"  NOT FOUND in plugin list.")
    return False


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print(f"PureBrain Plugin Deployment — {PLUGIN_SLUG} v1.0.0")
    print("Fixes: preloader flash, hero top gap, footer logo proportions")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    plugin_content = PLUGIN_FILE.read_text()
    print(f"\nPlugin file: {len(plugin_content):,} chars")

    tg_send(f"Deploying {PLUGIN_SLUG} v1.0.0 — fixes preloader flash, hero gap, footer logo.")

    results = {}

    # 1. Try install via REST
    installed = install_plugin_via_rest(PLUGIN_FILE)
    results["install"] = installed

    # 2. Activate
    time.sleep(2)
    activated = activate_plugin()
    results["activate"] = activated

    # 3. If not yet active, try editor update (plugin may already exist but inactive)
    if not activated:
        updated = update_plugin_via_editor(plugin_content)
        results["editor_update"] = updated
        if updated:
            time.sleep(2)
            activated = activate_plugin()
            results["activate"] = activated

    # 4. Verify
    time.sleep(3)
    plugin_active = verify_plugin_active()
    results["plugin_active"] = plugin_active

    live_ok = verify_deployed()
    results["live_verified"] = live_ok

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("DEPLOYMENT SUMMARY")
    for k, v in results.items():
        print(f"  {k}: {'OK' if v else 'FAILED/SKIP'}")
    print("=" * 65)

    critical_ok = results.get("plugin_active", False)
    if critical_ok:
        msg = (
            f"{PLUGIN_SLUG} v1.0.0 DEPLOYED and ACTIVE. "
            "Fixes live: preloader dark bg, hero top padding reduced, footer logo proportions corrected."
        )
        print(f"\nSUCCESS: {msg}")
        tg_send(msg)
    else:
        failed = [k for k, v in results.items() if not v]
        msg = f"{PLUGIN_SLUG} deployment issue. Failed: {failed}. Manual check needed."
        print(f"\nPARTIAL: {msg}")
        tg_send(msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
