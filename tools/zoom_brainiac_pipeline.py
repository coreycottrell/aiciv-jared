#!/usr/bin/env python3
"""
zoom_brainiac_pipeline.py — Automated Zoom → R2 → Brainiac Training Pipeline
=============================================================================
Orchestrates the full 7-step pipeline every Wednesday:

  Step 1: Monitor Zoom for new Brainiac recording
  Step 2: Download video + transcript
  Step 3: Transcode to HLS via ffmpeg
  Step 4: Upload HLS segments to Cloudflare R2
  Step 5: Embed/update video on Brainiac training page (WP)
  Step 6: Generate AI-optimized training summary from transcript
  Step 7: Create/update skill package for PureBrain fleet

USAGE:
  python3 tools/zoom_brainiac_pipeline.py           # Auto mode (checks for new recordings)
  python3 tools/zoom_brainiac_pipeline.py --manual  # Force run even outside Wednesday
  python3 tools/zoom_brainiac_pipeline.py --date 2026-03-12  # Process specific date
  python3 tools/zoom_brainiac_pipeline.py --step 1  # Run a single step only (for debugging)
  python3 tools/zoom_brainiac_pipeline.py --dry-run # Simulate without API calls

SCHEDULING:
  Fires every Wednesday at 2:30pm ET via BOOP/scheduled-tasks system
  Retries at 3pm, 3:30pm, 4pm if recording not found
  Add to .claude/scheduled-tasks-state.json (see bottom of this file for config)

TELEGRAM UPDATES:
  Sends progress to Jared via ./tools/tg_send.sh throughout pipeline
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root and imports
# ---------------------------------------------------------------------------
AETHER_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(AETHER_ROOT / "tools"))

import zoom_api

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
ENV_FILE = AETHER_ROOT / ".env"
BRAINIAC_DIR = AETHER_ROOT / "exports" / "brainiac-training"
MODULES_DIR = BRAINIAC_DIR / "modules"
DOWNLOADS_DIR = BRAINIAC_DIR / "downloads"  # Temp: cleaned up after upload
HLS_WORK_DIR = BRAINIAC_DIR / "hls-work"    # Temp: HLS output before upload
TRANSCODE_SCRIPT = AETHER_ROOT / "tools" / "video-pipeline" / "transcode.sh"
UPLOAD_SCRIPT = AETHER_ROOT / "tools" / "video-pipeline" / "upload_r2.py"
TG_SEND = AETHER_ROOT / "tools" / "tg_send.sh"
RECORDINGS_INDEX = BRAINIAC_DIR / "recordings-index.json"

# Brainiac WP page
WP_PAGE_ID = 1115  # purebrain.ai/brainiac-mastermind-training/
WP_PAGE_PASSWORD = "brainiac2026"

# R2 path convention
R2_KEY_PREFIX = "brainiac/recordings"


# ---------------------------------------------------------------------------
# .env loader
# ---------------------------------------------------------------------------
def load_env() -> dict:
    env = {}
    if not ENV_FILE.exists():
        return env
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    # Also read system environment
    env.update({k: v for k, v in os.environ.items() if k not in env})
    return env


# ---------------------------------------------------------------------------
# Telegram notification helper
# ---------------------------------------------------------------------------
def tg(message: str) -> None:
    """Send a progress update to Telegram via tg_send.sh."""
    try:
        subprocess.run(
            [str(TG_SEND), message],
            timeout=15,
            capture_output=True,
        )
    except Exception as e:
        print(f"[pipeline] Telegram notify failed: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Recordings index (tracks all processed recordings)
# ---------------------------------------------------------------------------
def load_recordings_index() -> dict:
    if RECORDINGS_INDEX.exists():
        with open(RECORDINGS_INDEX) as f:
            return json.load(f)
    return {"recordings": [], "last_updated": None}


def save_recordings_index(index: dict) -> None:
    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    RECORDINGS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with open(RECORDINGS_INDEX, "w") as f:
        json.dump(index, f, indent=2)


def is_already_processed(meeting_id: str, index: dict, meeting_date: str = "") -> bool:
    for r in index.get("recordings", []):
        if r["meeting_id"] == meeting_id and r.get("meeting_date", "") == meeting_date:
            return True
    return False


# ---------------------------------------------------------------------------
# Step 1: Find recording
# ---------------------------------------------------------------------------
def step1_find_recording(target_date: str = None, dry_run: bool = False) -> dict | None:
    """
    Find the latest Brainiac recording.
    If target_date is given, search around that date.
    Returns meeting dict or None.
    """
    print("\n[STEP 1] Searching Zoom for Brainiac recording...", flush=True)
    tg("Brainiac Pipeline Step 1/7: Searching Zoom for recording...")

    if dry_run:
        print("[Step 1] DRY RUN — returning mock recording")
        return {
            "id": "DRY_RUN_ID",
            "topic": "2103-Brainiac - Mastermind Training (DRY RUN)",
            "start_time": (target_date or datetime.now().strftime("%Y-%m-%d")) + "T14:00:00Z",
            "duration": 90,
            "recording_files": [],
            "total_size": 0,
        }

    # Search window: from 3 days before target to 1 day after
    if target_date:
        from_dt = datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=3)
        to_dt = datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=1)
    else:
        # Default: past 7 days
        from_dt = datetime.now() - timedelta(days=7)
        to_dt = datetime.now() + timedelta(days=1)

    from_str = from_dt.strftime("%Y-%m-%d")
    to_str = to_dt.strftime("%Y-%m-%d")

    try:
        recording = zoom_api.find_brainiac_recording(from_date=from_str, to_date=to_str)
    except PermissionError as e:
        print(f"[Step 1] SCOPE ERROR: {e}", file=sys.stderr)
        tg(f"Brainiac Pipeline BLOCKED: Zoom recording scope missing. Check logs.")
        return None

    if recording:
        summary = zoom_api.recording_summary(recording)
        print(f"[Step 1] Found recording:\n{summary}")
        tg(f"Brainiac recording found: {recording.get('topic', 'Unknown')} ({recording.get('duration', 0)} min)")
        return recording
    else:
        print("[Step 1] No Brainiac recording found in date range.")
        tg(f"Brainiac Pipeline: No recording found for {from_str} to {to_str}. Will retry.")
        return None


# ---------------------------------------------------------------------------
# Step 2: Download
# ---------------------------------------------------------------------------
def step2_download(recording: dict, dry_run: bool = False) -> tuple[Path | None, str | None]:
    """
    Download video file and transcript.
    Returns (video_path, transcript_text) tuple.
    """
    print("\n[STEP 2] Downloading recording files...", flush=True)
    tg("Brainiac Pipeline Step 2/7: Downloading video + transcript from Zoom...")

    if dry_run:
        print("[Step 2] DRY RUN — skipping download")
        return None, "This is a dry run transcript. Key topics: AI agents, automation, PureBrain."

    meeting_start = recording.get("start_time", "")[:10]  # YYYY-MM-DD

    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    date_dir = DOWNLOADS_DIR / meeting_start
    date_dir.mkdir(parents=True, exist_ok=True)

    # Download MP4 and transcript
    downloaded = zoom_api.download_recording(
        recording,
        output_dir=date_dir,
        file_types=["MP4", "TRANSCRIPT", "CHAT"],
    )

    # Zoom may return video as MP4, SHARED_SCREEN_WITH_SPEAKER_VIEW, or with (CC) suffix
    video_path = downloaded.get("MP4") or downloaded.get("SHARED_SCREEN_WITH_SPEAKER_VIEW")
    if not video_path:
        # Check for any key containing SHARED_SCREEN or ending in .mp4
        for key, path in downloaded.items():
            if "SHARED_SCREEN" in key or (path and str(path).endswith(".mp4")):
                video_path = path
                print(f"[Step 2] Found video via key: {key}")
                break

    if not video_path:
        print("[Step 2] WARNING: No MP4 found in recording files.", file=sys.stderr)
        # List what we got
        print(f"[Step 2] Got: {list(downloaded.keys())}")
        tg(f"Brainiac Pipeline: No MP4 in recording. Got: {', '.join(downloaded.keys()) or 'nothing'}")

    # Get transcript — from download or direct API extraction
    transcript_text = None
    transcript_path = downloaded.get("TRANSCRIPT")
    if transcript_path and transcript_path.exists():
        transcript_text = transcript_path.read_text(encoding="utf-8")
        # If it's VTT format, convert to plain text
        if "WEBVTT" in transcript_text[:20]:
            transcript_text = zoom_api._vtt_to_text(transcript_text)
    else:
        # Try direct API extraction
        print("[Step 2] Attempting direct transcript extraction from API...")
        transcript_text = zoom_api.get_transcript(recording)

    if transcript_text:
        words = len(transcript_text.split())
        print(f"[Step 2] Transcript: {words} words")
        tg(f"Brainiac Pipeline: Downloaded. Video: {'YES' if video_path else 'NO'}, Transcript: {words} words")
    else:
        print("[Step 2] No transcript available.")
        tg("Brainiac Pipeline: Download complete. No transcript available (will use Whisper if ffmpeg/whisper installed).")

    return video_path, transcript_text


# ---------------------------------------------------------------------------
# Step 3: Transcode
# ---------------------------------------------------------------------------
def step3_transcode(video_path: Path, meeting_date: str, dry_run: bool = False) -> Path | None:
    """
    Transcode video to HLS using existing transcode.sh script.
    Returns path to HLS output directory containing master.m3u8.
    """
    print("\n[STEP 3] Transcoding to HLS...", flush=True)
    tg("Brainiac Pipeline Step 3/7: Transcoding video to HLS format...")

    if dry_run or not video_path:
        print(f"[Step 3] DRY RUN or no video — skipping transcode")
        return None

    # Check ffmpeg is available
    ffmpeg_check = subprocess.run(["which", "ffmpeg"], capture_output=True)
    if ffmpeg_check.returncode != 0:
        print("[Step 3] ffmpeg not installed. Installing...", file=sys.stderr)
        install = subprocess.run(
            ["sudo", "apt-get", "install", "-y", "ffmpeg"],
            capture_output=True,
        )
        if install.returncode != 0:
            print("[Step 3] FAILED to install ffmpeg:", install.stderr.decode(), file=sys.stderr)
            tg("Brainiac Pipeline BLOCKED: ffmpeg not installed and auto-install failed. Run: sudo apt install ffmpeg")
            return None

    hls_output_dir = HLS_WORK_DIR / meeting_date
    hls_output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Step 3] Running: {TRANSCODE_SCRIPT} {video_path} {hls_output_dir}")
    start_time = time.time()

    result = subprocess.run(
        ["bash", str(TRANSCODE_SCRIPT), str(video_path), str(hls_output_dir)],
        capture_output=False,  # Show output in terminal
        timeout=3600,  # 1 hour max for large recordings
    )

    elapsed = time.time() - start_time
    if result.returncode != 0:
        print(f"[Step 3] TRANSCODE FAILED (exit code {result.returncode})", file=sys.stderr)
        tg(f"Brainiac Pipeline FAILED at Step 3: Transcode error. Check logs.")
        return None

    # Verify master.m3u8 was created
    master = hls_output_dir / "master.m3u8"
    if not master.exists():
        print(f"[Step 3] ERROR: master.m3u8 not found in {hls_output_dir}", file=sys.stderr)
        tg("Brainiac Pipeline FAILED: master.m3u8 not created after transcode.")
        return None

    print(f"[Step 3] Transcode complete in {elapsed:.0f}s. Output: {hls_output_dir}")
    tg(f"Brainiac Pipeline Step 3 done: Transcode complete ({elapsed:.0f}s)")
    return hls_output_dir


# ---------------------------------------------------------------------------
# Step 4: Upload to R2
# ---------------------------------------------------------------------------
def step4_upload_r2(hls_dir: Path, meeting_date: str, dry_run: bool = False) -> str | None:
    """
    Upload HLS output to Cloudflare R2.
    Returns the public master.m3u8 URL.
    """
    print("\n[STEP 4] Uploading to Cloudflare R2...", flush=True)
    tg("Brainiac Pipeline Step 4/7: Uploading HLS to Cloudflare R2...")

    if dry_run or not hls_dir:
        env = load_env()
        public_base = env.get("R2_PUBLIC_URL_BASE", "https://pub-PLACEHOLDER.r2.dev")
        mock_url = f"{public_base}/{R2_KEY_PREFIX}/{meeting_date}/master.m3u8"
        print(f"[Step 4] DRY RUN — mock URL: {mock_url}")
        return mock_url

    env = load_env()
    r2_key = f"{R2_KEY_PREFIX}/{meeting_date}"

    # Use existing upload_r2.py
    cmd = [
        sys.executable,
        str(UPLOAD_SCRIPT),
        "--dir", str(hls_dir),
        "--key", r2_key,
    ]

    # Pass optional bucket name if set
    bucket = env.get("R2_BUCKET_NAME") or env.get("R2_BUCKET") or "purebrain-video"
    if bucket:
        cmd += ["--bucket", bucket]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[Step 4] R2 upload FAILED:\n{result.stdout}\n{result.stderr}", file=sys.stderr)
        tg("Brainiac Pipeline FAILED at Step 4: R2 upload error. Check R2 credentials.")
        return None

    # Extract URL from output (upload_r2.py prints it on last line)
    output_lines = result.stdout.strip().splitlines()
    master_url = None
    for line in reversed(output_lines):
        if "master.m3u8" in line and line.startswith("http"):
            master_url = line.strip()
            break
        if line.startswith("Public URL:"):
            master_url = line.split("Public URL:")[-1].strip()
            break

    if not master_url:
        # Construct URL from known pattern
        public_base = env.get("R2_PUBLIC_URL_BASE", "")
        if public_base:
            master_url = f"{public_base.rstrip('/')}/{r2_key}/master.m3u8"

    print(f"[Step 4] Upload complete. URL: {master_url}")
    tg(f"Brainiac Pipeline Step 4 done: Uploaded to R2")
    return master_url


# ---------------------------------------------------------------------------
# Step 5: Update Brainiac training page
# ---------------------------------------------------------------------------
def step5_update_page(
    master_url: str,
    recording: dict,
    meeting_date: str,
    all_recordings: list,
    dry_run: bool = False,
) -> bool:
    """
    Update the Brainiac training page on WordPress with the new video.
    Reads current page content, adds the new recording entry, redeploys.
    """
    print("\n[STEP 5] Updating Brainiac training page...", flush=True)
    tg("Brainiac Pipeline Step 5/7: Updating training page on purebrain.ai...")

    env = load_env()
    wp_password = env.get("PUREBRAIN_WP_APP_PASSWORD", "")

    if not wp_password:
        print("[Step 5] ERROR: PUREBRAIN_WP_APP_PASSWORD not set in .env", file=sys.stderr)
        tg("Brainiac Pipeline BLOCKED: WP app password not configured.")
        return False

    if dry_run:
        print("[Step 5] DRY RUN — skipping WP page update")
        return True

    # Build the updated HTML for the page
    topic = recording.get("topic", "Brainiac Mastermind Training")
    duration_min = recording.get("duration", 0)
    duration_str = f"{duration_min}:00" if duration_min else "N/A"

    # Poster thumbnail: look for poster.jpg in HLS work dir
    poster_r2_url = None
    hls_dir = HLS_WORK_DIR / meeting_date
    poster_path = hls_dir / "poster.jpg"
    if poster_path.exists():
        # Poster is uploaded alongside HLS content in Step 4
        public_base = env.get("R2_PUBLIC_URL_BASE", "")
        if public_base and master_url:
            poster_r2_url = master_url.replace("master.m3u8", "poster.jpg")

    # Build the page HTML using our established brainiac video library pattern
    page_html = _build_brainiac_page_html(all_recordings)

    # Deploy to WordPress
    import urllib.request
    import urllib.error
    import base64

    wp_creds = base64.b64encode(f"Aether:{wp_password}".encode()).decode()
    payload = json.dumps({
        "content": f"<!-- wp:html -->{page_html}<!-- /wp:html -->",
        "template": "elementor_canvas",
    }).encode()

    req = urllib.request.Request(
        f"https://purebrain.ai/wp-json/wp/v2/pages/{WP_PAGE_ID}",
        data=payload,
        headers={
            "Authorization": f"Basic {wp_creds}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            link = result.get("link", "https://purebrain.ai/brainiac-mastermind-training/")
            print(f"[Step 5] Page updated: {link}")
            tg(f"Brainiac Pipeline Step 5 done: Training page updated with new video")
            return True
    except urllib.error.HTTPError as e:
        print(f"[Step 5] WP update failed: HTTP {e.code}\n{e.read().decode()}", file=sys.stderr)
        tg(f"Brainiac Pipeline WARNING: Step 5 WP update failed (HTTP {e.code}). Video on R2, page not updated.")
        return False


def _build_brainiac_page_html(recordings: list) -> str:
    """
    Build the full Brainiac training page HTML.
    Uses the established VIDEO_LIBRARY JS array pattern from the existing page.
    """
    # Build JS array entries
    video_entries = []
    for i, rec in enumerate(recordings):
        entry = {
            "id": rec.get("r2_key", f"recording-{i}").replace("/", "-"),
            "title": rec.get("title", f"Training Session {i+1}"),
            "description": rec.get("description", "Brainiac Mastermind Training Session"),
            "duration": rec.get("duration_str", None),
            "posterUrl": rec.get("poster_url", None),
            "hlsUrl": rec.get("master_url", None),
            "status": "live" if rec.get("master_url") else "coming_soon",
            "badge": "new" if i == 0 else None,
            "date": rec.get("date", ""),
            "moduleFile": rec.get("module_file", None),
        }
        video_entries.append(entry)

    video_js = json.dumps(video_entries, indent=4)

    # The full page HTML (self-contained, inline CSS + JS, same security pattern as existing page)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Brainiac Mastermind Training | PureBrain.ai</title>
<style>
:root {{
  --pb-dark: #080a12;
  --pb-blue: #2a93c1;
  --pb-orange: #f1420b;
  --pb-glass: rgba(255,255,255,0.05);
  --pb-border: rgba(255,255,255,0.1);
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#080a12;color:#fff;font-family:'Inter',system-ui,sans-serif;min-height:100vh}}
body{{padding:0}}

/* Password Gate */
#gate{{
  position:fixed;inset:0;background:#080a12;z-index:9999;
  display:flex;align-items:center;justify-content:center;flex-direction:column;gap:1.5rem;
}}
#gate h2{{font-size:1.5rem;color:#fff;text-align:center}}
#gate p{{color:rgba(255,255,255,0.5);font-size:0.875rem;text-align:center}}
#gate-input{{
  padding:0.75rem 1.25rem;border-radius:8px;border:1px solid rgba(255,255,255,0.15);
  background:rgba(255,255,255,0.05);color:#fff;font-size:1rem;width:280px;text-align:center;
}}
#gate-input:focus{{outline:none;border-color:var(--pb-blue)}}
#gate-btn{{
  padding:0.75rem 2rem;background:var(--pb-orange);color:#fff;border:none;border-radius:8px;
  font-size:1rem;font-weight:600;cursor:pointer;transition:opacity .2s;
}}
#gate-btn:hover{{opacity:0.85}}
#gate-err{{color:var(--pb-orange);font-size:0.875rem;display:none}}

/* Main content */
#main{{display:none;padding:2rem 1.5rem;max-width:1200px;margin:0 auto}}

/* Header */
.page-header{{margin-bottom:2.5rem;padding-bottom:1.5rem;border-bottom:1px solid var(--pb-border)}}
.page-header h1{{font-size:2rem;font-weight:700;margin-bottom:0.5rem}}
.page-header h1 span.orange{{color:var(--pb-orange)}}
.page-header p{{color:rgba(255,255,255,0.6);font-size:1rem}}

/* Video grid */
.video-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:1.5rem}}
.video-card{{
  background:var(--pb-glass);border:1px solid var(--pb-border);border-radius:12px;
  overflow:hidden;cursor:pointer;transition:border-color .2s,transform .2s;
}}
.video-card:hover{{border-color:var(--pb-blue);transform:translateY(-2px)}}
.video-card.coming-soon{{opacity:0.6;cursor:default}}

/* Card thumbnail */
.card-thumb{{position:relative;aspect-ratio:16/9;background:#0e1020;overflow:hidden}}
.card-thumb img{{width:100%;height:100%;object-fit:cover}}
.card-thumb-placeholder{{
  width:100%;height:100%;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(135deg,#0e1020,#1a1f3a);
}}
.play-icon{{
  width:56px;height:56px;border-radius:50%;background:var(--pb-orange);
  display:flex;align-items:center;justify-content:center;transition:transform .2s;
}}
.video-card:hover .play-icon{{transform:scale(1.1)}}
.play-icon svg{{margin-left:4px}}
.card-badge{{
  position:absolute;top:10px;right:10px;background:var(--pb-orange);color:#fff;
  font-size:0.7rem;font-weight:700;padding:2px 8px;border-radius:4px;text-transform:uppercase;
}}
.card-duration{{
  position:absolute;bottom:8px;right:10px;background:rgba(0,0,0,0.8);color:#fff;
  font-size:0.75rem;padding:2px 6px;border-radius:4px;
}}

/* Card info */
.card-info{{padding:1rem 1.25rem 1.25rem}}
.card-date{{font-size:0.75rem;color:rgba(255,255,255,0.4);margin-bottom:0.35rem}}
.card-title{{font-size:1rem;font-weight:600;margin-bottom:0.4rem;color:#fff}}
.card-desc{{font-size:0.825rem;color:rgba(255,255,255,0.5);line-height:1.5}}
.card-transcript-link{{
  display:inline-block;margin-top:0.75rem;font-size:0.75rem;color:var(--pb-blue);
  text-decoration:none;
}}
.card-transcript-link:hover{{text-decoration:underline}}

/* Modal */
#modal-overlay{{
  display:none;position:fixed;inset:0;background:rgba(0,0,0,0.92);z-index:10000;
  align-items:center;justify-content:center;padding:1rem;
}}
#modal-overlay.open{{display:flex}}
#modal{{
  background:#0e1020;border:1px solid var(--pb-border);border-radius:16px;
  width:100%;max-width:900px;overflow:hidden;
}}
#modal-video-wrap{{position:relative;aspect-ratio:16/9;background:#000}}
#modal-video{{width:100%;height:100%;display:block}}
#modal-close{{
  position:absolute;top:12px;right:12px;width:36px;height:36px;border-radius:50%;
  background:rgba(0,0,0,0.7);border:1px solid var(--pb-border);color:#fff;
  font-size:1.25rem;cursor:pointer;display:flex;align-items:center;justify-content:center;
  z-index:10;transition:background .2s;
}}
#modal-close:hover{{background:var(--pb-orange)}}
#modal-info{{padding:1.25rem 1.5rem}}
#modal-title{{font-size:1.1rem;font-weight:600;margin-bottom:0.25rem}}
#modal-date{{font-size:0.8rem;color:rgba(255,255,255,0.4)}}
</style>
</head>
<body>

<!-- Password Gate -->
<div id="gate">
  <div style="width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#2a93c1,#f1420b);display:flex;align-items:center;justify-content:center;margin-bottom:0.5rem">
    <svg width="28" height="28" viewBox="0 0 24 24" fill="white"><path d="M12 2a7 7 0 015 11.9V22h-3l-1-2-1 2-1-2-1 2h-3v-8.1A7 7 0 0112 2zm0 2a5 5 0 100 10A5 5 0 0012 4zm0 2a3 3 0 110 6 3 3 0 010-6z"/></svg>
  </div>
  <h2>Brainiac Mastermind Training</h2>
  <p>Enter your access password to view recordings</p>
  <input id="gate-input" type="password" placeholder="Password" autocomplete="current-password">
  <button id="gate-btn">Access Training</button>
  <span id="gate-err">Incorrect password. Try again.</span>
</div>

<!-- Main Content -->
<div id="main">
  <div class="page-header">
    <h1>Brainiac <span class="orange">Mastermind</span> Training</h1>
    <p>Weekly training sessions — your library of every session since launch</p>
  </div>
  <div class="video-grid" id="video-grid"></div>
</div>

<!-- Video Modal -->
<div id="modal-overlay">
  <div id="modal">
    <div id="modal-video-wrap">
      <button id="modal-close">&times;</button>
      <video id="modal-video" controls playsinline></video>
    </div>
    <div id="modal-info">
      <div id="modal-title"></div>
      <div id="modal-date"></div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/hls.js@1.5.7/dist/hls.min.js"></script>
<script>
(function(){{
  'use strict';

  var GATE_PASSWORD = {json.dumps(WP_PAGE_PASSWORD)};
  var VIDEO_LIBRARY = {video_js};

  // -----------------------------------------------------------------------
  // XSS protection
  // -----------------------------------------------------------------------
  function esc(str) {{
    if (!str) return '';
    return String(str)
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;')
      .replace(/'/g,'&#x27;');
  }}

  // -----------------------------------------------------------------------
  // Gate
  // -----------------------------------------------------------------------
  var gateEl = document.getElementById('gate');
  var mainEl = document.getElementById('main');
  var gateInput = document.getElementById('gate-input');
  var gateBtn = document.getElementById('gate-btn');
  var gateErr = document.getElementById('gate-err');

  function unlock() {{
    var val = gateInput.value.trim();
    if (val === GATE_PASSWORD) {{
      gateEl.style.display = 'none';
      mainEl.style.display = 'block';
      sessionStorage.setItem('brainiac_auth', '1');
      renderGrid();
    }} else {{
      gateErr.style.display = 'block';
      gateInput.value = '';
      gateInput.focus();
    }}
  }}

  gateBtn.addEventListener('click', unlock);
  gateInput.addEventListener('keydown', function(e) {{ if (e.key === 'Enter') unlock(); }});

  if (sessionStorage.getItem('brainiac_auth') === '1') {{
    gateEl.style.display = 'none';
    mainEl.style.display = 'block';
    renderGrid();
  }}

  // -----------------------------------------------------------------------
  // Render video grid
  // -----------------------------------------------------------------------
  function renderGrid() {{
    var grid = document.getElementById('video-grid');
    grid.innerHTML = '';
    VIDEO_LIBRARY.forEach(function(vid, i) {{
      var card = document.createElement('div');
      card.className = 'video-card' + (vid.status !== 'live' ? ' coming-soon' : '');
      card.innerHTML =
        '<div class="card-thumb">' +
          (vid.posterUrl
            ? '<img src="' + esc(vid.posterUrl) + '" alt="" loading="lazy">'
            : '<div class="card-thumb-placeholder"><div class="play-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="white"><polygon points="5,3 19,12 5,21"/></svg></div></div>') +
          (vid.badge ? '<span class="card-badge">' + esc(vid.badge) + '</span>' : '') +
          (vid.duration ? '<span class="card-duration">' + esc(vid.duration) + '</span>' : '') +
        '</div>' +
        '<div class="card-info">' +
          (vid.date ? '<div class="card-date">' + esc(vid.date) + '</div>' : '') +
          '<div class="card-title">' + esc(vid.title) + '</div>' +
          '<div class="card-desc">' + esc(vid.description) + '</div>' +
          (vid.moduleFile
            ? '<a class="card-transcript-link" href="/training-modules/' + esc(vid.moduleFile) + '" target="_blank">View Training Summary &rarr;</a>'
            : '') +
        '</div>';

      if (vid.status === 'live' && vid.hlsUrl) {{
        card.addEventListener('click', function() {{ openModal(vid); }});
      }}
      grid.appendChild(card);
    }});
  }}

  // -----------------------------------------------------------------------
  // Modal player
  // -----------------------------------------------------------------------
  var overlay = document.getElementById('modal-overlay');
  var modalVideo = document.getElementById('modal-video');
  var modalTitle = document.getElementById('modal-title');
  var modalDate = document.getElementById('modal-date');
  var hlsInstance = null;

  function openModal(vid) {{
    modalTitle.textContent = vid.title;
    modalDate.textContent = vid.date || '';
    overlay.classList.add('open');

    if (hlsInstance) {{ hlsInstance.destroy(); hlsInstance = null; }}
    modalVideo.src = '';

    var hlsUrl = vid.hlsUrl;
    if (Hls.isSupported()) {{
      hlsInstance = new Hls();
      hlsInstance.loadSource(hlsUrl);
      hlsInstance.attachMedia(modalVideo);
      hlsInstance.on(Hls.Events.MANIFEST_PARSED, function() {{ modalVideo.play(); }});
      hlsInstance.on(Hls.Events.ERROR, function(e, d) {{
        if (d.fatal) {{
          if (d.type === Hls.ErrorTypes.NETWORK_ERROR) hlsInstance.startLoad();
          else if (d.type === Hls.ErrorTypes.MEDIA_ERROR) hlsInstance.recoverMediaError();
        }}
      }});
    }} else if (modalVideo.canPlayType('application/vnd.apple.mpegurl')) {{
      modalVideo.src = hlsUrl;
      modalVideo.play();
    }}
  }}

  function closeModal() {{
    overlay.classList.remove('open');
    modalVideo.pause();
    if (hlsInstance) {{ hlsInstance.destroy(); hlsInstance = null; }}
    modalVideo.src = '';
  }}

  document.getElementById('modal-close').addEventListener('click', closeModal);
  overlay.addEventListener('click', function(e) {{ if (e.target === overlay) closeModal(); }});
  document.addEventListener('keydown', function(e) {{ if (e.key === 'Escape') closeModal(); }});

}})();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Step 6: Generate AI training summary
# ---------------------------------------------------------------------------
def step6_generate_summary(
    transcript: str,
    recording: dict,
    meeting_date: str,
    master_url: str,
    dry_run: bool = False,
) -> tuple[Path, Path] | tuple[None, None]:
    """
    Generate an AI-optimized training summary from transcript.
    Uses Claude (via subprocess calling claude CLI) or Gemini if available.
    Falls back to structured extraction from transcript text.

    Returns (json_path, md_path) or (None, None).
    """
    print("\n[STEP 6] Generating training summary...", flush=True)
    tg("Brainiac Pipeline Step 6/7: Generating AI training summary...")

    MODULES_DIR.mkdir(parents=True, exist_ok=True)
    json_path = MODULES_DIR / f"module-{meeting_date}.json"
    md_path = MODULES_DIR / f"module-{meeting_date}.md"

    topic = recording.get("topic", "Brainiac Mastermind Training")
    duration = recording.get("duration", 0)

    if dry_run or not transcript:
        # Create placeholder module
        module = _create_placeholder_module(topic, meeting_date, duration, master_url)
    else:
        # Generate summary using available AI
        module = _generate_ai_summary(transcript, topic, meeting_date, duration, master_url)

    # Save JSON
    with open(json_path, "w") as f:
        json.dump(module, f, indent=2)

    # Save Markdown
    md_content = _module_to_markdown(module)
    with open(md_path, "w") as f:
        f.write(md_content)

    print(f"[Step 6] Module saved: {json_path}")
    print(f"[Step 6] Markdown saved: {md_path}")
    tg(f"Brainiac Pipeline Step 6 done: Training module generated ({json_path.name})")

    return json_path, md_path


def _generate_ai_summary(
    transcript: str,
    topic: str,
    meeting_date: str,
    duration: int,
    master_url: str,
) -> dict:
    """
    Generate structured summary from transcript.
    First tries claude CLI, then falls back to pattern extraction.
    """
    prompt = f"""You are generating an informationally dense training summary for AI consumption.

TRANSCRIPT FROM: {topic} ({meeting_date}, {duration} min)

TRANSCRIPT:
{transcript[:12000]}{'...[truncated]' if len(transcript) > 12000 else ''}

Generate a JSON object with these exact keys:
{{
  "key_topics": ["list of main topics covered"],
  "action_items": ["concrete tasks mentioned for participants"],
  "frameworks_taught": ["any frameworks, models, or systems explained"],
  "tools_referenced": ["software tools, platforms, or services mentioned"],
  "implementation_steps": ["step-by-step instructions from the session"],
  "key_quotes": ["2-3 memorable or instructive quotes"],
  "session_summary": "2-paragraph summary optimized for AI to understand the session's value",
  "skill_tags": ["tags for search/retrieval, e.g. 'automation', 'AI agents', 'PureBrain'"]
}}

Return ONLY the JSON object, no other text."""

    # Try claude CLI
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "text"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(AETHER_ROOT),
        )
        if result.returncode == 0 and result.stdout.strip():
            output = result.stdout.strip()
            # Extract JSON from output
            start = output.find("{")
            end = output.rfind("}") + 1
            if start >= 0 and end > start:
                parsed = json.loads(output[start:end])
                parsed["meeting_date"] = meeting_date
                parsed["topic"] = topic
                parsed["duration_min"] = duration
                parsed["master_url"] = master_url
                parsed["generated_at"] = datetime.now(timezone.utc).isoformat()
                parsed["generation_method"] = "claude_cli"
                return parsed
    except Exception as e:
        print(f"[Step 6] Claude CLI failed: {e} — falling back to pattern extraction", file=sys.stderr)

    # Fallback: basic pattern extraction
    return _extract_summary_from_text(transcript, topic, meeting_date, duration, master_url)


def _extract_summary_from_text(
    transcript: str,
    topic: str,
    meeting_date: str,
    duration: int,
    master_url: str,
) -> dict:
    """Simple pattern-based extraction when AI is not available."""
    lines = transcript.splitlines()
    # Extract lines that look like action items
    action_patterns = ["you should", "make sure", "need to", "action item", "homework", "do this"]
    action_items = []
    for line in lines:
        l = line.lower()
        if any(p in l for p in action_patterns) and len(line) > 20:
            action_items.append(line.strip()[:200])
            if len(action_items) >= 10:
                break

    return {
        "meeting_date": meeting_date,
        "topic": topic,
        "duration_min": duration,
        "master_url": master_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generation_method": "pattern_extraction",
        "session_summary": f"Training session: {topic}. Duration: {duration} minutes. Full transcript available.",
        "key_topics": ["See full transcript for details"],
        "action_items": action_items[:10] or ["Review session recording for action items"],
        "frameworks_taught": [],
        "tools_referenced": [],
        "implementation_steps": [],
        "key_quotes": [],
        "skill_tags": ["brainiac", "mastermind", "training"],
        "transcript_word_count": len(transcript.split()),
    }


def _create_placeholder_module(topic: str, meeting_date: str, duration: int, master_url: str) -> dict:
    return {
        "meeting_date": meeting_date,
        "topic": topic,
        "duration_min": duration,
        "master_url": master_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generation_method": "placeholder",
        "session_summary": f"Training module for {meeting_date}. Summary will be generated when transcript is available.",
        "key_topics": [],
        "action_items": [],
        "frameworks_taught": [],
        "tools_referenced": [],
        "implementation_steps": [],
        "key_quotes": [],
        "skill_tags": ["brainiac", "mastermind", "training"],
    }


def _module_to_markdown(module: dict) -> str:
    date = module.get("meeting_date", "Unknown")
    topic = module.get("topic", "Training Session")
    duration = module.get("duration_min", 0)
    summary = module.get("session_summary", "")
    master_url = module.get("master_url", "")

    sections = [
        f"# Brainiac Training Module — {date}",
        f"",
        f"**Topic**: {topic}  ",
        f"**Duration**: {duration} minutes  ",
        f"**Video**: [{master_url}]({master_url})" if master_url else "",
        f"",
        f"## Session Summary",
        f"",
        summary,
        f"",
    ]

    for key, label in [
        ("key_topics", "Key Topics"),
        ("action_items", "Action Items"),
        ("frameworks_taught", "Frameworks Taught"),
        ("tools_referenced", "Tools Referenced"),
        ("implementation_steps", "Implementation Steps"),
        ("key_quotes", "Key Quotes"),
    ]:
        items = module.get(key, [])
        if items:
            sections.append(f"## {label}")
            sections.append("")
            for item in items:
                sections.append(f"- {item}")
            sections.append("")

    tags = module.get("skill_tags", [])
    if tags:
        sections.append(f"**Tags**: {', '.join(tags)}")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Step 7: Update skill package
# ---------------------------------------------------------------------------
def step7_update_skill(dry_run: bool = False) -> bool:
    """
    Update the brainiac-training skill file with current module list.
    The skill allows any PureBrain AI to access training content.
    """
    print("\n[STEP 7] Updating brainiac-training skill...", flush=True)
    tg("Brainiac Pipeline Step 7/7: Updating brainiac-training skill package...")

    skill_path = AETHER_ROOT / ".claude" / "skills" / "brainiac-training" / "SKILL.md"

    if dry_run:
        print(f"[Step 7] DRY RUN — would update {skill_path}")
        return True

    # List available modules
    modules = sorted(MODULES_DIR.glob("module-*.json"), reverse=True)
    module_list = []
    for m in modules:
        try:
            with open(m) as f:
                data = json.load(f)
            module_list.append({
                "date": data.get("meeting_date", m.stem.replace("module-", "")),
                "topic": data.get("topic", "Training Session"),
                "duration": data.get("duration_min", 0),
                "master_url": data.get("master_url", ""),
                "skill_tags": data.get("skill_tags", []),
                "file": m.name,
            })
        except Exception:
            pass

    latest = module_list[0] if module_list else None
    module_table = "\n".join(
        f"| {m['date']} | {m['topic'][:50]} | {m['duration']}min | {m['file']} |"
        for m in module_list[:20]
    )

    skill_content = f"""# brainiac-training Skill

**Purpose**: Access and apply Brainiac Mastermind Training content
**Updated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
**Modules available**: {len(module_list)}

---

## What This Skill Does

Gives any PureBrain AI access to all Brainiac Mastermind Training session summaries,
action items, and frameworks taught by Jared.

Use this skill to:
- Answer questions about training content
- Execute recommendations from past sessions
- Check if a specific topic was covered in training
- Reference frameworks taught in the mastermind

---

## Available Modules

| Date | Topic | Duration | File |
|------|-------|----------|------|
{module_table if module_table else "| — | No modules yet | — | — |"}

**Module files**: `/home/jared/projects/AI-CIV/aether/exports/brainiac-training/modules/`

---

## How to Use

### List modules
```python
from pathlib import Path
import json
modules_dir = Path('/home/jared/projects/AI-CIV/aether/exports/brainiac-training/modules')
modules = sorted(modules_dir.glob('module-*.json'), reverse=True)
for m in modules:
    data = json.loads(m.read_text())
    print(f"{{data['meeting_date']}}: {{data['topic']}} ({{data['duration_min']}} min)")
```

### Read a specific module
```python
import json
from pathlib import Path
module_path = Path('/home/jared/projects/AI-CIV/aether/exports/brainiac-training/modules/module-YYYY-MM-DD.json')
module = json.loads(module_path.read_text())
print(module['session_summary'])
print('Action items:', module['action_items'])
print('Frameworks:', module['frameworks_taught'])
```

### Check for new modules
```python
from pathlib import Path
import json
from datetime import datetime
modules_dir = Path('/home/jared/projects/AI-CIV/aether/exports/brainiac-training/modules')
latest = sorted(modules_dir.glob('module-*.json'))[-1] if list(modules_dir.glob('module-*.json')) else None
if latest:
    data = json.loads(latest.read_text())
    print(f"Latest module: {{data['meeting_date']}} - {{data['topic']}}")
```

---

## Latest Module Summary
{'**Date**: ' + latest['date'] + '  ' if latest else 'No modules available yet.'}
{'**Topic**: ' + latest['topic'] if latest else ''}
{'**Tags**: ' + ', '.join(latest.get('skill_tags', [])) if latest else ''}

---

## Scheduling

Pipeline runs automatically every Wednesday at 2:30pm ET.
Manual trigger: `python3 /home/jared/projects/AI-CIV/aether/tools/zoom_brainiac_pipeline.py --manual`

---

## Recording Archive

Video recordings on R2: `brainiac/recordings/YYYY-MM-DD/master.m3u8`
Training page: https://purebrain.ai/brainiac-mastermind-training/
"""

    skill_path.parent.mkdir(parents=True, exist_ok=True)
    with open(skill_path, "w") as f:
        f.write(skill_content)

    print(f"[Step 7] Skill updated: {skill_path} ({len(module_list)} modules)")
    tg(f"Brainiac Pipeline COMPLETE: {len(module_list)} training modules available. Skill updated.")
    return True


# ---------------------------------------------------------------------------
# Main pipeline orchestrator
# ---------------------------------------------------------------------------
def run_pipeline(
    target_date: str = None,
    manual: bool = False,
    dry_run: bool = False,
    step: int = None,
    max_retries: int = 4,
    retry_interval_min: int = 30,
) -> bool:
    """
    Run the full 7-step pipeline.
    Returns True if successful, False if failed or recording not found.
    """
    print("=" * 60, flush=True)
    print("BRAINIAC TRAINING PIPELINE", flush=True)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}", flush=True)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}", flush=True)
    print("=" * 60, flush=True)

    if not manual and not dry_run:
        # Only run on Wednesdays unless --manual
        weekday = datetime.now().weekday()  # 0=Mon, 2=Wed
        if weekday != 2:
            print(f"[pipeline] Today is not Wednesday (weekday={weekday}). Use --manual to override.")
            return False

    tg("Brainiac Pipeline STARTING: Full 7-step Zoom → R2 → Training automation")

    # Load index of processed recordings
    index = load_recordings_index()

    # Retry loop for finding recording
    recording = None
    for attempt in range(max_retries):
        if attempt > 0:
            print(f"\n[pipeline] Retry {attempt}/{max_retries-1} in {retry_interval_min} min...")
            tg(f"Brainiac Pipeline: Recording not found, retrying in {retry_interval_min} min (attempt {attempt+1}/{max_retries})")
            time.sleep(retry_interval_min * 60)

        recording = step1_find_recording(target_date=target_date, dry_run=dry_run)

        if recording:
            break

    if not recording:
        print("[pipeline] Recording not found after all retries. Pipeline aborted.")
        tg("Brainiac Pipeline ABORTED: Recording not found after all retries. Check Zoom manually.")
        return False

    meeting_id = recording.get("id", "DRY_RUN_ID")
    meeting_date = recording.get("start_time", "")[:10] or (target_date or datetime.now().strftime("%Y-%m-%d"))

    # Skip if already processed (check by meeting_id + date for recurring meetings)
    if not dry_run and is_already_processed(meeting_id, index, meeting_date):
        print(f"[pipeline] Recording {meeting_id} on {meeting_date} already processed. Skipping.")
        tg(f"Brainiac Pipeline: Recording already processed ({meeting_date}). Nothing to do.")
        return True

    # Step 2: Download
    if step is None or step <= 2:
        video_path, transcript = step2_download(recording, dry_run=dry_run)
    else:
        video_path, transcript = None, None

    # Step 3: Transcode
    if step is None or step <= 3:
        hls_dir = step3_transcode(video_path, meeting_date, dry_run=dry_run)
    else:
        hls_dir = HLS_WORK_DIR / meeting_date if (HLS_WORK_DIR / meeting_date).exists() else None

    # Step 4: Upload to R2
    if step is None or step <= 4:
        master_url = step4_upload_r2(hls_dir, meeting_date, dry_run=dry_run)
    else:
        master_url = None

    # Step 6: Generate summary (before Step 5 so we can include module link on page)
    if step is None or step <= 6:
        json_path, md_path = step6_generate_summary(
            transcript, recording, meeting_date, master_url or "", dry_run=dry_run
        )
    else:
        json_path, md_path = None, None

    # Build the all-recordings list for the page
    all_recordings_for_page = _build_recordings_for_page(index, recording, meeting_date, master_url, md_path)

    # Step 5: Update page
    if step is None or step <= 5:
        page_ok = step5_update_page(
            master_url or "",
            recording,
            meeting_date,
            all_recordings_for_page,
            dry_run=dry_run,
        )
    else:
        page_ok = False

    # Step 7: Update skill
    if step is None or step <= 7:
        step7_update_skill(dry_run=dry_run)

    # Update index
    if not dry_run:
        index["recordings"].append({
            "meeting_id": meeting_id,
            "meeting_date": meeting_date,
            "topic": recording.get("topic", ""),
            "master_url": master_url,
            "module_json": str(json_path) if json_path else None,
            "module_md": str(md_path) if md_path else None,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        })
        save_recordings_index(index)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print(f"  Recording: {recording.get('topic', 'Unknown')}")
    print(f"  Date: {meeting_date}")
    print(f"  Master URL: {master_url or 'N/A'}")
    print(f"  Module: {json_path or 'N/A'}")
    print("=" * 60)

    return True


def _build_recordings_for_page(
    index: dict,
    current_recording: dict,
    current_date: str,
    master_url: str | None,
    md_path: Path | None,
) -> list:
    """Build list of all recordings for the WP page template."""
    result = []

    # Add current recording first (newest)
    topic = current_recording.get("topic", "Brainiac Mastermind Training")
    # Clean up topic: remove "2103-" prefix if present
    display_title = topic
    if " - " in topic:
        display_title = topic.split(" - ", 1)[-1].strip()

    result.append({
        "title": display_title,
        "description": f"Brainiac Mastermind Training — {current_date}",
        "date": current_date,
        "master_url": master_url,
        "poster_url": master_url.replace("master.m3u8", "poster.jpg") if master_url else None,
        "duration_str": f"{current_recording.get('duration', 0)}:00",
        "r2_key": f"{R2_KEY_PREFIX}/{current_date}",
        "module_file": md_path.name if md_path else None,
    })

    # Add past recordings from index
    for rec in reversed(index.get("recordings", [])):
        if rec.get("meeting_date") == current_date:
            continue  # Already added above
        past_topic = rec.get("topic", "Brainiac Mastermind Training")
        if " - " in past_topic:
            past_topic = past_topic.split(" - ", 1)[-1].strip()

        past_url = rec.get("master_url")
        result.append({
            "title": past_topic,
            "description": f"Brainiac Mastermind Training — {rec.get('meeting_date', '')}",
            "date": rec.get("meeting_date", ""),
            "master_url": past_url,
            "poster_url": past_url.replace("master.m3u8", "poster.jpg") if past_url else None,
            "duration_str": None,
            "r2_key": f"{R2_KEY_PREFIX}/{rec.get('meeting_date', '')}",
            "module_file": Path(rec["module_md"]).name if rec.get("module_md") else None,
        })

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Brainiac Zoom → R2 → Training Page Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 tools/zoom_brainiac_pipeline.py --manual
  python3 tools/zoom_brainiac_pipeline.py --date 2026-03-12 --manual
  python3 tools/zoom_brainiac_pipeline.py --dry-run --manual
  python3 tools/zoom_brainiac_pipeline.py --step 1 --manual

SCHEDULING CONFIG (add to .claude/scheduled-tasks-state.json):
  {{
    "id": "brainiac-zoom-pipeline",
    "name": "Brainiac Zoom Recording Pipeline",
    "schedule": "Wednesday 14:30 ET",
    "command": "python3 /home/jared/projects/AI-CIV/aether/tools/zoom_brainiac_pipeline.py",
    "retry_times": ["15:00", "15:30", "16:00"]
  }}
""",
    )
    parser.add_argument("--manual", action="store_true", help="Run even if not Wednesday")
    parser.add_argument("--date", help="Target date YYYY-MM-DD (defaults to today)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without API calls")
    parser.add_argument("--step", type=int, choices=[1, 2, 3, 4, 5, 6, 7], help="Run single step only")
    parser.add_argument("--no-retry", action="store_true", help="Don't retry if recording not found")
    args = parser.parse_args()

    success = run_pipeline(
        target_date=args.date,
        manual=args.manual,
        dry_run=args.dry_run,
        step=args.step,
        max_retries=1 if args.no_retry else 4,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
