# AI Migration Portal — Feature Specification

**Agent**: feature-designer
**Domain**: UX Design / Feature Architecture
**Date**: 2026-02-23
**Version**: 1.0

---

## Executive Summary

The AI Migration Portal is PureBrain's answer to the #1 psychological barrier to switching AI tools: the fear of losing accumulated context. A customer switching from ChatGPT to PureBrain has spent months or years building up conversation history, custom instructions, and mental models. They feel like they are "starting over."

This portal flips that framing entirely.

"Your 847 ChatGPT conversations don't disappear. They become the foundation PureBrain builds on."

The portal lives inside PureBrain's product experience after signup. It has two components:

1. **Pre-Portal Data Collection** — Exodus landing pages collect migration intent signals before signup
2. **Migration Assistant** — Inside the portal, a guided 4-step flow connects accounts, imports data, shows PureBrain learning from the imported context, and suggests personalized first tasks

The portal is the antidote to switching cost anxiety. It transforms switching from a loss into an upgrade.

---

## Table of Contents

1. Feature Overview and User Journey
2. Pre-Portal Data Collection (Exodus Landing Pages)
3. Portal Screen Wireframes (All 4 Steps)
4. Technical Integration Matrix
5. Data Flow Diagram
6. MVP Scope vs Full Vision
7. Privacy and Security Considerations
8. Implementation Priority Order

---

## 1. Feature Overview and User Journey

### The User's Emotional Arc

```
BEFORE DISCOVERING PUREBRAIN
User is frustrated with their current AI tool.
They've tried to make it work. It hasn't.
They're googling "ChatGPT alternatives" or "better than Claude".

LANDING PAGE (Exodus Page)
They arrive at /switching-from-chatgpt/ or similar.
They see their exact frustration reflected back.
They take the quiz. It surfaces their specific pain.
Email is captured. Migration intent is recorded.
"What did you primarily use ChatGPT for?" feeds the portal.

SIGNUP
They purchase PureBrain. The post-payment chatbox asks questions.
Claude API key is collected. Profile is built.

PORTAL ARRIVAL (First Login)
They land in the portal. A prominent banner or card:
"Welcome. Let's bring your work with you."
Migration Assistant is front and center.

MIGRATION FLOW (4 Steps Inside Portal)
Step 1: Connect accounts
Step 2: Import data
Step 3: Watch PureBrain learn
Step 4: Get personalized first tasks

POST-MIGRATION
PureBrain knows them. It references their history.
First conversation feels like speaking to someone who already
understands the context.
The switching cost has been eliminated.
```

### User Journey Map

```
Exodus Page
    |
    | [Quiz answers collected, email captured]
    |
Email + Drip Sequence (Brevo)
    |
    | [Links back to purebrain.ai/#awakening]
    |
PureBrain Homepage → Awakening CTA
    |
    | [Payment complete]
    |
Post-Payment Chatbox (existing)
    |
    | [Name, role, goal, Claude API key collected]
    |
Portal — First Login
    |
    | [Migration Assistant banner visible]
    |
STEP 1: Connect Your Accounts
    |
STEP 2: What We Import (review + confirm)
    |
STEP 3: PureBrain Learns You
    |
STEP 4: Guided First Tasks
    |
Full PureBrain Experience
```

---

## 2. Pre-Portal Data Collection (Exodus Landing Pages)

### Current State

The existing exodus pages (/switching-from-chatgpt/, etc.) have a quiz. The competitor is known from the URL. Email is captured.

### Additional Data to Collect

These additions feed directly into the Migration Assistant, personalizing what gets imported and how PureBrain presents the learning phase.

#### Question Set Additions (After Current Quiz Flow)

These questions appear after the existing quiz but before the email capture gate. They should feel like natural continuation of the conversation, not a separate form.

**Question A: Primary Use Cases (Multi-select)**
"What did you use [ChatGPT/Claude/etc.] for most? Select all that apply."

Options (vary slightly by competitor):
- Writing and editing (emails, reports, proposals)
- Research and summarization
- Coding and technical help
- Image generation (if applicable)
- Brainstorming and ideation
- Customer-facing content
- Personal productivity and planning
- Data analysis
- Presentations and documents

*Why this matters*: Portal Step 4 (Guided First Tasks) uses these answers to surface relevant "Do this first with PureBrain" suggestions.

**Question B: Volume Signal**
"How often were you using it?"
- Multiple times a day (heavy user)
- Once a day
- A few times a week
- Occasionally

*Why this matters*: High-frequency users have more history worth importing. This signal triggers "Full Import Recommended" messaging in the portal. It also helps with lead scoring in Brevo.

**Question C: Custom Configuration Level**
"Had you set up any custom instructions, templates, or saved prompts?"
- Yes, I had everything customized exactly how I wanted it
- Some basic customization
- No, I used defaults

*Why this matters*: Users who answer "Yes" get emphasized messaging about the Custom Instructions import feature. This is their most painful loss — PureBrain can directly address it.

**Question D: What Frustrated You Most (Single select)**
"What finally made you look for something better?"

Options:
- Didn't remember anything between conversations
- Felt generic — like talking to a tool, not a partner
- Couldn't connect it to my other tools and workflows
- Results weren't consistent enough for professional use
- Too expensive for what I was getting
- Missing features I needed (image gen, voice, etc.)
- I wanted something specifically designed for business

*Why this matters*: This single answer personalizes the messaging throughout the migration flow. "You said it never remembered anything — here's how that changes."

#### Data Schema (What Gets Stored)

```json
{
  "source_page": "switching-from-chatgpt",
  "competitor": "chatgpt",
  "email": "user@company.com",
  "quiz_score": 24,
  "primary_use_cases": ["writing", "research", "brainstorming"],
  "usage_frequency": "multiple_times_daily",
  "had_custom_config": true,
  "main_frustration": "no_memory",
  "captured_at": "2026-02-23T14:22:00Z",
  "utm_source": "bluesky",
  "utm_campaign": "exodus-chatgpt"
}
```

This object is attached to the Brevo contact record as custom attributes, then passed to the portal on first login via the user's profile.

#### Brevo Integration

- Store `competitor`, `primary_use_cases`, `had_custom_config`, `main_frustration` as Brevo contact attributes
- Trigger a specific drip sequence based on `competitor` (ChatGPT users get ChatGPT-specific emails)
- Tag: `migration-intent`, `from-[competitor]`

---

## 3. Portal Screen Wireframes

### Portal Entry — Migration Banner

When a user logs into PureBrain for the first time (or until migration is complete), a Migration Assistant card appears prominently in the portal dashboard.

```
+----------------------------------------------------------+
|                                                          |
|   [PureBrain Logo]         [Your AI Name]   [Menu]      |
|                                                          |
+----------------------------------------------------------+
|                                                          |
|   +--------------------------------------------------+  |
|   |  WELCOME TO PUREBRAIN                            |  |
|   |                                                  |  |
|   |  You're switching from ChatGPT.                  |  |
|   |  Let's bring your work with you.                 |  |
|   |                                                  |  |
|   |  Your 6 months of context doesn't have to       |  |
|   |  disappear — it becomes PureBrain's foundation.  |  |
|   |                                                  |  |
|   |  [Start Migration ▶]     [Skip for now]          |  |
|   +--------------------------------------------------+  |
|                                                          |
|   [Rest of portal dashboard below]                      |
|                                                          |
+----------------------------------------------------------+
```

**Design notes:**
- Banner uses PureBrain dark background (#080a12) with orange accent on "Start Migration" button
- Personalized: "You're switching from [competitor]" populated from Brevo/profile data
- "Skip for now" is available but not prominent — portal nudges migration without forcing it
- After migration completes, banner is replaced by a "Migration Complete" badge + summary

---

### Step 1: Connect Your Accounts

**Screen header**: "Connect Your Accounts"
**Subtitle**: "We'll pull in the context that matters. You stay in control."

```
+----------------------------------------------------------+
|  STEP 1 OF 4                  [Progress: ●○○○]           |
|  Connect Your Accounts                                   |
+----------------------------------------------------------+
|                                                          |
|  We detected you came from ChatGPT.                      |
|  Connect below to start the import.                      |
|                                                          |
|  +----------------------------------------------------+  |
|  |  [ChatGPT Icon]  ChatGPT / OpenAI                  |  |
|  |                                                    |  |
|  |  Import: Conversation history, Custom Instructions |  |
|  |  Method: File upload (Export from Settings)        |  |
|  |                                                    |  |
|  |  [Upload conversations.zip ▲]  or  [How to export] |  |
|  +----------------------------------------------------+  |
|                                                          |
|  ALSO WANT TO BRING IN?                                  |
|                                                          |
|  +----------------+  +----------------+                 |
|  | [Notion icon]  |  | [HubSpot icon] |                 |
|  | Notion         |  | HubSpot CRM    |                 |
|  | Pages, DBs     |  | Contacts       |                 |
|  | [Connect ▶]    |  | [Connect ▶]    |                 |
|  +----------------+  +----------------+                 |
|                                                          |
|  +----------------+  +----------------+                 |
|  | [Canva icon]   |  | [Upload icon]  |                 |
|  | Canva          |  | Other Tool     |                 |
|  | Brand kit      |  | Upload CSV/JSON|                 |
|  | [Connect ▶]    |  | [Upload ▲]     |                 |
|  +----------------+  +----------------+                 |
|                                                          |
|  [Continue with what I have ▶]                          |
|                                                          |
+----------------------------------------------------------+
```

**UX Notes:**
- The detected competitor's card is shown first and expanded by default
- Other integrations are in a "Also want to bring in?" section below
- Each card shows exactly what will be imported — no surprises
- "How to export" links open a modal with step-by-step instructions, not a new tab
- "Continue with what I have" is always visible — user can proceed with partial data
- Completed integrations show a green checkmark and brief data summary ("847 conversations ready")

**Step 1 — Per-Competitor Connection Method**

| Competitor | Method | What User Sees |
|---|---|---|
| ChatGPT | File upload (ZIP from OpenAI export) | Upload button + instructions link |
| Claude | File upload (from Anthropic account settings) | Upload button + instructions link |
| Gemini | Google OAuth button | "Connect Google" button (reads Drive, Gmail context optionally) |
| Perplexity | Manual text paste OR file upload | Text area + upload fallback |
| Midjourney | Manual: describe your style | Short text form ("My Midjourney style was...") |
| Custom GPTs | File upload (GPT config JSON from OpenAI export) | Upload button + instructions |
| Notion | OAuth2 "Connect Notion" button | Standard OAuth flow |
| HubSpot | OAuth2 "Connect HubSpot" button | Standard OAuth flow |
| Canva | OAuth2 "Connect Canva" button | Standard OAuth flow |
| Other | CSV or JSON file upload | Upload button |

---

### Step 2: What We Import

**Screen header**: "Here's What We Found"
**Subtitle**: "Review what PureBrain will learn from. You can remove anything."

```
+----------------------------------------------------------+
|  STEP 2 OF 4                  [Progress: ●●○○]           |
|  Review Your Import                                      |
+----------------------------------------------------------+
|                                                          |
|  FROM CHATGPT                                            |
|  +----------------------------------------------------+  |
|  |  ✓  847 conversations                              |  |
|  |     3.2 years of history                           |  |
|  |     [Remove]                                       |  |
|  |                                                    |  |
|  |  ✓  Custom Instructions (found)                    |  |
|  |     "You are a direct, no-fluff assistant..."      |  |
|  |     [Remove]                                       |  |
|  |                                                    |  |
|  |  ✓  12 saved GPT configurations                    |  |
|  |     Writing assistant, Research agent, Code review |  |
|  |     [Remove]                                       |  |
|  +----------------------------------------------------+  |
|                                                          |
|  FROM NOTION                                             |
|  +----------------------------------------------------+  |
|  |  ✓  3 connected databases                          |  |
|  |     Projects, Team wiki, CRM                       |  |
|  |     [Remove]                                       |  |
|  |                                                    |  |
|  |  ✓  47 pages PureBrain can reference               |  |
|  |     [Remove]                                       |  |
|  +----------------------------------------------------+  |
|                                                          |
|  PRIVACY NOTE                                            |
|  Your data is never used to train any model.             |
|  It lives in your PureBrain instance only.               |
|  [See full privacy policy]                               |
|                                                          |
|  [Start Import ▶]                                        |
|                                                          |
+----------------------------------------------------------+
```

**UX Notes:**
- Every data category has a [Remove] option — user control is explicit
- Conversation history shows counts and date ranges, not individual conversations
- Custom Instructions shows a preview of the first 120 characters
- Privacy note is always visible above the CTA — trust-building at decision moment
- "Start Import" begins the processing — transitions to Step 3

---

### Step 3: PureBrain Learns You

**Screen header**: "PureBrain Is Learning From You"
**This screen is the emotional core of the migration portal.**

```
+----------------------------------------------------------+
|  STEP 3 OF 4                  [Progress: ●●●○]           |
|  PureBrain Is Learning                                   |
+----------------------------------------------------------+
|                                                          |
|  [Animated PureBrain orb — pulsing/processing state]    |
|                                                          |
|  Migration 73% complete                                  |
|  [████████████░░░░░░░]                                   |
|                                                          |
|  WHAT WE'VE LEARNED SO FAR                               |
|                                                          |
|  +----------------------------------------------------+  |
|  |  "You asked about market analysis 23 times.        |  |
|  |   We've flagged this as a core use pattern."        |  |
|  +----------------------------------------------------+  |
|                                                          |
|  +----------------------------------------------------+  |
|  |  "Your Custom Instructions say you prefer direct    |  |
|  |   answers without preamble. Noted permanently."     |  |
|  +----------------------------------------------------+  |
|                                                          |
|  +----------------------------------------------------+  |
|  |  "5 top topics identified: market strategy,         |  |
|  |   copywriting, competitive analysis,                |  |
|  |   hiring decisions, product positioning."           |  |
|  +----------------------------------------------------+  |
|                                                          |
|  BUILDING YOUR PROFILE                                   |
|  ✓ Communication style detected                          |
|  ✓ Top 5 use patterns extracted                          |
|  ✓ Custom instructions absorbed                          |
|  ◌ Knowledge base indexing... (47 Notion pages)          |
|  ◌ Brand style analysis... (Canva connection)            |
|                                                          |
|  [Estimated time: ~2 minutes]                            |
|                                                          |
+----------------------------------------------------------+
```

**UX Notes:**
- This screen is NOT a blank progress bar — it actively surfaces real-time insights as they are generated
- Insight cards animate in sequentially as processing completes each chunk
- Each insight card is written in plain language, not technical labels
- The "Building Your Profile" checklist shows completion in real time
- The animated orb connects this screen to the PureBrain brand language
- If processing takes more than 5 minutes, a "We'll email you when it's ready" option appears
- Mobile: same layout, orb is smaller, insight cards stack vertically

**Processing Architecture (What Happens Server-Side)**

The backend receives the imported data and runs an analysis pipeline:

1. **Pattern extraction**: Top N topics by conversation frequency
2. **Style extraction**: From custom instructions + message tone analysis
3. **Vocabulary extraction**: Domain-specific terms used repeatedly
4. **Entity extraction**: Companies, people, products mentioned
5. **Preference extraction**: Preferred answer format (bullet vs prose, brief vs detailed)

Output is written to the user's PureBrain profile as structured JSON. The AI partner reads this context on first conversation.

---

### Step 4: Guided First Tasks

**Screen header**: "You're Ready. Here's Where to Start."
**Subtitle**: "Based on what you used to do with [ChatGPT], here are your first moves with PureBrain."

```
+----------------------------------------------------------+
|  STEP 4 OF 4                  [Progress: ●●●●]           |
|  Your First Tasks With PureBrain                         |
+----------------------------------------------------------+
|                                                          |
|  Migration complete!                                     |
|  PureBrain has absorbed your context.                    |
|                                                          |
|  SUGGESTED BECAUSE OF YOUR HISTORY                       |
|                                                          |
|  +----------------------------------------------------+  |
|  |  [Chart icon]                                       |  |
|  |  Market Analysis                                    |  |
|  |                                                     |  |
|  |  You ran market analysis 23 times in ChatGPT.       |  |
|  |  PureBrain knows your framework now.                |  |
|  |  Ask it to run one and see the difference.          |  |
|  |                                                     |  |
|  |  [Start this task ▶]                                |  |
|  +----------------------------------------------------+  |
|                                                          |
|  +----------------------------------------------------+  |
|  |  [Pen icon]                                         |  |
|  |  Writing With Your Voice                            |  |
|  |                                                     |  |
|  |  We detected your writing style from your history.  |  |
|  |  PureBrain already writes the way you do.           |  |
|  |  Try asking it to write something.                  |  |
|  |                                                     |  |
|  |  [Start this task ▶]                                |  |
|  +----------------------------------------------------+  |
|                                                          |
|  +----------------------------------------------------+  |
|  |  [Database icon]                                    |  |
|  |  Ask About Your Notion Workspace                    |  |
|  |                                                     |  |
|  |  PureBrain can now answer questions about           |  |
|  |  your Projects database and Team wiki.              |  |
|  |  Try: "What's the status of my open projects?"      |  |
|  |                                                     |  |
|  |  [Start this task ▶]                                |  |
|  +----------------------------------------------------+  |
|                                                          |
|  [Go to my PureBrain ▶]                                  |
|                                                          |
+----------------------------------------------------------+
```

**UX Notes:**
- Tasks are generated from the combination of: use case quiz answers + extracted conversation patterns
- Each card has specific numbers from the import ("23 times", "your 3 databases")
- Tasks link directly into the chat interface with a pre-loaded starter prompt
- "Start this task" pre-fills the chat with a contextual first message, not a blank chat
- "Go to my PureBrain" goes to the main portal chat interface
- A "Migration Complete" badge is awarded and visible in the dashboard permanently

**Task Generation Logic (What Feeds Into Suggested Tasks)**

| Input Signal | What It Generates |
|---|---|
| ChatGPT: "market analysis" top topic | "Run a market analysis" starter task |
| Custom Instructions with preferred style | "Write [X] in your detected voice" |
| Notion databases connected | "Ask about your [database name]" |
| HubSpot connected | "Ask about your open deals" |
| Canva brand kit imported | "Generate a design with your brand" |
| Frustration = "no memory" | "Test long-term memory — ask about last month" |
| Use case = "coding" | "Get a code review on your current project" |

---

### Migration Complete — Dashboard Badge

After completing all 4 steps, the migration banner in the dashboard is replaced:

```
+--------------------------------------------------+
|  [Checkmark icon]  MIGRATION COMPLETE             |
|                                                  |
|  Absorbed: 847 conversations · 5 use patterns    |
|  Connected: ChatGPT, Notion                      |
|  Status: Your AI partner knows you.              |
|                                                  |
|  [View Migration Summary]                         |
+--------------------------------------------------+
```

---

## 4. Technical Integration Matrix

### Integration Feasibility by Tool

#### ChatGPT / OpenAI

| Attribute | Detail |
|---|---|
| API Availability | No direct conversation history API for consumer accounts |
| OAuth Flow | Not applicable for conversation export |
| Export Method | Manual: Settings > Data Controls > Export Data > ZIP file |
| ZIP Contents | conversations.json (full history), user.json, message_feedback.json |
| What We Parse | conversations.json — messages array, custom instructions |
| Rate Limits | N/A (file upload, not API) |
| Privacy Considerations | File is sensitive PII — must be processed and deleted from server |
| Feasibility Rating | HIGH — well-documented, predictable format |
| Fallback | Same — file upload is the primary method |

**Import Notes**: The OpenAI export ZIP contains `conversations.json` with a well-documented schema. Each conversation is an array of messages with role (user/assistant), content, and timestamp. Custom instructions are in `user.json`. This is the most valuable import for most users.

#### Claude / Anthropic

| Attribute | Detail |
|---|---|
| API Availability | No conversation history API |
| OAuth Flow | Not applicable |
| Export Method | Manual: Account Settings > Export data |
| Export Format | ZIP file with conversations in JSON |
| What We Parse | Conversation JSON similar to OpenAI format |
| Feasibility Rating | HIGH — similar to ChatGPT flow |
| Fallback | File upload |

#### Gemini / Google

| Attribute | Detail |
|---|---|
| API Availability | Google OAuth 2.0 — broad ecosystem access |
| OAuth Flow | Standard OAuth2 with Google scopes |
| Relevant Scopes | `https://www.googleapis.com/auth/drive.readonly` for Drive content |
| What We Import | Google Drive documents the user frequently references |
| Rate Limits | Google API standard limits (varies by product) |
| Important Note | No direct Gemini conversation export via API — Drive content is the value here |
| Privacy Considerations | Google OAuth grants broad access — scope carefully, request minimum necessary |
| Feasibility Rating | MEDIUM — valuable for Drive context, not conversation history |
| Fallback | Manual text description of use patterns |

#### Perplexity

| Attribute | Detail |
|---|---|
| API Availability | No public API for consumer conversation export |
| OAuth Flow | None available |
| Export Method | No built-in export (as of 2026-02-23) |
| Workaround | User manually pastes key prompts/findings they want preserved |
| Feasibility Rating | LOW — no programmatic path |
| Fallback | Text paste area: "What key things did you research with Perplexity?" |

#### Midjourney

| Attribute | Detail |
|---|---|
| API Availability | No official public API |
| OAuth Flow | No official OAuth |
| Export Method | No built-in export |
| What Has Value | Style prompts the user developed over time |
| Workaround | Short text form: "Describe your Midjourney style in your own words" |
| Example | "Cinematic, moody, wide angle, film grain, 1970s color palette" |
| Feasibility Rating | LOW for automation — MEDIUM for manual capture (high value) |
| Fallback | The style description form IS the product — treat it as a first-class feature, not fallback |

**Design insight**: Even without an API, capturing someone's Midjourney style in their own words is genuinely valuable. It goes directly into PureBrain's image generation context. Frame this form positively: "Tell us about your visual style."

#### Notion

| Attribute | Detail |
|---|---|
| API Availability | Full public API with OAuth 2.0 |
| OAuth Flow | OAuth2 — user authorizes access to their workspace |
| Token Endpoint | POST https://api.notion.com/v1/oauth/token |
| What We Can Read | Pages, databases, database entries |
| Scopes | read_content, read_user_without_email (minimum viable) |
| Rate Limits | 3 requests per second per integration |
| What We Import | Page titles and content, database schemas (not all data), selected databases |
| Privacy Considerations | OAuth must be scoped narrowly — do not import confidential records without explicit user selection |
| Feasibility Rating | HIGH — robust API, well-documented |
| Fallback | N/A — either OAuth works or user skips Notion |

**Import Notes**: The user should select WHICH databases to share, not grant blanket workspace access. Present a selection UI after OAuth: "Which Notion databases should PureBrain be able to reference?"

#### HubSpot

| Attribute | Detail |
|---|---|
| API Availability | Full public API with OAuth 2.0 |
| OAuth Flow | OAuth2 standard |
| What We Can Read | Contacts, companies, deals, activities (with `crm.objects.contacts.read` and related scopes) |
| Conversation Export | Conversations API exists but requires Super Admin and `conversations.read` scope |
| Rate Limits | 100 requests per 10 seconds (free), higher on paid |
| What We Import | Contact list structure, pipeline stage names, deal stages, company names |
| Privacy Considerations | CRM data includes third-party PII (your contacts) — must not be stored, only used for context |
| Feasibility Rating | MEDIUM-HIGH — API is robust, but scoping CRM PII carefully is critical |
| Fallback | User manually describes their sales workflow |

**Important**: CRM contact data belongs to the user's customers. PureBrain should use it for context ("You have 47 open deals") but should never store or process individual contact records beyond the session.

#### Canva

| Attribute | Detail |
|---|---|
| API Availability | Canva Connect APIs — full OAuth 2.0 with PKCE |
| OAuth Flow | Authorization URL: https://www.canva.com/api/oauth/authorize (PKCE required) |
| What We Can Read | Designs list, brand kits (colors, fonts, logos) |
| Export | Design export to PDF — 20 requests/minute limit |
| What We Import | Brand kit colors, brand fonts, logo presence indicator |
| Privacy Considerations | Low — brand kits are meant to be shared |
| Feasibility Rating | HIGH — well-documented API, clear brand kit value |
| Fallback | User uploads a brand kit PDF or manually inputs brand colors + fonts |

**Import Notes**: The primary value from Canva is the brand kit. After OAuth, extract hex color values, font names, and logo references. These feed directly into PureBrain's design generation context.

#### Generic CSV / JSON Upload (Fallback for Any Tool)

Every integration should have a CSV/JSON upload fallback:

- Prompt library: upload a CSV of prompts (columns: title, content, category)
- Contact list: upload from any CRM as CSV (columns: name, company, role, notes)
- Documents: upload PDF or text files
- Custom instructions: plain text paste

---

## 5. Data Flow Diagram

```
EXODUS LANDING PAGE
  (/switching-from-chatgpt/ etc.)
        |
        | User takes quiz
        |
        | Data collected:
        | - competitor (from URL slug)
        | - primary_use_cases (quiz Q1)
        | - usage_frequency (quiz Q2)
        | - had_custom_config (quiz Q3)
        | - main_frustration (quiz Q4)
        | - email
        |
        v
BREVO CONTACT RECORD
  (email + custom attributes)
        |
        | Trigger: migration-intent drip sequence
        | Drip emails personalized by competitor
        |
        v
PUREBRAIN.AI HOMEPAGE
  (//#awakening CTA)
        |
        | User purchases PureBrain
        |
        v
POST-PAYMENT CHATBOX (existing)
  (pay-test chatbox flow)
        |
        | Existing data collected:
        | - Full name
        | - Email (confirms Brevo match)
        | - Company + role
        | - Claude API key
        | - Primary goal
        | - Learn-more answers (working style, friction, vision)
        |
        v
PUREBRAIN USER PROFILE
  (server-side user object)
        |
        | Profile enriched with:
        | - exodus_data (from Brevo lookup by email)
        | - chatbox_data (from post-payment flow)
        |
        v
PORTAL — FIRST LOGIN
  (dashboard)
        |
        | Migration banner shown if:
        | - competitor is known from exodus_data
        | - migration_status != 'complete'
        |
        v
STEP 1: ACCOUNT CONNECTION
        |
        | File uploads → stored in encrypted temp storage
        | OAuth connections → tokens stored in secure vault
        |
        v
STEP 2: IMPORT REVIEW
        |
        | User confirms/removes data categories
        | Selection stored in migration_config
        |
        v
STEP 3: PROCESSING PIPELINE
        |
        | async jobs:
        | - parse_conversations(file) → pattern_extraction
        | - parse_custom_instructions(text) → style_profile
        | - index_notion_pages(oauth_token) → knowledge_base
        | - parse_hubspot(oauth_token) → crm_context
        | - parse_canva_brand(oauth_token) → brand_profile
        |
        | Output: user_context_profile (JSON)
        | {
        |   top_topics: [...],
        |   communication_style: {...},
        |   preferred_answer_format: "bullet|prose|mixed",
        |   domain_vocabulary: [...],
        |   brand_colors: [...],
        |   brand_fonts: [...],
        |   crm_pipeline_names: [...],
        |   conversation_count: N,
        |   date_range: { start, end }
        | }
        |
        v
STEP 4: PERSONALIZED TASKS
        |
        | Task generation reads:
        | - user_context_profile
        | - exodus_data.primary_use_cases
        | - exodus_data.main_frustration
        |
        | Outputs 3-5 starter task cards
        |
        v
PUREBRAIN AI PARTNER — FIRST CONVERSATION
        |
        | AI partner system prompt includes:
        | - user_context_profile summary
        | - detected style preferences
        | - top topic domains
        | - brand context (if available)
        |
        | First conversation feels like speaking to someone
        | who has done their homework.
```

---

## 6. MVP Scope vs Full Vision

### MVP (Phase 1 — Ship in 4-6 weeks)

The MVP proves the core value proposition: "Your ChatGPT history doesn't disappear."

**In scope:**
- ChatGPT file upload (conversations.zip → conversations.json parsing)
- Claude file upload (same parsing approach)
- Manual style description for Midjourney (short text form)
- CSV upload fallback for any other tool
- Pattern extraction: top 5 topics, conversation count, date range
- Custom instructions absorption (from OpenAI user.json)
- Step 3 insight display (show what was learned)
- Step 4 suggested tasks (3 tasks generated from data)
- Privacy: temp files deleted after processing
- Migration Complete badge

**Out of scope for MVP:**
- Notion OAuth integration
- HubSpot OAuth integration
- Canva OAuth integration
- Gemini/Google OAuth integration
- Real-time processing status (can show static progress bar with completion webhook)
- Advanced NLP analysis (MVP uses frequency analysis, not LLM-based extraction)

**MVP Data Model (Minimal)**

```json
{
  "migration_status": "complete|in_progress|not_started",
  "competitor": "chatgpt|claude|gemini|other",
  "conversation_count": 847,
  "date_range_years": 3.2,
  "top_topics": ["market analysis", "copywriting", "hiring"],
  "communication_style": "direct, no preamble, prefers bullet points",
  "custom_instructions_raw": "...",
  "migration_completed_at": "ISO timestamp"
}
```

### Phase 2 (After MVP Validation)

**Add in Phase 2:**
- Notion OAuth (pages + databases user selects)
- Canva OAuth (brand kit extraction)
- Richer NLP analysis (LLM-powered pattern extraction vs frequency analysis)
- Real-time processing status websocket
- "Migration Summary" PDF the user can download
- Selective reimport (connect more tools later)

### Phase 3 (Full Vision)

**Add in Phase 3:**
- HubSpot OAuth (CRM pipeline context)
- Gemini/Google Drive OAuth
- Automated re-sync (Notion databases stay current)
- Cross-tool insight: "Your ChatGPT market analysis questions align with your HubSpot deal stage — PureBrain can now bridge these"
- Team migrations (multiple users, shared workspace context)
- Migration score and benchmarking ("You're 94% migrated")

---

## 7. Privacy and Security Considerations

### Data Handling Principles

**1. Temporary file processing only**

Uploaded files (conversations.zip, etc.) are:
- Encrypted in transit (HTTPS required)
- Stored in temporary encrypted storage for processing only
- Deleted from server after extraction is complete (max 24 hours)
- Never sent to third-party services or used for model training

**2. OAuth token security**

OAuth tokens for Notion, HubSpot, Canva:
- Stored in a secrets vault (not in the database directly)
- Scoped to minimum necessary permissions
- User can revoke at any time via portal settings
- Re-fresh tokens automatically rotated

**3. CRM data special handling**

HubSpot data includes third-party PII (user's customers):
- Individual contact records should NOT be stored
- Only structural data (pipeline names, deal stage names, counts) is stored
- Contact names/emails are used for context generation only and immediately discarded

**4. User control**

Users can at any time:
- View what was imported (Migration Summary page)
- Remove any imported data category
- Disconnect OAuth integrations
- Delete all migration data (resets to pre-migration state)

**5. No training use**

Imported conversation history is never used to train any model. It is used only to populate the user's individual context profile. This must be stated clearly and repeatedly in the UI.

### Legal Considerations

**Terms of Service Compliance:**

Before building each integration, verify:
- OpenAI ToS: Does exporting and processing a user's own data for personal use violate ToS? Currently: No, personal export is permitted.
- Notion API: Public API for authorized integrations. OAuth flow is the approved method.
- HubSpot API: Public API for authorized integrations. Processing should comply with GDPR when handling EU user data.
- Canva API: Connect APIs are the official integration method.

**GDPR Considerations:**

- Users must consent to data processing before upload (explicit checkbox)
- Users in EU must be able to delete all imported data (Right to Erasure)
- Data processing agreement (DPA) may be required for B2B customers
- Data residency: clarify which region processes migration data

**Privacy Policy Update:**

The PureBrain privacy policy should explicitly cover:
- What migration data is collected
- How long it is retained
- How it is used (context only, not training)
- User rights regarding imported data

---

## 8. Implementation Priority Order

### Implementation Sequence

**Week 1-2: Foundation**
1. Design the database schema for `user_migration_profile` and `migration_status`
2. Build the file upload endpoint (accepts ZIP, JSON, CSV)
3. Build the ChatGPT conversations.json parser (extract messages, custom instructions, frequency data)
4. Build the Claude export parser (similar format to ChatGPT)
5. Build the pattern extraction pipeline (top topics, style detection, count/date range)

**Week 3: Portal UI — Steps 1-4**
6. Build Step 1: Upload UI (competitor detection, file upload cards, manual style form)
7. Build Step 2: Review UI (display parsed data categories, remove options)
8. Build Step 3: Processing UI (progress bar, insight cards, checklist)
9. Build Step 4: Tasks UI (3-5 personalized task cards, pre-loaded prompts)
10. Build Migration Complete badge for dashboard

**Week 4: Integration with AI Partner**
11. Connect `user_context_profile` to AI partner system prompt
12. Test first conversation quality improvement with and without migration data
13. Verify task card "Start this task" links create correctly pre-loaded chat sessions

**Week 5: Pre-Portal Data Collection**
14. Add 4 additional questions to exodus landing page quiz flows
15. Update Brevo contact attribute schema
16. Build exodus → portal data passthrough (email match on signup)
17. Update drip email sequences to use competitor-specific messaging

**Week 6: Security Review + QA**
18. Security review: file upload handling, temp file deletion verification
19. Security review: OAuth token storage
20. QA: full migration flow with real ChatGPT export file
21. QA: fallback flows (skipping steps, partial data)
22. Privacy policy review and update

**Phase 2 Additions (Post-Validation):**
23. Notion OAuth integration
24. Canva brand kit integration
25. Real-time processing status

---

## Acceptance Criteria

A migration is "complete" when:
- [ ] User successfully connects at least one previous tool
- [ ] At least one data category is processed and stored in `user_context_profile`
- [ ] Step 3 displays at least one personalized insight card (not generic)
- [ ] Step 4 displays at least one personalized task (with specific numbers from the import)
- [ ] AI partner's first response reflects the imported context
- [ ] Uploaded files are deleted from temporary storage
- [ ] Migration Complete badge appears in dashboard

A migration flow is "production ready" when:
- [ ] Full ChatGPT export flow works end-to-end (real ZIP file tested)
- [ ] All uploaded files are confirmed deleted after processing
- [ ] OAuth tokens stored in vault (not database)
- [ ] User can remove any data category and see it removed
- [ ] Privacy note visible on Step 2 above the CTA
- [ ] "How to export" instructions are correct and current for each competitor
- [ ] Mobile layout tested at 375px, 390px, 768px

---

## Memory Written

Path: `.claude/memory/agent-learnings/feature-designer/2026-02-23--ai-migration-portal-spec.md`
Type: synthesis
Topic: AI Migration Portal — complete feature spec for PureBrain portal
Key design insights:
- The core UX insight is "your history becomes PureBrain's foundation" — loss becomes investment
- Step 3 (PureBrain Learns You) is the emotional core — must show real-time insights, not a blank progress bar
- Midjourney has no API but manual style capture is high value — frame it as a feature, not a workaround
- CRM imports (HubSpot) carry third-party PII — structural data only, individual records discarded
- MVP should be ChatGPT + Claude file upload only, prove value before building OAuth integrations

---

**END OF SPECIFICATION**

**Status**: Ready for implementation planning
**Handoff to**: full-stack-developer (backend parsing + portal UI), security-engineer-tech (OAuth + file handling review)
**Pre-build review required by**: Jared (scope confirmation, Phase 1 boundaries)
