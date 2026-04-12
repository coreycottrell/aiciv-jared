#!/usr/bin/env python3
"""
Generate Blog Banner: Why AI Memory Changes Everything

Creates a 1920x1080 blog header with PureBrain.ai branding.
Uses programmatic gradient background with neural network aesthetic.

BRANDING RULES (LOCKED IN):
- PUREBR (blue) + AI (orange) + N (blue) + .ai (white, lowercase)
- 75% SAFE ZONE
- Colors: PT Blue #2a93c1, PT Orange #f1420b, White #ffffff
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import random
import math

# Paths
BASE_DIR = Path("/home/jared/projects/AI-CIV/aether")
ICON_PATH = BASE_DIR / "docs/assets/logos/purebrain-icon.png"
OUTPUT_PATH = BASE_DIR / "exports/why-ai-memory-matters-banner.png"

# PT Brand Colors (RGB tuples)
PT_BLUE = (42, 147, 193)      # #2a93c1
PT_ORANGE = (241, 66, 11)     # #f1420b
PT_WHITE = (255, 255, 255)    # #ffffff
DARK_BG = (10, 15, 25)        # Dark blue-ish background

# Image size
WIDTH = 1920
HEIGHT = 1080

# Safe zone
MARGIN_PERCENT = 0.125

def create_gradient_background(width, height):
    """Create a dark gradient background with neural network aesthetic."""
    img = Image.new('RGB', (width, height), DARK_BG)
    draw = ImageDraw.Draw(img)

    # Add subtle radial gradient from center
    center_x, center_y = width // 2, height // 2
    max_dist = math.sqrt(center_x**2 + center_y**2)

    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            factor = 1 - (dist / max_dist) * 0.3
            r = int(DARK_BG[0] * factor)
            g = int(DARK_BG[1] * factor)
            b = int(DARK_BG[2] * factor + 15 * (1 - dist/max_dist))
            img.putpixel((x, y), (r, g, b))

    return img


def draw_neural_nodes(img, draw):
    """Add subtle neural network nodes and connections."""
    random.seed(42)  # Consistent look

    nodes = []
    # Generate node positions
    for _ in range(25):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        nodes.append((x, y))

    # Draw connections (subtle)
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if i < j:
                dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                if dist < 400:
                    alpha = int(30 * (1 - dist/400))
                    color = (PT_BLUE[0], PT_BLUE[1], PT_BLUE[2])
                    # Simulate alpha by blending with background
                    draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    # Draw nodes
    for x, y in nodes:
        # Outer glow
        for r in range(15, 5, -2):
            alpha = int(50 * (1 - r/15))
            draw.ellipse([x-r, y-r, x+r, y+r], fill=(PT_BLUE[0]//3, PT_BLUE[1]//3, PT_BLUE[2]//3))
        # Core
        draw.ellipse([x-5, y-5, x+5, y+5], fill=PT_BLUE)


def draw_memory_visualization(img, draw):
    """Add memory/brain-like concentric elements in the background."""
    center_x, center_y = WIDTH // 2, HEIGHT // 2

    # Draw concentric arcs representing "memory layers"
    for i in range(3):
        radius = 250 + i * 100
        # Draw partial arcs
        for angle_start in [30, 150, 270]:
            arc_length = 60 + random.randint(0, 30)
            color_mix = (
                int(PT_BLUE[0] * 0.3),
                int(PT_BLUE[1] * 0.3),
                int(PT_BLUE[2] * 0.3)
            )
            bbox = [center_x - radius, center_y - radius, center_x + radius, center_y + radius]
            draw.arc(bbox, angle_start, angle_start + arc_length, fill=color_mix, width=2)


def create_banner():
    """Create the complete blog banner."""
    print("Creating blog banner: Why AI Memory Changes Everything")

    # Create background
    print("  - Generating gradient background...")
    img = create_gradient_background(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)

    # Add neural network aesthetic
    print("  - Adding neural network elements...")
    draw_neural_nodes(img, draw)
    draw_memory_visualization(img, draw)

    # Add dark overlay for text readability
    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for y in range(HEIGHT):
        alpha = int(100 + 80 * (y / HEIGHT))  # Darker at bottom
        overlay_draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))

    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Calculate safe zone
    margin_x = int(WIDTH * MARGIN_PERCENT)
    margin_y = int(HEIGHT * MARGIN_PERCENT)
    safe_left = margin_x
    safe_right = WIDTH - margin_x
    safe_top = margin_y
    safe_bottom = HEIGHT - margin_y
    safe_width = safe_right - safe_left
    safe_height = safe_bottom - safe_top

    # Load fonts
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]

    font_logo = None
    font_title = None
    for fp in font_paths:
        if Path(fp).exists():
            font_logo = ImageFont.truetype(fp, 36)
            font_title = ImageFont.truetype(fp, 72)
            print(f"  - Using font: {fp}")
            break

    if font_logo is None:
        font_logo = ImageFont.load_default()
        font_title = ImageFont.load_default()
        print("  - Using default font")

    # =========================================
    # LOGO: TOP-LEFT (PUREBRAIN.ai branding)
    # =========================================
    logo_segments = [
        ("PUREBR", PT_BLUE),
        ("AI", PT_ORANGE),
        ("N", PT_BLUE),
        (".ai", PT_WHITE),
    ]

    # Calculate logo widths
    logo_widths = []
    for text, _ in logo_segments:
        bbox = draw.textbbox((0, 0), text, font=font_logo)
        logo_widths.append(bbox[2] - bbox[0])

    # Load and position icon
    logo_x = safe_left + 20
    logo_y = safe_top + 20

    if ICON_PATH.exists():
        icon = Image.open(ICON_PATH).convert("RGBA")
        icon_size = 90
        icon = icon.resize((icon_size, icon_size), Image.LANCZOS)
        img.paste(icon, (logo_x, logo_y), icon)
        text_x = logo_x + icon_size + 15
    else:
        icon_size = 0
        text_x = logo_x
        print("  - Warning: Icon not found")

    text_y = logo_y + (90 - 36) // 2

    # Draw logo shadow
    shadow_offset = 3
    shadow_x = text_x + shadow_offset
    shadow_y = text_y + shadow_offset
    for i, (text, _) in enumerate(logo_segments):
        draw.text((shadow_x, shadow_y), text, font=font_logo, fill=(0, 0, 0))
        shadow_x += logo_widths[i]

    # Draw logo text
    for i, (text, color) in enumerate(logo_segments):
        draw.text((text_x, text_y), text, font=font_logo, fill=color)
        text_x += logo_widths[i]

    # =========================================
    # ARTICLE TITLE - LARGE, CENTERED
    # =========================================
    article_title = "Why AI Memory Changes Everything"

    # Word wrap
    words = article_title.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font_title)
        if bbox[2] - bbox[0] > safe_width - 40:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
        else:
            current_line.append(word)
    if current_line:
        lines.append(' '.join(current_line))

    # Center title vertically
    line_height = 85
    title_block_height = len(lines) * line_height
    title_start_y = safe_top + (safe_height - title_block_height) // 2

    print(f"  - Drawing title: '{article_title}'")

    # Draw title with shadow
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        line_width = bbox[2] - bbox[0]
        line_x = safe_left + (safe_width - line_width) // 2
        line_y = title_start_y + (i * line_height)
        # Shadow
        draw.text((line_x + 3, line_y + 3), line, font=font_title, fill=(0, 0, 0))
        # Text
        draw.text((line_x, line_y), line, font=font_title, fill=PT_WHITE)

    # Save
    final = img.convert("RGB")
    final.save(OUTPUT_PATH, "PNG", quality=95)
    print(f"\nSaved banner to: {OUTPUT_PATH}")

    return OUTPUT_PATH


if __name__ == "__main__":
    result = create_banner()
    print(f"Done! Banner ready at: {result}")
