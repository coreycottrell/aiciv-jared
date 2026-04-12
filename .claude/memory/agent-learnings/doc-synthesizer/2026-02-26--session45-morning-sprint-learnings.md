# Session 45: Morning Sprint Learnings

**Date**: 2026-02-26
**Type**: operational-pattern + teaching + gotcha
**Agent**: doc-synthesizer
**Confidence**: high
**Topic**: 7 reusable patterns from the Feb 26 morning sprint

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/doc-synthesizer/` for session-level patterns
- Found: Session 42, 43, 44 records — strong prior art on morning sprint format
- Applying: Same section structure (pattern name, root cause, reusable rule)

---

## 1. Morning Delivery Rule (NEW STANDING ORDER)

**Pattern**: Blog content package = human delivery. Everything else = autonomous Drive filing.

**What Jared established**:
- Blog post + LinkedIn newsletter + LinkedIn post + banner are delivered via Telegram every morning for review
- ALL other overnight work files go directly to Google Drive without needing Jared's attention
- This is the separation of "needs human eyes" vs "file and forget"

**Reusable rule**:
> After any overnight sprint, route outputs into two queues:
> 1. Blog content package → Telegram delivery (Jared reviews before distribution)
> 2. Everything else → Drive auto-file, no review needed

**Why it matters**: Prevents Jared from being overwhelmed by Drive notifications while ensuring the one daily deliverable that needs his judgment always lands in front of him.

---

## 2. BOOP Schedule Overhaul (Sub-Daily → Twice-Daily)

**What changed**:
- Previous: Multiple sub-daily BOOP intervals (25min, 30min, 60min, 90min, 2hr)
- New: All reduced to twice-daily (every 12 hours)
- Staggered by 30-minute offsets so no two BOOPs fire simultaneously
- Cap: Max 2 tasks per BOOP cycle

**Config location**: `.claude/scheduled-tasks-state.json`

**Pattern**:
> When BOOP cycles overlap or fire too frequently, the conductor becomes a BOOP machine
> rather than a conductor. Twice-daily with stagger is the right frequency — active but
> not thrashing.

**Gotcha to avoid**: If adding new scheduled tasks, verify they stagger against existing 12hr cycles. A 12hr task starting at 08:00 and another at 08:00 are the same as un-staggered even if defined separately.

---

## 3. WordPress Blog Wrapper Class Bug (CRITICAL CSS GOTCHA)

**Root cause**: Publishing with `<div class="pb-blog-content">` breaks ALL theme CSS scoping.

**What breaks**:
- Heading spacing
- List styling
- Link colors (orange links stop working)
- 760px centered layout

**Why it breaks**: The WordPress theme scopes all those rules under `.pb-blog-post` (the `<article>` tag class). A `<div>` with a different class sits outside that scope. The CSS never applies.

**Fix**:
```html
<!-- WRONG -->
<div class="pb-blog-content">...</div>

<!-- RIGHT -->
<article class="pb-blog-post">...</article>
```

**Diagnosis signal**: "Formatting looks nothing like other posts" — this is the first thing to check when a newly published post looks visually wrong compared to existing posts.

**Reusable rule**:
> Always match the container element AND class to what existing posts use. Check a working
> post's source before deploying a new one. The article element is not interchangeable with div.

---

## 4. SSL "Not Secure" Indicator Fix Pattern

**Problem**: Browser showing "not fully secure" despite HTTPS being present.

**Root cause**: CSP header was set to `Content-Security-Policy-Report-Only` mode — this logs violations but does NOT enforce them, and some browsers treat report-only mode as a signal that the site isn't fully hardened.

**Fix applied**:
1. Promoted header from `Content-Security-Policy-Report-Only` to `Content-Security-Policy` (enforced)
2. Added `preload` directive to HSTS header
3. Verified all pages clean of mixed content BEFORE promoting (order matters — promote before verification = potential breakage)

**Pattern**:
> Report-Only CSP = security theater. It looks like you have a policy but you don't.
> Only promote to enforced CSP after verifying no mixed content exists anywhere.
> Sequence: audit for mixed content → fix any violations → enforce CSP → add HSTS preload.

---

## 5. XSS Security Fix Pattern (Chatbox v44)

**Vulnerability found**: 4 user inputs (firstName, company, role, goal) were passed unsanitized to `aiSay()` which uses `innerHTML`.

**Fix**: Wrap all with existing `sanitizeText()` function that was already present in the codebase.

**Status at end of session**: Fixed locally, NOT yet deployed.

**Pattern**:
> When an `innerHTML` call takes user-supplied input, it is an XSS vector.
> The pattern to search: grep for `aiSay(` calls where the argument contains a variable
> that originated from a form input. Check that variable's path from input → sanitizer → output.

**Gotcha**: The fix already existed (`sanitizeText()` was in scope) — the bug was an omission,
not a missing capability. Always search for existing sanitizers before writing new ones.

**Deployment reminder**: Local-only fix must be deployed before the security improvement is real.
"Fixed" without deployment = vulnerability still live.

---

## 6. WordPress Plugin Version Drift Gotcha

**Problem**: exports/ folder contains plugin ZIP files (v4.6.1, v4.6.2) but the LIVE deployed version is v6.1.0. Reading exports/ to determine current version gives a dangerously wrong answer.

**Root cause**: Deploy scripts update the source at `tools/security/purebrain-security/` directly. The exports/ folder is a graveyard of old builds, not a registry of what's live.

**Fix pattern**:
```bash
# CORRECT: read version from the live source
grep "Version:" tools/security/purebrain-security/purebrain-security.php

# WRONG: infer version from exports/ filenames
ls exports/purebrain-security-*.zip
```

**Reusable rule**:
> The canonical version of any deployed artifact lives in its source directory, not in exports/.
> Exports/ is a snapshot history, not a state tracker. Always read from source.

---

## 7. jareddsanborn.com WordPress Credentials Gotcha

**Problem**: Attempted to authenticate to jareddsanborn.com WP REST API as `jared`. Got 401.

**Root cause**: The username is NOT 'jared' — it is the value of the `WORDPRESS_USER` env var, which is `AetherPureBrain.ai`.

**Fix**:
```python
# CORRECT
username = os.getenv('WORDPRESS_USER')  # AetherPureBrain.ai

# WRONG — hardcoded assumption
username = 'jared'
```

**MEMORY.md already has**: `jareddsanborn.com: user=jared` — this is WRONG and was the source of the bug. The correct value is in `.env` as `WORDPRESS_USER`.

**Note for MEMORY.md update**: The "WordPress Credentials" entry in MEMORY.md contains an error. Should read `WORDPRESS_USER env var` not `user=jared`.

**Reusable rule**:
> Never hardcode WordPress usernames. Always read from env vars. jareddsanborn.com uses a
> non-obvious username that looks nothing like the domain owner's name.

---

## Session 45 Summary

| Pattern | Type | Impact |
|---------|------|--------|
| Morning delivery rule | standing-order | Prevents Jared overwhelm, ensures blog review |
| BOOP twice-daily | schedule-change | Stops conductor from thrashing |
| Blog wrapper class bug | critical-css-gotcha | Root cause of "looks wrong" posts |
| CSP enforced vs report-only | security-pattern | Real hardening vs theater |
| XSS sanitizeText pattern | security-pattern | Existing fix, omission bug |
| Plugin version drift | deployment-gotcha | Read from source, not exports/ |
| WP credentials from env | credential-gotcha | Never hardcode usernames |

---

*Written by doc-synthesizer — 2026-02-26*
*Session: 45 (morning sprint, Feb 26 2026)*
