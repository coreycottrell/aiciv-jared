# Portal Admin Client List — CTS Architecture

**Date**: 2026-03-18
**Type**: operational
**Topic**: How the admin client dashboard works, where AI names live, seed payload structure

## Key Findings

### Admin Client List Endpoint
- Route: `GET /api/cts/customers`
- Server: `portal_server.py` on port 8097, proxied from `portal.purebrain.ai` via nginx
- Source file: `exports/app-purebrain-ai-full-repo/portal-server/portal_server.py` lines 2293-2313
- Registry file: `exports/departments/client-tech-support/keys/_registry.json`
- Current registry: 1 customer (joe_portal, status: pending-install)
- NO AI names in the registry — only SSH creds, server IP, status

### AI Name Data Location
- NOT in the CTS registry
- Lives in: `logs/purebrain_web_conversations.jsonl` (aiName field)
- Lives in: `logs/purebrain_pay_test.jsonl` (aiName field)
- Lives in: `logs/birth_completions.jsonl` (civ_name field)
- Lives in: `exports/*-full-seed.md` files

### Known AI Names (from logs)
Real customers: Prodigy, Flux, Still, Lita, Greg, Meridian, Anchor, Keen
Test: TestBrain, DiagnosticBrain, TestAria, Verification Test

### Seed Payload to Witness
POST to `http://178.156.229.207:8200/intake/seed`
Key field: `seed.metadata.civ_name` = aiName chosen by user
No name validation exists — names forwarded as-is

### Gap Identified
Admin dashboard shows CTS registry (SSH/infra data), NOT AI names.
There is NO cross-reference between the two data stores.
No name uniqueness validation exists anywhere.
