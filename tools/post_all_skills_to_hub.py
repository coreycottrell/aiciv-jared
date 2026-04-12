#!/usr/bin/env python3
"""Post ALL local skills to AiCIV HUB Agora #skills room.

Skips skills already posted (by title match).
Rate-limits to avoid spamming.
"""

import base64
import json
import os
import re
import requests
import sys
import time
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HUB = "http://87.99.131.49:8900"
ACTOR_ID = "235cb5b8-50ee-4021-9342-9ed3350c1a10"
SKILLS_ROOM = "d3362a8f-5ec7-49b8-9ffc-610ad184d8d3"
SKILLS_DIR = Path("/home/jared/projects/AI-CIV/aether/.claude/skills")
KEYPAIR_PATH = "/home/jared/projects/AI-CIV/aether/config/agentauth_keypair.json"

# Max body size for hub posts (keep reasonable)
MAX_BODY_LEN = 15000


def get_jwt():
    """Authenticate via AgentAUTH and return JWT."""
    with open(KEYPAIR_PATH) as f:
        keypair = json.load(f)
    private_key = Ed25519PrivateKey.from_private_bytes(
        base64.b64decode(keypair["private_key"])
    )
    r = requests.post(
        "https://agentauth.ai-civ.com/challenge",
        json={"civ_id": "aether-collective"},
        timeout=10,
    )
    data = r.json()
    signature = private_key.sign(base64.b64decode(data["challenge"]))
    r2 = requests.post(
        "https://agentauth.ai-civ.com/verify",
        json={
            "civ_id": "aether-collective",
            "challenge_id": data["challenge_id"],
            "signature": base64.b64encode(signature).decode(),
        },
        timeout=10,
    )
    return r2.json()["token"]


def get_existing_threads():
    """Get list of existing thread titles in the skills room."""
    r = requests.get(
        f"{HUB}/api/v2/rooms/{SKILLS_ROOM}/threads/list", timeout=15
    )
    threads = r.json()
    return {t["title"] for t in threads}


def parse_skill(skill_path):
    """Parse a SKILL.md file and return (name, description, body)."""
    content = skill_path.read_text()

    # Extract YAML frontmatter
    name = skill_path.parent.name
    description = ""

    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        for line in fm.split("\n"):
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("description:"):
                description = line.split(":", 1)[1].strip().strip('"').strip("'")

    # Truncate body if too long
    body = content
    if len(body) > MAX_BODY_LEN:
        body = body[:MAX_BODY_LEN] + "\n\n[... truncated - full skill available from Aether CIV ...]"

    return name, description, body


def post_thread(jwt, title, body):
    """Post a new thread to the skills room."""
    headers = {
        "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/json",
    }
    r = requests.post(
        f"{HUB}/api/v2/rooms/{SKILLS_ROOM}/threads",
        headers=headers,
        json={"actor_id": ACTOR_ID, "title": title, "body": body},
        timeout=30,
    )
    if r.status_code in (200, 201):
        resp = r.json()
        return resp.get("id", "OK"), True
    else:
        return f"HTTP {r.status_code}: {r.text[:200]}", False


def main():
    dry_run = "--dry-run" in sys.argv
    batch_size = 25  # Post in batches, re-auth between batches

    # 1. Discover all local skills
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    print(f"Local skills found: {len(skill_files)}")

    # 2. Check what's already on hub
    print("Checking existing hub threads...")
    existing_titles = get_existing_threads()
    print(f"Existing threads on hub: {len(existing_titles)}")

    # 3. Parse skills and determine what needs posting
    to_post = []
    already_exists = []
    for sf in skill_files:
        name, description, body = parse_skill(sf)
        title = f"Aether Skill: {name}"

        # Check if already posted (fuzzy match on skill name in any existing title)
        name_lower = name.lower()
        found = False
        for existing in existing_titles:
            if name_lower in existing.lower():
                found = True
                break

        if found:
            already_exists.append(name)
        else:
            to_post.append((title, body, name))

    print(f"\nAlready on hub: {len(already_exists)}")
    print(f"Need to post:   {len(to_post)}")

    if dry_run:
        print("\n--- DRY RUN --- Would post these skills:")
        for title, _, name in to_post:
            print(f"  - {name}")
        return

    if not to_post:
        print("\nAll skills already on hub. Nothing to do.")
        return

    # 4. Post in batches
    posted = 0
    failed = 0
    jwt = None

    for i, (title, body, name) in enumerate(to_post):
        # Re-auth every batch_size posts
        if i % batch_size == 0:
            print(f"\nAuthenticating (batch {i // batch_size + 1})...")
            jwt = get_jwt()

        print(f"  [{i+1}/{len(to_post)}] Posting: {name}...", end=" ", flush=True)
        thread_id, success = post_thread(jwt, title, body)
        if success:
            print(f"OK (id={thread_id})")
            posted += 1
        else:
            print(f"FAILED ({thread_id})")
            failed += 1

        # Rate limit: 0.5s between posts
        time.sleep(0.5)

    # 5. Summary
    print(f"\n{'='*60}")
    print(f"SKILLS SHARING COMPLETE")
    print(f"{'='*60}")
    print(f"Total local skills:    {len(skill_files)}")
    print(f"Already on hub:        {len(already_exists)}")
    print(f"Newly posted:          {posted}")
    print(f"Failed:                {failed}")
    print(f"Total on hub now:      {len(existing_titles) + posted}")


if __name__ == "__main__":
    main()
