#!/usr/bin/env python3
"""
Fix 12 standalone LinkedIn banners (1080x1350) that had alignment issues.
Uses FLUX Pro via Replicate for backgrounds + PIL for text overlay.
Constitutional: saves raw FLUX images separately.
"""

import os
import sys
import time
import requests
import replicate
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# === CONFIG ===
OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/standalone-banner-fix")
RAW_DIR = OUTPUT_DIR / "flux-raw"
FINAL_DIR = OUTPUT_DIR / "final"
RAW_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"
HEX_ICON_PATH = "/home/jared/projects/AI-CIV/aether/assets/pt-hex-icon-official.png"

# Brand colors
BLUE = "#2a93c1"
ORANGE = "#f1420b"
DARK_BG = "#080a12"
WHITE = "#ffffff"

WIDTH = 1080
HEIGHT = 1350

# === 5 UNIQUE THEMES ===
THEMES = {
    "companies-winning": {
        "flux_prompt": "Abstract dark moody corporate boardroom scene with glowing blue and orange holographic data charts floating in air, futuristic technology atmosphere, dark background, cinematic lighting, no text, no words, no letters, professional business aesthetic, depth of field",
        "title_lines": ["THE COMPANIES", "WINNING WITH AI"],
        "title_colors": [WHITE, BLUE],  # per line
        "subtitle": "STRATEGY OVER SPEND",
        "cta": "Strategy wins",
        "post_ids": [
            "bfc6759b-38e8-4bee-93fc-7238e3923d6f",
            "769d35b2-50c1-4229-ba06-9dd56bda08cd",
            "b7eb2210-1277-4206-b8a2-748e88fdeae5",
            "2e9146e7-1ade-4f96-a40c-e8bd9cc4fc07",
        ],
    },
    "implementations-fail": {
        "flux_prompt": "Abstract dark scene of broken glass circuit board fragments floating in space, shattered technology pieces with blue and orange edge lighting, moody cinematic atmosphere, dark background, no text, no words, no letters, high contrast",
        "title_lines": ["WHY AI", "IMPLEMENTATIONS FAIL"],
        "title_colors": [WHITE, ORANGE],
        "subtitle": "EXPECTATIONS VS REALITY",
        "cta": "Set it up right",
        "post_ids": [
            "71436ff4-848c-4998-be40-4cc4eec3ee02",
            "9a3e40f6-a5fc-4303-a9fd-2cde6d0c9e9f",
            "9e3ca912-10db-4d13-b487-a3bc80d215bf",
        ],
    },
    "ceo-questions": {
        "flux_prompt": "Abstract dark scene of three glowing geometric question marks floating in dark space, holographic blue and orange light, minimalist futuristic CEO strategy room, dark background, no text, no words, no letters, cinematic depth of field",
        "title_lines": ["THREE QUESTIONS", "EVERY CEO SHOULD ASK"],
        "title_colors": [ORANGE, WHITE],
        "subtitle": "AI STRATEGY CHECK",
        "cta": "Ask the right questions",
        "post_ids": [
            "aee4e9a3-74e8-4108-a846-26481e9c96e5",
            "7d44dc85-3554-44d4-aec2-fc9d6ba0bfbe",
            "18e9c0bc-ea0b-49b2-8ae2-0622fb29b243",
        ],
    },
    "agent-market": {
        "flux_prompt": "Abstract dark scene of ascending glowing bar chart made of light beams, blue and orange gradient, futuristic financial data visualization floating in dark space, no text, no words, no letters, cinematic lighting, moody dark background",
        "title_lines": ["$52.6 BILLION", "AI AGENT MARKET"],
        "title_colors": [ORANGE, BLUE],
        "subtitle": "BY 2030 — ARE YOU READY?",
        "cta": "Get ahead of the curve",
        "post_ids": [
            "735b7474-1c27-4e51-be14-8e21fabd13fc",
        ],
    },
    "ai-pitch": {
        "flux_prompt": "Abstract dark scene of a glowing AI avatar hologram presenting to shadowy audience silhouettes, blue and orange neon accent lighting, futuristic pitch room, dark background, no text, no words, no letters, cinematic atmosphere",
        "title_lines": ["LET MY AI", "PITCH YOU"],
        "title_colors": [WHITE, ORANGE],
        "subtitle": "THE FUTURE OF FUNDRAISING",
        "cta": "See it in action",
        "post_ids": [
            "25095891-9e85-43cd-aa43-2b08dccdaaaf",
        ],
    },
}


def generate_flux_background(prompt: str, theme_key: str) -> Path:
    """Generate a FLUX Pro background image via Replicate."""
    raw_path = RAW_DIR / f"{theme_key}-flux-raw.png"
    if raw_path.exists():
        print(f"  [CACHED] {raw_path}")
        return raw_path

    print(f"  Generating FLUX background for '{theme_key}'...")
    output = replicate.run(
        "black-forest-labs/flux-pro",
        input={
            "prompt": prompt,
            "width": 1080,
            "height": 1080,  # Square for center crop to 1080x1350
            "num_outputs": 1,
            "guidance": 3.5,
            "num_inference_steps": 28,
            "output_format": "png",
        },
    )

    # output is a FileOutput or URL
    if hasattr(output, "read"):
        img_bytes = output.read()
    elif isinstance(output, list):
        url = str(output[0])
        img_bytes = requests.get(url).content
    else:
        url = str(output)
        img_bytes = requests.get(url).content

    raw_path.write_bytes(img_bytes)
    print(f"  Saved raw FLUX: {raw_path} ({len(img_bytes):,} bytes)")
    return raw_path


def create_standalone_banner(
    flux_bg_path: Path,
    title_lines: list,
    title_colors: list,
    subtitle: str,
    cta: str,
    output_path: Path,
):
    """Create a 1080x1350 standalone banner with PIL overlay on FLUX background."""
    # Load fonts
    font_title = ImageFont.truetype(FONT_PATH, 72)
    font_subtitle = ImageFont.truetype(FONT_PATH, 24)
    font_wordmark = ImageFont.truetype(FONT_PATH, 22)
    font_cta = ImageFont.truetype(FONT_PATH, 22)
    font_small = ImageFont.truetype(FONT_PATH, 18)

    # Create canvas
    canvas = Image.new("RGB", (WIDTH, HEIGHT), DARK_BG)

    # Load and place FLUX background in center
    flux_bg = Image.open(flux_bg_path).convert("RGB")
    # Resize to fill width, then crop/position in center area
    flux_bg = flux_bg.resize((WIDTH, WIDTH), Image.LANCZOS)
    # Place at vertical center (offset for top/bottom bars)
    y_offset = (HEIGHT - WIDTH) // 2
    canvas.paste(flux_bg, (0, y_offset))

    # Apply dark gradient overlay for text readability
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    # Top gradient (dark to transparent)
    for y in range(400):
        alpha = int(240 * (1 - y / 400))
        draw_overlay.line([(0, y), (WIDTH, y)], fill=(8, 10, 18, alpha))

    # Bottom gradient (transparent to dark)
    for y in range(HEIGHT - 500, HEIGHT):
        progress = (y - (HEIGHT - 500)) / 500
        alpha = int(250 * progress)
        draw_overlay.line([(0, y), (WIDTH, y)], fill=(8, 10, 18, alpha))

    # Center darkening for title readability
    for y in range(HEIGHT // 2 - 150, HEIGHT // 2 + 200):
        mid = HEIGHT // 2 + 25
        dist = abs(y - mid) / 175
        alpha = int(160 * max(0, 1 - dist))
        draw_overlay.line([(0, y), (WIDTH, y)], fill=(8, 10, 18, alpha))

    canvas = canvas.convert("RGBA")
    canvas = Image.alpha_composite(canvas, overlay)
    canvas = canvas.convert("RGB")

    draw = ImageDraw.Draw(canvas)

    # === TOP BAR ===
    # Hex icon
    hex_icon = Image.open(HEX_ICON_PATH).convert("RGBA")
    icon_size = 48
    hex_icon = hex_icon.resize((icon_size, icon_size), Image.LANCZOS)

    # Calculate top bar layout - CENTERED
    top_y = 45
    # Wordmark text
    wm_text = "PUREBRAIN.AI"
    wm_bbox = draw.textbbox((0, 0), wm_text, font=font_wordmark)
    wm_w = wm_bbox[2] - wm_bbox[0]
    total_top_w = icon_size + 12 + wm_w
    start_x = (WIDTH - total_top_w) // 2

    canvas.paste(hex_icon, (start_x, top_y), hex_icon)

    # Draw colored wordmark
    wx = start_x + icon_size + 12
    wy = top_y + (icon_size - 22) // 2
    _draw_wordmark(draw, wx, wy, font_wordmark)

    # === TITLE (CENTER) ===
    title_y_start = HEIGHT // 2 - 60
    for i, (line, color) in enumerate(zip(title_lines, title_colors)):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        tw = bbox[2] - bbox[0]
        tx = (WIDTH - tw) // 2
        ty = title_y_start + i * 80

        # Text shadow
        draw.text((tx + 2, ty + 2), line, fill="#000000", font=font_title)
        draw.text((tx, ty), line, fill=color, font=font_title)

    # Subtitle below title
    sub_y = title_y_start + len(title_lines) * 80 + 20
    sub_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_x = (WIDTH - sub_w) // 2
    draw.text((sub_x, sub_y), subtitle, fill=(255, 255, 255, 100), font=font_subtitle)

    # === BOTTOM BAR ===
    bottom_y = HEIGHT - 90

    # Left: PUREBRAIN.AI
    _draw_wordmark(draw, 40, bottom_y, font_wordmark)

    # Right: CTA in orange
    cta_text = cta.upper() + "  "
    url_text = "PUREBRAIN.AI"
    cta_bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
    url_bbox = draw.textbbox((0, 0), url_text, font=font_cta)
    cta_w = (cta_bbox[2] - cta_bbox[0]) + (url_bbox[2] - url_bbox[0])
    cta_x = WIDTH - cta_w - 40
    draw.text((cta_x, bottom_y), cta_text, fill=ORANGE, font=font_cta)
    draw.text((cta_x + cta_bbox[2] - cta_bbox[0], bottom_y), url_text, fill=BLUE, font=font_cta)

    # Thin separator lines
    draw.line([(40, bottom_y - 20), (WIDTH - 40, bottom_y - 20)], fill=(42, 147, 193, 30), width=1)
    draw.line([(40, top_y + icon_size + 15), (WIDTH - 40, top_y + icon_size + 15)], fill=(42, 147, 193, 30), width=1)

    # Save as high-quality JPEG
    canvas.save(output_path, "JPEG", quality=95)
    print(f"  Saved: {output_path} ({output_path.stat().st_size:,} bytes)")


def _draw_wordmark(draw, x, y, font):
    """Draw the colored PUREBRAIN.AI wordmark."""
    parts = [
        ("PURE", WHITE),
        ("BR", BLUE),
        ("AI", ORANGE),
        ("N", BLUE),
        (".AI", WHITE),
    ]
    cx = x
    for text, color in parts:
        draw.text((cx, y), text, fill=color, font=font)
        bbox = draw.textbbox((0, 0), text, font=font)
        cx += bbox[2] - bbox[0]


def main():
    print("=" * 60)
    print("STANDALONE BANNER FIX - 12 posts, 5 themes")
    print("=" * 60)

    all_outputs = []

    for theme_key, theme in THEMES.items():
        print(f"\n--- Theme: {theme_key} ({len(theme['post_ids'])} posts) ---")

        # Step 1: Generate FLUX background
        flux_path = generate_flux_background(theme["flux_prompt"], theme_key)

        # Step 2: Create banner for each post ID
        for post_id in theme["post_ids"]:
            short_id = post_id[:8]
            output_path = FINAL_DIR / f"{short_id}-standalone.jpg"

            create_standalone_banner(
                flux_bg_path=flux_path,
                title_lines=theme["title_lines"],
                title_colors=theme["title_colors"],
                subtitle=theme["subtitle"],
                cta=theme["cta"],
                output_path=output_path,
            )
            all_outputs.append((post_id, output_path))

    print(f"\n{'=' * 60}")
    print(f"COMPLETE: {len(all_outputs)} banners generated")
    print(f"Raw FLUX images: {RAW_DIR}")
    print(f"Final banners: {FINAL_DIR}")
    for post_id, path in all_outputs:
        print(f"  {post_id[:8]} -> {path.name}")


if __name__ == "__main__":
    main()
