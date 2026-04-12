#!/usr/bin/env python3
"""
Banner generator for PureBrain blog post: "AI Doesn't Make Your Team Smarter. It Makes the Gap Bigger."
Uses PIL/Pillow with Pure Technology brand colors.
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# Brand colors
PT_ORANGE = (241, 66, 11)       # #f1420b
PT_BLUE = (42, 147, 193)        # #2a93c1
PT_DARK_BG = (8, 12, 24)        # Near-black dark background
PT_MID_BG = (14, 22, 45)        # Dark navy
PT_BLUE_DARK = (20, 60, 90)     # Deeper blue for contrast
WHITE = (255, 255, 255)
WHITE_TRANSPARENT = (255, 255, 255, 180)

# Banner dimensions (1200x630 - standard OG image)
WIDTH = 1200
HEIGHT = 630

OUTPUT_PATH = "/home/jared/projects/AI-CIV/aether/to-jared/overnight-blog/ai-competence-divide - banner.png"


def draw_gradient_bg(draw, width, height):
    """Draw a deep dark gradient background with subtle blue tones."""
    for y in range(height):
        ratio = y / height
        r = int(PT_DARK_BG[0] + (PT_MID_BG[0] - PT_DARK_BG[0]) * ratio)
        g = int(PT_DARK_BG[1] + (PT_MID_BG[1] - PT_DARK_BG[1]) * ratio)
        b = int(PT_DARK_BG[2] + (PT_MID_BG[2] - PT_DARK_BG[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_neural_network(draw, cx, cy, radius=220):
    """Draw an abstract neural network / brain node visualization."""
    import random
    random.seed(42)

    # Outer glow ring
    for r_offset in range(3, 0, -1):
        alpha = 60 + r_offset * 20
        ring_color = (*PT_BLUE, alpha)
        # PIL doesn't support alpha on ImageDraw directly for lines, so we approximate
        draw.ellipse(
            [cx - radius - r_offset*3, cy - radius - r_offset*3,
             cx + radius + r_offset*3, cy + radius + r_offset*3],
            outline=(PT_BLUE[0], PT_BLUE[1], PT_BLUE[2]),
            width=1
        )

    # Generate node positions in a brain-like cluster
    nodes = []
    # Inner cluster
    for i in range(12):
        angle = (i / 12) * 2 * math.pi
        r = random.uniform(0.2, 0.65) * radius
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle) * 0.75  # Slightly compressed vertically
        nodes.append((x, y))

    # Outer ring nodes
    for i in range(8):
        angle = (i / 8) * 2 * math.pi + 0.2
        r = random.uniform(0.75, 0.95) * radius
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle) * 0.75
        nodes.append((x, y))

    # Center node (the "AI core")
    nodes.append((cx, cy))

    # Draw connections first (below nodes)
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if i >= j:
                continue
            dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if dist < radius * 0.7:
                # Color based on distance - closer = brighter blue
                intensity = max(0, 1 - dist / (radius * 0.7))
                if random.random() < 0.6:  # Not all connections shown
                    line_color = (
                        int(PT_BLUE[0] * intensity + PT_DARK_BG[0] * (1 - intensity)),
                        int(PT_BLUE[1] * intensity + PT_DARK_BG[1] * (1 - intensity)),
                        int(PT_BLUE[2] * intensity + PT_DARK_BG[2] * (1 - intensity))
                    )
                    width = max(1, int(intensity * 2))
                    draw.line([(int(x1), int(y1)), (int(x2), int(y2))], fill=line_color, width=width)

    # A few orange "activated" connections to represent the divide/gap
    activated_pairs = [(0, 20), (3, 18), (7, 20), (10, 19)]
    for i, j in activated_pairs:
        if i < len(nodes) and j < len(nodes):
            x1, y1 = nodes[i]
            x2, y2 = nodes[j]
            draw.line([(int(x1), int(y1)), (int(x2), int(y2))], fill=PT_ORANGE, width=2)

    # Draw nodes
    for idx, (x, y) in enumerate(nodes):
        if idx == len(nodes) - 1:  # Center core node
            r_node = 10
            color = PT_ORANGE
            # Glow effect
            for glow in range(4, 0, -1):
                glow_color = (PT_ORANGE[0], PT_ORANGE[1] // 2, PT_ORANGE[2] // 4)
                draw.ellipse(
                    [x - r_node - glow*3, y - r_node - glow*3,
                     x + r_node + glow*3, y + r_node + glow*3],
                    fill=glow_color
                )
            draw.ellipse([x - r_node, y - r_node, x + r_node, y + r_node], fill=color)
        elif idx in [0, 3, 7, 10, 18, 19]:  # "Gap" nodes in orange
            r_node = 5
            draw.ellipse([x - r_node, y - r_node, x + r_node, y + r_node], fill=PT_ORANGE)
        else:
            r_node = random.randint(3, 6)
            draw.ellipse([x - r_node, y - r_node, x + r_node, y + r_node], fill=PT_BLUE)


def draw_hexagon(draw, cx, cy, size=40, color=PT_BLUE, outline_only=False):
    """Draw a hexagon shape (PureBrain visual language)."""
    points = []
    for i in range(6):
        angle = math.pi / 6 + i * math.pi / 3
        px = cx + size * math.cos(angle)
        py = cy + size * math.sin(angle)
        points.append((px, py))
    if outline_only:
        draw.polygon(points, outline=color)
    else:
        draw.polygon(points, fill=color)


def draw_gap_visualization(draw, x_start, x_end, y_center, height=80):
    """Draw a visual representing the 'gap' - two diverging lines."""
    # Lower line (floor being raised slightly)
    y_low_start = y_center + height * 0.1
    y_low_end = y_center + height * 0.3
    draw.line([(x_start, int(y_low_start)), (x_end, int(y_low_end))],
              fill=(*PT_BLUE, ), width=3)

    # Upper line (ceiling being raised dramatically)
    y_high_start = y_center - height * 0.2
    y_high_end = y_center - height * 0.85
    draw.line([(x_start, int(y_high_start)), (x_end, int(y_high_end))],
              fill=PT_ORANGE, width=3)

    # Label dots
    draw.ellipse([x_end - 5, int(y_low_end) - 5, x_end + 5, int(y_low_end) + 5],
                 fill=PT_BLUE)
    draw.ellipse([x_end - 5, int(y_high_end) - 5, x_end + 5, int(y_high_end) + 5],
                 fill=PT_ORANGE)


def get_font(size):
    """Try to load a system font, fall back to default."""
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def get_font_regular(size):
    """Try to load a regular (non-bold) system font."""
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/opentype/noto/NotoSans-Regular.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def main():
    # Create base image
    img = Image.new("RGB", (WIDTH, HEIGHT), PT_DARK_BG)
    draw = ImageDraw.Draw(img)

    # 1. Gradient background
    draw_gradient_bg(draw, WIDTH, HEIGHT)

    # 2. Subtle grid lines (tech aesthetic)
    grid_color = (20, 35, 60)
    for x in range(0, WIDTH, 80):
        draw.line([(x, 0), (x, HEIGHT)], fill=grid_color, width=1)
    for y in range(0, HEIGHT, 80):
        draw.line([(0, y), (WIDTH, y)], fill=grid_color, width=1)

    # 3. Neural network visualization (right side)
    draw_neural_network(draw, cx=870, cy=315, radius=210)

    # 4. Hexagon icon (top left area, part of PureBrain branding)
    draw_hexagon(draw, cx=95, cy=95, size=32, color=PT_BLUE, outline_only=False)
    draw_hexagon(draw, cx=95, cy=95, size=32, color=PT_DARK_BG, outline_only=False)
    draw_hexagon(draw, cx=95, cy=95, size=30, color=PT_BLUE, outline_only=True)

    # Small inner hex
    draw_hexagon(draw, cx=95, cy=95, size=14, color=PT_ORANGE)

    # 5. Orange accent line (left side decorative)
    draw.rectangle([60, 130, 63, 420], fill=PT_ORANGE)

    # 6. Main headline text
    # "AI Doesn't Make Your Team Smarter."
    font_headline = get_font(54)
    font_headline_sub = get_font(52)
    font_subhead = get_font(30)
    font_body = get_font_regular(22)
    font_logo = get_font(28)
    font_logo_small = get_font_regular(18)

    # Line 1
    line1 = "AI Doesn't Make"
    line2 = "Your Team Smarter."
    line3 = "It Makes the Gap Bigger."

    x_text = 90
    y_line1 = 145

    draw.text((x_text, y_line1), line1, font=font_headline, fill=WHITE)
    draw.text((x_text, y_line1 + 65), line2, font=font_headline, fill=WHITE)

    # Line 3 in PT Orange
    draw.text((x_text, y_line1 + 135), line3, font=font_headline_sub, fill=PT_ORANGE)

    # 7. Subheadline / body excerpt
    subtext = "The AI competence divide is widening."
    subtext2 = "Do you know which side your team is on?"
    draw.text((x_text, y_line1 + 215), subtext, font=font_body, fill=(160, 190, 210))
    draw.text((x_text, y_line1 + 245), subtext2, font=font_body, fill=(160, 190, 210))

    # 8. Gap visualization (small graphic)
    draw_gap_visualization(draw, x_start=90, x_end=310, y_center=490, height=70)

    # Labels for the gap viz
    font_small = get_font_regular(16)
    draw.text((315, 510), "Floor", font=font_small, fill=PT_BLUE)
    draw.text((315, 460), "Ceiling", font=font_small, fill=PT_ORANGE)

    # 9. PureBrain logo (bottom left, safe from edges)
    logo_y = HEIGHT - 70
    logo_x = x_text

    # "PUREBR" in PT Blue | "AI" in PT Orange | "N" in PT Blue | ".ai" in white
    draw.text((logo_x, logo_y), "PUREBR", font=font_logo, fill=PT_BLUE)

    # Calculate offset for "AI"
    purebr_bbox = draw.textbbox((logo_x, logo_y), "PUREBR", font=font_logo)
    ai_x = purebr_bbox[2]
    draw.text((ai_x, logo_y), "AI", font=font_logo, fill=PT_ORANGE)

    ai_bbox = draw.textbbox((ai_x, logo_y), "AI", font=font_logo)
    n_x = ai_bbox[2]
    draw.text((n_x, logo_y), "N", font=font_logo, fill=PT_BLUE)

    n_bbox = draw.textbbox((n_x, logo_y), "N", font=font_logo)
    dot_x = n_bbox[2]
    draw.text((dot_x, logo_y + 2), ".ai", font=font_logo_small, fill=WHITE)

    # 10. Right side label inside neural network area (subtle)
    font_tag = get_font_regular(16)
    draw.text((750, 560), "puretechnology.nyc", font=font_tag, fill=(60, 100, 130))

    # 11. Thin orange bottom border
    draw.rectangle([0, HEIGHT - 5, WIDTH, HEIGHT], fill=PT_ORANGE)

    # Save
    img.save(OUTPUT_PATH, "PNG", quality=95)
    print(f"Banner saved to: {OUTPUT_PATH}")
    print(f"Dimensions: {img.width}x{img.height}")


if __name__ == "__main__":
    main()
