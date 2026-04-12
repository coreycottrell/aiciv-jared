# Brevo Delivery Template via API Pattern

**Date**: 2026-02-24 (Session 38)
**Context**: Needed automated email delivery for website analysis reports

## What Was Done
- Created Brevo template ID 22 via Brevo SMTP API (not manual UI)
- Template: "Website Analysis Report Delivery" - active, verified
- Reply-to: jared@puretechnology.nyc (per email address rules)
- From: purebrain@puremarketing.ai

## Key Pattern
- Use Brevo API to create templates programmatically (faster than UI)
- Template IDs are sequential - track in brevo-template-registry
- Always verify template is active after creation
- Pair with `tools/website_analysis_delivery.py` for full automation pipeline

## Integration
- Delivery pipeline: `tools/website_analysis_delivery.py` → Brevo template 22 → client inbox
- Template registry: `.claude/memory/operational/brevo-template-registry-2026-02-23.md`
- Triggered by client-marketing agent completing website analysis
