#!/usr/bin/env python3
"""
Generate 3 URGENT replacement images for social dashboard.
All UNIQUE backgrounds via FLUX Pro + PIL text overlay with Oswald Bold.

Image 1: Blog banner 2400x1260 - "Your Customers Will Tell You Everything"
Image 2: Standalone 2160x2700 - "The Agentic Era Is Here"
Image 3: Standalone 2160x2700 - "The Stat Nobody Is Talking About"
"""

import os
import sys
import time
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO

# Config
REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
if not REPLICATE_TOKEN:
    # Load from .env
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip().startswith("REPLICATE_API_TOKEN"):
                    REPLICATE_TOKEN = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

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

# Parse hex to RGBA tuple
def hex_to_rgba(hex_color, alpha=255):
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


IMAGES = [
    {
        "name": "IMAGE 1: Blog Banner - Customers Tell Everything",
        "slug": "banner-customers-tell-everything-v2",
        "width": 2400,
        "height": 1260,
        "type": "blog-banner",
        "title": "Your Customers Will\nTell You Everything",
        "flux_prompt": (
            "Abstract visualization of transparent data streams flowing between a human silhouette "
            "and a glowing AI entity, streams of personal data represented as luminous particles "
            "forming a bridge of trust, warm orange and cool cerulean blue energy flows, "
            "crystalline data orbs floating in space, deep dark navy background #080a12, "
            "volumetric fog, cinematic rim lighting, depth of field, photorealistic 8k quality, "
            "no text, no letters, no words, no logos, no watermarks"
        ),
    },
    {
        "name": "IMAGE 2: Standalone - Agentic Era",
        "slug": "standalone-agentic-era-v2",
        "width": 2160,
        "height": 2700,
        "type": "standalone",
        "title": "The Agentic Era\nIs Here",
        "subtitle": "The AI inflection point has arrived",
        "flux_prompt": (
            "Vast network of interconnected autonomous AI agent nodes forming a constellation, "
            "each node is a glowing glass sphere with internal neural circuitry, connected by "
            "pulsing energy filaments in cerulean blue and orange, multiple layers of depth "
            "showing hundreds of agents working in parallel, dark space background #080a12, "
            "dramatic scale showing the emergence of a new era, bioluminescent quality, "
            "cinematic wide angle view from below looking up at this massive network, "
            "lens flare, volumetric lighting, photorealistic 8k, "
            "no text, no letters, no words, no logos, no watermarks"
        ),
    },
    {
        "name": "IMAGE 3: Standalone - CEO vs Employee",
        "slug": "standalone-ceo-vs-employee-v2",
        "width": 2160,
        "height": 2700,
        "type": "standalone",
        "title": "The Stat Nobody\nIs Talking About",
        "subtitle": "CEO vs Employee: The AI transformation gap",
        "flux_prompt": (
            "Split composition divided by a glowing vertical energy barrier, left side shows "
            "an elevated luxurious executive boardroom with holographic AI dashboards and "
            "advanced neural interfaces glowing cerulean blue, right side shows a dimmer "
            "traditional office workspace with a single desk and basic computer screen, "
            "stark contrast between high-tech adoption and analog work, "
            "the dividing line pulses with orange energy #f1420b, "
            "dark background #080a12, moody atmospheric lighting, "
            "cinematic split-screen composition, depth of field, volumetric haze, 8k quality, "
            "no text, no letters, no words, no logos, no watermarks"
        ),
    },
]


def get_aspect_ratio_string(width, height):
    """Map target dimensions to closest FLUX aspect_ratio string."""
    ratio = width / height
    # FLUX supported ratios
    options = [
        ("1:1", 1.0),
        ("16:9", 16/9),
        ("9:16", 9/16),
        ("4:5", 4/5),
        ("5:4", 5/4),
        ("3:2", 3/2),
        ("2:3", 2/3),
        ("4:3", 4/3),
        ("3:4", 3/4),
        ("21:9", 21/9),
        ("9:21", 9/21),
    ]
    best = min(options, key=lambda x: abs(x[1] - ratio))
    return best[0]


def generate_flux_image(prompt, target_width, target_height):
    """Generate image via Replicate FLUX Pro using aspect_ratio parameter."""
    aspect_str = get_aspect_ratio_string(target_width, target_height)
    print(f"  Generating with aspect_ratio={aspect_str} (target {target_width}x{target_height})...")

    resp = requests.post(
        "https://api.replicate.com/v1/models/black-forest-labs/flux-1.1-pro/predictions",
        headers={
            "Authorization": f"Bearer {REPLICATE_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "input": {
                "prompt": prompt,
                "aspect_ratio": aspect_str,
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
        output = data.get("output")
        if output:
            img_url = output if isinstance(output, str) else output[0]
            img_resp = requests.get(img_url)
            return Image.open(BytesIO(img_resp.content))
        print(f"  ERROR: No poll URL: {data}")
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
        elif status in ("failed", "canceled"):
            print(f"  {status.upper()}: {poll_data.get('error')}")
            return None

        if attempt % 10 == 0 and attempt > 0:
            print(f"  Still waiting... ({attempt * 3}s)")

    print("  TIMEOUT after 360s")
    return None


def generate_and_upscale(prompt, target_width, target_height):
    """Generate via FLUX then upscale to target dimensions."""
    img = generate_flux_image(prompt, target_width, target_height)
    if img is None:
        return None
    if img.size != (target_width, target_height):
        print(f"  Upscaling from {img.size[0]}x{img.size[1]} to {target_width}x{target_height}...")
        img = img.resize((target_width, target_height), Image.LANCZOS)
        # Slight sharpen after upscale
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.3)
    return img


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
        # Shadow
        draw.text((current_x + 2, y + 2), text, fill=(0, 0, 0, 200), font=font)
        draw.text((current_x, y), text, fill=color, font=font)
        bbox = font.getbbox(text)
        current_x += bbox[2] - bbox[0]
    return current_x - x


def get_wordmark_width(font_size, font_path):
    """Calculate total wordmark width."""
    font = ImageFont.truetype(font_path, font_size)
    total = 0
    for text in ["PUREBR", "AI", "N", ".ai"]:
        bbox = font.getbbox(text)
        total += bbox[2] - bbox[0]
    return total


def draw_text_with_glow(draw, position, text, font, fill_color, glow_color=(0, 0, 0), glow_radius=4):
    """Draw text with multi-layer shadow/glow for readability."""
    x, y = position
    # Multi-layer glow
    for offset in range(glow_radius, 0, -1):
        alpha = int(180 * (offset / glow_radius))
        glow = (*hex_to_rgba(glow_color)[:3], alpha) if isinstance(glow_color, str) else (*glow_color[:3], alpha)
        for dx in range(-offset, offset + 1):
            for dy in range(-offset, offset + 1):
                if dx * dx + dy * dy <= offset * offset:
                    draw.text((x + dx, y + dy), text, fill=glow, font=font)
    # Main text
    draw.text((x, y), text, fill=fill_color, font=font)


def add_gradient_overlay(img, top_strength=0.7, bottom_strength=0.85):
    """Add top and bottom gradient overlays for text readability."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size

    # Top gradient (for logo/wordmark)
    top_zone = int(h * 0.30)
    for y in range(top_zone):
        alpha = int(255 * top_strength * (1 - y / top_zone))
        draw.line([(0, y), (w, y)], fill=(8, 10, 18, alpha))

    # Bottom gradient (for title/subtitles)
    bottom_zone = int(h * 0.50)
    for y in range(bottom_zone):
        actual_y = h - bottom_zone + y
        alpha = int(255 * bottom_strength * (y / bottom_zone))
        draw.line([(0, actual_y), (w, actual_y)], fill=(8, 10, 18, alpha))

    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay)


def composite_blog_banner(base_img, image_info, logo_img):
    """Composite blog banner with 5 mandatory elements at 2400x1260 (2K)."""
    W, H = image_info["width"], image_info["height"]
    img = base_img.copy()
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)

    img = add_gradient_overlay(img, top_strength=0.80, bottom_strength=0.92)
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Scale factor (2x from 1200x630 base)
    s = 2

    # Fonts (scaled for 2K)
    title_font = ImageFont.truetype(FONT_PATH, 92)
    subtitle_font = ImageFont.truetype(FONT_PATH, 40)
    neural_font = ImageFont.truetype(FONT_PATH, 28)

    safe = 160  # safe zone at 2K

    # 1. Hexagon logo (top-left)
    logo_size = 160
    logo_resized = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
    img.paste(logo_resized, (safe, 60), logo_resized)

    # 2. PUREBRAIN.ai wordmark (next to logo)
    wm_font_size = 56
    draw_wordmark(draw, safe + logo_size + 30, 110, wm_font_size, FONT_PATH)

    # 3. Blog title (center-bottom area)
    title_text = image_info["title"]
    lines = title_text.split("\n")
    line_height = 108
    total_title_height = len(lines) * line_height
    title_y_start = H - safe - total_title_height - 190

    for i, line in enumerate(lines):
        bbox = title_font.getbbox(line)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w) // 2
        y = title_y_start + i * line_height
        draw_text_with_glow(draw, (x, y), line, title_font, WHITE, glow_radius=5)

    # 4. "Awaken Your AI Partner Today"
    awaken_text = "Awaken Your AI Partner Today"
    bbox = subtitle_font.getbbox(awaken_text)
    aw_w = bbox[2] - bbox[0]
    aw_y = title_y_start + total_title_height + 24
    draw_text_with_glow(draw, ((W - aw_w) // 2, aw_y), awaken_text, subtitle_font, BLUE, glow_radius=3)

    # 5. "The Neural Feed"
    neural_text = "The Neural Feed"
    bbox = neural_font.getbbox(neural_text)
    nf_w = bbox[2] - bbox[0]
    nf_y = aw_y + 64
    draw_text_with_glow(draw, ((W - nf_w) // 2, nf_y), neural_text, neural_font, SECONDARY, glow_radius=2)

    # Convert to RGB for saving
    result = Image.new("RGB", img.size, (8, 10, 18))
    result.paste(img, mask=img.split()[3])
    return result


def composite_standalone(base_img, image_info, logo_img):
    """Composite standalone LinkedIn image at 2160x2700 (2K)."""
    W, H = image_info["width"], image_info["height"]
    img = base_img.copy()
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)

    img = add_gradient_overlay(img, top_strength=0.75, bottom_strength=0.90)
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Fonts (scaled for 2K standalone)
    title_font = ImageFont.truetype(FONT_PATH, 120)
    subtitle_font = ImageFont.truetype(FONT_PATH, 48)

    safe = 160

    # Logo (top center)
    logo_size = 180
    logo_resized = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
    logo_x = (W - logo_size) // 2
    img.paste(logo_resized, (logo_x, safe), logo_resized)

    # Wordmark (centered below logo)
    wm_size = 64
    wm_width = get_wordmark_width(wm_size, FONT_PATH)
    draw_wordmark(draw, (W - wm_width) // 2, safe + logo_size + 20, wm_size, FONT_PATH)

    # Title (center of image)
    title_text = image_info["title"]
    lines = title_text.split("\n")
    line_height = 140
    total_h = len(lines) * line_height
    title_y = (H - total_h) // 2 + 80

    for i, line in enumerate(lines):
        bbox = title_font.getbbox(line)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w) // 2
        y = title_y + i * line_height
        draw_text_with_glow(draw, (x, y), line, title_font, WHITE, glow_radius=6)

    # Subtitle (below title if present)
    if "subtitle" in image_info:
        sub_text = image_info["subtitle"]
        bbox = subtitle_font.getbbox(sub_text)
        sub_w = bbox[2] - bbox[0]
        sub_y = title_y + total_h + 40
        draw_text_with_glow(draw, ((W - sub_w) // 2, sub_y), sub_text, subtitle_font, BLUE, glow_radius=3)

    # CTA at bottom
    cta_font = ImageFont.truetype(FONT_PATH, 42)
    cta_text = "purebrain.ai"
    bbox = cta_font.getbbox(cta_text)
    cta_w = bbox[2] - bbox[0]
    cta_y = H - safe - 60
    draw_text_with_glow(draw, ((W - cta_w) // 2, cta_y), cta_text, cta_font, ORANGE, glow_radius=3)

    # Convert to RGB
    result = Image.new("RGB", img.size, (8, 10, 18))
    result.paste(img, mask=img.split()[3])
    return result


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading logo...")
    logo = Image.open(LOGO_PATH).convert("RGBA")

    for idx, image_info in enumerate(IMAGES):
        print(f"\n{'='*70}")
        print(f"[{idx+1}/{len(IMAGES)}] {image_info['name']}")
        print(f"{'='*70}")

        if idx > 0:
            print("  Rate limit cooldown: 10s...")
            time.sleep(10)

        # Generate FLUX background + upscale to target
        base_img = generate_and_upscale(
            image_info["flux_prompt"],
            image_info["width"],
            image_info["height"],
        )

        if not base_img:
            print(f"  FAILED to generate background! Skipping.")
            continue

        # Composite with text overlay
        if image_info["type"] == "blog-banner":
            final = composite_blog_banner(base_img, image_info, logo)
        else:
            final = composite_standalone(base_img, image_info, logo)

        # Save
        output_path = os.path.join(OUTPUT_DIR, f"{image_info['slug']}.png")
        final.save(output_path, "PNG", quality=95)
        file_size = os.path.getsize(output_path)
        print(f"  SAVED: {output_path} ({file_size / 1024 / 1024:.1f} MB)")
        print(f"  Dimensions: {final.size[0]}x{final.size[1]}")

    print(f"\n{'='*70}")
    print("ALL 3 IMAGES COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
