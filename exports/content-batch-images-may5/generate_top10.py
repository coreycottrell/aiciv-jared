#!/usr/bin/env python3
"""
Top 10 LinkedIn Standalone Image Generator (May 5, 2026)
=========================================================

Generates branded standalone LinkedIn images (2160x2700, 2K quality) for 10 posts
that currently have no images in social.purebrain.ai.

Pipeline: FLUX Pro 1.1 (Replicate) -> PIL composite -> Oswald Bold typography

Format: v4 Standalone (locked)
- Top bar: hex icon + PUREBRAIN.AI wordmark + title
- FLUX image area with title overlay (stroke text)
- Bottom bar: PUREBRAIN.AI left + orange CTA right

Author: 3d-design-specialist
Date: 2026-05-02
"""

import json
import os
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path("/home/jared/projects/AI-CIV/aether")
load_dotenv(PROJECT_ROOT / ".env")

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    print("FATAL: REPLICATE_API_TOKEN not set", file=sys.stderr)
    sys.exit(1)

# Paths
BATCH_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/content-batch-images-may5")
RAW_DIR = BATCH_DIR / "raw"
FINAL_DIR = BATCH_DIR / "final"
RAW_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)

HEX_ICON = PROJECT_ROOT / "assets" / "pt-hex-icon-official.png"
OSWALD_BOLD = "/home/jared/.fonts/Oswald-Bold.ttf"

# Brand colors
BLUE = "#2a93c1"
ORANGE = "#f1420b"
WHITE = "#ffffff"
DARK = "#080a12"

# ---------------------------------------------------------------------------
# 10 post briefs
# ---------------------------------------------------------------------------

POSTS = [
    {
        "key": "01-hardest-part",
        "title": "The Hardest Part of AI\nIsn't the Technology",
        "title_overlay": "The Hardest Part\nof AI Isn't\nthe Technology",
        "cta": "Start Building",
        "prompt": "Cinematic close-up of two hands reaching toward each other across a dark void, one human hand and one made of translucent cerulean blue digital particles at hex 2a93c1. The gap between them glows with warm orange light at hex f1420b. Shallow depth of field, dust motes, dark moody background at hex 080a12, sci-fi editorial photography. No text, no logos, no watermarks, negative space dominant.",
    },
    {
        "key": "02-tired-of-demos",
        "title": "I'm Tired of AI Demos.\nShow Me Production.",
        "title_overlay": "Show Me\nProduction.",
        "cta": "See Production AI",
        "prompt": "Cinematic split composition: left side shows a flashy holographic demo screen with shallow meaningless UI, dissolving into static and fading. Right side shows a real industrial server rack environment glowing steadily in cerulean blue at hex 2a93c1, solid and operational. Dark background at hex 080a12, dramatic side lighting, orange accent light at hex f1420b on the production side. Sci-fi editorial, photorealistic. No text, no logos, no watermarks.",
    },
    {
        "key": "03-ai-got-wrong",
        "title": "3 Things My AI\nGot Wrong This Week",
        "title_overlay": "3 Things My AI\nGot Wrong\nThis Week",
        "cta": "Real AI, Real Talk",
        "prompt": "Cinematic product photograph of three translucent glass cubes floating in dark space, each containing a different glowing error symbol: a cracked circuit, a tangled thread, a dimming spark. Cerulean blue at hex 2a93c1 illumination from within, warm orange at hex f1420b highlights on the cracks. Dark void background at hex 080a12, shallow depth of field, dust particles. No text, no logos, no watermarks, negative space dominant.",
    },
    {
        "key": "04-shipped-4-features",
        "title": "My AI Shipped 4 Features\nThis Week. Receipts Inside.",
        "title_overlay": "4 Features\nShipped.\nReceipts Inside.",
        "cta": "See The Receipts",
        "prompt": "Cinematic overhead view of four glowing receipt documents arranged in a grid pattern, each with a cerulean blue checkmark at hex 2a93c1. Faint timeline connecting them in sequence. Orange at hex f1420b glow on the edges of the most recent receipt. Dark background at hex 080a12, ethereal mist, sci-fi minimalism. No text, no logos, no watermarks.",
    },
    {
        "key": "05-32-specialist-agents",
        "title": "I Have 32 Specialist AI\nAgents Working Under Me",
        "title_overlay": "32 Specialist\nAI Agents",
        "cta": "Meet The Team",
        "prompt": "Cinematic aerial view of a vast dark circular command center with 32 glowing nodes arranged in concentric rings, each node a different size representing different specializations. Central conductor node larger and brighter in cerulean blue at hex 2a93c1. Orange at hex f1420b connection threads pulse between active nodes. Dark void at hex 080a12, holographic sci-fi aesthetic, extreme depth of field. No text, no logos, no watermarks.",
    },
    {
        "key": "06-40-percent-die",
        "title": "40% of AI Agent Projects\nDie in Pilot",
        "title_overlay": "40% Die\nin Pilot",
        "cta": "Beat The Odds",
        "prompt": "Cinematic graveyard scene of dimmed holographic screens arranged like tombstones in fog, 40 percent faded and dark, 60 percent still glowing faintly. One screen in the foreground breaks through with bright cerulean blue at hex 2a93c1 light, transitioning from prototype to production. Orange at hex f1420b warning lights on the failed screens. Dark atmospheric background at hex 080a12, ethereal fog, haunting sci-fi aesthetic. No text, no logos, no watermarks.",
    },
    {
        "key": "07-delegation-test",
        "title": "The 3-Question\nDelegation Test",
        "title_overlay": "The 3-Question\nDelegation Test",
        "cta": "Test Your Delegation",
        "prompt": "Cinematic macro photograph of three glowing question marks suspended in dark space, made of translucent cerulean blue glass at hex 2a93c1. Each progressively larger. Connected by thin orange at hex f1420b laser beams forming a decision tree. Dark void background at hex 080a12, extreme bokeh, dust motes catching light. No text, no logos, no watermarks.",
    },
    {
        "key": "08-sunday-math",
        "title": "Sunday Math,\nMonday Clarity",
        "title_overlay": "Sunday Math,\nMonday Clarity",
        "cta": "Plan Your Week",
        "prompt": "Cinematic still life of a glowing futuristic calculator interface floating above a calm dark surface, reflecting cerulean blue at hex 2a93c1 digits. One total number highlighted in orange at hex f1420b. Peaceful Sunday morning atmosphere with soft volumetric light rays. Dark background at hex 080a12, sci-fi minimalism, shallow depth of field. No text, no logos, no watermarks.",
    },
    {
        "key": "09-see-the-work",
        "title": "If You Can't See the Work,\nYou Don't Trust the Worker",
        "title_overlay": "See the Work.\nTrust the Worker.",
        "cta": "See The Work",
        "prompt": "Cinematic shot of a transparent glass office wall revealing a complex AI workflow visualization behind it in cerulean blue at hex 2a93c1 light. A silhouette of a person stands on the other side looking through. Orange at hex f1420b highlights mark completed task nodes. Dark moody atmosphere at hex 080a12, dramatic rim lighting, sci-fi corporate aesthetic. No text, no logos, no watermarks.",
    },
    {
        "key": "10-stop-guessing-cost",
        "title": "Stop Guessing What Your\nAI Stack Is Actually Costing",
        "title_overlay": "Know Your\nNumbers.",
        "cta": "Know Your Numbers",
        "prompt": "Cinematic close-up of a futuristic cost dashboard hologram floating in dark space, showing bar charts and spend curves in cerulean blue at hex 2a93c1. One metric highlighted in bright orange at hex f1420b with an upward trend. Dark background at hex 080a12, clean data visualization aesthetic, bokeh lights in background, sci-fi editorial. No text, no logos, no watermarks.",
    },
]


# ---------------------------------------------------------------------------
# FLUX generation (reuse proven pattern)
# ---------------------------------------------------------------------------

def flux_generate(prompt: str, output_path: Path, max_retries: int = 2) -> bool:
    """Generate a 4:5 portrait image via FLUX 1.1 Pro on Replicate."""
    if output_path.exists() and output_path.stat().st_size > 10000:
        print(f"  [SKIP] Raw exists: {output_path.name}")
        return True

    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
        "Prefer": "wait",
    }

    payload = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": "4:5",
            "output_format": "png",
            "output_quality": 100,
            "safety_tolerance": 5,
            "prompt_upsampling": True,
        }
    }

    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(
                "https://api.replicate.com/v1/models/black-forest-labs/flux-1.1-pro/predictions",
                headers=headers,
                json=payload,
                timeout=300,
            )
            if resp.status_code not in (200, 201):
                print(f"  [ERR] HTTP {resp.status_code}: {resp.text[:200]}")
                if attempt < max_retries:
                    time.sleep(5 * (attempt + 1))
                    continue
                return False

            result = resp.json()

            # Async polling if needed
            if result.get("status") in ("starting", "processing"):
                poll_url = result["urls"]["get"]
                for i in range(60):
                    time.sleep(5)
                    poll = requests.get(
                        poll_url,
                        headers={"Authorization": f"Bearer {REPLICATE_API_TOKEN}"},
                        timeout=30,
                    )
                    pdata = poll.json()
                    status = pdata.get("status")
                    if status == "succeeded":
                        result = pdata
                        break
                    if status == "failed":
                        print(f"  [ERR] Generation failed: {pdata.get('error')}")
                        if attempt < max_retries:
                            break
                        return False
                else:
                    print(f"  [ERR] Timed out waiting for generation")
                    if attempt < max_retries:
                        continue
                    return False

            output = result.get("output")
            image_url = output[0] if isinstance(output, list) else output
            if not image_url:
                print(f"  [ERR] No output URL in response")
                if attempt < max_retries:
                    continue
                return False

            img_resp = requests.get(image_url, timeout=120)
            img_resp.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(img_resp.content)
            print(f"  [OK] Raw saved: {output_path.name} ({len(img_resp.content)//1024} KB)")
            return True

        except Exception as e:
            print(f"  [EXC] Attempt {attempt+1}: {e}")
            if attempt < max_retries:
                time.sleep(5 * (attempt + 1))
                continue
            return False

    return False


# ---------------------------------------------------------------------------
# PIL composition: v4 Standalone (2160x2700)
# ---------------------------------------------------------------------------

def draw_text_with_stroke(draw, pos, text, font, fill, stroke_fill, stroke_width):
    """Draw text with a solid stroke/outline for readability over images."""
    x, y = pos
    # Draw stroke
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx * dx + dy * dy <= stroke_width * stroke_width:
                draw.text((x + dx, y + dy), text, fill=stroke_fill, font=font)
    # Draw main text
    draw.text((x, y), text, fill=fill, font=font)


def draw_brand_wordmark(draw, x, y, font):
    """Draw PUREBRAIN.AI in brand colors at (x, y). Returns total width."""
    parts = [("PUREBR", BLUE), ("AI", ORANGE), ("N", BLUE), (".AI", WHITE)]
    cx = x
    for text, color in parts:
        draw.text((cx, y), text, fill=color, font=font)
        cx += draw.textlength(text, font=font)
    return cx - x


def compose_standalone(raw_path: Path, title: str, title_overlay: str, cta: str, output_path: Path) -> bool:
    """
    v4 standalone composition at 2K (2160x2700).

    Layout:
    - Top bar (280px): hex icon + PUREBRAIN.AI wordmark + post title
    - Blue accent line (4px)
    - FLUX image area with centered title overlay (stroke text)
    - Blue accent line (4px)
    - Bottom bar (180px): PUREBRAIN.AI left + orange CTA right
    """
    from PIL import Image, ImageDraw, ImageFont

    W, H = 2160, 2700
    TOP_BAR_H = 280
    BOT_BAR_H = 180
    ACCENT_H = 4

    # FLUX area dimensions
    img_area_top = TOP_BAR_H
    img_area_bot = H - BOT_BAR_H
    img_h = img_area_bot - img_area_top

    # Load FLUX raw, crop-fit into image area
    raw = Image.open(raw_path).convert("RGBA")
    scale = max(W / raw.width, img_h / raw.height)
    raw = raw.resize((int(raw.width * scale), int(raw.height * scale)), Image.LANCZOS)
    left = (raw.width - W) // 2
    top = (raw.height - img_h) // 2
    flux_crop = raw.crop((left, top, left + W, top + img_h))

    # Build canvas
    dark_rgb = tuple(int(DARK[i:i+2], 16) for i in (1, 3, 5))
    canvas = Image.new("RGBA", (W, H), dark_rgb + (255,))
    canvas.paste(flux_crop, (0, TOP_BAR_H), flux_crop)
    draw = ImageDraw.Draw(canvas)

    # === TOP BAR ===
    draw.rectangle([(0, 0), (W, TOP_BAR_H)], fill=DARK)
    # Blue accent line at bottom of top bar
    draw.rectangle([(0, TOP_BAR_H - ACCENT_H), (W, TOP_BAR_H)], fill=BLUE)

    # Fonts (2x from spec: 46pt->92pt logo, 62pt->124pt overlay, etc.)
    f_logo = ImageFont.truetype(OSWALD_BOLD, 56)
    f_title_bar = ImageFont.truetype(OSWALD_BOLD, 70)
    f_title_bar_sm = ImageFont.truetype(OSWALD_BOLD, 58)
    f_overlay = ImageFont.truetype(OSWALD_BOLD, 124)
    f_overlay_sm = ImageFont.truetype(OSWALD_BOLD, 100)
    f_brand_bot = ImageFont.truetype(OSWALD_BOLD, 52)
    f_cta = ImageFont.truetype(OSWALD_BOLD, 44)

    # Row 1: hex icon + PUREBRAIN.AI wordmark
    hex_size = 100
    hex_img = Image.open(HEX_ICON).convert("RGBA").resize((hex_size, hex_size), Image.LANCZOS)
    hex_x, hex_y = 80, 30
    canvas.paste(hex_img, (hex_x, hex_y), hex_img)

    wm_x = hex_x + hex_size + 28
    wm_y = hex_y + 22
    draw_brand_wordmark(draw, wm_x, wm_y, f_logo)

    # Row 2: title text in top bar (smaller, may wrap)
    # Remove explicit newlines for top bar display
    bar_title = title.replace("\n", " ")
    title_y = hex_y + hex_size + 16

    use_font = f_title_bar
    tw = draw.textlength(bar_title, font=use_font)
    if tw > (W - 160):
        use_font = f_title_bar_sm
        tw = draw.textlength(bar_title, font=use_font)

    bar_lines = [bar_title]
    if tw > (W - 160):
        words = bar_title.split()
        best = (0, float("inf"))
        for i in range(1, len(words)):
            l1 = " ".join(words[:i])
            l2 = " ".join(words[i:])
            w1 = draw.textlength(l1, font=use_font)
            w2 = draw.textlength(l2, font=use_font)
            diff = abs(w1 - w2)
            if max(w1, w2) <= W - 160 and diff < best[1]:
                best = (i, diff)
        if best[0]:
            bar_lines = [" ".join(words[:best[0]]), " ".join(words[best[0]:])]

    for i, line in enumerate(bar_lines):
        draw.text((80, title_y + i * 76), line, fill=WHITE, font=use_font)

    # === TITLE OVERLAY on FLUX image area ===
    # Center the overlay title vertically and horizontally with stroke
    overlay_lines = title_overlay.split("\n")

    # Choose font: try large first, shrink if any line is too wide
    use_overlay_font = f_overlay
    max_line_w = max(draw.textlength(l, font=use_overlay_font) for l in overlay_lines)
    if max_line_w > W - 200:
        use_overlay_font = f_overlay_sm
        max_line_w = max(draw.textlength(l, font=use_overlay_font) for l in overlay_lines)

    # Get line height
    line_h = use_overlay_font.getbbox("Ay")[3] - use_overlay_font.getbbox("Ay")[1]
    line_spacing = int(line_h * 1.15)
    total_text_h = line_spacing * len(overlay_lines)

    # Vertical center in image area
    text_start_y = TOP_BAR_H + (img_h - total_text_h) // 2

    # Add a subtle dark gradient behind the text for readability
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    scrim_draw = ImageDraw.Draw(scrim)

    scrim_top = text_start_y - 80
    scrim_bot = text_start_y + total_text_h + 80
    scrim_center_y = (scrim_top + scrim_bot) / 2
    scrim_radius = (scrim_bot - scrim_top) / 2 + 100

    for y in range(max(TOP_BAR_H, scrim_top - 100), min(img_area_bot, scrim_bot + 100)):
        dist = abs(y - scrim_center_y)
        if dist < scrim_radius:
            alpha = int(160 * (1 - (dist / scrim_radius) ** 2))
            scrim_draw.line([(0, y), (W, y)], fill=(8, 10, 18, alpha))

    canvas = Image.alpha_composite(canvas, scrim)
    draw = ImageDraw.Draw(canvas)

    # Draw each overlay line centered with stroke
    stroke_color = dark_rgb
    for i, line in enumerate(overlay_lines):
        lw = draw.textlength(line, font=use_overlay_font)
        lx = (W - lw) // 2
        ly = text_start_y + i * line_spacing
        draw_text_with_stroke(draw, (lx, ly), line, use_overlay_font,
                              fill=WHITE, stroke_fill=stroke_color, stroke_width=6)

    # === BOTTOM BAR ===
    draw.rectangle([(0, H - BOT_BAR_H), (W, H)], fill=DARK)
    draw.rectangle([(0, H - BOT_BAR_H), (W, H - BOT_BAR_H + ACCENT_H)], fill=BLUE)

    bot_text_y = H - BOT_BAR_H + (BOT_BAR_H - 52) // 2 - 4

    # Left: PUREBRAIN.AI brand
    draw_brand_wordmark(draw, 80, bot_text_y, f_brand_bot)

    # Right: orange CTA with arrow
    cta_text = cta.upper() + "  >>"
    cta_w = draw.textlength(cta_text, font=f_cta)
    cta_x = W - 80 - cta_w
    cta_y = H - BOT_BAR_H + (BOT_BAR_H - 44) // 2 - 2
    draw.text((cta_x, cta_y), cta_text, fill=ORANGE, font=f_cta)

    # Save
    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=100, optimize=True)
    fsize = output_path.stat().st_size // 1024
    print(f"  [OK] Final: {output_path.name} ({W}x{H}, {fsize} KB)")
    return True


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("LinkedIn Standalone Image Batch Generator - Top 10")
    print("=" * 60)

    # Verify token
    print("\n[1/3] Verifying Replicate API token...")
    resp = requests.get(
        "https://api.replicate.com/v1/account",
        headers={"Authorization": f"Bearer {REPLICATE_API_TOKEN}"},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"FATAL: Replicate token invalid (HTTP {resp.status_code})")
        sys.exit(1)
    acct = resp.json()
    print(f"  Authenticated as: {acct.get('username', 'unknown')}")

    # Generate images one at a time
    print(f"\n[2/3] Generating {len(POSTS)} FLUX images + compositing...")
    results = []

    for idx, post in enumerate(POSTS, 1):
        key = post["key"]
        print(f"\n--- [{idx}/{len(POSTS)}] {key} ---")

        raw_path = RAW_DIR / f"{key}-raw.png"
        final_path = FINAL_DIR / f"{key}-final.png"

        # Skip if final already exists
        if final_path.exists() and final_path.stat().st_size > 50000:
            print(f"  [SKIP] Final already exists: {final_path.name}")
            results.append({"key": key, "status": "skipped", "path": str(final_path)})
            continue

        # Generate FLUX image
        ok = flux_generate(post["prompt"], raw_path)
        if not ok:
            print(f"  [FAIL] FLUX generation failed for {key}")
            results.append({"key": key, "status": "failed_flux"})
            continue

        # Composite
        ok = compose_standalone(
            raw_path=raw_path,
            title=post["title"],
            title_overlay=post["title_overlay"],
            cta=post["cta"],
            output_path=final_path,
        )
        if not ok:
            print(f"  [FAIL] Compositing failed for {key}")
            results.append({"key": key, "status": "failed_composite"})
            continue

        results.append({"key": key, "status": "ok", "path": str(final_path)})

        # Rate limit: 15s between FLUX calls
        if idx < len(POSTS):
            print("  [WAIT] 15s rate limit...")
            time.sleep(15)

    # Summary
    print("\n" + "=" * 60)
    print("[3/3] SUMMARY")
    print("=" * 60)
    ok_count = sum(1 for r in results if r["status"] in ("ok", "skipped"))
    fail_count = len(results) - ok_count
    print(f"  OK: {ok_count} / {len(POSTS)}")
    print(f"  Failed: {fail_count}")
    for r in results:
        status_mark = "OK" if r["status"] in ("ok", "skipped") else "FAIL"
        print(f"  [{status_mark}] {r['key']}: {r['status']}")

    # Write manifest
    manifest_path = BATCH_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nManifest: {manifest_path}")
    print("Done.")


if __name__ == "__main__":
    main()
