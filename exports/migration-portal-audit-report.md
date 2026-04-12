# full-stack-developer: Migration Portal Audit — Quiz Integration Strategy

**Agent**: full-stack-developer
**Domain**: Full Stack Development
**Date**: 2026-02-24

---

## Executive Summary

The migration portal at `https://purebrain.ai/migrate/` is functionally built and deployed. The migration intelligence quiz (`migration-exodus-quiz.html`) is a fully standalone component. Neither is connected to the other yet.

The core question Jared is asking: **How does the quiz drive people into the migration portal, and when does it live in the funnel?**

This report answers that question across three dimensions:

1. **Current state** of the live portal vs. the spec
2. **What the quiz does and what data it captures**
3. **Three integration strategies** ranked by funnel impact, with a clear recommendation

---

## Part 1: Live Portal Audit — What Is Deployed vs. Spec

### What Is Live at `https://purebrain.ai/migrate/`

The live migration portal is a functionally complete 4-step wizard. Based on analysis of the deployed HTML and live page:

**What is working:**
- Full dark-theme UI with PureBrain brand colors (#080a12 background, #2a93c1 blue, #f1420b orange)
- 4-step wizard with step navigation and progress indicator dots
- File upload zone (drag-and-drop + click-to-upload)
- Source selection badges for ChatGPT, Gemini, and Claude
- Step 2 data review with checkboxes and remove toggles
- Step 3 animated processing orb with progress bar and insight cards
- Step 4 personalized task cards with "Start this task" CTAs
- Migration Complete badge state
- "How to Export" expandable accordion instructions
- Privacy notice on Step 2
- Responsive layout with proper PureBrain CSS scoping under `#pb-migration-portal`
- Client-side JSZip loading from CDN (`https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js`)

**What is visually present but functionally incomplete (based on architecture doc):**
- Backend API endpoints (`POST /api/migration/profile`, `GET /api/migration/profile/:userId`) — status of server-side implementation unknown. The client-side parser and UI are built but the hub server routes (`routes/migration.js`) may not be deployed yet.
- Email capture gate — the portal does not appear to have a login/auth gate. It's accessible without authentication at `/migrate/`.
- Brevo integration — `migration-brevo-integration.js` is a separate file not embedded in `migration-portal.html`. The connection between completing the portal and writing to Brevo is not verified as active.
- Exodus data passthrough — the `exodus_data` population from Brevo contact lookup is Sprint 5 work and not yet built.
- Dashboard migration banner — the "Start Migration" banner for first login is designed but the portal appears to be a standalone page, not yet integrated into the authenticated portal dashboard flow.

**Gap Summary:**
The frontend (portal UI + client-side parser) is the majority of the work and it is done. The backend integration (hub server routes, Brevo sync, auth gate, dashboard banner) is the remaining work per the architecture's Sprint 2-5 scope.

---

## Part 2: The Migration Intelligence Quiz — What It Is

The quiz at `migration-exodus-quiz.html` is a **5-question standalone intake form** with the following structure:

### Quiz Questions

**Step 1: Which AI are you currently using most?** (Single-select)
- ChatGPT / OpenAI
- Claude / Anthropic
- Gemini / Google
- Microsoft Copilot
- Perplexity
- Other

**Step 2: How long have you been using it?** (Single-select)
- Less than 3 months
- 3-12 months
- 1-2 years
- More than 2 years

**Step 3: What do you mainly use it for?** (Multi-select, up to 3)
- Writing & editing (emails, reports, proposals)
- Research & summarization
- Coding & technical work
- Creative & brainstorming
- Customer-facing content
- Data analysis & reporting
- Business strategy & planning
- Image/visual creation

**Step 4: What frustrates you most about your current AI tool?** (Single-select)
- It doesn't remember anything between conversations
- Responses feel generic, not tailored to my work
- Limited or no integrations with my other tools
- Inconsistent quality — good some days, poor others
- Too expensive for what I'm getting
- I've outgrown its capabilities

**Step 5: What's your primary business goal for AI this year?** (Single-select)
- Save time on repetitive tasks
- Improve quality of work output
- Scale operations without adding headcount
- Build AI-powered products or workflows
- Replace or reduce specific software subscriptions

### Quiz Outputs

After completing all 5 questions, the quiz:
1. Calculates a **Migration Readiness Score** (0-100 based on answer weighting)
2. Displays a **personalized result** based on score range (High/Medium/Low readiness)
3. Shows a **tailored recommendation message** that matches the competitor and frustration detected
4. Captures **email address** with a CTA to receive a personalized migration plan
5. Calls `saveMigrationIntent()` from `migration-brevo-integration.js` to create/update the Brevo contact
6. Calls `triggerMigrationDrip()` to add the contact to the competitor-specific drip list

### Data the Quiz Captures

```json
{
  "competitor": "chatgpt",
  "usage_duration": "1-2 years",
  "primary_use_cases": ["writing", "research", "business_strategy"],
  "main_frustration": "no_memory",
  "primary_goal": "save_time",
  "migration_readiness_score": 78,
  "email": "user@company.com"
}
```

This is the exact `exodus_data` object the migration portal architecture specifies as the input for personalizing Step 4 task cards.

---

## Part 3: Integration Strategy — Three Options

### Option A: Quiz BEFORE Portal (Pre-Qualification Funnel)

**Placement:** `/migrate/` page shows the quiz FIRST. After quiz + email capture, user is invited to access the full migration portal.

```
User visits /migrate/
         |
    [Migration Intelligence Quiz — 5 questions]
         |
    Email captured + Brevo tagged
         |
    Score displayed + competitor-matched copy
         |
    CTA: "Start Your Migration" → portal wizard
         |
    [4-Step Migration Portal]
         |
    Portal personalized with quiz exodus_data
```

**Pros:**
- Captures email BEFORE the portal (higher lead capture rate — most people won't upload a ZIP without being warmed first)
- Quiz data feeds directly into portal personalization (competitor pre-detected, frustration pre-known)
- Filters cold traffic from warm intent leads
- Lowers cognitive load by separating "learn about yourself" from "do the import"
- Every quiz completer becomes a tagged Brevo contact before they even use the portal

**Cons:**
- Adds friction before the portal (one more step)
- Users who want to "just migrate" have to go through the quiz first
- If quiz scoring is off, low-score users may self-select out before trying the portal

**Best for:** Cold traffic arriving from SEO, blog CTAs, Bluesky, LinkedIn. Users who don't know what PureBrain is yet.

---

### Option B: Quiz INSIDE the Portal as Step 0 (Seamless Inline Integration)

**Placement:** The quiz becomes the portal's entry gate. Instead of the current Step 1 (upload file), the portal now has a "Step 0" quiz that runs before the upload.

```
User visits /migrate/
         |
    [Portal Step 0: Quick Profile Quiz — 3 questions]
         |
    Competitor detected → Step 1 upload UI adapts
    (shows ChatGPT upload card first if competitor = ChatGPT)
         |
    [Step 1: Upload File — pre-personalized for detected competitor]
         |
    [Step 2: Review Data]
         |
    [Step 3: PureBrain Learns]
         |
    [Step 4: Personalized Tasks — enhanced with quiz data]
```

For inline use, the quiz would be shortened to 3 questions (competitor, main use case, main frustration) — not the full 5-question standalone version.

**Pros:**
- No extra URL or page — single coherent experience at `/migrate/`
- Quiz answers feed directly into Step 1 (upload card shows correct competitor first) and Step 4 (task cards personalized)
- Lower drop-off because quiz feels like onboarding, not qualification
- Users who know what they're doing can see "already using ChatGPT? Upload below" — less friction

**Cons:**
- More complex UI architecture — requires quiz state to persist through portal steps
- Full standalone quiz (5 questions) is too long to embed — must use shortened 3-question version
- Email capture timing is unclear — before Step 1? After Step 3?
- Portal email gate and quiz email gate become the same form (simpler, but loses lead capture before upload)

**Best for:** Users who arrive at `/migrate/` with high intent — they know they want to migrate, they just need guidance. Post-signup portal state.

---

### Option C: Quiz AFTER Account Setup — Enrichment Layer (Post-Purchase)

**Placement:** New PureBrain customers who haven't done the migration quiz see it as a prompt inside the portal dashboard, BEFORE they start the migration wizard.

```
New customer signs up / completes post-payment chatbox
         |
    Portal dashboard loads
         |
    If no exodus_data on file:
    → Migration Intelligence Quiz prompt card in dashboard
         |
    Customer completes 5-question quiz
    (more thorough — already a customer, higher engagement)
         |
    Portal learns competitor + frustration before import
         |
    "Based on your profile, here's your recommended migration path →"
         |
    [Migration wizard — fully personalized from quiz data]
```

**Pros:**
- Maximum engagement — customers have already bought, they're invested
- Full 5-question quiz is appropriate here (they have time, they want to onboard properly)
- Quiz answers create the richest profile before any file upload happens
- Combined with post-payment chatbox data, portal has the most complete user picture

**Cons:**
- Misses pre-purchase lead capture entirely — no email capture for non-customers
- Requires authenticated portal to work — can't be tested without a real account
- Users who skip the quiz on first login may never see it again

**Best for:** Existing customers who signed up without going through an exodus page, or customers whose quiz data wasn't captured pre-purchase.

---

## Part 4: Recommendation — The Layered Strategy

Do not choose one. Use all three at different stages of the funnel. Here is the layered architecture:

```
LAYER 1: PRE-PURCHASE (Option A — Quiz Before Portal)
Audience: Cold traffic from SEO, blog, social, ads

URL: /migrate/ (unauthenticated, public)
What they see: Quiz → Email capture → Score + competitor copy → CTA to sign up

Purpose: Lead capture + intent qualification + Brevo drip trigger
Data output: Brevo tagged with competitor + frustration + migration readiness score
Next step for user: CTA → purebrain.ai/#awakening (purchase)

---

LAYER 2: POST-PURCHASE ONBOARDING (Option C — Quiz in Dashboard)
Audience: New customers who didn't come through an exodus page

Where: Authenticated portal dashboard — prompt card
What they see: "Before we set up your migration, tell us about your AI background" → 5-question quiz
Purpose: Fill in missing exodus_data for users who purchased without quiz data
Data output: exodus_data written to user profile, Brevo contact updated
Next step for user: "Start Migration" → migration wizard (personalized)

---

LAYER 3: MIGRATION WIZARD (Option B logic — Quiz data pre-loaded)
Audience: All users entering the migration wizard

Where: Inside the 4-step portal wizard (already built)
What happens: Portal reads quiz data from profile, auto-selects competitor upload card in Step 1,
              personalizes Step 4 task cards with quiz answers
Purpose: Use collected data to make the portal feel personal without re-asking questions
Data output: Migration profile with combined quiz + import data
Next step for user: "Start this task" → first PureBrain conversation with full context
```

### Why This Order

**The funnel math:**
- 100 people visit `/migrate/`
- 60 complete the quiz (typical quiz completion for well-designed multi-step forms)
- 60 Brevo contacts created, tagged, and entered into competitor-specific drip
- 15-20 purchase PureBrain within 30 days (10-15% conversion per email sequence targets)
- 15-20 customers complete the migration wizard (60%+ completion target per spec)
- Each completer exits with a fully personalized first conversation

**Without the quiz before the portal, you lose:**
- The 45 people who completed the quiz but haven't bought yet — no Brevo contact, no drip, no conversion opportunity
- The competitor-specific personalization in the portal wizard (no pre-detected competitor = generic Step 1 experience)

---

## Part 5: Specific Implementation Steps (What to Build)

### Step 1: Deploy the Quiz Standalone at `/migrate/` (This Week)

The `migration-exodus-quiz.html` is ready. It needs to be deployed to WordPress at `/migrate/` as the page's visible content, with the migration portal accessible via a CTA button after quiz completion.

**Current state of `/migrate/`:** Shows the portal wizard directly.

**Required change:** Replace the current page content with:
1. A split layout: quiz on the left/top half, "Already have an account? Start migration" link for existing customers
2. After quiz completion: show score result + CTA button "Start Your Migration →" that links to the full portal wizard (could be modal overlay or link to separate `/migrate/portal/` page)

**Deployment:** WordPress REST API to page at `/migrate/`, using `elementor_canvas` template. Wrap in `<!-- wp:html -->` block.

### Step 2: Connect Quiz to Brevo (This Week)

The `migration-brevo-integration.js` functions are ready. They need to be called on quiz completion.

In `migration-exodus-quiz.html`, the quiz already has a submit handler. Connect it:

```javascript
// On quiz email capture + submission:
await handleExodusQuizCompletion({
  email: emailInput.value,
  competitor: answers.step1,           // e.g. 'chatgpt'
  primary_use_cases: answers.step3,    // array
  usage_frequency: answers.step2,      // duration → frequency map
  had_custom_config: null,             // not asked in quiz, default null
  main_frustration: answers.step4,
  primary_goal: answers.step5,
  quiz_score: calculatedScore,
  utm_source: getUTMParam('utm_source'),
  utm_campaign: getUTMParam('utm_campaign')
});
```

**Security note:** The Brevo API key must NOT be in the client-side quiz HTML. Route the call through a server-side proxy endpoint (e.g., `POST /api/migration/capture-intent` on the hub server). This is flagged as P0 security requirement (S-09 in the test plan).

### Step 3: Portal Reads Quiz Data on Entry

When a logged-in user enters the migration wizard, the portal should check for pre-existing `exodus_data`:

```javascript
// On portal load:
const profile = await fetch(`/api/migration/profile/${userId}`).then(r => r.json());

if (profile.exodus_data && profile.exodus_data.competitor) {
  // Pre-select the competitor upload card in Step 1
  preselectCompetitor(profile.exodus_data.competitor);

  // Show personalized banner: "You're switching from ChatGPT — let's bring your work with you"
  showPersonalizedBanner(profile.exodus_data.competitor, profile.exodus_data.main_frustration);
}
```

This is Sprint 5 work in the architecture doc but it is small — 20-30 lines of JS in the portal wizard.

### Step 4: Add Quiz Prompt Card to Dashboard for Non-Quiz Customers

For customers who purchased without going through the quiz, add a card to the portal dashboard:

```html
<!-- Shown if exodus_data is empty or not set -->
<div class="migration-quiz-nudge">
  <h3>Before we migrate your AI history...</h3>
  <p>Answer 3 quick questions so we can personalize your migration path.</p>
  <a href="#" class="btn-orange" onclick="openMigrationQuiz()">Personalize My Migration</a>
</div>
```

The quiz in this context only needs questions 1, 3, and 4 (competitor, use cases, frustration) — the 3 fields that feed directly into portal personalization.

---

## Part 6: The Full User Journey (After Integration)

### Journey A: Cold Traffic (First Time Visitor)

```
Google "ChatGPT alternative with memory" → purebrain.ai blog post
→ Blog CTA "Migrate from ChatGPT" → /migrate/
→ Sees Migration Intelligence Quiz
→ Answers 5 questions (45 seconds)
→ Reads score: "High Migration Readiness — your history is portable"
→ Enters email to get migration plan
→ Brevo: tagged from-chatgpt, migration-intent, readiness-score=78
→ Drip email 1 arrives: "Your frustration with ChatGPT makes sense"
→ Day 4 email: "Here's what happens to your ChatGPT history"
→ Clicks through to purebrain.ai/#awakening → Purchases
→ Post-payment chatbox → enters portal dashboard
→ Dashboard shows "Migration Ready" — portal remembers they came from ChatGPT
→ Starts migration wizard with ChatGPT upload card pre-selected
→ Uploads ZIP → Step 3 insights → Step 4 tasks personalized to their use cases
→ First conversation with PureBrain references their detected patterns
```

### Journey B: Direct Visitor (High Intent)

```
Finds PureBrain via recommendation → goes to /migrate/ directly
→ Skips quiz or sees condensed 3-question version
→ Signs up immediately (or has already signed up)
→ Portal dashboard prompts: "Tell us about your AI background (3 questions)"
→ Answers in 30 seconds → exodus_data populated
→ Starts migration wizard — personalized from dashboard quiz
```

### Journey C: Existing Customer (No Exodus Data)

```
Customer signed up via homepage, no exodus page, no quiz
→ Portal dashboard shows "Let's personalize your migration" quiz card
→ Fills out 3-question mini quiz
→ Migration wizard uses quiz data for Step 1 competitor pre-selection and Step 4 tasks
```

---

## Part 7: What the Quiz Data Does to the Portal (Technical Mapping)

| Quiz Answer | Portal Behavior |
|---|---|
| `competitor = chatgpt` | Step 1: ChatGPT upload card shown first and expanded by default |
| `competitor = claude` | Step 1: Claude upload card shown first |
| `main_frustration = no_memory` | Portal banner copy: "You said it never remembered anything — here's how that changes." |
| `main_frustration = generic_responses` | Portal banner: "You said it felt like a tool, not a partner — meet PureBrain." |
| `primary_use_cases = ['writing', 'research']` | Step 4 tasks: "Write with your voice" + "Research with context" shown first |
| `primary_use_cases = ['coding']` | Step 4 tasks: "Code review with your project context" shown first |
| `usage_duration = 2+ years` | Banner: "You have years of history — don't leave it behind." + high-priority import recommendation |
| `migration_readiness_score >= 70` | Portal CTA: "You're ready. Let's go." (low-friction messaging) |
| `migration_readiness_score < 40` | Portal CTA: "We'll walk you through it step by step." (reassuring messaging) |

---

## Part 8: What Is Missing From the Live Portal

Cross-referencing the spec, architecture, security review, and test plan against the live deployment:

### Missing — Backend (Hub Server)

| Item | Status | Priority |
|---|---|---|
| `POST /api/migration/profile` — save extracted profile | Not verified as deployed | P0 |
| `GET /api/migration/profile/:userId` — retrieve profile | Not verified as deployed | P0 |
| `POST /api/migration/complete` — mark migration done | Not verified as deployed | P0 |
| `DELETE /api/migration/profile/:userId` — GDPR erasure | Not verified as deployed | P1 |
| DB schema (`user_migration_profiles` table) | Not verified as created | P0 |

### Missing — Integrations

| Item | Status | Priority |
|---|---|---|
| Brevo intent capture on quiz completion | Not connected | P0 (blocks email capture) |
| Exodus data passthrough to portal profile | Sprint 5, not built | P1 |
| Dashboard migration banner | Not visible (no auth gate on current page) | P1 |
| Auth gate on portal | Portal is public — no login required | P1 |

### Missing — Quiz Integration (The Core Ask)

| Item | Status | Priority |
|---|---|---|
| Quiz deployed at `/migrate/` as entry gate | Not present | P0 |
| Quiz → Brevo connection (server-side proxy) | Not built | P0 |
| Quiz competitor data → portal Step 1 pre-selection | Not built | P1 |
| Quiz frustration data → portal banner copy | Not built | P1 |

### What Is Done Well

| Item | Status |
|---|---|
| Full portal UI (Steps 1-4) | Done |
| Client-side JSZip ZIP parsing | Built into portal HTML |
| Step 3 animation with insight cards | Built |
| Step 4 task card generation | Built |
| Brevo integration module | Done (needs server-side deployment) |
| Quiz HTML standalone component | Done |
| Email sequences for all 3 competitors | Done |
| Security review completed | Done |
| Test plan with fixtures | Done |

---

## Part 9: Recommended Priority Order

**This week (immediate):**

1. Deploy the quiz at `/migrate/` as the page entry point (30 min — WordPress REST API)
2. Build server-side proxy endpoint `POST /api/capture-migration-intent` on hub server to call Brevo without exposing the API key client-side (2-3 hours)
3. Wire quiz submit handler to call the proxy endpoint (1 hour)
4. Add quiz CTA → portal flow: quiz result page shows "Start Migration" button that leads to the portal wizard

**Next sprint:**

5. Verify hub server migration API routes are deployed and functional (test with curl as architecture doc specifies)
6. Connect quiz exodus_data to portal — portal reads Brevo or hub server profile on entry and pre-selects competitor
7. Add dashboard migration quiz nudge card for customers without exodus data

**After that:**

8. Full Brevo drip sequence activation for each competitor list
9. QA pass per the test plan
10. Security review sign-off per the security doc

---

## Verification

- Read all 8 attached files in full
- Fetched and analyzed live page at `https://purebrain.ai/migrate/`
- Compared live state against feature spec, architecture doc, security review, and test plan
- Cross-referenced quiz HTML structure against Brevo integration module data schema
- Report saved to `/home/jared/projects/AI-CIV/aether/exports/migration-portal-audit-report.md`

---

## Memory Written

Path: `.claude/memory/agent-learnings/full-stack-developer/2026-02-24--migration-portal-quiz-integration-audit.md`
Type: synthesis
Topic: Migration portal audit — quiz integration strategy, live page gap analysis, 3-layer funnel approach

Key findings:
- Portal UI (Steps 1-4) is built and deployed. Backend API routes not verified as active.
- Quiz is a standalone component, not yet connected to Brevo or the portal.
- Recommended: Quiz at /migrate/ as entry gate (pre-purchase lead capture) + dashboard quiz nudge for post-purchase customers without exodus data + portal reads quiz data to personalize Steps 1 and 4.
- The quiz captures exactly the `exodus_data` schema the architecture specifies for Step 4 task personalization.
- Critical gap: Brevo API key cannot be in client-side quiz — need server-side proxy endpoint.
