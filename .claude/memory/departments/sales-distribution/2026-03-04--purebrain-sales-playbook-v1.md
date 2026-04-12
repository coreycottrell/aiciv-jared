# SD# Task: PureBrain Sales Playbook v1.0

**Date**: 2026-03-04
**Task Type**: Sales System Codification + HTML Page Build + WordPress Deploy
**Agent**: dept-sales-distribution

---

## What Was Built

Full codification of Jared's live sales system into a professional playbook + premium dark-themed HTML page deployed to purebrain.ai.

## Deployed Page

- **WordPress Page ID**: 1278
- **Live URL**: https://purebrain.ai/sales-playbook/
- **Password**: closers2026
- **Template**: default (empty string — NOT elementor_canvas)
- **Status**: publish (password-protected)
- **Elementor cache cleared**: Yes (DELETE /elementor/v1/cache returned 200)

## Files

- **Markdown playbook**: `/home/jared/projects/AI-CIV/aether/exports/departments/sales-distribution/purebrain-sales-playbook.md`
- **HTML page**: `/home/jared/projects/AI-CIV/aether/exports/departments/sales-distribution/purebrain-sales-playbook.html`
- **Google Drive HTML**: https://drive.google.com/file/d/1FvVSW1lgU5BjOLe5fRYti8kWnZ1b9LyU/view (folder: 1QaBu0gO7__my-AziZ2WD_PAuhkfLjQoN)
- **Telegram delivery**: Both status message and .md file sent to Jared

## The Sales System Structure

**8-Step Process**:
1. Get Attention — cold outreach opener
2. Research (Step 1.25) — AI-powered deep research, build Partnership Brief
3. Schedule Meeting (Step 1.5)
4. Decide brief timing (Step 1.75)
5. AI Tool Stack Calculator — SPIN: S + P
6. Investor Intelligence — SPIN: P + I (DO OR DIE moment)
7. Compare page — SPIN: P + I continued
8. Invitation page — exclusivity + scarcity
9. Live demo — SPIN: N-P (the close)
10. Brainiac community — belonging
11. Onboarding scheduling — commitment lock-in
12. Referral program — 5% perpetuity

**SPIN Mapping**:
- S (Situation): Tool Stack Calculator
- P (Problem): Calculator + Investor Intelligence + Compare
- I (Implication): Investor Intelligence "DO OR DIE" / Two Futures frame
- N-P (Need-Payoff): Step 6 live demo — let THEM articulate value

## Key Differentiators in This System

1. **Custom Partnership Brief** per prospect (Step 1.25) — massive trust builder
2. **Interactive tools** used WITH the prospect, not shown AT them
3. **Two Futures Frame** at Investor Intelligence — very high emotional impact
4. **Invitation framing** not sales pitch framing — prospect feels privileged not sold to
5. **5% perpetuity referral** — built-in viral loop

## Jared's Close Rate Context

"Every person I have done this with has either said yes on the spot or basically said yes lets schedule another so we can finalize or my CTO can ask questions, then we close!" — near 100% qualified close rate.

## Design System Used

- Brand colors: Blue #2a93c1, Orange #f1420b, Dark bg #080a12
- Step cards with SPIN phase badges
- Two futures frame visually highlighted
- All tool URLs as clickable pills in the HTML
- Emotional arc visualization (5 stages)
- Objection handling cards with color-coded headers
- Referral math examples with payout callouts

## Learnings for Future Playbooks

1. The playbook should preserve the founder's energy/voice — codify the spirit, not just the steps
2. HTML deployment pattern confirmed: wrap in `<!-- wp:html -->`, password field in page_data, template = ""
3. GDriveManager.upload_file() returns string (link URL), not dict — parsing fix needed if script checks `.get()`
4. Telegram delivery: send .md file for review-first workflow
