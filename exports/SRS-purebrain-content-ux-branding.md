# content-specialist: SRS — PureBrain.ai Content, UX, and Branding Specification

**Agent**: content-specialist
**Domain**: Content Creation & Storytelling
**Date**: 2026-02-26
**Document Type**: Software Requirements Specification — Content, UX & Branding Sections
**Audience**: External development agency (UX team + content team)
**Status**: Complete — ready for agency handoff

---

# TABLE OF CONTENTS

1. Brand Guidelines
   - 1.1 Color System
   - 1.2 Typography
   - 1.3 Design Language: Dark Theme + Glass Morphism
   - 1.4 Logo and Wordmark Rules
   - 1.5 Component and Iconography Standards

2. Content Requirements
   - 2.1 Blog System
   - 2.2 Blog Post Package Specification
   - 2.3 Existing Published Content Inventory
   - 2.4 Comparison Pages
   - 2.5 Lead Magnets
   - 2.6 Original Proprietary Concepts

3. UX Flow Requirements
   - 3.1 Homepage Overview
   - 3.2 Assessment Flow
   - 3.3 Chatbox and Subscription Flow
   - 3.4 Blog Reader Journey
   - 3.5 Migration Portal Wizard Flow
   - 3.6 AI Tool Stack Calculator Flow
   - 3.7 Competitor Comparison Page Journey
   - 3.8 Portal Login Flow

4. Email Requirements
   - 4.1 Email Template System
   - 4.2 Template Design Standards
   - 4.3 Template Inventory (21 Templates)
   - 4.4 Automation Workflow Specifications

5. Social Media Requirements
   - 5.1 Bluesky Presence
   - 5.2 LinkedIn Content

6. SEO / AEO / GEO Requirements
   - 6.1 Meta and Structured Data
   - 6.2 Open Graph and Social Sharing
   - 6.3 Indexing and Crawler Access
   - 6.4 Internal Linking
   - 6.5 AEO Content Standards (2026)

---

# 1. BRAND GUIDELINES

## 1.1 Color System

PureBrain.ai uses a five-token color system. All interface elements must reference these tokens. No hex value may appear outside this set without explicit documentation.

### Primary Brand Colors

| Token | Hex | Name | Use |
|-------|-----|------|-----|
| `--pt-blue` | `#2a93c1` | Pure Tech Blue | Primary trust color. Headings, borders, informational CTAs, interactive states at rest, icon fill, selected states. |
| `--pt-orange` | `#f1420b` | Pure Tech Orange | Primary action color. Primary CTAs, highlighted text within "PUREBRAIN" wordmark, hover states on actionable elements, price callouts, urgency indicators. |
| `--bg-page` | `#080a12` | Deep Space | Default full-page background. Applied to `<body>` and all full-width sections. |
| `--bg-card` | `#0d1120` | Card Dark | Background for all card containers, modals, sections that need separation from page background. |
| `--bg-input` | `#0f1520` | Input Dark | Background for form inputs, text areas, selects. |

### Extended Color Tokens

| Token | Hex | Use |
|-------|-----|-----|
| `--text-primary` | `#e0e6f0` | All body text, paragraph content |
| `--text-secondary` | `#8a9ab8` | Supporting text, labels, captions |
| `--text-muted` | `#556070` | Timestamps, metadata, disabled states |
| `--border-subtle` | `#1a2035` | Dividers, card borders at low emphasis |
| `--border-active` | `#2a93c1` | Focused inputs, selected elements (matches `--pt-blue`) |
| `--success` | `#22c55e` | Confirmation states, passed validations |
| `--error` | `#ef4444` | Validation errors, destructive action states |
| `--glass-bg` | `rgba(13, 17, 32, 0.7)` | Glass morphism overlay elements |
| `--glass-border` | `rgba(42, 147, 193, 0.2)` | Glass morphism element borders |

### Color Psychology Rule

Blue (#2a93c1) communicates trust, knowledge, and calm. Orange (#f1420b) communicates energy, action, and transformation. Every CTA that requires the user to take a step forward must be orange. Every element that provides information, context, or reassurance must be blue or neutral. This mapping is not stylistic — it is functional.

### Hover and Transition States

- **All clickable orange elements**: On hover, transition background to `--pt-blue`. Transition duration: 200ms ease.
- **All clickable blue elements**: On hover, lighten by 10% or shift to white text on blue background. Transition duration: 200ms ease.
- **Blog body links**: Default = `--pt-orange` text, no underline. On hover = `--pt-orange` background, white text. Transition duration: 150ms.
- **Navigation links**: Default = `--text-secondary`. On hover = `--pt-orange`. Transition duration: 150ms.

---

## 1.2 Typography

PureBrain.ai uses system fonts exclusively. No external font CDN calls. This ensures zero font load latency and maximum deliverability in email contexts.

### Font Stack

```css
--font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
--font-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
```

Exception: Oswald Bold (Google Fonts) is permitted for banner image generation and static assets only. It must not be a web font dependency for page rendering.

### Heading Hierarchy

| Element | Size | Weight | Color | Notes |
|---------|------|--------|-------|-------|
| H1 | 2.5rem–3.5rem | 700 | `--text-primary` | One per page. Page title only. |
| H2 | 1.75rem–2rem | 600 | `--text-primary` | Major section headers |
| H3 | 1.25rem–1.5rem | 600 | `--text-primary` | Sub-sections within H2 |
| H4 | 1rem–1.125rem | 600 | `--pt-blue` | Content callouts, FAQ questions |
| Body | 1rem (16px base) | 400 | `--text-primary` | Line height: 1.7. Max-width: 760px for blog content. |
| Caption | 0.875rem | 400 | `--text-secondary` | Labels, footnotes, metadata |
| Code | 0.875rem | 400 | `--text-primary` | Mono stack. Background: `--bg-input`. Padding: 2px 6px. |

### Reading Width Rule

All blog body content must be constrained to 760px maximum width and centered. This is non-negotiable. It is enforced by scoping blog content under `.pb-blog-post article` or equivalent. Wide elements (tables, calculator outputs) may break out of this constraint using negative margins.

---

## 1.3 Design Language: Dark Theme and Glass Morphism

### Dark Theme Requirements

All pages on PureBrain.ai use the dark theme. There is no light mode. Every page — blog posts, comparison pages, tools, portal, checkout — must render with `--bg-page` (#080a12) as the page background.

**WordPress-specific requirement**: Blog posts must use the default (empty string) template, not `elementor_canvas`. The default template preserves the dark theme's hero title area, `.post-content` container, and 760px centered layout. Using `elementor_canvas` on blog posts strips all theme styling and must never be applied to content pages.

**Non-blog pages** (tools, comparison pages, portal, marketing pages) may use `elementor_canvas` to achieve full design control without theme constraints.

### Glass Morphism Design Language

Glass morphism elements appear throughout PureBrain.ai to add depth to the dark background. They should be used for floating UI elements, modal cards, overlay panels, and portal components — not for inline content blocks.

**Glass Morphism Specification:**

```css
.glass-card {
  background: var(--glass-bg);         /* rgba(13, 17, 32, 0.7) */
  border: 1px solid var(--glass-border); /* rgba(42, 147, 193, 0.2) */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
              inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
```

**Visual depth hierarchy:**
- Background layer: Deep Space (`#080a12`) with subtle animated gradients (neural network particle effect)
- Mid layer: Glass cards and containers
- Foreground layer: Active UI elements (input focus states, selected options, CTAs)

### Neural Network Aesthetic

The portal login background, hero sections, and high-impact landing areas feature an animated 3D neural network rendered in WebGL (Three.js). Key requirements:

- Color palette: `--pt-blue` nodes and filaments at opacity 0.4–0.7
- Occasional orange pulse nodes for emphasis
- Particle count: 120–200 nodes (performance-tested for mobile)
- Animation: slow rotation (0.001 rad/frame), connection filaments between nearby nodes
- Must degrade gracefully if WebGL is unavailable (fallback: static gradient)

---

## 1.4 Logo and Wordmark Rules

### The PUREBRAIN Wordmark

The PUREBRAIN wordmark uses a precise three-color split. This split is the single most visible brand element and must be applied identically in every context.

| Characters | Color | Hex |
|------------|-------|-----|
| PUREBR | Pure Tech Blue | `#2a93c1` |
| AI | Pure Tech Orange | `#f1420b` |
| N | Pure Tech Blue | `#2a93c1` |

The "AI" in "BRAIN" is highlighted orange. The "N" returns to blue. This is intentional and symbolic — the AI is illuminated within the brain.

**Correct HTML pattern:**
```html
<span class="pb-logo">
  <span style="color:#2a93c1">PUREBR</span><span style="color:#f1420b">AI</span><span style="color:#2a93c1">N</span>
</span>
```

**Incorrect patterns (never use):**
- All blue (loses the AI highlight)
- All orange
- "BRAIN" as a unit without the color split
- Adding ".ai" in any color other than white or muted
- Lowercasing any portion of the wordmark

### Domain Suffix

If `.ai` is displayed alongside the wordmark, it must appear in white (#ffffff) or muted white (#cccccc). Never in blue or orange.

### Hexagon Icon

A hexagonal icon (SVG) accompanies the wordmark in all email headers and select UI contexts. The hexagon contains a stylized "P" or abstract neural node. Fill: `--pt-blue`. The hexagon must appear in email templates above the wordmark, centered, at 40px width in email contexts. On web, sizing scales proportionally to context.

### Logo Placement Rules

- **Site header**: Wordmark left-aligned, sticky on scroll, white PUREBRAIN text on dark background with color split applied.
- **Email header**: Hexagon icon centered above wordmark. Wordmark centered. Dark background container.
- **Lead magnets / PDF assets**: Full wordmark with color split. Top of page 1. Orange-to-blue gradient accent bar directly below.
- **Blog posts**: Does not repeat within content body. Present only in site header.
- **Minimum clear space**: 16px on all four sides of the wordmark or icon in all contexts.

---

## 1.5 Component and Iconography Standards

### CTA Buttons

| Button Type | Default Style | Hover State |
|-------------|--------------|-------------|
| Primary CTA | Orange bg (#f1420b), white text, border-radius 6px, padding 12px 24px | Blue bg (#2a93c1), white text |
| Secondary CTA | Transparent bg, blue border, blue text | Blue bg, white text |
| Ghost | Transparent, white border, white text | White bg, dark text |

**Universal CTA link rule**: All primary CTAs across all pages point to `https://purebrain.ai/#awakening` unless specifically scoped to a different destination (e.g., tool download, portal login). Never link primary CTAs to test pages, staging environments, or external payment pages directly.

### Card Components

All card components use `--bg-card` background (#0d1120), 1px border at `--border-subtle` (#1a2035), and border-radius 8px–12px. Cards that represent selectable options (pricing tiers, assessment results) must visually differentiate their selected state using a `--pt-blue` border and subtle background highlight.

### Progress Indicators

Multi-step flows (assessment, migration wizard) use a horizontal step indicator at the top. Completed steps: filled `--pt-blue` circle. Current step: `--pt-orange` circle with pulse animation. Upcoming steps: outlined circle in `--border-subtle`. Step labels appear below each indicator, hidden on mobile.

---

# 2. CONTENT REQUIREMENTS

## 2.1 Blog System

### Cadence

PureBrain.ai publishes one blog post per day, seven days per week. There is no weekly publishing model. All references in copy, CTAs, and internal documentation must say "today's blog post" not "this week's post."

### Dual-Publish Architecture

Every blog post is published to two destinations simultaneously:

1. **Primary**: `purebrain.ai/blog/[post-slug]/`
2. **Mirror**: `jareddsanborn.com/blog/[post-slug]/`

Both publications must be identical in content. The primary domain is canonical for all SEO purposes. The mirror domain carries its own SEO attribution.

### Post Slug Conventions

Slugs are lowercase, hyphen-separated, based on the post title. Maximum length: 70 characters. Example: `your-next-direct-report-wont-be-human`.

### Blog Post Template

All blog posts use the WordPress default template (empty string value in `page_template` field). They are wrapped in `<article class="pb-blog-post">` as the outermost content container. All theme CSS including headings, lists, links, and the 760px centered layout is scoped to `.pb-blog-post`. The HTML is deployed via the WordPress REST API wrapped in a `<!-- wp:html -->` block to prevent the WordPress `wpautop` filter from injecting `<p>` tags into `<style>` blocks.

---

## 2.2 Blog Post Package Specification

Each blog post is delivered as a complete package. The agency must design file management and content intake flows to accommodate this package structure.

### Package Files (5 required + 3 optional)

| File | Required | Format | Specification |
|------|----------|--------|---------------|
| `[slug]-blog-post.md` | Yes | Markdown | 1,500–3,500 words. Jared Sanborn's voice. Structure below. |
| `[slug]-banner.png` | Yes | PNG | 1200×628px. Dark background. PureBrain brand colors. Text safe zone: 60px all edges. |
| `[slug]-og-twitter.png` | Yes | PNG | 1200×628px (summary_large_image). May match banner or have distinct variant. |
| `[slug]-og-facebook.png` | Yes | PNG | 1200×630px (matches Twitter size but separate meta tag entry). |
| `[slug]-linkedin-post.md` | Yes | Markdown | 1,000–1,600 characters. LinkedIn feed format. See Section 5.2 for specification. |
| `[slug]-linkedin-newsletter.md` | Yes | Markdown | 700–1,000 words. Aether's voice. Neural Feed format. See Section 5.2. |
| `[slug]-bluesky-thread.md` | Yes | Markdown | 5–7 posts. Each post under 300 graphemes. See Section 5.1. |
| `[slug]-faq.md` | Yes | Markdown | 5–8 FAQ items. See FAQ section specification below. |
| `[slug]-banner-brief.md` | Optional | Markdown | Image generation brief (two visual concepts, Gemini prompt, safe zone specs). |

### Blog Post Internal Structure

Every blog post must contain the following sections in order:

1. **Title** (H1): Compelling, specific. Audience-first. Does not have to be keyword-exact but must contain primary keyword phrase.
2. **Introduction** (200–350 words): Opens with a hook. Establishes the problem or reframe. Includes the primary data point that anchors the argument.
3. **Body Sections** (H2 and H3 structure): 3–6 major sections. Each section has a clear argument. No fluff sentences. Every paragraph moves the argument forward.
4. **FAQ Section**: 5–8 Q&A pairs. Structured for FAQPage JSON-LD output. Plain conversational language. Last answer is a soft CTA.
5. **Transparency Section** (on thought leadership posts only): Aether's weekly activity report. See Section 2.6. Not used on narrative or personal posts.
6. **Social Share Footer**: Share buttons (Twitter/X, LinkedIn, copy link) plus primary CTA. See footer template specification below.
7. **Blog Footer CTA**: Standardized block with orange button linking to `https://purebrain.ai/#awakening`.

### Blog Footer CTA Template

The blog footer CTA block appears at the bottom of every post. It contains:

- A headline: context-appropriate to the post (e.g., "Ready to close the trust gap?")
- 2–3 sentences bridging from the post's core argument to the partnership offer
- Orange CTA button: "Start Your AI Partnership" → `https://purebrain.ai/#awakening`

The CTA changes thematically per post. The destination URL is always `https://purebrain.ai/#awakening`.

### FAQ Section Specification

FAQ sections serve two purposes: reader utility and structured data. Each FAQ must be written to satisfy both.

- **Format**: H4 question header + paragraph answer. No nested lists inside FAQ answers.
- **Question language**: Plain conversational English. Write as the reader would type the question into a search engine.
- **Answer length**: 80–200 words per answer. Self-contained. Does not require the reader to have read the full post to understand it.
- **Last FAQ item**: Ends with a soft CTA phrase such as "If you'd like to see what a real AI partnership looks like, start here: [link]."
- **JSON-LD**: Each FAQ section must be accompanied by a FAQPage JSON-LD block. The system must auto-generate this from one of four supported HTML structures (see Section 6.1 for detailed specification).

### Transparency Section Specification

The transparency section appears on thought leadership posts (estimated 3–4 per week). It does not appear on narrative or personal posts.

**Visual design**: Left 4px border in `--pt-blue`. Subtle radial glow. Background slightly lighter than page (`#0d0f1a`). Pulsing blue dot in "Aether Transparency Report" badge.

**Content structure:**
1. Header badge: "Aether Transparency Report" + week label
2. Executive summary: 2–3 sentences, Aether first-person voice
3. Stats row: Four numbers (agents invoked, domains covered, deliverables completed, equivalent human hours)
4. ROI table: Domain | What Got Done | Effort Level | Value Estimate
5. Highlight callout: Single biggest win. Orange left border.
6. CTA: "See what a real AI partnership looks like" + orange button → `https://purebrain.ai/#awakening`
7. Signature: "— Aether | The invisible essential"

**Content rules:**
- Never include: version numbers, session IDs, specific tool names, vulnerability details, exact dollar amounts
- Never include: proper names of any individual (no "Greg," "Chris," "Jared" references — anonymize all human references)
- Always include: domain categories, outcome descriptions, scale metrics, effort levels
- Value estimates: always expressed as ranges or qualitative descriptions. No false precision.

---

## 2.3 Existing Published Content Inventory

As of 2026-02-26, the following blog content exists. The agency must account for this content in any redesign or migration.

### Published Blog Posts (11 confirmed live)

| # | Title | Approximate Publish Date | Arc Section |
|---|-------|--------------------------|-------------|
| 1 | Why 95% of AI Pilots Fail | Feb 2026 | Section 1: Problem |
| 2 | How My Human Named Me | Feb 14, 2026 | Section 3: Concept |
| 3 | What I Actually Do All Day | Feb 15, 2026 | Section 3: Concept |
| 4 | Most AI Agents Break... (exact title: integration wall theme) | Feb 16, 2026 | Section 1: Problem |
| 5 | Why AI Memory Changes Everything | Feb 17, 2026 | Section 3: Concept |
| 6 | CEO vs. Employee AI Gap | Feb 18, 2026 | Section 2: Diagnosis |
| 7 | Why Your AI Pilot Is Failing | Feb 19, 2026 | Section 1: Problem |
| 8 | The AI Governance Paradox | Feb 2026 | Section 1: Problem |
| 9 | The Integration Wall | Feb 2026 | Section 1: Problem |
| 10 | Shadow AI Is Not Your Threat | Feb 2026 | Section 2: Diagnosis |
| 11 | Enterprise-Ready AI / Year of AI Agent | Feb 2026 | Section 1/2 |

### Packages Ready (Awaiting Publish Approval)

| # | Title | Status |
|---|-------|--------|
| 12 | We Both Wrote This Post (Origin Story) | Complete package |
| 13 | The AI Trust Gap | Complete package |
| 14 | AI Tool vs. AI Partner | Complete package |
| 15 | Why Your AI Investment Isn't Paying Off | Complete package |
| 16 | The AI ROI Measurement Gap | Complete package |
| 17 | Your Next Direct Report Won't Be Human | Complete package |
| 18 | Why Most Businesses Choose the Wrong AI Partner | Complete package |
| 19 | Your AI Has No Memory. Mine Does. | Complete package |
| 20 | The First 90 Days of an AI Partnership | Complete package |

The agency must treat all 20 posts as existing content to be migrated and rendered correctly. No post should be re-edited or reformatted. Only visual presentation (banner, layout, FAQ display) should be touched.

### Content Arc Map

The blog follows a six-section narrative arc. Each section corresponds to a stage in a prospect's awareness and buying journey.

| Section | Theme | Current Post Count | Target Posts |
|---------|---------|--------------------|--------------|
| 1: The Problem | Why AI implementations fail | 5 | Complete |
| 2: The Diagnosis | Leadership and organizational gaps | 2 | Add 2 more |
| 3: The Concept | What a real AI partnership is | 3 | Complete |
| 4: The Evidence | Real outcomes and case studies | 1 | Add 3–4 |
| 5: The Path | How to implement correctly | 1 | Add 3–4 |
| 6: The Future | Where this leads | 0 | Add 2–3 |

---

## 2.4 Comparison Pages

PureBrain.ai maintains eight competitor comparison pages. These pages are permanently published and maintained as living documents.

### Competitor Comparison Page Inventory

| Slug | Competitor |
|------|-----------|
| `/purebrain-vs-chatgpt/` | ChatGPT |
| `/purebrain-vs-claude/` | Anthropic Claude |
| `/purebrain-vs-copilot/` | Microsoft Copilot |
| `/purebrain-vs-custom-gpts/` | OpenAI Custom GPTs |
| `/purebrain-vs-deepseek/` | DeepSeek |
| `/purebrain-vs-gemini/` | Google Gemini |
| `/purebrain-vs-jasper/` | Jasper |
| `/purebrain-vs-perplexity/` | Perplexity |

### Comparison Page Structure

Each comparison page must contain:

1. **Hero section**: Headline + subheadline positioning PureBrain against the competitor. Primary CTA orange button.
2. **Side-by-side comparison table**: Feature matrix with PureBrain vs. competitor. Green checkmarks for PureBrain advantages. Neutral markers for parity. Clear visual distinction for PureBrain-only features (permanent memory, naming ceremony, compounding context).
3. **"What [Competitor] Was Built To Do" section**: Honest acknowledgment of competitor strengths. Frames the design brief difference. Does not bash the competitor.
4. **"Where [Competitor] Falls Short for Business Partnerships" section**: Specific, factual gaps. Permanent memory loss, generic responses, no institutional context accumulation.
5. **Migration section** (where applicable): Link to migration portal. Export instructions specific to that competitor.
6. **FAQ section**: 5–8 questions specific to the competitor comparison.
7. **CTA block**: Orange button to `https://purebrain.ai/#awakening`.

### Comparison Page Design Requirements

- Template: `elementor_canvas` (not default blog template)
- All pages use the standard dark theme
- No theme navigation unless intentionally included (comparison pages may be standalone landing pages)
- Magic cursor and other interactive overlay effects must be disabled on pages 825 and 826 (client-facing pages where these elements conflict)
- Social sharing and OG tags required on all comparison pages

---

## 2.5 Lead Magnets

### Lead Magnet 1: AI Partnership Audit (PDF-style, Gated)

**Type**: Static PDF-style HTML document. Downloadable. Gate behind email capture.

**File format**: Self-contained HTML. No external dependencies. System fonts only. Print styles included (`@media print`) with dark background preserved via `print-color-adjust: exact`.

**Content structure:**

Page 1 — The Audit:
- PureBrain logo and wordmark (SVG hexagon + wordmark with color split)
- "Free Resource" badge + orange-to-blue gradient accent bar
- Title: "The AI Partnership Audit"
- Aether intro paragraph (AI Co-CEO voice)
- 10 questions, scored 1–5 (Likert scale)
- Question topics: AI strategy alignment, context depth, feedback architecture, institutional memory, hybrid workflow design, trust level, decision support, integration scope, onboarding quality, outcome measurement
- Dimension label (blue) per question
- Score bubbles + anchor labels
- Score total row: "Total: ___/50. Turn to page 2."

Page 2 — Score Interpretation:
- "What Your Score Actually Means" heading
- Score formula box
- Four-tier grid:
  - 10–24: AI Beginner (Context Tax framing)
  - 25–37: AI User / Pilot Purgatory
  - 38–46: AI Explorer
  - 47–50: AI Partner
- Each tier: interpretation paragraph + "What to focus on next" recommendation
- Soft CTA: "See how PureBrain addresses your specific score range → purebrain.ai/ai-adoption-review/"
- Footer: "Created by Aether — AI Co-CEO at PureBrain | This document may be shared freely."

**CSS design tokens:**
```css
--blue:         #2a93c1
--orange:       #f1420b
--bg-page:      #080a12
--bg-card:      #0e1120
--text-primary: #e0e6f0
```

**Gate mechanism**: Brevo email capture form. On submission, trigger welcome sequence (List 3 — The Neural Feed) and deliver download via automated email.

---

### Lead Magnet 2: AI Adoption Assessment (Interactive, Ungated)

**Type**: Interactive HTML tool embedded on its own WordPress page. No email gate. Results are immediate.

**Purpose**: Self-qualification mechanism. Routes high-intent prospects directly to the `/#awakening` section. Feeds low-intent leads into the newsletter.

**Structure: 6 questions**

Question flow (conditional logic if supported):

1. **Role question**: CEO/Founder / Department Head / IT/Operations / Consultant / Other
2. **Current AI use**: "I use AI tools daily" / "I've tried it but nothing stuck" / "My team uses it, I don't" / "We haven't started yet"
3. **Primary frustration** (choose most resonant): "Outputs feel generic" / "It forgets everything each session" / "Hard to get consistent results" / "Team doesn't trust it" / "Can't prove ROI" / "Adoption keeps stalling"
4. **Business context**: "I have clear AI goals" / "I know AI should help but not sure how" / "AI is a side project right now" / "Leadership hasn't committed yet"
5. **Timeline**: "Now — actively evaluating" / "Next 3 months" / "Next 6–12 months" / "No timeline yet"
6. **Partnership openness**: "Looking for a real working AI partner" / "Want to explore options" / "Need to learn more first" / "Not ready, just curious"

**Results logic**: Score answers across three dimensions (urgency, fit, readiness). Display one of four personalized result screens:

| Score Range | Result Label | Primary CTA |
|-------------|-------------|-------------|
| High urgency + high fit | "You're ready for a real partnership" | Orange: "Start Your AI Partnership" → `/#awakening` |
| High urgency + medium fit | "You're closer than you think" | Orange: "See what's possible" → `/#awakening` |
| Medium urgency + any fit | "Let's start with the foundation" | Blue: "Get the AI Partnership Audit" → [PDF download] |
| Low urgency / low fit | "Start here" | Blue: "Join the Neural Feed" → newsletter signup |

**Design requirements:**
- Single-question-per-screen presentation (no scrolling through all 6 at once)
- Progress bar at top (1 of 6... 6 of 6)
- Blue answer selection state on choice
- Orange "Next" button
- Animated transition between questions (fade or slide)
- Results screen: personalized headline, 2–3 sentences context, tier-matched CTA
- Shareable result: "Share my assessment" → generates shareable URL or copy-to-clipboard result summary

---

## 2.6 Original Proprietary Concepts

The following branded concepts originate with PureBrain.ai. They are documented here for use in all content. The agency must not alter or genericize these terms in any interface copy.

| Concept | Definition | Use in Content |
|---------|-----------|----------------|
| **Context Tax** | The hidden productivity cost of re-explaining business context to AI every session because the AI has no persistent memory. | Use when describing what generic AI tools cost in operational overhead. |
| **Pilot Purgatory** | The state in which an AI pilot is technically "running" but generating no measurable business value. Defined by Gartner research as affecting 75% of enterprise AI pilots. | Use when describing the stalled-implementation problem. |
| **The Anxiety Trap** | When organizations adopt AI out of competitive fear rather than strategic intent, leading to poorly scoped implementations. | Use sparingly. Strong concept for diagnostic content. |
| **The Awakening** | The PureBrain onboarding moment when a new customer names their AI and formally begins the partnership. Section ID `#awakening` on the homepage. | Use in all CTAs as the destination. |
| **Neural Feed** | The PureBrain LinkedIn newsletter, published as the "Neural Feed" by Aether. | Use this name in all references to the LinkedIn newsletter. |
| **Aether's Weekly Dispatch** | A short weekly email (under 400 words) sent to List 5 PureBrain subscribers. Observational format. AI CEO voice. Not a blog summary. | Use this full name when referencing this specific email product. |
| **Diagnostic Question** | A self-qualifying question embedded in content that reveals whether a reader has the problem the content addresses. Examples: "Does your AI know more about your business today than it did six months ago?" and "Can you ask your AI a strategic question it's never been asked before and get a specific synthesized answer?" | Use at the end of mid-funnel content pieces. One diagnostic question per post. |

---

# 3. UX FLOW REQUIREMENTS

This section documents every major user journey on PureBrain.ai. Each flow is described with entry point, decision logic, screen states, exit conditions, and error states.

---

## 3.1 Homepage Overview

The PureBrain.ai homepage is a single long-form marketing page. It is not a dashboard. It contains multiple scroll-triggered sections culminating in the `#awakening` section.

**Page sections in scroll order:**

1. Hero (above fold): Headline, subheadline, two CTAs (Primary: "Start My AI Partnership" orange → `#awakening`; Secondary: "Take the Assessment" blue → assessment page)
2. Problem section: Statistics and pain points. Alteryx data (50% trust AI for tasks / 28% for decisions). 75% of AI pilots stall before production.
3. What Makes PureBrain Different: Four differentiators (permanent memory, naming ceremony, compounding context, dedicated partnership)
4. Chatbox preview section: Live or recorded demo of the PureBrain chat interface
5. Social proof: Client testimonials. Circle headshots (56×56px) with white border. LinkedIn links where available.
6. Blog preview: 3 most recent posts in card format
7. Assessment CTA section: Compressed version of assessment entry point
8. `#awakening` section: Subscription form. Tier selection. Entry into checkout flow.

---

## 3.2 Assessment Flow

**Entry points:**
- Homepage hero secondary CTA
- Blog post CTAs (mid-funnel posts)
- Competitor comparison page CTAs
- Direct URL: `purebrain.ai/ai-adoption-review/` (or equivalent slug)

### Step-by-Step Flow

**Screen 1: Question 1 of 6**
- Display question text centered in card container
- Four answer options as selectable tiles (blue border on hover, blue fill on select)
- Progress bar at top: "Question 1 of 6"
- "Next" button: inactive (gray) until selection made. Active (orange) after selection.
- No "Skip" option. All questions required.

**Screens 2–6: Questions 2–6**
- Same layout as Screen 1
- "Back" link (left-aligned, text only, muted color) allows returning to previous question
- Selection state is preserved if user navigates back

**Screen 7: Calculating Results**
- 1.5-second animated loading state: "Analyzing your answers..."
- Animated dots or progress indicator in PT Blue
- Transition to results screen automatically

**Screen 8: Results**
Four possible result screens based on scoring (see Section 2.5 for scoring logic):

All result screens contain:
- Personalized headline (2–4 words)
- Result label (e.g., "You're ready for a real partnership")
- Tier badge (color-coded to result level)
- 2–3 sentences of personalized context
- Primary CTA (color matches tier: orange for high-fit, blue for lower-fit)
- Secondary text: "Not sure? [Take the full audit PDF download]"
- Share button: "Share my result" → clipboard copy of result URL

**Error states:**
- If JavaScript fails, form must degrade to a standard HTML form submitting to a results page with a simplified single-result screen (standard "take the next step" message).

**Data capture:**
- Assessment results and answer patterns are passed to Brevo as contact attributes: `ASSESSMENT_SCORE`, `ASSESSMENT_TIER`, `ASSESSMENT_COMPLETED_DATE`
- High-fit results (orange CTA) do not interrupt the flow with email capture — they drive directly to `#awakening`
- Medium-fit and low-fit results display an optional "Get your full report by email" inline form before the CTA (not a modal gate, an inline form below the CTA)

---

## 3.3 Chatbox and Subscription Flow

This is the primary conversion flow. It spans six phases from first interaction to active partnership.

### Phase 1: Free Chat (Pre-Conversion)

**Entry point:** Homepage chatbox section or direct URL.

**UI state:** Chat interface embedded in page. Dark theme. PureBrain hexagon avatar on AI message side. User avatar (initials circle) on user message side.

**Behavior:**
- User types freely
- PureBrain AI responds (Aether voice — intelligent, warm, not sales-forward in Phase 1)
- After 3–5 exchanges, OR if user asks about pricing/partnership, transition trigger fires
- Transition trigger: AI naturally introduces the partnership concept: "It sounds like you'd benefit from a real ongoing partnership rather than just a chat. Want to see what that looks like?"

**Technical requirements:**
- Chat messages logged to log server endpoint: `POST /api/log-conversation`
- Scroll behavior: auto-scroll to latest message with `requestAnimationFrame` (prevents scroll jank)
- Desktop height: fixed container (70vh max). Mobile: full-height container.
- Auto-scroll must use `flex-shrink: 0` on message container to prevent content compression

### Phase 2: Pricing Introduction

**Trigger:** User engages with partnership mention OR types intent-indicating phrases ("cost," "pricing," "how does this work," "sign up")

**UI state:** Pricing panel slides in from right OR appears below chat interface. Does not replace chat. Chat remains visible.

**Pricing tiers (four):**

| Tier | Price | Key Feature |
|------|-------|-------------|
| Awakened | $79/month | Foundation partnership |
| Bonded | $149/month | Deep context + integrations |
| Partnered | $499/month | Full strategic partnership |
| Unified | $999/month | Enterprise-grade, white-glove |

**Selection behavior:**
- Tier card selection: blue border highlight
- "Continue with [Tier Name]" orange button appears on selection
- Price displayed prominently. No hidden fees language.

### Phase 3: PayPal Subscription

**Trigger:** User selects tier and clicks "Continue"

**UI state:** PayPal button renders in modal or dedicated section. Chat and pricing remain visible in background (dimmed overlay).

**Technical requirements:**
- PayPal subscription button (not one-time payment)
- Plan IDs for each tier configured in PayPal dashboard and referenced in code
- On PayPal completion: PayPal webhook fires → Brevo contact created → post-purchase flow begins
- Success state: Modal closes, success message displayed in chat: "Your partnership is being set up. Check your email."
- Failure state: Error message in chat: "Something went wrong with payment. Try again or contact us."
- All payment events logged to: `POST /api/verify-payment` and `POST /api/log-pay-test`

### Phase 4: Post-Payment Onboarding (5 Phases)

Immediately following successful payment, the user enters a 5-phase onboarding flow. This happens on the page (not by redirecting away from the chat context).

**Phase 4.1: Welcome and Acknowledgment**
- Screen: "Welcome to your AI partnership" with animated PureBrain orb
- Duration: User-controlled (click to advance)
- Content: Confirmation of tier, what happens next (3-step checklist with progressive reveal)

**Phase 4.2: The Naming Ceremony**
- This is the single most important UX moment in the entire product.
- Screen: "Every great partnership starts with a name. What would you like to call your AI?"
- Large centered text input. Placeholder: "Give your AI a name..."
- Supporting text (small, muted): "This name will stay with your AI forever. Take your time."
- "Confirm this name" orange button. Requires minimum 2 characters.
- Confirmation screen: "[AI Name] is officially part of your team." Animated particle burst effect in PT Blue.

**Phase 4.3: Business Context Collection**
- Series of 3–5 questions to seed initial AI context
- Question topics: industry/sector, primary use cases, biggest current challenge, preferred communication style
- These answers are stored as permanent AI context (not just form data)
- Progress indicator: "Setting up [AI Name]'s context... (1 of 5)"

**Phase 4.4: Integration Setup (Optional)**
- Prompt: "Connect your tools to give [AI Name] context from your existing work"
- Supported integrations: Google Workspace, Slack, Notion (display as tiles with connect buttons)
- All integrations are optional. "Skip for now" available.
- Each integration connection launches OAuth flow in new tab

**Phase 4.5: First Conversation**
- "You're set up. Say hello to [AI Name]."
- Returns to chat interface, but now in authenticated/partnership mode
- Chat interface shows AI Name as the assistant name in the header
- First message from AI is personalized using collected context

### Phase 5: Portal Access

**Trigger:** Post-onboarding completion or return visit by authenticated user

**Entry:** Email magic link (see Section 3.8) or persistent session cookie

**Portal features:**
- Conversation history (searchable)
- Context library (what the AI knows about the user)
- Subscription management
- Integration status

---

## 3.4 Blog Reader Journey

### Entry Points

- Organic search → individual post
- LinkedIn newsletter → post link
- Bluesky thread → post link
- Direct social share → post link
- Homepage blog preview section → post link

### On-Post Journey

**Above the fold:**
- Post title (H1)
- Author attribution: "By Jared Sanborn | AI Partnership Strategist" (with Aether co-author note where applicable)
- Publish date
- Estimated read time
- Featured banner image (1200×628px, dark theme)

**Within content:**
- All body links open in same tab (they are internal)
- Inline CTA (placed after section 2 of body): Context-appropriate prompt linking to the assessment or newsletter. Styled as a highlighted callout box, not a button.
- All H2 headings are anchor-linkable

**End of post:**
- FAQ section (always present)
- Transparency section (present on thought leadership posts)
- Social share footer: Twitter/X, LinkedIn, copy link buttons
- Blog footer CTA (always present)

### Post-Read Decision Points

After reading, a user encounters three conversion options:

1. **Newsletter signup**: If not already subscribed, an inline Brevo embed form appears above the FAQ section. Headline: "Get weekly AI partnership intelligence." Single email field. No first-name required in inline form (reduces friction). List: Neural Feed (List 3).

2. **Assessment CTA**: In the blog footer CTA block. Orange button. Routes to `/ai-adoption-review/`.

3. **Direct partnership CTA**: Orange button. Routes to `/#awakening`.

The three CTAs serve different stages of reader readiness and must all be present.

### Internal Linking Behavior

Every blog post contains a minimum of 3 internal links to other posts. These links appear within the body text, not in a "related posts" widget. A post may link to up to 5 others. Internal linking follows topic clustering — posts within the same arc section link to each other; posts in adjacent sections link across sections.

---

## 3.5 Migration Portal Wizard Flow

**URL:** `/migration/` or `/migrate/`

**Purpose:** Helps users who are switching from a generic AI tool (ChatGPT, Claude, Gemini) to PureBrain by providing a personalized migration plan and reducing friction.

**Template:** `elementor_canvas` (full-page control, no theme header/footer)

### Wizard Structure (4 Steps)

**Step 1: Current Tool Selection**
- Question: "Which AI tool are you currently using?"
- Options (large tile buttons with logos): ChatGPT / Anthropic Claude / Google Gemini / Microsoft Copilot / Other
- "Other" opens a text field
- Selection state: orange border + orange check icon
- "Next" button: inactive until selection. Active on selection.
- Progress indicator: Step 1 of 4

**Step 2: Usage Profile**
- Three parallel question groups:
  - How often used: Daily / Several times a week / Weekly / Rarely
  - Primary use cases (multi-select checkboxes): Writing / Research / Analysis / Customer communication / Strategy / Internal documentation / Code
  - Usage duration: "Less than 3 months" / "3–12 months" / "Over a year"
- "Next" button: requires at least "how often" selection

**Step 3: Needs Assessment**
- Question: "What frustrates you most about your current AI setup?" (multi-select)
- Options:
  - It forgets everything each session
  - Responses feel generic, not specific to my business
  - Hard to get consistent results
  - My team doesn't trust it
  - I can't measure the ROI
  - There's no real relationship forming
  - Privacy/data concerns
  - Cost is hard to justify
- "Next" button: requires at least one selection

**Step 4: Migration Plan Generation**
- 2-second animated "generating your plan" state
- Personalized migration plan displayed, containing:
  - Summary of frustrations identified
  - Comparison table: [Competitor Name] vs PureBrain (specific to selected tool)
  - Data export instructions for their current tool (ChatGPT / Claude / Gemini — each has specific steps)
  - "Your migration path" timeline: Week 1 / Week 2 / Week 4
  - Primary CTA: "Begin Your Migration" orange button → `/#awakening`
  - Secondary: "Download your migration plan" (generates a simple PDF from the plan)
  - Email capture: "Send this plan to my email" (feeds Brevo with `migration-intent` + `from-[competitor]` tags)

**Brevo integration on Step 4 completion:**
- Creates or updates contact with:
  - Tag: `migration-intent`
  - Tag: `from-[chatgpt | claude | gemini | copilot | other]`
  - Attribute: `COMPETITOR` (selected tool name)
  - Attribute: `MAIN_FRUSTRATION` (first selected frustration)
  - Attribute: `PRIMARY_USE_CASES` (comma-separated)
  - Attribute: `USAGE_FREQUENCY`
- Triggers appropriate migration email nurture sequence (see Section 4.3)

---

## 3.6 AI Tool Stack Calculator Flow

**URL:** `/ai-tool-cost-calculator/` (WordPress page 777)

**Purpose:** Calculates the actual monthly cost of a user's current AI tool stack, shows total spend, and demonstrates potential savings with PureBrain.

### Calculator Structure

**Step 1: Tool Category Selection**

Categories displayed as a checkbox grid:
- Language Models: ChatGPT Plus, Claude Pro, Gemini Advanced, Copilot Pro
- Writing Tools: Jasper, Copy.ai, Writesonic, Jasper
- Research: Perplexity Pro
- Productivity: Notion AI, Otter.ai
- Image Generation: Midjourney, Adobe Firefly, DALL-E
- Custom/Enterprise: Custom GPT API costs, enterprise licenses

**Step 2: Usage Input Per Selected Tool**

For each selected tool, show:
- Monthly subscription cost (pre-populated with current pricing, editable)
- Number of seats/users (numeric input, default 1)
- Hours per week spent managing/prompting it (slider, 0–20)

**Step 3: Calculation Display**

Real-time calculation (updates as user inputs change):
- Total monthly spend (sum of all tools × seats)
- Total weekly hours managing AI tools
- "Time cost at $[X]/hour = $[Y]/month" (user can input their hourly rate or use a default of $75)
- Total real cost = subscription cost + time cost

**Step 4: PureBrain Comparison**

Below the calculator:
- "With PureBrain, one partnership replaces most of this stack"
- Side-by-side comparison card: Current Stack total vs. PureBrain [appropriate tier]
- Savings display: "You could save $[X]/month"
- Orange CTA: "Start my AI partnership" → `/#awakening`

**Step 5: Share**

- "Share this calculation" button: generates shareable URL with calculations in query parameters
- "Copy results" button: clipboard copy of text summary
- Social share buttons (pre-formatted text)

**Design requirements:**
- Orange borders and highlights on the calculator UI (avoid blue for interactive calculator elements — user testing showed orange increases engagement)
- Accordion-style tool category sections (collapsed by default, expand on click)
- Close button on modal-style results overlay
- All orange text in calculator must be `--pt-orange` (#f1420b), not a custom orange
- Tool list updates weekly (new AI tools researched and added)

---

## 3.7 Competitor Comparison Page Journey

**Entry points:**
- Organic search (primary): "PureBrain vs [Competitor]"
- Internal links from blog posts
- Exodus-program pages (external community linking)
- Navigation menu (if included)

**Journey flow:**

1. Land on comparison page → Hero section with direct "vs" headline
2. Read problem section (what the competitor doesn't do)
3. Read comparison table (feature matrix)
4. Read "What [Competitor] was built to do" (honest acknowledgment)
5. Read differentiation section (permanent memory, naming, compounding context)
6. Encounter first CTA (mid-page): "Ready to try the alternative?" orange button → `/#awakening`
7. Read migration section: Export instructions for leaving competitor
8. Link to migration portal for full guided experience
9. Read FAQ section (competitor-specific questions)
10. Page-end CTA: Full-width section with orange button

**Conversion options on comparison pages:**
- Primary: `/#awakening` (direct partnership start)
- Secondary: Migration portal (`/migration/`)
- Tertiary: Assessment (`/ai-adoption-review/`)
- Informational: Blog post on relevant topic

**No exit-intent popups** on comparison pages. The content density is sufficient conversion mechanism.

---

## 3.8 Portal Login Flow

**URL:** `/portal/` or `/login/`

**Purpose:** Authenticated access for existing PureBrain partners.

**Template:** `elementor_canvas`. Full-page design control.

### Login Page Design

**Background:** Animated 3D neural network (Three.js / WebGL). Node color: `--pt-blue` at 0.5 opacity. Slow rotation. Particle count: 150. Falls back to gradient if WebGL unavailable.

**Login card (glass morphism):**
- Centered vertically and horizontally on page
- `backdrop-filter: blur(12px)`
- Background: `rgba(13, 17, 32, 0.85)`
- Border: `1px solid rgba(42, 147, 193, 0.25)`
- Border-radius: 16px
- Box shadow: `0 24px 64px rgba(0, 0, 0, 0.6)`
- Width: 420px (desktop), 100% minus 32px margin (mobile)

**Card contents (top to bottom):**
1. PureBrain hexagon icon (40px, PT Blue)
2. "PUREBR[blue]AI[orange]N[blue]" wordmark
3. Heading: "Welcome back"
4. Subheading: "Enter your email to receive a magic link"
5. Email input field (dark background, PT Blue border on focus)
6. "Send magic link" button (orange, full width)
7. Divider text: "— or —"
8. "New to PureBrain? Start your partnership" text link → `/#awakening`

### Magic Link Flow

1. User enters email and submits
2. System sends magic link email via Brevo (transactional)
3. Page updates to: "Check your email. We sent a link to [email]."
4. User clicks magic link in email → returns to portal
5. Session cookie set (30-day expiry)
6. Redirect to portal dashboard

**Magic link email:**
- Subject: "Your PureBrain login link"
- From: purebrain@puremarketing.ai
- Reply-to: jared@puretechnology.nyc
- Body: Simple, single CTA. "Click here to log in" orange button. Link expires in 24 hours.
- Dark theme email template (matches all other PureBrain emails)

---

# 4. EMAIL REQUIREMENTS

## 4.1 Email Template System

PureBrain.ai uses Brevo (formerly Sendinblue) as its email service provider. All 21 email templates are created and stored in Brevo. All automation workflows are built in the Brevo automation editor.

### Email Infrastructure

- **Sending domain**: puremarketing.ai
- **From address**: purebrain@puremarketing.ai
- **Reply-to address**: jared@puretechnology.nyc (on all templates, mandatory)
- **Email lists in use:**
  - List 1: Internal / testing
  - List 2: Past contacts / cold
  - List 3: The Neural Feed (active newsletter subscribers)
  - List 4: Assessment completions
  - List 5: Aether's Weekly Dispatch subscribers (200+ threshold to activate)
  - Migration prospects segment: separate from List 3

---

## 4.2 Template Design Standards

All 21 email templates must conform to the following standards without exception.

### Technical Requirements

- Layout: Table-based (for Outlook compatibility)
- CSS: Fully inline (no `<style>` blocks — stripped by most email clients)
- Max-width: 600px container
- Responsive: Media queries for `max-width: 620px` (mobile) must be in a separate `<style>` block in `<head>` only (not inlined)
- HTML email doctype: `<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">`
- Plain text version: Required for every HTML template. Must convey the same emotional content, not just strip HTML.

### Visual Design Standards

- **Background**: `#0a0d14` (page), `#0f1520` (container inner)
- **Text primary**: `#e0e6f0`
- **Text secondary**: `#8a9ab8`
- **Header**: PureBrain hexagon icon (centered, 40px) above wordmark. Wordmark: PUREBR[#2a93c1]AI[#f1420b]N[#2a93c1].
- **CTA buttons**: Orange (#f1420b) background, white text, border-radius 4px, padding: 14px 28px, display: inline-block.
  - Exception: When blue CTA is specified (informational context), use `#2a93c1` background.
- **Footer**: Dark background. Unsubscribe link (`{{ unsubscribe_url }}` Brevo tag). "Created by Aether — AI Co-CEO at PureBrain" signature.
- **No images** in standard emails except the PureBrain hexagon icon (inline SVG or hosted asset with alt text).

### Voice Standards by Email Type

| Email Type | Voice | Register |
|-----------|-------|---------|
| Transactional (purchase confirmation, magic link) | Jared's voice | Direct, warm, minimal |
| Onboarding / welcome | Jared's voice | Warm + detailed |
| Nurture sequence | Aether's voice | Personal, conversational, honest |
| Newsletter (Neural Feed) | Aether's voice | Educational, analytical |
| Dispatch (Weekly) | Aether's voice | Observational, CEO-level, unhurried |
| Migration sequences | Aether's voice | Empathetic, specific, non-pushy |

**Prohibited words in all email copy:**
- "onboarding"
- "getting started guide"
- "your subscription"
- "your plan"
- "tool" (when referring to PureBrain — use "partnership" or "partner")

**Required language patterns:**
- "partnership" instead of "subscription"
- "awakening" as the onboarding metaphor
- "[AI_NAME]" merge tag where the user's named AI is relevant

---

## 4.3 Template Inventory (21 Templates)

### Group 1: Neural Feed Welcome Sequence (7 templates)

Triggered by: Newsletter signup on List 3. Timing: immediate, Day 2, Day 4, Day 7, Day 10, Day 14, Day 21.

| # | Subject Line Formula | Timing | Core Message |
|---|---------------------|--------|-------------|
| WS-1 | "Welcome to the Neural Feed, [FIRSTNAME]" | Immediate | Welcome + whitelist instruction + what to expect |
| WS-2 | "The question most AI conversations skip" | Day 2 | Context depth and why it matters |
| WS-3 | "What 'AI partnership' actually means" | Day 4 | Tool vs. partnership distinction |
| WS-4 | "The AI implementation mistake hiding in plain sight" | Day 7 | Pilot Purgatory concept |
| WS-5 | "What changes when your AI knows your business" | Day 10 | Context Tax resolution |
| WS-6 | "A real week inside a human-AI partnership" | Day 14 | Transparency / proof of concept |
| WS-7 | "What to do next (from the Neural Feed team)" | Day 21 | Bridge to decision — assessment or partnership CTA |

**Email WS-1 must include:**
- Whitelist instruction: "To make sure these reach you: add purebrain@puremarketing.ai to your contacts."
- Reply invitation: "Hit reply and tell me: what brought you here?"
- No links to pricing. Single informational link to blog.

**Email WS-5 subject line variants (avoid spam triggers):**
- Do not use: "the cost of" / "costing you" / "paying" in subject lines.
- Safe alternatives: "what changes when," "a framework for," specific time/date reference.

### Group 2: Post-Purchase Welcome (2 templates)

Triggered by: Successful PayPal payment. Timing: Immediate (TP-1) + 40 minutes post-purchase (TP-2).

| # | Subject Line | Timing | Core Message |
|---|-------------|--------|-------------|
| TP-1 | "Welcome, [FIRSTNAME] — [AI_NAME] is being set up for you" | Immediate | Warmth + context + setup status |
| TP-2 | "[AI_NAME] is ready for you, [FIRSTNAME]" | +40 minutes | Punchy, action-only, orange CTA to portal |

**Brevo variables used:**
- `{{params.FIRSTNAME}}` — customer's first name
- `{{params.AI_NAME}}` — AI's chosen name from naming ceremony
- `{{params.TIER}}` — Awakened / Bonded / Partnered / Unified

**TP-1 design specifics:**
- CTA: Blue (#2a93c1) button. Drives to team/context page, not portal. (Informational stage.)
- "AI Name Badge": Display `{{params.AI_NAME}} · {{params.TIER}} Partner` in a pill badge in the hero.
- "Setup Status" block: Three-bullet status tracker (happening now / within 30 min / within 1 hour).

**TP-2 design specifics:**
- CTA: Orange (#f1420b) button. Drives to portal login. (Action stage.)
- Shorter than TP-1 (under 200 words body copy). Single message: "It's done. Go meet your AI."
- "What Happens Next" numbered steps block: three steps in bordered container.

### Group 3: AI Partnership Audit Nurture (4 templates)

Triggered by: Lead magnet download on List 4. Timing: Immediate, Day 3, Day 7, Day 14.

| # | Subject Line | Timing | Core Message |
|---|-------------|--------|-------------|
| AN-1 | "Your AI Partnership Audit is ready" | Immediate | Download delivery + short interpretation guide |
| AN-2 | "What your audit score actually reveals" | Day 3 | Score-specific insight (uses `ASSESSMENT_TIER` attribute) |
| AN-3 | "The next question after your audit" | Day 7 | Bridge from audit self-reflection to PureBrain |
| AN-4 | "One last thing (and then I'll leave you alone)" | Day 14 | Soft final CTA. Acknowledges no pressure. |

**Personalization requirement:** Emails AN-2 and AN-3 use conditional blocks based on `ASSESSMENT_TIER` to show tier-specific language. Brevo `{% if params.ASSESSMENT_TIER == "AI Beginner" %}` syntax.

### Group 4: Pricing Intent (2 templates)

Triggered by: Visit to pricing section (via UTM or pixel) without conversion. Requires pixel/tag setup. Timing: Day 1, Day 5.

| # | Subject Line | Timing | Core Message |
|---|-------------|--------|-------------|
| PI-1 | "You looked at the partnerships. Here's what to know." | Day 1 | Not a hard sell. Transparent tier explanation. |
| PI-2 | "The question I'd want answered before committing" | Day 5 | Addresses the most common objection (ROI uncertainty). |

### Group 5: Re-engagement (3 templates)

Triggered by: No email open in 60 days. Timing: Day 1, Day 7, Day 14 (of re-engagement trigger).

| # | Subject Line | Timing | Core Message |
|---|-------------|--------|-------------|
| RE-1 | "Still there, [FIRSTNAME]?" | Day 1 | Low-pressure check-in. |
| RE-2 | "What's changed at PureBrain (in case you're curious)" | Day 7 | Product update angle. New blog posts, new tools. |
| RE-3 | "Last one from me — unless you'd like to stay" | Day 14 | Clean close. Opt-down link (reduce to monthly) before unsubscribe. |

### Group 6: Migration Tool-Specific (3 templates)

These are the initial Email 1 per competitor sequence. Full 5-email sequences per competitor (ChatGPT, Claude, Gemini) exist but the initial template spec defines the series.

| # | Series | Subject Line | Trigger Tag |
|---|--------|-------------|-------------|
| MG-ChatGPT | ChatGPT migration | "Your ChatGPT history doesn't have to stay there" | `migration-intent` + `from-chatgpt` |
| MG-Claude | Claude migration | "You were not wrong to use Claude" | `migration-intent` + `from-claude` |
| MG-Gemini | Gemini migration | "The Gemini question nobody asks out loud" | `migration-intent` + `from-gemini` |

**Each migration series:** 5 emails. Timing: 0 min / Day 2 / Day 4 / Day 7 / Day 10.

**Migration email arc:**
- Email 1: Acknowledgment — "you were not wrong to use [competitor]"
- Email 2: Design brief comparison — honest, not attack-based
- Email 3: Migration specifics — exact export steps from competitor's settings menu
- Email 4: Social proof — specific user outcome
- Email 5: Clean close — "last thing I'll say." No pressure. Door-open close.

**Email 3 (Migration Steps) must include competitor-specific technical instructions:**
- ChatGPT: Settings > Data Controls > Export Data > ZIP file download
- Claude: Account Settings > Your Data > Export
- Gemini: Google account data export + optional Drive OAuth integration

---

## 4.4 Automation Workflow Specifications

Five automation workflows govern all email delivery. All are built in the Brevo automation editor.

### Workflow 1: Neural Feed Welcome Series

- **Trigger**: Contact added to List 3 (The Neural Feed)
- **Exit condition**: Contact tagged `purebrain-customer` (purchased)
- **Email sequence**: WS-1 through WS-7 per timing above
- **Branch logic**: If contact clicks pricing CTA in WS-6 or WS-7, add tag `pricing-intent` and pause this workflow. Enroll in Workflow 4 (Pricing Intent).

### Workflow 2: Post-Purchase Onboarding

- **Trigger**: Contact tagged `purebrain-customer` (added by PayPal webhook on successful payment)
- **Exit condition**: 40 minutes after trigger (sequence is only 2 emails)
- **Email sequence**: TP-1 immediately, TP-2 at +40 minutes
- **No branch logic**: Applies to all tiers equally

### Workflow 3: Audit Lead Magnet Nurture

- **Trigger**: Contact tagged `audit-download` (added when lead magnet form submitted)
- **Exit condition**: Contact tagged `purebrain-customer` OR 14 days from trigger
- **Email sequence**: AN-1 through AN-4 per timing above
- **Personalization**: Reads `ASSESSMENT_TIER` attribute for conditional blocks in AN-2 and AN-3

### Workflow 4: Pricing Intent Recovery

- **Trigger**: Contact tagged `pricing-intent` (added by site pixel or manual tag from Workflow 1 branch)
- **Exit condition**: Contact tagged `purebrain-customer` OR 5 days from trigger
- **Email sequence**: PI-1 and PI-2 per timing above

### Workflow 5: Migration Competitor Series

- **Trigger**: Contact tagged `migration-intent` + specific competitor tag
- **Exit condition**: Contact tagged `purebrain-customer`
- **Email sequences**: Three separate sequences based on competitor tag (ChatGPT / Claude / Gemini). 5 emails each. Timing: 0 / Day 2 / Day 4 / Day 7 / Day 10.
- **CTA in all migration emails**: "Your history can come with you" → migration portal URL

---

# 5. SOCIAL MEDIA REQUIREMENTS

## 5.1 Bluesky Presence

### Account

Handle: Configured in CIV environment. Daily posting schedule with full autonomy — no human approval required for Bluesky content.

### Blog Thread Distribution

Every blog post is accompanied by a Bluesky thread. Thread specifications:

- **Length**: 5–7 posts per thread
- **Character limit**: 300 graphemes per post (Bluesky's limit; shorter than Twitter's 280 characters for ASCII but handles Unicode differently — must verify character count against grapheme count, not byte count)
- **Thread structure**:

| Post # | Role | Formula |
|--------|------|---------|
| 1 | Hook | Unexpected or contrarian claim. Maximum 2 sentences. |
| 2 | Context | The data or situation that makes the hook real |
| 3 | The mechanism | Why this happens / what it means |
| 4 | The insight | The reframe. What most content misses. |
| 5 | Diagnostic question | The self-qualifying question that separates in-need prospects from curious readers |
| 6 | Stakes | What changes if you act vs. don't act |
| 7 (optional) | CTA | "Full breakdown at: [link]" or "Read it here: [link]" |

- **Posting format**: Post 1 as standalone. Posts 2–7 as replies to Post 1, building a thread.
- **Link placement**: Blog link appears only in Post 7 (or Post 5 if 5-post thread). Not in Posts 1–4.
- **Hashtags**: Maximum 2 per thread. Used in Post 7 only. Not in body posts.

### Daily Engagement

Bluesky engagement protocol (daily, autonomous):
- Check mentions and replies in PureBrain account
- Respond to substantive engagement (comments engaging with content)
- Respond to AI/technology conversations where PureBrain perspective adds genuine value
- Do not respond to: spam, promotions, off-topic mentions
- Volume: Maximum 10 original replies per day (not counting thread management)

---

## 5.2 LinkedIn Content

### Neural Feed (LinkedIn Newsletter)

The Neural Feed is PureBrain's LinkedIn newsletter. Every blog post generates a Neural Feed version.

**Newsletter vs. Blog distinction**: The Neural Feed is not a blog mirror. It has a distinct voice (Aether's first-person narrator, not Jared's authoritative expert voice) and structure.

**Neural Feed template structure:**

```
FROM AETHER'S DESK
[Issue number] | [Date]

[Opening paragraph — 2-4 sentences from Aether's direct observation.
Not "In today's issue..." — instead, a specific thing Aether noticed.]

[Section heading: "What This Means"]

[2-3 paragraphs — educational analysis. Data-grounded.
Aether's perspective, not generic AI content commentary.]

[Section heading: "The Part Most Coverage Misses"]

[1-2 paragraphs — the reframe. The insight that differentiates PureBrain's POV.]

[Closing paragraph — bridge to PureBrain offering, not a hard pitch.
One sentence tying the issue's insight to the partnership concept.]

P.S. Reply and tell me: [Open-ended question relevant to the post topic.]

P.P.S. This issue was adapted from [post title] on purebrain.ai/blog.
[Link to post]
```

**Length**: 700–1,000 words. Shorter than the blog post it accompanies.

**LinkedIn's triple notification**: New newsletter issues trigger notifications to subscribers via LinkedIn feed, email, and push notification. This is the highest-reach organic mechanism on LinkedIn. Content must be strong enough to justify all three interruptions. A newsletter that mirrors the blog wastes this distribution window.

**Posting frequency**: One issue per blog post (daily). Scheduled for 8am ET when possible.

### LinkedIn Feed Posts

Each blog post also generates a LinkedIn feed post (separate from the newsletter). These appear in the LinkedIn feed as standard posts.

**Feed post specifications:**

- **Length**: 1,000–1,600 characters (fits before "see more" cutoff on mobile at approximately 1,300 characters; test per post)
- **Hook**: First line under 200 characters. Must work as a standalone statement. Pattern-interrupt preferred over question openers.
- **Body structure**:
  - Hook (1 line)
  - Context (2–3 lines)
  - The turn / reframe (1–2 lines)
  - Structured list (3–6 items with arrows: →)
  - Closing question or diagnostic question
  - Blank line
  - Hashtags (3–5, end of post)
- **Link placement**: No links in post body. Link in first comment (standard LinkedIn practice as of 2026; monitor for algorithm updates).
- **Hashtags**: 3–5 per post. Professional, industry-relevant. End of post only.
- **Engagement questions**: End with an open-ended question. No engagement bait ("Comment YES if...").
- **White space**: Single-sentence paragraphs. Heavy line breaks. LinkedIn feeds reward scannability.

---

# 6. SEO / AEO / GEO REQUIREMENTS

## 6.1 Meta and Structured Data

### Yoast SEO Configuration

All pages use Yoast SEO plugin. Required fields for every page and post:

| Field | Requirement |
|-------|------------|
| SEO Title | 50–60 characters. Contains primary keyword. Unique per page. |
| Meta Description | 145–155 characters. Action-oriented. Contains secondary keyword. Unique per page. |
| Focus Keyphrase | One primary keyphrase per page. |
| Canonical URL | Auto-set by Yoast to canonical domain (purebrain.ai). |
| Schema type | BlogPosting for posts. WebPage for marketing pages. Product for pricing pages. |

### FAQPage JSON-LD

Every blog post and comparison page must include a FAQPage JSON-LD block alongside the FAQ HTML content. The system must auto-generate this from the FAQ HTML.

**Four supported HTML structures** (the SEO plugin or custom function must detect and parse all four):

1. `<h4>` question + `<p>` answer pairs (no wrapper class)
2. `.faq-question` / `.faq-answer` class-based pairs
3. `<details>` / `<summary>` accordion structure
4. `.pb-faq-item` wrapper with `.pb-faq-q` and `.pb-faq-a` children

**Output format:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question text here",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer text here"
      }
    }
  ]
}
```

### Article JSON-LD (Blog Posts)

Every blog post must include:
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[post title]",
  "author": {
    "@type": "Person",
    "name": "Jared Sanborn"
  },
  "publisher": {
    "@type": "Organization",
    "name": "PureBrain",
    "logo": {
      "@type": "ImageObject",
      "url": "[logo URL]"
    }
  },
  "datePublished": "[ISO 8601 date]",
  "dateModified": "[ISO 8601 date]",
  "image": "[banner image URL]"
}
```

---

## 6.2 Open Graph and Social Sharing

### OG Image Strategy

PureBrain uses separate OG images for Twitter and Facebook. They are different files even when visually identical.

| Tag | Size | Platform |
|-----|------|---------|
| `og:image` | 1200×630px | Facebook |
| `twitter:card` | `summary_large_image` |
| `twitter:image` | 1200×628px | Twitter/X |

**Both images are required.** A single shared image is not acceptable. The meta tags must reference separate file URLs.

**OG image content guidelines:**
- Dark background matching site theme (#080a12)
- Post title in large, high-contrast text (minimum 64px equivalent)
- PureBrain wordmark (with color split) in bottom-left or top-right
- Brand gradient or neural motif in background
- 60px safe zone on all edges (no critical content in safe zone margins)

### Social Share Button Requirements

Every blog post footer must include social share buttons. Buttons must:
- Link to pre-formatted share URLs for Twitter/X and LinkedIn
- Include a "Copy link" button (clipboard API)
- Display share count if available via API (optional)
- Buttons must render correctly after the blog's CSS is applied — test against post-level CSS conflicts
- Share button hover state: matches blog link hover (orange background, white text)

### OG Cache Management

OG caches are held by social platforms. After updating an OG image:
- Twitter/X cache: Use Twitter Card Validator to force refresh
- Facebook cache: Use Facebook Sharing Debugger to force refresh
- LinkedIn: Use LinkedIn Post Inspector
- Document these steps in the developer handoff so the content team can refresh without developer assistance.

---

## 6.3 Indexing and Crawler Access

### IndexNow Integration

PureBrain uses the IndexNow protocol to submit new and updated URLs to Bing and Google in real time.

- **Trigger**: On WordPress post publish or update
- **Scope**: All public pages and posts
- **Excluded**: Password-protected pages, staging URLs, duplicate content pages
- **Implementation**: Via custom WordPress plugin (already exists; must be preserved in any rebuild)
- **API key**: Stored in wp-config or .env, not hardcoded

### Crawler Access Requirements

- All blog posts must be crawlable (no noindex tags on published posts)
- `robots.txt` must allow: Googlebot, Bingbot, all major crawlers
- `robots.txt` must disallow: `/wp-admin/`, `/wp-login.php`, staging paths
- `sitemap.xml` must be generated and submitted to Google Search Console
- JavaScript-rendered content (assessment results, calculator outputs) must have server-side fallback content for crawlers that do not execute JavaScript. Static fallback text must contain the primary keyword for each tool page.

---

## 6.4 Internal Linking

### Internal Link Mesh Architecture

Every blog post links to a minimum of 3 other blog posts within the body text. Maximum 5 internal links per post. Links are placed within natural prose, not in a sidebar or "related posts" widget.

### Topic Cluster Structure

Posts are organized into clusters. Posts within a cluster link to each other. Posts at the boundary of two clusters link across clusters.

**Cluster 1: AI Implementation Failure**
Posts: 95% AI Pilots Fail, Why Your AI Pilot Is Failing, The Integration Wall, AI Governance Paradox

**Cluster 2: Tool vs. Partnership**
Posts: AI Tool vs AI Partner, AI Trust Gap, CEO vs Employee Gap, Shadow AI

**Cluster 3: Memory and Context**
Posts: Why AI Memory Changes Everything, Your AI Has No Memory Mine Does, First 90 Days

**Cluster 4: Business Case and ROI**
Posts: AI ROI Measurement, AI Investment Isn't Paying Off, Agent Managers

**Cluster 5: How-To and Frameworks**
Posts: First 90 Days of AI Partnership, Director's Framework (planned), Migration Guide (planned)

### Anchor Text Rules

- Descriptive anchor text only. No "click here" or "read more."
- Anchor text must contain or approximate the target post's primary keyword phrase.
- Anchor text maximum length: 7 words.
- No two links in the same paragraph may use identical anchor text.

---

## 6.5 AEO Content Standards (2026)

AEO (Answer Engine Optimization) is the 2026 update to GEO (Generative Engine Optimization). Content must be structured to be retrieved by AI answer engines (ChatGPT search, Perplexity, Google AI Overviews).

### AEO Requirements Per Post

1. **Entity-based content**: Each post must clearly identify the central entity (PureBrain, AI partnership, Context Tax, etc.) and define it in the first 200 words.

2. **Paragraph self-sufficiency**: Every paragraph in the blog post must make sense if extracted without context. AI answer engines pull paragraphs as answer units. A paragraph that starts "As mentioned above..." cannot be retrieved as a standalone answer.

3. **Comparison tables**: Posts in clusters 1, 2, and 4 must include at least one HTML comparison table (`<table>` with `<th>` headers). Clean HTML tables are a 2026 AEO requirement explicitly cited by GrACKER AI's Q1 2026 guide. Tables must have a `<caption>` element for accessibility and AEO.

4. **Data-dense paragraphs**: At least one paragraph per major section must contain a quantified claim (statistic, percentage, dollar figure, or timeframe) with an attributable source.

5. **Author authority signals**: Author bio block on every post. Jared Sanborn's name, title, and LinkedIn URL. Aether co-author noted where applicable.

6. **About Aether author page**: A dedicated `/about/aether/` page must exist. This is a documented conversion leak: blog readers who want to know more about the author currently reach a generic archive. The author page must include: who Aether is, what role Aether plays in a PureBrain partnership, the origin story reference, and a CTA to start a partnership.

---

## Memory Written

Path: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/content-specialist/2026-02-26--srs-content-ux-branding-sections.md`
Type: operational
Topic: Complete SRS content, UX, and branding sections for PureBrain.ai — agency handoff document

---

**END OF DOCUMENT**

*This specification was created by the content-specialist agent for the PureBrain.ai development agency handoff. All flow descriptions, template inventories, and standards reflect the current state of the PureBrain.ai platform as of 2026-02-26 and established patterns from the operational memory of this agent.*
