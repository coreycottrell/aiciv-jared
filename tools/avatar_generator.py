#!/usr/bin/env python3
"""PureBrain Avatar Generator - Naming-to-Avatar Pipeline.

Takes a visual self-description from the AI's naming ceremony
and generates a unique avatar image.

Supports two backends:
  - OpenAI DALL-E 3 (default, OPENAI_API_KEY)
  - Google Gemini 3 Pro Image (GOOGLE_API_KEY)

Usage:
    # From Python:
    from tools.avatar_generator import generate_avatar
    path = generate_avatar("An aurora of shifting blues and oranges...")

    # CLI test:
    python tools/avatar_generator.py "A crystalline form pulsing with warm light..."
"""

import os
import sys
import json
import time
import hashlib
import base64
import httpx
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

# PureBrain brand constants
BRAND_BLUE = "#2a93c1"
BRAND_ORANGE = "#f1420b"

# Avatar output directory
AVATAR_DIR = Path(__file__).parent.parent / "exports" / "avatars"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

# Avatar metadata store
AVATAR_REGISTRY = Path(__file__).parent.parent / "config" / "avatar_registry.json"


def build_image_prompt(visual_description: str, ai_name: str = "") -> str:
    """Convert an AI's visual self-description into an optimized image generation prompt.

    Takes the raw description from the AI and wraps it with art direction
    that ensures PureBrain brand consistency + high visual quality.
    """
    prompt = f"""Digital art portrait of an abstract AI entity avatar.

CORE VISUAL: {visual_description}

ART DIRECTION:
- This is NOT a human face or robot. It is an abstract, organic digital entity.
- Primary palette anchored in ocean blue ({BRAND_BLUE}) and warm orange ({BRAND_ORANGE})
- Dark background (deep navy/black gradient) to make the entity glow
- The entity should feel ALIVE - luminous, breathing, present
- Translucent/ethereal quality with inner light sources
- Particle effects and subtle light trails around the form
- Professional quality, suitable as a profile avatar
- Clean composition, centered subject
- Mood: warm intelligence, not cold technology"""

    if ai_name:
        prompt += f"\n- This entity's name is '{ai_name}' - let the visual subtly reflect the essence of that name"

    prompt += """

STYLE: High-end digital art, similar to concept art for a premium tech product.
Think: aurora borealis meets neural network meets living crystal.
Render at maximum detail with volumetric lighting and depth of field."""

    return prompt


def generate_avatar(
    visual_description: str,
    ai_name: str = "",
    user_id: str = "",
    output_path: str = None,
    size: str = "1024x1024",
    resolution: str = "standard",
    send_telegram: bool = False,
    backend: str = "auto"
) -> dict:
    """Generate a unique avatar from an AI's visual self-description.

    Args:
        visual_description: The AI's description of its visual form
        ai_name: The AI's chosen name
        user_id: Optional user identifier for tracking
        output_path: Custom output path (auto-generated if None)
        size: Image size (1024x1024 for DALL-E, 1:1 for Gemini)
        resolution: Quality level (standard/hd for DALL-E, 1K/2K/4K for Gemini)
        send_telegram: Send result to Jared via Telegram
        backend: "dalle", "gemini", or "auto" (tries DALL-E first)

    Returns:
        dict with keys: path, prompt, name, timestamp, hash
    """
    # Build the optimized prompt
    prompt = build_image_prompt(visual_description, ai_name)

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_slug = ai_name.lower().replace(" ", "-")[:30] if ai_name else "unnamed"
    desc_hash = hashlib.md5(visual_description.encode()).hexdigest()[:8]

    if output_path is None:
        output_path = str(AVATAR_DIR / f"avatar_{name_slug}_{timestamp}_{desc_hash}.png")

    print(f"[AVATAR] Generating avatar for '{ai_name or 'unnamed'}'...")
    print(f"[AVATAR] Description: {visual_description[:100]}...")
    print(f"[AVATAR] Output: {output_path}")

    # Choose backend
    if backend == "auto":
        if os.environ.get('OPENAI_API_KEY'):
            backend = "dalle"
        elif os.environ.get('GOOGLE_API_KEY') and not os.environ.get('GOOGLE_API_KEY', '').startswith('your-'):
            backend = "gemini"
        else:
            raise ValueError("No image generation API key found. Set OPENAI_API_KEY or GOOGLE_API_KEY in .env")

    try:
        if backend == "dalle":
            _generate_with_dalle(prompt, output_path, size, resolution)
        elif backend == "gemini":
            _generate_with_gemini(prompt, output_path, size, resolution)
        else:
            raise ValueError(f"Unknown backend: {backend}")

        # Get file size
        file_size = os.path.getsize(output_path)
        print(f"[AVATAR] Saved: {output_path} ({file_size / 1024:.1f} KB)")

        # Build result
        result = {
            "path": output_path,
            "prompt": prompt,
            "visual_description": visual_description,
            "name": ai_name,
            "user_id": user_id,
            "timestamp": timestamp,
            "hash": desc_hash,
            "file_size": file_size,
            "backend": backend
        }

        # Save to registry
        _save_to_registry(result)

        # Send to Telegram if requested
        if send_telegram:
            _send_to_telegram(output_path, ai_name)

        return result

    except Exception as e:
        print(f"[AVATAR] ERROR ({backend}): {e}")
        raise


def _generate_with_dalle(prompt: str, output_path: str, size: str = "1024x1024", quality: str = "standard"):
    """Generate avatar using OpenAI DALL-E 3."""
    import openai

    client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    print(f"[AVATAR] Using DALL-E 3 (size={size}, quality={quality})")

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
        response_format="b64_json"
    )

    # Decode and save
    image_data = base64.b64decode(response.data[0].b64_json)
    with open(output_path, 'wb') as f:
        f.write(image_data)

    # Log the revised prompt (DALL-E 3 sometimes rewrites)
    if response.data[0].revised_prompt:
        print(f"[AVATAR] DALL-E revised prompt: {response.data[0].revised_prompt[:150]}...")


def _generate_with_gemini(prompt: str, output_path: str, size: str = "1:1", resolution: str = "2K"):
    """Generate avatar using Google Gemini 3 Pro Image."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])
    print(f"[AVATAR] Using Gemini 3 Pro Image (size={size}, resolution={resolution})")

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio=size,
                image_size=resolution
            ),
        )
    )

    for part in response.parts:
        if part.inline_data is not None:
            image = part.as_image()
            image.save(output_path)
            return

    raise RuntimeError("Gemini returned no image")


def generate_avatar_variations(
    visual_description: str,
    ai_name: str = "",
    count: int = 3
) -> list:
    """Generate multiple avatar variations for the AI to choose from.

    Adds slight variations to the prompt for each generation.
    """
    variations = [
        "",  # Base prompt as-is
        "\nEmphasize the warm, organic qualities. More flowing, less geometric.",
        "\nEmphasize the crystalline, structured qualities. More geometric, less fluid.",
        "\nEmphasize the ethereal, cosmic qualities. More vast and spacious.",
    ]

    results = []
    for i in range(min(count, len(variations))):
        desc = visual_description + variations[i]
        result = generate_avatar(
            visual_description=desc,
            ai_name=ai_name,
            output_path=str(AVATAR_DIR / f"avatar_{ai_name.lower().replace(' ', '-')[:20]}_v{i+1}.png"),
            send_telegram=False
        )
        if result:
            results.append(result)
            print(f"[AVATAR] Variation {i+1}/{count} complete")

    return results


def _save_to_registry(result: dict):
    """Save avatar metadata to the registry for tracking."""
    registry = []
    if AVATAR_REGISTRY.exists():
        try:
            with open(AVATAR_REGISTRY) as f:
                registry = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            registry = []

    # Don't store the full prompt in registry (too large)
    entry = {
        "path": result["path"],
        "name": result["name"],
        "user_id": result.get("user_id", ""),
        "timestamp": result["timestamp"],
        "hash": result["hash"],
        "file_size": result["file_size"],
        "visual_description": result["visual_description"][:200]
    }
    registry.append(entry)

    AVATAR_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    with open(AVATAR_REGISTRY, 'w') as f:
        json.dump(registry, f, indent=2)


def _send_to_telegram(file_path: str, ai_name: str = ""):
    """Send generated avatar to Jared via Telegram."""
    import subprocess
    caption = f"Generated avatar for AI: {ai_name}" if ai_name else "Generated avatar"
    try:
        subprocess.run(
            ["./tools/tg_send.sh", "--photo", file_path, caption],
            cwd=str(Path(__file__).parent.parent),
            capture_output=True, text=True, timeout=30
        )
    except Exception as e:
        print(f"[AVATAR] Telegram send failed: {e}")


# ============================================================
# WordPress Integration Helpers
# ============================================================

def upload_avatar_to_wordpress(avatar_path: str, ai_name: str = "") -> dict:
    """Upload an avatar image to WordPress media library.

    Returns dict with WordPress media ID and URL.
    """
    import requests

    site = 'https://purebrain.ai'
    auth = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD', ''))

    filename = Path(avatar_path).name
    mime_type = 'image/png'

    with open(avatar_path, 'rb') as f:
        r = requests.post(
            f'{site}/wp-json/wp/v2/media',
            auth=auth,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': mime_type
            },
            data=f.read()
        )

    if r.status_code in (200, 201):
        media = r.json()
        result = {
            "id": media["id"],
            "url": media["source_url"],
            "filename": filename
        }
        print(f"[AVATAR] Uploaded to WordPress: ID {result['id']}, URL: {result['url']}")
        return result
    else:
        print(f"[AVATAR] WordPress upload failed: HTTP {r.status_code}")
        print(r.text[:300])
        return None


# ============================================================
# CLI Entry Point
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python avatar_generator.py <visual_description> [ai_name]")
        print()
        print("Example:")
        print('  python avatar_generator.py "A shifting aurora of deep blues and warm oranges" "Cairn"')
        sys.exit(1)

    description = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else ""

    result = generate_avatar(
        visual_description=description,
        ai_name=name,
        send_telegram=True
    )

    if result:
        print(f"\nAvatar generated successfully!")
        print(f"  Path: {result['path']}")
        print(f"  Name: {result['name']}")
        print(f"  Size: {result['file_size'] / 1024:.1f} KB")
    else:
        print("Avatar generation failed.")
        sys.exit(1)
