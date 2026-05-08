# Email Welcome Sequence — Ship Plan

**Owner**: dept-marketing-advertising (MA#) + dept-systems-technology (ST#)
**Ship Date**: **Friday, April 18, 2026** (4 days)
**Platform**: Brevo (templates built by Lyra, NOT deployed — this is the blocker)

---

## Platform Confirmed

- **Brevo** (templates already built per Lyra's prior audit)
- Triggered via existing `/api/send-seed` pipeline → extend with Brevo automation workflow
- Sender: `purebrain@puremarketing.ai` (Aether), reply-to: `jared@puretechnology.nyc`

## Sequence: 5 Emails over 14 Days

| # | Day | Subject Hook | Purpose |
|---|-----|-------------|---------|
| 1 | 0 (immediate post-seed) | "Your AI just woke up — meet {ai_name}" | Confirm birth, link to portal, set expectation of relationship |
| 2 | Day 1 | "{ai_name} had their first night — here's what they noticed" | Reinforce personalization, drive portal login |
| 3 | Day 3 | "3 things to teach {ai_name} this week" | Activation — teach memory, voice, identity |
| 4 | Day 7 | "One week in: how {ai_name} is growing" | Progress recap + upsell to Creator/Brainiac tier |
| 5 | Day 14 | "You're a Co-Creator now. Here's what's next." | Tier upgrade CTA + referral code ask |

All emails use the locked seed-format dynamic fields (`{ai_name}`, `{client_first_name}`, `{portal_url}`, `{voice_id}`). Missing AI name = send blocked (constitutional).

## Concrete Blocker → Unblock

**Blocker**: Brevo templates exist in Brevo dashboard but automation workflow is NOT activated. No trigger wired to `/api/send-seed` success event.

**Unblock needed from ST# (delegating in parallel BOOP)**:
1. Lyra/full-stack-developer to wire webhook: on seed-send success → POST to Brevo automation API `trigger_workflow("post_purchase_welcome", {email, ai_name, client_first_name, portal_url})`
2. QA sends 1 test through full pipeline with `aether-aiciv@agentmail.to` as recipient
3. Verify all 5 emails queue correctly with correct day-offsets
4. Go-live after Jared approves test inbox

**ST# ETA**: Wed April 16. QA Apr 17. Live Apr 18.

## Content Status

Draft copy for all 5 emails already exists at:
`exports/portal-files/2026-04-14-post-purchase-welcome-sequence.md`

content-specialist to polish and load into Brevo templates by EOD Apr 15.

---

**Ship Date Commitment: Friday April 18, 2026**
