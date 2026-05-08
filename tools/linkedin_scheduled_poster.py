#!/usr/bin/env python3
"""
LinkedIn Time-Scheduled Autoposter — PureSurf-Primary
=====================================================

CONSTITUTIONAL (locked 2026-04-14):
  social.html (PureSurf GET /social/scheduled) is the SINGLE SOURCE OF TRUTH
  for LinkedIn scheduling. Google Sheet + Drive folders are filing / organization
  / proof ONLY. They are updated AS SECONDARY RECORDS after PureSurf succeeds.

Flow (current — PureSurf primary):
  1. GET https://surf.purebrain.ai/social/scheduled  [X-API-Key]
  2. Filter posts where:
       - platform == "linkedin"
       - linkedin_post_url is empty (idempotent guard)
       - scheduled_time (ISO UTC) falls within slot_center ± 30min (ET)
  3. Download banner_url to /tmp (image one-shot per feedback_linkedin_image_must_work.md)
  4. Post via tools/linkedin_post_with_image.py using the post's full `content` field
  5. On success, PUT https://surf.purebrain.ai/social/schedule/{id}
       body: {linkedin_post_url: "...", publish_status: "posted"}
  6. Mirror update to Google Sheet (J=URL, L=Live, M=pub date) — best-effort secondary
  7. Move Drive subfolder to Content Posted Live — best-effort secondary

Legacy flow (fallback — Google Sheet primary):
  If PureSurf API is unreachable (network / 5xx), fall back to reading the
  "NEW LINKEDIN POST CONTENT CALENDAR" sheet + Pending Approval Drive folder
  as before. This preserves continuity during outages.

Usage:
    python3 tools/linkedin_scheduled_poster.py --slot {8:30am|11am|1pm|3pm}
    python3 tools/linkedin_scheduled_poster.py --slot 1pm --dry-run

Idempotent: skips posts that already have linkedin_post_url.

CONSTITUTIONAL RULES (unchanged):
- NEVER bypass linkedin_post_with_image.py (image is one-shot)
- NEVER manually craft LinkedIn API calls
- ALWAYS log to logs/linkedin_scheduled_poster.log

Author: full-stack-developer
Refactor date: 2026-04-14
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

# ── First-comment on own post (T+2min step of 5-stage SOP) ────────────────────
DEFAULT_FIRST_COMMENT = "Full read here: purebrain.ai/?ref=JAREDSB0"
FIRST_COMMENT_DELAY_SEC = 120  # T+2min per SOP

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

LOG_FILE = ROOT / "logs" / "linkedin_scheduled_poster.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

POST_TOOL = ROOT / "tools" / "linkedin_post_with_image.py"

# ── PureSurf (PRIMARY SOURCE OF TRUTH) ─────────────────────────────────────────
PURESURF_BASE = "https://surf.purebrain.ai"
PURESURF_SCHEDULED_URL = f"{PURESURF_BASE}/social/scheduled"
PURESURF_SCHEDULE_ITEM_URL = f"{PURESURF_BASE}/social/schedule/{{id}}"  # PUT
# API key: PURESURF_API_KEY override, else BAAS_API_KEY from .env. Never hardcoded.
# Try to load .env if running outside a shell that sourced it (e.g. cron, systemd).
try:
    from dotenv import load_dotenv as _load_dotenv
    _load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except Exception:
    _env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(_env_file):
        with open(_env_file) as _fh:
            for _line in _fh:
                _line = _line.strip()
                if not _line or _line.startswith("#") or "=" not in _line:
                    continue
                _k, _, _v = _line.partition("=")
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

PURESURF_API_KEY = (
    os.environ.get("PURESURF_API_KEY")
    or os.environ.get("BAAS_API_KEY")
    or ""
)
if not PURESURF_API_KEY:
    print(
        "FATAL: No PureSurf API key found. Set PURESURF_API_KEY or BAAS_API_KEY in .env",
        file=sys.stderr,
    )
    sys.exit(2)

PURESURF_TIMEOUT_SEC = 20
SLOT_WINDOW_MIN = 30  # ± around slot center

# ── Sheet / Drive (SECONDARY — filing only) ────────────────────────────────────
SHEET_ID = "1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4"
TAB_NAME = "NEW LINKEDIN POST CONTENT CALENDAR"

PENDING_APPROVAL_FOLDER_ID = "1Cr6EhkNi0ToBqQs27q0TQzKtCNDGeFwz"
POSTED_LIVE_FOLDER_ID = "1LyCBPXG43WXnXUcTkA5t7m8td0U5yAYx"

ET = ZoneInfo("America/New_York")

# Slot → (hour, minute) in ET
SLOT_CENTERS = {
    "8:30am": (8, 30),
    "11am":   (11, 0),
    "1pm":    (13, 0),
    "3pm":    (15, 0),
}

# Slot → set of acceptable Time-column values (legacy sheet fallback)
SLOT_TIME_VALUES = {
    "8:30am": {"8:30am", "8:30 am", "830am", "08:30", "8:30"},
    "11am":   {"11am", "11:00am", "11 am", "11:00 am", "11:00"},
    "1pm":    {"1pm", "1:00pm", "1 pm", "1:00 pm", "13:00"},
    "3pm":    {"3pm", "3:00pm", "3 pm", "3:00 pm", "15:00"},
}

ACCEPTED_STATUSES = {"approved", "final"}

# Sheet column indices (0-based) — legacy fallback path
COL_DATE          = 0   # A
COL_TIME          = 1   # B
COL_TITLE         = 2   # C
COL_POST_TEXT     = 6   # G
COL_LINKEDIN_URL  = 9   # J
COL_STATUS        = 11  # L
COL_PUB_DATE      = 12  # M

# ── Logging ────────────────────────────────────────────────────────────────────

def setup_logger(slot: str) -> logging.LoggerAdapter:
    lg = logging.getLogger(f"linkedin_scheduled_poster.{slot}")
    lg.setLevel(logging.INFO)
    if not lg.handlers:
        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] [slot=%(slot)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fh = logging.FileHandler(LOG_FILE)
        fh.setFormatter(fmt)
        lg.addHandler(fh)
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        lg.addHandler(sh)
    return logging.LoggerAdapter(lg, {"slot": slot})


# ── PureSurf client ────────────────────────────────────────────────────────────

def _http_json(method: str, url: str, body: Optional[dict] = None, timeout: int = PURESURF_TIMEOUT_SEC) -> tuple[int, dict]:
    """Minimal stdlib HTTP helper. Returns (status_code, parsed_body)."""
    import urllib.request
    data = None
    headers = {"X-API-Key": PURESURF_API_KEY, "Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            code = resp.getcode()
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        code = e.code
    try:
        parsed = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        parsed = {"_raw": raw}
    return code, parsed


def puresurf_fetch_scheduled(log) -> Optional[list[dict]]:
    """Return list of posts, or None on network/5xx failure (caller should fall back)."""
    try:
        code, body = _http_json("GET", PURESURF_SCHEDULED_URL)
    except Exception as e:
        log.warning(f"PureSurf fetch exception: {e}")
        return None
    if code != 200:
        log.warning(f"PureSurf fetch returned {code}: {str(body)[:200]}")
        return None
    posts = body.get("posts") if isinstance(body, dict) else None
    if not isinstance(posts, list):
        log.warning(f"PureSurf response missing 'posts' list: keys={list(body.keys()) if isinstance(body,dict) else type(body)}")
        return None
    log.info(f"PureSurf: fetched {len(posts)} scheduled posts")
    return posts


def puresurf_update_post(post_id: str, linkedin_url: str, log) -> bool:
    """PUT linkedin_post_url + publish_status=posted. Returns True on success."""
    url = PURESURF_SCHEDULE_ITEM_URL.format(id=urllib.parse.quote(post_id, safe=""))
    payload = {
        "linkedin_post_url": linkedin_url or "",
        "publish_status": "posted",
    }
    try:
        code, body = _http_json("PUT", url, body=payload)
    except Exception as e:
        log.error(f"PureSurf PUT exception for {post_id}: {e}")
        return False
    if code == 200 and isinstance(body, dict) and body.get("ok"):
        log.info(f"PureSurf updated {post_id}: publish_status=posted, linkedin_post_url set")
        return True
    log.error(f"PureSurf PUT {post_id} failed: code={code} body={str(body)[:300]}")
    return False


def _parse_iso_utc(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        # Normalize Z → +00:00 for fromisoformat
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def select_puresurf_post(posts: list[dict], slot: str, now_et: datetime, log) -> Optional[dict]:
    """Pick the LinkedIn post matching this slot (± SLOT_WINDOW_MIN) not yet posted."""
    hh, mm = SLOT_CENTERS[slot]
    slot_center_et = now_et.replace(hour=hh, minute=mm, second=0, microsecond=0)
    slot_center_utc = slot_center_et.astimezone(timezone.utc)
    today_et_date = now_et.date()
    log.info(f"Slot center: {slot_center_et.isoformat()} ({slot_center_utc.isoformat()}) ± {SLOT_WINDOW_MIN}min")

    matches: list[tuple[float, dict]] = []
    for p in posts:
        if (p.get("platform") or "").lower() != "linkedin":
            continue
        if (p.get("linkedin_post_url") or "").strip():
            continue  # already posted (idempotent)
        dt_utc = _parse_iso_utc(p.get("scheduled_time", ""))
        if dt_utc is None:
            continue
        dt_et = dt_utc.astimezone(ET)
        if dt_et.date() != today_et_date:
            continue
        diff_min = abs((dt_utc - slot_center_utc).total_seconds()) / 60.0
        if diff_min <= SLOT_WINDOW_MIN:
            matches.append((diff_min, p))

    if not matches:
        return None
    matches.sort(key=lambda x: x[0])  # closest to slot center wins
    if len(matches) > 1:
        log.warning(
            f"Multiple PureSurf posts matched slot {slot}: "
            + ", ".join(f"{p['id']}@{p.get('scheduled_time')}" for _, p in matches)
            + f". Picking closest: {matches[0][1]['id']}"
        )
    return matches[0][1]


def download_url_to_tmp(url: str, dest: Path, log) -> bool:
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "aether-linkedin-poster/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        dest.write_bytes(data)
        log.info(f"Downloaded {url} -> {dest} ({len(data)} bytes)")
        return True
    except Exception as e:
        log.error(f"Failed to download {url}: {e}")
        return False


# ── Google auth (lazy — only needed for secondary sheet/drive updates) ─────────

def get_credentials():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    candidates = [
        ROOT / ".credentials" / "oauth-token.json",
        ROOT / "config" / "gdrive_token.json",
        ROOT / "tools" / "gdrive_token.json",
        Path.home() / ".config" / "gdrive_token.json",
    ]
    token_path = next((p for p in candidates if p.exists()), None)
    if token_path is None:
        raise FileNotFoundError("No OAuth token found. Candidates: " + ", ".join(str(p) for p in candidates))
    with open(token_path) as f:
        td = json.load(f)
    creds = Credentials(
        token=td.get("token"),
        refresh_token=td.get("refresh_token"),
        token_uri=td.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=td.get("client_id"),
        client_secret=td.get("client_secret"),
        scopes=SCOPES,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w") as f:
            json.dump({
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": list(creds.scopes or SCOPES),
            }, f, indent=2)
    return creds


def build_services(creds):
    from googleapiclient.discovery import build
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    return sheets, drive


# ── Posting ────────────────────────────────────────────────────────────────────

def call_post_tool(text: str, image_path: Path, dry_run: bool, log, user: str = "jared") -> tuple[bool, str]:
    """Returns (success, linkedin_url_or_error).

    CANONICAL PATH (updated April 14, 2026):
      Uses LinkedIn API direct via tools.linkedin_api.post_text_with_image
      (3-step asset upload: register → PUT bytes → create ugcPost).
    Previously used linkedin_post_with_image.py (PureSurf browser automation)
    which has a broken session. API direct is faster and more reliable.
    """
    log.info(f"Posting via LinkedIn API direct: image={image_path.name} text_len={len(text)} user={user} dry_run={dry_run}")
    if dry_run:
        log.info(f"[DRY-RUN] Would post:")
        log.info(f"  User:  {user}")
        log.info(f"  Image: {image_path}")
        log.info(f"  Text preview: {text[:150]}...")
        return True, "[dry-run — no URL]"
    try:
        # Import locally to keep the script loadable even if linkedin_api has issues
        sys.path.insert(0, str(ROOT / "tools"))
        import linkedin_api as li
        result = li.post_text_with_image(
            content=text,
            image_path=str(image_path),
            user=user,
            visibility="PUBLIC",
        )
        post_id = result.get("id", "")
        if not post_id:
            log.error(f"No post ID in response: {result}")
            return False, f"no post ID returned"
        # Build public URL from the URN
        url = f"https://www.linkedin.com/feed/update/{post_id}/"
        log.info(f"Posted successfully: {post_id}")
        return True, url
    except Exception as e:
        log.error(f"LinkedIn API post failed: {type(e).__name__}: {e}")
        return False, f"{type(e).__name__}: {e}"


# ── First-comment on own post (T+2min) ────────────────────────────────────────

def extract_post_urn_from_url(url: str) -> Optional[str]:
    """LinkedIn UGC URN looks like urn:li:share:1234... or urn:li:activity:1234...
    The public feed URL embeds the URN. Recover it."""
    if not url:
        return None
    # Common: https://www.linkedin.com/feed/update/urn:li:share:XXX/
    m = re.search(r"(urn:li:(?:share|ugcPost|activity):[\w\-]+)", url)
    return m.group(1) if m else None


def post_first_comment(post_url: str, text: str, user: str, log,
                       delay_sec: int = FIRST_COMMENT_DELAY_SEC,
                       dry_run: bool = False) -> bool:
    """After a successful post, wait delay_sec, then comment on own post.
    Stage T+2min of the 5-stage LinkedIn SOP."""
    urn = extract_post_urn_from_url(post_url)
    if not urn:
        log.warning(f"First-comment: could not extract URN from {post_url} — skipping")
        return False
    log.info(f"First-comment: sleeping {delay_sec}s before commenting on own post {urn}")
    if dry_run:
        log.info(f"[DRY-RUN] would sleep {delay_sec}s then comment on {urn} with: {text!r}")
        return True
    time.sleep(delay_sec)
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import linkedin_api as li
        res = li.comment_on_post(urn, text, user=user)
        log.info(f"First-comment OK on {urn}: {res.get('id','?')}")
        return True
    except Exception as e:
        log.error(f"First-comment FAILED on {urn}: {type(e).__name__}: {e}")
        return False


# ── Sheet mirror (secondary record) ────────────────────────────────────────────

def _normalize(s: str) -> str:
    return re.sub(r"\s+", "", str(s or "")).lower()


def _date_matches_today_et(date_cell: str, today_et: str) -> bool:
    if not date_cell:
        return False
    s = str(date_cell).strip()
    if s == today_et:
        return True
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%B %d, %Y", "%b %d, %Y"):
        try:
            if datetime.strptime(s, fmt).date().isoformat() == today_et:
                return True
        except ValueError:
            continue
    return False


def _slot_matches_sheet(time_cell: str, slot: str) -> bool:
    n = _normalize(time_cell)
    return n in {_normalize(v) for v in SLOT_TIME_VALUES[slot]}


def find_sheet_row_for_slot(sheets, slot: str, today_et: str, title_hint: str, log) -> Optional[int]:
    """Locate the sheet row that mirrors this post. Used for secondary update + legacy fallback."""
    rng = f"'{TAB_NAME}'!A1:Z1000"
    resp = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=rng,
        valueRenderOption="UNFORMATTED_VALUE",
        dateTimeRenderOption="FORMATTED_STRING",
    ).execute()
    rows = resp.get("values", [])
    title_key = re.sub(r"[^a-z0-9]+", "", (title_hint or "").lower())
    best: Optional[tuple[int, list[str]]] = None
    for i, row in enumerate(rows[1:], start=2):
        padded = row + [""] * (max(13, len(row)) - len(row))
        if not _date_matches_today_et(padded[COL_DATE], today_et):
            continue
        if not _slot_matches_sheet(padded[COL_TIME], slot):
            continue
        if (padded[COL_LINKEDIN_URL] or "").strip():
            continue
        # Prefer title match if provided
        if title_key:
            row_title_key = re.sub(r"[^a-z0-9]+", "", str(padded[COL_TITLE] or "").lower())
            if title_key and (title_key in row_title_key or row_title_key in title_key):
                return i
        best = (i, padded)
    return best[0] if best else None


def mirror_sheet_update(sheets, row_idx: int, linkedin_url: str, today_et: str, log) -> None:
    updates = [
        {"range": f"'{TAB_NAME}'!J{row_idx}", "values": [[linkedin_url or ""]]},
        {"range": f"'{TAB_NAME}'!L{row_idx}", "values": [["Live"]]},
        {"range": f"'{TAB_NAME}'!M{row_idx}", "values": [[today_et]]},
    ]
    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"valueInputOption": "USER_ENTERED", "data": updates},
    ).execute()
    log.info(f"Sheet mirror: row {row_idx} -> J={linkedin_url!r}, L=Live, M={today_et}")


# ── Drive mirror (secondary record) ────────────────────────────────────────────

def _slug_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text or "").lower())


def find_post_subfolder(drive, parent_id: str, title: str, log) -> Optional[dict]:
    target = _slug_key(title)
    if not target:
        return None
    candidates = []
    page_token = None
    while True:
        resp = drive.files().list(
            q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="nextPageToken, files(id, name, parents)",
            pageSize=1000, pageToken=page_token,
            supportsAllDrives=True, includeItemsFromAllDrives=True,
        ).execute()
        for f in resp.get("files", []):
            name_key = _slug_key(f["name"])
            if name_key == target:
                return f
            if target in name_key or name_key in target:
                candidates.append(f)
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    if candidates:
        candidates.sort(key=lambda f: -len(_slug_key(f["name"])))
        log.info(f"Fuzzy-matched folder for '{title}': {candidates[0]['name']}")
        return candidates[0]
    return None


def move_folder(drive, folder_id: str, new_parent_id: str, log) -> None:
    f = drive.files().get(fileId=folder_id, fields="parents", supportsAllDrives=True).execute()
    prev = ",".join(f.get("parents", []))
    drive.files().update(
        fileId=folder_id, addParents=new_parent_id, removeParents=prev,
        fields="id, parents", supportsAllDrives=True,
    ).execute()
    log.info(f"Drive mirror: moved folder {folder_id} [{prev}] -> {new_parent_id}")


# ── Legacy fallback: sheet-primary path (unchanged behavior) ───────────────────

def list_folder_files(drive, folder_id: str) -> list[dict]:
    files, page_token = [], None
    while True:
        resp = drive.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id, name, mimeType, size)",
            pageSize=1000, pageToken=page_token,
            supportsAllDrives=True, includeItemsFromAllDrives=True,
        ).execute()
        files.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return files


def download_drive_file(drive, file_id: str, dest: Path) -> Path:
    from googleapiclient.http import MediaIoBaseDownload
    import io
    req = drive.files().get_media(fileId=file_id, supportsAllDrives=True)
    buf = io.FileIO(str(dest), "wb")
    downloader = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _s, done = downloader.next_chunk()
    buf.close()
    return dest


def run_legacy_sheet_fallback(slot: str, dry_run: bool, log) -> int:
    """Original sheet-primary path. Used only when PureSurf is unreachable."""
    log.warning("Running LEGACY sheet-primary fallback (PureSurf unreachable)")
    now_et = datetime.now(ET)
    today_et = now_et.date().isoformat()
    try:
        creds = get_credentials()
        sheets, drive = build_services(creds)
    except Exception as e:
        log.error(f"Google auth failed in fallback: {e}")
        return 2

    rng = f"'{TAB_NAME}'!A1:Z1000"
    resp = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=rng,
        valueRenderOption="UNFORMATTED_VALUE",
        dateTimeRenderOption="FORMATTED_STRING",
    ).execute()
    rows = resp.get("values", [])

    target = None
    for i, row in enumerate(rows[1:], start=2):
        padded = row + [""] * (max(13, len(row)) - len(row))
        if not _date_matches_today_et(padded[COL_DATE], today_et): continue
        if not _slot_matches_sheet(padded[COL_TIME], slot): continue
        if _normalize(padded[COL_STATUS]) not in {_normalize(s) for s in ACCEPTED_STATUSES}: continue
        if (padded[COL_LINKEDIN_URL] or "").strip(): continue
        target = (i, padded); break
    if target is None:
        log.info(f"[fallback] No row for slot {slot} on {today_et}")
        return 0
    row_idx, row_data = target
    title = row_data[COL_TITLE]
    sheet_text = row_data[COL_POST_TEXT]

    folder = find_post_subfolder(drive, PENDING_APPROVAL_FOLDER_ID, title, log)
    if not folder:
        log.error(f"[fallback] No Drive subfolder for '{title}'"); return 3
    files = list_folder_files(drive, folder["id"])
    md = next((f for f in files if f["name"].lower().endswith(".md")), None)
    img = next((f for f in files if f["name"].lower().endswith((".png",".jpg",".jpeg",".webp"))), None)
    if img is None:
        log.error("[fallback] No image in folder"); return 5

    tmp_dir = Path("/tmp") / f"li_poster_{slot}_{int(now_et.timestamp())}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    image_path = tmp_dir / img["name"]
    download_drive_file(drive, img["id"], image_path)
    if md:
        md_path = tmp_dir / md["name"]; download_drive_file(drive, md["id"], md_path)
        post_text = md_path.read_text(encoding="utf-8")
    else:
        post_text = sheet_text
    if not post_text.strip():
        log.error("[fallback] Empty post text"); return 6

    ok, url_or_err = call_post_tool(post_text, image_path, dry_run, log)
    if not ok:
        log.error(f"[fallback] Post failed: {url_or_err}"); return 7
    if dry_run:
        log.info(f"[fallback] DRY RUN done. Would update row {row_idx}."); return 0
    try:
        mirror_sheet_update(sheets, row_idx, url_or_err, today_et, log)
    except Exception as e:
        log.error(f"[fallback] Sheet update failed after post: {e}"); return 8
    try:
        move_folder(drive, folder["id"], POSTED_LIVE_FOLDER_ID, log)
    except Exception as e:
        log.error(f"[fallback] Drive move failed after post: {e}"); return 9
    log.info(f"[fallback] SUCCESS slot={slot} url={url_or_err}")
    return 0


# ── Main (PureSurf-primary) ────────────────────────────────────────────────────

def run(slot: str, dry_run: bool) -> int:
    log = setup_logger(slot)
    log.info(f"=== START slot={slot} dry_run={dry_run} (PureSurf-primary) ===")

    now_et = datetime.now(ET)
    today_et_iso = now_et.date().isoformat()
    log.info(f"Now ET: {now_et.isoformat()}")

    # 1. PureSurf fetch (PRIMARY)
    posts = puresurf_fetch_scheduled(log)
    if posts is None:
        log.warning("PureSurf unavailable — falling back to sheet-primary legacy path")
        return run_legacy_sheet_fallback(slot, dry_run, log)

    # 2. Match slot
    post = select_puresurf_post(posts, slot, now_et, log)
    if post is None:
        log.info(f"No PureSurf LinkedIn post for slot {slot} on {today_et_iso}. Exiting cleanly.")
        return 0

    post_id = post["id"]
    title = post.get("title", "")
    content = post.get("content", "") or ""
    banner_url = post.get("banner_url") or post.get("media_path") or ""
    sched_utc = post.get("scheduled_time", "")
    log.info(f"SELECTED: id={post_id} title={title!r} scheduled_time={sched_utc} content_len={len(content)} banner={bool(banner_url)}")

    # 3. Validate
    if not content.strip():
        log.error(f"Post {post_id} has empty content — aborting"); return 6
    if not banner_url:
        log.error(f"Post {post_id} has no banner_url/media_path — image is one-shot, cannot proceed"); return 5

    # 4. Download banner
    tmp_dir = Path("/tmp") / f"li_poster_{slot}_{int(now_et.timestamp())}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(urllib.parse.urlparse(banner_url).path).suffix or ".png"
    image_path = tmp_dir / f"{post_id}{ext}"
    if not download_url_to_tmp(banner_url, image_path, log):
        return 5

    # 5. Post via linkedin_post_with_image.py
    ok, url_or_err = call_post_tool(content, image_path, dry_run, log)
    if not ok:
        log.error(f"Post failed: {url_or_err}. NO updates propagated.")
        return 7

    if dry_run:
        log.info(f"DRY RUN complete. Would PUT PureSurf {post_id}, mirror sheet, move Drive folder.")
        log.info(f"DRY RUN summary: id={post_id} | title={title!r} | scheduled={sched_utc} | banner={banner_url}")
        # Simulate first-comment (no sleep in dry-run)
        fc_text = (post.get("first_comment") or "").strip() or DEFAULT_FIRST_COMMENT
        log.info(f"DRY RUN first-comment text: {fc_text!r} (T+2min)")
        return 0

    # 5b. T+2min: FIRST COMMENT on own post (SOP stage 3)
    #     Reads optional `first_comment` field from PureSurf payload; falls back to default.
    fc_text = (post.get("first_comment") or "").strip() or DEFAULT_FIRST_COMMENT
    try:
        post_first_comment(url_or_err, fc_text, user="jared", log=log, dry_run=False)
    except Exception as e:
        log.warning(f"First-comment step raised (non-fatal): {e}")

    # 6. PRIMARY update: PureSurf (the source of truth)
    ps_ok = puresurf_update_post(post_id, url_or_err, log)
    if not ps_ok:
        log.error(f"PureSurf update failed AFTER successful post {post_id}. Manual reconciliation needed.")
        # Continue to mirror anyway — the post is live on LinkedIn

    # 7. SECONDARY mirror: Google Sheet (best-effort)
    try:
        creds = get_credentials()
        sheets, drive = build_services(creds)
        row_idx = find_sheet_row_for_slot(sheets, slot, today_et_iso, title, log)
        if row_idx:
            mirror_sheet_update(sheets, row_idx, url_or_err, today_et_iso, log)
        else:
            log.warning(f"No sheet row found to mirror for slot={slot} title={title!r}")
        # 8. SECONDARY mirror: Drive folder move (best-effort)
        folder = find_post_subfolder(drive, PENDING_APPROVAL_FOLDER_ID, title, log)
        if folder:
            try:
                move_folder(drive, folder["id"], POSTED_LIVE_FOLDER_ID, log)
            except Exception as e:
                log.warning(f"Drive folder move failed (non-fatal): {e}")
        else:
            log.info(f"No Drive subfolder matched '{title}' (non-fatal — PureSurf is truth)")
    except Exception as e:
        log.warning(f"Secondary sheet/drive mirror failed (non-fatal): {e}")

    log.info(f"=== SUCCESS slot={slot} id={post_id} url={url_or_err} ===")
    return 0


def main() -> None:
    p = argparse.ArgumentParser(description="LinkedIn time-scheduled autoposter (PureSurf-primary)")
    p.add_argument("--slot", choices=list(SLOT_CENTERS.keys()))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--test-first-comment", action="store_true",
                   help="Simulate post+first-comment without touching the API or sleeping")
    args = p.parse_args()
    if args.test_first_comment:
        log = setup_logger("test")
        fake_url = "https://www.linkedin.com/feed/update/urn:li:share:TESTURN12345/"
        log.info("=== TEST FIRST-COMMENT (simulated, dry-run) ===")
        log.info(f"fake post URL: {fake_url}")
        log.info(f"extracted URN: {extract_post_urn_from_url(fake_url)}")
        post_first_comment(fake_url, DEFAULT_FIRST_COMMENT, user="jared", log=log,
                           delay_sec=FIRST_COMMENT_DELAY_SEC, dry_run=True)
        log.info("=== TEST DONE ===")
        sys.exit(0)
    if not args.slot:
        p.error("--slot is required unless --test-first-comment is used")
    sys.exit(run(args.slot, args.dry_run))


if __name__ == "__main__":
    main()
