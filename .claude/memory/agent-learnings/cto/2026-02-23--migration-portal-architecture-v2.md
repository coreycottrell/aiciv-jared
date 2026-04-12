# Memory: AI Migration Portal Architecture — v2

**Date**: 2026-02-23
**Type**: synthesis
**Topic**: AI Migration Portal — v2 architecture with client-side JSZip, file ownership map, integration plan

---

## Key Decisions Changed from v1

### ZIP parsing: Python sidecar → JSZip client-side
- Raw conversation data never leaves the browser
- Profile JSON (keywords, style, topics) is all that gets sent to server
- Privacy claim: "Your raw conversations stay on your device" is literally true
- JSZip 3.10.1 via cdnjs CDN

### SSE: server-side streaming → client-side timed simulation
- Since extraction is synchronous client-side, all cards are ready before Step 3 starts
- setTimeout between card reveals (600-1000ms) gives identical emotional experience
- Eliminates SSE endpoint entirely from MVP backend
- Phase 2 (OAuth integrations) still needs SSE — build it then

### No Python sidecar at all in MVP
- Pattern extraction (frequency analysis) is simple enough for client-side JS
- Eliminates: child_process.spawn, Python dependency, stdout parsing, job queue
- Backend is now purely profile storage and retrieval

## File Ownership Map (No Conflicts)

- `exports/migration-portal-parser.js` → ai-ml-engineer (pure logic, no DOM)
- `exports/migration-portal.html` → full-stack-developer (wizard + API calls)
- `exports/migration-portal-step3-animation.js` → full-stack-developer (Step 3 animator only)
- `tools/purebrain_hub/server/routes/migration.js` → full-stack-developer (backend routes)
- `tools/purebrain_hub/server/db/migration-schema.sql` → full-stack-developer

## Cloudflare Worker Integration (Key Decision)

Worker at pure-brain-dashboard-api.purebrain.workers.dev/v1/messages is NOT modified.
Context injection is client-side: portal reads profile, builds prefix string, prepends to first message.
Worker sees it as a normal message — no Worker code changes needed.

## Sprint Parallelism

Sprints 1 (parser) and 2 (backend) are fully parallel — no shared files.
Sprint 3 portal HTML and animator are mostly parallel.
Sprints 4, 5, 6 sequential.

## Output

Architecture doc v2 saved to: exports/migration-portal-architecture.md
