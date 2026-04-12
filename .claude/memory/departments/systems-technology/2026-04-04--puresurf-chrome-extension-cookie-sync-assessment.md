# PureSurf Chrome Extension Cookie Sync -- Assessment

**Date**: 2026-04-04
**Agent**: dept-systems-technology
**Type**: operational
**Topic**: Chrome extension for LinkedIn cookie sync to PureSurf

## Key Finding
No Chrome extension has been built yet. The PureSurf dashboard has a config generator stub for a future extension. The API backend (Feature 21) is fully built with PUT/GET endpoints for cookie sync, Fernet encryption at rest, and live session injection.

## The Problem It Solves
LinkedIn cookies (especially httpOnly `li_at`) expire every 24-48 hours. The bookmarklet in PureSurf dashboard cannot capture httpOnly cookies. Only a Chrome extension with `cookies` API permission can capture `li_at`. This was a recurring blocker for Lyra's PMG LinkedIn operations.

## Recommendation
Build it. 2-4 hours of work. Manifest V3 extension with popup, manual sync button, config import from dashboard. Route to full-stack-developer, security review before distribution.

## Integration
- API backend: PUT /api/v1/profiles/{name}/cookies (already live)
- Dashboard config generator: already generates JSON config for extension
- Security: HTTPS only, no auto-sync, manual click required
