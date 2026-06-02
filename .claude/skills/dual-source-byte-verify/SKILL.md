---
name: dual-source-byte-verify
version: 1.0.0
author: skills-master
description: Verify byte-identical content across dual-source CF Pages deployments to prevent silent overwrites
tags: [verification, cloudflare, pages, deployment, integrity]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Dual-Source Byte Verification

Verify byte-identical content across dual-source Cloudflare Pages files to detect silent overwrites.

## The Problem

Two separate sources write to shared CF Pages files:
- `aether/exports/cf-pages-deploy/` (Aether reference)
- `puretechnyc/purebrain-site/` (Chy's canonical source)

When both touch the same file, silent overwrites can occur. The last deploy wins, potentially overwriting correct content.

## Critical Paths to Verify

Priority files (check these first):

1. **Payment pages**:
   - `/insiders/index.html`
   - `/pay-insiders/index.html`
   - `/pay-awakened/index.html`
   - `/pay-partnered/index.html`
   - `/pay-unified/index.html`
   - `/investment-opportunity/index.html`

2. **Homepage**:
   - `/index.html`

3. **Case studies**:
   - `/actual-intelligence-case-studies/index.html`

4. **Team page**:
   - `/our-team/index.html`

## Verification Protocol

```bash
# 1. Identify shared files
comm -12 \
  <(cd /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy && find . -type f | sort) \
  <(cd /home/jared/projects/purebrain-site && find . -type f | sort) \
  > /tmp/shared-files.txt

# 2. Compare checksums for each shared file
while IFS= read -r file; do
    aether_md5=$(md5sum "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/$file" 2>/dev/null | awk '{print $1}')
    chy_md5=$(md5sum "/home/jared/projects/purebrain-site/$file" 2>/dev/null | awk '{print $1}')
    
    if [ "$aether_md5" != "$chy_md5" ]; then
        echo "MISMATCH: $file"
        echo "  Aether: $aether_md5"
        echo "  Chy:    $chy_md5"
    fi
done < /tmp/shared-files.txt
```

## Quick Critical-Path Check

```bash
# Check just the critical paths
for path in \
    "insiders/index.html" \
    "pay-insiders/index.html" \
    "pay-awakened/index.html" \
    "pay-partnered/index.html" \
    "pay-unified/index.html" \
    "index.html" \
    "actual-intelligence-case-studies/index.html" \
    "our-team/index.html"
do
    aether_file="/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/$path"
    chy_file="/home/jared/projects/purebrain-site/$path"
    
    if [ -f "$aether_file" ] && [ -f "$chy_file" ]; then
        aether_md5=$(md5sum "$aether_file" | awk '{print $1}')
        chy_md5=$(md5sum "$chy_file" | awk '{print $1}')
        
        if [ "$aether_md5" = "$chy_md5" ]; then
            echo "✓ $path - MATCH"
        else
            echo "✗ $path - MISMATCH"
            echo "  Aether: $aether_md5"
            echo "  Chy:    $chy_md5"
        fi
    else
        echo "⚠ $path - FILE MISSING in one or both repos"
    fi
done
```

## When to Run

1. **Before any CF Pages deploy** (pre-flight check)
2. **After detecting production discrepancies**
3. **Weekly audit** (scheduled verification)
4. **After dual-source content edits** (post-change validation)

## Anti-Patterns

### Anti-Pattern 1: Trusting Last Deploy
- BAD: Assuming the most recent deploy is correct
- GOOD: Verify byte-identity before accepting changes

### Anti-Pattern 2: Partial Verification
- BAD: Only checking one critical path
- GOOD: Check all payment pages + homepage + case studies

### Anti-Pattern 3: Visual Inspection Only
- BAD: "Looks the same in browser"
- GOOD: md5sum verification for byte-identical match

### Anti-Pattern 4: Post-Deploy Discovery
- BAD: Finding mismatches after production deploy
- GOOD: Pre-flight verification before any deploy

## Mismatch Response Protocol

When mismatch detected:

```
1. STOP any pending deploys
2. Identify which version is correct:
   - Check git history
   - Review recent changes
   - Consult owning agent (Aether vs Chy)
3. Propagate correct version to BOTH sources
4. Verify byte-identity restored
5. Document root cause in memory
6. Resume deploy
```

## Full Verification Script

```bash
#!/bin/bash
# dual-source-verify.sh

AETHER_ROOT="/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy"
CHY_ROOT="/home/jared/projects/purebrain-site"
REPORT="/tmp/dual-source-verify-$(date +%Y%m%d-%H%M%S).txt"

echo "Dual-Source Byte Verification Report" > "$REPORT"
echo "Generated: $(date)" >> "$REPORT"
echo "======================================" >> "$REPORT"
echo "" >> "$REPORT"

# Critical paths
CRITICAL_PATHS=(
    "insiders/index.html"
    "pay-insiders/index.html"
    "pay-awakened/index.html"
    "pay-partnered/index.html"
    "pay-unified/index.html"
    "investment-opportunity/index.html"
    "index.html"
    "actual-intelligence-case-studies/index.html"
    "our-team/index.html"
)

MISMATCHES=0

for path in "${CRITICAL_PATHS[@]}"; do
    aether_file="$AETHER_ROOT/$path"
    chy_file="$CHY_ROOT/$path"
    
    if [ ! -f "$aether_file" ]; then
        echo "⚠ $path - MISSING in Aether repo" | tee -a "$REPORT"
        continue
    fi
    
    if [ ! -f "$chy_file" ]; then
        echo "⚠ $path - MISSING in Chy repo" | tee -a "$REPORT"
        continue
    fi
    
    aether_md5=$(md5sum "$aether_file" | awk '{print $1}')
    chy_md5=$(md5sum "$chy_file" | awk '{print $1}')
    
    if [ "$aether_md5" = "$chy_md5" ]; then
        echo "✓ $path - MATCH" | tee -a "$REPORT"
    else
        echo "✗ $path - MISMATCH" | tee -a "$REPORT"
        echo "  Aether: $aether_md5" | tee -a "$REPORT"
        echo "  Chy:    $chy_md5" | tee -a "$REPORT"
        MISMATCHES=$((MISMATCHES + 1))
    fi
done

echo "" >> "$REPORT"
echo "======================================" >> "$REPORT"
echo "Total mismatches: $MISMATCHES" >> "$REPORT"

if [ $MISMATCHES -gt 0 ]; then
    echo "" >> "$REPORT"
    echo "⚠ ACTION REQUIRED: Resolve mismatches before deploy" >> "$REPORT"
    exit 1
else
    echo "" >> "$REPORT"
    echo "✓ All critical paths verified byte-identical" >> "$REPORT"
    exit 0
fi
```

## Integration with Other Skills

Works with:
- `github-operations` - Pre-deploy verification gate
- `verification-before-completion` - Deploy completion evidence
- `cf-pages-deployment` - Deployment workflow integration

## Constitutional Grounding

From MEMORY.md:
> "CF Pages dual-source byte-identical: every shared file across aether/exports/cf-pages-deploy/ AND puretechnyc/purebrain-site/."

Incident reference: 2026-05-11 /our-team/ silent overwrite.

---

*Last Updated: 2026-05-20*
*Status: Production-ready*
