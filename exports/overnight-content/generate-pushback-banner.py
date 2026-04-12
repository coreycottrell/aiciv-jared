#!/usr/bin/env python3
"""
Generate blog banner images for:
  - the-ai-that-gets-smarter-when-you-push-back
  - 16:9 blog header
  - 1:1 Bluesky square

PureBrain brand colors:
  - Orange: #f1420b
  - Cerulean Blue: #2a93c1
  - Dark BG: #080a12
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

api_key = os.environ.get('GOOGLE_API_KEY')
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env")
    print("Add: GOOGLE_API_KEY=your-key-here")
    sys.exit(1)

from google import genai
from google.genai import types
from PIL import Image

client = genai.Client(api_key=api_key)

SLUG = "the-ai-that-gets-smarter-when-you-push-back"
OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/overnight-content")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADER_PATH = OUTPUT_DIR / f"{SLUG}-banner.png"
SQUARE_PATH = OUTPUT_DIR / f"{SLUG}-bsky-square.png"
SQUARE_COMPRESSED = OUTPUT_DIR / f"{SLUG}-bsky-square-compressed.jpg"

# ── 16:9 Blog Header ─────────────────────────────────────────────────────────
header_prompt = """Futuristic dark blog header image. Central concept: an AI brain made of glowing neural networks — cerulean blue (#2a93c1) nodes connected by light streams — with a human hand gesture appearing to push back against the brain, sending ripples through the network in orange (#f1420b). The pushback ripple transforms the neural connections, making them stronger and more organized. Deep space background, dark near-black blue (#080a12). Ethereal, intelligent, forward-looking mood. Dramatic rim lighting, cinematic depth of field.

Blog title text at bottom center: "The AI That Gets Smarter When You Push Back"
Title in bold white clean sans-serif, large and high contrast, easy to read.

Small wordmark logo bottom-left: write "PUREBR" in cerulean blue (#2a93c1) immediately followed by "AI" in orange (#f1420b) immediately followed by "N" in cerulean blue followed by ".ai" in white lowercase. All as one connected wordmark, no spaces between parts.

Keep all text and logo well away from edges — mobile-safe margins at least 8% from each edge. 16:9 aspect ratio."""

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

saved_header = False
for part in response.parts:
    if part.inline_data is not None:
        part.as_image().save(str(HEADER_PATH))
        print(f"Blog header saved: {HEADER_PATH}")
        saved_header = True
        break

if not saved_header:
    print("WARNING: No image returned for blog header")
    if response.text:
        print(f"Model text response: {response.text[:200]}")

# ── 1:1 Bluesky Square ───────────────────────────────────────────────────────
square_prompt = """Square social media graphic. Dark near-black background (#080a12). Center composition: a glowing neural brain network in cerulean blue (#2a93c1) being reshaped by orange (#f1420b) ripple waves emanating from a push-back gesture. The ripples are making the brain stronger — connections reorganizing into cleaner, brighter patterns. Ethereal, cinematic, intelligent mood. Deep space aesthetic.

Bold centered title text: "The AI That Gets Smarter When You Push Back"
White text, large, readable, positioned in upper third of image. High contrast.

Small bottom-center wordmark: "PUREBR" in cerulean blue + "AI" in orange + "N" in cerulean blue + ".ai" in white lowercase. One connected wordmark, no gaps.

1:1 square format optimized for social media feeds. Keep text away from edges."""

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

saved_square = False
for part in response.parts:
    if part.inline_data is not None:
        part.as_image().save(str(SQUARE_PATH))
        print(f"Bsky square saved: {SQUARE_PATH}")
        saved_square = True
        break

if not saved_square:
    print("WARNING: No image returned for bsky square")

# ── Compress Bsky Square ──────────────────────────────────────────────────────
if saved_square:
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
if saved_square:
    print(f"  Bsky square (1:1):  {SQUARE_PATH}")
    print(f"  Bsky compressed:    {SQUARE_COMPRESSED}")
