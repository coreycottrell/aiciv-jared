#!/usr/bin/env python3
"""
Generate 23 standalone LinkedIn banners (1080x1350) for social.purebrain.ai content.
v4.2 format: top bar + blue line + FLUX bg with title + blue line + bottom bar.
"""

import os
import sys
import time
import urllib.request
import replicate
from PIL import Image, ImageDraw, ImageFont
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
RAW_DIR = "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-apr30/flux-raw"
FINAL_DIR = "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-apr30"

os.environ["REPLICATE_API_TOKEN"] = "r8_HU0LIcWclhNkx01Qod0rms8bFeqovK03yBDLr"

FLUX_PREFIX = "Professional dark moody tech aesthetic, cinematic lighting, 8k quality, no text no words no letters, "

# --- 23 Standalones ---
POSTS = [
    {
        "slug": "ai-forgets-paying-twice",
        "title": "AI FORGETS YOU =\nPAYING FOR THE SAME\nINTRO TWICE",
        "flux_prompt": FLUX_PREFIX + "Fractured memory shards, coins falling through digital gaps, dark moody tech aesthetic"
    },
    {
        "slug": "junior-marketer-vs-ai",
        "title": "JUNIOR MARKETER VS\nAI PARTNER:\nTHE REAL COST",
        "flux_prompt": FLUX_PREFIX + "Split comparison desk with papers vs sleek AI brain, corporate tech"
    },
    {
        "slug": "context-problem-not-ai",
        "title": "YOU HAVE A\nCONTEXT PROBLEM\nNOT AN AI PROBLEM",
        "flux_prompt": FLUX_PREFIX + "Scattered puzzle pieces reforming into clear neural pattern"
    },
    {
        "slug": "monday-morning-ai-briefing",
        "title": "YOUR MONDAY MORNING\nAI BRIEFING",
        "flux_prompt": FLUX_PREFIX + "Morning sunrise through glass with data dashboard overlay"
    },
    {
        "slug": "better-context-not-model",
        "title": "YOUR AI DOESN'T NEED\nA BETTER MODEL",
        "flux_prompt": FLUX_PREFIX + "Fuel canister pouring data into dim engine"
    },
    {
        "slug": "day1-compound-effect",
        "title": "DAY 1 WITH AI:\nTHE COMPOUND EFFECT\nBEGINS",
        "flux_prompt": FLUX_PREFIX + "Single seed growing into sprawling neural tree"
    },
    {
        "slug": "gmail-newsletter-spam-fix",
        "title": "HOW TO FIX GMAIL\nNEWSLETTER SPAM FILTER",
        "flux_prompt": FLUX_PREFIX + "Email envelope breaking free from spam cage"
    },
    {
        "slug": "ai-compound-effect-article",
        "title": "THE AI COMPOUND EFFECT:\nWHY DAY 1\nMATTERS MOST",
        "flux_prompt": FLUX_PREFIX + "Exponential growth curve in glowing blue particles"
    },
    {
        "slug": "10k-content-engine-149",
        "title": "$10K CONTENT ENGINE\nFOR $149/MONTH",
        "flux_prompt": FLUX_PREFIX + "Massive glowing factory shrunk into tiny price tag"
    },
    {
        "slug": "ai-works-247am",
        "title": "YOUR AI WORKS\nAT 2:47AM\nWHILE YOU SLEEP",
        "flux_prompt": FLUX_PREFIX + "Clock showing 2:47 with glowing AI brain active in darkness"
    },
    {
        "slug": "ai-doesnt-sleep-3am",
        "title": "AI DOESN'T SLEEP.\nWHAT DOES IT DO\nAT 3AM?",
        "flux_prompt": FLUX_PREFIX + "Dark room glowing screen time display 3:00AM"
    },
    {
        "slug": "name-your-ai-before-pay",
        "title": "NAME YOUR AI\nBEFORE YOU PAY\nFOR IT",
        "flux_prompt": FLUX_PREFIX + "Holographic name badge floating above hand"
    },
    {
        "slug": "ai-forgot-everything",
        "title": "YOUR AI FORGOT\nEVERYTHING.\nTHE COST OF AMNESIA.",
        "flux_prompt": FLUX_PREFIX + "Shattered memory glass with data leaking away"
    },
    {
        "slug": "cost-of-ai-amnesia-74k",
        "title": "THE COST OF\nAI AMNESIA:\n$74,600 PER YEAR",
        "flux_prompt": FLUX_PREFIX + "Calculator with glowing red total data evaporating"
    },
    {
        "slug": "36-businesses-named-ai",
        "title": "36 BUSINESSES\nNAMED THEIR AI",
        "flux_prompt": FLUX_PREFIX + "Multiple holographic name tags floating in space"
    },
    {
        "slug": "skeptic-to-coceo",
        "title": "FROM 'I DON'T TRUST AI'\nTO CO-CEO",
        "flux_prompt": FLUX_PREFIX + "Journey path from dark skepticism to bright partnership"
    },
    {
        "slug": "journey-to-coceo",
        "title": "THE JOURNEY TO\nCO-CEO PARTNERSHIP",
        "flux_prompt": FLUX_PREFIX + "Two entities merging into unified bright form"
    },
    {
        "slug": "skeptics-timeline-with-ai",
        "title": "A SKEPTIC'S TIMELINE\nWITH AI",
        "flux_prompt": FLUX_PREFIX + "Timeline bar progressing from dim to radiant"
    },
    {
        "slug": "blog-written-sunday",
        "title": "BLOG WRITTEN ON SUNDAY.\nAI CONTENT ENGINE\nAT WORK.",
        "flux_prompt": FLUX_PREFIX + "Calendar page with gears and content flowing out"
    },
    {
        "slug": "20000-words-sunday-30min",
        "title": "20,000 WORDS\nEVERY SUNDAY\nIN 30 MINUTES",
        "flux_prompt": FLUX_PREFIX + "Massive text waterfall compressed into tiny clock"
    },
    {
        "slug": "last-post-content-automation",
        "title": "THE LAST POST I EVER\nWROTE BY HAND",
        "flux_prompt": FLUX_PREFIX + "Pen dissolving into digital particles"
    },
    {
        "slug": "small-agencies-ai-partners",
        "title": "SMALL AGENCIES +\nAI PARTNERS:\nTHE NEW MODEL",
        "flux_prompt": FLUX_PREFIX + "Small building with disproportionately large neural glow"
    },
    {
        "slug": "small-agencies-build-own-ai",
        "title": "SMALL AGENCIES SHOULD\nBUILD THEIR OWN AI",
        "flux_prompt": FLUX_PREFIX + "Blueprint of AI system being constructed"
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

    # Center wordmark vertically
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

    # Draw title lines with stroke
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

    # Bottom wordmark left
    bwm_parts = [
        ("PUREBR", BLUE),
        ("AI", ORANGE),
        ("N", BLUE),
        (".AI", WHITE),
    ]
    bwm_x = 40
    bwm_bbox = draw.textbbox((0, 0), "PUREBRAIN.AI", font=font_bottom_wm)
    bwm_h = bwm_bbox[3] - bwm_bbox[1]
    bwm_top_offset = bwm_bbox[1]
    bwm_y = bot_y + (BOTTOM_BAR_H // 2) - bwm_top_offset - bwm_h // 2
    for text_part, color in bwm_parts:
        draw.text((bwm_x, bwm_y), text_part, fill=color, font=font_bottom_wm)
        part_bbox = draw.textbbox((0, 0), text_part, font=font_bottom_wm)
        bwm_x += part_bbox[2] - part_bbox[0]

    # CTA right
    cta_text = "Awaken Your AI Partner"
    cta_bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
    cta_w = cta_bbox[2] - cta_bbox[0]
    cta_h = cta_bbox[3] - cta_bbox[1]
    cta_top_offset = cta_bbox[1]
    cta_x = WIDTH - 40 - cta_w
    cta_y = bot_y + (BOTTOM_BAR_H // 2) - cta_top_offset - cta_h // 2
    draw.text((cta_x, cta_y), cta_text, fill=ORANGE, font=font_cta)

    # Save as JPEG quality 92
    canvas.save(final_path, "JPEG", quality=92)
    print(f"  [DONE] {final_path} ({os.path.getsize(final_path)//1024}KB)")
    return final_path


def main():
    print("=" * 60)
    print("CONTENT BATCH APR30: 23 Standalone LinkedIn Banners")
    print("=" * 60)

    results = []
    success = 0
    failed = 0

    for i, post in enumerate(POSTS):
        print(f"\n[{i+1}/23] {post['slug']}")
        try:
            # Generate FLUX background
            flux_path = generate_flux(post["flux_prompt"], post["slug"])

            # Rate limit: 15s between FLUX calls
            if i < len(POSTS) - 1:
                next_raw = os.path.join(RAW_DIR, f"{POSTS[i+1]['slug']}-flux-raw.png")
                if not os.path.exists(next_raw):
                    print("  [WAIT] 15s rate limit...")
                    time.sleep(15)

            # Create final banner
            final_path = create_banner(flux_path, post["title"], post["slug"])
            results.append((post["slug"], final_path))
            success += 1
        except Exception as e:
            print(f"  [ERROR] {post['slug']}: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"COMPLETE: {success} succeeded, {failed} failed")
    print("=" * 60)
    for slug, path in results:
        print(f"  {slug}: {path}")


if __name__ == "__main__":
    main()
