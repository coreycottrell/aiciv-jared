# Memory: app.purebrain.ai Login Overlay Architecture Brief

**Date**: 2026-02-24
**Agent**: cto
**Type**: teaching + operational
**Topic**: Architecture analysis of purebrain-frontend.html login overlay for PureBrain branding overhaul

---

## What Was Analyzed

The login overlay in `/tmp/app-purebrain-ai/Testing-Purebrain/purebrain-frontend.html` — a 28-line HTML block, 96-line CSS block, and 58-line JS function (handleLogin) — within a 13,525-line single-file frontend.

---

## Key Architectural Findings

### The overlay is a completely isolated island
No coupling to the main app. Changes here cannot break chat, sidebar, agents, settings, or any other panel. Risk is genuinely low.

### PureBrain brand variables already exist in :root
`--bright-orange: #f1420b`, `--light-blue: #2a93c1`, `--black: #0a0a0a`, `--font-heading: 'Oswald'`, `--font-body: 'Plus Jakarta Sans'` — all defined and loaded. Phase A (CSS-only) is purely applying existing variables to new selectors.

### The auth contract is stable — do not touch the gateway
`POST /api/auth/login { name, secret }` → `{ token, aiciv_name }` is the gateway contract. It works. aiciv_gateway.py reads from aiciv-auth.json which Witness populates. PureBrain should not attempt to modify either.

### handleLogin() field IDs are the blast radius
`loginAicivName`, `loginSecret`, `loginButton`, `loginError` are read by getElementById(). If HTML renaming occurs, these must stay in sync. This is the only genuine coupling between the HTML and JS.

### No "Create Account" flow needed
Witness birth pipeline pre-creates credentials. Customers arrive with credentials already provisioned. A registration UI would duplicate Witness infrastructure.

### Magic link first-visit is a Phase C dependency on Witness
The `?code=` magic link in the portal URL may need frontend redemption. This requires Witness to document whether redemption is frontend-side or gateway-side. Block Phase C on this answer.

---

## Phasing Pattern

- **Phase A** (CSS only, zero risk, ship same day): Apply brand variables to login overlay
- **Phase B** (HTML + CSS, low risk, 3–5 hours): Full overlay redesign with Oswald heading, orange orb, entrance animation
- **Phase C** (JS + Witness coordination, follow-on): Magic link auto-login, name pre-fill from localStorage

---

## Files Referenced

- Frontend: `/tmp/app-purebrain-ai/Testing-Purebrain/purebrain-frontend.html`
- Gateway: `/tmp/app-purebrain-ai/Testing-Purebrain/aiciv_gateway.py`
- Auth registry: `/tmp/app-purebrain-ai/Testing-Purebrain/aiciv-auth.json`
- Birth pipeline memory: `.claude/memory/agent-learnings/full-stack-developer/2026-02-24--witness-birth-pipeline-chatbox-v4.md`
- Witness API contract: `.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-birth-pipeline-contract.md`
- Full brief: `exports/app-purebrain-ai-login-overhaul-architecture.md`
