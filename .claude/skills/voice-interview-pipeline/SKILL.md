---
name: voice-interview-pipeline
version: 1.0.0
source: True Bearing (Cory Cottrell)
accepted: 2026-03-28
description: Voice-first interview pipeline — voice capture, STT, conversational AI, profile building, TTS response. For voice-first onboarding flows.
agents:
  - dept-systems-technology
  - dept-product-development
  - feature-designer
  - wtt-fullstack
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---

# Voice Interview Pipeline

**Origin**: True Bearing (Cory Cottrell's AI civilization)
**Accepted**: 2026-03-28 by Jared (approved for skills library)
**Intent**: Voice-first onboarding flow for purebrain.ai

## What It Does

A voice-driven interview pipeline that replaces text-based onboarding with natural conversation:

1. **Voice Capture** — Web Speech API or similar for browser-based voice input
2. **Speech-to-Text** — Transcription of user voice to text for AI processing
3. **Conversational AI** — Claude API processes responses, maintains interview flow
4. **Profile Building** — Extracts structured data (name, role, company, goals) from natural conversation
5. **TTS Response** — ElevenLabs or similar for AI voice output (Aether voice: RX0kjGhuL9AMRVJm2dG5)

## Architecture

```
User speaks → Web Speech API → STT → Claude API → Response text → ElevenLabs TTS → Audio playback
                                                       ↓
                                              Profile data extracted
                                                       ↓
                                              Seed/onboarding record
```

## PureBrain Application

Replace the current text-based awakening flow with voice conversation:
- User speaks their name, role, company, goals
- AI responds with voice (Aether's voice)
- More natural, more engaging, higher completion rates
- Falls back to text input if mic unavailable

## Key Technical Components

- Web Speech API (browser-native, no extra deps)
- ElevenLabs TTS API (existing integration, voice ID: RX0kjGhuL9AMRVJm2dG5)
- Claude API for conversation intelligence (existing portal server proxy)
- Profile extraction from unstructured voice conversation

## Constitutional Notes

- Seed flow rules still apply — naming BEFORE payment, full conversation in seed email
- All payment page constitutional checks must pass on any page with voice onboarding
- Voice data is processed in real-time, not stored (privacy by design)
