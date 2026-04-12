#!/usr/bin/env python3
"""
replicate_tts.py -- Generate TTS audio using Replicate's Chatterbox model.

Usage:
    python3 tools/replicate_tts.py --text "Hello world" --output /path/to/audio.wav
    python3 tools/replicate_tts.py --input /path/to/text.txt --output /path/to/audio.mp3
    python3 tools/replicate_tts.py --input /path/to/blog.html --output /path/to/audio.mp3 --voice aether

Voices:
    chy     - https://purebrain.ai/voice-refs/chy.wav
    aether  - https://purebrain.ai/voice-refs/aether.mp3
    (or provide a custom URL with --voice-url)

Requires: REPLICATE_API_TOKEN in .env
"""

import argparse
import json
import os
import re
import sys
import time
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

_SCRIPT_DIR = Path(__file__).resolve().parent
_ENV_PATH = _SCRIPT_DIR.parent / ".env"
load_dotenv(_ENV_PATH)

REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
REPLICATE_API = "https://api.replicate.com/v1/predictions"
REPLICATE_VERSION = "1b8422bc49635c20d0a84e387ed20879c0dd09254ecdb4e75dc4bec10ff94e97"

VOICE_REFS = {
    "chy": "https://purebrain.ai/voice-refs/chy.wav",
    "aether": "https://purebrain.ai/voice-refs/aether.mp3",
}

CHUNK_LIMIT = 2000  # Chatterbox works best with shorter texts


def strip_html(text: str) -> str:
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    text = re.sub(r"&#\d+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_blog_text(html: str) -> str:
    """Extract readable blog text from HTML, trimming boilerplate."""
    text = strip_html(html)
    # Try to find article start
    for marker in ["~", "min read"]:
        idx = text.find(marker)
        if idx > 0 and idx < 500:
            # Find next sentence after the marker
            next_period = text.find(". ", idx)
            if next_period > 0:
                text = text[next_period + 2:]
            break

    # Trim FAQ/footer
    for marker in ["Frequently Asked Questions", "Ready to Partner", "Share This",
                    "Related Posts", "The Neural Feed", "Share:"]:
        idx = text.find(marker)
        if idx > 500:
            text = text[:idx]
            break
    return text.strip()


def chunk_text(text: str, limit: int = CHUNK_LIMIT) -> list:
    """Split text into chunks at sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) + 1 > limit and current:
            chunks.append(current.strip())
            current = s
        else:
            current = current + " " + s if current else s
    if current.strip():
        chunks.append(current.strip())
    return chunks


def create_prediction(text: str, voice_url: str) -> dict:
    """Create a Replicate prediction."""
    resp = requests.post(REPLICATE_API, headers={
        "Authorization": f"Bearer {REPLICATE_TOKEN}",
        "Content-Type": "application/json"
    }, json={
        "version": REPLICATE_VERSION,
        "input": {
            "prompt": text,
            "audio_prompt": voice_url,
            "exaggeration": 0.5,
            "cfg_weight": 0.5,
            "temperature": 0.8,
        }
    })
    resp.raise_for_status()
    return resp.json()


def poll_prediction(get_url: str, timeout: int = 120) -> str:
    """Poll until prediction completes. Returns audio URL."""
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(get_url, headers={"Authorization": f"Bearer {REPLICATE_TOKEN}"})
        data = resp.json()
        if data["status"] == "succeeded":
            return data["output"]
        if data["status"] in ("failed", "canceled"):
            raise RuntimeError(f"Prediction {data['status']}: {data.get('error', 'unknown')}")
        time.sleep(1)
    raise TimeoutError(f"Prediction timed out after {timeout}s")


def download_audio(url: str, path: str):
    """Download audio file from URL."""
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(path, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)


def generate_audio(text: str, voice_url: str, output_path: str):
    """Generate audio for text, chunking if needed."""
    chunks = chunk_text(text)
    print(f"[replicate_tts] {len(text)} chars, {len(chunks)} chunk(s)")

    if len(chunks) == 1:
        print(f"[replicate_tts] Generating single chunk...")
        pred = create_prediction(chunks[0], voice_url)
        audio_url = poll_prediction(pred["urls"]["get"])
        download_audio(audio_url, output_path)
        print(f"[replicate_tts] Saved to {output_path}")
        return

    # Multiple chunks: generate individually, then concatenate with ffmpeg
    temp_dir = tempfile.mkdtemp(prefix="replicate_tts_")
    chunk_files = []

    for i, chunk in enumerate(chunks):
        print(f"[replicate_tts] Generating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
        pred = create_prediction(chunk, voice_url)
        audio_url = poll_prediction(pred["urls"]["get"])
        chunk_path = os.path.join(temp_dir, f"chunk_{i:03d}.wav")
        download_audio(audio_url, chunk_path)
        chunk_files.append(chunk_path)

    # Concatenate with ffmpeg
    list_file = os.path.join(temp_dir, "concat.txt")
    with open(list_file, "w") as f:
        for cf in chunk_files:
            f.write(f"file '{cf}'\n")

    ext = Path(output_path).suffix.lower()
    codec = "-c:a libmp3lame -q:a 2" if ext == ".mp3" else "-c:a copy"

    cmd = f"ffmpeg -y -f concat -safe 0 -i {list_file} {codec} {output_path}"
    print(f"[replicate_tts] Concatenating {len(chunk_files)} chunks...")
    os.system(cmd)

    # Cleanup
    for cf in chunk_files:
        os.remove(cf)
    os.remove(list_file)
    os.rmdir(temp_dir)

    size = os.path.getsize(output_path)
    print(f"[replicate_tts] Done. {output_path} ({size:,} bytes)")


def main():
    parser = argparse.ArgumentParser(description="Replicate Chatterbox TTS")
    parser.add_argument("--text", help="Text to speak")
    parser.add_argument("--input", help="Input file (text, markdown, or HTML)")
    parser.add_argument("--output", required=True, help="Output audio file path")
    parser.add_argument("--voice", default="aether", choices=list(VOICE_REFS.keys()),
                        help="Voice preset (default: aether)")
    parser.add_argument("--voice-url", help="Custom voice reference URL (overrides --voice)")
    args = parser.parse_args()

    if not REPLICATE_TOKEN:
        print("[replicate_tts] ERROR: REPLICATE_API_TOKEN not found in .env")
        sys.exit(1)

    voice_url = args.voice_url or VOICE_REFS[args.voice]

    if args.text:
        text = args.text
    elif args.input:
        with open(args.input, "r") as f:
            raw = f.read()
        if args.input.endswith(".html"):
            text = extract_blog_text(raw)
        else:
            text = strip_html(raw) if "<" in raw else raw
    else:
        print("[replicate_tts] ERROR: Provide --text or --input")
        sys.exit(1)

    if not text.strip():
        print("[replicate_tts] ERROR: No text to synthesize")
        sys.exit(1)

    generate_audio(text, voice_url, args.output)


if __name__ == "__main__":
    main()
