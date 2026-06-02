# COO Firewall Phase-2 — boop_executor flag-gated digest

**Date**: 2026-06-02
**Type**: teaching + operational
**Topic**: Implementing aiciv-native-org COO Firewall additively into the 117+ clean-cycle boop_executor

## Critical architectural finding (corrects the spec's assumption)

The spec described the firewall as: "after sub-agent outputs are collected [by the
executor], invoke result-synthesizer ... write the digest to the Primary inbox path
that boop_executor already uses, and suppress the raw outputs."

**That interception point does not exist in boop_executor.py.** The executor's model
is fire-and-forget: each BOOP launches ONE independent `claude --print` process
(fire_boop, ~line 859) that does ALL work internally (including any delegation) and
self-reports to Telegram via a curl embedded in build_boop_prompt. The executor never
reads the child's stdout (goes to /tmp/boop_{task_id}.log), never collects "sub-agent
outputs," and has NO "Primary inbox" write path. `inbox/` is only used for
constitutional alarm/salvage bodies, not agent-output routing.

## The honest, additive solution

The ONE surface the executor controls is the PROMPT handed to the launched agent
(build_boop_prompt). So the firewall is applied as a prompt addendum: when
`task.get("coo_firewall")` is truthy, append the firewall discipline (from
.claude/templates/coo-firewall-prompt.md) instructing the agent to self-enforce —
route its sub-agent outputs through result-synthesizer, write ONLY the digest to
inbox/conductor-boop-{task_id}-{ts}.md, keep raw in /tmp/coo-firewall/{task_id}/.

This honors the spec's INTENT (Primary sees only a 3-bullet + YES/NO + action-queue
digest) without inventing an executor data path that doesn't exist. Reported the
mismatch rather than refactoring the heartbeat.

## Why flag-OFF is provably byte-identical

`if task.get("coo_firewall"):` — absent key returns None (falsy) and explicit false
is falsy, so the append block is skipped entirely. Proven by importing both the .bak
and patched modules and asserting build_boop_prompt output is byte-identical (547==547
chars) for both no-flag and coo_firewall:false.

## Gotcha: importing a .py.bak file in a test

`spec_from_file_location` returns a spec with loader=None for non-.py extensions.
Use `importlib.machinery.SourceFileLoader(name, path)` +
`spec_from_loader` to force-load a backup file for A/B comparison.

## Gotcha: running daemon does NOT hot-reload source

Python doesn't reload source on a running process. The live executor (started May 31)
keeps old code in memory until a natural restart. This is SAFE here because the flag
is default-OFF and no task uses it yet — zero live behavior change either way. Did NOT
restart per constraint; .pid untouched.

## Files
- Patch: tools/boop_executor.py (+33 net, ~25 functional, additive only)
- tools/boop_executor.py.bak-pre-phase2-2026-06-02 (backup)
- .claude/templates/coo-firewall-prompt.md (compression contract)
- .claude/flows/coo-firewall-flow.md (pattern doc)
