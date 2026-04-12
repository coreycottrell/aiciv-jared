#!/usr/bin/env python3
"""
Generate blog banners for PureBrain.ai using PIL/Pillow.
Dark theme: #080a12 background, blue #2a93c1 and orange #f1420b accents.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont

# --- Config ---
W, H = 1200, 630
BG_COLOR = (8, 10, 18)          # #080a12
BLUE = (42, 147, 193)           # #2a93c1
ORANGE = (241, 66, 11)          # #f1420b
WHITE = (255, 255, 255)
LIGHT_BLUE = (100, 180, 220)
DIM_BLUE = (20, 60, 90)
DIM_ORANGE = (80, 22, 4)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def make_base(img: Image.Image):
    """Draw the dark background with grid and hex overlay on img."""
    draw = ImageDraw.Draw(img)

    # Dark gradient — left darker, right slightly lighter
    for x in range(W):
        factor = x / W
        r = int(BG_COLOR[0] + factor * 6)
        g = int(BG_COLOR[1] + factor * 5)
        b = int(BG_COLOR[2] + factor * 12)
        draw.line([(x, 0), (x, H)], fill=(r, g, b))

    # Subtle grid lines
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill=(20, 24, 36), width=1)
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=(20, 24, 36), width=1)

    return draw


def draw_circuit_traces(draw: ImageDraw.Draw, seed=42):
    """Draw faint circuit-board trace lines."""
    random.seed(seed)
    for _ in range(18):
        x1 = random.randint(0, W)
        y1 = random.randint(0, H)
        # horizontal then vertical (L-shape)
        x2 = random.randint(0, W)
        y2 = y1
        x3 = x2
        y3 = random.randint(0, H)
        alpha_color = (BLUE[0], BLUE[1], BLUE[2])
        draw.line([(x1, y1), (x2, y2)], fill=(15, 45, 65), width=1)
        draw.line([(x2, y2), (x3, y3)], fill=(15, 45, 65), width=1)
        # dot at corner
        draw.ellipse([(x2-2, y2-2), (x2+2, y2+2)], fill=(20, 60, 88))


def draw_hex_grid(draw: ImageDraw.Draw, offset_x=800, offset_y=50, cols=5, rows=7, size=55, alpha_mul=0.25):
    """Draw a partial hex grid in the background."""
    for row in range(rows):
        for col in range(cols):
            cx = offset_x + col * size * 1.75
            if row % 2 == 1:
                cx += size * 0.875
            cy = offset_y + row * size * 1.52
            pts = []
            for i in range(6):
                angle = math.radians(60 * i - 30)
                pts.append((cx + size * 0.9 * math.cos(angle),
                             cy + size * 0.9 * math.sin(angle)))
            # faint hex outline
            draw.polygon(pts, outline=(18, 35, 52), fill=None)


def draw_glow_line(draw: ImageDraw.Draw, y=H-160, color=BLUE, width=2):
    """Draw a horizontal glow accent line."""
    # Outer glow
    for offset in range(6, 0, -1):
        alpha = int(255 * (1 - offset / 7) * 0.15)
        c = (color[0], color[1], color[2])
        draw.line([(0, y - offset), (W, y - offset)], fill=c, width=1)
        draw.line([(0, y + offset), (W, y + offset)], fill=c, width=1)
    draw.line([(0, y), (W, y)], fill=color, width=width)


def draw_side_bar(draw: ImageDraw.Draw, x=60, color=ORANGE, height=220):
    """Draw a vertical accent bar."""
    for offset in range(5, 0, -1):
        draw.line([(x - offset, H//2 - height//2), (x - offset, H//2 + height//2)],
                  fill=(color[0]//3, color[1]//3, color[2]//3), width=1)
        draw.line([(x + offset, H//2 - height//2), (x + offset, H//2 + height//2)],
                  fill=(color[0]//3, color[1]//3, color[2]//3), width=1)
    draw.line([(x, H//2 - height//2), (x, H//2 + height//2)], fill=color, width=2)


def draw_dot_scatter(draw: ImageDraw.Draw, seed=7):
    """Scatter small dots for star-like texture."""
    random.seed(seed)
    for _ in range(120):
        x = random.randint(0, W)
        y = random.randint(0, H)
        size = random.choice([1, 1, 1, 2])
        brightness = random.randint(30, 90)
        c = (brightness, brightness + 10, brightness + 20)
        draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=c)


def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current = []
    for word in words:
        test = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_title(draw, img, title_lines, font_large, font_small=None, start_y=None, line_spacing=18):
    """Draw title lines centered with drop-shadow."""
    # Measure total block height
    line_heights = []
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=font_large)
        line_heights.append(bbox[3] - bbox[1])

    total_h = sum(line_heights) + line_spacing * (len(title_lines) - 1)

    if start_y is None:
        start_y = (H - total_h) // 2 - 20  # slight upward offset

    y = start_y
    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=font_large)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = (W - lw) // 2

        # Shadow
        draw.text((x + 3, y + 3), line, font=font_large, fill=(0, 0, 0))
        # Text
        draw.text((x, y), line, font=font_large, fill=WHITE)
        y += lh + line_spacing

    return y  # return bottom of title block


def draw_branding(draw, font):
    """Draw PUREBRAIN.ai in bottom-right corner."""
    # Blue PUREBRAIN + orange .ai
    pb_text = "PUREBR"
    ai_text = "AI"
    n_text = "N.ai"

    bbox_pb = draw.textbbox((0, 0), pb_text, font=font)
    bbox_ai = draw.textbbox((0, 0), ai_text, font=font)
    bbox_n = draw.textbbox((0, 0), n_text, font=font)

    total_w = (bbox_pb[2] - bbox_pb[0]) + (bbox_ai[2] - bbox_ai[0]) + (bbox_n[2] - bbox_n[0])
    x = W - total_w - 30
    y = H - 40

    draw.text((x, y), pb_text, font=font, fill=BLUE)
    x += bbox_pb[2] - bbox_pb[0]
    draw.text((x, y), ai_text, font=font, fill=ORANGE)
    x += bbox_ai[2] - bbox_ai[0]
    draw.text((x, y), n_text, font=font, fill=BLUE)


# ============================================================
# Banner 1: "Most AI Agents Break the Moment You Ask Where the Data Goes"
# ============================================================
def banner_1(output_path):
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = make_base(img)

    draw_dot_scatter(draw, seed=11)
    draw_circuit_traces(draw, seed=22)
    draw_hex_grid(draw, offset_x=750, offset_y=20, cols=5, rows=8, size=60)

    # Orange glow line near bottom
    draw_glow_line(draw, y=H-120, color=ORANGE, width=2)
    draw_glow_line(draw, y=90, color=BLUE, width=1)

    # Left accent bar (blue)
    draw_side_bar(draw, x=48, color=BLUE, height=260)

    # Draw a "broken" data shield icon (simplified geometric)
    # Shield outline top-left region
    shield_cx, shield_cy = 200, H // 2
    shield_pts = [
        (shield_cx, shield_cy - 90),
        (shield_cx + 60, shield_cy - 60),
        (shield_cx + 60, shield_cy + 20),
        (shield_cx, shield_cy + 70),
        (shield_cx - 60, shield_cy + 20),
        (shield_cx - 60, shield_cy - 60),
    ]
    draw.polygon(shield_pts, outline=BLUE, fill=(8, 22, 38))
    # Crack through the shield
    draw.line([(shield_cx - 10, shield_cy - 80), (shield_cx + 25, shield_cy - 20),
               (shield_cx - 15, shield_cy + 30), (shield_cx + 20, shield_cy + 65)],
              fill=ORANGE, width=3)
    # Lock symbol inside
    draw.ellipse([(shield_cx - 18, shield_cy - 35), (shield_cx + 18, shield_cy + 0)],
                 outline=(42, 147, 193), fill=None, width=2)
    draw.rectangle([(shield_cx - 22, shield_cy - 8), (shield_cx + 22, shield_cy + 22)],
                   outline=(42, 147, 193), fill=(12, 30, 50))
    draw.rectangle([(shield_cx - 5, shield_cy + 2), (shield_cx + 5, shield_cy + 15)],
                   fill=ORANGE)

    # Title
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 62)
        font_sub = ImageFont.truetype(FONT_REG, 24)
        font_brand = ImageFont.truetype(FONT_BOLD, 20)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_brand = font_title

    # Adjust layout: title right of center (shield is left)
    title_x_start = 290  # leave room for shield
    title_max_w = W - title_x_start - 60

    # Pre-defined 3-line split that fits the space
    rendered_lines = [
        "Most AI Agents Break",
        "the Moment You Ask",
        "Where the Data Goes",
    ]

    line_heights = []
    for line in rendered_lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        line_heights.append(bbox[3] - bbox[1])

    spacing = 16
    total_h = sum(line_heights) + spacing * (len(rendered_lines) - 1)
    start_y = (H - total_h) // 2 - 30

    y = start_y
    for i, line in enumerate(rendered_lines):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = title_x_start + (title_max_w - lw) // 2

        # Shadow
        draw.text((x + 3, y + 3), line, font=font_title, fill=(0, 0, 0))
        # Last line: highlight "Data Goes" in orange if present
        if "Data Goes" in line:
            idx = line.index("Data Goes")
            part1 = line[:idx]
            part2 = "Data Goes"
            p1b = draw.textbbox((0, 0), part1, font=font_title)
            p1w = p1b[2] - p1b[0]
            draw.text((x, y), part1, font=font_title, fill=WHITE)
            draw.text((x + p1w, y), part2, font=font_title, fill=ORANGE)
        else:
            draw.text((x, y), line, font=font_title, fill=WHITE)

        y += lh + spacing

    # Subtitle
    sub = "AI data security shouldn't be a mystery"
    sb = draw.textbbox((0, 0), sub, font=font_sub)
    sw = sb[2] - sb[0]
    draw.text(((W - sw) // 2, y + 18), sub, font=font_sub, fill=(150, 190, 210))

    draw_branding(draw, font_brand)

    img.save(output_path, "JPEG", quality=92)
    print(f"Saved: {output_path}")


# ============================================================
# Banner 2: "Why Your AI Should Have a Name"
# ============================================================
def banner_2(output_path):
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = make_base(img)

    draw_dot_scatter(draw, seed=33)
    draw_hex_grid(draw, offset_x=60, offset_y=30, cols=4, rows=7, size=55)
    draw_circuit_traces(draw, seed=44)

    draw_glow_line(draw, y=H-100, color=BLUE, width=2)
    draw_glow_line(draw, y=H-104, color=BLUE, width=1)

    # Right accent bar (orange)
    draw_side_bar(draw, x=W-48, color=ORANGE, height=200)

    # Identity icon: stylized "AI" tag with a name label
    icon_cx, icon_cy = W - 200, H // 2
    # Badge/tag shape
    badge_pts = [
        (icon_cx - 70, icon_cy - 80),
        (icon_cx + 70, icon_cy - 80),
        (icon_cx + 70, icon_cy + 50),
        (icon_cx + 20, icon_cy + 80),
        (icon_cx - 20, icon_cy + 80),
        (icon_cx - 70, icon_cy + 50),
    ]
    draw.polygon(badge_pts, outline=BLUE, fill=(8, 18, 32))
    # Name line inside badge
    try:
        font_badge = ImageFont.truetype(FONT_BOLD, 22)
        font_badge_sm = ImageFont.truetype(FONT_REG, 14)
    except Exception:
        font_badge = ImageFont.load_default()
        font_badge_sm = font_badge

    name_text = "AETHER"
    nb = draw.textbbox((0, 0), name_text, font=font_badge)
    nw = nb[2] - nb[0]
    draw.text((icon_cx - nw // 2, icon_cy - 30), name_text, font=font_badge, fill=ORANGE)
    # Underline
    draw.line([(icon_cx - 40, icon_cy + 0), (icon_cx + 40, icon_cy + 0)], fill=BLUE, width=1)
    # "AI Partner" sub
    sub_text = "AI Partner"
    sb2 = draw.textbbox((0, 0), sub_text, font=font_badge_sm)
    sw2 = sb2[2] - sb2[0]
    draw.text((icon_cx - sw2 // 2, icon_cy + 8), sub_text, font=font_badge_sm, fill=LIGHT_BLUE)
    # Hole at top of badge
    draw.ellipse([(icon_cx - 12, icon_cy - 90), (icon_cx + 12, icon_cy - 70)],
                 outline=BLUE, fill=BG_COLOR)

    # Title
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 68)
        font_sub = ImageFont.truetype(FONT_REG, 26)
        font_brand = ImageFont.truetype(FONT_BOLD, 20)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_brand = font_title

    title_max_w = W - 340  # leave room for icon on right
    lines_raw = ["Why Your AI Should", "Have a Name"]

    rendered = []
    for line in lines_raw:
        wrapped = wrap_text(line, font_title, title_max_w, draw)
        rendered.extend(wrapped)

    spacing = 18
    line_heights = [draw.textbbox((0, 0), l, font=font_title)[3] -
                    draw.textbbox((0, 0), l, font=font_title)[1] for l in rendered]
    total_h = sum(line_heights) + spacing * (len(rendered) - 1)
    start_y = (H - total_h) // 2 - 35
    left_margin = 100

    y = start_y
    for i, line in enumerate(rendered):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = left_margin

        draw.text((x + 3, y + 3), line, font=font_title, fill=(0, 0, 0))
        if i == 1:
            # "Have a " white, "Name" orange
            part1 = "Have a "
            part2 = "Name"
            p1b = draw.textbbox((0, 0), part1, font=font_title)
            p1w = p1b[2] - p1b[0]
            draw.text((x, y), part1, font=font_title, fill=WHITE)
            draw.text((x + p1w, y), part2, font=font_title, fill=ORANGE)
        else:
            draw.text((x, y), line, font=font_title, fill=WHITE)
        y += lh + spacing

    sub = "Identity transforms how AI shows up for you"
    sb = draw.textbbox((0, 0), sub, font=font_sub)
    draw.text((left_margin, y + 20), sub, font=font_sub, fill=(150, 190, 210))

    draw_branding(draw, font_brand)
    img.save(output_path, "PNG")
    print(f"Saved: {output_path}")


# ============================================================
# Banner 3: "Why Enterprises Are Betting on Agentic AI"
# ============================================================
def banner_3(output_path):
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = make_base(img)

    draw_dot_scatter(draw, seed=55)
    draw_circuit_traces(draw, seed=66)
    draw_hex_grid(draw, offset_x=700, offset_y=0, cols=6, rows=9, size=65)

    draw_glow_line(draw, y=H - 110, color=ORANGE, width=2)
    draw_glow_line(draw, y=80, color=BLUE, width=1)

    # Center-bottom: upward chart bars (enterprise growth concept)
    bar_base_y = H - 120
    bar_heights = [60, 100, 140, 180, 230]
    bar_colors = [DIM_BLUE, DIM_BLUE, BLUE, BLUE, ORANGE]
    bar_w = 28
    bar_gap = 14
    bar_start_x = W // 2 - (len(bar_heights) * (bar_w + bar_gap)) // 2

    for i, (bh, bc) in enumerate(zip(bar_heights, bar_colors)):
        bx = bar_start_x + i * (bar_w + bar_gap)
        draw.rectangle([(bx, bar_base_y - bh), (bx + bar_w, bar_base_y)],
                        fill=bc)
        # Glow top edge
        draw.rectangle([(bx, bar_base_y - bh), (bx + bar_w, bar_base_y - bh + 3)],
                        fill=WHITE if bc == ORANGE else LIGHT_BLUE)

    # Network nodes (agent network concept)
    nodes = [(130, 160), (200, 300), (155, 450), (250, 380), (290, 200)]
    for i, (nx, ny) in enumerate(nodes):
        draw.ellipse([(nx - 10, ny - 10), (nx + 10, ny + 10)],
                     fill=BLUE if i < 4 else ORANGE, outline=WHITE)
    for i in range(len(nodes) - 1):
        draw.line([nodes[i], nodes[i+1]], fill=(30, 80, 110), width=1)
        draw.line([nodes[0], nodes[-1]], fill=(30, 80, 110), width=1)

    # Title
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 60)
        font_sub = ImageFont.truetype(FONT_REG, 25)
        font_brand = ImageFont.truetype(FONT_BOLD, 20)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_brand = font_title

    title_lines_raw = ["Why Enterprises Are", "Betting on Agentic AI"]
    title_max_w = W - 200

    rendered = []
    for line in title_lines_raw:
        wrapped = wrap_text(line, font_title, title_max_w, draw)
        rendered.extend(wrapped)

    spacing = 16
    line_heights = [draw.textbbox((0, 0), l, font=font_title)[3] -
                    draw.textbbox((0, 0), l, font=font_title)[1] for l in rendered]
    total_h = sum(line_heights) + spacing * (len(rendered) - 1)
    start_y = (H - total_h) // 2 - 70  # push up to make room for bars

    y = start_y
    for i, line in enumerate(rendered):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = (W - lw) // 2

        draw.text((x + 3, y + 3), line, font=font_title, fill=(0, 0, 0))
        if i == 1:
            # "Betting on " white, "Agentic AI" orange
            part1 = "Betting on "
            part2 = "Agentic AI"
            p1b = draw.textbbox((0, 0), part1, font=font_title)
            p1w = p1b[2] - p1b[0]
            draw.text((x, y), part1, font=font_title, fill=WHITE)
            draw.text((x + p1w, y), part2, font=font_title, fill=ORANGE)
        else:
            draw.text((x, y), line, font=font_title, fill=WHITE)
        y += lh + spacing

    sub = "The enterprise AI revolution isn't coming — it's here"
    sb = draw.textbbox((0, 0), sub, font=font_sub)
    sw = sb[2] - sb[0]
    draw.text(((W - sw) // 2, y + 18), sub, font=font_sub, fill=(150, 190, 210))

    draw_branding(draw, font_brand)
    img.save(output_path, "PNG")
    print(f"Saved: {output_path}")


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    BASE = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog"

    banner_1(f"{BASE}/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/banner.jpg")
    banner_2(f"{BASE}/why-your-ai-should-have-a-name/banner.png")
    banner_3(f"{BASE}/why-enterprises-are-betting-on-agentic-ai/banner.png")

    print("All 3 banners generated successfully.")
