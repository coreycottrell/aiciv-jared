# Brainiac Training Scan -- Summary & Actionable Suggestions

**Date**: 2026-05-01
**Scanned By**: web-researcher
**Modules Live**: 9 (all ingested)
**Modules Coming Soon**: 4 spotlights + 2 advanced = 6 planned

---

## What Was Learned

### Modules Newly Ingested (7, 8, 9)

**Module 7 -- Shipping & Measurement** (Apr 15, 82 min):
The ship-to-generator ratio as the only AI metric that matters. Introduces the waste-as-progress anti-pattern where teams celebrate 10,000 lines generated while only 1,900 ship. Also covers the conductor-of-conductors architecture (main AI never works directly, only delegates), pre-compaction note-taking, and the Hub for compounding skills across the network.

**Module 8 -- Software Building** (Apr 22, 77 min):
Build-don't-subscribe philosophy. Small businesses hemorrhage $500-2000/month on generic SaaS tools. AI can build bespoke replacements to exact specifications. Introduces the 7-question pre-build checklist (now constitutional in Aether's ops) and the automation triage framework: deterministic tasks go to software, judgment tasks go to AI.

**Module 9 -- Getting 10x from Your AI Partner** (Apr 29, 81 min):
AI partnership as compound investment. Month 1 generic answers become Month 6 anticipatory partnership saving 20-40+ hours/week. Memory as competitive moat. The operator (not the model) determines outcome quality. Early adopters lock in structural advantage because late starters owe both time gap AND setup curve.

### Cross-Module Arc

The 9 modules form a clear progression: Foundation -> Automate -> Scale -> Coordinate -> Persist -> Self-Assess -> Measure -> Build -> Compound. Each module builds on previous ones, and Module 9 ties the entire arc together by showing how all the practices compound over time.

---

## 5 Actionable Suggestions

### 1. UPDATE THE AI-TRAINING-MANIFEST JSON (High Priority)

The `ai-training-manifest` in brainiac.purebrain.ai/index.html only lists modules 1-6 (last updated 2026-04-06). The TRAINING_VIDEOS array is current with all 9, but the manifest JSON -- the thing AI scanners are designed to read -- is 3 modules behind. This means any member's AI using the "AI Training Hacks" button that relies on the manifest will miss modules 7-9 entirely.

**Action**: Update the manifest JSON to include modules 7, 8, 9 with full metadata (themes, frameworks, implementation items, quote sources).

### 2. APPLY SHIP-TO-GENERATOR RATIO INTERNALLY (Medium Priority)

Module 7's core metric should be applied to our own operations. We generate significant volume across agents. How much actually ships? A weekly "shipped vs generated" audit would surface waste patterns and validate that delegation is producing output, not just activity.

**Action**: Add a weekly BOOP that calculates shipped-to-generated ratio across all agent output.

### 3. AUTOMATION TRIAGE AUDIT (Medium Priority)

Module 8's automation triage framework identifies a real risk: AI doing deterministic work that plain software should handle. Internally, several BOOPs may be doing deterministic polling/checking that could be CF Workers or cron jobs instead of burning AI context.

**Action**: Audit current BOOPs and identify which are deterministic (should be software) vs judgment-based (correctly assigned to AI).

### 4. COMPOUND PROGRESS TRACKING FOR CLIENTS (High Priority)

Module 9's compound investment thesis is the core PureBrain sales argument, but there is no dashboard showing clients their progression on the calibration curve (Month 1 generic -> Month 6 anticipatory). Showing members their AI's growth trajectory would dramatically improve retention and referral enthusiasm.

**Action**: Build a simple "AI Partnership Maturity" metric visible in each client's portal -- hours saved, corrections absorbed, patterns learned, months active.

### 5. MODULE 10 PREP (Low Priority)

No Module 10 stub exists in the TRAINING_VIDEOS array or HTML. Next Wednesday's session (May 6) will need a new entry. The pattern is well-established (see ptt-fullstack learnings on the Zoom pipeline + R2 upload + CF Pages deploy flow).

**Action**: Pre-build Module 10 card stub with placeholder content in index.html before next Wednesday.

---

## Files Reference

- **Full ingestion**: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/primary/brainiac-training-ingestion-2026-05-01.md`
- **Previous scan (M1-6)**: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/brainiac-training-scan-2026-04-17.md`
- **Training hub source**: `/home/jared/projects/brainiac-purebrain/index.html`
- **Module transcripts**: `/home/jared/projects/AI-CIV/aether/exports/brainiac-training/modules/module-2026-04-{08,15,22,29}.md`
