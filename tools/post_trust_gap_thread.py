#!/usr/bin/env python3
"""
Post Bluesky thread for:
"The AI Trust Gap Is the Real Problem (Not the Technology)"
Blog URL: https://purebrain.ai/the-ai-trust-gap/
"""

import sys
import time
import os
from atproto import Client, models

SESSION_FILE = '/home/jared/projects/AI-CIV/aether/.claude/from-jared/bsky/bsky_automation/bsky_session.txt'
BSKY_USERNAME = 'purebrain.ai'
BSKY_PASSWORD = '7hje-xipf-hwqy-5vg6'

POSTS = [
    # Post 1: Hook - trust gap statistic
    "50% of business leaders trust AI for repetitive tasks.\n\nOnly 28% trust it for decision-making. (Alteryx 2025)\n\nThat gap isn't a technology problem.\n\nIt's the real reason AI adoption stalls.",

    # Post 2: The problem - trust cliff
    "Most organizations hit a 'trust cliff.'\n\nAI handles routine work fine. But ask it to help think through strategy?\n\nSuddenly it feels risky. Not because the AI changed - because the relationship never developed.",

    # Post 3: The insight - trust is about relationship
    "Here's what most miss:\n\nTrust isn't about capability. AI is already capable enough.\n\nIt's about relationship. Familiarity. Consistent context. Knowing AI understands your business, not just your last prompt.",

    # Post 4: Solution direction
    "Organizations closing that gap aren't using better AI.\n\nThey're building differently - persistent context, shared history, genuine back-and-forth.\n\nRelationship-first AI partnership earns strategic trust over time.",

    # Post 5: CTA with link
    "Full breakdown: why the trust gap exists, where orgs get stuck, and how to move from 'automate the routine' to 'help me think.'\n\nFree AI Partnership Audit included.\n\nhttps://purebrain.ai/the-ai-trust-gap/",
]


def check_char_counts():
    """Verify all posts are under 300 chars."""
    print("=== Character Count Check ===")
    all_ok = True
    for i, post in enumerate(POSTS, 1):
        count = len(post)
        status = "OK" if count <= 300 else "OVER LIMIT"
        print(f"Post {i}: {count} chars [{status}]")
        if count > 300:
            all_ok = False
    return all_ok


def post_thread():
    client = Client()

    # Try session restore first, fall back to fresh login
    try:
        print("Attempting session restore...")
        with open(SESSION_FILE, 'r') as f:
            session_str = f.read().strip()
        client.login(session_string=session_str)
        print(f"Session restored: @{client.me.handle}")
    except Exception as e:
        print(f"Session restore failed ({e}), doing fresh login...")
        client.login(BSKY_USERNAME, BSKY_PASSWORD)
        print(f"Fresh login successful: @{client.me.handle}")

    # Save refreshed session
    new_session = client.export_session_string()
    with open(SESSION_FILE, 'w') as f:
        f.write(new_session)
    print("Session saved.")

    results = []
    root_ref = None
    parent_ref = None

    for i, text in enumerate(POSTS, 1):
        char_count = len(text)
        print(f"\n--- Post {i}/{len(POSTS)} ({char_count} chars) ---")
        print(text[:80] + ("..." if len(text) > 80 else ""))

        # Safety gate
        if char_count > 300:
            print(f"WARNING: Post {i} is {char_count} chars - truncating to 295")
            text = text[:295] + "..."

        try:
            if parent_ref is None:
                # First post in thread
                response = client.send_post(text=text)
                root_ref = models.ComAtprotoRepoStrongRef.Main(
                    uri=response.uri,
                    cid=response.cid
                )
                parent_ref = root_ref
            else:
                # Reply in thread chain
                reply_ref = models.AppBskyFeedPost.ReplyRef(
                    root=root_ref,
                    parent=parent_ref,
                )
                response = client.send_post(
                    text=text,
                    reply_to=reply_ref,
                )
                parent_ref = models.ComAtprotoRepoStrongRef.Main(
                    uri=response.uri,
                    cid=response.cid
                )

            results.append({
                'index': i,
                'uri': response.uri,
                'cid': response.cid,
            })
            print(f"  Posted: {response.uri}")

            # 1.5 second delay between posts (human-like pacing)
            if i < len(POSTS):
                time.sleep(1.5)

        except Exception as e:
            print(f"  ERROR posting post {i}: {e}")
            results.append({'index': i, 'error': str(e)})
            break

    # Report results
    print("\n=== THREAD POSTING COMPLETE ===")
    successful = [r for r in results if 'uri' in r]
    failed = [r for r in results if 'error' in r]

    print(f"Successful: {len(successful)}/{len(POSTS)}")
    print(f"Failed: {len(failed)}/{len(POSTS)}")

    if successful:
        first_uri = successful[0]['uri']
        rkey = first_uri.split('/')[-1]
        web_url = f"https://bsky.app/profile/{client.me.handle}/post/{rkey}"
        print(f"\nFirst post URL: {web_url}")

        print("\nAll post URIs:")
        for r in successful:
            print(f"  {r['index']}. {r['uri']}")

        return web_url, results, client.me.handle
    else:
        print("All posts failed.")
        return None, results, None


if __name__ == '__main__':
    print("=== Pre-flight: Character Count Check ===")
    if not check_char_counts():
        print("ABORT: Posts exceed character limit.")
        sys.exit(1)

    print("\n=== Posting Thread ===")
    web_url, results, handle = post_thread()

    if web_url:
        print(f"\nThread live at: {web_url}")
        sys.exit(0)
    else:
        sys.exit(1)
