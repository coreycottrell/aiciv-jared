# Operational Blockers: Netlify Suspension + Gemini Quota

**Date**: 2026-02-26
**Type**: operational-blocker
**Agent**: doc-synthesizer
**Topic**: Active service outages affecting deployment and image generation

---

## Netlify — SUSPENDED (Credit Limit)

- **Status**: Account suspended due to credit limit exceeded
- **Impact**: Cannot deploy to ANY Netlify site — hub dashboard, sageandweaver blog, new deploys
- **Resolution**: Jared must update billing on Netlify account
- **Workaround**: WordPress-only deploys still work (purebrain.ai, jareddsanborn.com)

## Gemini API — Image Quota Exhausted

- **Status**: Daily generation limit hit during Session 44
- **Impact**: Cannot generate images via Gemini 3 Pro Image API
- **Resolution**: Wait for daily quota reset (typically midnight PT)
- **Workaround**: Programmatic banners via Python Pillow library (1200x630 with brand colors)
  - Pattern: Pure Tech Blue (#2a93c1) + Orange (#f1420b) gradient, white text
  - Not as polished as Gemini but functional for blog banners

## Check Before Starting Image/Deploy Work

```bash
# Test Gemini quota
python3 -c "from google import generativeai; print('quota check')"

# Test Netlify
netlify status 2>&1 | head -5
```

If either is still blocked, skip those tasks and note in scratch-pad.
