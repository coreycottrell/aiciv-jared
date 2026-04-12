#!/usr/bin/env python3
"""
Generate Blog Banner V3: Why AI Memory Changes Everything

Creates a 1920x1200 blog header with PROPERLY GLOWING background:
- Taller (1200px)
- Actual glowing orbs (additive blending)
- More vibrant neural network
- Energy/data flow aesthetic

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
OUTPUT_PATH = BASE_DIR / "exports/why-ai-memory-changes-everything-banner-v3.png"

# PT Brand Colors (RGB tuples)
PT_BLUE = (42, 147, 193)      # #2a93c1
PT_ORANGE = (241, 66, 11)     # #f1420b
PT_WHITE = (255, 255, 255)    # #ffffff
DARK_BG = (10, 15, 30)        # Deep blue-black

# Image size - TALLER
WIDTH = 1920
HEIGHT = 1200

# Safe zone
MARGIN_PERCENT = 0.125

def create_gradient_background(width, height):
    """Create a gradient from deep blue-black to slightly lighter."""
    img = Image.new('RGB', (width, height), DARK_BG)

    # Add vertical gradient (darker at top, slightly lighter at bottom)
    for y in range(height):
        factor = y / height
        for x in range(width):
            r = int(DARK_BG[0] + 15 * factor)
            g = int(DARK_BG[1] + 20 * factor)
            b = int(DARK_BG[2] + 30 * factor)
            img.putpixel((x, y), (r, g, b))

    return img

def add_glow_orb(img, cx, cy, radius, color, intensity=0.5):
    """Add a single glowing orb with proper additive blending."""
    width, height = img.size

    for y in range(max(0, cy - radius * 2), min(height, cy + radius * 2)):
        for x in range(max(0, cx - radius * 2), min(width, cx + radius * 2)):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            if dist < radius * 2:
                # Gaussian-like falloff
                glow = math.exp(-(dist**2) / (2 * (radius * 0.7)**2)) * intensity

                # Get current pixel
                current = img.getpixel((x, y))

                # Additive blend
                new_r = min(255, int(current[0] + color[0] * glow))
                new_g = min(255, int(current[1] + color[1] * glow))
                new_b = min(255, int(current[2] + color[2] * glow))

                img.putpixel((x, y), (new_r, new_g, new_b))

    return img

def add_glowing_orbs(img):
    """Add multiple glowing orbs in brand colors."""
    width, height = img.size

    orb_configs = [
        # (x_factor, y_factor, radius, color, intensity)
        (0.12, 0.20, 200, PT_BLUE, 0.4),
        (0.88, 0.15, 180, PT_ORANGE, 0.35),
        (0.80, 0.78, 220, PT_BLUE, 0.35),
        (0.20, 0.82, 150, PT_ORANGE, 0.3),
        (0.50, 0.10, 280, PT_BLUE, 0.25),
        (0.92, 0.50, 120, PT_ORANGE, 0.35),
        (0.08, 0.55, 160, PT_BLUE, 0.3),
        (0.65, 0.88, 180, PT_ORANGE, 0.25),
        (0.35, 0.35, 100, PT_BLUE, 0.2),
        (0.70, 0.40, 90, PT_ORANGE, 0.2),
    ]

    print("  - Adding glowing orbs (this takes a moment)...")
    for i, (x_f, y_f, radius, color, intensity) in enumerate(orb_configs):
        cx = int(width * x_f)
        cy = int(height * y_f)
        img = add_glow_orb(img, cx, cy, radius, color, intensity)

    return img

def add_neural_network(img, num_nodes=50):
    """Add neural network connections."""
    draw = ImageDraw.Draw(img)
    width, height = img.size

    margin_x = int(width * 0.03)
    margin_y = int(height * 0.03)

    # Generate nodes
    nodes = []
    for _ in range(num_nodes):
        x = random.randint(margin_x, width - margin_x)
        y = random.randint(margin_y, height - margin_y)
        size = random.randint(3, 10)
        brightness = random.uniform(0.5, 1.0)
        nodes.append((x, y, size, brightness))

    # Draw connections
    for i, (x1, y1, s1, b1) in enumerate(nodes):
        for j, (x2, y2, s2, b2) in enumerate(nodes[i+1:], i+1):
            dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if dist < 300:
                alpha = (1 - dist / 300) * min(b1, b2) * 0.4
                line_color = tuple(int(c * alpha) for c in PT_BLUE)
                draw.line([(x1, y1), (x2, y2)], fill=line_color, width=1)

    # Draw nodes
    for x, y, size, brightness in nodes:
        # Node color based on brightness
        node_color = tuple(int(c * brightness) for c in PT_BLUE)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=node_color)

        # Bright center for larger nodes
        if size > 5:
            center_size = size // 3
            center_color = tuple(min(255, int(c * brightness * 1.3)) for c in PT_BLUE)
            draw.ellipse([x - center_size, y - center_size, x + center_size, y + center_size], fill=center_color)

    return img

def add_energy_lines(img):
    """Add subtle energy flow lines."""
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Curved energy lines
    for _ in range(5):
        start_x = random.randint(0, width)
        start_y = random.randint(0, height)

        points = [(start_x, start_y)]
        for _ in range(8):
            last_x, last_y = points[-1]
            new_x = last_x + random.randint(100, 300)
            new_y = last_y + random.randint(-100, 100)
            if 0 <= new_x < width and 0 <= new_y < height:
                points.append((new_x, new_y))

        if len(points) > 2:
            color = tuple(int(c * 0.15) for c in PT_BLUE)
            draw.line(points, fill=color, width=1)

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
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 78)
        brand_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        print(f"  - Using DejaVu Sans Bold")
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
            icon = icon.resize((65, 65), Image.Resampling.LANCZOS)
            img.paste(icon, (logo_x, logo_y), icon)
            logo_x += 75
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
        draw.text((current_x, logo_y + 14), text, font=brand_font, fill=color)
        bbox = draw.textbbox((current_x, logo_y + 14), text, font=brand_font)
        current_x = bbox[2]

    # Draw title - centered
    title = "Why AI Memory Changes Everything"
    print(f"  - Drawing title: '{title}'")

    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    title_height = bbox[3] - bbox[1]

    title_x = (width - title_width) // 2
    title_y = (height - title_height) // 2 - 20

    # Draw text shadow for depth
    shadow_offset = 4
    for offset in range(shadow_offset, 0, -1):
        shadow_alpha = int(100 * (1 - offset / shadow_offset))
        shadow_color = (0, 0, 0)
        draw.text((title_x + offset, title_y + offset), title, font=title_font, fill=shadow_color)

    # Draw main title
    draw.text((title_x, title_y), title, font=title_font, fill=PT_WHITE)

    # Add tagline
    tagline = "The foundation of AI partnership"
    bbox = draw.textbbox((0, 0), tagline, font=small_font)
    tagline_width = bbox[2] - bbox[0]
    tagline_x = (width - tagline_width) // 2
    tagline_y = title_y + title_height + 25

    # Tagline with slight glow
    tagline_color = (200, 200, 210)
    draw.text((tagline_x, tagline_y), tagline, font=small_font, fill=tagline_color)

    return img

def main():
    print(f"Creating ENHANCED blog banner v3: Why AI Memory Changes Everything")

    # Create gradient background
    print("  - Generating gradient background...")
    img = create_gradient_background(WIDTH, HEIGHT)

    # Add glowing orbs
    img = add_glowing_orbs(img)

    # Add neural network
    print("  - Adding neural network...")
    img = add_neural_network(img)

    # Add energy lines
    print("  - Adding energy flow lines...")
    img = add_energy_lines(img)

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
