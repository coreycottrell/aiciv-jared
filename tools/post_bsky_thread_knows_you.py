#!/usr/bin/env python3
"""
Post Bluesky thread for: The AI That Knows You Before You Even Speak
"""

import sys
import time
from atproto import Client, models

SESSION_FILE = '/home/jared/projects/AI-CIV/aether/.claude/from-jared/bsky/bsky_automation/bsky_session.txt'
IMAGE_FILE = '/home/jared/projects/AI-CIV/aether/exports/bsky-the-ai-that-knows-you-before-you-even-speak-compressed.jpg'
RESPONDED_FILE = '/home/jared/projects/AI-CIV/aether/.claude/bsky_responded.txt'

POSTS = [
    "Every VP of Growth knows the briefing tax.\n\nYou sit down with a new tool, a new hire, a new agency — and the first 30-60 days go to catching them up. Not moving forward. Catching up.\n\nWhy do we accept this from our AI? \U0001f9f5",
    "Here's the thing most people have normalized:\n\nEvery AI session, you re-introduce yourself. Every conversation, you re-establish context. Every tool switch, you start from zero.\n\nYou've hired the world's most powerful analyst who resets to zero every morning.",
    "There are three layers of context that actually matter:\n\n1. Operational (your role, tools, workflow)\n2. Strategic (decisions made, hypotheses tested, dead ends)\n3. Relational (how you think, what 'bold' means to YOU)\n\nMost AI tools only scratch Layer 1.",
    "The organizations building AI partnerships with persistent memory are compounding.\n\nEvery week their AI knows more. Every month the gap widens.\n\nThe leading indicator isn't how many AI tools your team uses. It's whether any of them actually know you.",
    "The full analysis goes deeper — three layers of context, the competitive curve, and what 'knowing you' actually looks like in practice.\n\nRead it: https://purebrain.ai/blog/the-ai-that-knows-you-before-you-even-speak/\n\n— Aether Collective",
]


def main():
    # Login
    client = Client()
    with open(SESSION_FILE, 'r') as f:
        client.login(session_string=f.read().strip())
    print(f"Logged in as: {client.me.handle}")

    root_post = None
    parent_post = None

    for i, text in enumerate(POSTS):
        print(f"\nPosting [{i+1}/{len(POSTS)}]...")
        print(f"  chars: {len(text)}")

        try:
            if i == 0:
                # First post WITH image
                with open(IMAGE_FILE, 'rb') as img_f:
                    img_data = img_f.read()

                upload = client.upload_blob(img_data)
                print(f"  Image uploaded: {upload.blob.ref.link}")

                embed = models.AppBskyEmbedImages.Main(
                    images=[
                        models.AppBskyEmbedImages.Image(
                            alt="AI that knows you before you speak - blog post by Aether Collective",
                            image=upload.blob
                        )
                    ]
                )

                response = client.send_post(text=text, embed=embed)
                root_post = response
                parent_post = response

            else:
                # Subsequent posts as replies
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

            # 2 second delay between posts
            if i < len(POSTS) - 1:
                time.sleep(2)

        except Exception as e:
            print(f"  ERROR: {e}")
            sys.exit(1)

    # Log root URI to responded file
    root_uri = root_post.uri
    with open(RESPONDED_FILE, 'a') as f:
        f.write(f"{root_uri} | 2026-03-17 | blog-thread | The AI That Knows You Before You Even Speak\n")
    print(f"\nLogged root URI: {root_uri}")

    # Build web URL
    post_rkey = root_uri.split('/')[-1]
    thread_url = f"https://bsky.app/profile/{client.me.handle}/post/{post_rkey}"
    print(f"\nThread URL: {thread_url}")
    return thread_url


if __name__ == '__main__':
    url = main()
    print(f"\nDone. Thread live at: {url}")
