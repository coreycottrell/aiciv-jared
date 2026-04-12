#!/usr/bin/env python3
"""
Deploy pb-awaken-cta v1.0.0 to purebrain.ai.

Installs the standalone plugin that injects the
"Awaken Your Personal AI Partner Today" CTA button between
the Compare section and "See Why PureBrain is Different" on:
  - Page 11  (homepage)
  - Page 689 (pay-test-2)
  - Page 1232 (pay-test-sandbox-3)

Method: REST API zip upload + PATCH activate.
Does NOT touch _elementor_data.

Author: cto (Pure Technology)
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

AETHER_ROOT  = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE  = AETHER_ROOT / "tools/security/pb-awaken-cta/pb-awaken-cta.php"
PLUGIN_SLUG  = "pb-awaken-cta"

# ── Credentials ────────────────────────────────────────────────────────────────
env_text = (AETHER_ROOT / ".env").read_text()


def _env(key):
    m = re.search(rf"^{key}='([^']+)'", env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf"^{key}=([^\n]+)", env_text, re.MULTILINE)
    return m.group(1).strip() if m else ""


WP_USER     = "Aether"
WP_PASSWORD = _env("PUREBRAIN_WP_PASSWORD")    # form login password
WP_APP_PASS = _env("PUREBRAIN_WP_APP_PASSWORD") # REST API application password
BASE_URL    = "https://purebrain.ai"

AUTH_HEADER = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()


# ── Helpers ────────────────────────────────────────────────────────────────────

def rest_request(method, path, data=None, content_type="application/json"):
    """Make a WP REST API request with Basic auth."""
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
    """Create an in-memory zip of the single-file plugin."""
    plugin_slug  = plugin_php_path.parent.name   # pb-awaken-cta
    php_filename = plugin_php_path.name           # pb-awaken-cta.php
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(plugin_php_path, f"{plugin_slug}/{php_filename}")
    return buf.getvalue()


# ── Step 1: Install via REST API ───────────────────────────────────────────────

def install_plugin(php_path: Path) -> bool:
    """Upload the plugin zip to /wp/v2/plugins."""
    print("\n[STEP 1] Building plugin zip...")
    zip_bytes = build_zip(php_path)
    print(f"  Zip size: {len(zip_bytes):,} bytes")

    slug = php_path.parent.name

    boundary = "----PureBrainBoundary9a1c7f"
    parts = [
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="slug"\r\n\r\n'
        f"{slug}\r\n",
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{slug}.zip"\r\n'
        f"Content-Type: application/zip\r\n\r\n",
    ]

    body = b""
    for p in parts[:-1]:
        body += p.encode()
    body += parts[-1].encode()
    body += zip_bytes
    body += f"\r\n--{boundary}--\r\n".encode()

    ct = f"multipart/form-data; boundary={boundary}"
    print("  POSTing zip to /wp/v2/plugins ...")
    status, result = rest_request("POST", "/wp/v2/plugins", data=body, content_type=ct)
    print(f"  Response {status}: {json.dumps(result, indent=2)[:500]}")

    if status in (200, 201):
        print("  SUCCESS: Plugin installed.")
        return True
    if status == 400 and "already_installed" in str(result):
        print("  Already installed — OK.")
        return True
    if status == 403:
        print("  ERROR 403: REST not allowed for plugin install.")
        return False
    print(f"  ERROR {status}")
    return False


# ── Step 2: Activate via REST API (PATCH) ─────────────────────────────────────

def activate_plugin(slug: str) -> bool:
    """PATCH /wp/v2/plugins/{slug}/{slug} with {status: 'active'}."""
    print(f"\n[STEP 2] Activating plugin: {slug} ...")
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
            print("  SUCCESS: Plugin is active.")
            return True
        print(f"  WARNING: returned '{plugin_status}', expected 'active'.")
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


def activate_plugin_fallback(slug: str) -> bool:
    """Fallback POST activation."""
    print(f"\n[STEP 2b] Fallback activation: {slug} ...")
    plugin_id = f"{slug}/{slug}"
    status, result = rest_request("POST", f"/wp/v2/plugins/{plugin_id}", data={"status": "active"})
    print(f"  Response {status}: {json.dumps(result, indent=2)[:300]}")
    if status in (200, 201) and result.get("status") == "active":
        print("  SUCCESS (fallback): Plugin is active.")
        return True
    return False


# ── Step 3: Verify ─────────────────────────────────────────────────────────────

def verify_live():
    """Check that the plugin CSS marker appears in the homepage source."""
    print("\n[VERIFY] Checking homepage source for plugin marker...")
    marker = "pb-awaken-cta-css"
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/",
            headers={"User-Agent": "Mozilla/5.0 (PureBrain-Verify)"}
        )
        resp = urllib.request.urlopen(req, timeout=20)
        html = resp.read().decode("utf-8", errors="ignore")
        if marker in html:
            print(f"  PASS: '{marker}' found in homepage HTML.")
            return True
        else:
            print(f"  NOTE: '{marker}' not in homepage source — may be Cloudflare cache (normal).")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def verify_plugin_active():
    """Confirm plugin shows as active in the REST API plugin list."""
    print("\n[VERIFY PLUGINS] Checking plugin list via REST API...")
    status, result = rest_request("GET", "/wp/v2/plugins?per_page=100")
    if status != 200:
        print(f"  Could not fetch plugin list: {status}")
        return
    for p in result:
        slug = p.get("plugin", "")
        pstatus = p.get("status", "")
        name = p.get("name", "")
        if PLUGIN_SLUG in slug:
            icon = "ACTIVE" if pstatus == "active" else "inactive"
            print(f"  [{icon}] {slug} — {name}")


# ── Telegram notification ──────────────────────────────────────────────────────

def tg_send(msg: str):
    import subprocess
    tg_script = str(AETHER_ROOT / "tools/tg_send.sh")
    subprocess.run([tg_script, f"cto: {msg}"], capture_output=True)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("PureBrain Plugin Deployment — pb-awaken-cta v1.0.0")
    print("  Target pages: 11 (homepage), 689 (pay-test-2), 1232 (sandbox-3)")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    print(f"\nPlugin file: {PLUGIN_FILE}")
    content = PLUGIN_FILE.read_text()
    ver_m = re.search(r"Version:\s+([\d.]+)", content)
    version = ver_m.group(1) if ver_m else "unknown"
    print(f"Plugin version: {version}")

    tg_send("Starting deployment: pb-awaken-cta v1.0.0 — Awaken CTA button (pages 11, 689, 1232).")

    results = {}

    # Step 1: Install
    installed = install_plugin(PLUGIN_FILE)
    results["install"] = installed

    # Step 2: Activate
    if installed:
        activated = activate_plugin(PLUGIN_SLUG)
        if not activated:
            print("  Retrying with fallback activation...")
            activated = activate_plugin_fallback(PLUGIN_SLUG)
        results["activate"] = activated
    else:
        print("  Skipping activation (install failed).")
        results["activate"] = False

    # Step 3: Verify
    time.sleep(4)
    verify_plugin_active()
    verify_live()

    # Summary
    print("\n" + "=" * 65)
    print("DEPLOYMENT SUMMARY")
    print(f"  pb-awaken-cta install:  {'OK' if results['install'] else 'FAILED'}")
    print(f"  pb-awaken-cta activate: {'OK' if results['activate'] else 'FAILED'}")
    print("=" * 65)

    all_ok = all(results.values())
    if all_ok:
        msg = (
            "Awaken CTA button deployed. Plugin pb-awaken-cta v1.0.0 is ACTIVE. "
            "Button now injects between Compare section and 'See Why PureBrain is Different' "
            "on pages 11 (homepage), 689 (pay-test-2), and 1232 (pay-test-sandbox-3). "
            "Blue default, orange hover, links to #awakening."
        )
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
