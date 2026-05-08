# Morning Pulse Verification - Rehydration Gap Found

**Date**: 2026-04-14
**Type**: gotcha
**Topic**: 777.purebrain.ai Morning Pulse save works, UI rehydration on refresh does NOT

## Findings
- Deployment `c91e6b54` confirmed live: served HTML contains `morning-pulse-manual-v1` and 3 `submitMorningPulse` refs
- Submit path works end-to-end: console logs `[Morning Pulse] submitMorningPulse() invoked → manual drop persisted to localStorage → sheet write result=OK`
- Green badges "Saved 4:26 PM" appear — sheet writes succeeded
- `localStorage.morning-pulse-manual-v1` contains proper JSON with all 3 priorities + combined field
- **BUG**: After hard refresh on same context, `#morning-pulse-items` still shows "No priorities set yet today. Approve suggestions above or drop manually." despite localStorage being populated
- Rehydration logic either not running on load, or not targeting `#morning-pulse-items` render

## Root Cause Hypothesis
The safety-net localStorage write works, but the READ/rehydrate-on-init path is missing/broken. Need ST# to check boot sequence for code that reads `morning-pulse-manual-v1` and renders into `#morning-pulse-items`.

## Screenshot
/tmp/mp-final-verify.png

## Console Evidence Captured
All 6 expected `[Morning Pulse]` log lines fired on submit.
