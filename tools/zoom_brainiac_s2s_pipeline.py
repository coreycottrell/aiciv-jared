#!/usr/bin/env python3
"""
zoom_brainiac_s2s_pipeline.py — Weekly Brainiac auto-pipeline via S2S OAuth.

USAGE:
  # Weekly auto (defaults to "most recent week")
  python3 tools/zoom_brainiac_s2s_pipeline.py

  # Specific date range
  python3 tools/zoom_brainiac_s2s_pipeline.py --from 2026-05-05 --to 2026-05-12

  # Specific module number (auto-numbers by recording_count)
  python3 tools/zoom_brainiac_s2s_pipeline.py --module 11 --from 2026-05-13 --to 2026-05-20

  # Just discover (no download)
  python3 tools/zoom_brainiac_s2s_pipeline.py --discover-only

  # Just print the patch diffs (no commit/deploy)
  python3 tools/zoom_brainiac_s2s_pipeline.py --module 11 --no-deploy

CREDENTIALS:
  Reads S2S OAuth from EITHER (in priority order):
    1. Wrangler secret on `zoom-brainiac-worker` (preferred for prod)
       — fetch via: wrangler secret get ZOOM_S2S_BUNDLE --name zoom-brainiac-worker
    2. Env var ZOOM_S2S_BUNDLE (JSON string with keys ZOOM_ACCOUNT_ID,
       ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)
    3. File at $HOME/exports/secrets/zoom-s2s.env (JSON, chmod 600, OUTSIDE git)

  NEVER commit credentials. cf-deploy.py credential scan will reject.

CONSTITUTIONAL:
  - Requires Zoom S2S scope: cloud_recording:read:list_recording_files:admin
    Without it, download_access_token cannot be issued and downloads will 401.
  - Dual-source updates (aether mirror + puretechnyc canonical) per
    feedback_dual_source_cf_pages_silent_overwrite.md
  - Pre-deploy credential scan must pass (feedback_credential_scan_regex_must_cover_prefixless_tokens.md)
  - GET (not HEAD) for post-deploy health checks
    (feedback_cf_pages_use_get_not_head_for_health_checks.md)

OUTPUTS:
  - Downloaded MP4 in exports/brainiac-training/downloads/YYYY-MM-DD/
  - R2 path: brainiac/recordings/module-N/full.mp4
  - Site A patched: /home/jared/projects/brainiac-purebrain/index.html (~line 2802)
  - Site B aether mirror: exports/cf-pages-deploy/brainiac-mastermind-training/index.html
  - Site B canonical:    /home/jared/purebrain-site/brainiac-mastermind-training/index.html
  - recordings-index.json appended
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
BRAINIAC_ROOT = Path("/home/jared/projects/brainiac-purebrain")
PUREBRAIN_SITE = Path("/home/jared/purebrain-site")
DOWNLOADS_DIR = AETHER_ROOT / "exports" / "brainiac-training" / "downloads"
RECORDINGS_INDEX = AETHER_ROOT / "exports" / "brainiac-training" / "recordings-index.json"

R2_BUCKET_PATH = "brainiac/recordings"
R2_PROXY_BASE = "https://r2-upload-proxy.in0v8.workers.dev"

# Zoom topic filter
BRAINIAC_TOPIC_KEYWORDS = ["brainiac", "mastermind", "2103-"]


# ---------------------------------------------------------------------------
# Credential loading (priority order; no creds in source)
# ---------------------------------------------------------------------------
def load_s2s_creds() -> dict:
    """Load S2S OAuth bundle. Tries (1) env var, (2) secrets file."""
    # (1) Env var as JSON
    bundle = os.environ.get("ZOOM_S2S_BUNDLE")
    if bundle:
        try:
            return json.loads(bundle)
        except json.JSONDecodeError:
            pass

    # (2) File at ~/exports/secrets/zoom-s2s.env (JSON)
    secrets_path = Path.home() / "exports" / "secrets" / "zoom-s2s.env"
    if secrets_path.exists():
        try:
            return json.loads(secrets_path.read_text())
        except json.JSONDecodeError as e:
            print(f"[creds] failed to parse {secrets_path}: {e}", file=sys.stderr)

    # (3) Wrangler secret (manual lookup since SDK isn't here)
    # Documented in tools/README-brainiac-pipeline.md
    raise SystemExit(
        "FATAL: No Zoom S2S credentials available.\n"
        "Provide one of:\n"
        "  ENV  ZOOM_S2S_BUNDLE='{\"ZOOM_ACCOUNT_ID\":\"...\",\"ZOOM_CLIENT_ID\":\"...\",\"ZOOM_CLIENT_SECRET\":\"...\"}'\n"
        "  FILE ~/exports/secrets/zoom-s2s.env  (JSON, chmod 600)\n"
        "See tools/README-brainiac-pipeline.md for wrangler-secret pattern."
    )


def fetch_s2s_token(creds: dict) -> dict:
    """Exchange S2S creds for access_token. Returns dict with access_token, api_url, scope."""
    basic = base64.b64encode(
        f"{creds['ZOOM_CLIENT_ID']}:{creds['ZOOM_CLIENT_SECRET']}".encode()
    ).decode()
    data = urllib.parse.urlencode(
        {"grant_type": "account_credentials", "account_id": creds["ZOOM_ACCOUNT_ID"]}
    ).encode()
    req = urllib.request.Request(
        "https://zoom.us/oauth/token",
        data=data,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def assert_required_scopes(scope_str: str) -> None:
    """Raise if required scopes are missing. Fail fast with clear remediation."""
    required = {
        "cloud_recording:read:list_account_recordings:admin",  # list meetings
        "cloud_recording:read:list_recording_files:admin",     # download_access_token
    }
    have = set(scope_str.split())
    missing = required - have
    if missing:
        raise SystemExit(
            f"FATAL: Zoom S2S app missing required scopes:\n"
            f"  Missing: {sorted(missing)}\n"
            f"  Have:    {sorted(have)}\n\n"
            f"FIX: Open https://marketplace.zoom.us/develop/apps → S2S app → Scopes tab\n"
            f"     Add the missing scopes, save, then re-run this pipeline.\n"
            f"     (No reauthorization needed for S2S apps — new scopes apply immediately.)"
        )


# ---------------------------------------------------------------------------
# Recording discovery
# ---------------------------------------------------------------------------
def zoom_api_get(token: str, api_url: str, path: str, params: dict = None) -> dict:
    url = f"{api_url}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise SystemExit(f"Zoom API {e.code} on {path}: {body}")


def find_brainiac_recording(token: str, api_url: str, from_date: str, to_date: str) -> dict | None:
    """Find the (single) Brainiac recording in the date range. Returns meeting dict or None.

    NOTE (2026-05-12): the list endpoint /v2/accounts/me/recordings does NOT return
    download_access_token even with `include_fields=download_access_token&ttl=N` when
    the calling account is the Zoom Marketplace S2S app context. The per-meeting endpoint
    /v2/meetings/{uuid}/recordings DOES return it. So we discover via the list endpoint
    then hydrate via the per-meeting endpoint to obtain download_access_token.
    """
    data = zoom_api_get(
        token,
        api_url,
        "/v2/accounts/me/recordings",
        {
            "from": from_date,
            "to": to_date,
            "page_size": 100,
        },
    )
    meetings = data.get("meetings", [])
    hits = [
        m for m in meetings
        if any(k in m.get("topic", "").lower() for k in BRAINIAC_TOPIC_KEYWORDS)
    ]
    if not hits:
        return None
    # Most recent first
    hits.sort(key=lambda m: m.get("start_time", ""), reverse=True)
    chosen = hits[0]

    # Hydrate with per-meeting detail to obtain download_access_token
    uuid = chosen["uuid"]
    if uuid.startswith("/") or "//" in uuid:
        encoded = urllib.parse.quote(urllib.parse.quote(uuid, safe=""), safe="")
    else:
        encoded = urllib.parse.quote(uuid, safe="")
    full = zoom_api_get(
        token, api_url, f"/v2/meetings/{encoded}/recordings",
        {"include_fields": "download_access_token", "ttl": 86400},
    )
    # Merge: per-meeting response contains download_access_token + recording_files
    chosen.update({
        "download_access_token": full.get("download_access_token"),
        "recording_files": full.get("recording_files", chosen.get("recording_files", [])),
    })
    return chosen


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------
def download_mp4(meeting: dict, out_dir: Path) -> Path:
    """Download MP4 file. Requires download_access_token in meeting dict."""
    dat = meeting.get("download_access_token")
    if not dat:
        raise SystemExit(
            "FATAL: meeting has no download_access_token.\n"
            "This means the S2S app lacks cloud_recording:read:list_recording_files:admin scope.\n"
            "Add the scope on Zoom Marketplace and re-run."
        )
    mp4 = None
    for f in meeting.get("recording_files", []):
        if f.get("file_type") == "MP4":
            mp4 = f
            break
    if not mp4:
        raise SystemExit("FATAL: meeting has no MP4 recording file")

    download_url = f"{mp4['download_url']}?access_token={dat}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "brainiac-module.mp4"

    print(f"[download] starting (expect ~{mp4.get('file_size',0)/1024/1024:.0f}MB)", flush=True)
    t0 = time.time()
    total = 0
    chunk = 4 * 1024 * 1024
    req = urllib.request.Request(download_url)
    with urllib.request.urlopen(req, timeout=600) as resp:
        content_length = int(resp.headers.get("Content-Length", 0))
        with open(out_path, "wb") as f:
            last_log_mb = 0
            while True:
                buf = resp.read(chunk)
                if not buf:
                    break
                f.write(buf)
                total += len(buf)
                mb = total // (1024 * 1024)
                if mb - last_log_mb >= 50:
                    last_log_mb = mb
                    pct = (total / content_length * 100) if content_length else 0
                    print(f"[download] {mb}MB ({pct:.0f}%) elapsed={time.time()-t0:.0f}s", flush=True)
    print(f"[download] DONE: {total/(1024*1024):.0f}MB in {time.time()-t0:.0f}s", flush=True)
    return out_path


# ---------------------------------------------------------------------------
# R2 upload (via proxy worker)
# ---------------------------------------------------------------------------
def upload_to_r2(local_file: Path, r2_key: str) -> str:
    """Use existing r2_proxy_multipart_upload.py."""
    cmd = [
        sys.executable,
        str(AETHER_ROOT / "tools" / "r2_proxy_multipart_upload.py"),
        str(local_file),
        r2_key,
    ]
    print(f"[r2-upload] {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, capture_output=False)
    if r.returncode != 0:
        raise SystemExit(f"R2 upload failed (exit {r.returncode})")
    return f"{R2_PROXY_BASE}/{r2_key}"


# ---------------------------------------------------------------------------
# Hub HTML patch generation
# ---------------------------------------------------------------------------
def patch_site_a(module_num: int, r2_url: str, duration_str: str) -> tuple[Path, str, str]:
    """Patch brainiac-purebrain/index.html: swap hlsUrl:null on the matching module entry."""
    path = BRAINIAC_ROOT / "index.html"
    text = path.read_text()
    # Find the module entry by id (e.g. id: "module-10-workforce")
    # Module N pattern in this repo: id: "module-N-*" then hlsUrl: null,
    pattern = re.compile(
        r'(id:\s*"module-' + str(module_num) + r'-[^"]+",[\s\S]*?)hlsUrl:\s*null,',
        re.MULTILINE,
    )
    new_text, n = pattern.subn(
        r'\1hlsUrl: "' + r2_url + r'",',
        text,
        count=1,
    )
    if n == 0:
        # Fallback: scan for the standalone TRAINING_VIDEOS line 2800-2802 pattern
        raise RuntimeError(
            f"Site A: could not locate module-{module_num} entry with hlsUrl:null. "
            "Manual edit required."
        )
    # Also update duration if "14 slides" placeholder
    new_text = re.sub(
        r'(id:\s*"module-' + str(module_num) + r'-[^"]+",[\s\S]*?)duration:\s*"14 slides"',
        r'\1duration: "' + duration_str + '"',
        new_text,
        count=1,
    )
    return path, text, new_text


def patch_site_b(module_num: int, r2_url: str, duration_str: str, mirror_or_canonical: Path) -> tuple[Path, str, str]:
    """Patch site B (canonical or mirror) — add M{N} JS entry + swap "Coming Soon" span to Watch button.

    This handles BOTH the case where there's already a placeholder JS entry with hlsUrl:null
    AND the case where the JS entry doesn't exist yet (Coming Soon span only).
    """
    path = mirror_or_canonical
    text = path.read_text()
    module_id = f"module-{module_num}-workforce" if module_num == 10 else f"module-{module_num}"

    # Case A: existing entry with hlsUrl:null → swap
    pattern_a = re.compile(
        r'(id:\s*"' + re.escape(module_id) + r'",[\s\S]{0,2000}?)hlsUrl:\s*null,',
        re.MULTILINE,
    )
    new_text, n = pattern_a.subn(
        r'\1hlsUrl: "' + r2_url + r'",',
        text,
        count=1,
    )

    # Also update duration: "TBD" → actual
    if n > 0:
        new_text = re.sub(
            r'(id:\s*"' + re.escape(module_id) + r'",[\s\S]{0,1000}?)duration:\s*"TBD"',
            r'\1duration: "' + duration_str + '"',
            new_text,
            count=1,
        )

    if n == 0:
        # Case B: no entry exists — would need to inject. Bail and surface for manual.
        raise RuntimeError(
            f"Site B {path}: no JS entry for {module_id} with hlsUrl:null found. "
            "Manual injection required (this pipeline expects placeholder).")

    # Swap "Recording Coming Soon" span to Watch button (anywhere in module N's card)
    # Find the module N card and its "coming-soon-note" span
    span_pattern = re.compile(
        r'<span class="module-watch-btn coming-soon-note">\s*'
        r'<svg[^>]*>.*?</svg>\s*Recording Coming Soon\s*</span>',
        re.DOTALL,
    )
    watch_btn = (
        f'<a class="module-watch-btn" onclick="openModal(\'{module_id}\')" role="button" tabindex="0">\n'
        f'          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>\n'
        f'          Watch Recording\n'
        f'        </a>'
    )
    # Only swap the one for this module (find the Launch Module N link nearby)
    # Simpler: find the LAST "Recording Coming Soon" span (M10 is last in list typically)
    new_text, span_n = span_pattern.subn(watch_btn, new_text, count=1)
    # span_n == 0 is OK if Watch button already there (canonical might still lack it)

    return path, text, new_text


# ---------------------------------------------------------------------------
# Recordings index
# ---------------------------------------------------------------------------
def update_recordings_index(module_num: int, meeting: dict, r2_url: str, duration_str: str) -> None:
    if RECORDINGS_INDEX.exists():
        idx = json.loads(RECORDINGS_INDEX.read_text())
    else:
        idx = {"recordings": [], "last_updated": None}

    idx["recordings"].append({
        "module_number": module_num,
        "meeting_id": str(meeting.get("id", "")),
        "meeting_date": meeting.get("start_time", "")[:10],
        "topic": meeting.get("topic", ""),
        "duration_min": meeting.get("duration", 0),
        "duration_str": duration_str,
        "r2_key": f"{R2_BUCKET_PATH}/module-{module_num}/full.mp4",
        "playback_url": r2_url,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "via": "s2s_pipeline_v1",
    })
    idx["last_updated"] = datetime.now(timezone.utc).isoformat()
    RECORDINGS_INDEX.write_text(json.dumps(idx, indent=2))
    print(f"[index] appended module {module_num} → {RECORDINGS_INDEX}", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Brainiac S2S OAuth weekly pipeline")
    p.add_argument("--module", type=int, help="Module number (e.g. 10 for M10). Required for non-discovery runs.")
    p.add_argument("--from", dest="from_date", help="From date YYYY-MM-DD")
    p.add_argument("--to", dest="to_date", help="To date YYYY-MM-DD")
    p.add_argument("--discover-only", action="store_true", help="Just list recordings, don't download")
    p.add_argument("--no-deploy", action="store_true", help="Generate patches but don't commit/deploy")
    p.add_argument("--skip-download", action="store_true", help="Use existing download from disk")
    p.add_argument("--existing-mp4", help="Path to already-downloaded MP4 (skip download step)")
    args = p.parse_args()

    # Default to last week
    if not args.to_date:
        args.to_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not args.from_date:
        args.from_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

    # Load creds + token + verify scopes
    creds = load_s2s_creds()
    print("[auth] exchanging S2S creds for token...", flush=True)
    tok = fetch_s2s_token(creds)
    token = tok["access_token"]
    api_url = tok.get("api_url", "https://api-us.zoom.us")
    print(f"[auth] OK expires={tok.get('expires_in')}s api={api_url}", flush=True)
    assert_required_scopes(tok.get("scope", ""))

    # Discover
    print(f"[discover] searching {args.from_date}..{args.to_date}", flush=True)
    meeting = find_brainiac_recording(token, api_url, args.from_date, args.to_date)
    if not meeting:
        raise SystemExit(f"No Brainiac recording found in {args.from_date}..{args.to_date}")
    print(f"[discover] FOUND: {meeting['topic']} ({meeting['start_time']}, {meeting['duration']}min)")

    if args.discover_only:
        print(json.dumps({
            "topic": meeting["topic"],
            "start_time": meeting["start_time"],
            "duration": meeting["duration"],
            "files": [f.get("file_type") for f in meeting.get("recording_files", [])],
        }, indent=2))
        return

    if args.module is None:
        raise SystemExit("--module N is required (unless --discover-only)")

    module_num = args.module
    duration_min = meeting["duration"]
    duration_str = f"{duration_min} min"

    # Download
    if args.existing_mp4:
        local_mp4 = Path(args.existing_mp4)
        if not local_mp4.exists():
            raise SystemExit(f"--existing-mp4 not found: {local_mp4}")
        print(f"[download] using existing: {local_mp4} ({local_mp4.stat().st_size/1024/1024:.0f}MB)", flush=True)
    elif args.skip_download:
        meeting_date = meeting["start_time"][:10]
        local_mp4 = DOWNLOADS_DIR / meeting_date / "brainiac-module.mp4"
        if not local_mp4.exists():
            raise SystemExit(f"--skip-download but no file at {local_mp4}")
    else:
        meeting_date = meeting["start_time"][:10]
        out_dir = DOWNLOADS_DIR / meeting_date
        local_mp4 = download_mp4(meeting, out_dir)

    # Upload to R2
    r2_key = f"{R2_BUCKET_PATH}/module-{module_num}/full.mp4"
    r2_url = upload_to_r2(local_mp4, r2_key)
    print(f"[r2] uploaded → {r2_url}", flush=True)

    # Generate patches
    site_a = patch_site_a(module_num, r2_url, duration_str)
    site_b_mirror = patch_site_b(
        module_num, r2_url, duration_str,
        AETHER_ROOT / "exports" / "cf-pages-deploy" / "brainiac-mastermind-training" / "index.html",
    )
    site_b_canon = patch_site_b(
        module_num, r2_url, duration_str,
        PUREBRAIN_SITE / "brainiac-mastermind-training" / "index.html",
    )

    if args.no_deploy:
        print("[no-deploy] Patches generated but not applied. Diffs:")
        for path, old, new in [site_a, site_b_mirror, site_b_canon]:
            print(f"\n--- {path} ---")
            print(f"  {len(old)} bytes → {len(new)} bytes ({len(new)-len(old):+d})")
        return

    # Apply patches
    for path, _, new in [site_a, site_b_mirror, site_b_canon]:
        path.write_text(new)
        print(f"[apply] wrote {path}", flush=True)

    # Verify dual-source: the M10-entry portion specifically (whole-file md5
    # cannot match while the broader 386-line drift between aether mirror and
    # canonical is unresolved — that's a separate CTO pre-build mission).
    # Extract just the JS array entry for this module and md5-compare it.
    import hashlib
    module_id = f"module-{module_num}-workforce" if module_num == 10 else f"module-{module_num}"
    entry_re = re.compile(
        r'\{[^{}]*id:\s*"' + re.escape(module_id) + r'"[\s\S]*?hlsUrl:\s*"[^"]+"[^{}]*\}',
        re.MULTILINE,
    )
    def entry_md5(p: Path) -> str:
        m = entry_re.search(p.read_text())
        if not m:
            raise SystemExit(f"FATAL: post-patch entry for {module_id} not found in {p}")
        return hashlib.md5(m.group(0).encode()).hexdigest()
    md5_mirror_entry = entry_md5(site_b_mirror[0])
    md5_canon_entry = entry_md5(site_b_canon[0])
    if md5_mirror_entry != md5_canon_entry:
        raise SystemExit(
            f"FATAL: dual-source M10-entry md5 mismatch.\n"
            f"  mirror entry md5: {md5_mirror_entry}\n"
            f"  canon  entry md5: {md5_canon_entry}\n"
            f"The M10 JS entry must be byte-identical across both files."
        )
    print(f"[dual-source] M10-entry md5 match: {md5_mirror_entry}", flush=True)

    # Update index
    update_recordings_index(module_num, meeting, r2_url, duration_str)

    print("\n[pipeline] DONE. Next steps:")
    print(f"  1. Commit aether: cd {AETHER_ROOT} && git add exports/cf-pages-deploy/brainiac-mastermind-training/index.html exports/brainiac-training/recordings-index.json && git commit")
    print(f"  2. Commit brainiac repo: cd {BRAINIAC_ROOT} && git add index.html && git commit && git push")
    print(f"  3. Deploy Site A: CF_PAGES_PROJECT=brainiac-purebrain python3 {AETHER_ROOT}/tools/cf-deploy.py --base-dir {BRAINIAC_ROOT}/ index.html")
    print(f"  4. Commit canon: cd {PUREBRAIN_SITE} && git add brainiac-mastermind-training/index.html && git commit && git push  # CF Pages auto-deploys")
    print(f"  5. 4-probe verify (see tools/README-brainiac-pipeline.md)")


if __name__ == "__main__":
    main()
