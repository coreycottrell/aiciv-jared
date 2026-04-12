#!/usr/bin/env python3
"""
LinkedIn Post Image v5 - Fix orange color muting.

Compositing order:
1. FLUX base image (from v4)
2. Gradient overlays (dark semi-transparent)
3. ALL text and logo ON TOP (not under overlay)

This ensures #f1420b orange stays vibrant and isn't darkened by gradients.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import os

# === Configuration ===
WIDTH, HEIGHT = 1080, 1350
SAFE = 80  # safe zone from edges

# Colors
ORANGE = "#f1420b"
BLUE = "#2a93c1"
WHITE = "#ffffff"
LIGHT_GRAY = "#94a3b8"

# Paths
BASE_IMG = "/home/jared/exports/portal-files/linkedin-post-image-2026-04-03-v4.png"
LOGO_PATH = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investor-avatar/pt-hex-logo.png"
OUTPUT = "/home/jared/exports/portal-files/linkedin-post-image-2026-04-03-v5.png"
FONT_OSWALD = "/home/jared/.fonts/Oswald-Bold.ttf"
FONT_DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def load_font(size):
    """Load Oswald Bold, fallback to DejaVu Sans Bold."""
    try:
        return ImageFont.truetype(FONT_OSWALD, size)
    except:
        return ImageFont.truetype(FONT_DEJAVU, size)

def draw_text_with_shadow(draw, xy, text, font, fill, shadow_offset=2, shadow_color="#000000"):
    """Draw text with a black shadow for readability."""
    x, y = xy
    # Shadow
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    # Main text
    draw.text((x, y), text, font=font, fill=fill)

def draw_text_centered_with_shadow(draw, y, text, font, fill, canvas_width=WIDTH, shadow_offset=2):
    """Draw centered text with shadow."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (canvas_width - tw) // 2
    draw_text_with_shadow(draw, (x, y), text, font, fill, shadow_offset)

def draw_multicolor_text_centered(draw, y, segments, canvas_width=WIDTH, shadow_offset=2):
    """Draw centered text with multiple color segments.
    segments = [(text, font, color), ...]
    """
    # Calculate total width
    total_w = 0
    for text, font, color in segments:
        bbox = draw.textbbox((0, 0), text, font=font)
        total_w += bbox[2] - bbox[0]

    x = (canvas_width - total_w) // 2
    for text, font, color in segments:
        draw_text_with_shadow(draw, (x, y), text, font, color, shadow_offset)
        bbox = draw.textbbox((0, 0), text, font=font)
        x += bbox[2] - bbox[0]

def main():
    # --- Step 1: Load base image from v4 ---
    base = Image.open(BASE_IMG).convert("RGBA")
    base = base.resize((WIDTH, HEIGHT), Image.LANCZOS)

    # --- Step 2: Apply gradient overlays FIRST (using numpy for speed) ---
    alpha_channel = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)

    top_zone = int(HEIGHT * 0.30)
    bot_zone = int(HEIGHT * 0.30)

    # Top gradient: 85% opacity fading to 45% (center opacity)
    for y in range(top_zone):
        progress = y / top_zone  # 0 at top, 1 at boundary
        alpha_channel[y, :] = int(217 * (1 - progress) + 115 * progress)

    # Center band: 45% opacity
    center_alpha = int(255 * 0.45)
    alpha_channel[top_zone:HEIGHT - bot_zone, :] = center_alpha

    # Bottom gradient: 45% (center) fading to 90% at very bottom
    for y in range(HEIGHT - bot_zone, HEIGHT):
        progress = (y - (HEIGHT - bot_zone)) / bot_zone  # 0 at boundary, 1 at bottom
        alpha_channel[y, :] = int(115 * (1 - progress) + 230 * progress)

    # Build RGBA overlay from alpha channel
    overlay_arr = np.zeros((HEIGHT, WIDTH, 4), dtype=np.uint8)
    overlay_arr[:, :, 3] = alpha_channel  # R,G,B stay 0 (black), alpha varies
    overlay = Image.fromarray(overlay_arr, "RGBA")

    # Composite overlay onto base
    composited = Image.alpha_composite(base, overlay)

    # --- Step 3: Draw ALL text ON TOP of overlaid image ---
    # Convert to RGBA for text drawing
    canvas = composited.copy()
    draw = ImageDraw.Draw(canvas)

    # Load fonts
    font_wordmark = load_font(38)
    font_88 = load_font(180)
    font_subtitle = load_font(56)
    font_tagline = load_font(32)
    font_cta = load_font(28)
    font_url = load_font(34)

    # 3a. Hexagon logo (80px, centered, y=60)
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_size = 80
    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
    logo_x = (WIDTH - logo_size) // 2
    canvas.paste(logo, (logo_x, 60), logo)

    # 3b. PUREBRAIN.ai wordmark (y=160)
    # PUREBR=#2a93c1, AI=#f1420b, N=#2a93c1, .ai=#ffffff
    wordmark_segments = [
        ("PUREBR", font_wordmark, BLUE),
        ("AI", font_wordmark, ORANGE),
        ("N", font_wordmark, BLUE),
        (".ai", font_wordmark, WHITE),
    ]
    draw_multicolor_text_centered(draw, 160, wordmark_segments)

    # 3c. "88%" (180pt, pure orange, centered, y=360)
    draw_text_centered_with_shadow(draw, 360, "88%", font_88, ORANGE, shadow_offset=3)

    # 3d. "of AI Agent Projects" (56pt white, y=555)
    draw_text_centered_with_shadow(draw, 555, "of AI Agent Projects", font_subtitle, WHITE)

    # 3e. "Die Before Production" (56pt white, y=625)
    draw_text_centered_with_shadow(draw, 625, "Die Before Production", font_subtitle, WHITE)

    # 3f. Blue divider line (y=710)
    line_w = 300
    line_x = (WIDTH - line_w) // 2
    draw.line([(line_x, 710), (line_x + line_w, 710)], fill=BLUE, width=3)

    # 3g. "The memory layer is the difference." (32pt light gray, y=740)
    draw_text_centered_with_shadow(draw, 740, "The memory layer is the difference.", font_tagline, LIGHT_GRAY)

    # 3h. "Your AI should remember you" (28pt white, y=1100)
    draw_text_centered_with_shadow(draw, 1100, "Your AI should remember you", font_cta, WHITE)

    # 3i. "purebrain.ai" (34pt blue, y=1160)
    draw_text_centered_with_shadow(draw, 1160, "purebrain.ai", font_url, BLUE)

    # --- Step 4: Save as PNG (flatten to RGB) ---
    final = canvas.convert("RGB")
    final.save(OUTPUT, "PNG", quality=95)
    print(f"Saved: {OUTPUT}")
    print(f"Size: {final.size}")

    # Verify file
    verify = Image.open(OUTPUT)
    print(f"Verified: {verify.size}, mode={verify.mode}")

if __name__ == "__main__":
    main()
