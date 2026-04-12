#!/usr/bin/env python3
"""
upload_r2.py — Upload HLS directory to Cloudflare R2
=====================================================
Uploads all files in a directory to R2 under a given key prefix.

Usage:
  python3 tools/video-pipeline/upload_r2.py --dir /path/to/hls --key brainiac/recordings/2026-04-08
  python3 tools/video-pipeline/upload_r2.py --dir /path/to/hls --key brainiac/recordings/2026-04-08 --bucket purebrain-video
"""

import argparse
import mimetypes
import os
import sys
from pathlib import Path

import boto3


def load_env(env_file: str = None) -> dict:
    """Load .env file."""
    if env_file is None:
        env_file = str(Path(__file__).parent.parent.parent / ".env")
    env = {}
    try:
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env


def get_content_type(filepath: str) -> str:
    """Determine content type for a file."""
    ext_map = {
        ".m3u8": "application/vnd.apple.mpegurl",
        ".ts": "video/mp2t",
        ".mp4": "video/mp4",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".json": "application/json",
        ".vtt": "text/vtt",
    }
    ext = Path(filepath).suffix.lower()
    return ext_map.get(ext, mimetypes.guess_type(filepath)[0] or "application/octet-stream")


def upload_directory(
    directory: str,
    key_prefix: str,
    bucket: str,
    access_key: str,
    secret_key: str,
    account_id: str,
) -> str:
    """Upload all files in directory to R2. Returns the public URL of master.m3u8."""
    endpoint = f"https://{account_id}.r2.cloudflarestorage.com"

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )

    dir_path = Path(directory)
    files = sorted(dir_path.iterdir())
    total = len(files)
    uploaded = 0

    for f in files:
        if not f.is_file():
            continue
        key = f"{key_prefix}/{f.name}"
        content_type = get_content_type(str(f))

        print(f"  [{uploaded + 1}/{total}] {f.name} -> s3://{bucket}/{key} ({content_type})")
        s3.upload_file(
            str(f),
            bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        uploaded += 1

    print(f"\nUploaded {uploaded} files to R2 bucket '{bucket}' under '{key_prefix}/'")

    # Construct public URL
    # Use known public URL pattern for purebrain-video bucket
    public_url = f"https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/{key_prefix}/master.m3u8"
    print(f"Public URL: {public_url}")
    return public_url


def main():
    parser = argparse.ArgumentParser(description="Upload HLS directory to Cloudflare R2")
    parser.add_argument("--dir", required=True, help="Directory containing HLS files")
    parser.add_argument("--key", required=True, help="R2 key prefix (e.g. brainiac/recordings/2026-04-08)")
    parser.add_argument("--bucket", default="purebrain-video", help="R2 bucket name")
    args = parser.parse_args()

    env = load_env()

    access_key = env.get("R2_ACCESS_KEY")
    secret_key = env.get("R2_SECRET_KEY")
    account_id = env.get("CF_ACCOUNT_ID")

    if not all([access_key, secret_key, account_id]):
        print("ERROR: Missing R2_ACCESS_KEY, R2_SECRET_KEY, or CF_ACCOUNT_ID in .env")
        sys.exit(1)

    url = upload_directory(
        directory=args.dir,
        key_prefix=args.key,
        bucket=args.bucket,
        access_key=access_key,
        secret_key=secret_key,
        account_id=account_id,
    )
    print(url)


if __name__ == "__main__":
    main()
