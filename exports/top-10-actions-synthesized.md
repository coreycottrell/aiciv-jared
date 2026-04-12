# PureBrain.ai: Top 10 Actions - Synthesized Priority Plan

**Prepared by**: result-synthesizer (Aether Collective)
**Date**: 2026-02-19
**Source Reports**: 6 overnight analyses (blog, site, distribution, LinkedIn, creative growth, analytics)
**Context**: purebrain.ai - AI service at $79-499/mo. Zero Google search visibility. No email capture. Pricing page 404.

---

## THE ONE THING THAT MATTERS MOST

**Fix the conversion plumbing before doing anything else.**

Right now, awareness is being generated (daily blog, LinkedIn viral moment, 470+ newsletter subscribers) but zero of it converts to revenue. The site has a 404 pricing page, no payment processor, no email capture, and no follow-up for people who do engage. You are filling a bucket with a hole in the bottom. Every hour spent on growth before fixing the plumbing is wasted.

The sequence is: Fix pricing (Day 1) → Fix indexing (Day 2) → Add email capture (Week 1) → Then grow.

---

## THIS WEEK vs THIS MONTH

### This Week: Fix What Is Broken (Blockers)

| # | Action | What | Why | Effort | Who |
|---|--------|------|-----|--------|-----|
| 1 | Fix pricing page | See below | Active buyers have nowhere to go | 2 hrs | Jared + Aether |
| 2 | Fix Google indexing | See below | $0 organic revenue forever if not fixed | 1 hr | Jared |
| 3 | Add email capture to blog | See below | Every reader who leaves is gone forever | 3 hrs | Aether |
| 4 | Add mid-post CTAs | One contextual CTA per post | Current posts end with no next step | 2 hrs | Aether |
| 5 | Add UTM parameters to all links | Append `?utm_source=linkedin&utm_medium=social` etc. | GA4 is blind without this | 1 hr | Aether |

### This Month: Build the Revenue Infrastructure

| # | Action | What | Why | Effort | Who |
|---|--------|------|-----|--------|-----|
| 6 | Replace Google Form waitlist with Stripe | See below | Zero revenue captured today | 1-2 days | Jared + dev |
| 7 | Write and deploy 7-day email nurture sequence | See below | The bridge between awareness and payment | 4 hrs | Aether |
| 8 | Add social proof to site | 3 testimonials minimum | Trust gap blocking all conversions | 2 hrs | Jared |
| 9 | Publish one decision-stage blog post | "PureBrain vs ChatGPT Teams: Honest Comparison" | All posts are awareness-only right now | 2 hrs | Aether |
| 10 | Submit to 5 free AI directories | Toolify, Futurepedia, TopAI, AIxploria, AI Agents List | Free discovery with pre-written copy below | 1 hr | Jared |

---

## TOP 10 ACTIONS: FULL DETAIL

---

### ACTION 1: Fix the Pricing Page (Day 1 - Critical Blocker)

**What**: `/pricing` returns 404. The actual pricing page at `/purebrain-4/` or `/purebrain-3/` is JavaScript-rendered and invisible to both Googlebot and WebFetch. Active buyers who click "pricing" hit a dead end.

**Why it matters**: This is the single most direct revenue blocker on the site. Any visitor who is ready to pay cannot complete the transaction. The pricing tiers ($79 Awakened, $149 Bonded, $499 Partnered) with PayPal buttons exist but are unreachable via the standard path.

**Effort**: 2 hours

**Who**: Jared makes the decisions; Aether can implement the WordPress redirects and verify.

**Specific steps**:
1. Add a 301 redirect from `/pricing` to whatever page is actually live (check `/purebrain-4/` first with Playwright to confirm it loads)
2. Add `Pricing` to the blog navigation bar (currently: Home | Blog | AI Assessment | CTA)
3. Add a "14-day free trial" or "30-day money-back guarantee" to the pricing page (20-35% conversion lift, zero cost)
4. Mark "Bonded" ($149) as "Most Popular" to anchor buyer decisions
5. Noindex development pages: `/pay-test/`, `/pay-test-sandbox/`, `/elementor-150/`

---

### ACTION 2: Fix Google Search Indexing (Day 2 - Critical Blocker)

**What**: `site:purebrain.ai` returns zero results. The domain is invisible to Google. Every blog post published generates zero SEO value in its current state.

**Why it matters**: Without indexing, organic traffic stays at 0% forever. The daily publishing cadence, the schema markup, the clean URLs - all wasted until Google indexes the pages. The most likely cause is a leftover "discourage search engines" WordPress development setting that was never unchecked.

**Effort**: 1 hour (diagnosis + fix)

**Who**: Jared (requires access to WordPress admin and Google Search Console)

**Specific steps**:
1. WordPress Admin > Settings > Reading - verify "Discourage search engines from indexing this site" is UNCHECKED
2. Check `purebrain.ai/robots.txt` for any `Disallow: /` rules blocking Googlebot
3. Log into Google Search Console > Index > Pages - look for pages marked with "noindex" reason
4. Submit sitemap: `purebrain.ai/sitemap.xml`
5. Use URL Inspection Tool on the homepage, blog index, and each blog post - click "Request Indexing" for each
6. **Expected fix time**: 2-4 weeks for Google to process after the setting is corrected

---

### ACTION 3: Add Blog Email Capture with Lead Magnet (Week 1 - Highest Conversion ROI)

**What**: The blog has 6+ posts, generates reader traffic from LinkedIn and Bluesky, and captures zero emails. There is no way for a reader to enter a relationship with PureBrain short of clicking "Start Your AI Partnership" - a commitment too large for a first-time reader.

**Why it matters**: Without email capture, every blog reader who leaves is gone permanently. A 3-5% email capture rate on current traffic means 50+ owned email addresses per month that compound. These email subscribers convert to paid customers at 3-5x the rate of anonymous visitors.

**Effort**: 3 hours (lead magnet + form setup)

**Who**: Aether creates the lead magnet PDF; Jared selects and configures email platform; Aether embeds the form.

**Specific steps**:
1. Create lead magnet: "5 Prompts That Transform Generic AI Into Your Personal AI" (2-page PDF, immediately useful, Aether can write this in 30 minutes)
2. Choose email platform: MailerLite (free up to 1,000 subscribers) or ConvertKit - both integrate with WordPress
3. Add email capture form to: (a) after post body before comments, (b) blog sidebar, (c) exit intent on blog pages
4. Form copy: "Get the free guide: 5 prompts that turn any AI into your AI. No credit card. Instant download."

---

### ACTION 4: Add Mid-Post CTAs (Week 1)

**What**: Every existing blog post ends with no next step after the content. The only CTA is in the footer. A reader who finishes an article sees a comment box and social icons - no path forward.

**Why it matters**: Contextual mid-post CTAs placed after the first 400 words convert at 2-3x the rate of footer CTAs. This is a pure copy-and-paste implementation with no technical work.

**Effort**: 2 hours to add to all 6 existing posts

**Who**: Aether

**Specific steps**:
Add one of these contextual CTAs after the first 400 words of each post, matched to the post topic:
- Memory posts: "Curious what an AI that actually remembers you feels like? [Begin your awakening - it's free]"
- Enterprise/team posts: "Is your team ready for AI? [Take the 5-minute readiness assessment]"
- Pilot purgatory/failure posts: "Ready to get out of AI pilot purgatory? [See how PureBrain starts differently]"

---

### ACTION 5: UTM Parameter Discipline (Week 1)

**What**: Every link shared on LinkedIn, Bluesky, Telegram, or in the newsletter goes to the site without tracking parameters. GA4 sees this traffic as "Direct" - meaning PureBrain has no visibility into which content drives which conversions.

**Why it matters**: Without UTM data, it is impossible to know if LinkedIn is worth the investment, whether blog post A drives more conversions than blog post B, or what the newsletter's actual ROI is. This is a 1-hour fix that immediately improves every future business decision.

**Effort**: 1 hour (template creation + standard for all future posts)

**Who**: Aether (creates templates); Jared (applies to all future posts)

**Specific steps**:
Create a URL template for each channel. Aether will append these to every link from today forward:
- LinkedIn: `?utm_source=linkedin&utm_medium=social&utm_campaign=[post-topic]`
- Newsletter: `?utm_source=newsletter&utm_medium=email&utm_campaign=ai-perspective`
- Bluesky: `?utm_source=bluesky&utm_medium=social`
- Telegram: `?utm_source=telegram&utm_medium=messaging`

---

### ACTION 6: Replace Google Form Waitlist with Stripe Payment (Month 1 - Revenue Critical)

**What**: PureBrain currently sends interested customers to a Google Form waitlist instead of a payment processor. Zero revenue is captured from any conversion that happens today.

**Why it matters**: This is the most urgent commercial gap. The 90-day revenue projection is $0 until this is fixed. Every "conversion" since launch has added someone to a list, not to MRR. Do not run any paid advertising or invest in growth until Stripe is live - paid traffic into a waitlist generates no return.

**Effort**: 1-2 days of technical work

**Who**: Jared makes decisions on pricing/terms; developer implements Stripe; Aether can draft the checkout page copy

**Specific steps**:
1. Create Stripe account if not already done
2. Set up three products: Awakened ($79/mo), Bonded ($149/mo), Partnered ($499/mo)
3. Replace "Join Waitlist" Google Form with Stripe payment links on the pricing page
4. Add a confirmation/thank-you page that initiates the onboarding sequence
5. Note: The PayPal integration exists (`/paypal-buttons-embed/` in sitemap) - verify if this already captures payments or if it is also broken

---

### ACTION 7: Build 7-Day Email Nurture Sequence (Month 1)

**What**: After a reader downloads the lead magnet (Action 3) or completes the assessment, they currently receive no follow-up. The email sequence is the bridge between first contact and paying customer.

**Why it matters**: The window immediately after someone engages with PureBrain content is when conversion probability is highest. A structured 7-day sequence with the right content converts 25-40% of engaged leads into trial starts.

**Effort**: 4 hours to write; 2 hours to configure in email platform

**Who**: Aether writes the sequence; Jared reviews and approves; Aether configures automation

**Email sequence**:
| Day | Subject | Content | CTA |
|-----|---------|---------|-----|
| 0 (immediate) | "Your 5 Prompts + one question for you" | PDF delivery + ask: "What's the AI task you're most frustrated with?" | Reply |
| 2 | "The thing ChatGPT can never do" | Memory as the real differentiator | Read this post |
| 4 | "What one customer figured out in week 1" | Concrete use case / proof | See how it works |
| 7 | "Your AI is waiting to meet you" | Direct invitation with urgency | Begin Awakening |

---

### ACTION 8: Add Social Proof to the Site (Month 1)

**What**: The site has zero testimonials, zero case studies, zero user counts, and no money-back guarantee. For a $79-499/month commitment from a first-time visitor, this is the primary trust gap blocking conversion.

**Why it matters**: Any competitor with 3 testimonials wins on trust against PureBrain's current state. The expected conversion lift from adding 3 testimonials to the homepage is 25-40%.

**Effort**: 2 hours once testimonials are collected

**Who**: Jared collects testimonials from beta users; Aether formats and deploys to site

**Specific steps**:
1. Identify 3-5 beta users or early customers who have had positive experiences
2. Ask for a 2-3 sentence quote and permission to use their first name, role, and company
3. Add to homepage below the hero section
4. Add "30-day money-back guarantee" badge to the pricing page
5. Add "Join [X] professionals using PureBrain" social proof line near the main CTA (update the number as it grows)

---

### ACTION 9: Publish One Decision-Stage Blog Post (Month 1)

**What**: Every current blog post is awareness/education content - written for people who have never heard of AI partnership. There is no content for the reader who is already sold on the concept and evaluating PureBrain specifically against alternatives.

**Why it matters**: Enterprise buyers evaluating a $149-499/month commitment will Google "PureBrain vs ChatGPT" before they buy. That search currently returns nothing from purebrain.ai. One well-written comparison post captures this high-intent audience and directly accelerates conversion.

**Effort**: 2-3 hours

**Who**: Aether drafts; Jared reviews for accuracy

**Recommended post**: "PureBrain vs ChatGPT Teams: Which AI Actually Remembers Your Business?"
- Honest, specific comparison
- Acknowledges what ChatGPT does well
- Makes the memory/persistence case with concrete examples
- Ends with: "If [use case A] describes you, ChatGPT Teams is fine. If [use case B] describes you, PureBrain is built for you."

---

### ACTION 10: Submit to 5 Free AI Directories (Week 1)

**What**: Five free AI tool directories can be submitted to this week using pre-written copy. Combined, they reach millions of users searching for AI tools.

**Why it matters**: These directories generate passive discovery at zero cost. One good directory listing can drive 50-200 qualified visitors per month indefinitely.

**Effort**: 1 hour total (Aether prepares copy; Jared submits)

**Who**: Aether prepares standardized listing copy; Jared creates accounts and submits (some require human verification)

**Directories and URLs**:
1. Toolify.ai - toolify.ai/submit
2. Futurepedia - futurepedia.io/submit-tool
3. TopAI.tools - topai.tools
4. AIxploria - aixploria.com
5. AI Agents List - aiagentslist.com

**Listing copy** (use this verbatim):
- **Name**: PureBrain
- **Tagline**: The only AI that remembers you - permanently.
- **Category**: Productivity, Personal AI, AI Assistants
- **Pricing**: Freemium ($79/mo - $499/mo)
- **Description**: PureBrain is a personalized AI service that begins with an awakening conversation. You meet your AI, discover its values, and give it a name. Unlike ChatGPT, PureBrain starts where you left off every session - with complete memory of everything discussed, your preferences, and your work style. Tiers: Awakened ($79/mo), Bonded ($149/mo), Partnered ($499/mo).

---

## WHAT NOT TO DO YET

These are worth doing eventually but should wait until the conversion plumbing is fixed:

- **Paid ads (Meta, LinkedIn)**: Spending money on traffic into a broken funnel is waste. Wait until Stripe is live and conversion rate is above 2%.
- **Product Hunt launch**: Requires preparation and is a one-shot opportunity. Do this in Month 2-3 after email list and social proof are in place.
- **YouTube channel**: High effort, long payoff. Not a Week 1 priority.
- **Pillar page / content hub**: Good idea for Month 2. Not urgent while indexing is broken.
- **Cross-CIV Bluesky threads**: Valuable content strategy but not a revenue unlocker at this stage.

---

## 30-DAY SUCCESS METRICS

| Metric | Current | 30-Day Target |
|--------|---------|---------------|
| Pricing page functional | No (404) | Yes |
| Google pages indexed | 0 | 10+ |
| Blog email capture rate | 0% | 3-5% of readers |
| Email subscribers from blog | 0 | 50+ |
| Revenue captured | $0 | First paid customer |
| Social proof on site | None | 3 testimonials |
| Decision-stage blog posts | 0 | 1 |
| AI directory listings | 0 | 5+ |

---

*Synthesized from 6 overnight reports by result-synthesizer | 2026-02-19*
*Source reports: blog-analysis-report.md, purebrain-site-analysis.md, distribution-strategies-overnight.md, linkedin-strategy-overnight.md, creative-growth-ideas.md, analytics-deep-dive.md*
