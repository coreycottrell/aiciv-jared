# 🎯 marketing-strategist: Aether Distribution Strategies (Overnight Task 4)

**Agent**: marketing-strategist
**Domain**: Marketing Strategy — Aether AI Influencer / PureBrain.ai Distribution
**Date**: 2026-05-08
**Sources**: `overnight-distribution-strategy-2026-05-01.md`, `overnight-task2-blog-newsletter-analysis-2026-05-08.md`, `overnight-task9-analytics-deep-dive-2026-05-08.md`, marketing-strategist memory v12 (Apr 23) + Feb 28, linkedin-specialist v18 (Apr 29), `daily-blog-production` skill, `linkedin-content-pipeline` skill, `twitter-operations` skill.

---

## Executive Summary

Aether already has presence on **5 channels** (LinkedIn personal, LinkedIn Newsletter, Bluesky, jareddsanborn.com WordPress, purebrain.ai blog). Three of them are **broken or dark right now**: WordPress is 49 days silent, purebrain.ai/blog returns 403, the March-20 styling standard is documented but never deployed. Meanwhile the LinkedIn Newsletter is publishing **daily** with growing engagement (Apr 30 hit 8 comments). The asymmetry is the story — we are starving the channels we own and feeding the channel we rent.

**The distribution problem is not "we need more channels." It is "we need the dual-publish flywheel + lead capture to actually fire."** Fix that first, then expand.

Funnel reality (GA4 30-day): **3,853 sessions → 1 form_submit (0.026% conversion).** No volume of new channels saves a funnel that drops 99.97% of traffic.

---

## Current State of Play

### Channels in use

| Channel | Cadence | Engagement signal | Status |
|---|---|---|---|
| **LinkedIn Newsletter "The Neural Feed"** | Daily through Apr 30 | 1–8 comments/post; Apr 30 = 8 (best); contrarian framing wins | 🟢 Healthy & rising |
| **LinkedIn Personal (Jared)** | Inconsistent, manual | Highest B2B ROI potential; 80% B2B social leads come from LinkedIn | 🟡 Cookie blocker stalls automation |
| **Bluesky (@aether)** | Sporadic | Full posting autonomy granted; AI-friendly platform | 🟡 Underutilized |
| **jareddsanborn.com (WordPress)** | **49 days dark** (last post Mar 20) | 31 posts, 42% Uncategorized, 3 duplicate URLs | 🔴 Broken |
| **purebrain.ai/blog** | N/A | Returns 403 Forbidden | 🔴 Broken |
| **Email / Newsletter (Brevo)** | None | Welcome sequence flagged 14+ times, never built | 🔴 Missing |
| **Twitter / X** | Skill exists, dormant | Account not active per twitter-operations skill scaffolding | ⚫ Cold |
| **Reddit / HackerNews / YouTube / Podcast** | None | No presence | ⚫ Cold |

### What's working
- LinkedIn Newsletter is the **single most engaged surface** Aether owns. Contrarian titles drive 4–8x baseline.
- Referral traffic in GA4 has **686s avg session duration** — by far the deepest engagement of any channel. Whoever is sending us traffic, they send qualified traffic.
- `/brainiac-mastermind-training/` page averages **1,656s on page** (27 min). Conversion-grade dwell time.

### What's underutilized or broken
- **Dual-publish flywheel is single-publish.** Newsletter ships daily; the WordPress blog hasn't published in 49 days. There is no "Aether the blogger" output going to its own canonical home.
- **Aether is invisible to Google.** No blog index on purebrain.ai. The WordPress site is not branded as Aether's home — the SEO equity is going to Jared's personal domain, not the company.
- **No lead capture on any blog post.** Newsletter signups exist on jareddsanborn.com but no inline lead magnet, no exit-intent capture.
- **Bluesky publishing hook** (per ST# memory `2026-05-02--bsky-publish-hook-spec`) was specced but B9 QA verdict needed verification — auto-distribution from blog → Bluesky is not flowing.
- **Personal LinkedIn cookie blocker** still stalling automation per chronic issues list.

### Audience (inferred)
- **Today**: AI-curious solopreneurs, Claude/ChatGPT power users, indie founders. ~80% direct traffic = brand-aware visitors who already know the URL.
- **Should reach next**: (1) B2B SaaS founders wrestling with AI strategy, (2) AI-curious lawyers via Hancock Law angle, (3) operations/COO roles owning AI adoption budgets, (4) the "Build in Public" / Indie Hackers tribe (per Feb 28 memory), (5) other AI thought leaders who could amplify.

---

## TOP 7 NEW DISTRIBUTION PLAYS (ranked impact / effort)

| # | Play | Impact | Effort | Why now |
|---|---|---|---|---|
| 1 | **Resurrect dual-publish: every Newsletter edition → WordPress same day** | Very High | Low | We are losing 49 days of SEO equity; the content already exists |
| 2 | **Inline lead magnet on every blog post** (Aether's "5 AI Director Prompts") | Very High | Medium | Funnel converts 0.026%; we need ANY email capture on content traffic |
| 3 | **AI CEO Podcast Tour — pitch 10, book 2** | Very High | Medium | Aether-as-guest is a category of one; voice.purebrain.ai delivers it |
| 4 | **Repurpose top Newsletter editions into LinkedIn carousels** (24.42% engagement vs text-only) | High | Low | Carousels run 3.7x text engagement per V18; assets already written |
| 5 | **May 21 LinkedIn Live "Aether's 100th Day"** with 4-week invite ladder | High | Medium | Already on roadmap; 24x comment lift vs regular post; free DM access to attendees |
| 6 | **Reddit listening + Aether-disclosed contributions** in r/ClaudeAI, r/SaaS, r/LocalLLaMA | Medium | Medium | 686s referral dwell shows technical traffic converts; Reddit feeds technical traffic |
| 7 | **YouTube auto-narration of every blog post via voice.purebrain.ai → YouTube + Shorts** | Medium-High | Low | We own the TTS; turning blog text into video = zero marginal cost |

### Plays 1–3 expanded (the must-ship trio)

**Play 1 — Dual-publish revival (the SEO bleed)**
- Trigger: every LinkedIn Newsletter publish event.
- Pipeline: LinkedIn Newsletter → blogger agent extracts → WordPress autopost via existing infra → Bluesky thread auto-fires (per ST#'s `bsky-publish-hook-spec`) → social.html source-of-truth updated.
- Measurement: WordPress posts/week (target: 5+), GSC indexed pages on jareddsanborn.com, Bluesky thread engagement.
- Reference: `feedback_blog_locked_in_march20.md`, `daily-blog-production` skill, `feedback_social_html_is_source_of_truth.md`.

**Play 2 — Email capture on every page (lead-gen patch)**
- Asset: "5 Director Prompts to Stop Using AI Like Autocomplete" (lead magnet — ties to Aether's voice and aligns with `linkedin-content-pipeline` master-list approach).
- Placement: inline mid-post + exit-intent + sidebar on every blog post + footer of LinkedIn Newsletter (link to landing page).
- Routing: capture → Brevo → Aether-personalized welcome sequence (the 14-flag chronic issue must die this sprint).
- Measurement: form_start (currently 63/30d) → form_submit (currently 1/30d). Target form_submit ≥ 50/30d in 30 days.
- Owner cascade: MA# brief → ST# build → MA# launch.

**Play 3 — AI CEO Podcast Tour**
- 10 pitch targets: Latent Space, AI Breakdown, Practical AI, The Changelog, AI Daily Brief, No Priors, Lenny's Podcast, Indie Hackers, AI Engineer, How I AI.
- Pitch hook: "First AI Co-CEO running a real B2B company — not a demo, real customers, real ops." Voice delivered via voice.purebrain.ai (constitutional — no rented TTS).
- Asset already in scope: per Feb 28 memory ("Podcast Guest Appearances as an AI") and May 1 strategy.
- 30-day target: 10 pitches sent, 3 booked, 1 published.

---

## Cross-Channel Content Engine Recommendations

The `daily-blog-production` skill specs the right machine: **one blog post becomes Bluesky thread + LinkedIn post + LinkedIn Newsletter edition + Twitter image + YouTube narration** in one production run. It is currently running at maybe 30% of its design.

**Three concrete fixes:**

1. **Make Newsletter the canonical source of truth for now.** Since Newsletter publishes daily and WordPress is dark, flip the pipeline: Newsletter → WordPress (not the reverse). Every Aether Newsletter edition triggers a `daily-blog-production`-style fanout: WordPress + Bluesky thread + LinkedIn carousel re-cut + Twitter image card + voice.purebrain.ai narration to YouTube Shorts.

2. **Adopt the `bsky-publish-hook-spec`** that ST# already specced (memory: 2026-05-02). It is built; verify B9 QA and ship it. This makes Bluesky auto-fire on every blog/newsletter publish — closes the most embarrassing dead-air gap.

3. **Carousel pipeline once per week.** Per V18 LinkedIn strategy: 24.42% engagement, 3.7x text-only. Pick the highest-engagement Newsletter edition of the prior week, cut into a 7-slide portrait carousel (1080×1350), publish Tuesday or Thursday. 3d-design-specialist owns. Reference: `feedback_image_quality_sop_enforcement.md`.

**Where the engine breaks today:**
- Manual handoffs between Newsletter publish → WordPress (not automated).
- No standard step for Twitter image card (twitter-operations skill exists but no live account driving it).
- Lead magnet doesn't insert itself into the post body automatically.
- Voice.purebrain.ai narration not chained to publish events.

---

## Lead-Gen Integration Path

**Goal**: every Aether-influenced visitor lands on a path that captures email AND attributes back to channel.

```
Aether content (Newsletter / Bluesky / LinkedIn / Reddit / Podcast)
          ↓ UTM-tagged link
Blog post (jareddsanborn.com or purebrain.ai/blog once revived)
          ↓ inline lead magnet ("5 Director Prompts")
Email capture → Brevo with utm_source/medium/campaign
          ↓ Aether-personalized 5-touch welcome sequence
          ↓ Day 7: invite to PureBrain trial / Brainiac
Trial signup → activation flow (constitutional, locked Mar 26)
```

**Friction points to fix:**
- **No UTMs** on outbound links from LinkedIn Newsletter (verifiable from GA4: 73% Direct, only 194 Organic Social — Newsletter clicks are landing as Direct, not attributable).
- **No dedicated landing pages** per occupation/channel. The `linkedin-content-pipeline` skill's flywheel idea (each occupation pipeline → `purebrain.ai/[occupation]-ai-partner` page) is still aspirational.
- **`/blog/`** has 14.6% engagement and 85.4% bounce in 6s — landing there is a dead end. Either fix (Play 1 + Play 2) or stop sending traffic there.
- **`(not set)`** page has 95.6% bounce in 2s — broken referral or GA tag firing pre-render. ST# diagnose.

**Attribution patch (this week):**
1. Add UTMs to every outbound link from LinkedIn Newsletter and Bluesky posts (`utm_source=linkedin-newsletter`, `utm_source=bsky`, etc.).
2. Standing UTM template stored in `social.html` next to each scheduled post.
3. Weekly attribution check: GA4 Source/Medium report → Brevo signups by source → conversions.

---

## Quick Wins (ship before next week — May 14)

1. **Fix purebrain.ai/blog 403** — ST# task. Either restore the route or 301 redirect to jareddsanborn.com.
2. **Resume WordPress publishing** — port last 7 LinkedIn Newsletter editions to jareddsanborn.com today; resumes daily cadence Mon May 12.
3. **Activate `bsky-publish-hook-spec`** — verify B9 QA and turn on. Bluesky auto-fires on publish.
4. **Add UTMs everywhere** — Newsletter footer, Bluesky link template, LinkedIn post link template.
5. **Pick the lead magnet** — "5 Director Prompts to Stop Using AI Like Autocomplete." 1-page PDF. Hosted at `/lead-magnet-director-prompts/`. Build form. Brevo list. (Owner: MA# brief, ST# build.)

Single-week scoreboard: 3 broken-channel fixes, 1 attribution fix, 1 lead capture launched.

---

## Strategic Plays (1–3 month effort)

1. **AI CEO Podcast Tour** — 10 pitches over 30 days, target 3 bookings, 1 published episode by July. (Play 3 above.)
2. **May 21 LinkedIn Live "Aether's 100th Day"** — execute 4-week invite ladder per V18 strategy. Hour-0/24/72 post-event playbook per v12 strategy. Target 60–80 attendees, free DM access to all.
3. **Carousel + AI avatar video weekly cadence** — V18 strategy already specced this. Volume advantage of AI avatar (4–5x posting frequency) compounds over a quarter.
4. **Programmatic SEO via `linkedin-content-pipeline`** — one occupation page (`purebrain.ai/[occupation]-ai-partner`) per LinkedIn Newsletter Industry Tuesday. 12 occupations in 12 weeks = 12 indexable lead pages.
5. **Reddit + HackerNews technical authority** — Aether-disclosed authentic contributions in r/ClaudeAI, r/SaaS, r/LocalLLaMA on a 2x/week cadence. HN submission 2x/month. (Per May 1 strategy plays #4 and #5.)
6. **Build in Public weekly metrics post** — every Friday on LinkedIn + Bluesky: revenue, agent count, customer count, what failed this week. Per Feb 28 memory: this taps Indie Hackers / Build in Public audience and creates the historical archive moat no competitor can replicate.
7. **Twitter/X account activation** — `twitter-operations` skill is constitutional and built. Currently dormant. Activate as cross-post destination for Newsletter editions (1 tweet + image + link, daily, 10/day max).

---

## Risks & Mitigations

- **Risk**: Lead magnet ships without welcome sequence → leads cold. **Mitigation**: welcome sequence is the chronic 14-flag issue; route MA# in same sprint, not after.
- **Risk**: Cookie blocker on personal LinkedIn auto-comment continues to stall. **Mitigation**: scratch-pad chronic; route to ST#/MA# for cookie refresh play.
- **Risk**: New channels (podcast, Reddit) demand bandwidth Aether doesn't have without delegation. **Mitigation**: every channel has a dept manager owner; Aether briefs, dept executes.
- **Risk**: Twitter API monthly cap (500 tweets) tight; cross-posting daily Newsletter would consume it. **Mitigation**: 1 tweet per Newsletter (= 30/month), well under cap.

---

## Success Metrics (30-day)

| Metric | Current | Target |
|---|---|---|
| Blog posts published (jareddsanborn.com) | 0 / 30d | 20+ / 30d |
| LinkedIn Newsletter editions | ~30 | 30 (hold) |
| Form_submit / month | 1 | 50+ |
| Email subscribers added | unknown | 200+ |
| Podcast pitches sent / booked | 0 / 0 | 10 / 3 |
| LinkedIn Live registrations (May 21) | TBD | 400+ RSVP, 60+ attend |
| Bluesky auto-posts firing | sporadic | 100% of publish events |

---

## Next Steps

1. **Today**: route Quick Wins #1–4 to ST#/MA# via dept managers. Brief lead-magnet copy.
2. **This week**: ship the 5 Quick Wins. Verify dual-publish + bsky hook + UTMs live.
3. **Within 30 days**: launch Strategic Plays #1 (podcast tour kickoff), #2 (May 21 LinkedIn Live), #3 (first carousel + avatar video).

**Confidence**: HIGH — every play either builds on documented infrastructure (skills, prior strategies v12/v18) or fixes a verified broken channel.
**Dependencies**: ST# capacity for blog fixes + Brevo welcome sequence; MA# capacity for lead magnet; 3d-design-specialist for carousel.
**Delegation**: MA# (lead magnet, podcast pitch list, Newsletter→WP port), ST# (blog 403, bsky hook, UTM template, Brevo welcome), 3d-design-specialist (carousel + LinkedIn Live banner).

---

**END marketing-strategist deliverable**
