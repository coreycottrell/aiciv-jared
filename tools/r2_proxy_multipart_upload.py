#!/usr/bin/env python3
"""
r2_proxy_multipart_upload.py
Upload a large file to R2 via the r2-upload-proxy Worker using multipart upload.
Bypasses the 100MB CF Worker body limit by chunking into ~90MB parts.

Usage:
  python3 tools/r2_proxy_multipart_upload.py <local_file> <r2_key>

Example:
  python3 tools/r2_proxy_multipart_upload.py \
    /path/to/full.mp4 \
    brainiac/recordings/module-9/full.mp4
"""
import sys
import os
import json
from pathlib import Path
from urllib.parse import quote
import urllib.request
import urllib.error

PROXY = "https://r2-upload-proxy.in0v8.workers.dev"
CHUNK_SIZE = 90 * 1024 * 1024  # 90MB per part (under CF 100MB worker body limit)


def http(method: str, url: str, data=None, headers=None, timeout=600):
    headers = headers or {}
    # CF managed challenge (1010) blocks default Python UA — set browser UA
    headers.setdefault(
        "User-Agent",
        "Mozilla/5.0 (X11; Linux x86_64) PureBrain-Aether-Pipeline/1.0",
    )
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def mpu_create(key: str) -> str:
    # Worker reads key from URL path, NOT query param
    url = f"{PROXY}/{quote(key, safe='/')}?action=mpu-create"
    status, body = http("POST", url)
    if status != 200:
        raise RuntimeError(f"mpu-create failed [{status}]: {body[:300]}")
    j = json.loads(body)
    return j["uploadId"]


def mpu_upload_part(key: str, upload_id: str, part_number: int, chunk: bytes) -> str:
    url = (
        f"{PROXY}/{quote(key, safe='/')}"
        f"?action=mpu-uploadpart"
        f"&uploadId={quote(upload_id, safe='')}"
        f"&partNumber={part_number}"
    )
    status, body = http(
        "PUT",
        url,
        data=chunk,
        headers={"Content-Type": "application/octet-stream"},
        timeout=900,
    )
    if status != 200:
        raise RuntimeError(f"upload-part {part_number} failed [{status}]: {body[:300]}")
    j = json.loads(body)
    # Worker returns {etag: ..., partNumber: ...}
    etag = j.get("etag") or j.get("ETag") or j.get("eTag")
    if not etag:
        raise RuntimeError(f"upload-part {part_number} no etag in response: {body[:300]}")
    return etag


def mpu_complete(key: str, upload_id: str, parts: list) -> dict:
    url = (
        f"{PROXY}/{quote(key, safe='/')}"
        f"?action=mpu-complete"
        f"&uploadId={quote(upload_id, safe='')}"
    )
    # Worker expects bare JSON array, NOT wrapped in {"parts": [...]}
    body_json = json.dumps(parts).encode()
    status, body = http(
        "POST",
        url,
        data=body_json,
        headers={"Content-Type": "application/json"},
        timeout=600,
    )
    if status != 200:
        raise RuntimeError(f"mpu-complete failed [{status}]: {body[:300]}")
    return json.loads(body)


def mpu_abort(key: str, upload_id: str):
    url = (
        f"{PROXY}/{quote(key, safe='/')}"
        f"?action=mpu-abort"
        f"&uploadId={quote(upload_id, safe='')}"
    )
    http("POST", url)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    local_path = Path(sys.argv[1])
    r2_key = sys.argv[2]

    if not local_path.exists():
        print(f"ERROR: file not found: {local_path}", file=sys.stderr)
        sys.exit(2)

    size = local_path.stat().st_size
    print(f"[upload] {local_path} ({size:,} bytes) -> r2://{r2_key}")

    # Create multipart upload
    print(f"[mpu-create] key={r2_key}")
    upload_id = mpu_create(r2_key)
    print(f"[mpu-create] uploadId={upload_id[:20]}...")

    parts = []
    part_number = 1
    uploaded = 0
    try:
        with open(local_path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                print(
                    f"[part {part_number}] uploading {len(chunk):,} bytes "
                    f"({uploaded + len(chunk):,}/{size:,} = "
                    f"{(uploaded + len(chunk)) * 100 // size}%)",
                    flush=True,
                )
                etag = mpu_upload_part(r2_key, upload_id, part_number, chunk)
                parts.append({"partNumber": part_number, "etag": etag})
                uploaded += len(chunk)
                part_number += 1

        print(f"[mpu-complete] finalizing {len(parts)} parts...")
        result = mpu_complete(r2_key, upload_id, parts)
        print(f"[done] {json.dumps(result)}")
        print(f"\nPublic URL: {PROXY}/{r2_key}")
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        print(f"[abort] aborting upload {upload_id[:20]}...", file=sys.stderr)
        try:
            mpu_abort(r2_key, upload_id)
        except Exception:
            pass
        sys.exit(3)


if __name__ == "__main__":
    main()
