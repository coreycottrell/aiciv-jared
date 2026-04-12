# SD# Task: RideHovr Sales Presentation Page

**Date**: 2026-03-03
**Task Type**: Sales Presentation Page Build + Deploy
**Agent**: dept-sales-distribution

---

## Company Research: RideHovr (HOVR)

- **HQ**: Toronto, Canada
- **Model**: Rideshare platform — subscription-based for drivers (NO commission cuts, flat monthly fee)
- **Differentiator vs Uber/Lyft**: Zero commission for drivers — major driver loyalty hook
- **Funding**: $1M+ raised
- **Team**: Self-described "small but mighty team"
- **Tech**: Next.js, mobile-first (iOS + Android apps)
- **Enterprise Clients**: Rogers, Sony, BMO, RBC, Adyen, Adway
- **Expansion**: Toronto-based, actively expanding to new cities
- **CEO**: Not publicly prominent — not findable via Crunchbase, BetaKit, LinkedIn (private/early stage)
- **Website**: ridehovr.com (limited public info, no team page visible)

## Pain Points Identified

1. Driver acquisition and retention at scale
2. Fragmented ops as they expand city by city
3. Corporate client management without big team
4. Competing against Uber/Lyft with leaner resources
5. Institutional knowledge staying only in people's heads

## Deployment Details

- **WordPress Page ID**: 1231
- **Live URL**: https://purebrain.ai/purebrain-x-hovr-ai-partnership-brief/
- **Password**: hovr2026
- **Template**: default (empty string)
- **Status**: publish (password-protected)
- **WP User**: Aether (PUREBRAIN_WP_APP_PASSWORD)

## Files

- **HTML Source**: `/home/jared/projects/AI-CIV/aether/exports/departments/sales-distribution/ridehovr-sales-page.html`
- **Google Drive**: https://drive.google.com/file/d/1vCGrQm4Ni4MQ_egvMnlsToqbtUffi-gx/view
- **Drive Folder**: 1QaBu0gO7__my-AziZ2WD_PAuhkfLjQoN (purebrain.ai HTML files)

## Learnings for Future Sales Pages

1. CEO research for early-stage startups often yields nothing public — build the page around company intel
2. WordPress deploy pattern: `PUREBRAIN_WP_APP_PASSWORD` + user `Aether` + site `https://purebrain.ai`
3. Password-protected pages via WP REST API: include `"password": "value"` in page_data payload
4. WP REST API returns `"content": {"protected": true}` when password is set — use for verification
5. GDriveManager.upload_file() signature: `(local_path, folder_id, new_name=None)` — not `parent_folder_id`
6. Page content must be wrapped in `<!-- wp:html -->` block to prevent wpautop from destroying CSS/JS
