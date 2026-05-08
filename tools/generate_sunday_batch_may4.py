#!/usr/bin/env python3
"""
Sunday Batch May 4-10 Image Generator
=====================================

Generates 21 images for the week of May 4-10, 2026:
- 7 blog/newsletter banners (2400x1260, Option D format)
- 14 standalone LinkedIn posts (2160x2700, v4 format — 2K upscale of 1080x1350)

Pipeline: FLUX Pro (Replicate) -> PIL composite -> Oswald Bold typography
Auth: REPLICATE_API_TOKEN from .env
Output: /home/jared/exports/portal-files/sunday-batch-may4-10/images/{raw,final}/

Resumable: skips images already present in final/ directory.
Cost: FLUX 1.1 Pro ~$0.040/image x 21 = ~$0.84 total

Author: 3d-design-specialist
Date: 2026-05-03
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
BATCH_DIR = Path("/home/jared/exports/portal-files/sunday-batch-may4-10")
RAW_DIR = BATCH_DIR / "images" / "raw"
FINAL_DIR = BATCH_DIR / "images" / "final"
RAW_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)

HEX_ICON = PROJECT_ROOT / "assets" / "pt-hex-icon-official.png"
OSWALD_BOLD = "/home/jared/.fonts/Oswald-Bold.ttf"

# Brand colors
BLUE = "#2a93c1"
ORANGE = "#f1420b"
WHITE = "#ffffff"
DIM_WHITE = "#bbbbbb"
DARK = "#080a12"

MANIFEST_PATH = BATCH_DIR / "image-manifest.json"

# ---------------------------------------------------------------------------
# Image briefs (mirror of 04-IMAGE-BRIEFS.md)
# ---------------------------------------------------------------------------

BANNERS = [
    {
        "key": "banner-01-mon-compounding",
        "title": "The Compounding Problem",
        "prompt": "A futuristic ethereal visualization of an exponential curve rising from darkness into light, representing AI memory compounding over time. Abstract data streams in cerulean blue and warm orange flowing into a glowing core. Cinematic lighting, deep shadows, ethereal mist, sci-fi aesthetic. Wide cinematic composition with negative space in the upper-left for branding overlay. 16:9 landscape, photorealistic, dark moody background. No text, no logos, no watermarks.",
    },
    {
        "key": "banner-02-tue-trust",
        "title": "Trust Is Not a Vibe",
        "prompt": "A minimalist futuristic vault or gateway with translucent verification layers stacked like a security audit. Glowing cerulean blue verification beams scanning through the layers. One orange beam highlighting an active audit. Clean negative space, ethereal atmosphere, sci-fi minimalism, deep dark background. 16:9 landscape, cinematic depth, photorealistic. No text, no logos, no watermarks.",
    },
    {
        "key": "banner-03-wed-reset",
        "title": "The $200K Reset",
        "prompt": "An abstract representation of memory dissolving into static, then reforming. A clock-like circular form where each segment shows different states of context: full, partial, empty. Cerulean blue data flowing in, orange warning highlights on the empty segments. Futuristic dark aesthetic with ethereal mist. 16:9 landscape, dramatic side lighting, photorealistic. No text, no logos, no watermarks.",
    },
    {
        "key": "banner-04-thu-delegation",
        "title": "Delegation as a Force Multiplier",
        "prompt": "A central abstract figure silhouette at the top of a hierarchical lattice of glowing nodes, each node connected by cerulean blue threads. A few orange highlights mark active branches. Dark ethereal background, futuristic, sci-fi command-center aesthetic. The structure feels like a conductor with an orchestra of light. 16:9 landscape, cinematic, photorealistic. No text, no logos, no watermarks.",
    },
    {
        "key": "banner-05-fri-receipt",
        "title": "The Ship Receipt",
        "prompt": "A floating, translucent receipt or document materializing in air, with verification stamps and timestamps glowing on its surface. Cerulean blue lines of digital signature flowing across the document. One orange seal of approval. Dark futuristic background, ethereal mist, cinematic depth. 16:9 landscape, photorealistic. No text, no logos, no watermarks.",
    },
    {
        "key": "banner-06-sat-postmortem",
        "title": "The Honest Postmortem",
        "prompt": "A futuristic transparent autopsy table with three glowing data signatures laid out, each marked with a small orange flag. Cerulean blue diagnostic lines tracing through them. Dark background, clinical-meets-ethereal aesthetic, sci-fi forensics lab. 16:9 landscape, dramatic top-down lighting, photorealistic. No text, no logos, no watermarks.",
    },
    {
        "key": "banner-07-sun-quietcompound",
        "title": "The Quiet Compound",
        "prompt": "A long, slow horizon. A flat line in the foreground that bends upward in the distance into an exponential curve glowing cerulean blue. A single orange dot near where the curve begins to bend marks an inflection point. Ethereal, sunrise mood, dark sci-fi aesthetic with deep atmospheric perspective. 16:9 landscape, cinematic wide shot, photorealistic. No text, no logos, no watermarks.",
    },
]

STANDALONES = [
    {
        "key": "stand-01-mon-5percent",
        "title": "The 5% Who Ship",
        "cta": "READ MORE",
        "prompt": "A futuristic city of interconnected lights, with 95% of the buildings dim and 5% blazing in cerulean blue and orange. Wide aerial perspective, ethereal night atmosphere, sci-fi cinematic. 4:5 portrait composition. Dark background. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-02-tue-reset",
        "title": "Tuesday Morning Reset",
        "cta": "USE TODAY",
        "prompt": "A floating clipboard or checklist materialized in air, glowing cerulean blue. Five checkboxes. The first one being checked by a stream of light. Dark ethereal background, futuristic minimalism. 4:5 portrait. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-03-tue-calculator",
        "title": "Stop Guessing Your AI Spend",
        "cta": "RUN THE NUMBERS",
        "prompt": "A futuristic abacus or calculator made of light, beads transforming into digital numbers. Cerulean blue framework, orange numbers. Clean minimal composition, ethereal sci-fi aesthetic. 4:5 portrait. Dark background. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-04-wed-overnight",
        "title": "While You Sleep",
        "cta": "SEE THE RECEIPTS",
        "prompt": "A sleeping operator silhouette in the foreground, with translucent agent activity glowing in the room around them in cerulean blue threads. Orange highlights mark completed tasks. Dark, peaceful, sci-fi night-shift aesthetic. 4:5 portrait. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-05-wed-meridian",
        "title": "$70-110K Saved",
        "cta": "READ THE CASE",
        "prompt": "A construction site at dawn with futuristic AI-assisted overlays — schedule grids, compliance markers, crew assignments — glowing cerulean blue across the scene. Orange highlights on key transitions. Dramatic golden hour lighting, sci-fi aesthetic. 4:5 portrait. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-06-thu-test",
        "title": "The Delegation Test",
        "cta": "RUN IT FRIDAY",
        "prompt": "Three glowing question marks suspended in space, each a different size, connected by cerulean blue beams. Orange highlight on the third one. Minimal composition, deep dark background, ethereal sci-fi. 4:5 portrait. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-07-thu-pilot",
        "title": "Pilot Death Pattern",
        "cta": "SHIP UGLY",
        "prompt": "A graveyard of demo screens stacked like tombstones, glowing faintly. One single demo screen at the front breaks through into a brighter color, transitioning to production reality. Cerulean blue and orange contrast. Dark, slightly haunting, sci-fi aesthetic. 4:5 portrait. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-08-fri-shipped",
        "title": "Receipts Inside",
        "cta": "SEE WHAT SHIPPED",
        "prompt": "Four glowing receipt-like documents floating in formation, each with a checkmark. Below them, a faint timeline of activity from the past week. Cerulean blue framework, orange accents. Sci-fi cinematic minimalism, dark background. 4:5 portrait. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-09-fri-customervoice",
        "title": "Better Than Mine",
        "cta": "READ THE STORY",
        "prompt": "An abstract speech bubble made of woven light, cerulean blue threads forming the shape, with orange highlights at the edges. Inside the bubble, faint silhouettes of words flowing. Ethereal, calm, sci-fi minimalism. 4:5 portrait. Dark background. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-10-sat-production",
        "title": "Show Me Production",
        "cta": "WHERE AI COMPOUNDS",
        "prompt": "A large stage in spotlight foreground, empty and theatrical. Behind it, a working production environment glowing in cerulean blue, real and unpolished. Orange transition between the two zones. Cinematic depth, sci-fi contrast. 4:5 portrait. Dark background. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-11-sat-sundayprep",
        "title": "Sunday Prep Ritual",
        "cta": "20 MIN, 4 HRS BACK",
        "prompt": "A peaceful Sunday evening study scene with a glowing AI context block on the desk. Five floating bullet points hover above it in cerulean blue. Soft warm orange ambient lighting from a single lamp. Sci-fi but cozy, minimalist composition. 4:5 portrait. Dark background. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-12-sun-math",
        "title": "Sunday Math",
        "cta": "RUN THE NUMBERS",
        "prompt": "A glowing calculator interface floating above a quiet Sunday morning landscape. Cerulean blue digits and framework, one orange total at the bottom. Peaceful, reflective, sci-fi minimalism. 4:5 portrait. Dark background. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-13-sun-94percent",
        "title": "The 94% You Don't See",
        "cta": "READ THE MATH",
        "prompt": "A receipt-like document floating in dark space. Below the empty surface of the receipt, faint annotations and grid lines breaking down some math. Cinematic minimalism, ethereal background, cerulean blue and orange highlights. 4:5 portrait. No text, no logos, no watermarks.",
    },
    {
        "key": "stand-14-flex-letgo",
        "title": "The Hardest Part",
        "cta": "LET GO",
        "prompt": "An open hand silhouette in lower foreground, releasing a glowing cerulean blue orb of work that is rising and being caught by a network of agent-nodes above it. Orange threads connect the conductor (hand) to the orchestra (nodes). Sci-fi cinematic, peaceful, ethereal. 4:5 portrait. Dark background. No text, no logos, no watermarks.",
    },
]

# ---------------------------------------------------------------------------
# FLUX generation
# ---------------------------------------------------------------------------

def flux_generate(prompt: str, aspect_ratio: str, output_path: Path, max_retries: int = 2) -> bool:
    """Generate an image via FLUX 1.1 Pro on Replicate. Returns True on success."""
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
# PIL composition: BANNER (Option D, 2400x1260)
# ---------------------------------------------------------------------------

def compose_banner(raw_path: Path, title: str, output_path: Path) -> bool:
    """Option D: bottom gradient panel with hex+wordmark upper-left, title bottom-left."""
    from PIL import Image, ImageDraw, ImageFont

    W, H = 2400, 1260
    SAFE_LEFT = 150
    SAFE_RIGHT = W - 150

    raw = Image.open(raw_path).convert("RGBA")
    scale = max(W / raw.width, H / raw.height)
    raw = raw.resize((int(raw.width * scale), int(raw.height * scale)), Image.LANCZOS)
    left = (raw.width - W) // 2
    top = (raw.height - H) // 2
    canvas = raw.crop((left, top, left + W, top + H))

    # Bottom gradient overlay (Option D — gradual darkening of bottom 50%)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    grad_start_y = int(H * 0.45)
    grad_end_y = H
    for y in range(grad_start_y, grad_end_y):
        # 0 alpha at start, 240/255 (94%) at base
        progress = (y - grad_start_y) / (grad_end_y - grad_start_y)
        # Ease curve for smoother fade
        eased = progress ** 1.5
        alpha = int(240 * eased)
        odraw.line([(0, y), (W, y)], fill=(8, 10, 18, alpha))
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    # Fonts
    f_logo = ImageFont.truetype(OSWALD_BOLD, 56)
    f_title = ImageFont.truetype(OSWALD_BOLD, 110)
    f_subtitle = ImageFont.truetype(OSWALD_BOLD, 44)
    f_footer = ImageFont.truetype(OSWALD_BOLD, 28)

    # Upper-left: hex icon + PUREBRAIN.AI wordmark
    hex_size = 90
    hex_img = Image.open(HEX_ICON).convert("RGBA").resize((hex_size, hex_size), Image.LANCZOS)
    hex_x, hex_y = SAFE_LEFT, 70
    canvas.paste(hex_img, (hex_x, hex_y), hex_img)

    wm_x = hex_x + hex_size + 24
    wm_y = hex_y + 14
    parts = [("PUREBR", BLUE), ("AI", ORANGE), ("N", BLUE), (".AI", WHITE)]
    cx = wm_x
    for text, color in parts:
        # Slight shadow for legibility on bright FLUX backgrounds
        draw.text((cx + 2, wm_y + 2), text, fill=(0, 0, 0, 200), font=f_logo)
        draw.text((cx, wm_y), text, fill=color, font=f_logo)
        cx += draw.textlength(text, font=f_logo)

    # Bottom-left: blog title (in dark gradient zone)
    # Wrap title to two lines if needed
    title_text = title
    title_w = draw.textlength(title_text, font=f_title)
    title_lines = [title_text]
    if title_w > (SAFE_RIGHT - SAFE_LEFT - 100):
        # Find wrap point at last space before midpoint
        words = title_text.split()
        mid = len(words) // 2
        title_lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    # Title baseline: ~210 from bottom
    title_y = H - 280 - (len(title_lines) - 1) * 110
    for i, line in enumerate(title_lines):
        ly = title_y + i * 110
        # Subtle shadow
        draw.text((SAFE_LEFT + 3, ly + 3), line, fill=(0, 0, 0, 220), font=f_title)
        draw.text((SAFE_LEFT, ly), line, fill=WHITE, font=f_title)

    # Subtitle: "Awaken Your AI Partner Today" (orange)
    sub_y = H - 130
    subtitle = "Awaken Your AI Partner Today"
    draw.text((SAFE_LEFT + 2, sub_y + 2), subtitle, fill=(0, 0, 0, 200), font=f_subtitle)
    draw.text((SAFE_LEFT, sub_y), subtitle, fill=ORANGE, font=f_subtitle)

    # Footer: "The Neural Feed - A Blog by Aether"
    footer = "The Neural Feed  |  A Blog by Aether  |  AI Partner for PureTechnology.ai"
    foot_y = H - 60
    draw.text((SAFE_LEFT, foot_y), footer, fill=DIM_WHITE, font=f_footer)

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=100, optimize=True)
    print(f"  [OK] Banner final: {output_path.name} ({W}x{H})")
    return True


# ---------------------------------------------------------------------------
# PIL composition: STANDALONE (v4, 2160x2700)
# ---------------------------------------------------------------------------

def compose_standalone(raw_path: Path, title: str, cta: str, output_path: Path) -> bool:
    """v4 standalone: top bar (hex+wordmark+title) / FLUX image / bottom bar (PUREBRAIN.AI+CTA)."""
    from PIL import Image, ImageDraw, ImageFont

    W, H = 2160, 2700
    # Bar heights scale by 2x from 1080x1350 spec (140px -> 280px, 90px -> 180px)
    TOP_BAR_H = 280
    BOT_BAR_H = 180
    ACCENT_H = 4  # blue line (2px x2 scale)

    # FLUX area
    img_h = H - TOP_BAR_H - BOT_BAR_H

    # Load FLUX raw, fit into image area
    raw = Image.open(raw_path).convert("RGBA")
    scale = max(W / raw.width, img_h / raw.height)
    raw = raw.resize((int(raw.width * scale), int(raw.height * scale)), Image.LANCZOS)
    left = (raw.width - W) // 2
    top = (raw.height - img_h) // 2
    flux_crop = raw.crop((left, top, left + W, top + img_h))

    # Build canvas (dark bg)
    canvas = Image.new("RGBA", (W, H), tuple(int(DARK[i:i+2], 16) for i in (1, 3, 5)) + (255,))
    canvas.paste(flux_crop, (0, TOP_BAR_H), flux_crop)
    draw = ImageDraw.Draw(canvas)

    # Top bar fill (already dark from canvas init)
    draw.rectangle([(0, 0), (W, TOP_BAR_H)], fill=DARK)
    # Blue accent line at bottom of top bar
    draw.rectangle([(0, TOP_BAR_H - ACCENT_H), (W, TOP_BAR_H)], fill=BLUE)

    # Bottom bar fill
    draw.rectangle([(0, H - BOT_BAR_H), (W, H)], fill=DARK)
    # Blue accent line at top of bottom bar
    draw.rectangle([(0, H - BOT_BAR_H), (W, H - BOT_BAR_H + ACCENT_H)], fill=BLUE)

    # Fonts (scaled 2x from spec for 2K)
    f_logo = ImageFont.truetype(OSWALD_BOLD, 56)
    f_title = ImageFont.truetype(OSWALD_BOLD, 84)
    f_title_sm = ImageFont.truetype(OSWALD_BOLD, 70)
    f_brand_bot = ImageFont.truetype(OSWALD_BOLD, 64)
    f_cta = ImageFont.truetype(OSWALD_BOLD, 56)

    # --- TOP BAR ---
    # Row 1: hex icon + PUREBRAIN.AI wordmark
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

    # Row 2: title (large, white, may wrap to 2 lines)
    title_y = hex_y + hex_size + 24

    # Choose font size based on title length
    use_font = f_title
    title_w = draw.textlength(title, font=use_font)
    if title_w > (W - 160):
        use_font = f_title_sm
        title_w = draw.textlength(title, font=use_font)

    title_lines = [title]
    if title_w > (W - 160):
        words = title.split()
        # Pick a wrap point that keeps lines roughly balanced
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
            title_lines = [" ".join(words[:best[0]]), " ".join(words[best[0]:])]

    for i, line in enumerate(title_lines):
        draw.text((80, title_y + i * 90), line, fill=WHITE, font=use_font)

    # --- BOTTOM BAR ---
    bot_text_y = H - BOT_BAR_H + (BOT_BAR_H - 64) // 2 - 4

    # Left: PUREBRAIN.AI brand
    cx = 80
    for text, color in parts:
        draw.text((cx, bot_text_y), text, fill=color, font=f_brand_bot)
        cx += draw.textlength(text, font=f_brand_bot)

    # Right: orange CTA
    cta_text = cta + "  >>"
    cta_w = draw.textlength(cta_text, font=f_cta)
    cta_x = W - 80 - cta_w
    cta_y = H - BOT_BAR_H + (BOT_BAR_H - 56) // 2 - 2
    draw.text((cta_x, cta_y), cta_text, fill=ORANGE, font=f_cta)

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=100, optimize=True)
    print(f"  [OK] Standalone final: {output_path.name} ({W}x{H})")
    return True


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def load_manifest():
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text())
        except Exception:
            pass
    return {"banners": {}, "standalones": {}, "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def save_manifest(manifest):
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")


def process_banner(brief, manifest):
    key = brief["key"]
    raw_path = RAW_DIR / f"{key}.png"
    final_path = FINAL_DIR / f"{key}.png"

    print(f"\n[BANNER] {key} - {brief['title']}")

    if final_path.exists() and final_path.stat().st_size > 50000:
        print(f"  [SKIP] Final already exists: {final_path.name}")
        manifest["banners"][key] = {
            "title": brief["title"],
            "raw": str(raw_path),
            "final": str(final_path),
            "status": "complete",
            "format": "banner-2400x1260-optionD",
        }
        return True

    print(f"  [FLUX] aspect=16:9")
    if not flux_generate(brief["prompt"], "16:9", raw_path):
        manifest["banners"][key] = {"title": brief["title"], "status": "flux_failed"}
        return False

    if not compose_banner(raw_path, brief["title"], final_path):
        manifest["banners"][key] = {"title": brief["title"], "status": "compose_failed", "raw": str(raw_path)}
        return False

    manifest["banners"][key] = {
        "title": brief["title"],
        "raw": str(raw_path),
        "final": str(final_path),
        "status": "complete",
        "format": "banner-2400x1260-optionD",
    }
    return True


def process_standalone(brief, manifest):
    key = brief["key"]
    raw_path = RAW_DIR / f"{key}.png"
    final_path = FINAL_DIR / f"{key}.png"

    print(f"\n[STANDALONE] {key} - {brief['title']}")

    if final_path.exists() and final_path.stat().st_size > 50000:
        print(f"  [SKIP] Final already exists: {final_path.name}")
        manifest["standalones"][key] = {
            "title": brief["title"],
            "cta": brief["cta"],
            "raw": str(raw_path),
            "final": str(final_path),
            "status": "complete",
            "format": "standalone-2160x2700-v4",
        }
        return True

    print(f"  [FLUX] aspect=4:5")
    if not flux_generate(brief["prompt"], "4:5", raw_path):
        manifest["standalones"][key] = {"title": brief["title"], "status": "flux_failed"}
        return False

    if not compose_standalone(raw_path, brief["title"], brief["cta"], final_path):
        manifest["standalones"][key] = {
            "title": brief["title"],
            "status": "compose_failed",
            "raw": str(raw_path),
        }
        return False

    manifest["standalones"][key] = {
        "title": brief["title"],
        "cta": brief["cta"],
        "raw": str(raw_path),
        "final": str(final_path),
        "status": "complete",
        "format": "standalone-2160x2700-v4",
    }
    return True


def main():
    print("=" * 70)
    print("Sunday Batch May 4-10 Image Generator")
    print(f"  Banners: {len(BANNERS)} @ 2400x1260 (Option D)")
    print(f"  Standalones: {len(STANDALONES)} @ 2160x2700 (v4)")
    print(f"  Output: {FINAL_DIR}")
    print("=" * 70)

    manifest = load_manifest()

    success = 0
    failed = []

    only_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if only_arg == "banners":
        targets = [("banner", b) for b in BANNERS]
    elif only_arg == "standalones":
        targets = [("standalone", s) for s in STANDALONES]
    elif only_arg and only_arg.startswith("key="):
        wanted = only_arg[4:]
        targets = [("banner", b) for b in BANNERS if b["key"] == wanted]
        targets += [("standalone", s) for s in STANDALONES if s["key"] == wanted]
    else:
        targets = [("banner", b) for b in BANNERS] + [("standalone", s) for s in STANDALONES]

    for kind, brief in targets:
        try:
            if kind == "banner":
                ok = process_banner(brief, manifest)
            else:
                ok = process_standalone(brief, manifest)
            if ok:
                success += 1
            else:
                failed.append(brief["key"])
        except Exception as e:
            print(f"  [EXC] {brief['key']}: {e}")
            import traceback
            traceback.print_exc()
            failed.append(brief["key"])
        finally:
            save_manifest(manifest)

    manifest["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    manifest["summary"] = {
        "total": len(targets),
        "success": success,
        "failed": failed,
    }
    save_manifest(manifest)

    print("\n" + "=" * 70)
    print(f"DONE: {success}/{len(targets)} succeeded")
    if failed:
        print(f"FAILED ({len(failed)}): {', '.join(failed)}")
    print(f"Manifest: {MANIFEST_PATH}")
    print("=" * 70)

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
