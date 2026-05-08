# Memory: legal.purebrain.ai — LawInsider Rebuild Architecture

**Date**: 2026-04-27
**Type**: teaching
**Agent**: architect
**Task**: Design 16-hour AI build plan for a contract intelligence SaaS platform matching LawInsider.com

---

## Pattern: Large Clause Database + FTS5 in D1

D1 FTS5 virtual table is sufficient for full-text search up to approximately 10M rows. Beyond that, sharding by clause_type into separate D1 databases extends viability to ~50M rows. At 50M+, the correct architecture is: R2 for clause text storage, D1 for metadata + embeddings, Cloudflare Vectorize for semantic search.

This three-phase scaling pattern applies to any text search product built on D1.

## Pattern: Dual-Model Claude Strategy for AI Products

For AI products with two distinct workloads:
- **Bulk/background processing** (classification, summarization, ingestion): use claude-haiku — 5x lower cost, higher rate limits, adequate quality for classification tasks
- **User-facing generation** (drafting, review, explanation): use claude-sonnet — highest quality for the customer-visible output

Never use claude-sonnet for bulk ingestion. Never use claude-haiku for contract generation (quality gap is noticeable to lawyers).

## Pattern: User Memory as SaaS Differentiator

The `user_memory` table pattern (user_id, memory_type, key, value, confidence, source) is reusable for any product where persistent preferences create compound value. The pattern:

1. Implicit learning: system extracts preferences from usage patterns after each session
2. Explicit saving: user can state preferences directly
3. Prompt injection: memory fetched before each AI call, injected into system prompt
4. Confidence scoring: allows gradual updates without overwriting established preferences

This pattern applies to voice (preferred speaking pace, vocabulary level), legal (governing law, liability cap structure), and any other AI assistant product. Build the `user_memory` table into every new product from day one.

## Pattern: Public Domain Data Ingestion Sources for Legal

For a clause database product, the three highest-quality free sources are:
1. **SEC EDGAR Exhibit 10**: Material contract exhibits from public company filings. Highest quality (legal-reviewed), widest variety (NDAs, MSAs, employment, licensing). API at efts.sec.gov.
2. **USAspending.gov**: Government contracts with detailed terms. Good for indemnification, payment, termination clause patterns.
3. **SAM.gov**: Federal procurement with pre-award solicitation language. Good for compliance, security, and data handling clauses.

All three are free public APIs with no per-request cost. EDGAR requires no API key. USAspending requires no API key. SAM.gov requires free registration.

## Pattern: Cloudflare CRON Trigger for Continuous Ingestion

For any product that needs to continuously ingest data from external sources, use a separate `ingestion-worker` with a CRON trigger (every 6 hours) rather than building ingestion logic into the main API worker. Benefits: independent scaling, separate rate limit budget, does not affect API worker performance, can be paused/resumed without touching the API.

Cursor-based pagination state stored in Cloudflare KV (lightweight, fast, free within limits).

## Key D1 Schema Decisions

For a clause database product:
- FTS5 virtual table is required from day one — adding it retroactively to millions of rows is painful
- `benchmark_score` and `quality_score` fields enable filter-by-quality — critical for surfacing good clauses over raw volume
- `usage_count` on clauses enables popularity ranking — clauses users include in drafts are better than clauses they ignore
- `user_memory` table with UNIQUE(user_id, memory_type, key) constraint ensures clean upserts

## Office JS Word Add-in Architecture

Word add-in task pane is just HTML/JS served from CF Pages. No separate hosting needed. Key facts:
- `manifest.xml` references the task pane URL (CF Pages URL works fine)
- Auth via `OfficeRuntime.storage` (equivalent to localStorage for add-ins)
- All API calls go to the same CF Worker endpoints as the web app
- Enterprise customers can sideload via Microsoft 365 admin center without AppSource review — this is the fast path for B2B sales
- AppSource listing takes 3-7 business days review — submit on night 2 immediately

## Files Produced

- `/home/jared/exports/portal-files/legal-purebrain-rebuild-plan.md`

## What Was NOT Decided (Deferred to Build Phase)

- Whether to use pdf-parse (npm) or a dedicated text extraction service — depends on PDF complexity encountered during ingestion testing
- Exact Claude prompt structure for contract review — will require iteration against real contracts
- Whether to use Cloudflare Queues or `waitUntil()` for async review processing — waitUntil is simpler, Queues give better error recovery; decide based on review failure rate in practice
- Embeddings for semantic search — deferred to Month 6; FTS5 is sufficient for launch
