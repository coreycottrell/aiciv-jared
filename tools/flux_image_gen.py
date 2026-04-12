#!/usr/bin/env python3
"""
FLUX Image Generation via Replicate API

Supports FLUX.2 Dev (high quality, ~$0.012/MP) and FLUX.1 Schnell (fast/cheap).
Brand-aware presets for PureBrain content.

Usage:
  python3 tools/flux_image_gen.py "A futuristic glass hexagon" --output banner.png
  python3 tools/flux_image_gen.py "prompt" --model dev --aspect 16:9 --output filename.png
  python3 tools/flux_image_gen.py "prompt" --preset blog-banner --output banner.png
  python3 tools/flux_image_gen.py "prompt" --preset social-post --output social.png

Models:
  dev      - FLUX.2 Dev: High quality, 2.5s, ~$0.012/megapixel (default)
  schnell  - FLUX.1 Schnell: Fast, 4 steps, cheapest
  pro      - FLUX.2 Pro: Highest quality, 6s, ~$0.015+$0.015/megapixel

Presets:
  blog-banner  - 16:9, PureBrain dark+neural aesthetic
  social-post  - 1:1, Clean dark minimalist tech
  investor     - 16:9, Professional premium dark
  story        - 9:16, Vertical mobile format
  linkedin     - 4:5, Cinematic window, orange+blue, photorealistic (1080x1350)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Resolve project root (parent of tools/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env manually for REPLICATE_API_TOKEN
def load_env():
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = value

load_env()

# ---------------------------------------------------------------------------
# Brand presets
# ---------------------------------------------------------------------------
PRESETS = {
    "blog-banner": {
        "aspect_ratio": "16:9",
        "suffix": (
            "futuristic dark background color #080a12, "
            "cerulean blue #2a93c1 and orange #f1420b accent lighting, "
            "ethereal AI brain neural network aesthetic, "
            "glass morphism translucent surfaces, "
            "volumetric lighting, cinematic composition, "
            "no text, no logos, no watermarks"
        ),
    },
    "social-post": {
        "aspect_ratio": "1:1",
        "suffix": (
            "clean dark background #080a12, "
            "minimalist technology aesthetic, "
            "blue #2a93c1 and orange #f1420b subtle accents, "
            "modern digital art, sharp details, "
            "no text, no logos, no watermarks"
        ),
    },
    "investor": {
        "aspect_ratio": "16:9",
        "suffix": (
            "professional premium dark theme #080a12, "
            "subtle technology elements, "
            "clean elegant composition, "
            "soft blue #2a93c1 accent lighting, "
            "cinematic, high-end corporate feel, "
            "no text, no logos, no watermarks"
        ),
    },
    "story": {
        "aspect_ratio": "9:16",
        "suffix": (
            "dark background #080a12, "
            "vertical composition optimized for mobile, "
            "blue #2a93c1 and orange #f1420b neon accents, "
            "futuristic AI aesthetic, dramatic lighting, "
            "no text, no logos, no watermarks"
        ),
    },
    "linkedin": {
        "aspect_ratio": "4:5",
        "suffix": (
            "cinematic lighting, vibrant orange #f1420b and cerulean blue #2a93c1 color palette, "
            "high resolution photorealistic commercial style, "
            "futuristic AI technology aesthetic, dramatic composition, "
            "full frame 4:5 vertical, no black borders, fill entire canvas, "
            "no text, no logos, no watermarks"
        ),
    },
}

# Model ID mapping
MODEL_MAP = {
    "dev": "black-forest-labs/flux-2-dev",
    "schnell": "black-forest-labs/flux-schnell",
    "pro": "black-forest-labs/flux-2-pro",
}

# Approximate cost per megapixel (USD)
COST_PER_MP = {
    "dev": 0.012,
    "schnell": 0.003,
    "pro": 0.030,
}

# Megapixels by aspect ratio (at default resolution)
ASPECT_MP = {
    "1:1": 1.0,
    "16:9": 1.0,
    "9:16": 1.0,
    "21:9": 1.0,
    "3:2": 1.0,
    "2:3": 1.0,
    "4:5": 1.0,
    "5:4": 1.0,
    "3:4": 1.0,
    "4:3": 1.0,
    "9:21": 1.0,
}

VALID_ASPECTS = list(ASPECT_MP.keys())
VALID_FORMATS = ["png", "jpg", "webp"]

# ---------------------------------------------------------------------------
# Cost tracking
# ---------------------------------------------------------------------------
COST_LOG = PROJECT_ROOT / "logs" / "flux-generations.json"


def log_generation(model: str, prompt: str, aspect: str, output_path: str, duration_s: float):
    """Append a generation record to the cost log."""
    mp = ASPECT_MP.get(aspect, 1.0)
    est_cost = COST_PER_MP.get(model, 0.012) * mp

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "model_id": MODEL_MAP[model],
        "prompt": prompt[:200],
        "aspect_ratio": aspect,
        "megapixels": mp,
        "estimated_cost_usd": round(est_cost, 4),
        "duration_seconds": round(duration_s, 2),
        "output_path": str(output_path),
    }

    entries = []
    if COST_LOG.exists():
        try:
            entries = json.loads(COST_LOG.read_text())
        except (json.JSONDecodeError, Exception):
            entries = []

    entries.append(entry)
    COST_LOG.parent.mkdir(parents=True, exist_ok=True)
    COST_LOG.write_text(json.dumps(entries, indent=2) + "\n")

    return est_cost


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
def generate_image(
    prompt: str,
    model: str = "dev",
    aspect_ratio: str = "1:1",
    output_path: str = "output.png",
    output_format: str = "png",
    output_quality: int = 95,
    seed: int | None = None,
    disable_safety: bool = False,
) -> Path:
    """Generate an image using FLUX via Replicate API.

    Args:
        prompt: Text description of the image to generate.
        model: One of 'dev', 'schnell', 'pro'.
        aspect_ratio: Aspect ratio string (e.g. '16:9', '1:1').
        output_path: Where to save the downloaded image.
        output_format: 'png', 'jpg', or 'webp'.
        output_quality: JPEG/WebP quality 0-100.
        seed: Optional seed for reproducibility.
        disable_safety: Disable safety checker.

    Returns:
        Path to the saved image file.
    """
    import replicate

    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        raise RuntimeError(
            "REPLICATE_API_TOKEN not set. Add it to .env or export it."
        )

    model_id = MODEL_MAP.get(model)
    if not model_id:
        raise ValueError(f"Unknown model '{model}'. Choose from: {list(MODEL_MAP.keys())}")

    if aspect_ratio not in VALID_ASPECTS:
        raise ValueError(f"Invalid aspect ratio '{aspect_ratio}'. Choose from: {VALID_ASPECTS}")

    # Build input payload
    input_params = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "output_format": output_format,
        "output_quality": output_quality,
        "num_outputs": 1,
    }

    if seed is not None:
        input_params["seed"] = seed

    if disable_safety:
        input_params["disable_safety_checker"] = True

    # Add inference steps for schnell (needs fewer)
    if model == "schnell":
        input_params["num_inference_steps"] = 4

    print(f"[FLUX] Model: {model_id}")
    print(f"[FLUX] Aspect: {aspect_ratio} | Format: {output_format} | Quality: {output_quality}")
    print(f"[FLUX] Prompt: {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
    print(f"[FLUX] Generating...")

    start = time.time()
    output = replicate.run(model_id, input=input_params)
    duration = time.time() - start

    # output is a list of FileOutput objects or URLs
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle different output types
    if isinstance(output, list) and len(output) > 0:
        item = output[0]
    else:
        item = output

    # If it's a file-like object with .read()
    if hasattr(item, "read"):
        with open(out_path, "wb") as f:
            f.write(item.read())
    # If it's a URL string
    elif isinstance(item, str) and item.startswith("http"):
        import urllib.request
        urllib.request.urlretrieve(item, out_path)
    # If it's an iterator
    elif hasattr(item, "__iter__"):
        with open(out_path, "wb") as f:
            for chunk in item:
                if isinstance(chunk, bytes):
                    f.write(chunk)
                elif isinstance(chunk, str) and chunk.startswith("http"):
                    import urllib.request
                    urllib.request.urlretrieve(chunk, out_path)
                    break
    else:
        raise RuntimeError(f"Unexpected output type: {type(item)} = {item}")

    file_size = out_path.stat().st_size
    est_cost = log_generation(model, prompt, aspect_ratio, str(out_path), duration)

    print(f"[FLUX] Done in {duration:.1f}s")
    print(f"[FLUX] Saved: {out_path} ({file_size / 1024:.0f} KB)")
    print(f"[FLUX] Est. cost: ${est_cost:.4f}")

    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="FLUX Image Generation via Replicate API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument(
        "--model", "-m",
        choices=list(MODEL_MAP.keys()),
        default="dev",
        help="Model variant (default: dev)",
    )
    parser.add_argument(
        "--aspect", "-a",
        choices=VALID_ASPECTS,
        default=None,
        help="Aspect ratio (default: 1:1, or preset default)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (default: auto-generated in current dir)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=VALID_FORMATS,
        default="png",
        help="Output format (default: png)",
    )
    parser.add_argument(
        "--quality", "-q",
        type=int,
        default=95,
        help="Output quality 0-100 (default: 95)",
    )
    parser.add_argument(
        "--preset", "-p",
        choices=list(PRESETS.keys()),
        default=None,
        help="Brand preset (appends style suffix + sets aspect ratio)",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--no-safety",
        action="store_true",
        help="Disable safety checker",
    )

    args = parser.parse_args()

    # Apply preset
    final_prompt = args.prompt
    aspect = args.aspect or "1:1"

    if args.preset:
        preset = PRESETS[args.preset]
        final_prompt = f"{args.prompt}. {preset['suffix']}"
        if args.aspect is None:
            aspect = preset["aspect_ratio"]

    # Auto-generate output path if not specified
    if args.output:
        output_path = args.output
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        preset_tag = f"-{args.preset}" if args.preset else ""
        output_path = f"flux-{args.model}{preset_tag}-{ts}.{args.format}"

    result = generate_image(
        prompt=final_prompt,
        model=args.model,
        aspect_ratio=aspect,
        output_path=output_path,
        output_format=args.format,
        output_quality=args.quality,
        seed=args.seed,
        disable_safety=args.no_safety,
    )

    print(f"\n[RESULT] {result}")
    return str(result)


if __name__ == "__main__":
    main()
