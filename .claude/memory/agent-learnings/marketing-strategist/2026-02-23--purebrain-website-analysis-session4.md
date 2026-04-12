# marketing-strategist Learning: PureBrain Website Analysis Session 4 — New Findings

**Date**: 2026-02-23
**Type**: synthesis
**Agent**: marketing-strategist
**Confidence**: high

---

## Task Summary

Fourth comprehensive website analysis of purebrain.ai. Specifically avoided repeating Sessions 1-3 content. Used WordPress REST API data, live WebFetch of 7 pages, and prior memory context to identify new conversion gaps not previously covered.

---

## Key New Discoveries

### 1. Three Lead Capture Pages Exist With No Escalation Architecture

PureBrain has three separate lead capture tools (Assessment, Audit, Adoption Review) that are parallel alternatives rather than a sequential escalation ladder. A visitor completing one is not offered the next. This wastes warm lead momentum. The fix is a commitment escalation sequence: Assessment → Adoption Review (for "Ready" scorers) → Audit (for qualified leads). No prior session identified all three pages or their relationship problem.

### 2. AI Partnership Guide Is Ungated — Significant Missed Lead Capture

The 7-section AI Partnership Guide at /ai-partnership-guide/ is freely accessible. This is the most substantive freely available content on the site. Gating it behind an email form (with a 7-part email series delivery) converts the highest-intent traffic segment (people reading a full guide) into named subscribers. Expected capture rate: 15-25% of guide visitors.

### 3. Thank You Page Is a Dead End

The post-purchase Thank You page has zero secondary conversion elements: no social sharing, no referral mechanism, no testimonials, no upsell path, and a brand-inconsistent support email (puremarketing.ai instead of purebrain.ai). The moment immediately after purchase is peak enthusiasm — this is where referrals happen. The page wastes this moment with only "Return to Homepage."

### 4. Four Development Pages Are Publicly Accessible and Crawlable

REST API reveals 17 published pages. Four are pay-test/sandbox pages: /pay-test/, /pay-test-sandbox/, /pay-test-2/, /pay-test-sandbox-2/. These are publicly accessible, brand-credibility risks, and waste Google crawl budget. Fix: noindex in Yoast or password-protect. Legacy pages /purebrain-2-0/, /purebrain-3/, /blog-old/ also need noindex.

### 5. Assessment Score Buckets Send All Visitors to the Same Purchase CTA

Assessment has three score buckets (Ready / Friction / Starting Line) but all three CTA buttons go to the same #awakening purchase URL. "Starting Line" visitors (low readiness, low budget willingness) are being sent to a $79-999/month pricing page. Matching CTAs to score buckets (Starting Line → free guide nurture, Friction → guide + light CTA, Ready → purchase) is the highest-ROI assessment fix.

### 6. Category Architecture Has a Single-Post Category

The AI Strategy category (ID 5) has only 1 post. A single-post category archive is an SEO dead end. Either merge into AI Insights or build to 5+ posts before maintaining as separate category.

---

## Patterns Worth Noting

### Assessment-to-Purchase Gap Pattern

Quiz/assessment tools collect warm leads but have a natural gap between "completed quiz" and "purchased product." The gap is filled by: (1) score-matched CTAs, (2) post-result email sequence triggered by score bucket, (3) benchmark comparisons ("You scored higher than X% of users") that make scores feel meaningful enough to act on. PureBrain currently uses none of these three gap-fillers.

### Ungated Long-Form Content Pattern

Long-form guides are the highest-intent content type on any site. Visitors reading 7-section guides are not casually browsing. Leaving this content ungated is equivalent to putting your highest-converting sales conversation in the lobby with no one to follow up. Gate long-form content at section 2, deliver rest via email.

### Post-Conversion Opportunity Pattern

The Thank You page is consistently underutilized across SaaS products. At peak enthusiasm, buyers are most likely to share, refer, and upgrade. Dropbox built significant early growth from post-signup referral prompts. A simple LinkedIn share button with pre-written copy on the Thank You page costs 1 hour of development and produces ongoing referral traffic.

---

## A/B Tests Added (Tests 15-20)

- Test 15: Score-matched assessment CTAs (HIGH priority)
- Test 16: AI Partnership Guide gate (HIGH priority)
- Test 17: Thank You page referral vs. homepage return (MEDIUM-HIGH)
- Test 18: Assessment Q6 context copy (MEDIUM)
- Test 19: Adoption Review as post-assessment escalation (MEDIUM)
- Test 20: Blog nav "Free AI Assessment" copy (LOW-MEDIUM)

---

## File Reference

Full analysis: `/home/jared/projects/AI-CIV/aether/exports/overnight-content/purebrain-website-analysis-session4.md`

Prior sessions:
- Session 3 (Feb 22): `/home/jared/projects/AI-CIV/aether/exports/overnight-content/website-analysis-ab-tests.md`
- Web researcher (Feb 21): `.claude/memory/agent-learnings/web-researcher/2026-02-21--purebrain-website-cro-analysis.md`

---

**END MEMORY**
