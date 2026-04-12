#!/usr/bin/env python3
"""
Banner generator: "We Both Wrote This Post. That's the Point."
Visual concept: Two streams — human (orange, organic curves) and AI (blue, geometric)
— converging into a shared glowing center hex, with text above and below.
Canvas: 1456x816, safe zone: 182px margins (inner 1092x612)
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Config ───────────────────────────────────────────────────────────────────
W, H = 1456, 816
SAFE_X1, SAFE_X2 = 182, 1274
SAFE_Y1, SAFE_Y2 = 102, 714

ORANGE   = (241, 66, 11)
BLUE     = (42, 147, 193)
WHITE    = (255, 255, 255)
GOLD     = (255, 195, 80)        # warm accent for merged/unified zone
DARK_BG1 = (8, 10, 18)
DARK_BG2 = (10, 15, 28)
HEX_MESH = (22, 36, 58)

FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"
ICON_PATH = "/home/jared/projects/AI-CIV/aether/docs/assets/logos/purebrain-icon.png"
OUT_PATH  = "/home/jared/projects/AI-CIV/aether/exports/origin-story-banner.png"


# ── Helpers ──────────────────────────────────────────────────────────────────
def load_font(size):
    return ImageFont.truetype(FONT_PATH, size)


def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def draw_glow_ellipse(img, cx, cy, rx, ry, color, alpha_max=90, blur_r=40):
    """Soft radial glow centered at (cx, cy)."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    steps = 10
    for i in range(steps):
        t = i / steps
        erx = int(rx * (1 - t * 0.6))
        ery = int(ry * (1 - t * 0.6))
        a = int(alpha_max * (1 - t))
        ld.ellipse([cx - erx, cy - ery, cx + erx, cy + ery], fill=(*color, a))
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=blur_r))
    return Image.alpha_composite(img, blurred)


def draw_line_glow(img, pts, color, max_width=18, passes=6):
    """Draw a glowing polyline."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for i in range(passes, 0, -1):
        t = i / passes
        w = max(1, int(max_width * t))
        a = int(140 * (1 - t * 0.65))
        ld.line(pts, fill=(*color, a), width=w)
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=3))
    ld2 = ImageDraw.Draw(blurred)
    ld2.line(pts, fill=(*color, 255), width=2)
    return Image.alpha_composite(img, blurred)


def hex_points(cx, cy, r, angle_offset=0):
    """Return list of 6 (x,y) vertices for a regular hex."""
    pts = []
    for i in range(6):
        angle = math.radians(60 * i + angle_offset)
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


# ── Background gradient ──────────────────────────────────────────────────────
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


# ── Hexagonal mesh overlay ───────────────────────────────────────────────────
def draw_hex_mesh(img, opacity=18):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    hex_r = 38
    col_w = hex_r * math.sqrt(3)
    row_h = hex_r * 1.5
    cols = int(W / col_w) + 3
    rows = int(H / row_h) + 3
    for row in range(-1, rows):
        for col in range(-1, cols):
            cx_h = col * col_w + (hex_r * math.sqrt(3) / 2 if row % 2 else 0)
            cy_h = row * row_h
            pts = hex_points(cx_h, cy_h, hex_r, angle_offset=30)
            ld.polygon(pts, outline=(*HEX_MESH, opacity), fill=None)
    return Image.alpha_composite(img, layer)


# ── Central convergence hex ──────────────────────────────────────────────────
def draw_center_hex(img):
    """
    Large glowing hex in center of canvas — the meeting point of human + AI.
    Radiates outward with orange-blue gradient glow.
    """
    cx = W // 2
    cy = int(H * 0.60)   # lower — clear of subline text, more breathing room

    # Outer soft ambient glow (mixed orange + blue = convergence)
    img = draw_glow_ellipse(img, cx, cy, 340, 260, BLUE, alpha_max=45, blur_r=70)
    img = draw_glow_ellipse(img, cx, cy, 240, 190, ORANGE, alpha_max=35, blur_r=55)
    img = draw_glow_ellipse(img, cx, cy, 150, 120, WHITE, alpha_max=28, blur_r=35)

    # Draw concentric hexagons (outer → inner, fading in)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    # Outer hex rings (subtle mesh brightening)
    for r_size, alpha in [(200, 12), (165, 18), (135, 24)]:
        pts = hex_points(cx, cy, r_size, angle_offset=30)
        ld.polygon(pts, outline=(*BLUE, alpha), fill=None)

    # Mid hex — blue tinted fill
    pts_mid = hex_points(cx, cy, 110, angle_offset=30)
    ld.polygon(pts_mid, outline=(*BLUE, 55), fill=(12, 22, 42, 120))

    # Inner hex — orange tinted fill (convergence glow)
    pts_inner = hex_points(cx, cy, 70, angle_offset=30)
    ld.polygon(pts_inner, outline=(*ORANGE, 80), fill=(30, 15, 10, 140))

    # Core hex — bright center
    pts_core = hex_points(cx, cy, 38, angle_offset=30)
    ld.polygon(pts_core, fill=(255, 255, 255, 25), outline=(*WHITE, 160))

    # Glow border for mid hex
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.alpha_composite(img, blurred)

    # Crisp hex outlines on top (drawn fresh after blur) — bright and bold
    layer2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld2 = ImageDraw.Draw(layer2)
    # Draw each hex outline 2x for extra crispness
    for _ in range(2):
        pts_mid2 = hex_points(cx, cy, 110, angle_offset=30)
        ld2.polygon(pts_mid2, outline=(*BLUE, 200), fill=None)
        pts_inner2 = hex_points(cx, cy, 70, angle_offset=30)
        ld2.polygon(pts_inner2, outline=(*ORANGE, 220), fill=None)
        pts_core2 = hex_points(cx, cy, 38, angle_offset=30)
        ld2.polygon(pts_core2, outline=(*WHITE, 240), fill=None)
    # Bright outer ring
    pts_outer2 = hex_points(cx, cy, 135, angle_offset=30)
    ld2.polygon(pts_outer2, outline=(*BLUE, 90), fill=None)
    img = Image.alpha_composite(img, layer2)

    # PureBrain icon inside center hex
    icon = Image.open(ICON_PATH).convert("RGBA")
    icon_size = 52
    icon = icon.resize((icon_size, icon_size), Image.LANCZOS)
    ix = cx - icon_size // 2
    iy = cy - icon_size // 2
    img.paste(icon, (ix, iy), icon)

    return img, cx, cy


# ── Human stream (left → center) ─────────────────────────────────────────────
def draw_human_stream(img, cx_center, cy_center):
    """
    From left side: organic flowing curves in orange → converging to center hex.
    Fan of 5 streams — spread wide at left, converge to center hex.
    Represents the human voice / writer.
    """
    start_x = SAFE_X1 + 30
    start_y_center = int(H * 0.60)   # match cy_center
    end_x = cx_center - 118

    # 5 streams: fan spread at left (±110px), converge tight at center (±25px)
    stream_defs = [
        # (start_y_offset, end_y_offset, ctrl_bulge)
        (-110,  -22, -60),
        (-55,   -12, -30),
        (  0,     0,  10),
        ( 55,    12,  35),
        (110,    22,  70),
    ]

    max_widths = [6, 9, 14, 9, 6]  # center stream widest

    for (sy_off, ey_off, ctrl_b), max_w in zip(stream_defs, max_widths):
        sy = start_y_center + sy_off
        ey = cy_center + ey_off
        ctrl_x = int(start_x + (end_x - start_x) * 0.45)
        ctrl_y = int((sy + ey) / 2 + ctrl_b)

        pts = []
        n = 50
        for i in range(n + 1):
            t = i / n
            bx = (1-t)**2 * start_x + 2*(1-t)*t * ctrl_x + t**2 * end_x
            by = (1-t)**2 * sy      + 2*(1-t)*t * ctrl_y  + t**2 * ey
            pts.append((bx, by))

        img = draw_line_glow(img, pts, ORANGE, max_width=max_w, passes=6)

    # Flowing particles along main (center) stream
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ctrl_x_main = int(start_x + (end_x - start_x) * 0.45)
    ctrl_y_main = int((start_y_center + cy_center) / 2 + 10)
    for t_val in [0.12, 0.25, 0.40, 0.55, 0.68, 0.82]:
        bx = (1-t_val)**2 * start_x + 2*(1-t_val)*t_val * ctrl_x_main + t_val**2 * end_x
        by = (1-t_val)**2 * start_y_center + 2*(1-t_val)*t_val * ctrl_y_main + t_val**2 * cy_center
        r = int(3 + 5 * t_val)
        ld.ellipse([bx-r, by-r, bx+r, by+r], fill=(*ORANGE, int(160 * t_val + 80)))
        for spread in [r*3, r*2]:
            a = int(22 * (1 - spread / (r*4)))
            ld.ellipse([bx-spread, by-spread, bx+spread, by+spread], fill=(*ORANGE, a))
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=1))
    img = Image.alpha_composite(img, blurred)

    # "HUMAN" label on left side — below the fan spread
    layer2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld2 = ImageDraw.Draw(layer2)
    label_font = load_font(22)
    label = "HUMAN"
    lw = text_width(ld2, label, label_font)
    lx = start_x + 6
    ly = start_y_center + 125    # below the lowest stream
    ld2.rounded_rectangle([lx - 8, ly - 4, lx + lw + 8, ly + 30], radius=4,
                          fill=(*ORANGE, 30))
    ld2.text((lx + 1, ly + 1), label, fill=(0, 0, 0, 70), font=label_font)
    ld2.text((lx, ly), label, fill=(*ORANGE, 230), font=label_font)
    img = Image.alpha_composite(img, layer2)

    return img


# ── AI stream (right → center) ───────────────────────────────────────────────
def draw_ai_stream(img, cx_center, cy_center):
    """
    From right side: geometric fan of 5 lines in blue → converging to center hex.
    Represents the AI voice / writer.
    """
    start_x = SAFE_X2 - 30
    start_y_center = int(H * 0.60)   # match cy_center
    end_x = cx_center + 118

    stream_defs = [
        (-110,  -22, -58),
        (-55,   -12, -28),
        (  0,     0,   8),
        ( 55,    12,  33),
        (110,    22,  68),
    ]

    max_widths = [6, 9, 14, 9, 6]

    for (sy_off, ey_off, ctrl_b), max_w in zip(stream_defs, max_widths):
        sy = start_y_center + sy_off
        ey = cy_center + ey_off
        ctrl_x = int(start_x + (end_x - start_x) * 0.45)
        ctrl_y = int((sy + ey) / 2 + ctrl_b)

        pts = []
        n = 50
        for i in range(n + 1):
            t = i / n
            bx = (1-t)**2 * start_x + 2*(1-t)*t * ctrl_x + t**2 * end_x
            by = (1-t)**2 * sy      + 2*(1-t)*t * ctrl_y  + t**2 * ey
            pts.append((bx, by))

        img = draw_line_glow(img, pts, BLUE, max_width=max_w, passes=6)

    # Flowing particles along main (center) stream
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ctrl_x_main = int(start_x + (end_x - start_x) * 0.45)
    ctrl_y_main = int((start_y_center + cy_center) / 2 + 8)
    for t_val in [0.12, 0.25, 0.40, 0.55, 0.68, 0.82]:
        bx = (1-t_val)**2 * start_x + 2*(1-t_val)*t_val * ctrl_x_main + t_val**2 * end_x
        by = (1-t_val)**2 * start_y_center + 2*(1-t_val)*t_val * ctrl_y_main + t_val**2 * cy_center
        r = int(3 + 5 * t_val)
        ld.ellipse([bx-r, by-r, bx+r, by+r], fill=(*BLUE, int(160 * t_val + 80)))
        for spread in [r*3, r*2]:
            a = int(22 * (1 - spread / (r*4)))
            ld.ellipse([bx-spread, by-spread, bx+spread, by+spread], fill=(*BLUE, a))
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=1))
    img = Image.alpha_composite(img, blurred)

    # "AI" label on right side — below the fan spread
    layer2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld2 = ImageDraw.Draw(layer2)
    label_font = load_font(22)
    label = "AI"
    lw = text_width(ld2, label, label_font)
    lx = start_x - lw - 16
    ly = start_y_center + 125    # below the lowest stream
    ld2.rounded_rectangle([lx - 8, ly - 4, lx + lw + 8, ly + 30], radius=4,
                          fill=(*BLUE, 30))
    ld2.text((lx + 1, ly + 1), label, fill=(0, 0, 0, 70), font=label_font)
    ld2.text((lx, ly), label, fill=(*BLUE, 230), font=label_font)
    img = Image.alpha_composite(img, layer2)

    return img


# ── Vignette ─────────────────────────────────────────────────────────────────
def draw_vignette(img, strength=155):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    steps = 60
    for i in range(steps):
        t = i / steps
        a = int(strength * t * t)
        shrink = int((steps - i) * (min(W, H) / 2) / steps)
        ld.rectangle([shrink, shrink, W - shrink, H - shrink],
                     outline=(0, 0, 0, a), width=4)
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=22))
    return Image.alpha_composite(img, blurred)


# ── Text layers ───────────────────────────────────────────────────────────────
def draw_text_layers(img, cy_center):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    cx = W // 2

    # ── Kicker (top eyebrow) ──
    kicker_font = load_font(22)
    kicker_text = "ORIGIN STORY"
    kicker_w = text_width(ld, kicker_text, kicker_font)
    kicker_x = cx - kicker_w // 2
    kicker_y = SAFE_Y1 + 14
    # pill bg
    ld.rounded_rectangle(
        [kicker_x - 12, kicker_y - 5, kicker_x + kicker_w + 12, kicker_y + 28],
        radius=4,
        fill=(*ORANGE, 30)
    )
    ld.text((kicker_x + 1, kicker_y + 1), kicker_text, fill=(0, 0, 0, 70), font=kicker_font)
    ld.text((kicker_x, kicker_y), kicker_text, fill=(*ORANGE, 220), font=kicker_font)

    # ── Headline — Line 1: "We Both Wrote This Post." ──
    h1_font = load_font(72)
    line1 = "We Both Wrote This Post."
    l1_w = text_width(ld, line1, h1_font)
    line1_x = cx - l1_w // 2
    l1_bbox = ld.textbbox((0, 0), line1, font=h1_font)
    l1_h = l1_bbox[3] - l1_bbox[1]
    # Position headline: below kicker, above center
    kicker_bbox = ld.textbbox((0, 0), kicker_text, font=kicker_font)
    kicker_h = kicker_bbox[3] - kicker_bbox[1]
    line1_y = kicker_y + kicker_h + 16

    # shadow
    for dx, dy in [(2, 3), (3, 4)]:
        ld.text((line1_x + dx, line1_y + dy), line1, fill=(0, 0, 0, 90), font=h1_font)
    ld.text((line1_x, line1_y), line1, fill=(*WHITE, 255), font=h1_font)

    line1_bottom = line1_y + l1_h

    # ── Headline — Line 2: "That's the Point." (mixed color: orange "That's" + white rest) ──
    h2_font = load_font(72)
    part_a = "That\u2019s the Point."
    # Keep it one color — pure white for clean read. "That's" emphasis via size not color.
    part_a_w = text_width(ld, part_a, h2_font)
    line2_x = cx - part_a_w // 2
    line2_y = line1_bottom + 8
    l2_bbox = ld.textbbox((0, 0), part_a, font=h2_font)
    l2_h = l2_bbox[3] - l2_bbox[1]

    # Shadow
    for dx, dy in [(2, 3), (3, 4)]:
        ld.text((line2_x + dx, line2_y + dy), part_a, fill=(0, 0, 0, 90), font=h2_font)

    # Split coloring: "That\u2019s the Point." — make "That\u2019s" orange
    thatw = text_width(ld, "That\u2019s ", h2_font)
    ld.text((line2_x, line2_y), "That\u2019s ", fill=(*ORANGE, 255), font=h2_font)
    ld.text((line2_x + thatw, line2_y), "the Point.", fill=(*WHITE, 255), font=h2_font)

    line2_bottom = line2_y + l2_h

    # ── Subline — ensure gap from headline and doesn't hit center hex ──
    sub_font = load_font(28)
    sub_text = "A human + AI writing partnership, from the start."
    sub_w = text_width(ld, sub_text, sub_font)
    sub_x = cx - sub_w // 2
    sub_y = line2_bottom + 18
    # Shadow
    ld.text((sub_x + 1, sub_y + 2), sub_text, fill=(0, 0, 0, 80), font=sub_font)
    ld.text((sub_x, sub_y), sub_text, fill=(*BLUE, 220), font=sub_font)

    # ── URL at bottom-left safe zone ──
    url_font = load_font(20)
    url_text = "purebrain.ai/blog"
    url_w = text_width(ld, url_text, url_font)
    url_x = SAFE_X1 + 10
    url_y = SAFE_Y2 - 32
    ld.text((url_x + 1, url_y + 1), url_text, fill=(0, 0, 0, 70), font=url_font)
    ld.text((url_x, url_y), url_text, fill=(*WHITE, 160), font=url_font)

    img = Image.alpha_composite(img, layer)
    return img


# ── PureBrain logo (bottom-right safe zone) ──────────────────────────────────
def draw_logo(img):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    icon_size = 40
    logo_font = load_font(22)

    icon = Image.open(ICON_PATH).convert("RGBA")
    icon = icon.resize((icon_size, icon_size), Image.LANCZOS)

    logo_right = SAFE_X2 - 6
    logo_bot = SAFE_Y2 - 10
    logo_top = logo_bot - icon_size

    parts = [("PUREBR", BLUE), ("AI", ORANGE), ("N", BLUE), (".ai", WHITE)]
    total_text_w = sum(text_width(ld, t, logo_font) for t, _ in parts)
    gap = 8
    total_w = icon_size + gap + total_text_w
    logo_x = logo_right - total_w

    img.paste(icon, (int(logo_x), int(logo_top)), icon)

    bx = logo_x + icon_size + gap
    text_y = logo_top + (icon_size // 2) - 11
    for text, color in parts:
        ld.text((bx, text_y), text, fill=(*color, 240), font=logo_font)
        bx += text_width(ld, text, logo_font)

    return Image.alpha_composite(img, layer)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("Generating banner: We Both Wrote This Post. That's the Point.")
    print(f"Canvas: {W}x{H}, Safe zone: {SAFE_X1}-{SAFE_X2} x {SAFE_Y1}-{SAFE_Y2}")

    img = make_background()
    print("  [1/9] Background gradient done")

    img = draw_hex_mesh(img, opacity=18)
    print("  [2/9] Hex mesh done")

    img, cx_center, cy_center = draw_center_hex(img)
    print(f"  [3/9] Center convergence hex done (cx={cx_center}, cy={cy_center})")

    img = draw_human_stream(img, cx_center, cy_center)
    print("  [4/9] Human stream (orange, left) done")

    img = draw_ai_stream(img, cx_center, cy_center)
    print("  [5/9] AI stream (blue, right) done")

    img = draw_vignette(img, strength=150)
    print("  [6/9] Vignette done")

    img = draw_text_layers(img, cy_center)
    print("  [7/9] Text layers done")

    img = draw_logo(img)
    print("  [8/9] PureBrain logo done")

    # Final flatten to RGB
    final = Image.new("RGB", (W, H), DARK_BG1)
    final.paste(img, mask=img.split()[3])
    final.save(OUT_PATH, "PNG", optimize=False)
    print(f"  [9/9] Saved to: {OUT_PATH}")

    # Verify
    check = Image.open(OUT_PATH)
    print(f"\nVerification: {check.size[0]}x{check.size[1]} {check.mode}")
    size_kb = os.path.getsize(OUT_PATH) // 1024
    print(f"File size: {size_kb}KB")
    print("Done.")


if __name__ == "__main__":
    main()
