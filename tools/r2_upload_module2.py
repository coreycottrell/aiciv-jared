#!/usr/bin/env python3
"""
Upload Module 2 HLS files to Cloudflare R2
Source: exports/brainiac-training/hls/2026-03-11/
Destination: purebrain-videos/brainiac/recordings/module-2/
"""

import os
import sys
import boto3
from botocore.config import Config
from pathlib import Path
import mimetypes

# Credentials from .env
ACCOUNT_ID = "19bb52a20bc7fc1b34036fea91f6860c"
ACCESS_KEY = "6c0d119663825c37e74c915df3a38864"
SECRET_KEY = "30c40c061fd2a920824fae3fbc05db69fc1d39199d5821fa9841e08223b73136"
BUCKET = "purebrain-video"
DEST_PREFIX = "brainiac/recordings/module-2"
SOURCE_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/brainiac-training/hls/2026-03-11")
R2_ENDPOINT = f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com"

def get_content_type(filename):
    if filename.endswith(".m3u8"):
        return "application/vnd.apple.mpegurl"
    elif filename.endswith(".ts"):
        return "video/mp2t"
    return "application/octet-stream"

def main():
    # Create S3 client pointed at R2
    s3 = boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )

    # Collect all files to upload
    files = sorted(SOURCE_DIR.iterdir())
    total = len(files)
    print(f"Found {total} files to upload")

    uploaded = 0
    failed = []

    for i, filepath in enumerate(files, 1):
        if not filepath.is_file():
            continue

        filename = filepath.name
        s3_key = f"{DEST_PREFIX}/{filename}"
        content_type = get_content_type(filename)

        try:
            s3.upload_file(
                str(filepath),
                BUCKET,
                s3_key,
                ExtraArgs={"ContentType": content_type},
            )
            uploaded += 1
            # Progress every 10 files
            if i % 10 == 0 or i == total:
                pct = int((i / total) * 100)
                print(f"  [{pct}%] {i}/{total} uploaded — last: {filename}")
        except Exception as e:
            print(f"  ERROR uploading {filename}: {e}")
            failed.append(filename)

    print(f"\nUpload complete: {uploaded}/{total} succeeded, {len(failed)} failed")
    if failed:
        print("Failed files:")
        for f in failed:
            print(f"  - {f}")
    return len(failed) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
