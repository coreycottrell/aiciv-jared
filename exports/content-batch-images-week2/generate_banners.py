#!/usr/bin/env python3
"""
Generate 14 standalone LinkedIn banners (1080x1350) for Apr 28 - May 4 content batch.
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
RAW_DIR = "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-week2/flux-raw"
FINAL_DIR = "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-week2"

os.environ["REPLICATE_API_TOKEN"] = "r8_HU0LIcWclhNkx01Qod0rms8bFeqovK03yBDLr"

# --- 14 Standalones ---
POSTS = [
    # APR 28 S1
    {
        "slug": "purebrain-vs-va-math",
        "title": "PureBrain vs Hiring a VA:\nThe Math Nobody Wants to Do",
        "flux_prompt": "Abstract dark scene, glowing holographic calculator dissolving into blue digital particles, golden coins scattered on one side and a sleek AI brain on the other, dark moody background with blue and orange accent rim lighting, volumetric fog, cinematic depth of field, bokeh orbs, film grain, 8k photorealistic, no text"
    },
    # APR 28 S2
    {
        "slug": "ai-remembers-client-birthday",
        "title": "What Happens When Your AI\nRemembers Your Client's Birthday",
        "flux_prompt": "Abstract dark scene, glowing blue neural memory network with warm orange light nodes representing human moments, ethereal birthday candle flame reflected in glass surface, dark moody atmosphere, soft particle effects, volumetric light beams, shallow depth of field, bokeh, film grain, 8k photorealistic, no text"
    },
    # APR 29 S1
    {
        "slug": "stopped-writing-linkedin-posts",
        "title": "I Stopped Writing My Own\nLinkedIn Posts 3 Months Ago",
        "flux_prompt": "Abstract dark scene, a sleek laptop with glowing blue holographic text streaming upward from screen, pen lying abandoned beside it, orange accent lighting on the edges, dark moody background, volumetric rays, cinematic shallow depth of field, glass reflections, bokeh, film grain, 8k photorealistic, no text"
    },
    # APR 29 S2
    {
        "slug": "32-ai-agents-not-tech-company",
        "title": "The Company That Runs\n32 AI Agents Isn't a Tech Company",
        "flux_prompt": "Abstract dark scene, 32 small glowing blue orbs orbiting a central larger orb in organized patterns, orange energy connections between them, dark moody space background, volumetric fog, glass morphism reflections, cinematic lighting, shallow depth of field, bokeh, film grain, 8k photorealistic, no text"
    },
    # APR 30 S1
    {
        "slug": "ai-doesnt-need-better-model",
        "title": "Your AI Doesn't Need\na Better Model",
        "flux_prompt": "Abstract dark scene, a glowing blue fuel canister pouring luminous data streams into a dim engine shape, the fuel glows brighter than the engine, orange accent sparks, dark moody background, volumetric light, cinematic composition, shallow depth of field, bokeh orbs, film grain, 8k photorealistic, no text"
    },
    # APR 30 S2
    {
        "slug": "day1-skepticism-month6-indispensable",
        "title": "Day 1: Skepticism.\nMonth 6: Can't Imagine Going Back.",
        "flux_prompt": "Abstract dark split composition, left side cold and dim with a single faint blue spark, right side warm and vibrant with a full glowing neural constellation in blue and orange, transition gradient between them, dark moody atmosphere, volumetric lighting, glass reflections, shallow depth of field, bokeh, film grain, 8k photorealistic, no text"
    },
    # MAY 1 S1
    {
        "slug": "ai-texts-midnight-security",
        "title": "The AI That Texts Me\nat Midnight When Something's Wrong",
        "flux_prompt": "Abstract dark scene, a glowing smartphone screen in darkness casting blue light on surrounding fog, red-orange alert notification pulse emanating from the screen, dark moody night atmosphere, volumetric light rays from phone, cinematic shallow depth of field, bokeh, film grain, 8k photorealistic, no text"
    },
    # MAY 1 S2
    {
        "slug": "most-ai-glorified-autocomplete",
        "title": "Most AI Tools Are\nGlorified Autocomplete",
        "flux_prompt": "Abstract dark scene, a simple blinking text cursor on left side fading and dim, contrasted with a complex glowing blue neural brain on right side radiating intelligence, orange accent highlights, dark moody background, volumetric fog, cinematic composition, shallow depth of field, bokeh, film grain, 8k photorealistic, no text"
    },
    # MAY 2 S1
    {
        "slug": "ai-caught-billing-error",
        "title": "My AI Partner Caught a\nBilling Error I Missed for 3 Months",
        "flux_prompt": "Abstract dark scene, glowing invoice document with a bright orange magnifying glass highlighting a discrepancy, blue data streams flowing around it, dark moody background, dramatic spotlight lighting, volumetric fog, shallow depth of field, bokeh, film grain, 8k photorealistic, no text"
    },
    # MAY 2 S2
    {
        "slug": "stop-evaluating-ai-by-capabilities",
        "title": "Stop Evaluating AI\nBy What It Can Do",
        "flux_prompt": "Abstract dark scene, a glowing blue brain with deep root-like memory tendrils extending downward versus a shallow flashy surface-level sparkle above, orange accent lighting showing the depth versus surface contrast, dark moody background, volumetric rays, shallow depth of field, bokeh, film grain, 8k photorealistic, no text"
    },
    # MAY 3 S1
    {
        "slug": "next-hire-no-resume",
        "title": "Your Next Hire Doesn't\nNeed a Resume",
        "flux_prompt": "Abstract dark scene, a traditional paper resume dissolving into blue digital particles transforming into a glowing AI presence, orange accent lighting on the transformation edge, dark moody background, volumetric light beams, glass morphism, shallow depth of field, bokeh, film grain, 8k photorealistic, no text"
    },
    # MAY 3 S2
    {
        "slug": "36-businesses-named-their-ai",
        "title": "36 Businesses Named Their AI.\nHere's What They Named Them.",
        "flux_prompt": "Abstract dark scene, multiple glowing holographic name tags floating in dark space at different depths, each with a soft unique color tint but predominantly blue, warm orange glow behind the cluster, dark moody atmosphere, glass morphism reflections, volumetric fog, shallow depth of field, bokeh, film grain, 8k photorealistic, no text"
    },
    # MAY 4 S1
    {
        "slug": "company-runs-32-agents",
        "title": "The Company That Runs\n32 AI Agents",
        "flux_prompt": "Abstract dark scene, a network of 32 glowing blue nodes arranged in a hexagonal grid pattern, pulsing energy connections between them, a central conductor node glowing brighter with orange rim, dark moody space background, volumetric fog, cinematic lighting, shallow depth of field, bokeh, film grain, 8k photorealistic, no text"
    },
    # MAY 4 S2
    {
        "slug": "next-hire-naming-ceremony",
        "title": "Your Next Hire Doesn't Need\na Resume. It Needs a Name.",
        "flux_prompt": "Abstract dark scene, a glowing blue holographic badge with an empty name field floating above an outstretched hand silhouette, warm orange light emanating from behind the badge, dark moody atmosphere, volumetric light rays, glass morphism reflections, shallow depth of field, bokeh, film grain, 8k photorealistic, no text"
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

    # Draw wordmark with brand colors
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
        center = (grad_top + grad_bot) // 2
        dist = abs(y - center) / ((grad_bot - grad_top) / 2)
        alpha = int(180 * (1 - dist * dist))
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
    print("CONTENT BATCH WEEK 2: 14 Standalone LinkedIn Banners")
    print("=" * 60)

    results = []

    for i, post in enumerate(POSTS):
        print(f"\n[{i+1}/14] {post['slug']}")

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
    print("ALL 14 BANNERS COMPLETE")
    print("=" * 60)
    for slug, path in results:
        print(f"  {slug}: {path}")


if __name__ == "__main__":
    main()
