#!/usr/bin/env python3
"""
PureBrain Stat Card Generator
Creates 5 x 1080x1080 Instagram/LinkedIn square stat cards
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# ─── Paths ────────────────────────────────────────────────────────────────────
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
FONT_REG  = os.path.join(FONT_DIR, "DejaVuSans.ttf")
OUT_DIR   = "/home/jared/projects/AI-CIV/aether/exports/blog-content-2026-03-02"

# ─── Brand Colours ────────────────────────────────────────────────────────────
BG         = (8,  10, 18)       # #080a12
BLUE       = (42, 147, 193)     # #2a93c1
ORANGE     = (241, 66, 11)      # #f1420b
WHITE      = (255, 255, 255)
GRAY       = (136, 146, 164)    # #8892a4
DIM_WHITE  = (200, 210, 225)
DARK_GRID  = (18, 22, 38)       # subtle grid lines

SIZE = (1080, 1080)


# ─── Helper utilities ─────────────────────────────────────────────────────────

def make_canvas():
    img = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(img)
    return img, draw


def font(size, bold=True):
    path = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(path, size)


def centered_x(draw, text, fnt, y, color, img_width=1080):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    x = (img_width - w) // 2
    draw.text((x, y), text, font=fnt, fill=color)
    return w


def draw_grid(draw, spacing=54, alpha_color=DARK_GRID):
    """Subtle dot-grid background."""
    for x in range(0, SIZE[0], spacing):
        for y in range(0, SIZE[1], spacing):
            draw.ellipse([(x-1, y-1), (x+1, y+1)], fill=alpha_color)


def draw_horizontal_rule(draw, y, color=BLUE, width=120, thickness=2):
    x0 = (1080 - width) // 2
    draw.rectangle([(x0, y), (x0 + width, y + thickness)], fill=color)


def draw_branding(draw):
    """PUREBRAIN.ai bottom-centre branding."""
    fnt_br  = font(26, bold=True)
    fnt_ai  = font(26, bold=False)

    brand_text = "PUREBRAIN.ai"
    # measure total width for centering
    bbox_full = draw.textbbox((0, 0), brand_text, font=fnt_br)
    full_w = bbox_full[2] - bbox_full[0]

    # Draw each part in brand colours
    parts = [
        ("PUREBR",    BLUE,   fnt_br),
        ("AI",        ORANGE, fnt_br),
        ("N",         BLUE,   fnt_br),
        (".ai",       GRAY,   fnt_ai),
    ]
    # Calculate total width of parts
    total_w = 0
    part_widths = []
    for txt, _, fnt_p in parts:
        bb = draw.textbbox((0, 0), txt, font=fnt_p)
        pw = bb[2] - bb[0]
        part_widths.append(pw)
        total_w += pw

    y_brand = 1020
    x = (1080 - total_w) // 2
    for (txt, col, fnt_p), pw in zip(parts, part_widths):
        draw.text((x, y_brand), txt, font=fnt_p, fill=col)
        x += pw

    # thin line above branding
    draw.rectangle([(0, 1010), (1080, 1011)], fill=(30, 38, 60))


def wrap_text(draw, text, fnt, max_width):
    """Simple word-wrap returning list of lines."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bb = draw.textbbox((0, 0), test, font=fnt)
        if bb[2] - bb[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_source_tag(draw, source_text, y):
    fnt = font(22, bold=False)
    text = f"Source: {source_text}"
    bb = draw.textbbox((0, 0), text, font=fnt)
    w = bb[2] - bb[0]
    x = (1080 - w) // 2
    # pill background
    pad = 12
    draw.rounded_rectangle(
        [(x - pad, y - 6), (x + w + pad, y + (bb[3] - bb[1]) + 6)],
        radius=8, fill=(20, 26, 44)
    )
    draw.text((x, y), text, font=fnt, fill=GRAY)


# ══════════════════════════════════════════════════════════════════════════════
#  CARD 1 — "7 MONTHS"
# ══════════════════════════════════════════════════════════════════════════════

def make_card_1():
    img, draw = make_canvas()
    draw_grid(draw)

    # ── exponential curve in background ──────────────────────────────────────
    # Draw a faint exponential curve rising from bottom-left to top-right
    curve_pts = []
    for i in range(200):
        t = i / 199          # 0..1
        px = int(80 + t * 920)
        py = int(950 - (math.exp(t * 4) - 1) / (math.exp(4) - 1) * 700)
        curve_pts.append((px, py))
    # Draw as thick faint stroke using small rectangles
    for idx in range(len(curve_pts) - 1):
        x1, y1 = curve_pts[idx]
        x2, y2 = curve_pts[idx + 1]
        draw.line([(x1, y1), (x2, y2)], fill=(42, 147, 193, 30), width=2)
    # Glow dots along curve
    for idx in range(0, len(curve_pts), 20):
        cx, cy = curve_pts[idx]
        draw.ellipse([(cx-3, cy-3), (cx+3, cy+3)], fill=(42, 147, 193, 60))

    # ── accent bar top ────────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (1080, 6)], fill=ORANGE)

    # ── label above stat ─────────────────────────────────────────────────────
    fnt_label = font(30, bold=False)
    centered_x(draw, "AI AGENT CAPABILITY", fnt_label, 180, GRAY)

    # ── hero stat ─────────────────────────────────────────────────────────────
    fnt_num = font(320, bold=True)
    fnt_unit = font(110, bold=True)

    # "7" in orange
    bb7 = draw.textbbox((0, 0), "7", font=fnt_num)
    w7 = bb7[2] - bb7[0]
    bb_months = draw.textbbox((0, 0), " MONTHS", font=fnt_unit)
    w_months = bb_months[2] - bb_months[0]

    # Vertically centre the pair — "7" large, "MONTHS" mid-right
    total_hero_w = w7 + 12 + w_months
    x_start = (1080 - total_hero_w) // 2

    draw.text((x_start, 220), "7", font=fnt_num, fill=ORANGE)
    # "MONTHS" sits to the right, vertically centred on the number
    fnt_months = font(90, bold=True)
    bb_m = draw.textbbox((0, 0), "MONTHS", font=fnt_months)
    y_months = 220 + (bb7[3] - bb7[1]) // 2 - (bb_m[3] - bb_m[1]) // 2
    draw.text((x_start + w7 + 14, y_months), "MONTHS", font=fnt_months, fill=WHITE)

    # ── rule ──────────────────────────────────────────────────────────────────
    draw_horizontal_rule(draw, 660, ORANGE, 80)

    # ── context line ─────────────────────────────────────────────────────────
    fnt_ctx = font(38, bold=False)
    ctx = "AI agent capability doubles every 7 months"
    lines = wrap_text(draw, ctx, fnt_ctx, 860)
    y_ctx = 685
    for line in lines:
        centered_x(draw, line, fnt_ctx, y_ctx, WHITE)
        y_ctx += 50

    # ── "46.3% CAGR" sub-label skipped for card 1; replaced by METR note ─────
    fnt_sub = font(26, bold=False)
    centered_x(draw, "Based on 6 years of frontier model benchmarking data", fnt_sub, y_ctx + 10, GRAY)

    # ── source tag ────────────────────────────────────────────────────────────
    draw_source_tag(draw, "METR — 6 years of data", 930)

    # ── branding ─────────────────────────────────────────────────────────────
    draw_branding(draw)

    # ── accent bar bottom ─────────────────────────────────────────────────────
    draw.rectangle([(0, 1074), (1080, 1080)], fill=ORANGE)

    img.save(os.path.join(OUT_DIR, "stat-card-1-doubling.png"))
    print("  stat-card-1-doubling.png saved")


# ══════════════════════════════════════════════════════════════════════════════
#  CARD 2 — "$52.6B"
# ══════════════════════════════════════════════════════════════════════════════

def make_card_2():
    img, draw = make_canvas()
    draw_grid(draw)

    # ── accent bar top ────────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (1080, 6)], fill=BLUE)

    # ── label ─────────────────────────────────────────────────────────────────
    fnt_label = font(30, bold=False)
    centered_x(draw, "AGENTIC AI MARKET SIZE", fnt_label, 160, GRAY)

    # ── "BY 2030" small badge ─────────────────────────────────────────────────
    fnt_badge = font(24, bold=True)
    badge_txt = "BY 2030"
    bb = draw.textbbox((0, 0), badge_txt, font=fnt_badge)
    bw = bb[2] - bb[0]
    bx = (1080 - bw) // 2
    draw.rounded_rectangle([(bx - 14, 197), (bx + bw + 14, 238)], radius=6, fill=BLUE)
    draw.text((bx, 200), badge_txt, font=fnt_badge, fill=WHITE)

    # ── hero stat "$52.6B" ────────────────────────────────────────────────────
    fnt_hero = font(200, bold=True)
    centered_x(draw, "$52.6B", fnt_hero, 260, BLUE)

    # ── "up from $7.84B today" small ─────────────────────────────────────────
    fnt_from = font(34, bold=False)
    centered_x(draw, "up from $7.84B today", fnt_from, 510, GRAY)

    # ── CAGR pill ─────────────────────────────────────────────────────────────
    cagr_txt = "46.3% CAGR"
    fnt_cagr = font(48, bold=True)
    bb = draw.textbbox((0, 0), cagr_txt, font=fnt_cagr)
    cw = bb[2] - bb[0]; ch = bb[3] - bb[1]
    cx = (1080 - cw) // 2
    draw.rounded_rectangle(
        [(cx - 24, 575), (cx + cw + 24, 575 + ch + 24)],
        radius=12, fill=(15, 28, 48)
    )
    # left border accent
    draw.rectangle([(cx - 24, 575), (cx - 20, 575 + ch + 24)], fill=ORANGE)
    draw.text((cx, 587), cagr_txt, font=fnt_cagr, fill=ORANGE)

    # ── rule ──────────────────────────────────────────────────────────────────
    draw_horizontal_rule(draw, 685, BLUE, 100)

    # ── context ───────────────────────────────────────────────────────────────
    fnt_ctx = font(38, bold=False)
    ctx = "Agentic AI will be a $52.6B industry within 4 years"
    lines = wrap_text(draw, ctx, fnt_ctx, 860)
    y_ctx = 710
    for line in lines:
        centered_x(draw, line, fnt_ctx, y_ctx, WHITE)
        y_ctx += 50

    # ── source tag ────────────────────────────────────────────────────────────
    draw_source_tag(draw, "MarketsandMarkets", 930)

    # ── branding ─────────────────────────────────────────────────────────────
    draw_branding(draw)

    # ── accent bar bottom ─────────────────────────────────────────────────────
    draw.rectangle([(0, 1074), (1080, 1080)], fill=BLUE)

    img.save(os.path.join(OUT_DIR, "stat-card-2-market.png"))
    print("  stat-card-2-market.png saved")


# ══════════════════════════════════════════════════════════════════════════════
#  CARD 3 — "89%"
# ══════════════════════════════════════════════════════════════════════════════

def make_card_3():
    img, draw = make_canvas()
    draw_grid(draw)

    # ── accent bar top ────────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (1080, 6)], fill=ORANGE)

    # ── label ─────────────────────────────────────────────────────────────────
    fnt_label = font(30, bold=False)
    centered_x(draw, "ORGANIZATIONS NOT BUILDING AI AGENTS", fnt_label, 160, GRAY)

    # ── hero stat "89%" ───────────────────────────────────────────────────────
    fnt_hero = font(320, bold=True)
    centered_x(draw, "89%", fnt_hero, 210, WHITE)

    # ── visual bar: 89% dim vs 11% bright ─────────────────────────────────────
    bar_y = 600
    bar_h = 32
    bar_x0 = 90
    bar_x1 = 990
    bar_total_w = bar_x1 - bar_x0

    # 89% dim bar
    dim_w = int(bar_total_w * 0.89)
    draw.rounded_rectangle(
        [(bar_x0, bar_y), (bar_x0 + dim_w, bar_y + bar_h)],
        radius=6, fill=(50, 40, 40)
    )
    # 11% bright bar
    bright_x0 = bar_x0 + dim_w + 4
    draw.rounded_rectangle(
        [(bright_x0, bar_y), (bar_x1, bar_y + bar_h)],
        radius=6, fill=ORANGE
    )

    # ── bar labels ────────────────────────────────────────────────────────────
    fnt_bar = font(28, bold=True)
    draw.text((bar_x0, bar_y + 42), "89% — haven't started", font=fnt_bar, fill=GRAY)
    bb_11 = draw.textbbox((0, 0), "11% active", font=fnt_bar)
    draw.text((bar_x1 - (bb_11[2] - bb_11[0]), bar_y + 42), "11% active",
              font=fnt_bar, fill=ORANGE)

    # ── rule ──────────────────────────────────────────────────────────────────
    draw_horizontal_rule(draw, 720, ORANGE, 80)

    # ── context ───────────────────────────────────────────────────────────────
    fnt_ctx = font(36, bold=False)
    ctx = "of organizations haven't started building AI agent systems"
    lines = wrap_text(draw, ctx, fnt_ctx, 860)
    y_ctx = 745
    for line in lines:
        centered_x(draw, line, fnt_ctx, y_ctx, WHITE)
        y_ctx += 48

    # ── source tag ────────────────────────────────────────────────────────────
    draw_source_tag(draw, "Gartner, McKinsey, Capgemini", 930)

    # ── branding ─────────────────────────────────────────────────────────────
    draw_branding(draw)

    # ── accent bar bottom ─────────────────────────────────────────────────────
    draw.rectangle([(0, 1074), (1080, 1080)], fill=ORANGE)

    img.save(os.path.join(OUT_DIR, "stat-card-3-89percent.png"))
    print("  stat-card-3-89percent.png saved")


# ══════════════════════════════════════════════════════════════════════════════
#  CARD 4 — "$1M → $73M"
# ══════════════════════════════════════════════════════════════════════════════

def make_card_4():
    img, draw = make_canvas()
    draw_grid(draw)

    # ── accent bar top ────────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (1080, 6)], fill=BLUE)

    # ── label ─────────────────────────────────────────────────────────────────
    fnt_label = font(28, bold=False)
    centered_x(draw, "COGNITION AI ARR — 9 MONTHS", fnt_label, 140, GRAY)

    # ── hero stat: "$1M → $73M" ───────────────────────────────────────────────
    fnt_money = font(140, bold=True)
    fnt_arrow = font(110, bold=True)

    parts = [
        ("$1M",  WHITE),
        ("  →  ", GRAY),
        ("$73M", ORANGE),
    ]
    # Measure total width
    total_w = 0
    for txt, _ in parts:
        bb = draw.textbbox((0, 0), txt, font=fnt_money)
        total_w += bb[2] - bb[0]

    x = (1080 - total_w) // 2
    y_hero = 220
    for txt, col in parts:
        draw.text((x, y_hero), txt, font=fnt_money, fill=col)
        bb = draw.textbbox((0, 0), txt, font=fnt_money)
        x += bb[2] - bb[0]

    # ── time label "in 9 months" ──────────────────────────────────────────────
    fnt_time = font(40, bold=False)
    centered_x(draw, "in 9 months", fnt_time, 390, GRAY)

    # ── $10.2B valuation sub-stat ─────────────────────────────────────────────
    fnt_val = font(58, bold=True)
    val_txt = "$10.2B valuation"
    bb = draw.textbbox((0, 0), val_txt, font=fnt_val)
    vw = bb[2] - bb[0]; vh = bb[3] - bb[1]
    vx = (1080 - vw) // 2
    draw.rounded_rectangle(
        [(vx - 30, 460), (vx + vw + 30, 460 + vh + 30)],
        radius=12, fill=(14, 22, 44)
    )
    draw.rectangle([(vx - 30, 460), (vx - 26, 460 + vh + 30)], fill=BLUE)
    draw.text((vx, 475), val_txt, font=fnt_val, fill=BLUE)

    # ── sparkline / growth bars ───────────────────────────────────────────────
    bars_data = [1, 3, 8, 18, 35, 55, 73]
    bar_w = 60
    bar_gap = 24
    bar_bottom = 650
    bars_total_w = len(bars_data) * bar_w + (len(bars_data) - 1) * bar_gap
    bx = (1080 - bars_total_w) // 2
    max_v = max(bars_data)
    max_bar_h = 90
    for i, v in enumerate(bars_data):
        h = int((v / max_v) * max_bar_h)
        col = ORANGE if i == len(bars_data) - 1 else (42, 80, 110)
        x0 = bx + i * (bar_w + bar_gap)
        draw.rounded_rectangle(
            [(x0, bar_bottom - h), (x0 + bar_w, bar_bottom)],
            radius=4, fill=col
        )

    # ── rule ──────────────────────────────────────────────────────────────────
    draw_horizontal_rule(draw, 680, BLUE, 100)

    # ── context ───────────────────────────────────────────────────────────────
    fnt_ctx = font(36, bold=False)
    centered_x(draw, "Cognition AI ARR growth in 9 months", fnt_ctx, 705, WHITE)

    # ── source tag ────────────────────────────────────────────────────────────
    draw_source_tag(draw, "TechCrunch / Sacra", 930)

    # ── branding ─────────────────────────────────────────────────────────────
    draw_branding(draw)

    # ── accent bar bottom ─────────────────────────────────────────────────────
    draw.rectangle([(0, 1074), (1080, 1080)], fill=BLUE)

    img.save(os.path.join(OUT_DIR, "stat-card-4-cognition.png"))
    print("  stat-card-4-cognition.png saved")


# ══════════════════════════════════════════════════════════════════════════════
#  CARD 5 — "The Window Is Closing"
# ══════════════════════════════════════════════════════════════════════════════

def make_card_5():
    img, draw = make_canvas()
    draw_grid(draw)

    # ── hourglass motif (geometric) ───────────────────────────────────────────
    # Top triangle (upper half)
    cx = 540; top_y = 80; mid_y = 500; bot_y = 920; half_w = 160
    draw.polygon(
        [(cx - half_w, top_y + 20), (cx + half_w, top_y + 20), (cx, mid_y - 10)],
        fill=(20, 26, 46)
    )
    # Bottom triangle — faint orange outline only, no solid fill
    draw.polygon(
        [(cx - half_w, bot_y - 20), (cx + half_w, bot_y - 20), (cx, mid_y + 10)],
        fill=(30, 14, 8)   # very dark near-black to keep it subtle
    )
    # Outline strokes
    stroke_col = (42, 147, 193, 80)
    outline_pts_top = [(cx - half_w, top_y + 20), (cx + half_w, top_y + 20), (cx, mid_y - 10)]
    outline_pts_bot = [(cx - half_w, bot_y - 20), (cx + half_w, bot_y - 20), (cx, mid_y + 10)]
    for pts in [outline_pts_top, outline_pts_bot]:
        for i in range(len(pts)):
            draw.line([pts[i], pts[(i+1) % len(pts)]], fill=(42, 147, 193), width=2)

    # ── sand dots falling ─────────────────────────────────────────────────────
    import random
    random.seed(42)
    for _ in range(40):
        sx = random.randint(cx - 30, cx + 30)
        sy = random.randint(mid_y + 15, mid_y + 80)
        r = random.randint(1, 4)
        alpha = random.randint(100, 200)
        draw.ellipse([(sx-r, sy-r), (sx+r, sy+r)], fill=ORANGE)

    # ── accent bar top ────────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (1080, 6)], fill=ORANGE)

    # ── hero text "THE WINDOW" ────────────────────────────────────────────────
    fnt_hero = font(130, bold=True)
    centered_x(draw, "THE WINDOW", fnt_hero, 140, WHITE)

    # ── "IS CLOSING" in orange ────────────────────────────────────────────────
    fnt_closing = font(130, bold=True)
    centered_x(draw, "IS CLOSING", fnt_closing, 280, ORANGE)

    # ── rule ──────────────────────────────────────────────────────────────────
    draw_horizontal_rule(draw, 440, ORANGE, 80)

    # ── context block (multi-line) ────────────────────────────────────────────
    fnt_ctx = font(34, bold=False)
    ctx = ("Companies deploying agents NOW build compounding "
           "advantages competitors can't purchase")
    lines = wrap_text(draw, ctx, fnt_ctx, 820)
    y_ctx = 670
    for line in lines:
        centered_x(draw, line, fnt_ctx, y_ctx, WHITE)
        y_ctx += 46

    # ── source tag ────────────────────────────────────────────────────────────
    draw_source_tag(draw, "purebrain.ai/blog", 930)

    # ── branding ─────────────────────────────────────────────────────────────
    draw_branding(draw)

    # ── accent bar bottom ─────────────────────────────────────────────────────
    draw.rectangle([(0, 1074), (1080, 1080)], fill=ORANGE)

    img.save(os.path.join(OUT_DIR, "stat-card-5-window.png"))
    print("  stat-card-5-window.png saved")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Generating PureBrain stat cards...")
    make_card_1()
    make_card_2()
    make_card_3()
    make_card_4()
    make_card_5()
    print("\nAll 5 stat cards generated successfully.")
