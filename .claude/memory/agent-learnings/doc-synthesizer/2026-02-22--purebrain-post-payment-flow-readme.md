# Memory: PureBrain Post-Payment Flow README Synthesis

**Agent**: doc-synthesizer
**Date**: 2026-02-22
**Type**: operational
**Topic**: Synthesized comprehensive README from 6 source documents into single reference for AICIV team

---

## Context

Synthesized a 47KB, 926-line README from 6 source documents:
1. CTO architecture spec (50KB) — complete v3 change specification
2. v3 JS script header (2016 lines) — the actual implementation
3. Code archaeology analysis (17KB) — v2 architecture mapping
4. Security pre-audit — 4 CRITICAL findings with fixes
5. Security review memory — v3 status (what was fixed, what remains)
6. QA verification memory — SHIP verdict, 55/56 checks pass

## Synthesis Techniques Used

1. **Security posture layering**: Cross-referenced pre-audit findings with v3 security review to produce an accurate "fixed vs remaining" table. Critical: the raw v3 file had PARTIALLY fixed CRIT-002 (masked in UI but still logged) — the security review memory had the definitive status.

2. **Audience-split structure**: The README serves two audiences simultaneously — business stakeholders (Section 2, user flow) and backend developers (Sections 3-5, integration specs). Separated clearly without duplication.

3. **Gap surfacing as actionable items**: The portal-status API stub and credential delivery gap were scattered across documents. Synthesized into a concrete "what AICIV needs to build" checklist (Section 5 + Appendix).

4. **Phase numbering consistency**: The architecture spec used Phase 4/5/6/7 for new phases, while the code analysis used Phase 1-5 for the v2 flow. Resolved by using v3 phase numbers throughout and noting v2 context where relevant.

## Key Facts Worth Remembering

- v3 script: 69,229 chars, deployed to pages 688 (sandbox) and 689 (live)
- Script is always at index 23 (0-based) in the widget's script tag list
- Claude key and Telegram token are stripped via destructuring: `const { claudeSessionInfo: _sk, telegramBotToken: _tg, ...safeData } = data`
- Portal URL validation: must be https + hostname ends in purebrain.ai
- The portal-status API endpoint does NOT exist yet — needs to be built by AICIV
- Credential delivery to AICIV backend also has no mechanism yet — identified as a gap

## What Works Well for Technical READMEs Destined for Integration Teams

- Lead with a "what still needs building" signal in the overview (avoids wasted reading)
- Provide exact request/response JSON for every API endpoint
- Include a Quick Integration Checklist appendix — developers use this as their task list
- Cross-reference security fixes explicitly ("this was CRIT-002, here's how it was fixed") so the receiving team can verify independently
- Separate "what's deployed" from "what needs connecting" clearly

## File Produced

`/home/jared/projects/AI-CIV/aether/exports/README-purebrain-post-payment-flow.md`
Size: 47KB, 926 lines
