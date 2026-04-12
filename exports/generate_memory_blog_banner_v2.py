#!/usr/bin/env python3
"""
Generate Blog Banner V2: Why AI Memory Changes Everything

Creates a 1920x1200 blog header with MORE ENTICING background:
- Taller (1200px instead of 1080px)
- Dynamic gradient with glowing orbs
- Neural network with pulsing nodes
- More vibrant color treatment

BRANDING RULES (LOCKED IN):
- PUREBR (blue) + AI (orange) + N (blue) + .ai (white, lowercase)
- 75% SAFE ZONE
- Colors: PT Blue #2a93c1, PT Orange #f1420b, White #ffffff
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import random
import math

# Paths
BASE_DIR = Path("/home/jared/projects/AI-CIV/aether")
ICON_PATH = BASE_DIR / "docs/assets/logos/purebrain-icon.png"
OUTPUT_PATH = BASE_DIR / "exports/why-ai-memory-changes-everything-banner-v2.png"

# PT Brand Colors (RGB tuples)
PT_BLUE = (42, 147, 193)      # #2a93c1
PT_ORANGE = (241, 66, 11)     # #f1420b
PT_WHITE = (255, 255, 255)    # #ffffff
DARK_BG = (8, 12, 24)         # Deeper dark blue

# Image size - TALLER
WIDTH = 1920
HEIGHT = 1200

# Safe zone
MARGIN_PERCENT = 0.125

def create_dynamic_background(width, height):
    """Create a more enticing background with glowing orbs and gradients."""
    img = Image.new('RGB', (width, height), DARK_BG)
    draw = ImageDraw.Draw(img)

    # Create radial gradient from center-bottom
    center_x, center_y = width // 2, height + 200
    max_dist = math.sqrt(width**2 + height**2)

    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            factor = max(0, 1 - (dist / max_dist) * 1.2)

            # Blend dark blue to slightly brighter
            r = int(DARK_BG[0] + (PT_BLUE[0] * 0.15 * factor))
            g = int(DARK_BG[1] + (PT_BLUE[1] * 0.15 * factor))
            b = int(DARK_BG[2] + (PT_BLUE[2] * 0.25 * factor))

            img.putpixel((x, y), (min(255, r), min(255, g), min(255, b)))

    return img

def add_glowing_orbs(img, num_orbs=8):
    """Add soft glowing orbs in brand colors."""
    draw = ImageDraw.Draw(img)
    width, height = img.size

    orb_configs = [
        # (x_factor, y_factor, radius, color, alpha)
        (0.15, 0.25, 180, PT_BLUE, 0.08),
        (0.85, 0.20, 150, PT_ORANGE, 0.06),
        (0.75, 0.75, 200, PT_BLUE, 0.07),
        (0.25, 0.80, 120, PT_ORANGE, 0.05),
        (0.50, 0.15, 250, PT_BLUE, 0.04),
        (0.90, 0.55, 100, PT_ORANGE, 0.06),
        (0.10, 0.60, 140, PT_BLUE, 0.05),
        (0.60, 0.85, 160, PT_ORANGE, 0.04),
    ]

    for x_f, y_f, radius, color, alpha in orb_configs:
        cx = int(width * x_f)
        cy = int(height * y_f)

        # Draw gradient circles
        for r in range(radius, 0, -2):
            fade = (r / radius) ** 2
            c = tuple(int(color[i] * (1 - fade) * alpha + img.getpixel((min(cx, width-1), min(cy, height-1)))[i] * fade) for i in range(3))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)

    return img

def add_neural_network_v2(img, num_nodes=45):
    """Add a more dynamic neural network with varied node sizes."""
    draw = ImageDraw.Draw(img)
    width, height = img.size

    margin_x = int(width * 0.05)
    margin_y = int(height * 0.05)

    # Generate nodes with varied sizes
    nodes = []
    for _ in range(num_nodes):
        x = random.randint(margin_x, width - margin_x)
        y = random.randint(margin_y, height - margin_y)
        size = random.randint(4, 12)
        brightness = random.uniform(0.4, 1.0)
        nodes.append((x, y, size, brightness))

    # Draw connections with gradient opacity based on distance
    for i, (x1, y1, s1, b1) in enumerate(nodes):
        for j, (x2, y2, s2, b2) in enumerate(nodes[i+1:], i+1):
            dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if dist < 350:  # Longer connections
                alpha = int(40 * (1 - dist / 350) * min(b1, b2))
                color = (PT_BLUE[0], PT_BLUE[1], PT_BLUE[2], alpha)
                # Draw line (approximate with thin ellipses since PIL doesn't do alpha lines easily)
                line_color = tuple(int(c * alpha / 255) for c in PT_BLUE)
                draw.line([(x1, y1), (x2, y2)], fill=line_color, width=1)

    # Draw nodes with glow effect
    for x, y, size, brightness in nodes:
        # Outer glow
        glow_color = tuple(int(c * brightness * 0.3) for c in PT_BLUE)
        draw.ellipse([x - size*2, y - size*2, x + size*2, y + size*2], fill=glow_color)

        # Inner node
        node_color = tuple(int(c * brightness) for c in PT_BLUE)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=node_color)

        # Bright center
        if size > 6:
            center_color = tuple(min(255, int(c * brightness * 1.5)) for c in PT_BLUE)
            draw.ellipse([x - size//3, y - size//3, x + size//3, y + size//3], fill=center_color)

    return img

def add_accent_lines(img):
    """Add subtle accent lines for depth."""
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Horizontal accent lines
    for i in range(3):
        y = int(height * (0.3 + i * 0.2))
        alpha = 15 - i * 3
        color = tuple(int(c * alpha / 255) for c in PT_BLUE)
        draw.line([(0, y), (width, y)], fill=color, width=1)

    return img

def add_text_and_branding(img):
    """Add the title and PureBrain branding."""
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Calculate safe zone
    margin_x = int(width * MARGIN_PERCENT)
    margin_y = int(height * MARGIN_PERCENT)

    # Try to load fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        brand_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        print(f"  - Using font: /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    except:
        title_font = ImageFont.load_default()
        brand_font = title_font
        small_font = title_font
        print("  - Using default font")

    # Add PureBrain logo if exists
    logo_x = margin_x
    logo_y = margin_y

    if ICON_PATH.exists():
        try:
            icon = Image.open(ICON_PATH).convert('RGBA')
            icon = icon.resize((60, 60), Image.Resampling.LANCZOS)
            img.paste(icon, (logo_x, logo_y), icon)
            logo_x += 70
        except Exception as e:
            print(f"  - Could not load icon: {e}")

    # Draw PUREBRAIN.ai with color coding
    brand_text_parts = [
        ("PUREBR", PT_BLUE),
        ("AI", PT_ORANGE),
        ("N", PT_BLUE),
        (".ai", PT_WHITE)
    ]

    current_x = logo_x
    for text, color in brand_text_parts:
        draw.text((current_x, logo_y + 12), text, font=brand_font, fill=color)
        bbox = draw.textbbox((current_x, logo_y + 12), text, font=brand_font)
        current_x = bbox[2]

    # Draw title - centered
    title = "Why AI Memory Changes Everything"
    print(f"  - Drawing title: '{title}'")

    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    title_height = bbox[3] - bbox[1]

    title_x = (width - title_width) // 2
    title_y = (height - title_height) // 2

    # Draw text shadow for depth
    shadow_offset = 3
    draw.text((title_x + shadow_offset, title_y + shadow_offset), title, font=title_font, fill=(0, 0, 0))

    # Draw main title
    draw.text((title_x, title_y), title, font=title_font, fill=PT_WHITE)

    # Add subtle tagline
    tagline = "The foundation of AI partnership"
    bbox = draw.textbbox((0, 0), tagline, font=small_font)
    tagline_width = bbox[2] - bbox[0]
    tagline_x = (width - tagline_width) // 2
    tagline_y = title_y + title_height + 20

    # Tagline in muted color
    tagline_color = (180, 180, 180)
    draw.text((tagline_x, tagline_y), tagline, font=small_font, fill=tagline_color)

    return img

def main():
    print(f"Creating enhanced blog banner: Why AI Memory Changes Everything")

    # Create dynamic background
    print("  - Generating dynamic gradient background...")
    img = create_dynamic_background(WIDTH, HEIGHT)

    # Add glowing orbs
    print("  - Adding glowing orbs...")
    img = add_glowing_orbs(img)

    # Add neural network
    print("  - Adding enhanced neural network...")
    img = add_neural_network_v2(img)

    # Add accent lines
    print("  - Adding accent lines...")
    img = add_accent_lines(img)

    # Add text and branding
    print("  - Adding text and branding...")
    img = add_text_and_branding(img)

    # Save
    img.save(OUTPUT_PATH, quality=95)
    print(f"\nSaved banner to: {OUTPUT_PATH}")
    print(f"Dimensions: {WIDTH}x{HEIGHT}")
    print(f"Done! Banner ready at: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
