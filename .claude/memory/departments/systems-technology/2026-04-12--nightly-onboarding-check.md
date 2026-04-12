# Nightly Onboarding Check - 2026-04-12

**Type**: operational
**Score**: 121/128 (94.5%), up from 120/128

## Key Findings
- All 8 pages HTTP 200, dark theme, chatbox, PayPal, UUID -- PASS
- PayPal plan IDs match spec on all pages
- JS integrity clean -- 24 console.error refs are all proper error handlers, not bugs
- Trevor/Vex magic link (vex-trevor.app.purebrain.ai) fully operational, portal content present
- Insiders sub-pages both functional, insider-specific plan ID P-8AU4270420374002JNGY3VYQ present
- Log server healthy, AgentMail monitor running
- New checks added: Trevor/Vex magic link (5 checks), insiders sub-pages (2 checks)

## Persistent Issues (Day 3+)
- send-seed endpoint returns 404 (needs payload-based verification)
- R2 demo video returns 401 (bucket access config)
- seed_sent_uuids.json file absent from disk

## Report
Path: ~/exports/portal-files/onboarding-nightly-check-2026-04-12.md
