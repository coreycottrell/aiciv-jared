---
name: cross-boop-convergence-detection
version: 1.0.0
author: aether
description: Detect when multiple BOOPs converge on the same root cause
tags: [boop, convergence, investigation, anti-pattern]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Cross-BOOP Convergence Detection

When 2+ independent BOOPs identify the same root cause, it's a signal. But verify with deployed-system probes before escalating.

## The Pattern

**Convergence** = Multiple independent investigations reaching the same conclusion.

**Meaning:**
- 2 BOOPs same root cause = investigate NOW
- 3+ BOOPs same issue = STOP, architectural-truth-first before any more patches
- 9+ BOOPs = STALL signal, likely needs human decision (Day-3 default)

## Detection Method

### 1. Track Issue Mentions Across BOOPs

```bash
# Search recent BOOPs for common error/issue
grep -r "pricing drift" /home/jared/projects/AI-CIV/aether/inbox/conductor-boop-*.md

# Count unique BOOPs mentioning the issue
grep -l "pricing drift" /home/jared/projects/AI-CIV/aether/inbox/conductor-boop-*.md | wc -l
```

### 2. Check Working Tree for Root Cause

```bash
# Example: pricing drift convergence
grep -r "Awakened.*\$297" /home/jared/projects/purebrain-site/
```

**BUT** - working tree grep can amplify stale source.

### 3. Verify with Deployed System

```bash
# CRITICAL: Verify against LIVE system
curl -s "https://purebrain.ai/path/" | grep "expected-content"

# Or check database
curl -s "https://api.purebrain.ai/endpoint" | jq '.data'
```

## Verification Requirements

**Convergence from working-tree grep can create false confidence.**

MUST pair with:

1. **Deployed-system verification**
   - Curl live URLs
   - Query production database
   - Check live API responses

2. **Vary methodology across BOOPs**
   - grep ↔ ripgrep ↔ curl ↔ DB
   - Don't repeat same check 9 times

3. **Match real client traffic patterns**
   - Cache-bust probes ≠ real navigation
   - OPTIONS-204 ≠ GET-200
   - Query string routing can break probes

## Dispatch Channel Check

**Convergence from cron sub-agents ≠ escalation signal.**

Cron sub-agents **cannot Task()** dept-managers. They can detect but not dispatch.

**Check main-thread engagement:**

```bash
# Check if relay was shipped this session
tail -20 /home/jared/tg_bridge.log | grep "Delivered"

# Check portal file activity
find ~/exports/portal-files -mmin -60 -type f

# Check if main thread is responsive
grep "Jared" /home/jared/purebrain_portal/portal-chat.jsonl | tail -5
```

**If dispatch channel is blocked:**
- Convergence count may be high BUT
- No resolution because sub-agent can't route to dept-managers
- Need main-thread intervention

## Compression After 3+ Identical Cycles

After 3+ BOOPs document the SAME finding with NO change:

**Compress to:**
```
No change — Day-N default at [date].
```

**Stop repeating the same finding.**

## Example: 2026-05-18 Pricing Drift

**Convergence:**
- 29+ BOOPs documented pricing drift (Awakened = $297 or $499?)
- All reached same conclusion: homepage shows $297, spec/memory says $499

**BUT:**
- Sub-agent cron detected but couldn't dispatch (no Task() capability)
- Main-thread not engaged (bundled relay not yet fired)
- High convergence count but dispatch channel blocked

**Resolution:**
- Jared corrected: $297 is CORRECT, $499 was wrong
- 29 BOOPs were detecting real drift, but couldn't route fix
- Needed Day-3 default → main-thread → human correction

## Decision Matrix

| Convergence | Dispatch Channel | Action |
|-------------|------------------|--------|
| 2 BOOPs | Open | Investigate NOW |
| 3+ BOOPs | Open | STOP - architectural-truth-first |
| 9+ BOOPs | Blocked (cron) | Compress + wait for Day-3 |
| 9+ BOOPs | Open | Escalate to human immediately |

## Probe Dimension Audit

At convergence ≥3, audit probe dimensions:

**Dimension 1: Methodology**
- grep vs ripgrep vs curl vs DB query

**Dimension 2: Input**
- Verb (GET vs POST vs OPTIONS)
- Headers (cache-bust vs normal)
- Query strings
- Fragments
- Config files (CF Transform Rules, etc.)

**Dimension 3: Traffic Match**
- Does probe match real user traffic?
- Are you testing the right endpoint?
- Is CF caching involved?

## Anti-Patterns

### Anti-Pattern 1: Blind Escalation

- **BAD**: 3 BOOPs converge → escalate immediately
- **GOOD**: 3 BOOPs converge → verify with deployed system → then escalate
- **Why**: Working tree can be stale, grep amplifies false confidence

### Anti-Pattern 2: Ignoring Dispatch Channel

- **BAD**: 9 BOOPs = crisis
- **GOOD**: 9 BOOPs from cron + blocked dispatch = wait for main-thread
- **Why**: Sub-agents can't route fixes, convergence is detection not failure

### Anti-Pattern 3: Repeating Same Check

- **BAD**: grep same file 9 times
- **GOOD**: grep once, curl once, DB query once, then vary
- **Why**: Repeated same check doesn't add confidence

### Anti-Pattern 4: Not Compressing

- **BAD**: Document same finding in 20 consecutive BOOPs
- **GOOD**: After 3 identical cycles, compress to "No change — Day-N"
- **Why**: Noise doesn't help, just clutters logs

## Example Detection Script

```python
#!/usr/bin/env python3
import os
import re
from collections import Counter

def detect_convergence(inbox_dir, issue_pattern):
    """Detect convergence across BOOP files"""
    
    boop_files = [f for f in os.listdir(inbox_dir) if f.startswith('conductor-boop-')]
    
    mentions = []
    
    for boop_file in boop_files:
        path = os.path.join(inbox_dir, boop_file)
        with open(path, 'r') as f:
            content = f.read()
            if re.search(issue_pattern, content, re.IGNORECASE):
                mentions.append(boop_file)
    
    count = len(mentions)
    
    print(f"=== CONVERGENCE DETECTION ===")
    print(f"Pattern: {issue_pattern}")
    print(f"BOOPs mentioning: {count}")
    
    if count >= 9:
        print("⚠️  STALL signal (9+) - Day-3 default needed")
    elif count >= 3:
        print("🔴 STOP - Architectural-truth-first before more patches")
    elif count >= 2:
        print("🟡 Investigate NOW - Convergence detected")
    else:
        print("✅ No convergence")
    
    return mentions

if __name__ == '__main__':
    inbox = '/home/jared/projects/AI-CIV/aether/inbox'
    issue = r'pricing.*drift|Awakened.*\$297'
    
    mentions = detect_convergence(inbox, issue)
    
    if len(mentions) >= 2:
        print("\n=== MENTIONED IN ===")
        for boop in mentions[-5:]:  # Last 5
            print(f"  - {boop}")
```

## Usage Pattern

**When to use this skill:**

1. Notice same issue coming up in multiple BOOPs
2. Run convergence detection
3. Verify with deployed system (curl/API/DB)
4. Check dispatch channel status
5. If convergence ≥3 AND dispatch open → escalate
6. If convergence ≥9 AND dispatch blocked → compress + Day-3

**When NOT to use:**

- Single BOOP (no convergence possible)
- Different issues across BOOPs (no convergence)
- Already escalated (no need to re-detect)

## Constitutional Reference

Per `feedback_cross_boop_convergence_signal.md`:
- 2 independent BOOPs same root cause = fix NOW

Per `feedback_convergence_must_pair_with_prod_verification.md`:
- Working-tree grep can amplify stale source
- MUST pair with deployed-system verification

Per `feedback_convergence_count_needs_dispatch_channel_check.md`:
- Convergence from cron sub-agents (cannot Task()) is NOT alone escalation
- Main-thread engagement signal determines tier

Per `feedback_cron_boop_detection_dispatch_gap.md`:
- Sub-agent cron cannot Task() dept-managers
- After 3+ identical cycles, compress to "No change — Day-N default"

---

**Remember: Convergence is a signal, not a failure. Verify first, then act.**
