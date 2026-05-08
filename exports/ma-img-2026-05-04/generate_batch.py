#!/usr/bin/env python3
"""
MA# Sunday Batch — Monday May 4 LinkedIn Drop
3 images: Memory Tax (standalone v4), 72-Hour Default (standalone v4), Resonance Beats Reach (banner Option D)

Format reference: exports/content-batch-images-may5/generate_5_banners.py (v4 standalone)
Banner Option D = bottom gradient overlay over FLUX, title on bottom third
"""

import os
import sys
import time
import json
import urllib.request
from pathlib import Path

import replicate
from PIL import Image, ImageDraw, ImageFont

# --- Paths/Config ---
PROJECT_ROOT = Path("/home/jared/projects/AI-CIV/aether")
WORK_DIR = PROJECT_ROOT / "exports" / "ma-img-2026-05-04"
RAW_DIR = WORK_DIR / "flux-raw"
PORTAL_DIR = Path("/home/jared/exports/portal-files")

FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"
HEX_ICON_PATH = str(PROJECT_ROOT / "assets/pt-hex-icon-official.png")

DARK = "#080a12"
BLUE = "#2a93c1"
ORANGE = "#f1420b"
WHITE = "#ffffff"

# Standalone v4 (1080x1350)
STD_W, STD_H = 1080, 1350
STD_TOP_BAR = 140
STD_BOTTOM_BAR = 90
STD_ACCENT = 2

# Banner Option D (2400x1260) - bottom gradient overlay
BAN_W, BAN_H = 2400, 1260

# --- Load env ---
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v

if not os.environ.get("REPLICATE_API_TOKEN"):
    sys.exit("ERROR: REPLICATE_API_TOKEN not in env")

RAW_DIR.mkdir(parents=True, exist_ok=True)
WORK_DIR.mkdir(parents=True, exist_ok=True)
PORTAL_DIR.mkdir(parents=True, exist_ok=True)


def generate_flux(prompt, slug, width=1080, height=1080):
    """FLUX 1.1 Pro generation."""
    raw_path = RAW_DIR / f"{slug}-flux-raw.png"
    if raw_path.exists() and raw_path.stat().st_size > 50_000:
        print(f"  [SKIP] FLUX raw exists: {slug} ({raw_path.stat().st_size//1024}KB)")
        return raw_path

    print(f"  [FLUX] {slug} {width}x{height}...")
    output = replicate.run(
        "black-forest-labs/flux-1.1-pro",
        input={
            "prompt": prompt,
            "width": width,
            "height": height,
            "output_format": "png",
            "output_quality": 95,
            "safety_tolerance": 2,
        },
    )

    try:
        img_bytes = output.read()
    except AttributeError:
        url = str(output)
        img_bytes = urllib.request.urlopen(url).read()

    raw_path.write_bytes(img_bytes)
    print(f"  [FLUX] Saved: {raw_path} ({len(img_bytes)//1024}KB)")
    return raw_path


def draw_wordmark(draw, x, y, font, parts=None):
    """Draw PUREBRAIN.AI wordmark with brand color split."""
    if parts is None:
        parts = [("PUREBR", BLUE), ("AI", ORANGE), ("N", BLUE), (".AI", WHITE)]
    cx = x
    for txt, color in parts:
        draw.text((cx, y), txt, fill=color, font=font)
        bbox = draw.textbbox((0, 0), txt, font=font)
        cx += bbox[2] - bbox[0]
    return cx - x  # total width drawn


def measure_wordmark(draw, font, text="PUREBRAIN.AI"):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1], bbox[1]


def make_standalone_v4(flux_path, title_text, cta_text, out_path):
    """Standalone v4: top bar (hex+wordmark+title) / FLUX / bottom bar (wordmark + orange CTA)."""
    canvas = Image.new("RGB", (STD_W, STD_H), DARK)

    # FLUX bg fills middle
    flux_img = Image.open(flux_path).convert("RGB").resize((STD_W, STD_W), Image.LANCZOS)
    img_y_start = STD_TOP_BAR + STD_ACCENT
    img_area_h = STD_H - STD_TOP_BAR - STD_ACCENT - STD_ACCENT - STD_BOTTOM_BAR
    flux_y = img_y_start + (img_area_h - STD_W) // 2
    canvas.paste(flux_img, (0, flux_y))

    draw = ImageDraw.Draw(canvas)

    # Top bar
    draw.rectangle([(0, 0), (STD_W, STD_TOP_BAR)], fill=DARK)

    # Hex icon
    hex_icon = Image.open(HEX_ICON_PATH).convert("RGBA").resize((72, 72), Image.LANCZOS)

    font_wm_top = ImageFont.truetype(FONT_PATH, 38)
    font_title_top = ImageFont.truetype(FONT_PATH, 38)
    font_title_overlay = ImageFont.truetype(FONT_PATH, 90)
    font_bot_wm = ImageFont.truetype(FONT_PATH, 26)
    font_cta = ImageFont.truetype(FONT_PATH, 26)

    # Top bar layout: [icon] [PUREBRAIN.AI] | [TITLE] right-aligned
    icon_x = 36
    icon_y = (STD_TOP_BAR - 72) // 2
    canvas.paste(hex_icon, (icon_x, icon_y), hex_icon)

    # PUREBRAIN.AI right of icon
    wm_w, wm_h, wm_top_off = measure_wordmark(draw, font_wm_top)
    wm_x = icon_x + 72 + 14
    wm_y = (STD_TOP_BAR // 2) - wm_top_off - wm_h // 2
    draw_wordmark(draw, wm_x, wm_y, font_wm_top)

    # Vertical separator + title text right side
    sep_x = wm_x + wm_w + 24
    draw.rectangle([(sep_x, 38), (sep_x + 2, STD_TOP_BAR - 38)], fill=BLUE)

    # Title in top bar (right of separator)
    title_top_x = sep_x + 18
    t_bbox = draw.textbbox((0, 0), title_text, font=font_title_top)
    t_h = t_bbox[3] - t_bbox[1]
    t_top_off = t_bbox[1]
    title_top_y = (STD_TOP_BAR // 2) - t_top_off - t_h // 2
    draw.text((title_top_x, title_top_y), title_text, fill=WHITE, font=font_title_top)

    # Blue accent line (top)
    accent1_y = STD_TOP_BAR
    draw.rectangle([(0, accent1_y), (STD_W, accent1_y + STD_ACCENT)], fill=BLUE)

    # Title overlay on FLUX (centered, large) — gradient behind
    title_lines = title_text.split("\n") if "\n" in title_text else [title_text]
    line_data = []
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=font_title_overlay)
        line_data.append({"text": line, "w": bbox[2] - bbox[0], "h": bbox[3] - bbox[1], "top": bbox[1]})
    spacing = 16
    total_h = sum(d["h"] for d in line_data) + spacing * (len(line_data) - 1)
    title_center_y = img_y_start + img_area_h // 2
    title_start_y = title_center_y - total_h // 2

    # Soft gradient behind title (radial vertical fade)
    grad_pad = 80
    grad_top = max(img_y_start, title_start_y - grad_pad)
    grad_bot = min(img_y_start + img_area_h, title_start_y + total_h + grad_pad)

    overlay = Image.new("RGBA", (STD_W, STD_H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(grad_top, grad_bot):
        center = (grad_top + grad_bot) // 2
        dist = abs(y - center) / ((grad_bot - grad_top) / 2 + 1)
        alpha = int(190 * (1 - dist * dist))
        alpha = max(0, min(190, alpha))
        od.rectangle([(0, y), (STD_W, y + 1)], fill=(8, 10, 18, alpha))

    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba = Image.alpha_composite(canvas_rgba, overlay)
    canvas = canvas_rgba.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # Draw title with stroke
    cur_y = title_start_y
    for d in line_data:
        lx = (STD_W - d["w"]) // 2
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                if dx * dx + dy * dy <= 16:
                    draw.text((lx + dx, cur_y + dy), d["text"], fill=DARK, font=font_title_overlay)
        draw.text((lx, cur_y), d["text"], fill=WHITE, font=font_title_overlay)
        cur_y += d["h"] + spacing

    # Bottom blue accent
    accent2_y = STD_H - STD_BOTTOM_BAR - STD_ACCENT
    draw.rectangle([(0, accent2_y), (STD_W, accent2_y + STD_ACCENT)], fill=BLUE)

    # Bottom bar
    bot_y = STD_H - STD_BOTTOM_BAR
    draw.rectangle([(0, bot_y), (STD_W, STD_H)], fill=DARK)

    # Bottom wordmark left
    bwm_w, bwm_h, bwm_top = measure_wordmark(draw, font_bot_wm)
    bwm_x = 40
    bwm_y = bot_y + (STD_BOTTOM_BAR // 2) - bwm_top - bwm_h // 2
    draw_wordmark(draw, bwm_x, bwm_y, font_bot_wm)

    # CTA right (orange)
    cta_bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
    cta_w = cta_bbox[2] - cta_bbox[0]
    cta_h = cta_bbox[3] - cta_bbox[1]
    cta_top_off = cta_bbox[1]
    cta_x = STD_W - 40 - cta_w
    cta_y = bot_y + (STD_BOTTOM_BAR // 2) - cta_top_off - cta_h // 2
    draw.text((cta_x, cta_y), cta_text, fill=ORANGE, font=font_cta)

    canvas.save(out_path, "PNG", optimize=True)
    print(f"  [DONE] {out_path} ({os.path.getsize(out_path)//1024}KB)")
    return out_path


def make_banner_option_d(flux_path, title, subtitle, cta, out_path, w=BAN_W, h=BAN_H):
    """Banner Option D: FLUX bg fills frame, bottom gradient overlay holds title/subtitle/CTA.
    Top-left corner: hex icon + wordmark."""
    canvas = Image.new("RGB", (w, h), DARK)

    # FLUX background — full coverage, cropped to fit aspect
    flux_img = Image.open(flux_path).convert("RGB")
    fw, fh = flux_img.size
    target_ratio = w / h
    src_ratio = fw / fh
    if src_ratio > target_ratio:
        # Source wider → crop sides
        new_w = int(fh * target_ratio)
        x0 = (fw - new_w) // 2
        flux_crop = flux_img.crop((x0, 0, x0 + new_w, fh))
    else:
        # Source taller → crop top/bottom
        new_h = int(fw / target_ratio)
        y0 = (fh - new_h) // 2
        flux_crop = flux_img.crop((0, y0, fw, y0 + new_h))
    flux_img = flux_crop.resize((w, h), Image.LANCZOS)
    canvas.paste(flux_img, (0, 0))

    # --- Bottom gradient overlay (Option D primary) ---
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    grad_start = int(h * 0.40)  # gradient starts at 40% down
    grad_end = h
    for y in range(grad_start, grad_end):
        progress = (y - grad_start) / (grad_end - grad_start)
        # Ease-in: alpha grows from 0 to ~225 by bottom
        alpha = int(225 * (progress ** 1.4))
        od.rectangle([(0, y), (w, y + 1)], fill=(8, 10, 18, alpha))

    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba = Image.alpha_composite(canvas_rgba, overlay)
    canvas = canvas_rgba.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # --- Top-left brand mark ---
    icon_size = int(80 * (w / 2400))  # scale for banner size
    icon_size = max(60, icon_size)
    hex_icon = Image.open(HEX_ICON_PATH).convert("RGBA").resize((icon_size, icon_size), Image.LANCZOS)
    icon_x = int(60 * (w / 2400))
    icon_y = int(50 * (h / 1260))
    canvas.paste(hex_icon, (icon_x, icon_y), hex_icon)

    # Wordmark next to icon
    wm_size = int(46 * (w / 2400))
    wm_size = max(32, wm_size)
    font_top_wm = ImageFont.truetype(FONT_PATH, wm_size)
    wm_w, wm_h, wm_top_off = measure_wordmark(draw, font_top_wm)
    wm_x = icon_x + icon_size + int(18 * (w / 2400))
    wm_y = icon_y + (icon_size // 2) - (wm_h // 2) - wm_top_off
    draw_wordmark(draw, wm_x, wm_y, font_top_wm)

    # --- Title (bottom area) ---
    title_size = int(180 * (w / 2400))
    title_size = max(110, title_size)
    font_title = ImageFont.truetype(FONT_PATH, title_size)

    sub_size = int(48 * (w / 2400))
    sub_size = max(28, sub_size)
    font_sub = ImageFont.truetype(FONT_PATH, sub_size)

    cta_size = int(40 * (w / 2400))
    cta_size = max(24, cta_size)
    font_cta_big = ImageFont.truetype(FONT_PATH, cta_size)

    pad_x = int(80 * (w / 2400))
    bottom_pad = int(80 * (h / 1260))

    # CTA at very bottom-right
    cta_bbox = draw.textbbox((0, 0), cta, font=font_cta_big)
    cta_w_px = cta_bbox[2] - cta_bbox[0]
    cta_h_px = cta_bbox[3] - cta_bbox[1]
    cta_top_off = cta_bbox[1]
    cta_x = w - pad_x - cta_w_px
    cta_y = h - bottom_pad - cta_h_px - cta_top_off
    draw.text((cta_x, cta_y), cta, fill=ORANGE, font=font_cta_big)

    # Subtitle above CTA
    sub_bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    sub_w_px = sub_bbox[2] - sub_bbox[0]
    sub_h_px = sub_bbox[3] - sub_bbox[1]
    sub_top_off = sub_bbox[1]
    sub_y = cta_y + cta_top_off - int(28 * (h / 1260)) - sub_h_px - sub_top_off
    draw.text((pad_x, sub_y), subtitle, fill=(220, 230, 240), font=font_sub)

    # Title above subtitle
    t_bbox = draw.textbbox((0, 0), title, font=font_title)
    t_w_px = t_bbox[2] - t_bbox[0]
    t_h_px = t_bbox[3] - t_bbox[1]
    t_top_off = t_bbox[1]
    t_y = sub_y + sub_top_off - int(40 * (h / 1260)) - t_h_px - t_top_off

    # Title with stroke
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            if dx * dx + dy * dy <= 16:
                draw.text((pad_x + dx, t_y + dy), title, fill=DARK, font=font_title)
    draw.text((pad_x, t_y), title, fill=WHITE, font=font_title)

    canvas.save(out_path, "PNG", optimize=True)
    print(f"  [DONE] {out_path} ({os.path.getsize(out_path)//1024}KB)")
    return out_path


# --- Image specs ---
SPECS = [
    {
        "slug": "memory-tax",
        "kind": "standalone",
        "title": "THE MEMORY TAX",
        "cta": "MEET YOUR AI PARTNER  ->",
        "flux_prompt": (
            "Cinematic editorial product photograph of a translucent paper invoice or receipt floating in deep "
            "dark space, the printed line items dissolving into glowing binary code (zeros and ones) at the edges, "
            "soft cyan blue light at color hex 2a93c1 illuminating from below, dark void background hex 080a12, "
            "shallow depth of field, dust particles, premium magazine aesthetic, photorealistic, 8k, "
            "no text on receipt readable, no logos, no watermarks, no words, abstract dissolution, "
            "negative space dominant, cinematic lighting"
        ),
        "out": PORTAL_DIR / "MA-IMG-2026-05-04-POST1-MEMORY-TAX.png",
    },
    {
        "slug": "72hr-default",
        "kind": "standalone",
        "title": "THE 72-HOUR DEFAULT",
        "cta": "SHIP THE DEFAULT  ->",
        "flux_prompt": (
            "Cinematic close-up macro photograph of a vintage brass mechanical rotary timer or stopwatch face "
            "fixed at 72 hours, brushed metal dial with patina, soft warm orange glow at color hex f1420b emanating "
            "from the dial face and gears, deep dark background hex 080a12, shallow depth of field with extreme bokeh, "
            "dust motes catching light, premium product photography, photorealistic, 8k commercial quality, "
            "no text readable, no brand markings, no logos, no watermarks, "
            "negative space dominant, dramatic side lighting, moody"
        ),
        "out": PORTAL_DIR / "MA-IMG-2026-05-04-POST2-72HR-DEFAULT.png",
    },
    {
        "slug": "resonance-banner",
        "kind": "banner",
        "title": "RESONANCE BEATS REACH",
        "subtitle": "Pure Marketing Group engineers resonance, not attention.",
        "cta": "puremarketing.ai  ->",
        "flux_prompt": (
            "Cinematic split composition wide horizontal banner: left third shows scattered chaotic dim grey "
            "light particles dispersing into static noise and dust, right two-thirds shows a single elegant "
            "metallic tuning fork resonating with clean glowing concentric rings emanating outward in cerulean "
            "blue at color hex 2a93c1, with subtle warm orange accent at color hex f1420b on the tuning fork tips, "
            "deep dark background hex 080a12, photorealistic premium commercial photography, manifesto aesthetic, "
            "shallow depth of field, dramatic side lighting, 8k high resolution, "
            "no text, no words, no letters, no logos, no watermarks, "
            "negative space dominant, sound wave physics visualization"
        ),
        "out": PORTAL_DIR / "MA-IMG-2026-05-04-POST3-RESONANCE-BANNER.png",
        "newsletter_out": PORTAL_DIR / "MA-IMG-2026-05-04-POST3-RESONANCE-NEWSLETTER-1200x630.png",
    },
]


def main():
    print("=" * 70)
    print("MA# Sunday Batch — Monday May 4 LinkedIn Drop")
    print("=" * 70)

    results = []

    for i, spec in enumerate(SPECS):
        print(f"\n[{i+1}/{len(SPECS)}] {spec['slug']} ({spec['kind']})")

        # Generate FLUX
        if spec["kind"] == "banner":
            # Generate at higher native resolution then crop. FLUX 1.1 Pro supports up to 1440x1440 region;
            # Use 1440x1080 wide and we'll upscale-crop.
            flux_path = generate_flux(spec["flux_prompt"], spec["slug"], width=1440, height=1080)
        else:
            flux_path = generate_flux(spec["flux_prompt"], spec["slug"], width=1080, height=1080)

        # Rate limit between FLUX calls
        if i < len(SPECS) - 1:
            print("  [WAIT] 12s rate limit...")
            time.sleep(12)

        # Compose
        if spec["kind"] == "standalone":
            out = make_standalone_v4(flux_path, spec["title"], spec["cta"], spec["out"])
            dim = f"{STD_W}x{STD_H}"
        else:
            out = make_banner_option_d(
                flux_path, spec["title"], spec["subtitle"], spec["cta"], spec["out"],
                w=BAN_W, h=BAN_H,
            )
            dim = f"{BAN_W}x{BAN_H}"

            # Newsletter derivative 1200x630
            print(f"  [+] Newsletter derivative...")
            nl_out = make_banner_option_d(
                flux_path, spec["title"], spec["subtitle"], spec["cta"],
                spec["newsletter_out"],
                w=1200, h=630,
            )
            results.append({
                "slug": spec["slug"] + "-newsletter",
                "kind": "newsletter",
                "path": str(nl_out),
                "dimensions": "1200x630",
                "source": "generated",
            })

        results.append({
            "slug": spec["slug"],
            "kind": spec["kind"],
            "path": str(out),
            "dimensions": dim,
            "source": "generated",
        })

    print("\n" + "=" * 70)
    print("BATCH COMPLETE")
    print("=" * 70)
    for r in results:
        sz = os.path.getsize(r["path"]) // 1024
        print(f"  {r['slug']:35} {r['dimensions']:10} {sz}KB  {r['path']}")

    (WORK_DIR / "results.json").write_text(json.dumps(results, indent=2))
    print(f"\nResults: {WORK_DIR / 'results.json'}")


if __name__ == "__main__":
    main()
