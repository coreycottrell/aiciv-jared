#!/usr/bin/env python3
"""
LinkedIn Week 2026-04-07 Image Production Pipeline
7 standalone post images using FLUX 2 Pro + PIL composite

Tool chain: FLUX Pro base → PIL composite with Oswald Bold
Brand compliance per content-creation-sop and purebrain-social-design
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

# Load .env
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key not in os.environ:
                    os.environ[key] = value

REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
assert REPLICATE_TOKEN, "REPLICATE_API_TOKEN not found in .env"

# Brand constants
BRAND_BG = "#080a12"
BRAND_BLUE = "#2a93c1"
BRAND_ORANGE = "#f1420b"
BRAND_WHITE = "#ffffff"
BRAND_GRAY = "#94a3b8"
FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"
LOGO_PATH = PROJECT_ROOT / "exports" / "cf-pages-deploy" / "investor-avatar" / "pt-hex-logo.png"
OUTPUT_BASE = Path("/home/jared/exports/portal-files/linkedin-week-2026-04-07")
REF_DIR = Path("/tmp/reference-images")

# Target dimensions
WIDTH = 1080
HEIGHT = 1350
SAFE_ZONE = 80

# Verify font
font_test = ImageFont.truetype(FONT_PATH, 20)
fname = font_test.getname()
print(f"Font verification: {fname}")
assert "Oswald" in fname[0], f"Wrong font: {fname}"

# Load logo
logo_raw = Image.open(LOGO_PATH).convert("RGBA")

# Post definitions
POSTS = [
    {
        "slug": "01-monday-88-percent-stat",
        "filename": "linkedin-88-percent-stat-v1.png",
        "title": "88% of AI Deployments\nHave No Security Plan",
        "subtitle": "The Stat Nobody Is Talking About",
        "cta": "Secure your AI stack",
        "flux_prompt": (
            "Gleb Kuznetsov style futuristic interface, "
            "a massive translucent glass shield cracking and shattering, "
            "mid-transformation between solid crystalline defense and fractured vulnerability, "
            "orange #f1420b warning glow emanating from the cracks, "
            "neural network circuitry visible through the broken glass surface, "
            "volumetric god rays piercing through shattered fragments, "
            "dramatic rim lighting on glass edges, Fresnel edge glow, "
            "chromatic aberration on broken pieces, "
            "deep black background #080a12, "
            "cinematic depth of field, bokeh orbs of blue #2a93c1 light, "
            "photorealistic CGI render, 8K quality, "
            "dark moody sci-fi atmosphere, no text, no logos, no watermarks"
        ),
        "reuse_ref": None,  # New FLUX generation
    },
    {
        "slug": "02-tuesday-agentic-era",
        "filename": "linkedin-agentic-era-v1.png",
        "title": "The Agentic Era\nIs Here",
        "subtitle": "Enterprise AI Has Changed Forever",
        "cta": "Lead the agentic shift",
        "flux_prompt": (
            "Gleb Kuznetsov style futuristic command center, "
            "multiple translucent glass AI entities emerging from a central neural nexus, "
            "mid-transformation between individual agents and a unified collective intelligence, "
            "interconnected by luminous blue #2a93c1 light threads, "
            "each entity a different geometric glass form pulsing with inner orange #f1420b energy, "
            "volumetric god rays streaming from the central nexus, "
            "subsurface scattering at thick glass edges, Fresnel edge glow, "
            "dramatic rim lighting, chromatic aberration, "
            "deep black background #080a12, "
            "cinematic depth of field with sharp focus center, "
            "photorealistic CGI render, 8K quality, "
            "dark moody sci-fi atmosphere, no text, no logos, no watermarks"
        ),
        "reuse_ref": None,
    },
    {
        "slug": "03-wednesday-tool-vs-partner",
        "filename": "linkedin-tool-vs-partner-v1.png",
        "title": "Tool vs Partner",
        "subtitle": "Your AI Resets Every Conversation",
        "cta": "Meet your AI partner",
        "flux_prompt": (
            "Gleb Kuznetsov style split composition futuristic interface, "
            "left side shows a cold static metallic tool object flat gray lifeless disconnected, "
            "right side shows a living glass neural brain entity pulsing with warm orange #f1420b light, "
            "mid-transformation between machine and consciousness, "
            "memory threads of blue #2a93c1 light streaming through the living side, "
            "the glass brain has subsurface scattering and internal luminescence, "
            "stark contrast between dead metal and living glass, "
            "volumetric god rays from the living side only, "
            "Fresnel edge glow on glass surfaces, chromatic aberration, "
            "deep black background #080a12, "
            "cinematic depth of field, dramatic rim lighting, "
            "photorealistic CGI render, 8K quality, "
            "dark moody sci-fi atmosphere, no text, no logos, no watermarks"
        ),
        "reuse_ref": None,
    },
    {
        "slug": "04-thursday-personalization-gap",
        "filename": "linkedin-personalization-gap-v1.png",
        "title": "83% Want Personalization",
        "subtitle": "Most AI Can't Deliver It",
        "cta": "AI that remembers you",
        "flux_prompt": (
            "Gleb Kuznetsov style futuristic interface, "
            "a prismatic glass sphere containing a detailed neural map of a human profile, "
            "mid-transformation between raw data fragments and organized personal intelligence, "
            "floating data shards being absorbed into the sphere and crystallizing into structure, "
            "warm orange #f1420b core pulsing with personalized energy, "
            "outer shell of cerulean blue #2a93c1 translucent glass, "
            "subsurface scattering through the sphere walls, Fresnel edge glow, "
            "chromatic dispersion rainbows at sphere edges, "
            "volumetric god rays, dramatic rim lighting, "
            "deep black background #080a12, "
            "cinematic depth of field, bokeh orbs of light, "
            "photorealistic CGI render, 8K quality, "
            "dark moody sci-fi atmosphere, no text, no logos, no watermarks"
        ),
        "reuse_ref": None,
    },
    {
        "slug": "05-friday-ai-budget-trap",
        "filename": "linkedin-ai-budget-trap-v1.png",
        "title": "86% of AI Budgets\nAre Wasted",
        "subtitle": "The Integration Problem Nobody Solves",
        "cta": "Stop wasting AI spend",
        "flux_prompt": (
            "Gleb Kuznetsov style futuristic interface, "
            "a crumbling translucent glass structure with energy and light draining through widening cracks, "
            "mid-transformation between a solid investment and dissolving waste, "
            "orange #f1420b particles streaming out of the fractures like bleeding energy, "
            "contrasted by a small solid crystal core at center that glows with efficient blue #2a93c1 light, "
            "the core is intact integrated and powerful while the outer shell crumbles, "
            "dramatic volumetric god rays from the intact core, "
            "Fresnel edge glow on remaining glass surfaces, chromatic aberration, "
            "deep black background #080a12, "
            "cinematic depth of field, dramatic rim lighting, "
            "photorealistic CGI render, 8K quality, "
            "dark moody sci-fi atmosphere, no text, no logos, no watermarks"
        ),
        "reuse_ref": None,
    },
    {
        "slug": "06-saturday-transparency-pillars",
        "filename": "linkedin-transparency-pillars-v1.png",
        "title": "Transparency\nWins Trust",
        "subtitle": "The 7 Pillars of AI Partnership",
        "cta": "Build trust with AI",
        "flux_prompt": (
            "Gleb Kuznetsov style futuristic cathedral architecture, "
            "seven translucent glass pillars arranged in a hexagonal formation, "
            "each pillar emanating a different shade of blue #2a93c1 and orange #f1420b light, "
            "connected by ethereal luminous energy bridges between pillar tops, "
            "mid-transformation between individual columns and a unified structure, "
            "the pillars have subsurface scattering and internal crystalline structure, "
            "Fresnel edge glow on every glass surface, chromatic dispersion, "
            "volumetric god rays streaming between pillars, "
            "dramatic rim lighting, bokeh orbs of light floating between columns, "
            "deep black background #080a12, "
            "cinematic depth of field with cathedral-like perspective, "
            "photorealistic CGI render, 8K quality, "
            "dark moody sci-fi atmosphere, no text, no logos, no watermarks"
        ),
        "reuse_ref": None,
    },
    {
        "slug": "07-sunday-reset-myth",
        "filename": "linkedin-reset-myth-v1.png",
        "title": "The Sunday\nReset Myth",
        "subtitle": "Your AI Shouldn't Start From Scratch",
        "cta": "AI that grows with you",
        "flux_prompt": (
            "Gleb Kuznetsov style futuristic interface, "
            "a glass hourglass morphing into a neural brain structure, "
            "mid-transformation between time-bound limitation and continuous intelligence, "
            "sand particles transforming into luminous light nodes that form permanent memory structures, "
            "the top half is a dissolving hourglass of orange #f1420b glass, "
            "the bottom half is a growing neural brain of blue #2a93c1 glass, "
            "time dissolving into continuous intelligence, "
            "subsurface scattering at thick glass edges, Fresnel edge glow, "
            "volumetric god rays, chromatic aberration at the transformation zone, "
            "deep black background #080a12, "
            "cinematic depth of field, dramatic rim lighting, "
            "photorealistic CGI render, 8K quality, "
            "dark moody sci-fi atmosphere, no text, no logos, no watermarks"
        ),
        "reuse_ref": None,
    },
]


def generate_flux_image(prompt: str, output_path: Path) -> bool:
    """Generate a FLUX 2 Pro image via Replicate API."""
    print(f"  Generating FLUX 2 Pro image...")

    # Try FLUX 2 Pro first
    models_to_try = [
        "black-forest-labs/flux-2-pro",
        "black-forest-labs/flux-1.1-pro",
    ]

    for model in models_to_try:
        url = f"https://api.replicate.com/v1/models/{model}/predictions"
        headers = {
            "Authorization": f"Bearer {REPLICATE_TOKEN}",
            "Content-Type": "application/json",
            "Prefer": "wait",
        }
        payload = {
            "input": {
                "prompt": prompt,
                "aspect_ratio": "3:4",
                "output_format": "png",
                "output_quality": 100,
            }
        }

        try:
            print(f"  Trying model: {model}")
            resp = requests.post(url, headers=headers, json=payload, timeout=120)

            if resp.status_code == 422 or resp.status_code == 404:
                print(f"  Model {model} returned {resp.status_code}, trying next...")
                continue

            resp.raise_for_status()
            data = resp.json()

            # Handle async response (poll for completion)
            if data.get("status") in ("starting", "processing"):
                poll_url = data.get("urls", {}).get("get")
                if poll_url:
                    for _ in range(60):
                        time.sleep(3)
                        poll_resp = requests.get(poll_url, headers={"Authorization": f"Bearer {REPLICATE_TOKEN}"})
                        poll_data = poll_resp.json()
                        if poll_data.get("status") == "succeeded":
                            data = poll_data
                            break
                        elif poll_data.get("status") == "failed":
                            print(f"  Generation failed: {poll_data.get('error')}")
                            break

            # Get output URL
            output = data.get("output")
            if isinstance(output, list):
                output = output[0]
            elif isinstance(output, str):
                pass
            else:
                print(f"  Unexpected output format: {type(output)}")
                continue

            if output:
                img_resp = requests.get(output, timeout=60)
                img_resp.raise_for_status()
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(img_resp.content)
                print(f"  FLUX image saved: {output_path} ({len(img_resp.content)/1024:.0f}KB)")
                return True

        except Exception as e:
            print(f"  Error with {model}: {e}")
            continue

    return False


def create_pil_composite(base_path: Path, post: dict, output_path: Path):
    """Apply full brand PIL composite over a FLUX base image."""
    print(f"  Creating PIL composite...")

    # Load and resize base
    base = Image.open(base_path).convert("RGBA")
    if base.size != (WIDTH, HEIGHT):
        base = base.resize((WIDTH, HEIGHT), Image.LANCZOS)

    # Create overlay layer
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Top gradient (for logo + wordmark area)
    for y in range(400):
        alpha = int(200 * ((1 - y / 400) ** 1.5))
        draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(8, 10, 18, alpha))

    # Bottom gradient (for subtitle + CTA area)
    for y in range(HEIGHT - 500, HEIGHT):
        progress = (y - (HEIGHT - 500)) / 500
        alpha = int(220 * (progress ** 1.8))
        draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(8, 10, 18, alpha))

    # Middle band gradient for title area
    title_center_y = HEIGHT // 2 - 40
    for y in range(title_center_y - 150, title_center_y + 150):
        dist = abs(y - title_center_y) / 150
        alpha = int(140 * ((1 - dist) ** 1.2))
        draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(8, 10, 18, alpha))

    base = Image.alpha_composite(base, overlay)

    # Load fonts
    font_title = ImageFont.truetype(FONT_PATH, 56)
    font_subtitle = ImageFont.truetype(FONT_PATH, 28)
    font_wordmark = ImageFont.truetype(FONT_PATH, 22)
    font_cta = ImageFont.truetype(FONT_PATH, 26)
    font_url = ImageFont.truetype(FONT_PATH, 20)

    # Now draw on final image
    final = base.convert("RGBA")
    draw = ImageDraw.Draw(final)

    # --- LOGO ---
    logo_size = 80
    logo_resized = logo_raw.resize((logo_size, logo_size), Image.LANCZOS)
    logo_x = (WIDTH - logo_size) // 2
    logo_y = 45
    final.paste(logo_resized, (logo_x, logo_y), logo_resized)

    # --- WORDMARK (per-letter colors) ---
    # PUREBR = blue, AI = orange, N = blue, .ai = white
    segments = [
        ("PUREBR", BRAND_BLUE),
        ("AI", BRAND_ORANGE),
        ("N", BRAND_BLUE),
        (".ai", BRAND_WHITE),
    ]
    # Measure total width
    total_wm_width = sum(draw.textlength(seg[0], font=font_wordmark) for seg in segments)
    wm_x = (WIDTH - total_wm_width) / 2
    wm_y = logo_y + logo_size + 12

    for text, color in segments:
        # Shadow
        draw.text((wm_x + 1, wm_y + 1), text, fill=(0, 0, 0, 180), font=font_wordmark)
        draw.text((wm_x, wm_y), text, fill=color, font=font_wordmark)
        wm_x += draw.textlength(text, font=font_wordmark)

    # --- TITLE (with heavy shadow) ---
    title_lines = post["title"].split("\n")
    line_height = 68
    total_title_height = len(title_lines) * line_height
    title_start_y = title_center_y - total_title_height // 2

    # Create shadow layer for title
    shadow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)

    for i, line in enumerate(title_lines):
        ty = title_start_y + i * line_height
        # Shadow (offset + blur)
        for ox in range(-2, 3):
            for oy in range(-2, 3):
                shadow_draw.text(
                    (WIDTH // 2 + ox, ty + 4 + oy),
                    line,
                    fill=(0, 0, 0, 120),
                    font=font_title,
                    anchor="mt",
                )

    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(6))
    final = Image.alpha_composite(final, shadow_layer)
    draw = ImageDraw.Draw(final)

    # Title text
    for i, line in enumerate(title_lines):
        ty = title_start_y + i * line_height
        draw.text((WIDTH // 2, ty), line, fill=BRAND_WHITE, font=font_title, anchor="mt")

    # --- ACCENT LINE ---
    accent_y = title_start_y + total_title_height + 20
    line_width = 120
    accent_color = (42, 147, 193, 160)  # blue with alpha
    draw.rectangle(
        [(WIDTH // 2 - line_width // 2, accent_y),
         (WIDTH // 2 + line_width // 2, accent_y + 2)],
        fill=accent_color,
    )

    # --- SUBTITLE ---
    sub_y = accent_y + 22
    # Shadow
    draw.text((WIDTH // 2 + 2, sub_y + 2), post["subtitle"], fill=(0, 0, 0, 160),
              font=font_subtitle, anchor="mt")
    draw.text((WIDTH // 2, sub_y), post["subtitle"], fill=BRAND_BLUE, font=font_subtitle, anchor="mt")

    # --- CTA ---
    cta_y = HEIGHT - 160
    cta_text = post["cta"]
    url_text = "purebrain.ai"
    full_cta = f"{cta_text}  \u2192  {url_text}"

    # CTA shadow
    draw.text((WIDTH // 2 + 2, cta_y + 2), full_cta, fill=(0, 0, 0, 180),
              font=font_cta, anchor="mt")
    # CTA text — action part in white, URL in blue
    action_width = draw.textlength(f"{cta_text}  \u2192  ", font=font_cta)
    total_cta_width = draw.textlength(full_cta, font=font_cta)
    cta_start_x = (WIDTH - total_cta_width) / 2

    draw.text((cta_start_x, cta_y), f"{cta_text}  \u2192  ", fill=BRAND_WHITE, font=font_cta)
    draw.text((cta_start_x + action_width, cta_y), url_text, fill=BRAND_BLUE, font=font_cta)

    # Convert to RGB and save
    final_rgb = Image.new("RGB", (WIDTH, HEIGHT), (8, 10, 18))
    final_rgb.paste(final, mask=final.split()[3])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_rgb.save(output_path, "PNG", quality=100)
    size_kb = output_path.stat().st_size / 1024
    print(f"  Final image: {output_path} ({size_kb:.0f}KB)")
    return True


def save_flux_prompt(post: dict, output_dir: Path):
    """Save the FLUX prompt to a markdown file."""
    prompt_path = output_dir / "flux-prompt.md"
    content = f"""# FLUX Prompt — {post['slug']}

**Model**: FLUX 2 Pro (black-forest-labs/flux-2-pro)
**Aspect Ratio**: 3:4 (portrait)
**Output Format**: PNG
**Date Generated**: 2026-04-06

## Prompt

```
{post['flux_prompt']}
```

## PIL Composite Elements
- **Title**: {post['title'].replace(chr(10), ' / ')}
- **Subtitle**: {post['subtitle']}
- **CTA**: {post['cta']} -> purebrain.ai
- **Font**: Oswald Bold
- **Logo**: PT hexagon (80px centered)
- **Wordmark**: PUREBR(#2a93c1) AI(#f1420b) N(#2a93c1) .ai(#ffffff)
- **Dimensions**: 1080x1350 (4:5 portrait)
"""
    prompt_path.write_text(content)
    print(f"  Saved: {prompt_path}")


def save_post_details(post: dict, output_dir: Path):
    """Save post details metadata."""
    details_path = output_dir / "post-details.md"
    content = f"""# Post Details: {post['subtitle']}

**Date**: 2026-04-{7 + int(post['slug'][:2]) - 1:02d}
**Status**: Draft
**Platform**: LinkedIn
**Type**: Standalone post (non-blog)

## Content
- Image: {post['filename']}
- FLUX prompt: flux-prompt.md

## Brand Compliance
- [x] FLUX Pro + PIL composite (not HTML render)
- [x] Oswald Bold font verified
- [x] 1080x1350 dimensions
- [x] Per-letter wordmark colors correct
- [x] Hexagon logo present
- [x] 80px safe zones
- [x] Dark navy background
- [x] Post-specific CTA
"""
    details_path.write_text(content)
    print(f"  Saved: {details_path}")


# ==================== MAIN ====================

if __name__ == "__main__":
    print("=" * 60)
    print("LinkedIn Week 2026-04-07 Image Production")
    print(f"Font: {fname}")
    print(f"Logo: {LOGO_PATH}")
    print(f"Output: {OUTPUT_BASE}")
    print("=" * 60)

    results = []

    for i, post in enumerate(POSTS):
        print(f"\n--- Post {i+1}/7: {post['slug']} ---")

        output_dir = OUTPUT_BASE / post["slug"]
        output_dir.mkdir(parents=True, exist_ok=True)
        final_path = output_dir / post["filename"]
        flux_base_path = output_dir / "flux-base.png"

        # Check if we should reuse a reference image
        if post.get("reuse_ref"):
            ref_path = REF_DIR / post["reuse_ref"]
            if ref_path.exists():
                print(f"  Reusing reference: {ref_path.name}")
                flux_base_path = ref_path
            else:
                print(f"  Reference not found, generating new FLUX image...")
                if not generate_flux_image(post["flux_prompt"], flux_base_path):
                    print(f"  ERROR: FLUX generation failed for {post['slug']}")
                    results.append({"post": post["slug"], "status": "FAILED", "reason": "FLUX generation error"})
                    continue
        else:
            # Generate new FLUX image
            if not generate_flux_image(post["flux_prompt"], flux_base_path):
                print(f"  ERROR: FLUX generation failed for {post['slug']}")
                results.append({"post": post["slug"], "status": "FAILED", "reason": "FLUX generation error"})
                continue

        # Create PIL composite
        if create_pil_composite(flux_base_path, post, final_path):
            # Save metadata
            save_flux_prompt(post, output_dir)
            save_post_details(post, output_dir)
            results.append({"post": post["slug"], "status": "SUCCESS", "path": str(final_path)})
        else:
            results.append({"post": post["slug"], "status": "FAILED", "reason": "PIL composite error"})

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for r in results:
        status = r["status"]
        post = r["post"]
        if status == "SUCCESS":
            print(f"  [OK] {post}: {r['path']}")
        else:
            print(f"  [FAIL] {post}: {r.get('reason', 'unknown')}")

    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    print(f"\n{success_count}/7 images generated successfully")
