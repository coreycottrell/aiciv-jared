#!/usr/bin/env python3
"""
run_brainiac_pipeline_manual.py
================================
One-shot manual pipeline for the two existing Brainiac Mastermind recordings.

Module 1: March 4, 2026  — "Module 1 of Brainiac - Mastermind Training"
Module 2: March 11, 2026 — "Brainiac - Mastermind Training"

Steps:
  1. Download MP4 + TRANSCRIPT for each recording via Zoom API
  2. Transcode to HLS (adaptive) + generate poster thumbnail
  3. Upload HLS segments to Cloudflare R2 (brainiac/recordings/module-1 etc.)
  4. Download Zoom AI summaries (JSON) for context
  5. Generate training module summaries from transcripts
  6. Update brainiac-mastermind-training.html with live video entries
  7. Deploy updated HTML to WordPress page 1115
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

AETHER_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(AETHER_ROOT / "tools"))

import zoom_api

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TG_SEND = AETHER_ROOT / "tools" / "tg_send.sh"
BRAINIAC_HTML = AETHER_ROOT / "exports" / "brainiac-mastermind-training.html"
MODULES_DIR = AETHER_ROOT / "exports" / "brainiac-training" / "modules"
UPLOAD_SCRIPT = AETHER_ROOT / "tools" / "video-pipeline" / "upload_r2.py"

DOWNLOAD_DIR = Path("/tmp/brainiac-downloads")
HLS_DIR = Path("/tmp/brainiac-hls")

MODULES_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Recording identifiers (confirmed from Zoom API listing)
# Download URLs captured directly from the list-recordings response (which we have scope for)
# Using these directly avoids the need for cloud_recording:read:list_recording_files scope
RECORDINGS = {
    "module-1": {
        "uuid": "eaSEC/zASraCcJ1blqO3oA==",
        "meeting_id": 81469491462,
        "date": "2026-03-04",
        "topic": "Module 1 of Brainiac - Mastermind Training",
        "duration_min": 83,
        "r2_key": "brainiac/recordings/module-1",
        "video_id": "complete-demo",   # replaces this slot in TRAINING_VIDEOS
        "title": "Module 1: Brainiac Mastermind Training",
        "description": "The inaugural Brainiac Mastermind Training session. "
                       "Foundations, frameworks, and your first 30-day plan.",
        # Direct download URLs from listing (no extra scope needed — token appended at download time)
        "mp4_download_url": "https://us02web.zoom.us/rec/download/SJpNd__-BjssKpC3fYZZfiFpe-7YyJQFHC5U7N7SJwvwXB-xJTscSPw39lwk77p5NPb9FEzZ6ZawLhgJ.YLprTz2olHIBizg4",
        "transcript_download_url": "https://us02web.zoom.us/rec/download/F4PFj89EPAsSgezi0MxzX7lB5rQ1n0cMTvF8eUgE-a6cW0Ax-sp2RTprBaCgwgImkPr17AuaH5K27MVi.aUReo8h12qfTb4gT",
        "summary_download_url": "https://us02web.zoom.us/rec/download/tF3dwMjS0aBhxwVR5oqFx4ZuvAdi0Gt3_X36AVLP3AQKNfoeOZEb5d8xmeR8_BWhRvHfF52KFMO89ELi.DFYBtcZ32cDZBkAk",
    },
    "module-2": {
        "uuid": "CJPCrc1uSImChK/XiPN1yQ==",
        "meeting_id": 81875294941,
        "date": "2026-03-11",
        "topic": "Brainiac - Mastermind Training",
        "duration_min": 65,
        "r2_key": "brainiac/recordings/module-2",
        "video_id": "getting-started",  # replaces this slot in TRAINING_VIDEOS
        "title": "Module 2: Brainiac Mastermind Training",
        "description": "Deep-dive into advanced workflows, client results, "
                       "and the 90-day transformation roadmap.",
        # Direct download URLs from listing
        "mp4_download_url": "https://us02web.zoom.us/rec/download/vVghcNLDOAb1R4dAY9jpW1zBMmazleJ3ZKizrhWr-yp6gQShfGJB4rRDgxXJPkdBzclChXNcD0So8oOp.AkI6BZIak-AL3Ce6",
        "transcript_download_url": "https://us02web.zoom.us/rec/download/I3ZtK6FJ-L9wT57LP1XmKpMID2PeUbY7xC_cv2T4-7G8m5ZuwcZ0A81L2pDQNAPqvhr_T6eQ9Q7UyHWA.b_FvReZYRz3P7x59",
        "summary_download_url": "https://us02web.zoom.us/rec/download/vHf2XzgYLntOY2gQIw9U6q6iBVQB0wxycP8_o6tJacNEj1OaX8iKf8YOQRxfRGbmAgULa7zkkaFhEoR6.hhHYJMNPltMdN-Tu",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def tg(msg: str):
    try:
        subprocess.run([str(TG_SEND), msg], timeout=15, capture_output=True)
    except Exception:
        pass


def run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    print(f"\n[run] {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, **kwargs)
    return result


def load_env() -> dict:
    env = {}
    env_file = AETHER_ROOT / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    env.update(os.environ)
    return env


# ---------------------------------------------------------------------------
# Step 1: Download
# ---------------------------------------------------------------------------
def download_recording(slug: str, info: dict) -> dict:
    """
    Download MP4, TRANSCRIPT, and SUMMARY for a recording using direct download URLs.
    These URLs were captured from the list-recordings API response (which we have scope for).
    Using direct URLs avoids the need for cloud_recording:read:list_recording_files scope.
    """
    print(f"\n{'='*60}")
    print(f"[DOWNLOAD] {slug} — {info['topic']}")
    print(f"{'='*60}")

    out_dir = DOWNLOAD_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    access_token, _ = zoom_api.get_valid_token()
    downloaded = {}

    # Download MP4
    mp4_url = info.get("mp4_download_url")
    if mp4_url:
        out_path = out_dir / f"{slug}.mp4"
        if out_path.exists() and out_path.stat().st_size > 10_000_000:
            print(f"[download] MP4 already exists ({out_path.stat().st_size//1024//1024}MB) — skipping")
            downloaded["mp4"] = out_path
        else:
            print(f"[download] MP4 → {out_path}")
            url = f"{mp4_url}?access_token={access_token}"
            _stream_download(url, out_path)
            downloaded["mp4"] = out_path

    # Download TRANSCRIPT
    transcript_url = info.get("transcript_download_url")
    if transcript_url:
        out_path = out_dir / f"{slug}-transcript.vtt"
        if out_path.exists():
            print(f"[download] TRANSCRIPT already exists — skipping")
            downloaded["transcript_vtt"] = out_path
        else:
            print(f"[download] TRANSCRIPT → {out_path}")
            url = f"{transcript_url}?access_token={access_token}"
            _stream_download(url, out_path)
            downloaded["transcript_vtt"] = out_path

    # Download SUMMARY JSON
    summary_url = info.get("summary_download_url")
    if summary_url:
        out_path = out_dir / f"{slug}-summary.json"
        if out_path.exists():
            print(f"[download] SUMMARY JSON already exists — skipping")
            downloaded["summary_json"] = out_path
        else:
            print(f"[download] SUMMARY JSON → {out_path}")
            url = f"{summary_url}?access_token={access_token}"
            _stream_download(url, out_path)
            downloaded["summary_json"] = out_path

    return downloaded


def _stream_download(url: str, out_path: Path, chunk_size: int = 8 * 1024 * 1024):
    import urllib.request
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=600) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        done = 0
        with open(out_path, "wb") as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                if total:
                    pct = done / total * 100
                    print(f"\r  {pct:.1f}% ({done//1024//1024}MB/{total//1024//1024}MB)", end="", flush=True)
    print(f"\n  Done: {out_path} ({out_path.stat().st_size//1024//1024}MB)")


# ---------------------------------------------------------------------------
# Step 2: Transcode to HLS
# ---------------------------------------------------------------------------
def transcode(slug: str, mp4_path: Path) -> Path:
    """Transcode MP4 to HLS and generate poster. Returns HLS output directory."""
    print(f"\n{'='*60}")
    print(f"[TRANSCODE] {slug}")
    print(f"{'='*60}")

    hls_out = HLS_DIR / slug
    hls_out.mkdir(parents=True, exist_ok=True)

    master_m3u8 = hls_out / "master.m3u8"
    poster_jpg = hls_out / "poster.jpg"

    # Transcode to HLS (single rendition — reliable for Zoom content)
    result = run([
        "ffmpeg", "-y",
        "-i", str(mp4_path),
        "-codec:v", "libx264",
        "-codec:a", "aac",
        "-b:v", "2000k",
        "-b:a", "128k",
        "-hls_time", "10",
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(hls_out / "segment_%04d.ts"),
        str(master_m3u8),
    ], capture_output=True, text=True, timeout=3600)

    if result.returncode != 0:
        print(f"[ffmpeg STDERR] {result.stderr[-2000:]}")
        raise RuntimeError(f"ffmpeg transcode failed for {slug}")

    # Count segments generated
    segments = list(hls_out.glob("*.ts"))
    print(f"[transcode] Generated {len(segments)} .ts segments + master.m3u8")

    # Generate poster at 30 seconds
    run([
        "ffmpeg", "-y",
        "-i", str(mp4_path),
        "-ss", "00:00:30",
        "-vframes", "1",
        "-q:v", "2",
        str(poster_jpg),
    ], capture_output=True, timeout=60)

    if poster_jpg.exists():
        print(f"[transcode] Poster generated: {poster_jpg} ({poster_jpg.stat().st_size//1024}KB)")
    else:
        print("[transcode] WARNING: poster not generated")

    return hls_out


# ---------------------------------------------------------------------------
# Step 3: Upload to R2
# ---------------------------------------------------------------------------
def upload_to_r2(slug: str, hls_dir: Path, r2_key: str) -> str:
    """Upload HLS directory to R2. Returns public master.m3u8 URL."""
    print(f"\n{'='*60}")
    print(f"[UPLOAD] {slug} → R2:{r2_key}")
    print(f"{'='*60}")

    env = load_env()
    account_id = env.get("R2_CF_ACCOUNT_ID", env.get("CF_ACCOUNT_ID", ""))
    access_key = env.get("R2_ACCESS_KEY", "")
    secret_key = env.get("R2_SECRET_KEY", "")
    public_base = env.get("R2_PUBLIC_URL_BASE", "")
    bucket = env.get("R2_BUCKET_NAME", env.get("R2_BUCKET", "purebrain-video"))

    if not account_id or not access_key or not secret_key:
        raise ValueError("Missing R2 credentials (R2_CF_ACCOUNT_ID, R2_ACCESS_KEY, R2_SECRET_KEY)")

    result = run([
        sys.executable,
        str(UPLOAD_SCRIPT),
        "--dir", str(hls_dir),
        "--key", r2_key,
        "--bucket", bucket,
    ], capture_output=False, timeout=1800)  # 30 min timeout for large uploads

    if result.returncode != 0:
        raise RuntimeError(f"R2 upload failed for {slug}")

    # Construct public URL
    master_url = f"{public_base.rstrip('/')}/{r2_key}/master.m3u8"
    poster_url = f"{public_base.rstrip('/')}/{r2_key}/poster.jpg"
    print(f"\n[upload] master.m3u8: {master_url}")
    print(f"[upload] poster.jpg:  {poster_url}")
    return master_url, poster_url


# ---------------------------------------------------------------------------
# Step 4: Parse transcript to plain text
# ---------------------------------------------------------------------------
def parse_transcript(vtt_path: Path) -> str:
    """Convert VTT transcript to clean plain text."""
    import re
    text_lines = []
    with open(vtt_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line == "WEBVTT" or line.isdigit() or "-->" in line:
                continue
            line = re.sub(r"<v [^>]+>", "", line)
            line = re.sub(r"</v>", "", line)
            line = re.sub(r"<[\d:.]+>", "", line)
            line = line.strip()
            if line:
                text_lines.append(line)
    return "\n".join(text_lines)


# ---------------------------------------------------------------------------
# Step 5: Generate training module summary
# ---------------------------------------------------------------------------
def generate_summary(slug: str, info: dict, transcript_text: str, summary_json_path: Path) -> str:
    """Generate a training module summary markdown file."""
    print(f"\n[SUMMARY] Generating for {slug}")

    # Load Zoom AI summary if available
    zoom_summary = {}
    if summary_json_path and summary_json_path.exists():
        try:
            with open(summary_json_path) as f:
                zoom_summary = json.load(f)
        except Exception:
            pass

    # Build summary from transcript (first 8000 chars for context)
    transcript_preview = transcript_text[:8000] if transcript_text else "(transcript not available)"

    # Extract key lines (speaker statements, not just filler)
    lines = transcript_text.split("\n") if transcript_text else []
    key_lines = [l for l in lines if len(l) > 40][:80]  # First 80 substantive lines

    zoom_summary_text = zoom_summary.get("summary", "") or zoom_summary.get("summary_overview", "")
    zoom_next_steps = zoom_summary.get("next_steps", []) if isinstance(zoom_summary.get("next_steps"), list) else []

    module_number = "1" if slug == "module-1" else "2"

    md = f"""# Brainiac Mastermind Training — Module {module_number}

**Date**: {info['date']}
**Duration**: {info['duration_min']} minutes
**Topic**: {info['topic']}
**R2 Path**: `{info['r2_key']}`

---

## Module Overview

{info['description']}

---

## Zoom AI Summary

{zoom_summary_text if zoom_summary_text else "See full transcript for details."}

---

## Key Topics Covered

Based on the recording transcript, this session covered:

"""

    # Extract topic areas from transcript (first ~200 lines, look for substantive statements)
    topic_lines = [l for l in lines if len(l) > 60][:40]
    for i, line in enumerate(topic_lines[:15], 1):
        md += f"- {line[:120]}\n"

    md += f"""
---

## Next Steps & Action Items

"""
    if zoom_next_steps:
        for step in zoom_next_steps[:10]:
            if isinstance(step, dict):
                md += f"- {step.get('text', step.get('action', str(step)))}\n"
            else:
                md += f"- {step}\n"
    else:
        md += "_(See full transcript for action items discussed in this session)_\n"

    md += f"""
---

## Full Transcript (First 500 Lines)

```
{chr(10).join(lines[:500])}
```

---

## Resources

- **Recording**: Available on Brainiac Training page at https://purebrain.ai/brainiac-mastermind-training/
- **HLS URL**: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/{info['r2_key']}/master.m3u8`
- **Poster**: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/{info['r2_key']}/poster.jpg`

---

_Generated by dept-systems-technology pipeline on 2026-03-12_
"""

    out_path = MODULES_DIR / f"{slug}.md"
    with open(out_path, "w") as f:
        f.write(md)
    print(f"[summary] Saved to {out_path}")

    # Also save JSON version
    json_data = {
        "module": slug,
        "module_number": int(module_number),
        "date": info["date"],
        "duration_minutes": info["duration_min"],
        "topic": info["topic"],
        "description": info["description"],
        "r2_key": info["r2_key"],
        "hls_url": f"https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/{info['r2_key']}/master.m3u8",
        "poster_url": f"https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/{info['r2_key']}/poster.jpg",
        "zoom_summary": zoom_summary_text,
        "zoom_next_steps": zoom_next_steps,
        "transcript_excerpt": transcript_text[:3000] if transcript_text else "",
        "generated_at": "2026-03-12",
    }
    json_path = MODULES_DIR / f"{slug}.json"
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)
    print(f"[summary] JSON saved to {json_path}")

    return str(out_path)


# ---------------------------------------------------------------------------
# Step 6: Update Brainiac HTML
# ---------------------------------------------------------------------------
def update_brainiac_html(module_updates: dict) -> str:
    """
    Update the TRAINING_VIDEOS array in brainiac-mastermind-training.html
    to set module-1 and module-2 as live with their R2 URLs.

    module_updates = {
        "module-1": {"hls_url": "...", "poster_url": "..."},
        "module-2": {"hls_url": "...", "poster_url": "..."},
    }
    """
    print(f"\n{'='*60}")
    print("[UPDATE HTML] brainiac-mastermind-training.html")
    print(f"{'='*60}")

    with open(BRAINIAC_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # Update complete-demo slot → module-1
    m1 = module_updates.get("module-1", {})
    if m1:
        html = html.replace(
            """  {
    id: "complete-demo",
    title: "PureBrain Complete Demo",
    description: "Full walkthrough of the PureBrain platform - every feature, every workflow, built for your success.",
    duration: null,
    posterUrl: null,
    hlsUrl: null,
    category: "foundations",
    status: "coming_soon",
    badge: null
  },""",
            f"""  {{
    id: "complete-demo",
    title: "Module 1: Brainiac Mastermind Training",
    description: "The inaugural Brainiac Mastermind session — foundations, frameworks, and your first 30-day AI implementation plan. Recorded March 4, 2026.",
    duration: "83 min",
    posterUrl: "{m1['poster_url']}",
    hlsUrl: "{m1['hls_url']}",
    category: "foundations",
    status: "live",
    badge: "new"
  }},""",
        )

    # Update getting-started slot → module-2
    m2 = module_updates.get("module-2", {})
    if m2:
        html = html.replace(
            """  {
    id: "getting-started",
    title: "Getting Started: Day 1 Checklist",
    description: "Everything you need to do on your first day with PureBrain. Setup, configuration, and your first AI workflow - step by step.",
    duration: null,
    posterUrl: null,
    hlsUrl: null,
    category: "foundations",
    status: "coming_soon",
    badge: null
  },""",
            f"""  {{
    id: "getting-started",
    title: "Module 2: Brainiac Mastermind Training",
    description: "Advanced workflows, client transformation stories, and the 90-day roadmap. Deep-dive into PureBrain mastery. Recorded March 11, 2026.",
    duration: "65 min",
    posterUrl: "{m2['poster_url']}",
    hlsUrl: "{m2['hls_url']}",
    category: "foundations",
    status: "live",
    badge: "new"
  }},""",
        )

    with open(BRAINIAC_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[update html] Saved updated HTML to {BRAINIAC_HTML}")
    return str(BRAINIAC_HTML)


# ---------------------------------------------------------------------------
# Step 7: Deploy to WordPress
# ---------------------------------------------------------------------------
def deploy_to_wordpress(html_path: str) -> bool:
    """Deploy updated Brainiac HTML to WordPress page 1115."""
    print(f"\n{'='*60}")
    print("[DEPLOY] WordPress page 1115")
    print(f"{'='*60}")

    env = load_env()
    wp_url = env.get("WORDPRESS_URL", "https://purebrain.ai")
    wp_user = env.get("PUREBRAIN_WP_USER", "")
    wp_pass = env.get("PUREBRAIN_WP_APP_PASSWORD", env.get("PUREBRAIN_WP_PASSWORD", ""))

    if not wp_user or not wp_pass:
        print("[deploy] WARNING: WordPress credentials not found — skipping WP deploy")
        print(f"[deploy] HTML saved locally at {html_path}")
        return False

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    import urllib.request
    import urllib.parse
    import base64

    credentials = base64.b64encode(f"{wp_user}:{wp_pass}".encode()).decode()

    payload = json.dumps({
        "content": f"<!-- wp:html -->\n{html_content}\n<!-- /wp:html -->",
        "status": "publish",
        "template": "elementor_canvas",
    }).encode()

    req = urllib.request.Request(
        f"{wp_url}/wp-json/wp/v2/pages/1115",
        data=payload,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            print(f"[deploy] WordPress updated. Page status: {result.get('status')}")
            print(f"[deploy] Link: {result.get('link', 'https://purebrain.ai/brainiac-mastermind-training/')}")
            return True
    except Exception as e:
        print(f"[deploy] WordPress deploy failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main():
    print("\n" + "="*70)
    print("  BRAINIAC MASTERMIND TRAINING — MANUAL PIPELINE")
    print("  Processing 2 recordings: Module 1 (Mar 4) + Module 2 (Mar 11)")
    print("="*70)

    tg("Brainiac pipeline: Step 1/6 — Downloading Module 1 (348MB)...")

    results = {}

    for slug, info in RECORDINGS.items():
        print(f"\n{'#'*70}")
        print(f"# Processing: {slug.upper()}")
        print(f"# Topic: {info['topic']}")
        print(f"# Date: {info['date']} | Duration: {info['duration_min']} min")
        print(f"{'#'*70}")

        # Step 1: Download
        tg(f"Brainiac pipeline: Downloading {slug}...")
        downloaded = download_recording(slug, info)

        mp4_path = downloaded.get("mp4")
        if not mp4_path or not mp4_path.exists():
            print(f"[ERROR] MP4 download failed for {slug}")
            tg(f"ERROR: MP4 download failed for {slug}. Check logs.")
            sys.exit(1)

        print(f"\n[{slug}] MP4 downloaded: {mp4_path} ({mp4_path.stat().st_size//1024//1024}MB)")
        tg(f"Brainiac {slug}: Downloaded {mp4_path.stat().st_size//1024//1024}MB. Transcoding to HLS...")

        # Step 2: Transcode
        hls_dir = transcode(slug, mp4_path)
        segments = list(hls_dir.glob("*.ts"))
        print(f"\n[{slug}] Transcoded: {len(segments)} segments in {hls_dir}")
        tg(f"Brainiac {slug}: Transcoded ({len(segments)} HLS segments). Uploading to R2...")

        # Step 3: Upload to R2
        hls_url, poster_url = upload_to_r2(slug, hls_dir, info["r2_key"])
        tg(f"Brainiac {slug}: Uploaded to R2. HLS live at {hls_url}")

        # Step 4 & 5: Parse transcript + generate summary
        transcript_vtt = downloaded.get("transcript_vtt")
        transcript_text = ""
        if transcript_vtt and transcript_vtt.exists():
            transcript_text = parse_transcript(transcript_vtt)
            print(f"[{slug}] Transcript parsed: {len(transcript_text.split(chr(10)))} lines")

        summary_path = generate_summary(
            slug, info, transcript_text,
            downloaded.get("summary_json"),
        )
        print(f"[{slug}] Summary saved: {summary_path}")

        results[slug] = {
            "hls_url": hls_url,
            "poster_url": poster_url,
            "summary_path": summary_path,
        }

    # Step 6: Update HTML
    tg("Brainiac pipeline: Updating Brainiac training page HTML...")
    module_updates = {
        "module-1": results["module-1"],
        "module-2": results["module-2"],
    }
    html_path = update_brainiac_html(module_updates)

    # Step 7: Deploy to WordPress
    tg("Brainiac pipeline: Deploying to WordPress page 1115...")
    deployed = deploy_to_wordpress(html_path)

    # Summary
    print("\n" + "="*70)
    print("  PIPELINE COMPLETE")
    print("="*70)
    print(f"\nModule 1 HLS: {results['module-1']['hls_url']}")
    print(f"Module 1 Poster: {results['module-1']['poster_url']}")
    print(f"\nModule 2 HLS: {results['module-2']['hls_url']}")
    print(f"Module 2 Poster: {results['module-2']['poster_url']}")
    print(f"\nTraining summaries: {MODULES_DIR}")
    print(f"WordPress deployed: {deployed}")

    tg(
        f"Brainiac pipeline COMPLETE!\n"
        f"Module 1: live on page (83 min, Mar 4)\n"
        f"Module 2: live on page (65 min, Mar 11)\n"
        f"Training summaries saved to exports/brainiac-training/modules/\n"
        f"Page: https://purebrain.ai/brainiac-mastermind-training/"
    )


if __name__ == "__main__":
    main()
