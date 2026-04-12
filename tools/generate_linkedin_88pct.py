#!/usr/bin/env python3
"""
Generate 3 LinkedIn post images for "88% of AI Agents" post.
FLUX Pro backgrounds via Replicate + PIL compositing with PureBrain branding.
"""

import os
import sys
import time
import requests
import replicate
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv

# Load env
load_dotenv("/home/jared/projects/AI-CIV/aether/.env")

# Constants
OUTPUT_DIR = Path("/home/jared/exports/portal-files")
LOGO_PATH = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investor-avatar/pt-hex-logo.png"
FONT_BOLD = "/home/jared/.fonts/Oswald-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
WIDTH, HEIGHT = 1080, 1350

# Brand colors
BLUE = "#2a93c1"
ORANGE = "#f1420b"
WHITE = "#ffffff"
SLATE = "#94a3b8"
DARK = "#080a12"

# FLUX prompts
PROMPTS = {
    "a": (
        "photorealistic glass brain sculpture floating in dark void, "
        "volumetric light cones from upper left cerulean blue and upper right orange, "
        "caustic reflections on polished dark floor, neural circuits glowing inside the glass, "
        "atmospheric fog, cinematic lighting, 8k, hyper detailed, dark navy background"
    ),
    "b": (
        "large crystal hexagon floating and rotating in dark space, "
        "memory data streams flowing through it like liquid light, "
        "cerulean blue and orange volumetric lighting from opposing sides, "
        "glass refractions, particles dissolving from edges, deep atmospheric depth, "
        "photorealistic, cinematic, 8k"
    ),
    "c": (
        "vast dark neural vault interior, towering columns of glowing data, "
        "a single bright brain-shaped light source at center, "
        "cerulean blue ambient light with orange accent highlights, "
        "fog rolling across reflective floor, cinematic wide angle, "
        "volumetric god rays, photorealistic, 8k, dark navy atmosphere"
    ),
}

LABELS = {
    "a": "Glass Brain",
    "b": "Crystal Hexagon",
    "c": "Neural Vault",
}


def generate_flux_image(prompt: str, label: str) -> Image.Image:
    """Generate image via FLUX Pro on Replicate."""
    print(f"  Generating FLUX background for {label}...")
    start = time.time()

    for attempt in range(5):
        try:
            output = replicate.run(
                "black-forest-labs/flux-pro",
                input={
                    "prompt": prompt,
                    "width": 1080,
                    "height": 1350,
                    "num_inference_steps": 25,
                    "guidance": 3.5,
                },
            )
            break
        except Exception as e:
            if "429" in str(e) or "throttle" in str(e).lower():
                wait = 15 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s (attempt {attempt + 1}/5)...")
                time.sleep(wait)
            else:
                raise

    # output is a FileOutput URL
    url = str(output)
    print(f"  FLUX returned in {time.time() - start:.1f}s, downloading...")

    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content)).convert("RGBA")

    # Resize to exact dimensions if needed
    if img.size != (WIDTH, HEIGHT):
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)

    print(f"  Background ready: {img.size}")
    return img


def apply_gradient_overlay(img: Image.Image) -> Image.Image:
    """Apply dark gradient overlays for text readability."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Top 30% - 85% black opacity (for logo/wordmark area)
    top_zone = int(HEIGHT * 0.30)
    for y in range(top_zone):
        # Fade from 217 alpha at top to ~100 at bottom of zone
        progress = y / top_zone
        alpha = int(217 - (117 * progress))  # 85% -> ~40%
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))

    # Center zone (30%-70%) - 40% black opacity
    center_start = int(HEIGHT * 0.30)
    center_end = int(HEIGHT * 0.70)
    for y in range(center_start, center_end):
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, 102))  # 40%

    # Bottom 30% - 90% black opacity (for CTA area)
    bottom_start = int(HEIGHT * 0.70)
    for y in range(bottom_start, HEIGHT):
        progress = (y - bottom_start) / (HEIGHT - bottom_start)
        alpha = int(102 + (128 * progress))  # 40% -> ~90%
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))

    return Image.alpha_composite(img, overlay)


def hex_to_rgb(hex_color: str):
    """Convert hex color to RGB tuple."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def draw_text_with_shadow(draw, xy, text, font, fill, shadow_offset=2, shadow_color=(0, 0, 0, 200)):
    """Draw text with a drop shadow."""
    x, y = xy
    # Shadow
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    # Main text
    draw.text((x, y), text, font=font, fill=fill)


def draw_colored_wordmark(draw, center_x, y, font):
    """Draw PUREBRAIN.ai wordmark with correct per-segment colors."""
    segments = [
        ("PUREBR", hex_to_rgb(BLUE)),
        ("AI", hex_to_rgb(ORANGE)),
        ("N", hex_to_rgb(BLUE)),
        (".ai", hex_to_rgb(WHITE)),
    ]

    # Calculate total width
    total_width = 0
    segment_widths = []
    for text, _ in segments:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        segment_widths.append(w)
        total_width += w

    # Draw from left
    x = center_x - total_width // 2
    for (text, color), w in zip(segments, segment_widths):
        # Shadow
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 200))
        draw.text((x, y), text, font=font, fill=color)
        x += w


def composite_image(base: Image.Image, option: str) -> Image.Image:
    """Composite all text and branding on top of the FLUX base."""
    # Apply gradient overlays first
    img = apply_gradient_overlay(base)
    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        font_stat_huge = ImageFont.truetype(FONT_BOLD, 180)
        font_headline = ImageFont.truetype(FONT_BOLD, 56)
        font_wordmark = ImageFont.truetype(FONT_BOLD, 38)
        font_subline = ImageFont.truetype(FONT_BOLD, 32)
        font_cta_text = ImageFont.truetype(FONT_BOLD, 28)
        font_cta_url = ImageFont.truetype(FONT_BOLD, 34)
    except Exception as e:
        print(f"  Font loading issue: {e}, trying fallback...")
        font_stat_huge = ImageFont.truetype(FONT_REGULAR, 180)
        font_headline = ImageFont.truetype(FONT_REGULAR, 56)
        font_wordmark = ImageFont.truetype(FONT_REGULAR, 38)
        font_subline = ImageFont.truetype(FONT_REGULAR, 32)
        font_cta_text = ImageFont.truetype(FONT_REGULAR, 28)
        font_cta_url = ImageFont.truetype(FONT_REGULAR, 34)

    cx = WIDTH // 2  # center x

    # 1. Hexagon logo - 80px centered at y=60
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo = logo.resize((80, 80), Image.LANCZOS)
        logo_x = cx - 40
        img.paste(logo, (logo_x, 60), logo)
        print("  Logo placed.")
    except Exception as e:
        print(f"  Logo error: {e}")

    # 2. PUREBRAIN.ai wordmark at y=160
    draw_colored_wordmark(draw, cx, 160, font_wordmark)

    # 3. "88%" stat in orange at y=360
    stat_text = "88%"
    stat_bbox = draw.textbbox((0, 0), stat_text, font=font_stat_huge)
    stat_w = stat_bbox[2] - stat_bbox[0]
    stat_h = stat_bbox[3] - stat_bbox[1]
    stat_x = cx - stat_w // 2
    # Extra strong shadow for the big stat
    draw.text((stat_x + 4, 364), stat_text, font=font_stat_huge, fill=(0, 0, 0, 220))
    draw.text((stat_x + 2, 362), stat_text, font=font_stat_huge, fill=(0, 0, 0, 180))
    draw.text((stat_x, 360), stat_text, font=font_stat_huge, fill=hex_to_rgb(ORANGE))

    # 4. "of AI Agent Projects" at y=555
    line1 = "of AI Agent Projects"
    bbox1 = draw.textbbox((0, 0), line1, font=font_headline)
    w1 = bbox1[2] - bbox1[0]
    draw_text_with_shadow(draw, (cx - w1 // 2, 555), line1, font_headline, hex_to_rgb(WHITE))

    # 5. "Die Before Production" at y=625
    line2 = "Die Before Production"
    bbox2 = draw.textbbox((0, 0), line2, font=font_headline)
    w2 = bbox2[2] - bbox2[0]
    draw_text_with_shadow(draw, (cx - w2 // 2, 625), line2, font_headline, hex_to_rgb(WHITE))

    # 6. Blue divider line at y=710
    line_half = 200
    draw.line([(cx - line_half, 710), (cx + line_half, 710)], fill=hex_to_rgb(BLUE), width=3)

    # 7. "The memory layer is the difference." at y=740
    tagline = "The memory layer is the difference."
    bbox_tag = draw.textbbox((0, 0), tagline, font=font_subline)
    w_tag = bbox_tag[2] - bbox_tag[0]
    draw_text_with_shadow(draw, (cx - w_tag // 2, 740), tagline, font_subline, hex_to_rgb(SLATE))

    # 8. "Your AI should remember you" at y=1100
    cta_line = "Your AI should remember you"
    bbox_cta = draw.textbbox((0, 0), cta_line, font=font_cta_text)
    w_cta = bbox_cta[2] - bbox_cta[0]
    draw_text_with_shadow(draw, (cx - w_cta // 2, 1100), cta_line, font_cta_text, hex_to_rgb(WHITE))

    # 9. "purebrain.ai" at y=1160
    url_text = "purebrain.ai"
    bbox_url = draw.textbbox((0, 0), url_text, font=font_cta_url)
    w_url = bbox_url[2] - bbox_url[0]
    draw_text_with_shadow(draw, (cx - w_url // 2, 1160), url_text, font_cta_url, hex_to_rgb(BLUE))

    # Convert to RGB for PNG save
    final = Image.new("RGB", (WIDTH, HEIGHT), hex_to_rgb(DARK))
    final.paste(img, (0, 0), img)

    return final


def main():
    print("=" * 60)
    print("LinkedIn 88% AI Agents — Image Generator")
    print("=" * 60)

    for option in ["a", "b", "c"]:
        label = LABELS[option]
        prompt = PROMPTS[option]
        output_path = OUTPUT_DIR / f"linkedin-88pct-option-{option}.png"

        print(f"\n--- Option {option.upper()}: {label} ---")

        # Skip if already generated
        if output_path.exists() and os.path.getsize(output_path) > 100000:
            print(f"  Already exists ({os.path.getsize(output_path) / 1024:.0f}KB), skipping.")
            continue

        # Step 1: Generate FLUX background
        base = generate_flux_image(prompt, label)

        # Step 2: Composite with branding
        print(f"  Compositing branding...")
        final = composite_image(base, option)

        # Step 3: Save
        final.save(str(output_path), "PNG", quality=95)
        print(f"  Saved: {output_path}")
        print(f"  Size: {final.size}, File: {os.path.getsize(output_path) / 1024:.0f}KB")

    print("\n" + "=" * 60)
    print("ALL 3 IMAGES GENERATED SUCCESSFULLY")
    print("=" * 60)
    for opt in ["a", "b", "c"]:
        p = OUTPUT_DIR / f"linkedin-88pct-option-{opt}.png"
        print(f"  {opt.upper()}: {p}")


if __name__ == "__main__":
    main()
