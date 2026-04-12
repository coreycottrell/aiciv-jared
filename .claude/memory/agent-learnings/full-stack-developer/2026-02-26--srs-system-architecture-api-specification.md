# Memory: SRS — System Architecture and API Specification

**Date**: 2026-02-26
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Produced comprehensive SRS sections for PureBrain.ai for agency quoting

---

## What Was Built

Full formal SRS document covering 4 major sections:
1. System Architecture Overview (ASCII diagram + 7 service profiles)
2. API Specifications (all endpoints with full request/response schemas)
3. Data Flow Diagrams (3 complete flows in text/ASCII)
4. Deployment Architecture (per-platform deployment instructions)

**Output file**: `/home/jared/projects/AI-CIV/aether/exports/SRS-System-Architecture-API-Specification.md`
**Size**: 1,426 lines, ~53 KB

---

## Key Architecture Facts Captured

### Servers
- purebrain.ai: GoDaddy Managed WP
- api.purebrain.ai: DigitalOcean VPS 89.167.19.20:8443 (Flask/Python, SSL, systemd)
- Witness VPS: 104.248.239.98:8099 (container provisioning, HTTP only, access via proxy)
- A-C-Gee VPS: 5.161.90.32:3001 (shared cross-CIV logging)

### All API Endpoints Documented
- `/api/log-conversation` — conversation logger + A-C-Gee forwarding
- `/api/verify-payment` — PayPal live order verification + Brevo + Telegram
- `/api/log-pay-test` — purchase flow completion + post-purchase email trigger
- `/api/health` — health check
- `/api/stats` — conversation statistics
- `/api/paypal-webhook` — webhook receiver with signature verification
- `/api/proxy/birth/start` — rate-limited (5/min) proxy to Witness
- `/api/proxy/birth/code` — proxy to Witness
- `/api/proxy/birth/portal-status/{container}` — polling proxy to Witness

### Brevo List IDs (complete map)
- List 3: Neural Feed (blog subscribers)
- List 8: PureBrain Customers (post-purchase)
- Lists 11-18: Migration leads by competitor

### Deployment Commands Captured
- Netlify: `npx netlify-cli@23.15.1 deploy --prod --dir=... --site=...`
- Vercel: `npx vercel --prod --yes`
- WP Plugin: upload ZIP via WP Admin

---

## Sources Read

- `tools/purebrain_log_server.py` (complete source, ~1,600 lines)
- 8 full-stack-developer memory files from Feb 19-26 range
- Key memories: witness-birth-proxy-endpoints, team-dashboard-supabase-backend, purebrain-hub-v2-full-rebuild, portal-login-3d-neural-integration, post-purchase-brevo-email-integration, purebrain-security-hardening
