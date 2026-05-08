# BrainScore Full Buildout Plan
## What We Have vs What We Need to Match/Beat ARA Index

---

## WHAT WE HAVE NOW (MVP)

| Dimension | Status | Scoring |
|-----------|--------|---------|
| A1 Structural Readiness | LIVE | robots.txt, llms.txt, schema.org, meta tags, OG tags (0-20) |
| A2 Semantic Clarity | PLACEHOLDER (0) | Not built |
| A3 Synthetic Customer Test | LIVE | Claude + GPT-4o recommendations (0-20) |
| A4 Emotional Residue | PLACEHOLDER (0) | Not built |
| A5 Voice & Archetype | PLACEHOLDER (0) | Not built |

**Current output:** Total score 0-100, tier badge, 5 dimension bars (2 real, 3 placeholder)

---

## WHAT ARA INDEX HAS THAT WE DON'T (YET)

### 1. FOUR AI MODELS (they use 4, we use 2)
They test: Claude Sonnet, GPT-4o, Perplexity Sonar-pro, Gemini 2.5-flash
We test: Claude, GPT-4o only

**Fix:** Add Perplexity API + Gemini API calls to synthetic test. Build time: 2 hours.

### 2. SEMANTIC CLARITY DIMENSION (A2)
They check if AI uses the brand's OWN vocabulary vs competitor framing.
Method: Ask AI to describe the brand → analyze if response uses the brand's language or competitor comparisons.

**How to build:**
- Prompt each AI model: "Describe [brand] in 3 sentences"
- Score: Does it use brand's own words (from their website) or say "like [competitor]"?
- Scrape brand's homepage for key positioning terms → compare against AI descriptions
- Build time: 4 hours

### 3. EMOTIONAL RESIDUE DIMENSION (A4)
They check if AI carries cultural narrative about the brand.
Method: Ask AI about brand associations, sentiment, cultural moments.

**How to build:**
- Prompt: "What cultural associations does [brand] have? What emotions does it evoke?"
- Score: Specific associations (high) vs generic ("it's fun", low) vs nothing (zero)
- Build time: 3 hours

### 4. VOICE & ARCHETYPE DIMENSION (A5)
They check if brand identity survives without visuals (voice/text only).
Method: Ask AI to describe the brand's personality/archetype.

**How to build:**
- Prompt: "What is [brand]'s brand personality? What archetype does it represent?"
- Score: Clear archetype named (high) vs generic descriptors (low) vs nothing (zero)
- Build time: 2 hours

### 5. DETAILED RUBRIC BREAKDOWN PER DIMENSION
They show tiered rubric (Awesome/Strong/Average/Weak/Invisible) with specific criteria per dimension, not just a number.

**How to build:**
- Add rubric text to each dimension result
- Show what "Awesome" looks like vs what the brand scored
- "You scored 8/20 because [specific reasons]. To reach 17+, you need [specific actions]."
- Build time: 3 hours (content + frontend)

### 6. COMPETITIVE BENCHMARKING
They score against competitors in the same category.
"You scored 45, your top competitor scored 78."

**How to build:**
- When user enters brand + industry, also score 2-3 top competitors automatically
- Show comparison chart
- Build time: 4 hours (but costs 3x API calls per scan)

### 7. ACTIONABLE RECOMMENDATIONS
They provide a "prioritized roadmap to move the number."

**How to build:**
- Based on which dimensions scored low, generate specific recommendations
- Low structural → "Add schema.org markup, create llms.txt"
- Low synthetic → "Publish authoritative content about [category], get mentioned in industry lists"
- Low semantic → "Strengthen your brand voice on your website, use consistent positioning language"
- Build time: 3 hours

### 8. EMAIL-GATED FULL REPORT
Free: See your score + tier
Email gate: See detailed breakdown + recommendations + competitive comparison

**How to build:**
- Score animation shows on page (no gate)
- "Get Full Report" button → email capture → detailed PDF or expanded view
- Captures lead for sales follow-up
- Build time: 2 hours

---

## WHAT WE CAN DO THAT ARA CAN'T

### 1. REAL-TIME SCORING (they do manual audits, we do instant)
ARA requires "requesting an audit" — manual process. BrainScore scores instantly. This is our #1 differentiator.

### 2. BEFORE/AFTER TRACKING
"Your BrainScore was 45 in May. After 3 months with PureBrain, it's 72."
Track scores over time per brand. Show improvement. This ties directly to PureBrain subscription value.

### 3. AI PARTNER UPSELL
"Your BrainScore is 45 (Weak). A PureBrain AI partner can help improve your structural readiness, content strategy, and brand voice. Get started →"
Every low score = direct sales funnel.

### 4. CATEGORY LEADERBOARDS (public)
"Top 10 AI-ready brands in [Payments / SaaS / Fitness / etc.]"
Publishable content that drives organic traffic + brand awareness.

---

## BUILD PRIORITY (what to do first)

| Priority | Task | Time | Impact |
|----------|------|------|--------|
| 1 | Add Perplexity + Gemini to synthetic tests | 2 hrs | 4 models vs 2 = more credible |
| 2 | Build Semantic Clarity (A2) dimension | 4 hrs | Score jumps from 2 to 3 real dimensions |
| 3 | Email-gated full report | 2 hrs | Lead capture = revenue |
| 4 | Actionable recommendations engine | 3 hrs | Makes report valuable, not just a number |
| 5 | Build Emotional Residue (A4) | 3 hrs | 4 of 5 dimensions live |
| 6 | Build Voice & Archetype (A5) | 2 hrs | All 5 dimensions complete |
| 7 | Competitive benchmarking | 4 hrs | "You vs competitors" is compelling |
| 8 | Before/after tracking | 3 hrs | Ties to PureBrain subscription value |

**Total to match ARA: ~23 hours of build time**
**Total to BEAT ARA: ~30 hours (add real-time, tracking, upsell)**

---

## WHAT THE FULL REPORT SHOULD LOOK LIKE (email-gated)

**Page 1: Score Overview**
- BrainScore: 45/100 (Weak)
- Score ring animation
- 5 dimension bars with labels

**Page 2: Dimension Details (SAVE HALF FOR FULL REPORT)**
- Each dimension: score, rubric level, key findings, what's working, what's missing
- Specific evidence: "Claude says [X] about your brand, GPT says [Y]"

**Page 3: Recommendations (FULL REPORT ONLY)**
- Prioritized actions to improve each dimension
- "Add llms.txt to your site" → estimated +3 points
- "Publish 5 authoritative blog posts about [category]" → estimated +5 points
- "Strengthen brand voice consistency" → estimated +4 points

**Page 4: Competitive Comparison (FULL REPORT ONLY)**
- Your score vs top 3 competitors
- Where you win, where you lose
- Opportunity gaps

---

*BrainScore by PureBrain — "The SEO audit of the AI era"*
