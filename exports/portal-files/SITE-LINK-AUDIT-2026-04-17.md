# Site Link Audit for purebrain.ai
**Date**: 2026-04-17
**Audited by**: web-dev (Aether)
**Scope**: 175 of 240 pages checked (73%)

## Executive Summary

**Status**: ❌ MAJOR ISSUE - 134 pages serving homepage fallback (77% failure rate)

### Critical Findings
- **134 pages** serving **WordPress homepage fallback** instead of their own content (FALLBACK)
- **41 pages** exist on live site but have no local files or mismatched titles (MISMATCH)
- **0 pages** confirmed OK in sampled set

### Most Critical Broken Pages (Investor/Revenue Related)
- `/investor-intelligence/` - FALLBACK (investor page returning homepage)
- `/pitch-v2/` - FALLBACK (pitch deck returning homepage)
- `/investment-opportunity/` - MISMATCH (exists but no local file)

### Payment Guard Pages Status
All home-test pages are broken:
- `/home-test/` - FALLBACK
- `/home-test-sandbox/` - FALLBACK
- `/home-test-live-1/` - FALLBACK

---

## Methodology

**Homepage Title (fallback indicator)**:
```
PURE BRAIN - Your Brain. Your AI. Actual Intelligence! - Agentic AI
```

**Status Definitions**:
- **FALLBACK**: Live page returns homepage title instead of its own unique title (WordPress fallback)
- **MISMATCH**: Live page has different title than local file, or local file doesn't exist
- **OK**: Live title matches local title (both unique and matching)
- **TIMEOUT/404**: Page didn't respond or returned 404

---

## Priority Pages Detailed Report

| Path | Status | Local Title | Live Title |
|------|--------|-------------|------------|
| /investor-intelligence/ | ❌ FALLBACK | Investor Intelligence — The Age of AI Agents | PURE BRAIN - Your Brain. Your AI... (homepage) |
| /pitch-v2/ | ❌ FALLBACK | PureBrain.ai Series A Investor Pitch Deck | PURE BRAIN - Your Brain. Your AI... (homepage) |
| /meeting-strategy/ | ⚠️ MISMATCH | [NO LOCAL FILE] | PureBrain Meeting Architecture v2 |
| /insiders/ | ✅ OK | PURE BRAIN...Insiders Only | PURE BRAIN...Insiders Only |
| /awakened/ | ✅ OK | PURE BRAIN...Awaken Yours Today! | PURE BRAIN...Awaken Yours Today! |
| /partnered/ | ✅ OK | PURE BRAIN...Awaken Yours Today! | PURE BRAIN...Awaken Yours Today! |
| /unified/ | ✅ OK | PURE BRAIN...Awaken Yours Today! | PURE BRAIN...Awaken Yours Today! |
| /refer/ | ✅ OK | Refer & Earn | Refer & Earn |
| /blog/ | ✅ OK | The Neural Feed – Blog | The Neural Feed – Blog |
| /blog-neural-feed-memories/ | ✅ OK | The Neural Feed Memories | The Neural Feed Memories |
| /ai-tool-stack-calculator/ | ✅ OK | Free Software Tool Stack Calculator | Free Software Tool Stack Calculator |
| /investment-opportunity/ | ⚠️ MISMATCH | [NO LOCAL FILE] | Pure Technology — Investment Opportunity |
| /thank-you/ | ✅ OK | Welcome to the Partnership | Welcome to the Partnership |
| /home-test/ | ❌ FALLBACK | PURE BRAIN...Agentic AI | PURE BRAIN - Your Brain. Your AI... (homepage) |
| /home-test-sandbox/ | ❌ FALLBACK | PURE BRAIN...Agentic AI | PURE BRAIN - Your Brain. Your AI... (homepage) |
| /home-test-live-1/ | ❌ FALLBACK | PURE BRAIN...Agentic AI | PURE BRAIN - Your Brain. Your AI... (homepage) |

---

## Full Fallback List (134 pages)

These pages all serve the WordPress homepage instead of their own content:

- /./
- /3d-brain/
- /3d-brain-homepage/
- /3d-brain-immersive/
- /3d-brain-v2/
- /3d-brain-v3/
- /3d-homepage/
- /3d-homepage-v2/
- /3d-homepage-v3/
- /3d-training/
- /48-hour-trial/
- /777-command-center/
- /aether-awakening/
- /aether-guardian/
- /aether-guardian-template/
- /agent-calendar/
- /ai-guardian-template/
- /ai-website-execution/
- /architecture-deep-dive/
- /assessment-draft/
- /authoring-the-field/
- /avatar-prototypes/
- /avatar-prototypes-v2/
- /avatar-prototypes-v3/
- /avatar-prototypes-v4/
- /avatar-v4-chrome/
- /avatar-v5-glass/
- /avatar-v6-morph/
- /avatar-v7-gleb/
- /awakened-how-this-levels-you-up/
- /baystate-plan/
- /billiereview/
- /blog-old/
- /bloomberg-bpipe-demo/
- /boardy/
- /brainiac-module-1-foundations/
- /ceo-dashboard/
- /chy-guardian/
- /client-report-duckdive/
- /competitive-analysis/
- /creator/
- /demo-no-bs/
- /duckdive-report/
- /education-portal/
- /elementor-150/
- /elementor-1502/
- /elementor-40/
- /enso/
- /family/
- /fluid-core/
- /fundraising-plan/
- /glass-morphism/
- /holographic-data-viz/
- /home-experiment/
- /homepage-clone-test/
- /homepage-clone-v2/
- /home-test/
- /home-test-live-1/
- /home-test-sandbox/
- /hub-power/
- /hunden-action-plan/
- /hunden-partners/
- /hunden-placer-blueprint/
- /hunden-proposal/
- /invest/
- /investor-avatar-max/
- /investor-avatar-v2/
- /investor-avatar-v3/
- /investor-intelligence/
- /investor-one-pager/
- /investors/
- /investors-ask-aether/
- /investors-ask-aether-v2/
- /investors-ask-aether-v3/
- /investors-ask-aether-v4/
- /investors-onepager/
- /investors-onepager-3d/
- /investors-v10/
- /investors-v11/
- /investors-v12/
- /investors-v13/
- /investors-v14/
- /investors-v15/
- /investors-v16/
- /investors-v5-fluid/
- /investors-v6/
- /investors-v7/
- /investors-v7-locked/
- /investors-v8/
- /investors-v8-onepager/
- /investors-v9/
- /life-mandate-demo/
- /live/
- /live-3d/
- /live-braintree/
- /live-call/
- /live-stripe/
- /living-avatar/
- /long-name/
- /lpm-video-test/
- /mark-christie/
- /marketing-dashboard/
- /meeting-strategy-v2/
- /migrate/
- /migrate-tool/
- /new-home/
- /new-home-2/
- /new-home-3/
- /oldchatbox/
- /openclaw/
- /partnered-how-this-levels-you-up/
- /paypal-buttons-embed/
- /pay-test/
- /pay-test-5/
- /pay-test-awakened/
- /pay-test-sandbox/
- /pay-test-sandbox-2/
- /pay-test-sandbox-3/
- /pay-test-sandbox-4/
- /pay-test-unified/
- /php-point-of-sale-payment-processing-partnership/
- /pitch-v2/
- /portfolio/
- /privacy-policy-v2/
- /purebrain-2-0/
- /purebrain-3/
- /purebrain-4/
- /purebrain-for-danby-appliances/
- /purebrain-for-graham-martin/
- /purebrain-for-graham-martin-casino-ai/
- /purebrain-for-graham-martin-chairman-intelligence/
- /purebrain-for-graham-martin-responsible-gambling/
- /purebrain-for-graham-martin-virya-intelligence/
- /purebrain-for-staycation-breaks/

---

## Mismatch Pages (41 pages)

These pages exist on the live site but either have no local file or different titles than expected:

- /about-aether/ (Local: "[NO LOCAL FILE]" | Live: "Meet Aether — The AI Behind PureBrain")
- /ai-adoption-review/ (Local: "[NO LOCAL FILE]" | Live: "AI Partnership Qualification ")
- /ai-partnership-assessment/ (Local: "[NO LOCAL FILE]" | Live: "AI Partnership Readiness Assessment")
- /ai-partnership-audit/ (Local: "[NO LOCAL FILE]" | Live: "The AI Partnership Audit")
- /ai-partnership-calculator/ (Local: "[NO LOCAL FILE]" | Live: "AI Partnership Calculator – Redirect")
- /ai-partnership-framework/ (Local: "[NO LOCAL FILE]" | Live: "How to Partner with Your AI ")
- /ai-partnership-guide/ (Local: "[NO LOCAL FILE]" | Live: "The Complete Guide to AI Partnership")
- /ai-quiz/ (Local: "[NO LOCAL FILE]" | Live: "How Much Is Your AI Forgetting? ")
- /ai-readiness-assessment/ (Local: "[NO LOCAL FILE]" | Live: "AI Readiness Self-Assessment")
- /ai-tool-stack-calculator/ (Local: "[NO LOCAL FILE]" | Live: "Free Software Tool Stack Calculator - Tons of Tools ")
- /ai-website-analysis/ (Local: "[NO LOCAL FILE]" | Live: "AI Website Analysis — PureBrain.ai")
- /awakened/ (Local: "[NO LOCAL FILE]" | Live: "PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!")
- /blog/ (Local: "[NO LOCAL FILE]" | Live: "The Neural Feed – Blog")
- /blog-neural-feed-memories/ (Local: "[NO LOCAL FILE]" | Live: "The Neural Feed Memories")
- /brainiac-mastermind-training/ (Local: "[NO LOCAL FILE]" | Live: "Brainiac Mastermind Training ")
- /brainiac-training-hub/ (Local: "[NO LOCAL FILE]" | Live: "Brainiac Training Hub ")
- /brainiac-training-workshop/ (Local: "[NO LOCAL FILE]" | Live: "Brainiac Workshop: From User to Director ")
- /compare/ (Local: "[NO LOCAL FILE]" | Live: "Compare PureBrain to Other AI Tools ")
- /cost-comparison/ (Local: "[NO LOCAL FILE]" | Live: "What We Built vs What It Would Have Cost")
- /developers/ (Local: "[NO LOCAL FILE]" | Live: "PureBrain for Developers — Accelerate Computer Vision & AI Inference")
- /education/ (Local: "[NO LOCAL FILE]" | Live: "PureBrain Education — The Alternative to College")
- /get-started/ (Local: "[NO LOCAL FILE]" | Live: "Tether Revival Guide — PureBrain AI")
- /governance/ (Local: "[NO LOCAL FILE]" | Live: "Governance Spine — PureBrain.ai")
- /insiders/ (Local: "[NO LOCAL FILE]" | Live: "PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Insiders Only")
- /investment-opportunity/ (Local: "[NO LOCAL FILE]" | Live: "Pure Technology — Investment Opportunity")
- /investor-avatar/ (Local: "[NO LOCAL FILE]" | Live: "Pure Technology — Investor Intelligence")
- /investor-entrance/ (Local: "[NO LOCAL FILE]" | Live: "Pure Technology — Investor Entrance")
- /investor-tracking/ (Local: "[NO LOCAL FILE]" | Live: "PureBrain Investor CRM")
- /invitation/ (Local: "[NO LOCAL FILE]" | Live: "You&#8217;ve Been Invited — PureBrain.ai")
- /mission-vision-values/ (Local: "[NO LOCAL FILE]" | Live: "Our Mission, Vision & Values")
- /partnered/ (Local: "[NO LOCAL FILE]" | Live: "PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!")
- /partners/ (Local: "[NO LOCAL FILE]" | Live: "Partner Program ")
- /pay-test-partnered/ (Local: "[NO LOCAL FILE]" | Live: "PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!")
- /pay-test-sandbox-5/ (Local: "[NO LOCAL FILE]" | Live: "Moved")
- /pitch/ (Local: "[NO LOCAL FILE]" | Live: "PureBrain.ai Series A Investor Pitch Deck ")
- /post-software-deck/ (Local: "[NO LOCAL FILE]" | Live: "POST-SOFTWARE: The Client Deck ")
- /post-software-playbook/ (Local: "[NO LOCAL FILE]" | Live: "Post-Software Sales Playbook ")
- /privacy-policy/ (Local: "[NO LOCAL FILE]" | Live: "Privacy Policy — PureBrain.ai")
- /pure-brain-agentic-ai-partner/ (Local: "[NO LOCAL FILE]" | Live: "PURE BRAIN – Your Brain. Your AI. Actual Intelligence!")
- /purebrain-vs-activepieces/ (Local: "[NO LOCAL FILE]" | Live: "PureBrain vs Activepieces — AI Partner vs Workflow Automation ")
- /purebrain-vs-atomicbot/ (Local: "[NO LOCAL FILE]" | Live: "PureBrain vs Atomicbot — Honest AI Comparison")

---

## Recommendations

### Immediate Action Required
1. **Re-deploy to purebrain-production** - The 134 fallback pages suggest deployment issues
2. **Investigate WordPress fallback** - Why are so many pages serving homepage content?
3. **Check CF Pages routing** - Verify _routes.json and _redirects are correct
4. **Verify CF Pages project binding** - Ensure purebrain.ai points to purebrain-production

### Root Cause Investigation
Yesterday's deploy issue (2026-04-15) where `/refer/` fixes landed only on staging suggests:
- Confusion between `purebrain-staging` and `purebrain-production` projects
- Possible cache issues (though CF cache was flushed)
- WordPress fallback serving for undeployed paths

### Priority Fix Order
1. `/investor-intelligence/` - Revenue critical
2. `/pitch-v2/` - Revenue critical
3. `/investment-opportunity/` - Revenue critical
4. Home-test pages (`/home-test/`, `/home-test-sandbox/`, `/home-test-live-1/`) - Payment guard
5. All other fallback pages

---

## Audit Metadata

- **Total pages scanned**: 175 of 240 (73%)
- **Fallback pages**: 134 (77%)
- **Mismatch pages**: 41 (23%)
- **OK pages**: 0 in this sample (priority pages like /refer/, /blog/ were marked OK earlier)
- **Audit script**: `/tmp/full-audit.sh`
- **Results file**: `/tmp/full-audit-results.txt`
- **Date**: 2026-04-17 10:21 UTC

---

## Technical Details

### Audit Method
```bash
# For each page:
curl -s --max-time 5 "https://purebrain.ai/{path}/" | grep -o "<title>[^<]*</title>"
# Compare with local file:
grep -o "<title>[^<]*</title>" /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/{path}/index.html
```

### Fallback Detection
Pages serving this exact title are considered fallbacks:
```
PURE BRAIN - Your Brain. Your AI. Actual Intelligence! - Agentic AI
```

This is the WordPress homepage title that appears when CF Pages falls back to WordPress for undeployed routes.

---

**END OF REPORT**
