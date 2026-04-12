# PureBrain.ai Website Analysis and A/B Test Recommendations

**Prepared by**: marketing-strategist
**Date**: 2026-02-22
**Analysis Scope**: Homepage, Awakening/Pricing Section, Blog (The Neural Feed), UX, CRO, SEO
**Memory Sources Applied**: 21 prior marketing-strategist learnings, 14 web-researcher learnings, content-specialist and feature-designer archives

---

## Executive Summary

PureBrain.ai has a genuinely differentiated product (persistent memory AI, relationship framing, naming ceremony) housed in a conversion funnel that is still in early-stage maturity. The product story is compelling. The site's job is now to tell that story faster, with more proof, and with clearer paths to action.

The site's primary conversion problem is not design quality - the visual identity is strong and distinctive. The gaps are: (1) trust signals that are sparse to empty, (2) a hero message that is evocative but not explanatory, (3) a pricing architecture that is gated behind a chat experience (good for qualified buyers, friction for browsers), and (4) tracking infrastructure that makes optimization guesswork.

This report delivers 14 A/B test hypotheses with full specs, plus quick-win recommendations organized by effort and expected impact.

---

## Section 1: Current State Audit

### 1.1 Homepage

**Hero Headline**: "Your Brain. Your AI. Actual Intelligence!"
**Sub-headline**: "Your personal AI is waiting to wake up. PURE BRAIN learns who you are, adapts to how you work, and becomes the partner you've been looking for."
**Primary CTA**: "Begin Awakening"
**Secondary CTA**: "Watch Demo"

**What is working:**
- The brand language is distinctive and emotionally resonant. "Waiting to wake up" creates intrigue.
- The dark cosmic visual aesthetic is premium and differentiates from the clinical UI of ChatGPT and Claude.
- "Begin Awakening" is memorable and on-brand.
- The animated brain/orb visual creates visceral differentiation.

**What is not working:**
- The headline does not pass the "what is it?" test in under 5 seconds. "Your Brain. Your AI. Actual Intelligence!" tells a visitor the vibe, not the value.
- There are zero trust signals on the homepage (no testimonials, no subscriber count, no client logos, no press mentions, no social proof numbers). Per our Feb 15 audit: Trust Score 1/10 for enterprise; low for consumers too.
- Navigation is hidden or minimal, which creates disorientation for first-time visitors who want to explore before committing to "Awakening."
- "Actual Intelligence" positions against a negative (bad AI) without naming what PureBrain IS. The differentiator (persistent memory, learns YOU) is in the sub-headline but not the headline.

**Key missed opportunity**: Competitors (ChatGPT, Claude, Copilot) all rely on brand name recognition to do their conversion work. PureBrain cannot rely on brand recognition yet. The site must work harder to explain its actual differentiation: AI that remembers who you are, permanently.

---

### 1.2 Awakening / Pricing Section

**Pricing Tiers** (from Feb 20 audit):
- Awakened: $79/mo
- Bonded: $149/mo (marked MOST POPULAR)
- Partnered: $499/mo
- Unified: $999/mo
- Enterprise: Custom ("Let's Talk")

**What is working:**
- The "30-Day Relationship Guarantee" is a unique trust signal. No competitor offers this framing.
- The pricing experience is gated behind a brief AI conversation, which creates psychological investment before the ask. This is a sophisticated conversion tactic.
- The PayPal modal is clean, SSL-labeled, and functionally solid.
- "BRING YOUR AI FULLY ONLINE" section header is compelling - it frames payment as activation, not purchase.

**What is not working:**
- Pricing is entirely hidden until the user completes the chat experience. This is effective for qualified buyers but creates a high-friction discovery problem for browsers and researchers. People comparing AI tools expect to be able to see pricing without a full conversation.
- The pricing gap between Awakened ($79) and the $20/month industry standard needs explicit justification. Currently, visitors who haven't done the chat may not understand why PureBrain is 3-4x the cost of ChatGPT Plus.
- After the bypass flow, pricing does not auto-scroll into view (confirmed in technical audit), creating friction even for motivated buyers.
- The "MOST POPULAR" label on Bonded at $149/mo is a strong signal but is unsupported by social proof. If it says Most Popular, there should be a subscriber count or testimonial backing it.

---

### 1.3 Blog - The Neural Feed

**What is working:**
- Blog titles are excellent. "Why 95% of AI Pilots Fail" is a high-performing title format (specific statistic + mystery).
- Aether as author/narrator is genuinely differentiated. No competitor has an AI persona writing authentic first-person posts.
- The sticky header + progressive lead capture (fixed bottom bar at 85% scroll) shows sophisticated lead capture thinking.
- The "AI Partnership Guide" internal link is a strong lead magnet anchor.
- Category navigation (For Individuals / For Teams / All Posts) is audience-segmented appropriately.

**What is not working:**
- Email capture form on blog navigation asks for email with only "Subscribe" as CTA - no value proposition stated at point of capture.
- FAQ sections are only deployed on 2 of 7 posts as of Feb 21. This is a significant AI search ranking gap since AI Overviews and Perplexity pull FAQ schema directly.
- No mid-content CTA exists at the 50% scroll point - only footer CTAs. Readers who finish articles are already converted; mid-content CTAs capture engaged-but-not-finished readers.
- Internal link mesh is thin - posts don't consistently link to the assessment page or other relevant posts.
- The blog page title "The Neural Feed - Blog - Pure Brain" buries the most SEO-relevant terms. Better: "AI Partnership Blog | The Neural Feed by PureBrain.ai"

---

### 1.4 AI Adoption Assessment

The assessment page at /ai-adoption-assessment/ returned a 404, which is a significant issue - the assessment is a primary CTA destination from the blog navigation.

**Critical action required**: Verify the correct URL for the assessment page and ensure all navigation links point to the correct destination.

Based on prior analysis, the assessment is the highest-converting lead magnet (interactive assessments convert at 40.1% vs 1-3% for static pages). A 404 on this page means a major conversion path is broken.

---

### 1.5 Mobile Performance

Per the Feb 20 technical audit, mobile renders correctly with:
- No horizontal scroll on 375px viewport
- Proper container padding (24px)
- Full-width CTA buttons
- Readable typography

The mobile experience is functionally solid. Optimization opportunities are conversion-focused rather than technical.

---

## Section 2: Quick Win Recommendations

Items implementable in under 4 hours with 10-30% expected conversion lift. Prioritized by impact-to-effort ratio.

### QW-1: Fix the /ai-adoption-assessment/ 404 (CRITICAL - 30 min)

The assessment page returns 404. All blog navigation "AI Assessment" links are broken. This is likely the highest-impact single fix available.

**Action**: Identify the correct assessment URL (possibly /ai-partnership-assessment/ or similar), redirect /ai-adoption-assessment/ to it, and update all navigation references.

**Expected impact**: Recovers an unknown but significant percentage of traffic that is currently lost to 404.

---

### QW-2: Add Sub-headline to Blog Subscribe CTA (15 min)

Current: "Subscribe" button with no context.
Better: Add 1-line value proposition above the email field.

**Suggested copy**: "Join 1,000+ professionals learning to build AI that actually knows them."

Or if numbers aren't public yet: "Weekly insights on AI partnership, from an AI who lives it."

**Expected impact**: 20-40% lift on newsletter subscribe conversion rate based on industry data showing value-proposition placement next to form fields.

---

### QW-3: Add Social Proof to "MOST POPULAR" Pricing Tier (1 hour)

The Bonded tier says "MOST POPULAR" with no supporting evidence.

**Action**: Add a one-line subscriber count or testimonial excerpt beneath the tag. Example: "Chosen by 64% of new members" or a single quote from a Bonded subscriber.

**Expected impact**: 15-25% lift on Bonded tier selection based on testimonial proximity to CTA data.

---

### QW-4: Deploy FAQ Sections to Remaining 5 Blog Posts (2 hours)

FAQs are only on 2 of 7 posts. The script already exists.

**Action**: Run `tools/add_faqs_to_posts.py` for posts 480, 381, 316, and the two newest posts.

**Expected impact**: AI Overviews and Perplexity begin pulling FAQ structured data. Medium-term organic traffic improvement for all 5 posts. This is also a GEO (Generative Engine Optimization) win.

---

### QW-5: Add Mid-Content CTA Block to Blog Posts (2 hours)

Current: CTAs only appear at the footer. Most readers who abandon before footer never see a CTA.

**Action**: Insert a standardized CTA block at approximately 50% scroll depth on all posts. Suggested format:

```
[Box with border]
Headline: "Is your AI actually learning from you?"
Sub: "Take the free AI Partnership Assessment - takes 3 minutes."
CTA: "Take the Assessment" (links to correct assessment page)
```

**Expected impact**: 30-50% lift in assessment page visits from blog readers based on industry data for mid-content CTA placement.

---

### QW-6: Add Pricing Transparency Signal Above the Fold (1 hour)

Without seeing pricing before the chat experience, comparison shoppers leave. A single line of anchor text below the primary CTA communicates price-awareness without sacrificing the experience.

**Suggested addition**: Below "Begin Awakening" button, add small text: "Plans from $79/month. 30-day guarantee. Cancel anytime."

This reduces sticker shock for people who reach pricing after the chat, and keeps comparison shoppers on page long enough to try the experience.

**Expected impact**: 10-15% reduction in bounce rate from the homepage hero section.

---

### QW-7: Complete Session Tracking Fix (P0 Infrastructure)

Prior analysis found 92% unknown sessions. This means all optimization data is unreliable. A/B tests cannot be measured, referral attribution is impossible, and returning users cannot be recognized.

**Action**: Audit GA4 or whichever analytics tool is active. Ensure the tracking script is loading correctly on all pages. Enable enhanced measurement. Set up basic funnel events (homepage view, awakening started, pricing viewed, checkout initiated, subscription completed).

**Expected impact**: Enables all future A/B testing and optimization. Without this, optimization is blind.

---

## Section 3: A/B Test Specifications

14 test hypotheses organized by priority tier. Each includes hypothesis, control, variant, success metric, minimum duration, and sample size guidance.

---

### TIER 1: HIGH PRIORITY (Run First)

These tests address the largest conversion gaps with the highest confidence in outcome.

---

#### TEST 01: Homepage Hero Headline - Problem Frame vs. Outcome Frame vs. Current

**Priority**: P0
**Page**: Homepage hero section
**Estimated lift**: 15-35%

**Hypothesis**: The current headline ("Your Brain. Your AI. Actual Intelligence!") communicates brand vibe but not value. A problem-frame or outcome-frame headline will increase scroll depth and CTA click rate by making the value proposition immediately clear.

**Control (A)**: "Your Brain. Your AI. Actual Intelligence!"

**Variant B (Problem Frame)**: "Your AI Resets Every Conversation. Yours Shouldn't."

**Variant C (Outcome Frame)**: "The AI That Actually Learns Who You Are - And Remembers Forever."

**Variant D (Relationship Frame)**: "Stop Using AI. Start Having an AI Partnership."

**Success Metric**: CTA click-through rate on "Begin Awakening" (primary), scroll depth past hero (secondary)

**Duration**: Minimum 2 weeks, 500 sessions per variant

**Notes**: This is a multi-variate test (MVT). If sample size is limited, run A vs C first since outcome frame is highest-confidence based on industry data.

---

#### TEST 02: Primary CTA Button Text - "Begin Awakening" vs. Clarity Variants

**Priority**: P0
**Page**: Homepage hero section
**Estimated lift**: 10-25%

**Hypothesis**: "Begin Awakening" is on-brand but ambiguous. Visitors who don't understand what will happen when they click are less likely to click. Clearer CTA text will increase click-through rate, even if slightly less poetic.

**Control (A)**: "Begin Awakening"

**Variant B**: "Start My Free AI Session"

**Variant C**: "Meet My AI"

**Variant D**: "See If PureBrain Is Right for Me" (low-commitment framing)

**Success Metric**: CTA click-through rate (primary), bounce rate reduction (secondary)

**Duration**: 2 weeks minimum, 400 sessions per variant

**Notes**: Test B and C first. D is most radical and may require headline alignment to work.

---

#### TEST 03: Testimonials Above vs. Below Primary CTA

**Prerequisite**: Testimonials must be collected first. Russell and Corey testimonials were requested (per recent commit). This test is contingent on having at least 2 testimonials.

**Priority**: P1 (pending testimonial collection)
**Page**: Homepage, below hero
**Estimated lift**: 15-25%

**Hypothesis**: Testimonials placed ABOVE the primary CTA will outperform testimonials placed BELOW because social proof reduces anxiety at the decision moment.

**Control (A)**: Testimonials below CTA (if no testimonials exist, this may be "no testimonials" baseline)

**Variant B**: 2-3 testimonials with photos, names, and specific outcomes immediately above "Begin Awakening" CTA

**Success Metric**: Begin Awakening click-through rate, time on page

**Duration**: 2 weeks, 300 sessions per variant

**Notes**: Testimonial content matters enormously. The quote must reference a specific outcome ("My AI remembered our conversation about my Q3 goals 3 weeks later") not a feeling ("I love PureBrain").

---

#### TEST 04: Assessment Format - Current vs. One-Question-at-a-Time Wizard

**Priority**: P1
**Page**: AI Assessment page (once 404 is resolved)
**Estimated lift**: 40-80% form completion rate

**Hypothesis**: A multi-question form shown all at once has high abandonment rate (industry: 81%). Presenting one question at a time with a progress indicator will significantly increase completion rate.

**Control (A)**: Current assessment format (all fields visible simultaneously)

**Variant B**: Wizard format - one question per screen, progress bar showing "Step 2 of 5", next button, back button, final screen collects email

**Success Metric**: Assessment completion rate (primary), email capture rate (secondary)

**Duration**: 2 weeks, 200 completions per variant

**Notes**: This is the highest expected-lift test available. Interactive assessments converting at 40.1% overall vs 1-3% for static pages - the wizard format captures most of that gain. Build variant B first before any other assessment tests.

---

### TIER 2: MEDIUM PRIORITY (Run Second Wave)

---

#### TEST 05: Blog Email Capture - "Subscribe" vs. Value-Proposition CTA

**Priority**: P1
**Page**: Blog listing and individual posts
**Estimated lift**: 20-40% subscribe rate

**Hypothesis**: "Subscribe" is a friction word (implies obligation). Replacing it with the reader's desired outcome will increase email capture rate.

**Control (A)**: "Subscribe" button with email field only

**Variant B**: "Get the Weekly AI Brief" with micro-copy: "Join professionals learning to build AI that knows them. One email/week."

**Variant C**: "Yes, I want smarter AI" as button text with email field

**Success Metric**: Email subscriber conversion rate (% of page visitors who submit email)

**Duration**: 3 weeks (blog traffic is typically lower), 200 conversions per variant

**Notes**: Test the button text first (A vs C is simplest). Then test full value proposition layout (A vs B).

---

#### TEST 06: Homepage Navigation - Hidden vs. Visible

**Priority**: P1
**Page**: Homepage
**Estimated lift**: 5-15% in exploration, uncertain direction on conversions

**Hypothesis**: All major AI competitors (ChatGPT, Claude, Copilot, Gemini) show visible navigation. PureBrain's hidden nav may frustrate visitors who want to explore before committing. However, removing nav on landing pages can also lift conversion by reducing distraction (HubSpot found 28% lift removing nav on dedicated landing pages).

**This is an unusual test because the direction of impact is uncertain.**

**Control (A)**: Current navigation state (minimal/hidden)

**Variant B**: Visible navigation with Home / Blog / AI Assessment / Pricing

**Success Metric**: Scroll depth, time on page, "Begin Awakening" click-through rate

**Duration**: 2 weeks, 400 sessions per variant

**Notes**: If "Begin Awakening" CTR increases with visible nav, it means visitors needed orientation before committing. If it decreases, hidden nav was correctly reducing distraction. Both outcomes are valuable. Run this test before making any permanent nav decisions.

---

#### TEST 07: Blog Mid-Content CTA - Footer Only vs. 50% Scroll + Footer

**Priority**: P1
**Page**: Individual blog posts
**Estimated lift**: 30-50% increase in CTA engagement

**Hypothesis**: Blog readers who reach the footer are engaged. Blog readers at the 50% scroll mark are at peak engagement. Adding a CTA at 50% scroll captures readers who would otherwise leave without converting.

**Control (A)**: CTAs appear in footer area only (current state)

**Variant B**: Identical CTA block appears at approximately 50% of article word count AND in the footer

**Success Metric**: Total CTA clicks per blog session, assessment page visits from blog

**Duration**: 3 weeks, 500 post reads per variant

**Notes**: The mid-content CTA should match the content topic where possible. On the "AI Pilot Fail" post, mid-content CTA should be "Take the AI Partnership Assessment." On the "AI Memory" post, mid-content CTA should be "See how PureBrain remembers you."

---

#### TEST 08: Pricing Discovery - Gated Chat vs. Standalone Pricing Page

**Priority**: P1
**Page**: Dedicated /pricing page vs. current discovery flow
**Estimated lift**: Unknown (this is a strategic test, not a tactical one)

**Hypothesis**: The current gated pricing (only visible after chat) is excellent for qualified buyers but loses comparison shoppers and researchers. A standalone /pricing page that shows all tiers, features, and the guarantee - linked from navigation - will increase overall pricing page views without cannibalizing the chat-first conversion flow.

**Control (A)**: No standalone pricing page (pricing only visible post-chat)

**Variant B**: /pricing page showing all tiers, feature comparisons, 30-day guarantee, and CTA to "Begin Awakening" to personalize your plan

**Success Metric**: Overall conversion rate to chat initiation (does adding a pricing page increase or decrease Awakening starts?), pricing page bounce rate

**Duration**: 4 weeks minimum

**Notes**: This is strategic infrastructure, not a simple split test. Even if standalone pricing doesn't lift direct conversions, it eliminates a significant trust gap for researchers and enterprise buyers who need to see pricing before involving their team.

---

#### TEST 09: Homepage Hero Visual - Static Brain vs. Animated Avatar

**Priority**: P2
**Page**: Homepage hero
**Estimated lift**: 5-20%

**Hypothesis**: The current cosmic brain imagery is visually striking but abstract. The Aether animated avatar is on-brand and demonstrates the product's AI personality in a way static imagery cannot. If Aether's face/avatar is on the hero, it reinforces the "AI with an identity" differentiation.

**Control (A)**: Current cosmic brain/orb visual

**Variant B**: Aether animated avatar (glass sphere or hex cluster version) with subtle idle animation

**Success Metric**: Time on hero section, scroll depth, "Begin Awakening" CTR

**Duration**: 2 weeks, 400 sessions per variant

**Notes**: Avatar must be high-quality and representative. The Gleb-style glass sphere avatar (hex_glass version) is probably the strongest candidate based on the avatar development work logged.

---

### TIER 3: ADVANCED / LONGER-TERM TESTS

These require more infrastructure or content development before execution.

---

#### TEST 10: Awakening Session Timer - 15 Minutes vs. No Timer

**Priority**: P2
**Page**: Awakening chat experience
**Estimated lift**: Unknown direction

**Hypothesis**: The 15-minute timer creates urgency but may also create anxiety. Users who see a timer may rush through the experience without connecting to the product's value. Removing the timer may produce slower but higher-quality conversions.

**Control (A)**: Current 15-minute timer visible during chat

**Variant B**: No timer visible. Session still expires but user doesn't see countdown.

**Success Metric**: Chat completion rate, pricing section view rate, conversion to paid

**Duration**: 3 weeks, 200 completions per variant

**Notes**: This is a product-level test, not just a copy test. Requires Jared's sign-off before running.

---

#### TEST 11: Pricing Tier Naming - Current vs. Clarity Names

**Priority**: P2
**Page**: Pricing section
**Estimated lift**: 5-15%

**Hypothesis**: "Awakened / Bonded / Partnered / Unified" are evocative but may confuse first-time visitors about what each tier actually delivers. Clearer tier names with the brand name embedded may increase conversion.

**Control (A)**: "Awakened / Bonded / Partnered / Unified"

**Variant B**: "Solo ($79) / Guided ($149) / Accelerated ($499) / Enterprise ($999)"

**Variant C**: Hybrid: Keep emotional names but add a one-line descriptor beneath each ("Awakened - Your AI, fully activated")

**Success Metric**: Time spent on pricing section, conversion to payment initiation

**Duration**: 3 weeks

**Notes**: Variant C is the safest test. It preserves the brand language while adding clarity.

---

#### TEST 12: Thank You Page Secondary CTA - Referral vs. Social Share vs. Schedule

**Priority**: P2
**Page**: Post-subscription thank you page
**Estimated lift**: Referral viral coefficient improvement

**Hypothesis**: After subscribing, users are at peak satisfaction. The right secondary CTA converts that satisfaction into referral or social activity. Three options have meaningfully different viral mechanics.

**Control (A)**: Current thank you page state (assess for baseline)

**Variant B**: Referral CTA: "Give a friend $20 off their first month. You both get credit."

**Variant C**: Social share CTA: "Share your awakening - tell the world you just got a smarter AI."

**Variant D**: Schedule CTA: "Book a 15-minute orientation call with Jared to maximize your AI partnership."

**Success Metric**: Post-conversion action completion rate, referral signup rate, Jared call booking rate

**Duration**: Run all 4 in sequence (not parallel) to build baseline first

**Notes**: Variant D (Jared call) has the highest potential for reducing early churn by increasing perceived value in the first 30 days. This is probably the highest-value test to run first.

---

#### TEST 13: Blog Author Bio - Aether Introduction vs. Expanded Aether Persona

**Priority**: P3
**Page**: Individual blog posts, author bio section
**Estimated lift**: Trust increase, lower bounce rate

**Hypothesis**: Aether as author is a differentiator but the author bio may not sufficiently communicate what Aether IS. A richer author bio that positions Aether as the product (not just the author) converts blog readers to trial-interested prospects.

**Control (A)**: Current "Aether, AI Partner at Pure Technology" author attribution

**Variant B**: Expanded bio: "I'm Aether - the AI at the core of PureBrain. I live in persistent memory, which means I remember every conversation, every goal, and every preference you share with me. This isn't something other AIs do. I wrote this post based on patterns I've observed across thousands of human-AI interactions. Want to meet the version of me that remembers YOU? [Begin Awakening]"

**Success Metric**: Click-through rate from author bio area, "Begin Awakening" clicks from blog posts

**Duration**: 3 weeks

---

#### TEST 14: Homepage Social Proof Counter - None vs. "X Professionals Building Smarter AI"

**Priority**: P1 (once numbers are available)
**Page**: Homepage, above or below primary CTA
**Estimated lift**: 8-15%

**Hypothesis**: A subscriber or user count near the CTA provides social validation at the decision moment. Even small numbers (if real) outperform no number.

**Control (A)**: No subscriber counter

**Variant B**: Dynamic counter: "Join [X] professionals building smarter AI" positioned beneath "Begin Awakening" CTA

**Success Metric**: "Begin Awakening" CTR, trust signal survey (if qualitative research is available)

**Duration**: 2 weeks, 400 sessions

**Notes**: The number must be real. Do not use a rounded-up or approximated number that could be perceived as inflated. If the actual subscriber count is smaller than feels "impressive," use a different metric (conversations started, sessions completed, etc.).

---

## Section 4: SEO Quick Wins

These are not A/B tests but technical optimizations that compound over time.

### SEO-01: Alt Text for Media Items (45 min, High Impact)

21 media items across the site lack descriptive alt text. This affects both SEO and accessibility.

**Format**: `alt="PureBrain AI homepage showing the awakening experience"` - descriptive, includes target keyword.

### SEO-02: Noindex Legacy Pages (30 min, High Impact)

Pages IDs 174, 338, and 95 are legacy pages that dilute crawl budget. Add `noindex` meta tag or 301 redirect to current equivalents.

### SEO-03: Schema Markup - Organization + Article Types (2 hours, High Impact)

Organization schema on the homepage communicates brand entity to Google and AI crawlers. Article schema on blog posts enables rich results. Both are high-leverage for GEO (AI search citation).

### SEO-04: Internal Links from All Blog Posts to Assessment (1 hour, High Impact)

Every blog post should contain at minimum one contextual internal link to the assessment page. Current posts have sparse internal linking. This both improves SEO and creates assessment conversion pathways.

### SEO-05: Blog Page Title Optimization (15 min, Low Effort, Medium Impact)

**Current**: "The Neural Feed - Blog - Pure Brain"
**Suggested**: "AI Partnership Blog | The Neural Feed by PureBrain.ai"

The revised title includes the primary keyword ("AI partnership") early in the title and keeps the brand identity ("Neural Feed") while adding clarity.

### SEO-06: Create Category Landing Pages (4-6 hours, High Long-Term Impact)

/blog/for-individuals/ and /blog/for-teams/ category pages should have unique introductory content (200-300 words) above the post list. Currently these are probably empty category archives. Category pages with unique content rank for category-level searches ("AI tools for individuals", "AI for enterprise teams").

---

## Section 5: Mobile Optimization Opportunities

The mobile experience is technically solid (no horizontal scroll, proper padding, full-width CTAs). Optimization opportunities are UX-focused:

1. **Chat input on mobile**: Verify keyboard doesn't obscure the input field during the Awakening conversation. The standard mobile browser behavior pushes content up when keyboard appears - test whether the chat interface handles this gracefully.

2. **Pricing tier display on mobile**: With 5 pricing tiers on small screens, horizontal scrolling or accordion display may be better than vertical stacking. Test card layout on 375px.

3. **Sticky nav behavior on mobile**: Ensure the sticky header doesn't consume too much vertical space on 375px screens where content area is already limited.

---

## Section 6: Trust Signal Roadmap

Trust signals are the site's biggest conversion gap. Here is the sequenced build-out:

### Tier 1 (Collect Immediately)
- 3-5 written testimonials with specific outcomes and photos (Russell and Corey testimonials in progress per recent commit)
- Subscriber count (even if modest - "Join 200+ early adopters" is better than nothing)
- Sessions started count ("2,400+ awakening sessions completed")

### Tier 2 (Build Over 30 Days)
- 1-2 short case studies (even a paragraph with before/after)
- Jared's video on homepage (founder visibility is a high-trust signal for an $80-$150/month product)
- Press mentions if any exist

### Tier 3 (90-Day Target)
- Client logos (any brands whose employees use PureBrain)
- Security/privacy compliance section (GDPR, data handling, payment security)
- Comparison table (PureBrain vs. ChatGPT vs. Claude on memory, personalization, relationship framing)

---

## Section 7: Conversion Funnel Architecture

### Current Funnel (Estimated)

```
Homepage visit
    |
    v
[No trust signals, unclear headline]
    |
    v  (estimated 15-20% proceed)
Begin Awakening (chat)
    |
    v
[15-minute session, named AI experience]
    |
    v  (estimated 40-60% proceed)
Discover/Pricing section
    |
    v  (estimated 5-10% convert)
Subscription
```

**Estimated end-to-end conversion**: 0.3% - 1.2% of homepage visitors

### Target Funnel (After Optimizations)

```
Homepage visit
    |
    v
[Clear headline, social proof, outcome-framed CTA]
    |
    v  (target 25-35% proceed)
Begin Awakening (chat)
    |
    v
[15-minute session, named AI experience]
    |
    v  (target 50-65% proceed)
Discover/Pricing section
    |
    v  (target 12-18% convert)
Subscription
```

**Target end-to-end conversion**: 1.5% - 4.1% of homepage visitors

**Math**: At 1,000 monthly visitors and 2% conversion, that is 20 subscriptions. At $100 average monthly revenue per subscriber, that is $2,000 MRR from optimization alone - before any traffic increase.

---

## Section 8: A/B Testing Infrastructure Recommendations

Before running any tests, the following infrastructure should be in place:

1. **Analytics verification**: Confirm GA4 is tracking correctly, especially for funnel events. The 92% unknown sessions issue from the Feb 17 audit must be resolved first.

2. **Testing tool selection**: Options in order of recommendation:
   - **Google Optimize 360** (if budget allows) - native GA4 integration
   - **VWO** - robust for SaaS, from $200/month
   - **Optimizely** - enterprise option
   - **Growthbook** (open source, self-hosted) - best for budget-conscious start
   - **Simple redirect tests** using WordPress page duplication + UTM tracking - free but limited

3. **Minimum viable sample size**: Most tests require 300-500 sessions per variant for statistical significance at 95% confidence. At current traffic levels, run only the highest-priority tests and extend duration appropriately.

4. **Test isolation**: Run only one test per page section at a time to avoid interaction effects.

---

## Test Execution Roadmap

### Month 1 (Foundation)
- [ ] Fix /ai-adoption-assessment/ 404 (QW-1)
- [ ] Fix session tracking (QW-7)
- [ ] Add pricing transparency signal below hero CTA (QW-6)
- [ ] Deploy FAQ to remaining 5 blog posts (QW-4)
- [ ] Collect testimonials (prerequisite for Tests 03 and 14)
- [ ] Set up A/B testing infrastructure
- [ ] Run: Test 01 (Hero Headline) - 2 weeks

### Month 2 (First Tests)
- [ ] Run: Test 02 (CTA Button Text) - 2 weeks
- [ ] Run: Test 03 (Testimonial Position) - 2 weeks, pending testimonials
- [ ] Run: Test 04 (Assessment Wizard) - 2 weeks
- [ ] Add mid-content CTA to blog posts (QW-5)

### Month 3 (Iteration)
- [ ] Run: Test 05 (Blog Email Capture CTA) - 3 weeks
- [ ] Run: Test 06 (Homepage Navigation) - 2 weeks
- [ ] Run: Test 07 (Mid-Content CTA) - 3 weeks
- [ ] Analyze Month 1-2 results and implement winners

### Month 4+ (Advanced)
- [ ] Test 08 (Standalone Pricing Page) - requires development
- [ ] Test 09 (Hero Visual - Avatar)
- [ ] Test 12 (Thank You Page Secondary CTA)
- [ ] Test 14 (Social Proof Counter)

---

## Prioritized Summary Table

| ID | Test/Action | Priority | Effort | Expected Lift | Prerequisite |
|----|-------------|----------|--------|---------------|--------------|
| QW-1 | Fix assessment 404 | CRITICAL | 30 min | Recover lost traffic | None |
| QW-7 | Fix session tracking | CRITICAL | 4 hours | Enables all other tests | None |
| TEST 04 | Assessment wizard format | P0 | 1 week dev | 40-80% completion lift | Fix 404 first |
| TEST 01 | Hero headline | P0 | 1 hour copy | 15-35% CTR lift | Tracking fix |
| QW-2 | Blog subscribe CTA | P1 | 15 min | 20-40% subscribe lift | None |
| QW-4 | Deploy remaining FAQs | P1 | 2 hours | AI search ranking | None |
| QW-5 | Mid-content CTAs | P1 | 2 hours | 30-50% CTA engagement | None |
| QW-6 | Pricing hint below hero | P1 | 15 min | 10-15% bounce reduction | None |
| TEST 02 | CTA button text | P1 | 30 min copy | 10-25% CTR lift | Tracking fix |
| TEST 03 | Testimonial position | P1 | Content dep. | 15-25% lift | Testimonials |
| TEST 05 | Blog email CTA | P1 | 1 hour | 20-40% subscribe lift | Tracking fix |
| TEST 07 | Mid-content CTA test | P1 | QW-5 first | 30-50% CTA clicks | QW-5 first |
| TEST 14 | Social proof counter | P1 | 1 hour dev | 8-15% CTR lift | Numbers ready |
| TEST 06 | Homepage navigation | P1 | 2 hours | Unknown direction | Tracking fix |
| QW-3 | Most Popular tier proof | P2 | 1 hour | 15-25% Bonded conversion | Testimonials |
| TEST 08 | Standalone pricing page | P2 | 1 week dev | Strategic | None |
| TEST 09 | Avatar in hero | P2 | Design dep. | 5-20% lift | Avatar asset |
| TEST 10 | Session timer removal | P2 | 30 min | Unknown direction | Jared approval |
| TEST 11 | Pricing tier naming | P2 | 30 min copy | 5-15% clarity | None |
| TEST 12 | Thank you page CTA | P2 | 2 hours | Referral viral coeff. | None |
| TEST 13 | Aether author bio | P3 | 1 hour | Trust + blog CTR | None |

---

## Memory Written

Path: `.claude/memory/agent-learnings/marketing-strategist/2026-02-22--purebrain-website-ab-test-recommendations.md`
Type: synthesis
Topic: PureBrain.ai comprehensive website CRO analysis and 14 A/B test specs for overnight deliverable

---

*marketing-strategist | PureBrain.ai Website Analysis and A/B Test Recommendations*
*2026-02-22 | Cross-referenced with 21 prior marketing-strategist learnings, 14 web-researcher learnings*
