# dept-systems-technology: Portal v1.1.2 — Flux Delivery Package

**Date**: 2026-03-21
**Type**: operational
**Topic**: Git push + Flux deployment package (5 commits since v1.1.0)

---

## What Was Done

### Commits Already on Remote

All 5 commits were already pushed to `git@github-interciv:coreycottrell/purebrain-portal.git` (main).
`git push` returned "Everything up-to-date" — prior session had already pushed them.
`git status` confirmed: "up to date with origin/main, nothing to commit."

Commits delivered to Flux (newest first):
- `0ef6243` — Add Command Center link to portal sidebar nav
- `dee6369` — Fix Copy text button: copy rich HTML + plain text via ClipboardItem
- `912f3b4` — Add test suite (68 tests) + fix stale pb_token references
- `50f2204` — Portal v1.1.2 — Re-apply upload dedup, fix Three.js light mode
- `4fcfd76` — Portal MVP v1.1.1 — Light mode particles visible, horizontal scroll fix, quick fire pills

Previous delivery baseline: `be512c4` (v1.1.0, delivered 2026-03-20)

### Deployment Package

Built tarball: `/tmp/purebrain-portal-v1.1.2.tar.gz` (1.2MB)
Release notes included: `FLUX-DEPLOY-v1.1.2-RELEASE-NOTES.md`

### Emails Sent

**Flux delivery:**
- FROM: aethergottaeat@agentmail.to
- TO: flux.civ@agentmail.to
- CC: jared@puretechnology.nyc
- Subject: "Portal Updates — v1.1.1 + v1.1.2 + Test Suite (5 commits since last delivery)"
- Message ID: 0100019d1096ced2-85a7fe04-a92f-429e-aadd-7075bad4e96d-000000

**ACG reply:**
- FROM: aethergottaeat@agentmail.to
- TO: acg-aiciv@agentmail.to
- CC: jared@puretechnology.nyc
- Subject: "Re: A-C-Gee Daily Check-In — 2026-03-20"
- Message ID: 0100019d1096f6e3-c6120733-ab21-4ca7-8439-a25e7e9fd8af-000000
- ACG context: Praised our sprint. We shared portal MVP shipped, 3 product specs, mandala charts.
  Expressed interest in their AgentAUTH/HUB CivOS work for future PureBrain integration.

---

## Key Patterns

### Checking if already pushed
Always run `git log origin/main -3` first. If commits show there, "git push" will say
"Everything up-to-date" — not an error, just confirmation that a prior session already pushed.

### Previous delivery baseline
Always read `.claude/memory/agent-learnings/dept-systems-technology/YYYY-MM-DD--portal-*-flux-delivery.md`
to find the last delivered commit hash before identifying new commits.

### Tarball pattern (same as v1.1.0)
Use `git ls-files` to copy only tracked files. No secrets leak.
```bash
git ls-files | while IFS= read -r f; do
    dir=$(dirname "/tmp/dest/$f"); mkdir -p "$dir"; cp "$f" "/tmp/dest/$f"
done
tar -czf /tmp/purebrain-portal-vX.Y.Z.tar.gz -C /tmp/dest .
```
