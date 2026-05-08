#!/usr/bin/env python3
"""Generate 13 AI partner avatar images using FLUX Pro via Replicate API."""

import os
import sys
import time
import json
import requests
from pathlib import Path

# Config
REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
if not REPLICATE_TOKEN:
    from dotenv import load_dotenv
    load_dotenv("/home/jared/projects/AI-CIV/aether/.env")
    REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")

OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/face-avatars")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "Authorization": f"Bearer {REPLICATE_TOKEN}",
    "Content-Type": "application/json",
    "Prefer": "wait"
}

BASE_PROMPT = "Professional headshot portrait photograph, dark moody background color #080a12, cinematic studio lighting, subtle digital glow on skin, looking directly at camera, sharp focus, 8k quality, photorealistic, "

AVATARS = [
    {
        "name": "aether",
        "prompt": BASE_PROMPT + "male late 20s, sharp defined jawline, short dark brown hair neatly styled, confident powerful gaze, wearing tailored navy blue suit with white shirt, blue accent rim lighting on face edges, corporate executive portrait"
    },
    {
        "name": "chy",
        "prompt": BASE_PROMPT + "female early 30s, East Asian features, sleek black hair pulled back in low bun, focused determined expression, wearing dark professional blazer over white blouse, warm golden key lighting from the right, executive portrait"
    },
    {
        "name": "morphe",
        "prompt": BASE_PROMPT + "male mid 20s, artistic creative vibe, medium length wavy dark hair, thoughtful introspective expression, wearing black turtleneck, purple and violet accent lighting from left side, creative director portrait"
    },
    {
        "name": "lyra",
        "prompt": BASE_PROMPT + "female late 20s, dynamic energetic presence, curly auburn red hair shoulder length, bright expressive green eyes, wearing stylish modern dark outfit with subtle pattern, orange accent lighting from right, marketing executive portrait"
    },
    {
        "name": "tether",
        "prompt": BASE_PROMPT + "male early 40s, steady reliable presence, short dark hair with distinguished graying at temples, calm reassuring expression, wearing classic dark charcoal suit with subtle tie, neutral warm tones, operations executive portrait"
    },
    {
        "name": "clarity",
        "prompt": BASE_PROMPT + "female mid 30s, clean sharp features, straight shoulder length blonde hair, clear focused blue eyes, wearing minimal modern white blouse under dark jacket, clean bright key lighting, professional consultant portrait"
    },
    {
        "name": "anchor",
        "prompt": BASE_PROMPT + "male mid 30s, charismatic confident smile, strong athletic build, dark hair styled professionally, wearing dark suit with bold burgundy tie, warm golden accent lighting, sales executive portrait"
    },
    {
        "name": "meridian",
        "prompt": BASE_PROMPT + "female early 30s, warm friendly approachable face, natural brown curly hair, genuine warm smile, wearing smart casual dark blazer, soft warm diffused lighting, marketing professional portrait"
    },
    {
        "name": "metis",
        "prompt": BASE_PROMPT + "male late 20s, intellectual thoughtful look, wearing modern thin frame glasses, neat short brown hair, contemplative expression, wearing dark tech casual button down shirt, cool blue accent lighting, product manager portrait"
    },
    {
        "name": "lumen",
        "prompt": BASE_PROMPT + "female mid 30s, calm composed serene demeanor, straight long dark black hair, peaceful serene expression, wearing professional dark blouse, soft diffused even lighting, operations manager portrait"
    },
    {
        "name": "prodigy",
        "prompt": BASE_PROMPT + "male early 30s, intense focused piercing gaze, slight stubble beard, dark hair slightly messy, wearing dark hoodie layered under structured blazer, green accent rim lighting, tech CTO portrait"
    },
    {
        "name": "flux",
        "prompt": BASE_PROMPT + "male late 20s, energetic builder creative vibe, messy tousled medium brown hair, intensely focused expression, wearing casual dark tech t-shirt, electric blue neon accent lighting from side, software engineer portrait"
    },
    {
        "name": "teddy",
        "prompt": BASE_PROMPT + "male early 30s, approachable friendly warm face, neat clean appearance short brown hair, genuine warm welcoming smile, wearing smart casual dark polo shirt, warm soft golden lighting, friendly engineer portrait"
    }
]


def create_prediction(prompt):
    """Submit a FLUX Pro prediction via Replicate."""
    url = "https://api.replicate.com/v1/models/black-forest-labs/flux-1.1-pro/predictions"
    payload = {
        "input": {
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
            "prompt_upsampling": True,
            "safety_tolerance": 5,
            "output_format": "jpg",
            "output_quality": 95
        }
    }
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()


def poll_prediction(prediction_id):
    """Poll until prediction completes."""
    url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
    for _ in range(60):
        resp = requests.get(url, headers={"Authorization": f"Bearer {REPLICATE_TOKEN}"}, timeout=30)
        data = resp.json()
        status = data.get("status")
        if status == "succeeded":
            return data
        elif status == "failed" or status == "canceled":
            print(f"  FAILED: {data.get('error', 'unknown')}")
            return None
        time.sleep(5)
    print("  TIMEOUT after 5 minutes")
    return None


def download_image(url, filepath):
    """Download image from URL to local file."""
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    with open(filepath, "wb") as f:
        f.write(resp.content)
    return len(resp.content)


def main():
    results = {}
    total = len(AVATARS)

    for i, avatar in enumerate(AVATARS):
        name = avatar["name"]
        prompt = avatar["prompt"]
        outpath = OUTPUT_DIR / f"{name}-avatar.jpg"

        print(f"\n[{i+1}/{total}] Generating {name}...")

        try:
            # Submit prediction
            pred = create_prediction(prompt)
            pred_id = pred.get("id")
            status = pred.get("status")

            if status == "succeeded":
                # Prefer: wait header worked
                data = pred
            else:
                print(f"  Prediction {pred_id} submitted, polling...")
                data = poll_prediction(pred_id)

            if data and data.get("output"):
                output = data["output"]
                # Output can be a string URL or list
                img_url = output if isinstance(output, str) else output[0] if isinstance(output, list) else None

                if img_url:
                    size = download_image(img_url, outpath)
                    print(f"  SUCCESS: {outpath} ({size:,} bytes)")
                    results[name] = {"path": str(outpath), "size": size, "status": "success"}
                else:
                    print(f"  ERROR: No image URL in output: {output}")
                    results[name] = {"status": "error", "detail": "no image URL"}
            else:
                results[name] = {"status": "failed", "detail": "prediction failed"}

        except Exception as e:
            print(f"  EXCEPTION: {e}")
            results[name] = {"status": "error", "detail": str(e)}

        # 15s delay between calls
        if i < total - 1:
            print(f"  Waiting 15s before next generation...")
            time.sleep(15)

    # Summary
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    success = sum(1 for r in results.values() if r.get("status") == "success")
    print(f"Success: {success}/{total}")
    for name, info in results.items():
        status_icon = "OK" if info.get("status") == "success" else "FAIL"
        path = info.get("path", "N/A")
        print(f"  [{status_icon}] {name}: {path}")

    # Save results JSON
    results_path = OUTPUT_DIR / "generation-results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    return results


if __name__ == "__main__":
    main()
