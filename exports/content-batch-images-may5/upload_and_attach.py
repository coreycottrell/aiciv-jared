#!/usr/bin/env python3
"""
Upload generated images to R2 and attach to social.purebrain.ai content items.

Pipeline: Login -> Upload PNG to R2 -> PATCH media_refs on content item
Auth: social-api login (email/password)
Uses: social.purebrain.ai /api/uploads + /api/content/{id} PATCH

Author: 3d-design-specialist
Date: 2026-05-02
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

SOCIAL_API = "https://social-api.in0v8.workers.dev"
EMAIL = "jared@puretechnology.nyc"
PASSWORD = os.environ.get("SOCIAL_API_PASSWORD", "PureBrain2026!")
UA = "curl/7.81.0"

FINAL_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/content-batch-images-may5/final")

# Mapping: image key -> content item ID (best match from search)
IMAGE_TO_CONTENT = {
    "01-hardest-part-final.png": "7da025e7-9d2e-4b40-b026-90b7b18e1a4f",
    "02-tired-of-demos-final.png": "a37aed7c-4008-447b-9e43-c4e28b891c28",
    "03-ai-got-wrong-final.png": "1fd51746-b970-475f-892a-71fb5dbb49b4",
    "04-shipped-4-features-final.png": "33f3dd48-5954-4702-85e2-458078c266a9",
    "05-32-specialist-agents-final.png": "18478c21-b493-4264-848e-8152848a4487",
    "06-40-percent-die-final.png": "ca009537-c7bd-4079-8576-ff41c8fe2027",
    "07-delegation-test-final.png": "6153b626-0252-4a82-a71b-cde1261043b1",
    "08-sunday-math-final.png": "ae8080e1-f2d0-4f59-b3aa-3871ec589b2e",
    "09-see-the-work-final.png": "0d8af6be-f8d7-499d-8113-7eec33830148",
    "10-stop-guessing-cost-final.png": "542384c5-dc14-4137-b965-075d7e2c5761",
}


def login():
    """Login to social API, return bearer token."""
    data = json.dumps({"email": EMAIL, "password": PASSWORD}).encode()
    req = urllib.request.Request(
        f"{SOCIAL_API}/api/login",
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": UA},
    )
    resp = urllib.request.urlopen(req, timeout=15)
    body = json.loads(resp.read())
    return body["token"]


def upload_image(file_path: Path, token: str) -> str:
    """Upload image file to R2 via /api/uploads. Returns the R2 proxy URL."""
    boundary = "----PythonFormBoundary7MA4YWxkTrZu0gW"
    filename = file_path.name
    file_data = file_path.read_bytes()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: image/png\r\n"
        f"\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{SOCIAL_API}/api/uploads",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": UA,
        },
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=60)
    result = json.loads(resp.read())

    # Response may have url or key
    url = result.get("url") or result.get("public_url")
    key = result.get("key")

    if url:
        # If it returns an r2.dev URL, convert to proxy URL
        if "r2.dev" in url:
            # Extract key from URL
            parts = url.split("/")
            r2_key = "/".join(parts[3:])  # after domain
            url = f"https://social.purebrain.ai/media/{r2_key}"
        return url
    elif key:
        return f"https://social.purebrain.ai/media/{key}"
    else:
        raise ValueError(f"No URL or key in upload response: {result}")


def patch_media_refs(content_id: str, image_url: str, token: str) -> dict:
    """PATCH content item with media_refs array."""
    data = json.dumps({"media_refs": [image_url]}).encode()
    req = urllib.request.Request(
        f"{SOCIAL_API}/api/content/{content_id}",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": UA,
        },
        method="PATCH",
    )
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())


def main():
    print("=" * 60)
    print("Upload & Attach: 10 LinkedIn Images to social.purebrain.ai")
    print("=" * 60)

    # Login
    print("\n[1/3] Logging in...")
    token = login()
    print(f"  Token: {token[:20]}...")

    # Upload and attach each image
    print(f"\n[2/3] Uploading and attaching {len(IMAGE_TO_CONTENT)} images...")
    results = []

    for filename, content_id in IMAGE_TO_CONTENT.items():
        file_path = FINAL_DIR / filename
        print(f"\n  --- {filename} -> {content_id[:12]}... ---")

        if not file_path.exists():
            print(f"  [SKIP] File not found: {file_path}")
            results.append({"file": filename, "status": "missing"})
            continue

        try:
            # Upload to R2
            print(f"  Uploading ({file_path.stat().st_size // 1024} KB)...")
            image_url = upload_image(file_path, token)
            print(f"  R2 URL: {image_url}")

            # PATCH content item
            print(f"  PATCHing content {content_id[:12]}...")
            patch_result = patch_media_refs(content_id, image_url, token)
            print(f"  PATCH OK")

            results.append({
                "file": filename,
                "content_id": content_id,
                "image_url": image_url,
                "status": "ok",
            })

        except Exception as e:
            print(f"  [ERR] {e}")
            results.append({"file": filename, "status": f"error: {e}"})

        # Small delay between uploads
        time.sleep(2)

    # Summary
    print("\n" + "=" * 60)
    print("[3/3] SUMMARY")
    print("=" * 60)
    ok_count = sum(1 for r in results if r["status"] == "ok")
    print(f"  Attached: {ok_count} / {len(IMAGE_TO_CONTENT)}")
    for r in results:
        mark = "OK" if r["status"] == "ok" else "FAIL"
        print(f"  [{mark}] {r['file']}: {r['status']}")
        if r.get("image_url"):
            print(f"         URL: {r['image_url']}")

    # Save results
    results_path = FINAL_DIR.parent / "upload-results.json"
    results_path.write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nResults saved: {results_path}")


if __name__ == "__main__":
    main()
