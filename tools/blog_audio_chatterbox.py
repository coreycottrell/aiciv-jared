#!/usr/bin/env python3
"""
blog_audio_chatterbox.py — Canonical blog TTS using PureBrain GPU (Chatterbox).

- Voice: `aether` (canonical PureBrain blog narration — the AI author IS the narrator)
- Server: http://37.27.237.109:8950 (GPU Chatterbox Turbo on Vast.ai RTX 3060)
- Output: mp3 (128 kbps mono), written ATOMICALLY (tmp file -> rename only on full success)
- Pre-processing: applies script-to-speech-optimization (cleanForSpeech) so compounds,
  acronyms, domains, currency, etc. sound natural.

CLI:
    python3 tools/blog_audio_chatterbox.py --input path/to/post.md --output path/to/audio.mp3
    python3 tools/blog_audio_chatterbox.py --html  path/to/index.html --output path/to/audio.mp3

Import:
    from blog_audio_chatterbox import generate_blog_audio_chatterbox
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

# Reuse the extractor from blog_audio.py (markdown -> readable text)
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from blog_audio import extract_readable_text  # noqa: E402

# ---------------------------------------------------------------------------
# Canonical configuration — LOCKED
# ---------------------------------------------------------------------------
CHATTERBOX_URL = os.getenv("CHATTERBOX_URL", "http://37.27.237.109:8950")
CANONICAL_VOICE = "aether"          # PureBrain canonical blog narration voice
CHUNK_LIMIT = 1200                   # chars; matches sentence-streaming sweet spot
MP3_BITRATE = "128k"
REQUEST_TIMEOUT = 180
MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# Speech cleanup — per script-to-speech-optimization skill
# ---------------------------------------------------------------------------

# Common pronunciation / acronym fixes for PureBrain blog content
_PRONUNCIATION_MAP = [
    # ---------------------------------------------------------------
    # Names (CONSTITUTIONAL)
    # ---------------------------------------------------------------
    (r"\bAether's\b", "ae-ther's"),
    (r"\bAethers\b", "ae-thers"),
    (r"\bAether\b", "ae-ther"),
    (r"\bChy's\b", "Key's"),
    (r"\bChy\b", "Key"),
    (r"\bMorphe\b", "More-fay"),
    (r"\bDiMAP\b", "die-map"),
    (r"\bPMG\b", "Pure Marketing Group"),

    # ---------------------------------------------------------------
    # Brand
    # ---------------------------------------------------------------
    (r"\bPureBrain\.ai\b", "Pure Brain dot A I"),
    (r"\bPureBrain\b", "Pure Brain"),
    (r"\bPureTechnology\b", "Pure Technology"),
    (r"\bpurebrain\.ai\b", "Pure Brain dot A I"),

    # Compounds that read as one word
    (r"\bcompounds\b", "com-pounds"),
    (r"\bcompounding\b", "com-pounding"),

    # Domains / URLs — never read aloud verbatim
    (r"\bhttps?://\S+", " "),

    # ---------------------------------------------------------------
    # Titles
    # ---------------------------------------------------------------
    (r"\bCEO\b", "C E O"),
    (r"\bCTO\b", "C T O"),
    (r"\bCOO\b", "C O O"),
    (r"\bCFO\b", "C F O"),
    (r"\bCMO\b", "C M O"),
    (r"\bCRO\b", "C R O"),
    (r"\bSVP\b", "senior vice president"),
    (r"\bEVP\b", "executive vice president"),
    (r"\bVP\b", "vice president"),

    # ---------------------------------------------------------------
    # Business acronyms (speak like a CFO)
    # ---------------------------------------------------------------
    (r"\bARPU\b", "are-poo"),
    (r"\bEBITDA\b", "ee-bit-dah"),
    (r"\bCAC\b", "cack"),
    (r"\bCAGR\b", "kagger"),
    (r"\bSaaS\b", "sass"),
    (r"\bMRR\b", "em are are"),
    (r"\bARR\b", "ay are are"),
    (r"\bLTV\b", "L T V"),
    (r"\bROI\b", "are oh eye"),
    (r"\bIPO\b", "eye pee oh"),
    (r"\bKPIs?\b", "K P eyes"),
    (r"\bKPI\b", "K P I"),
    (r"\bTAM\b", "tam"),
    (r"\bSAM\b", "sam"),
    (r"\bSOM\b", "som"),
    (r"\bGTM\b", "go to market"),
    (r"\bPMF\b", "product market fit"),
    (r"\bNRR\b", "net revenue retention"),
    (r"\bAUM\b", "assets under management"),
    (r"\bNDA\b", "N D A"),
    (r"\bOKRs\b", "O K Rs"),
    (r"\bOKR\b", "O K R"),
    (r"\bSEO\b", "S E O"),
    (r"\bCRM\b", "C R M"),
    (r"\bB2B\b", "B to B"),
    (r"\bB2C\b", "B to C"),
    (r"\bD2C\b", "D to C"),
    (r"\bM&A\b", "M and A"),
    (r"\bP&L\b", "P and L"),
    (r"\bR&D\b", "R and D"),
    (r"\bSDK\b", "S D K"),
    (r"\bCPG\b", "C P G"),
    (r"\bQoQ\b", "quarter over quarter"),
    (r"\bYoY\b", "year over year"),
    (r"\bMoM\b", "month over month"),
    (r"\bLPs\b", "L Ps"),
    (r"\bLP\b", "L P"),
    (r"\bGP\b", "G P"),
    (r"\bVCs\b", "V Cs"),
    (r"\bVC\b", "V C"),
    (r"\bPE\b", "P E"),

    # ---------------------------------------------------------------
    # Tech acronyms
    # ---------------------------------------------------------------
    (r"\bAIs\b", "A I s"),
    (r"\bAI\b", "A I"),
    (r"\bAPI\b", "A P I"),
    (r"\bLLMs\b", "L L Ms"),
    (r"\bLLM\b", "L L M"),
    (r"\bSOP\b", "S O P"),

    # ---------------------------------------------------------------
    # Financial / Legal
    # ---------------------------------------------------------------
    (r"\bSeed-2\b", "Seed Two"),
    (r"\bSeries-A\b", "Series A"),
    (r"\bReg D\b", "Reg Dee"),
    (r"\b506\(b\)", "five oh six bee"),

    # ---------------------------------------------------------------
    # Multiplier shorthand (10x, 5x, 1.9x, etc.)
    # ---------------------------------------------------------------
    (r"\b(\d+\.\d+)x\b", r"\1 x"),
    (r"\b(\d+)x\b", r"\1 x"),

    # ---------------------------------------------------------------
    # Currency
    # ---------------------------------------------------------------
    (r"\$(\d+)(?:\.(\d+))?K\b", r"\1 thousand dollars"),
    (r"\$(\d+)(?:\.(\d+))?M\b", r"\1 million dollars"),
    (r"\$(\d+)(?:\.(\d+))?B\b", r"\1 billion dollars"),

    # ---------------------------------------------------------------
    # Punctuation / formatting cleanup
    # ---------------------------------------------------------------
    # Multiple dashes / ellipses -> natural pause
    (r"—", ", "),
    (r"–", ", "),
    (r"\.\.\.", ", "),
    # Strip markdown leftovers if any slipped through
    (r"[\*_`]+", ""),
    # Emoji / non-ASCII glyphs
    (r"[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF\u2600-\u27BF]", ""),
    # Collapse whitespace
    (r"\s+", " "),
]


def clean_for_speech(text: str) -> str:
    """Apply script-to-speech-optimization rules to make text sound natural."""
    for pattern, replacement in _PRONUNCIATION_MAP:
        text = re.sub(pattern, replacement, text)
    # Ensure sentence-ending punctuation exists so Chatterbox splits correctly
    text = re.sub(r"\s+([,.!?])", r"\1", text)
    return text.strip()


def extract_text_from_html(html_path: str) -> str:
    """HTML-only fallback extractor (used when no .md source exists)."""
    with open(html_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    content = re.sub(r"<script[^>]*>.*?</script>", " ", content, flags=re.DOTALL)
    content = re.sub(r"<style[^>]*>.*?</style>", " ", content, flags=re.DOTALL)
    content = re.sub(r"<!--.*?-->", " ", content, flags=re.DOTALL)
    # Drop nav / header / footer
    content = re.sub(r"<nav[^>]*>.*?</nav>", " ", content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"<header[^>]*>.*?</header>", " ", content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"<footer[^>]*>.*?</footer>", " ", content, flags=re.DOTALL | re.IGNORECASE)
    # Isolate <article> if present
    m = re.search(r"<article[^>]*>(.*?)</article>", content, flags=re.DOTALL | re.IGNORECASE)
    if m:
        content = m.group(1)
    content = re.sub(r"<[^>]+>", " ", content)
    # Decode common entities
    for k, v in [("&#8217;", "'"), ("&#8220;", '"'), ("&#8221;", '"'),
                 ("&#8230;", "..."), ("&#8211;", "-"), ("&amp;", "&"),
                 ("&nbsp;", " "), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')]:
        content = content.replace(k, v)
    content = re.sub(r"\s+", " ", content).strip()
    # Best-effort: skip breadcrumb noise before first 'min read'
    m2 = re.search(r"\d+\s*min\s*read\s*(.+)", content, flags=re.IGNORECASE)
    if m2:
        content = m2.group(1).strip()
    return content


# ---------------------------------------------------------------------------
# Chunking — respects sentence boundaries
# ---------------------------------------------------------------------------

def split_into_chunks(text: str, limit: int = CHUNK_LIMIT) -> list:
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]
    chunks = []
    current = ""
    for para in paragraphs:
        if len(para) > limit:
            sentences = re.split(r"(?<=[.!?])\s+", para)
            for s in sentences:
                if len(current) + len(s) + 2 > limit:
                    if current:
                        chunks.append(current.strip())
                    current = s
                else:
                    current = (current + " " + s).strip() if current else s
        else:
            if len(current) + len(para) + 2 > limit:
                if current:
                    chunks.append(current.strip())
                current = para
            else:
                current = (current + " " + para).strip() if current else para
    if current:
        chunks.append(current.strip())
    return chunks


# ---------------------------------------------------------------------------
# Chatterbox call with retries
# ---------------------------------------------------------------------------

def tts_chunk_to_wav(text: str, voice: str = CANONICAL_VOICE) -> bytes:
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(
                f"{CHATTERBOX_URL}/tts",
                json={"text": text, "voice": voice},
                timeout=REQUEST_TIMEOUT,
            )
            if r.status_code == 200 and len(r.content) > 1000:
                return r.content
            last_err = f"status {r.status_code}, body {r.text[:200]}"
        except Exception as e:
            last_err = repr(e)
        print(f"    [retry {attempt}/{MAX_RETRIES}] {last_err}", file=sys.stderr)
        time.sleep(2 * attempt)
    raise RuntimeError(f"Chatterbox TTS failed after {MAX_RETRIES} attempts: {last_err}")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def generate_blog_audio_chatterbox(
    source_path: str,
    output_path: str,
    source_type: str = "auto",
    voice: str = CANONICAL_VOICE,
) -> str:
    src = Path(source_path)
    out = Path(output_path)

    if source_type == "auto":
        source_type = "html" if src.suffix.lower() in (".html", ".htm") else "md"

    print(f"[chatterbox-tts] source={src} ({source_type}) -> {out} voice={voice}")

    if source_type == "html":
        raw_text = extract_text_from_html(str(src))
    else:
        raw_text = extract_readable_text(str(src))

    text = clean_for_speech(raw_text)
    print(f"[chatterbox-tts] {len(text)} chars after cleanForSpeech")

    if len(text) < 100:
        raise RuntimeError(f"Extracted text too short ({len(text)} chars) — aborting")

    chunks = split_into_chunks(text)
    print(f"[chatterbox-tts] split into {len(chunks)} chunk(s)")

    # Generate all WAV chunks BEFORE writing output (prevents 0-byte-on-fail)
    wav_paths = []
    with tempfile.TemporaryDirectory(prefix="chatterbox_") as tmpdir:
        tmpdir_path = Path(tmpdir)
        for i, chunk in enumerate(chunks, 1):
            print(f"  [{i}/{len(chunks)}] {len(chunk)} chars -> Chatterbox...")
            wav_bytes = tts_chunk_to_wav(chunk, voice=voice)
            wav_file = tmpdir_path / f"chunk_{i:03d}.wav"
            wav_file.write_bytes(wav_bytes)
            wav_paths.append(wav_file)
            print(f"        {len(wav_bytes):,} bytes")

        # Concat with ffmpeg -> mp3
        concat_list = tmpdir_path / "concat.txt"
        concat_list.write_text("".join(f"file '{p}'\n" for p in wav_paths))

        out.parent.mkdir(parents=True, exist_ok=True)
        tmp_mp3 = out.with_suffix(out.suffix + ".tmp")

        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c:a", "libmp3lame", "-b:a", MP3_BITRATE, "-ac", "1",
            "-f", "mp3", str(tmp_mp3),
        ]
        print(f"[chatterbox-tts] ffmpeg concat -> {tmp_mp3.name}")
        subprocess.run(cmd, check=True)

        # Verify size before rename (atomic-ish: only overwrite if success)
        size = tmp_mp3.stat().st_size
        if size < 10_000:
            tmp_mp3.unlink(missing_ok=True)
            raise RuntimeError(f"Output mp3 suspiciously small ({size} bytes) — not writing")

        tmp_mp3.replace(out)
        print(f"[chatterbox-tts] SUCCESS: {out} ({size:,} bytes)")

    return str(out.resolve())


def main():
    ap = argparse.ArgumentParser(description="PureBrain canonical blog TTS via Chatterbox GPU.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--input", help="Path to blog markdown (.md) source")
    g.add_argument("--html", help="Path to blog index.html (fallback when no .md)")
    ap.add_argument("--output", required=True, help="Destination .mp3 path")
    ap.add_argument("--voice", default=CANONICAL_VOICE, help=f"Chatterbox voice (default: {CANONICAL_VOICE})")
    args = ap.parse_args()

    src = args.input or args.html
    stype = "md" if args.input else "html"

    try:
        path = generate_blog_audio_chatterbox(src, args.output, stype, args.voice)
        print(f"DONE: {path}")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
