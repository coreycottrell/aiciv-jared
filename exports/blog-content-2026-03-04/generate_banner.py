#!/usr/bin/env python3
"""
PureBrain Blog Banner Generator — "The Context Tax"
Creates 1200x630 OG banner with PureBrain branding
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# ─── Paths ────────────────────────────────────────────────────────────────────
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
FONT_REG  = os.path.join(FONT_DIR, "DejaVuSans.ttf")
OUT_DIR   = "/home/jared/projects/AI-CIV/aether/exports/blog-content-2026-03-04"

# ─── Brand Colours ────────────────────────────────────────────────────────────
BG         = (8,  10, 18)       # #080a12
BLUE       = (42, 147, 193)     # #2a93c1
ORANGE     = (241, 66, 11)      # #f1420b
WHITE      = (255, 255, 255)
GRAY       = (136, 146, 164)
DIM_WHITE  = (200, 210, 225)
DARK_GRID  = (18, 22, 38)

SIZE = (1200, 630)
SAFE_MARGIN = 60  # Keep text away from edges for mobile


def font(size, bold=True):
    path = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(path, size)


def draw_grid(draw, spacing=40):
    """Subtle tech grid background"""
    for x in range(0, SIZE[0], spacing):
        draw.line([(x, 0), (x, SIZE[1])], fill=DARK_GRID, width=1)
    for y in range(0, SIZE[1], spacing):
        draw.line([(0, y), (SIZE[0], y)], fill=DARK_GRID, width=1)


def draw_hexagon(draw, cx, cy, radius, color, width=2):
    """Draw a hexagon outline"""
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))
    points.append(points[0])
    draw.line(points, fill=color, width=width)


def draw_brain_circuit(draw, cx, cy, radius):
    """Draw stylized brain/circuit pattern"""
    # Central node
    draw.ellipse([cx-4, cy-4, cx+4, cy+4], fill=BLUE)

    # Radiating connections
    for i in range(8):
        angle = math.radians(45 * i)
        x1 = cx + radius * 0.3 * math.cos(angle)
        y1 = cy + radius * 0.3 * math.sin(angle)
        x2 = cx + radius * 0.7 * math.cos(angle)
        y2 = cy + radius * 0.7 * math.sin(angle)

        # Line
        draw.line([(cx, cy), (x1, y1)], fill=(BLUE[0]//3, BLUE[1]//3, BLUE[2]//3), width=1)
        draw.line([(x1, y1), (x2, y2)], fill=(BLUE[0]//2, BLUE[1]//2, BLUE[2]//2), width=1)

        # Node at end
        draw.ellipse([x2-2, y2-2, x2+2, y2+2], fill=BLUE)

        # Extended connections on some
        if i % 2 == 0:
            x3 = cx + radius * math.cos(angle)
            y3 = cy + radius * math.sin(angle)
            draw.line([(x2, y2), (x3, y3)], fill=(BLUE[0]//4, BLUE[1]//4, BLUE[2]//4), width=1)
            draw.ellipse([x3-2, y3-2, x3+2, y3+2], fill=(BLUE[0]//2, BLUE[1]//2, BLUE[2]//2))


def draw_disconnect_symbol(draw, x, y, size=30):
    """Draw a broken connection / disconnect symbol"""
    # Left side
    draw.line([(x - size, y), (x - 4, y)], fill=ORANGE, width=2)
    draw.ellipse([x - size - 3, y - 3, x - size + 3, y + 3], fill=ORANGE)

    # Gap (the "tax")

    # Right side
    draw.line([(x + 4, y), (x + size, y)], fill=GRAY, width=2)
    draw.ellipse([x + size - 3, y - 3, x + size + 3, y + 3], fill=GRAY)


def centered_text(draw, text, fnt, y, color):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    x = (SIZE[0] - w) // 2
    draw.text((x, y), text, font=fnt, fill=color)
    return w


def draw_purebrain_text(draw, y):
    """Draw PUREBRAIN.ai with proper color split — bottom right"""
    f = font(18)

    # Calculate total width first
    parts = [("PUREBR", BLUE), ("AI", ORANGE), ("N", BLUE), (".ai", WHITE)]
    total_w = 0
    for text, _ in parts:
        bbox = draw.textbbox((0, 0), text, font=f)
        total_w += bbox[2] - bbox[0]

    # Position bottom-right with margin
    x = SIZE[0] - total_w - SAFE_MARGIN
    for text, color in parts:
        draw.text((x, y), text, font=f, fill=color)
        bbox = draw.textbbox((0, 0), text, font=f)
        x += bbox[2] - bbox[0]


def generate_banner():
    img = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(img)

    # Background grid
    draw_grid(draw)

    # Decorative hexagons (scattered, semi-transparent feel)
    hexagon_positions = [
        (120, 100, 45), (1080, 80, 35), (180, 520, 30),
        (1050, 480, 50), (950, 150, 25), (80, 350, 20),
        (1130, 320, 28), (300, 80, 22), (850, 550, 32),
    ]
    for hx, hy, hr in hexagon_positions:
        hex_color = (BLUE[0]//4, BLUE[1]//4, BLUE[2]//4)
        draw_hexagon(draw, hx, hy, hr, hex_color, width=1)

    # Brain circuit pattern on right side
    draw_brain_circuit(draw, 1000, 300, 120)

    # Disconnected nodes on left (representing fragmentation)
    for i in range(5):
        dy = 180 + i * 60
        draw_disconnect_symbol(draw, 160, dy, size=25 + i * 3)

    # ─── Main Content ─────────────────────────────────────────────────────────

    # Top: Blog label
    centered_text(draw, "PUREBRAIN.AI BLOG", font(14, bold=False), SAFE_MARGIN + 10, GRAY)

    # Title line 1
    title_y = 160
    centered_text(draw, "THE CONTEXT TAX", font(58), title_y, WHITE)

    # Title line 2
    centered_text(draw, "What It Really Costs When Your AI", font(26, bold=False), title_y + 85, DIM_WHITE)

    # Title line 3
    centered_text(draw, "Starts Every Conversation From Zero", font(26, bold=False), title_y + 120, DIM_WHITE)

    # Accent line
    line_y = title_y + 170
    line_w = 200
    lx = (SIZE[0] - line_w) // 2
    draw.line([(lx, line_y), (lx + line_w, line_y)], fill=ORANGE, width=3)

    # Key stat
    stat_y = line_y + 30
    centered_text(draw, "76%", font(72), stat_y, ORANGE)
    centered_text(draw, "of enterprises hurt by disconnected AI", font(20, bold=False), stat_y + 85, GRAY)

    # Horizontal separator
    sep_y = stat_y + 130
    draw.line([(SAFE_MARGIN + 100, sep_y), (SIZE[0] - SAFE_MARGIN - 100, sep_y)], fill=(30, 35, 55), width=1)

    # Bottom stats row
    bottom_y = sep_y + 15
    stats = [
        ("46.5%", "switch 2+ AI tools\nfor ONE task"),
        ("$85K/mo", "avg enterprise\nAI spend"),
        ("9%", "annual work time\nlost to tool switching"),
    ]

    col_w = (SIZE[0] - 2 * SAFE_MARGIN) // 3
    for i, (num, desc) in enumerate(stats):
        cx = SAFE_MARGIN + col_w * i + col_w // 2

        # Number
        f_num = font(28)
        bbox = draw.textbbox((0, 0), num, font=f_num)
        nw = bbox[2] - bbox[0]
        draw.text((cx - nw // 2, bottom_y), num, font=f_num, fill=BLUE)

        # Description
        f_desc = font(11, bold=False)
        for j, line in enumerate(desc.split("\n")):
            bbox = draw.textbbox((0, 0), line, font=f_desc)
            lw = bbox[2] - bbox[0]
            draw.text((cx - lw // 2, bottom_y + 35 + j * 16), line, font=f_desc, fill=GRAY)

    # PUREBRAIN.ai branding — bottom right corner
    draw_purebrain_text(draw, SIZE[1] - 35)

    # Save
    out_path = os.path.join(OUT_DIR, "the-context-tax-banner.png")
    img.save(out_path, "PNG", quality=95)
    print(f"Banner saved: {out_path}")
    return out_path


if __name__ == "__main__":
    generate_banner()
