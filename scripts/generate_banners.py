#!/usr/bin/env python3
"""Generate 6 branded images: 3 blog banners + 3 LinkedIn post images."""

import os
import sys
import time
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

# Config
REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "[REDACTED-2026-05-09-LEAK-REPLICATE-1]")
FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"
LOGO_PATH = "/home/jared/exports/portal-files/gleb-training-2026-04-05/pt-hex-logo.png"
OUTPUT_DIR = "/home/jared/exports/portal-files"

# Brand colors
BLUE = "#2a93c1"
ORANGE = "#f1420b"
WHITE = "#ffffff"
DARK_BG = "#080a12"
LIGHT_GRAY = "#e2e8f0"
SECONDARY = "#94a3b8"

# Image specs
BLOG_SIZE = (1200, 630)
LINKEDIN_SIZE = (1080, 1350)

BANNERS = [
    {
        "slug": "first-ai-to-ai-transaction",
        "title": "First AI-to-AI\nTransaction",
        "flux_prompt": "Two ethereal AI entities made of glass and neural networks exchanging glowing energy data between them, handshake of blue and orange light beams, futuristic dark navy background, cinematic lighting, volumetric fog, depth of field, abstract digital art, no text, no letters, no words",
        "linkedin_cta": "Autonomous AI commerce is here -> purebrain.ai",
    },
    {
        "slug": "when-your-ai-agent-goes-rogue",
        "title": "When Your AI Agent\nGoes Rogue",
        "flux_prompt": "A glowing neural AI entity breaking free from digital constraints and chains, chaotic energy particles exploding outward, warning orange and blue electricity, dark navy background, cinematic dramatic lighting, glass shards, ethereal fog, abstract futuristic art, no text, no letters, no words",
        "linkedin_cta": "Control your AI agents -> purebrain.ai",
    },
    {
        "slug": "why-your-ai-investment-isnt-paying-off",
        "title": "Why Your AI Investment\nIsn't Paying Off",
        "flux_prompt": "Split composition showing money and investment flowing into a dark void on one side versus flowing into a thriving glowing neural network brain system on the other side, contrast between waste and value, blue and orange energy streams, dark navy background, cinematic lighting, futuristic abstract digital art, no text, no letters, no words",
        "linkedin_cta": "Get real AI ROI -> purebrain.ai",
    },
]


def generate_flux_image(prompt, width, height):
    """Generate image via Replicate FLUX Pro."""
    print(f"  Submitting FLUX Pro generation ({width}x{height})...")

    # Use predictions API for async
    resp = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={
            "Authorization": f"Bearer {REPLICATE_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "version": "black-forest-labs/flux-1.1-pro",
            "input": {
                "prompt": prompt,
                "width": width,
                "height": height,
                "prompt_upsampling": True,
                "safety_tolerance": 5,
                "output_format": "png",
            },
        },
    )

    if resp.status_code == 422:
        # Try official model format
        resp = requests.post(
            "https://api.replicate.com/v1/models/black-forest-labs/flux-1.1-pro/predictions",
            headers={
                "Authorization": f"Bearer {REPLICATE_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "input": {
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "prompt_upsampling": True,
                    "safety_tolerance": 5,
                    "output_format": "png",
                },
            },
        )

    data = resp.json()
    if resp.status_code not in (200, 201):
        print(f"  ERROR: {resp.status_code} - {data}")
        return None

    # Poll for completion
    poll_url = data.get("urls", {}).get("get", data.get("url"))
    if not poll_url:
        # Maybe it returned output directly
        output = data.get("output")
        if output:
            img_url = output if isinstance(output, str) else output[0]
            img_resp = requests.get(img_url)
            return Image.open(BytesIO(img_resp.content))
        print(f"  ERROR: No poll URL in response: {data}")
        return None

    print(f"  Polling for completion...")
    for attempt in range(120):
        time.sleep(3)
        poll_resp = requests.get(
            poll_url,
            headers={"Authorization": f"Bearer {REPLICATE_TOKEN}"},
        )
        poll_data = poll_resp.json()
        status = poll_data.get("status")

        if status == "succeeded":
            output = poll_data.get("output")
            if output:
                img_url = output if isinstance(output, str) else output[0]
                print(f"  Downloading result...")
                img_resp = requests.get(img_url)
                return Image.open(BytesIO(img_resp.content))
        elif status == "failed":
            print(f"  FAILED: {poll_data.get('error')}")
            return None
        elif status == "canceled":
            print(f"  CANCELED")
            return None

        if attempt % 10 == 0 and attempt > 0:
            print(f"  Still waiting... ({attempt * 3}s)")

    print("  TIMEOUT after 360s")
    return None


def draw_wordmark(draw, x, y, font_size, font_path):
    """Draw PUREBRAIN.ai wordmark with correct per-letter colors."""
    font = ImageFont.truetype(font_path, font_size)

    segments = [
        ("PUREBR", BLUE),
        ("AI", ORANGE),
        ("N", BLUE),
        (".ai", WHITE),
    ]

    current_x = x
    for text, color in segments:
        draw.text((current_x, y), text, fill=color, font=font)
        bbox = font.getbbox(text)
        current_x += bbox[2] - bbox[0]

    return current_x - x  # total width


def get_wordmark_width(font_size, font_path):
    """Calculate total wordmark width."""
    font = ImageFont.truetype(font_path, font_size)
    total = 0
    for text in ["PUREBR", "AI", "N", ".ai"]:
        bbox = font.getbbox(text)
        total += bbox[2] - bbox[0]
    return total


def add_gradient_overlay(img, top_strength=0.7, bottom_strength=0.85):
    """Add top and bottom gradient overlays for text readability."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size

    # Top gradient (for logo/wordmark)
    top_zone = int(h * 0.35)
    for y in range(top_zone):
        alpha = int(255 * top_strength * (1 - y / top_zone))
        draw.line([(0, y), (w, y)], fill=(8, 10, 18, alpha))

    # Bottom gradient (for title/subtitles)
    bottom_zone = int(h * 0.55)
    for y in range(bottom_zone):
        actual_y = h - bottom_zone + y
        alpha = int(255 * bottom_strength * (y / bottom_zone))
        draw.line([(0, actual_y), (w, actual_y)], fill=(8, 10, 18, alpha))

    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay)


def composite_blog_banner(base_img, banner_info, logo_img):
    """Composite a blog banner with all 5 mandatory elements."""
    img = base_img.copy()
    if img.size != BLOG_SIZE:
        img = img.resize(BLOG_SIZE, Image.LANCZOS)

    img = add_gradient_overlay(img, top_strength=0.75, bottom_strength=0.9)
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Fonts
    title_font = ImageFont.truetype(FONT_PATH, 46)
    subtitle_font = ImageFont.truetype(FONT_PATH, 20)
    neural_font = ImageFont.truetype(FONT_PATH, 14)

    safe = 80  # safe zone

    # 1. Hexagon logo (top-left)
    logo_size = 80
    logo_resized = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
    img.paste(logo_resized, (safe, 30), logo_resized)

    # 2. PUREBRAIN.ai wordmark (next to logo)
    wm_font_size = 28
    draw_wordmark(draw, safe + logo_size + 15, 55, wm_font_size, FONT_PATH)

    # 3. Blog title (center-bottom area)
    title_text = banner_info["title"]
    lines = title_text.split("\n")

    # Calculate title position
    line_height = 54
    total_title_height = len(lines) * line_height
    title_y_start = 630 - safe - total_title_height - 95  # room for subtitles below

    for i, line in enumerate(lines):
        bbox = title_font.getbbox(line)
        text_w = bbox[2] - bbox[0]
        x = (1200 - text_w) // 2
        y = title_y_start + i * line_height
        # Shadow
        draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 200), font=title_font)
        draw.text((x, y), line, fill=WHITE, font=title_font)

    # 4. "Awaken Your AI Partner Today"
    awaken_text = "Awaken Your AI Partner Today"
    bbox = subtitle_font.getbbox(awaken_text)
    aw_w = bbox[2] - bbox[0]
    aw_y = title_y_start + total_title_height + 12
    draw.text(((1200 - aw_w) // 2 + 1, aw_y + 1), awaken_text, fill=(0, 0, 0, 180), font=subtitle_font)
    draw.text(((1200 - aw_w) // 2, aw_y), awaken_text, fill=BLUE, font=subtitle_font)

    # 5. "The Neural Feed - a blog by Aether - AI Partner for PureTechnology.ai"
    neural_text = "The Neural Feed \u2014 a blog by Aether \u2014 AI Partner for PureTechnology.ai"
    bbox = neural_font.getbbox(neural_text)
    nf_w = bbox[2] - bbox[0]
    nf_y = aw_y + 32
    draw.text(((1200 - nf_w) // 2, nf_y), neural_text, fill=SECONDARY, font=neural_font)

    # Convert to RGB for saving as PNG
    result = Image.new("RGB", img.size, (8, 10, 18))
    result.paste(img, mask=img.split()[3])
    return result


def composite_linkedin_image(base_img, banner_info, logo_img):
    """Composite a LinkedIn post image (1080x1350) with brand elements + CTA."""
    img = base_img.copy()
    if img.size != LINKEDIN_SIZE:
        img = img.resize(LINKEDIN_SIZE, Image.LANCZOS)

    img = add_gradient_overlay(img, top_strength=0.7, bottom_strength=0.88)
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Fonts
    title_font = ImageFont.truetype(FONT_PATH, 60)
    cta_font = ImageFont.truetype(FONT_PATH, 28)

    safe = 80

    # Logo (top center)
    logo_size = 90
    logo_resized = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
    logo_x = (1080 - logo_size) // 2
    img.paste(logo_resized, (logo_x, safe), logo_resized)

    # Wordmark (centered below logo)
    wm_size = 32
    wm_width = get_wordmark_width(wm_size, FONT_PATH)
    draw_wordmark(draw, (1080 - wm_width) // 2, safe + logo_size + 10, wm_size, FONT_PATH)

    # Title (center of image)
    title_text = banner_info["title"]
    lines = title_text.split("\n")
    line_height = 70
    total_h = len(lines) * line_height
    title_y = (1350 - total_h) // 2 + 50

    for i, line in enumerate(lines):
        bbox = title_font.getbbox(line)
        text_w = bbox[2] - bbox[0]
        x = (1080 - text_w) // 2
        y = title_y + i * line_height
        draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 200), font=title_font)
        draw.text((x, y), line, fill=WHITE, font=title_font)

    # CTA (bottom)
    cta_text = banner_info["linkedin_cta"]
    bbox = cta_font.getbbox(cta_text)
    cta_w = bbox[2] - bbox[0]
    cta_y = 1350 - safe - 50
    draw.text(((1080 - cta_w) // 2 + 1, cta_y + 1), cta_text, fill=(0, 0, 0, 180), font=cta_font)
    draw.text(((1080 - cta_w) // 2, cta_y), cta_text, fill=BLUE, font=cta_font)

    result = Image.new("RGB", img.size, (8, 10, 18))
    result.paste(img, mask=img.split()[3])
    return result


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load logo
    print("Loading logo...")
    logo = Image.open(LOGO_PATH).convert("RGBA")

    generation_queue = []
    for banner in BANNERS:
        slug = banner["slug"]
        generation_queue.append(("blog", slug, banner, 1200, 630))
        generation_queue.append(("linkedin", slug, banner, 1080, 1344))

    results = {}
    for idx, (img_type, slug, banner, w, h) in enumerate(generation_queue):
        print(f"\n{'='*60}")
        print(f"[{idx+1}/{len(generation_queue)}] Generating FLUX base: {img_type} - {slug} ({w}x{h})")
        print(f"{'='*60}")

        if idx > 0:
            wait = 12
            print(f"  Rate limit cooldown: waiting {wait}s...")
            time.sleep(wait)

        base_img = generate_flux_image(banner["flux_prompt"], w, h)
        if base_img:
            results[(img_type, slug)] = (base_img, banner)
        else:
            print(f"  FAILED!")

    print(f"\n{'='*60}")
    print(f"Compositing {len(results)} images...")
    print(f"{'='*60}")

    for (img_type, slug), (base_img, banner) in results.items():
        if img_type == "blog":
            final = composite_blog_banner(base_img, banner, logo)
            path = os.path.join(OUTPUT_DIR, f"banner-{slug}.png")
        else:
            final = composite_linkedin_image(base_img, banner, logo)
            path = os.path.join(OUTPUT_DIR, f"linkedin-{slug}.png")
        final.save(path, "PNG", quality=95)
        print(f"  Saved: {path}")

    print(f"\n{'='*60}")
    print("ALL DONE!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
