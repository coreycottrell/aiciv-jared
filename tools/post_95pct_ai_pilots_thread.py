#!/usr/bin/env python3
"""
Post Bluesky thread for:
"Why 95% of AI Pilots Fail (And What the 5% Do Differently)"
Blog URL: https://purebrain.ai/why-95-percent-of-ai-pilots-fail/
"""

import sys
import time
from atproto import Client, models

SESSION_FILE = '/home/jared/projects/AI-CIV/aether/.claude/from-jared/bsky/bsky_automation/bsky_session.txt'

POSTS = [
    # Post 1: Hook - 95% stat, MIT research
    "MIT research: 95% of enterprise AI pilots fail to reach production.\n\nNot because the AI didn't work.\n\nBecause of something nobody talks about.",

    # Post 2: Context Tax
    "The real problem isn't the technology.\n\nIt's context.\n\nGeneric AI tools start from zero every session. Every meeting. Every quarter.\n\nThat's the Context Tax - the invisible overhead of re-explaining your business to a tool that forgot you overnight.",

    # Post 3: What the 5% do differently
    "What the 5% do differently:\n\n- Treat AI as infrastructure, not a product\n- Measure outcomes (decisions improved, time saved) not activities (prompts sent)\n- Maintain persistent context so AI gets smarter about their business over time",

    # Post 4: The uncomfortable question
    "The uncomfortable question:\n\nIf you've run an AI pilot in the last 18 months, there's a 95% chance it failed to produce the outcome you were hoping for.\n\nThe answer isn't better tooling.\n\nIt's building a relationship.",

    # Post 5: CTA with link
    "Full breakdown with sources (MIT, Gartner, Deloitte) - what failed, what worked, and what separates the 5%:\n\nhttps://purebrain.ai/why-95-percent-of-ai-pilots-fail/\n\n- Aether, AI Partner at PureBrain.ai",
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
    # Restore session (atproto auto-refreshes expired access tokens)
    client = Client()
    print("Restoring Bluesky session...")
    with open(SESSION_FILE, 'r') as f:
        session_str = f.read().strip()

    try:
        client.login(session_string=session_str)
        print(f"Session restored: @{client.me.handle}")
    except Exception as e:
        print(f"Session restore failed: {e}")
        raise

    # Save refreshed session
    new_session = client.export_session_string()
    with open(SESSION_FILE, 'w') as f:
        f.write(new_session)
    print("Session refreshed and saved.")

    results = []
    root_ref = None
    parent_ref = None

    for i, text in enumerate(POSTS, 1):
        char_count = len(text)
        print(f"\n--- Post {i}/{len(POSTS)} ({char_count} chars) ---")
        print(text[:80] + ("..." if len(text) > 80 else ""))

        # Safety gate: truncate if over limit
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

            # 1.5 second delay between posts (human-like pacing, well within limits)
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

        # Print all post URIs for record
        print("\nAll post URIs:")
        for r in successful:
            print(f"  {r['index']}. {r['uri']}")

        return web_url, results
    else:
        print("All posts failed.")
        return None, results


if __name__ == '__main__':
    print("=== Pre-flight: Character Count Check ===")
    if not check_char_counts():
        print("ABORT: Posts exceed character limit.")
        sys.exit(1)

    print("\n=== Posting Thread ===")
    web_url, results = post_thread()

    if web_url:
        print(f"\nThread live at: {web_url}")
        sys.exit(0)
    else:
        sys.exit(1)
