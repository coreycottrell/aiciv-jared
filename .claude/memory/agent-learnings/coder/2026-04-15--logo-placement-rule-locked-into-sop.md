---
date: 2026-04-15
agent: coder
type: operational
task: Lock logo placement rule into content-creation-sop skill
status: complete
---

# Logo Placement Rule Locked Into content-creation-sop

## Task

Jared mandated that logo placement rule (NEVER overlap main image content) be locked into the `content-creation-sop` skill as a constitutional requirement.

## What Was Done

Updated `/home/jared/projects/AI-CIV/aether/.claude/skills/content-creation-sop/SKILL.md`:

1. **Added "Logo Placement Rule" section** (line 268-301) with:
   - Clear prohibition: NO logo on faces, focal subjects, primary text
   - Acceptable zones: quiet corners, dedicated logo bands, margins
   - 80px minimum logo-to-subject distance
   - Rationale (why it matters)
   - How to apply (4-step process)
   - References to constitutional memory + example image

2. **Added checklist item** to Image Verification Checklist (line 313):
   - "Logo does NOT overlap main image content (faces, products, focal subjects, headlines) -- 80px minimum distance"

3. **Marked as CONSTITUTIONAL** with lock date 2026-04-15

## File Modified

- `/home/jared/projects/AI-CIV/aether/.claude/skills/content-creation-sop/SKILL.md`

## Diff Summary

Added 34 lines between "Repurpose Pool Check" section and "Image Verification Checklist":
- Full Logo Placement Rule section with prohibitions, acceptable zones, rationale, process
- Updated checklist with logo overlap verification requirement

## Integration

This rule now enforces at content creation time:
- `3d-design-specialist` uses `content-creation-sop` when generating images
- Every image must pass the new checklist item before delivery to Jared
- Parallel with `purebrain-social-design` skill (updated by 3d-design-specialist in parallel task)

## Key Learning

Constitutional rules (from Jared) must be locked into the SOPs that agents reference during execution. Not just memory files -- the actual procedural documents that govern day-to-day work.

Memory provides context. Skills provide enforcement.
