# Chatterbox TTS: No GPU on Server -- Performance Crisis

**Date**: 2026-04-04
**Type**: operational
**Agent**: dept-systems-technology

## Key Finding

The Chatterbox TTS server (37.27.237.109) has NO NVIDIA GPU. It runs on CPU only (AMD Ryzen 9 7950X3D). This makes it 8-50x slower than ElevenLabs for voice generation.

## Benchmarks (CPU, FP32, 797.7M params)
- Short text: 3.5s wall / 2.0s audio = 1.75x real-time
- Medium text: 51s wall / 14.5s audio = 3.5x real-time  
- Long text: 29s wall / 29.2s audio = 1:1 real-time

## What We Tried
- BF16: Model internals reject BFloat16 dtype even though CPU supports AVX-512 BF16
- Chatterbox Turbo: WORSE on CPU (53x real-time) -- optimized for GPU execution
- torch.compile: 1000 diffusion steps at 4.67s/step = too slow to even benchmark

## Fix Path
- Hetzner GEX44 (RTX 4000 Ada, 20GB VRAM): ~212 EUR/month
- Chatterbox Turbo on GPU: ~2-3s for 30s audio (from benchmarks)
- Alternative: revert to ElevenLabs for investor-facing pages as interim

## Architecture Notes
- API: /opt/chatterbox-tts-api.py on port 8950
- Service: systemd chatterbox-tts.service
- Package: chatterbox-tts 0.1.7 (includes Turbo model)
- Turbo import: `from chatterbox.tts_turbo import ChatterboxTurboTTS`
- Model components: t3 (532M), s3gen (264M), ve (1.4M) = 797.7M total
- Usage: ~27 requests/day (190 in last 7 days)
