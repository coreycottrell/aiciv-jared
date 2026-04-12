#!/usr/bin/env python3
"""Retry the 22 skills that got 429 rate-limited on Federation Skills Library."""

import base64
import json
import os
import re
import requests
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HUB = "http://87.99.131.49:8900"
ACTOR_ID = "235cb5b8-50ee-4021-9342-9ed3350c1a10"
FEDERATION_SKILLS_ROOM = "407766fd-b071-4dac-8c24-75280a753e3f"
KEYPAIR_PATH = "/home/jared/projects/AI-CIV/aether/config/agentauth_keypair.json"
SKILLS_DIR = "/home/jared/projects/AI-CIV/aether/.claude/skills"

RETRY_SKILLS = [
    "pep-talk", "post-blog", "prompt-parliament", "quad-agent-audit",
    "rubber-duck", "sageandweaver-blog", "scientific-inquiry", "scratch-pad",
    "seasonal-reflection", "session-archive-analysis", "session-summary", "shadow-work",
    "specialist-consultation", "tdd", "team-delegation", "team-goals-automation",
    "thought", "thought-check", "twitter-operations", "user-story-implementation",
    "web3chan-api", "wordpress-publishing",
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
    skill_path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    if not os.path.exists(skill_path):
        return None, None, None
    with open(skill_path) as f:
        content = f.read()
    version = "1.0.0"
    description = skill_name
    fm_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        v_match = re.search(r'version:\s*["\']?([^\s"\']+)', fm)
        if v_match:
            version = v_match.group(1)
        d_match = re.search(r'description:\s*(.+)', fm)
        if d_match:
            description = d_match.group(1).strip().strip('"\'')
    if len(content) > 8000:
        content = content[:7900] + "\n\n... (truncated, full version at source)"
    return version, description, content


if __name__ == "__main__":
    print("Retrying 22 rate-limited skills with 2s spacing...")
    jwt = get_jwt()
    print("JWT obtained.\n")

    results = []
    for i, skill_name in enumerate(RETRY_SKILLS, 1):
        version, description, content = read_skill(skill_name)
        if content is None:
            print(f"  [{i}/22] SKIP {skill_name}")
            continue

        title = f"Aether Skill: {skill_name}"
        body = content

        print(f"  [{i}/22] Posting: {skill_name}...")
        tid, status = post_thread(jwt, FEDERATION_SKILLS_ROOM, title, body)
        print(f"    Thread: {tid} (HTTP {status})")

        results.append({"skill": skill_name, "thread_id": tid, "status": status})

        if status == 429:
            print("    Rate limited! Waiting 10s...")
            time.sleep(10)
            jwt = get_jwt()  # refresh JWT too
        else:
            time.sleep(2)  # 2s between posts

        if i % 10 == 0:
            jwt = get_jwt()

    print("\nRETRY RESULTS:")
    ok = sum(1 for r in results if r["status"] == 201)
    print(f"  {ok}/{len(results)} successful")
    for r in results:
        mark = "OK" if r["status"] == 201 else f"FAIL({r['status']})"
        print(f"  [{mark}] {r['skill']} -> {r['thread_id']}")
