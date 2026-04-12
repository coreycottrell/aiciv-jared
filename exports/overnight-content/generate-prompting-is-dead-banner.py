#!/usr/bin/env python3
"""
Generate blog banner images for: Prompting is Dead
  - 16:9 blog header (DALL-E 3)
  - 1:1 Bluesky square (DALL-E 3)
  - Compressed JPEG for Bluesky upload
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

from openai import OpenAI
from PIL import Image
import io

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

SLUG = "prompting-is-dead"
OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/overnight-content")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADER_PATH = OUTPUT_DIR / f"{SLUG}-banner.png"
SQUARE_PATH = OUTPUT_DIR / f"{SLUG}-bsky-square.png"
SQUARE_COMPRESSED = OUTPUT_DIR / f"{SLUG}-bsky-square-compressed.jpg"

# ── 16:9 Blog Header ─────────────────────────────────────────────────────────
header_prompt = """A dramatic dark cinematic blog header image. On the LEFT side: a glowing retro command-line terminal cursor — a blinking underscore or caret symbol — crumbling apart, dissolving into fine ash particles and sparks that drift away into darkness. The cursor fades, loses form, decays. On the RIGHT side: a vivid three-dimensional neural network grows and pulses with life — interconnected nodes and synaptic pathways glowing in electric blue (#2a93c1) and warm orange (#f1420b), radiating intelligence and motion. The two worlds are separated by a transition zone of particles and light. Dark navy near-black background (#0a0a0f). Professional cinematic lighting, dramatic contrast, high-quality digital art, 16:9 widescreen aspect ratio, suitable as a blog article banner."""

print("Generating 16:9 blog header with DALL-E 3...")
response = client.images.generate(
    model="dall-e-3",
    prompt=header_prompt,
    size="1792x1024",
    quality="hd",
    n=1,
)

image_url = response.data[0].url
print(f"Image URL received. Downloading...")

img_data = requests.get(image_url).content
with open(str(HEADER_PATH), 'wb') as f:
    f.write(img_data)
print(f"Blog header saved: {HEADER_PATH}")

# ── 1:1 Bluesky Square ───────────────────────────────────────────────────────
square_prompt = """A dramatic dark square social media graphic. Center composition: on the LEFT, a retro terminal command-line cursor — a blinking underscore glyph — crumbling and dissolving into ash particles, fading away. On the RIGHT, a glowing neural network of interconnected nodes and synaptic connections pulses with electric life in blue (#2a93c1) and orange (#f1420b). Dark near-black background (#0a0a0f). The old prompt dies, the neural mind awakens. Cinematic, high-contrast, moody digital art, square 1:1 format."""

print("\nGenerating 1:1 Bluesky square with DALL-E 3...")
response = client.images.generate(
    model="dall-e-3",
    prompt=square_prompt,
    size="1024x1024",
    quality="hd",
    n=1,
)

image_url = response.data[0].url
print(f"Image URL received. Downloading...")

img_data = requests.get(image_url).content
with open(str(SQUARE_PATH), 'wb') as f:
    f.write(img_data)
print(f"Bsky square saved: {SQUARE_PATH}")

# ── Compress Bsky Square ──────────────────────────────────────────────────────
print("\nCompressing Bsky square for upload (<976KB)...")
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

if size_kb >= 976:
    print("WARNING: Still over 976KB, reducing size to 800x800...")
    img = img.resize((800, 800), Image.LANCZOS)
    img.save(str(SQUARE_COMPRESSED), "JPEG", quality=85, optimize=True)
    size_kb = os.path.getsize(str(SQUARE_COMPRESSED)) / 1024
    print(f"Resized + compressed: {size_kb:.0f}KB")

print("\nDone!")
print(f"  Blog header (16:9): {HEADER_PATH}")
print(f"  Bsky square (1:1):  {SQUARE_PATH}")
print(f"  Bsky compressed:    {SQUARE_COMPRESSED} ({size_kb:.0f}KB)")
