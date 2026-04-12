#!/bin/bash
# Run this to send the CTO levels-up audit report to the portal
# Created by: cto agent 2026-03-06
/home/jared/purebrain_portal/portal_send_file.sh --text "CTO Report: 'How This Levels You Up' Link Audit (2026-03-06)

AUDIT COMPLETE — ALL 4 PAGES CHECKED

❌ /partnered/ — LINK MISSING
  CTA: 'Get Partnered Now' / 'Activate Your Partnered AI'
  Should link to: /partnered-how-this-levels-you-up/

❌ /unified/ — LINK MISSING
  CTA: 'Activate Unified' (animated button)
  Should link to: /unified-how-this-levels-you-up/

❌ /pay-test-2/ (ID 689) — LINK MISSING
  Password-protected multi-tier page
  Needs links under both Partnered + Unified cards

❌ /pay-test-sandbox-3/ (ID 1232) — LINK MISSING
  Confirmed missing by browser QA (2026-03-04)
  Button IDs: partnerCta + unifiedCta

DEPLOYMENT SCRIPT READY:
python3 /home/jared/projects/AI-CIV/aether/tools/deploy_levels_up_links.py

Script handles: page lookup by slug, smart button injection, Elementor cache clear.
Full report: /home/jared/projects/AI-CIV/aether/exports/cto-levels-up-audit-20260306.md"

echo "Portal message sent."
