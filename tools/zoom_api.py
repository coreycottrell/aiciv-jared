#!/usr/bin/env python3
"""
zoom_api.py — Zoom API Helper for PureBrain Brainiac Pipeline
=============================================================
Handles all Zoom API interactions:
  - Token refresh (access tokens expire in 1 hour)
  - List recordings for a user/date range
  - Download recording files (video + transcript)
  - Check recording availability

CREDENTIALS:
  - .credentials/zoom_tokens.json  — access_token, refresh_token (persisted)
  - .env ZOOM_CLIENT_ID            — OAuth client ID
  - .env ZOOM_CLIENT_SECRET        — OAuth client secret

RECORDING SCOPE REQUIRED:
  - recording:read:admin  OR  cloud_recording:read:admin
  If scope check fails, this file will print a clear remediation message.

USAGE:
  python3 tools/zoom_api.py --list --from 2026-03-10 --to 2026-03-12
  python3 tools/zoom_api.py --list
  python3 tools/zoom_api.py --download <recording_id> --out /tmp/zoom
  python3 tools/zoom_api.py --refresh
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error
import base64


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
AETHER_ROOT = Path(__file__).parent.parent
TOKENS_FILE = AETHER_ROOT / ".credentials" / "zoom_tokens.json"
ENV_FILE = AETHER_ROOT / ".env"


# ---------------------------------------------------------------------------
# .env loader
# ---------------------------------------------------------------------------
def load_env(env_path: Path = ENV_FILE) -> dict:
    env = {}
    if not env_path.exists():
        return env
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


# ---------------------------------------------------------------------------
# Token management
# ---------------------------------------------------------------------------
def load_tokens() -> dict:
    """Load tokens from disk."""
    if not TOKENS_FILE.exists():
        raise FileNotFoundError(
            f"Zoom tokens file not found: {TOKENS_FILE}\n"
            "You need to complete the OAuth flow first."
        )
    with open(TOKENS_FILE) as f:
        return json.load(f)


def save_tokens(tokens: dict) -> None:
    """Persist tokens to disk with updated saved_at."""
    tokens["saved_at"] = datetime.now(timezone.utc).isoformat()
    TOKENS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)
    print(f"[zoom_api] Tokens saved to {TOKENS_FILE}", file=sys.stderr)


def is_token_expired(tokens: dict) -> bool:
    """
    Returns True if the access token is likely expired.
    Zoom access tokens expire in 3600 seconds (1 hour).
    We refresh proactively with a 5-minute buffer.
    """
    saved_at_str = tokens.get("saved_at")
    if not saved_at_str:
        return True
    try:
        saved_at = datetime.fromisoformat(saved_at_str)
        expires_in = tokens.get("expires_in", 3600)
        expiry = saved_at + timedelta(seconds=expires_in - 300)  # 5 min buffer
        return datetime.now(timezone.utc) >= expiry
    except Exception:
        return True  # Assume expired if we can't parse


def refresh_tokens(tokens: dict, env: dict) -> dict:
    """
    Refresh Zoom access token using refresh_token grant.
    Updates tokens dict in place and persists to disk.
    Returns the updated tokens dict.
    """
    client_id = env.get("ZOOM_CLIENT_ID") or tokens.get("client_id")
    client_secret = env.get("ZOOM_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "ZOOM_CLIENT_ID and ZOOM_CLIENT_SECRET must be set in .env\n"
            "These are found in the Zoom Marketplace app settings."
        )

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise ValueError("No refresh_token found in zoom_tokens.json")

    print("[zoom_api] Refreshing access token...", file=sys.stderr)

    # Basic auth header
    credentials = f"{client_id}:{client_secret}"
    b64 = base64.b64encode(credentials.encode()).decode()

    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }).encode()

    req = urllib.request.Request(
        "https://zoom.us/oauth/token",
        data=body,
        headers={
            "Authorization": f"Basic {b64}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            new_tokens = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        raise RuntimeError(
            f"Token refresh failed: HTTP {e.code}\n{body_text}\n\n"
            "Common causes:\n"
            "  - Client secret wrong or rotated\n"
            "  - Refresh token expired (user must re-authorize app)\n"
            "  - App not published / scopes changed"
        )

    # Merge with existing tokens (preserve client_id etc.)
    tokens.update(new_tokens)
    save_tokens(tokens)
    print(f"[zoom_api] Token refreshed. New scope: {new_tokens.get('scope', 'N/A')}", file=sys.stderr)
    return tokens


def get_valid_token() -> tuple[str, str]:
    """
    Returns (access_token, api_url), refreshing if needed.
    This is the main entry point for all API calls.
    """
    env = load_env()
    tokens = load_tokens()

    if is_token_expired(tokens):
        tokens = refresh_tokens(tokens, env)

    access_token = tokens.get("access_token")
    api_url = tokens.get("api_url", "https://api-us.zoom.us")

    if not access_token:
        raise ValueError("No access_token in zoom_tokens.json after refresh")

    return access_token, api_url


# ---------------------------------------------------------------------------
# API request helper
# ---------------------------------------------------------------------------
def zoom_get(endpoint: str, params: dict = None) -> dict:
    """
    Make an authenticated GET request to the Zoom API.
    Handles token refresh on 401 automatically (one retry).
    """
    access_token, api_url = get_valid_token()

    url = f"{api_url}/v2{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()

        if e.code == 401:
            # Token expired mid-session — force refresh and retry once
            print("[zoom_api] Got 401 — forcing token refresh and retrying...", file=sys.stderr)
            env = load_env()
            tokens = load_tokens()
            tokens = refresh_tokens(tokens, env)
            new_token = tokens["access_token"]
            new_api = tokens.get("api_url", api_url)

            url2 = f"{new_api}/v2{endpoint}"
            if params:
                url2 += "?" + urllib.parse.urlencode(params)
            req2 = urllib.request.Request(
                url2,
                headers={
                    "Authorization": f"Bearer {new_token}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req2, timeout=30) as resp2:
                return json.loads(resp2.read())

        if e.code in (400, 403):
            scope_error = "scope" in body_text.lower() or "access token" in body_text.lower()
            if scope_error:
                raise PermissionError(
                    f"Zoom API scope error on {endpoint}\n"
                    f"Response: {body_text}\n\n"
                    "SCOPE ISSUE: The Zoom OAuth app lacks recording scopes.\n"
                    "Required scopes (Zoom's exact names):\n"
                    "  cloud_recording:read:list_user_recordings\n"
                    "  cloud_recording:read:list_user_recordings:admin\n\n"
                    "Fix:\n"
                    "  1. Go to: https://marketplace.zoom.us/develop/apps\n"
                    "  2. Select your OAuth app → Scopes tab\n"
                    "  3. Search for 'cloud_recording' and add both scopes above\n"
                    "  4. Re-authorize via OAuth flow to get new tokens with recording scope\n"
                    "     (The refresh token you have won't gain new scopes without re-auth)\n"
                    "  5. New tokens auto-save to .credentials/zoom_tokens.json\n\n"
                    "Current token scopes:\n"
                    f"  {load_tokens().get('scope', 'unknown')}"
                )
            raise RuntimeError(f"Zoom API error {e.code} on {endpoint}:\n{body_text}")

        raise RuntimeError(f"Zoom API error {e.code} on {endpoint}:\n{body_text}")


# ---------------------------------------------------------------------------
# Recording list
# ---------------------------------------------------------------------------
def list_recordings(
    user_id: str = "me",
    from_date: str = None,
    to_date: str = None,
    page_size: int = 30,
    topic_filter: str = None,
) -> list[dict]:
    """
    List cloud recordings for a user.

    Args:
        user_id: Zoom user ID or 'me' for the authorized user
        from_date: YYYY-MM-DD (defaults to 7 days ago)
        to_date: YYYY-MM-DD (defaults to today)
        page_size: Number of results per page (max 300)
        topic_filter: If set, only return recordings whose topic contains this string

    Returns:
        List of meeting recording dicts, each containing:
          - id: meeting UUID
          - topic: meeting name
          - start_time: ISO8601 timestamp
          - duration: minutes
          - recording_files: list of file dicts
          - total_size: bytes
    """
    if not from_date:
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")

    params = {
        "from": from_date,
        "to": to_date,
        "page_size": min(page_size, 300),
    }

    print(f"[zoom_api] Listing recordings from {from_date} to {to_date}...", file=sys.stderr)

    data = zoom_get(f"/users/{user_id}/recordings", params)
    meetings = data.get("meetings", [])

    if topic_filter:
        meetings = [
            m for m in meetings
            if topic_filter.lower() in m.get("topic", "").lower()
        ]
        print(f"[zoom_api] Topic filter '{topic_filter}' matched {len(meetings)} recording(s)", file=sys.stderr)

    return meetings


def find_brainiac_recording(
    from_date: str = None,
    to_date: str = None,
) -> dict | None:
    """
    Find the most recent Brainiac Mastermind Training recording.
    Returns the meeting dict or None if not found.
    """
    recordings = list_recordings(
        from_date=from_date,
        to_date=to_date,
        topic_filter="Brainiac",
    )

    if not recordings:
        return None

    # Sort by start_time descending, return most recent
    recordings.sort(key=lambda m: m.get("start_time", ""), reverse=True)
    return recordings[0]


# ---------------------------------------------------------------------------
# Download recording
# ---------------------------------------------------------------------------
def download_recording(
    recording: dict,
    output_dir: Path,
    file_types: list[str] = None,
) -> dict[str, Path]:
    """
    Download recording files from a meeting recording dict.

    Args:
        recording: Meeting dict from list_recordings()
        output_dir: Directory to save files into
        file_types: List of file types to download.
                    Default: ["MP4", "TRANSCRIPT", "CHAT"]
                    Zoom file types: MP4, M4A, TRANSCRIPT, CHAT, TIMELINE, CC

    Returns:
        Dict mapping file_type -> local Path for each downloaded file.

    Notes:
        - Zoom download URLs require the access token as a query param OR header
        - Video files can be several GB — this streams in chunks to avoid RAM issues
        - Zoom rate limits downloads, so we add small delays between files
    """
    if file_types is None:
        file_types = ["MP4", "TRANSCRIPT", "CHAT"]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    access_token, _ = get_valid_token()
    topic = recording.get("topic", "recording").replace("/", "-").replace(" ", "_")[:60]
    meeting_start = recording.get("start_time", "")[:10]  # YYYY-MM-DD

    downloaded = {}
    recording_files = recording.get("recording_files", [])

    for rf in recording_files:
        rtype = rf.get("recording_type", "").upper()
        file_ext = rf.get("file_extension", "mp4").lower()
        file_type_label = rf.get("file_type", "").upper()
        status = rf.get("status", "")

        # Zoom uses both file_type and recording_type — match against both
        matched = (rtype in file_types) or (file_type_label in file_types)
        if not matched:
            continue

        if status != "completed":
            print(f"[zoom_api] Skipping {rtype} — status: {status}", file=sys.stderr)
            continue

        download_url = rf.get("download_url")
        if not download_url:
            print(f"[zoom_api] No download URL for {rtype}", file=sys.stderr)
            continue

        # Construct filename
        suffix = f"_{rf.get('id', '')[:8]}" if len(recording_files) > 3 else ""
        filename = f"{meeting_start}_{topic}{suffix}.{file_ext}"
        out_path = output_dir / filename

        print(f"[zoom_api] Downloading {rtype} → {out_path} ...", file=sys.stderr)

        # Zoom accepts token as query param OR Authorization header
        # Using query param because some download URLs redirect and headers may not follow
        url_with_token = f"{download_url}?access_token={access_token}"

        req = urllib.request.Request(url_with_token)

        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded_bytes = 0
                chunk_size = 8 * 1024 * 1024  # 8 MB chunks

                with open(out_path, "wb") as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded_bytes += len(chunk)
                        if total:
                            pct = downloaded_bytes / total * 100
                            print(
                                f"\r[zoom_api]   {pct:.1f}% ({downloaded_bytes // 1024 // 1024}MB / {total // 1024 // 1024}MB)",
                                end="",
                                file=sys.stderr,
                            )

            print(f"\n[zoom_api] Downloaded: {out_path} ({out_path.stat().st_size // 1024 // 1024}MB)", file=sys.stderr)
            downloaded[rtype] = out_path

        except urllib.error.HTTPError as e:
            print(f"[zoom_api] Download failed for {rtype}: HTTP {e.code}", file=sys.stderr)

        # Small delay between downloads — Zoom rate limits
        time.sleep(1)

    return downloaded


def get_transcript(recording: dict) -> str | None:
    """
    Extract transcript text from a recording dict.
    Zoom provides VTT-format transcripts. We return plain text.

    Returns transcript text or None if no transcript available.
    """
    access_token, _ = get_valid_token()
    recording_files = recording.get("recording_files", [])

    for rf in recording_files:
        file_type = rf.get("file_type", "").upper()
        recording_type = rf.get("recording_type", "").upper()

        if file_type not in ("TRANSCRIPT",) and recording_type not in ("TRANSCRIPT",):
            continue

        download_url = rf.get("download_url")
        if not download_url:
            continue

        url_with_token = f"{download_url}?access_token={access_token}"
        req = urllib.request.Request(url_with_token)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            # Parse VTT → plain text (strip timestamps and headers)
            return _vtt_to_text(raw)
        except Exception as e:
            print(f"[zoom_api] Transcript download failed: {e}", file=sys.stderr)

    return None


def _vtt_to_text(vtt: str) -> str:
    """Convert WebVTT transcript to clean plain text."""
    lines = vtt.splitlines()
    text_lines = []
    skip_next = False

    for line in lines:
        line = line.strip()
        # Skip header
        if line == "WEBVTT":
            continue
        # Skip cue identifiers (numeric)
        if line.isdigit():
            continue
        # Skip timestamps (contain -->)
        if "-->" in line:
            skip_next = False
            continue
        # Skip speaker labels on their own line (e.g. "<v Jared>")
        if line.startswith("<v ") and line.endswith(">"):
            continue
        # Skip empty lines
        if not line:
            continue
        # Remove inline speaker tags: <v Speaker Name>text</v>
        import re
        line = re.sub(r"<v [^>]+>", "", line)
        line = re.sub(r"</v>", "", line)
        # Remove timestamp tags: <00:01:23.456>
        line = re.sub(r"<[\d:.]+>", "", line)
        line = line.strip()
        if line:
            text_lines.append(line)

    return "\n".join(text_lines)


# ---------------------------------------------------------------------------
# Convenience: recording metadata summary
# ---------------------------------------------------------------------------
def recording_summary(recording: dict) -> str:
    """Return a human-readable summary of a recording for display/logging."""
    topic = recording.get("topic", "Unknown")
    start = recording.get("start_time", "Unknown")[:19].replace("T", " ")
    duration = recording.get("duration", 0)
    total_size_mb = recording.get("total_size", 0) // 1024 // 1024
    meeting_id = recording.get("id", "Unknown")

    files = recording.get("recording_files", [])
    file_types = [f.get("file_type", f.get("recording_type", "?")) for f in files]

    return (
        f"Topic:     {topic}\n"
        f"ID:        {meeting_id}\n"
        f"Started:   {start} UTC\n"
        f"Duration:  {duration} minutes\n"
        f"Total:     {total_size_mb} MB\n"
        f"Files:     {', '.join(file_types)}"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Zoom API helper for PureBrain Brainiac pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    # --list
    list_parser = subparsers.add_parser("list", help="List cloud recordings")
    list_parser.add_argument("--from", dest="from_date", help="Start date YYYY-MM-DD (default: 7 days ago)")
    list_parser.add_argument("--to", dest="to_date", help="End date YYYY-MM-DD (default: today)")
    list_parser.add_argument("--filter", help="Topic substring filter (e.g. 'Brainiac')")
    list_parser.add_argument("--user", default="me", help="Zoom user ID or 'me'")
    list_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # --refresh
    subparsers.add_parser("refresh", help="Force token refresh")

    # --download
    dl_parser = subparsers.add_parser("download", help="Download a recording by meeting ID/UUID")
    dl_parser.add_argument("meeting_id", help="Meeting UUID from list output")
    dl_parser.add_argument("--out", default="/tmp/zoom-downloads", help="Output directory")
    dl_parser.add_argument(
        "--types",
        default="MP4,TRANSCRIPT",
        help="File types to download, comma-separated (MP4,TRANSCRIPT,CHAT)",
    )

    # --find-brainiac
    fb_parser = subparsers.add_parser("find-brainiac", help="Find latest Brainiac recording")
    fb_parser.add_argument("--from", dest="from_date", help="Start date YYYY-MM-DD")
    fb_parser.add_argument("--to", dest="to_date", help="End date YYYY-MM-DD")

    # --status
    subparsers.add_parser("status", help="Show token status")

    args = parser.parse_args()

    if args.command == "refresh":
        env = load_env()
        tokens = load_tokens()
        tokens = refresh_tokens(tokens, env)
        print(f"Token refreshed. Scope: {tokens.get('scope', 'N/A')}")

    elif args.command == "status":
        tokens = load_tokens()
        saved = tokens.get("saved_at", "unknown")
        expired = is_token_expired(tokens)
        scope = tokens.get("scope", "unknown")
        has_recording = "cloud_recording:read:list_user_recordings" in scope
        print(f"Saved at:          {saved}")
        print(f"Token expired:     {expired}")
        print(f"Has recording scope: {has_recording}")
        print(f"Scope: {scope}")
        if not has_recording:
            print("\nWARNING: Token scope does not include recording access.")
            print("Required scopes:")
            print("  cloud_recording:read:list_user_recordings")
            print("  cloud_recording:read:list_user_recordings:admin")
            print("\nFix:")
            print("  1. https://marketplace.zoom.us/develop/apps → Your App → Scopes")
            print("  2. Add both cloud_recording scopes above")
            print("  3. Re-run OAuth flow to get new refresh token with recording scope")

    elif args.command == "list":
        try:
            meetings = list_recordings(
                user_id=args.user,
                from_date=args.from_date,
                to_date=args.to_date,
                topic_filter=args.filter,
            )
            if getattr(args, "json", False):
                print(json.dumps(meetings, indent=2))
            else:
                if not meetings:
                    print("No recordings found.")
                else:
                    print(f"\nFound {len(meetings)} recording(s):\n")
                    for i, m in enumerate(meetings, 1):
                        print(f"--- [{i}] ---")
                        print(recording_summary(m))
                        print()
        except PermissionError as e:
            print(f"PERMISSION ERROR:\n{e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "find-brainiac":
        try:
            rec = find_brainiac_recording(
                from_date=getattr(args, "from_date", None),
                to_date=getattr(args, "to_date", None),
            )
            if rec:
                print("Found Brainiac recording:\n")
                print(recording_summary(rec))
                print(f"\nFull JSON saved to /tmp/brainiac_recording.json")
                with open("/tmp/brainiac_recording.json", "w") as f:
                    json.dump(rec, f, indent=2)
            else:
                print("No Brainiac recording found in date range.")
                print("Try extending the --from date or check the recording is in the cloud.")
        except PermissionError as e:
            print(f"PERMISSION ERROR:\n{e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "download":
        # Look up the meeting by ID
        try:
            data = zoom_get(f"/meetings/{args.meeting_id}/recordings")
            file_types = [t.strip().upper() for t in args.types.split(",")]
            downloaded = download_recording(data, Path(args.out), file_types)
            print(f"\nDownloaded {len(downloaded)} file(s):")
            for ftype, path in downloaded.items():
                print(f"  {ftype}: {path}")
        except PermissionError as e:
            print(f"PERMISSION ERROR:\n{e}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
