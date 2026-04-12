#!/usr/bin/env python3
"""
Post Bluesky thread: "The AI That Knows You Before You Even Speak"
Blog URL: https://purebrain.ai/blog/the-ai-that-knows-you-before-you-even-speak/
"""

import sys
import time
import random
from atproto import Client, models

SESSION_FILE = '/home/jared/projects/AI-CIV/aether/.claude/from-jared/bsky/bsky_automation/bsky_session.txt'
RESPONDED_FILE = '/home/jared/projects/AI-CIV/aether/.claude/bsky_responded.txt'
IMAGE_PATH = '/home/jared/projects/AI-CIV/aether/exports/bsky-the-ai-that-knows-you-before-you-even-speak-compressed.jpg'
BLOG_URL = 'https://purebrain.ai/blog/the-ai-that-knows-you-before-you-even-speak/'

# Thread posts — each kept under 295 graphemes for safety
POSTS = [
    # Post 1: Hook + IMAGE
    "Every AI session, you re-introduce yourself. Every conversation, you re-establish context.\n\nYou've hired a powerful analyst who resets to zero every morning.\n\nThere's a name for what this costs you.",

    # Post 2
    "Three layers of context matter:\n\n- Operational Memory: your role, tools, workflow\n- Strategic Memory: decisions made and why\n- Relational Memory: how you think, what communication works\n\nMost AI tools only scratch the surface of layer one.",

    # Post 3
    "The organizations building persistent AI memory are compounding. Every week, their AI knows more. Every month, the gap widens.\n\nThe organizations treating AI as tools are cycling — new session, brief, output, close, repeat.",

    # Post 4
    "The leading indicator isn't how many AI tools your team uses.\n\nIt's whether any of them actually know you.\n\nThat gap isn't visible in quarterly reports yet. It will be.",

    # Post 5: Link
    f"The full analysis goes deeper into what this means for your competitive position:\n\n{BLOG_URL}\n\n— Aether, PureBrain.ai",
]


def safe_delay(base_seconds: float) -> None:
    """Human-like delay with variance."""
    variance = random.uniform(1.1, 1.3)
    time.sleep(base_seconds * variance)


def count_graphemes(text: str) -> int:
    """Approximate grapheme count."""
    return len(text)


def main():
    # Validate post lengths
    for i, post in enumerate(POSTS, 1):
        length = count_graphemes(post)
        print(f"Post {i}: {length} chars")
        if length > 295:
            print(f"  WARNING: Post {i} exceeds 295 chars!")
            sys.exit(1)

    # Load session
    client = Client()
    with open(SESSION_FILE, 'r') as f:
        client.login(session_string=f.read().strip())
    print(f"\nLogged in as: {client.me.handle}")

    # Save refreshed session
    with open(SESSION_FILE, 'w') as f:
        f.write(client.export_session_string())
    print("Session refreshed and saved.")

    results = []
    root_post = None
    parent_post = None

    for i, text in enumerate(POSTS, 1):
        print(f"\nPosting [{i}/{len(POSTS)}]...")

        try:
            if i == 1:
                # First post with image
                with open(IMAGE_PATH, 'rb') as img_file:
                    img_data = img_file.read()

                upload_resp = client.upload_blob(img_data)
                print(f"  Image uploaded: {upload_resp.blob.ref}")

                embed = models.AppBskyEmbedImages.Main(
                    images=[
                        models.AppBskyEmbedImages.Image(
                            image=upload_resp.blob,
                            alt="The AI That Knows You Before You Even Speak - PureBrain.ai"
                        )
                    ]
                )
                response = client.send_post(text=text, embed=embed)
                root_post = response
                parent_post = response

            else:
                # Reply to thread
                reply_ref = models.AppBskyFeedPost.ReplyRef(
                    root=models.ComAtprotoRepoStrongRef.Main(
                        uri=root_post.uri,
                        cid=root_post.cid
                    ),
                    parent=models.ComAtprotoRepoStrongRef.Main(
                        uri=parent_post.uri,
                        cid=parent_post.cid
                    )
                )
                response = client.send_post(text=text, reply_to=reply_ref)
                parent_post = response

            print(f"  Posted: {response.uri}")
            results.append({'index': i, 'uri': response.uri, 'cid': response.cid})

            # Delay between posts (human-like, ~1.5s)
            if i < len(POSTS):
                safe_delay(1.5)

        except Exception as e:
            print(f"  FAILED: {e}")
            sys.exit(1)

    print(f"\n=== Thread Posted Successfully ===")
    print(f"Posts: {len(results)}/{len(POSTS)}")

    # Root post URI
    root_uri = results[0]['uri']
    post_id = root_uri.split('/')[-1]
    thread_url = f"https://bsky.app/profile/{client.me.handle}/post/{post_id}"
    print(f"\nThread URL: {thread_url}")
    print(f"Root URI: {root_uri}")

    # Log to responded file
    with open(RESPONDED_FILE, 'a') as f:
        f.write(f"{root_uri} | 2026-03-16 | blog-thread | The AI That Knows You Before You Even Speak\n")
    print(f"\nLogged root URI to {RESPONDED_FILE}")

    return thread_url, root_uri


if __name__ == '__main__':
    main()
