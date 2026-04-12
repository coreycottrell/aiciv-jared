# Memory: The AI That Knows You Before You Even Speak - Full Publish

**Date**: 2026-03-17
**Agent**: blogger
**Type**: operational

## What Was Published

Blog post: "The AI That Knows You Before You Even Speak"
- Target ICP: VP of Growth / senior business leader
- Core argument: The "briefing tax" costs organizations months per year; the solution is persistent AI context that accumulates rather than resets
- Three layers framework: Operational, Strategic, Relational memory

## Pipeline Results

| Step | Result | URL/Notes |
|------|--------|-----------|
| CF Pages deploy | HTTP 200 | https://purebrain.ai/blog/the-ai-that-knows-you-before-you-even-speak/ |
| WordPress (jareddsanborn.com) | Post ID 1283, published live | https://jareddsanborn.com/2026/03/17/the-ai-that-knows-you-before-you-even-speak-3/ |
| Bluesky thread | 6 posts, image on post 1 | https://bsky.app/profile/purebrain.ai/post/3mhbpy75bvp2u |
| Blog audio (ElevenLabs) | 21.8 min MP3 | /home/jared/projects/AI-CIV/aether/exports/the-ai-that-knows-you-before-you-even-speak-audio.mp3 |

## Key Technical Notes

- The existing blog directory already had the HTML and banner pre-built (from a prior session). Only needed deployment + social + audio.
- Bluesky atproto client login times out via `client.login(session_string=...)` when session is expired. Fresh `client.login(user, pass)` also times out via atproto SDK. Workaround: use httpx direct HTTP calls to bsky.social/xrpc endpoints. This worked reliably.
- Banner image matched portal upload exactly (md5 verified): 266587 bytes.
- WordPress content: must convert markdown to HTML. `markdown` module not installed by default — needed `pip install markdown --break-system-packages`.

## Bluesky Thread URIs

1. at://did:plc:zy537fjp73tuq52ercz4ydo2/app.bsky.feed.post/3mhbpy75bvp2u (with image)
2. at://did:plc:zy537fjp73tuq52ercz4ydo2/app.bsky.feed.post/3mhbpybqomr2c
3. at://did:plc:zy537fjp73tuq52ercz4ydo2/app.bsky.feed.post/3mhbpydu6ov2w
4. at://did:plc:zy537fjp73tuq52ercz4ydo2/app.bsky.feed.post/3mhbpyfxj3b2c
5. at://did:plc:zy537fjp73tuq52ercz4ydo2/app.bsky.feed.post/3mhbpyi2ofn2w
6. at://did:plc:zy537fjp73tuq52ercz4ydo2/app.bsky.feed.post/3mhbpykbvrz2c

## Lessons Learned

1. Atproto Python SDK has unreliable timeout behavior. Direct httpx HTTP calls to bsky.social/xrpc are more reliable.
2. When markdown module not available, `pip install markdown --break-system-packages` works.
3. Banner JPEG from portal at 266KB is well under Bluesky 976KB limit — no compression needed for the original.
4. WordPress post URL slug may get a suffix (e.g., -3) if the slug already exists from prior drafts.
