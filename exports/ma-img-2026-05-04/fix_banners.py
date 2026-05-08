#!/usr/bin/env python3
"""
Fix Resonance banner: add dark scrim behind top-left brand mark + tighten newsletter title.
Reuses the existing FLUX raw.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_batch import (
    BAN_W, BAN_H, FONT_PATH, HEX_ICON_PATH, DARK, BLUE, ORANGE, WHITE,
    measure_wordmark, draw_wordmark, RAW_DIR, PORTAL_DIR
)

from PIL import Image, ImageDraw, ImageFont
import os


def make_banner_option_d_v2(flux_path, title, subtitle, cta, out_path, w=BAN_W, h=BAN_H,
                             title_scale=1.0):
    """Banner Option D v2 — adds dark scrim behind top-left brand mark for legibility.
    title_scale lets us shrink the title for smaller derivatives."""
    canvas = Image.new("RGB", (w, h), DARK)

    # FLUX bg crop-fit
    flux_img = Image.open(flux_path).convert("RGB")
    fw, fh = flux_img.size
    target_ratio = w / h
    src_ratio = fw / fh
    if src_ratio > target_ratio:
        new_w = int(fh * target_ratio)
        x0 = (fw - new_w) // 2
        flux_crop = flux_img.crop((x0, 0, x0 + new_w, fh))
    else:
        new_h = int(fw / target_ratio)
        y0 = (fh - new_h) // 2
        flux_crop = flux_img.crop((0, y0, fw, y0 + new_h))
    flux_img = flux_crop.resize((w, h), Image.LANCZOS)
    canvas.paste(flux_img, (0, 0))

    # Top-left scrim — solid alpha box with vertical fade-out for brand mark legibility
    scrim_h = int(170 * (h / 1260))
    scrim_w_full = int(560 * (w / 2400))
    scrim = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    # Solid darkened pill: fully opaque in left chunk, fade rightward and downward
    for y in range(0, scrim_h):
        progress = y / scrim_h
        # Top 70% fully opaque, then fade
        if progress < 0.65:
            alpha_y = 230
        else:
            alpha_y = int(230 * ((1 - progress) / 0.35) ** 1.4)
        sd.rectangle([(0, y), (scrim_w_full, y + 1)], fill=(8, 10, 18, alpha_y))
    # Soft right edge fade — overlay a narrow alpha-graded band on the right side of the scrim
    fade_w = int(180 * (w / 2400))
    fade_start = scrim_w_full - fade_w
    for x in range(fade_start, scrim_w_full):
        x_progress = (x - fade_start) / fade_w
        # Use alpha to subtract — actually re-paint with reduced alpha
        for y in range(0, scrim_h):
            y_progress = y / scrim_h
            if y_progress < 0.65:
                base_alpha = 230
            else:
                base_alpha = int(230 * ((1 - y_progress) / 0.35) ** 1.4)
            new_alpha = int(base_alpha * (1 - x_progress) ** 1.4)
            sd.point((x, y), fill=(8, 10, 18, new_alpha))

    # Bottom gradient overlay (Option D primary)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    grad_start = int(h * 0.40)
    for y in range(grad_start, h):
        progress = (y - grad_start) / (h - grad_start)
        alpha = int(225 * (progress ** 1.4))
        od.rectangle([(0, y), (w, y + 1)], fill=(8, 10, 18, alpha))

    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba = Image.alpha_composite(canvas_rgba, scrim)
    canvas_rgba = Image.alpha_composite(canvas_rgba, overlay)
    canvas = canvas_rgba.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # --- Top-left brand mark ---
    icon_size = max(60, int(80 * (w / 2400)))
    hex_icon = Image.open(HEX_ICON_PATH).convert("RGBA").resize((icon_size, icon_size), Image.LANCZOS)
    icon_x = int(60 * (w / 2400))
    icon_y = int(50 * (h / 1260))
    canvas.paste(hex_icon, (icon_x, icon_y), hex_icon)

    wm_size = max(32, int(46 * (w / 2400)))
    font_top_wm = ImageFont.truetype(FONT_PATH, wm_size)
    wm_w, wm_h, wm_top_off = measure_wordmark(draw, font_top_wm)
    wm_x = icon_x + icon_size + int(18 * (w / 2400))
    wm_y = icon_y + (icon_size // 2) - (wm_h // 2) - wm_top_off
    draw_wordmark(draw, wm_x, wm_y, font_top_wm)

    # --- Bottom title block ---
    title_size = max(80, int(180 * (w / 2400) * title_scale))
    font_title = ImageFont.truetype(FONT_PATH, title_size)

    sub_size = max(24, int(48 * (w / 2400)))
    font_sub = ImageFont.truetype(FONT_PATH, sub_size)

    cta_size = max(22, int(40 * (w / 2400)))
    font_cta_big = ImageFont.truetype(FONT_PATH, cta_size)

    pad_x = int(80 * (w / 2400))
    bottom_pad = int(80 * (h / 1260))

    cta_bbox = draw.textbbox((0, 0), cta, font=font_cta_big)
    cta_w_px = cta_bbox[2] - cta_bbox[0]
    cta_h_px = cta_bbox[3] - cta_bbox[1]
    cta_top_off = cta_bbox[1]
    cta_x = w - pad_x - cta_w_px
    cta_y = h - bottom_pad - cta_h_px - cta_top_off
    draw.text((cta_x, cta_y), cta, fill=ORANGE, font=font_cta_big)

    sub_bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    sub_w_px = sub_bbox[2] - sub_bbox[0]
    sub_h_px = sub_bbox[3] - sub_bbox[1]
    sub_top_off = sub_bbox[1]
    sub_y = cta_y + cta_top_off - int(28 * (h / 1260)) - sub_h_px - sub_top_off
    draw.text((pad_x, sub_y), subtitle, fill=(220, 230, 240), font=font_sub)

    t_bbox = draw.textbbox((0, 0), title, font=font_title)
    t_w_px = t_bbox[2] - t_bbox[0]
    t_h_px = t_bbox[3] - t_bbox[1]
    t_top_off = t_bbox[1]
    t_y = sub_y + sub_top_off - int(40 * (h / 1260)) - t_h_px - t_top_off

    # If title is wider than available, shrink iteratively
    avail = w - pad_x * 2
    while t_w_px > avail and title_size > 60:
        title_size -= 4
        font_title = ImageFont.truetype(FONT_PATH, title_size)
        t_bbox = draw.textbbox((0, 0), title, font=font_title)
        t_w_px = t_bbox[2] - t_bbox[0]
        t_h_px = t_bbox[3] - t_bbox[1]
        t_top_off = t_bbox[1]
        t_y = sub_y + sub_top_off - int(40 * (h / 1260)) - t_h_px - t_top_off

    for dx in range(-4, 5):
        for dy in range(-4, 5):
            if dx * dx + dy * dy <= 16:
                draw.text((pad_x + dx, t_y + dy), title, fill=DARK, font=font_title)
    draw.text((pad_x, t_y), title, fill=WHITE, font=font_title)

    canvas.save(out_path, "PNG", optimize=True)
    print(f"  [DONE] {out_path} ({os.path.getsize(out_path)//1024}KB)")
    return out_path


def main():
    flux_path = RAW_DIR / "resonance-banner-flux-raw.png"
    title = "RESONANCE BEATS REACH"
    subtitle = "Pure Marketing Group engineers resonance, not attention."
    cta = "puremarketing.ai  ->"

    print("Regenerating banner 2400x1260 with brand-mark scrim...")
    make_banner_option_d_v2(
        flux_path, title, subtitle, cta,
        PORTAL_DIR / "MA-IMG-2026-05-04-POST3-RESONANCE-BANNER.png",
        w=BAN_W, h=BAN_H, title_scale=1.0,
    )

    print("Regenerating newsletter 1200x630 with auto-shrink title...")
    make_banner_option_d_v2(
        flux_path, title, subtitle, cta,
        PORTAL_DIR / "MA-IMG-2026-05-04-POST3-RESONANCE-NEWSLETTER-1200x630.png",
        w=1200, h=630, title_scale=0.85,
    )


if __name__ == "__main__":
    main()
