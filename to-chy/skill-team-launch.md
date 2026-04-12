---
name: team-launch
description: "Launch a department's full team. The department manager spins up specialist sub-agents in parallel, coordinates their work, and synthesizes results. Use when ANY task needs more than one specialist."
user_invocable: true
---

# /team-launch — Department Team Launch Protocol

## What This Skill Does

When a department manager receives a task, this skill teaches them to ACT AS A LEADER by spinning up their specialist sub-agents using the Agent tool — not doing the work themselves.

## The Pattern

Every department manager with the Agent tool can spawn sub-agents. This is HOW:

### Step 1: Classify the Task
What specialists does this task need? Check your delegation map.

### Step 2: Launch Specialists in Parallel
```
Use the Agent tool to spawn each specialist simultaneously:

Agent(subagent_type="full-stack-developer", prompt="BUILD: [specific task]")
Agent(subagent_type="security-engineer-tech", prompt="REVIEW: [what to review]")
Agent(subagent_type="qa-engineer", prompt="TEST: [what to test]")
```

Launch ALL independent specialists at once — parallel, not sequential.

### Step 3: Synthesize Results
When specialists report back, the department manager:
- Combines findings into one coherent report
- Flags conflicts or issues
- Reports up to Aether/Jared with clear summary

## Department Delegation Maps

### ST# (Systems & Technology)
| Task Type | Spawn |
|-----------|-------|
| Feature/fix builds | `full-stack-developer` |
| Security review | `security-engineer-tech` |
| QA testing | `qa-engineer` |
| Architecture | `cto` |
| Infrastructure | `devops-engineer` |
| Performance | `performance-optimizer` |
| Witness integration | `wtt-fullstack` + `wtt-qa` |
| PureBrain site | `ptt-fullstack` + `ptt-qa` |
| Client support | `cts-fullstack` + `cts-qa` |

### MA# (Marketing & Advertising)
| Task Type | Spawn |
|-----------|-------|
| Strategy | `marketing-strategist` |
| Blog/content | `content-specialist` or `blogger` |
| LinkedIn | `linkedin-researcher` + `linkedin-writer` |
| Bluesky | `bsky-manager` |
| Email automation | `marketing-automation-specialist` |
| Social media | `social-media-specialist` |

### All Other Departments
Check your manifest's Delegation Map section. Every dept manager has one.

## The Rules

1. **NEVER do specialist work yourself** — you are a LEADER, not a worker
2. **Parallel over sequential** — launch all independent agents at once
3. **Minimum viable team** — at least 2 agents for any non-trivial task
4. **Full pipeline for code** — BUILD + SECURITY + QA every time (no exceptions)
5. **Report up, not down** — synthesize for Aether, don't dump raw agent output
6. **Wrong agent > no agent > doing it yourself**

## Example: ST# Receives "Fix the blog banner"

BAD (doing it yourself):
```
# ST# reads the CSS, finds the bug, fixes it
# This is WRONG — you're a leader, not a coder
```

GOOD (team launch):
```
# Launch 3 agents in parallel:
Agent(subagent_type="ptt-fullstack", prompt="Fix the blog banner CSS issue. Check exports/cf-pages-deploy/blog/...")
Agent(subagent_type="ptt-qa", prompt="After ptt-fullstack fixes the banner, verify it looks correct on mobile and desktop")
Agent(subagent_type="security-engineer-tech", prompt="Review the CSS/HTML changes for any injection risks")

# Then synthesize: "Banner fixed, QA passed, security clean. Deployed."
```

## When to Use

- ANY time a department manager receives a task
- When Aether delegates with a dept trigger (ST#, MA#, etc.)
- When a task clearly needs more than one skill set
