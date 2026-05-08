#!/usr/bin/env python3
"""
migrate_blog_audios_to_chatterbox.py

Process ONE pending post per run from blog-audio-migration-queue.json. Backs up the
ElevenLabs original as audio.mp3.bak-elevenlabs-YYYY-MM-DD, regenerates with the
canonical Chatterbox `aether` voice via tools/blog_audio_chatterbox.py, and deploys
the single file via tools/cf-deploy.py.

Designed to be run once per day by a BOOP so GPU load stays low.

Usage:
    python3 tools/migrate_blog_audios_to_chatterbox.py            # process next 1
    python3 tools/migrate_blog_audios_to_chatterbox.py --count 2  # process N
    python3 tools/migrate_blog_audios_to_chatterbox.py --dry-run
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / ".claude/scheduled-tasks/blog-audio-migration-queue.json"
BLOG_ROOT = ROOT / "exports/cf-pages-deploy/blog"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(QUEUE.read_text())
    pending = [p for p in data["posts"] if p.get("status") == "pending"]
    if not pending:
        print("[migrate] queue empty — all posts migrated")
        return 0

    today = datetime.date.today().isoformat()
    processed = 0

    for post in pending[: args.count]:
        slug = post["slug"]
        post_dir = BLOG_ROOT / slug
        audio = post_dir / "audio.mp3"
        html = post_dir / "index.html"

        if not html.exists():
            print(f"[migrate] SKIP {slug} — no index.html")
            post["status"] = "skipped:no_html"
            continue

        backup = post_dir / f"audio.mp3.bak-elevenlabs-{today}"
        print(f"[migrate] {slug}")
        print(f"  backup -> {backup.name}")

        if args.dry_run:
            print("  (dry-run) skipping actual work")
            continue

        if audio.exists() and audio.stat().st_size > 1000:
            audio.rename(backup)

        # Regenerate via canonical pipeline
        cmd = [
            sys.executable,
            str(ROOT / "tools/blog_audio_chatterbox.py"),
            "--html", str(html),
            "--output", str(audio),
        ]
        result = subprocess.run(cmd, cwd=str(ROOT))
        if result.returncode != 0:
            print(f"  FAIL — restoring backup")
            if backup.exists():
                backup.rename(audio)
            post["status"] = "failed"
            post["last_error_date"] = today
            continue

        # Deploy just this file
        rel = f"blog/{slug}/audio.mp3"
        deploy = subprocess.run(
            [sys.executable, str(ROOT / "tools/cf-deploy.py"), rel,
             "-m", f"Migrate blog audio to Chatterbox aether: {slug}"],
            cwd=str(ROOT),
        )
        if deploy.returncode != 0:
            print(f"  DEPLOY FAIL")
            post["status"] = "deploy_failed"
            post["last_error_date"] = today
            continue

        post["status"] = "done"
        post["migrated_date"] = today
        post["new_size_bytes"] = audio.stat().st_size
        processed += 1

    # Save queue state
    if not args.dry_run:
        QUEUE.write_text(json.dumps(data, indent=2) + "\n")

    print(f"[migrate] processed={processed} remaining={len([p for p in data['posts'] if p.get('status')=='pending'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
