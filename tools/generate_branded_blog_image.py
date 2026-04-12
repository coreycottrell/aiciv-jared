#!/usr/bin/env python3
"""
Generate Branded Blog Images for PureBrain.ai

Creates blog header images with:
1. AI-generated abstract background (DALL-E 3) - NO TEXT
2. Pure Brain hexagon logo (top-left, within safe margin)
3. "PUREBR" in PT Blue (#2a93c1) + "AI" in PT Orange (#f1420b)
4. Blog title (white text, bold, readable, with shadow)

Safe zones: 100px margin from all edges for mobile compatibility.
Output: 1792x1024 (16:9 for blog headers)

Usage:
    python3 generate_branded_blog_image.py --title "Blog Title" --concept "visual description" --output path/to/output.png

Example:
    python3 generate_branded_blog_image.py \\
        --title "65% of Enterprise AI Tools Operate Without IT Oversight" \\
        --concept "Abstract split visual - chaotic fragmented AI nodes vs unified controlled network" \\
        --output exports/blog-content/2026-02-18-shadow-ai-problem/blog-header-branded.png
"""

import sys
import os
import argparse
import requests
import textwrap
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# For mocking in tests
try:
    import openai
except ImportError:
    openai = None


def load_env():
    """Load environment variables from .env file."""
    env_vars = {}
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars


class BrandedBlogImageGenerator:
    """Generator for branded PureBrain.ai blog header images."""

    # Pure Technology brand colors
    pt_blue = '#2a93c1'
    pt_orange = '#f1420b'

    # Output configuration
    output_size = (1792, 1024)
    safe_margin = 100

    def __init__(self, base_path: str):
        """Initialize generator with base project path."""
        self.base_path = base_path
        self.logo_path = os.path.join(base_path, "docs/assets/logos/purebrain-icon.png")
        self.api_key = None

        # Find available fonts
        self.font_paths = [
            "/home/jared/.fonts/Oswald-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]

        self._title_font = None
        self._brand_font = None

    def hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get a font at specified size, trying multiple paths."""
        for fp in self.font_paths:
            if os.path.exists(fp):
                try:
                    return ImageFont.truetype(fp, size)
                except Exception:
                    continue
        # Fallback to default
        return ImageFont.load_default()

    def load_logo(self, max_height: int = 100) -> Image.Image:
        """Load and scale the Pure Brain hexagon logo."""
        if not os.path.exists(self.logo_path):
            raise FileNotFoundError(f"Logo not found at {self.logo_path}")

        logo = Image.open(self.logo_path).convert("RGBA")

        # Scale to max height while preserving aspect ratio
        aspect = logo.width / logo.height
        new_height = min(max_height, logo.height)
        new_width = int(new_height * aspect)
        logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)

        return logo

    def load_api_key(self) -> str:
        """Load OpenAI API key from environment."""
        if self.api_key:
            return self.api_key

        env = load_env()
        self.api_key = env.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")
        return self.api_key

    def generate_background(self, concept: str) -> Image.Image:
        """Generate abstract background using DALL-E 3."""
        api_key = self.load_api_key()
        client = openai.OpenAI(api_key=api_key)

        # Build prompt - emphasize NO TEXT
        prompt = f"""Abstract, conceptual visualization: {concept}

Style requirements:
- Dark tech background (deep navy, black, or dark gray)
- Glowing elements in blue/cyan/orange tones
- Professional, clean, modern tech aesthetic
- Subtle depth and dimension
- NO TEXT whatsoever
- NO letters, numbers, words, or symbols
- NO human faces or hands
- Wide format composition suitable for header image
- Leave space in lower area for text overlay"""

        print(f"Generating background with DALL-E 3...")
        print(f"Concept: {concept}")

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",
            quality="hd",
            n=1
        )

        image_url = response.data[0].url
        print(f"Image generated, downloading...")

        img_response = requests.get(image_url)
        return Image.open(BytesIO(img_response.content)).convert("RGBA")

    def add_title(self, img: Image.Image, title: str) -> Image.Image:
        """Add title text at bottom center with safe margins."""
        draw = ImageDraw.Draw(img)
        width, height = img.size

        # Get title font
        title_font = self._get_font(56)

        # Calculate max width for text (with safe margins)
        max_text_width = width - (2 * self.safe_margin)

        # Wrap title if needed
        # Estimate characters per line based on font
        avg_char_width = title_font.getbbox("M")[2]
        chars_per_line = max_text_width // avg_char_width
        wrapped_lines = textwrap.wrap(title, width=int(chars_per_line * 0.9))

        # Colors
        white = (255, 255, 255, 255)
        shadow = (0, 0, 0, 200)

        # Calculate position - bottom center, within safe margin
        line_height = title_font.getbbox("Ay")[3] + 10
        total_text_height = len(wrapped_lines) * line_height
        start_y = height - self.safe_margin - total_text_height

        for i, line in enumerate(wrapped_lines):
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = start_y + (i * line_height)

            # Draw shadow (offset for depth)
            for offset in [(-3, -3), (-3, 3), (3, -3), (3, 3), (-3, 0), (3, 0), (0, -3), (0, 3)]:
                draw.text((x + offset[0], y + offset[1]), line, font=title_font, fill=shadow)

            # Draw main text
            draw.text((x, y), line, font=title_font, fill=white)

        return img

    def add_brand_text(self, img: Image.Image) -> Image.Image:
        """Add 'PUREBRAIN.ai' with proper PT color coding at top right.

        Colors:
        - PUREBR = PT Blue (#2a93c1)
        - AI = PT Orange (#f1420b)
        - N.ai = PT Blue (#2a93c1)
        """
        draw = ImageDraw.Draw(img)
        width, height = img.size

        brand_font = self._get_font(48)

        # PT Brand colors
        blue_rgb = self.hex_to_rgb(self.pt_blue) + (255,)
        orange_rgb = self.hex_to_rgb(self.pt_orange) + (255,)
        shadow = (0, 0, 0, 180)

        # Brand text segments: PUREBR (blue) + AI (orange) + N.ai (blue)
        part1_text = "PUREBR"  # Blue
        part2_text = "AI"      # Orange
        part3_text = "N.ai"    # Blue

        # Get widths for each segment
        part1_bbox = draw.textbbox((0, 0), part1_text, font=brand_font)
        part2_bbox = draw.textbbox((0, 0), part2_text, font=brand_font)
        part3_bbox = draw.textbbox((0, 0), part3_text, font=brand_font)

        part1_width = part1_bbox[2] - part1_bbox[0]
        part2_width = part2_bbox[2] - part2_bbox[0]
        part3_width = part3_bbox[2] - part3_bbox[0]

        total_width = part1_width + part2_width + part3_width

        # Position at top right with safe margin
        x_start = width - self.safe_margin - total_width
        y = self.safe_margin

        # Draw PUREBR (blue) with shadow
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            draw.text((x_start + offset[0], y + offset[1]), part1_text, font=brand_font, fill=shadow)
        draw.text((x_start, y), part1_text, font=brand_font, fill=blue_rgb)

        # Draw AI (orange) with shadow
        x_part2 = x_start + part1_width
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            draw.text((x_part2 + offset[0], y + offset[1]), part2_text, font=brand_font, fill=shadow)
        draw.text((x_part2, y), part2_text, font=brand_font, fill=orange_rgb)

        # Draw N.ai (blue) with shadow
        x_part3 = x_part2 + part2_width
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            draw.text((x_part3 + offset[0], y + offset[1]), part3_text, font=brand_font, fill=shadow)
        draw.text((x_part3, y), part3_text, font=brand_font, fill=blue_rgb)

        return img

    def add_logo(self, img: Image.Image) -> Image.Image:
        """Add Pure Brain hexagon logo at top left."""
        logo = self.load_logo(max_height=80)

        # Position at top left with safe margin
        x = self.safe_margin
        y = self.safe_margin

        # Paste logo with transparency
        img.paste(logo, (x, y), logo)

        return img

    def compose_final_image(self, background: Image.Image, title: str) -> Image.Image:
        """Compose final branded image with all elements."""
        # Ensure we're working with RGBA
        img = background.convert("RGBA")

        # Add elements in order (bottom to top)
        img = self.add_logo(img)
        img = self.add_brand_text(img)
        img = self.add_title(img, title)

        # Convert to RGB for final output (removes alpha)
        return img.convert("RGB")

    def save_image(self, img: Image.Image, output_path: str) -> str:
        """Save image to disk."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        img.save(output_path, format='PNG', quality=95)
        print(f"Saved: {output_path}")
        return output_path


def parse_arguments(args=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate branded blog header images for PureBrain.ai"
    )
    parser.add_argument(
        '--title',
        required=True,
        help='Blog post title to display'
    )
    parser.add_argument(
        '--concept',
        required=True,
        help='Abstract visual description for DALL-E background (no text)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output file path (PNG)'
    )
    parser.add_argument(
        '--skip-dalle',
        action='store_true',
        help='Skip DALL-E generation, use solid background (for testing)'
    )

    return parser.parse_args(args)


def main():
    """Main entry point."""
    args = parse_arguments()

    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generator = BrandedBlogImageGenerator(base_path)

    # Generate or create background
    if args.skip_dalle:
        print("Using solid background (--skip-dalle)")
        background = Image.new('RGBA', generator.output_size, (20, 30, 50, 255))
    else:
        background = generator.generate_background(args.concept)

    # Compose final image
    print("Composing final branded image...")
    final_image = generator.compose_final_image(background, args.title)

    # Determine output path
    output_path = args.output
    if not os.path.isabs(output_path):
        output_path = os.path.join(base_path, output_path)

    # Save
    generator.save_image(final_image, output_path)

    print(f"\nBranded blog image created successfully!")
    print(f"Output: {output_path}")
    print(f"Size: {final_image.size[0]}x{final_image.size[1]}")

    return output_path


if __name__ == "__main__":
    main()
