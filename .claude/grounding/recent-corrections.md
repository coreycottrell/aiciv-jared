# Recent Corrections (HOT 7 days)

**Authority**: Tier 4 Constitutional. Re-read every grounding trigger.
**Rotation**: Last 5 corrections from Jared. Hot for 7 days, then promoted to constitutional OR dropped.

---

```yaml
corrections:
  - date: 2026-04-11
    from: Jared
    rule: "Edit tool silently fails on files over 100KB. Use sed for large-file edits."
    why: "Lost edits on index.html (>300KB) — Edit returned success but change never landed. Broke deploy verification."
    how_to_apply: "Check file size before editing. If >100KB → sed + verify with grep. Test deployed content via curl before declaring done."
    status: hot
    applies_to: [all]
    promoted_to: null

  - date: 2026-04-12
    from: Jared
    rule: "Never curl live CF content into local cf-pages-deploy directory."
    why: "Overwrote local source-of-truth with minified/modified production HTML, caused rebuild divergence."
    how_to_apply: "Local dir IS source of truth. One-time disaster recovery only, and only with explicit Jared approval + backup first."
    status: hot
    applies_to: [all]
    promoted_to: null

  - date: 2026-04-13
    from: Jared
    rule: "Check spreadsheet before sending ANY email. Skip if 'Sent' present in column I."
    why: "Duplicate emails sent to same recipient from different AI agents simultaneously."
    how_to_apply: "Pre-send hook reads tracking sheet. If 'Sent' exists, abort send + log skip reason. No exceptions."
    status: hot
    applies_to: [all]
    promoted_to: null

  - date: 2026-04-14
    from: Jared
    rule: "Customer count updates MUST update ALL 4 source files, not just one."
    why: "Customer count drift across dashboards — updated main count but investor portal and 3 other surfaces showed stale numbers."
    how_to_apply: "When customer count changes, grep all source files referencing the count and update atomically. Verify each surface shows new value."
    status: hot
    applies_to: [chy]
    promoted_to: null

  - date: 2026-04-14
    from: Jared
    rule: "Image generation stack — Aether was wrong TWICE today. Ground truth lives at /home/jared/projects/AI-CIV/aether/docs/DESIGN-FLOW-GROUND-TRUTH.md. ALL sub-agents MUST read the actual design flow doc before answering image generation questions. Do not guess. Do not extrapolate. Quote the doc."
    why: "Prior corrections (Replicate-is-dead / Gemini-never-used) were both wrong and contradicted the 2026-04-06 design skill package authored by Aether. Guessing at the stack keeps producing wrong answers. The doc is canonical."
    how_to_apply: "Before answering ANY question about image generation, FLUX, Gemini, Replicate, 3d-design-specialist, PIL compositing, or brand image pipeline: read /home/jared/projects/AI-CIV/aether/docs/DESIGN-FLOW-GROUND-TRUTH.md. The doc specifies BOTH Gemini 3 Pro Image AND FLUX Pro via Replicate as active generators with PIL text overlay. If live env contradicts doc (e.g. API keys missing), ASK Jared — do not assume."
    status: hot
    applies_to: [all]
    promoted_to: null
```

---

## Daily Refresh (BOOP: reground-corrections-daily-6am-ET)

- Corrections older than 7 days: evaluated for promotion to constitutional (TRIO-SHARED-RULES.md) OR dropped.
- New corrections added as they arrive from Jared.
- Max 5 in HOT state at any time — oldest falls off if new arrives.
