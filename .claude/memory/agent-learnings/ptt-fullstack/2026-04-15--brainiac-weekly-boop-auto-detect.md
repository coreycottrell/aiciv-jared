---
type: teaching
topic: Replacing hardcoded BOOP values with live-state auto-detection
---

# Brainiac weekly BOOP — restructured 2026-04-15

## Problem
`brainiac-weekly-module` BOOP had a hardcoded description saying
"Module 03 = Advanced Agent Delegation". The live page was already at Module 06.
Each week the BOOP would effectively target the wrong module or rebuild Module 3.

## Fix
Created `tools/brainiac_weekly_module_builder.py`:
- Fetches https://purebrain.ai/brainiac-mastermind-training/?bypass=portal
- Parses `Launch Module N` + `brainiac-module-N-<slug>` patterns, takes max
- Cross-checks local `exports/cf-pages-deploy/brainiac-mastermind-training/`
  for max module directory (belt + suspenders)
- Target = max(live, local) + 1
- Idempotency: if `brainiac-module-{N}-*` directory already exists, SKIP
- Scaffold-only build (copies Module 2 directory as template, drops
  SCAFFOLD_PENDING_EDITORIAL.md marker). Editorial fill-in is delegated to
  Aether + brainiac-training-pipeline skill. We do NOT autogenerate full
  training module bodies without human-in-loop review.
- Deploy via tools/cf-deploy.py (never wrangler); pre-deploy-sync.sh first.
- Writes JSONL to exports/brainiac-training/weekly-builder-log.jsonl
- Writes memory entry under agent-learnings/ptt-fullstack/ every run

BOOP config in `.claude/scheduled-tasks-state.json` replaced. New entry carries
`command`, `dry_run_command`, `idempotent: true`, `auto_detect_source` keys.

## Current state (2026-04-15)
- Live max module: 6
- Next target: 7
- Dry-run verified: "Next module: 7 / Already exists: False / Action: build"

## Pattern to reuse
Any BOOP that references a "next thing" (next episode, next post, next module)
should derive the number from live state, never from a hardcoded description
field. Put detection + idempotency in a tool script, let the BOOP just call it.

## File paths
- Tool: /home/jared/projects/AI-CIV/aether/tools/brainiac_weekly_module_builder.py
- BOOP config: /home/jared/projects/AI-CIV/aether/.claude/scheduled-tasks-state.json
- Backup: /home/jared/projects/AI-CIV/aether/.claude/scheduled-tasks-state.json.bak-2026-04-15-brainiac-fix
- Build log: /home/jared/projects/AI-CIV/aether/exports/brainiac-training/weekly-builder-log.jsonl
- Deploy tree: /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-mastermind-training/
