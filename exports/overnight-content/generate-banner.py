#!/usr/bin/env python3
"""
Banner generator: "Why Your AI Investment Isn't Paying Off"
Visual concept: Leaking investment funnel metaphor
Canvas: 1456x816, safe zone: 182px margins
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Config ─────────────────────────────────────────────────────────────────────
W, H = 1456, 816
SAFE_X1, SAFE_X2 = 182, 1274
SAFE_Y1, SAFE_Y2 = 102, 714

ORANGE   = (241, 66, 11)
BLUE     = (42, 147, 193)
WHITE    = (255, 255, 255)
DARK_BG1 = (8, 10, 18)
DARK_BG2 = (13, 18, 32)
HEX_MESH = (26, 41, 64)

FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"
ICON_PATH = "/home/jared/projects/AI-CIV/aether/docs/assets/logos/purebrain-icon.png"
OUT_PATH  = "/home/jared/projects/AI-CIV/aether/exports/overnight-content/why-your-ai-investment-isnt-paying-off-banner.png"


# ── Helpers ────────────────────────────────────────────────────────────────────
def load_font(size):
    return ImageFont.truetype(FONT_PATH, size)


def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def draw_glow(img, x, y, w, h, color, radius=40, alpha_max=80):
    """Paint a soft radial glow rectangle on an RGBA overlay."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    steps = 10
    for i in range(steps):
        t = i / steps
        spread = int(radius * (1 - t))
        a = int(alpha_max * (1 - t))
        ld.rectangle(
            [x - spread, y - spread, x + w + spread, y + h + spread],
            fill=(*color, a)
        )
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=radius // 2))
    img = Image.alpha_composite(img, blurred)
    return img


def draw_line_glow(img, pts, color, max_width=18, passes=6):
    """Draw a glowing polyline."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for i in range(passes, 0, -1):
        t = i / passes
        w = max(1, int(max_width * t))
        a = int(120 * (1 - t * 0.7))
        ld.line(pts, fill=(*color, a), width=w)
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=3))
    # crisp bright core on top
    ld2 = ImageDraw.Draw(blurred)
    ld2.line(pts, fill=(*color, 255), width=2)
    img = Image.alpha_composite(img, blurred)
    return img


# ── Background gradient ─────────────────────────────────────────────────────────
def make_background():
    img = Image.new("RGBA", (W, H), DARK_BG1)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(DARK_BG1[0] + (DARK_BG2[0] - DARK_BG1[0]) * t)
        g = int(DARK_BG1[1] + (DARK_BG2[1] - DARK_BG1[1]) * t)
        b = int(DARK_BG1[2] + (DARK_BG2[2] - DARK_BG1[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
    return img


# ── Hexagonal mesh overlay ───────────────────────────────────────────────────────
def draw_hex_mesh(img, opacity=22):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    hex_r = 36  # outer radius
    col_w = hex_r * math.sqrt(3)
    row_h = hex_r * 1.5
    cols = int(W / col_w) + 3
    rows = int(H / row_h) + 3
    for row in range(-1, rows):
        for col in range(-1, cols):
            cx = col * col_w + (hex_r * math.sqrt(3) / 2 if row % 2 else 0)
            cy = row * row_h
            pts = []
            for angle_deg in range(0, 360, 60):
                angle_rad = math.radians(angle_deg + 30)
                px = cx + hex_r * math.cos(angle_rad)
                py = cy + hex_r * math.sin(angle_rad)
                pts.append((px, py))
            ld.polygon(pts, outline=(*HEX_MESH, opacity), fill=None)
    img = Image.alpha_composite(img, layer)
    return img


# ── Funnel structure ──────────────────────────────────────────────────────────────
def draw_funnel(img):
    """
    Funnel centered horizontally, occupying lower 55% of safe zone.
    Top (wide mouth): data/money flows IN (blue)
    Sides crack out (orange leaks)
    Bottom (narrow output): tiny ROI stream (blue)
    """
    # Funnel geometry — positioned in lower 55% so text has breathing room
    cx = W // 2
    funnel_top_y   = int(H * 0.475)   # moved down from 0.38 — clear of subline
    funnel_bot_y   = int(H * 0.875)   # extends a bit below safe zone for depth
    funnel_top_hw  = 310   # slightly wider mouth for visual impact
    funnel_bot_hw  = 28    # half-width at bottom (narrow ROI stream)
    # Funnel outline polygon (trapezoid)
    f_tl = (cx - funnel_top_hw, funnel_top_y)
    f_tr = (cx + funnel_top_hw, funnel_top_y)
    f_br = (cx + funnel_bot_hw, funnel_bot_y)
    f_bl = (cx - funnel_bot_hw, funnel_bot_y)

    # ── Draw dark funnel interior ──
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.polygon([f_tl, f_tr, f_br, f_bl], fill=(12, 16, 28, 200))
    img = Image.alpha_composite(img, layer)

    # ── Funnel border glow (blue edges — the "correct" path) ──
    edge_pts_left  = [f_tl, f_bl]
    edge_pts_right = [f_tr, f_br]
    img = draw_line_glow(img, edge_pts_left,  BLUE,  max_width=10, passes=5)
    img = draw_line_glow(img, edge_pts_right, BLUE,  max_width=10, passes=5)
    # Top opening
    img = draw_line_glow(img, [f_tl, f_tr],  BLUE,  max_width=8, passes=4)
    # Bottom exit
    img = draw_line_glow(img, [f_bl, f_br],  BLUE,  max_width=6, passes=4)

    # ── Blue particles flowing IN at top — just above the funnel mouth ──
    layer2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld2 = ImageDraw.Draw(layer2)
    flow_in_positions = [
        (cx - 220, funnel_top_y - 28),
        (cx - 130, funnel_top_y - 38),
        (cx - 40,  funnel_top_y - 44),
        (cx + 40,  funnel_top_y - 44),
        (cx + 130, funnel_top_y - 38),
        (cx + 220, funnel_top_y - 28),
        (cx - 80,  funnel_top_y - 18),
        (cx + 80,  funnel_top_y - 18),
        (cx,       funnel_top_y - 12),
    ]
    for (fx, fy) in flow_in_positions:
        r = 5 + (abs(fx - cx) % 4)
        ld2.ellipse([fx - r, fy - r, fx + r, fy + r], fill=(*BLUE, 210))
        for spread in [14, 9, 5]:
            a = 25 + (14 - spread) * 9
            ld2.ellipse([fx-spread, fy-spread, fx+spread, fy+spread], fill=(*BLUE, a))
    # flow arrows — downward chevrons pointing into funnel
    for fx in [cx - 190, cx - 80, cx, cx + 80, cx + 190]:
        fy = funnel_top_y - 62
        pts = [(fx - 9, fy - 10), (fx, fy + 5), (fx + 9, fy - 10)]
        ld2.line(pts, fill=(*BLUE, 170), width=2)
    blurred2 = layer2.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.alpha_composite(img, blurred2)

    # ── Cracks in funnel sides (orange leaks) ──
    # Left side crack — 3 leak jets
    crack_positions_left = [
        (0.30, 0.35),  # (fraction down funnel, fraction of side-length)
        (0.50, 0.28),
        (0.70, 0.20),
    ]
    for (fd, fw_frac) in crack_positions_left:
        crack_y = int(funnel_top_y + fd * (funnel_bot_y - funnel_top_y))
        crack_x_inner = int(cx - funnel_top_hw + fd * (funnel_top_hw - funnel_bot_hw))
        crack_x_outer = crack_x_inner - int(fw_frac * funnel_top_hw * 1.1)
        # jagged crack line
        jag_pts = []
        n_jags = 6
        for i in range(n_jags + 1):
            t = i / n_jags
            jx = int(crack_x_inner + (crack_x_outer - crack_x_inner) * t)
            jy = int(crack_y + ((-1) ** i) * 6 * (1 - t))
            jag_pts.append((jx, jy))
        img = draw_line_glow(img, jag_pts, ORANGE, max_width=14, passes=7)

        # orange drip droplets beyond crack
        for k in range(4):
            dx = crack_x_outer - 10 - k * 12
            dy = crack_y + (k * 8) - 10
            r2 = max(2, 5 - k)
            layer3 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld3 = ImageDraw.Draw(layer3)
            ld3.ellipse([dx-r2, dy-r2, dx+r2, dy+r2], fill=(*ORANGE, 200 - k*40))
            img = Image.alpha_composite(img, layer3)

    # Right side crack — 3 leak jets (mirror)
    crack_positions_right = [
        (0.25, 0.38),
        (0.45, 0.30),
        (0.65, 0.22),
    ]
    for (fd, fw_frac) in crack_positions_right:
        crack_y = int(funnel_top_y + fd * (funnel_bot_y - funnel_top_y))
        crack_x_inner = int(cx + funnel_top_hw - fd * (funnel_top_hw - funnel_bot_hw))
        crack_x_outer = crack_x_inner + int(fw_frac * funnel_top_hw * 1.1)
        jag_pts = []
        n_jags = 6
        for i in range(n_jags + 1):
            t = i / n_jags
            jx = int(crack_x_inner + (crack_x_outer - crack_x_inner) * t)
            jy = int(crack_y + ((-1) ** i) * 6 * (1 - t))
            jag_pts.append((jx, jy))
        img = draw_line_glow(img, jag_pts, ORANGE, max_width=14, passes=7)
        for k in range(4):
            dx = crack_x_outer + 10 + k * 12
            dy = crack_y + (k * 8) - 10
            r2 = max(2, 5 - k)
            layer4 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld4 = ImageDraw.Draw(layer4)
            ld4.ellipse([dx-r2, dy-r2, dx+r2, dy+r2], fill=(*ORANGE, 200 - k*40))
            img = Image.alpha_composite(img, layer4)

    # ── ROI stream at bottom — narrow blue flow ──
    roi_stream_top = funnel_bot_y
    roi_stream_bot = funnel_bot_y + 54
    roi_stream_pts = [
        (cx - funnel_bot_hw, roi_stream_top),
        (cx - funnel_bot_hw - 2, roi_stream_bot),
        (cx + funnel_bot_hw + 2, roi_stream_bot),
        (cx + funnel_bot_hw, roi_stream_top),
    ]
    img = draw_glow(img, cx - funnel_bot_hw, roi_stream_top,
                    funnel_bot_hw * 2, 54, BLUE, radius=22, alpha_max=90)
    layer5 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld5 = ImageDraw.Draw(layer5)
    ld5.polygon(roi_stream_pts, fill=(*BLUE, 180))
    img = Image.alpha_composite(img, layer5)

    # ── "ROI" label at bottom of stream ──
    layer6 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld6 = ImageDraw.Draw(layer6)
    roi_font = load_font(18)
    roi_text = "ROI"
    roi_tw = text_width(ld6, roi_text, roi_font)
    ld6.text((cx - roi_tw // 2, roi_stream_bot + 6), roi_text,
             fill=(*BLUE, 220), font=roi_font)
    img = Image.alpha_composite(img, layer6)

    return img


# ── Vignette ──────────────────────────────────────────────────────────────────
def draw_vignette(img, strength=160):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    steps = 60
    for i in range(steps):
        t = i / steps
        a = int(strength * t * t)
        shrink = int((steps - i) * (min(W, H) / 2) / steps)
        ld.rectangle([shrink, shrink, W - shrink, H - shrink],
                     outline=(0, 0, 0, a), width=4)
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=20))
    img = Image.alpha_composite(img, blurred)
    return img


# ── Text layers ───────────────────────────────────────────────────────────────
def draw_text_layers(img):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    cx = W // 2

    # ── Headline — two lines with metric-based layout (no overlap) ──
    h1_font = load_font(76)
    line1 = "Why Your AI Investment"
    line2 = "Isn\u2019t Paying Off"
    l1_w = text_width(ld, line1, h1_font)
    l2_w = text_width(ld, line2, h1_font)
    line1_x = cx - l1_w // 2
    line2_x = cx - l2_w // 2
    line1_y = SAFE_Y1 + 14           # y=116 — within safe zone

    # Use textbbox to get actual pixel heights (font renders ~75px for 76pt)
    l1_bbox = ld.textbbox((0, 0), line1, font=h1_font)
    l1_h = l1_bbox[3] - l1_bbox[1]  # ~75
    line2_y = line1_y + l1_h + 10   # 10px inter-line gap => y~201

    l2_bbox = ld.textbbox((0, 0), line2, font=h1_font)
    l2_h = l2_bbox[3] - l2_bbox[1]  # ~78
    line2_bottom = line2_y + l2_h   # ~279 — actual bottom pixel of line2

    # shadow
    for dx, dy in [(2, 3), (3, 4)]:
        ld.text((line1_x + dx, line1_y + dy), line1, fill=(0, 0, 0, 90), font=h1_font)
        ld.text((line2_x + dx, line2_y + dy), line2, fill=(0, 0, 0, 90), font=h1_font)
    ld.text((line1_x, line1_y), line1, fill=(*WHITE, 255), font=h1_font)
    ld.text((line2_x, line2_y), line2, fill=(*WHITE, 255), font=h1_font)

    # ── Subline — anchored to line2_bottom + 20px gap (no overlap) ──
    sub_font = load_font(32)
    sub_text = "(And What to Do About It)"
    sub_w = text_width(ld, sub_text, sub_font)
    sub_x = cx - sub_w // 2
    sub_y = line2_bottom + 20       # e.g. ~299 — funnel mouth at ~387, so clean gap
    ld.text((sub_x + 1, sub_y + 2), sub_text, fill=(0, 0, 0, 80), font=sub_font)
    ld.text((sub_x, sub_y), sub_text, fill=(*BLUE, 230), font=sub_font)

    # ── Data callout: lower-left ──
    stat_font = load_font(28)
    stat_text = "Only 24% achieve real ROI"
    stat_x = SAFE_X1 + 8
    stat_y = SAFE_Y2 - 88
    # subtle bg pill
    stat_w = text_width(ld, stat_text, stat_font)
    pill_pad = 10
    ld.rounded_rectangle(
        [stat_x - pill_pad, stat_y - 6,
         stat_x + stat_w + pill_pad, stat_y + 36],
        radius=6,
        fill=(241, 66, 11, 28)
    )
    ld.text((stat_x + 1, stat_y + 2), stat_text, fill=(0, 0, 0, 80), font=stat_font)
    ld.text((stat_x, stat_y), stat_text, fill=(*ORANGE, 240), font=stat_font)

    img = Image.alpha_composite(img, layer)
    return img


# ── PureBrain logo (bottom-right safe zone) ─────────────────────────────────
def draw_logo(img):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    icon_size = 40
    logo_font = load_font(22)

    # Load and resize hex icon
    icon = Image.open(ICON_PATH).convert("RGBA")
    icon = icon.resize((icon_size, icon_size), Image.LANCZOS)

    # Position: bottom-right of safe zone
    logo_right = SAFE_X2 - 6
    logo_bot = SAFE_Y2 - 10
    logo_top = logo_bot - icon_size

    # Measure total text width for brand name
    parts = [("PUREBR", BLUE), ("AI", ORANGE), ("N", BLUE), (".ai", WHITE)]
    total_text_w = sum(
        text_width(ld, t, logo_font) for t, _ in parts
    )
    gap = 8  # between icon and text
    total_w = icon_size + gap + total_text_w
    logo_x = logo_right - total_w

    # Paste icon
    img.paste(icon, (int(logo_x), int(logo_top)), icon)

    # Draw brand text
    bx = logo_x + icon_size + gap
    text_y = logo_top + (icon_size // 2) - 11
    for text, color in parts:
        ld.text((bx, text_y), text, fill=(*color, 240), font=logo_font)
        bx += text_width(ld, text, logo_font)

    img = Image.alpha_composite(img, layer)
    return img


# ── Subtle ambient glow ──────────────────────────────────────────────────────
def draw_ambient_glow(img):
    """Soft blue glow behind the funnel intake area — matches updated funnel_top_y."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx = W // 2
    funnel_top_y = int(H * 0.475)  # matches updated funnel position
    for r_px in [300, 220, 150, 90]:
        a = max(6, 26 - r_px // 16)
        ImageDraw.Draw(layer).ellipse(
            [cx - r_px, funnel_top_y - r_px // 2,
             cx + r_px, funnel_top_y + r_px // 2],
            fill=(*BLUE, a)
        )
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=44))
    img = Image.alpha_composite(img, blurred)
    return img


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Generating banner: Why Your AI Investment Isn't Paying Off")
    print(f"Canvas: {W}x{H}, Safe zone: {SAFE_X1}-{SAFE_X2} x {SAFE_Y1}-{SAFE_Y2}")

    img = make_background()
    print("  [1/8] Background gradient done")

    img = draw_hex_mesh(img, opacity=22)
    print("  [2/8] Hex mesh done")

    img = draw_ambient_glow(img)
    print("  [3/8] Ambient glow done")

    img = draw_funnel(img)
    print("  [4/8] Funnel with leaks done")

    img = draw_vignette(img, strength=150)
    print("  [5/8] Vignette done")

    img = draw_text_layers(img)
    print("  [6/8] Text layers done")

    img = draw_logo(img)
    print("  [7/8] Logo done")

    # Final flatten to RGB for PNG export
    final = Image.new("RGB", (W, H), DARK_BG1)
    final.paste(img, mask=img.split()[3])
    final.save(OUT_PATH, "PNG", optimize=False)
    print(f"  [8/8] Saved to: {OUT_PATH}")

    # Verify
    from PIL import Image as Img2
    check = Img2.open(OUT_PATH)
    print(f"\nVerification: {check.size[0]}x{check.size[1]} {check.mode}")
    size_kb = os.path.getsize(OUT_PATH) // 1024
    print(f"File size: {size_kb}KB")
    print("Done.")


if __name__ == "__main__":
    main()
