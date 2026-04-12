#!/usr/bin/env python3
"""
Demo: Programmatic content creation using Pillow.
Shows what we can generate RIGHT NOW on our VPS at $0 cost.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont

# --- Brand Constants ---
W, H = 1200, 630
BG = (8, 10, 18)           # #080a12
BLUE = (42, 147, 193)      # #2a93c1
ORANGE = (241, 66, 11)     # #f1420b
WHITE = (255, 255, 255)
DIM_BLUE = (20, 60, 90)
DIM_ORANGE = (80, 22, 4)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def draw_gradient_bg(draw):
    """Dark gradient background with subtle blue shift."""
    for x in range(W):
        f = x / W
        r = int(BG[0] + f * 8)
        g = int(BG[1] + f * 6)
        b = int(BG[2] + f * 16)
        draw.line([(x, 0), (x, H)], fill=(r, g, b))


def draw_hex_grid(draw):
    """Subtle hexagonal grid pattern."""
    hex_size = 40
    for row in range(-1, H // (hex_size) + 2):
        for col in range(-1, W // (hex_size * 2) + 2):
            cx = col * hex_size * 1.75 + (row % 2) * hex_size * 0.875
            cy = row * hex_size * 1.5
            points = []
            for i in range(6):
                angle = math.pi / 3 * i + math.pi / 6
                px = cx + hex_size * 0.6 * math.cos(angle)
                py = cy + hex_size * 0.6 * math.sin(angle)
                points.append((px, py))
            if len(points) >= 6:
                draw.polygon(points, outline=(18, 22, 34))


def draw_glow(draw, cx, cy, radius, color, alpha_base=30):
    """Radial glow effect."""
    for r in range(radius, 0, -2):
        alpha = int(alpha_base * (r / radius))
        c = tuple(int(c * alpha / 255) for c in color)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)


def draw_neural_nodes(draw):
    """Neural network node visualization."""
    nodes = []
    random.seed(42)  # Reproducible
    for _ in range(12):
        x = random.randint(600, 1100)
        y = random.randint(80, 550)
        size = random.randint(3, 8)
        nodes.append((x, y, size))

    # Draw connections
    for i, (x1, y1, _) in enumerate(nodes):
        for j, (x2, y2, _) in enumerate(nodes):
            if i < j and random.random() > 0.6:
                dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                if dist < 300:
                    opacity = max(10, int(40 * (1 - dist / 300)))
                    draw.line([(x1, y1), (x2, y2)],
                              fill=(BLUE[0] // 4, BLUE[1] // 4, BLUE[2] // 4),
                              width=1)

    # Draw nodes
    for x, y, size in nodes:
        draw.ellipse([x - size, y - size, x + size, y + size],
                     fill=BLUE, outline=(BLUE[0] + 40, BLUE[1] + 40, BLUE[2] + 40))


def generate_demo_banner():
    """Generate a full PureBrain-branded demo banner."""
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Layers
    draw_gradient_bg(draw)
    draw_hex_grid(draw)
    draw_neural_nodes(draw)

    # Blue accent bar (left edge)
    draw.rectangle([0, 0, 5, H], fill=BLUE)

    # Orange accent line (bottom)
    draw.rectangle([0, H - 3, W, H], fill=ORANGE)

    # Top tag
    try:
        font_sm = ImageFont.truetype(FONT_REG, 14)
        font_tag = ImageFont.truetype(FONT_BOLD, 16)
        font_title = ImageFont.truetype(FONT_BOLD, 44)
        font_subtitle = ImageFont.truetype(FONT_REG, 22)
        font_footer = ImageFont.truetype(FONT_REG, 13)
    except OSError:
        font_sm = font_tag = font_title = font_subtitle = font_footer = ImageFont.load_default()

    # Tag line
    draw.text((60, 50), "PUREBRAIN.AI", fill=BLUE, font=font_tag)

    # Title
    draw.text((60, 120), "Own Your Content\nPipeline", fill=WHITE, font=font_title)

    # Orange divider
    draw.rectangle([60, 280, 200, 284], fill=ORANGE)

    # Subtitle
    draw.text((60, 310), "Stop paying per image. Stop renting creativity.", fill=(180, 190, 210), font=font_subtitle)
    draw.text((60, 345), "Open-source AI + programmatic generation = $0/image.", fill=(140, 150, 170), font=font_subtitle)

    # Stats boxes
    stats = [
        ("$0.00", "per image"),
        ("60+", "OS models"),
        ("63.8%", "beat ElevenLabs"),
    ]
    box_y = 420
    for i, (value, label) in enumerate(stats):
        bx = 60 + i * 180
        # Box background
        draw.rectangle([bx, box_y, bx + 160, box_y + 80],
                       fill=(14, 18, 30), outline=(30, 40, 60))
        draw.text((bx + 15, box_y + 10), value, fill=ORANGE, font=font_tag)
        draw.text((bx + 15, box_y + 40), label, fill=(120, 130, 150), font=font_sm)

    # Footer
    draw.text((60, H - 30), "The Neural Feed -- a training document by Aether -- AI Partner for PureTechnology.ai",
              fill=(60, 70, 90), font=font_footer)

    # Hex logo (top right area)
    cx, cy = 1050, 80
    hex_pts = []
    for i in range(6):
        angle = math.pi / 3 * i - math.pi / 6
        hex_pts.append((cx + 25 * math.cos(angle), cy + 25 * math.sin(angle)))
    draw.polygon(hex_pts, outline=BLUE, fill=(14, 18, 30))
    draw.text((cx - 8, cy - 8), "PB", fill=BLUE, font=font_tag)

    output_path = "/home/jared/exports/portal-files/demo-content-creation-banner.png"
    img.save(output_path, quality=95)
    print(f"Banner saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    path = generate_demo_banner()
    print(f"Demo banner generated at: {path}")
    print(f"Cost: $0.00")
    print(f"Time: <1 second")
    print(f"GPU required: No")
