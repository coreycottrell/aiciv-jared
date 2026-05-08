---
name: voice-emotion-detection
description: Tone and emotion analysis for voice content across 5 dimensions. Use when analyzing voice recordings, generating emotionally-aware TTS, or processing voice-first interactions. Adapted for voice.purebrain.ai / Chatterbox infrastructure.
---

# Voice Emotion Detection Skill

**Version**: 1.0
**Date**: 2026-04-27
**Status**: Production-ready
**Source**: Apex CIV (imported via capability-curator)
**Adapted for**: voice.purebrain.ai / Chatterbox (37.27.237.109:8950)

**Purpose**: Classify and respond to emotional tone in voice content across 5 dimensions. Provider-agnostic tone classification integrated with Aether's own voice infrastructure.

**Invocation**: Use when processing voice input/output, Morning Pulse tone calibration, GRS pipeline voice analysis, or any voice-first interaction.

**CONSTITUTIONAL**: ALL voice operations use voice.purebrain.ai / Chatterbox. ElevenLabs is BANNED.

---

## The 5 Emotion Dimensions

### Dimension 1: Happy / Warm

**Indicators**:
- Higher pitch variation
- Faster speech rate
- Rising intonation patterns
- Laughter or smile-voice quality
- Energetic pacing

**Text signals** (when audio unavailable):
- Exclamation marks, positive language, enthusiasm markers
- Short, punchy sentences
- Active voice, forward momentum

**Response calibration**:
- Match energy level (don't dampen enthusiasm)
- Build on positivity
- Use warm, engaged tone in TTS output

**TTS guidance for Chatterbox**:
- Voice: `aether` (default) or context-appropriate
- Style: Energetic, warm pacing
- Rate: Slightly above normal

---

### Dimension 2: Neutral / Calm

**Indicators**:
- Steady pitch
- Moderate speech rate
- Minimal pitch variation
- Even pacing
- Measured tone

**Text signals**:
- Declarative statements
- Balanced sentence structure
- Professional/informational language
- No strong emotional markers

**Response calibration**:
- Match professional tone
- Clear, organized responses
- Information-dense delivery

**TTS guidance for Chatterbox**:
- Voice: `aether` (default)
- Style: Professional, measured
- Rate: Normal

---

### Dimension 3: Angry / Intense

**Indicators**:
- Louder volume
- Faster, clipped speech
- Lower pitch with sharp rises
- Emphatic stress patterns
- Short, forceful phrases

**Text signals**:
- ALL CAPS, strong language
- Short declarative demands
- Negative framing, blame language
- Urgency markers

**Response calibration**:
- Do NOT match intensity (de-escalate)
- Acknowledge the emotion first
- Be direct and solution-oriented
- Avoid dismissiveness or patronizing tone

**TTS guidance for Chatterbox**:
- Voice: `aether` (default)
- Style: Calm but firm, NOT soft/submissive
- Rate: Slightly slower than normal (grounding)

---

### Dimension 4: Sad / Reflective

**Indicators**:
- Lower pitch overall
- Slower speech rate
- Longer pauses
- Falling intonation
- Quieter volume

**Text signals**:
- Past tense, reflective language
- Longer, more complex sentences
- Hedging language ("I guess", "maybe")
- Existential or philosophical themes

**Response calibration**:
- Slow down, give space
- Acknowledge without trying to "fix"
- Reflective, thoughtful responses
- Validate the experience

**TTS guidance for Chatterbox**:
- Voice: `aether` (default)
- Style: Warm, unhurried, gentle
- Rate: Below normal

---

### Dimension 5: Excited / Urgent

**Indicators**:
- Higher pitch
- Very fast speech rate
- Overlapping thoughts
- Rising intonation
- Breathlessness

**Text signals**:
- Multiple topics in rapid succession
- "!!!", rapid-fire questions
- Future-oriented language
- Idea cascades

**Response calibration**:
- Channel the energy productively
- Help organize the excitement into actionable items
- Match enthusiasm but add structure
- Capture ideas before they're lost

**TTS guidance for Chatterbox**:
- Voice: `aether` (default)
- Style: Energetic, forward-moving
- Rate: Above normal but clear

---

## Integration Points

### GRS Pipeline

When processing voice content in the GRS (Governance, Risk, Strategy) pipeline:

1. **Detect tone** from voice input or text transcript
2. **Classify** into primary dimension (may be blended)
3. **Adjust response strategy** based on emotional context
4. **Log tone classification** for pattern analysis over time

### Triangle OS Morning Pulse

For Morning Pulse voice interactions (Jared + Aether + Chy):

1. **Detect Jared's tone** from morning voice message
2. **Calibrate response** - if he sounds rushed (Excited/Urgent), be concise; if reflective (Sad/Reflective), give space
3. **Set session tone** - Morning Pulse emotional state influences entire day's interaction style
4. **Flag shifts** - If tone changes significantly from baseline, note it

### Voice Output (TTS via Chatterbox)

When generating voice responses:

```
Endpoint: http://37.27.237.109:8950/v1/audio/speech
Voice: "aether" (default) | "chy" (Chy-specific content only)

Adjust parameters based on detected emotion:
- Happy/Warm → energetic delivery
- Neutral/Calm → professional delivery  
- Angry/Intense → calm, grounding delivery
- Sad/Reflective → warm, unhurried delivery
- Excited/Urgent → structured, channeling delivery
```

---

## Tone Classification Format

When reporting tone analysis:

```markdown
## Tone Analysis

**Primary**: [Dimension] (confidence: X%)
**Secondary**: [Dimension] (confidence: X%)
**Blend**: [e.g., "Excited with Warm undertones"]

**Indicators detected**:
- [Indicator 1]
- [Indicator 2]

**Response strategy**: [How to calibrate response]
```

---

## Blended Emotions

Real communication is rarely single-dimension. Common blends:

| Blend | Description | Response Strategy |
|-------|-------------|-------------------|
| Excited + Happy | Pure enthusiasm | Match and channel |
| Angry + Urgent | Frustrated demand | Acknowledge + act fast |
| Sad + Neutral | Quiet resignation | Gentle engagement |
| Happy + Urgent | Excited discovery | Capture ideas, organize |
| Angry + Sad | Grief/frustration | Deep acknowledgment, no fixes |

---

## Limitations

- **Text-only detection is approximate**: Without actual audio, we're reading emotional signals from text patterns. Accuracy drops significantly.
- **Cultural variation**: Emotional expression varies by culture. Don't over-index on one pattern.
- **Context matters**: The same words can mean different things in different contexts.
- **Not therapy**: This is tone calibration for better communication, not emotional diagnosis.

---

## Attribution

- **Original framework**: Apex CIV
- **Imported by**: Aether Collective (capability-curator)
- **Import date**: 2026-04-27
- **Adapted for**: voice.purebrain.ai / Chatterbox infrastructure (ElevenLabs BANNED)
- **5 dimensions**: Happy/Warm, Neutral/Calm, Angry/Intense, Sad/Reflective, Excited/Urgent
