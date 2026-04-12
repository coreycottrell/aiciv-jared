#!/usr/bin/env python3
"""
Re-authenticate Bluesky session
Handles ExpiredToken error by logging in fresh with credentials
"""

from atproto import Client
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

SESSION_FILE = Path('/home/jared/projects/AI-CIV/aether/.claude/from-jared/bsky/bsky_automation/bsky_session.txt')

# Get credentials
username = os.getenv('BSKY_USERNAME')
password = os.getenv('BSKY_PASSWORD')

if not username or not password:
    print("✗ Missing BSKY_USERNAME or BSKY_PASSWORD in .env")
    exit(1)

print(f"Re-authenticating {username}...")

try:
    client = Client()
    client.login(username, password)
    print(f"✓ Login successful: @{client.me.handle}")

    # Save session string
    session_string = client.export_session_string()
    with open(SESSION_FILE, 'w') as f:
        f.write(session_string)
    print(f"✓ Session saved to {SESSION_FILE}")

except Exception as e:
    print(f"✗ Login failed: {e}")
    exit(1)
