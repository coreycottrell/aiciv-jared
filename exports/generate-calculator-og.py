#!/usr/bin/env python3
"""
AI Tool Stack Calculator OG Image Generator
Size: 1456x816 (16:9)
PureBrain dark theme - striking calculator/money waste visual
"""

from PIL import Image, ImageDraw, ImageFont
import math
import random

# Dimensions
W, H = 1456, 816
SAFE_X1, SAFE_Y1 = 182, 102
SAFE_X2, SAFE_Y2 = 1274, 714

# Brand colors
BLUE        = (42, 147, 193)
ORANGE      = (241, 66, 11)
WHITE       = (255, 255, 255)
DARK_BG1    = (8, 10, 18)
DARK_BG2    = (13, 18, 32)
DARK_BG3    = (16, 22, 38)
LIGHT_BLUE  = (140, 200, 230)
PALE        = (180, 200, 220)

FONT_PATH   = "/home/jared/.fonts/Oswald-Bold.ttf"
ICON_PATH   = "/home/jared/projects/AI-CIV/aether/docs/assets/logos/purebrain-icon.png"


def load_font(size):
    return ImageFont.truetype(FONT_PATH, size)


def text_size(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_line_glow(img, pts, color, max_width=10, passes=6):
    """Draw a glowing line through pts using multiple transparent passes."""
    for p in range(passes, 0, -1):
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        alpha = int(30 + (passes - p) * 25)
        width = max(1, int(max_width * p / passes))
        ld.line(pts, fill=(*color, alpha), width=width)
        img = Image.alpha_composite(img, layer)
    # Crisp core
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.line(pts, fill=(*color, 255), width=max(1, max_width // 5))
    img = Image.alpha_composite(img, layer)
    return img


def draw_glow_circle(img, cx, cy, radius, color, max_alpha=60):
    """Radial soft glow circle."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    steps = 20
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(max_alpha * (1 - (i - 1) / steps) * (i / steps) ** 0.5)
        ld.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, a))
    img = Image.alpha_composite(img, layer)
    return img


def draw_hex_outline(draw, cx, cy, size, color, alpha=80, width=2):
    """Draw a hexagon outline."""
    pts = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        pts.append((cx + size * math.cos(angle), cy + size * math.sin(angle)))
    pts_int = [(int(x), int(y)) for x, y in pts]
    # Draw on a layer for alpha
    return pts_int


def vertical_gradient(img, color1, color2):
    """Fill image with vertical gradient."""
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    return img


def add_vignette(img, strength=120):
    """Dark vignette around edges."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = W // 2, H // 2
    max_r = math.sqrt(cx**2 + cy**2) * 1.05
    steps = 40
    for i in range(steps, 0, -1):
        t = i / steps
        rw = int(W * t * 0.85)
        rh = int(H * t * 0.85)
        a = int(strength * (1 - t) ** 1.6)
        draw.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(0, 0, 0, a))
    img = Image.alpha_composite(img, layer)
    return img


def hex_mesh_overlay(img, opacity=10):
    """Subtle hex mesh background texture."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    hex_r = 44
    col_step = int(hex_r * 1.73)
    row_step = hex_r * 1.5
    cols = W // col_step + 3
    rows = int(H / row_step) + 3
    for row in range(rows):
        for col in range(cols):
            cx = col * col_step + (hex_r if row % 2 else 0) - col_step
            cy = int(row * row_step) - hex_r
            pts = []
            for i in range(6):
                angle = math.radians(60 * i - 30)
                pts.append((int(cx + hex_r * math.cos(angle)),
                             int(cy + hex_r * math.sin(angle))))
            ld.polygon(pts, outline=(*BLUE, opacity))
    img = Image.alpha_composite(img, layer)
    return img


def build_image():
    img = Image.new("RGBA", (W, H), DARK_BG1)

    # --- Background gradient ---
    img = vertical_gradient(img, DARK_BG1, DARK_BG2)
    img = img.convert("RGBA")

    # --- Hex mesh overlay ---
    img = hex_mesh_overlay(img, opacity=14)

    # --- Right-side ambient glow (blue energy field) ---
    # Large soft blue glow on right half, representing tool ecosystem
    for cx, cy, radius, color, alpha in [
        (1050, 350, 480, BLUE, 22),
        (1050, 350, 260, BLUE, 30),
        (1100, 300, 140, BLUE, 18),
        (820, 600, 220, BLUE, 12),
    ]:
        img = draw_glow_circle(img, cx, cy, radius, color, max_alpha=alpha)

    # Orange glow accent (waste/loss theme) - left-center
    for cx, cy, radius, color, alpha in [
        (320, 580, 180, ORANGE, 28),
        (320, 580, 90, ORANGE, 35),
        (420, 620, 70, ORANGE, 20),
    ]:
        img = draw_glow_circle(img, cx, cy, radius, color, max_alpha=alpha)

    # --- Diagonal "slash" divider line ---
    # Separates left text area from right visual area
    diag_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(diag_layer)
    # Subtle diagonal gradient bar
    for i in range(3):
        alpha = [12, 25, 12][i]
        offset = [-2, 0, 2][i]
        dd.line([(620 + offset, 60), (760 + offset, 756)],
                fill=(*BLUE, alpha), width=3)
    img = Image.alpha_composite(img, diag_layer)

    # --- Draw floating tool "bubbles" on right side (represents 140+ tools) ---
    rng = random.Random(42)
    bubble_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bubble_layer)

    # Define bubble clusters in right 40% of image
    bubble_zone_x = (760, 1340)
    bubble_zone_y = (80, 740)

    # Some larger "category" circles
    category_circles = [
        (820, 160, 36, BLUE, 55),
        (940, 120, 28, BLUE, 45),
        (1060, 155, 32, ORANGE, 50),
        (1180, 130, 24, BLUE, 40),
        (1280, 170, 30, BLUE, 45),
        (850, 260, 20, ORANGE, 55),
        (990, 240, 26, BLUE, 50),
        (1120, 265, 22, ORANGE, 40),
        (1240, 250, 28, BLUE, 45),
        (1350, 230, 18, ORANGE, 35),
        (790, 380, 24, BLUE, 45),
        (910, 360, 30, ORANGE, 55),
        (1040, 390, 20, BLUE, 40),
        (1160, 370, 26, ORANGE, 48),
        (1310, 360, 22, BLUE, 42),
        (830, 490, 28, ORANGE, 50),
        (960, 470, 22, BLUE, 45),
        (1090, 500, 30, ORANGE, 50),
        (1230, 480, 18, BLUE, 40),
        (1370, 500, 24, ORANGE, 38),
        (870, 600, 20, BLUE, 45),
        (1000, 590, 26, ORANGE, 48),
        (1140, 615, 22, BLUE, 42),
        (1280, 600, 28, ORANGE, 45),
        (920, 690, 18, BLUE, 40),
        (1060, 700, 24, ORANGE, 42),
        (1210, 710, 20, BLUE, 38),
    ]

    for cx, cy, r, color, alpha in category_circles:
        # Outer glow ring
        bd.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4],
                   outline=(*color, alpha // 3), width=1)
        # Main ring
        bd.ellipse([cx - r, cy - r, cx + r, cy + r],
                   outline=(*color, alpha), width=2)
        # Subtle fill
        bd.ellipse([cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3],
                   fill=(*color, alpha // 5))

    # Draw connecting lines between some circles (network effect)
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (5, 0), (5, 6), (6, 7), (7, 8), (8, 9),
        (10, 11), (11, 12), (12, 13), (13, 14),
        (15, 16), (16, 17), (17, 18), (18, 19),
        (20, 21), (21, 22), (22, 23),
        (24, 25), (25, 26),
        (0, 5), (1, 6), (2, 7), (6, 11), (11, 16), (16, 20),
    ]
    for a_idx, b_idx in connections:
        ax, ay = category_circles[a_idx][:2]
        bx, by = category_circles[b_idx][:2]
        bd.line([(ax, ay), (bx, by)], fill=(*BLUE, 18), width=1)

    img = Image.alpha_composite(img, bubble_layer)

    # --- "WASTE" amount visual: big orange $ number on lower left ---
    # This is the emotional hook: "you're wasting $X"

    # --- TEXT AREA (left ~55% of image) ---
    draw_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(draw_layer)

    # ---- QUESTION HEADLINE (top, left-aligned) ----
    # "HOW MUCH ARE YOU"
    # "WASTING ON AI TOOLS?"
    font_h1 = load_font(82)
    font_h2 = load_font(90)
    font_sub = load_font(30)
    font_badge = load_font(26)
    font_logo = load_font(30)
    font_dollar = load_font(110)
    font_dollar_small = load_font(48)

    # Headline line 1: "HOW MUCH ARE YOU"
    h1_text = "HOW MUCH ARE YOU"
    h1_x = SAFE_X1
    h1_y = SAFE_Y1 + 20

    td.text((h1_x + 2, h1_y + 2), h1_text, fill=(0, 0, 0, 120), font=font_h1)
    td.text((h1_x, h1_y), h1_text, fill=(*WHITE, 235), font=font_h1)

    h1_bb = td.textbbox((0, 0), h1_text, font=font_h1)
    h1_h = h1_bb[3] - h1_bb[1]

    # Headline line 2: "WASTING ON AI?" in ORANGE
    h2_text = "WASTING ON AI?"
    h2_y = h1_y + h1_h + 8

    # Orange glow behind headline 2
    h2_bb = td.textbbox((h1_x, h2_y), h2_text, font=font_h2)
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    for spread in range(18, 0, -2):
        a = int(8 + spread * 2.5)
        gd.text((h1_x - spread, h2_y - spread // 2), h2_text,
                fill=(*ORANGE, a), font=font_h2)
        gd.text((h1_x + spread, h2_y + spread // 2), h2_text,
                fill=(*ORANGE, a), font=font_h2)
    img = Image.alpha_composite(img, glow_layer)
    draw_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(draw_layer)

    td.text((h1_x + 2, h1_y + 2), h1_text, fill=(0, 0, 0, 120), font=font_h1)
    td.text((h1_x, h1_y), h1_text, fill=(*WHITE, 235), font=font_h1)

    h2_bb_2 = td.textbbox((0, 0), h2_text, font=font_h2)
    h2_h = h2_bb_2[3] - h2_bb_2[1]
    td.text((h1_x, h2_y), h2_text, fill=(*ORANGE, 255), font=font_h2)

    # ---- SUBTEXT STATS BAR ----
    sub_y = h2_y + h2_h + 28
    sub_text = "140+ Tools  •  31 Categories  •  See Your Real AI Spend"
    td.text((h1_x + 1, sub_y + 1), sub_text, fill=(0, 0, 0, 100), font=font_sub)
    td.text((h1_x, sub_y), sub_text, fill=(*LIGHT_BLUE, 220), font=font_sub)

    sub_bb = td.textbbox((0, 0), sub_text, font=font_sub)
    sub_h = sub_bb[3] - sub_bb[1]

    # ---- HORIZONTAL DIVIDER LINE ----
    div_y = sub_y + sub_h + 22
    line_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lld = ImageDraw.Draw(line_layer)
    line_x2 = h1_x + 560
    # Gradient line: blue → transparent
    for i in range(line_x2 - h1_x):
        t = i / (line_x2 - h1_x)
        a = int(200 * (1 - t ** 1.5))
        lld.line([(h1_x + i, div_y), (h1_x + i, div_y + 1)],
                 fill=(*BLUE, a))
    img = Image.alpha_composite(img, line_layer)

    # ---- CALCULATOR TITLE ----
    calc_font = load_font(52)
    calc_text = "AI TOOL STACK CALCULATOR"
    calc_y = div_y + 18

    td.text((h1_x + 1, calc_y + 2), calc_text, fill=(0, 0, 0, 100), font=calc_font)
    td.text((h1_x, calc_y), calc_text, fill=(*WHITE, 255), font=calc_font)

    calc_bb = td.textbbox((0, 0), calc_text, font=calc_font)
    calc_h = calc_bb[3] - calc_bb[1]

    # ---- WASTE AMOUNT CALLOUT BOX ----
    # Bottom-left: "Average team wastes $X/mo"
    box_x = h1_x
    box_y = calc_y + calc_h + 42
    box_w = 520
    box_h_size = 148

    # Draw box background
    box_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bld = ImageDraw.Draw(box_layer)

    # Dark glass box
    bld.rectangle([box_x - 8, box_y - 8,
                   box_x + box_w, box_y + box_h_size],
                  fill=(8, 14, 28, 180))
    # Orange left accent bar
    bld.rectangle([box_x - 8, box_y - 8,
                   box_x - 4, box_y + box_h_size],
                  fill=(*ORANGE, 220))
    # Blue top border
    bld.line([(box_x - 8, box_y - 8), (box_x + box_w, box_y - 8)],
             fill=(*BLUE, 100), width=1)
    img = Image.alpha_composite(img, box_layer)

    # Callout text
    font_callout_label = load_font(22)
    font_callout_big = load_font(68)
    font_callout_sub = load_font(22)

    callout_label = "AVERAGE TEAM WASTES"
    label_bb = td.textbbox((0, 0), callout_label, font=font_callout_label)
    td.text((box_x + 4, box_y + 2), callout_label,
            fill=(*PALE, 180), font=font_callout_label)

    label_h = label_bb[3] - label_bb[1]

    # Big dollar amount
    dollar_text = "$847"
    dollar_y = box_y + label_h + 8
    td.text((box_x + 4, dollar_y), dollar_text,
            fill=(*ORANGE, 255), font=font_callout_big)
    dollar_bb = td.textbbox((0, 0), dollar_text, font=font_callout_big)
    dollar_w = dollar_bb[2] - dollar_bb[0]

    # "/month" suffix
    td.text((box_x + 6 + dollar_w + 4, dollar_y + 28),
            "/ MONTH", fill=(*WHITE, 200), font=font_callout_sub)

    # Sub-note
    dollar_h = dollar_bb[3] - dollar_bb[1]
    td.text((box_x + 4, dollar_y + dollar_h + 4),
            "on overlapping & unused tools",
            fill=(*PALE, 160), font=font_callout_sub)

    # ---- PUREBRAIN ICON (bottom-left area, behind callout) ----
    icon_raw = Image.open(ICON_PATH).convert("RGBA")
    icon_size = 160
    icon_raw = icon_raw.resize((icon_size, icon_size), Image.LANCZOS)

    icon_x = box_x + box_w + 24
    icon_y = box_y + (box_h_size - icon_size) // 2 + 4

    # Glow behind icon
    img = draw_glow_circle(img, icon_x + icon_size // 2,
                           icon_y + icon_size // 2,
                           icon_size, BLUE, max_alpha=35)

    img_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img_layer.paste(icon_raw, (icon_x, icon_y), icon_raw)
    img = Image.alpha_composite(img, img_layer)

    # ---- PUREBRAIN LOGO TEXT (bottom-right) ----
    logo_y = SAFE_Y2 - 40
    logo_parts = [("PUREBR", BLUE), ("AI", ORANGE), ("N", BLUE), (".ai", WHITE)]
    logo_font = load_font(28)

    # Measure total width
    total_logo_w = 0
    for t, _ in logo_parts:
        bb = td.textbbox((0, 0), t, font=logo_font)
        total_logo_w += bb[2] - bb[0]

    logo_x = SAFE_X2 - total_logo_w
    lx = logo_x
    for t, col in logo_parts:
        bb = td.textbbox((0, 0), t, font=logo_font)
        td.text((lx, logo_y), t, fill=(*col, 220), font=logo_font)
        lx += bb[2] - bb[0]

    # ---- BOTTOM ACCENT BAR ----
    accent_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(accent_layer)
    # Thin orange line at very bottom
    for i in range(W):
        t = i / W
        # Blue left half, orange right half
        if t < 0.5:
            col = BLUE
            a = int(180 * (1 - abs(t - 0.25) * 4))
        else:
            col = ORANGE
            a = int(180 * (1 - abs(t - 0.75) * 4))
        a = max(0, min(255, a))
        ad.line([(i, H - 4), (i, H - 2)], fill=(*col, a))
    img = Image.alpha_composite(img, accent_layer)

    # Composite text layer
    img = Image.alpha_composite(img, draw_layer)

    # --- VIGNETTE ---
    img = add_vignette(img, strength=100)

    # --- Final convert and save ---
    final = img.convert("RGB")
    out_path = "/home/jared/projects/AI-CIV/aether/exports/calculator-og-image.png"
    final.save(out_path, "PNG", optimize=True)
    print(f"Saved: {out_path}")
    print(f"Size: {final.size}")
    import os
    file_size = os.path.getsize(out_path)
    print(f"File size: {file_size / 1024:.1f} KB")
    return out_path


if __name__ == "__main__":
    out = build_image()
    print(f"Done: {out}")
