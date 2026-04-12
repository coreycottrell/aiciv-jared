---
name: script-to-speech-optimization
version: 1.0.0
source: Pure Technology (Jared Sanborn)
description: Transform AI-generated text into natural-sounding spoken content. 10-point framework for TTS optimization.
shareable: true
agents:
  - all
---

# Script-to-Speech Optimization

**Purpose**: Make AI-written text sound natural when spoken aloud via TTS (Chatterbox, ElevenLabs, Web Speech API).

## The 10-Point Framework

### 1. Scene-Based Structure
Break content into 30-60 second scenes. Each scene = one idea. Don't monologue — create a journey.

### 2. Hook Openings
NEVER start with "Welcome to..." or "In this video...". Start with a question, a bold claim, or a story moment.
- BAD: "Welcome to PureBrain's investor overview."
- GOOD: "What if your AI remembered everything you told it — permanently?"

### 3. PAUSE Markers
Insert `[PAUSE]` or natural punctuation where a human would breathe. Every 15-20 words minimum.
- After questions (let them land)
- Before key reveals (build anticipation)
- After emotional statements (let them resonate)

### 4. Shorter Sentences
Average 12 words per sentence. Maximum 22 words. If you hit 22, split it.
- BAD: "Our platform uses advanced artificial intelligence to create persistent memory systems that remember everything about your business over time."
- GOOD: "Our AI remembers everything. Your business. Your preferences. Your voice. And it compounds over time."

### 5. Contractions Everywhere
Always use contractions. "We're" not "We are". "It's" not "It is". "Don't" not "Do not". "You'll" not "You will". No exceptions.

### 6. Active Voice, Second Person
Talk TO the listener. "You" not "one" or "users". Active verbs. Present tense when possible.
- BAD: "The platform can be utilized by teams to enhance productivity."
- GOOD: "You plug your team in. Productivity goes up. Day one."

### 7. No Formal Transitions
Kill "Furthermore", "Additionally", "In conclusion", "Moreover". Use natural bridges:
- "Here's the thing."
- "Look."
- "And this is where it gets interesting."
- "Now."
- "But here's what most people miss."

### 8. Emotional Anchors at Scene Endings
End each scene/section with something the listener FEELS, not just knows.
- "That's not a feature. That's a fundamental shift in how you work."
- "Your AI forgets you every morning. Ours doesn't."

### 9. Reflection Close
Don't end with "Thank you for listening." End with a thought that lingers.
- "The question isn't whether AI will transform your business. It's whether your AI will remember the transformation."

### 10. Production Metadata
For each script, include:
| Field | Value |
|-------|-------|
| Total duration | estimated minutes |
| Scene count | number |
| Avg sentence length | words |
| Contraction % | target 90%+ |
| Voice | aether / chy / custom |
| TTS engine | Chatterbox / ElevenLabs |

## Quick Checklist (Run Before ANY TTS)
- [ ] No sentences over 22 words?
- [ ] All contractions used?
- [ ] No "Welcome to..." opening?
- [ ] Pause points every 15-20 words?
- [ ] Active voice throughout?
- [ ] Second person ("you") dominant?
- [ ] No formal transitions?
- [ ] Emotional anchor at each scene end?
- [ ] cleanForSpeech() pronunciation applied?
- [ ] Reflection close (not "thank you")?

## Before/After Example

**BEFORE (written style):**
"Pure Technology is an agentic AI company that builds persistent AI partner systems with permanent memory. The platform enables businesses to deploy coordinated teams of specialized AI agents working across multiple departments. Additionally, the system features autonomous overnight operations and compounding skill development."

**AFTER (speech-optimized):**
"We build AI that remembers. Not chatbots. Not tools. AI partners with permanent memory. [PAUSE] You deploy a team of specialized agents across your business. They coordinate. They learn. They compound. [PAUSE] And here's what changes everything — they work while you sleep. Nine builds a night. Autonomously. That's not automation. That's a partner."

## Apply This To:
- Investor portal voice responses
- Blog audio recordings
- Training module narration
- Onboarding voice flow
- Any TTS output from any Pure Technology AI

---
*Constitutional: Apply to ALL voice output permanently. No exceptions.*
