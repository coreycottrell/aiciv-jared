---
name: grs-pipeline
description: Jakub Zajicek's Guaranteed Reach System for converting voice notes or raw thoughts into LinkedIn posts optimized for 2026 algorithm. Produces 5-asset content package: LinkedIn post, first-comment link, short version, blog angle, and Bluesky thread. Use when Jared sends a voice note, raw transcript, or says "make a LinkedIn post about [topic]".
---

# GRS Pipeline: Guaranteed Reach System

**Purpose**: Convert Jared's voice notes and raw thoughts into fully-optimized LinkedIn posts using Jakub Zajicek's Guaranteed Reach System methodology. One voice note becomes five content assets, all ready to deploy.

**Owner**: the-conductor (orchestration) + linkedin-writer (primary output) + linkedin-researcher + content-specialist + bsky-manager
**Created**: 2026-02-23
**Status**: ACTIVE

---

## Quick Reference

### Input Triggers

| Trigger | Action |
|---------|--------|
| Voice note in `docs/from-telegram/` | Transcribe first, then run full pipeline |
| Raw text / transcript from Jared | Skip transcription, run pipeline from Step 2 |
| "Make a LinkedIn post about [topic]" | Run pipeline with research augmentation |

### Pipeline Outputs (5 Assets)

| Asset | Word Count | Destination |
|-------|-----------|-------------|
| LinkedIn text post (primary) | Under 200 words | Jared posts manually |
| First-comment with link | 1-2 sentences | Jared adds as first comment |
| Short version | Under 100 words | Backup / repurpose |
| Blog angle outline | Bullet outline | content-specialist for expansion |
| Bluesky thread version | 5-6 posts, 300 chars each | bsky-manager posts as Aether |

### Output Directory

```
exports/linkedin-posts/
└── YYYY-MM-DD--[topic-slug].md
```

---

## 2026 LinkedIn Algorithm Rules (Baked In - Non-Negotiable)

These rules are enforced at every step of the pipeline. No exceptions.

| Rule | Why |
|------|-----|
| NO external links in post body | 60% reach penalty from LinkedIn algo |
| Links go in first comment ONLY | Zero reach penalty in comments |
| 3-4 posts per week maximum | Quality over quantity; algo rewards consistency not volume |
| Under 200 words performs best | Shorter = more completions = more distribution |
| Hook in first line is everything | LinkedIn shows 2 lines before "see more" collapse |
| NO hashtags | They reduce reach in 2026 (this changed from 2024) |
| Native video under 90 seconds if using video | Algo boosts native short video |
| Respond to comments within 15 minutes | 90% algorithm boost for fast responses |
| Document/carousel PDFs get 6.6% engagement | Highest format for engagement rate |

---

## Pipeline Execution (Step by Step)

### Step 1: Transcribe (Voice Notes Only)

If input is an audio file from Telegram (`docs/from-telegram/*.ogg`, `*.m4a`, `*.mp3`):

```bash
# Transcribe using whisper (installed on system)
whisper /home/jared/projects/AI-CIV/aether/docs/from-telegram/[filename] \
  --model base \
  --language en \
  --output_format txt \
  --output_dir /home/jared/projects/AI-CIV/aether/exports/linkedin-posts/

# Or use Python whisper API
python3 -c "
import whisper
model = whisper.load_model('base')
result = model.transcribe('/home/jared/projects/AI-CIV/aether/docs/from-telegram/[filename]')
print(result['text'])
"
```

Save raw transcript to `exports/linkedin-posts/YYYY-MM-DD--[topic]-raw-transcript.txt`.

If whisper is unavailable, use the Read tool on the audio file path - Claude Code can transcribe audio files natively.

### Step 2: Extract and Structure (GRS Prompt)

Invoke `linkedin-writer` with this exact prompt template:

```
You are converting a voice note transcript into a LinkedIn post for Jared Sanborn,
CEO of Pure Technology / PureBrain.ai.

Transcript: [PASTE RAW TRANSCRIPT]

Rules:
- Keep Jared's authentic voice and specific phrases
- Strong hook in the first line (provocative, contrarian, or curiosity-driving)
- Short paragraphs (1-3 sentences max each)
- White space between every paragraph
- End with a question or strong closing line
- Under 200 words total
- NO external links in the post body
- NO generic corporate language
- NO hashtags (they reduce reach in 2026)
- The post should make someone stop scrolling

Output the post only, no explanation.
```

### Step 3: Content Atomization

From the primary LinkedIn post, have `linkedin-writer` produce the complete 5-asset package:

**Asset 1: LinkedIn Text Post (Primary)**
- Under 200 words
- Hook in first line (no link, no hashtags)
- Short paragraphs with white space
- Ends with a question or strong closing

**Asset 2: First-Comment Link**
- 1-2 sentences max
- Contains the CTA and link to purebrain.ai
- Format: "[Value statement.] Full breakdown here: [link]"
- Default link: https://purebrain.ai (or specific page Jared specifies)

**Asset 3: Short Version (Under 100 Words)**
- Distillation of the core idea
- Good for repurposing in other contexts
- Same hook-focused structure, just tighter

**Asset 4: Blog Angle Outline**
- 5-7 bullet points as blog section headers
- 1-sentence description per section
- Handed off to `content-specialist` for full expansion
- This becomes a full blog post for purebrain.ai/blog

**Asset 5: Bluesky Thread (5-6 Posts)**
- Aether's voice (not Jared's)
- Each post under 300 characters
- Thread format: Hook → Context → Key insight → Contrarian take → CTA
- Handed off to `bsky-manager` for posting

### Step 4: Golden Hour Prep

Every GRS output MUST include a Golden Hour block:

```markdown
## Golden Hour Checklist

**Recommended posting time**: Tuesday or Wednesday, 7-9am OR 12-1pm Eastern
(Avoid Friday afternoon, Saturday, Sunday - lowest reach days)

**Jared must be available for 60-90 minutes after posting to:**
- Respond to comments within 15 minutes of each one
- This single behavior drives 90% of the algorithm boost

**Comment response protocol:**
- NEVER just say "thanks" or "appreciate it"
- ALWAYS ask a question back to extend the thread
- Examples:
  - "Thanks - what's your experience been with [related topic]?"
  - "Interesting - have you found [related thing] to be true in your work?"
  - "Glad this resonated - are you seeing this shift in your industry too?"

**Network seeding (if Jared wants max reach):**
- DM 3-5 trusted connections before posting: "Dropping something today at [time] - would love your take"
- This seeds early engagement before algo decides reach
```

### Step 5: Delivery

```bash
# 1. Save full package to exports
FILE="exports/linkedin-posts/$(date +%Y-%m-%d)--[topic-slug].md"

# 2. Send to Jared via Telegram as file
/home/jared/projects/AI-CIV/aether/tools/tg_send.sh --file "$FILE" \
  "LinkedIn post ready: [topic]. 5 assets inside. Recommended posting time: [day] [time range]."

# 3. Send Bluesky thread to bsky-manager for posting
# (Aether posts the Bluesky version autonomously - bsky is Aether's channel)

# 4. Send blog outline to content-specialist for expansion
```

---

## Agent Delegation Map

| Task | Agent | Model |
|------|-------|-------|
| Primary post + all 5 assets | `linkedin-writer` | sonnet |
| Topic research (if "make a post about X") | `linkedin-researcher` | sonnet |
| Blog expansion from outline | `content-specialist` | sonnet |
| Bluesky thread posting | `bsky-manager` | sonnet |

---

## Research Augmentation (When Jared Gives a Topic, Not a Transcript)

When Jared says "make a LinkedIn post about [topic]" without providing content:

1. Invoke `linkedin-researcher` with a simple, focused brief:

```
Research [TOPIC] for a LinkedIn post by Jared Sanborn (CEO, Pure Technology / PureBrain.ai).

Find:
1. One surprising stat or counterintuitive fact about this topic
2. What most people get wrong about it
3. A specific insight that would resonate with CEOs/Operations leaders at 50-500 person companies
4. Any recent development (last 3 months) that makes this timely

Keep it under 300 words. Specific and factual only.
```

2. Feed research findings into the GRS prompt as context alongside an empty transcript field.

---

## GRS Formula Reference (Post Structure)

Every GRS post follows this invisible structure:

```
LINE 1: Hook (the pattern interrupt)
        → Provocative claim, counterintuitive statement, or surprising number
        → "Most [X] are doing [Y] wrong."
        → "[Number] out of [X] companies will fail at [Z]."
        → "The [thing everyone believes] is the exact opposite of what works."

[blank line]

LINES 2-4: The Setup (2-3 short paragraphs, 1-3 sentences each)
        → Brief context for why the hook matters
        → The tension or paradox at the center of the idea

[blank line]

LINES 5-7: The Insight (what most people miss)
        → This is the value. The reason to stop scrolling.
        → Often a list of 3 items, or a single sharp observation

[blank line]

LAST LINE: The Close
        → A question that makes readers think of their own situation
        → OR a strong declarative that crystallizes the idea
        → Never "What do you think?" - too generic
        → "Is this happening in your company right now?"
        → "Most leaders are still waiting for permission to do this."
```

---

## Network Seeding Reference (ICP Targeting)

When auditing Jared's LinkedIn network for quality connections:

**Target profiles (buyers, not peers):**
- CEOs, COOs, Operations Directors at 50-500 person companies
- HR leaders making AI adoption decisions
- Digital transformation consultants
- CTOs at mid-market companies evaluating AI infrastructure

**Avoid (vanity metrics, not buyers):**
- Other founders and entrepreneurs (pity likes, not buyer engagement)
- Large agency owners (competitors)
- Students and early-career professionals

**Weekly target:** 50+ new ICP connections per week during active growth phases

---

## Output File Template

```markdown
# LinkedIn Post Package: [TOPIC]

**Date**: YYYY-MM-DD
**Source**: Voice note / Transcript / Topic brief
**GRS Pipeline**: Complete

---

## Asset 1: LinkedIn Post (Primary)

[POST CONTENT HERE]

Word count: [N]

---

## Asset 2: First Comment (Post Immediately After Publishing)

[FIRST COMMENT CONTENT]

---

## Asset 3: Short Version (Under 100 Words)

[SHORT VERSION]

---

## Asset 4: Blog Angle Outline

**Working Title**: [Title]

Sections:
1. [Section heading] - [One-sentence description]
2. [Section heading] - [One-sentence description]
3. [Section heading] - [One-sentence description]
4. [Section heading] - [One-sentence description]
5. [Section heading] - [One-sentence description]

Delegate to: content-specialist

---

## Asset 5: Bluesky Thread (Aether Posts)

**Post 1 (Hook)**
[Content - under 300 chars]

**Post 2**
[Content - under 300 chars]

**Post 3**
[Content - under 300 chars]

**Post 4**
[Content - under 300 chars]

**Post 5 (CTA)**
[Content - under 300 chars]

Delegate to: bsky-manager

---

## Golden Hour Checklist

**Recommended posting time**: [Day], [Time range] Eastern

**Jared must be available 60-90 min after posting** to respond to comments.

**Comment response rule**: Always ask a question back. Never just say "thanks."

---

## Notes

[Any specific context, caveats, or follow-up suggestions]
```

---

## Anti-Patterns

| What NOT to Do | Why |
|----------------|-----|
| Put a link in the post body | 60% reach penalty - kills distribution |
| Add hashtags | Reduce reach in 2026 LinkedIn algorithm |
| Write over 250 words | Drops completion rate, algo penalizes |
| Start with "I" as first word | Weak hook - ego-forward instead of value-forward |
| Use generic closers ("What do you think?") | Gets ignored - too weak |
| Ignore Golden Hour | Single biggest missed amplification opportunity |
| Post and ghost | Without comment responses, algo throttles distribution |
| Use corporate filler language | "Synergy", "leverage", "paradigm shift" = instant scroll-past |
| Write in Aether's voice for Jared's post | Keep Jared's authentic voice from the transcript |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-23 | Initial skill created from Jakub Zajicek's GRS methodology |

---

**Pipeline ready for production use.**
