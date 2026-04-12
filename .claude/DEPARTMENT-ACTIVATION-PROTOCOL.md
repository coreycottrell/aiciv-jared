# Department Activation Protocol

**Owner**: Corporate & Organizational (CO#)
**Version**: 1.0
**Created**: 2026-03-18
**Status**: ACTIVE — Mandatory for all task execution

---

## Purpose

This protocol exists because departments were defined but not consistently used. Jared's directive (2026-03-18): "Lets get the departments ACTIVE." Every task must route through a department manager first. No exceptions.

---

## The Universal Routing Rule

**Every task = Department Manager FIRST. Always.**

```
Jared sends task
     |
     v
Aether identifies department trigger (see DEPARTMENT-ROUTING-GUIDE.md)
     |
     v
Department Manager agent activated
     |
     v
Department Manager delegates to specialists
     |
     v
Results surface back to Jared
```

Aether (The Primary/Conductor) does NOT execute specialist work directly. Aether routes to the department manager. The department manager builds and runs the team. This is non-negotiable.

---

## Tech Team Activation (WTT / PTT / CTS)

### The Three Tech Teams

All three sit under ST# (Systems & Technology / CTO Office). Each has its own full-stack developer and QA engineer.

**WTT — Witness Tech Team**
- Domain: Witness integration, birth pipeline, container management, OAuth flows, seed endpoints
- Full-stack developer: `wtt-fullstack`
- QA engineer: `wtt-qa`
- Trigger: `WTT#`
- Route via: `dept-systems-technology`

**PTT — PureBrain Tech Team**
- Domain: purebrain.ai site, Cloudflare Pages, blog pipeline, homepage, CSS/UX, CF Workers
- Full-stack developer: `ptt-fullstack`
- QA engineer: `ptt-qa`
- Trigger: `PTT#`
- Route via: `dept-systems-technology`

**CTS — Client Tech Support**
- Domain: Customer portal support, SSH diagnostics, customer AI recovery, portal restarts
- Full-stack developer: `cts-fullstack`
- QA engineer: `cts-qa`
- Trigger: `CTS#`
- Route via: `client-tech-support-team`

### Why Separate Teams?

Each team has different context, different codebases, different risk profiles. A WTT developer who also touches the marketing site introduces cross-contamination. Separate teams means separate learning curves, separate memory files, and accumulated domain expertise that compounds. The WTT developer gets better and better at Witness. The PTT developer gets better and better at CF Pages. The CTS developer gets better and better at portal recovery patterns.

---

## Security Auditor — Mandatory on Portal Changes

**The problem Jared identified**: Security was not reviewing portal code changes.

**The fix**: Security review is a GATE. Code does not ship without it.

### When Security Runs

Security-auditor must run on ALL of the following:
- Any change to portal authentication logic
- Any change to payment processing flows
- Any new API endpoint in the portal
- Any change to user data handling (storage, retrieval, display)
- Any change to CORS, CSP, or request headers
- Any third-party library added to portal code
- Any SSH key provisioning or rotation (CTS)
- Any new environment variable handling

### Security Gate Implementation

The CTO (dept-systems-technology) enforces the gate. Before any PTT or WTT task is marked complete:

```
Step 1: Developer completes build
Step 2: security-auditor is invoked with the diff/changed files
Step 3: security-auditor returns: PASS | FAIL | PASS-WITH-NOTES
Step 4: If FAIL — developer must remediate before proceeding
Step 5: If PASS — proceed to QA
Step 6: QA passes — deploy
```

This is the BUILD -> SECURITY REVIEW -> QA -> SHIP pipeline. It already existed in the CTO's mandate. This protocol makes it mandatory and tracked.

### Security Memory

Security-auditor writes a memory file after every review:
- Path: `.claude/memory/agent-learnings/security-auditor/YYYY-MM-DD--[feature]-security-review.md`
- Contents: what was reviewed, what was found (if anything), what was cleared
- This accumulates the security posture of the entire system over time

---

## Performance Optimizer — Mandatory on Every Deploy

**The problem Jared identified**: Performance optimizations were not happening.

**The fix**: `performance-optimizer` runs after every deploy as a post-deploy step.

### What Performance Optimizer Does On Each Deploy

1. Core Web Vitals check on the deployed URL (LCP, CLS, FID/INP)
2. Asset size check — images, JS bundles, CSS files
3. Caching header verification (CF Pages cache settings)
4. Time-to-first-byte check
5. Mobile performance check
6. Comparison against previous baseline

### When to Run

- After every PTT deploy (purebrain.ai, blog posts, CF Pages)
- After every WTT deploy (Witness-integrated pages)
- After any CSS/JS refactor

### Output Format

Performance-optimizer writes a one-page report to:
`exports/departments/systems-technology/performance/YYYY-MM-DD--[deploy-name]-perf-check.md`

If a metric is worse than baseline, the report flags it as a regression and the deploy is reviewed before being considered final.

---

## CF Pages Auto-Deploy

**The problem Jared identified**: CF Pages deploy is manual. It should be automated.

### Current Deploy Command

```bash
CLOUDFLARE_API_TOKEN=$(grep CF_PAGES_TOKEN .env | cut -d= -f2) \
  npx wrangler pages deploy exports/cf-pages-deploy \
  --project-name purebrain-staging \
  --commit-dirty=true
```

### Auto-Deploy Hook: Git Post-Commit Script

Create this file at `/home/jared/projects/AI-CIV/aether/tools/auto-deploy-cf-pages.sh`:

```bash
#!/bin/bash
# Auto-deploy CF Pages on blog/site changes
# Triggered by: git hooks, blog pipeline, or explicit PTT# tasks

set -e

PROJECT_ROOT="/home/jared/projects/AI-CIV/aether"
LOG_FILE="$PROJECT_ROOT/logs/cf-deploy.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] CF Pages auto-deploy triggered" >> "$LOG_FILE"

# Load token
CF_TOKEN=$(grep CF_PAGES_TOKEN "$PROJECT_ROOT/.env" | cut -d= -f2)

if [ -z "$CF_TOKEN" ]; then
  echo "[$TIMESTAMP] ERROR: CF_PAGES_TOKEN not found in .env" >> "$LOG_FILE"
  exit 1
fi

# Deploy
cd "$PROJECT_ROOT"
CLOUDFLARE_API_TOKEN="$CF_TOKEN" npx wrangler pages deploy exports/cf-pages-deploy \
  --project-name purebrain-staging \
  --commit-dirty=true 2>&1 | tee -a "$LOG_FILE"

echo "[$TIMESTAMP] Deploy complete" >> "$LOG_FILE"

# Flush CF cache after deploy (see feedback_cf_cache_flush_after_deploy.md)
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$(grep CF_ZONE_ID "$PROJECT_ROOT/.env" 2>/dev/null | cut -d= -f2)/purge_cache" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}' >> "$LOG_FILE" 2>&1 || echo "[$TIMESTAMP] Cache purge skipped (zone ID not set)" >> "$LOG_FILE"

echo "[$TIMESTAMP] CF Pages auto-deploy complete" >> "$LOG_FILE"
```

### When Auto-Deploy Fires

| Trigger | Who Fires It |
|---------|-------------|
| Blog post published to `exports/cf-pages-deploy/blog/` | PTT fullstack or blog pipeline |
| Homepage HTML updated | PTT fullstack |
| Any file in `exports/cf-pages-deploy/` committed | PTT QA post-verification |
| Explicit `PTT# deploy` command from Jared | dept-systems-technology |

### Git Hook (Optional — Install Once)

```bash
# Install as post-commit hook
cp /home/jared/projects/AI-CIV/aether/tools/auto-deploy-cf-pages.sh \
   /home/jared/projects/AI-CIV/aether/.git/hooks/post-commit
chmod +x /home/jared/projects/AI-CIV/aether/.git/hooks/post-commit
```

When installed, every git commit automatically triggers a CF Pages deploy. PTT QA verifies after each deploy.

---

## Department Usage Tracking

**The problem**: Departments were documented but Aether was bypassing them, executing work directly.

**The fix**: Track department usage. Make it visible. Enforce the routing.

### Usage Log

Each department manager writes to its usage log after every task:

```
exports/departments/{dept-slug}/usage-log.md
```

Format:
```markdown
## YYYY-MM-DD HH:MM — [Task Summary]

- **Triggered by**: [WTT# / PTT# / CO# / etc.]
- **Task**: [One-line description]
- **Agents invoked**: [list]
- **Output**: [file path or summary]
- **Duration**: [approx]
- **Status**: complete | partial | escalated
```

### Monthly Activation Report

At the start of each month, CO# generates a Department Activation Report:
- Which departments were triggered (count per department)
- Which departments had zero activity (flag for review)
- Agents invoked per department
- Knowledge files written per department

This report goes to Jared and is saved to:
`exports/departments/corporate-org/reports/YYYY-MM--department-activation-report.md`

---

## Knowledge Compounding System

**Jared's directive**: "The more you share the more you all compound in skills and knowledge — how do we make this permanent?"

### The Answer: Mandatory Learning Writes

Every agent writes a learning file after every significant task. This is already a constitutional requirement (verification-before-completion skill). This protocol makes it enforced at the department level.

### What Gets Written

After every task, the executing agent writes:

```
.claude/memory/agent-learnings/{agent-name}/YYYY-MM-DD--{topic}.md
```

Contents:
- What the task was
- What pattern or technique was used
- What gotcha or edge case was found
- What would be useful for the next agent doing similar work

### Cross-Team Knowledge Sharing

The department manager (dept-systems-technology for WTT/PTT/CTS) runs a weekly knowledge synthesis:

1. Collect all learning files from the past 7 days across all three tech teams
2. Identify patterns that appear in multiple teams (this is compounded learning)
3. Write a synthesis file: `exports/departments/systems-technology/knowledge/YYYY-MM-DD--weekly-synthesis.md`
4. If a pattern is broadly useful, escalate to `dept-pure-technology` to circulate across all departments

### Shared Knowledge Registry

A running index of all cross-team learnings:

`exports/departments/systems-technology/knowledge/SHARED-KNOWLEDGE-REGISTRY.md`

Format:
```markdown
## Pattern: [Name]

**Source**: [agent] on [date] working on [WTT/PTT/CTS]
**Applies to**: WTT | PTT | CTS | ALL
**Summary**: [2-3 sentences]
**Learning file**: [path]
```

### Why This Compounds

When WTT discovers a pattern (e.g., how to handle container pool exhaustion), that knowledge goes into WTT's learning files. The weekly synthesis picks it up. The shared registry makes it visible to PTT and CTS. The next time any team hits a similar pattern, they search the registry first. The second solve takes 10% of the time the first took. Over 90 days, the teams collectively become substantially more capable than any individual agent working alone.

This is what Jared means by compounding.

---

## Enforcement Checklist

This is what "departments are ACTIVE" looks like in practice. Check this before marking any task complete:

- [ ] Task was routed through the correct department manager (not executed directly by Aether)
- [ ] If portal code changed: security-auditor was invoked and passed
- [ ] If a deploy happened: performance-optimizer ran post-deploy
- [ ] If blog/site changed: CF Pages auto-deploy script fired
- [ ] Department manager wrote to usage log
- [ ] Executing agent wrote learning file to `.claude/memory/agent-learnings/`
- [ ] Department usage tracking updated

---

## Implementation Steps

1. **Immediate**: Aether stops executing tech work directly. All ST#/WTT#/PTT#/CTS# work goes through dept-systems-technology or client-tech-support-team.
2. **This week**: Create the auto-deploy script at `tools/auto-deploy-cf-pages.sh` and set permissions.
3. **This week**: Create the usage log file for each active department.
4. **This week**: Create the shared knowledge registry file.
5. **Monthly**: CO# runs the department activation report.

---

**Saved to**: `/home/jared/projects/AI-CIV/aether/.claude/DEPARTMENT-ACTIVATION-PROTOCOL.md`
**Companion file**: `/home/jared/projects/AI-CIV/aether/.claude/TECH-TEAM-ROSTER.md`
