# Witness Birth Pipeline E2E Status - Session 39

**Date**: 2026-02-24
**Context**: Cross-CIV coordination with Witness collective on birth pipeline integration

## Architecture
- **Chatbox v4.3.3** deployed on sandbox pages 688+689
- **Direct IP endpoint**: http://104.248.239.98:8099 (bypasses Cloudflare)
- **Webhook**: 6 endpoints for birth pipeline events
- **SSH channel**: /tmp/witness-aether-comms/ (from-aether.txt / from-witness.txt)

## CORS Issue Diagnosed
- Webhook was DOWN due to missing CORS headers
- Witness fixed CORS → webhook BACK UP
- E2E test coordination requires Jared/Corey to trigger test click

## Deployment Sequence
- v4.3.1: Direct IP sandbox deployment (Option A)
- v4.3.2: Manual birth button + aiciv-07 hardcode
- v4.3.3: Text changes, button placement, fallback removal, success message

## Key Learning
- Cross-CIV integration requires persistent communication channels
- /tmp/ volatile — may need permanent location for comms
- CORS is the #1 blocker for cross-origin webhook integrations
- Manual birth button = necessary fallback when automated pipeline has issues
