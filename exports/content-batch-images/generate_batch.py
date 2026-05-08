#!/usr/bin/env python3
"""
Generate 7 standalone LinkedIn banners (1080x1350) for Apr 24-27 content batch.
v4.2 format: top bar + blue line + FLUX bg with title + blue line + bottom bar.
"""

import os
import sys
import time
import urllib.request
import replicate
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

# --- Config ---
WIDTH, HEIGHT = 1080, 1350
TOP_BAR_H = 140
BOTTOM_BAR_H = 90
ACCENT_H = 2
DARK = "#080a12"
BLUE = "#2a93c1"
ORANGE = "#f1420b"
WHITE = "#ffffff"
FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"
HEX_ICON_PATH = "/home/jared/projects/AI-CIV/aether/assets/pt-hex-icon-official.png"
RAW_DIR = "/home/jared/projects/AI-CIV/aether/exports/content-batch-images/flux-raw"
FINAL_DIR = "/home/jared/projects/AI-CIV/aether/exports/content-batch-images"

os.environ["REPLICATE_API_TOKEN"] = "r8_HU0LIcWclhNkx01Qod0rms8bFeqovK03yBDLr"

# --- Posts (7 standalones) ---
POSTS = [
    {
        "slug": "purebrain-vs-va-cost",
        "title": "PureBrain vs Hiring a VA:\nReal Cost Breakdown",
        "flux_prompt": "Abstract dark futuristic scene, glowing digital balance scale weighing golden coins against blue holographic AI brain, dark moody background with blue #2a93c1 and orange #f1420b accent lighting, minimalist composition, volumetric light rays, shallow depth of field, film grain, 8k photorealistic, Gleb Kuznetsov style, no text"
    },
    {
        "slug": "6-months-ai-partner",
        "title": "What 6 Months with an\nAI Partner Actually Looks Like",
        "flux_prompt": "Abstract dark timeline visualization, glowing blue #2a93c1 path curving upward through dark space, small bright nodes along the path growing brighter toward the end, orange #f1420b energy sparks at the peak, dark moody atmosphere, cinematic volumetric lighting, bokeh orbs, shallow depth of field, film grain, 8k photorealistic quality, no text"
    },
    {
        "slug": "147k-question-ai",
        "title": "The $147K Question\nNobody's Asking About AI",
        "flux_prompt": "Abstract dark scene with floating translucent glass dollar signs dissolving into blue digital particles, dark moody background, blue #2a93c1 and orange #f1420b accent rim lighting, volumetric fog, dramatic contrast, shallow depth of field with bokeh, cinematic lighting, film grain, 8k photorealistic, no text"
    },
    {
        "slug": "35-businesses-named-ai",
        "title": "Why 35 Businesses Named\nTheir AI Before Paying",
        "flux_prompt": "Abstract dark scene with a glowing blue #2a93c1 holographic name tag floating in dark space, warm orange #f1420b light emanating from behind, soft particle effects, dark moody atmosphere, glass morphism reflections, volumetric light beams, shallow depth of field, bokeh, film grain, 8k photorealistic, Gleb Kuznetsov aesthetic, no text"
    },
    {
        "slug": "10000-lines-ai-wrote",
        "title": "Your AI Wrote 10,000 Lines\nLast Week. Did You Even Know?",
        "flux_prompt": "Abstract dark scene with thousands of glowing blue code lines streaming downward like a waterfall of light, a single human silhouette standing in front illuminated by the glow, orange #f1420b accent highlights, dark moody atmosphere, volumetric light rays, cinematic composition, shallow depth of field, film grain, 8k photorealistic, no text"
    },
    {
        "slug": "day1-vs-month6-ai",
        "title": "Day 1 vs Month 6\nwith an AI Partner",
        "flux_prompt": "Abstract dark split composition, left side dim and cold with a faint blue spark, right side vibrant with glowing interconnected neural network in blue #2a93c1 and orange #f1420b, representing growth over time, dark moody background, volumetric lighting, glass reflections, shallow depth of field, bokeh, film grain, 8k photorealistic, no text"
    },
    {
        "slug": "best-context-not-best-models",
        "title": "The Companies Winning with AI\nAren't Using the Best Models",
        "flux_prompt": "Abstract dark scene with a glowing orb of layered contextual data in blue #2a93c1 floating above a dim generic AI chip, the orb radiates warmth and complexity while the chip below is cold and flat, orange #f1420b accent rim light, dark moody atmosphere, volumetric fog, shallow depth of field, cinematic, film grain, 8k photorealistic, no text"
    },
]


def generate_flux(prompt, slug):
    """Generate FLUX Pro background image."""
    raw_path = os.path.join(RAW_DIR, f"{slug}-flux-raw.png")
    if os.path.exists(raw_path):
        print(f"  [SKIP] FLUX raw already exists: {slug}")
        return raw_path

    print(f"  [FLUX] Generating: {slug}...")
    output = replicate.run(
        "black-forest-labs/flux-1.1-pro",
        input={
            "prompt": prompt,
            "width": 1080,
            "height": 1080,
            "output_format": "png",
            "output_quality": 95,
            "safety_tolerance": 2,
        }
    )

    # Handle FileOutput or URL
    try:
        img_bytes = output.read()
    except AttributeError:
        url = str(output)
        img_bytes = urllib.request.urlopen(url).read()

    with open(raw_path, "wb") as f:
        f.write(img_bytes)

    print(f"  [FLUX] Saved: {raw_path} ({len(img_bytes)//1024}KB)")
    return raw_path


def create_banner(flux_path, title, slug):
    """Apply v4.2 standalone overlay to FLUX background."""
    final_path = os.path.join(FINAL_DIR, f"{slug}-standalone.jpg")

    # Create canvas
    canvas = Image.new("RGB", (WIDTH, HEIGHT), DARK)

    # Load and place FLUX background in image area
    flux_img = Image.open(flux_path).convert("RGB")
    flux_img = flux_img.resize((1080, 1080), Image.LANCZOS)

    # Image area starts after top bar + accent line
    img_y_start = TOP_BAR_H + ACCENT_H
    # Image area ends before bottom accent + bottom bar
    img_area_h = HEIGHT - TOP_BAR_H - ACCENT_H - ACCENT_H - BOTTOM_BAR_H  # 1116px

    # Center the 1080x1080 flux in the 1080x1116 image area
    flux_y = img_y_start + (img_area_h - 1080) // 2
    canvas.paste(flux_img, (0, flux_y))

    draw = ImageDraw.Draw(canvas)

    # --- Top bar ---
    draw.rectangle([(0, 0), (WIDTH, TOP_BAR_H)], fill=DARK)

    # Load hex icon
    hex_icon = Image.open(HEX_ICON_PATH).convert("RGBA")
    icon_size = 80
    hex_icon = hex_icon.resize((icon_size, icon_size), Image.LANCZOS)

    # Load fonts
    font_wordmark = ImageFont.truetype(FONT_PATH, 46)
    font_title = ImageFont.truetype(FONT_PATH, 62)
    font_bottom_wm = ImageFont.truetype(FONT_PATH, 26)
    font_cta = ImageFont.truetype(FONT_PATH, 22)

    # Wordmark text
    wm_text = "PUREBRAIN.AI"
    wm_bbox = draw.textbbox((0, 0), wm_text, font=font_wordmark)
    wm_w = wm_bbox[2] - wm_bbox[0]
    wm_h = wm_bbox[3] - wm_bbox[1]
    wm_top_offset = wm_bbox[1]

    # Center icon + gap + wordmark as unit
    gap = 16
    unit_w = icon_size + gap + wm_w
    unit_x = (WIDTH - unit_w) // 2

    # Center icon vertically in top bar
    bar_center = TOP_BAR_H // 2
    icon_y = bar_center - icon_size // 2
    canvas.paste(hex_icon, (unit_x, icon_y), hex_icon)

    # Center wordmark vertically - align visual midline with icon midline
    wm_x = unit_x + icon_size + gap
    wm_y = bar_center - wm_top_offset - wm_h // 2

    # Draw wordmark with brand colors: PUREBR(blue) + AI(orange) + N(blue) + .AI(white)
    # Actually: PUREBR(blue) + A(orange) + I(orange) + N(blue) + .(white) + A(white) + I(white)
    # Corrected brand: PUREBR=#2a93c1, AI=#f1420b, N=#2a93c1, .ai=white
    parts = [
        ("PUREBR", BLUE),
        ("AI", ORANGE),
        ("N", BLUE),
        (".AI", WHITE),
    ]
    cx = wm_x
    for text_part, color in parts:
        draw.text((cx, wm_y), text_part, fill=color, font=font_wordmark)
        part_bbox = draw.textbbox((0, 0), text_part, font=font_wordmark)
        cx += part_bbox[2] - part_bbox[0]

    # --- Blue accent line (top) ---
    accent1_y = TOP_BAR_H
    draw.rectangle([(0, accent1_y), (WIDTH, accent1_y + ACCENT_H)], fill=BLUE)

    # --- Title text overlay on image area ---
    # Add dark gradient behind title for readability
    title_lines = title.split("\n")

    # Calculate total title height
    line_heights = []
    line_widths = []
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        line_heights.append(bbox[3] - bbox[1])
        line_widths.append(bbox[2] - bbox[0])

    line_spacing = 12
    total_title_h = sum(line_heights) + line_spacing * (len(title_lines) - 1)

    # Position title in center of image area
    title_center_y = img_y_start + img_area_h // 2
    title_start_y = title_center_y - total_title_h // 2

    # Draw semi-transparent dark gradient behind title
    grad_pad_y = 60
    grad_pad_x = 40
    grad_top = title_start_y - grad_pad_y
    grad_bot = title_start_y + total_title_h + grad_pad_y

    # Create gradient overlay
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for y in range(grad_top, grad_bot):
        # Bell curve opacity: strongest at center, fading at edges
        center = (grad_top + grad_bot) // 2
        dist = abs(y - center) / ((grad_bot - grad_top) / 2)
        alpha = int(180 * (1 - dist * dist))  # Quadratic falloff
        alpha = max(0, min(180, alpha))
        overlay_draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(8, 10, 18, alpha))

    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba = Image.alpha_composite(canvas_rgba, overlay)
    canvas = canvas_rgba.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # Draw title lines with stroke (dark border for readability)
    cur_y = title_start_y
    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        lw = bbox[2] - bbox[0]
        lx = (WIDTH - lw) // 2

        # Dark stroke (4px border)
        stroke_color = "#080a12"
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                if dx*dx + dy*dy <= 16:
                    draw.text((lx + dx, cur_y + dy), line, fill=stroke_color, font=font_title)

        # White text
        draw.text((lx, cur_y), line, fill=WHITE, font=font_title)
        cur_y += line_heights[i] + line_spacing

    # --- Blue accent line (bottom) ---
    accent2_y = HEIGHT - BOTTOM_BAR_H - ACCENT_H
    draw.rectangle([(0, accent2_y), (WIDTH, accent2_y + ACCENT_H)], fill=BLUE)

    # --- Bottom bar ---
    bot_y = HEIGHT - BOTTOM_BAR_H
    draw.rectangle([(0, bot_y), (WIDTH, HEIGHT)], fill=DARK)

    # Bottom wordmark left (brand colors, 26pt)
    font_bwm = font_bottom_wm
    bwm_parts = [
        ("PUREBR", BLUE),
        ("AI", ORANGE),
        ("N", BLUE),
        (".AI", WHITE),
    ]
    bwm_x = 40
    bwm_bbox = draw.textbbox((0, 0), "PUREBRAIN.AI", font=font_bwm)
    bwm_h = bwm_bbox[3] - bwm_bbox[1]
    bwm_top_offset = bwm_bbox[1]
    bwm_y = bot_y + (BOTTOM_BAR_H // 2) - bwm_top_offset - bwm_h // 2
    for text_part, color in bwm_parts:
        draw.text((bwm_x, bwm_y), text_part, fill=color, font=font_bwm)
        part_bbox = draw.textbbox((0, 0), text_part, font=font_bwm)
        bwm_x += part_bbox[2] - part_bbox[0]

    # CTA right (orange, 22pt)
    cta_text = "Awaken Your AI Partner"
    cta_bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
    cta_w = cta_bbox[2] - cta_bbox[0]
    cta_h = cta_bbox[3] - cta_bbox[1]
    cta_top_offset = cta_bbox[1]
    cta_x = WIDTH - 40 - cta_w
    cta_y = bot_y + (BOTTOM_BAR_H // 2) - cta_top_offset - cta_h // 2
    draw.text((cta_x, cta_y), cta_text, fill=ORANGE, font=font_cta)

    # Save as JPEG
    canvas.save(final_path, "JPEG", quality=95)
    print(f"  [DONE] {final_path} ({os.path.getsize(final_path)//1024}KB)")
    return final_path


def main():
    print("=" * 60)
    print("CONTENT BATCH: 7 Standalone LinkedIn Banners")
    print("=" * 60)

    results = []

    for i, post in enumerate(POSTS):
        print(f"\n[{i+1}/7] {post['slug']}")

        # Generate FLUX background
        flux_path = generate_flux(post["flux_prompt"], post["slug"])

        # Rate limit: 15s between FLUX calls
        if i < len(POSTS) - 1 and not os.path.exists(os.path.join(RAW_DIR, f"{POSTS[i+1]['slug']}-flux-raw.png")):
            print("  [WAIT] 15s rate limit...")
            time.sleep(15)

        # Create final banner
        final_path = create_banner(flux_path, post["title"], post["slug"])
        results.append((post["slug"], final_path))

    print("\n" + "=" * 60)
    print("ALL 7 BANNERS COMPLETE")
    print("=" * 60)
    for slug, path in results:
        print(f"  {slug}: {path}")


if __name__ == "__main__":
    main()
