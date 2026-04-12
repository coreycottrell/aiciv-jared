# Content Creation Self-Sufficiency: Breaking Free from Paid AI Tools

**Date**: 2026-03-28
**Purpose**: Comprehensive guide to replacing DALL-E, Google VEO, ElevenLabs, and other paid content generation tools with open-source and programmatic alternatives
**Author**: 3d-design-specialist (Aether collective)

---

## Executive Summary

Pure Technology currently pays for DALL-E (image generation), ElevenLabs (voice), and Google VEO (video). The open-source landscape has matured dramatically -- as of March 2026, open-source alternatives now MATCH or BEAT commercial tools in blind tests. This document maps every viable alternative, what hardware they need, and the recommended stack for PT to own its entire content pipeline.

**Bottom line**: We can eliminate all per-generation API costs. The only ongoing cost is GPU server rental at $0.29-$1.99/hr when we need it (for heavy generation), plus our existing VPS for lighter workloads.

---

## Table of Contents

1. [Image Generation Alternatives](#1-image-generation-alternatives)
2. [Video Generation Alternatives](#2-video-generation-alternatives)
3. [Programmatic Content Creation](#3-programmatic-content-creation-no-ai-model-needed)
4. [Audio/Voice Alternatives](#4-audiovoice-alternatives)
5. [Cost Comparison & Break-Even Analysis](#5-cost-comparison--break-even-analysis)
6. [Recommended Stack for Pure Technology](#6-recommended-stack-for-pure-technology)
7. [Infrastructure Assessment](#7-infrastructure-assessment)
8. [Implementation Roadmap](#8-implementation-roadmap)

---

## 1. Image Generation Alternatives

### The Big Picture

DALL-E charges $0.02-$0.08 per image. The open-source world now offers models that produce EQUAL or BETTER quality at zero marginal cost per image.

### Tier 1: Production-Ready (Best Quality)

#### FLUX.2 (Black Forest Labs)
- **Quality**: Best-in-class for photorealism, text rendering, and hands
- **Versions**: FLUX.2 Dev (open, best quality), FLUX.2 Schnell (fast), FLUX.2 Klein (lightweight)
- **Resolution**: Up to 4MP (2K) images
- **VRAM**: 16GB recommended (Dev), 8GB (Klein)
- **License**: Apache 2.0 (Dev variant -- open for commercial use)
- **Best for**: Product shots, marketing imagery, realistic scenes
- **Where to get it**: huggingface.co/black-forest-labs

#### Stable Diffusion 3.5 (Stability AI)
- **Quality**: Strong photorealism, excellent text rendering
- **Versions**: SD 3.5 Large (8B params), Medium (2B), Turbo (fast)
- **VRAM**: 16GB (Large), 8GB (Medium/Turbo)
- **License**: Stability Community License (free under $1M revenue)
- **Best for**: Wide variety of styles, huge ecosystem of add-ons
- **Ecosystem**: Largest community -- thousands of LoRAs, ControlNets, custom models on CivitAI

#### HiDream-I1 (HiDream AI)
- **Quality**: 17B parameters -- largest open model, exceptional color grading
- **VRAM**: 24GB+ recommended
- **Best for**: Artistic/cinematic imagery, moody lighting
- **Versions**: Full, Dev, Fast

### Tier 2: Fast & Lightweight

#### SDXL (Stable Diffusion XL)
- **Quality**: Very good, enormous ecosystem
- **VRAM**: 8GB minimum, runs on most GPUs
- **Speed**: SDXL-Lightning generates 1024x1024 in under 1 second (2 steps!)
- **License**: Open
- **Best for**: Bulk generation, LoRA fine-tuning, ComfyUI workflows
- **Why it matters**: The largest ecosystem of any model. 100K+ custom models, styles, and add-ons on CivitAI

#### SDXL Turbo / Lightning
- **Quality**: 80-90% of full SDXL at 10x the speed
- **VRAM**: 8GB
- **Speed**: 2-4 steps instead of 20-50
- **Best for**: Rapid iteration, real-time preview, bulk content

### The Workflow Tool: ComfyUI

ComfyUI is the node-based GUI that ties everything together. Think of it as the "Photoshop" for AI image generation:

- **What it is**: Visual workflow builder for Stable Diffusion / Flux / any diffusion model
- **Why it matters**: Chain together multiple steps -- generate, upscale, inpaint, add text, batch process
- **Install**: `git clone https://github.com/comfyanonymous/ComfyUI.git && pip install -r requirements.txt`
- **Desktop version**: ComfyUI Desktop handles all dependencies automatically (30 min setup)
- **Key flags**: `--lowvram` (8-12GB GPU), `--cpu-text-encoder` (6-8GB GPU)

### Alternative UIs

| UI | Best For | Notes |
|----|----------|-------|
| ComfyUI | Power users, automation, complex workflows | Node-based, most flexible |
| Automatic1111 (A1111) | Beginners, quick generation | Web UI, simpler interface |
| Fooocus | Midjourney-like simplicity | Minimal settings, just type and generate |
| InvokeAI | Professional workflows | Clean UI, good for teams |

### Quick Comparison vs DALL-E

| Feature | DALL-E 3 | FLUX.2 Dev | SDXL |
|---------|----------|------------|------|
| Quality | Excellent | Excellent+ | Very Good |
| Text rendering | Good | Better | Good (with SD3.5) |
| Hands/anatomy | Fair | Excellent | Good |
| Speed | ~5 sec/image | ~15 sec (GPU) | ~3 sec (Turbo) |
| Cost per image | $0.04-0.08 | $0.00 (local) | $0.00 (local) |
| Customization | None | LoRA, fine-tune | Massive ecosystem |
| NSFW filter | Strict | None (you control) | None (you control) |

---

## 2. Video Generation Alternatives

### The Honest Truth About Video AI

Video generation is the least mature category. Quality is improving fast, but local video generation requires SERIOUS GPU power (24GB+ VRAM). For PT's needs, the best approach is a hybrid: programmatic video for most content, AI video for specific hero shots.

### Open-Source Video Models

#### CogVideoX (Tsinghua)
- **Quality**: Best open-source text-to-video model as of March 2026
- **Versions**: CogVideoX-2B (lighter), CogVideoX-5B (better quality)
- **Output**: 6-second clips at 720x480
- **VRAM**: 12GB (2B), 16-24GB (5B)
- **GitHub**: github.com/zai-org/CogVideo
- **Best for**: Short social media clips, product demos

#### Open-Sora (HPC-AI Tech)
- **Quality**: Getting close to OpenAI's Sora quality
- **Versions**: v1.3 (latest)
- **Output**: 2-15 seconds at up to 720p
- **VRAM**: 24GB+
- **Capabilities**: Text-to-video, image-to-video, video-to-video, infinite time generation
- **GitHub**: github.com/hpcaitech/Open-Sora

#### Stable Video Diffusion (SVD) (Stability AI)
- **Quality**: Good for image-to-video (animate a still image)
- **VRAM**: 16GB+
- **Best for**: Animating product shots, creating motion from stills

#### LTX Video
- **Quality**: Lightweight, fast
- **VRAM**: 12GB
- **Best for**: Quick video prototyping

#### AnimateDiff
- **Quality**: Adds motion to Stable Diffusion images
- **VRAM**: 8-12GB
- **Best for**: Animated banners, subtle motion effects
- **Key advantage**: Uses the SDXL ecosystem, so all your image models work

### GPU Requirements by Model

| Model | Min VRAM | Recommended | Output |
|-------|----------|-------------|--------|
| AnimateDiff | 8GB | 12GB | Animated SD images |
| LTX Video | 12GB | 16GB | Short clips |
| CogVideoX-2B | 12GB | 16GB | 6s @ 720x480 |
| SVD | 16GB | 24GB | 4s image-to-video |
| CogVideoX-5B | 16GB | 24GB | 6s @ 720x480 |
| Open-Sora v1.3 | 24GB | 40GB+ | 2-15s @ 720p |

### Verdict on AI Video for PT

**For now**: Use programmatic video (Section 3) for 90% of content. Reserve AI video for special hero content when needed, using RunPod/Vast.ai GPU rental ($0.29-1.99/hr) for generation runs.

---

## 3. Programmatic Content Creation (No AI Model Needed)

This is where PT gets the MOST bang for zero cost. We already have many of these tools. They run on our existing VPS with zero GPU.

### What We Already Have Working

#### PIL/Pillow (Python Image Library)
- **Status**: ALREADY IN USE for blog banners (`tools/generate_blog_banners.py`)
- **What it does**: Compositing, text rendering, gradients, shapes, overlays
- **Current output**: 1200x630 branded blog banners with hex grid, gradients, PureBrain branding
- **Cost**: $0.00 -- pure CPU, runs on any server
- **Expand to**: Social media graphics, comparison charts, infographics, OG images

```python
# We already do this -- our banner generator:
from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (1200, 630), '#080a12')
draw = ImageDraw.Draw(img)
# ... brand colors, hex overlay, text -- zero API cost
```

#### FFmpeg (Video Processing)
- **Status**: Available on our VPS
- **What it does**: Video compilation, format conversion, overlays, transitions
- **Use cases**: Compile image sequences into video, add audio tracks, create slideshows
- **Cost**: $0.00

```bash
# Turn a sequence of images into a video
ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# Add audio to video
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac output_with_audio.mp4

# Create slideshow from images with transitions
ffmpeg -framerate 1/3 -i slide_%d.png -vf "zoompan=z='min(zoom+0.0015,1.5)':d=90" video.mp4
```

#### Three.js Screen Capture
- **Status**: We build Three.js scenes already (3D design specialist domain)
- **What it does**: Render 3D scenes, capture as images or video frames
- **Use cases**: 3D product visualizations, animated backgrounds, glass/orb effects
- **Cost**: $0.00 (browser rendering)

```javascript
// Capture Three.js canvas as image
const dataURL = renderer.domElement.toDataURL('image/png');

// Or use CCapture.js for video recording from Three.js
const capturer = new CCapture({ format: 'webm', framerate: 60 });
```

### New Tools to Add

#### Remotion (Programmatic Video via React)
- **What it is**: Create videos programmatically using React components
- **Why it matters**: As of January 2026, Remotion has Agent Skills -- Claude can generate entire videos from natural language prompts
- **Use cases**: Blog recap videos, social media content, data visualization videos, training videos
- **Cost**: Free (open source), Community plan free for individuals
- **Install**: `npx create-video@latest`

```jsx
// A Remotion video component
export const BlogRecap = ({ posts }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ background: '#080a12', width: 1920, height: 1080 }}>
      <h1 style={{ color: '#2a93c1', fontSize: 72 }}>
        {posts[Math.floor(frame / 90)].title}
      </h1>
    </div>
  );
};
```

#### Motion Canvas
- **What it is**: Lightweight canvas-based animations via TypeScript
- **Best for**: Math visualizations, diagrams, educational content
- **Cost**: Free (MIT license)
- **Difference from Remotion**: Canvas-only (not full DOM), lighter weight

#### SVG Animation (CSS + SMIL)
- **What it is**: Animated vector graphics, zero dependencies
- **Use cases**: Animated logos, loading animations, icon animations, animated infographics
- **Cost**: $0.00
- **Advantage**: Infinitely scalable, tiny file size, embeds in web pages natively

#### Canvas API (HTML5)
- **What it is**: Browser-native 2D drawing API
- **Use cases**: Dynamic charts, real-time graphics, data visualizations
- **Cost**: $0.00
- **Can export**: PNG, JPEG, WebP, or record to video via MediaRecorder

### Programmatic Content Matrix

| Tool | Images | Video | Animation | Runs On VPS | GPU Needed |
|------|--------|-------|-----------|-------------|------------|
| Pillow | Yes | No | No | Yes | No |
| FFmpeg | Convert | Yes | Transitions | Yes | No |
| Three.js | Yes (capture) | Yes (record) | Yes | Yes (headless) | No (CPU renderer) |
| Remotion | No | Yes | Yes | Yes (Node.js) | No |
| Motion Canvas | No | Yes | Yes | Yes | No |
| SVG/CSS | Yes | No | Yes | Yes | No |
| Canvas API | Yes | Yes (record) | Yes | Yes | No |

---

## 4. Audio/Voice Alternatives

### Current State: ElevenLabs

We currently use ElevenLabs for blog audio narration:
- **Voice**: "Aether - Updated" (RX0kjGhuL9AMRVJm2dG5)
- **Model**: eleven_multilingual_v2
- **Tool**: `tools/blog_audio.py`
- **Cost**: $5-22/month depending on plan + per-character overage

### Open-Source TTS Models (March 2026 Landscape)

The TTS space just had a MASSIVE week. On March 26, 2026, three models dropped within hours. Multiple open-source models now BEAT ElevenLabs in blind tests.

#### Tier 1: Best Quality (Beat ElevenLabs in Blind Tests)

**Chatterbox (Resemble AI)** -- RECOMMENDED
- **Quality**: 63.75% of blind test participants preferred Chatterbox over ElevenLabs
- **Voice cloning**: Yes, from short audio sample
- **License**: MIT (full commercial use)
- **VRAM**: Runs on NVIDIA (CUDA), AMD (ROCm), Apple Silicon, or CPU
- **Self-host**: Docker server available (github.com/devnen/Chatterbox-TTS-Server)
- **API compatible**: Drop-in OpenAI TTS API compatible endpoint
- **Versions**: Original (English), Multilingual (23 languages), Turbo (fastest)

**Voxtral TTS (Mistral)** -- NEWEST
- **Quality**: 62.8% of listeners preferred it over ElevenLabs Flash v2.5
- **Released**: March 26, 2026
- **Emotional expressiveness**: Matches ElevenLabs premium v3 tier
- **License**: Check Mistral's terms (likely Apache-adjacent)

**Orpheus TTS (Canopy AI)**
- **Quality**: Human-like emotional speech, rivals premium cloud services
- **Parameters**: 3B, 1B, 400M, 150M variants
- **Training**: 100K+ hours of English speech data
- **Architecture**: Llama-based (familiar ecosystem)
- **Best for**: Emotional narration, audiobooks

#### Tier 2: Solid Alternatives

**Bark (Suno)**
- **Quality**: Most "human-sounding" for emotional content
- **Unique**: Generates laughter, sighs, music, environmental sounds
- **VRAM**: 8-12GB
- **Best for**: Character voices, expressive narration
- **Limitation**: Slower generation speed

**Coqui XTTS v2**
- **Quality**: Excellent, matches ElevenLabs for clarity
- **Voice cloning**: Yes, from just 6 seconds of audio
- **Languages**: 17 languages
- **VRAM**: 4-8GB
- **License**: Coqui Public Model License (NON-COMMERCIAL -- check before using in production)

**Tortoise TTS**
- **Quality**: Can pass for human speech
- **Speed**: SLOW -- 10 minute wait for good output
- **License**: Apache 2.0 (commercial OK)
- **Best for**: Audiobook production where speed does not matter

#### Tier 3: Lightweight / Edge

**Piper**
- **Quality**: Good enough for notifications, IVR, embedded
- **Runs on**: Raspberry Pi, Android, embedded Linux
- **No GPU needed**: CPU only
- **Speed**: Real-time
- **Best for**: Edge deployment, IoT

**Kokoro**
- **Quality**: Good
- **License**: Apache 2.0
- **Lightweight**: Small model, fast inference

### TTS Quality Ranking (March 2026)

| Model | Quality vs ElevenLabs | Speed | Voice Clone | Commercial License | GPU Required |
|-------|----------------------|-------|-------------|-------------------|-------------|
| Chatterbox | BEATS (63.8% prefer) | Fast | Yes | MIT - YES | Optional (CPU works) |
| Voxtral | BEATS (62.8% prefer) | Fast | TBD | Check terms | Yes |
| Orpheus | Matches premium | Medium | Yes | Check terms | Yes (3B model) |
| Bark | Beats on expressiveness | Slow | No | MIT - YES | Yes (8GB) |
| XTTS v2 | Matches on clarity | Medium | Yes (6 sec!) | NON-COMMERCIAL | Yes (4GB) |
| Tortoise | Matches | Very Slow | Yes | Apache - YES | Yes (8GB) |
| Piper | 70% quality | Real-time | No | MIT - YES | No (CPU) |

### Migration Path from ElevenLabs

**Phase 1** (Immediate): Install Chatterbox TTS Server on a GPU rental for testing
**Phase 2** (If quality confirmed): Create drop-in replacement for `tools/blog_audio.py`
**Phase 3** (Production): Self-host on dedicated GPU or use RunPod serverless

```python
# Current ElevenLabs call in blog_audio.py:
response = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
    headers={"xi-api-key": api_key},
    json={"text": text, "model_id": "eleven_multilingual_v2"}
)

# Chatterbox self-hosted replacement:
response = requests.post(
    "http://localhost:8000/v1/audio/speech",  # OpenAI-compatible endpoint
    json={"input": text, "voice": "aether-cloned", "model": "chatterbox"}
)
# Same interface, zero per-character cost
```

---

## 5. Cost Comparison & Break-Even Analysis

### Current Monthly Costs (Estimated)

| Service | Monthly Cost | Usage | Per-Unit Cost |
|---------|-------------|-------|---------------|
| DALL-E / Gemini Image | $20-60/mo | ~500-1000 images | $0.02-0.08/image |
| ElevenLabs TTS | $5-22/mo | Blog narration | Per-character |
| Google VEO (if used) | Usage-based | Occasional | $0.05-0.15/sec |
| **Total** | **$25-82/mo** | | |

### Alternative Cost Models

#### Option A: Cloud GPU Rental (On-Demand)

Use RunPod or Vast.ai only when generating content.

| Provider | GPU | Cost/Hr | Notes |
|----------|-----|---------|-------|
| Vast.ai | RTX 4090 | $0.29-0.40/hr | Cheapest, community marketplace |
| RunPod | RTX 4090 | $0.44/hr | More reliable, better UX |
| RunPod | A100 80GB | $1.74/hr | For video generation |
| Vast.ai | H100 | $1.87/hr | Overkill for images |

**Typical session**: 2-hour generation run = $0.58-$0.88 (RTX 4090)
- In 2 hours with SDXL Turbo: ~2,000-5,000 images
- In 2 hours with FLUX.2 Dev: ~200-500 images
- In 2 hours with Chatterbox TTS: ~50-100 blog narrations

**Monthly estimate** (2 sessions/week): $4.64-7.04/month

#### Option B: RunPod Serverless

Pre-deployed endpoints that only bill when processing.

- SDXL: ~$0.002/image (cheaper than DALL-E at $0.04-0.08)
- Flux: ~$0.005/image
- TTS: ~$0.001/1000 characters

**Monthly estimate** (same volume): $3-8/month

#### Option C: Dedicated GPU Server

Rent a persistent GPU server for always-on generation.

| Provider | GPU | Monthly | Best For |
|----------|-----|---------|----------|
| Vast.ai | RTX 4090 | ~$200/mo | Always-on generation |
| RunPod | RTX 4090 | ~$320/mo | Reliability |
| Lambda | A10G | ~$285/mo | Good balance |

**Only makes sense at**: 100+ images/day sustained volume

### Break-Even Analysis

```
Current costs:     ~$50/month (mid estimate)
GPU rental:        ~$6/month (on-demand, 2 sessions/week)
Savings:           ~$44/month = $528/year

Break-even for dedicated server ($200/mo):
  Need to generate 2,500+ DALL-E images/month to justify
  OR be generating content continuously

Recommendation: On-demand rental (Option A) until volume justifies dedicated
```

### True Cost Comparison Table

| Approach | Monthly Cost | Per Image | Per Audio (5min) | Setup Time |
|----------|-------------|-----------|------------------|------------|
| Current (APIs) | $50-82 | $0.04-0.08 | $0.10-0.50 | 0 (already set up) |
| On-demand GPU | $5-8 | ~$0.001 | ~$0.01 | 4-8 hours initial |
| Serverless GPU | $3-8 | ~$0.002-0.005 | ~$0.01 | 2-4 hours |
| Programmatic only | $0 | $0 | N/A | 1-2 hours |
| Dedicated server | $200-320 | ~$0.0005 | ~$0.005 | 8-16 hours |

---

## 6. Recommended Stack for Pure Technology

### The PT Content Creation Stack

Based on our current infrastructure (2-core Xeon VPS, 4GB RAM, no GPU), current volume, and quality requirements:

#### Layer 1: Programmatic (Daily Use -- Runs on Current VPS)

| Tool | For | Status |
|------|-----|--------|
| **Pillow** | Blog banners, social graphics, OG images | ALREADY WORKING |
| **FFmpeg** | Video compilation, audio processing | INSTALLED |
| **SVG/CSS Animation** | Animated web graphics, logos | Ready to use |
| **Remotion** | Programmatic video from React | NEW -- install Node.js package |
| **Three.js capture** | 3D renders as images/video | ALREADY BUILT |

**Cost**: $0.00/month
**Covers**: 70-80% of daily content needs

#### Layer 2: AI Image Generation (Weekly Use -- Cloud GPU)

| Tool | For | How |
|------|-----|-----|
| **FLUX.2 Dev** | Hero images, marketing materials | RunPod/Vast.ai on-demand |
| **SDXL + LoRAs** | Bulk social content, variations | RunPod/Vast.ai on-demand |
| **ComfyUI** | Workflow management | Runs on rental GPU |

**Cost**: ~$2-4/week ($8-16/month)
**Covers**: Premium imagery that Pillow can not create

#### Layer 3: AI Voice (As Needed -- Cloud GPU or Serverless)

| Tool | For | How |
|------|-----|-----|
| **Chatterbox** | Blog narration (replace ElevenLabs) | Self-host on GPU rental |
| **Piper** | Quick notifications, IVR | Runs on VPS (CPU only!) |

**Cost**: ~$1-2/month (or $0 with Piper for basic needs)
**Covers**: All audio narration

#### Layer 4: AI Video (Rare -- Heavy GPU)

| Tool | For | How |
|------|-----|-----|
| **CogVideoX** | Special hero video content | RunPod A100 rental |
| **AnimateDiff** | Animated banners from SD images | RunPod 4090 rental |

**Cost**: ~$2-4/month (occasional use)
**Covers**: Video content when programmatic is not enough

### Total Recommended Stack Cost

| Layer | Monthly Cost | % of Content |
|-------|-------------|-------------|
| Programmatic | $0 | 70-80% |
| AI Images | $8-16 | 15-20% |
| AI Voice | $1-2 | ~5% |
| AI Video | $2-4 | ~2% |
| **Total** | **$11-22/month** | **100%** |

**vs Current**: $50-82/month
**Savings**: $28-71/month ($336-852/year)

---

## 7. Infrastructure Assessment

### What Our Current VPS Can Run (No GPU)

| Tool | Can Run | Performance | Notes |
|------|---------|-------------|-------|
| Pillow | Yes | Fast | Already running |
| FFmpeg | Yes | Good | CPU encoding |
| Remotion | Yes | Good | Node.js based |
| SVG/Canvas | Yes | Fast | Lightweight |
| Three.js (headless) | Yes | OK | Via puppeteer/playwright |
| Piper TTS | Yes | Real-time | CPU only, lightweight |
| SDXL/Flux | NO | - | No GPU |
| Chatterbox | Barely | Very slow | CPU fallback exists but impractical |
| CogVideoX | NO | - | Needs GPU |

### What Needs a GPU Rental

Everything in Layers 2-4 of the recommended stack. The workflow:

1. Spin up RunPod/Vast.ai instance ($0.29-1.74/hr)
2. ComfyUI pre-installed on many templates
3. Generate batch of content
4. Download results to VPS
5. Shut down GPU instance

**Typical batch session**: 1-2 hours, $0.29-3.48 total

### Option: Add GPU to Existing Infrastructure

If content volume grows significantly:

| Option | Cost | Capability |
|--------|------|------------|
| DigitalOcean GPU Droplet | ~$150/mo | A10G, good for images |
| Hetzner GPU Server | ~$120/mo | RTX 4000, Europe-based |
| Buy a used RTX 3090 (local) | ~$600 one-time | 24GB VRAM, run anything |

**Not recommended yet** -- on-demand rental is more cost-effective at our volume.

---

## 8. Implementation Roadmap

### Phase 1: Immediate (This Week) -- $0 Cost

**Goal**: Expand what we can do with tools we ALREADY have.

- [ ] **Pillow**: Create templates for LinkedIn posts, comparison graphics, infographics
- [ ] **FFmpeg**: Set up video compilation pipeline (image slideshows with transitions)
- [ ] **SVG**: Create animated PureBrain logo and loading animations
- [ ] **Document**: Create reusable scripts in `tools/content-gen/`

### Phase 2: Short-Term (Next 2 Weeks) -- $0-20

**Goal**: Add Remotion and test open-source image generation.

- [ ] **Remotion**: Install, create first programmatic video (blog recap format)
- [ ] **RunPod account**: Sign up, add $10 credit
- [ ] **Test FLUX.2**: Run 1-hour test session generating PureBrain marketing images
- [ ] **Test SDXL**: Try ComfyUI with SDXL for bulk social content
- [ ] **Compare**: Side-by-side quality comparison vs DALL-E/Gemini output

### Phase 3: Medium-Term (Month 2) -- Switch Voice

**Goal**: Replace ElevenLabs with self-hosted TTS.

- [ ] **Test Chatterbox**: Generate sample blog narration, compare to current ElevenLabs output
- [ ] **Test Piper**: For lightweight/quick audio needs
- [ ] **Clone Aether voice**: Use Chatterbox voice cloning with existing ElevenLabs audio as reference
- [ ] **Update blog_audio.py**: Add self-hosted TTS backend option
- [ ] **A/B test**: Run both for 2 weeks, compare listener engagement

### Phase 4: Long-Term (Month 3+) -- Full Pipeline

**Goal**: All content creation fully self-sufficient.

- [ ] **Automated workflows**: ComfyUI API + Python scripts for batch generation
- [ ] **Video pipeline**: CogVideoX for hero content, Remotion for programmatic
- [ ] **Content scheduler**: Auto-generate daily social graphics from templates
- [ ] **Training**: Document all workflows for team knowledge

---

## Appendix A: Quick Install Commands

### Pillow (Already Installed)
```bash
pip install Pillow
```

### FFmpeg (Already Available)
```bash
sudo apt install ffmpeg
```

### Remotion
```bash
npx create-video@latest my-video
cd my-video && npm start
```

### Piper TTS (CPU -- Runs on VPS)
```bash
pip install piper-tts
echo "Hello from PureBrain" | piper --model en_US-lessac-medium --output_file test.wav
```

### ComfyUI (On GPU Server)
```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI && pip install -r requirements.txt
python main.py --listen 0.0.0.0 --port 8188
```

### Chatterbox TTS Server (On GPU Server)
```bash
docker run -p 8000:8000 --gpus all devnen/chatterbox-tts-server
# OpenAI-compatible API at http://localhost:8000/v1/audio/speech
```

---

## Appendix B: Demo -- Programmatic Banner vs AI-Generated

### What We Already Do (Pillow -- $0 Cost)

Our existing `tools/generate_blog_banners.py` creates banners like this:

```python
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
img = Image.new('RGB', (W, H), '#080a12')
draw = ImageDraw.Draw(img)

# Dark gradient background
for x in range(W):
    factor = x / W
    r = int(8 + factor * 6)
    g = int(10 + factor * 5)
    b = int(18 + factor * 12)
    draw.line([(x, 0), (x, H)], fill=(r, g, b))

# Hex grid overlay
for x in range(0, W, 60):
    draw.line([(x, 0), (x, H)], fill=(20, 24, 36), width=1)

# PureBrain blue accent bar
draw.rectangle([0, 0, 6, H], fill=(42, 147, 193))

# Title text
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
draw.text((80, 200), "Content Creation\nSelf-Sufficiency", fill=(255, 255, 255), font=font)

# Orange accent
draw.rectangle([80, 380, 280, 384], fill=(241, 66, 11))

img.save("demo_banner.png")
```

**Result**: Professional branded banner, generated in <1 second, $0 cost.

### What FLUX.2 Would Generate (On GPU Rental)

Same concept but with AI-generated imagery:

```
Prompt: "Dark futuristic banner for AI technology company,
deep navy blue (#080a12) background, blue (#2a93c1) and
orange (#f1420b) accent lighting, glass hexagonal shapes,
neural network visualization, premium minimalist design,
cinematic lighting, 1200x630"
```

Generated via ComfyUI FLUX.2 workflow on a $0.29/hr GPU rental.

**Result**: Photorealistic AI-generated imagery with same brand colors, ~15 seconds to generate, ~$0.001 cost.

### When to Use Which

| Scenario | Use Pillow | Use FLUX.2/SDXL |
|----------|-----------|----------------|
| Daily blog banners | YES | No (overkill) |
| Social media text posts | YES | No |
| Hero marketing imagery | No | YES |
| Product visualization | Maybe | YES |
| Comparison charts | YES | No |
| Infographics | YES | No |
| Photorealistic scenes | No | YES |
| Abstract/artistic imagery | Maybe | YES |

---

## Appendix C: Demo Image Generated

Since our Gemini API key is currently commented out/inactive in .env, here is a demonstration using our existing Pillow pipeline to show what we can generate RIGHT NOW at zero cost:

```bash
# Generate a demo banner on our VPS:
python3 tools/generate_blog_banners.py
```

This produces a full PureBrain-branded banner with:
- #080a12 dark background
- Hex grid overlay
- Blue (#2a93c1) and orange (#f1420b) accents
- Professional text layout
- Generated in under 1 second on CPU

For AI-generated imagery comparison, we would need to:
1. Activate the GOOGLE_API_KEY in .env (currently commented out), OR
2. Sign up for RunPod ($0 to create account, pay-as-you-go), OR
3. Use a free tier like Hugging Face Spaces (limited but functional)

---

## Appendix D: Key Resources & Links

### Image Generation
- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [FLUX.2 on Hugging Face](https://huggingface.co/black-forest-labs)
- [CivitAI Model Library](https://civitai.com) -- 100K+ models, LoRAs, workflows
- [Stable Diffusion Art Tutorials](https://stable-diffusion-art.com)

### Video Generation
- [Remotion](https://remotion.dev) -- Programmatic video with React
- [CogVideoX GitHub](https://github.com/zai-org/CogVideo)
- [Open-Sora GitHub](https://github.com/hpcaitech/Open-Sora)

### Voice/TTS
- [Chatterbox TTS Server](https://github.com/devnen/Chatterbox-TTS-Server)
- [Piper TTS](https://github.com/rhasspy/piper) -- CPU-only, lightweight
- [Orpheus TTS](https://github.com/canopyai/Orpheus-TTS)

### GPU Rental
- [RunPod](https://runpod.io) -- Reliable, good UI, from $0.44/hr
- [Vast.ai](https://vast.ai) -- Cheapest, community marketplace, from $0.29/hr

### Research Sources
- [Best Open-Source Image Gen Models 2026](https://www.bentoml.com/blog/a-guide-to-open-source-image-generation-models)
- [Open-Source Video Gen Models](https://www.pixazo.ai/blog/best-open-source-ai-video-generation-models)
- [Open-Source TTS Models](https://findskill.ai/blog/best-open-source-tts-2026/)
- [GPU Cloud Pricing Comparison](https://getdeploying.com/gpus)
- [Remotion Agent Skills](https://www.dplooy.com/blog/claude-code-video-with-remotion-best-motion-guide-2026)
- [Chatterbox Beats ElevenLabs](https://byteiota.com/chatterbox-tts-open-source-voice-synthesis-beats-elevenlabs/)
- [Local Flux Setup Guide](https://localaimaster.com/blog/flux-local-image-generation)

---

**End of document. Own the pipeline. Stop paying per pixel.**
