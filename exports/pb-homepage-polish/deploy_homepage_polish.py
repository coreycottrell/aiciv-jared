#!/usr/bin/env python3
"""
Deploy pb-homepage-polish plugin to purebrain.ai via WP REST API.
Creates the plugin via file upload endpoint or activates it if already present.
"""
import os
import sys
import json
import base64
import urllib.request
import urllib.error
import zipfile
import tempfile

WP_URL = "https://purebrain.ai"
WP_USER = "purebrain@puremarketing.ai"
WP_APP_PASS = "41w3 xWWZ 11em UXgj hjAF sx2T"

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_FILE = os.path.join(PLUGIN_DIR, "pb-homepage-polish.php")
PLUGIN_SLUG = "pb-homepage-polish/pb-homepage-polish.php"

# Build Basic Auth header
credentials = f"{WP_USER}:{WP_APP_PASS}"
b64_creds = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
AUTH_HEADER = f"Basic {b64_creds}"


def wp_request(method, endpoint, data=None, headers=None):
    url = f"{WP_URL}/wp-json{endpoint}"
    req_headers = {
        "Authorization": AUTH_HEADER,
        "Content-Type": "application/json",
    }
    if headers:
        req_headers.update(headers)
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return e.code, body


def create_zip():
    """Create a zip of the plugin directory for upload."""
    tmpdir = tempfile.mkdtemp()
    zip_path = os.path.join(tmpdir, "pb-homepage-polish.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(PLUGIN_FILE, arcname="pb-homepage-polish/pb-homepage-polish.php")
    return zip_path


def upload_plugin(zip_path):
    """Upload plugin zip via WP REST API."""
    with open(zip_path, "rb") as f:
        zip_data = f.read()

    boundary = "----PBUploadBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="pb-homepage-polish.zip"\r\n'
        f"Content-Type: application/zip\r\n\r\n"
    ).encode("utf-8") + zip_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    url = f"{WP_URL}/wp-json/wp/v2/plugins"
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": AUTH_HEADER,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return e.code, body


def activate_plugin():
    """Activate plugin via WP REST API PATCH."""
    status, resp = wp_request(
        "PUT",
        f"/wp/v2/plugins/{PLUGIN_SLUG.replace('/', '%2F')}",
        data={"status": "active"},
    )
    return status, resp


def check_plugin_status():
    """Check if plugin exists and its status."""
    status, resp = wp_request("GET", f"/wp/v2/plugins/{PLUGIN_SLUG.replace('/', '%2F')}")
    return status, resp


def main():
    print("=" * 60)
    print("pb-homepage-polish deployment script")
    print("=" * 60)

    # Step 1: Check if plugin already exists
    print("\n[1] Checking if plugin already exists on server...")
    status, resp = check_plugin_status()
    print(f"    Status: {status}")

    if status == 200:
        plugin_data = resp if isinstance(resp, dict) else json.loads(resp)
        current_status = plugin_data.get("status", "unknown")
        print(f"    Plugin exists. Current status: {current_status}")
        if current_status == "active":
            print("    Plugin already active. Nothing to do.")
            return True
        else:
            print("    Plugin exists but not active. Activating...")
            act_status, act_resp = activate_plugin()
            print(f"    Activation response: {act_status}")
            if act_status == 200:
                print("    Plugin activated successfully.")
                return True
            else:
                print(f"    Activation failed: {act_resp}")
                return False
    else:
        print(f"    Plugin not found (status {status}). Uploading...")

    # Step 2: Create zip and upload
    print("\n[2] Creating plugin zip...")
    zip_path = create_zip()
    print(f"    Zip created: {zip_path}")

    print("\n[3] Uploading plugin zip to WordPress...")
    upload_status, upload_resp = upload_plugin(zip_path)
    print(f"    Upload status: {upload_status}")

    if upload_status in (200, 201):
        print("    Upload successful.")
        # Check if it got auto-activated
        if isinstance(upload_resp, dict):
            new_status = upload_resp.get("status", "unknown")
            print(f"    Plugin status after upload: {new_status}")
            if new_status == "active":
                print("    Plugin is active. Done.")
                return True
    else:
        print(f"    Upload failed: {upload_resp}")
        # Try alternative: maybe plugin exists with different slug
        print("    Trying to activate by slug anyway...")

    # Step 3: Activate
    print("\n[4] Activating plugin...")
    act_status, act_resp = activate_plugin()
    print(f"    Activation status: {act_status}")

    if act_status == 200:
        print("    Plugin activated successfully.")
        return True
    else:
        print(f"    Could not activate: {act_resp}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
