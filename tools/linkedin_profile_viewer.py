#!/usr/bin/env python3
"""
LinkedIn Profile Viewer — Passive Growth Engine
================================================
Visits LinkedIn profiles of Premium ICP-matched prospects to trigger
return visits to Jared's profile. ~50% return visit rate on Premium accounts.

Usage:
  python3 tools/linkedin_profile_viewer.py [--batch morning|afternoon|evening|all]
  python3 tools/linkedin_profile_viewer.py --discover  # Find new profiles
  python3 tools/linkedin_profile_viewer.py --dry-run   # Preview without visiting

Architecture:
  1. Reads "Profile Views" tab from Google Sheets
  2. Filters for Premium profiles not visited in 7 days
  3. Navigates to each profile via PureSurf (jared-linkedin-fresh)
  4. Updates Google Sheet with visit timestamp
  5. Logs everything

PureSurf Integration:
  Uses surf.purebrain.ai API with jared-linkedin-fresh browser profile.
  Residential proxy always. Human-like timing (45-75s between visits).

BOOP Schedule:
  Morning:   9:00 AM ET  — 30 profiles
  Afternoon: 2:00 PM ET  — 30 profiles
  Evening:   6:00 PM ET  — 20 profiles
"""

import os
import sys
import json
import time
import random
import logging
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# -- Configuration ----------------------------------------------------------

CIV_ROOT = Path("/home/jared/projects/AI-CIV/aether")
LOG_DIR = CIV_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

SPREADSHEET_ID = "1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4"
SHEET_TAB = "Profile Views"

PURESURF_BASE = "https://surf.purebrain.ai"
PURESURF_KEY_JARED = "WtHJY1zr0HuP4NmcBNMUSGXlM2kxIeibDDmY-btXSHs"
LINKEDIN_PROFILE = "jared-linkedin-fresh"

# Batch sizes
BATCH_SIZES = {
    "morning": 30,
    "afternoon": 30,
    "evening": 20,
}

# Rate limiting
MIN_WAIT_SECONDS = 45    # Minimum wait between profile visits
MAX_WAIT_SECONDS = 75    # Maximum wait between profile visits
VIEW_DWELL_MIN = 3       # Minimum seconds on profile page
VIEW_DWELL_MAX = 6       # Maximum seconds on profile page
MAX_DAILY_VISITS = 100   # Hard cap per day
REVISIT_COOLDOWN_DAYS = 7  # Don't revisit within this window

# Priority order for ICP tiers
ICP_PRIORITY = ["Primary", "Secondary", "Tertiary", "Wildcard"]

# -- Logging ----------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "linkedin_profile_viewer.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("linkedin-profile-viewer")

# -- Google Sheets ----------------------------------------------------------

def get_sheets_service():
    """Get authenticated Google Sheets service."""
    try:
        sys.path.insert(0, str(CIV_ROOT / "tools"))
        from gdrive_manager import GDriveManager
        gm = GDriveManager()
        from googleapiclient.discovery import build
        creds = gm._get_oauth_credentials()
        return build('sheets', 'v4', credentials=creds)
    except Exception as e:
        log.error(f"Failed to get Sheets service: {e}")
        raise


def read_profile_list(sheets_service):
    """Read all profiles from the Profile Views tab."""
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{SHEET_TAB}'!A2:L1000"
        ).execute()
        rows = result.get('values', [])
        profiles = []
        for i, row in enumerate(rows):
            # Pad row to 12 columns
            while len(row) < 12:
                row.append("")
            profiles.append({
                "row_index": i + 2,  # 1-indexed, skip header
                "url": row[0].strip(),
                "name": row[1].strip(),
                "title": row[2].strip(),
                "company": row[3].strip(),
                "followers": row[4].strip(),
                "premium": row[5].strip().upper(),
                "icp_match": row[6].strip(),
                "last_visited": row[7].strip(),
                "visit_count": int(row[8]) if row[8].strip().isdigit() else 0,
                "return_visit": row[9].strip(),
                "became_connection": row[10].strip(),
                "notes": row[11].strip(),
            })
        return profiles
    except Exception as e:
        log.error(f"Failed to read profile list: {e}")
        return []


def update_visit(sheets_service, row_index, visit_count):
    """Update the Last Visited and Visit Count for a profile."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{SHEET_TAB}'!H{row_index}:I{row_index}",
            valueInputOption="RAW",
            body={"values": [[today, visit_count]]}
        ).execute()
    except Exception as e:
        log.error(f"Failed to update row {row_index}: {e}")


def get_daily_visit_count(profiles):
    """Count how many profiles were visited today."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return sum(1 for p in profiles if p["last_visited"] == today)

# -- Profile Selection ------------------------------------------------------

def select_profiles(profiles, batch_size):
    """Select profiles for this batch based on priority and cooldown."""
    now = datetime.now(timezone.utc)
    cooldown_cutoff = (now - timedelta(days=REVISIT_COOLDOWN_DAYS)).strftime("%Y-%m-%d")
    today = now.strftime("%Y-%m-%d")

    eligible = []
    for p in profiles:
        # Must be Premium
        if p["premium"] != "YES":
            continue
        # Must have a URL
        if not p["url"] or not p["url"].startswith("http"):
            # Try to fix common issue
            if p["url"] and "linkedin.com" in p["url"]:
                p["url"] = "https://" + p["url"]
            else:
                continue
        # Must not have been visited today
        if p["last_visited"] == today:
            continue
        # Must not have been visited within cooldown window
        if p["last_visited"] and p["last_visited"] > cooldown_cutoff:
            continue
        eligible.append(p)

    # Sort by ICP priority, then by least-visited
    def sort_key(p):
        tier_index = ICP_PRIORITY.index(p["icp_match"]) if p["icp_match"] in ICP_PRIORITY else 99
        return (tier_index, p["visit_count"])

    eligible.sort(key=sort_key)

    # Take batch_size profiles
    selected = eligible[:batch_size]
    log.info(f"Selected {len(selected)} profiles from {len(eligible)} eligible (batch size: {batch_size})")
    return selected

# -- PureSurf Integration --------------------------------------------------

def create_puresurf_session():
    """Create a PureSurf browser session with jared-linkedin-fresh profile."""
    import urllib.request
    import urllib.error

    url = f"{PURESURF_BASE}/sessions"
    headers = {
        "X-API-Key": PURESURF_KEY_JARED,
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "profile": LINKEDIN_PROFILE,
        "proxy_provider": "floppydata",
        "device": "macbook"
    }).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            session_id = result.get("session_id") or result.get("id")
            log.info(f"PureSurf session created: {session_id}")
            return session_id
    except urllib.error.HTTPError as e:
        log.error(f"PureSurf session creation failed: {e.code} {e.read().decode()}")
        return None
    except Exception as e:
        log.error(f"PureSurf session creation failed: {e}")
        return None


def navigate_to_profile(session_id, profile_url):
    """Navigate PureSurf session to a LinkedIn profile."""
    import urllib.request
    import urllib.error

    url = f"{PURESURF_BASE}/sessions/{session_id}/navigate"
    headers = {
        "X-API-Key": PURESURF_KEY_JARED,
        "Content-Type": "application/json"
    }
    data = json.dumps({"url": profile_url}).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return True
    except Exception as e:
        log.error(f"Navigation failed for {profile_url}: {e}")
        return False


def close_puresurf_session(session_id):
    """Close a PureSurf browser session."""
    import urllib.request
    import urllib.error

    url = f"{PURESURF_BASE}/sessions/{session_id}"
    headers = {"X-API-Key": PURESURF_KEY_JARED}

    req = urllib.request.Request(url, headers=headers, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            log.info(f"PureSurf session {session_id} closed")
    except Exception as e:
        log.warning(f"Failed to close PureSurf session: {e}")

# -- Main Execution ---------------------------------------------------------

def run_batch(batch_name, dry_run=False):
    """Run a single viewing batch."""
    batch_size = BATCH_SIZES.get(batch_name, 30)
    log.info(f"=== Starting {batch_name} batch ({batch_size} profiles) ===")

    sheets = get_sheets_service()
    profiles = read_profile_list(sheets)

    if not profiles:
        log.warning("No profiles found in spreadsheet. Please populate the Profile Views tab.")
        return 0

    # Check daily cap
    daily_count = get_daily_visit_count(profiles)
    remaining_today = MAX_DAILY_VISITS - daily_count
    if remaining_today <= 0:
        log.info(f"Daily limit reached ({daily_count}/{MAX_DAILY_VISITS}). Skipping batch.")
        return 0

    actual_batch_size = min(batch_size, remaining_today)
    selected = select_profiles(profiles, actual_batch_size)

    if not selected:
        log.info("No eligible profiles for this batch.")
        return 0

    if dry_run:
        log.info(f"[DRY RUN] Would visit {len(selected)} profiles:")
        for p in selected:
            log.info(f"  - {p['name']} ({p['title']}) [{p['icp_match']}] {p['url']}")
        return len(selected)

    # Create PureSurf session
    session_id = create_puresurf_session()
    if not session_id:
        log.error("Could not create PureSurf session. Aborting batch.")
        return 0

    visited = 0
    try:
        for i, profile in enumerate(selected):
            profile_url = profile["url"]
            log.info(f"[{i+1}/{len(selected)}] Visiting: {profile['name']} ({profile['title']}) - {profile_url}")

            success = navigate_to_profile(session_id, profile_url)
            if success:
                # Dwell on page (register the view)
                dwell = random.uniform(VIEW_DWELL_MIN, VIEW_DWELL_MAX)
                time.sleep(dwell)

                # Update spreadsheet
                new_count = profile["visit_count"] + 1
                update_visit(sheets, profile["row_index"], new_count)
                visited += 1
                log.info(f"  Visited successfully (dwell: {dwell:.1f}s, total visits: {new_count})")
            else:
                log.warning(f"  Failed to visit {profile['name']}")

            # Wait between visits (human-like interval)
            if i < len(selected) - 1:
                wait = random.uniform(MIN_WAIT_SECONDS, MAX_WAIT_SECONDS)
                log.info(f"  Waiting {wait:.0f}s before next visit...")
                time.sleep(wait)

    except KeyboardInterrupt:
        log.info("Batch interrupted by user")
    finally:
        close_puresurf_session(session_id)

    log.info(f"=== {batch_name} batch complete: {visited}/{len(selected)} profiles visited ===")
    return visited


def run_all_batches(dry_run=False):
    """Run all three daily batches sequentially."""
    total = 0
    for batch_name in ["morning", "afternoon", "evening"]:
        count = run_batch(batch_name, dry_run=dry_run)
        total += count
    log.info(f"=== All batches complete: {total} total profiles visited today ===")
    return total


def determine_batch():
    """Determine which batch to run based on current Eastern Time."""
    from datetime import timezone as tz
    # Eastern Time is UTC-4 (EDT) or UTC-5 (EST)
    # Approximate: use UTC-4 for April
    et_offset = timedelta(hours=-4)
    et_now = datetime.now(timezone.utc) + et_offset
    hour = et_now.hour

    if 8 <= hour < 12:
        return "morning"
    elif 13 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        log.info(f"Current ET hour is {hour}. Outside batch windows (9-10, 14-15, 18-19).")
        return None

# -- CLI --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Profile Viewer - Passive Growth Engine")
    parser.add_argument("--batch", choices=["morning", "afternoon", "evening", "all", "auto"],
                        default="auto", help="Which batch to run (default: auto-detect)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without visiting")
    parser.add_argument("--discover", action="store_true", help="Run profile discovery mode")
    args = parser.parse_args()

    if args.discover:
        log.info("Discovery mode not yet implemented. Populate profiles manually or via PureSurf search.")
        return

    if args.batch == "all":
        run_all_batches(dry_run=args.dry_run)
    elif args.batch == "auto":
        batch = determine_batch()
        if batch:
            run_batch(batch, dry_run=args.dry_run)
        else:
            log.info("No batch scheduled for current time. Use --batch to force.")
    else:
        run_batch(args.batch, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
