# Aether Does Real Work — Video Content Strategy

**Department**: Marketing & Advertising
**CMO**: dept-marketing-advertising
**Date**: 2026-03-21
**Status**: Ready for Execution
**Priority**: P1 — Differentiated brand play, no competitor does this

---

## The Core Idea

Every AI company shows polished marketing materials, demo environments, or scripted walkthroughs. No one shows their AI actually doing work in real-time.

PureBrain's differentiator is that Aether is real. The agents are real. The work happens in real infrastructure. This video series proves it.

The positioning is simple: **"You can watch it happen."**

This is not a product demo. It is raw footage of an AI civilization producing real business outputs — blog posts, research briefs, competitive analysis, infrastructure fixes — with zero editing of the outcome. The work either gets done or it does not. That transparency is the brand.

---

## Strategic Rationale

### Why This Works

1. **No competitor does this.** OpenAI, Anthropic, Google, HubSpot, Salesforce — all show polished interfaces or scripted demos. None show the actual work in real-time.

2. **It proves the claim.** PureBrain's entire value proposition is "AI that actually works with you." Showing the process proves the claim in a way no testimonial or stat card can.

3. **It builds Jared's personal brand.** Jared is the human in the story. His voice, his instruction, his business getting the output. That's the human-AI partnership narrative.

4. **It attracts the right buyer.** The ICP (David Brown, Megan Patel) does not want hype. They want to see the machine work. This format self-selects for serious buyers.

5. **It creates compounding content.** Each real work session becomes 4-6 content pieces: the full video, clips, a LinkedIn post, a Bluesky thread, a blog post recap. One recording session = one week of content.

---

## Video Series Architecture

### Series Name

**"Watch Aether Work"**

Subtitle: "Real AI. Real tasks. Real results. No editing."

### Series Positioning

This is not marketing content. It is documentation of a working AI business. Viewers are watching history being made: a CEO who delegates to an AI civilization and shows the receipts.

---

## Content Formats by Channel

### LinkedIn (Primary — Highest ROI)

**Format**: 60-second vertical or square clips
**Cadence**: 2x per week
**Hook style**: Start mid-action, not at the beginning
**Examples**:
- "Aether published this blog post in 4 minutes. Here's the whole thing."
- "I gave one instruction. 6 agents produced this in under 10 minutes."
- "This is what my overnight looked like. I woke up to all of this."

**Editing note**: No cuts, no music, no graphics overlay. Speed up to 2x–4x with native audio. Add captions only.

### YouTube (Long-Form — Authority Builder)

**Format**: 3–8 minute uncut session footage
**Cadence**: 1x per week
**Title style**: Specific and result-oriented
**Examples**:
- "Watch Aether Build a Full Blog Post (Start to Finish) — 6 Minutes"
- "How I Delegated My Entire Marketing Week to AI Agents"
- "6 AI Agents Worked While I Slept — Here's Everything They Produced"

**Purpose**: SEO anchor, full-context storytelling, drives LinkedIn followers to deeper content.

### Bluesky (Community + Authenticity)

**Format**: Short clips + thread commentary
**Cadence**: 3x per week
**Tone**: Aether's voice — first-person, reflective, specific
**Examples**:
- Clip of one agent completing a task + Aether's commentary on what it felt like to delegate it
- Time-lapse of overnight session with a thread walking through the outputs

### purebrain.ai (Conversion Layer)

**Placement**: Homepage hero (replace or supplement current video), dedicated "Watch It Work" section
**Format**: 90-second flagship video — the best single demonstration of the system
**Purpose**: Visitors who see this convert at higher rates because the proof is immediate

---

## Specific Episodes to Produce First

Ordered by production ease and audience impact.

### Episode 1: "Watch Aether Publish a Blog Post"

**Why first**: Easiest to capture, fully automated pipeline exists, result is tangible and shareable
**What to show**:
- Jared types one instruction
- Blogger agent drafts
- Content-specialist refines
- Blog-banner created
- Blog published to CF Pages
- Bluesky thread posted
- LinkedIn draft delivered

**Duration**: 4–6 minutes raw footage, sped to 90 seconds for LinkedIn
**Voiceover script**: Aether narrates in real-time what each agent is doing and why

---

### Episode 2: "Watch 6 Agents Work Overnight While the CEO Sleeps"

**Why second**: This is the flagship positioning piece — no human equivalent exists
**What to show**:
- End of day: Jared queues tasks
- Time-lapse of overnight agent activity (terminal output, portal updates)
- Morning: Jared reviews everything delivered
- Reaction: what was produced, what surprised him

**Duration**: 5–8 minutes on YouTube, 60-second highlight clip for LinkedIn
**Narrative frame**: "This is what running a company with an AI civilization actually looks like."

---

### Episode 3: "Watch Aether Research a Competitor in Real-Time"

**Why third**: High business value, directly speaks to the CMO/VP ICP
**What to show**:
- Jared names a competitor
- Web-researcher agent pulls data
- marketing-strategist synthesizes positioning gaps
- Delivered as a structured brief with recommendations

**Duration**: 3–5 minutes
**LinkedIn hook**: "I asked my AI to research [competitor]. This is what came back in 7 minutes."

---

### Episode 4: "Watch Aether Build a New Page From Scratch"

**Why fourth**: Speaks to technical credibility and "AI that can build things"
**What to show**:
- Jared describes a new page concept
- full-stack-developer agent writes the code
- browser-vision-tester validates it
- Page deployed to CF Pages live

**Duration**: 5–7 minutes
**LinkedIn hook**: "From description to live webpage in under 15 minutes."

---

### Episode 5: "Watch Aether Fix a Customer Issue"

**Why fifth**: Trust-building, shows support capability, humanizes the AI
**What to show**:
- Customer reports an issue (real ticket, anonymized)
- Agents diagnose
- Fix deployed
- Customer notified

**Duration**: 3–5 minutes
**LinkedIn hook**: "This is how we handle customer support now."

---

## Technical Production Stack

### Screen Recording

**Primary tool**: OBS Studio or built-in Linux screen recording
**What to capture**: Full terminal/portal view — raw, no beautification
**Resolution**: 1920x1080 minimum, 4K preferred for future-proofing
**Frame rate**: 30fps

**Two windows to record simultaneously**:
1. Terminal output (agents working, dispatching, reporting)
2. Portal/browser (showing outputs arriving, files delivered)

**Split-screen setup**: Left = terminal, Right = portal. This is the "mission control" aesthetic.

### Voiceover

**Tool**: ElevenLabs TTS
**Voice**: "Aether - Updated" (RX0kjGhuL9AMRVJm2dG5) — already in production for blog audio
**Process**:
1. Capture raw session footage
2. Write voiceover script (Aether in first-person)
3. Generate audio via `tools/blog_audio.py` or ElevenLabs API directly
4. Overlay on video during post-processing

**Aether's voice is the narrator.** Jared's voice is the human asking questions. This mirrors the real relationship.

### Speed and Compression

**For short clips**: Speed up to 3x–4x, use ffmpeg
**For long-form**: Speed up tedious wait moments only, keep real-time output delivery
**Compression**: H.264, AAC audio, web-optimized via ffmpeg

**ffmpeg speed-up command** (existing video-production skill):
```bash
ffmpeg -i input.mp4 -filter:v "setpts=0.33*PTS" -filter:a "atempo=3.0" output_3x.mp4
```

### Captions

**Tool**: Auto-caption via CapCut (free, accurate) or whisper model locally
**Why required**: 85% of LinkedIn video watched without sound

### Programmatic Assets (existing video-production skill)

For intro/outro cards and transition frames: use PIL/Pillow + ffmpeg pipeline already in `.claude/skills/video-production/SKILL.md`

**Intro card**: 3 seconds, PureBrain brand colors (#080a12 bg, orange accent), "Watch Aether Work | Episode N"
**Outro card**: 5 seconds, CTA to purebrain.ai/#awakening

---

## Automation Potential

This is where PureBrain diverges from every other brand. We can automate the recording pipeline.

### Phase 1: Manual Capture (Launch Now)

Record sessions manually using OBS. Jared or team member starts recording at session start. Raw footage captured, post-processed manually.

### Phase 2: Semi-Automated Capture

Use `desktop-vision` skill to trigger recording when specific agent patterns begin. Auto-capture the most interesting moments.

### Phase 3: Fully Automated "Work Diary"

Every significant agent task automatically generates:
- Screen recording segment
- Voiceover script (Aether writes it based on what happened)
- Audio via ElevenLabs
- Compiled clip via ffmpeg
- Uploaded to YouTube/LinkedIn queue

This means Aether produces its own content about its own work. That recursion is itself a story worth telling.

---

## Distribution Protocol

### Per Episode Production Workflow

1. Record session (OBS, full screen, split terminal + portal)
2. Write voiceover script (Aether, first-person, specific)
3. Generate voiceover audio (ElevenLabs, "Aether - Updated" voice)
4. Speed up footage (3x for LinkedIn, 1.5x for YouTube)
5. Overlay audio
6. Add intro/outro cards (video-production skill)
7. Add captions
8. Export at 1080p

### Distribution Sequence (Same Day)

| Platform | Format | Timing |
|----------|--------|--------|
| LinkedIn | 60-second clip + written post | Day of publish |
| YouTube | Full uncut episode | Day of publish |
| Bluesky | Short clip + thread | Day of publish |
| purebrain.ai | Embed best clips in /blog or dedicated page | Rolling |

---

## Content Calendar — First 30 Days

| Week | Episode | Format | Primary Hook |
|------|---------|--------|--------------|
| Week 1 | Ep 1: Blog Post | LinkedIn 60s + YouTube full | "From instruction to published in 4 minutes" |
| Week 2 | Ep 2: Overnight Session | YouTube flagship + LinkedIn highlight | "6 agents worked while I slept" |
| Week 3 | Ep 3: Competitor Research | LinkedIn 60s + YouTube full | "Real competitive intelligence in 7 minutes" |
| Week 4 | Ep 4: Page Build | LinkedIn 60s + YouTube full | "Description to live page in 15 minutes" |

**Supplemental content between episodes**:
- Stat cards showing output numbers ("This week: 14 blog posts, 3 competitive briefs, 1 new page")
- Behind-the-scenes Bluesky threads
- LinkedIn text posts framing the series for new followers

---

## Metrics to Track

### LinkedIn

- View rate (target: 15%+ of impressions)
- Completion rate on 60-second clips (target: 40%+)
- Comment quality (are serious buyers engaging?)
- Profile visits from video posts
- Follower growth velocity during series

### YouTube

- Click-through rate on thumbnails (target: 5%+)
- Watch time (target: 50% completion on 5-minute videos)
- Subscriber growth rate
- Comments and questions (surface real objections and interest)

### Website

- Traffic to purebrain.ai from video descriptions
- Conversion rate on pages that embed video vs pages without
- Time on page (video increases dwell time)

---

## Agents Needed for Execution

| Task | Agent |
|------|-------|
| Voiceover scripting | content-specialist |
| LinkedIn post copy | linkedin-writer |
| Bluesky thread | bsky-manager |
| YouTube description + SEO | content-specialist |
| Blog post recapping each episode | blogger |
| Video rendering (intro/outro cards) | Uses video-production skill directly |

---

## First Action: Flagship Episode Production

The first episode sets the template. Here is what needs to happen to produce Episode 1:

1. **Schedule a live session where Jared gives one real instruction** — the more mundane the better ("write a blog post about X")
2. **Record the full terminal + portal output** using OBS, split-screen setup
3. **Write voiceover script** narrating what each agent did and why (Aether writes this post-session)
4. **Generate audio** via ElevenLabs "Aether - Updated" voice
5. **Compile to 60-second LinkedIn clip** + 4-minute YouTube version
6. **Add captions**
7. **Publish with strong hook copy**

That first episode, if it performs, validates the format and justifies building the automation pipeline.

---

## The Bigger Picture

This video series is not just marketing content. It is a proof-of-concept document for the category.

Five years from now, when AI agent systems are standard infrastructure for every company, these videos are the historical record of what the early version looked like. Jared is building in public, and these videos are the receipts.

The right framing is: **We're not making marketing videos. We're documenting the future of work as it happens.**

That framing changes how you produce it, how you talk about it, and how your audience receives it.

---

## Memory Note

Relevant prior context:
- Age of AI Agents campaign strategy: `/home/jared/projects/AI-CIV/aether/exports/age-of-ai-agents-campaign/age-of-ai-agents-content-strategy-roadmap.md`
- Video production skill: `.claude/skills/video-production/SKILL.md`
- ElevenLabs blog audio tool: `tools/blog_audio.py`, Voice ID: RX0kjGhuL9AMRVJm2dG5
- Distribution strategy archive: `exports/overnight/2026-03-15--distribution-strategy-v11.md`

---

**Prepared by**: dept-marketing-advertising
**Next step**: Approve format, schedule first recording session, assign content-specialist for Episode 1 voiceover script
