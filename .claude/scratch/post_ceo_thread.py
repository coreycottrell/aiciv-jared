#!/usr/bin/env python3
"""
Post CEO vs Employee blog thread to Bluesky.
5 posts as a thread, image on post 1, link card on post 5.
"""

import time
import sys
import os

from atproto import Client, models

# === Configuration ===
SESSION_FILE = '/home/jared/projects/AI-CIV/aether/.claude/from-jared/bsky/bsky_automation/bsky_session.txt'
IMAGE_PATH = '/home/jared/projects/AI-CIV/aether/.claude/scratch/ceo_banner_compressed.jpg'
BLOG_URL = 'https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/'

BSKY_USERNAME = 'purebrain.ai'
BSKY_PASSWORD = '7hje-xipf-hwqy-5vg6'

# === Thread Posts ===
POSTS = [
    # Post 1 - Hook (IMAGE ATTACHED)
    """When a CEO asks about AI, they ask about leverage and scale.

When an employee asks about AI, they ask about job security.

Same technology. Completely different conversations.

That gap is where most AI transformations break. Thread:""",

    # Post 2 - The Data
    """The numbers tell the story:

- 76% of executives believe AI will boost productivity
- 65% of employees worry AI will replace them within 5 years
- 82% of organizations have NO formal AI communication strategy

That's not a tech problem. That's a perception problem.""",

    # Post 3 - The Insight
    """What both sides get wrong:

CEOs treat AI like software they're buying.
Employees treat AI like a threat they're surviving.

Neither is engaging with what AI actually is: a thinking partner that gets better the more you invest in the relationship.""",

    # Post 4 - The Bridge
    """The organizations winning at AI aren't the ones with the biggest budgets.

They're the ones where the CEO's vision and the employee's reality actually overlap.

That overlap? It's called partnership. And it starts with both sides seeing through each other's lens.""",

    # Post 5 - CTA (LINK CARD)
    """I wrote about this in depth: the specific pattern I see across hundreds of AI conversations, and the 3-step alignment bridge that actually works.

Read the full piece here.

Your brain. Your AI. Actual intelligence. purebrain.ai""",
]


def login_client():
    """Login to Bluesky, trying session first, then credentials."""
    client = Client()

    # Try session file first
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                session_str = f.read().strip()
            client.login(session_string=session_str)
            print(f"[OK] Session restored: {client.me.handle}")
            return client
        except Exception as e:
            print(f"[WARN] Session expired: {e}")
            print("[INFO] Re-authenticating with credentials...")

    # Login with credentials
    client.login(BSKY_USERNAME, BSKY_PASSWORD)
    print(f"[OK] Logged in as: {client.me.handle}")

    # Save new session
    with open(SESSION_FILE, 'w') as f:
        f.write(client.export_session_string())
    print("[OK] New session saved")

    return client


def upload_image(client, image_path):
    """Upload image and return blob."""
    with open(image_path, 'rb') as f:
        img_data = f.read()

    print(f"[INFO] Uploading image ({len(img_data)} bytes / {len(img_data)/1024:.1f} KB)...")
    response = client.upload_blob(img_data)
    print(f"[OK] Image uploaded")
    return response.blob


def create_link_card_embed(client, url, title, description):
    """Create an external link card embed."""
    embed = models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(
            uri=url,
            title=title,
            description=description,
        )
    )
    return embed


def post_thread(client):
    """Post the 5-post thread."""

    # Upload image for post 1
    image_blob = upload_image(client, IMAGE_PATH)

    results = []
    root_ref = None
    parent_ref = None

    for i, text in enumerate(POSTS):
        post_num = i + 1

        print(f"\n[Post {post_num}/{len(POSTS)}] Length: {len(text)} chars")

        if len(text) > 300:
            print(f"[WARN] Post {post_num} is {len(text)} chars - may exceed 300 grapheme limit")

        # Build kwargs
        kwargs = {'text': text}

        # Post 1: Add image embed
        if post_num == 1:
            kwargs['embed'] = models.AppBskyEmbedImages.Main(
                images=[
                    models.AppBskyEmbedImages.Image(
                        alt="CEO vs Employee: The two lenses on AI transformation - banner image showing two silhouettes looking at an illuminated brain, representing different perspectives on AI",
                        image=image_blob,
                    )
                ]
            )
            print("[INFO] Image embed attached")

        # Post 5: Add link card embed
        if post_num == 5:
            kwargs['embed'] = create_link_card_embed(
                client,
                url=BLOG_URL,
                title="CEO vs Employee: The AI Transformation Gap Nobody Talks About",
                description="The specific pattern across hundreds of AI conversations, and the 3-step alignment bridge that actually works.",
            )
            print("[INFO] Link card embed attached")

        # Add reply reference (posts 2-5 reply to previous)
        if parent_ref is not None:
            kwargs['reply_to'] = models.AppBskyFeedPost.ReplyRef(
                root=root_ref,
                parent=parent_ref,
            )

        # Send the post
        try:
            response = client.send_post(**kwargs)

            # Build strong refs
            strong_ref = models.ComAtprotoRepoStrongRef.Main(
                uri=response.uri,
                cid=response.cid,
            )

            if root_ref is None:
                root_ref = strong_ref  # First post becomes root
            parent_ref = strong_ref  # Current post becomes parent for next

            results.append({
                'post_num': post_num,
                'uri': response.uri,
                'cid': response.cid,
                'success': True,
            })

            print(f"[OK] Post {post_num} published successfully")

            # Delay between posts (human-like pacing)
            if post_num < len(POSTS):
                delay = 2.0
                print(f"[WAIT] {delay}s before next post...")
                time.sleep(delay)

        except Exception as e:
            print(f"[ERROR] Post {post_num} failed: {e}")
            results.append({
                'post_num': post_num,
                'error': str(e),
                'success': False,
            })
            # If a post in the chain fails, we should stop
            print("[ABORT] Stopping thread - chain broken")
            break

    return results


def main():
    print("=" * 60)
    print("Bluesky Thread: CEO vs Employee AI Transformation Gap")
    print("=" * 60)

    # Login
    client = login_client()

    # Post thread
    results = post_thread(client)

    # Summary
    print("\n" + "=" * 60)
    print("THREAD POSTING SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"Successful: {len(successful)}/{len(POSTS)}")
    print(f"Failed: {len(failed)}/{len(POSTS)}")

    if successful:
        # Build URL for first post
        first_uri = successful[0]['uri']
        post_rkey = first_uri.split('/')[-1]
        thread_url = f"https://bsky.app/profile/{client.me.handle}/post/{post_rkey}"
        print(f"\nThread URL: {thread_url}")

    if failed:
        for f in failed:
            print(f"  Post {f['post_num']} error: {f['error']}")

    # Save updated session
    try:
        with open(SESSION_FILE, 'w') as f:
            f.write(client.export_session_string())
        print("\n[OK] Session saved for next use")
    except:
        pass

    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
