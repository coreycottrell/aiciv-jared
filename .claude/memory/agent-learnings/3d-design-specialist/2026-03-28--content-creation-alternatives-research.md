# Content Creation Alternatives Research

**Date**: 2026-03-28
**Type**: teaching
**Agent**: 3d-design-specialist
**Topic**: Open-source alternatives to paid content creation tools (DALL-E, VEO, ElevenLabs)

---

## Key Findings

### Image Generation (March 2026)
- **FLUX.2 Dev** is the best open-source image model -- beats DALL-E on photorealism, text, and hands
- **SDXL** has the largest ecosystem (100K+ models on CivitAI)
- **ComfyUI** is the standard workflow tool for all diffusion models
- GPU requirement: 8GB minimum (SDXL), 16GB recommended (FLUX.2)
- Cost: $0.29-0.44/hr on Vast.ai/RunPod (RTX 4090)

### Voice/TTS (March 2026 -- MAJOR BREAKTHROUGH)
- **Chatterbox** beats ElevenLabs in 63.8% of blind tests (MIT license, commercial OK)
- **Voxtral** beats ElevenLabs Flash v2.5 in 62.8% of blind tests (released March 26, 2026)
- **Piper** runs on CPU only -- good for lightweight TTS on our VPS
- Self-hosted Chatterbox has OpenAI-compatible API -- drop-in replacement for ElevenLabs

### Video Generation
- Still immature -- needs 24GB+ VRAM for decent quality
- **CogVideoX** best open-source (6s clips at 720x480)
- **Remotion** (programmatic video via React) is the better approach for most content
- Remotion has Claude Code Agent Skills as of Jan 2026

### Programmatic (Already Available)
- Pillow already generates our blog banners at $0 cost
- FFmpeg already on VPS for video processing
- Three.js capture for 3D content (already in our stack)

## Infrastructure Notes
- Our VPS: 2-core Xeon, 4GB RAM, NO GPU -- cannot run AI models locally
- On-demand GPU rental is the right approach ($0.29-1.99/hr)
- Dedicated GPU server only justified at 100+ images/day sustained

## Cost Summary
- Current: $50-82/month on APIs
- Recommended stack: $11-22/month (on-demand GPU + programmatic)
- Savings: $336-852/year

## Files Created
- Training doc: `/home/jared/exports/portal-files/content-creation-alternatives-march30.md`
- Demo banner: `/home/jared/exports/portal-files/demo-content-creation-banner.png`
- Demo script: `/home/jared/projects/AI-CIV/aether/tools/demo_content_creation.py`
