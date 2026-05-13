#!/usr/bin/env python3
"""
Upload Brainiac MP4 recordings to R2 bucket.
Module 1: 332MB, Module 2: 604MB
"""
import boto3
import os
import sys
from pathlib import Path
from botocore.config import Config

# R2 credentials — loaded from .env (chmod 600), NEVER hardcoded.
# Moved out of source 2026-05-13 per Jared. Repo grep should never find these values again.
def _load_env(env_path=Path(__file__).parent.parent / ".env"):
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_env()

ACCOUNT_ID = os.environ["R2_BRAINIAC_ACCOUNT_ID"]
ACCESS_KEY = os.environ["R2_BRAINIAC_ACCESS_KEY"]
SECRET_KEY = os.environ["R2_BRAINIAC_SECRET_KEY"]
BUCKET = os.environ.get("R2_BRAINIAC_BUCKET", "purebrain-video")
ENDPOINT = f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com"

# File paths
MODULE = sys.argv[1] if len(sys.argv) > 1 else "both"

FILES = {
    "module-1": {
        "src": "/home/jared/projects/AI-CIV/aether/exports/brainiac-training/downloads/module-1-2026-03-04.mp4",
        "dst": "brainiac/recordings/module-1/full.mp4",
    },
    "module-2": {
        "src": "/home/jared/projects/AI-CIV/aether/exports/brainiac-training/downloads/2026-03-11/2026-03-11_2103-Brainiac_-_Mastermind_Training_-_PureBrain.ai_-_Jared_0e010dfe.mp4",
        "dst": "brainiac/recordings/module-2/full.mp4",
    },
}

def upload(key, info):
    src = info["src"]
    dst = info["dst"]
    size_mb = os.path.getsize(src) / 1024 / 1024
    print(f"[{key}] Uploading {src}")
    print(f"[{key}] Size: {size_mb:.1f} MB -> s3://{BUCKET}/{dst}")

    s3 = boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "standard"},
        ),
        region_name="auto",
    )

    # Use multipart upload for large files (threshold 100MB)
    from boto3.s3.transfer import TransferConfig
    transfer_config = TransferConfig(
        multipart_threshold=100 * 1024 * 1024,   # 100MB
        multipart_chunksize=50 * 1024 * 1024,    # 50MB chunks
        max_concurrency=4,
        use_threads=True,
    )

    class ProgressCallback:
        def __init__(self, total):
            self.total = total
            self.uploaded = 0
            self.last_pct = 0

        def __call__(self, bytes_transferred):
            self.uploaded += bytes_transferred
            pct = int(self.uploaded / self.total * 100)
            if pct >= self.last_pct + 10:
                self.last_pct = pct
                print(f"[{key}] Progress: {pct}% ({self.uploaded / 1024 / 1024:.1f} MB)", flush=True)

    total = os.path.getsize(src)
    callback = ProgressCallback(total)

    s3.upload_file(
        src,
        BUCKET,
        dst,
        ExtraArgs={"ContentType": "video/mp4"},
        Config=transfer_config,
        Callback=callback,
    )
    print(f"[{key}] Upload complete.")

if MODULE == "module-1":
    upload("module-1", FILES["module-1"])
elif MODULE == "module-2":
    upload("module-2", FILES["module-2"])
else:
    for key, info in FILES.items():
        upload(key, info)
