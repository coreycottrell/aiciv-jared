# IT Incident/Research: Cloudflare Management Guide for purebrain.ai

**Date**: 2026-03-12
**Type**: synthesis / reference
**Agent**: dept-it-support

## Summary

Produced a comprehensive Cloudflare management guide covering 4 topics as requested by Jared.

## Key Architecture Facts Confirmed

- purebrain.ai is a HYBRID stack: WordPress as content origin + CF as CDN/proxy + CF Pages as static staging
- CF Pages project: `purebrain-staging` (ID: 7c467c82-7f69-46a4-a337-53c57a6e30cc)
- Staging URL: https://purebrain-staging.pages.dev
- DNS: purebrain.ai → 188.114.96.3 / 188.114.97.3 (CF proxy IPs)
- CF Tunnel ID: fa55839c-e753-4a96-935c-cc58cf24b4b8 (routes api., portal., cc., *.purebrain.ai to server)
- CF Account email: jared@puretechnology.nyc
- CF Account ID: d526a3e9498dd167509003004df03290
- CF Pages API token: CF_PAGES_TOKEN in .env

## Patterns Documented

1. Team access = Cloudflare Member roles OR scoped API tokens per-AI
2. SEO metadata bakes into exported HTML from WordPress/Yoast — no SEO plugin needed separately on CF Pages
3. GA4 must be embedded in WP plugin head injection to survive page exports
4. GSC verification = DNS TXT method is most robust (survives hosting changes)
5. Brevo requires DKIM/SPF TXT records in Cloudflare DNS
6. CF Tunnel must be running on server for all subdomains to work

## Output File

`/home/jared/projects/AI-CIV/aether/exports/cloudflare-management-guide-2026-03-12.md`

## Prevention Notes

- Always check CF Tunnel status before debugging subdomain issues
- New team member access = create scoped API token, not share account credentials
- SEO continuity = keep WordPress RankMath/Yoast active, all meta bakes into exports automatically
