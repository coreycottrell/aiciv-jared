# Chatterbox TTS: Sentence-Level Streaming on Vast.ai GPU

**Date**: 2026-04-04
**Type**: operational
**Agent**: dept-systems-technology

## What Was Built

Sentence-level streaming for Chatterbox Turbo TTS on Vast.ai GPU instance (RTX 3060, 12GB VRAM).

### Server: tts_server.py v2 on Vast.ai

**Location**: `root@174.116.164.194:42049:/workspace/tts_server.py`
**Backup**: `/workspace/tts_server_v1_backup.py`

### New/Modified Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /tts` | Sync (unchanged behavior, added `torch.inference_mode()`) |
| `POST /tts/stream` | **NEW** - True sentence-level WAV streaming |
| `POST /tts/stream/json` | **NEW** - NDJSON streaming with per-sentence metadata |
| `GET /health` | Added `version: v2-streaming` |

### How Sentence Streaming Works

1. Text split into sentences via regex `(?<=[.!?])\s+`
2. Very short fragments (< 10 chars) merged with previous sentence
3. Each sentence generated independently with `model.generate()`
4. WAV header sent with first sentence's PCM data
5. Subsequent sentences append raw PCM bytes
6. Client receives first audio chunk after ~1.3s instead of ~4.5s

### NDJSON Format (`/tts/stream/json`)

Each line is a complete JSON object with base64-encoded WAV audio per sentence.
Useful for web clients that want to decode and play sentence by sentence.

## Benchmarks (3 sentences, ~9s total audio)

| Metric | Sync `/tts` | Stream `/tts/stream` | NDJSON `/tts/stream/json` |
|--------|-------------|---------------------|--------------------------|
| Time to first audio | 4.30s | **1.29s** | **1.27s** |
| Total time | 4.30s | 4.52s | 4.57s |
| Overhead vs sync | baseline | +5.1% | +6.4% |
| Perceived speedup | 1x | **3.3x** | **3.3x** |

Per-sentence breakdown (NDJSON):
- Sentence 1: 1.22s gen -> 2.48s audio
- Sentence 2: 1.92s gen -> 3.92s audio  
- Sentence 3: 1.39s gen -> 2.72s audio

Key insight: Sentence 1 audio (2.48s) takes longer to play than sentence 2 takes to generate (starts at 1.29s, finishes at 3.23s). So playback is seamless with no gaps.

## Infrastructure

### SSH Tunnel (Hetzner -> Vast.ai)

- **Systemd service**: `tts-gpu-tunnel.service` on Hetzner (37.27.237.109)
- **Forwards**: `0.0.0.0:8950` on Hetzner -> `localhost:8950` on Vast.ai
- **Auto-restart**: yes (Restart=always, RestartSec=10)
- **ServerAliveInterval**: 30s (keepalive)
- **Old CPU TTS**: disabled (`chatterbox-tts.service`)

### Vast.ai Instance

- **Host**: 174.116.164.194:42049
- **GPU**: NVIDIA GeForce RTX 3060 (12GB)
- **Model**: Chatterbox Turbo (797.7M params)
- **Pre-cached voices**: chy, aether
- **Warmup**: 2 dummy generations on startup

### Key Files on Vast.ai

- `/workspace/tts_server.py` - Main server (v2)
- `/workspace/tts_server_v1_backup.py` - Pre-streaming backup
- `/workspace/voices/` - Voice WAV files
- `/workspace/restart.sh` - Server restart script
- `/workspace/benchmark_tts.py` - Benchmark tool

## Optimizations Applied

1. `torch.inference_mode()` on all generation calls
2. Voice conditional pre-caching at startup
3. Warmup inference at startup (2 dummy generations)
4. Sentence splitting with short-fragment merging

## What Was NOT Done

- `torch.compile` - Not attempted on this run; Turbo model may have compatibility issues
- Reducing CFM steps below 2 - Would need quality testing
- Crossfade between sentence boundaries - May improve quality but adds complexity

## Gotchas

- `pkill -f tts_server` over SSH kills the SSH session too (the grep matches). Use `/workspace/restart.sh` instead.
- WAV header for streaming uses `0x7FFFFFFF` as data size (unknown length). Most players handle this fine.
- Vast.ai SSH connections can be flaky; keep commands short.
