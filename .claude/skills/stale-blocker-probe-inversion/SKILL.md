---
status: provisional
tick_count: 0
last_used: 2026-05-22
introduced: 2026-05-22
---
# Stale Blocker Probe Inversion

**Purpose**: When a recurring health check reports the same failure across 5+ cycles, invert the hypothesis — assume the probe methodology is broken, not the target system.

**Origin**: 2026-05-22 Handshake Queue incident. 777-api was healthy for 10+ BOOPs, but sub-agent probes missed the Origin header, making every cycle report "still broken."

## Core Rule

> After 5+ BOOPs (or equivalent monitoring cycles) reporting the same failure with NO target-side change, **INVERT**: assume your probe is broken, not the target. Verify via alternate methodology.

## When to Apply

- Same "broken" status across 5+ consecutive monitoring cycles
- Target system shows no other symptoms (other endpoints healthy, no error spikes)
- Fix attempts on the "target" have no effect
- The same diagnostic command is copy-pasted across cycles

## Diagnostic Steps

1. **Count persistence**: How many cycles has this exact failure been reported?
2. **Check target independently**: Can you reach it via browser, different tool, or different auth?
3. **Audit the probe itself**:
   - Auth headers present and correct?
   - Param names exact (case-sensitive)?
   - Value format matching API spec (encoding, delimiters)?
   - Endpoint URL correct (not a stale/cached reference)?
4. **Vary the methodology**: If using curl, try httpie. If using API, try Dashboard. If using GET, check the Worker logs.
5. **Compound failure check**: APIs often require 3 things simultaneously (auth + param name + param format). Fixing 1 of 3 still returns failure — check all three dimensions.

## Anti-Pattern This Prevents

**"Echo Chamber Diagnosis"**: When every monitoring cycle uses the same broken probe command, each cycle's "confirmation" of the failure is actually just re-confirming the probe bug. The system appears more broken with each passing BOOP, but it was healthy all along.

## Examples

### 777-api Handshake Queue (2026-05-22)
- **Symptom**: "Not found" for 10+ BOOPs
- **Assumed cause**: Sheet permissions or tab encoding
- **Actual cause**: Probe missing Origin header + wrong param name + wrong range format
- **Resolution**: Fixed all three dimensions simultaneously

### R2 Binding Mismatch (2026-05-19)
- **Symptom**: 404 on all social media uploads
- **Assumed cause**: Upload endpoint broken
- **Actual cause**: Worker binding name (`purebrain-social-uploads`) didn't match bucket name (`purebrain-uploads`)

## Integration with Existing Skills

- Complements `cross-boop-convergence-detection` (which assumes the signal is truthful)
- Extends `multi-probe-diagnosis-required` (which mandates varying methodology)
- Predecessor to `architectural-truth-first` (which forces code-level investigation)

## Gotchas

- Don't invert too early (< 3 cycles) — sometimes things are genuinely broken
- The threshold (5 cycles) is a guideline, not absolute — context matters
- After inverting successfully, update the canonical probe command for future cycles
