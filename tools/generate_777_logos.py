#!/usr/bin/env python3
"""
Generate 7 variants of the 777 Triangle OS logo via FLUX Pro on Replicate.
V2: Improved prompts with precise 7-arrangement, material styles, background removal.
"""

import requests
import time
import os
import sys
import numpy as np

from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

from PIL import Image

REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
OUTPUT_DIR = os.path.expanduser("~/exports/portal-files/777-logos-v2")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Core logo description - PRECISE about the 777 triangular arrangement
CORE_DESC = (
    "Professional logo mark icon design, centered composition with generous negative space. "
    "Two large numeral 7s placed side by side, angled inward so their tops lean toward each other "
    "and their bases spread apart, forming an inverted triangle or V shape pointing downward. "
    "A third numeral 7 is placed centered on top, overlapping where the two bottom 7s meet. "
    "The three 7s together clearly read as 777 while forming a triangular geometric shape. "
    "No text, no words, no letters besides the three numeral 7s. "
    "Pure black background. "
)

VARIANTS = [
    {
        "name": "clean-geometric",
        "prompt": (
            CORE_DESC +
            "Style: Ultra clean geometric vector design. Perfectly sharp edges, mathematically precise angles. "
            "Smooth gradient flowing from vibrant orange #f1420b on the left side to cerulean blue #2a93c1 on the right. "
            "Flat minimal design with subtle beveled edge for depth. No texture, no noise. "
            "Swiss design precision, Dieter Rams inspired minimalism. "
            "Professional corporate logo mark, would work at 16px favicon and 4000px billboard. "
            "Pure black background #000000."
        ),
    },
    {
        "name": "glass-material",
        "prompt": (
            CORE_DESC +
            "Style: Gleb Kuznetsov style translucent crystal glass material. "
            "The 7s are made of thick transparent glass with visible light refraction inside. "
            "Subsurface scattering at thick glass edges, chromatic aberration where light passes through. "
            "Fresnel edge glow in cerulean blue #2a93c1, internal caustics casting orange #f1420b light patterns. "
            "Volumetric god rays passing through the glass body. "
            "Dramatic rim lighting on glass edges, photorealistic CGI render, 8K quality. "
            "Deep black background #080a12."
        ),
    },
    {
        "name": "metallic-chrome",
        "prompt": (
            CORE_DESC +
            "Style: Polished chrome titanium metal with mirror-like reflections. "
            "Subtle environment reflections showing abstract blue #2a93c1 and orange #f1420b studio lighting. "
            "Brushed metal texture on flat surfaces with razor-sharp beveled edges catching specular highlights. "
            "Premium luxury automotive finish, like a Rolls Royce hood ornament. "
            "Product photography lighting setup with key light, fill, and rim. "
            "Photorealistic CGI render, 8K quality. Deep black background #080a12."
        ),
    },
    {
        "name": "neon-glow",
        "prompt": (
            CORE_DESC +
            "Style: Bright neon light tubes forming the outline of each 7. "
            "Left bottom 7 glowing intense orange neon #f1420b, right bottom 7 glowing cerulean blue neon #2a93c1. "
            "Top 7 transitions from orange to blue along its stroke. "
            "Intense volumetric neon glow with light bleeding and scattering in atmospheric fog. "
            "Reflections on glossy dark ground plane below. "
            "Cyberpunk futuristic Blade Runner aesthetic. "
            "Deep black background #080a12. Photorealistic CGI render, 8K quality."
        ),
    },
    {
        "name": "gradient-mesh",
        "prompt": (
            CORE_DESC +
            "Style: Smooth flowing gradient mesh fill across all three 7s as one unified shape. "
            "Seamless color flow from orange #f1420b through magenta and purple to cerulean blue #2a93c1. "
            "Modern flat design with soft rounded edges, subtle inner shadow for dimension. "
            "Apple-style gradient quality, Instagram/Firefox logo level color blending. "
            "Contemporary tech brand aesthetic, silk-smooth transitions. "
            "Pure black background #000000. Clean vector logo design."
        ),
    },
    {
        "name": "embossed-metal",
        "prompt": (
            CORE_DESC +
            "Style: The 7s appear stamped and embossed into a brushed dark titanium metal surface. "
            "Raised 3D relief with sharp edges catching dramatic side light. "
            "Subtle blue #2a93c1 anodized tint on the raised metal surfaces. "
            "Orange #f1420b warm accent light from above illuminating the top edges. "
            "Executive premium finish like a luxury Swiss watch case detail or credit card embossing. "
            "Photorealistic product macro photography with shallow depth of field. "
            "Dark matte black metal background."
        ),
    },
    {
        "name": "holographic-iridescent",
        "prompt": (
            CORE_DESC +
            "Style: Holographic iridescent material that shifts between orange #f1420b and blue #2a93c1. "
            "Oil-on-water thin-film interference patterns across the surface. "
            "Prismatic rainbow edge highlights, holographic foil shimmer. "
            "Like a premium holographic trading card or Apple Vision Pro material. "
            "Dramatic studio lighting revealing the color-shift iridescence. "
            "Premium futuristic material science aesthetic. "
            "Photorealistic CGI render, 8K quality. Deep black background #080a12."
        ),
    },
]


def generate_flux_image(prompt, output_path, variant_name):
    """Generate image via FLUX 1.1 Pro on Replicate using REST API."""
    print(f"  Calling FLUX 1.1 Pro...")

    try:
        response = requests.post(
            "https://api.replicate.com/v1/models/black-forest-labs/flux-1.1-pro/predictions",
            headers={
                "Authorization": f"Bearer {REPLICATE_TOKEN}",
                "Content-Type": "application/json",
                "Prefer": "wait",
            },
            json={
                "input": {
                    "prompt": prompt,
                    "aspect_ratio": "1:1",
                    "output_format": "png",
                    "output_quality": 100,
                    "safety_tolerance": 5,
                    "prompt_upsampling": True,
                }
            },
            timeout=180,
        )

        if response.status_code == 429:
            retry_after = int(response.headers.get("retry-after", "30"))
            print(f"  Rate limited, waiting {retry_after + 5}s...")
            time.sleep(retry_after + 5)
            return generate_flux_image(prompt, output_path, variant_name)

        if response.status_code != 200 and response.status_code != 201:
            print(f"  HTTP {response.status_code}: {response.text[:200]}")
            # Try polling approach
            if response.status_code == 422:
                return False

        data = response.json()

        # Handle async polling if needed
        if data.get("status") in ("starting", "processing"):
            poll_url = data.get("urls", {}).get("get", "")
            if poll_url:
                print(f"  Polling for completion...")
                for attempt in range(60):
                    time.sleep(5)
                    poll_resp = requests.get(
                        poll_url,
                        headers={"Authorization": f"Bearer {REPLICATE_TOKEN}"},
                    )
                    poll_data = poll_resp.json()
                    if poll_data["status"] == "succeeded":
                        data = poll_data
                        break
                    elif poll_data["status"] == "failed":
                        print(f"  Generation failed: {poll_data.get('error', 'unknown')}")
                        return False

        # Get output URL
        output_url = data.get("output")
        if isinstance(output_url, list):
            output_url = output_url[0]

        if not output_url:
            print(f"  No output URL. Response keys: {list(data.keys())}")
            print(f"  Status: {data.get('status')}")
            return False

        # Download
        img_resp = requests.get(str(output_url), timeout=60)
        img_resp.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(img_resp.content)

        print(f"  Saved raw: {output_path} ({len(img_resp.content) / 1024:.0f}KB)")
        return True

    except requests.exceptions.Timeout:
        print(f"  Timeout!")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def remove_black_background(input_path, output_path, threshold=30):
    """Convert near-black pixels to transparent alpha with smooth edge transition."""
    img = Image.open(input_path).convert("RGBA")
    data = np.array(img)

    r, g, b = data[:, :, 0].astype(float), data[:, :, 1].astype(float), data[:, :, 2].astype(float)
    brightness = np.maximum(r, np.maximum(g, b))

    # Hard transparent for very dark pixels
    hard_mask = brightness < threshold
    data[hard_mask, 3] = 0

    # Gradient transparency for edge pixels (smooth anti-alias)
    edge_low = threshold
    edge_high = threshold + 25
    edge_mask = (brightness >= edge_low) & (brightness < edge_high)
    if np.any(edge_mask):
        edge_alpha = ((brightness[edge_mask] - edge_low) / (edge_high - edge_low) * 255).astype(np.uint8)
        data[edge_mask, 3] = edge_alpha

    result = Image.fromarray(data)
    result.save(output_path, "PNG")

    # Count transparent pixels
    transparent_pct = np.sum(data[:, :, 3] == 0) / (data.shape[0] * data.shape[1]) * 100
    print(f"  Background removed: {transparent_pct:.1f}% transparent -> {output_path}")


def main():
    print("=" * 60)
    print("777 Triangle OS Logo Generation - v2 (REDO)")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60)

    results = []

    for i, variant in enumerate(VARIANTS, 1):
        name = variant["name"]
        prompt = variant["prompt"]

        raw_path = os.path.join(OUTPUT_DIR, f"777-logo-v2-option-{i}-{name}-raw.png")
        final_path = os.path.join(OUTPUT_DIR, f"777-logo-v2-option-{i}-{name}.png")

        print(f"\n[{i}/7] Generating: {name}")
        print(f"  Prompt: {len(prompt)} chars")

        success = generate_flux_image(prompt, raw_path, name)

        if success and os.path.exists(raw_path):
            remove_black_background(raw_path, final_path)
            results.append((name, final_path, True))
        else:
            results.append((name, None, False))

        # Rate limit spacing between calls
        if i < len(VARIANTS):
            print("  Waiting 12s (rate limit)...")
            time.sleep(12)

    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    for name, path, ok in results:
        status = f"OK -> {path}" if ok else "FAILED"
        print(f"  [{name}]: {status}")

    success_count = sum(1 for _, _, ok in results if ok)
    print(f"\n{success_count}/7 generated successfully")
    print(f"Output directory: {OUTPUT_DIR}")
    return success_count


if __name__ == "__main__":
    count = main()
    sys.exit(0 if count > 0 else 1)
