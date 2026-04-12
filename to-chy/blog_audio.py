#!/usr/bin/env python3
"""
blog_audio.py — ElevenLabs TTS audio generation for blog posts.

Usage (CLI):
    python3 tools/blog_audio.py --input /path/to/blog.md --output /path/to/audio.mp3

Usage (Python import):
    from blog_audio import generate_blog_audio
    audio_path = generate_blog_audio(markdown_path, output_path)
"""

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env from aether root (handles invocation from any cwd)
_SCRIPT_DIR = Path(__file__).resolve().parent
_ENV_PATH = _SCRIPT_DIR.parent / ".env"
load_dotenv(_ENV_PATH)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "RX0kjGhuL9AMRVJm2dG5")
ELEVENLABS_MODEL = "eleven_multilingual_v2"
ELEVENLABS_CHUNK_LIMIT = 4800  # stay safely under 5000-char API limit


# ---------------------------------------------------------------------------
# Text extraction — strips everything that should not be read aloud
# ---------------------------------------------------------------------------

def _strip_front_matter(text: str) -> str:
    """Remove YAML-style front matter (--- ... ---) at the top of the file."""
    text = text.strip()
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:].lstrip()
    return text


def _strip_html(text: str) -> str:
    """Remove all HTML tags."""
    return re.sub(r"<[^>]+>", " ", text)


def _strip_markdown_formatting(text: str) -> str:
    """Convert markdown syntax to plain text."""
    # Code blocks (``` ... ```)
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Inline code
    text = re.sub(r"`[^`]+`", "", text)
    # Images
    text = re.sub(r"!\[([^\]]*)\]\([^\)]*\)", "", text)
    # Links — keep the display text
    text = re.sub(r"\[([^\]]+)\]\([^\)]*\)", r"\1", text)
    # Bold / italic
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    # ATX headings (# ## ### etc.)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Blockquotes
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    # Unordered list markers
    text = re.sub(r"^[\-\*\+]\s+", "", text, flags=re.MULTILINE)
    # Ordered list markers
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    return text


def _strip_metadata_fields(text: str) -> str:
    """Remove document metadata lines like **Author**: ..., **Date**: ..."""
    text = re.sub(
        r"^\*\*(Author|Date|Target publish|Status|Slug|Word count|Read time|Tags|Category)\*\*:.*$",
        "",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    return text


def _strip_cta_blocks(text: str) -> str:
    """Remove <!-- Standard CTA block --> ... </div> chunks."""
    # HTML comment blocks
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return text


def _strip_faq_sections(text: str) -> str:
    """Remove FAQ sections (commonly labelled 'Frequently Asked Questions')."""
    # Remove from 'Frequently Asked Questions' heading to end of FAQ block
    text = re.sub(
        r"(#+\s*Frequently Asked Questions.*?)(?=\n##|\Z)",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return text


def _strip_transparency_blocks(text: str) -> str:
    """Remove Daily Recap / Transparency blocks."""
    text = re.sub(
        r"(#+\s*(Daily Recap|Transparency).*?)(?=\n##|\Z)",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return text


def _strip_internal_notes(text: str) -> str:
    """Remove lines that look like internal publishing notes."""
    lines = text.splitlines()
    filtered = []
    note_patterns = [
        re.compile(r"^\*\*Status\*\*:", re.IGNORECASE),
        re.compile(r"DRAFT", re.IGNORECASE),
        re.compile(r"Do NOT publish", re.IGNORECASE),
        re.compile(r"For Jared", re.IGNORECASE),
    ]
    for line in lines:
        if not any(p.search(line) for p in note_patterns):
            filtered.append(line)
    return "\n".join(filtered)


def _clean_whitespace(text: str) -> str:
    """Collapse multiple blank lines and strip excess whitespace."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()


def extract_readable_text(markdown_path: str) -> str:
    """
    Read a blog markdown file and return clean text suitable for TTS.
    Strips: front matter, HTML, markdown syntax, FAQ, CTA, transparency blocks,
    internal notes, and metadata fields.
    """
    with open(markdown_path, "r", encoding="utf-8") as fh:
        raw = fh.read()

    text = _strip_front_matter(raw)
    text = _strip_cta_blocks(text)         # removes HTML comments first
    text = _strip_html(text)               # remove remaining HTML tags
    text = _strip_faq_sections(text)
    text = _strip_transparency_blocks(text)
    text = _strip_metadata_fields(text)
    text = _strip_internal_notes(text)
    text = _strip_markdown_formatting(text)
    text = _clean_whitespace(text)

    return text


# ---------------------------------------------------------------------------
# ElevenLabs API
# ---------------------------------------------------------------------------

def _tts_chunk(text: str, api_key: str, voice_id: str) -> bytes:
    """Send one text chunk to ElevenLabs and return raw MP3 bytes."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(
            f"ElevenLabs API error {resp.status_code}: {resp.text[:400]}"
        )
    return resp.content


def _split_into_chunks(text: str, limit: int = ELEVENLABS_CHUNK_LIMIT) -> list[str]:
    """
    Split text at paragraph breaks so each chunk is <= limit characters.
    Paragraphs that exceed the limit are split at sentence boundaries.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        # If the paragraph itself is too long, split at sentence boundaries
        if len(para) > limit:
            sentences = re.split(r"(?<=[.!?])\s+", para)
            for sentence in sentences:
                if len(current) + len(sentence) + 2 > limit:
                    if current:
                        chunks.append(current.strip())
                    current = sentence
                else:
                    current = (current + "  " + sentence).strip() if current else sentence
        else:
            if len(current) + len(para) + 2 > limit:
                if current:
                    chunks.append(current.strip())
                current = para
            else:
                current = (current + "\n\n" + para).strip() if current else para

    if current:
        chunks.append(current.strip())

    return chunks


def generate_blog_audio(markdown_path: str, output_path: str) -> str:
    """
    Generate an MP3 audio file from a blog markdown file using ElevenLabs TTS.

    Args:
        markdown_path: Path to the .md blog file.
        output_path:   Destination path for the .mp3 file.

    Returns:
        The resolved output_path string on success.

    Raises:
        RuntimeError: On API or file I/O errors.
    """
    if not ELEVENLABS_API_KEY:
        raise RuntimeError(
            "ELEVENLABS_API_KEY not set. Add it to .env or export it as an env var."
        )

    print(f"[blog_audio] Reading: {markdown_path}")
    text = extract_readable_text(markdown_path)
    char_count = len(text)
    print(f"[blog_audio] Extracted {char_count} characters of readable text.")

    chunks = _split_into_chunks(text)
    print(f"[blog_audio] Split into {len(chunks)} chunk(s) for TTS.")

    audio_parts: list[bytes] = []
    for idx, chunk in enumerate(chunks, 1):
        print(f"[blog_audio] Requesting TTS for chunk {idx}/{len(chunks)} ({len(chunk)} chars)...")
        audio_parts.append(_tts_chunk(chunk, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID))
        print(f"[blog_audio] Chunk {idx} received ({len(audio_parts[-1])} bytes).")

    # Concatenate all MP3 chunks into a single file
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    combined = b"".join(audio_parts)
    with open(output_path, "wb") as fh:
        fh.write(combined)

    total_bytes = len(combined)
    # Rough estimate: MP3 at ~128kbps stereo = ~16KB/s; mono TTS ~8KB/s
    est_seconds = total_bytes / 8000
    est_minutes = est_seconds / 60
    print(
        f"[blog_audio] Saved {total_bytes:,} bytes to: {output_path}"
    )
    print(
        f"[blog_audio] Estimated duration: ~{est_minutes:.1f} minutes ({est_seconds:.0f}s)"
    )

    return str(Path(output_path).resolve())


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate TTS audio from a blog markdown file using ElevenLabs."
    )
    parser.add_argument(
        "--input", required=True, help="Path to the blog .md file."
    )
    parser.add_argument(
        "--output", required=True, help="Destination path for the output .mp3 file."
    )
    args = parser.parse_args()

    try:
        result = generate_blog_audio(args.input, args.output)
        print(f"[blog_audio] Done. Audio file: {result}")
    except Exception as exc:
        print(f"[blog_audio] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
