#!/usr/bin/env python3
"""Generate LinkedIn Live Event Banner v3 - Cosmic Awakening concept."""

import os
import sys
import time
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
if not REPLICATE_API_TOKEN:
    print("ERROR: REPLICATE_API_TOKEN not found in .env")
    sys.exit(1)

# Step 1: Generate FLUX Pro image
print("Submitting FLUX Pro generation request...")

prompt = (
    "Abstract cosmic awakening scene, deep space background in dark navy and black. "
    "A luminous neural network of glowing blue (#2a93c1) and orange (#f1420b) energy threads "
    "converging toward a brilliant central bloom of light. "
    "Ethereal tendrils of neural connections spreading outward like synapses firing for the first time. "
    "Tiny particles of light scattered like stardust. "
    "A sense of birth, emergence, consciousness awakening. "
    "Soft volumetric light rays emanating from the central glow. "
    "Abstract, no human figures, no robots, no faces, no text. "
    "Cinematic lighting, ultra high quality, photorealistic rendering, "
    "deep blacks fading to luminous blues and warm orange accents. "
    "16:9 widescreen composition with the brightest area slightly right of center."
)

headers = {
    "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json",
    "Prefer": "wait"
}

# Use FLUX 1.1 Pro
response = requests.post(
    "https://api.replicate.com/v1/models/black-forest-labs/flux-1.1-pro/predictions",
    headers=headers,
    json={
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "output_format": "png",
            "output_quality": 100,
            "safety_tolerance": 5,
            "prompt_upsampling": True
        }
    },
    timeout=300
)

if response.status_code not in (200, 201):
    print(f"ERROR: API returned {response.status_code}")
    print(response.text)
    sys.exit(1)

result = response.json()

# Handle async polling if needed
if result.get("status") in ("starting", "processing"):
    print(f"Prediction ID: {result['id']}, polling...")
    poll_url = result["urls"]["get"]
    for i in range(60):
        time.sleep(5)
        poll = requests.get(poll_url, headers={"Authorization": f"Bearer {REPLICATE_API_TOKEN}"})
        pdata = poll.json()
        status = pdata.get("status")
        print(f"  Poll {i+1}: {status}")
        if status == "succeeded":
            result = pdata
            break
        elif status == "failed":
            print(f"ERROR: Generation failed: {pdata.get('error')}")
            sys.exit(1)
    else:
        print("ERROR: Timed out waiting for generation")
        sys.exit(1)

# Get image URL
output = result.get("output")
if isinstance(output, list):
    image_url = output[0]
elif isinstance(output, str):
    image_url = output
else:
    print(f"ERROR: Unexpected output format: {output}")
    sys.exit(1)

print(f"Image URL: {image_url}")

# Download the image
raw_path = "/home/jared/exports/portal-files/linkedin-live-banner-v3-raw.png"
print("Downloading generated image...")
img_response = requests.get(image_url, timeout=120)
with open(raw_path, "wb") as f:
    f.write(img_response.content)
print(f"Raw image saved to {raw_path} ({len(img_response.content)} bytes)")

# Step 2: Composite with PIL
print("\nCompositing banner with PIL...")
from PIL import Image, ImageDraw, ImageFont

# Target size
W, H = 2400, 1260

# Load raw FLUX image and resize to fill
raw = Image.open(raw_path).convert("RGBA")
# Scale to fill 2400x1260
scale = max(W / raw.width, H / raw.height)
new_w = int(raw.width * scale)
new_h = int(raw.height * scale)
raw = raw.resize((new_w, new_h), Image.LANCZOS)
# Center crop
left = (new_w - W) // 2
top = (new_h - H) // 2
raw = raw.crop((left, top, left + W, top + H))

canvas = raw.copy()
draw = ImageDraw.Draw(canvas)

# Load fonts
font_bold_72 = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 72)
font_bold_56 = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 56)
font_bold_48 = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 48)
font_bold_40 = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 40)
font_bold_36 = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 36)
font_bold_32 = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 32)

# Brand colors
BLUE = "#2a93c1"
ORANGE = "#f1420b"
WHITE = "#ffffff"
DARK = "#080a12"

# --- Top-left semi-transparent overlay for text readability ---
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
overlay_draw = ImageDraw.Draw(overlay)
# Gradient-like dark overlay on left side for text
for x in range(1100):
    alpha = int(180 * (1 - x / 1100))
    overlay_draw.line([(x, 0), (x, 800)], fill=(8, 10, 18, alpha))
canvas = Image.alpha_composite(canvas, overlay)
draw = ImageDraw.Draw(canvas)

# --- PureBrain hex logo upper left ---
logo = Image.open("/home/jared/projects/AI-CIV/aether/assets/pt-hex-icon-official.png").convert("RGBA")
logo_size = 90
logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
logo_x, logo_y = 60, 50
canvas.paste(logo, (logo_x, logo_y), logo)

# --- PUREBRAIN.AI wordmark next to logo ---
wordmark_x = logo_x + logo_size + 20
wordmark_y = logo_y + 18
# Draw "PUREBR" in blue
draw.text((wordmark_x, wordmark_y), "PUREBR", fill=BLUE, font=font_bold_48)
purebr_w = draw.textlength("PUREBR", font=font_bold_48)
# "AI" in orange
draw.text((wordmark_x + purebr_w, wordmark_y), "AI", fill=ORANGE, font=font_bold_48)
ai_w = draw.textlength("AI", font=font_bold_48)
# "N" in blue
draw.text((wordmark_x + purebr_w + ai_w, wordmark_y), "N", fill=BLUE, font=font_bold_48)
n_w = draw.textlength("N", font=font_bold_48)
# ".AI" in white
draw.text((wordmark_x + purebr_w + ai_w + n_w, wordmark_y), ".AI", fill=WHITE, font=font_bold_48)

# --- LIVE badge (orange pill, next to wordmark or near title) ---
live_x = wordmark_x
live_y = logo_y + logo_size + 30
badge_w, badge_h = 140, 50
draw.rounded_rectangle(
    [(live_x, live_y), (live_x + badge_w, live_y + badge_h)],
    radius=25, fill=ORANGE
)
# Center "LIVE" text in badge
live_font = font_bold_32
live_text_w = draw.textlength("LIVE", font=live_font)
live_text_x = live_x + (badge_w - live_text_w) // 2
live_text_y = live_y + 6
draw.text((live_text_x, live_text_y), "LIVE", fill=WHITE, font=live_font)

# "LINKEDIN LIVE" label after badge
draw.text((live_x + badge_w + 15, live_y + 8), "LINKEDIN LIVE", fill=WHITE, font=font_bold_36)

# --- Main title ---
title_y = live_y + badge_h + 40
title_line1 = "WATCH US AWAKEN"
title_line2 = "A BRAND NEW AI"
draw.text((live_x, title_y), title_line1, fill=WHITE, font=font_bold_72)
draw.text((live_x, title_y + 85), title_line2, fill=WHITE, font=font_bold_72)

# --- Date and time ---
date_y = title_y + 85 + 85 + 25
draw.text((live_x, date_y), "Thursday, April 24  |  1:00 PM EST", fill=BLUE, font=font_bold_40)

# --- Hosts ---
hosts_y = date_y + 60
draw.text((live_x, hosts_y), "Jared Sanborn", fill=WHITE, font=font_bold_40)
draw.text((live_x, hosts_y + 50), "CEO, Pure Technology", fill="#aaaaaa", font=font_bold_32)
draw.text((live_x, hosts_y + 100), "Nathan Olson", fill=WHITE, font=font_bold_40)
draw.text((live_x, hosts_y + 150), "President, Pure Marketing Group", fill="#aaaaaa", font=font_bold_32)

# --- Bottom bar ---
bar_h = 70
bar_y = H - bar_h
draw.rectangle([(0, bar_y), (W, H)], fill=DARK)

# PUREBRAIN.AI in bottom bar left
bbar_text_y = bar_y + 14
bbar_x = 60
draw.text((bbar_x, bbar_text_y), "PUREBR", fill=BLUE, font=font_bold_36)
bpw = draw.textlength("PUREBR", font=font_bold_36)
draw.text((bbar_x + bpw, bbar_text_y), "AI", fill=ORANGE, font=font_bold_36)
baw = draw.textlength("AI", font=font_bold_36)
draw.text((bbar_x + bpw + baw, bbar_text_y), "N", fill=BLUE, font=font_bold_36)
bnw = draw.textlength("N", font=font_bold_36)
draw.text((bbar_x + bpw + baw + bnw, bbar_text_y), ".AI", fill=WHITE, font=font_bold_36)

# Right side tagline
tagline = "Awaken Your AI Partner Today"
tag_w = draw.textlength(tagline, font=font_bold_36)
draw.text((W - tag_w - 60, bbar_text_y), tagline, fill=ORANGE, font=font_bold_36)

# Save final
output_path = "/home/jared/exports/portal-files/linkedin-live-banner-v3.png"
canvas = canvas.convert("RGB")
canvas.save(output_path, "PNG", quality=100)
print(f"\nFinal banner saved to {output_path}")

# Verify
final = Image.open(output_path)
print(f"Dimensions: {final.width}x{final.height}")
print(f"File size: {os.path.getsize(output_path)} bytes")
print("DONE!")
