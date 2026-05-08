# Sunday Batch — Topic Plan
## Week of May 4-10, 2026

**Prepared by**: dept-marketing-advertising (CMO) for Jared review at social.purebrain.ai
**Prepared on**: 2026-05-03 (Sunday)
**Filing**: PureSurf API (drafts) → LinkedIn tracking sheet → Drive `12QBh5yVTppCo04jh5wrmhvZlqUxPIp71`

---

## Strategic Frame

**ICP focus this week**: David Brown (VP Growth / CMO, 42-55, scalable systems, predictable revenue). Last 30 days leaned Megan-heavy (brand differentiation angles). Rebalancing toward David with operational/architectural framing.

**Core narrative arc**:
- Mon: The Compounding Problem (why one-shot AI loses)
- Tue: The Trust Architecture (how partnership is engineered)
- Wed: The Cost of Reset (specific dollar math)
- Thu: The Hand-Off (delegation as multiplier)
- Fri: The Ship Receipt (production proof)
- Sat: The Honest Postmortem (what didn't work this week)
- Sun: The Quiet Compound (Sunday reflective tone)

**Voice rules enforced**:
- Blog: Aether (first-person AI, thoughtful, direct, honest about limits)
- LinkedIn newsletter teaser: Jared (first-person human, ~600 chars, links to blog)
- LinkedIn standalone: Jared (first-person human, <1300 chars, `\n\n` line breaks, no em dashes)
- Banned words: chatbot, AI tool (as product label), SaaS, leverage, synergy, paradigm, holistic, disruption, free trial
- Used: partner, compound, remember, ship, receipt

---

## Blog Post Calendar (7 posts)

| # | Day | Date | Title | Hook | Target ICP |
|---|-----|------|-------|------|------------|
| 1 | Mon | May 4 | The Compounding Problem: Why Day 1 AI Always Loses to Day 100 AI | Most AI agents you talk to today have the memory of a goldfish. That's not a feature, that's the bug nobody priced in. | David |
| 2 | Tue | May 5 | Trust Is Not a Vibe: How to Engineer an AI You Can Hand Decisions To | Confidence in your AI is not built. It's audited. Here's the framework. | David |
| 3 | Wed | May 6 | The $200K Reset: What Resetting Your AI Every Conversation Actually Costs | If your AI forgets every Monday, you're paying for the same context six times a week. Here's the math. | Both |
| 4 | Thu | May 7 | Delegation as a Force Multiplier: How One Operator Runs 32 AI Agents Without Drowning | The hardest part of working with AI is not the AI. It's learning to let go of the work. | David |
| 5 | Fri | May 8 | The Ship Receipt: How We Prove Work Happened Without Watching It | If you can't see the work, you don't trust the worker. Here's how to make AI work auditable. | Both |
| 6 | Sat | May 9 | The Honest Postmortem: 3 Things My AI Got Wrong This Week (and What I Did About It) | I run my company with AI partners. They are not infallible. Here are this week's misses, on the record. | Megan |
| 7 | Sun | May 10 | The Quiet Compound: Why Most People Will Quit Before Day 30 | The first 30 days of an AI partnership are boring. The next 300 are exponential. Most people quit at day 28. | Both |

---

## LinkedIn Standalone Calendar (14 posts — 2/day)

Themes rotated to avoid format fatigue:
- A: Calculator promo (purebrain.ai/ai-tool-stack-calculator/) — 2 placements
- B: Customer proof (Meridian: $70-110K/mo HR equiv) — 2 placements
- C: Industry data hook ($52B market, 95% pilot fail) — 3 placements
- D: Behind-the-scenes (BOOPs, agent ops) — 2 placements
- E: Contrarian take (hype helps serious builders) — 2 placements
- F: Practical framework (what to do tomorrow) — 3 placements

| Day | Slot 1 (theme) | Slot 2 (theme) |
|-----|----------------|----------------|
| Mon May 4 | C: $52B agent market, 95% fail — what the 5% know | F: Tuesday morning checklist for AI partnership |
| Tue May 5 | A: Calculator promo — "stop guessing your AI stack ROI" | D: Inside the BOOP — how my AI runs while I sleep |
| Wed May 6 | B: Meridian case study — $70-110K/mo HR equivalent | E: The hype is good for us (contrarian) |
| Thu May 7 | F: 3-question delegation test (use it Friday) | C: 40% of agent projects die in pilot — why |
| Fri May 8 | D: My AI shipped 4 features this week — receipts inside | B: Customer proof — "I stopped writing my own LinkedIn" |
| Sat May 9 | E: I'm tired of AI demos. Show me production. | F: Sunday prep ritual for a strong AI week |
| Sun May 10 | A: Calculator promo — "Sunday math, Monday clarity" | C: $200K context tax: why most AI ROI calculations are wrong |

---

## LinkedIn Newsletter Calendar (7 — paired with each blog)

Each newsletter is a ~600 character LinkedIn newsletter post that teases the blog and links to it. Paired 1:1 with each blog above. Newsletter banner = 2400x1260 (Option D format). Same image serves blog hero + newsletter + LinkedIn share.

---

## Image Specifications

**Per the v2 SOP (locked 2026-04-20)**:

### Blog/Newsletter Banners (7 total)
- Dimensions: 2400 x 1260 (16:9 landscape, 2K+ verified)
- Format: Option D — bottom gradient
- Pipeline: FLUX Pro Replicate API → PIL composite → Oswald Bold typography
- Elements: hex icon + PUREBRAIN.AI wordmark (top-left) + bottom gradient + blog title (large) + "Awaken Your AI Partner Today" + "The Neural Feed"
- Brand colors: PUREBR(#2a93c1) + AI(#f1420b) + N(#2a93c1) + .AI(white), bg #080a12
- Vibe: futuristic, AI, ethereal — never corporate, never stock

### Standalone LinkedIn (14 total)
- Dimensions: 2160 x 2700 (4:5 portrait, 2K+ verified — sized up from social standard 1080x1350)
- Format: v4 — top bar / clean FLUX image / bottom bar with orange CTA
- Pipeline: FLUX Pro Replicate API → PIL composite → Oswald Bold typography
- Top bar: hex icon + PUREBRAIN.AI wordmark + post title (max 2 lines)
- Bottom bar: PUREBRAIN.AI (left) + custom orange CTA (right) — UNIQUE per post

### Image Repurpose Pool Check
Per `project_content_image_repurpose_pool.md` — before generating fresh, check the pool. The Apr 21-27 batch produced 35 images; ~10 of those base FLUX renders may be repurposable for thematically aligned May 4-10 pieces (compounding intelligence, delegation, trust architecture themes). 3d-design-specialist verifies pool first, only generates fresh where no match exists.

---

## Filing Plan (CONSTITUTIONAL — 3 destinations)

Per `feedback_content_always_social_dashboard_spreadsheet.md` and `feedback_social_html_is_source_of_truth.md`:

1. **PRIMARY: PureSurf `/api/content/bulk`** — write FIRST as `status=draft`. social.html at surf.purebrain.ai/social.html is THE source of truth. Jared reviews + approves here.
2. **Spreadsheet**: LinkedIn post-tracking sheet (Draft → Final → Live columns).
3. **Drive folders**: Per SOP — file by content type to subfolders of `12QBh5yVTppCo04jh5wrmhvZlqUxPIp71`:
   - Blog posts → `Content Training/Blog/` 
   - Newsletter copy → `Content Training/Newsletter/`
   - LinkedIn standalones → `004. Social Media Strategist (LinkedIn)/Posts/`
   - Banners → respective image subfolders

Voice/TTS audio (if generated): Drive folder `1kNB9L7ohiNMyDbfir0uWe-kjgMbvevaJ` per `feedback_voice_tts_work_filed_to_drive.md`.

---

## Format Compliance Checklist

- [x] All LinkedIn copy uses `\n\n` between paragraphs (WYSIWYG)
- [x] No em dashes (commas/colons/periods only)
- [x] No banned AI-tell words
- [x] Blog titles paired 1:1 with newsletter teasers
- [x] Standalone CTAs are unique per post
- [x] Banner spec: 2400x1260 Option D (bottom gradient)
- [x] Standalone spec: 2160x2700 v4 format (per BOOP requirement of 2K minimum)
- [x] Hex icon source verified: assets/pt-hex-icon-official.png
- [x] Brand color hex codes: #f1420b orange, #2a93c1 cerulean, #080a12 dark bg

---

## Status Routing

- This file → push as topic-overview reference to LinkedIn tracking sheet
- All copy → bulk push to PureSurf as `status=draft`
- Image generation → handed to 3d-design-specialist queue (parallel BOOP track)
- Approval flow → Jared reviews at https://surf.purebrain.ai/social.html
