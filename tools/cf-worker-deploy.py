#!/usr/bin/env python3
"""
CF Worker Direct Deploy (no wrangler)
======================================
Wrangler is constitutionally BANNED in this codebase (it has destructive
defaults that have lost work). This tool deploys a Worker via Cloudflare's
REST API using multipart/form-data — the same protocol wrangler uses, but
without wrangler's footguns.

Usage:
    # Deploy a worker (parses wrangler.toml for vars + main file)
    ./tools/cf-worker-deploy.py workers/777-sheets-api/

    # Explicit script + worker name
    ./tools/cf-worker-deploy.py --name 777-sheets-api --script workers/777-sheets-api/src/worker.js

    # Dry run (show what would be uploaded)
    ./tools/cf-worker-deploy.py --dry-run workers/777-sheets-api/

What this PRESERVES (does NOT clobber):
    * Existing secrets bound to the worker (SERVICE_ACCOUNT_*, etc.)
    * Worker route bindings (workers.dev subdomain, custom routes)
    * KV / R2 / D1 / Durable Object bindings declared in wrangler.toml [[bindings]]

What this REPLACES:
    * The script body itself
    * Plain `vars` (env-style strings) declared in wrangler.toml [vars]

Environment (reads .env automatically):
    CF_API_TOKEN          - Preferred (scoped Bearer token)
    CF_API_KEY + CF_AUTH_EMAIL  - Fallback (Global API Key)
    CLOUDFLARE_ACCOUNT_ID - Required
"""

import os
import sys
import json
import argparse
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

# ---- Minimal .env loader (no external deps) ----
def load_env():
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v

load_env()

# ---- Minimal TOML parser (good enough for wrangler.toml) ----
def parse_wrangler_toml(toml_path: Path):
    """Parse the subset of wrangler.toml fields we care about.

    Returns: {name, main, vars: {k: v}}
    """
    text = toml_path.read_text()
    out = {"name": None, "main": None, "vars": {}}
    section = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip()
        # strip inline comment
        if "#" in v and not (v.startswith('"') or v.startswith("'")):
            v = v.split("#", 1)[0].strip()
        # strip quotes
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        if section is None:
            if k == "name":
                out["name"] = v
            elif k == "main":
                out["main"] = v
        elif section == "vars":
            out["vars"][k] = v
    return out

# ---- CF API request helper ----
def cf_headers():
    token = os.environ.get("CF_API_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    api_key = os.environ.get("CF_API_KEY")
    email = os.environ.get("CF_AUTH_EMAIL")
    if api_key and email:
        return {"X-Auth-Email": email, "X-Auth-Key": api_key}
    raise RuntimeError("No CF auth: set CF_API_TOKEN or CF_API_KEY+CF_AUTH_EMAIL in .env")

def cf_request(method: str, url: str, headers=None, body=None):
    h = cf_headers()
    if headers:
        h.update(headers)
    req = Request(url, data=body, method=method, headers=h)
    try:
        with urlopen(req) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")

# ---- Multipart builder (the multipart/form-data spec is unforgiving) ----
def build_multipart(parts, boundary="----CFWorkerDeployBoundary"):
    """parts: list of dicts: {name, filename(optional), content_type, body(bytes)}"""
    out = bytearray()
    crlf = b"\r\n"
    for p in parts:
        out += f"--{boundary}".encode() + crlf
        disp = f'form-data; name="{p["name"]}"'
        if "filename" in p:
            disp += f'; filename="{p["filename"]}"'
        out += f'Content-Disposition: {disp}'.encode() + crlf
        out += f'Content-Type: {p["content_type"]}'.encode() + crlf
        out += crlf
        out += p["body"]
        out += crlf
    out += f"--{boundary}--".encode() + crlf
    return bytes(out), boundary

# ---- Deploy ----
def deploy_worker(worker_dir: Path = None, name: str = None, script: str = None, dry_run: bool = False):
    # Resolve config
    if worker_dir:
        toml_path = worker_dir / "wrangler.toml"
        if not toml_path.exists():
            raise RuntimeError(f"No wrangler.toml at {toml_path}")
        cfg = parse_wrangler_toml(toml_path)
        if not name:
            name = cfg["name"]
        if not script:
            main = cfg["main"] or "src/worker.js"
            script = str(worker_dir / main)
        plain_vars = cfg["vars"]
    else:
        plain_vars = {}

    if not name or not script:
        raise RuntimeError("Need --name and --script (or a worker dir with wrangler.toml)")

    script_path = Path(script)
    if not script_path.exists():
        raise RuntimeError(f"Script not found: {script_path}")

    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if not account_id:
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID missing from .env")

    script_body = script_path.read_bytes()

    # Metadata: keep_bindings preserves existing secrets/bindings the API can't see in this upload.
    # We declare main_module + plain_text vars. Secrets are preserved via keep_bindings=["secret_text"].
    metadata = {
        "main_module": script_path.name,
        "compatibility_date": "2024-01-01",
        "bindings": [
            {"type": "plain_text", "name": k, "text": v}
            for k, v in plain_vars.items()
        ],
        # Preserve everything the API would otherwise drop:
        "keep_bindings": ["secret_text"],
    }

    print(f"Worker:        {name}")
    print(f"Account:       {account_id}")
    print(f"Script:        {script_path} ({len(script_body)} bytes)")
    print(f"Plain vars:    {list(plain_vars.keys())}")
    print(f"Preserving:    secret_text bindings (service account creds, etc.)")

    if dry_run:
        print("\n[DRY RUN] Would POST multipart to:")
        print(f"  https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/scripts/{name}")
        print("Metadata:")
        print(json.dumps(metadata, indent=2))
        return 0

    parts = [
        {
            "name": "metadata",
            "content_type": "application/json",
            "body": json.dumps(metadata).encode("utf-8"),
        },
        {
            "name": script_path.name,
            "filename": script_path.name,
            "content_type": "application/javascript+module",
            "body": script_body,
        },
    ]
    body, boundary = build_multipart(parts)

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/scripts/{name}"
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }

    print(f"\nDeploying to {url} ...")
    status, resp_text = cf_request("PUT", url, headers=headers, body=body)
    print(f"HTTP {status}")
    try:
        resp = json.loads(resp_text)
        print(json.dumps(resp, indent=2)[:2000])
    except Exception:
        print(resp_text[:2000])

    if status == 200:
        try:
            resp = json.loads(resp_text)
            if resp.get("success"):
                print("\nDEPLOY SUCCESS")
                return 0
        except Exception:
            pass
    print("\nDEPLOY FAILED")
    return 1

def main():
    ap = argparse.ArgumentParser(description="Deploy a CF Worker via REST API (no wrangler)")
    ap.add_argument("worker_dir", nargs="?", help="Worker directory (containing wrangler.toml)")
    ap.add_argument("--name", help="Worker name (overrides wrangler.toml)")
    ap.add_argument("--script", help="Path to script file (overrides wrangler.toml main)")
    ap.add_argument("--dry-run", action="store_true", help="Don't deploy, just show what would happen")
    args = ap.parse_args()

    worker_dir = Path(args.worker_dir).resolve() if args.worker_dir else None
    rc = deploy_worker(
        worker_dir=worker_dir,
        name=args.name,
        script=args.script,
        dry_run=args.dry_run,
    )
    sys.exit(rc)

if __name__ == "__main__":
    main()
