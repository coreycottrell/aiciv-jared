#!/usr/bin/env python3
"""
Generate 2400x1260 landscape blog banners using FLUX Pro + PIL compositing.
Option D format: bottom gradient with title text.
Brand: hex icon + PUREBRAIN.AI wordmark (PUREBR blue, AI orange, N blue, .AI white)
"""

import os
import sys
import time
import urllib.request
import replicate
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

# --- Config ---
WIDTH, HEIGHT = 2400, 1260
DARK = "#080a12"
BLUE = "#2a93c1"
ORANGE = "#f1420b"
WHITE = "#ffffff"
FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"
HEX_ICON_PATH = "/home/jared/projects/AI-CIV/aether/assets/pt-hex-icon-official.png"
RAW_DIR = "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-may5/flux-raw-banners"
FINAL_DIR = "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-may5"

os.environ["REPLICATE_API_TOKEN"] = "r8_7PtU7gFQ9yKWXemIFbFHnReAMCdgS9H1zhfFt"

FLUX_PREFIX = "Professional dark moody tech aesthetic, cinematic lighting, 8k quality, wide landscape composition, no text no words no letters, "

# Blog posts that need banners
BLOGS = [
    {
        "slug": "ai-works-247am",
        "title": "WHAT YOUR AI DID\nLAST NIGHT",
        "subtitle": "The 3am economy is real",
        "flux_prompt": FLUX_PREFIX + "Dark server room at night, blue and purple ambient glow from rack LEDs, cinematic depth of field, moody atmosphere, digital work happening in darkness"
    },
    {
        "slug": "ai-forgot-everything",
        "title": "THE REAL COST OF\nAI AMNESIA",
        "subtitle": "A CFO's nightmare calculated",
        "flux_prompt": FLUX_PREFIX + "Shattered glass memory fragments floating in dark void, neural connections breaking apart, data evaporating upward, blue and red accent lighting"
    },
    {
        "slug": "skeptic-to-coceo",
        "title": "FROM SKEPTIC\nTO CO-CEO",
        "subtitle": "How I learned to trust my AI",
        "flux_prompt": FLUX_PREFIX + "Journey path from shadow into bright blue light, transformation scene, person silhouette walking from doubt toward illuminated future"
    },
    {
        "slug": "blog-written-sunday",
        "title": "THE SUNDAY BATCH",
        "subtitle": "A week of content in 30 minutes",
        "flux_prompt": FLUX_PREFIX + "Assembly line of glowing content blocks being produced efficiently, factory of ideas, blue conveyor belt with illuminated article thumbnails"
    },
]


def generate_flux_image(prompt, slug):
    """Generate base image using FLUX Pro via Replicate."""
    raw_path = os.path.join(RAW_DIR, f"{slug}-raw.jpg")
    if os.path.exists(raw_path):
        print(f"  [CACHED] Using existing raw image")
        return Image.open(raw_path)

    print(f"  [FLUX] Generating base image...")
    # FLUX Pro max width is 1440, generate at 1440x756 (same aspect ratio) and upscale
    output = replicate.run(
        "black-forest-labs/flux-pro",
        input={
            "prompt": prompt,
            "width": 1440,
            "height": 756,
            "num_inference_steps": 25,
            "guidance_scale": 3.5,
        }
    )

    # Handle output (can be URL string or FileOutput)
    if hasattr(output, 'read'):
        img_data = output.read()
    elif isinstance(output, str):
        req = urllib.request.Request(output, headers={"User-Agent": "Mozilla/5.0"})
        img_data = urllib.request.urlopen(req).read()
    elif isinstance(output, list) and output:
        url = str(output[0])
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        img_data = urllib.request.urlopen(req).read()
    else:
        url = str(output)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        img_data = urllib.request.urlopen(req).read()

    img = Image.open(BytesIO(img_data)).convert("RGB")
    img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
    img.save(raw_path, quality=95)
    print(f"  [FLUX] Saved raw: {raw_path}")
    return img


def draw_wordmark(draw, x, y, font_size=28):
    """Draw PUREBRAIN.AI wordmark with correct brand colors."""
    font = ImageFont.truetype(FONT_PATH, font_size)
    parts = [
        ("PUREBR", BLUE),
        ("AI", ORANGE),
        ("N", BLUE),
        (".AI", WHITE),
    ]
    cx = x
    for text, color in parts:
        draw.text((cx, y), text, fill=color, font=font)
        bbox = font.getbbox(text)
        cx += bbox[2] - bbox[0]


def composite_banner(base_img, blog):
    """Apply Option D bottom gradient + branding to base image."""
    img = base_img.copy()
    draw = ImageDraw.Draw(img)

    # --- Bottom gradient (60% opacity dark gradient from bottom) ---
    gradient_height = int(HEIGHT * 0.45)
    for i in range(gradient_height):
        alpha = int(220 * (i / gradient_height))
        y = HEIGHT - gradient_height + i
        draw.rectangle([(0, y), (WIDTH, y)], fill=(8, 10, 18, alpha))

    # Since we can't use alpha on RGB, create with RGBA
    img_rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    gradient_height = int(HEIGHT * 0.50)
    for i in range(gradient_height):
        alpha = int(230 * (i / gradient_height))
        y = HEIGHT - gradient_height + i
        overlay_draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(8, 10, 18, alpha))

    img_rgba = Image.alpha_composite(img_rgba, overlay)

    # Convert back to draw text
    draw = ImageDraw.Draw(img_rgba)

    # --- Title text ---
    title_font = ImageFont.truetype(FONT_PATH, 72)
    lines = blog["title"].split("\n")
    title_y = HEIGHT - 280
    for line in lines:
        draw.text((80, title_y), line, fill=WHITE, font=title_font)
        title_y += 85

    # --- Subtitle ---
    if blog.get("subtitle"):
        sub_font = ImageFont.truetype(FONT_PATH, 36)
        draw.text((80, title_y + 10), blog["subtitle"], fill=BLUE, font=sub_font)

    # --- Hex icon + wordmark in top-left ---
    try:
        hex_icon = Image.open(HEX_ICON_PATH).convert("RGBA")
        hex_icon = hex_icon.resize((50, 50), Image.LANCZOS)
        img_rgba.paste(hex_icon, (40, 30), hex_icon)
    except Exception as e:
        print(f"  [WARN] Could not load hex icon: {e}")

    draw_wordmark(draw, 100, 40, 32)

    # --- "The Neural Feed" label bottom-right ---
    feed_font = ImageFont.truetype(FONT_PATH, 24)
    draw.text((WIDTH - 320, HEIGHT - 60), "THE NEURAL FEED", fill=WHITE, font=feed_font)

    # --- "PUREBRAIN.AI" bottom-left ---
    draw_wordmark(draw, 80, HEIGHT - 60, 24)

    # Convert to RGB for saving as JPEG
    final = img_rgba.convert("RGB")
    return final


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(FINAL_DIR, exist_ok=True)

    results = []

    for blog in BLOGS:
        slug = blog["slug"]
        print(f"\n{'='*60}")
        print(f"Processing: {slug}")
        print(f"{'='*60}")

        try:
            # Generate base image
            base = generate_flux_image(blog["flux_prompt"], slug)

            # Composite with branding
            final = composite_banner(base, blog)

            # Save
            out_path = os.path.join(FINAL_DIR, f"{slug}-banner.jpg")
            final.save(out_path, quality=95)
            print(f"  [DONE] Saved: {out_path}")
            print(f"  [SIZE] {final.size[0]}x{final.size[1]}")
            results.append({"slug": slug, "path": out_path, "success": True})

        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
            results.append({"slug": slug, "error": str(e), "success": False})

        time.sleep(12)  # Rate limit between FLUX calls (low credit tier = 6/min)

    # Summary
    print(f"\n{'='*60}")
    print(f"RESULTS: {sum(1 for r in results if r['success'])}/{len(results)} banners generated")
    for r in results:
        status = "OK" if r["success"] else f"FAIL: {r.get('error','')[:50]}"
        print(f"  {r['slug']}: {status}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
