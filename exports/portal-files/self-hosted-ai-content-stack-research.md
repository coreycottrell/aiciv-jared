# Self-Hosted AI Content Generation Stack: Complete Research Report

**Date**: 2026-03-30
**Purpose**: Replace all commercial AI content services with self-hosted/open-source alternatives
**Goal**: Pure Technology owns its entire creative stack -- zero dependency on Google, OpenAI, or ElevenLabs

---

## Executive Summary

The open-source AI content generation landscape has matured dramatically in 2025-2026. Every commercial service Pure Technology currently uses has a viable open-source replacement. The strongest opportunities are:

1. **Images**: FLUX models (production-grade, runs on RTX 4090 in <10 seconds)
2. **Voice/TTS**: Chatterbox TTS (beats ElevenLabs in 63.8% of blind tests, MIT license)
3. **Video**: LTX-Video (runs on 8GB VRAM, fastest open-source option)
4. **Music**: ACE-Step 1.5 (runs on 4GB VRAM, MIT license, rivals Suno)
5. **3D**: Hunyuan3D 2.1 (6GB VRAM minimum, exports GLB for Three.js)

**Recommended approach**: GPU rental (RunPod/Vast.ai at $0.29-0.39/hr for RTX 4090) for heavy generation, Cloudflare Workers AI for lightweight/on-demand image generation, and CPU-based TTS via Chatterbox for voice.

---

## 1. IMAGE GENERATION (Replace DALL-E / Midjourney)

### Tier 1: Best Quality

| Tool | License | VRAM | Quality (vs DALL-E 3) | Speed (4090) | Setup | Best For |
|------|---------|------|----------------------|--------------|-------|----------|
| **FLUX.1 Schnell** | Apache 2.0 | 8-12GB (FP8) | 8/10 | ~5-10 sec | Easy (ComfyUI) | Fast blog banners, social graphics |
| **FLUX.1 Dev** | Non-commercial | 12-16GB | 9/10 | ~15-20 sec | Easy (ComfyUI) | High-quality product mockups |
| **FLUX.2 Pro** | Commercial license | 16-24GB | 9.5/10 | ~10 sec | Medium | Production marketing assets |
| **FLUX.2 Klein 4B** | Open | ~13GB | 8.5/10 | ~5 sec | Easy | Real-time generation + editing |
| **SD 3.5 Large** | Stability Community | 16-24GB | 8/10 | ~15 sec | Medium | Complex multi-element prompts |
| **SDXL** | Open | 8-12GB | 7/10 | ~5-8 sec | Easy | Workhorse, huge ecosystem of LoRAs |

### Tier 2: Lightweight / Special Purpose

| Tool | License | VRAM | Quality | Speed | Best For |
|------|---------|------|---------|-------|----------|
| **SDXL Turbo** | Open | 6-8GB | 6.5/10 | ~1-2 sec | Quick drafts, iteration |
| **SDXL Lightning** | Open | 6-8GB | 7/10 | ~2-4 sec | Fast previews |

### Hardware Requirements

- **RTX 4090 (24GB)**: Runs ALL models at full quality. FLUX.1 Schnell in <10 seconds. Recommended.
- **RTX 4070/3060 12GB**: Runs FLUX Schnell FP8, SDXL, SDXL Turbo. Good enough for blog banners.
- **CPU Only**: YES, possible via FastSD CPU (OpenVINO). ~45 seconds per image with quantized models. Usable for batch overnight generation.
- **Hetzner (no GPU)**: CPU-only mode works but slow. Better to use Cloudflare Workers AI or GPU rental.

### ComfyUI: The Interface

ComfyUI is the standard self-hosted interface. Node-based workflows. Supports all models. Install once, swap models freely.

- URL: https://github.com/comfyanonymous/ComfyUI
- Setup: `git clone` + `pip install` + download model weights
- Complexity: Easy to get running, medium to master workflows

### PureBrain Recommendation

**Primary**: FLUX.1 Schnell via ComfyUI on rented RTX 4090 ($0.39/hr RunPod). Generate 100+ images per dollar.
**Backup**: Cloudflare Workers AI FLUX Schnell -- 10,000 free neurons/day = ~2,000 images/day at 512x512.
**Overnight batch**: CPU-only FastSD on Hetzner for non-urgent banners.

---

## 2. VIDEO GENERATION (Replace Google VEO)

### Top Open-Source Video Models

| Tool | License | VRAM Min | Quality (vs VEO/Sora) | Speed | Setup | Best For |
|------|---------|----------|----------------------|-------|-------|----------|
| **LTX-Video 2.3** | Open | 8GB | 7/10 | 11 sec/121 frames (4090) | Easy (desktop app) | Short marketing clips |
| **LTX-2 19B** | Open | 16GB+ | 8/10 | Fast | Medium | Video + audio in single pass |
| **HunyuanVideo 1.5** | Tencent Open | 14GB (offload) | 8.5/10 | Minutes | Medium | High-quality product demos |
| **CogVideoX-5B** | Apache 2.0 | 12-16GB | 7/10 | Minutes | Medium | Text-to-video basics |
| **Open-Sora 2.0** | Apache 2.0 | 40GB+ (full) | 8/10 | Slow | Hard | Research-grade quality |
| **Mochi 1** | Apache 2.0 | 24-40GB | 8/10 | Slow | Hard | Highest fidelity open-source |
| **Wan 2.1** | Open | 24GB+ | 8/10 | Moderate | Medium | Emerging strong contender |

### Hardware Reality Check

- **RTX 4090 (24GB)**: LTX-Video runs great. HunyuanVideo 1.5 usable with offloading. CogVideoX works.
- **12GB GPU**: LTX-Video at lower res. CogVideoX-2B variant.
- **Hetzner (no GPU)**: NOT viable for video generation. Must use GPU rental.
- **CPU Only**: NOT practical for video generation.

### LTX-Video: Best for PureBrain

LTX-Video stands out because:
- **Desktop app available** (LTX Desktop -- open source)
- **Lowest VRAM requirement** (8GB viable)
- **Fastest generation** (121 frames in 11 seconds on 4090)
- **LTX-2 adds audio generation** in the same pass
- **Q8 optimization** specifically designed for consumer GPUs
- URL: https://github.com/Lightricks/LTX-Video

### PureBrain Recommendation

**Primary**: LTX-Video on RunPod RTX 4090 ($0.39/hr). Generate a 5-second clip for ~$0.01.
**High quality**: HunyuanVideo 1.5 on RunPod A100 ($2.49/hr) for hero marketing videos.
**Workflow**: ComfyUI supports most video models via community nodes.

---

## 3. VOICE / TTS (Replace ElevenLabs)

### Top Open-Source TTS Models

| Tool | License | GPU Needed? | Quality (vs ElevenLabs) | Voice Clone | Languages | Setup |
|------|---------|-------------|------------------------|-------------|-----------|-------|
| **Chatterbox Turbo** | MIT | Optional (CPU works) | 9.5/10 (wins 63.8% blind tests) | Yes (5 sec sample) | 23 | Easy |
| **XTTS v2** | Open (Coqui) | Recommended | 8/10 | Yes (6 sec sample) | 17 | Medium |
| **OpenVoice V2** | MIT | Optional | 7/10 | Yes (zero-shot) | 6 native | Easy |
| **Bark** | MIT | Recommended | 7.5/10 | Limited | Multi | Medium |
| **Piper** | MIT | No (CPU only) | 6/10 | No (pre-trained voices) | 30+ | Easy |

### Chatterbox: The Clear Winner

- **350M parameters** -- lightweight enough for CPU inference
- **Sub-200ms streaming latency** on consumer GPU
- **Production-grade quality**: 95/100 vs ElevenLabs Turbo's 90/100
- **Paralinguistic tags**: [cough], [laugh], [sigh] for natural speech
- **Built-in watermarking** (PerTh) for responsible AI
- **23 languages** including English, Spanish, Mandarin, Hindi, Arabic
- **MIT License** -- fully commercial, modify freely
- URL: https://github.com/resemble-ai/chatterbox

### Hardware Requirements

- **RTX 4090**: Overkill for TTS. Sub-200ms per sentence.
- **Any GPU (4-8GB)**: Works great for Chatterbox and XTTS.
- **CPU Only**: YES! Chatterbox runs on CPU. Slower but totally usable for batch processing.
- **Hetzner (no GPU)**: Viable for Chatterbox on CPU. Perfect for blog audio generation.

### Voice Cloning Comparison

| Feature | Chatterbox | XTTS v2 | OpenVoice V2 |
|---------|------------|---------|-------------|
| Reference audio needed | 5 seconds | 6 seconds | Short clip |
| Cross-lingual cloning | Yes (23 lang) | Yes (17 lang) | Yes (6 lang) |
| Emotion control | Yes (tags) | Via reference | Limited |
| Streaming | Yes (<200ms) | Yes (<150ms) | No |
| Active development | Yes (Resemble AI) | Community only* | MyShell |

*Note: Coqui AI shut down December 2025, but open-source models remain community-maintained.

### PureBrain Recommendation

**Primary**: Chatterbox Turbo self-hosted on Hetzner (CPU mode). FREE, unlimited, better than ElevenLabs.
**Voice cloning**: Clone Aether's voice once, use forever. No per-character fees.
**Blog audio**: Batch generate all blog post audio overnight on Hetzner CPU.
**Immediate win**: This replaces the ElevenLabs dependency TODAY with zero cost.

---

## 4. MUSIC / AUDIO (Replace Suno/Udio)

### Open-Source Music Generation

| Tool | License | VRAM Min | Quality (vs Suno) | Speed | Setup |
|------|---------|----------|-------------------|-------|-------|
| **ACE-Step 1.5** | MIT | 4GB | 8/10 | <10 sec (RTX 3090) | Easy (Gradio UI) |
| **HeartMuLa** | Open | High (4B params) | 7.5/10 | Slow | Hard |
| **Riffusion** | Open | 8GB | 6/10 | Fast | Medium |

### ACE-Step 1.5: The Clear Winner

- **Runs on 4GB VRAM** -- even old GPUs work
- **MIT License** -- fully commercial
- **Full song in <10 seconds** on RTX 3090, <2 seconds on A100
- **LoRA fine-tuning** from just a few songs to capture custom style
- **Voice cloning, lyric editing, remixing, track generation**
- **Gradio UI + REST API** out of the box
- URL: https://github.com/ace-step/ACE-Step-1.5

### Sound Effects

- **AudioCraft (Meta)**: Open-source sound effect generation. Runs on consumer GPUs.
- **Bark**: Can generate non-speech audio (environmental sounds, music snippets).

### PureBrain Recommendation

**Primary**: ACE-Step 1.5 on RunPod RTX 4090 for on-demand music generation.
**Use case**: Background music for marketing videos, podcast intros, social content.
**Cost**: Essentially free -- one GPU hour ($0.39) generates hundreds of tracks.

---

## 5. 3D GENERATION (Replace Meshy)

### Open-Source 3D Models

| Tool | License | VRAM Min | Quality (vs Meshy) | Speed | Export Format | Setup |
|------|---------|----------|-------------------|-------|---------------|-------|
| **Hunyuan3D 2.1** | Tencent Open | 6GB | 8.5/10 | Seconds-minutes | GLB, USDZ (PBR) | Medium |
| **TripoSR** | MIT | Moderate | 7/10 | <0.5 sec (A100) | Mesh | Medium |
| **Stable DreamFusion** | Open | 12-24GB | 6/10 | Minutes-hours | Mesh | Hard |
| **Shap-E (OpenAI)** | MIT | 8GB | 5/10 | Fast | Mesh | Easy |
| **Trellis** | Open | 12GB+ | 7.5/10 | Minutes | GLB | Medium |

### Hunyuan3D 2.1: Best for PureBrain

- **6GB VRAM minimum** -- runs on consumer hardware
- **PBR materials** -- physically-based rendering for realistic output
- **GLB export** -- native Three.js compatibility
- **Text-to-3D AND Image-to-3D**
- **Tencent-backed** -- active development
- URL: https://github.com/Tencent-Hunyuan/HunyuanVideo (3D variant)

### Three.js Integration

Hunyuan3D exports GLB files which load directly into Three.js:
```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
const loader = new GLTFLoader();
loader.load('model.glb', (gltf) => scene.add(gltf.scene));
```

### PureBrain Recommendation

**Primary**: Hunyuan3D 2.1 for orbs/glass/hex assets (matching Meshy constraint).
**Workflow**: Generate on RunPod -> export GLB -> deploy to CF Pages with Three.js.
**Cost**: ~$0.05-0.10 per 3D asset on rented GPU.

---

## 6. INFRASTRUCTURE OPTIONS

### GPU Rental (On-Demand)

| Provider | RTX 4090/hr | A100/hr | Best For |
|----------|-------------|---------|----------|
| **Vast.ai** | $0.29 | ~$1.50 | Cheapest raw GPU price |
| **RunPod** | $0.39 | $2.49 | Most reliable, pay-per-second |
| **Lambda** | ~$0.50 | ~$2.00 | Enterprise stability |

**Cost estimates for PureBrain content pipeline:**
- 100 blog banner images: ~$0.15 (1 GPU-hour / ~600 images)
- 10 short video clips: ~$0.50 (RTX 4090, LTX-Video)
- 30 blog audio files: $0.00 (CPU on Hetzner via Chatterbox)
- 5 music tracks: ~$0.10
- 3 3D assets: ~$0.15
- **Total daily content budget: ~$0.90**

### Cloudflare Workers AI

- **Free tier**: 10,000 neurons/day
- **FLUX Schnell**: 4.80 neurons per 512x512 image = ~2,083 free images/day
- **Paid**: $0.011 per 1,000 neurons (~$0.00005 per image)
- **Models available**: FLUX Schnell, FLUX 2 Klein, SDXL Lightning, Leonardo, SD Inpainting
- **No GPU management needed** -- runs on CF edge
- **Best for**: On-demand image generation triggered by API calls (e.g., dynamic social graphics)

### Hugging Face Inference API

- **Free tier**: ~$0.10/month in credits (very limited)
- **PRO**: $9/month for 2M inference credits
- **Best for**: Testing/prototyping, not production
- **Supports**: FLUX, SD, TTS models via API

### CPU-Only on Hetzner (No GPU)

| Task | Possible? | Speed | Tool |
|------|-----------|-------|------|
| Image generation | Yes | ~45-60 sec/image | FastSD CPU (OpenVINO) |
| TTS/Voice | Yes | 1-5 sec/sentence | Chatterbox, Piper |
| Music | Marginal | Minutes per track | ACE-Step (slow) |
| Video | No | Not practical | -- |
| 3D | No | Not practical | -- |

### Recommended Architecture

```
HETZNER SERVER (CPU - always on, free)
  |-- Chatterbox TTS (blog audio, voice clone)
  |-- FastSD CPU (overnight batch image generation)
  |-- Piper TTS (lightweight notifications)

CLOUDFLARE WORKERS AI (edge, pay-per-use)
  |-- FLUX Schnell (on-demand images via API)
  |-- SDXL Lightning (fast previews)
  |-- SD Inpainting (image editing)

RUNPOD/VAST.AI (GPU rental, on-demand)
  |-- ComfyUI + FLUX Dev/Pro (high-quality images)
  |-- LTX-Video (marketing videos)
  |-- HunyuanVideo 1.5 (hero videos)
  |-- ACE-Step 1.5 (music generation)
  |-- Hunyuan3D 2.1 (3D assets)
```

---

## 7. MIGRATION PRIORITY (What to Replace First)

### Phase 1: IMMEDIATE (This Week)
1. **Chatterbox TTS replaces ElevenLabs** -- MIT license, runs on Hetzner CPU, better quality
   - Estimated savings: $22-330/month (depending on ElevenLabs plan)
   - Setup time: 2-3 hours

### Phase 2: QUICK WIN (This Month)
2. **Cloudflare Workers AI for images** -- Already on CF, 2,000+ free images/day
   - Estimated savings: Per-image DALL-E costs
   - Setup time: 1-2 hours (Workers script)
3. **ComfyUI + FLUX on RunPod** for high-quality images when needed
   - Setup time: 3-4 hours (one-time template setup)

### Phase 3: BUILD OUT (Next Month)
4. **LTX-Video for marketing clips** -- RunPod template
5. **ACE-Step 1.5 for music** -- RunPod template
6. **Hunyuan3D 2.1 for 3D assets** -- RunPod template

### Phase 4: OPTIMIZE (Ongoing)
7. Overnight batch generation pipeline on Hetzner CPU
8. Custom LoRA fine-tuning for PureBrain brand consistency
9. Voice clone of Aether's ElevenLabs voice into Chatterbox
10. Automated content pipeline: text -> image + audio + video

---

## 8. COST COMPARISON: Current vs Self-Hosted

| Service | Current Monthly Cost | Self-Hosted Cost | Savings |
|---------|---------------------|------------------|---------|
| ElevenLabs TTS | $22-99/mo | $0 (Hetzner CPU) | 100% |
| DALL-E / image gen | $0.04-0.08/image | $0.00005/image (CF) | 99.9% |
| Google VEO (video) | Usage-based | ~$0.05/clip (RunPod) | 90%+ |
| Music services | $10-50/mo | ~$2/mo (RunPod bursts) | 90%+ |
| Meshy (3D) | $20-60/mo | ~$2/mo (RunPod bursts) | 90%+ |
| **Total estimated** | **$100-350/mo** | **$5-15/mo** | **95%+** |

---

## 9. RISKS AND LIMITATIONS

| Risk | Mitigation |
|------|-----------|
| Quality gap on video (vs Sora/VEO) | LTX-Video + HunyuanVideo closing fast; use commercial for hero content only |
| GPU rental availability | Pre-build RunPod templates; have Vast.ai as backup |
| Model weights storage (~30-100GB per model) | Store on Hetzner; RunPod has network volumes |
| Setup complexity | One-time investment; create reproducible scripts/templates |
| Open-source model obsolescence | Active community; models update frequently |
| No SLA on GPU rentals | Keep CF Workers AI as always-available fallback for images |

---

## 10. KEY URLs AND REPOSITORIES

### Image
- ComfyUI: https://github.com/comfyanonymous/ComfyUI
- FLUX models: https://huggingface.co/black-forest-labs
- FastSD CPU: https://github.com/rupeshs/fastsdcpu

### Video
- LTX-Video: https://github.com/Lightricks/LTX-Video
- LTX Desktop: https://github.com/Lightricks/LTX-Desktop
- HunyuanVideo: https://github.com/Tencent-Hunyuan/HunyuanVideo
- CogVideoX: https://github.com/zai-org/CogVideo
- Open-Sora: https://github.com/hpcaitech/Open-Sora

### Voice/TTS
- Chatterbox: https://github.com/resemble-ai/chatterbox
- Coqui XTTS: https://github.com/coqui-ai/TTS
- OpenVoice: https://github.com/myshell-ai/OpenVoice
- Piper: https://github.com/rhasspy/piper

### Music
- ACE-Step 1.5: https://github.com/ace-step/ACE-Step-1.5
- ACE-Step UI: https://github.com/fspecii/ace-step-ui

### 3D
- Hunyuan3D: https://github.com/Tencent-Hunyuan/HunyuanVideo
- TripoSR: https://github.com/VAST-AI-Research/TripoSR
- Shap-E: https://github.com/openai/shap-e

### Infrastructure
- RunPod: https://www.runpod.io/
- Vast.ai: https://vast.ai/
- CF Workers AI: https://developers.cloudflare.com/workers-ai/
- Hugging Face: https://huggingface.co/

---

*Research conducted 2026-03-30. Open-source AI moves fast -- verify current model versions before implementation.*
