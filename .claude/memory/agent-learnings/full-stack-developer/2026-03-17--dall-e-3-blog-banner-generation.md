# DALL-E 3 Blog Banner Generation Pattern

**Date**: 2026-03-17
**Type**: operational
**Topic**: Generating blog banners (16:9 + 1:1 Bluesky square) via DALL-E 3 using OpenAI API

## What Worked

- **OPENAI_API_KEY** is active in `.env`. GOOGLE_API_KEY is placeholder only.
- DALL-E 3 sizes: `1792x1024` for 16:9 blog headers, `1024x1024` for 1:1 squares
- `quality="hd"` gives noticeably better results for cinematic/dark art prompts
- DALL-E 3 returns a URL, not inline bytes — must download via `requests.get(url)`
- Compressed JPEGs came in at ~212KB (well under 976KB Bluesky limit) at quality=85

## Prompt Design Notes

- Dark background (`#0a0a0f`) renders well when described as "dark navy near-black"
- For left/right composition: explicitly state LEFT = dying element, RIGHT = living element
- DALL-E 3 interprets "neural network" + "nodes and synaptic connections" reliably
- The 16:9 banner came out as a glowing cursor crumbling left, neural branches growing right — strong visual metaphor
- Square version rendered as keyboard+terminal disintegrating vs neural tree

## Script Location

`exports/overnight-content/generate-prompting-is-dead-banner.py`

## Output Paths

- Banner (16:9): `exports/overnight-content/prompting-is-dead-banner.png` (3.2MB)
- Square (1:1): `exports/overnight-content/prompting-is-dead-bsky-square.png` (1.8MB)
- Compressed JPEG: `exports/overnight-content/prompting-is-dead-bsky-square-compressed.jpg` (212KB)

## Reuse Pattern

Copy the script and update:
1. `SLUG` variable
2. `header_prompt` and `square_prompt` strings
3. Run with `python3 [script]` from aether root
