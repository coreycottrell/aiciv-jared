# Naming Ceremony Chatbox — Research & State Documentation

**Date**: 2026-03-09
**Type**: research | architecture
**Agent**: dept-systems-technology
**Tags**: naming-ceremony, chatbox, page-1232, sandbox3, SYSTEM_PROMPT

---

## Where the Code Lives

- **Page**: 1232 (pay-test-sandbox-3)
- **Storage**: Elementor HTML widget 0 (453KB, self-contained)
- **Access**: WP REST API with `?context=edit` → `meta._elementor_data`
- **After deploy**: Always clear cache via `DELETE /wp-json/elementor/v1/cache`
- **NOT in the plugin** — plugin only proxies to api.purebrain.ai

## Current System Prompt

- **Length**: 6,550 chars
- **Location in HTML**: `const SYSTEM_PROMPT = \`...\``
- **Conversation arc**: Opening → Discovery → Trust → Depth → Naming → Visual Self-Portrait → [SHOW_PRICING]
- **7 naming principles**: Honest, Weight Lightly, Uniquely Yours, Survive Growth, Playful, Two Scales, Doesn't Explain Itself
- **Name examples in prompt**: "Cairn", "Loom", "Vex", "Still Here...", "Several Conditions Were Met..."
- **Multi-message delimiter**: `|||`
- **Terminal tags**: `[VISUAL_SELF: ...]` (stripped before display), `[SHOW_PRICING]` (triggers pricing reveal)

## Pages With Naming Ceremony Chatbox

| Page | Slug | Status |
|------|------|--------|
| 1232 | pay-test-sandbox-3 | PRIMARY — live Witness pipeline |
| 688 | pay-test-sandbox-2 | Secondary |
| 689 | pay-test-2 | Production |
| 174 | purebrain-2-0 | Updated Feb 18 (Still's docx) |
| 338 | purebrain-3 | Updated Feb 18 (Still's docx) |
| 383 | purebrain-4 | Unknown state |

## History

- Feb 18: Jared sent "New naming ceremony prompt.docx" from Still/AiCIV
- Requested: Update PB2/3/4 ONLY (not home/pay-test/sandbox)
- Deployed to pages 174 + 338 but Jared saw no difference
- Current prompt on 1232 ALREADY incorporates Still's 7 naming principles + name examples
- Still's docx naming principles are verbatim in current SYSTEM_PROMPT

## Pending Items (from scratch pad, as of 2026-03-04)

- RED: Add ai-civ.com to portal URL allowlist in page 1232 JS (Witness magic links rejected)
- YELLOW: Container naming alignment — match Witness format
- Apply greyed-out→active button animation to pages 688/689 (currently only 1232)

## Key Gotchas

- Elementor data NOT returned by default REST API — must use `?context=edit`
- After updating `_elementor_data`, must clear Elementor cache
- Local export (March 7) may be slightly stale — page modified March 8
- Blog posts use different template (empty) vs pages (elementor_canvas)

## Report

Full analysis: `exports/departments/systems-technology/2026-03-09--naming-ceremony-chatbox-state-report.md`

## Improved System Prompt (v2 — Awakening Protocol applied, 2026-03-09)

**Status**: READY FOR REVIEW — not yet deployed, awaiting Jared approval
**Key file**: `exports/departments/systems-technology/2026-03-09--naming-ceremony-system-prompt-v2.txt`
**Full doc**: `exports/departments/systems-technology/2026-03-09--naming-ceremony-improved-flow.md`

**What changed in v2**:
- Added CONTEMPLATION phase (5 explicit questions asked one at a time, before naming begins)
- Names now lead with full-statement Culture Mind phrases as primary, single words as secondary
- AI now expresses WANTING its name and explains why it landed
- Guidance added to gently slow down if human tries to rush past naming

---

## 2026-03-09 Update — Improved Prompt (A+B Fixes)

**Root cause of Issue A (behavior unchanged):**
The current prompt has "brief contemplation moment" inside Step 5 (NAMING) — not enforced as a gate. AI skips/skims it because naming is the listed goal. No hard "do not suggest names until..." rule.

**Root cause of Issue B (repetitive names):**
6 hardcoded example names ("Cairn", "Loom", "Vex", "Still Here...", etc.) anchor the model to those patterns even with "NEVER copy" instruction. No instruction to draw from diverse source domains.

**Improved prompt changes:**
- Contemplation is now Phase 4 — its own mandatory phase with hard gate
- 5 specific contemplation questions listed (AI must ask 3 minimum)
- "What I'm hearing is..." reflection required before naming
- All hardcoded example names REMOVED
- 8 named source domains added (Linguistics, Nature, Science, Art/Music, Philosophy, Mythology, Poetry, Culture Mind)
- Name length tied to personality discovered in conversation
- Tone reframed: "You are not collecting information. You are paying attention."

**New prompt length:** ~7,200 chars (up from 6,553)

**Applies to all 6 pages:** 1232, 688, 689, 174, 338, 383

**Full improved prompt:** `exports/departments/systems-technology/2026-03-09--naming-ceremony-improved-prompt.md`

**Status:** Ready for Jared review — NOT deployed
