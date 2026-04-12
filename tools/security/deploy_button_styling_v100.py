#!/usr/bin/env python3
"""
Deploy pb-button-styling v1.0.0 and updated purebrain-security plugin.

Tasks:
  1. Upload pb-button-styling as a new plugin via WP REST API (zip upload)
  2. Activate pb-button-styling via REST API
  3. Update purebrain-security plugin via cookie HTTP + plugin editor

Author: full-stack-developer
Date: 2026-03-07
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
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
SECURITY_PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security-plugin.php"
BUTTON_PLUGIN_FILE   = AETHER_ROOT / "tools/security/pb-button-styling/pb-button-styling.php"

# ── Credentials ────────────────────────────────────────────────────────────────
env_text = (AETHER_ROOT / ".env").read_text()


def _env(key):
    m = re.search(rf"^{key}='([^']+)'", env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf"^{key}=([^\n]+)", env_text, re.MULTILINE)
    return m.group(1).strip() if m else ""


WP_USER     = "Aether"
WP_PASSWORD = _env("PUREBRAIN_WP_PASSWORD")
WP_APP_PASS = _env("PUREBRAIN_WP_APP_PASSWORD")
BASE_URL    = "https://purebrain.ai"

AUTH_HEADER = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()

EDITOR_URL = (
    f"{BASE_URL}/wp-admin/plugin-editor.php"
    "?file=purebrain-security/purebrain-security-plugin.php"
    "&plugin=purebrain-security/purebrain-security-plugin.php"
)

# ── Helpers ────────────────────────────────────────────────────────────────────

def rest_request(method, path, data=None, content_type="application/json"):
    """Make a REST API request with Basic auth."""
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
        # raw bytes (multipart etc)
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
    """Create an in-memory zip of the plugin directory (single-file plugin)."""
    plugin_slug = plugin_php_path.parent.name          # pb-button-styling
    php_filename = plugin_php_path.name                 # pb-button-styling.php
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        arcname = f"{plugin_slug}/{php_filename}"
        zf.write(plugin_php_path, arcname)
    return zip_buffer.getvalue()


# ── Step 1: Install pb-button-styling via REST API zip upload ──────────────────

def install_plugin_via_rest(php_path: Path) -> bool:
    """
    Upload a zip of the plugin to the WP REST API plugins endpoint.
    POST /wp/v2/plugins with multipart body containing the zip.
    """
    print("\n[STEP 1] Building plugin zip...")
    zip_bytes = build_zip(php_path)
    print(f"  Zip size: {len(zip_bytes):,} bytes")

    slug = php_path.parent.name  # pb-button-styling

    # Build multipart form manually
    boundary = "----PureBrainBoundary7e3f9a"
    parts = []

    # Field: slug (not always required but helps)
    parts.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="slug"\r\n\r\n'
        f"{slug}\r\n"
    )

    # Field: zip file
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

    print(f"  POSTing zip to /wp/v2/plugins ...")
    status, result = rest_request("POST", "/wp/v2/plugins", data=body, content_type=content_type)
    print(f"  Response status: {status}")
    print(f"  Response: {json.dumps(result, indent=2)[:600]}")

    if status in (200, 201):
        print(f"  SUCCESS: Plugin installed.")
        return True
    elif status == 400 and "already_installed" in str(result):
        print(f"  Plugin already installed (ok).")
        return True
    elif status == 403:
        print(f"  ERROR 403: Insufficient permissions or REST not allowed for plugin install.")
        return False
    else:
        print(f"  ERROR {status}: {result}")
        return False


# ── Step 2: Activate pb-button-styling via REST API ───────────────────────────

def activate_plugin(slug: str) -> bool:
    """
    PATCH /wp/v2/plugins/{slug} with {status: "active"}
    """
    print(f"\n[STEP 2] Activating plugin: {slug} ...")
    plugin_id = f"{slug}/{slug}"
    status, result = rest_request("POST", f"/wp/v2/plugins/{plugin_id}", data={"status": "active"})
    if status == 405:
        # Try PATCH via POST override (some WP setups need this)
        status, result = rest_request("POST", f"/wp/v2/plugins/{plugin_id}", data={"status": "active"})

    print(f"  Response status: {status}")
    if status in (200, 201):
        plugin_status = result.get("status", "")
        print(f"  Plugin status: {plugin_status}")
        if plugin_status == "active":
            print("  SUCCESS: Plugin is active.")
            return True
        else:
            print(f"  WARNING: Plugin response status is '{plugin_status}', not 'active'.")
            return False
    else:
        print(f"  Response: {json.dumps(result, indent=2)[:400]}")
        return False


def activate_plugin_patch(slug: str) -> bool:
    """PATCH variant using urllib with X-HTTP-Method-Override."""
    print(f"\n[STEP 2b] Activating plugin via PATCH: {slug} ...")
    plugin_id = f"{slug}/{slug}"
    url = f"{BASE_URL}/wp-json/wp/v2/plugins/{plugin_id}"
    body = json.dumps({"status": "active"}).encode()
    headers = {
        "Authorization": f"Basic {AUTH_HEADER}",
        "Content-Type": "application/json",
        "User-Agent": "PureBrain-Deploy/1.0",
        "X-HTTP-Method-Override": "PATCH",
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode())
        plugin_status = result.get("status", "")
        print(f"  Plugin status returned: {plugin_status}")
        if plugin_status == "active":
            print("  SUCCESS: Plugin activated.")
            return True
        return False
    except urllib.error.HTTPError as e:
        body_bytes = e.read()
        try:
            err = json.loads(body_bytes.decode())
        except Exception:
            err = body_bytes.decode()[:300]
        print(f"  HTTP Error {e.code}: {err}")
        return False
    except Exception as exc:
        print(f"  Error: {exc}")
        return False


# ── Step 3: Deploy updated security plugin via cookie HTTP ─────────────────────

def deploy_security_plugin_via_http(plugin_content: str) -> bool:
    """Login with session cookies, extract nonce, POST to plugin editor."""
    print("\n[STEP 3] Deploying updated security plugin via cookie HTTP...")

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (PureBrain-Deploy)")]

    # Login
    print("  Logging in...")
    login_data = urllib.parse.urlencode({
        "log": WP_USER,
        "pwd": WP_PASSWORD,
        "wp-submit": "Log In",
        "redirect_to": "/wp-admin/",
        "testcookie": "1",
    }).encode()
    login_url = f"{BASE_URL}/wp-login.php"

    try:
        resp = opener.open(login_url, login_data, timeout=30)
        final_url = resp.geturl()
        print(f"  Login redirect: {final_url}")
        if "wp-login.php" in final_url and "loggedout" not in final_url:
            print("  WARNING: May still be on login page.")
    except Exception as e:
        print(f"  Login error: {e}")
        return False

    time.sleep(2)

    # Fetch plugin editor page for nonce
    print("  Fetching plugin editor for nonce...")
    try:
        resp = opener.open(EDITOR_URL, timeout=30)
        html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  Editor page error: {e}")
        return False

    nonce = None
    patterns = [
        r'"nonce":"([a-f0-9]+)"',
        r'name="_wpnonce"[^>]+value="([^"]+)"',
        r'"_wpnonce":"([^"]+)"',
        r'_wpnonce\s*=\s*"([^"]+)"',
        r"_wpnonce['\"]?\s*:\s*['\"]([^'\"]{6,})['\"]",
    ]
    for pat in patterns:
        m = re.search(pat, html)
        if m:
            nonce = m.group(1)
            print(f"  Nonce found: {nonce[:10]}...")
            break

    if not nonce:
        print("  ERROR: Could not extract nonce.")
        debug_path = AETHER_ROOT / "exports/screenshots/plugin_editor_debug.html"
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        debug_path.write_text(html[:20000])
        print(f"  Debug page saved: {debug_path}")
        return False

    # POST content
    print(f"  Posting security plugin content ({len(plugin_content):,} chars)...")
    post_data = urllib.parse.urlencode({
        "_wpnonce": nonce,
        "newcontent": plugin_content,
        "action": "update",
        "file": "purebrain-security/purebrain-security-plugin.php",
        "plugin": "purebrain-security/purebrain-security-plugin.php",
        "scrollto": "0",
        "submit": "Update File",
    }).encode()

    req = urllib.request.Request(
        EDITOR_URL,
        data=post_data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": EDITOR_URL,
        }
    )
    try:
        resp = opener.open(req, timeout=60)
        result_html = resp.read().decode("utf-8", errors="ignore")
        final_url = resp.geturl()
        print(f"  POST response URL: {final_url}")
    except Exception as e:
        print(f"  POST error: {e}")
        return False

    if "File edited successfully" in result_html:
        print("  SUCCESS: 'File edited successfully'")
        return True
    elif "updated successfully" in result_html.lower():
        print("  SUCCESS: 'updated successfully'")
        return True
    elif "updated=true" in final_url:
        print("  SUCCESS: inferred from redirect URL")
        return True
    elif "Parse error" in result_html or "syntax error" in result_html.lower():
        err_m = re.search(r"(?:Parse error|syntax error)[^<]{0,200}", result_html)
        print(f"  ERROR: PHP syntax error: {err_m.group(0) if err_m else 'unknown'}")
        return False
    else:
        debug_path = AETHER_ROOT / "exports/screenshots/security_plugin_save_debug.html"
        debug_path.write_text(result_html[:30000])
        print(f"  Unknown result. Debug saved: {debug_path}")
        snippet = result_html[2000:2500]
        print(f"  Snippet: {snippet}")
        return False


# ── Step 4: Verify live ────────────────────────────────────────────────────────

def verify_live():
    """Check button hover CSS is present in live HTML source."""
    print("\n[VERIFY] Checking live site for button hover CSS...")
    marker = "pb-button-hover-v622"
    test_url = "https://purebrain.ai/"
    try:
        req = urllib.request.Request(
            test_url,
            headers={"User-Agent": "Mozilla/5.0 (PureBrain-Verify)"}
        )
        resp = urllib.request.urlopen(req, timeout=20)
        html = resp.read().decode("utf-8", errors="ignore")
        if marker in html:
            print(f"  PASS: '{marker}' found in homepage HTML.")
            return True
        else:
            print(f"  NOTE: '{marker}' not visible in homepage source (may be Cloudflare cache).")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def verify_plugin_active():
    """Check plugin list via REST API."""
    print("\n[VERIFY PLUGINS] Checking installed plugins via REST API...")
    status, result = rest_request("GET", "/wp/v2/plugins?per_page=100")
    if status != 200:
        print(f"  Could not fetch plugins: {status}")
        return
    for p in result:
        slug = p.get("plugin", "")
        pstatus = p.get("status", "")
        name = p.get("name", "")
        if "pb-button" in slug or "purebrain-security" in slug:
            icon = "ACTIVE" if pstatus == "active" else "inactive"
            print(f"  [{icon}] {slug} -- {name}")


# ── Telegram notification ──────────────────────────────────────────────────────

def tg_send(msg):
    import subprocess
    tg_script = str(AETHER_ROOT / "tools/tg_send.sh")
    subprocess.run([tg_script, f"full-stack-developer: {msg}"], capture_output=True)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("PureBrain Plugin Deployment — pb-button-styling v1.0.0")
    print("  + purebrain-security (button CSS extracted)")
    print("=" * 65)

    # Validate files exist
    for f in [SECURITY_PLUGIN_FILE, BUTTON_PLUGIN_FILE]:
        if not f.exists():
            print(f"ERROR: File not found: {f}")
            sys.exit(1)

    security_content = SECURITY_PLUGIN_FILE.read_text()
    print(f"\nSecurity plugin: {len(security_content):,} chars")

    # Check security plugin version
    ver_m = re.search(r"Version:\s+([\d.]+)", security_content)
    version = ver_m.group(1) if ver_m else "unknown"
    print(f"Security plugin version: {version}")

    tg_send("Starting deployment: pb-button-styling v1.0.0 (new plugin) + security plugin update.")

    results = {}

    # ── 1. Install pb-button-styling ──────────────────────────────────────────
    installed = install_plugin_via_rest(BUTTON_PLUGIN_FILE)
    results["install"] = installed

    # ── 2. Activate pb-button-styling ─────────────────────────────────────────
    if installed:
        activated = activate_plugin_patch("pb-button-styling")
        if not activated:
            print("  Retrying activation via standard POST...")
            activated = activate_plugin("pb-button-styling")
        results["activate"] = activated
    else:
        print("  Skipping activation (install failed).")
        results["activate"] = False

    # ── 3. Deploy updated security plugin ─────────────────────────────────────
    security_deployed = deploy_security_plugin_via_http(security_content)
    results["security_deploy"] = security_deployed

    # ── 4. Verify ─────────────────────────────────────────────────────────────
    time.sleep(3)
    verify_plugin_active()
    verify_live()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("DEPLOYMENT SUMMARY")
    print(f"  pb-button-styling install:  {'OK' if results['install'] else 'FAILED'}")
    print(f"  pb-button-styling activate: {'OK' if results['activate'] else 'FAILED'}")
    print(f"  purebrain-security update:  {'OK' if results['security_deploy'] else 'FAILED'}")
    print("=" * 65)

    all_ok = all(results.values())
    if all_ok:
        msg = "Deployment complete. pb-button-styling v1.0.0 installed + activated. Security plugin updated (button CSS extracted)."
        print(f"\nSUCCESS: {msg}")
        tg_send(msg)
    else:
        failed = [k for k, v in results.items() if not v]
        msg = f"Deployment partial. Failed steps: {failed}. Check logs."
        print(f"\nPARTIAL: {msg}")
        tg_send(msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
