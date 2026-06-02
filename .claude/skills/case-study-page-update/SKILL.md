---
name: case-study-page-update
version: 1.0.0
author: skills-master
description: Update Actual Intelligence case studies page with skill counts, timeline, and metrics
tags: [case-study, website, deployment, metrics, git]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Case Study Page Update

Update the Actual Intelligence case studies page at purebrain.ai/actual-intelligence-case-studies/ with current metrics.

## Page Location

**Source file**: `/home/jared/projects/purebrain-site/actual-intelligence-case-studies/index.html`

**Live URL**: `https://purebrain.ai/actual-intelligence-case-studies/`

**Git repo**: `puretechnyc/purebrain-site` (main branch)

## Deploy Protocol

**CONSTITUTIONAL**: Git is the only source of truth.

```bash
# 1. Make changes to local file
# Edit /home/jared/projects/purebrain-site/actual-intelligence-case-studies/index.html

# 2. Git commit
cd /home/jared/projects/purebrain-site
git add actual-intelligence-case-studies/index.html
git commit -m "Update case study metrics: [description]"

# 3. Push to main
git push origin main

# 4. Wait for CF Pages propagation (90-150s)
sleep 120

# 5. Verify with curl polling
for i in {1..5}; do
    echo "Verification attempt $i..."
    curl -s "https://purebrain.ai/actual-intelligence-case-studies/" | grep -o "VERIFICATION_STRING"
    sleep 20
done
```

## Key Sections to Update

### 1. Skills Count Card

Location: Top stat card

```html
<div class="stat-card">
    <div class="stat-number">[NUMBER]</div>
    <div class="stat-label">Claude Code Native Skills</div>
</div>
```

**Update when**: New skills added to `.claude/skills/`

### 2. Timeline Entry

Location: Timeline section

```html
<div class="timeline-item">
    <div class="timeline-marker"></div>
    <div class="timeline-content">
        <h3>[Date] - Skills Milestone</h3>
        <p>Reached [NUMBER] production-ready skills...</p>
    </div>
</div>
```

**CRITICAL**: When changing skill count card, MUST also add/update timeline entry.

### 3. Speed Cards

Location: Efficiency metrics section

```html
<div class="stat-number">[NUMBER]%</div>
<div class="stat-label">Faster Than Traditional Development</div>
```

**Update when**: New efficiency measurements captured

### 4. Live Properties Grid

Location: Technical showcase section

```html
<div class="property-item">
    <span class="property-label">Skills Deployed:</span>
    <span class="property-value">[NUMBER]</span>
</div>
```

**Update when**: Infrastructure changes (agents, skills, flows)

## Atomic Update Protocol

**Rule**: Skills count card and timeline MUST be updated together.

```bash
# WRONG: Update card only
# Update skill count card from 42 → 47
# Forget to add timeline entry

# RIGHT: Atomic update
# 1. Update skill count card: 42 → 47
# 2. Add timeline entry: "December 2025 - Skills Milestone: Reached 47..."
# 3. Commit both changes together
```

## CF Pages Propagation

**Timing**: 90-150s from git push to live

**Verification window**: Wait minimum 120s before polling

**Anti-pattern**: Checking <60s may show stale content

## Verification Script

```bash
#!/bin/bash
# verify-case-study-update.sh

TARGET_STRING="$1"
URL="https://purebrain.ai/actual-intelligence-case-studies/"
MAX_ATTEMPTS=10
WAIT_SECONDS=20

echo "Waiting 120s for CF Pages propagation..."
sleep 120

for i in $(seq 1 $MAX_ATTEMPTS); do
    echo "Verification attempt $i/$MAX_ATTEMPTS..."
    
    if curl -s "$URL" | grep -q "$TARGET_STRING"; then
        echo "✓ Verification successful: '$TARGET_STRING' found"
        exit 0
    fi
    
    echo "  Not found yet, waiting ${WAIT_SECONDS}s..."
    sleep $WAIT_SECONDS
done

echo "✗ Verification failed after $MAX_ATTEMPTS attempts"
exit 1
```

Usage:
```bash
# After updating skill count to 47
bash verify-case-study-update.sh "47"

# After updating efficiency metric to 115%
bash verify-case-study-update.sh "115%"
```

## Anti-Patterns

### Anti-Pattern 1: Local Deploy
- BAD: Using cf-deploy.py or direct API
- GOOD: Git commit + push to main (only valid method)

### Anti-Pattern 2: Partial Update
- BAD: Updating skill count card without timeline entry
- GOOD: Atomic update of both card and timeline

### Anti-Pattern 3: Premature Verification
- BAD: curl check immediately after push
- GOOD: Wait 120s minimum for propagation

### Anti-Pattern 4: Single Verification Attempt
- BAD: One curl, declare success/failure
- GOOD: Poll 5-10 times with 20s spacing

### Anti-Pattern 5: Forgetting PROTECTED_PATHS
- BAD: Assuming PROTECTED_PATHS prevents all issues
- GOOD: Manual GET probe on every protected path after deploy

## Common Updates

### Add New Skill to Count
```bash
cd /home/jared/projects/purebrain-site/actual-intelligence-case-studies

# 1. Update stat card
sed -i 's/<div class="stat-number">42/<div class="stat-number">47/' index.html

# 2. Add timeline entry (manual - find insertion point)
# Add new timeline-item div with current date + description

# 3. Commit + push
git add index.html
git commit -m "Update case study: 42 → 47 skills deployed"
git push origin main

# 4. Verify
sleep 120
curl -s "https://purebrain.ai/actual-intelligence-case-studies/" | grep -o "47"
```

### Update Efficiency Metric
```bash
cd /home/jared/projects/purebrain-site/actual-intelligence-case-studies

# Update speed card
sed -i 's/>115%</>125%</' index.html

git add index.html
git commit -m "Update efficiency metric: 115% → 125%"
git push origin main

sleep 120
curl -s "https://purebrain.ai/actual-intelligence-case-studies/" | grep "125%"
```

## Integration with Other Skills

Works with:
- `github-operations` - Git workflow
- `verification-before-completion` - Deploy verification
- `dual-source-byte-verify` - Pre-deploy integrity check

## Constitutional Grounding

From MEMORY.md:
> "Git is the only source of truth. Production state must derive from `git HEAD`."

> "CF Pages github:push propagation 90-150s: verification <60s may show stale. Wait ≥120s OR poll CF API."

> "Case study page update: BOTH the card number AND the timeline entry when changing counts."

---

*Last Updated: 2026-05-20*
*Status: Production-ready*
