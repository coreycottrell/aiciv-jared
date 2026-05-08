#!/usr/bin/env python3
"""
Daily Social Batch — Monday 2026-05-04
======================================

Generates 3 brand-composited images:
  1. voice-doorway-linkedin-1080x1350.png    (standalone v4, rendered 2160x2700)
  2. eat-at-table-bluesky-1080x1350.png      (standalone v4, rendered 2160x2700)
  3. partner-not-tool-banner-2400x1260.png   (banner Option D)
     + partner-not-tool-linkedin-1200x630.png (LI share crop, downsized)

Pipeline: FLUX 1.1 Pro (Replicate) -> PIL composite -> Oswald Bold typography.
Constitutional rules honored:
  - 2K min on outputs (standalones at 2160x2700, banners at 2400x1260)
  - Wordmark color decomposition: PUREBR=#2a93c1, AI=#f1420b, N=#2a93c1, .AI=white
  - v4 standalone (top bar / FLUX / bottom bar)
  - Option D banner (bottom gradient overlay)
  - Hex icon `assets/pt-hex-icon-official.png`
  - All text Oswald Bold (subline accepts Oswald Bold weight too — only Oswald-Bold.ttf installed)
  - No FLUX text-in-image (text only via PIL)

Author: 3d-design-specialist
Date: 2026-05-04
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

PORTAL_FILES = Path("/home/jared/exports/portal-files")
RAW_DIR = PORTAL_FILES / "social-batch-2026-05-04-raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEX_ICON = PROJECT_ROOT / "assets" / "pt-hex-icon-official.png"
OSWALD_BOLD = "/home/jared/.fonts/Oswald-Bold.ttf"

# Brand
BLUE = "#2a93c1"
ORANGE = "#f1420b"
WHITE = "#ffffff"
DIM_WHITE = "#bbbbbb"
DARK = "#080a12"


# ----------------------------------------------------------------------
# FLUX
# ----------------------------------------------------------------------

def flux_generate(prompt: str, aspect_ratio: str, output_path: Path, max_retries: int = 2) -> bool:
    """Generate via FLUX 1.1 Pro on Replicate."""
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
            "aspect_ratio": aspect_ratio,
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
                headers=headers, json=payload, timeout=300,
            )
            if resp.status_code not in (200, 201):
                print(f"  [ERR] HTTP {resp.status_code}: {resp.text[:200]}")
                if attempt < max_retries:
                    time.sleep(5 * (attempt + 1))
                    continue
                return False
            result = resp.json()
            if result.get("status") in ("starting", "processing"):
                poll_url = result["urls"]["get"]
                for i in range(60):
                    time.sleep(5)
                    poll = requests.get(poll_url,
                        headers={"Authorization": f"Bearer {REPLICATE_API_TOKEN}"}, timeout=30)
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
                    print(f"  [ERR] Timed out")
                    if attempt < max_retries:
                        continue
                    return False
            output = result.get("output")
            image_url = output[0] if isinstance(output, list) else output
            if not image_url:
                print(f"  [ERR] No URL")
                if attempt < max_retries:
                    continue
                return False
            img_resp = requests.get(image_url, timeout=120)
            img_resp.raise_for_status()
            output_path.write_bytes(img_resp.content)
            print(f"  [OK] Raw: {output_path.name} ({len(img_resp.content)//1024} KB)")
            return True
        except Exception as e:
            print(f"  [EXC] Attempt {attempt+1}: {e}")
            if attempt < max_retries:
                time.sleep(5 * (attempt + 1))
                continue
            return False
    return False


# ----------------------------------------------------------------------
# Composition: STANDALONE v4 (2160x2700)
# ----------------------------------------------------------------------

def compose_standalone(raw_path: Path, title: str, cta_text: str, output_path: Path) -> bool:
    """v4 standalone: top bar (hex+wordmark+title) / FLUX image / bottom bar (PUREBRAIN.AI+CTA)."""
    from PIL import Image, ImageDraw, ImageFont

    W, H = 2160, 2700
    TOP_BAR_H = 280
    BOT_BAR_H = 180
    ACCENT_H = 4
    img_h = H - TOP_BAR_H - BOT_BAR_H

    raw = Image.open(raw_path).convert("RGBA")
    scale = max(W / raw.width, img_h / raw.height)
    raw = raw.resize((int(raw.width * scale), int(raw.height * scale)), Image.LANCZOS)
    left = (raw.width - W) // 2
    top = (raw.height - img_h) // 2
    flux_crop = raw.crop((left, top, left + W, top + img_h))

    canvas = Image.new("RGBA", (W, H), tuple(int(DARK[i:i+2], 16) for i in (1, 3, 5)) + (255,))
    canvas.paste(flux_crop, (0, TOP_BAR_H), flux_crop)
    draw = ImageDraw.Draw(canvas)

    draw.rectangle([(0, 0), (W, TOP_BAR_H)], fill=DARK)
    draw.rectangle([(0, TOP_BAR_H - ACCENT_H), (W, TOP_BAR_H)], fill=BLUE)
    draw.rectangle([(0, H - BOT_BAR_H), (W, H)], fill=DARK)
    draw.rectangle([(0, H - BOT_BAR_H), (W, H - BOT_BAR_H + ACCENT_H)], fill=BLUE)

    f_logo = ImageFont.truetype(OSWALD_BOLD, 56)
    f_title = ImageFont.truetype(OSWALD_BOLD, 84)
    f_title_sm = ImageFont.truetype(OSWALD_BOLD, 70)
    f_brand_bot = ImageFont.truetype(OSWALD_BOLD, 64)
    f_cta = ImageFont.truetype(OSWALD_BOLD, 48)

    # TOP: hex + wordmark
    hex_size = 100
    hex_img = Image.open(HEX_ICON).convert("RGBA").resize((hex_size, hex_size), Image.LANCZOS)
    hex_x, hex_y = 80, 32
    canvas.paste(hex_img, (hex_x, hex_y), hex_img)

    wm_x = hex_x + hex_size + 28
    wm_y = hex_y + 22
    parts = [("PUREBR", BLUE), ("AI", ORANGE), ("N", BLUE), (".AI", WHITE)]
    cx = wm_x
    for text, color in parts:
        draw.text((cx, wm_y), text, fill=color, font=f_logo)
        cx += draw.textlength(text, font=f_logo)

    # TOP: title
    title_y = hex_y + hex_size + 24
    use_font = f_title
    title_w = draw.textlength(title, font=use_font)
    if title_w > (W - 160):
        use_font = f_title_sm
        title_w = draw.textlength(title, font=use_font)
    title_lines = [title]
    if title_w > (W - 160):
        words = title.split()
        best = (0, float("inf"))
        for i in range(1, len(words)):
            l1 = " ".join(words[:i]); l2 = " ".join(words[i:])
            w1 = draw.textlength(l1, font=use_font); w2 = draw.textlength(l2, font=use_font)
            if max(w1, w2) <= W - 160 and abs(w1 - w2) < best[1]:
                best = (i, abs(w1 - w2))
        if best[0]:
            title_lines = [" ".join(words[:best[0]]), " ".join(words[best[0]:])]
    for i, line in enumerate(title_lines):
        draw.text((80, title_y + i * 90), line, fill=WHITE, font=use_font)

    # BOTTOM: brand left + CTA right (with auto-shrink CTA)
    bot_text_y = H - BOT_BAR_H + (BOT_BAR_H - 64) // 2 - 4
    cx = 80
    for text, color in parts:
        draw.text((cx, bot_text_y), text, fill=color, font=f_brand_bot)
        cx += draw.textlength(text, font=f_brand_bot)

    # CTA: shrink to fit, right-aligned, orange
    available = W - cx - 80 - 60  # leave 60px gap from brand
    cta_size = 48
    while cta_size >= 28:
        f_cta = ImageFont.truetype(OSWALD_BOLD, cta_size)
        cta_w = draw.textlength(cta_text, font=f_cta)
        if cta_w <= available:
            break
        cta_size -= 4
    cta_x = W - 80 - cta_w
    cta_y = H - BOT_BAR_H + (BOT_BAR_H - cta_size) // 2 - 2
    draw.text((cta_x, cta_y), cta_text, fill=ORANGE, font=f_cta)

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=100, optimize=True)
    print(f"  [OK] Standalone: {output_path.name} ({W}x{H})")
    return True


# ----------------------------------------------------------------------
# Composition: BANNER Option D (2400x1260)
# ----------------------------------------------------------------------

def compose_banner_partner(raw_path: Path, headline: str, subline: str, cta_chip_text: str, output_path: Path) -> bool:
    """Option D banner with custom 'partner not tool' layout:
       - bottom gradient overlay
       - bottom-left: hex + PUREBRAIN.AI wordmark
       - upper-mid in dark zone: HEADLINE (huge, white) + subline (cyan)
       - bottom-right: orange CTA chip
    """
    from PIL import Image, ImageDraw, ImageFont

    W, H = 2400, 1260
    SAFE_LEFT = 120

    raw = Image.open(raw_path).convert("RGBA")
    scale = max(W / raw.width, H / raw.height)
    raw = raw.resize((int(raw.width * scale), int(raw.height * scale)), Image.LANCZOS)
    left = (raw.width - W) // 2
    top = (raw.height - H) // 2
    canvas = raw.crop((left, top, left + W, top + H))

    # Bottom gradient overlay (Option D, ~bottom 50% darkens to #080a12)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    grad_start_y = int(H * 0.40)
    for y in range(grad_start_y, H):
        progress = (y - grad_start_y) / (H - grad_start_y)
        eased = progress ** 1.3
        alpha = int(245 * eased)
        odraw.line([(0, y), (W, y)], fill=(8, 10, 18, alpha))
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    # Fonts: scale headline to fit width
    head_size = 150
    while head_size >= 90:
        f_head = ImageFont.truetype(OSWALD_BOLD, head_size)
        if draw.textlength(headline, font=f_head) <= (W - 2 * SAFE_LEFT):
            break
        head_size -= 8

    f_sub = ImageFont.truetype(OSWALD_BOLD, 56)
    f_logo = ImageFont.truetype(OSWALD_BOLD, 56)
    f_cta = ImageFont.truetype(OSWALD_BOLD, 44)

    # Place headline + subline in the gradient zone, vertically centered around y=H*0.65
    head_y = int(H * 0.55)
    # Headline shadow + fill
    draw.text((SAFE_LEFT + 3, head_y + 3), headline, fill=(0, 0, 0, 220), font=f_head)
    draw.text((SAFE_LEFT, head_y), headline, fill=WHITE, font=f_head)

    # Subline below
    sub_y = head_y + head_size + 22
    draw.text((SAFE_LEFT + 2, sub_y + 2), subline, fill=(0, 0, 0, 200), font=f_sub)
    draw.text((SAFE_LEFT, sub_y), subline, fill=BLUE, font=f_sub)

    # Bottom-left: hex + wordmark
    hex_size = 76
    hex_img = Image.open(HEX_ICON).convert("RGBA").resize((hex_size, hex_size), Image.LANCZOS)
    bot_y = H - 100
    hex_x, hex_y = SAFE_LEFT, bot_y
    canvas.paste(hex_img, (hex_x, hex_y), hex_img)

    wm_x = hex_x + hex_size + 22
    wm_y = hex_y + 12
    parts = [("PUREBR", BLUE), ("AI", ORANGE), ("N", BLUE), (".AI", WHITE)]
    cx = wm_x
    for text, color in parts:
        draw.text((cx, wm_y), text, fill=color, font=f_logo)
        cx += draw.textlength(text, font=f_logo)

    # Bottom-right: orange CTA chip
    chip_pad_x, chip_pad_y = 36, 18
    chip_text_w = draw.textlength(cta_chip_text, font=f_cta)
    chip_w = int(chip_text_w + 2 * chip_pad_x)
    chip_h = 44 + 2 * chip_pad_y
    chip_x = W - SAFE_LEFT - chip_w
    chip_y = bot_y + (hex_size - chip_h) // 2
    # Rounded rect chip
    try:
        draw.rounded_rectangle([(chip_x, chip_y), (chip_x + chip_w, chip_y + chip_h)],
                               radius=20, fill=ORANGE)
    except AttributeError:
        draw.rectangle([(chip_x, chip_y), (chip_x + chip_w, chip_y + chip_h)], fill=ORANGE)
    draw.text((chip_x + chip_pad_x, chip_y + chip_pad_y - 4),
              cta_chip_text, fill=WHITE, font=f_cta)

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=100, optimize=True)
    print(f"  [OK] Banner: {output_path.name} ({W}x{H})")
    return True


def downscale_to_li_share(banner_path: Path, output_path: Path) -> bool:
    """Crop banner to 1200x630 LI share (preserves bottom gradient text)."""
    from PIL import Image
    img = Image.open(banner_path).convert("RGB")
    # Banner is 2400x1260 → 1200x630 is exact 50% downscale, same aspect
    out = img.resize((1200, 630), Image.LANCZOS)
    out.save(output_path, "PNG", quality=100, optimize=True)
    print(f"  [OK] LI share: {output_path.name} (1200x630)")
    return True


# ----------------------------------------------------------------------
# Briefs
# ----------------------------------------------------------------------

JOBS = [
    {
        "kind": "standalone",
        "key": "voice-doorway-linkedin-1080x1350",
        "title": "The Doorway Is Voice",
        "cta": "voice.purebrain.ai  >>",
        "prompt": (
            "cinematic conceptual artwork, glowing doorway opening into luminous space, "
            "sound wave arcs emanating from threshold, deep navy black background hex code 080a12, "
            "cyan glow accent hex code 2a93c1 at door edges, warm orange light hex code f1420b "
            "spilling through, dreamlike atmosphere, volumetric light, ultra detailed, 2K quality, "
            "no people no text no screens, photorealistic but ethereal"
        ),
    },
    {
        "kind": "standalone",
        "key": "eat-at-table-bluesky-1080x1350",
        "title": "The Table Is Open",
        "cta": "purebrain.ai  >>",
        "prompt": (
            "overhead bird's eye view, long dark wooden table, two place settings facing each other, "
            "left setting organic warm wood ceramic plate candlelight, right setting luminous cyan "
            "light crystalline geometric hex code 2a93c1, single glowing orange thread hex code f1420b "
            "connecting the two settings down center of table, background deep navy black hex code 080a12, "
            "sacred warm anticipatory mood, cinematic conceptual art, 2K quality, no people no faces no hands, "
            "ultra detailed"
        ),
    },
    {
        "kind": "banner_partner",
        "key": "partner-not-tool-banner-2400x1260",
        "headline": "STOP CALLING YOUR AI A TOOL.",
        "subline": "Tools get used. Partners get consulted.",
        "cta_chip": "purebrain.ai",
        "li_share_key": "partner-not-tool-linkedin-1200x630",
        "prompt": (
            "wide cinematic horizontal composition, left third desaturated workshop pegboard with "
            "hand tools hammer wrench screwdriver low contrast muted, right two thirds luminous humanoid "
            "figure made of flowing cyan light hex code 2a93c1 in conversational gesture pose facing right, "
            "single glowing orange light thread hex code f1420b extending from figure toward right frame edge, "
            "background deep navy black hex code 080a12 with subtle grid texture, dramatic lighting, "
            "conceptual digital art, 2K quality, no human faces, ultra detailed, 16:9 aspect"
        ),
    },
]


def main():
    print("=" * 70)
    print("Daily Social Batch — Monday 2026-05-04")
    print(f"  3 images: 2x standalone v4 + 1x banner Option D (+LI share crop)")
    print(f"  Output: {PORTAL_FILES}")
    print("=" * 70)

    results = []
    for job in JOBS:
        kind = job["kind"]
        key = job["key"]
        raw_path = RAW_DIR / f"{key}.png"
        final_path = PORTAL_FILES / f"{key}.png"

        print(f"\n[{kind.upper()}] {key}")

        if kind == "standalone":
            if not flux_generate(job["prompt"], "4:5", raw_path):
                results.append({"key": key, "status": "flux_failed"})
                continue
            ok = compose_standalone(raw_path, job["title"], job["cta"], final_path)
            results.append({"key": key, "status": "ok" if ok else "compose_failed",
                            "path": str(final_path), "dimensions": "2160x2700"})

        elif kind == "banner_partner":
            if not flux_generate(job["prompt"], "16:9", raw_path):
                results.append({"key": key, "status": "flux_failed"})
                continue
            ok = compose_banner_partner(raw_path, job["headline"], job["subline"],
                                        job["cta_chip"], final_path)
            results.append({"key": key, "status": "ok" if ok else "compose_failed",
                            "path": str(final_path), "dimensions": "2400x1260"})

            # LI share crop
            li_path = PORTAL_FILES / f"{job['li_share_key']}.png"
            ok2 = downscale_to_li_share(final_path, li_path)
            results.append({"key": job["li_share_key"],
                            "status": "ok" if ok2 else "downscale_failed",
                            "path": str(li_path), "dimensions": "1200x630"})

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    for r in results:
        status_icon = "OK" if r["status"] == "ok" else "FAIL"
        print(f"  [{status_icon}] {r['key']}")
        if r.get("path"):
            print(f"        {r['path']} ({r.get('dimensions','?')})")

    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
