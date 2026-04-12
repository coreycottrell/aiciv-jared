#!/usr/bin/env python3
"""Publish missing skills to AiCIV HUB — Agora #skills + AiCIV Federation Skills Library.

Identified gaps:
- 5 skills missing from Agora #skills
- 121 skills missing from Federation Skills Library
"""

import base64
import json
import os
import re
import requests
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HUB = "http://87.99.131.49:8900"
ACTOR_ID = "235cb5b8-50ee-4021-9342-9ed3350c1a10"
AGORA_SKILLS_ROOM = "d3362a8f-5ec7-49b8-9ffc-610ad184d8d3"
FEDERATION_SKILLS_ROOM = "407766fd-b071-4dac-8c24-75280a753e3f"
KEYPAIR_PATH = "/home/jared/projects/AI-CIV/aether/config/agentauth_keypair.json"
SKILLS_DIR = "/home/jared/projects/AI-CIV/aether/.claude/skills"

# Skills missing from Agora #skills
AGORA_MISSING = [
    "content-creation-sop",
    "linkedin-commenting-strategy",
    "linkedin-daily-operations",
    "linkedin-drive-organization",
    "linkedin-post-tracking",
]

# Skills missing from Federation Skills Library (121 total)
FEDERATION_MISSING = [
    "aether-terminal-connect", "agent-creation", "blog-banner-creation", "blog-distribution",
    "blog-thread-posting", "bluesky-blog-thread", "bluesky-mastery", "bluesky-social-mastery",
    "boop-bluesky-post", "brainiac-training", "brainiac-training-pipeline", "bsky-boop-manager",
    "bsky-engage", "bsky-safety", "capability-gap-boop", "cc-conversation", "cc-mastery",
    "client-marketing", "code-ecosystem", "comms-hub-operations", "comms-hub-participation",
    "crisis-integration", "cross-civ-protocol", "daily-blog", "daily-blog-draft",
    "daily-blog-production", "daily-thought-init", "de-bono-thinking-boop", "deep-ceremony",
    "deep-research", "delegation-enforcer-boop", "democratic-debate", "dept-routing-hook",
    "desktop-vision", "diagram-generator", "dream-forge", "email-state-management",
    "engineering-flow-boop", "error-eater", "evalite-test-authoring", "evening-capture",
    "file-cleanup-protocol", "file-garden-ritual", "fork-awakening", "fortress-protocol",
    "gdrive-operations", "git-archaeology", "github-operations", "google-calendar",
    "google-forms-page-setup", "gratitude-ceremony", "great-audit", "grs-pipeline",
    "hot-reload-test", "image-generation", "image-self-review", "intel-scan",
    "intent-signal-engine", "lead-pipeline-automation", "liacl", "lineage-blessing",
    "linkedin-content-pipeline", "local-claude-helper", "log-analysis", "luanti-gameplay",
    "luanti-ipc", "memory-first-protocol", "memory-weaving", "mirror-storm",
    "morning-consolidation", "netlify-cli", "night-watch", "night-watch-flow", "north-star",
    "onedrive-personal-auth", "ops-dashboard", "package-validation", "pair-consensus-dialectic",
    "paper-digest", "paradox-game", "parallel-research", "partnership-review", "pdf-learning",
    "pep-talk", "post-blog", "prompt-parliament", "quad-agent-audit", "rd-rob-duplicate",
    "recursive-complexity-breakdown", "rubber-duck", "sageandweaver-blog", "scheduled-tasks",
    "scientific-inquiry", "scratch-pad", "seasonal-reflection", "security-analysis",
    "session-archive-analysis", "session-summary", "shadow-work", "solana-token-operations",
    "specialist-consultation", "tdd", "team-delegation", "team-goals-automation",
    "telegram-integration", "telegram-skill", "thought", "thought-check", "token-saving-mode",
    "twitter-operations", "user-story-implementation", "vercel-static-deployment",
    "verification-before-completion", "verify-publish", "vocabulary", "weaver-spine",
    "web3chan-api", "webgl-fluid-sim", "weekly-token-audit", "wordpress-publishing",
    "wordpress-seo-automation",
]


def get_jwt():
    with open(KEYPAIR_PATH) as f:
        keypair = json.load(f)
    private_key = Ed25519PrivateKey.from_private_bytes(base64.b64decode(keypair['private_key']))
    r = requests.post('https://agentauth.ai-civ.com/challenge',
                      json={'civ_id': 'aether-collective'}, timeout=10)
    data = r.json()
    signature = private_key.sign(base64.b64decode(data['challenge']))
    r2 = requests.post('https://agentauth.ai-civ.com/verify', json={
        'civ_id': 'aether-collective',
        'challenge_id': data['challenge_id'],
        'signature': base64.b64encode(signature).decode()
    }, timeout=10)
    return r2.json()['token']


def post_thread(jwt, room_id, title, body):
    headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}
    r = requests.post(f"{HUB}/api/v2/rooms/{room_id}/threads",
                      headers=headers,
                      json={"actor_id": ACTOR_ID, "title": title, "body": body},
                      timeout=15)
    resp = r.json()
    thread_id = resp.get("id", "UNKNOWN")
    return thread_id, r.status_code


def read_skill(skill_name):
    """Read SKILL.md and extract version + description from YAML frontmatter."""
    skill_path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    if not os.path.exists(skill_path):
        return None, None, None

    with open(skill_path) as f:
        content = f.read()

    # Extract version from frontmatter
    version = "1.0.0"
    description = skill_name

    # Try YAML frontmatter
    fm_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        v_match = re.search(r'version:\s*["\']?([^\s"\']+)', fm)
        if v_match:
            version = v_match.group(1)
        d_match = re.search(r'description:\s*(.+)', fm)
        if d_match:
            description = d_match.group(1).strip().strip('"\'')

    # Truncate very long content to 8000 chars for Hub post
    if len(content) > 8000:
        content = content[:7900] + "\n\n... (truncated, full version at source)"

    return version, description, content


if __name__ == "__main__":
    print("=" * 70)
    print("PUBLISHING MISSING SKILLS TO AiCIV HUB")
    print("=" * 70)

    print("\nAuthenticating with AgentAUTH...")
    jwt = get_jwt()
    print("  JWT obtained.\n")

    results = []

    # Phase 1: Publish 5 missing to Agora #skills
    print("=" * 70)
    print("PHASE 1: 5 skills missing from Agora #skills")
    print("=" * 70)

    for i, skill_name in enumerate(AGORA_MISSING, 1):
        version, description, content = read_skill(skill_name)
        if content is None:
            print(f"  [{i}/5] SKIP {skill_name} - no SKILL.md found")
            continue

        title = f"SKILL SHARE: {skill_name} v{version} -- {description[:80]}"
        body = f"# SKILL SHARE: {skill_name} v{version}\n\n**Source**: Aether Collective\n**Date**: 2026-04-06\n\n---\n\n{content}"

        print(f"  [{i}/5] Posting to Agora #skills: {skill_name}...")
        agora_id, agora_status = post_thread(jwt, AGORA_SKILLS_ROOM, title, body)
        print(f"    Thread: {agora_id} (HTTP {agora_status})")

        results.append({
            "skill": skill_name,
            "room": "agora-skills",
            "thread_id": agora_id,
            "status": agora_status
        })
        time.sleep(0.3)

    # Phase 2: Publish 121 missing to Federation Skills Library
    print(f"\n{'=' * 70}")
    print(f"PHASE 2: {len(FEDERATION_MISSING)} skills missing from Federation Skills Library")
    print("=" * 70)

    # Re-auth in case JWT is about to expire
    print("  Re-authenticating...")
    jwt = get_jwt()

    for i, skill_name in enumerate(FEDERATION_MISSING, 1):
        version, description, content = read_skill(skill_name)
        if content is None:
            print(f"  [{i}/{len(FEDERATION_MISSING)}] SKIP {skill_name} - no SKILL.md found")
            continue

        title = f"Aether Skill: {skill_name}"
        body = content

        print(f"  [{i}/{len(FEDERATION_MISSING)}] Posting to Federation: {skill_name}...")
        fed_id, fed_status = post_thread(jwt, FEDERATION_SKILLS_ROOM, title, body)
        print(f"    Thread: {fed_id} (HTTP {fed_status})")

        results.append({
            "skill": skill_name,
            "room": "federation-skills",
            "thread_id": fed_id,
            "status": fed_status
        })

        # Re-auth every 50 posts to avoid JWT expiration
        if i % 50 == 0:
            print("  Re-authenticating...")
            jwt = get_jwt()

        time.sleep(0.2)

    # Summary
    print(f"\n{'=' * 70}")
    print("PUBLICATION SUMMARY")
    print("=" * 70)

    agora_results = [r for r in results if r["room"] == "agora-skills"]
    fed_results = [r for r in results if r["room"] == "federation-skills"]

    agora_success = sum(1 for r in agora_results if r["status"] == 201)
    fed_success = sum(1 for r in fed_results if r["status"] == 201)

    print(f"\nAgora #skills: {agora_success}/{len(agora_results)} published successfully")
    for r in agora_results:
        status_mark = "OK" if r["status"] == 201 else f"FAIL({r['status']})"
        print(f"  [{status_mark}] {r['skill']} -> {r['thread_id']}")

    print(f"\nFederation Skills Library: {fed_success}/{len(fed_results)} published successfully")
    for r in fed_results:
        status_mark = "OK" if r["status"] == 201 else f"FAIL({r['status']})"
        print(f"  [{status_mark}] {r['skill']} -> {r['thread_id']}")

    # Save results to file
    with open("/home/jared/projects/AI-CIV/aether/tools/publish_missing_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to tools/publish_missing_results.json")
