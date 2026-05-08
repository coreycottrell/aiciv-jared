# marketing-strategist Learning: Distribution v2 Implementation Specs

**Date**: 2026-04-19
**Type**: synthesis
**Agent**: marketing-strategist
**Confidence**: high
**Tags**: distribution, purebrain, calculator, brevo, nurture, referral, linkedin, flywheel, wrapped

---

## Task Summary

Built v2 implementation specs with exact HTML/JS/copy for 5 workstreams. This edition moves from STRATEGY to EXECUTION.

Output: `/home/jared/exports/portal-files/OVERNIGHT-DISTRIBUTION-V2-2026-04-19.md`

---

## Key Technical Finding

The calculator email capture EXISTS but sends to `api.purebrain.ai/api/investor-inquiry` only -- NOT Brevo. Leads enter the database and get zero follow-up. The fix is a 2-hour Cloudflare Worker proxy (`/api/brevo-subscribe`) that forwards to Brevo's contacts API. This is the #1 revenue leak.

## What Was Delivered

1. **Calculator email gate**: Full CSS/JS spec for blur-gate upgrade + Brevo API integration code
2. **5-email Brevo nurture**: Complete subject lines, preview text, body copy for all 5 emails with personalization variables (STACK_COST, TOOL_COUNT, RECOMMENDED_PLAN, ESTIMATED_SAVINGS)
3. **Referral activation email**: Template Jared sends to 30 customers, with personalization guide by customer type
4. **LinkedIn engagement bot**: Architecture spec for PureSurf-powered daily ICP commenting with safety rails
5. **Content flywheel**: Exact 8-asset breakdown from "Context Tax" blog post with copy for LinkedIn, Bluesky (5 posts), newsletter, FAQ schema, calculator CTA card, audio spec, quote graphic spec
6. **PureBrain Wrapped**: Full implementation plan for Spotify Wrapped-style quarterly report (voted top surprise-and-delight idea)

## Patterns Confirmed

- Calculator-to-Brevo connection is the single highest-leverage fix (11 editions running)
- Nurture emails work best with personalized data from the calculator (not generic)
- Email 4 (Naming Ceremony) is the differentiation email -- emotional, not logical
- PureBrain Wrapped has highest viral coefficient of all surprise-and-delight ideas (shareable artifact + social proof)

---

**END MEMORY**
