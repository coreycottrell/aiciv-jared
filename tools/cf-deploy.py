#!/usr/bin/env python3
"""
CF Pages Direct File Deploy
============================
Upload specific files to CF Pages without a full directory deploy.
Preserves all existing files from the current production deployment.

Usage:
    # Deploy specific files (paths relative to site root)
    ./tools/cf-deploy.py blog/new-post/index.html blog/new-post/banner.png

    # Deploy all files in a directory
    ./tools/cf-deploy.py investor-avatar/

    # Deploy from a local base directory (default: exports/cf-pages-deploy/)
    ./tools/cf-deploy.py --base-dir /tmp/mybuild/ index.html about/index.html

    # Dry run - show what would be uploaded without deploying
    ./tools/cf-deploy.py --dry-run blog/new-post/index.html

    # Deploy files that don't exist locally (provide content via stdin or --content)
    echo '<h1>Hello</h1>' | ./tools/cf-deploy.py --stdin test-page/index.html

    # Delete a file from the site (remove from manifest)
    ./tools/cf-deploy.py --delete old-page/index.html

Environment variables (reads from .env automatically):
    CF_API_KEY       - Cloudflare Global API Key
    CF_AUTH_EMAIL    - Cloudflare account email
    CF_PAGES_ACCOUNT - Account ID (default: d526a3e9498dd167509003004df03290)
    CF_PAGES_PROJECT - Project name (default: purebrain-staging)
"""

import os
import sys
import json
import base64
import hashlib
import mimetypes
import time
import argparse
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"

# CF Pages project lives under the In0v8 account
DEFAULT_ACCOUNT_ID = "d526a3e9498dd167509003004df03290"
DEFAULT_PROJECT_NAME = "purebrain-staging"
DEFAULT_BASE_DIR = PROJECT_ROOT / "exports" / "cf-pages-deploy"

# API limits
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB per upload request
MAX_BUCKET_FILES = 100
MAX_RETRIES = 3

# ---------------------------------------------------------------------------
# PROTECTED PATHS — CONSTITUTIONAL: These paths can NEVER be overwritten,
# deleted, or deployed to without explicit --force-protected flag.
# Added 2026-04-11 after investment-opportunity-backup-2 was erased by
# a full deployment that didn't include it in the local directory.
# Added 2026-05-08: user-guide/ after bulk deploy stripped it from manifest;
# stale CF cache masked the origin 404 for ~46 hours, real users hit 404s.
# ---------------------------------------------------------------------------
PROTECTED_PATHS = {
    "investment-opportunity/",
    "investment-opportunity-backup-2/",
    "investment-opportunity-backup/",
    "investment-opportunity-backup-3/",
    "user-guide/",
    # 2026-05-11: brainiac mastermind training (M1-M10 + hub) added after
    # M9/M10 restore. Frozen because (a) public training cohort relies on
    # stable URLs, (b) hub references via JS array, (c) prior accidental
    # erasure pattern (cf. user-guide 2026-05-08).
    "brainiac-mastermind-training/",
    "brainiac-mastermind-training/brainiac-module-1-foundations/",
    "brainiac-mastermind-training/brainiac-module-2-ai-workflows/",
    "brainiac-mastermind-training/brainiac-module-3-agent-delegation/",
    "brainiac-mastermind-training/brainiac-module-4-multi-agent-teams/",
    "brainiac-mastermind-training/brainiac-module-5-memory-context/",
    "brainiac-mastermind-training/brainiac-module-6-self-assessment/",
    "brainiac-mastermind-training/brainiac-module-7-shipping-measurement/",
    "brainiac-mastermind-training/brainiac-module-8-software-building/",
    "brainiac-mastermind-training/brainiac-module-9-10x-ai-partner/",
    "brainiac-mastermind-training/brainiac-module-10-ai-workforce/",
}

def check_protected_paths(paths_to_deploy: list, force: bool = False) -> list:
    """Block deployment to protected paths unless --force-protected is used."""
    blocked = []
    for p in paths_to_deploy:
        for protected in PROTECTED_PATHS:
            if p.startswith(protected) or p == protected.rstrip("/"):
                blocked.append(p)
    if blocked and not force:
        print(f"\n🚨 BLOCKED: Deployment would touch PROTECTED paths:")
        for b in blocked:
            print(f"   ❌ {b}")
        print(f"\nThese paths are FROZEN (CONSTITUTIONAL). Use --force-protected to override.")
        print(f"This requires EXPLICIT permission from Jared.\n")
        return blocked
    return []

# ---------------------------------------------------------------------------
# .env loader
# ---------------------------------------------------------------------------

def load_env(env_path: Path) -> dict:
    """Load .env file into a dict (simple key=value parser)."""
    env = {}
    if not env_path.exists():
        return env
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            env[key] = value
    return env


def get_config():
    """Load config from environment, falling back to .env file."""
    env = load_env(ENV_FILE)

    api_key = os.environ.get("CF_API_KEY") or env.get("CF_API_KEY")
    auth_email = os.environ.get("CF_AUTH_EMAIL") or env.get("CF_AUTH_EMAIL")
    account_id = os.environ.get("CF_PAGES_ACCOUNT") or env.get("CF_PAGES_ACCOUNT") or DEFAULT_ACCOUNT_ID
    project_name = os.environ.get("CF_PAGES_PROJECT") or env.get("CF_PAGES_PROJECT") or DEFAULT_PROJECT_NAME

    if not api_key or not auth_email:
        print("ERROR: CF_API_KEY and CF_AUTH_EMAIL required.", file=sys.stderr)
        print("Set them in environment or in .env file.", file=sys.stderr)
        sys.exit(1)

    return {
        "api_key": api_key,
        "auth_email": auth_email,
        "account_id": account_id,
        "project_name": project_name,
    }

# ---------------------------------------------------------------------------
# Blake3 hashing (matches wrangler's algorithm exactly)
# ---------------------------------------------------------------------------

try:
    import blake3 as _blake3

    def compute_hash(content: bytes, filepath: str) -> str:
        """Compute CF Pages file hash: blake3(base64(content) + extension)[:32]."""
        b64 = base64.b64encode(content).decode("ascii")
        ext = Path(filepath).suffix.lstrip(".")
        hash_input = b64 + ext
        return _blake3.blake3(hash_input.encode()).hexdigest()[:32]

except ImportError:
    print("WARNING: blake3 not installed. Install with: pip3 install blake3", file=sys.stderr)
    print("Falling back to computing hashes via Node.js (slower).", file=sys.stderr)

    def compute_hash(content: bytes, filepath: str) -> str:
        """Fallback: use Node.js blake3-wasm to compute hash."""
        import subprocess
        import tempfile
        b64 = base64.b64encode(content).decode("ascii")
        ext = Path(filepath).suffix.lstrip(".")
        js_code = f"""
        const blake3 = require('blake3-wasm');
        blake3.load().then(() => {{
            const hash = blake3.hash('{b64}{ext}').toString('hex').slice(0, 32);
            process.stdout.write(hash);
        }});
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(js_code)
            f.flush()
            try:
                result = subprocess.run(["node", f.name], capture_output=True, text=True, timeout=10)
                return result.stdout.strip()
            finally:
                os.unlink(f.name)

# ---------------------------------------------------------------------------
# Cloudflare API helpers
# ---------------------------------------------------------------------------

def cf_api(method: str, path: str, config: dict, body=None, headers=None, is_jwt=False):
    """Make a Cloudflare API request."""
    if path.startswith("/"):
        url = f"https://api.cloudflare.com/client/v4{path}"
    else:
        url = path

    hdrs = {}
    if is_jwt:
        hdrs["Authorization"] = f"Bearer {headers['jwt']}"
    else:
        hdrs["X-Auth-Email"] = config["auth_email"]
        hdrs["X-Auth-Key"] = config["api_key"]

    if body is not None and not isinstance(body, bytes):
        hdrs["Content-Type"] = "application/json"
        body = json.dumps(body).encode()

    if headers:
        for k, v in headers.items():
            if k != "jwt":
                hdrs[k] = v

    req = Request(url, data=body, headers=hdrs, method=method)

    for attempt in range(MAX_RETRIES):
        try:
            with urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
                if not data.get("success", True):
                    errors = data.get("errors", [])
                    raise Exception(f"API error: {errors}")
                return data.get("result", data)
        except HTTPError as e:
            error_body = e.read().decode() if e.fp else str(e)
            if attempt < MAX_RETRIES - 1 and e.code in (429, 500, 502, 503, 504):
                wait = 2 ** attempt
                print(f"  Retrying in {wait}s (HTTP {e.code})...", file=sys.stderr)
                time.sleep(wait)
                continue
            raise Exception(f"HTTP {e.code}: {error_body}")

    raise Exception("Max retries exceeded")


def cf_api_multipart(path: str, config: dict, fields: dict):
    """Make a multipart/form-data POST request to CF API."""
    import uuid
    boundary = uuid.uuid4().hex
    url = f"https://api.cloudflare.com/client/v4{path}"

    body_parts = []
    for name, value in fields.items():
        body_parts.append(f"--{boundary}\r\n".encode())
        body_parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        if isinstance(value, bytes):
            body_parts.append(value)
        else:
            body_parts.append(str(value).encode())
        body_parts.append(b"\r\n")
    body_parts.append(f"--{boundary}--\r\n".encode())

    body = b"".join(body_parts)

    hdrs = {
        "X-Auth-Email": config["auth_email"],
        "X-Auth-Key": config["api_key"],
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    req = Request(url, data=body, headers=hdrs, method="POST")

    for attempt in range(MAX_RETRIES):
        try:
            with urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read())
                if not data.get("success", True):
                    errors = data.get("errors", [])
                    raise Exception(f"API error: {errors}")
                return data.get("result", data)
        except HTTPError as e:
            error_body = e.read().decode() if e.fp else str(e)
            if attempt < MAX_RETRIES - 1 and e.code in (429, 500, 502, 503, 504):
                wait = 2 ** attempt
                print(f"  Retrying in {wait}s (HTTP {e.code})...", file=sys.stderr)
                time.sleep(wait)
                continue
            raise Exception(f"HTTP {e.code}: {error_body}")

    raise Exception("Max retries exceeded")

# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def get_current_manifest(config: dict) -> dict:
    """Get the file manifest from the latest production deployment."""
    acct = config["account_id"]
    proj = config["project_name"]

    # Get latest deployment
    deployments = cf_api(
        "GET",
        f"/accounts/{acct}/pages/projects/{proj}/deployments?per_page=1",
        config,
    )

    if not deployments:
        print("No existing deployments found. Starting fresh.", file=sys.stderr)
        return {}

    latest = deployments[0]
    deploy_id = latest["id"]
    print(f"Current deployment: {deploy_id} ({latest.get('url', 'unknown')})", file=sys.stderr)

    # Get full deployment details including file manifest
    deployment = cf_api(
        "GET",
        f"/accounts/{acct}/pages/projects/{proj}/deployments/{deploy_id}",
        config,
    )

    manifest = deployment.get("files", {})
    print(f"Current site has {len(manifest)} files.", file=sys.stderr)
    return manifest


def get_upload_token(config: dict) -> str:
    """Get a JWT for uploading assets."""
    acct = config["account_id"]
    proj = config["project_name"]
    result = cf_api(
        "GET",
        f"/accounts/{acct}/pages/projects/{proj}/upload-token",
        config,
    )
    return result["jwt"]


def check_missing_hashes(jwt: str, hashes: list) -> list:
    """Check which hashes are not yet on CF's servers."""
    if not hashes:
        return []

    result = cf_api(
        "POST",
        "/pages/assets/check-missing",
        {},
        body={"hashes": hashes},
        headers={"jwt": jwt},
        is_jwt=True,
    )
    return result  # Returns list of missing hashes


def upload_files(jwt: str, files_to_upload: list):
    """Upload files to CF Pages asset storage.

    files_to_upload: list of (hash, base64_content, content_type)
    """
    # Split into buckets respecting size limits
    buckets = []
    current_bucket = []
    current_size = 0

    for file_hash, b64_content, content_type in files_to_upload:
        file_size = len(b64_content)
        if current_size + file_size > MAX_UPLOAD_SIZE or len(current_bucket) >= MAX_BUCKET_FILES:
            if current_bucket:
                buckets.append(current_bucket)
            current_bucket = []
            current_size = 0
        current_bucket.append((file_hash, b64_content, content_type))
        current_size += file_size

    if current_bucket:
        buckets.append(current_bucket)

    for i, bucket in enumerate(buckets):
        payload = []
        for file_hash, b64_content, content_type in bucket:
            payload.append({
                "key": file_hash,
                "value": b64_content,
                "metadata": {"contentType": content_type},
                "base64": True,
            })

        print(f"  Uploading bucket {i + 1}/{len(buckets)} ({len(bucket)} files)...", file=sys.stderr)
        cf_api(
            "POST",
            "/pages/assets/upload",
            {},
            body=payload,
            headers={"jwt": jwt},
            is_jwt=True,
        )


def upsert_hashes(jwt: str, hashes: list):
    """Confirm all hashes are registered."""
    if not hashes:
        return
    cf_api(
        "POST",
        "/pages/assets/upsert-hashes",
        {},
        body={"hashes": hashes},
        headers={"jwt": jwt},
        is_jwt=True,
    )


def create_deployment(config: dict, manifest: dict, branch: str = "main", commit_message: str = "") -> dict:
    """Create a new deployment with the given manifest."""
    acct = config["account_id"]
    proj = config["project_name"]

    fields = {
        "manifest": json.dumps(manifest),
        "branch": branch,
    }
    if commit_message:
        fields["commit_message"] = commit_message
    fields["commit_dirty"] = "true"

    result = cf_api_multipart(
        f"/accounts/{acct}/pages/projects/{proj}/deployments",
        config,
        fields,
    )
    return result

# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

def get_content_type(filepath: str) -> str:
    """Guess MIME type for a file."""
    ct, _ = mimetypes.guess_type(filepath)
    return ct or "application/octet-stream"


def collect_files(paths: list, base_dir: Path) -> dict:
    """Collect files from paths. Returns {site_path: (content_bytes, content_type)}.

    Paths can be files or directories relative to site root.
    Files are read from base_dir / path.
    """
    files = {}

    for path_str in paths:
        # Normalize: remove leading slash, ensure consistent format
        site_path = path_str.strip("/")
        local_path = base_dir / site_path

        if local_path.is_dir():
            # Recursively add all files in directory
            for file_path in sorted(local_path.rglob("*")):
                if file_path.is_file():
                    rel = file_path.relative_to(base_dir)
                    site_key = "/" + str(rel).replace(os.sep, "/")
                    content = file_path.read_bytes()
                    ct = get_content_type(str(file_path))
                    files[site_key] = (content, ct)
        elif local_path.is_file():
            site_key = "/" + site_path
            content = local_path.read_bytes()
            ct = get_content_type(str(local_path))
            files[site_key] = (content, ct)
        else:
            print(f"WARNING: {local_path} not found, skipping.", file=sys.stderr)

    return files

# ---------------------------------------------------------------------------
# Pre-deploy credential scan (SECURITY gate — CONSTITUTIONAL, no bypass)
# Wires .claude/skills/pre-deploy-credential-scan/scan.sh as a hard gate.
# Added 2026-05-09 per Tier-1 retire (17 conductor BOOPs / ~40h undispatched)
# after CE SME / Phil-creds leak 2026-05-07 showed skill-filed != skill-enforced.
# ---------------------------------------------------------------------------

CRED_SCAN_SKILL = PROJECT_ROOT / ".claude" / "skills" / "pre-deploy-credential-scan" / "scan.sh"

PARITY_CHECK_SCRIPT = PROJECT_ROOT / "tools" / "check-dual-source-parity.sh"
EXTERNAL_PUREBRAIN_SITE = Path(os.environ.get("EXTERNAL_DIR", "/home/jared/purebrain-site"))


class _ParityDriftError(Exception):
    """Raised when dual-source parity check fails for files in the deploy set."""


def _parity_pre_deploy_check(new_files: dict) -> None:
    """Dual-source parity gate for CF Pages dual-source race condition.

    Per feedback_dual_source_cf_pages_silent_overwrite.md: this CF Pages project
    has TWO writers — cf-deploy.py (this script) AND github:push from
    `puretechnyc/purebrain-site`. Every shared file MUST stay byte-identical
    across both repos. Drift means the next external push (Lumen update,
    investor gift page, pitch deck, partner page) atomically regresses prod.

    This gate fires on every cf-deploy.py invocation, checking ONLY the files
    being deployed against their counterparts in the external repo. If the
    external repo's copy differs from what we're about to upload, drift exists
    NOW (or will after this push) — block until reconciled.

    Skips files that don't exist in the external repo (those are aether-only,
    no drift possible). Skips binary files (no semantic compare relevant for
    parity beyond byte-identity, which is what md5 already does).

    Set CF_DEPLOY_SKIP_PARITY=1 to bypass (emergency only).
    """
    import hashlib

    if not EXTERNAL_PUREBRAIN_SITE.exists():
        # No external repo cloned locally — parity check is a no-op (deployer
        # may be running from a CI host without the second repo).
        print(
            "  ⚠️  parity-check: external repo not found at "
            f"{EXTERNAL_PUREBRAIN_SITE} (skipping)",
            file=sys.stderr,
        )
        return

    drifted = []
    checked = 0
    for site_path, (content, _ct) in new_files.items():
        rel = site_path.lstrip("/")
        external_path = EXTERNAL_PUREBRAIN_SITE / rel
        if not external_path.exists():
            continue  # external doesn't have this — no shared-path drift
        try:
            external_bytes = external_path.read_bytes()
        except Exception as e:
            print(f"  ⚠️  parity-check: could not read {external_path}: {e}", file=sys.stderr)
            continue
        h_new = hashlib.md5(content).hexdigest()
        h_ext = hashlib.md5(external_bytes).hexdigest()
        checked += 1
        if h_new != h_ext:
            drifted.append((rel, h_new, h_ext))

    if drifted:
        print(
            f"\n🛡️  DRIFT GATE: {len(drifted)} file(s) being deployed differ "
            "from external purebrain-site:",
            file=sys.stderr,
        )
        for rel, h_new, h_ext in drifted:
            print(f"   - {rel}", file=sys.stderr)
            print(f"       this deploy: {h_new}", file=sys.stderr)
            print(f"       external:    {h_ext}", file=sys.stderr)
        raise _ParityDriftError(
            f"{len(drifted)} file(s) in this deploy diverge from "
            "puretechnyc/purebrain-site. Sync the two repos before deploying."
        )

    if checked > 0:
        print(
            f"  🛡️  parity-check: {checked} shared file(s) match external repo",
            file=sys.stderr,
        )

def pre_deploy_credential_scan(new_files: dict) -> None:
    """Block deploy if hardcoded credentials detected in actual upload payload.

    Materializes the exact bytes about to be uploaded (including --stdin content)
    into a temp directory, then invokes the scan.sh skill against that directory.
    This guarantees we scan the real upload contents — not just git working tree —
    so stdin-injected content and any in-memory transforms are also covered.

    Exits with code 2 on any HIGH or CRITICAL finding. No environment-variable
    bypass exists by design (filing != enforcement; the gate must not be skippable).
    """
    import subprocess
    import tempfile
    import shutil

    if not CRED_SCAN_SKILL.exists():
        print(f"🔴 BLOCKED: pre-deploy credential scan skill missing at {CRED_SCAN_SKILL}", file=sys.stderr)
        print("   Restore .claude/skills/pre-deploy-credential-scan/scan.sh before deploying.", file=sys.stderr)
        sys.exit(2)

    # Only scan text artifacts that scan.sh's --include patterns match.
    # Binary assets (images, fonts, etc.) are out of scope for credential greps.
    SCAN_EXTENSIONS = (".html", ".js", ".ts", ".mjs", ".cjs", ".htm")
    scan_targets = {p: data for p, data in new_files.items()
                    if p.lower().endswith(SCAN_EXTENSIONS)}

    if not scan_targets:
        print("Pre-deploy credential scan: no scannable text artifacts in payload (skipping).", file=sys.stderr)
        return

    print(f"Pre-deploy credential scan: materializing {len(scan_targets)} file(s) for scan...", file=sys.stderr)

    tmpdir = Path(tempfile.mkdtemp(prefix="cf-deploy-credscan-"))
    try:
        for site_path, (content, _ct) in scan_targets.items():
            # Mirror site_path under tmpdir so grep -n line numbers map to real paths.
            rel = site_path.lstrip("/")
            target = tmpdir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

        result = subprocess.run(
            ["bash", str(CRED_SCAN_SKILL), str(tmpdir)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("", file=sys.stderr)
            print("🔴 BLOCKED: pre-deploy credential scan FAILED", file=sys.stderr)
            print(f"   Skill: {CRED_SCAN_SKILL}", file=sys.stderr)
            print(f"   Scanned payload root: {tmpdir} (preserved for audit)", file=sys.stderr)
            print("   Findings (line numbers are within materialized payload):", file=sys.stderr)
            if result.stdout:
                # Rewrite tmpdir prefix in output so reviewers see site paths, not /tmp/...
                cleaned = result.stdout.replace(str(tmpdir) + "/", "/")
                print(cleaned, file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            print("", file=sys.stderr)
            print("   This gate is CONSTITUTIONAL — no bypass env var exists.", file=sys.stderr)
            print("   Fix the credential leak in source, re-stage, and re-run.", file=sys.stderr)
            # Intentionally NOT cleaning up tmpdir on failure — auditors can inspect.
            sys.exit(2)

        # Clean only on success
        shutil.rmtree(tmpdir, ignore_errors=True)
        print("Pre-deploy credential scan: clean", file=sys.stderr)

    except FileNotFoundError as e:
        # bash missing or skill removed mid-run — fail closed
        shutil.rmtree(tmpdir, ignore_errors=True)
        print(f"🔴 BLOCKED: cannot execute credential scan ({e})", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Main deploy logic
# ---------------------------------------------------------------------------

def deploy(paths: list, base_dir: Path, dry_run: bool = False,
           delete_paths: list = None, stdin_content: bytes = None,
           commit_message: str = ""):
    """Deploy specific files to CF Pages, preserving all other files."""

    config = get_config()

    # 1. Get current deployment manifest
    print("Fetching current deployment manifest...", file=sys.stderr)
    current_manifest = get_current_manifest(config)

    # 2. Collect files to upload
    if stdin_content and len(paths) == 1:
        # Single file from stdin
        site_key = "/" + paths[0].strip("/")
        ct = get_content_type(paths[0])
        new_files = {site_key: (stdin_content, ct)}
    else:
        new_files = collect_files(paths, base_dir)

    if not new_files and not delete_paths:
        print("No files to deploy.", file=sys.stderr)
        return

    # 2.5. SECURITY GATE — pre-deploy credential scan (CONSTITUTIONAL, no bypass)
    # Runs on the EXACT bytes about to be uploaded (including --stdin payloads).
    # Fires before hash compute, manifest merge, AND the dry-run short-circuit,
    # so dry-runs also surface credential leaks. Exits 2 on any finding.
    if new_files:
        pre_deploy_credential_scan(new_files)

    # 2.6. DRIFT GATE — dual-source parity check (CONSTITUTIONAL, CTO 2026-05-12)
    # Per feedback_dual_source_cf_pages_silent_overwrite.md: CF Pages production
    # has TWO writers (this cf-deploy.py + github:push from puretechnyc/purebrain-site).
    # Drift on any path means the next external push regresses production.
    # Pre-deploy parity check on the files being deployed catches drift before
    # we make it worse. Set CF_DEPLOY_SKIP_PARITY=1 to bypass (emergency-only).
    if new_files and os.environ.get("CF_DEPLOY_SKIP_PARITY") != "1":
        try:
            _parity_pre_deploy_check(new_files)
        except _ParityDriftError as e:
            print(f"\nDRIFT GATE FAILED — {e}", file=sys.stderr)
            print(
                "Run: tools/check-dual-source-parity.sh --paths <comma-sep>\n"
                "Or set CF_DEPLOY_SKIP_PARITY=1 to bypass (emergency-only).",
                file=sys.stderr,
            )
            sys.exit(3)

    # 3. Compute hashes for new files
    print(f"Computing hashes for {len(new_files)} file(s)...", file=sys.stderr)
    new_hashes = {}  # site_path -> hash
    file_data = {}   # hash -> (base64_content, content_type)

    for site_path, (content, ct) in new_files.items():
        file_hash = compute_hash(content, site_path)
        new_hashes[site_path] = file_hash
        b64 = base64.b64encode(content).decode("ascii")
        file_data[file_hash] = (b64, ct)

        # Check if changed
        old_hash = current_manifest.get(site_path)
        status = "NEW" if old_hash is None else ("CHANGED" if old_hash != file_hash else "UNCHANGED")
        print(f"  {status}: {site_path} ({file_hash[:12]}...)", file=sys.stderr)

    # 4. Build merged manifest
    merged_manifest = dict(current_manifest)  # Start with all existing files

    # GUARD: Ensure protected paths are NEVER removed from the manifest
    protected_entries = {}
    for key, val in current_manifest.items():
        for protected in PROTECTED_PATHS:
            if key.lstrip("/").startswith(protected):
                protected_entries[key] = val
    if protected_entries:
        print(f"\n🛡️  Preserving {len(protected_entries)} protected files (CONSTITUTIONAL)", file=sys.stderr)

    # Apply deletions
    if delete_paths:
        for dp in delete_paths:
            dp_key = "/" + dp.strip("/")
            if dp_key in merged_manifest:
                print(f"  DELETE: {dp_key}", file=sys.stderr)
                del merged_manifest[dp_key]
            else:
                print(f"  DELETE (not found): {dp_key}", file=sys.stderr)

    # Apply new/changed files
    for site_path, file_hash in new_hashes.items():
        merged_manifest[site_path] = file_hash

    # RE-INJECT protected paths that may have been accidentally removed
    for key, val in protected_entries.items():
        if key not in merged_manifest:
            print(f"  🛡️  RE-INJECTED protected: {key}", file=sys.stderr)
            merged_manifest[key] = val

    # Block any deployment that tries to CHANGE protected paths.
    # EXCEPTION: if a protected file is MISSING from current_manifest, this is a
    # restoration (the path was wiped by an upstream dual-source deploy and we
    # are restoring canonical bytes from aether's exports/cf-pages-deploy/).
    # Restoration is allowed; overwriting an existing protected hash is blocked.
    blocked = []
    restored = []
    for site_path, new_hash in new_hashes.items():
        for protected in PROTECTED_PATHS:
            if not site_path.lstrip("/").startswith(protected):
                continue
            if site_path not in current_manifest:
                restored.append(site_path)
            elif current_manifest[site_path] != new_hash:
                blocked.append(site_path)
            # else: unchanged hash, no action
    if blocked:
        print(f"\n🚨 BLOCKED: Cannot CHANGE existing PROTECTED paths:", file=sys.stderr)
        for b in blocked:
            print(f"   ❌ {b}", file=sys.stderr)
        print(f"These paths are FROZEN (CONSTITUTIONAL). Aborting.", file=sys.stderr)
        sys.exit(1)
    if restored:
        print(f"\n🛡️  RESTORING {len(restored)} missing PROTECTED paths (canonical from aether):", file=sys.stderr)
        for r in restored:
            print(f"   ↩  {r}", file=sys.stderr)

    # Summary
    added = sum(1 for p in new_hashes if p not in current_manifest)
    changed = sum(1 for p in new_hashes if p in current_manifest and current_manifest[p] != new_hashes[p])
    unchanged = sum(1 for p in new_hashes if p in current_manifest and current_manifest[p] == new_hashes[p])
    deleted = len(delete_paths) if delete_paths else 0

    print(f"\nSummary: {added} new, {changed} changed, {unchanged} unchanged, {deleted} deleted", file=sys.stderr)
    print(f"Total files in deployment: {len(merged_manifest)}", file=sys.stderr)

    if dry_run:
        print("\nDRY RUN - no deployment created.", file=sys.stderr)
        return

    # 5. Upload new/changed files
    hashes_to_check = [h for p, h in new_hashes.items()
                       if current_manifest.get(p) != h]

    if hashes_to_check:
        print(f"\nGetting upload token...", file=sys.stderr)
        jwt = get_upload_token(config)

        print(f"Checking which files need uploading...", file=sys.stderr)
        missing = check_missing_hashes(jwt, hashes_to_check)
        print(f"  {len(missing)} file(s) need uploading, {len(hashes_to_check) - len(missing)} already on CF.", file=sys.stderr)

        if missing:
            files_to_upload = [
                (h, file_data[h][0], file_data[h][1])
                for h in missing
                if h in file_data
            ]
            print(f"Uploading {len(files_to_upload)} file(s)...", file=sys.stderr)
            upload_files(jwt, files_to_upload)

        # Confirm all hashes
        all_new_hashes = list(new_hashes.values())
        print("Confirming hashes...", file=sys.stderr)
        upsert_hashes(jwt, all_new_hashes)

    # 6. Create deployment
    msg = commit_message or f"cf-deploy.py: {added} new, {changed} changed, {deleted} deleted"
    print(f"\nCreating deployment...", file=sys.stderr)
    result = create_deployment(config, merged_manifest, commit_message=msg)

    deploy_url = result.get("url", "unknown")
    deploy_id = result.get("id", "unknown")
    print(f"\nDeployment created!", file=sys.stderr)
    print(f"  ID: {deploy_id}", file=sys.stderr)
    print(f"  URL: {deploy_url}", file=sys.stderr)
    print(f"  Production: https://purebrain.ai", file=sys.stderr)

    return result

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Deploy specific files to CF Pages without overwriting other files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy a single file
  %(prog)s blog/new-post/index.html

  # Deploy a directory
  %(prog)s investor-avatar/

  # Deploy multiple files
  %(prog)s blog/new-post/index.html blog/new-post/banner.png

  # Deploy from a custom local directory
  %(prog)s --base-dir /tmp/build/ index.html

  # Dry run
  %(prog)s --dry-run blog/new-post/index.html

  # Delete a file
  %(prog)s --delete old-page/index.html

  # Pipe content in
  echo '<h1>Test</h1>' | %(prog)s --stdin test/index.html
        """,
    )

    parser.add_argument(
        "paths",
        nargs="*",
        help="File or directory paths relative to site root (e.g., blog/new-post/index.html)",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=DEFAULT_BASE_DIR,
        help=f"Local directory containing site files (default: {DEFAULT_BASE_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deployed without actually deploying",
    )
    parser.add_argument(
        "--delete",
        nargs="+",
        dest="delete_paths",
        help="File paths to remove from the site",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read file content from stdin (use with a single path)",
    )
    parser.add_argument(
        "--message", "-m",
        default="",
        help="Deployment commit message",
    )
    parser.add_argument(
        "--manifest",
        action="store_true",
        help="Print current deployment manifest as JSON and exit",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_files",
        help="List all files in current deployment",
    )
    parser.add_argument(
        "--list-path",
        type=str,
        default=None,
        help="List files under a specific path prefix",
    )

    args = parser.parse_args()

    # Manifest mode
    if args.manifest:
        config = get_config()
        manifest = get_current_manifest(config)
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return

    # List mode
    if args.list_files or args.list_path is not None:
        config = get_config()
        manifest = get_current_manifest(config)
        prefix = ("/" + args.list_path.strip("/")) if args.list_path else ""
        for path in sorted(manifest.keys()):
            if path.startswith(prefix):
                print(path)
        return

    # Deploy mode
    if not args.paths and not args.delete_paths:
        parser.print_help()
        sys.exit(1)

    stdin_content = None
    if args.stdin:
        if len(args.paths) != 1:
            print("ERROR: --stdin requires exactly one path.", file=sys.stderr)
            sys.exit(1)
        stdin_content = sys.stdin.buffer.read()

    deploy(
        paths=args.paths or [],
        base_dir=args.base_dir,
        dry_run=args.dry_run,
        delete_paths=args.delete_paths,
        stdin_content=stdin_content,
        commit_message=args.message,
    )


if __name__ == "__main__":
    main()
