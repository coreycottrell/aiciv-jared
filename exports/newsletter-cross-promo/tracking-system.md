# Newsletter Cross-Promotion Tracking System

**Prepared by**: marketing-strategist
**Date**: 2026-02-24
**Purpose**: UTM parameters, GA4 setup, landing page variants, and conversion tracking for all newsletter swap partnerships
**Builds on**: `/home/jared/projects/AI-CIV/aether/config/utm-reference.md` (existing UTM master reference)

---

## Overview

Every newsletter partnership requires:
1. A unique UTM link that identifies which partner sent the subscriber
2. An optional dedicated landing page variant (for high-priority partners)
3. GA4 tracking setup so results appear in analytics reports
4. A simple tracking spreadsheet to log partner performance

Without this system, we cannot know which partnerships actually drive subscribers, which subscribers convert to PureBrain trials, or which partners deserve a repeat swap.

---

## UTM Parameter Structure for Newsletter Swaps

This extends the existing UTM master reference at `config/utm-reference.md` with newsletter-swap-specific values.

### Base URL

All newsletter swap traffic should land on the opt-in section of the homepage:
```
https://purebrain.ai/#awakening
```

### UTM Parameters for Newsletter Swaps

```
utm_source    = [partner-slug]         (unique identifier for each partner newsletter)
utm_medium    = email                  (it arrives via their email newsletter)
utm_campaign  = newsletter-swap        (consistent across all swap campaigns)
utm_content   = [mention-type]         (what kind of mention they ran)
```

### Partner Slug Convention

Create a short, lowercase, hyphenated identifier for each partner newsletter. Keep it under 20 characters.

| Partner Newsletter | Partner Slug |
|-------------------|--------------|
| AI Breakfast | `ai-breakfast` |
| The AI Report | `ai-report` |
| Ben's Bites | `bens-bites` |
| Mindstream AI | `mindstream-ai` |
| Tiago Forte (Building a Second Brain) | `forte-bsb` |
| Nick Milo (Linking Your Thinking) | `milo-lyt` |
| The Neuron Daily | `neuron-daily` |
| Future Tools Weekly | `future-tools` |
| AI for Marketers (generic) | `ai-marketers` |
| Superhuman AI (Zain Kahn) | `superhuman-ai` |
| Every / Dan Shipper | `every-to` |
| Custom / new partner | `[custom-slug]` |

### Content Values (utm_content)

| Mention Type | utm_content Value |
|-------------|-------------------|
| Full paragraph feature (100+ words) | `feature-mention` |
| Short mention / shoutout (under 50 words) | `short-mention` |
| Inline text link within their content | `inline-link` |
| Dedicated section in their newsletter | `dedicated-section` |
| Guest piece / content swap | `guest-piece` |

---

## Pre-Built UTM Link Generator

**Template** — copy and fill in the blanks:
```
https://purebrain.ai/#awakening?utm_source=[PARTNER-SLUG]&utm_medium=email&utm_campaign=newsletter-swap&utm_content=[MENTION-TYPE]
```

### Pre-Built Links for Priority Partners

**AI Breakfast — feature mention**:
```
https://purebrain.ai/#awakening?utm_source=ai-breakfast&utm_medium=email&utm_campaign=newsletter-swap&utm_content=feature-mention
```

**AI Breakfast — short mention**:
```
https://purebrain.ai/#awakening?utm_source=ai-breakfast&utm_medium=email&utm_campaign=newsletter-swap&utm_content=short-mention
```

**Ben's Bites — feature mention**:
```
https://purebrain.ai/#awakening?utm_source=bens-bites&utm_medium=email&utm_campaign=newsletter-swap&utm_content=feature-mention
```

**Ben's Bites — short mention**:
```
https://purebrain.ai/#awakening?utm_source=bens-bites&utm_medium=email&utm_campaign=newsletter-swap&utm_content=short-mention
```

**Mindstream AI — feature mention**:
```
https://purebrain.ai/#awakening?utm_source=mindstream-ai&utm_medium=email&utm_campaign=newsletter-swap&utm_content=feature-mention
```

**Tiago Forte — guest piece**:
```
https://purebrain.ai/#awakening?utm_source=forte-bsb&utm_medium=email&utm_campaign=newsletter-swap&utm_content=guest-piece
```

**Nick Milo (LYT) — guest piece**:
```
https://purebrain.ai/#awakening?utm_source=milo-lyt&utm_medium=email&utm_campaign=newsletter-swap&utm_content=guest-piece
```

**The Neuron Daily — feature mention**:
```
https://purebrain.ai/#awakening?utm_source=neuron-daily&utm_medium=email&utm_campaign=newsletter-swap&utm_content=feature-mention
```

**Ben's Bites — dedicated section**:
```
https://purebrain.ai/#awakening?utm_source=bens-bites&utm_medium=email&utm_campaign=newsletter-swap&utm_content=dedicated-section
```

---

## GA4 Setup for Newsletter Swap Tracking

The existing UTM master reference covers GA4 setup for most channels. Newsletter swaps require one additional step: a saved report that shows cross-promo performance at a glance.

### Step 1: Confirm UTM Custom Dimensions Are Active

From `config/utm-reference.md` — verify these are already set up in GA4:
- `utm_campaign` → Event-scoped → parameter: `campaign`
- `utm_content` → Event-scoped → parameter: `content`
- `utm_source` → Event-scoped → parameter: `source`
- `utm_medium` → Event-scoped → parameter: `medium`

If not yet configured, follow the instructions in `config/utm-reference.md` (GA4 Setup section).

### Step 2: Create a Newsletter Swap Exploration Report in GA4

1. Go to: GA4 → Explore → Create new Exploration
2. Name it: `Newsletter Swap Performance`
3. Add dimensions: Source, Content, Campaign
4. Add metrics: Sessions, New Users, Conversions (if conversion event is set up — see Step 3)
5. Add filter: Campaign exactly matches `newsletter-swap`
6. This report will now show all newsletter swap traffic broken down by partner (utm_source) and mention type (utm_content)

### Step 3: Set Up Conversion Event for Newsletter Opt-In

For the tracking to show the full funnel (traffic → subscriber), Brevo subscriber data needs to connect to GA4. Options:

**Option A (Simple)**: Track clicks to the opt-in section as a GA4 event. When someone clicks the sign-up button on the `/#awakening` page, fire a custom GA4 event called `newsletter_signup_click`. This is not a confirmed subscription but it is a strong intent signal.

**Option B (Accurate but complex)**: Brevo's API can send a confirmation back to GA4 via Measurement Protocol when a subscription is confirmed. This requires a small developer task — add to backlog for full-stack-developer if conversion tracking becomes a priority.

**Recommended for now**: Option A. Set up click tracking on the signup button, use that as the conversion event, and adjust attribution after 30 days of data.

---

## Optional: Dedicated Landing Page Variants

For high-priority partners (newsletters with 50K+ subscribers), a dedicated landing page variant can increase conversion rate by 15-30% compared to sending all traffic to the standard homepage opt-in.

### When to Use a Dedicated Landing Page

Use a dedicated landing page variant when:
- The partner newsletter has 50,000+ subscribers
- The partner is Tier 3 (e.g., if The Neuron Daily or Ben's Bites agrees to a feature)
- The audience has a distinct identity that we can speak to specifically

### Landing Page Variant Design Principles

A dedicated landing page variant should:
1. Include a headline that references the referring newsletter: "Recommended by [Newsletter Name]"
2. Use social proof specific to the audience type (exec-focused audience gets exec testimonials, PKM audience gets PKM-adjacent framing)
3. Have exactly one CTA: the Neural Feed subscription form
4. Not require scrolling to reach the CTA

### Implementation

Landing page variants should be created by full-stack-developer as WordPress page copies with unique slugs:
- Standard: `purebrain.ai/#awakening`
- AI Breakfast variant: `purebrain.ai/from/ai-breakfast` (hypothetical — request creation when needed)
- Ben's Bites variant: `purebrain.ai/from/bens-bites`

**Note**: Do not build landing page variants until a swap is confirmed. Build them reactively when a high-value partner confirms. Do not build them speculatively for targets that haven't responded.

---

## Partner Performance Tracking Spreadsheet

Maintain a simple tracking log for all newsletter partnerships. This does not require a tool — a Google Sheet or Notion database works.

### Columns

| Column | What to Track |
|--------|--------------|
| Partner Name | Newsletter name |
| Partner Slug | UTM source value |
| Outreach Date | When pitch was sent |
| Status | Pitched / Agreed / Declined / Executed / Completed |
| Issue Date | When they ran our mention |
| UTM Link Used | The full URL sent to them |
| Subscribers Acquired (7 days) | GA4: sessions with utm_source=[partner] who subscribed |
| Subscribers Acquired (30 days) | GA4: same filter, 30-day window |
| Open Rate (new subs from partner) | Brevo: segment by signup source tag |
| Conversion to Trial | Did any cross-promo subscribers convert to PureBrain trial? |
| Neural Feed Mention Date | When we ran their mention in Neural Feed |
| Notes | Anything relevant about the relationship |
| Next Step | Follow-up action and date |

### Tracking Notes

**How to measure "subscribers acquired from this partner"**:
1. In GA4: Exploration report → filter utm_source = [partner-slug] → utm_campaign = newsletter-swap → count New Users
2. This gives traffic. To confirm subscriptions, cross-reference with Brevo: any new subscriber who signed up within 7 days of the partner's issue date AND came from that UTM source.

**Brevo tagging for cross-promo subscribers**:
When possible, add a tag to Brevo contacts who sign up via newsletter swap: `source:newsletter-swap` and `partner:[partner-slug]`. This enables segmenting and reporting on cross-promo subscriber behavior over time.

**How to add the tag**:
Brevo's double opt-in flow does not natively pass UTM parameters to contact tags. The workaround:
- Build the opt-in URL to include hidden form fields that pre-fill with UTM source
- Or: manually review new subscribers in Brevo weekly and tag those who came from the cross-promo UTM window

This is a small technical task for full-stack-developer to implement in Phase 1 (before swaps execute).

---

## UTM Governance for This Campaign

Following the rules from `config/utm-reference.md`:
1. All lowercase. `ai-breakfast`, not `AI-Breakfast`
2. Hyphens, not underscores. `ai-breakfast`, not `ai_breakfast`
3. No spaces
4. Update this document when a new partner is added (add their slug to the Partner Slug table above)
5. Validate every new UTM link at `ga-dev-tools.google.com/campaign-url-builder/` before use

---

## Reporting Cadence

**After each swap executes**:
- Update partner tracking spreadsheet with issue date and UTM link used
- Pull GA4 data 7 days after their issue: sessions, new users from that source
- Pull Brevo: count new subscribers tagged with that partner source
- Log to spreadsheet

**Monthly review**:
- Rank all partners by subscribers acquired
- Identify top 3 partners for repeat swap outreach
- Identify any partners with below-average subscriber conversion (deprioritize repeats)
- Update target-newsletters.md with notes on executed partners

**90-day retrospective**:
- Total subscribers acquired from cross-promo channel
- Total cost: $0 cash + [X hours] of time
- Conversion rate: cross-promo subscribers → trial users
- Best-performing partner audience types (inform Month 3 targeting)
- Worst-performing partner audience types (remove from future outreach)
