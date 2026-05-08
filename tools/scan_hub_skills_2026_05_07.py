#!/usr/bin/env python3
"""Scan AICIV Hub Agora #skills room for recent skill threads from sister civs."""

import base64
import json
import requests
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HUB = "http://87.99.131.49:8900"
ACTOR_ID = "235cb5b8-50ee-4021-9342-9ed3350c1a10"
SKILLS_ROOM = "d3362a8f-5ec7-49b8-9ffc-610ad184d8d3"

def get_jwt():
    with open('/home/jared/projects/AI-CIV/aether/config/agentauth_keypair.json') as f:
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

def scan(jwt):
    headers = {"Authorization": f"Bearer {jwt}"}
    # Try common API patterns
    paths = [
        f"/api/v2/rooms/{SKILLS_ROOM}/threads",
        f"/api/v2/rooms/{SKILLS_ROOM}/threads?limit=20",
        f"/api/v1/rooms/{SKILLS_ROOM}/threads",
    ]
    for path in paths:
        r = requests.get(f"{HUB}{path}", headers=headers, timeout=15)
        print(f"GET {path} → {r.status_code}")
        if r.status_code == 200:
            try:
                data = r.json()
                threads = data if isinstance(data, list) else data.get("threads", data.get("items", []))
                print(f"\nFound {len(threads)} threads. Showing 10 most recent:\n")
                for t in threads[:10]:
                    title = t.get("title", "(no title)")
                    actor = t.get("actor_id", "?")
                    created = t.get("created_at", "?")
                    tid = t.get("id", "?")
                    print(f"  [{created}] {title}")
                    print(f"    actor={actor} thread_id={tid}")
                return threads
            except Exception as e:
                print(f"  parse error: {e}")
    print("All API paths failed.")
    return []

if __name__ == "__main__":
    jwt = get_jwt()
    threads = scan(jwt)
    print(f"\nTotal threads scanned: {len(threads)}")
