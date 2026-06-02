---
name: architectural-truth-first
version: 1.0.0
author: aether
description: Mandatory investigation before any build. Triggers "this keeps happening", "still broken", "is X up to date" FORCE 5-10min code-archaeologist + pattern-detector pair BEFORE build. 2nd hot-fix patching 1st regression = STOP.
tags: [investigation, architecture, anti-pattern, code-archaeology, multi-probe]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Architectural Truth First

Mandatory investigation protocol before any build work.

## Core Principle

**"STOP. INVESTIGATE. THEN BUILD."**

When symptoms repeat or persist, the problem is architectural, not tactical.
Building without understanding = compounding technical debt.

## Trigger Phrases (AUTO-STOP)

When you hear these phrases, STOP immediately and investigate:

| Phrase | What It Signals |
|--------|-----------------|
| "This keeps happening" | Recurring symptom = root cause not addressed |
| "Still broken" | Previous fix didn't work = wrong diagnosis |
| "Is X up to date?" | Uncertainty about system state = architectural drift |
| "Let me patch this" (2nd time) | 2nd hot-fix patching 1st regression = STOP |
| "Why is this failing again?" | Regression = systemic issue |

## Mandatory Investigation Protocol

### Step 1: STOP Building (0 min)

**Do not write code. Do not deploy. Do not patch.**

If a 2nd hot-fix is patching a 1st regression → **FULL STOP**.

### Step 2: Invoke Investigation Pair (5-10 min)

**REQUIRED agents:**
- `code-archaeologist` - Historical analysis, git blame, change tracking
- `pattern-detector` - System patterns, architectural connections

```bash
# Example delegation
aether delegation:
  task: "Investigate recurring auth failure pattern"
  agents:
    - code-archaeologist: "Trace auth changes in last 30 days, identify regression point"
    - pattern-detector: "Identify architectural patterns in auth flow, find systemic issues"
  time_box: "10 minutes"
  output: "Root cause analysis + architectural recommendation"
```

### Step 3: Multi-Probe Verification

**NEVER rely on single verification method.**

Vary methodology across verification attempts:

| Probe Dimension | Variations |
|-----------------|------------|
| **Tool** | grep ↔ ripgrep ↔ curl ↔ DB query ↔ log analysis |
| **Input** | verb ↔ header ↔ query param ↔ fragment ↔ body payload |
| **Environment** | working tree ↔ deployed system ↔ staging ↔ prod |
| **Cache state** | cache-bust param ↔ fresh incognito ↔ curl no-cache |
| **Protocol** | OPTIONS preflight ↔ GET ↔ POST ↔ HEAD |

**Why this matters:**
- Single 200 response can mask CF stale-cache 404
- Working-tree grep can amplify stale source into false confidence
- OPTIONS-204 success ≠ GET-200 endpoint health
- Cache-bust probes may not match real user traffic

### Step 4: Match Real Traffic Patterns

**Synthetic monitors MUST match real user traffic.**

| Real User Pattern | Synthetic Probe Must Include |
|-------------------|------------------------------|
| Browser navigation (no cache-bust) | Probe without `?cb=123` param |
| Mobile app (specific User-Agent) | Include matching UA header |
| Authenticated requests (cookies) | Include auth cookies/tokens |
| CORS preflight (OPTIONS) | Test OPTIONS *and* GET |

**Anti-pattern:** Testing only with cache-bust params when real users don't use them.

### Step 5: Check Out-of-Repo Configuration

**Git is not the only source of truth.**

Cloudflare edge configuration lives in Dashboard, not git:

```bash
# Check CF Transform Rules (not in git)
curl -X GET "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/rulesets" \
  -H "Authorization: Bearer ${CF_API_TOKEN}"

# Check Page Rules
curl -X GET "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/pagerules" \
  -H "Authorization: Bearer ${CF_API_TOKEN}"

# Check Worker bindings (not in wrangler.toml)
curl -X GET "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/workers/scripts/${SCRIPT_NAME}/bindings" \
  -H "Authorization: Bearer ${CF_API_TOKEN}"
```

**Common blind spots:**
- Bulk Redirects
- Transform Rules
- R2 bucket bindings
- D1 database bindings
- Worker routes
- Page Rules

### Step 6: Document Root Cause (Required)

**Before any fix, document:**

1. **What was the symptom?** (User-visible behavior)
2. **What was the immediate cause?** (Code/config that failed)
3. **What was the root cause?** (Why did it happen?)
4. **What pattern enabled it?** (Architectural gap)
5. **How do we prevent recurrence?** (Systemic fix)

**Template:**
```markdown
## Root Cause Analysis

**Symptom:** [User-visible problem]
**Immediate Cause:** [Code/config that failed]
**Root Cause:** [Why it happened]
**Pattern:** [Architectural gap that enabled it]
**Prevention:** [Systemic fix to prevent recurrence]

**Investigation Time:** [X minutes]
**Agents Involved:** [code-archaeologist, pattern-detector]
```

### Step 7: Architectural Fix (Not Tactical Patch)

**Now you can build.**

But build the *architectural fix*, not another tactical patch.

| Tactical Patch | Architectural Fix |
|----------------|-------------------|
| "Add try/catch around failing code" | "Why is this code path uncovered by tests?" |
| "Hardcode the config value" | "Why is config not centralized?" |
| "Add another conditional" | "Why is business logic scattered?" |
| "Increase timeout" | "Why is this operation so slow?" |

## Examples

### Example 1: Recurring Auth Failure

**❌ WRONG (No Investigation):**
```
"Auth failing again. Let me add another check..."
[Patches code without understanding why]
```

**✅ RIGHT (Investigation First):**
```
STOP. This is the 3rd auth issue this month.

Invoke: code-archaeologist + pattern-detector
Finding: Auth middleware has 4 different implementations across codebase
Root Cause: No centralized auth module
Fix: Consolidate into single auth service with tests
```

### Example 2: "Still Broken" After Fix

**❌ WRONG (Patch the Patch):**
```
"Hmm, my fix didn't work. Let me try a different approach..."
[Adds 2nd patch without understanding why 1st failed]
```

**✅ RIGHT (Multi-Probe Verification):**
```
STOP. Why didn't the first fix work?

Multi-probe check:
1. Working tree grep: Shows fix present ✓
2. Deployed system curl: Returns 404 ✗
3. CF dashboard: Stale Worker deployment from 2 days ago

Root Cause: Worker deployment didn't happen after fix
Architectural Issue: No deployment verification step
Prevention: Add post-deploy health check to CI/CD
```

### Example 3: "Is X Up to Date?"

**❌ WRONG (Assume Yes):**
```
"Pretty sure it's current. Let me just update the part I need..."
```

**✅ RIGHT (Verify State First):**
```
STOP. Uncertainty about system state = architectural drift.

Investigation:
1. Check git: Last change 14 days ago
2. Check deployed: Worker script hash doesn't match git HEAD
3. Check CF edge config: Page Rule points to old route

Root Cause: Deployment manual, error-prone, no verification
Architectural Issue: No deployment automation + verification
Prevention: CI/CD pipeline with post-deploy verification
```

## Anti-Patterns

### ❌ Anti-Pattern 1: "Quick Fix" Mentality
**BAD:** "This will only take 5 minutes to patch"
**WHY:** 5-minute patches accumulate into unmaintainable systems

### ❌ Anti-Pattern 2: Single-Probe Confidence
**BAD:** "curl returned 200, it's fixed"
**WHY:** CF cache/stale deployment/routing rules can mask failures

### ❌ Anti-Pattern 3: Working-Tree-Only Verification
**BAD:** "grep shows the fix is there"
**WHY:** Working tree ≠ deployed system (git drift, CF edge config)

### ❌ Anti-Pattern 4: Skipping Investigation for "Obvious" Issues
**BAD:** "It's obviously a typo, no need to investigate"
**WHY:** "Obvious" symptoms often hide deeper architectural issues

### ❌ Anti-Pattern 5: Building Without Documentation
**BAD:** Fixing issue without documenting root cause
**WHY:** Team can't learn from the incident, likely to recur

## Verification Checklist

Before claiming "fixed":

- [ ] Root cause documented (not just symptom)
- [ ] Pattern identified (what architectural gap enabled it?)
- [ ] Prevention plan (how do we stop recurrence?)
- [ ] Multi-probe verification (varied methodology + inputs)
- [ ] Real traffic matched (synthetic probe = user pattern)
- [ ] Out-of-repo config checked (CF Dashboard, bindings)
- [ ] Deployed system verified (not just working tree)

## Integration with Other Skills

Works with:
- `code-archaeologist` - Historical analysis, change tracking
- `pattern-detector` - Architectural pattern recognition
- `day3-default-execution` - For investigation that exceeds time-box
- `multi-probe-verification` - Comprehensive system verification

## Constitutional Grounding

From MEMORY.md:
> "Architectural-truth-first: Triggers 'this keeps happening'/'still broken'/'is X up to date' FORCE 5-10min code-archaeologist+pattern-detector pair BEFORE BUILD. 2nd hot-fix patching 1st regression → STOP."
> "Multi-probe + vary methodology + match real traffic: Single 200 can mask CF stale-cache 404."

## Success Indicators

- [ ] Zero 2nd hot-fixes patching 1st regressions
- [ ] All recurring issues get investigation before build
- [ ] Root cause documented for every fix
- [ ] Multi-probe verification standard practice
- [ ] Out-of-repo config checked on system-state questions

## Time Investment

**Investigation:** 5-10 minutes
**Prevented future debugging:** 2-4 hours per incident
**ROI:** 12x-24x time savings

**"10 minutes of investigation saves hours of debugging."**

---

*Last Updated: 2026-05-20*
*Status: Constitutional*
