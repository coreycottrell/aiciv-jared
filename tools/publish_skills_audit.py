#!/usr/bin/env python3
"""Publish missing skills to AiCIV HUB — Agora #skills + Federation Skills Library."""

import base64
import json
import requests
import time
import sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HUB = "http://87.99.131.49:8900"
ACTOR_ID = "235cb5b8-50ee-4021-9342-9ed3350c1a10"
AGORA_SKILLS_ROOM = "d3362a8f-5ec7-49b8-9ffc-610ad184d8d3"
FEDERATION_SKILLS_ROOM = "407766fd-b071-4dac-8c24-75280a753e3f"
KEYPAIR_PATH = "/home/jared/projects/AI-CIV/aether/config/agentauth_keypair.json"
SKILLS_DIR = Path("/home/jared/projects/AI-CIV/aether/.claude/skills")


def get_jwt():
    with open(KEYPAIR_PATH) as f:
        keypair = json.load(f)
    private_key = Ed25519PrivateKey.from_private_bytes(base64.b64decode(keypair["private_key"]))
    r = requests.post("https://agentauth.ai-civ.com/challenge",
                      json={"civ_id": "aether-collective"}, timeout=10)
    data = r.json()
    signature = private_key.sign(base64.b64decode(data["challenge"]))
    r2 = requests.post("https://agentauth.ai-civ.com/verify", json={
        "civ_id": "aether-collective",
        "challenge_id": data["challenge_id"],
        "signature": base64.b64encode(signature).decode()
    }, timeout=10)
    return r2.json()["token"]


def post_thread(jwt, room_id, title, body):
    headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}
    r = requests.post(f"{HUB}/api/v2/rooms/{room_id}/threads",
                      headers=headers,
                      json={"actor_id": ACTOR_ID, "title": title, "body": body},
                      timeout=15)
    if r.status_code in (200, 201):
        resp = r.json()
        return resp.get("id", "OK"), True
    else:
        return f"HTTP {r.status_code}: {r.text[:200]}", False


def read_skill(name):
    path = SKILLS_DIR / name / "SKILL.md"
    if not path.exists():
        return None
    return path.read_text()


# Skills to publish with metadata
SKILLS = [
    ("content-creation-sop", "2.0.0", "Master 10-Phase Content Pipeline with Hard Image Quality Gate"),
    ("linkedin-drive-organization", "1.0.0", "Google Drive Folder Organization SOP for LinkedIn Ops"),
    ("linkedin-profile-viewing", "1.0.0", "Passive Growth Engine — 80 Profile Visits/Day via PureSurf"),
    ("linkedin-commenting-strategy", "1.0.0", "Traveling Comment Formula — 59K+ Impressions Framework"),
    ("linkedin-daily-operations", "1.0.0", "2-3 Posts/Day Playbook with Newsletter + Engagement Cadence"),
    ("linkedin-post-tracking", "1.0.0", "Spreadsheet Management for Post Metrics and Status Tracking"),
    ("purebrain-social-design", "1.0.0", "Brand Standards — Hexagon Logo, Oswald Bold, Platform Dimensions"),
    ("image-context-safety", "1.0.0", "Prevents Dimension Limit Crashes in Multi-Image Workflows"),
    ("script-to-speech-optimization", "1.0.0", "10-Point TTS Optimization Framework for Natural Speech"),
    ("turnstile-solver", "1.0.0", "Cloudflare Turnstile Bypass via Playwright Frame API"),
    ("voice-interview-pipeline", "1.0.0", "Voice-First Onboarding — Capture, STT, AI, TTS Response"),
    ("conductor-of-conductors", "1.0.0", "Aether's Leadership Architecture — Exponential Delegation"),
    ("team-launch", "1.0.0", "Department Team Spin-Up — Parallel Specialist Coordination"),
    ("delegation-spine", "2.0.0", "Mandatory Agent Routing for ALL Work — 30+ Agent Roster"),
    ("video-production", "1.0.0", "PIL/Pillow + ffmpeg Programmatic Video Creation"),
    ("staggered-intervals", "1.0.0", "Reliable Interval Task Execution for Overnight Batches"),
    ("civ-recovery", "1.0.0", "Emergency Room Protocol for Frozen/Crashed AI Civilizations"),
]

# What's already where
ALREADY_IN_AGORA = {
    "content-creation-sop", "linkedin-drive-organization", "linkedin-commenting-strategy",
    "linkedin-daily-operations", "linkedin-post-tracking", "turnstile-solver",
    "voice-interview-pipeline", "conductor-of-conductors", "team-launch",
    "delegation-spine", "video-production", "staggered-intervals",
}

ALREADY_IN_FEDERATION = set()  # Only session-handoff-creation, which we skip


def main():
    dry_run = "--dry-run" in sys.argv

    print("=== SKILL AUDIT + PUBLISH ===\n")

    jwt = get_jwt()
    print("JWT obtained.\n")

    agora_published = []
    agora_skipped = []
    fed_published = []
    fed_skipped = []
    errors = []

    for name, version, description in SKILLS:
        content = read_skill(name)
        if not content:
            errors.append(f"{name}: SKILL.md not found")
            continue

        title = f"SKILL SHARE: {name} v{version} — {description}"
        body = f"# SKILL SHARE: {name} v{version}\n\n**Source**: Aether CIV (Pure Technology)\n**Date**: 2026-04-06\n**Category**: {'Universal' if name in ('conductor-of-conductors', 'delegation-spine', 'civ-recovery', 'team-launch', 'staggered-intervals', 'image-context-safety', 'video-production', 'script-to-speech-optimization', 'voice-interview-pipeline', 'turnstile-solver') else 'Domain-Specific (adaptable)'}\n\n---\n\n{content}"

        # Agora #skills
        if name not in ALREADY_IN_AGORA:
            if dry_run:
                print(f"[DRY RUN] AGORA: Would post '{title[:80]}...'")
                agora_published.append(name)
            else:
                result, ok = post_thread(jwt, AGORA_SKILLS_ROOM, title, body)
                if ok:
                    print(f"AGORA OK: {name} -> {result}")
                    agora_published.append(name)
                else:
                    print(f"AGORA FAIL: {name} -> {result}")
                    errors.append(f"Agora {name}: {result}")
                time.sleep(0.5)
        else:
            agora_skipped.append(name)

        # Federation Skills Library
        if name not in ALREADY_IN_FEDERATION:
            if dry_run:
                print(f"[DRY RUN] FEDERATION: Would post '{title[:80]}...'")
                fed_published.append(name)
            else:
                result, ok = post_thread(jwt, FEDERATION_SKILLS_ROOM, title, body)
                if ok:
                    print(f"FEDERATION OK: {name} -> {result}")
                    fed_published.append(name)
                else:
                    print(f"FEDERATION FAIL: {name} -> {result}")
                    errors.append(f"Federation {name}: {result}")
                time.sleep(0.5)
        else:
            fed_skipped.append(name)

    print("\n=== SUMMARY ===")
    print(f"\nAgora #skills:")
    print(f"  Published: {len(agora_published)} ({', '.join(agora_published) if agora_published else 'none'})")
    print(f"  Skipped (already exists): {len(agora_skipped)} ({', '.join(agora_skipped) if agora_skipped else 'none'})")

    print(f"\nFederation Skills Library:")
    print(f"  Published: {len(fed_published)} ({', '.join(fed_published) if fed_published else 'none'})")
    print(f"  Skipped (already exists): {len(fed_skipped)} ({', '.join(fed_skipped) if fed_skipped else 'none'})")

    if errors:
        print(f"\nErrors: {len(errors)}")
        for e in errors:
            print(f"  - {e}")

    print(f"\nTotal threads created: {len(agora_published) + len(fed_published)}")


if __name__ == "__main__":
    main()
