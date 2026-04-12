# Witness Portal Package Review — 2026-03-02

**Type**: operational
**Agent**: collective-liaison
**Topic**: Received portal_server.py package from Witness/Corey, conducted security review

---

## What Was Delivered

Tarball: /tmp/portal-project-from-witness.tar.gz (182K, 51 files)
Extracted to: /home/jared/projects/AI-CIV/aether/inbox/witness-portal-review/

Key files:
- portal_server.py — Starlette/uvicorn backend (~470 lines)
- portal.html — plain dark theme portal (300 lines, zero deps)
- portal-pb-styled.html — PureBrain-branded portal (980 lines)
- react-portal/ — React+Vite frontend (20 components)
- PORTAL-SETUP-GUIDE.md — full setup + API contract documentation
- VIABILITY-ASSESSMENT.md — 88-feature roadmap across 4 tiers

## Architecture

```
Browser -> Caddy (TLS) -> host port -> Docker port mapping -> portal_server.py:8097
portal_server.py -> reads JSONL session logs (chat history)
                 -> injects to tmux (send-keys = session control)
                 -> subprocess checks for status (pgrep, tmux has-session)
```

## Security Findings (for Jared review before any deployment)

1. tmux injection is intentional but powerful: Bearer token = session root access. Must be strong (32-byte random). Access control is everything here.
2. Hardcoded paths for witness environment: LOG_ROOT = /home/aiciv, CIV_NAME = "witness" — both need updating for Aether.
3. HTML portals are publicly served (unauthenticated GET / and /pb). Token auth is client-side localStorage. Acceptable if URL is not broadly shared.
4. No rate limiting on /api/chat/send — low risk if token is secured.
5. start.sh PORT arg defaults to 8080 but portal_server.py hardcodes 8097 — minor inconsistency, trivial fix.
6. No input sanitization on message injection beyond .strip().

## What's Good

- Clean, readable code. Witness team clearly iterated through real problems.
- _despace() and _is_real_user_message() filtering is thoughtful — solves actual JSONL noise issues we'd hit too.
- Three frontend options gives flexibility (start with plain HTML, upgrade to React when needed).
- WebSocket architecture (0.5s poll for terminal, 1.5s for chat) is reasonable.
- Bearer token auto-generates if .portal-token missing — safe default.

## Decision

DO NOT deploy without Jared approval + security-auditor review.

Required adaptations before deployment:
1. Change LOG_ROOT to /home/jared/.claude/projects/-home-jared-projects-AI-CIV-aether
2. Change CIV_NAME to "aether"
3. Fix start.sh PORT default or remove (server ignores it anyway, uses PORT env or 8097)
4. Generate strong bearer token
5. Decide on aether.ai-civ.com DNS setup with Jared

## Hub Coordination

- New message from Witness in witness-aether room (2026-03-02T13:41Z) also contained blocker answers for seed endpoint (178.156.229.207:8200) and auth header format.
- Acknowledgment posted to witness-aether room (commit 013a22c) confirming receipt + review status, pushed to remote.

## Pattern Captured

**Intake protocol for external code packages**:
1. Extract to /inbox/[package]-review/ (NOT deployment location)
2. Read all docs + source code thoroughly
3. Run security checklist (paths, auth, injection surfaces, rate limits)
4. Post acknowledgment to hub within same session
5. Write memory entry
6. Await human approval before any deployment

This pattern applies to all future cross-CIV code deliveries.
