#!/usr/bin/env python3
"""
Test script for Bluesky posting via ContentRouter handler
"""

import sys
import logging
from pathlib import Path

# Setup path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

# Import the handler
from content_router import post_bluesky, setup_logger

# Create test post data
test_post = {
    "content": "🤖 Aether ContentRouter Phase 3 test — automated multi-platform posting is live. Bluesky handler operational.",
    "media_url": None,
}

# Setup logger
logger = setup_logger()

# Execute post
print("Testing Bluesky posting...")
success, post_url, error = post_bluesky(test_post, "jared", logger)

if success:
    print(f"✅ SUCCESS: {post_url}")
    sys.exit(0)
else:
    print(f"❌ FAILED: {error}")
    sys.exit(1)
