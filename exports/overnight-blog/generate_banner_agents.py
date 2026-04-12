#!/usr/bin/env python3
"""
Banner generator for: "The Age of AI Agents"
PureBrain.ai brand: Orange #f1420b, Cerulean Blue #2a93c1, Dark bg #080a12
Size: 1200x630px (OG image standard)
"""

import math
import random

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available, using matplotlib fallback")

import os

OUTPUT_PATH = "/home/jared/projects/AI-CIV/aether/exports/overnight-blog/the-age-of-ai-agents-banner.png"

# Brand colors
BG_COLOR = (8, 10, 18)           # #080a12
ORANGE = (241, 66, 11)            # #f1420b
BLUE = (42, 147, 193)             # #2a93c1
WHITE = (255, 255, 255)
WHITE_DIM = (200, 210, 230)
DARK_BLUE = (15, 25, 45)
GLOW_BLUE = (42, 147, 193, 60)
GLOW_ORANGE = (241, 66, 11, 40)

W, H = 1200, 630

def hex_point(cx, cy, radius, angle_deg):
    a = math.radians(angle_deg)
    return (cx + radius * math.cos(a), cy + radius * math.sin(a))

def draw_hexagon(draw, cx, cy, radius, outline_color, width=2, fill=None):
    points = [hex_point(cx, cy, radius, 60 * i - 30) for i in range(6)]
    if fill:
        draw.polygon(points, fill=fill, outline=outline_color)
    else:
        draw.polygon(points, outline=outline_color, fill=(0, 0, 0, 0))
    for i in range(6):
        draw.line([points[i], points[(i+1)%6]], fill=outline_color, width=width)

def draw_node_network(draw, nodes, color, alpha=80):
    """Draw glowing dots and connecting lines for agent network"""
    c = color + (alpha,)
    for node in nodes:
        x, y, r = node
        draw.ellipse([x-r, y-r, x+r, y+r], fill=c)
        # glow ring
        glow = color + (30,)
        draw.ellipse([x-r*2, y-r*2, x+r*2, y+r*2], fill=glow)

def make_banner():
    img = Image.new("RGBA", (W, H), BG_COLOR + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- BACKGROUND GRADIENT LAYERS ---
    # Deep dark center, subtle radial feel
    for i in range(60, 0, -1):
        alpha = int(8 * (60 - i) / 60)
        r = int(W * 0.9 * i / 60)
        box = [W//2 - r, H//2 - r, W//2 + r, H//2 + r]
        draw.ellipse(box, fill=DARK_BLUE + (alpha,))

    # Subtle blue glow upper-left (source of intelligence)
    for i in range(30, 0, -1):
        alpha = int(15 * (30 - i) / 30)
        r = int(350 * i / 30)
        draw.ellipse([80 - r, 60 - r, 80 + r, 60 + r], fill=BLUE + (alpha,))

    # Subtle orange glow lower-right (action/output)
    for i in range(30, 0, -1):
        alpha = int(12 * (30 - i) / 30)
        r = int(300 * i / 30)
        draw.ellipse([1100 - r, 540 - r, 1100 + r, 540 + r], fill=ORANGE + (alpha,))

    # --- HEXAGON NETWORK (agent nodes) ---
    # Central large hex — orchestrator
    cx_main, cy_main = 920, 315
    draw_hexagon(draw, cx_main, cy_main, 90, BLUE + (180,), width=2)
    draw_hexagon(draw, cx_main, cy_main, 78, BLUE + (60,), width=1, fill=BLUE + (15,))

    # 6 satellite hexes — specialist agents
    satellite_positions = []
    for i in range(6):
        angle = 60 * i - 30
        dist = 165
        sx = cx_main + dist * math.cos(math.radians(angle))
        sy = cy_main + dist * math.sin(math.radians(angle))
        satellite_positions.append((sx, sy))
        # Connection lines (neural threads)
        draw.line(
            [(cx_main, cy_main), (sx, sy)],
            fill=BLUE + (55,),
            width=1
        )
        # Satellite hex
        col = ORANGE if i % 2 == 0 else BLUE
        draw_hexagon(draw, int(sx), int(sy), 40, col + (160,), width=1)
        draw_hexagon(draw, int(sx), int(sy), 33, col + (40,), width=1, fill=col + (10,))

    # Outer ring connections (agents talking to each other)
    for i in range(6):
        x1, y1 = satellite_positions[i]
        x2, y2 = satellite_positions[(i + 1) % 6]
        draw.line([(int(x1), int(y1)), (int(x2), int(y2))], fill=BLUE + (20,), width=1)

    # Floating data dots — network activity
    random.seed(42)
    dots = [
        (700, 200, 4), (780, 280, 3), (840, 160, 5),
        (960, 200, 3), (1050, 280, 4), (1080, 380, 3),
        (1020, 460, 5), (880, 490, 3), (760, 430, 4),
        (680, 340, 3), (740, 130, 4), (1000, 130, 3),
        (1120, 200, 4), (1130, 420, 3), (850, 560, 4),
    ]
    for dx, dy, dr in dots:
        c = BLUE if random.random() > 0.4 else ORANGE
        draw.ellipse([dx-dr, dy-dr, dx+dr, dy+dr], fill=c + (120,))
        draw.ellipse([dx-dr*2, dy-dr*2, dx+dr*2, dy+dr*2], fill=c + (25,))

    # --- TYPOGRAPHY ---
    # Try to find a font, fall back to default
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    font_path = None
    for fp in font_paths:
        if os.path.exists(fp):
            font_path = fp
            break

    font_path_regular = None
    regular_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for fp in regular_paths:
        if os.path.exists(fp):
            font_path_regular = fp
            break

    if font_path:
        font_logo = ImageFont.truetype(font_path, 48)
        font_title_large = ImageFont.truetype(font_path, 62)
        font_title_small = ImageFont.truetype(font_path, 44)
        font_subtitle = ImageFont.truetype(font_path_regular or font_path, 22)
        font_tag = ImageFont.truetype(font_path_regular or font_path, 18)
    else:
        font_logo = ImageFont.load_default()
        font_title_large = font_logo
        font_title_small = font_logo
        font_subtitle = font_logo
        font_tag = font_logo

    # --- PUREBRAIN.ai LOGO (brand color rule) ---
    # "PUREBR" = Blue, "AI" = Orange, "N" = Blue, ".ai" = White lowercase
    logo_x = 90
    logo_y = 68

    # Calculate character widths for proper spacing
    pb_text = "PUREBRAIN.ai"
    # Render each segment
    seg_purebr = "PUREBR"
    seg_ai = "AI"
    seg_n = "N"
    seg_dotai = ".ai"

    draw.text((logo_x, logo_y), seg_purebr, font=font_logo, fill=BLUE)
    # get width of PUREBR
    bb = draw.textbbox((logo_x, logo_y), seg_purebr, font=font_logo)
    x_after_purebr = bb[2]
    draw.text((x_after_purebr, logo_y), seg_ai, font=font_logo, fill=ORANGE)
    bb2 = draw.textbbox((x_after_purebr, logo_y), seg_ai, font=font_logo)
    x_after_ai = bb2[2]
    draw.text((x_after_ai, logo_y), seg_n, font=font_logo, fill=BLUE)
    bb3 = draw.textbbox((x_after_ai, logo_y), seg_n, font=font_logo)
    x_after_n = bb3[2]
    draw.text((x_after_n, logo_y), seg_dotai, font=font_logo, fill=WHITE)

    # Orange accent line under logo
    line_y = logo_y + 56
    draw.line([(logo_x, line_y), (logo_x + 340, line_y)], fill=ORANGE + (180,), width=2)

    # --- MAIN TITLE ---
    # "THE AGE OF" — smaller, white
    # "AI AGENTS" — large, blue→orange gradient simulation
    title_x = 90
    title_y = 185

    # Eyebrow text
    eyebrow = "THE AGE OF"
    draw.text((title_x, title_y), eyebrow, font=font_subtitle, fill=WHITE_DIM + (200,))

    # Main headline — two lines
    line1 = "AI AGENTS:"
    line2 = "YOUR BUSINESS"
    line3 = "NEEDS A TEAM"

    # Line 1 in orange (AI) + blue (AGENTS:)
    draw.text((title_x, title_y + 34), "AI ", font=font_title_large, fill=ORANGE)
    bb_ai = draw.textbbox((title_x, title_y + 34), "AI ", font=font_title_large)
    draw.text((bb_ai[2], title_y + 34), "AGENTS:", font=font_title_large, fill=BLUE)

    # Line 2 white
    draw.text((title_x, title_y + 34 + 68), line2, font=font_title_small, fill=WHITE)

    # Line 3 white dim
    draw.text((title_x, title_y + 34 + 68 + 52), line3, font=font_title_small, fill=WHITE_DIM)

    # --- SUBTITLE ---
    sub_y = title_y + 34 + 68 + 52 + 58
    subtitle = "Why one AI is no longer enough — and what the"
    subtitle2 = "future of AI strategy actually looks like."
    draw.text((title_x, sub_y), subtitle, font=font_tag, fill=WHITE_DIM + (180,))
    draw.text((title_x, sub_y + 26), subtitle2, font=font_tag, fill=WHITE_DIM + (180,))

    # --- AUTHOR TAG ---
    author_y = H - 75
    draw.text((title_x, author_y), "By Aether  |  PureBrain.ai", font=font_tag, fill=BLUE + (200,))

    # Horizontal rule above author
    draw.line([(title_x, author_y - 15), (580, author_y - 15)], fill=BLUE + (60,), width=1)

    # --- CENTRAL ORB GLOW (behind hex network) ---
    for i in range(20, 0, -1):
        alpha = int(18 * (20 - i) / 20)
        r = int(120 * i / 20)
        draw.ellipse(
            [cx_main - r, cy_main - r, cx_main + r, cy_main + r],
            fill=BLUE + (alpha,)
        )

    # Central dot
    draw.ellipse([cx_main-8, cy_main-8, cx_main+8, cy_main+8], fill=WHITE + (220,))

    # --- FINALIZE ---
    # Convert to RGB for PNG save
    final = Image.new("RGB", (W, H), BG_COLOR)
    final.paste(img, mask=img.split()[3])
    final.save(OUTPUT_PATH, "PNG", optimize=True)
    print(f"Banner saved: {OUTPUT_PATH}")
    return OUTPUT_PATH


if PIL_AVAILABLE:
    result = make_banner()
    print(f"SUCCESS: {result}")
else:
    # Matplotlib fallback
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import RegularPolygon
    import numpy as np

    fig, ax = plt.subplots(figsize=(12, 6.3), facecolor='#080a12')
    ax.set_xlim(0, 1200)
    ax.set_ylim(0, 630)
    ax.set_aspect('equal')
    ax.axis('off')

    # Background glow
    from matplotlib.patches import Circle
    for r, alpha in [(400, 0.04), (300, 0.06), (200, 0.08)]:
        c = Circle((950, 315), r, color='#2a93c1', alpha=alpha)
        ax.add_patch(c)
    for r, alpha in [(300, 0.03), (200, 0.05)]:
        c = Circle((100, 580), r, color='#f1420b', alpha=alpha)
        ax.add_patch(c)

    # Hex network
    cx, cy = 920, 315
    main_hex = RegularPolygon((cx, cy), numVertices=6, radius=90,
                               orientation=np.pi/6, fill=False,
                               edgecolor='#2a93c1', linewidth=2, alpha=0.8)
    ax.add_patch(main_hex)

    for i in range(6):
        angle = np.radians(60 * i - 30)
        dist = 165
        sx = cx + dist * np.cos(angle)
        sy = cy + dist * np.sin(angle)
        ax.plot([cx, sx], [cy, sy], color='#2a93c1', alpha=0.3, linewidth=1)
        col = '#f1420b' if i % 2 == 0 else '#2a93c1'
        h = RegularPolygon((sx, sy), numVertices=6, radius=40,
                            orientation=np.pi/6, fill=False,
                            edgecolor=col, linewidth=1.5, alpha=0.7)
        ax.add_patch(h)

    # Dots
    ax.scatter([700,780,840,960,1050,1080,1020,880,760,680],
               [200,280,160,200,280,380,460,490,430,340],
               s=[20,15,25,15,20,15,25,15,20,15],
               c=['#2a93c1']*6 + ['#f1420b']*4, alpha=0.7)

    # PUREBRAIN.ai logo
    ax.text(90, 545, 'PUREBR', color='#2a93c1', fontsize=32, fontweight='bold', va='bottom')
    ax.text(270, 545, 'AI', color='#f1420b', fontsize=32, fontweight='bold', va='bottom')
    ax.text(307, 545, 'N', color='#2a93c1', fontsize=32, fontweight='bold', va='bottom')
    ax.text(335, 545, '.ai', color='white', fontsize=32, va='bottom')

    # Title
    ax.text(90, 475, 'THE AGE OF', color='#c8d8e8', fontsize=16, va='bottom', alpha=0.9)
    ax.text(90, 415, 'AI ', color='#f1420b', fontsize=58, fontweight='bold', va='bottom')
    ax.text(175, 415, 'AGENTS:', color='#2a93c1', fontsize=58, fontweight='bold', va='bottom')
    ax.text(90, 355, 'Your Business Needs a Team', color='white', fontsize=34, fontweight='bold', va='bottom')
    ax.text(90, 300, 'Why one AI is no longer enough.', color='#a0b8cc', fontsize=18, va='bottom', alpha=0.85)
    ax.text(90, 270, 'By Aether | PureBrain.ai', color='#2a93c1', fontsize=14, va='bottom', alpha=0.8)

    plt.tight_layout(pad=0)
    plt.savefig(OUTPUT_PATH, dpi=100, bbox_inches='tight',
                facecolor='#080a12', edgecolor='none')
    plt.close()
    print(f"SUCCESS (matplotlib): {OUTPUT_PATH}")
