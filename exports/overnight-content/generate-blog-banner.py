#!/usr/bin/env python3
"""
Generate blog banner images for:
  - the-ai-relationship-you-cant-take-with-you
  - 16:9 blog header
  - 1:1 Bluesky square
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

from google import genai
from google.genai import types
from PIL import Image

client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])

SLUG = "the-ai-relationship-you-cant-take-with-you"
OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/overnight-content")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADER_PATH = OUTPUT_DIR / f"{SLUG}-banner.png"
SQUARE_PATH = OUTPUT_DIR / f"{SLUG}-bsky-square.png"
SQUARE_COMPRESSED = OUTPUT_DIR / f"{SLUG}-bsky-square-compressed.jpg"

# ── 16:9 Blog Header ─────────────────────────────────────────────────────────
header_prompt = """Dark futuristic blog header. Two glowing orbs connected by a dissolving light bridge — one orb vibrant cerulean blue (#2a93c1), one orb warm orange (#f1420b) — drifting apart as the bridge between them fades into particles. The orange orb trails memories as scattered glowing data fragments receding into darkness. Deep space background, dark near-black blue (#080a12). Ethereal, personal, melancholic yet forward-looking mood. Dramatic rim lighting, shallow depth of field.

Large readable title text at bottom center: "The AI Relationship You Can't Take With You"
Title in clean white bold sans-serif, high contrast.

Bottom-left corner logo text: "PUREBR" in cerulean blue (#2a93c1) immediately followed by "AI" in orange (#f1420b) immediately followed by "N.ai" where N is in cerulean blue and ".ai" is in white lowercase. Logo styled together as one wordmark, no spaces between parts.

Keep all text and logo away from edges — mobile-safe margins. 16:9 aspect ratio."""

print("Generating 16:9 blog header...")
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=header_prompt,
    config=types.GenerateContentConfig(
        response_modalities=['IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"
        ),
    )
)

for part in response.parts:
    if part.inline_data is not None:
        part.as_image().save(str(HEADER_PATH))
        print(f"Blog header saved: {HEADER_PATH}")
        break

# ── 1:1 Bluesky Square ───────────────────────────────────────────────────────
square_prompt = """Square social media graphic. Dark near-black background (#080a12). Center composition: two glowing orbs — cerulean blue (#2a93c1) and orange (#f1420b) — connected by a fading dissolving bridge of light particles. The connection is breaking. Ethereal, cinematic mood. Deep space aesthetic. Dramatic rim lighting.

Bold centered text overlay: "The AI Relationship You Can't Take With You"
White text, large and readable, positioned in upper third.

Small bottom-center logo: "PUREBR" in cerulean blue + "AI" in orange + "N.ai" in cerulean/white. One wordmark, no gaps.

1:1 square format optimized for social feed."""

print("Generating 1:1 Bluesky square...")
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=square_prompt,
    config=types.GenerateContentConfig(
        response_modalities=['IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="1:1",
            image_size="1K"
        ),
    )
)

for part in response.parts:
    if part.inline_data is not None:
        part.as_image().save(str(SQUARE_PATH))
        print(f"Bsky square saved: {SQUARE_PATH}")
        break

# ── Compress Bsky Square ──────────────────────────────────────────────────────
print("Compressing Bsky square for upload (<976KB)...")
img = Image.open(str(SQUARE_PATH))
if img.mode in ('RGBA', 'P'):
    img = img.convert('RGB')
img.save(str(SQUARE_COMPRESSED), "JPEG", quality=85, optimize=True)

size_kb = os.path.getsize(str(SQUARE_COMPRESSED)) / 1024
print(f"Compressed: {SQUARE_COMPRESSED} ({size_kb:.0f}KB)")

if size_kb >= 976:
    print("WARNING: Still over 976KB, reducing quality further...")
    img.save(str(SQUARE_COMPRESSED), "JPEG", quality=70, optimize=True)
    size_kb = os.path.getsize(str(SQUARE_COMPRESSED)) / 1024
    print(f"Re-compressed: {size_kb:.0f}KB")

print("\nDone!")
print(f"  Blog header (16:9): {HEADER_PATH}")
print(f"  Bsky square (1:1):  {SQUARE_PATH}")
print(f"  Bsky compressed:    {SQUARE_COMPRESSED} ({size_kb:.0f}KB)")
