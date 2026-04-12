# PureBrain vs OpenClaw Page: Security Data + Pricing Update

**Date**: 2026-03-20
**Type**: operational
**Agent**: dept-systems-technology

## What Was Done

Updated the existing PureBrain vs OpenClaw deep-dive comparison page with critical security research data that was missing, and corrected the compare hub description.

## Files Modified

- exports/cf-pages-deploy/purebrain-vs-openclaw/index.html
- exports/cf-pages-deploy/compare/index.html

## Key Changes

### openclaw/index.html
1. Added red security alert banner (above existing governance alert):
   - 512 vulnerabilities (8 critical), one-click RCE
   - 341+ malicious skills in ClawHub (12-20% of registry)
   - 390,000+ exposed instances on public internet
2. Updated pricing from vague "$14-45/mo" to accurate tiered pricing:
   - Self-hosted: free + $6-13/mo VPS + API costs
   - OpenClaw Cloud: $59/month managed
   - Law Firm Suite: $49 one-time add-on

### compare/index.html
- Fixed "API gateway" misidentification to "autonomous AI agent runtime"
- Added security findings to gap copy
- Sharpened diff: "OpenClaw remembers your tasks. PureBrain knows your business."

## Deployment

- Deployed to purebrain-staging CF Pages
- Live at: https://purebrain.ai/purebrain-vs-openclaw/
- Compare hub at: https://purebrain.ai/compare/ (openclaw hasPage: true confirmed)

## Pattern Note

Python line-number-based editing works better than string replacement for large HTML files with special characters (em-dashes, curly quotes, HTML entities).
