# BrainScore Calibration Recalibration

**Date**: 2026-04-30
**Type**: operational
**Topic**: ARA Index scoring recalibration across all 5 dimensions

## What Was Done

Recalibrated all 5 BrainScore dimensions in `/workers/ara-index/src/worker.js`:
- A1: Quality-based structural checks (not just file existence)
- A2: 6+ char positioning words only, stopword filter
- A3: Graduated 0-10 per model (position-aware)
- A4: Requires named entities/campaigns/events (not just keywords)
- A5: Expanded distinctiveness detection, negative signal check

## Key Learnings

- Canva blocks bot fetching aggressively — low structural scores are valid signal
- LLM-based dimensions (A2-A5) have inherent variance of +/-5 per run
- McDonald's and Canva don't get recommended by AI models for their categories
- PureBrain scores higher than expected on A1/A5 because it genuinely has good structure and distinctive voice

## Files

- Worker: `/home/jared/projects/AI-CIV/aether/workers/ara-index/src/worker.js`
- Results: `/home/jared/projects/AI-CIV/aether/exports/portal-files/brainscore-calibration-2026-05-02.md`
- Deploy command: `CLOUDFLARE_API_TOKEN=... npx wrangler deploy` from workers/ara-index/
