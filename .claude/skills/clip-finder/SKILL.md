---
name: clip-finder
description: Find the best 30-90 second shareable moments in any meeting or video recording, then cut them into clips with ffmpeg. Works with ANY recording platform (Zoom, Google Meet, Teams, Riverside, Loom, OBS, or a raw local video/audio file) and ANY of several transcription backends including fully free/offline options (whisper.cpp, faster-whisper, local openai-whisper, Vosk) as well as cloud APIs (OpenAI, Deepgram, AssemblyAI, Google, ElevenLabs). Use when you have a long recording and want to pull out the highlight clips automatically.
version: 1.0.0
source: PureBrain community
created: 2026-06-03
allowed-tools: Read, Write, Bash, Grep, Glob
---

# Clip Finder

Turn any long recording into a handful of short, shareable highlight clips.

You point it at a video or audio file (or an export from your meeting platform), it
transcribes the recording with timestamps using a backend of your choice, scans the
transcript for the strongest moments, and cuts clean 30-90 second clips with ffmpeg.

It does NOT depend on any single platform or any single transcription service. Pick
whatever you already use. There is at least one fully free, offline path so cost is
never a blocker.

---

## What it does (end to end)

1. **Get a recording** from whatever platform you use (or a local file).
2. **Transcribe** it to timestamped segments using the backend of your choice.
3. **Find moments** by scanning the transcript (optionally aided by audio energy) for
   the most shareable 30-90 second windows.
4. **Output clip timestamps** with a suggested title, key quote, and a score.
5. **Cut the clips** with ffmpeg.

The core value (moment detection plus clip extraction) is platform neutral. Only the
first step (getting the recording) and the second step (transcription) are pluggable.

---

## Prerequisites

- **Python 3.9+**
- **ffmpeg** on your PATH. Verify with `ffmpeg -version`.
  - macOS: `brew install ffmpeg`
  - Debian/Ubuntu: `sudo apt-get install ffmpeg`
  - Windows: `winget install Gyan.FFmpeg` or download a static build
- **One transcription backend** installed (see the table below). Start with
  `faster-whisper` for a free, offline, accurate default.
- Python deps: `pip install -r requirements.txt`

---

## Quickstart

```bash
# 1. Install Python deps (and pick a transcription backend, e.g. faster-whisper)
pip install -r requirements.txt
pip install faster-whisper          # free, offline default

# 2. Find the best moments in a recording and cut the clips
python3 clip_finder.py --input meeting.mp4 --backend faster-whisper --cut

# Output: a transcript JSON, a ranked list of clip candidates, and cut .mp4 clips
# written next to the input file.
```

Common variations:

```bash
# Just analyze, do not cut yet (review candidates first)
python3 clip_finder.py --input meeting.mp4 --backend faster-whisper

# Use a transcript you already have (skip transcription entirely)
python3 clip_finder.py --input meeting.mp4 --transcript existing.srt --cut

# Use a cloud backend (needs an API key in the matching env var)
python3 clip_finder.py --input meeting.mp4 --backend deepgram --cut

# Audio-only file works too
python3 clip_finder.py --input call.m4a --backend vosk
```

---

## Step 1: Get a recording from any platform

The skill only needs a local **video or audio file**. Here is how to get one out of the
common platforms. Once you have the file, every platform is treated the same.

| Platform | How to get a local file |
|----------|-------------------------|
| **Local file** | You already have it. Any `.mp4`, `.mov`, `.mkv`, `.m4a`, `.mp3`, `.wav` works. |
| **Zoom** | Record to the cloud or locally, then download the MP4 from the Zoom web portal (Recordings tab) or your local `Documents/Zoom` folder. If a `.vtt` transcript was generated, you can pass it with `--transcript` to skip transcription. |
| **Google Meet** | Recordings land in the organizer's Google Drive under "Meet Recordings". Download the `.mp4`. Captions, if saved, come as a `.sbv` or `.txt` you can convert, or just re-transcribe. |
| **Microsoft Teams** | Recordings save to OneDrive/SharePoint (organizer's "Recordings" folder). Download the `.mp4`. Teams transcripts export as `.vtt` and can be passed with `--transcript`. |
| **Riverside** | Download the recorded track(s) from the Riverside dashboard as `.mp4` or `.wav`. |
| **Loom** | Use the "Download" option on the video page to get the `.mp4`. |
| **OBS** | OBS writes directly to a local `.mkv` or `.mp4`. Use it as-is. |
| **Anything else** | If you can export or screen-record it to a video/audio file, it works. |

> Tip: if your platform already produced a timestamped transcript (`.srt`, `.vtt`),
> pass it with `--transcript` and skip the transcription step entirely.

---

## Step 2: Choose a transcription backend

The transcript (with timestamps) is what feeds moment detection, so each backend emits
timestamped segments. Pick based on whether you want free/offline or a managed cloud API.

| Backend | Type | Offline | API key | Accuracy | Speed | Setup |
|---------|------|---------|---------|----------|-------|-------|
| **faster-whisper** | Open source | Yes | No | High | Fast (CTranslate2) | `pip install faster-whisper` |
| **whisper.cpp** | Open source | Yes | No | High | Fast on CPU/Metal | Build from source, pass `--whisper-cpp-bin` and a `.bin` model |
| **openai-whisper (local pip)** | Open source | Yes | No | High | Moderate | `pip install openai-whisper` (runs locally, NO API key) |
| **Vosk** | Open source | Yes | No | Moderate | Fast, light | `pip install vosk` + download a model folder |
| **OpenAI Whisper API** | Cloud | No | `OPENAI_API_KEY` | High | Fast | `pip install openai` |
| **Deepgram** | Cloud | No | `DEEPGRAM_API_KEY` | High | Very fast | `pip install deepgram-sdk` |
| **AssemblyAI** | Cloud | No | `ASSEMBLYAI_API_KEY` | High | Fast | `pip install assemblyai` |
| **Google Cloud Speech-to-Text** | Cloud | No | `GOOGLE_APPLICATION_CREDENTIALS` | High | Fast | `pip install google-cloud-speech` |
| **ElevenLabs Scribe** | Cloud | No | `ELEVENLABS_API_KEY` | High | Fast | `pip install elevenlabs` |

**Recommended default:** `faster-whisper` (free, offline, accurate, no key). Use a cloud
backend only if you want zero local setup or the fastest possible turnaround.

`clip_finder.py` auto-selects a backend if you do not pass `--backend`: it prefers any
installed offline backend, then falls back to a cloud backend whose API key is present
in the environment.

---

## Step 3: Moment detection (platform neutral)

The script scans the transcript for high-value moment types, scores each candidate,
and selects the strongest non-overlapping 30-90 second windows. Moment types, in
rough priority order:

1. **Hot takes / bold claims**: strong opinions, contrarian views, predictions.
2. **Numbers and comparisons**: specific figures, dollar amounts, percentages, "X vs Y".
3. **Emotional reactions**: excitement, surprise, laughter, energy spikes.
4. **Teaching moments**: clear step-by-step explanations and analogies.
5. **Social proof**: results, before/after, testimonials.
6. **Vision / inspiration**: future state, mission, "imagine a world where...".

Each candidate is scored on shareability, quote-worthiness, whether a clean 30-90s
window can be cut around it, and how strong the opening hook is (the first few seconds
must grab attention). Optionally, audio energy is used to confirm laughter/energy peaks.

The script outputs the top candidates. For an LLM-driven pass, read the transcript JSON
it produces and apply your own scoring prompt; the file format is documented in the
script header.

---

## Step 4: Output format

For each selected moment the script prints and writes JSON like:

```
CLIP #1  score 9.2/10
time     06:23 - 07:45  (82s)
title    "Your AI is a software team"
quote    "Who wants to bet that what we're working with right now changes everything..."
why      Bold comparison, specific numbers, high energy
```

---

## Step 5: Cut the clips

With `--cut`, the script trims each selected window with ffmpeg using re-encode (never
`-c copy`, which causes keyframe/freeze issues at clip boundaries):

```bash
ffmpeg -i input.mp4 -ss <start> -to <end> -c:v libx264 -c:a aac clip_1.mp4
```

Clips are written next to the input as `clip_1.mp4`, `clip_2.mp4`, etc. Branding,
captions, and intro/outro stitching are intentionally left out so this stays a clean,
generic core you can extend however you like.

---

## Example

```bash
# Free offline run on a Google Meet recording downloaded from Drive
pip install -r requirements.txt
pip install faster-whisper
python3 clip_finder.py --input team-standup.mp4 --backend faster-whisper --cut --max-clips 5
```

Result: `team-standup.transcript.json`, a ranked candidate list in the console, and up
to five cut clips `clip_1.mp4` ... `clip_5.mp4` in the same folder.

---

## Files in this skill

- `SKILL.md`: this guide
- `clip_finder.py`: the end-to-end helper (transcribe, detect moments, cut)
- `requirements.txt`: Python dependencies (install only the backend you want)

## Notes

- ffmpeg is a hard prerequisite for cutting clips.
- For long recordings, prefer a `base` or `small` model for speed; bump to `medium`
  for accuracy if you have the time/compute.
- If you already have a transcript, `--transcript file.srt|file.vtt|file.json` skips
  transcription entirely and is by far the fastest path.


---

**Helper script:** clip_finder.py (end-to-end: transcribe, detect moments, cut). **Deps:** requirements.txt + ffmpeg.
**Platforms supported:** Zoom, Google Meet, Microsoft Teams, Riverside, Loom, OBS, or any local video/audio file.
**Transcription backends:** faster-whisper, whisper.cpp, local openai-whisper, Vosk (all free/offline, no API key); OpenAI Whisper API, Deepgram, AssemblyAI, Google Cloud Speech-to-Text, ElevenLabs Scribe (cloud).
