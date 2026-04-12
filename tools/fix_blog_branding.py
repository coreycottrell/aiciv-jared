#!/usr/bin/env python3
"""
Blog Header Branding Tool - PureBrain.ai Standard

BRANDING RULES (LOCKED IN):
1. Logo format: PUREBR (blue) + AI (orange) + N (blue) + .ai (white, lowercase)
2. 75% SAFE ZONE: All important content within 75% of image
   - 12.5% margin on each side (25% total borders)
3. Layout (top to bottom within safe zone):
   - Top: Hexagon icon + PUREBRAINai logo
   - Middle: Article title (LARGE)
   - Bottom: Tagline
4. Colors:
   - PT Blue: #2a93c1
   - PT Orange: #f1420b
   - White: #ffffff (for .ai)
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Paths
BASE_DIR = Path("/home/jared/projects/AI-CIV/aether")
BLOG_DIR = BASE_DIR / "exports/blog-content/2026-02-15-enterprise-ready-ai"
ICON_PATH = BASE_DIR / "docs/assets/logos/purebrain-icon.png"
OUTPUT_PATH = BLOG_DIR / "blog-header-corrected.png"

# PT Brand Colors
PT_BLUE = "#2a93c1"
PT_ORANGE = "#f1420b"
PT_WHITE = "#ffffff"

# SAFE ZONE: 75% of image (12.5% margin on each side)
SAFE_ZONE_PERCENT = 0.75
MARGIN_PERCENT = 0.125  # 12.5% on each side

def hex_to_rgb(hex_color):
    """Convert hex to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_corrected_header(article_title="Enterprise AI That Learns How Your Business Runs"):
    """Create blog header with correct PUREBRAIN.AI branding.

    Follows the 75% SAFE ZONE rule - all important content within center 75%.
    """

    # Load the background image (use final which has nice background)
    bg = Image.open(BLOG_DIR / "blog-header-final.png").convert("RGBA")
    width, height = bg.size
    print(f"Image size: {width}x{height}")

    # Calculate SAFE ZONE boundaries (75% of image, 12.5% margins)
    margin_x = int(width * MARGIN_PERCENT)
    margin_y = int(height * MARGIN_PERCENT)
    safe_left = margin_x
    safe_right = width - margin_x
    safe_top = margin_y
    safe_bottom = height - margin_y
    safe_width = safe_right - safe_left
    safe_height = safe_bottom - safe_top

    print(f"Safe zone: {safe_left},{safe_top} to {safe_right},{safe_bottom}")

    # Create drawing context
    draw = ImageDraw.Draw(bg)

    # FIRST: Cover the old text area at the bottom completely
    # The old image had text in the bottom ~150px
    old_text_area_top = height - 180
    draw.rectangle([(0, old_text_area_top), (width, height)], fill=(10, 15, 25))

    # Add gradient fade above the solid cover
    for i in range(50):
        alpha = int(255 * (1 - i/50))
        y = old_text_area_top - i
        if y >= 0:
            # Blend with dark color
            gray = int(10 + (i/50) * 20)
            draw.line([(0, y), (width, y)], fill=(gray, gray+5, gray+15, alpha))

    # Add semi-transparent dark overlay for overall text readability
    overlay = Image.new('RGBA', bg.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    # Gradient from bottom to top for readability (lighter version)
    for y in range(height - 180):  # Don't overlay the already-covered bottom
        alpha = int(120 * (y / (height - 180)))
        overlay_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))

    bg = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(bg)

    # Try to load a good font
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]

    font_logo = None
    font_title = None
    font_tagline = None
    for fp in font_paths:
        if Path(fp).exists():
            font_logo = ImageFont.truetype(fp, 36)      # Logo text
            font_title = ImageFont.truetype(fp, 72)     # Article title - LARGE
            font_tagline = ImageFont.truetype(fp, 24)   # Tagline
            print(f"Using font: {fp}")
            break

    if font_logo is None:
        font_logo = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_tagline = ImageFont.load_default()
        print("Using default font")

    # =========================================
    # LAYOUT (within 75% SAFE ZONE):
    # TOP-LEFT: Hexagon icon (LARGE) + PUREBRAINai logo (with shadow)
    # MIDDLE: Article title (LARGE, centered)
    # =========================================

    # Load and resize hexagon icon - LARGER
    icon = Image.open(ICON_PATH).convert("RGBA")
    icon_size = 90  # LARGER icon
    icon = icon.resize((icon_size, icon_size), Image.LANCZOS)

    # LOCKED LOGO FORMAT (2026-02-16 - NON-NEGOTIABLE)
    # PUREBR (PT Blue, UPPERCASE) + AI (PT Orange, UPPERCASE) + N (PT Blue, UPPERCASE) + .ai (White, lowercase)
    # This format applies EVERYWHERE on ANYTHING we create for PureBrain.ai
    logo_segments = [
        ("PUREBR", PT_BLUE),   # PT Blue #2a93c1, UPPERCASE
        ("AI", PT_ORANGE),     # PT Orange #f1420b, UPPERCASE
        ("N", PT_BLUE),        # PT Blue #2a93c1, UPPERCASE
        (".ai", PT_WHITE),     # White #ffffff, lowercase
    ]

    # Calculate logo text widths
    logo_widths = []
    total_logo_width = 0
    for text, _ in logo_segments:
        bbox = draw.textbbox((0, 0), text, font=font_logo)
        w = bbox[2] - bbox[0]
        logo_widths.append(w)
        total_logo_width += w

    # Position logo at TOP-LEFT of safe zone (not centered)
    logo_x = safe_left + 20  # Left aligned within safe zone
    logo_y = safe_top + 20

    # Paste hexagon icon
    bg.paste(icon, (logo_x, logo_y), icon)

    # Draw logo text with SHADOW for lift effect
    text_x = logo_x + icon_size + 15
    text_y = logo_y + (icon_size - 36) // 2  # Vertically center with icon

    # Draw shadow first (offset by 3px)
    shadow_offset = 3
    shadow_color = (0, 0, 0)  # Black shadow
    shadow_x = text_x + shadow_offset
    shadow_y = text_y + shadow_offset
    for i, (text, _) in enumerate(logo_segments):
        draw.text((shadow_x, shadow_y), text, font=font_logo, fill=shadow_color)
        shadow_x += logo_widths[i]

    # Draw logo text on top of shadow
    for i, (text, color) in enumerate(logo_segments):
        draw.text((text_x, text_y), text, font=font_logo, fill=hex_to_rgb(color))
        text_x += logo_widths[i]

    # =========================================
    # ARTICLE TITLE - LARGE, in MIDDLE of safe zone
    # This IS the title: "Enterprise AI That Learns How Your Business Runs"
    # =========================================
    # Word wrap if needed
    words = article_title.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font_title)
        if bbox[2] - bbox[0] > safe_width - 40:  # Leave some padding
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
        else:
            current_line.append(word)
    if current_line:
        lines.append(' '.join(current_line))

    # Calculate title block height
    line_height = 85
    title_block_height = len(lines) * line_height

    # Center title vertically in safe zone
    title_start_y = safe_top + (safe_height - title_block_height) // 2

    # Draw each line of title (with subtle shadow for readability)
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        line_width = bbox[2] - bbox[0]
        line_x = safe_left + (safe_width - line_width) // 2
        line_y = title_start_y + (i * line_height)
        # Shadow
        draw.text((line_x + 2, line_y + 2), line, font=font_title, fill=(0, 0, 0))
        # Text
        draw.text((line_x, line_y), line, font=font_title, fill=(255, 255, 255))

    # NO TAGLINE - title is the main content

    # Convert to RGB for saving as PNG (remove alpha)
    final = bg.convert("RGB")
    final.save(OUTPUT_PATH, "PNG", quality=95)
    print(f"Saved corrected image to: {OUTPUT_PATH}")

    return OUTPUT_PATH

if __name__ == "__main__":
    # Article title for this specific blog post
    title = "Enterprise AI That Learns How Your Business Runs"
    result = create_corrected_header(article_title=title)
    print(f"Done! Image at: {result}")
