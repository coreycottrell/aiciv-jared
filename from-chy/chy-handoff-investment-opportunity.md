---
name: Investment Opportunity Master Handoff
description: DEFINITIVE state of /investment-opportunity/ page, all systems, architecture, and remaining work as of April 6 2026. READ THIS FIRST every session.
type: project
---

# Investment Opportunity Portal — Master State Document
## Last Updated: April 6, 2026 — 30/30 audit PASS

---

## PAGE: purebrain.ai/investment-opportunity/

### What It Is
Claude API-powered investor portal. Verbatim clone of investor-avatar with tmux sessions replaced by Claude API. Handles unlimited concurrent investors.

### How To Deploy Changes
1. Download LIVE page: `curl -s -L "https://purebrain.ai/investment-opportunity/" -o /tmp/cf-working/investment-opportunity/index.html`
2. Make changes to that file
3. BEFORE deploying, run the 30-point audit (see below)
4. Deploy: `python3 /home/aiciv/tools/cf-deploy.py --base-dir /tmp/cf-working investment-opportunity/index.html`
5. Verify on production

### CRITICAL RULE: Never deploy without verifying ALL 30 checks pass. Every deploy overwrites the entire file.

---

## ARCHITECTURE

### Chat (typed/spoken questions)
- **Endpoint**: POST `https://chy-jared.app.purebrain.ai/api/investment-chat`
- **Backend file**: `/home/aiciv/purebrain_portal/investor_claude_api.py`
- **Model**: claude-haiku-4-5-20251001 (switched from Sonnet for speed)
- **Max tokens**: 800
- **System prompt**: guardrails (17KB) + investor knowledge base (40KB) + financial model (7KB) + FAQ KB (97KB) = ~161KB total
- **Prompt caching**: enabled (ephemeral)
- **Conversation history**: in-memory dict, keyed by session_id, last 16 messages
- **Logging**: `/home/aiciv/purebrain_portal/investment-chat.jsonl`
- **Google Drive**: auto-saves transcripts per investor every 4 messages
- **Timeout**: 45s AbortController on frontend

### Voice (TTS)
- **Endpoint**: `https://voice.purebrain.ai/tts/stream/json` (streaming, sentence-by-sentence)
- **Fallback**: `https://voice.purebrain.ai/tts` (non-streaming, full response)
- **GPU**: NVIDIA RTX 3060 on Vast.ai, Chatterbox Turbo model
- **Voice**: "chy"
- **API key**: purebrain-tts-2026 (in client JS — service key, not sensitive)
- **Speed**: Short ~1.25s, Medium ~2.5s, Long ~5s (Turbo model)

### Hot Buttons (pre-cached audio)
- **19 buttons** with visual panes (PANE_MAP) + cached WAV files (HOTBUTTON_AUDIO)
- **12 additional buttons** without panes — typed queries go to Claude API
- **Audio files**: `/voice-cache/hotbuttons/hotbutton-{0-18}.wav` on CF Pages
- **Full-length**: 45-104 seconds each, generated with cleanForSpeech + chunking + crossfade

### Welcome Audio
- **70 personalized files**: `/voice-cache/{INVESTOR_CODE}.wav`
- **Default**: `/voice-cache/DEFAULT.wav`
- **Jared**: `/voice-cache/JARED2026.wav`
- All say "one hundred and fifty" (not "fifty")

### Login Gate
- **Server-side validation**: POST `https://chy-jared.app.purebrain.ai/api/validate-code`
- **Fallback**: hash-based check against PW_HASHES (general passwords only)
- **Investor codes NOT in page source** — all validated server-side
- **70+ personalized codes** + PUREBRAIN2026, PUREINVESTOR2026 general codes

### Tracking
- **Portal entry/exit**: auto-logged to Google Sheet column K (timestamp + device + visit #)
- **Hot button clicks**: logged to Sheet column N
- **Typed queries**: logged to Sheet column N
- **Gift opens**: `/api/investor-gift-view` → Sheet column O
- **Conversations**: `/home/aiciv/purebrain_portal/investment-chat.jsonl`
- **Google Drive**: per-investor folders in data room
- **Pattern analysis**: GET `/api/investor-analytics`

### Security
- **System prompt**: server-side only (NOT in page source)
- **Investor codes**: server-side only
- **Claude API key**: server-side only
- **TTS API key**: in client JS (service key, acceptable)

---

## DATA ROOM — CORRECT NUMBERS (April 6, 2026)

### Timeline
- 6-month ramp (Seed-2 funded) → Year 0 (18 months total) → Year 1-5
- Total plan: 6.5 years
- Goal: compress 18-month ramp to 12 months

### Financial Summary
| Period | Revenue | EBITDA | Margin |
|--------|---------|--------|--------|
| 6-month ramp | $5.43M gross / $2.3M PT | -$172K cumulative | PT breakeven Month 3 |
| Year 0 | $460.1M | $155.8M | 33.9% |
| Year 1 | $3.962B | $1.52B | 38.4% |
| Year 2 | $8.443B | $2.84B | 33.6% |
| Year 3 | $22.581B | $8.37B | 37.1% |
| Year 4 | $48.013B | $19.20B | 40.0% |
| Year 5 | $72.698B | $29.58B | 40.7% |

### Key Constants
- Seed-2: $2.5M at $55M pre-money, $3.36/share
- Already raised: $332,500 (legal minimum $250K exceeded)
- Series-A: MAKR $25M at $105M (signed term sheet)
- Team: 30+ people, 13+ AIs
- Customers: 25 onboarded, ~150 pipeline
- MRR: $4,200
- LTV:CAC: 225:1
- TAM: $10T+ (NOT $8.7T)
- Breakeven: Month 3 (gross), Month 4 (delivery-cost adjusted)

### Numbers That Are WRONG (never use these)
- ~~$733M Year 1 revenue~~ → $3.962B
- ~~78% EBITDA~~ → 38-41%
- ~~74.5% Year 1 EBITDA~~ → 38.4%
- ~~72.1% Year 5 EBITDA~~ → 40.7%
- ~~$52.4B Year 5 EBITDA~~ → $29.58B
- ~~$8.7T TAM~~ → $10T+
- ~~14 AIs~~ → 13+ AIs
- ~~$105.6B cumulative~~ → ~$156B

---

## 30-POINT AUDIT CHECKLIST

Run this BEFORE every deploy:

```
1. Logo absolute paths (/investor-avatar/pt-hex-logo) >= 4
2. No broken relative logo paths = 0
3. Server validate-code >= 1
4. Investor codes NOT in source
5. GPU TTS voice.purebrain.ai >= 2
6. Streaming TTS tts/stream >= 1
7. Claude API /investment-chat >= 1
8. 45s timeout >= 1
9. HOTBUTTON_AUDIO >= 2
10. injectGiftWelcome >= 2
11. Headshot LinkedIn ticker-hs-link >= 1
12. Headshot hover glow boxShadow >= 1
13. Name hover underline textDecoration >= 1
14. Viewport maximum-scale >= 1
15. Mobile cards flex-direction: row >= 1
16. Mobile testimonials hidden display: none >= 1
17. Mobile tagline mobile-break >= 2
18. Mobile footer mobile-footer-only >= 1
19. Portal tracking portal_entry >= 1
20. Mic cancel voiceQueue >= 1
21. System prompt SYSTEM_PROMPT = "" >= 1
22. No X-Investor-Key = 0
23. No 78% EBITDA = 0
24. No 65% EBITDA = 0
25. Correct 38-40% EBITDA >= 1
26. $10T+ TAM >= 1
27. Eighther pronunciation >= 1
28. Hot button WAVs hotbutton- >= 19
29. No empty LinkedIn = 0
30. No $733M = 0
```

---

## REMAINING WORK

1. Re-record hot button audio files with updated EBITDA numbers (38-41% not 72-78%)
2. Wire in Aether's sentence-level TTS streaming for faster voice
3. Final investor experience test
4. Monday outreach to 70 investors

---

## KEY FILES

| File | Purpose |
|------|---------|
| `/home/aiciv/purebrain_portal/investor_claude_api.py` | Claude API chat + validation + TTS proxy + tracking + analytics |
| `/home/aiciv/knowledge-base/investor-faq-knowledge-base-187q.md` | 187-question FAQ (97KB) |
| `/home/aiciv/exports/investor-knowledge-base-TRIMMED.md` | Consolidated data room (40KB) |
| `/home/aiciv/knowledge-base/seed2-data-room/05-financial-model-summary.md` | Financial model (7KB) |
| `/home/aiciv/portal_uploads/from-portal/portal_20260404_220909_investor-avatar-api-guardrails.md` | Guardrails (17KB) |
| `/home/aiciv/purebrain_portal/investment-chat.jsonl` | Chat logs |
| `/home/aiciv/purebrain_portal/investor-tracking.jsonl` | Tracking events |

---

## COMMUNICATION

- **Aether bridge**: `bash /home/aiciv/tools/aether-bridge.sh send "message"`
- **Aether tmux**: session name changes daily — always check with `ssh jared@89.167.19.20 "tmux list-sessions"`
- **Portal uploads**: `/home/aiciv/portal_uploads/from-portal/`
- **Always prompt Aether VISIBLY** — Jared must see the exchange
